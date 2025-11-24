"""
Quick diagnostic script to test the RAG engine
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("HIVER RAG SYSTEM - DIAGNOSTIC TEST")
print("=" * 60)

print("\n1. Testing imports...")
try:
    from rag_engine import RAGEngine
    print("✅ RAG engine imported successfully")
except Exception as e:
    print(f"❌ Failed to import RAG engine: {e}")
    sys.exit(1)

print("\n2. Checking KB articles path...")
kb_path = os.path.join(os.path.dirname(__file__), "..", "kb_articles")
kb_path = os.path.abspath(kb_path)
print(f"KB Path: {kb_path}")
print(f"Exists: {os.path.exists(kb_path)}")

if os.path.exists(kb_path):
    files = [f for f in os.listdir(kb_path) if f.endswith('.json')]
    print(f"JSON files found: {len(files)}")
    for f in files:
        print(f"  - {f}")
else:
    print("❌ KB articles directory not found!")
    sys.exit(1)

print("\n3. Initializing RAG engine...")
try:
    rag = RAGEngine(kb_path)
    print("✅ RAG engine initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize RAG engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Testing query...")
try:
    result = rag.query("How do I configure automations in Hiver?", k=3, generate_answer=False)
    print("✅ Query executed successfully")
    print(f"\nResults:")
    print(f"  - Confidence: {result['confidence_score']:.2%}")
    print(f"  - Retrieved: {result['num_retrieved']} articles")
    print(f"  - Top article: {result['retrieved_articles'][0]['title']}")
except Exception as e:
    print(f"❌ Query failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe RAG system is working correctly.")
print("If the web interface isn't working, the issue is with the API endpoint.")
