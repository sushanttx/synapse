"""
Configuration helper for Synapse backend
"""

import os
from typing import Optional

# Supabase Configuration
SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

# Gemini API (Optional - for auto-categorization)
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

# Ingestion Configuration
DEMO_DOCUMENTS_FOLDER: str = os.getenv("DEMO_DOCUMENTS_FOLDER", "./demo_documents")
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))

# Server Configuration
PORT: int = int(os.getenv("PORT", "8000"))

# Model Configuration
MODEL_NAME: str = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION: int = 384

def validate_config():
    """Validate that required configuration is present"""
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable is required")
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY environment variable is required")
    return True





