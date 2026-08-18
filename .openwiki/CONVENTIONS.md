# 📋 memB – Development Conventions

This document defines coding standards, database schemas, and embedding invariants for **memB**.

---

## 🛠️ Python & Core Conventions

- **Runtime:** Python 3.10+
- **Embedding Invariants:** Use pre-quantized ONNX runtime model (`all-MiniLM-L6-v2`) outputting 384-dimensional float32 vectors. Never depend on remote embedding APIs.
- **Database Safety:** SQLite database transactions in `~/.MemBDB/` must be thread-safe with WAL mode enabled.
- **Zero Cloud Leakage:** All memory storage and vector search must execute 100% locally.

---

## 🌿 Git & Release Workflow

- **Branching:** Main branch `main` is production-ready.
- **Commit Messages:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- **SemVer:** Semantic version synchronization across `package.json` and release tags.
