import { createMemB, MemBProvider } from "../src";
import { MemBGenericLanguageModel } from "../src/memb-generic-language-model";
import { MemBClassSelector } from "../src/memb-provider-selector";
import MemBAITextGenerator from "../src/provider-response-provider";
import { MemBConfigSettings } from "../src/memb-types";

// Mock fetch globally for memory API tests
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe("V3 Provider Contract", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe("MemBProvider factory", () => {
    let provider: MemBProvider;

    beforeEach(() => {
      provider = createMemB({
        provider: "openai",
        membApiKey: "test-key",
        apiKey: "test-openai-key",
      });
    });

    it("should have specificationVersion v3", () => {
      expect(provider.specificationVersion).toBe("v3");
    });

    it("should expose languageModel, chat, and completion methods", () => {
      expect(typeof provider.languageModel).toBe("function");
      expect(typeof provider.chat).toBe("function");
      expect(typeof provider.completion).toBe("function");
    });

    it("should be callable as a function", () => {
      const model = provider("gpt-4o");
      expect(model).toBeDefined();
      expect(model.specificationVersion).toBe("v3");
    });

    it("should throw when called with new keyword", () => {
      expect(() => new (provider as any)("gpt-4o")).toThrow(
        "The MemB model function cannot be called with the new keyword."
      );
    });
  });

  describe("MemBGenericLanguageModel V3 interface", () => {
    let model: MemBGenericLanguageModel;

    beforeEach(() => {
      model = new MemBGenericLanguageModel(
        "gpt-4o",
        { user_id: "test-user" },
        {
          provider: "openai",
          membApiKey: "test-key",
          apiKey: "test-openai-key",
        }
      );
    });

    it("should implement specificationVersion v3", () => {
      expect(model.specificationVersion).toBe("v3");
    });

    it("should not have deprecated V2 properties", () => {
      expect((model as any).defaultObjectGenerationMode).toBeUndefined();
      expect((model as any).supportsImageUrls).toBeUndefined();
    });

    it("should have supportedUrls as a record", () => {
      expect(model.supportedUrls).toBeDefined();
      expect(typeof model.supportedUrls).toBe("object");
      expect(model.supportedUrls["*"]).toBeDefined();
      expect(Array.isArray(model.supportedUrls["*"])).toBe(true);
    });

    it("should have doGenerate and doStream methods", () => {
      expect(typeof model.doGenerate).toBe("function");
      expect(typeof model.doStream).toBe("function");
    });

    it("should have provider and modelId properties", () => {
      expect(model.provider).toBe("openai");
      expect(model.modelId).toBe("gpt-4o");
    });
  });

  describe("MemBClassSelector", () => {
    const supportedProviders = ["openai", "anthropic", "cohere", "groq", "google", "gemini"];

    it.each(supportedProviders)("should accept %s as a valid provider", (providerName) => {
      const selector = new MemBClassSelector(
        "test-model",
        { provider: providerName, apiKey: "test-key" }
      );
      expect(selector).toBeDefined();
    });

    it("should throw for unsupported provider", () => {
      expect(
        () => new MemBClassSelector("test-model", { provider: "invalid-provider" })
      ).toThrow("Model not supported: invalid-provider");
    });

    it("should create a V3 provider instance", () => {
      const selector = new MemBClassSelector(
        "gpt-4o",
        { provider: "openai", apiKey: "test-key" }
      );
      const provider = selector.createProvider();
      expect(provider.specificationVersion).toBe("v3");
      expect(typeof provider.doGenerate).toBe("function");
      expect(typeof provider.doStream).toBe("function");
    });
  });

  describe("Provider modelType routing", () => {
    it("should create chat model with chat modelType", () => {
      const provider = createMemB({
        provider: "openai",
        membApiKey: "test-key",
        apiKey: "test-openai-key",
      });

      const chatModel = provider.chat("gpt-4o");
      expect(chatModel).toBeDefined();
      expect(chatModel.specificationVersion).toBe("v3");
      expect((chatModel as any).config.modelType).toBe("chat");
    });

    it("should create completion model with completion modelType", () => {
      const provider = createMemB({
        provider: "openai",
        membApiKey: "test-key",
        apiKey: "test-openai-key",
      });

      const completionModel = provider.completion("gpt-4o");
      expect(completionModel).toBeDefined();
      expect(completionModel.specificationVersion).toBe("v3");
      expect((completionModel as any).config.modelType).toBe("completion");
    });
  });

  describe("Default baseURL", () => {
    it("should default to https, not http", () => {
      const provider = createMemB({
        provider: "openai",
        membApiKey: "test-key",
      });
      const model = provider("gpt-4o") as MemBGenericLanguageModel;
      expect((model as any).config.baseURL).toMatch(/^https:\/\//);
    });
  });

  describe("google/gemini alias routing", () => {
    it("should route google and gemini to the same provider", () => {
      const googleModel = new MemBAITextGenerator(
        "gemini-2.0-flash",
        { provider: "google", apiKey: "test-key" },
        {}
      );
      const geminiModel = new MemBAITextGenerator(
        "gemini-2.0-flash",
        { provider: "gemini", apiKey: "test-key" },
        {}
      );
      expect(googleModel.specificationVersion).toBe("v3");
      expect(geminiModel.specificationVersion).toBe("v3");
      expect(googleModel.modelId).toBe(geminiModel.modelId);
    });
  });

  describe("Graph memory removal", () => {
    it("should not have enable_graph in MemBConfigSettings type", () => {
      const config: MemBConfigSettings = {
        user_id: "test-user",
        membApiKey: "test-key",
      };
      expect((config as any).enable_graph).toBeUndefined();
    });
  });

  describe("processMemories prompt cloning", () => {
    it("should not mutate the original prompt array", async () => {
      const model = new MemBGenericLanguageModel(
        "gpt-4o",
        { user_id: "test-user" },
        {
          provider: "openai",
          membApiKey: "test-key",
          apiKey: "test-openai-key",
        }
      );

      const originalPrompt = [
        { role: "user" as const, content: [{ type: "text" as const, text: "Hello" }] },
      ];
      const originalLength = originalPrompt.length;

      // Mock both MemB API calls — addMemories (POST /v3/memories/add/) and getMemories (POST /v3/memories/search/)
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [
            { memory: "User likes TypeScript" },
          ],
        });

      // Access processMemories via reflection
      const processMemories = (model as any).processMemories.bind(model);
      await processMemories(originalPrompt, { membApiKey: "test-key", user_id: "test-user" });

      // Original prompt should NOT have been mutated
      expect(originalPrompt.length).toBe(originalLength);
    });
  });

  describe("getMemories normalization", () => {
    it("should return a flat array when API returns a flat array", async () => {
      const { getMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { memory: "User prefers dark mode" },
          { memory: "User likes React" },
        ],
      });

      const result = await getMemories("test query", { membApiKey: "test-key", user_id: "test-user" });
      expect(Array.isArray(result)).toBe(true);
      expect(result).toHaveLength(2);
      expect(result[0].memory).toBe("User prefers dark mode");
    });

    it("should return a flat array when API returns { results: [...] }", async () => {
      const { getMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [
            { memory: "User prefers dark mode" },
          ],
        }),
      });

      const result = await getMemories("test query", { membApiKey: "test-key", user_id: "test-user" });
      expect(Array.isArray(result)).toBe(true);
      expect(result).toHaveLength(1);
    });

    it("should return empty array when API returns empty results", async () => {
      const { getMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      const result = await getMemories("test query", { membApiKey: "test-key", user_id: "test-user" });
      expect(Array.isArray(result)).toBe(true);
      expect(result).toHaveLength(0);
    });
  });

  describe("retrieveMemories normalization", () => {
    it("should return empty string when no memories exist", async () => {
      const { retrieveMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      const result = await retrieveMemories("test query", { membApiKey: "test-key", user_id: "test-user" });
      expect(result).toBe("");
    });

    it("should return formatted string when memories exist as flat array", async () => {
      const { retrieveMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { memory: "User likes pizza" },
        ],
      });

      const result = await retrieveMemories("test query", { membApiKey: "test-key", user_id: "test-user" });
      expect(result).toContain("System Message:");
      expect(result).toContain("User likes pizza");
    });

    it("should return formatted string when memories come as { results: [...] }", async () => {
      const { retrieveMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [{ memory: "User likes pizza" }],
        }),
      });

      const result = await retrieveMemories("test query", { membApiKey: "test-key", user_id: "test-user" });
      expect(result).toContain("System Message:");
      expect(result).toContain("User likes pizza");
    });
  });

  describe("top_k zero handling", () => {
    it("should respect top_k: 0 and not fall back to default", async () => {
      const { searchMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await searchMemories("test query", {
        membApiKey: "test-key",
        user_id: "test-user",
        top_k: 0,
      });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.top_k).toBe(0);
    });
  });

  describe("MemB v3 API migration", () => {
    it("should call /v3/memories/search/ endpoint for search", async () => {
      const { searchMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await searchMemories("test query", { membApiKey: "test-key", user_id: "test-user" });

      const url = mockFetch.mock.calls[0][0];
      expect(url).toBe("https://api.memb.ai/v3/memories/search/");
    });

    it("should call /v3/memories/add/ endpoint for add", async () => {
      const { addMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "ok", status: "PENDING", event_id: "test" }),
      });

      await addMemories(
        [{ role: "user" as const, content: [{ type: "text" as const, text: "Hello" }] }],
        { membApiKey: "test-key", user_id: "test-user" }
      );

      const url = mockFetch.mock.calls[0][0];
      expect(url).toBe("https://api.memb.ai/v3/memories/add/");
    });

    it("should put entity IDs inside filters for search (not top-level)", async () => {
      const { searchMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await searchMemories("test query", {
        membApiKey: "test-key",
        user_id: "user-123",
        agent_id: "agent-456",
      });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.filters.user_id).toBe("user-123");
      expect(body.filters.agent_id).toBe("agent-456");
      // Should NOT be top-level
      expect(body.user_id).toBeUndefined();
      expect(body.agent_id).toBeUndefined();
    });

    it("should not send deprecated v2 params (version, output_format, org_id, etc.)", async () => {
      const { searchMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await searchMemories("test query", { membApiKey: "test-key", user_id: "test-user" });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.version).toBeUndefined();
      expect(body.output_format).toBeUndefined();
      expect(body.org_id).toBeUndefined();
      expect(body.project_id).toBeUndefined();
      expect(body.org_name).toBeUndefined();
      expect(body.project_name).toBeUndefined();
    });

    it("should not send deprecated params in add body", async () => {
      const { addMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "ok", status: "PENDING", event_id: "test" }),
      });

      await addMemories(
        [{ role: "user" as const, content: [{ type: "text" as const, text: "Hello" }] }],
        { membApiKey: "test-key", user_id: "test-user" }
      );

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.version).toBeUndefined();
      expect(body.async_mode).toBeUndefined();
      expect(body.output_format).toBeUndefined();
      expect(body.enable_graph).toBeUndefined();
      expect(body.filter_memories).toBeUndefined();
      expect(body.org_id).toBeUndefined();
      expect(body.project_id).toBeUndefined();
      // Should have entity ID at top-level for add endpoint
      expect(body.user_id).toBe("test-user");
    });

    it("should not have deprecated fields in MemBConfigSettings type", () => {
      const config: MemBConfigSettings = {
        user_id: "test-user",
        membApiKey: "test-key",
      };
      expect((config as any).org_id).toBeUndefined();
      expect((config as any).project_id).toBeUndefined();
      expect((config as any).org_name).toBeUndefined();
      expect((config as any).project_name).toBeUndefined();
      expect((config as any).output_format).toBeUndefined();
      expect((config as any).filter_memories).toBeUndefined();
      expect((config as any).async_mode).toBeUndefined();
      expect((config as any).enable_graph).toBeUndefined();
    });

    it("should default top_k to 10 (v3 default) when not provided", async () => {
      const { searchMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await searchMemories("test query", { membApiKey: "test-key", user_id: "test-user" });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.top_k).toBe(10);
    });

    it("should merge user-provided filters with entity ID filters", async () => {
      const { searchMemories } = require("../src/memb-utils");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await searchMemories("test query", {
        membApiKey: "test-key",
        user_id: "user-123",
        filters: { category: "preferences" },
      });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.filters.user_id).toBe("user-123");
      expect(body.filters.category).toBe("preferences");
    });
  });
});
