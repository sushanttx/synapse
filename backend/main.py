"""
Synapse Backend API - FastAPI Server
Provides semantic search endpoint for marketing documents
"""

# Patch websockets before importing supabase
import websockets_patch  # noqa: F401

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import os
from supabase import create_client, Client
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Synapse API",
    description="Smart Marketing Knowledge Search API",
    version="1.0.0"
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set as environment variables.\n"
        "Please create a .env file with your Supabase credentials.\n"
        "See .env.example for reference."
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load the sentence transformer model (cache it globally)
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!")


# Request/Response models
class SearchRequest(BaseModel):
    query: str
    match_threshold: Optional[float] = 0.5
    match_count: Optional[int] = 10
    topic: Optional[str] = None
    project: Optional[str] = None


class SearchResult(BaseModel):
    id: str
    content: str
    source: str  # Filename
    file_name: str  # Same as source, for clarity
    similarity: float
    topic: Optional[str] = None
    project: Optional[str] = None
    chunk_index: Optional[int] = None  # Which chunk this is from the document


class FileResult(BaseModel):
    """Grouped results by file"""
    file_name: str
    file_path: str  # Full path or relative path
    chunks: List[SearchResult]
    best_similarity: float
    topic: Optional[str] = None
    project: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]  # Individual chunks
    files: List[FileResult]  # Grouped by file
    query: str
    total_results: int
    total_files: int


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Synapse API",
        "version": "1.0.0"
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Semantic search endpoint
    
    Converts the user's query into an embedding and finds the most
    semantically similar document chunks from the database.
    Returns both individual chunks and results grouped by file.
    """
    try:
        # Generate embedding for the query
        query_embedding = model.encode(request.query).tolist()
        
        # Call the RPC function
        response = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': request.match_threshold,
                'match_count': request.match_count * 2  # Get more results to filter
            }
        ).execute()
        
        # Filter results if topic/project filters are provided
        filtered_data = response.data if response.data else []
        if request.topic:
            filtered_data = [r for r in filtered_data if r.get('topic') == request.topic]
        if request.project:
            filtered_data = [r for r in filtered_data if r.get('project') == request.project]
        
        # Limit to requested count after filtering
        filtered_data = filtered_data[:request.match_count]
        
        # Format individual chunk results
        results = [
            SearchResult(
                id=str(result['id']),
                content=result['content'],
                source=result['source'],
                file_name=result['source'],  # Explicit file name
                similarity=round(result['similarity'] * 100, 2),  # Convert to percentage
                topic=result.get('topic'),
                project=result.get('project'),
                chunk_index=None
            )
            for result in filtered_data
        ]
        
        # Group results by file
        files_dict = {}
        for result in filtered_data:
            file_name = result['source']
            if file_name not in files_dict:
                files_dict[file_name] = {
                    'chunks': [],
                    'topic': result.get('topic'),
                    'project': result.get('project'),
                    'best_similarity': result['similarity']
                }
            
            chunk_result = SearchResult(
                id=str(result['id']),
                content=result['content'],
                source=result['source'],
                file_name=result['source'],
                similarity=round(result['similarity'] * 100, 2),
                topic=result.get('topic'),
                project=result.get('project'),
                chunk_index=None
            )
            files_dict[file_name]['chunks'].append(chunk_result)
            
            # Update best similarity
            if result['similarity'] > files_dict[file_name]['best_similarity']:
                files_dict[file_name]['best_similarity'] = result['similarity']
        
        # Convert to FileResult list, sorted by best similarity
        files = [
            FileResult(
                file_name=file_name,
                file_path=f"demo_documents/{file_name}",  # Relative path
                chunks=sorted(file_data['chunks'], key=lambda x: x.similarity, reverse=True),
                best_similarity=round(file_data['best_similarity'] * 100, 2),
                topic=file_data['topic'],
                project=file_data['project']
            )
            for file_name, file_data in sorted(
                files_dict.items(),
                key=lambda x: x[1]['best_similarity'],
                reverse=True
            )
        ]
        
        return SearchResponse(
            results=results,
            files=files,
            query=request.query,
            total_results=len(results),
            total_files=len(files)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/topics")
async def get_topics():
    """Get all unique topics from the database"""
    try:
        response = supabase.table('documents').select('topic').execute()
        topics = list(set([r['topic'] for r in response.data if r.get('topic')]))
        return {"topics": sorted(topics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch topics: {str(e)}")


@app.get("/projects")
async def get_projects():
    """Get all unique projects from the database"""
    try:
        response = supabase.table('documents').select('project').execute()
        projects = list(set([r['project'] for r in response.data if r.get('project')]))
        return {"projects": sorted(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get database statistics - useful for debugging"""
    try:
        # Get total chunks
        chunks_response = supabase.table('documents').select('id', count='exact').execute()
        total_chunks = chunks_response.count if hasattr(chunks_response, 'count') else len(chunks_response.data)
        
        # Get unique sources
        sources_response = supabase.table('documents').select('source').execute()
        unique_sources = list(set([r['source'] for r in sources_response.data]))
        
        # Get topics and projects
        topics_response = supabase.table('documents').select('topic').execute()
        topics = list(set([r['topic'] for r in topics_response.data if r.get('topic')]))
        
        projects_response = supabase.table('documents').select('project').execute()
        projects = list(set([r['project'] for r in projects_response.data if r.get('project')]))
        
        return {
            "total_chunks": total_chunks,
            "total_files": len(unique_sources),
            "files": unique_sources,
            "topics": sorted(topics),
            "projects": sorted(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

