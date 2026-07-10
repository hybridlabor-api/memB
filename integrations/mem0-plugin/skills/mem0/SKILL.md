---
name: memb
description: MemB SDK reference covering Python and TypeScript APIs, memory client methods, configuration, and framework integrations. Use when writing code that calls memb APIs, configuring memory providers, or integrating memb into an application.
license: Apache-2.0
metadata:
  author: membai
  version: "0.1.1"
  category: ai-memory
  tags: "memory, personalization, ai, python, typescript, vector-search"
compatibility: Requires Python 3.10+ or Node.js 18+, pip install membai or npm install membai, MEMB_API_KEY env var (Platform), and internet access to api.memb.ai. Uses MemB v3 API.
---

# MemB Platform Integration

> **Skill Graph:** This skill is part of the MemB skill graph:
> - **memb** (this skill) -- Platform Client SDK + OSS (Python + TypeScript)
> - **[memb-vercel-ai-sdk](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk)** -- Vercel AI SDK provider

MemB is a managed memory layer for AI applications. It stores, retrieves, and manages user memories via API — no infrastructure to deploy. For self-hosted usage, see the OSS section in the client references below.

## Step 1: Install and authenticate

**Python:**
```bash
pip install membai
export MEMB_API_KEY="m0-your-api-key"
```

**TypeScript/JavaScript:**
```bash
npm install membai
export MEMB_API_KEY="m0-your-api-key"
```

Get an API key at: https://app.memb.ai/dashboard/api-keys?utm_source=oss&utm_medium=memb-plugin-skill

> **Don't have a `MEMB_API_KEY`?** Sign up at https://app.memb.ai and create one from the dashboard. Keys start with `m0-`.

## Step 2: Initialize the client

**Python:**
```python
from memb import MemoryClient
client = MemoryClient(api_key="m0-xxx")
```

**TypeScript:**
```typescript
import MemoryClient from 'membai';
const client = new MemoryClient({ apiKey: 'm0-xxx' });
```

For async Python, use `AsyncMemoryClient`.

## Step 3: Core operations

Every MemB integration follows the same pattern: **retrieve → generate → store**.

### Add memories
```python
messages = [
    {"role": "user", "content": "I'm a vegetarian and allergic to nuts."},
    {"role": "assistant", "content": "Got it! I'll remember that."}
]
client.add(messages, user_id="alice")
```

### Search memories
```python
results = client.search("dietary preferences", filters={"user_id": "alice"})
for mem in results.get("results", []):
    print(mem["memory"])
```

### Get all memories
```python
all_memories = client.get_all(filters={"user_id": "alice"})
```

### Update a memory
```python
client.update("memory-uuid", text="Updated: vegetarian, nut allergy, prefers organic")
```

### Delete a memory
```python
client.delete("memory-uuid")
client.delete_all(user_id="alice")  # delete all for a user
```

## Common integration pattern

```python
from memb import MemoryClient
from openai import OpenAI

memb = MemoryClient()
openai = OpenAI()

def chat(user_input: str, user_id: str) -> str:
    # 1. Retrieve relevant memories
    memories = memb.search(user_input, filters={"user_id": user_id})
    context = "\n".join([m["memory"] for m in memories.get("results", [])])

    # 2. Generate response with memory context
    response = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": f"User context:\n{context}"},
            {"role": "user", "content": user_input},
        ]
    )
    reply = response.choices[0].message.content

    # 3. Store interaction for future context
    memb.add(
        [{"role": "user", "content": user_input}, {"role": "assistant", "content": reply}],
        user_id=user_id
    )
    return reply
```

## Common edge cases

- **Search returns empty:** v3 processes `add()` asynchronously — returns an event ID immediately. Wait 2-3s before searching. Also verify `user_id` matches exactly (case-sensitive) and use `filters={"user_id": "..."}` syntax.
- **AND filter with user_id + agent_id returns empty:** Entities are stored separately. `{"AND": [{"user_id": "alice"}, {"agent_id": "bot"}]}` returns nothing. Use `OR` instead, or query each separately.
- **Duplicate memories:** Don't mix `infer=True` (default) and `infer=False` for the same data. `infer=True` extracts facts via LLM with dedup. `infer=False` stores raw — same text can be stored twice.
- **Implicit null scoping:** `filters={"user_id": "alice"}` only returns memories where `agent_id`, `app_id`, `run_id` are ALL null. Wrap in `{"OR": [...]}` to include memories with non-null scoping fields.
- **Platform vs OSS imports:** Platform: `from memb import MemoryClient`. OSS: `from memb import Memory`. Don't mix them — `MemoryClient` talks to `api.memb.ai`, `Memory` runs locally.
- **v3 defaults:** `top_k=20`, `threshold=0.1`, `rerank=False`. Adjust as needed.

## v3 API (Current)

MemB v3 uses single-pass extraction, entity linking, and multi-signal retrieval.

**Key v3 changes from v2:**
- **Endpoints:** `POST /v3/memories/add/`, `POST /v3/memories/search/`, `POST /v3/memories/` (paginated list)
- **Extraction:** Single ADD-only pass — no more UPDATE/DELETE operations during extraction. Memories accumulate rather than consolidate.
- **Entity linking:** Replaces graph memory. Auto-extracted during `add()`, no config needed. Remove `enable_graph` and `graph_store` from any old config.
- **Defaults:** `top_k=20`, `threshold=0.1`, `rerank=False`
- **Removed params:** `org_id`, `project_id`, `enable_graph` — all removed from SDK
- **TypeScript:** Exclusively camelCase (`userId`, `agentId`, `appId`, `topK`)
- **Add response:** Async — returns event ID immediately, poll via `GET /v1/event/{event_id}/`

See the [migration guide](https://docs.memb.ai/migration/platform-v2-to-v3) for details.

## Live documentation search

For the latest docs beyond what's in the references, use the doc search tool:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/memb_doc_search.py --query "topic"
python ${CLAUDE_SKILL_DIR}/scripts/memb_doc_search.py --page "/platform/features/graph-memory"
python ${CLAUDE_SKILL_DIR}/scripts/memb_doc_search.py --index
```

No API key needed — searches docs.memb.ai directly.

## Client SDK References

Language-specific deep references (Platform + OSS):

| Language | File |
|----------|------|
| Python (MemoryClient + AsyncMemoryClient + Memory OSS) | [client/python.md](client/python.md) |
| TypeScript/Node.js (MemoryClient + Memory OSS) | [client/node.md](client/node.md) |
| Python vs TypeScript differences | [client/differences.md](client/differences.md) |

## Platform References

Load these on demand for deeper detail:

| Topic | File |
|-------|------|
| Quickstart (Python, TS, cURL) | [references/quickstart.md](references/quickstart.md) |
| SDK guide (all methods, both languages) | [references/sdk-guide.md](references/sdk-guide.md) |
| API reference (endpoints, filters, object schema) | [references/api-reference.md](references/api-reference.md) |
| Architecture (pipeline, lifecycle, scoping, performance) | [references/architecture.md](references/architecture.md) |
| Platform features (retrieval, graph, categories, MCP, etc.) | [references/features.md](references/features.md) |
| Framework integrations (LangChain, CrewAI, OpenAI Agents, etc.) | [references/integration-patterns.md](references/integration-patterns.md) |
| Use cases & examples (real-world patterns with code) | [references/use-cases.md](references/use-cases.md) |

## Related MemB Skills

| Skill | When to use | Link |
|-------|-------------|------|
| memb-vercel-ai-sdk | Vercel AI SDK provider with automatic memory | [GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk) |
