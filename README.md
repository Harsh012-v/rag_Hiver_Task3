# Hiver RAG System

A complete **Retrieval-Augmented Generation (RAG)** system for Hiver's knowledge base, featuring semantic search with embeddings, intelligent answer generation, and a beautiful responsive UI.

![System Architecture](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge) ![Embeddings](https://img.shields.io/badge/Embeddings-SentenceTransformers-FF6F00?style=for-the-badge) ![Vector Search](https://img.shields.io/badge/Search-FAISS-4285F4?style=for-the-badge) ![LLM](https://img.shields.io/badge/LLM-OpenAI-412991?style=for-the-badge)

---

## 🎯 Features

- **Semantic Search**: Uses sentence-transformers for intelligent document retrieval
- **Vector Similarity**: FAISS-powered fast similarity search
- **AI Answers**: OpenAI GPT-3.5 generates contextual answers from retrieved articles
- **Confidence Scoring**: Transparent confidence metrics for retrieval quality
- **Modern UI**: Responsive, dark-themed interface with glassmorphism effects
- **8 KB Articles**: Comprehensive coverage of Hiver features

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │ ───> │   FastAPI    │ ───> │ RAG Engine  │
│  (HTML/CSS/ │      │   Backend    │      │             │
│     JS)     │ <─── │              │ <─── │             │
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                              ┌─────▼────┐  ┌──────▼─────┐  ┌────▼────┐
                              │ Sentence │  │   FAISS    │  │ OpenAI  │
                              │Transform.│  │   Vector   │  │   API   │
                              │          │  │   Store    │  │         │
                              └──────────┘  └────────────┘  └─────────┘
```

---

## 📋 Prerequisites

- Python 3.8+
- Node.js (optional, for serving frontend)
- OpenAI API key

---

## 🚀 Deployment

### Deploy to Vercel

This project is ready for Vercel deployment!

**Quick Deploy:**
```bash
npm install -g vercel
vercel login
vercel
```

**Add Environment Variables:**
```bash
vercel env add OPENAI_API_KEY
vercel --prod
```

**Important:** Vercel has a 10-second timeout on free tier. For production use, consider:
- **Railway** for backend (always-on, ~$5/month)
- **Vercel** for frontend (free)

See [DEPLOY_QUICK.md](DEPLOY_QUICK.md) for quick start or [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd C:\Users\Hp\Downloads\HIVER_TASK3
```

### 2. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI API key
copy .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Start Backend Server

```bash
# From backend directory
python -m uvicorn main:app --reload

# Server will start at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### 4. Open Frontend

```bash
# Option 1: Open directly in browser
# Navigate to frontend/index.html and open in browser

# Option 2: Use Python's HTTP server
cd ../frontend
python -m http.server 3000
# Open http://localhost:3000 in browser
```

---

## 📁 Project Structure

```
HIVER_TASK3/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag_engine.py        # Core RAG logic
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
│
├── kb_articles/             # Knowledge base articles (JSON)
│   ├── automations.json
│   ├── csat_troubleshooting.json
│   ├── shared_inbox.json
│   ├── email_templates.json
│   ├── analytics.json
│   ├── collision_detection.json
│   ├── tags.json
│   └── sla_management.json
│
├── frontend/
│   ├── index.html           # Main UI
│   ├── styles.css           # Styling
│   └── app.js               # Frontend logic
│
├── docs/
│   ├── improvements.md      # 5 improvement suggestions
│   └── failure_case.md      # Failure case analysis
│
└── README.md                # This file
```

---

## 🧪 Testing the Required Queries

### Query 1: Automations Configuration

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I configure automations in Hiver?", "k": 3}'
```

**Expected Results**:
- Top article: "How to Configure Automations in Hiver"
- High confidence score (>0.8)
- Detailed answer about automation setup

### Query 2: CSAT Troubleshooting

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is CSAT not appearing?", "k": 3}'
```

**Expected Results**:
- Top article: "Troubleshooting CSAT Survey Issues"
- High confidence score (>0.8)
- Troubleshooting steps and solutions

---

## 📊 API Endpoints

### `POST /query`
Query the knowledge base

**Request**:
```json
{
  "query": "How do I configure automations?",
  "k": 3
}
```

**Response**:
```json
{
  "query": "How do I configure automations?",
  "retrieved_articles": [
    {
      "rank": 1,
      "title": "How to Configure Automations in Hiver",
      "category": "Automations",
      "tags": ["automations", "workflows"],
      "similarity_score": 0.87,
      "content_preview": "..."
    }
  ],
  "answer": "To configure automations in Hiver...",
  "confidence_score": 0.85,
  "num_retrieved": 3
}
```

### `GET /health`
Check system health

### `GET /stats`
Get knowledge base statistics

---

## 🎨 UI Features

- **Dark Theme**: Easy on the eyes with vibrant gradient accents
- **Glassmorphism**: Modern frosted glass effects
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Polished micro-interactions
- **Confidence Visualization**: Color-coded confidence bars
- **Quick Queries**: One-click testing of common questions

---

## 📚 Documentation

### Improvement Suggestions
See [`docs/improvements.md`](docs/improvements.md) for 5 detailed strategies to enhance retrieval quality:
1. Hybrid Search (Semantic + Keyword)
2. Query Expansion and Reformulation
3. Re-ranking with Cross-Encoders
4. Metadata Filtering
5. User Feedback Loop

### Failure Case Analysis
See [`docs/failure_case.md`](docs/failure_case.md) for:
- Real failure scenario
- Root cause analysis
- Step-by-step debugging process
- Multiple solution approaches

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### Customization

**Change embedding model**:
```python
# In rag_engine.py
model = EmbeddingModel("all-mpnet-base-v2")  # More accurate but slower
```

**Adjust retrieval count**:
```python
# In frontend/app.js
body: JSON.stringify({ query: query, k: 5 })  # Retrieve 5 articles
```

**Modify confidence calculation**:
```python
# In rag_engine.py, RAGEngine.calculate_confidence()
weights = [0.6, 0.3, 0.1]  # Give more weight to top result
```

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check port 8000 is available

### Frontend can't connect to backend
- Ensure backend is running at `http://localhost:8000`
- Check CORS settings in `main.py`
- Verify API_BASE_URL in `app.js`

### Low confidence scores
- Check if query matches KB article topics
- Review similarity scores in API response
- Consider adding more relevant articles

### OpenAI errors
- Verify API key is correct in `.env`
- Check API quota and billing
- System works without OpenAI (retrieval only)

---

## 📈 Performance

- **Embedding Generation**: ~50ms per query
- **Vector Search**: ~10ms for 8 documents
- **Answer Generation**: ~1-2s (OpenAI API)
- **Total Response Time**: ~2-3s end-to-end

**Scalability**:
- Current setup handles 8 articles efficiently
- For 100+ articles, consider:
  - FAISS IVF index for faster search
  - Caching frequent queries
  - Async answer generation

---

## 🤝 Contributing

To add new KB articles:

1. Create a JSON file in `kb_articles/`:
```json
{
  "title": "Your Article Title",
  "category": "Category Name",
  "tags": ["tag1", "tag2"],
  "content": "Article content here..."
}
```

2. Restart the backend server
3. Articles are automatically indexed on startup

---

## 📝 License

This project is created for the Hiver Copilot task evaluation.

---

## 🙏 Acknowledgments

- **FastAPI**: Modern Python web framework
- **Sentence Transformers**: Excellent embedding models
- **FAISS**: Lightning-fast similarity search
- **OpenAI**: Powerful language models

---

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review API documentation at `http://localhost:8000/docs`
3. Examine failure case analysis in `docs/failure_case.md`

---

**Built with ❤️ for Hiver**
