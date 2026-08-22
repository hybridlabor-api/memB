import os
import sys
import threading
import time
# Ensure local memb module is loaded
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run

def test_concurrent_writes():
    """Stress test 10 parallel threads writing to verify SQLite WAL concurrency."""
    errors = []
    
    def worker(worker_id):
        try:
            for i in range(5):
                text = f"Concurrent test fact from worker {worker_id}, iteration {i} at {time.time()}"
                run.add_memory(text, user_id="stress_test_user", category="testing_patterns", project_id="concurrency_suite", infer=False)
        except Exception as e:
            errors.append((worker_id, str(e)))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Clean up test data
    run.delete_all_memories(user_id="stress_test_user", project_id="concurrency_suite")
    
    assert len(errors) == 0, f"Concurrent writes failed with errors: {errors}"
    print("✅ test_concurrent_writes PASSED: 50 concurrent writes across 10 threads succeeded without locking.")

def test_hybrid_search():
    """Verify exact keyword matching via FTS5 BM25 + dense search."""
    unique_token = f"TOKEN_XYZ_PORT_8899_CONFIG_{int(time.time())}"
    run.add_memory(f"Network setting: The DMX gateway runs on {unique_token} with ArtNet subnet 2.", user_id="token_test_user", category="domain_glossary", project_id="lighting_rig", infer=False)
    
    # Query exact token
    results = run.search_memory(unique_token, user_id="token_test_user", limit=1)
    assert len(results) > 0, "Failed: Keyword search did not find unique token"
    assert unique_token in results[0]["memory"], f"Failed: Memory content missing token: {results[0]['memory']}"
    
    # Cleanup
    run.delete_all_memories(user_id="token_test_user", project_id="lighting_rig")
    print("✅ test_hybrid_search PASSED: Exact token search succeeded via FTS5 BM25 hybrid ranking.")

def test_scoped_delete_safety():
    """Verify delete_all_memories only deletes matching project and preserves others."""
    run.add_memory("Project A secret convention", user_id="safety_test_user", project_id="proj_A", infer=False)
    run.add_memory("Project B secret convention", user_id="safety_test_user", project_id="proj_B", infer=False)
    
    # Delete only proj_A
    run.delete_all_memories(user_id="safety_test_user", project_id="proj_A")
    
    # Verify proj_B is still intact
    res_b = run.search_memory("secret convention", user_id="safety_test_user", project_id="proj_B", limit=5)
    assert len(res_b) > 0, "Failed: delete_all wiped proj_B when proj_A was targeted!"
    
    # Cleanup
    run.delete_all_memories(user_id="safety_test_user", project_id="proj_B")
    print("✅ test_scoped_delete_safety PASSED: Scoped deletion safely preserved unrelated projects.")

def test_ingest_deduplication():
    """Verify that memb_ingest skips duplicate document chunks across runs via flat content_hash."""
    import memb_ingest
    mem = memb_ingest.init_memory()
    
    docs = [
        {
            "project": "dedup_test_suite",
            "type": "unit_test_doc",
            "source": "test_file.md",
            "content": "This is unique content for testing cross-run deduplication."
        }
    ]
    
    # Run 1: Should ingest 1
    memb_ingest.ingest_to_memb(mem, docs, category="testing_patterns", purge_project="dedup_test_suite")
    items_after_run1 = mem.vector_store.list(filters={"project_id": "dedup_test_suite"})
    assert len(items_after_run1) == 1, f"Expected 1 item, got {len(items_after_run1)}"
    
    # Run 2: Should detect content_hash and skip
    memb_ingest.ingest_to_memb(mem, docs, category="testing_patterns")
    items_after_run2 = mem.vector_store.list(filters={"project_id": "dedup_test_suite"})
    assert len(items_after_run2) == 1, f"Expected still 1 item due to deduplication, got {len(items_after_run2)}"
    
    # Cleanup
    for item in items_after_run2:
        mem.delete(getattr(item, "id"))
    print("✅ test_ingest_deduplication PASSED: Cross-run deduplication successfully skipped identical chunks.")

if __name__ == "__main__":
    test_concurrent_writes()
    test_hybrid_search()
    test_scoped_delete_safety()
    test_ingest_deduplication()
    print("\n🎉 ALL PRODUCTION HARDENING TESTS PASSED!")
