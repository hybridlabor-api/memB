import os
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DB_PATH = os.path.expanduser("~/.MemBDB/memb.db")
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Pydantic Models for type safety
class Node(BaseModel):
    id: str
    label: str
    type: str
    color: str
    size: float
    payload: Optional[Dict[str, Any]] = None

class Edge(BaseModel):
    source: str
    target: str

# Initialize app
app = FastAPI(
    title="memB Semantic Brain Visualizer Backend",
    description="Clean API providing nodes and edges for the graph visualizer",
    version="1.0.0"
)

def get_db_connection() -> Optional[sqlite3.Connection]:
    if not os.path.exists(DB_PATH):
        logger.warning(f"Database not found at {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)

def fetch_graph_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Fetches and transforms raw data from SQLite into nodes and links."""
    conn = get_db_connection()
    if not conn:
        return [], []
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, payload FROM memb_vectors")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        logger.error(f"Database operational error: {e}")
        # Table might not exist yet
        return [], []
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise HTTPException(status_code=500, detail="Internal database error")
    finally:
        conn.close()

    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, str]] = []
    
    # Static central hub
    hubs: Dict[str, Dict[str, Any]] = {
        "hub_godmode": {
            "id": "hub_godmode",
            "label": "GODMODE ALL NODES",
            "type": "hub",
            "color": "#6B21A8",
            "size": 18.0
        }
    }
    
    for row_id, payload_str in rows:
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON payload for row {row_id}")
            continue
            
        category = payload.get("category", "godmode")
        project_id = payload.get("project_id")
        text = payload.get("data", "Memory record")
        
        leaf_node = {
            "id": str(row_id),
            "label": text[:50] + "..." if len(text) > 50 else text,
            "type": "leaf",
            "color": "rgba(240, 240, 255, 0.95)",
            "size": 4.0,
            "payload": payload
        }
        nodes.append(leaf_node)
        
        if category == "godmode":
            links.append({"source": "hub_godmode", "target": str(row_id)})
        else:
            proj_key = f"hub_{project_id}" if project_id else "hub_other"
            proj_label = project_id if project_id else "Other Projects"
            
            if proj_key not in hubs:
                hubs[proj_key] = {
                    "id": proj_key,
                    "label": proj_label,
                    "type": "hub",
                    "color": "#00F2FE",
                    "size": 12.0
                }
            
            links.append({"source": proj_key, "target": str(row_id)})
            
    combined_nodes = list(hubs.values()) + nodes
    
    for h_id in hubs:
        if h_id != "hub_godmode":
            links.append({"source": "hub_godmode", "target": h_id})
            
    return combined_nodes, links

@app.get("/api/nodes", response_model=List[Node])
async def get_nodes():
    """Returns the list of graph nodes."""
    nodes, _ = fetch_graph_data()
    return nodes

@app.get("/api/edges", response_model=List[Edge])
async def get_edges():
    """Returns the list of graph edges."""
    _, edges = fetch_graph_data()
    return edges

# Ensure frontend directory exists before mounting to avoid FastAPI crash
if not os.path.exists(FRONTEND_DIR):
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    with open(index_path, "w") as f:
        f.write("<!DOCTYPE html><html><head><title>memB</title></head><body><h1>Frontend pending build</h1></body></html>")

# Mount static files at root
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8088, reload=True)
