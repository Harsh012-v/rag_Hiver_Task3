"""
FastAPI Backend for Hiver RAG System - Vercel Serverless Compatible
Provides REST API endpoints for querying the knowledge base
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from rag_engine import RAGEngine

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Hiver RAG API",
    description="Retrieval-Augmented Generation API for Hiver Knowledge Base",
    version="1.0.0"
)

# Configure CORS - Allow all origins for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine (will be cached by Vercel)
KB_ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "..", "kb_articles")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Global variable to cache RAG engine
_rag_engine = None

def get_rag_engine():
    """Get or initialize RAG engine (singleton pattern for serverless)"""
    global _rag_engine
    if _rag_engine is None:
        try:
            _rag_engine = RAGEngine(KB_ARTICLES_PATH, OPENAI_API_KEY)
            print("RAG Engine initialized successfully!")
        except Exception as e:
            print(f"Error initializing RAG engine: {e}")
            _rag_engine = None
    return _rag_engine


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 3  # Number of documents to retrieve
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I configure automations in Hiver?",
                "k": 3
            }
        }


class QueryResponse(BaseModel):
    query: str
    retrieved_articles: list
    answer: str
    confidence_score: float
    num_retrieved: int


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Hiver RAG API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "query": "/api/query",
            "health": "/api/health",
            "stats": "/api/stats"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    rag_engine = get_rag_engine()
    return {
        "status": "healthy",
        "rag_engine_initialized": rag_engine is not None,
        "openai_configured": OPENAI_API_KEY is not None and len(OPENAI_API_KEY) > 0
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_kb(request: QueryRequest):
    """
    Query the knowledge base using RAG
    
    Args:
        request: QueryRequest containing the user query and optional parameters
        
    Returns:
        QueryResponse with retrieved articles, generated answer, and confidence score
    """
    rag_engine = get_rag_engine()
    
    if not rag_engine:
        raise HTTPException(
            status_code=500,
            detail="RAG engine not initialized. Check server logs."
        )
    
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    try:
        # Process query through RAG engine
        # Use fast mode (no LLM) if OpenAI is not configured for better performance
        generate_answer = OPENAI_API_KEY is not None and len(OPENAI_API_KEY) > 0
        result = rag_engine.query(request.query, k=request.k, generate_answer=generate_answer)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """Get statistics about the knowledge base"""
    rag_engine = get_rag_engine()
    
    if not rag_engine:
        raise HTTPException(
            status_code=500,
            detail="RAG engine not initialized"
        )
    
    return {
        "total_articles": len(rag_engine.vector_store.documents),
        "embedding_dimension": rag_engine.embedding_model.dimension,
        "model_name": "all-MiniLM-L6-v2"
    }


# Vercel serverless function handler
handler = app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
