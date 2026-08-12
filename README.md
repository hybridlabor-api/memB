![memB: Local Offline Long-Term Agentic Memory](header.png)

---

```text
██████╗ ██████╗ ██████╗      █████╗  ██████╗ ███████╗███╗   ██╗████████╗     ██████╗ ███████╗
██╔══██╗██╔══██╗██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝    ██╔═══██╗██╔════╝
██████╔╝██║  ██║██████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║       ██║   ██║███████╗
██╔══██╗██║  ██║██╔══██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║       ██║   ██║╚════██║
██████╔╝██████╔╝██████╔╝    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║       ╚██████╔╝███████║
╚═════╝ ╚═════╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝        ╚═════╝ ╚══════╝

                              L O C A L   M E M O R Y   E N G I N E
```

# 🚀 memB - Local Offline Long-Term Agentic Memory

[![CI](https://github.com/hybridlabor-api/memB/actions/workflows/ci.yml/badge.svg)](https://github.com/hybridlabor-api/memB/actions)
[![Version](https://img.shields.io/badge/version-2.2.1-blue.svg)](https://github.com/hybridlabor-api/memB)
[![runtime](https://img.shields.io/badge/python-3.10+-blue.svg)](https://github.com/hybridlabor-api/memB)
[![license](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![database](https://img.shields.io/badge/database-SQLite-brightgreen.svg)](https://github.com/hybridlabor-api/memB)

> **memB** is a private, custom-built long-term memory engine developed for the **Hybridlabor / BDB OS** ecosystem. Based on the open-source `memb` project, `memB` has been fully refactored, optimized for local resource efficiency without cloud dependency requirements, and designed for strict data privacy.

---

## 🎯 Overview

It acts as the persistent semantic brain for your agents, storing learned preferences, project-specific details, and system styling guidelines without leaking sensitive data to cloud database providers.

![Offline Pipeline Workflow](memb_offline_pipeline_sketch.jpg)

---

## 📚 Documentation Wiki

Comprehensive developer manuals and design specifications are maintained in the project's **OpenWiki** directory:
- 🏁 **[Quickstart Guide](.openwiki/quickstart.md):** Virtual environments setup, test suite execution, and visualizer server runs.
- 📐 **[System Architecture](.openwiki/architecture.md):** Tech stack, SQLite tables schemas, and God Mode memory queries.
- 🧠 **[Design Decisions Log](.openwiki/decisions.md):** Architecture trade-offs (ONNX vs PyTorch, NumPyFlat vs Qdrant, Canvas vs SVG).
- 📋 **[Release Notes](.openwiki/release_notes.md):** Version timeline and changelogs.

---

## 🔒 Security & Privacy Hardening (BDB Standards)

*   **Zero Telemetry:** Built from the ground up to ensure absolute data sovereignty, with no remote logging, tracking, or analytics endpoints present in the codebase.
*   **Plaintext Key Protection:** Includes a pre-ingestion filter that detects high-entropy strings (passwords, private keys, GCP/NPM tokens) and automatically redacts them (`[REDACTED_SECRET]`) or blocks ingestion entirely.
*   **Global Database Path:** Deployed database files and configurations are strictly bound to:
    - Deployed Environment: **`~/.MemBDB/memb.db`**
    - Local Dev Environment: `./test_memb.db` (isolated testing)

---

## 🧠 Architectural Highlights

### 1. Bundled Embedding Engine (Offline out-of-the-box)
*   **Natively Bundled Model:** Packages a pre-quantized 30MB **`all-MiniLM-L6-v2`** model file inside the repository assets (`memb/models/`).
*   **No Heavy Dependencies:** Avoids massive PyTorch (~1.5GB) installations. The Python backend extracts embeddings locally in milliseconds using a lightweight compilation of `onnxruntime` and HuggingFace `tokenizers`.
*   **Hybrid Reasoning:** Uses local vectors for similarity math while leveraging active Google Gemini API credentials (`gemma-4-31b-it` / `gemini-1.5-flash`) for logical memory extraction and reasoning.

### 2. Clustered "God Mode" Memory Layout
To prevent context pollution between different tasks (e.g., separating TouchDesigner scripts from React frontend patterns), `memB` models memory in a hierarchical flower-like node structure:

![God Mode Topology](memb_godmode_topology_sketch.jpg)

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

When an agent executes a search, the SQLite query automatically filters:
```sql
SELECT * FROM memb_vectors 
WHERE collection = :collection_name 
  AND (category = 'godmode' OR (category = :project_category AND project_id = :project_id))
```

---

## 📦 Installation

### Option A: Quick Install (via NPM/NPX)
The easiest way to install and configure memB globally is via our NPM installer:
```bash
npx -y @hybridlabor-api/memb@latest
```

### Option B: Local Development (Python)
Ensure you have Python 3.10+ installed.

### 2. Setup Virtual Environment
```bash
# Clone the private repository
git clone https://github.com/hybridlabor-api/memB.git
cd memB

# Initialize venv
python3 -m venv .venv
source .venv/bin/activate

# Install pruned requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run Verification Tests
Verify local embedding generation and SQLite flat vector search:
```bash
python test_memb.py
```

---

## 🔌 Model Context Protocol (MCP) & Multi-Agent Integration

`memB` exposes a standard, compliant Model Context Protocol (MCP) server. Because it conforms to the open MCP specification, **any compatible AI agent, editor plugin, or CLI developer assistant** (including Google Antigravity, Claude Code, Cursor, Windsurf, or Roo Cline) can register the `memB` server and interact with the following memory tools:

*   **`add_memory(text, user_id, metadata)`**: Extracts facts and inserts them into SQLite.
*   **`search_memory(query, user_id, limit, metadata)`**: Runs Cosine similarity searches on local vectors.
*   **`update_memory(memory_id, text)`**: Modifies a memory record.
*   **`delete_memory(memory_id)`**: Removes a memory.
*   **`list_memories(user_id, limit)`**: Lists registered facts.

### How to Configure across different Agents:

#### 1. Claude Code (CLI)
Add the server definition to `~/.claude.json`:
```json
{
  "mcpServers": {
    "memb-mcp": {
      "command": "python3",
      "args": ["/absolute/path/to/memB/run.py"]
    }
  }
}
```

#### 2. Cursor (Desktop IDE)
Go to **Settings ➔ Features ➔ MCP**:
1. Click **+ Add New MCP Server**.
2. Name: `memb-mcp`
3. Type: `command`
4. Command: `python3 /absolute/path/to/memB/run.py`

#### 3. Roo Cline / VS Code Extensions
Add to your global MCP configurations file (e.g. `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):
```json
{
  "mcpServers": {
    "memb-mcp": {
      "command": "python3",
      "args": ["/absolute/path/to/memB/run.py"],
      "disabled": false
    }
  }
}
```

---

## ⚙️ BDB OS Integration (v2.0.0+)

Starting in BDB OS v2.0.0 (`bdb-dev-optimized-antigravity-skills`), `memB` is integrated natively. 
The core BDB `installer.js` script clones `hybridlabor-api/memB` to your local environment, installs the dependencies, and registers the server inside your `mcp_config.json`:

```json
{
  "mcpServers": {
    "memb-mcp": {
      "command": "python3",
      "args": ["~/.gemini/antigravity-cli/mcp/memb-mcp/run.py"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}",
        "MEMB_DATA_DIR": "~/.MemBDB"
      }
    }
  }
}
```

---

## ⚖️ License

Private repository under BDB/Hybridlabor proprietary license. All rights reserved.
