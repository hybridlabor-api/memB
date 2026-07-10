export const DREAM_PROTOCOL = `<memb-dream>
You are running memory consolidation. Complete these steps using the memb_memory tool:

1. ORIENT — Call memb_memory with action "get_all" to list all memories. Count by category. Note oldest/newest.

2. GATHER TARGETS — Review each memory. Classify as:
   - DELETE: sensitive information (API keys, passwords, tokens), expired/stale entries, noise, redundant operational details
   - MERGE: near-duplicates (same fact stated differently). Keep the better-worded one, delete the other.
   - REWRITE: vague, first-person, or poorly-categorized entries. Use memb_memory "add" with improved text, then "delete" the old one.
   - KEEP: everything else.
   Skip any memory starting with "[PINNED]".

3. CONSOLIDATE — Execute the changes:
   - Delete stale/duplicate entries
   - For merges: add the merged text, delete both originals
   - For rewrites: add improved version, delete original

4. REPORT — Summarize: how many reviewed, deleted, merged, rewritten, final count.

Quality targets: zero sensitive data stored, zero duplicates, all entries are atomic (one fact each), 15-50 words each.
After consolidation, respond to the user's message normally.
</memb-dream>`;
