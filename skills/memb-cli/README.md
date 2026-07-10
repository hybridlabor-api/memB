# MemB CLI Skill for Claude

Manage memories from the terminal using the [MemB CLI](https://docs.memb.ai/cli). This skill teaches Claude how to use every `memb` command, flag, and output mode -- for both the Node.js and Python implementations.

## What This Skill Does

When installed, Claude can:

- **Run memb commands** correctly in your terminal (add, search, list, get, update, delete, import, config, init, status, entity, event)
- **Construct complex invocations** with the right flags, scoping, filters, and output formats
- **Pipe and script** memb commands in shell workflows, CI/CD pipelines, and agent loops
- **Debug issues** like missing API keys, entity scoping conflicts, and async processing delays

## Installation

### CLI (Claude Code, OpenCode, OpenClaw, or any tool that supports skills)

```bash
npx skills add https://github.com/membai/memb --skill memb-cli
```

### Claude.ai

1. Download this `skills/memb-cli` folder as a ZIP
2. Go to **Settings > Capabilities > Skills**
3. Click **Upload skill** and select the ZIP

### Claude API (Skills API)

```bash
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "memb-cli", "source": "https://github.com/membai/memb/tree/main/skills/memb-cli"}'
```

## Prerequisites

- A MemB Platform API key ([Get one here](https://app.memb.ai/dashboard/api-keys?utm_source=oss&utm_medium=skill-memb-cli-readme))
- **Node.js 18+** or **Python 3.10+**
- Install the CLI:

  ```bash
  # Node.js
  npm install -g @memb/cli

  # Python
  pip install memb-cli
  ```

- Set the environment variable:

  ```bash
  export MEM0_API_KEY="m0-your-api-key"
  ```

  Or run `memb init` for the interactive setup wizard.

## Quick Start

After installing, just ask Claude:

- "Add a memory for user alice that she prefers dark mode"
- "Search alice's memories for dietary preferences"
- "List all memories and output as JSON"
- "Delete all memories for user bob"
- "Set up memb CLI in my CI pipeline"
- "Pipe the output of my script into memb add"

## What's Inside

```text
skills/memb-cli/
├── SKILL.md                          # Skill definition and instructions
├── README.md                         # This file
├── LICENSE                           # Apache-2.0
└── references/                       # Documentation (loaded on demand)
    ├── command-reference.md           # Every command, flag, option, and example
    ├── configuration.md               # Config file, env vars, precedence, init wizard
    └── workflows.md                   # Piping, scripting, CI/CD, agent mode recipes
```

## Links

- [MemB Platform Dashboard](https://app.memb.ai?utm_source=oss&utm_medium=skill-memb-cli-readme)
- [MemB Documentation](https://docs.memb.ai)
- [MemB CLI Docs](https://docs.memb.ai/cli)
- [MemB GitHub](https://github.com/membai/memb)

## Skill Graph

This skill is part of the **MemB skill graph** -- three interconnected skills for different interfaces to the MemB platform:

| Skill | Purpose | Link |
|-------|---------|------|
| **memb** | Python/TypeScript SDK, REST API, framework integrations | [local](../memb/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb) |
| **memb-cli** (this skill) | Terminal commands for memory operations | [local](./SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-cli) |
| **memb-vercel-ai-sdk** | Vercel AI SDK provider with automatic memory | [local](../memb-vercel-ai-sdk/SKILL.md) / [GitHub](https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk) |

## License

Apache-2.0
