# 🧠 Technical Design Decisions

This log documents key architecture trade-offs, decisions, and system constraints adopted during `memB` development.

---

## 1. Local ONNX Embeddings vs. PyTorch

*   **Decision:** Use `onnxruntime` + HuggingFace `tokenizers` instead of standard `sentence-transformers` (which depends on PyTorch).
*   **Rationale:** Installing PyTorch consumes roughly 1.5GB of disk space and slows down installation runs significantly. The pre-quantized 30MB ONNX model file achieves identical semantic similarity scores while running within a fraction of the memory footprint.
*   **Result:** Deployed virtual environments remain lightweight and performant on both high-end Macs and low-spec developer systems.

---

## 2. Flat SQLite Vector Store vs. Server Databases (Qdrant/Milvus)

*   **Decision:** Build a custom `NumPyFlat` store inside SQLite (`memb_vectors` table) instead of running Qdrant or Milvus in a Docker container.
*   **Rationale:** Requiring a running Docker container introduces setup friction, background daemon overhead, and path resolving risks across platforms (especially Windows vs macOS). SQLite is pre-installed on all systems, writes directly to user folders, and is exceptionally stable.
*   **Result:** Local flat vector search on a few thousand nodes takes less than 2 milliseconds, making a server database unnecessary for local desktop agent memory scales.

---

## 3. HTML5 Canvas vs. SVG for Graph Visualization

*   **Decision:** Transition the visualizer dashboard from SVG D3.js elements to an HTML5 Canvas-based renderer.
*   **Rationale:** SVG DOM node limits cause noticeable lag once the graph grows beyond 200 nodes. Canvas 2D context handles batch draws and degree-dependent layout calculations efficiently, allowing smooth 60 FPS panning, zooming, and physics ticks for up to 5,000 nodes.
*   **Result:** Seamless transition from zoomed-out dense stardust clusters to detail sidebar inspectors.
