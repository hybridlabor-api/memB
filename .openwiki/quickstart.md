# 🏁 memB Quickstart Guide

Welcome to the **memB** development setup guide. `memB` is a 100% offline-first, local long-term memory engine integrated with BDB OS.

---

## 🛠️ Prerequisites

- Python 3.10 or higher
- SQLite3
- Recommended: `pip` or `uv` package manager

---

## 🚀 Local Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/hybridlabor-api/memB.git
   cd memB
   ```

2. **Initialize Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   *Note: This automatically downloads and configures the `numpy_flat` vector database store and local ONNX embedding engines.*

---

## 🧪 Testing the Database Core

To verify that the offline vector store and local ONNX embedding models are working correctly:

```bash
python3 test_memb.py
```

Expected output:
```
=== Testing memB offline core ===
Initializing Memory engine...
Testing local ONNX embedder directly...
Embedding success. Dimensions: 384
Testing NumPyFlat insert...
Insert success.
Testing NumPyFlat search...
Search results count: 1
Match: ID=test-id-1, Score=1.0, Payload={'text': 'This is a BDB test string', 'category': 'godmode'}
=== memB test passed successfully ===
```

---

## 🎨 Running the Graph Visualizer

To run the interactive Orca-style D3.js Canvas graph visualizer locally:

```bash
# Start the FastAPI visualizer server and mount the frontend
./start.sh
```

Open your browser and navigate to:
👉 **[http://localhost:8088](http://localhost:8088)**

---

## ⚙️ Configuration (.env)

Define your environment variables in a `.env` file at the root of your project or in your system path.

```env
# Optional LLM API keys for memory extraction
OPEN_AI_KEY=<YOUR_OPENAI_KEY>
GEMINI_API_KEY=<YOUR_GEMINI_KEY>

# Custom SQLite database paths
MEMB_DIR=~/.MemBDB
```
