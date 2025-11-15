"""
Synapse Ingestion Pipeline
Crawls local documents, extracts text, chunks, embeds, and stores in Supabase
"""

# Patch websockets before importing supabase
import websockets_patch  # noqa: F401

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DEMO_DOCUMENTS_FOLDER = os.getenv("DEMO_DOCUMENTS_FOLDER", "./demo_documents")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize clients (lazy initialization to avoid import-time errors)
supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set as environment variables")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

# Load the sentence transformer model
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!")


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a PDF file"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from a DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""


def extract_text_from_txt(file_path: Path) -> str:
    """Extract text from a TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""


def extract_text_from_md(file_path: Path) -> str:
    """Extract text from a Markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading MD {file_path}: {e}")
        return ""


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
        print(f"Unsupported file type: {suffix}")
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        
        # Prevent infinite loop
        if start >= len(text):
            break
    
    return chunks


def categorize_document(text: str, filename: str = "") -> Dict[str, Optional[str]]:
    """
    Free rule-based categorization using keyword matching
    Returns dict with 'topic' and 'project' keys
    """
    text_lower = text.lower()
    filename_lower = filename.lower()
    combined_text = f"{filename_lower} {text_lower}"
    
    # Topic categorization based on keywords
    topic = None
    topic_scores = {
        "Strategy": 0,
        "Content": 0,
        "Report": 0,
        "Brief": 0
    }
    
    # Strategy keywords
    strategy_keywords = [
        "strategy", "strategic", "plan", "planning", "roadmap", "vision",
        "objective", "goal", "mission", "approach", "framework", "methodology"
    ]
    for keyword in strategy_keywords:
        if keyword in combined_text:
            topic_scores["Strategy"] += 1
    
    # Content keywords
    content_keywords = [
        "content", "blog", "post", "article", "calendar", "schedule",
        "editorial", "publishing", "social media", "social", "campaign",
        "email", "newsletter", "draft", "writing"
    ]
    for keyword in content_keywords:
        if keyword in combined_text:
            topic_scores["Content"] += 1
    
    # Report keywords
    report_keywords = [
        "report", "results", "performance", "metrics", "analytics", "data",
        "analysis", "summary", "findings", "insights", "quarterly", "q1", "q2",
        "q3", "q4", "roi", "conversion", "engagement", "campaign results"
    ]
    for keyword in report_keywords:
        if keyword in combined_text:
            topic_scores["Report"] += 1
    
    # Brief keywords
    brief_keywords = [
        "brief", "briefing", "overview", "summary", "outline", "proposal",
        "project brief", "campaign brief", "creative brief"
    ]
    for keyword in brief_keywords:
        if keyword in combined_text:
            topic_scores["Brief"] += 1
    
    # Get topic with highest score
    if max(topic_scores.values()) > 0:
        topic = max(topic_scores, key=topic_scores.get)
    
    # Project categorization based on keywords
    project = None
    
    # Check for Project X
    project_x_keywords = ["project x", "projectx", "proj x", "projx"]
    for keyword in project_x_keywords:
        if keyword in combined_text:
            project = "Project X"
            break
    
    # Check for Project Y
    if not project:
        project_y_keywords = ["project y", "projecty", "proj y", "projy"]
        for keyword in project_y_keywords:
            if keyword in combined_text:
                project = "Project Y"
                break
    
    # If no project found, check filename patterns
    if not project:
        if "internal" in combined_text or "team" in combined_text or "meeting" in combined_text:
            project = "Internal"
    
    return {
        "topic": topic,
        "project": project
    }


def crawl_documents(folder_path: Path) -> List[Path]:
    """Crawl folder for supported document types"""
    supported_extensions = ['.pdf', '.docx', '.txt', '.md']
    documents = []
    
    for ext in supported_extensions:
        documents.extend(folder_path.rglob(f"*{ext}"))
    
    return documents


def ingest_document(file_path: Path, topic: Optional[str] = None, project: Optional[str] = None):
    """Process a single document: extract, chunk, embed, and store"""
    print(f"\nProcessing: {file_path.name}")
    
    # Extract text
    text = extract_text(file_path)
    if not text.strip():
        print(f"  ⚠️  No text extracted from {file_path.name}")
        return
    
    # Auto-categorize using free rule-based classifier
    if topic is None or project is None:
        print(f"  🤖 Auto-categorizing document (free rule-based)...")
        categorization = categorize_document(text, file_path.name)
        topic = topic or categorization.get("topic")
        project = project or categorization.get("project")
        if topic or project:
            print(f"  ✅ Categorized: topic={topic}, project={project}")
    
    # Chunk text
    chunks = chunk_text(text)
    print(f"  📄 Created {len(chunks)} chunks")
    
    # Generate embeddings for all chunks
    print(f"  🔄 Generating embeddings...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    
    # Prepare data for batch insert
    records = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        records.append({
            "content": chunk,
            "source": file_path.name,
            "embedding": embedding.tolist(),
            "topic": topic,
            "project": project
        })
    
    # Insert into Supabase (batch insert)
    print(f"  💾 Storing {len(records)} chunks in database...")
    try:
        client = get_supabase_client()
        response = client.table('documents').insert(records).execute()
        print(f"  ✅ Successfully stored {len(records)} chunks")
    except Exception as e:
        print(f"  ❌ Error storing chunks: {e}")
        raise


def main():
    """Main ingestion function"""
    print("=" * 60)
    print("Synapse Ingestion Pipeline")
    print("=" * 60)
    
    # Check if demo_documents folder exists
    demo_folder = Path(DEMO_DOCUMENTS_FOLDER)
    if not demo_folder.exists():
        print(f"❌ Error: Demo documents folder not found: {demo_folder}")
        print(f"   Please create the folder and add some documents.")
        sys.exit(1)
    
    # Crawl for documents
    print(f"\n📁 Crawling folder: {demo_folder}")
    documents = crawl_documents(demo_folder)
    
    if not documents:
        print(f"❌ No supported documents found in {demo_folder}")
        print(f"   Supported formats: .pdf, .docx, .txt, .md")
        sys.exit(1)
    
    print(f"✅ Found {len(documents)} documents")
    
    # Ask user if they want to clear existing data
    print("\n⚠️  Warning: This will add new documents to the database.")
    print("   If you want to start fresh, delete existing data in Supabase first.")
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Process each document
    total_chunks = 0
    for doc_path in documents:
        try:
            ingest_document(doc_path)
            # Count chunks for this document
            chunks = chunk_text(extract_text(doc_path))
            total_chunks += len(chunks)
        except Exception as e:
            print(f"❌ Failed to process {doc_path.name}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"✅ Ingestion complete!")
    print(f"   Processed {len(documents)} documents")
    print(f"   Created {total_chunks} chunks")
    print("=" * 60)


if __name__ == "__main__":
    main()

