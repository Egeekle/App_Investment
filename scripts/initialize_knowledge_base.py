"""Script to initialize the knowledge base"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.vector_store import VectorStore
from src.rag.knowledge_base import initialize_knowledge_base
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize knowledge base"""
    try:
        chroma_db_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        
        logger.info(f"Initializing knowledge base at {chroma_db_path}")
        
        vector_store = VectorStore(chroma_db_path=chroma_db_path)
        initialize_knowledge_base(vector_store)
        
        logger.info("Knowledge base initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing knowledge base: {e}")
        raise


if __name__ == "__main__":
    main()

