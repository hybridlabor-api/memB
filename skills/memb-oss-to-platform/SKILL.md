---
name: memb-oss-to-platform
description: >-
  Plan and then execute a migration of a project from the memb open-source / self-hosted SDK
  (the local `Memory` class) to the memb Platform / hosted / managed SDK (the `MemoryClient`
  class). Use this whenever a developer wants to move, switch, or migrate their memb usage off
  OSS/self-hosted to the hosted API — e.g. "migrate my memb setup to the platform", "switch from
  self-hosted memb to MemoryClient", "use my memb API key instead of a local Qdrant", "move memb
  to the cloud/hosted/managed service", or "replace my local memb vector store + embedder config
  with the platform". Applies to Python (`from memb import Memory` → `from memb import MemoryClient`)
  and TypeScript/JavaScript (`import { Memory } from "membai/oss"` → `import MemoryClient from "membai"`).
  Trigger even when the user doesn't say the word "migrate" but clearly wants their existing memb
  integration to run against the hosted platform. It first produces a reviewable migration plan,
  then executes it after the developer approves. Strictly scoped to the memb integration — it does
  not refactor, restructure, or "improve" any unrelated code.
---

# Migrate memb OSS → memb Platform (hosted)

This skill migrates a project's memory layer from the **self-hosted memb OSS SDK** to the
**hosted memb Platform SDK**, working for any project shape — an agent, a RAG pipeline, an API
service, a chatbot, a background worker. You discover where memb is actually used, write a plan the
developer reviews, and then execute it on approval.

## The mental model (read this first — it's why the migration is shaped the way it is)

OSS memb means **the developer runs the whole memory stack themselves**: a vector store
(Qdrant/pgvector/Chroma/…), an embedder, an LLM for fact extraction, and a local history DB. All of
that is wired up in a config object passed to `Memory`.

The Platform means **memb runs that stack for them**. The developer just holds an **API key**. So
the migration is mostly *subtraction*: the local infrastructure config collapses into a single
`MemoryClient(api_key=...)`. The method calls stay recognizable (`add`/`search`/`get_all`/…), but a
few parameter conventions tighten up and the return values are server responses.

So the core of every migration is:
1. `Memory` / `Memory.from_config({...})` → `MemoryClient()` (reads the API key from the env).
2. Delete the local `vector_store` / `llm` / `embedder` / `graph_store` / `history_db_path` config.
3. Fix up each call site to the hosted call convention (entity IDs into `filters`, pagination, etc.).
4. Flag everything that *isn't* a clean 1:1 so the developer can decide (see `references/gotchas.md`).

**Scope discipline:** touch only memb-related code, config, dependencies, and env. Preserve the
project's existing behavior, structure, and style. Do not rename things, "tidy" nearby code, or
change the app's logic. The developer asked to swap a backend, not to refactor their project.

## Workflow

Work through these phases in order. Phases 1–4 produce the plan; phase 5 runs only after approval.

### Phase 0 — Prerequisite check
The hosted SDK needs a memb API key (`MEMB_API_KEY`, obtainable at https://app.memb.ai). Confirm
the developer has one. You don't need the key value to write the plan, but flag in the plan that it
must be set (in `.env` / secrets manager, never hardcoded) before execution and verification.

### Phase 1 — Discover the memb footprint
Do not assume the layout. Find every place memb appears. Detect the language and the **installed**
version first, then sweep for usage. Concretely, search for:
- **Imports / instantiation:** `from memb import Memory`, `Memory.from_config`, `Memory(`,
  `import ... from "membai"`, `from "membai/oss"`, `new Memory(`.
- **Config blocks:** keys like `vector_store`/`vectorStore`, `embedder`, `llm`, `graph_store`/
  `graphStore`, `history_db_path`, `historyStore`, `custom_fact_extraction_prompt`,
  `custom_update_memory_prompt`, `enable_graph`.
- **Every call site:** `.add(`, `.search(`, `.get_all(`/`.getAll(`, `.delete_all(`/`.deleteAll(`,
  `.get(`, `.update(`, `.delete(`, `.reset(`, `.history(`.
- **Dependencies & env:** `requirements.txt`/`pyproject.toml`/`package.json` for `membai` and any
  local-infra deps that exist *only* for memb (e.g. `qdrant-client`, `chromadb`); `.env`/config for
  things like `OPENAI_API_KEY` used by the local embedder/LLM; any docker-compose service (e.g. a
  Qdrant container) that exists only to back memb.

Use Grep/Glob broadly; a single missed call site is a runtime break later. Record `file:line` for
each finding — the plan's inventory is built from this.

### Phase 2 — Verify the API against the installed SDK (don't guess)
Versions drift, and the OSS and hosted classes have subtly different signatures. Before mapping,
confirm the **real** signatures of the installed package rather than trusting memory:
- **Python:** `python -c "import inspect; from memb import MemoryClient; print(inspect.signature(MemoryClient.search))"`
  for each method you'll touch, and read the installed source under
  `site-packages/memb/client/main.py` if anything is ambiguous (e.g. whether a method *rejects*
  top-level entity params). Also check the OSS side the project currently uses.
- **TypeScript:** read the installed types/dist under `node_modules/membai/` to confirm option names
  (`limit` vs `topK`, `userId` vs a nested `filters`) and the default vs `membai/oss` export.

This verification step is the single most important habit — it's what keeps the plan correct across
memb versions. Then consult `references/api-mapping.md` for the OSS→hosted translation of each
method (Python and TypeScript), and the official guide at https://docs.memb.ai/migration/oss-v2-to-v3.

### Phase 3 — Map each site and flag the gaps
For every call site and config block from Phase 1, determine the hosted equivalent using the
mapping. Most calls map cleanly. Some don't — and those matter more than the mechanical edits.
Read `references/gotchas.md` and flag anything that needs a human decision: self-hosted/data-
residency setups, local model choices moving server-side, graph-memory usage, custom prompts, hot-
path calls that now make network round-trips, and **existing locally-stored memories not carrying
over** (data migration is out of scope unless the developer asks — note it, don't silently attempt it).

### Phase 4 — Write the plan and stop
Write the full plan to `MEMB_MIGRATION_PLAN.md` at the repo root, following the structure in
`references/plan-template.md`. It must be concrete enough to execute from and honest about the gaps.
Then **stop and present it for review.** Do not start editing code in the same turn — the whole
point is that the developer reads and approves the plan first.

### Phase 5 — Execute on approval (guided)
Once the developer approves (they may ask for changes first — incorporate them), execute the plan:
- Make the edits file by file, staying strictly within memb scope.
- Update dependencies and env (`MEMB_API_KEY`; remove now-dead local-infra deps/services only if
  they exist solely for memb and you're confident).
- **Verify**, mirroring how you'd confirm any backend swap:
  - It imports / type-checks / byte-compiles.
  - A smoke test exercises `add` → `search`/`get_all` → `delete_all` against the hosted API with a
    real `MEMB_API_KEY`, and the app's own entry point still runs.
  - No local memb storage directory gets created anymore (e.g. a `.memb/`, local Qdrant path) —
    proof the memory really lives on the platform now.
- Report what changed, what was verified, and any flagged concerns the developer still needs to act
  on (e.g. configuring custom instructions in the dashboard, migrating old data).

## Reference files
- `references/api-mapping.md` — exact OSS→hosted method/param/return mapping for Python and
  TypeScript, plus dependency and env changes. Read during Phase 2–3.
- `references/gotchas.md` — the things that aren't a clean 1:1 and need a human decision. Read
  during Phase 3 so the plan's "Concerns" section is complete.
- `references/plan-template.md` — the exact structure for `MEMB_MIGRATION_PLAN.md`. Use in Phase 4.
