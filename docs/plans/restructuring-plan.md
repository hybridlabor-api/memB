# memB & OpenWiki Restructuring Plan

## Overview
This plan addresses the critical architectural flaws in the `memB` and `openwiki` implementations that caused infinite subagent loops and resulted in an unpolished "AI slop" visualizer. 

We will execute this using Subagent-Driven Development.

## Task 1: Fix OpenWiki Agent Loop & Ecosystem Triggers
**Context**: Antigravity agents are getting stuck in infinite loops spawning `Synchronize Documentation` subagents. This is likely caused by the `openwiki-skill/SKILL.md` or project-level `agent.md` files encouraging subagent spawning for trivial doc syncs.
**Instructions**:
1. Review `/Users/timrennings/.gemini/config/skills/openwiki-skill/SKILL.md`. Ensure there is an absolute, strict ban on using `invoke_subagent` for documentation synchronization.
2. Review `/Users/timrennings/agent-Projects/memB/agent.md` (and `.openwiki` configurations). Remove any instructions that tell the agent to autonomously spawn subagents on commits or file changes.
3. If necessary, introduce a silent, deterministic bash/python script or git hook approach that performs the OpenWiki sync strictly in the background WITHOUT LLM/agent intervention.

## Task 2: Architectural Teardown & Backend Restructuring for memB Visualizer
**Context**: The current `/Users/timrennings/agent-Projects/memB/scripts/visualizer.py` is a messy monolith that mixes backend HTTP serving and frontend HTML/JS rendering. It needs to be cleanly separated.
**Instructions**:
1. Delete the existing `/Users/timrennings/agent-Projects/memB/scripts/visualizer.py`.
2. Create a new, clean Python backend using FastAPI (or a robust HTTP server) at `src/backend/server.py`.
3. The backend should cleanly read the SQLite database (or mock structure if no DB exists yet) and expose `/api/nodes` and `/api/edges` as clean JSON.
4. Ensure robust error handling, typing, and standard REST practices.

## Task 3: Premium Frontend Implementation (Orca Super Brain Style)
**Context**: The user explicitly requested an "Orca Super Brain" style visualization: a horror/dark aesthetic, fade-in on hover/select, a symmetric flower radial layout, and a highly polished UI. No "AI slop".
**Instructions**:
1. Create a dedicated frontend directory at `src/frontend/`.
2. Implement a modern HTML/CSS/JS frontend (Vanilla JS with D3.js or a lightweight build setup).
3. Implement the strict design requirements:
   - Deep dark/horror aesthetic (blacks, deep grays, subtle glowing accents).
   - Symmetric Flower Radial Layout for nodes.
   - Elements should fade in gracefully on hover or selection (no jarring pop-ins).
   - High performance, smooth physics, and a premium "wow" factor.
4. Ensure the frontend fetches data cleanly from the backend API.
5. Create a clean startup script `start.sh` in the root to launch both backend and frontend cleanly.
