import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CHROMA_DB_PATH = Path("./chroma_db")
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o-mini"
    
    # Vector store settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5
    
    # Sample data settings
    NUM_SAMPLE_DOCUMENTS = 20
    
    # External content settings
    ENABLE_EXTERNAL_CONTENT = os.getenv("ENABLE_EXTERNAL_CONTENT", "true").lower() == "true"
    EXTERNAL_CONTENT_TIMEOUT = int(os.getenv("EXTERNAL_CONTENT_TIMEOUT", "10"))
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Create chroma db directory if it doesn't exist
        cls.CHROMA_DB_PATH.mkdir(exist_ok=True)