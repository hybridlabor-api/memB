import os
import sys
import uuid
import hashlib
from datetime import datetime, timezone

# Ensure we can import memb
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from memb import Memory

def main():
    db_dir = os.path.expanduser("~/.MemBDB")
    db_path = os.path.join(db_dir, "memb.db")
    history_db_path = os.path.join(db_dir, "history.db")
    
    print(f"=== Initializing memB database at {db_path} ===")
    
    memory_config = {
        "embedder": {
            "provider": "local_onnx",
            "config": {}
        },
        "vector_store": {
            "provider": "numpy_flat",
            "config": {
                "collection_name": "bdb_agent_memory",
                "path": db_path
            }
        },
        "llm": {
            "provider": "gemini",
            "config": {
                "model": "gemini-1.5-flash",
                "api_key": "dummy-key-offline"
            }
        },
        "history_db_path": history_db_path
    }
    
    os.makedirs(db_dir, exist_ok=True)
    memory = Memory.from_config(memory_config)
    
    # Define our manually audited facts from the Second Brain
    memories_to_ingest = [
        # 1. Global God Mode (category="godmode", project_id=None)
        {"text": "Tim Rennings is the lead creative technologist and developer.", "category": "godmode", "project_id": None},
        {"text": "Tim Rennings owns Denck Design Studio (3D Design, Architecture, Visual Identity) and Hybridlabor (Event Planning).", "category": "godmode", "project_id": None},
        {"text": "Yola is Tim's partner/collaborator who handles 3D rendering and previz projections.", "category": "godmode", "project_id": None},
        {"text": "Tim Rennings is responsible for technical direction and engineering; he does not handle event teardown (Abbau).", "category": "godmode", "project_id": None},
        {"text": "For event setups, Tim and Yola prefer to arrive 5-7 days early, provided budget accommodations are arranged.", "category": "godmode", "project_id": None},
        {"text": "React frontend projects should prioritize React 18, Vite as build tool, and TailwindCSS.", "category": "godmode", "project_id": None},
        {"text": "React Three Fiber (R3F) setups should keep geometries optimized (max 10k vertices) for premium 3D preloaders.", "category": "godmode", "project_id": None},
        {"text": "Email settings migration: Thunderbird uses IONOS mail servers for custom domains.", "category": "godmode", "project_id": None},
        {"text": "Local network mesh: Fritz!Box Cable is configured as a Mesh-Repeater for technical operations.", "category": "godmode", "project_id": None},
        
        # 2. Project Leaf: StrandInSicht (project_id="StrandInSicht")
        {"text": "TV Quiz show 'Strand in Sicht' is sponsored by schauinsland-reisen with yellow/azure-blue corporate colors.", "category": "project_node", "project_id": "StrandInSicht"},
        {"text": "Shoot structure: 8 episodes block-filmed over 4 to 5 days.", "category": "project_node", "project_id": "StrandInSicht"},
        {"text": "Set design in Tropical Islands (Krausnick) requires high-humidity (60-80%) protection. Do not use plain paper/cardboard; use Forex, laminated print, or composite boards.", "category": "project_node", "project_id": "StrandInSicht"},
        {"text": "Tropical Islands shoot requires nighttime setup shifts due to daytime park guests.", "category": "project_node", "project_id": "StrandInSicht"},
        {"text": "Standard TV camera crew package for 5 days ranges between 20,000 EUR to 32,000 EUR including equipment.", "category": "project_node", "project_id": "StrandInSicht"},
        {"text": "Set design and prop styling budget quotes: Efficiency: 12k-18k EUR; Mid-range: 20k-35k EUR; High-end custom builds: 40k+ EUR.", "category": "project_node", "project_id": "StrandInSicht"},

        # 3. Project Leaf: CreativeTech (project_id="CreativeTech")
        {"text": "Rhino 3D models are exported via Datasmith format for Unreal Engine imports.", "category": "project_node", "project_id": "CreativeTech"},
        {"text": "Resolume Arena uses 8-position bar animations bound to BPM clocks.", "category": "project_node", "project_id": "CreativeTech"},
        {"text": "grandMA3 lighting consoles use custom macros mapped to Quickkeys.", "category": "project_node", "project_id": "CreativeTech"},
        {"text": "MadMapper DMX blackout troubleshooting is resolved by checking active NDI streaming sources.", "category": "project_node", "project_id": "CreativeTech"}
    ]
    
    print(f"Starting offline ingestion of {len(memories_to_ingest)} memories...")
    
    for idx, item in enumerate(memories_to_ingest):
        text = item["text"]
        category = item["category"]
        project_id = item["project_id"]
        
        # 1. Generate local embedding vector
        emb = memory.embedding_model.embed(text)
        
        # 2. Setup ID and MD5 hash
        memory_id = str(uuid.uuid4())
        mem_hash = hashlib.md5(text.encode()).hexdigest()
        created_at = datetime.now(timezone.utc).isoformat()
        
        # 3. Construct the payload matching SQLite NumPyFlat expectations
        payload = {
            "user_id": "bdb_developer",
            "category": category,
            "data": text,
            "hash": mem_hash,
            "created_at": created_at,
            "updated_at": created_at
        }
        if project_id:
            payload["project_id"] = project_id
            
        # 4. Insert into SQLite vector store table
        memory.vector_store.insert(
            vectors=[emb],
            ids=[memory_id],
            payloads=[payload]
        )
        
        # 5. Insert audit log history record
        memory.db.add_history(
            memory_id=memory_id,
            old_memory=None,
            new_memory=text,
            event="ADD",
            created_at=created_at,
            is_deleted=0,
            actor_id="bdb_developer"
        )
        
        print(f" -> [{idx+1}/{len(memories_to_ingest)}] Ingested offline: '{text[:45]}...'")
        
    print("\n=== All Second Brain memories ingested successfully into memB! ===")

if __name__ == "__main__":
    main()
