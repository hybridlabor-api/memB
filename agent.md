# memB Agent Guidelines

Welcome, developer agent. Please follow these rules and system designs when modifying the **memB** codebase.

---

## 📚 Documentation & Wiki

- **Entrypoint:** [.openwiki/quickstart.md](.openwiki/quickstart.md) (onboarding, quick CLI commands, test suites instructions, and workspace orientation)
- **Reference Guides:**
  - [System Architecture](.openwiki/architecture.md) (Tech stack, module boundaries, data flows, and SQLite schemas)
  - [Design Decisions Log](.openwiki/decisions.md) (Architecture trade-offs, vector search strategies)
  - [Release Notes](.openwiki/release_notes.md) (Changelog history)

---

## 🔒 Crucial Rules (Must Follow)

1. **Absolute Privacy:** Under no circumstances should absolute paths containing local usernames (e.g. `/Users/timrennings/...`) be written to repository files, documentation, README, or wiki markdown files. Always use relative paths (`.openwiki/quickstart.md`) or generic home folder variables (e.g. `~/.MemBDB/` or `$HOME/...`).
2. **Zero Telemetry:** Ensure that no tracking, PostHog logs, analytics, or remote logging calls are introduced during edits.
3. **No Key Leakage:** Do not commit or document API keys, passwords, or credentials in any file. Use placeholders.
