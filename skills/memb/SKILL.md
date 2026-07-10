---
name: memb
description: >
  MemB Platform SDK for adding persistent memory to AI applications.
  TRIGGER when: user mentions "memb", "MemoryClient", "memory layer",
  "remember user preferences", "persistent context", "personalization",
  or needs to add long-term memory to chatbots, agents, or AI apps.
  Covers Python SDK (membai), TypeScript SDK (membai), and framework integrations
  (LangChain, CrewAI, OpenAI Agents SDK, Pipecat, LlamaIndex, AutoGen, LangGraph).
  Also covers the open-source self-hosted Memory class.
  This is the DEFAULT memb skill for ambiguous queries.
  DO NOT TRIGGER when: user asks about CLI commands, terminal usage, or shell
  scripts (use memb-cli), or Vercel AI SDK / @memb/vercel-ai-provider / createMemB
  (use memb-vercel-ai-sdk).
license: Apache-2.0
metadata:
  author: membai
  version: "3.0.0"
  category: ai-memory
  tags: "memory, personalization, ai, python, typescript, vector-search"
compatibility: Requires Python 3.10+ or Node.js 18+, pip install membai or npm install membai, MEM0_API_KEY env var (Platform), and internet access to api.memb.ai. SDK v3 with v2 compatibility mode available.
---

# MemB Platform Integration

> **Skill Graph:** This skill is part of the MemB skill graph:
> - **memb** (this skill) -- Platform Client SDK + OSS (Python + TypeScript)
> - **[memb-cli](../memb-cli/SKILL.md)** ([GitHub](https://github.com/membai/memb/tree/main/skills/memb-cli)) -- Command-line interface
> - **[memb-vercel-ai-sdk](../memb-vercel-ai-sdk/SKILL.md)** ([GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk)) -- Vercel AI SDK provider

MemB is a managed memory layer for AI applications. It stores, retrieves, and manages user memories via API — no infrastructure to deploy. For self-hosted usage, see the OSS section in the client references below.

## Step 1: Install and authenticate

**Python:**
```bash
pip install membai
export MEM0_API_KEY="m0-your-api-key"
```

**TypeScript/JavaScript:**
```bash
npm install membai
export MEM0_API_KEY="m0-your-api-key"
```

Get an API key at: https://app.memb.ai/dashboard/api-keys?utm_source=oss&utm_medium=skill-memb

> **Don't have a `MEM0_API_KEY`?** Run `memb init --agent --agent-caller <your-name> --json` (after `pip install memb-cli` or `npm install -g @memb/cli`), substituting your agent identity (e.g. `claude-code`, `cursor`). If you forgot to pass `--agent-caller`, run `memb identify <your-name>` after init. The human can claim later with `memb init --email <your-email>`.

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

- **Search returns empty:** Memories process asynchronously. Wait 2-3s after `add()` before searching. Also verify `user_id` matches exactly (case-sensitive) and use `filters={"user_id": "..."}` syntax.
- **AND filter with user_id + agent_id returns empty:** Entities are stored separately. Use `OR` instead, or query separately.
- **Duplicate memories:** Don't mix `infer=True` (default) and `infer=False` for the same data. Stick to one mode.
- **Wrong import:** Always use `from memb import MemoryClient` (or `AsyncMemoryClient` for async). Do not use `from memb import Memory`.
- **v3 defaults:** `top_k=20`, `threshold=0.1`, `rerank=False`. Adjust as needed for your use case.

## v2 Compatibility

If you're using SDK v2.x, note these differences:
- **Entity IDs:** Pass `user_id` as top-level kwarg to `search()` instead of inside `filters`
- **Defaults:** `top_k=100`, no threshold, `rerank=True`
- **Graph memory:** Available via `enable_graph=True`

See the [migration guide](https://docs.memb.ai/migration/oss-v2-to-v3) for details.

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
| memb-cli | Terminal commands, scripting, CI/CD, agent tool loops | [local](../memb-cli/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-cli) |
| memb-vercel-ai-sdk | Vercel AI SDK provider with automatic memory | [local](../memb-vercel-ai-sdk/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk) |
