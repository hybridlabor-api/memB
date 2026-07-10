# memb-integrate — Pipeline Skill

Wire [MemB](https://memb.ai) into an existing repository end-to-end, using a goal-driven, test-first pipeline.

> **This is a pipeline skill, not a reference skill.** Invoke it as `/memb-integrate` when you want your assistant to do the work of integrating MemB into a target repo. For day-to-day SDK coding help, install [`memb`](../memb/SKILL.md) instead.
>
> **Part of the MemB Skill Graph:**
> - Reference: [memb](../memb/SKILL.md) · [memb-cli](../memb-cli/SKILL.md) · [memb-vercel-ai-sdk](../memb-vercel-ai-sdk/SKILL.md)
> - Pipeline: **memb-integrate** (this skill) → [memb-test-integration](../memb-test-integration/SKILL.md)

## What This Skill Does

When invoked, your assistant will:

- **Detect** the target repo's language and stack automatically
- **Ask** whether to integrate with MemB Platform (managed) or MemB Open Source (self-hosted)
- **Write failing tests first** — no implementation until tests exist
- **Keep the integration additive and feature-flagged** — existing behavior stays byte-for-byte identical when the flag is unset
- **Produce a local feature branch** (`memb-integrate/...`) and a `.memb-integration/` directory of artifacts (`goal.md`, `plan.md`, `product.json`) consumed by the companion verification skill

## When to Use

Trigger phrases:

- "Integrate MemB into this repo"
- "Add MemB to my project"
- "Wire MemB into `<repo>`"
- "How do I add memory to an existing project?"

Do **not** use this skill for general SDK usage (install [`memb`](../memb/SKILL.md)), terminal workflows (install [`memb-cli`](../memb-cli/SKILL.md)), or Vercel AI SDK integration (install [`memb-vercel-ai-sdk`](../memb-vercel-ai-sdk/SKILL.md)).

## Installation

### CLI (Claude Code, Codex, OpenCode, OpenClaw, or any tool that supports skills)

```bash
npx skills add https://github.com/membai/memb --skill memb-integrate
```

For verification on the same branch, also install the companion skill:

```bash
npx skills add https://github.com/membai/memb --skill memb-test-integration
```

### Claude.ai

1. Download this `skills/memb-integrate` folder as a ZIP
2. Go to **Settings > Capabilities > Skills**
3. Click **Upload skill** and select the ZIP

### Claude API (Skills API)

```bash
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "memb-integrate", "source": "https://github.com/membai/memb/tree/main/skills/memb-integrate"}'
```

### Prerequisites

- A MemB Platform API key ([get one](https://app.memb.ai/dashboard/api-keys)) *or* a working OSS setup (LLM + vector store)
- Python 3.10+ or Node.js 18+ in the target repo
- A clean working tree on the target repo's default branch

## Workflow

```
/memb-integrate          →  creates memb-integrate/<slug> branch,
                            writes .memb-integration/ artifacts,
                            implements against failing tests
/memb-test-integration   →  runs the repo's native test suite,
                            executes a real end-to-end smoke flow,
                            produces a scorecard
```

The two skills are loosely coupled — they share the same workspace and branch via `.memb-integration/`, but the verifier never modifies source.

## Links

- [MemB Platform Dashboard](https://app.memb.ai)
- [MemB Documentation](https://docs.memb.ai)
- [MemB GitHub](https://github.com/membai/memb)
- [Platform vs OSS comparison](https://docs.memb.ai/platform/platform-vs-oss)

## License

Apache-2.0
