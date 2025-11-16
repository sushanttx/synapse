# Synapse: The Seeker 🧠✨

Synapse is a smart semantic search engine for your documents. Upload your knowledge base (PDFs, DOCX, TXT files) and ask questions in natural language to find the most relevant information.

### Live Demo
* **Frontend (Vercel):** `[https://synapse-chi-five.vercel.app/]`
* **Backend (Render):** `https://synapse-s10m.onrender.com`



---

## 🚀 Key Features

* **Semantic Search:** Uses AI (Sentence Transformers) to understand the *meaning* of your query, not just keywords.
* **File Upload:** Ingest new documents (`.pdf`, `.docx`, `.txt`, `.md`) directly from the UI.
* **AI-Powered Processing:** Automatically extracts text, splits it into manageable chunks, and generates vector embeddings.
* **Vector Database:** Leverages Supabase with the `pgvector` extension for efficient vector storage and similarity search.
* **Metadata Filtering:** Automatically categorizes and tags documents, allowing you to filter search results by `topic` or `project`.
* **Backend Status:** A live status indicator shows if the backend API is online and responsive.

## 🛠️ Technology Stack

* **Frontend:** React (Vite), Tailwind CSS
* **Backend:** Python, FastAPI, Uvicorn
* **AI Model:** `SentenceTransformers ('all-MiniLM-L6-v2')`
* **Database:** Supabase (PostgreSQL with `pgvector`)
* **Deployment:**
    * Frontend on **Vercel**
    * Backend on **Render**

## 🔧 Local Development Setup

### Prerequisites

* Git
* Python 3.11+
* Node.js & npm
* A Supabase account (with a new project)

### 1. Supabase Database Setup

Before running the code, you need to set up your Supabase database.

1.  **Create a new Supabase Project.**
2.  Go to the **SQL Editor** in your project dashboard.
3.  **Enable the `vector` extension:**
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```
4.  **Create the `documents` table:**
    ```sql
    CREATE TABLE documents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        content TEXT NOT_NULL,
        source TEXT NOT_NULL,  -- The filename
        topic TEXT,
        project TEXT,
        embedding VECTOR(384)  -- 384 dimensions for 'all-MiniLM-L6-v2'
    );
    ```
5.  **Create the database function (`match_documents_v2`)**
    This function is what `FastAPI` calls. It calculates the similarity between your query and the stored chunks.
    ```sql
    CREATE OR REPLACE FUNCTION match_documents_v2 (
        query_embedding VECTOR(384),
        match_threshold FLOAT,
        match_count INT,
        filter_topic TEXT,
        filter_project TEXT
    )
    RETURNS TABLE (
        id UUID,
        content TEXT,
        source TEXT,
        topic TEXT,
        project TEXT,
        similarity FLOAT
    )
    LANGUAGE sql STABLE
    AS $$
      SELECT
          documents.id,
          documents.content,
          documents.source,
          documents.topic,
          documents.project,
          1 - (documents.embedding <=> query_embedding) AS similarity
      FROM documents
      WHERE (filter_topic IS NULL OR documents.topic = filter_topic)
        AND (filter_project IS NULL OR documents.project = filter_project)
        AND 1 - (documents.embedding <=> query_embedding) > match_threshold
      ORDER BY similarity DESC
      LIMIT match_count;
    $$;
    ```

---

### 2. Local Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/sushanttx/synapse.git](https://github.com/sushanttx/synapse.git)
    cd synapse
    ```

2.  **Setup Backend (FastAPI):**
    ```bash
    # Navigate to the backend folder
    cd backend

    # Create a Python virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt

    # Create a .env file
    cp .env.example .env
    ```
    Now, edit the `backend/.env` file and add your Supabase credentials (from your project's "API" settings page):
    ```env
    SUPABASE_URL="https"//your-project-id.supabase.co"
    SUPABASE_KEY="your-public-anon-key"
    ```

3.  **Setup Frontend (React):**
    ```bash
    # Navigate to the frontend folder (from the root)
    cd ../frontend

    # Install dependencies
    npm install

    # Create a .env.local file
    touch .env.local
    ```
    Now, edit the `frontend/.env.local` file to point to your *local* backend:
    ```env
    VITE_API_BASE_URL="http://localhost:8000"
    ```

4.  **Run the App:**
    * **Run Backend:** Open a terminal in the `/backend` folder and run:
        ```bash
        python main.py
        ```
    * **Run Frontend:** Open a *second* terminal in the `/frontend` folder and run:
        ```bash
        npm run dev
        ```
    Open `http://localhost:5173` in your browser.

## 🚢 Deployment

This project is designed for a split deployment.

### Backend (Render)

1.  Create a new **Web Service** on Render.
2.  Connect your GitHub repository.
3.  Use the following settings:
    * **Root Directory:** `backend`
    * **Build Command:** `pip install -r requirements.txt`
    * **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
    * **Python Version:** `3.12.0` (or as required)
4.  Add your **Environment Variables**:
    * `SUPABASE_URL`: (Your Supabase URL)
    * `SUPABASE_KEY`: (Your Supabase Key)
    * `PYTHON_VERSION`: `3.12.0`

### Frontend (Vercel)

1.  Create a new **Project** on Vercel.
2.  Connect your GitHub repository.
3.  Configure the project settings:
    * **Framework Preset:** `Vite`
    * **Root Directory:** `frontend`
4.  Add your **Environment Variable**:
    * `VITE_API_BASE_URL`: `https://synapse-s10m.onrender.com` (Your *live* Render backend URL)
5.  Deploy!

## 🗺️ API Endpoints

The backend provides the following endpoints:

* `GET /health`: A simple health check. Returns `{"status": "ok"}`.
* `POST /search`: The main search endpoint.
* `POST /upload`: Uploads a new document for processing and ingestion.
* `GET /stats`: Provides stats about the documents in the database.
* `GET /topics`: Returns a list of all unique topics.
* `GET /projects`: Returns a list of all unique projects.