"""Vector store implementation using ChromaDB"""

import chromadb
from chromadb.config import Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for financial knowledge base using ChromaDB"""
    
    def __init__(
        self,
        embedding_model: str = "models/embedding-001",
        chroma_db_path: str = "./data/chroma_db",
        collection_name: str = "financial_knowledge"
    ):
        self.embedding_model = embedding_model
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        
        # Initialize Google AI embeddings
        google_api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable is required")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=google_api_key
        )
        
        # Initialize ChromaDB client
        os.makedirs(chroma_db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize LangChain Chroma wrapper
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
        
        logger.info(f"Initialized VectorStore at {chroma_db_path}")
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to the vector store
        
        Args:
            texts: List of text documents
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
        """
        try:
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            List of dictionaries with 'content', 'metadata', and 'score'
        """
        try:
            # Use similarity search with metadata filtering
            if filter_dict:
                results = self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k
                )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def delete_collection(self):
        """Delete the collection (use with caution)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

