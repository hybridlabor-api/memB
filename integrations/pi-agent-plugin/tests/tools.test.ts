import { describe, it, expect, vi } from "vitest";
import { buildToolExecute } from "../src/memory/tools.ts";
import type { ScopeContext } from "../src/types.ts";

const mockMemB = {
  search: vi.fn(),
  add: vi.fn(),
  getAll: vi.fn(),
  delete: vi.fn(),
  deleteAll: vi.fn(),
};

const scopeCtx: ScopeContext = {
  userId: "testuser",
  appId: "testproject",
  runId: "session123",
};

describe("buildToolExecute", () => {
  const execute = buildToolExecute(mockMemB as any, scopeCtx, "project");

  it("search calls memb.search with correct filters", async () => {
    mockMemB.search.mockResolvedValue({ results: [] });
    await execute({ action: "search", query: "dark mode" });
    expect(mockMemB.search).toHaveBeenCalledWith("dark mode", {
      filters: { user_id: "testuser", app_id: "testproject" },
    });
  });

  it("add calls memb.add with customCategories and entity params", async () => {
    mockMemB.add.mockResolvedValue([{ id: "new-id", memory: "test" }]);
    await execute({ action: "add", content: "User likes tabs" });
    const call = mockMemB.add.mock.calls[0];
    expect(call[0]).toEqual([{ role: "user", content: "User likes tabs" }]);
    expect(call[1].userId).toBe("testuser");
    expect(call[1].appId).toBe("testproject");
    expect(call[1].customCategories).toBeDefined();
    expect(call[1].customCategories.length).toBe(10);
  });

  it("search with scope=global filters by user_id with app_id wildcard", async () => {
    mockMemB.search.mockResolvedValue({ results: [] });
    await execute({ action: "search", query: "preferences", scope: "global" });
    expect(mockMemB.search).toHaveBeenCalledWith("preferences", {
      filters: { user_id: "testuser", app_id: "*" },
    });
  });

  it("delete calls memb.delete with full memory_id", async () => {
    mockMemB.delete.mockResolvedValue({ message: "deleted" });
    await execute({ action: "delete", memory_id: "abc12345-6789-0abc-def0-123456789abc" });
    expect(mockMemB.delete).toHaveBeenCalledWith("abc12345-6789-0abc-def0-123456789abc");
  });

  it("delete passes memory_id directly to memb.delete", async () => {
    const fullId = "956e3d68-b420-4e07-a4e3-3019e7cebe6f";
    mockMemB.delete.mockResolvedValue({ message: "deleted" });
    await execute({ action: "delete", memory_id: fullId });
    expect(mockMemB.delete).toHaveBeenCalledWith(fullId);
  });
});
