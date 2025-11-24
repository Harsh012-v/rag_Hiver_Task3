"""
RAG Engine for Hiver Knowledge Base
Handles embeddings, vector search, and answer generation with confidence scoring
"""

import os
import json
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI


class EmbeddingModel:
    """Handles text embedding generation using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence-transformers model
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings
        """
        return self.model.encode(texts, convert_to_numpy=True)


class VectorStore:
    """FAISS-based vector storage and similarity search"""
    
    def __init__(self, dimension: int):
        """
        Initialize the vector store
        
        Args:
            dimension: Dimension of the embedding vectors
        """
        self.dimension = dimension
        # Using L2 distance for similarity (can also use inner product)
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadata = []
    
    def add_documents(self, embeddings: np.ndarray, documents: List[str], metadata: List[Dict]):
        """
        Add documents and their embeddings to the vector store
        
        Args:
            embeddings: Document embeddings
            documents: Original document texts
            metadata: Document metadata (title, category, etc.)
        """
        # Ensure embeddings are float32 for FAISS
        embeddings = embeddings.astype('float32')
        self.index.add(embeddings)
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        print(f"Added {len(documents)} documents to vector store. Total: {len(self.documents)}")
    
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of dictionaries containing document, metadata, and similarity score
        """
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):  # Valid index
                # Convert L2 distance to similarity score (0-1 range)
                # Lower distance = higher similarity
                similarity = 1 / (1 + dist)
                
                results.append({
                    'rank': i + 1,
                    'document': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'similarity_score': float(similarity),
                    'distance': float(dist)
                })
        
        return results


class RAGEngine:
    """Main RAG engine orchestrating retrieval and generation"""
    
    def __init__(self, kb_articles_path: str, openai_api_key: str = None):
        """
        Initialize the RAG engine
        
        Args:
            kb_articles_path: Path to directory containing KB articles
            openai_api_key: OpenAI API key for answer generation
        """
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(self.embedding_model.dimension)
        
        # Initialize OpenAI client
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
        else:
            print("Warning: No OpenAI API key provided. Answer generation will be disabled.")
            self.client = None
        
        # Load and index KB articles
        self._load_kb_articles(kb_articles_path)
    
    def _load_kb_articles(self, kb_articles_path: str):
        """Load KB articles from JSON files and index them"""
        print(f"Loading KB articles from: {kb_articles_path}")
        
        documents = []
        metadata = []
        
        # Read all JSON files in the directory
        for filename in os.listdir(kb_articles_path):
            if filename.endswith('.json'):
                filepath = os.path.join(kb_articles_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    
                    # Combine title and content for better retrieval
                    doc_text = f"{article['title']}\n\n{article['content']}"
                    documents.append(doc_text)
                    
                    metadata.append({
                        'title': article['title'],
                        'category': article.get('category', 'General'),
                        'tags': article.get('tags', []),
                        'filename': filename
                    })
        
        if not documents:
            raise ValueError(f"No KB articles found in {kb_articles_path}")
        
        # Generate embeddings and add to vector store
        print(f"Generating embeddings for {len(documents)} articles...")
        embeddings = self.embedding_model.encode(documents)
        self.vector_store.add_documents(embeddings, documents, metadata)
        print("KB articles indexed successfully!")
    
    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query string
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search vector store
        results = self.vector_store.search(query_embedding, k=k)
        
        return results
    
    def generate_answer(self, query: str, retrieved_docs: List[Dict]) -> str:
        """
        Generate an answer using retrieved documents and LLM
        
        Args:
            query: User query
            retrieved_docs: Retrieved documents from vector search
            
        Returns:
            Generated answer string
        """
        if not self.client:
            return "Answer generation unavailable (no OpenAI API key provided)"
        
        # Prepare context from retrieved documents
        context = "\n\n---\n\n".join([
            f"Article: {doc['metadata']['title']}\n{doc['document']}"
            for doc in retrieved_docs
        ])
        
        # Create prompt for LLM
        system_prompt = """You are a helpful assistant for Hiver, a customer support platform. 
Answer user questions based on the provided knowledge base articles. 
Be concise, accurate, and helpful. If the information isn't in the articles, say so."""
        
        user_prompt = f"""Based on the following knowledge base articles, answer this question:

Question: {query}

Knowledge Base Articles:
{context}

Please provide a clear and helpful answer."""
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def calculate_confidence(self, retrieved_docs: List[Dict]) -> float:
        """
        Calculate confidence score based on retrieval results
        
        Args:
            retrieved_docs: Retrieved documents with similarity scores
            
        Returns:
            Confidence score between 0 and 1
        """
        if not retrieved_docs:
            return 0.0
        
        # Use weighted average of top results
        # Give more weight to the top result
        weights = [0.5, 0.3, 0.2]  # For top 3 results
        
        confidence = 0.0
        for i, doc in enumerate(retrieved_docs[:3]):
            weight = weights[i] if i < len(weights) else 0.0
            confidence += doc['similarity_score'] * weight
        
        # Normalize to 0-1 range
        confidence = min(max(confidence, 0.0), 1.0)
        
        return confidence
    
    def query(self, query: str, k: int = 3, generate_answer: bool = True) -> Dict:
        """
        Main query method - retrieves documents and optionally generates answer
        
        Args:
            query: User query string
            k: Number of documents to retrieve
            generate_answer: Whether to generate AI answer (slower) or just retrieve
            
        Returns:
            Dictionary containing retrieved docs, answer, and confidence
        """
        print(f"\nProcessing query: {query}")
        
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, k=k)
        
        # Calculate confidence
        confidence = self.calculate_confidence(retrieved_docs)
        
        # Generate answer only if requested and OpenAI is available
        if generate_answer and self.client:
            answer = self.generate_answer(query, retrieved_docs)
        else:
            # Fast response without LLM - use top article content
            if retrieved_docs:
                top_article = retrieved_docs[0]
                answer = f"Based on the knowledge base article '{top_article['metadata']['title']}', here's what I found:\n\n{top_article['document'][:500]}..."
            else:
                answer = "No relevant information found in the knowledge base."
        
        # Prepare response
        response = {
            'query': query,
            'retrieved_articles': [
                {
                    'rank': doc['rank'],
                    'title': doc['metadata']['title'],
                    'category': doc['metadata']['category'],
                    'tags': doc['metadata']['tags'],
                    'similarity_score': doc['similarity_score'],
                    'content_preview': doc['document'][:300] + "..."
                }
                for doc in retrieved_docs
            ],
            'answer': answer,
            'confidence_score': confidence,
            'num_retrieved': len(retrieved_docs)
        }
        
        return response
