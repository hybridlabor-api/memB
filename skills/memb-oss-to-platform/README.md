# memb-oss-to-platform — Pipeline Skill

Migrate a project from the MemB Open Source (self-hosted) SDK to the MemB Platform (hosted) SDK, end to end. The skill audits where MemB is used, writes a reviewable migration plan, and executes it after you approve.

> **This is a pipeline skill, not a reference skill.** Invoke it when you want your agent to migrate an existing project's MemB integration from OSS to the Platform. For day-to-day SDK coding help, install [`memb`](../memb/SKILL.md) instead.
>
> **Part of the MemB Skill Graph:**
> - Reference: [memb](../memb/SKILL.md) · [memb-cli](../memb-cli/SKILL.md) · [memb-vercel-ai-sdk](../memb-vercel-ai-sdk/SKILL.md)
> - Pipeline: [memb-integrate](../memb-integrate/SKILL.md) → [memb-test-integration](../memb-test-integration/SKILL.md) · **memb-oss-to-platform** (this skill)

## What This Skill Does

When invoked, your assistant will:

- **Discover** every place MemB is used in the project — imports, client init, config blocks, call sites, dependencies, env, and local infra
- **Verify** the exact API against the installed SDK rather than guessing
- **Map** each OSS `Memory` usage to its hosted `MemoryClient` equivalent (Python and TypeScript)
- **Flag** everything that isn't a clean 1:1 and needs a human decision
- **Write** a reviewable `MEMB_MIGRATION_PLAN.md`, then **execute it after you approve** — strictly scoped to the MemB integration, with no unrelated refactors

## When to Use

Trigger phrases:

- "Migrate my MemB setup to the Platform"
- "Switch from self-hosted MemB to MemoryClient"
- "Use my MemB API key instead of a local Qdrant"
- "Move MemB to the hosted/managed service"

Do **not** use this skill for general SDK usage (install [`memb`](../memb/SKILL.md)), or to add MemB to a repo that doesn't use it yet (use [`memb-integrate`](../memb-integrate/SKILL.md)).

## Installation

### CLI (Claude Code, Codex, OpenCode, OpenClaw, or any tool that supports skills)

```bash
npx skills add https://github.com/membai/memb --skill memb-oss-to-platform
```

### Claude.ai

1. Download this `skills/memb-oss-to-platform` folder as a ZIP
2. Go to **Settings > Capabilities > Skills**
3. Click **Upload skill** and select the ZIP

### Claude API (Skills API)

```bash
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "memb-oss-to-platform", "source": "https://github.com/membai/memb/tree/main/skills/memb-oss-to-platform"}'
```

### Prerequisites

- A MemB Platform API key ([get one](https://app.memb.ai/dashboard/api-keys))
- An existing project that uses the MemB OSS SDK

## Workflow

```
(invoke skill)  →  audits the repo's MemB usage,
                   writes MEMB_MIGRATION_PLAN.md,
                   stops for your review
(approve)       →  executes the plan and verifies
                   (compile/import, real-API smoke test)
```

## Links

- [MemB Platform Dashboard](https://app.memb.ai)
- [MemB Documentation](https://docs.memb.ai)
- [OSS → Platform migration guide](https://docs.memb.ai/migration/oss-v2-to-v3)
- [Platform vs OSS comparison](https://docs.memb.ai/platform/platform-vs-oss)

## License

Apache-2.0
