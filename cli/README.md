# memb CLI

The official command-line interface for [memb](https://memb.ai) — the memory layer for AI agents. Works with the MemB Platform API. Available in Python and Node.js.

> **For AI agents:** pass `--agent` (or `--json`) on any command for structured JSON output purpose-built for tool loops — sanitized fields, no colors or spinners, errors as JSON. See [Agent mode](#agent-mode) below.

## Installation

```bash
npm install -g @memb/cli
```

```bash
pip install memb-cli
```

Both packages install a `memb` binary with identical behavior.

## Quick start

```bash
# Interactive setup wizard
memb init

# Or login via email (get a new API key)
memb init --email alice@company.com

# Or authenticate with an existing API key
memb init --api-key m0-xxx

# Add a memory
memb add "I prefer dark mode and use vim keybindings" --user-id alice

# Search memories
memb search "What are Alice's preferences?" --user-id alice

# List all memories for a user
memb list --user-id alice

# Update a memory
memb update <memory-id> "I switched to light mode"

# Delete a memory
memb delete <memory-id>
```

## Commands

| Command | Description |
|---------|-------------|
| `memb init` | Setup wizard — login via email or configure API key manually |
| `memb add` | Add a memory from text, JSON messages, a file, or stdin |
| `memb search` | Search memories using natural language |
| `memb list` | List memories with optional filters and pagination |
| `memb get` | Retrieve a specific memory by ID |
| `memb update` | Update the text or metadata of a memory |
| `memb delete` | Delete a memory, all memories for a scope, or an entity |
| `memb import` | Bulk import memories from a JSON file |
| `memb config` | View or modify CLI configuration |
| `memb entity` | List or delete entities (users, agents, apps, runs) |
| `memb event` | Inspect background processing events (bulk deletes, large add jobs) |
| `memb status` | Verify API connection and display current project |
| `memb version` | Print the CLI version |

Run `memb <command> --help` for detailed usage on any command.

## Agent mode

Pass `--agent` (or its alias `--json`) as a **global flag** on any command to get output designed for AI agent tool loops:

```bash
memb --agent search "user preferences" --user-id alice
memb --agent add "User prefers dark mode" --user-id alice
memb --agent list --user-id alice
```

Every command returns the same envelope shape:

```json
{
  "status": "success",
  "command": "search",
  "duration_ms": 134,
  "scope": { "user_id": "alice" },
  "count": 2,
  "data": [
    { "id": "abc-123", "memory": "User prefers dark mode", "score": 0.97, "created_at": "2026-01-15", "categories": ["preferences"] }
  ]
}
```

What agent mode does differently from `--output json`:
- **Sanitized `data`**: only the fields an agent needs (id, memory, score, etc.) — no internal API noise
- **No human output**: spinners, colors, and banners are suppressed entirely
- **Errors as JSON**: errors go to stdout as `{"status": "error", "command": "...", "error": "..."}` with a non-zero exit code

Use `memb help --json` to get the full command tree as JSON — useful for agents that need to self-discover available commands.

## Output formats

Control how results are displayed with `--output`:

| Format | Description |
|--------|-------------|
| `text` | Human-readable with colors and formatting (default) |
| `json` | Structured JSON for piping to `jq` (raw API response) |
| `table` | Tabular format (default for `list`) |
| `quiet` | Minimal — just IDs or status codes |
| `agent` | Structured JSON envelope with sanitized fields (set by `--agent`/`--json`) |

## Environment variables

| Variable | Description |
|----------|-------------|
| `MEM0_API_KEY` | API key (overrides config file) |
| `MEM0_BASE_URL` | API base URL |
| `MEM0_USER_ID` | Default user ID |
| `MEM0_AGENT_ID` | Default agent ID |
| `MEM0_APP_ID` | Default app ID |
| `MEM0_RUN_ID` | Default run ID |
| `MEM0_ENABLE_GRAPH` | Enable graph memory (`true` / `false`) |

## Implementations

| Language | Directory | Package | Docs |
|----------|-----------|---------|------|
| TypeScript | [`node/`](./node/) | `@memb/cli` | [README](./node/README.md) |
| Python | [`python/`](./python/) | `memb-cli` | [README](./python/README.md) |

## Documentation

Full documentation is available at [docs.memb.ai/platform/cli](https://docs.memb.ai/platform/cli).

## License

Apache-2.0
