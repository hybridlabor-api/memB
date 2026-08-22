# 📜 memB – Changelog

All notable changes to **memB** are documented in this file in accordance with [Keep a Changelog](https://keepachangelog.com/).

---

## [2.3.0] - 2026-08-22

### Added
- **SQLite WAL Mode & Hardening**: Concurrent thread-safe database access (`PRAGMA journal_mode = WAL;`, `busy_timeout = 30000`).
- **FTS5 BM25 Hybrid Search**: Full-text token and keyword indexing with BM25 ranking and 1.25x hybrid boost.
- **8-Tool FastMCP Surface**: Full tool suite (`add_memory`, `search_memory`, `get_memory`, `update_memory`, `list_memories`, `delete_memory`, `delete_all_memories`, `list_entities`).
- **SHA-256 Deduplication**: Cross-run MD5/SHA-256 chunk hash detection preventing duplicate embeddings.
- **17 Memory Scopes & Taxonomy**: Complete classification hierarchy across architectural and developer domains.

---

## [2.2.2] - 2026-08-18

### Added
- Standardized NPM packaging and root distribution workflow (`@hybridlabor-api/memb`).
- Standardized OpenWiki documentation suite.
- Enhanced CI/CD workflows and automated release tagging.

### Fixed
- Fixed NPM token authorization and packaging guards.

---

## [2.2.0] - 2026-08-01

### Added
- Hierarchical God Mode memory retrieval (global preferences + project-specific context).
- D3.js interactive stardust force graph memory visualizer.
- SQLite-backed fast flat vector indexing with pre-quantized ONNX embeddings.
