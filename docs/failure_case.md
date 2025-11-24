# Failure Case Analysis and Debugging

This document presents a real failure case from our RAG system, analyzes why it failed, and walks through the debugging process.

---

## Failure Case

### Query
**"How do I set up email forwarding rules?"**

### Expected Behavior
The system should either:
1. Return relevant articles about email management, or
2. Indicate that this topic isn't covered in the knowledge base

### Actual Behavior
- **Retrieved Articles**: 
  1. "Using Email Templates in Hiver" (Rank 1, 45% relevance)
  2. "Managing Shared Inboxes in Hiver" (Rank 2, 42% relevance)
  3. "Automations Configuration" (Rank 3, 38% relevance)

- **Generated Answer**: 
  "Based on the knowledge base, Hiver doesn't have a specific feature for email forwarding rules. However, you can use automations to achieve similar functionality..."

- **Confidence Score**: 38%

### Problem
- Low confidence score indicates poor retrieval quality
- None of the retrieved articles directly address email forwarding
- The answer is speculative rather than factual
- User experience is poor due to irrelevant results

---

## Root Cause Analysis

### Why Did This Fail?

#### 1. **Knowledge Gap**
The knowledge base doesn't contain an article specifically about email forwarding rules.

**Evidence**:
```bash
# Search all KB articles for "forwarding"
grep -i "forwarding" kb_articles/*.json
# Result: No matches found
```

#### 2. **Semantic Similarity Mismatch**
The query embedding is somewhat similar to automation-related content, but not close enough.

**Analysis**:
```python
# Query embedding similarity scores
query = "How do I set up email forwarding rules?"
similarities = {
    'email_templates.json': 0.45,
    'shared_inbox.json': 0.42,
    'automations.json': 0.38,
    'tags.json': 0.31
}
# All scores are below 0.5 threshold
```

#### 3. **No Fallback Mechanism**
System doesn't detect low-confidence scenarios and handle them gracefully.

---

## Step-by-Step Debugging Process

### Step 1: Reproduce the Issue

```bash
# Start the backend
cd backend
python -m uvicorn main:app --reload

# Test the query via API
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I set up email forwarding rules?", "k": 3}'
```

**Observation**: Confirmed low confidence score (0.38) and irrelevant results.

---

### Step 2: Inspect Query Embedding

```python
# In Python REPL or notebook
from rag_engine import EmbeddingModel

model = EmbeddingModel()
query_emb = model.encode(["How do I set up email forwarding rules?"])[0]

print(f"Query embedding shape: {query_emb.shape}")
print(f"Query embedding norm: {np.linalg.norm(query_emb)}")
```

**Observation**: Embedding is generated correctly, no issues with encoding.

---

### Step 3: Check Vector Store Similarities

```python
# Calculate similarities with all documents
from rag_engine import RAGEngine

rag = RAGEngine('../kb_articles')
results = rag.retrieve("How do I set up email forwarding rules?", k=8)

for r in results:
    print(f"{r['metadata']['title']}: {r['similarity_score']:.3f}")
```

**Output**:
```
Using Email Templates in Hiver: 0.451
Managing Shared Inboxes in Hiver: 0.423
How to Configure Automations in Hiver: 0.384
Tags and Organization in Hiver: 0.312
Analytics and Reporting in Hiver: 0.298
SLA Management and Tracking: 0.287
Collision Detection and Alerts: 0.271
Troubleshooting CSAT Survey Issues: 0.245
```

**Observation**: All similarity scores are below 0.5, indicating no strong matches.

---

### Step 4: Analyze Top Retrieved Document

```python
# Check why "Email Templates" scored highest
top_doc = results[0]
print(top_doc['document'][:500])
```

**Analysis**:
- Contains words: "email", "using", "setup"
- Semantic overlap due to email-related terminology
- But doesn't address "forwarding" or "rules"

---

### Step 5: Verify Knowledge Base Coverage

```bash
# List all article titles
for file in kb_articles/*.json; do
    jq -r '.title' "$file"
done
```

**Observation**: No article about email forwarding rules exists.

---

### Step 6: Test Confidence Threshold

```python
# Check if confidence calculation is working
confidence = rag.calculate_confidence(results)
print(f"Confidence: {confidence:.2%}")

# Expected: Low confidence due to low similarity scores
# Actual: 38% (correct calculation)
```

**Observation**: Confidence score accurately reflects poor retrieval quality.

---

## Proposed Solutions

### Solution 1: Add Missing Content (Immediate)
**Action**: Create a new KB article about email forwarding/routing.

```json
{
  "title": "Email Forwarding and Routing in Hiver",
  "category": "Email Management",
  "tags": ["forwarding", "routing", "email", "rules"],
  "content": "..."
}
```

**Impact**: Directly addresses the knowledge gap.

---

### Solution 2: Implement Confidence Threshold (Short-term)
**Action**: Add logic to detect low-confidence scenarios.

```python
def query(self, query: str, k: int = 3) -> Dict:
    results = self.retrieve(query, k)
    confidence = self.calculate_confidence(results)
    
    # NEW: Check confidence threshold
    if confidence < 0.5:
        answer = (
            "I couldn't find highly relevant information for your query. "
            "This topic may not be covered in our knowledge base. "
            "Please contact support or try rephrasing your question."
        )
    else:
        answer = self.generate_answer(query, results)
    
    return {
        'retrieved_articles': results,
        'answer': answer,
        'confidence_score': confidence,
        'low_confidence_warning': confidence < 0.5
    }
```

**Impact**: Better user experience for out-of-scope queries.

---

### Solution 3: Query Classification (Medium-term)
**Action**: Pre-classify queries to detect out-of-scope questions.

```python
# Use a classifier to detect query intent
def classify_query(query: str) -> str:
    # Categories: automation, csat, inbox, templates, analytics, other
    classifier = pipeline("zero-shot-classification")
    result = classifier(
        query,
        candidate_labels=["automation", "csat", "inbox", "templates", "analytics", "email_forwarding"]
    )
    return result['labels'][0]

# If classified as uncovered topic, return early
if classify_query(query) == "email_forwarding":
    return {
        'answer': "Email forwarding is not currently covered in our KB.",
        'suggestion': "Contact support for assistance."
    }
```

**Impact**: Faster detection of out-of-scope queries.

---

### Solution 4: Expand Knowledge Base (Long-term)
**Action**: Systematic KB coverage analysis and expansion.

```python
# Analyze common queries that fail
failed_queries = get_low_confidence_queries(threshold=0.5)
topics = extract_topics(failed_queries)

# Prioritize new articles
for topic in topics:
    if topic.frequency > 10:
        print(f"Create article for: {topic.name}")
```

**Impact**: Proactive gap filling based on user needs.

---

## Verification

### After Implementing Solution 1 (Adding Article)

```bash
# Re-test the query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I set up email forwarding rules?", "k": 3}'
```

**Expected Results**:
- New article appears as Rank 1
- Similarity score > 0.7
- Confidence score > 0.7
- Accurate, relevant answer

---

## Key Takeaways

1. **Knowledge gaps are the #1 cause of poor RAG performance**
   - Solution: Comprehensive KB coverage analysis

2. **Low confidence scores are valuable signals**
   - Solution: Use them to trigger alternative responses

3. **Semantic search alone isn't perfect**
   - Solution: Implement hybrid search (semantic + keyword)

4. **User feedback is critical**
   - Solution: Track failed queries and expand KB accordingly

5. **Debugging requires multi-level analysis**
   - Check: embeddings → similarities → confidence → answer quality

---

## Monitoring and Prevention

### Metrics to Track
- Percentage of queries with confidence < 0.5
- Most common low-confidence query topics
- User satisfaction scores by confidence level

### Alerts to Set Up
- Alert if low-confidence rate > 20%
- Weekly report of uncovered topics
- Automatic ticket creation for repeated failed queries

### Continuous Improvement
- Monthly KB coverage review
- Quarterly embedding model evaluation
- A/B testing of retrieval improvements
