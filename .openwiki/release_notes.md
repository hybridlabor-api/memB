# 📋 memB Release Notes

Changelog and development progress tracker for **memB**.

---

## 🚀 Version 1.0.0 (July 11, 2026)

First major stable release of `memB` as a local, whitelabeled long-term memory engine integrated with BDB OS.

### 🌟 Key Features

*   **100% Local Embeddings:** Integrated `local_onnx` provider utilizing `all-MiniLM-L6-v2` ONNX model. Generates embeddings locally without cloud fees or latency.
*   **Custom NumPyFlat SQLite Store:** Built a robust SQLite-backed flat vector database mapping vectors directly to `~/.MemBDB/memb.db`.
*   **Zero Telemetry:** Removed all remote event tracking, analytics, and telemetry to enforce total privacy and data sovereignty.
*   **Symmetric Flower Graph Visualizer:** Created a high-performance HTML5 Canvas + D3.js web visualizer at `http://localhost:8088`. Displays memories arranged symmetrically in a flower cluster layout with hover triggers and sidebar inspectors.
*   **Plaintext Credentials Redaction:** Hardened security rules to automatically redact high-entropy keys and passwords before memory ingestion occurs.

---

## 🛠️ Upcoming Plans

- Support for local LLM extraction pipelines using Ollama (running completely offline without Gemini/OpenAI).
- Project name mapping configs to customize dynamic folder basenames.
- Automated snapshot exports and backup tasks.
