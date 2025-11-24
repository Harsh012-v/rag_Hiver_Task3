"""
Ultra-Simple RAG Backend - No Heavy Dependencies
Uses simple TF-IDF for retrieval instead of sentence transformers
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize FastAPI
app = FastAPI(title="Hiver RAG API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
articles = []
vectorizer = None
article_vectors = None

def load_kb_articles():
    """Load KB articles from JSON files"""
    global articles
    kb_path = os.path.join(os.path.dirname(__file__), "..", "kb_articles")
    
    articles = []
    for filename in os.listdir(kb_path):
        if filename.endswith('.json'):
            with open(os.path.join(kb_path, filename), 'r', encoding='utf-8') as f:
                article = json.load(f)
                articles.append(article)
    
    print(f"✅ Loaded {len(articles)} articles")
    return articles

def initialize_vectorizer():
    """Initialize TF-IDF vectorizer"""
    global vectorizer, article_vectors, articles
    
    if not articles:
        load_kb_articles()
    
    # Combine title and content for better matching
    texts = [f"{a['title']} {a['content']}" for a in articles]
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    article_vectors = vectorizer.fit_transform(texts)
    
    print("✅ Vectorizer initialized")

def search_articles(query: str, k: int = 3) -> List[Dict]:
    """Search for relevant articles"""
    global vectorizer, article_vectors, articles
    
    if vectorizer is None:
        initialize_vectorizer()
    
    # Vectorize query
    query_vector = vectorizer.transform([query])
    
    # Calculate similarities
    similarities = cosine_similarity(query_vector, article_vectors)[0]
    
    # Get top k
    top_indices = np.argsort(similarities)[::-1][:k]
    
    results = []
    for rank, idx in enumerate(top_indices, 1):
        article = articles[idx]
        results.append({
            'rank': rank,
            'title': article['title'],
            'category': article['category'],
            'tags': article['tags'],
            'similarity_score': float(similarities[idx]),
            'content_preview': article['content'][:300] + "..."
        })
    
    return results

def calculate_confidence(results: List[Dict]) -> float:
    """Calculate confidence score"""
    if not results:
        return 0.0
    
    # Weighted average of top 3 scores
    weights = [0.5, 0.3, 0.2]
    scores = [r['similarity_score'] for r in results]
    
    confidence = sum(s * w for s, w in zip(scores, weights[:len(scores)]))
    return min(confidence, 1.0)

def generate_answer(query: str, results: List[Dict]) -> str:
    """Generate answer from top result"""
    if not results:
        return "No relevant information found in the knowledge base."
    
    top_article = results[0]
    article_content = next(a['content'] for a in articles if a['title'] == top_article['title'])
    
    answer = f"Based on the article '{top_article['title']}', here's what I found:\n\n{article_content[:500]}..."
    return answer


# Models
class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 3

class QueryResponse(BaseModel):
    query: str
    retrieved_articles: list
    answer: str
    confidence_score: float
    num_retrieved: int


# Endpoints
@app.on_event("startup")
async def startup_event():
    """Load articles on startup"""
    print("Starting Hiver RAG API...")
    load_kb_articles()
    initialize_vectorizer()
    print("✅ Ready to serve requests!")

@app.get("/")
async def root():
    return {"message": "Hiver RAG API", "status": "running"}

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "rag_engine_initialized": vectorizer is not None,
        "articles_loaded": len(articles)
    }

@app.post("/api/query", response_model=QueryResponse)
async def query_kb(request: QueryRequest):
    """Query the knowledge base"""
    
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Search for articles
        results = search_articles(request.query, k=request.k)
        
        # Calculate confidence
        confidence = calculate_confidence(results)
        
        # Generate answer
        answer = generate_answer(request.query, results)
        
        return {
            'query': request.query,
            'retrieved_articles': results,
            'answer': answer,
            'confidence_score': confidence,
            'num_retrieved': len(results)
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
