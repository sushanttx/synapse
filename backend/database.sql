-- Synapse Database Schema for Supabase
-- This script sets up the vector database for semantic search

-- 1. Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the table to store documents and embeddings
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,              -- The text chunk
    source TEXT NOT NULL,               -- The filename (e.g., "Q3_Report.pdf")
    embedding VECTOR(384) NOT NULL,     -- The 384-dim embedding from all-MiniLM-L6-v2
    topic TEXT,                         -- Auto-categorized topic (Strategy, Content, Report, Brief)
    project TEXT,                       -- Auto-categorized project (Project X, Project Y, Internal)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create an index on the embedding column for faster similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Create indexes for filtering by topic and project
CREATE INDEX IF NOT EXISTS documents_topic_idx ON documents(topic);
CREATE INDEX IF NOT EXISTS documents_project_idx ON documents(project);
CREATE INDEX IF NOT EXISTS documents_source_idx ON documents(source);

-- 5. Create a function for similarity search
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    source TEXT,
    similarity FLOAT,
    topic TEXT,
    project TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.source,
        1 - (documents.embedding <=> query_embedding) AS similarity,
        documents.topic,
        documents.project
    FROM documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 6. Optional: Create a function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents INT,
    total_chunks INT,
    unique_sources INT,
    topics JSONB,
    projects JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(DISTINCT source) FROM documents)::INT AS total_documents,
        (SELECT COUNT(*) FROM documents)::INT AS total_chunks,
        (SELECT COUNT(DISTINCT source) FROM documents)::INT AS unique_sources,
        (SELECT jsonb_agg(DISTINCT topic) FROM documents WHERE topic IS NOT NULL) AS topics,
        (SELECT jsonb_agg(DISTINCT project) FROM documents WHERE project IS NOT NULL) AS projects;
END;
$$;

-- 7. Grant necessary permissions (adjust as needed for your Supabase setup)
-- These are typically handled automatically by Supabase, but included for reference
-- GRANT USAGE ON SCHEMA public TO authenticated;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO authenticated;


