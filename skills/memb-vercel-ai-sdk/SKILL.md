---
name: memb-vercel-ai-sdk
description: >
  MemB provider for Vercel AI SDK (@memb/vercel-ai-provider).
  TRIGGER when: user mentions "vercel ai sdk", "@memb/vercel-ai-provider",
  "createMemB", "retrieveMemories", "addMemories", "getMemories",
  "searchMemories", "memb vercel", "AI SDK provider", "AI SDK memory",
  or is using generateText/streamText with memb. Also triggers for Next.js
  apps needing memory-augmented AI.
  DO NOT TRIGGER when: user asks about direct Python/TS SDK calls without Vercel
  (use memb skill), or CLI terminal commands (use memb-cli skill).
license: Apache-2.0
metadata:
  author: membai
  version: "1.1.0"
  category: ai-memory
  tags: "vercel, ai-sdk, memory, nextjs, typescript, provider"
compatibility: Node.js 18+, npm install @memb/vercel-ai-provider, Vercel AI SDK v5 (ai package), MEM0_API_KEY + LLM provider API key
---

# MemB Vercel AI SDK Provider

Memory-enhanced AI provider for Vercel AI SDK. Automatically retrieves and stores memories during LLM calls.

## Step 1: Install

```bash
npm install @memb/vercel-ai-provider ai
```

## Step 2: Set up environment variables

```bash
export MEM0_API_KEY="m0-xxx"
export OPENAI_API_KEY="sk-xxx"   # or ANTHROPIC_API_KEY, GOOGLE_API_KEY, etc.
```

Get a MemB API key at: https://app.memb.ai/dashboard/api-keys?utm_source=oss&utm_medium=skill-memb-vercel-ai-sdk

## Pattern 1: Wrapped Model

The wrapped model approach is the simplest. `createMemB` returns a provider that wraps any supported LLM with automatic memory retrieval and storage.

```typescript
import { generateText } from "ai";
import { createMemB } from "@memb/vercel-ai-provider";

const memb = createMemB();
const { text } = await generateText({
  model: memb("gpt-5-mini", { user_id: "alice" }),
  prompt: "Recommend a restaurant",
});
```

What happens under the hood:
1. The prompt is sent to MemB search (`POST /v3/memories/search/`) to retrieve relevant memories
2. Retrieved memories are injected as a system message at the start of the prompt
3. The underlying LLM (e.g., OpenAI gpt-5-mini) generates a response using the enriched prompt
4. The conversation is stored back to MemB (`POST /v3/memories/add/`) as a fire-and-forget async call (no await)

## Pattern 2: Standalone Utilities

Use standalone utilities when you want full control over the memory retrieve/store cycle, or you want to use a provider that is already configured separately.

```typescript
import { openai } from "@ai-sdk/openai";
import { generateText } from "ai";
import { retrieveMemories, addMemories } from "@memb/vercel-ai-provider";

const prompt = "Recommend a restaurant";

// Retrieve memories -- returns a formatted system prompt string
const memories = await retrieveMemories(prompt, {
  user_id: "alice",
  membApiKey: "m0-xxx",
});

// Generate using any provider with injected memories
const { text } = await generateText({
  model: openai("gpt-5-mini"),
  prompt,
  system: memories,
});

// Optionally store the conversation back
await addMemories(
  [
    { role: "user", content: [{ type: "text", text: prompt }] },
    { role: "assistant", content: [{ type: "text", text }] },
  ],
  { user_id: "alice", membApiKey: "m0-xxx" }
);
```

## Pattern 3: Streaming

Use `streamText` for streaming responses with memory augmentation:

```typescript
import { streamText } from "ai";
import { createMemB } from "@memb/vercel-ai-provider";

const memb = createMemB();
const result = streamText({
  model: memb("gpt-5-mini", { user_id: "alice" }),
  prompt: "What should I cook for dinner?",
});

for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

The wrapped model handles memory retrieval before streaming begins and stores the conversation after.

## Supported Providers

| Provider | Config value | Required env var |
|----------|-------------|------------------|
| OpenAI (default) | `"openai"` | `OPENAI_API_KEY` |
| Anthropic | `"anthropic"` | `ANTHROPIC_API_KEY` |
| Google | `"google"` | `GOOGLE_GENERATIVE_AI_API_KEY` |
| Groq | `"groq"` | `GROQ_API_KEY` |
| Cohere | `"cohere"` | `COHERE_API_KEY` |

Select a provider when creating the MemB instance:

```typescript
const memb = createMemB({ provider: "anthropic" });
const { text } = await generateText({
  model: memb("gpt-5-mini", { user_id: "alice" }),
  prompt: "Hello!",
});
```

## How It Works Internally

### Wrapped model flow

```
User prompt
  --> searchInternalMemories (POST /v3/memories/search/)
  --> memories injected as system message at start of prompt
  --> underlying LLM generates response (doGenerate or doStream)
  --> processMemories fires addMemories as fire-and-forget (no await)
  --> response returned to caller
```

### Standalone flow

```
User controls each step:
  1. retrieveMemories / getMemories / searchMemories -> fetch memories
  2. inject into system prompt manually
  3. call generateText / streamText with any provider
  4. addMemories -> store new conversation to MemB
```

## Key Differences Between the 4 Utility Functions

| Function | Returns | Use when |
|----------|---------|----------|
| `retrieveMemories` | Formatted system prompt **string** | Injecting directly into `system` parameter |
| `getMemories` | Raw memory **array** | Processing memories programmatically |
| `searchMemories` | Full search **response** (results + relations) | Need relations, scores, metadata |
| `addMemories` | API response | Storing new messages to MemB |

All four accept `LanguageModelV2Prompt | string` as the first argument and optional `MemBConfigSettings` as the second.

## Common Edge Cases and Tips

- **Always provide `user_id`** (or `agent_id`/`app_id`/`run_id`) for consistent memory retrieval. Without an entity identifier, memories cannot be scoped.
- **Standalone utilities require explicit API key**: pass `membApiKey` in the config object, or set the `MEM0_API_KEY` environment variable.
- **This uses Vercel AI SDK v5** (LanguageModelV2 / ProviderV2 interfaces). It is not compatible with AI SDK v3 or v4.
- **`processMemories` fires `addMemories` as fire-and-forget** (`.then()` without `await`). Memory storage happens asynchronously and does not block the LLM response.
- **The `"gemini"` alias** exists in the provider switch but is NOT in the `supportedProviders` list. Use `"google"` instead.
- **Custom host**: set `host` in the config to point to a different MemB API endpoint (default: `https://api.memb.ai`).

## References

| Topic | File |
|-------|------|
| Provider API (`createMemB`, `MemBProvider`, types) | [local](references/provider-api.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk/references/provider-api.md) |
| Memory utilities (`addMemories`, `retrieveMemories`, etc.) | [local](references/memory-utilities.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk/references/memory-utilities.md) |
| Usage patterns and examples | [local](references/usage-patterns.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk/references/usage-patterns.md) |

## Related MemB Skills

| Skill | When to use | Link |
|-------|-------------|------|
| memb | Python/TypeScript SDK, REST API, framework integrations | [local](../memb/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb) |
| memb-cli | Terminal commands, scripting, CI/CD, agent tool loops | [local](../memb-cli/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-cli) |
