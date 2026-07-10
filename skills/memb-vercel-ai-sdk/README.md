# MemB Vercel AI SDK Skill for Claude

Add persistent memory to any Vercel AI SDK application using [@memb/vercel-ai-provider](https://www.npmjs.com/package/@memb/vercel-ai-provider).

## What This Skill Does

When installed, Claude can:

- **Set up `@memb/vercel-ai-provider`** in your TypeScript or Next.js project
- **Generate working code** using the wrapped model (`createMemB`) or standalone utilities (`retrieveMemories`, `addMemories`, etc.)
- **Configure multi-provider setups** (OpenAI, Anthropic, Google, Groq, Cohere)
- **Integrate memory** into streaming responses, structured output, and API routes

## Installation

### CLI (Claude Code, OpenCode, OpenClaw, or any tool that supports skills)

```bash
npx skills add https://github.com/membai/memb --skill memb-vercel-ai-sdk
```

### Claude.ai

1. Download this `skills/memb-vercel-ai-sdk` folder as a ZIP
2. Go to **Settings > Capabilities > Skills**
3. Click **Upload skill** and select the ZIP

### Claude API (Skills API)

```bash
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "memb-vercel-ai-sdk", "source": "https://github.com/membai/memb/tree/main/skills/memb-vercel-ai-sdk"}'
```

### Prerequisites

- **Node.js 18+**
- **Vercel AI SDK v5** (`ai` package version 5.x)
- A MemB Platform API key ([Get one here](https://app.memb.ai/dashboard/api-keys?utm_source=oss&utm_medium=skill-memb-vercel-ai-sdk-readme))
- An LLM provider API key (OpenAI, Anthropic, Google, Groq, or Cohere)
- Set environment variables:

  ```bash
  export MEM0_API_KEY="m0-xxx"
  export OPENAI_API_KEY="sk-xxx"  # or your chosen provider's key
  ```

## Quick Start

After installing, just ask Claude:

- "Add memory to my Vercel AI SDK app"
- "Set up memb with streamText in my Next.js API route"
- "Use retrieveMemories with Anthropic instead of the wrapped model"
- "Show me how to use graph memories with the Vercel AI provider"
- "Help me store conversation history with addMemories"

## What's Inside

```text
skills/memb-vercel-ai-sdk/
├── SKILL.md                          # Skill definition and instructions
├── README.md                         # This file
├── LICENSE                           # Apache-2.0
└── references/                       # Documentation (loaded on demand)
    ├── provider-api.md               # createMemB, MemBProvider, types, config
    ├── memory-utilities.md           # addMemories, retrieveMemories, getMemories, searchMemories
    └── usage-patterns.md             # Working examples: streaming, Next.js, multi-provider, graph
```

## Links

- [MemB Platform Dashboard](https://app.memb.ai?utm_source=oss&utm_medium=skill-memb-vercel-ai-sdk-readme)
- [MemB Documentation](https://docs.memb.ai)
- [MemB GitHub](https://github.com/membai/memb)
- [@memb/vercel-ai-provider on npm](https://www.npmjs.com/package/@memb/vercel-ai-provider)
- [Vercel AI SDK Documentation](https://ai-sdk.dev/docs)

## Skill Graph

This skill is part of the MemB skill graph. The three MemB skills (memb, memb-cli, memb-vercel-ai-sdk) each cover a different interface to the same MemB Platform API.

## License

Apache-2.0
