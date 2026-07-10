# MemB Skills for AI Coding Assistants

MemB ships structured skill definitions for Claude Code, Codex, Cursor, OpenCode, OpenClaw, and any assistant that supports the [skills standard](https://github.com/anthropic-experimental/skills). Skills teach the assistant how to work with MemB — either by loading SDK knowledge into context, or by executing an end-to-end workflow on demand.

## Two Categories

### Reference skills — always on

Installed once, loaded into context so the assistant writes correct MemB code. Use these for day-to-day development.

| Skill | Surface | Install |
|-------|---------|---------|
| [`memb`](./memb/) | Python + TypeScript SDKs (Platform + OSS), framework integrations | `npx skills add https://github.com/membai/memb --skill memb` |
| [`memb-cli`](./memb-cli/) | Terminal workflows (`memb` CLI, both Node and Python) | `npx skills add https://github.com/membai/memb --skill memb-cli` |
| [`memb-vercel-ai-sdk`](./memb-vercel-ai-sdk/) | `@memb/vercel-ai-provider` and `createMemB` | `npx skills add https://github.com/membai/memb --skill memb-vercel-ai-sdk` |

### Pipeline skills — run on demand

Invoked as a slash command to execute a specific end-to-end workflow. These do real work: they create branches, write tests, run code.

| Skill | Trigger | Install |
|-------|---------|---------|
| [`memb-integrate`](./memb-integrate/) | `/memb-integrate` — wire MemB into an existing repo via TDD | `npx skills add https://github.com/membai/memb --skill memb-integrate` |
| [`memb-test-integration`](./memb-test-integration/) | `/memb-test-integration` — verify what `/memb-integrate` produced | `npx skills add https://github.com/membai/memb --skill memb-test-integration` |
| [`memb-oss-to-platform`](./memb-oss-to-platform/) | `/memb-oss-to-platform` — migrate a project from MemB OSS to the hosted Platform SDK | `npx skills add https://github.com/membai/memb --skill memb-oss-to-platform` |

The `memb-integrate` and `memb-test-integration` skills are designed to run in sequence on the same workspace:

```
/memb-integrate          →  memb-integrate/<slug> branch + .memb-integration/ artifacts
/memb-test-integration   →  scorecard (compile + runtime verification, real API smoke test)
```

## Choosing a Skill

- **Writing MemB code in a new or existing project?** → `memb`
- **Using the terminal CLI?** → `memb-cli`
- **Building with `@ai-sdk/*`?** → `memb-vercel-ai-sdk`
- **Want the assistant to wire MemB into an existing repo for you?** → `memb-integrate`, then `memb-test-integration`
- **Already using MemB OSS and want to move to the hosted Platform?** → `memb-oss-to-platform`

## Links

- [Vibecoding with MemB](https://docs.memb.ai/vibecoding) — canonical landing page
- [Claude Code integration](https://docs.memb.ai/integrations/claude-code)
- [MemB Platform Dashboard](https://app.memb.ai)
- [MemB Documentation](https://docs.memb.ai)

## License

Apache-2.0
