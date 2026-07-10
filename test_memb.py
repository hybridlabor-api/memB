import os
import sys

# Add path so we can import memb directly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from memb import Memory

def test_memb():
    print("=== Testing memB offline core ===")
    
    # Configure Memory to use local_onnx and numpy_flat
    config = {
        "embedder": {
            "provider": "local_onnx",
            "config": {}
        },
        "vector_store": {
            "provider": "numpy_flat",
            "config": {
                "collection_name": "test_collection",
                "path": os.path.abspath("./test_memb.db")
            }
        },
        "llm": {
            "provider": "gemini",
            "config": {
                "model": "gemini-1.5-flash"
            }
        }
    }
    
    # Initialize Memory
    os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY") or "dummy-api-key"
    
    print("Initializing Memory engine...")
    m = Memory.from_config(config)
    
    # Direct embedding test
    print("Testing local ONNX embedder directly...")
    emb = m.embedding_model.embed("This is a BDB test string")
    print(f"Embedding success. Dimensions: {len(emb)}")
    
    # Inserting directly into flat SQLite vector store
    print("Testing NumPyFlat insert...")
    m.vector_store.insert(
        vectors=[emb],
        payloads=[{"text": "This is a BDB test string", "category": "godmode"}],
        ids=["test-id-1"]
    )
    print("Insert success.")
    
    # Searching directly
    print("Testing NumPyFlat search...")
    results = m.vector_store.search(
        query=None,
        vectors=emb,
        top_k=1
    )
    
    print(f"Search results count: {len(results)}")
    for res in results:
        print(f"Match: ID={res.id}, Score={res.score}, Payload={res.payload}")
        
    print("=== memB test passed successfully ===")

if __name__ == "__main__":
    test_memb()
export_placeholder = "done"
