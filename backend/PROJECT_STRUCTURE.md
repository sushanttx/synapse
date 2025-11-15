# Synapse Backend - Project Structure

```
backend/
├── main.py              # FastAPI server with /search endpoint
├── ingest.py            # Document ingestion pipeline
├── database.sql         # Supabase schema and functions
├── requirements.txt     # Python dependencies
├── config.py            # Configuration helper
├── setup_env.py         # Environment setup helper
├── .gitignore          # Git ignore rules
├── README.md           # Full documentation
└── PROJECT_STRUCTURE.md # This file
```

## Key Files

### `main.py`
FastAPI backend server with:
- `POST /search` - Semantic search endpoint
- `GET /topics` - Get all unique topics
- `GET /projects` - Get all unique projects
- `GET /` - Health check

### `ingest.py`
One-time ingestion script that:
- Crawls `demo_documents/` folder
- Extracts text from PDF, DOCX, TXT, MD files
- Chunks text into 500-char segments with 100-char overlap
- Generates embeddings using `all-MiniLM-L6-v2`
- Stores in Supabase with optional auto-categorization

### `database.sql`
SQL schema for Supabase:
- Enables `pgvector` extension
- Creates `documents` table
- Creates `match_documents()` function for similarity search
- Creates indexes for performance

### `requirements.txt`
All Python dependencies including:
- FastAPI & Uvicorn
- Sentence Transformers
- Supabase client
- File parsers (pdfplumber, python-docx)
- Google Generative AI (optional)

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up `.env` file with Supabase credentials
3. Run `database.sql` in Supabase SQL Editor
4. Run `python ingest.py` to index documents
5. Run `python main.py` to start the API server

See `README.md` for detailed instructions.


