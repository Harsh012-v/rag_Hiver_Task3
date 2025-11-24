"""
Simplified FastAPI Backend - Loads RAG engine lazily
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Hiver RAG API",
    description="Retrieval-Augmented Generation API for Hiver Knowledge Base",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for RAG engine (lazy loading)
_rag_engine = None
_rag_loading = False

def get_rag_engine():
    """Get or initialize RAG engine (lazy loading)"""
    global _rag_engine, _rag_loading
    
    if _rag_engine is not None:
        return _rag_engine
    
    if _rag_loading:
        return None  # Still loading
    
    _rag_loading = True
    try:
        print("Loading RAG engine...")
        from rag_engine import RAGEngine
        
        KB_ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "..", "kb_articles")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        _rag_engine = RAGEngine(KB_ARTICLES_PATH, OPENAI_API_KEY)
        print("✅ RAG Engine loaded successfully!")
        return _rag_engine
    except Exception as e:
        print(f"❌ Error loading RAG engine: {e}")
        _rag_loading = False
        return None


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 3


class QueryResponse(BaseModel):
    query: str
    retrieved_articles: list
    answer: str
    confidence_score: float
    num_retrieved: int


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hiver RAG API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    rag_engine = get_rag_engine()
    return {
        "status": "healthy",
        "rag_engine_initialized": rag_engine is not None,
        "rag_engine_loading": _rag_loading
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_kb(request: QueryRequest):
    """Query the knowledge base"""
    
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Try to get RAG engine
    rag_engine = get_rag_engine()
    
    if rag_engine is None:
        if _rag_loading:
            raise HTTPException(
                status_code=503,
                detail="RAG engine is still loading. Please try again in a few seconds."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="RAG engine failed to initialize. Check server logs."
            )
    
    try:
        # Process query
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        generate_answer = OPENAI_API_KEY is not None and len(OPENAI_API_KEY) > 0
        result = rag_engine.query(request.query, k=request.k, generate_answer=generate_answer)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("Starting Hiver RAG API...")
    print("RAG engine will load on first query (lazy loading)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
