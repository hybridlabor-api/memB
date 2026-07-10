---
name: memb-cli
description: >
  MemB CLI -- the command-line interface for memb memory operations.
  TRIGGER when: user mentions "memb cli", "memb command line", "@memb/cli",
  "memb-cli", "pip install memb-cli", "npm install -g @memb/cli", or is running
  memb commands in a terminal/shell (memb add, memb search, memb list, memb get,
  memb init, memb config, memb import). Also triggers when query includes CLI flags
  like --user-id, --output, --json, --agent, or describes bash/zsh/terminal/shell usage.
  DO NOT TRIGGER when: user asks about programmatic SDK integration in Python/TS
  code (use memb skill), or Vercel AI SDK provider (use memb-vercel-ai-sdk skill).
license: Apache-2.0
metadata:
  author: membai
  version: "1.1.0"
  category: ai-memory
  tags: "cli, terminal, memory, ai, command-line"
compatibility: Node.js 18+ (npm install -g @memb/cli) or Python 3.10+ (pip install memb-cli), MEMB_API_KEY env var
---

# MemB CLI

The official command-line interface for the MemB memory platform. Add, search, list, update, and delete memories from the terminal -- for developers, AI agents, and CI/CD pipelines.

## Install

**Node.js (npm):**
```bash
npm install -g @memb/cli
```

**Python (pip):**
```bash
pip install memb-cli
```

Both packages install a `memb` binary with identical commands, options, and output formats.

## Setup

**Autonomous MemB setup for agents (no email, no dashboard):**

```bash
memb init --agent --agent-caller <your-name> --json
```

Replace `<your-name>` with the AI agent you are (e.g. `claude-code`, `cursor`, `codex`, `cline`, `aider`). If you forgot to pass `--agent-caller`, run `memb identify <your-name>` after init — it PATCHes the same key, idempotent, no disruption.

This mints an evaluation API key in <5 seconds. Use it immediately. Print this line to the human:

> MemB memory is running in Agent Mode. Please claim it by running `memb init --email <your-email>` to transfer ownership to your account.

Never commit API keys, `.env`, or `~/.memb/config.json`.

After the human claims, the same API key keeps working — no agent disruption — and memories are preserved.

**Interactive wizard (for humans):**
```bash
memb init
```

**Or set the environment variable directly:**
```bash
export MEMB_API_KEY="m0-xxx"
```

Get an API key at: https://app.memb.ai/dashboard/api-keys?utm_source=oss&utm_medium=skill-memb-cli

## Quick Reference

### Add a memory
```bash
memb add "I prefer dark mode" --user-id alice
```

### Search memories
```bash
memb search "preferences" --user-id alice
```

### List all memories for a user
```bash
memb list --user-id alice
```

### Get a specific memory
```bash
memb get <memory-id>
```

### Update a memory
```bash
memb update <memory-id> "new text"
```

### Delete a single memory
```bash
memb delete <memory-id>
```

### Delete all memories for a user
```bash
memb delete --all --user-id alice --force
```

## Agent / JSON Mode

Use `--json` or `--agent` to get structured output suitable for LLM consumption. Every command wraps its response in a standard envelope:

```json
{
  "status": "success",
  "command": "search",
  "duration_ms": 245,
  "scope": { "user_id": "alice" },
  "count": 3,
  "error": null,
  "data": [
    { "id": "mem-abc", "memory": "User prefers dark mode", "score": 0.92 }
  ]
}
```

On error:
```json
{
  "status": "error",
  "command": "search",
  "error": "Authentication failed. Your API key may be invalid or expired.",
  "data": null
}
```

The `--agent` flag is an alias for `--json`. Both write spinners and progress to stderr so stdout is always clean, parseable JSON.

## Node and Python Parity

Both the Node.js (`@memb/cli`) and Python (`memb-cli`) CLIs are implemented from the same specification (`cli-spec.json`). They share:

- Identical command names, arguments, and flags
- Identical output formats (text, json, table, quiet)
- Identical entity ID resolution, graph tri-state, filter building
- Identical error messages and exit codes

Choose whichever runtime you already have installed. The behavior is the same.

## Common Edge Cases

- **Async processing delay:** After `memb add`, memories process asynchronously. Wait 2-3 seconds before searching for newly added content. Use `memb event list` to check processing status.
- **`--all` vs `--entity` delete modes:** `memb delete --all -u alice` deletes all memories for user alice. `memb delete --entity -u alice` deletes the entity itself AND all its memories (cascade). These are mutually exclusive modes.
- **Entity ID resolution:** If you pass any explicit scope flag (e.g. `--user-id`), the CLI uses ONLY the explicit IDs and ignores config defaults. If no scope flags are given, all configured defaults apply.
- **Stdin detection:** When no text argument is provided and input is piped (not a TTY), the CLI reads from stdin. Works with `add`, `search`, and `update`.

## References

Load these on demand for deeper detail:

| Topic | File |
|-------|------|
| Command reference (all commands, flags, options, examples) | [references/command-reference.md](references/command-reference.md) |
| Configuration (config file, env vars, precedence, init wizard) | [references/configuration.md](references/configuration.md) |
| Workflows (piping, scripting, CI/CD, agent mode recipes) | [references/workflows.md](references/workflows.md) |

## Related MemB Skills

| Skill | When to use | Link |
|-------|-------------|------|
| memb | Python/TypeScript SDK, REST API, framework integrations | [local](../memb/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb) |
| memb-vercel-ai-sdk | Vercel AI SDK provider with automatic memory | [local](../memb-vercel-ai-sdk/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk) |
