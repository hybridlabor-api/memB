# @memb/opencode-plugin

Persistent memory for [OpenCode](https://opencode.ai). Your agent remembers decisions, preferences, and learnings across sessions automatically.

## Install

```bash
opencode plugin @memb/opencode-plugin
```

This adds the plugin to your `~/.config/opencode/opencode.json`. The plugin registers its memory tools and skills itself — there is no MCP server to configure.

**Or let your agent do it** — paste this into OpenCode:

```
Install @memb/opencode-plugin by following https://raw.githubusercontent.com/membai/memb/main/integrations/memb-plugin/.opencode-plugin/README.md
```

Get your API key (free): [app.memb.ai/dashboard/api-keys](https://app.memb.ai/dashboard/api-keys)

```bash
echo 'export MEMB_API_KEY="m0-your-key"' >> ~/.zshrc && source ~/.zshrc
```

Restart OpenCode.

## What's included

| Component | Description |
|-----------|-------------|
| **9 Native Memory Tools** | `add_memory`, `search_memories`, `get_memories`, `update_memory`, `delete_memory`, and more — registered as OpenCode tools, backed by the `membai` SDK (no MCP server required) |
| **Lifecycle Hooks** | Auto-search on session start and every prompt, error memory lookup, compaction context, secret redaction |
| **9 Skills** | `/memb-remember`, `/memb-tour`, `/memb-search`, `/memb-status`, `/memb-scope`, `/memb-dream`, `/memb-forget`, `/memb-pin`, `/memb-context-loader` — discovered in place from the plugin via OpenCode's `skills.paths` |

## Hooks

Pure TypeScript — no Python, no shell scripts. Memory operations are native OpenCode tools backed by the [membai](https://www.npmjs.com/package/membai) SDK directly.

| Hook | Event | What it does |
|------|-------|-------------|
| **Config** | `config` | Registers the `/memb-*` slash commands (via `config.command`) and adds the plugin's own `opencode-skills/` dir to OpenCode's `skills.paths` for in-place skill discovery — no copying into `~/.config/opencode/skills` |
| **Chat message** | `chat.message` | Loads prior memories on session start, searches relevant memories before each prompt, auto-captures learnings periodically |
| **Pre-tool** | `tool.execute.before` | Blocks MEMORY.md writes, steering them to the `add_memory` tool |
| **Post-tool** | `tool.execute.after` | Scans bash errors and pre-fetches related memories |
| **Messages transform** | `experimental.chat.messages.transform` | Injects memory context (session memories, search results, error lookups) into the prompt |
| **Compaction** | `experimental.session.compacting` | Stores session state memory, then injects prior memories into compaction context so nothing is lost |
| **Shell env** | `shell.env` | Exports `MEMB_USER_ID`, `MEMB_APP_ID`, `MEMB_SESSION_ID`, and `MEMB_BRANCH` to shell |

## Memory Tools

| Tool | Description |
|------|-------------|
| `add_memory` | Save text or conversation history |
| `search_memories` | Semantic search across memories |
| `get_memories` | List memories with filters and pagination |
| `get_memory` | Retrieve a specific memory by ID |
| `update_memory` | Overwrite a memory's text by ID |
| `delete_memory` | Delete a single memory by ID |
| `delete_all_memories` | Bulk delete all memories in scope |
| `delete_entities` | Delete an entity and its memories |
| `list_entities` | List users/agents/apps stored in MemB |

## Memory scope

Every memory tool accepts an optional `scope`, and you can set the **default**
scope (used when none is passed) with the `/memb-scope` skill:

| Scope | Reads | Writes |
|-------|-------|--------|
| `project` (default) | this repo (`user_id` + `app_id`) | this repo |
| `session` | this run (adds `run_id`) | this run |
| `global` | all your projects (`app_id="*"`) | user-wide (drops `app_id`) |

```
/memb-scope            # show the current default scope
/memb-scope global     # save & search across all your projects by default
/memb-scope project    # back to repo-only (default)
```

The default persists in `~/.memb/settings.json` (`default_scope`) and is read
fresh on each memory operation, so a change applies immediately — no restart.
`delete_all_memories` always requires an explicit `scope="global"` to delete
user-wide, so changing the default can't trigger a cross-project wipe.

## Verify

Start OpenCode and ask: *"Search my memories for recent decisions"*

If the `memb` tools respond, you're all set.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No tools appearing | Restart OpenCode after installing |
| 401 Unauthorized | `echo $MEMB_API_KEY` must print your `m0-` key |
| Plugin not loading | Run `opencode plugin @memb/opencode-plugin` again |

## License

Apache-2.0
