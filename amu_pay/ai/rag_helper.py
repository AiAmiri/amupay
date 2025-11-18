"""
RAG Helper module for querying Pinecone vector database.
Provides documentation search functionality for the AI chatbot.
"""

import logging
import os
from typing import List, Optional
from decouple import config
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

logger = logging.getLogger(__name__)


class RAGHelper:
    """
    Helper class for Retrieval-Augmented Generation (RAG).
    Handles documentation search from Pinecone vector database.
    """
    
    _embeddings = None
    _vector_store = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """
        Initialize embeddings and vector store (lazy loading).
        Only initializes once per application lifecycle.
        """
        if cls._initialized:
            return
        
        try:
            logger.info("Initializing RAG Helper...")
            
            # Explicitly check environment variable
            if "PINECONE_API_KEY" not in os.environ:
                logger.error("Pinecone API key not found in environment variables")
                return
            
            # Initialize embeddings
            cls._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Initialize Pinecone
            api_key = config('PINECONE_API_KEY')
            index_name = config('PINECONE_INDEX_NAME', default='amu-pay-docs')
            
            if api_key == 'your_pinecone_api_key_here':
                logger.warning("Pinecone API key not configured - RAG disabled")
                return
            
            # Initialize vector store
            cls._vector_store = PineconeVectorStore(
                index_name=index_name,
                embedding=cls._embeddings
            )
            
            cls._initialized = True
            logger.info("RAG Helper initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Helper: {str(e)}")
            cls._initialized = False
    
    @classmethod
    def search_documentation(cls, query: str, top_k: int = 3) -> str:
        """
        Search for relevant documentation based on user query.
        
        Args:
            query: User's question or search query
            top_k: Number of most relevant documents to retrieve
            
        Returns:
            Formatted string with relevant documentation chunks
        """
        try:
            # Initialize if not already done
            if not cls._initialized:
                cls.initialize()
            
            # If initialization failed, return empty
            if not cls._vector_store:
                logger.warning("Vector store not initialized - RAG disabled")
                return ""
            
            # Perform similarity search
            logger.info(f"Searching Pinecone for query: '{query}'")
            docs = cls._vector_store.similarity_search(query, k=top_k)
            
            if not docs:
                logger.warning(f"No relevant documentation found for query: '{query}'")
                return ""
            
            # Format results
            formatted_results = []
            for i, doc in enumerate(docs, 1):
                title = doc.metadata.get('title') or doc.metadata.get('screen_name', 'Unknown')
                content = doc.page_content
                
                # Truncate long content for logging
                log_content = content[:75] + "..." if len(content) > 75 else content
                logger.info(f"Retrieved doc {i}: {title} | {log_content}")
                
                # Include metadata in response
                source = doc.metadata.get('source', 'Unknown source')
                page_ref = doc.metadata.get('page_ref', '')
                formatted_results.append(
                    f"[مستند {i} - {title}]\n"
                    f"منبع: {source}\n"
                    f"مرجع صفحه: {page_ref}\n\n"
                    f"{content}"
                )
            
            result = "\n\n".join(formatted_results)
            logger.info(f"Found {len(docs)} relevant chunks for query: '{query}'")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error searching documentation: {str(e)}")
            return ""
    
    @classmethod
    def is_documentation_query(cls, query: str) -> bool:
        """
        Determine if the query is asking about app documentation/usage.
        
        Args:
            query: User's question
            
        Returns:
            True if query is about documentation, False otherwise
        """
        # Keywords that indicate documentation queries
        doc_keywords = [
            # Dari/Pashto question words
            'چطور', 'چطوری', 'چگونه', 'چی', 'چیه', 'کجا', 'کجاست', 'چرا',
            'راهنما', 'آموزش', 'استفاده', 'کار', 'عملکرد', 'توضیح',
            # English question words
            'how', 'what', 'where', 'why', 'guide', 'tutorial', 'use', 'using', 'work', 'working',
            # App features
            'feature', 'screen', 'page', 'button', 'menu', 'setting', 'settings',
            'theme', 'language', 'profile', 'account', 'زبان', 'صفحه',
            # UI elements
            'دکمه', 'فیلد', 'منو', 'تنظیمات', 'پروفایل', 'حساب', 'تب',
            # Actions
            'ورود', 'ثبت نام', 'رمز', 'رمزعبور', 'تایید', 'تغییر', 'عوض', 'انتخاب',
            'اضافه', 'حذف', 'ویرایش', 'انجام', 'اجرا', 'راه اندازی',
            'login', 'register', 'signup', 'password', 'verify', 'change', 'select',
            'add', 'remove', 'delete', 'edit', 'do', 'run', 'setup',
            # Common phrases
            'امکان دارد', 'میتوانم', 'میتونم', 'میشه', 'می شود', 'چطور می توانم',
            'how can i', 'is it possible', 'can i', 'how to'
        ]
        
        query_lower = query.lower()
        is_doc_query = any(keyword in query_lower for keyword in doc_keywords)
        
        # Additional check for question words at start
        question_prefixes = ['چطور', 'چگونه', 'چرا', 'کجا', 'چی', 'how', 'what', 'where', 'why']
        starts_with_question = any(query_lower.startswith(prefix) for prefix in question_prefixes)
        
        final_decision = is_doc_query or starts_with_question
        logger.info(f"Query classification: '{query}' -> is_documentation={final_decision}")
        return final_decision
    
    @classmethod
    def get_relevant_context(cls, query: str, top_k: int = 3) -> Optional[str]:
        """
        Get relevant documentation context for a query.
        Returns None if query is not about documentation.
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            
        Returns:
            Documentation context or None
        """
        # Check if this is a documentation query
        if not cls.is_documentation_query(query):
            logger.info(f"Query not classified as documentation: '{query}'")
            return None
        
        logger.info(f"Query classified as documentation: '{query}' - searching Pinecone")
        
        # Search and return results
        result = cls.search_documentation(query, top_k)
        
        if not result:
            logger.warning(f"No documentation found for query: '{query}'")
        else:
            logger.info(f"Returning {top_k} documentation chunks for query: '{query}'")
            
        return result


def search_app_documentation(query: str, top_k: int = 3) -> str:
    """
    Convenience function to search app documentation.
    
    Args:
        query: User's question
        top_k: Number of documents to retrieve
        
    Returns:
        Formatted documentation results
    """
    return RAGHelper.search_documentation(query, top_k)


def get_documentation_context(query: str, top_k: int = 3) -> Optional[str]:
    """
    Convenience function to get documentation context if relevant.
    
    Args:
        query: User's question
        top_k: Number of documents to retrieve
        
    Returns:
        Documentation context or None
    """
    return RAGHelper.get_relevant_context(query, top_k)
