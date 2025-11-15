"""
Helper script to create .env file from template
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping creation.")
        return
    
    # Create .env.example content if it doesn't exist
    if not env_example.exists():
        env_example.write_text("""# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Optional: Google Gemini API Key (for auto-categorization)
GEMINI_API_KEY=your_gemini_api_key

# Ingestion Configuration
DEMO_DOCUMENTS_FOLDER=./demo_documents

# Server Configuration (optional)
PORT=8000
""")
        print("✅ Created .env.example template")
    
    # Copy example to .env
    env_file.write_text(env_example.read_text())
    print("✅ Created .env file from template")
    print("📝 Please edit .env and add your Supabase credentials")

if __name__ == "__main__":
    create_env_file()


