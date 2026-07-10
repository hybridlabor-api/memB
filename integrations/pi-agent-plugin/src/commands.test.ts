import { describe, it, expect, vi, beforeEach } from "vitest";
import { registerCommands } from "./commands.ts";
import type { MemBConfig, ScopeContext } from "./types.ts";

vi.mock("./telemetry.ts", () => ({
  captureCommandEvent: vi.fn(),
}));

vi.mock("./dream/index.ts", () => ({
  acquireDreamLock: vi.fn(() => true),
}));

vi.mock("./dream/prompt.ts", () => ({
  DREAM_PROTOCOL: "dream protocol text",
}));

function makeMemB() {
  return {
    search: vi.fn(),
    delete: vi.fn(),
    add: vi.fn(),
    get: vi.fn(),
    getAll: vi.fn(),
    update: vi.fn(),
  } as any;
}

function makePi() {
  const commands = new Map<string, { handler: (args: string, ctx: any) => Promise<void> }>();
  return {
    registerCommand: vi.fn((name: string, opts: any) => {
      commands.set(name, opts);
    }),
    sendMessage: vi.fn(),
    _commands: commands,
    _invoke: (name: string, args: string, ctx: any) => commands.get(name)!.handler(args, ctx),
  };
}

function makeCtx(confirmResult = true) {
  return {
    hasUI: true,
    ui: {
      notify: vi.fn(),
      confirm: vi.fn(async () => confirmResult),
      select: vi.fn(),
      input: vi.fn(),
    },
  };
}

const defaultConfig: MemBConfig = {
  apiKey: "test-key",
  userId: "test-user",
  autoCapture: false,
  defaultScope: "project",
  contextInjection: false,
  searchThreshold: 0.3,
  dream: { enabled: false, auto: false, minHours: 24, minSessions: 5, minMemories: 20 },
};

const scopeCtx: ScopeContext = { userId: "test-user", appId: "test-app", runId: "test-run" };

describe("registerCommands", () => {
  let pi: ReturnType<typeof makePi>;
  let memb: ReturnType<typeof makeMemB>;

  beforeEach(() => {
    pi = makePi();
    memb = makeMemB();
    defaultConfig.defaultScope = "project";
    registerCommands(pi as any, memb, defaultConfig, () => scopeCtx);
  });

  it("registers all expected commands", () => {
    const names = [...pi._commands.keys()];
    expect(names).toContain("memb-remember");
    expect(names).toContain("memb-forget");
    expect(names).toContain("memb-search");
    expect(names).toContain("memb-tour");
    expect(names).toContain("memb-dream");
    expect(names).toContain("memb-pin");
    expect(names).toContain("memb-scope");
    expect(names).toContain("memb-status");
  });

  describe("/memb-forget", () => {
    it("shows warning when no query provided", async () => {
      const ctx = makeCtx();
      await pi._invoke("memb-forget", "", ctx);
      expect(ctx.ui.notify).toHaveBeenCalledWith("Usage: /memb-forget <query>", "warning");
      expect(memb.search).not.toHaveBeenCalled();
    });

    it("sends a visible message naming the query when no memories match", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({ results: [] });
      await pi._invoke("memb-forget", "old preference", ctx);
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-forget",
          content: expect.stringContaining('No matches for "old preference"'),
          display: true,
        }),
      );
    });

    it("asks for confirmation before deleting a single match", async () => {
      const ctx = makeCtx(true);
      memb.search.mockResolvedValue({ results: [{ id: "abc-123", memory: "test mem" }] });
      memb.delete.mockResolvedValue({ message: "Deleted" });

      await pi._invoke("memb-forget", "test", ctx);

      expect(ctx.ui.confirm).toHaveBeenCalledWith(
        "Delete this memory?",
        expect.stringContaining("test mem"),
      );
      expect(memb.delete).toHaveBeenCalledWith("abc-123");
    });

    it("sends a visible confirmation showing what was forgotten", async () => {
      const ctx = makeCtx(true);
      memb.search.mockResolvedValue({ results: [{ id: "abc-123", memory: "test mem" }] });
      memb.delete.mockResolvedValue({ message: "Deleted" });

      await pi._invoke("memb-forget", "test", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-forget",
          content: expect.stringContaining("Forgotten"),
          display: true,
        }),
      );
    });

    it("does not delete when user cancels confirmation", async () => {
      const ctx = makeCtx(false);
      memb.search.mockResolvedValue({ results: [{ id: "abc-123", memory: "test mem" }] });

      await pi._invoke("memb-forget", "test", ctx);

      expect(ctx.ui.confirm).toHaveBeenCalled();
      expect(memb.delete).not.toHaveBeenCalled();
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ content: expect.stringContaining("Cancelled"), display: true }),
      );
    });

    it("uses select UI for multiple matches and deletes chosen memory", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({
        results: [
          { id: "id-1", memory: "mem one" },
          { id: "id-2", memory: "mem two" },
        ],
      });
      memb.delete.mockResolvedValue({ message: "Deleted" });
      ctx.ui.select = vi.fn(async (_title: string, options: string[]) => options[1]);

      await pi._invoke("memb-forget", "test", ctx);

      expect(ctx.ui.select).toHaveBeenCalledWith(
        expect.stringContaining("which should I delete"),
        expect.arrayContaining([
          expect.stringContaining("mem one"),
          expect.stringContaining("mem two"),
        ]),
      );
      expect(memb.delete).toHaveBeenCalledWith("id-2");
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-forget",
          content: expect.stringContaining("Forgotten"),
          display: true,
        }),
      );
    });

    it("does not delete when user cancels select", async () => {
      const ctx = makeCtx();
      ctx.ui.select = vi.fn(async () => undefined);
      memb.search.mockResolvedValue({
        results: [
          { id: "id-1", memory: "mem one" },
          { id: "id-2", memory: "mem two" },
        ],
      });

      await pi._invoke("memb-forget", "test", ctx);

      expect(memb.delete).not.toHaveBeenCalled();
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ content: expect.stringContaining("Cancelled"), display: true }),
      );
    });
  });

  describe("/memb-pin", () => {
    it("uses update to pin in-place, preserving memory ID", async () => {
      const ctx = makeCtx(true);
      memb.search.mockResolvedValue({ results: [{ id: "abc-123", memory: "important fact" }] });
      memb.update.mockResolvedValue([]);

      await pi._invoke("memb-pin", "important", ctx);

      expect(ctx.ui.confirm).toHaveBeenCalledWith(
        "Pin this memory?",
        expect.stringContaining("important fact"),
      );
      expect(memb.update).toHaveBeenCalledWith("abc-123", { text: "[PINNED] important fact" });
      expect(memb.add).not.toHaveBeenCalled();
      expect(memb.delete).not.toHaveBeenCalled();
    });

    it("sends a visible confirmation after pinning", async () => {
      const ctx = makeCtx(true);
      memb.search.mockResolvedValue({ results: [{ id: "abc-123", memory: "important fact" }] });
      memb.update.mockResolvedValue([]);

      await pi._invoke("memb-pin", "important", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-pin",
          content: expect.stringContaining("Pinned"),
          display: true,
        }),
      );
    });

    it("does not pin when user cancels", async () => {
      const ctx = makeCtx(false);
      memb.search.mockResolvedValue({ results: [{ id: "abc-123", memory: "fact" }] });

      await pi._invoke("memb-pin", "fact", ctx);

      expect(memb.update).not.toHaveBeenCalled();
    });

    it("skips already-pinned memories with a visible message", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({ results: [{ id: "abc-123", memory: "[PINNED] fact" }] });

      await pi._invoke("memb-pin", "fact", ctx);

      expect(ctx.ui.confirm).not.toHaveBeenCalled();
      expect(memb.add).not.toHaveBeenCalled();
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ content: expect.stringContaining("Already pinned"), display: true }),
      );
    });

    it("uses select UI for multiple matches and pins chosen memory", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({
        results: [
          { id: "id-1", memory: "fact one" },
          { id: "id-2", memory: "fact two" },
        ],
      });
      memb.update.mockResolvedValue([]);
      ctx.ui.select = vi.fn(async (_title: string, options: string[]) => options[1]);

      await pi._invoke("memb-pin", "fact", ctx);

      expect(ctx.ui.select).toHaveBeenCalledWith(
        expect.stringContaining("which should I pin"),
        expect.arrayContaining([
          expect.stringContaining("fact one"),
          expect.stringContaining("fact two"),
        ]),
      );
      expect(memb.update).toHaveBeenCalledWith("id-2", { text: "[PINNED] fact two" });
    });

    it("does not pin when user cancels select", async () => {
      const ctx = makeCtx();
      ctx.ui.select = vi.fn(async () => undefined);
      memb.search.mockResolvedValue({
        results: [
          { id: "id-1", memory: "fact one" },
          { id: "id-2", memory: "fact two" },
        ],
      });

      await pi._invoke("memb-pin", "fact", ctx);

      expect(memb.update).not.toHaveBeenCalled();
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ content: expect.stringContaining("Cancelled"), display: true }),
      );
    });
  });

  describe("/memb-search", () => {
    it("performs server-side semantic search with a relevance threshold", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({ results: [{ id: "id-1", memory: "result" }] });

      await pi._invoke("memb-search", "my preferences", ctx);

      expect(memb.search).toHaveBeenCalledWith(
        "my preferences",
        expect.objectContaining({ threshold: 0.3, topK: 10, rerank: true }),
      );
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ customType: "memb-search" }),
      );
    });

    it("uses semantic search even for hex-looking strings", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({ results: [] });

      await pi._invoke("memb-search", "abcd1234", ctx);

      expect(memb.search).toHaveBeenCalledWith("abcd1234", expect.any(Object));
      expect(memb.getAll).not.toHaveBeenCalled();
      expect(memb.get).not.toHaveBeenCalled();
    });

    it("shows a no-matches message naming the query", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({ results: [] });

      await pi._invoke("memb-search", "nonexistent", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ content: expect.stringContaining("No matches") }),
      );
    });

    it("shows a result count header when there are matches", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({
        results: [
          { id: "id-1", memory: "one" },
          { id: "id-2", memory: "two" },
        ],
      });

      await pi._invoke("memb-search", "stuff", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ content: expect.stringContaining("2 matches") }),
      );
    });

    it("shows all results the API returns (relevance gating is server-side)", async () => {
      const ctx = makeCtx();
      memb.search.mockResolvedValue({
        results: [
          { id: "id-1", memory: "first match", score: 0.62 },
          { id: "id-2", memory: "second match", score: 0.31 },
        ],
      });

      await pi._invoke("memb-search", "stuff", ctx);

      const call = pi.sendMessage.mock.calls.find(([m]: any[]) => m.customType === "memb-search");
      expect(call?.[0].content).toContain("first match");
      expect(call?.[0].content).toContain("second match");
      expect(call?.[0].content).toContain("2 matches");
    });
  });

  describe("/memb-remember", () => {
    it("stores a memory verbatim", async () => {
      const ctx = makeCtx();
      memb.add.mockResolvedValue({ message: "Memory stored." });

      await pi._invoke("memb-remember", "I prefer dark mode", ctx);

      expect(memb.add).toHaveBeenCalledWith(
        [{ role: "user", content: "I prefer dark mode" }],
        expect.objectContaining({ infer: false }),
      );
    });

    it("shows the stored text in a visible confirmation (infer:false status response)", async () => {
      const ctx = makeCtx();
      memb.add.mockResolvedValue({ message: "Memories stored successfully" });

      await pi._invoke("memb-remember", "I prefer dark mode", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-remember",
          content: expect.stringContaining("I prefer dark mode"),
          display: true,
        }),
      );
    });

    it("lists memory objects returned by the API when present", async () => {
      const ctx = makeCtx();
      memb.add.mockResolvedValue([{ id: "m1", memory: "Uses dark mode", event: "ADD" }]);

      await pi._invoke("memb-remember", "I prefer dark mode", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-remember",
          content: expect.stringContaining("Uses dark mode"),
          display: true,
        }),
      );
    });

    it("shows warning when no text provided", async () => {
      const ctx = makeCtx();
      await pi._invoke("memb-remember", "  ", ctx);
      expect(ctx.ui.notify).toHaveBeenCalledWith("Usage: /memb-remember <text>", "warning");
    });
  });

  describe("/memb-scope", () => {
    it("sends a visible message showing the current scope when no arg is given", async () => {
      const ctx = makeCtx();
      await pi._invoke("memb-scope", "", ctx);
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-scope",
          content: expect.stringContaining("Current scope:"),
          display: true,
        }),
      );
    });

    it("sends a visible confirmation after changing scope", async () => {
      const ctx = makeCtx();
      await pi._invoke("memb-scope", "global", ctx);
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-scope",
          content: expect.stringContaining("Scope changed to global"),
          display: true,
        }),
      );
    });

    it("warns on an invalid scope", async () => {
      const ctx = makeCtx();
      await pi._invoke("memb-scope", "bogus", ctx);
      expect(ctx.ui.notify).toHaveBeenCalledWith(
        expect.stringContaining('Invalid scope "bogus"'),
        "warning",
      );
    });
  });

  describe("/memb-tour", () => {
    it("shows an empty-state message when there are no memories", async () => {
      const ctx = makeCtx();
      memb.getAll.mockResolvedValue({ results: [] });

      await pi._invoke("memb-tour", "", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-tour",
          content: expect.stringContaining("No memories"),
          display: true,
        }),
      );
    });

    it("groups memories by category with a count header", async () => {
      const ctx = makeCtx();
      memb.getAll.mockResolvedValue({
        results: [
          { id: "id-1", memory: "likes tea", categories: ["preferences"] },
          { id: "id-2", memory: "uses vim", categories: ["technical"] },
        ],
      });

      await pi._invoke("memb-tour", "", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-tour",
          content: expect.stringContaining("Memory tour"),
          display: true,
        }),
      );
    });
  });

  describe("/memb-dream", () => {
    it("feeds the protocol to the agent and shows a clean status line", async () => {
      const ctx = makeCtx();

      await pi._invoke("memb-dream", "", ctx);

      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ customType: "memb-dream", display: false }),
        expect.objectContaining({ triggerTurn: true }),
      );
      expect(pi.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          customType: "memb-dream",
          content: expect.stringContaining("Dreaming"),
          display: true,
        }),
      );
    });
  });
});
