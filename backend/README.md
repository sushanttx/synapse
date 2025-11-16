# Synapse Backend

Smart Marketing Knowledge Search - Backend API built with FastAPI and Supabase.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Supabase account (free tier works)
- (Optional) Google Gemini API key for auto-categorization

### Installation

1. **Clone and navigate to backend folder:**
```bash
cd backend
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Database Setup (Supabase)

1. **Create a new Supabase project** at [supabase.com](https://supabase.com)

2. **Enable pgvector extension:**
   - Go to Database → Extensions
   - Search for "vector" and enable it

3. **Run the SQL schema:**
   - Go to SQL Editor in Supabase dashboard
   - Copy and paste the contents of `database.sql`
   - Execute the script

4. **Get your credentials:**
   - Go to Settings → API
   - Copy your Project URL and anon/public key
   - Add them to your `.env` file

### Running the Ingestion Pipeline

1. **Create a demo documents folder:**
```bash
mkdir demo_documents
# Add some .pdf, .docx, .txt, or .md files to this folder
```

2. **Run the ingestion script:**
```bash
python ingest.py
```

This will:
- Crawl the `demo_documents` folder
- Extract text from all supported files
- Split into chunks
- Generate embeddings
- Store in Supabase

### Running the API Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### `GET /`
Health check endpoint.

#### `POST /search`
Semantic search endpoint.

**Request:**
```json
{
  "query": "What were our Q3 campaign results?",
  "match_threshold": 0.5,
  "match_count": 10,
  "topic": "Report",  // Optional filter
  "project": "Project X"  // Optional filter
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "content": "The campaign results for Q3 showed...",
      "source": "Q3_Report.pdf",
      "similarity": 89.5,
      "topic": "Report",
      "project": "Project X"
    }
  ],
  "query": "What were our Q3 campaign results?",
  "total_results": 1
}
```

#### `GET /topics`
Get all unique topics from the database.

#### `GET /projects`
Get all unique projects from the database.

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📦 Deployment

### Deploy to Render

1. **Create a new Web Service** on [Render](https://render.com)

2. **Connect your GitHub repository**

3. **Configure build settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add environment variables:**
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GEMINI_API_KEY` (optional)
   - `PORT` (Render sets this automatically)

5. **Deploy!**

### Alternative: Deploy to Hugging Face Spaces

1. Create a new Space with Docker
2. Use the Dockerfile provided (if created)
3. Set environment variables in Space settings

## 🔧 Configuration

### Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `GEMINI_API_KEY`: (Optional) For auto-categorization
- `DEMO_DOCUMENTS_FOLDER`: Path to documents folder (default: `./demo_documents`)
- `PORT`: Server port (default: 8000)

### Chunking Configuration

Edit `ingest.py` to adjust:
- `CHUNK_SIZE`: Size of text chunks (default: 500 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 100 characters)

## 🧪 Testing

Test the API with curl:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "marketing strategy"}'
```

## 📝 Notes

- The first run will download the `all-MiniLM-L6-v2` model (~80MB)
- Embeddings are 384-dimensional vectors
- Similarity scores are returned as percentages (0-100)
- Auto-categorization requires a Gemini API key

## 🐛 Troubleshooting

**Issue: "SUPABASE_URL not set"**
- Make sure your `.env` file exists and contains the correct values

**Issue: "Model download fails"**
- Check your internet connection
- The model downloads automatically on first use

**Issue: "No documents found"**
- Ensure `demo_documents` folder exists and contains supported file types
- Supported: `.pdf`, `.docx`, `.txt`, `.md`

**Issue: "Vector similarity search slow"**
- The ivfflat index is created automatically
- For large datasets, you may need to tune the `lists` parameter in the index

## 📚 Project Structure

```
backend/
├── main.py              # FastAPI server
├── ingest.py            # Ingestion pipeline
├── database.sql         # Supabase schema
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── README.md           # This file
└── demo_documents/     # Your documents folder (create this)
```

## 🤝 Contributing

This is a hackathon project. Feel free to extend it!

## 📄 License

MIT



