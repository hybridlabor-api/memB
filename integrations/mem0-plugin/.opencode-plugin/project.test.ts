import { describe, expect, test } from "bun:test";
import { parseProjectFromRemote } from "./project";

describe("parseProjectFromRemote", () => {
  test("ssh remote with a custom host alias (github.com-work)", () => {
    expect(parseProjectFromRemote("git@github.com-memb:membai/memb.git")).toBe("membai-memb");
  });

  test("standard scp-style ssh remote", () => {
    expect(parseProjectFromRemote("git@github.com:openai/gym.git")).toBe("openai-gym");
  });

  test("https remote", () => {
    expect(parseProjectFromRemote("https://github.com/membai/memb.git")).toBe("membai-memb");
  });

  test("https remote without a .git suffix", () => {
    expect(parseProjectFromRemote("https://gitlab.com/acme/widgets")).toBe("acme-widgets");
  });

  test("trailing slash is ignored", () => {
    expect(parseProjectFromRemote("https://github.com/acme/widgets/")).toBe("acme-widgets");
  });

  test("returns null when no owner/repo can be parsed", () => {
    expect(parseProjectFromRemote("not-a-remote")).toBeNull();
    expect(parseProjectFromRemote("")).toBeNull();
  });
});
