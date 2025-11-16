"""
Synapse Backend API - FastAPI Server
Provides semantic search endpoint for marketing documents
"""

# Patch websockets before importing supabase
import websockets_patch  # noqa: F401
# Add this import
import aiofiles
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import os
from typing import Dict, Optional
import tempfile
from pathlib import Path
from supabase import create_client, Client
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
import pdfplumber
from docx import Document
from fastapi.staticfiles import StaticFiles
# Import the Supabase error class
from postgrest.exceptions import APIError

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
# This line "mounts" the demo_documents folder so it's accessible over the web
DEMO_DOCUMENTS_DIR = "demo_documents"
os.makedirs(DEMO_DOCUMENTS_DIR, exist_ok=True)
app.mount("/demo_documents", StaticFiles(directory="demo_documents"), name="demo_documents")

# Load the sentence transformer model (cache it globally)
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!")


# Request/Response models
class SearchRequest(BaseModel):
    query: str
    match_threshold: Optional[float] = 0.1
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
    Semantic search endpoint with CORRECTED LOGGING.
    """
    print("\n" + "="*30)
    print(f"🔥 NEW SEARCH REQUEST 🔥")
    print(f"Query: {request.query}")
    print(f"Topic Filter: {request.topic}")
    print(f"Project Filter: {request.project}")
    print(f"Threshold: {request.match_threshold}")
    print("="*30)
    
    try:
        # Generate embedding for the query
        print("1. Encoding query...")
        query_embedding = model.encode(request.query).tolist()
        print(f"   Done. Embedding starts with: {str(query_embedding)[:50]}...")

        rpc_params = {
            'query_embedding': query_embedding,
            'match_threshold': request.match_threshold,
            'match_count': request.match_count,
            'filter_topic': request.topic,
            'filter_project': request.project
        }
        
        # Calling the new V2 function to bypass cache
        print("2. Calling database function 'match_documents_v2'...")
        # A successful call returns a response object
        # A failed call raises an APIError
        response = supabase.rpc('match_documents_v2', rpc_params).execute()
        
        print("\n--- DATABASE RESPONSE ---")
        print("✅ Call Succeeded.")
        print(f"Response Data: {response.data}")
        print("---------------------------\n")

        # The database now does all the filtering
        filtered_data = response.data if response.data else []
        
        print(f"3. Found {len(filtered_data)} matching chunks.")

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
        
        print("4. Formatting complete. Sending response.")

        return SearchResponse(
            results=results,
            files=files,
            query=request.query,
            total_results=len(results),
            total_files=len(files)
        )
        
    except APIError as e:
        print(f"💥💥💥 CAUGHT SUPABASE APIError 💥💥💥")
        print(f"Code: {e.code}")
        print(f"Message: {e.message}")
        print(f"Details: {e.details}")
        print(f"Hint: {e.hint}")
        raise HTTPException(status_code=500, detail=f"Database Search Error: {e.message}")
    except Exception as e:
        print(f"💥💥💥 CAUGHT GENERAL Exception 💥💥💥")
        print(f"{type(e)}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/testsearch/{query_text}")
async def test_search(query_text: str):
    """
    A 'dumb' test to see if we can find new rows at all,
    bypassing all vector logic. CORRECTED ERROR HANDLING.
    """
    print(f"🔥 DUMB SEARCH for: {query_text}")
    try:
        response = supabase.rpc('test_search', {'query_text': query_text}).execute()
        
        print(f"✅ DUMB SEARCH found {len(response.data)} rows.")
        return {"results": response.data}
        
    except APIError as e:
        print(f"❌ DUMB SEARCH FAILED (APIError): {e.message}")
        return {"error": e.message}
    except Exception as e:
        print(f"💥 DUMB SEARCH CRASHED (Exception): {str(e)}")
        return {"error": str(e)}


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


# Helper functions for file processing (reused from ingest.py)
def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a PDF file"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF: {e}")


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from a DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise ValueError(f"Error reading DOCX: {e}")


def extract_text_from_txt(file_path: Path) -> str:
    """Extract text from a TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"Error reading TXT: {e}")


def extract_text_from_md(file_path: Path) -> str:
    """Extract text from a Markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"Error reading MD: {e}")


def extract_text(file_path: Path) -> str:
    """Extract text from a file based on its extension"""
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return extract_text_from_pdf(file_path)
    elif suffix == '.docx':
        return extract_text_from_docx(file_path)
    elif suffix == '.txt':
        return extract_text_from_txt(file_path)
    elif suffix == '.md':
        return extract_text_from_md(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def categorize_document(text: str, filename: str = "") -> Dict[str, Optional[str]]:
    """Free rule-based categorization using keyword matching"""
    text_lower = text.lower()
    filename_lower = filename.lower()
    combined_text = f"{filename_lower} {text_lower}"
    
    topic = None
    topic_scores = {"Strategy": 0, "Content": 0, "Report": 0, "Brief": 0}
    
    strategy_keywords = ["strategy", "strategic", "plan", "planning", "roadmap", "vision",
                         "objective", "goal", "mission", "approach", "framework", "methodology"]
    for keyword in strategy_keywords:
        if keyword in combined_text:
            topic_scores["Strategy"] += 1
    
    content_keywords = ["content", "blog", "post", "article", "calendar", "schedule",
                        "editorial", "publishing", "social media", "social", "campaign",
                        "email", "newsletter", "draft", "writing"]
    for keyword in content_keywords:
        if keyword in combined_text:
            topic_scores["Content"] += 1
    
    report_keywords = ["report", "results", "performance", "metrics", "analytics", "data",
                       "analysis", "summary", "findings", "insights", "quarterly", "q1", "q2",
                       "q3", "q4", "roi", "conversion", "engagement", "campaign results"]
    for keyword in report_keywords:
        if keyword in combined_text:
            topic_scores["Report"] += 1
    
    brief_keywords = ["brief", "briefing", "overview", "summary", "outline", "proposal",
                      "project brief", "campaign brief", "creative brief"]
    for keyword in brief_keywords:
        if keyword in combined_text:
            topic_scores["Brief"] += 1
    
    if max(topic_scores.values()) > 0:
        topic = max(topic_scores, key=topic_scores.get)
    
    project = None
    project_x_keywords = ["project x", "projectx", "proj x", "projx"]
    for keyword in project_x_keywords:
        if keyword in combined_text:
            project = "Project X"
            break
    
    if not project:
        project_y_keywords = ["project y", "projecty", "proj y", "projy"]
        for keyword in project_y_keywords:
            if keyword in combined_text:
                project = "Project Y"
                break
    
    if not project:
        if "internal" in combined_text or "team" in combined_text or "meeting" in combined_text:
            project = "Internal"
    
    return {"topic": topic, "project": project}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    topic: Optional[str] = Form(None),
    project: Optional[str] = Form(None)
):
    """
    Upload and ingest a document file
    
    Supported formats: PDF, DOCX, TXT, MD
    Optionally provide topic and project for categorization
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # === MODIFIED: Define permanent save path ===
    save_path = Path(DEMO_DOCUMENTS_DIR) / file.filename

    try:
        # === MODIFIED: Asynchronously read and write the file ===
        try:
            content = await file.read()
            async with aiofiles.open(save_path, 'wb') as out_file:
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        # === MODIFIED: Process the file from its new permanent path ===
        try:
            # Extract text
            text = extract_text(save_path)
            if not text.strip():
                # Clean up the file if it's bad and we can't extract text
                save_path.unlink(missing_ok=True) 
                raise HTTPException(status_code=400, detail="No text could be extracted from the file")
            
            # Auto-categorize if topic/project not provided
            if topic is None or project is None:
                categorization = categorize_document(text, file.filename)
                topic = topic or categorization.get("topic")
                project = project or categorization.get("project")
            
            # Chunk text
            chunks = chunk_text(text, chunk_size=500, overlap=100)
            
            # Generate embeddings
            embeddings = model.encode(chunks, show_progress_bar=False)
            
            # Prepare records for batch insert
            records = []
            for chunk, embedding in zip(chunks, embeddings):
                records.append({
                    "content": chunk,
                    "source": file.filename,
                    "embedding": embedding.tolist(),
                    "topic": topic,
                    "project": project
                })
            
            # Insert into Supabase
            response = supabase.table('documents').insert(records).execute()
            
            # === MODIFIED: We no longer delete the file ===
            # tmp_file_path.unlink() # <-- This is gone!
            
            return {
                "success": True,
                "filename": file.filename,
                "chunks_created": len(records),
                "topic": topic,
                "project": project,
                "message": f"Successfully ingested {file.filename} with {len(records)} chunks"
            }
            
        except ValueError as e:
            # Clean up the saved file on a processing error
            save_path.unlink(missing_ok=True) 
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Clean up the saved file on a processing error
            save_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
            
    except Exception as e:
        # This will catch the file save error
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Enable reload so changes are picked up
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)