# 📐 memB System Architecture

This document describes the technical architecture, data flows, and component layouts of the **memB** offline-first memory engine.

---

## 🏗️ Core Technology Stack

- **Core Framework:** Python 3.10+
- **API Server:** FastAPI + Uvicorn (exposed via Model Context Protocol)
- **Local Embedding Engine:** `onnxruntime` + HuggingFace `tokenizers` running a pre-quantized `all-MiniLM-L6-v2` model (30MB).
- **Relational & Vector Storage:** SQLite3 (custom flat vector index implementation in `numpy_flat.py`).

---

## 🗄️ Storage Topology

To ensure strict data security and separation between different projects and global settings, `memB` stores all data locally in the user's home directory.

```
~/.MemBDB/
├── memb.db        <-- Main SQLite file containing vectors, payloads, and clusters
└── history.db     <-- Audit trails, memory revisions, and timeline logs
```

### 1. Vector Database Schema (`memb_vectors` Table)

| Column | Type | Description |
| :--- | :--- | :--- |
| **`id`** | `TEXT` (Primary Key) | Auto-generated UUID reference for the memory. |
| **`collection`** | `TEXT` | Isolates memory boundaries (defaults to `bdb_agent_memory`). |
| **`vector`** | `BLOB` | Packed binary float32 representation of the 384-dimensional ONNX embedding vector. |
| **`payload`** | `TEXT` | JSON string containing memory keys (`data`, `category`, `project_id`, `created_at`). |
| **`created_at`** | `TIMESTAMP` | Record creation timestamp. |

---

## 🔄 Dynamic Memory Retrieval (God Mode Hierarchy)

To prevent context leakage between isolated projects, memory queries leverage a hierarchical search. When an agent searches for memories, the retrieval system performs a parallel check:

1. **Global preferences:** Fetches memories where `category="godmode"` and `project_id=None`.
2. **Project-specific context:** Fetches memories matching the active folder basename (`project_id="<current-folder-name>"`).
3. **Merging & Ranking:** Merges both sets, performs cosine similarity calculation on the local float32 vectors, and returns the top-ranked results to the agent.

```
                       ┌───────────────────────────────┐
                       │   "GOD MODE" GENERAL KNOWLEDGE │
                       │   (category="godmode",         │
                       │    project_id=None)           │
                       └──────────────┬───────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
     ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
     │   PROJECT A     │      │   PROJECT B     │      │   PROJECT C     │
     │ (project_id=    │      │ (project_id=    │      │ (project_id=    │
     │ "VisualSelect") │      │ "litha-gather") │      │ "hybrid-api")   │
     └─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## 📈 Visual Graph Pipeline

The interactive graph visualizer (`scripts/visualizer.py`) reads directly from the `memb_vectors` table and translates SQLite records into a D3.js Canvas force simulation:
- **GODMODE ALL NODES** acts as the central purple gravitational hub.
- **Project IDs** act as sub-hub anchors distributed radially in a circle.
- **Leaf nodes** (memory statements) are attracted to their parent hubs, forming dense stardust clouds (flower petals).
- **Labels** are hidden by default to prevent overlapping cluttered hairballs, fading in on mouse hover or node selection.
