# Provider API Reference

Complete reference for the `@memb/vercel-ai-provider` provider layer. Source: `integrations/vercel-ai-sdk/src/`.

## `createMemB(options?)`

Factory function that creates a `MemBProvider` instance. This is the primary entry point for the wrapped model approach.

```typescript
import { createMemB } from "@memb/vercel-ai-provider";

const memb = createMemB();                           // defaults: provider "openai"
const memb = createMemB({ provider: "anthropic" });  // use Anthropic as LLM backend
```

**Signature:**

```typescript
function createMemB(options?: MemBProviderSettings): MemBProvider;
```

When called with no arguments, defaults to `{ provider: "openai" }`.

**Returns:** `MemBProvider` -- a callable function that also exposes `.chat()`, `.completion()`, and `.languageModel()` methods.

## `MemBProvider` Interface

Implements `ProviderV2` from `@ai-sdk/provider`.

```typescript
interface MemBProvider extends ProviderV2 {
  // Call directly as a function
  (modelId: MemBChatModelId, settings?: MemBChatSettings): LanguageModelV2;

  // Or use named methods
  chat(modelId: MemBChatModelId, settings?: MemBChatSettings): LanguageModelV2;
  completion(modelId: MemBChatModelId, settings?: MemBChatSettings): LanguageModelV2;
  languageModel(modelId: MemBChatModelId, settings?: MemBChatSettings): LanguageModelV2;
}
```

- **Direct call** (`memb("gpt-5-mini", {...})`): creates a generic language model (neither chat nor completion mode forced).
- **`chat()`**: creates a model with `modelType: "chat"` (note: in the current source, the chat constructor sets `modelType: "completion"` -- this appears to be a bug; functionally equivalent to `completion()` at present).
- **`completion()`**: creates a model with `modelType: "completion"`.
- **`languageModel()`**: alias for the generic model (same as direct call).

All three return a `MemBGenericLanguageModel` instance implementing `LanguageModelV2`.

## `MemBProviderSettings` Interface

Configuration passed to `createMemB()`.

```typescript
interface MemBProviderSettings {
  baseURL?: string;            // Base URL for the LLM provider (default: "http://api.openai.com")
  headers?: Record<string, string>;  // Custom headers for LLM requests
  provider?: string;           // LLM provider name (default: "openai")
  membApiKey?: string;         // MemB Platform API key (or use MEM0_API_KEY env var)
  apiKey?: string;             // LLM provider API key (e.g., OpenAI key)
  membConfig?: MemBConfig;     // Default MemB config (user_id, etc.) applied to all calls
  config?: LLMProviderSettings; // Provider-specific settings (OpenAI, Anthropic, etc.)
  fetch?: typeof fetch;        // Custom fetch implementation (for testing/middleware)
  generateId?: () => string;   // Custom ID generator (internal use)
  name?: string;               // Provider instance name
  modelType?: "completion" | "chat";  // Force model type
}
```

### Key fields explained

| Field | Purpose | Example |
|-------|---------|---------|
| `provider` | Which LLM backend to use | `"openai"`, `"anthropic"`, `"google"`, `"groq"`, `"cohere"` |
| `membApiKey` | MemB Platform API key | `"m0-xxx"` |
| `apiKey` | LLM provider API key | `"sk-xxx"` (OpenAI), `"sk-ant-xxx"` (Anthropic) |
| `membConfig` | Default MemB settings for all calls | `{ user_id: "alice" }` |
| `config` | Provider-specific SDK settings | `{ organization: "org-xxx" }` for OpenAI |
| `baseURL` | Override LLM provider base URL | `"https://my-proxy.example.com"` |

## `memb` Singleton

A pre-configured instance using default settings (OpenAI provider, no API keys set -- relies on env vars).

```typescript
import { memb } from "@memb/vercel-ai-provider";

const { text } = await generateText({
  model: memb("gpt-5-mini", { user_id: "alice" }),
  prompt: "Hello",
});
```

Equivalent to `createMemB()` with no arguments.

## `MemBConfigSettings` Interface

Configuration for memory operations. Used as `MemBChatSettings` (per-call) or `MemBConfig` (provider-level default). All fields are optional.

```typescript
interface MemBConfigSettings {
  user_id?: string;              // Scope memories to a specific user
  app_id?: string;               // Scope memories to an application
  agent_id?: string;             // Scope memories to an agent
  run_id?: string;               // Scope memories to a specific run/session
  metadata?: Record<string, any>; // Custom metadata attached to memories
  filters?: Record<string, any>; // Custom filters for memory search
  infer?: boolean;               // Enable inference during memory operations
  page?: number;                 // Pagination: page number
  page_size?: number;            // Pagination: results per page
  membApiKey?: string;           // MemB API key (overrides provider-level key)
  top_k?: number;                // Number of memories to retrieve (default: 5)
  threshold?: number;            // Minimum similarity score for retrieval (default: 0.1)
  rerank?: boolean;              // Enable re-ranking of search results (default: false)
  host?: string;                 // Custom MemB API host (default: "https://api.memb.ai")
}
```

## `MemBChatConfig` Type

Combined type used internally by the language model. Merges memory config with provider config.

```typescript
interface MemBChatConfig extends MemBConfigSettings, MemBProviderSettings {}
```

This means a `MemBChatConfig` has all fields from both `MemBConfigSettings` and `MemBProviderSettings`.

## `MemBChatSettings` Type

Alias for `MemBConfigSettings`. Passed as the second argument when creating a model:

```typescript
memb("gpt-5-mini", { user_id: "alice" })
//                   ^^^^^^^^^^^^^^^^^^
//                   This object is MemBChatSettings
```

## `LLMProviderSettings` Type

Union of provider-specific settings. Extends all supported provider setting interfaces:

```typescript
interface LLMProviderSettings extends
  OpenAIProviderSettings,
  AnthropicProviderSettings,
  CohereProviderSettings,
  GroqProviderSettings {}
```

Pass via the `config` field of `MemBProviderSettings` to forward settings to the underlying LLM provider SDK.

## Provider Selection: `MemBClassSelector`

Internal class that maps the `provider` string to the correct AI SDK provider.

```typescript
class MemBClassSelector {
  static supportedProviders = ["openai", "anthropic", "cohere", "groq", "google"];
  // ...
}
```

**Important:** The `"gemini"` alias exists in the provider switch statement (maps to `createGoogleGenerativeAI`) but is **NOT** in the `supportedProviders` list. The constructor validates against `supportedProviders`, so using `"gemini"` will throw `"Model not supported: gemini"`. Use `"google"` instead.

### Provider mapping

| Config value | SDK used | Factory function |
|-------------|----------|------------------|
| `"openai"` | `@ai-sdk/openai` | `createOpenAI` |
| `"anthropic"` | `@ai-sdk/anthropic` | `createAnthropic` |
| `"cohere"` | `@ai-sdk/cohere` | `createCohere` |
| `"groq"` | `@ai-sdk/groq` | `createGroq` |
| `"google"` | `@ai-sdk/google` | `createGoogleGenerativeAI` |

## `MemB` Facade Class

An alternative exported class that creates models directly without the callable-function pattern.

```typescript
import { MemB } from "@memb/vercel-ai-provider";

const memb = new MemB({ provider: "openai" });
const chatModel = memb.chat("gpt-5-mini", { user_id: "alice" });
const completionModel = memb.completion("gpt-5-mini");
```

The facade defaults its base URL to `"http://127.0.0.1:11434/api"` (Ollama-style) rather than `"http://api.openai.com"`. It always uses `"openai"` as the provider for created models.

**Methods:**
- `chat(modelId, settings?)` -- creates a model with `modelType: "chat"`
- `completion(modelId, settings?)` -- creates a model with `modelType: "completion"`

## `MemBGenericLanguageModel` Class

The core class implementing `LanguageModelV2`. Created by `createMemB` or the `MemB` facade.

```typescript
class MemBGenericLanguageModel implements LanguageModelV2 {
  readonly specificationVersion = "v2";
  readonly defaultObjectGenerationMode = "json";
  readonly supportsImageUrls = false;
  readonly supportedUrls: Record<string, RegExp[]> = { '*': [/.*/] };

  provider: string;   // e.g., "openai"
  modelId: string;    // e.g., "gpt-5-mini"
  settings: MemBChatSettings;
  config: MemBChatConfig;

  async doGenerate(options: LanguageModelV2CallOptions): Promise<...>;
  async doStream(options: LanguageModelV2CallOptions): Promise<...>;
}
```

Both `doGenerate` and `doStream` follow the same internal flow:

1. Build `MemBConfigSettings` from `config.membConfig` merged with `settings`
2. Call `processMemories`:
   - Fire `addMemories` as fire-and-forget (no await, `.then().catch()`)
   - Await `getMemories` to retrieve relevant memories
   - Format memories as a system message and prepend to the prompt
3. Create the underlying LLM model via `MemBClassSelector`
4. Delegate to the underlying model's `doGenerate` or `doStream`
5. Return the result

**Note:** Entity identifier fields use snake_case (`user_id`, `app_id`, `agent_id`, `run_id`) to match the MemB API.

## Type: `MemBChatModelId`

```typescript
type MemBChatModelId = string & NonNullable<unknown>;
```

Any non-null string. The model ID is passed through to the underlying provider (e.g., `"gpt-5-mini"`, `"gemini-pro"`).
