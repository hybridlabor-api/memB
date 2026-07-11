import os
import sqlite3
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any

db_path = os.path.expanduser("~/.MemBDB/memb.db")

app = FastAPI(title="memB Semantic Brain Visualizer")

# D3.js interactive HTML5 Canvas dashboard template matching Orca SuperBrain styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>memB Semantic Brain Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #020204;
            --dark-surface: rgba(10, 10, 15, 0.55);
            --accent-teal: #00F2FE;
            --accent-purple: #6B21A8;
            --accent-pink: #BD00FF;
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --text-muted: #4a5568;
            --glass-border: rgba(0, 242, 254, 0.15);
            --glow-color: rgba(189, 0, 255, 0.4);
        }

        body {
            margin: 0;
            padding: 0;
            background: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(107, 33, 168, 0.15), transparent 45%),
                radial-gradient(circle at 85% 30%, rgba(0, 242, 254, 0.12), transparent 40%);
        }

        header {
            position: absolute;
            top: 24px;
            left: 24px;
            z-index: 10;
            display: flex;
            align-items: center;
            gap: 15px;
            pointer-events: none;
        }

        h1 {
            margin: 0;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            background: linear-gradient(to right, #ffffff, var(--accent-teal));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 10px;
            color: var(--accent-teal);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border: 1px solid var(--glass-border);
            padding: 4px 10px;
            border-radius: 20px;
            background: rgba(0, 242, 254, 0.05);
            backdrop-filter: blur(8px);
        }

        #graph-container {
            width: 100vw;
            height: 100vh;
            position: absolute;
            top: 0;
            left: 0;
        }

        canvas {
            display: block;
            width: 100%;
            height: 100%;
            cursor: grab;
        }

        canvas:active {
            cursor: grabbing;
        }

        /* Glassmorphism Sidebar */
        .sidebar {
            position: absolute;
            top: 24px;
            right: 24px;
            bottom: 24px;
            width: 380px;
            background: var(--dark-surface);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            z-index: 10;
            padding: 28px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            animation: borderPulse 8s infinite alternate;
        }

        @keyframes borderPulse {
            0% { border-color: rgba(0, 242, 254, 0.15); }
            50% { border-color: rgba(189, 0, 255, 0.25); }
            100% { border-color: rgba(0, 242, 254, 0.15); }
        }

        .sidebar-header {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--accent-teal);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Search Bar styling */
        .search-box {
            position: relative;
            display: flex;
            align-items: center;
        }

        .search-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 10px 16px;
            font-size: 13px;
            color: var(--text-primary);
            outline: none;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            border-color: var(--accent-teal);
            background: rgba(255, 255, 255, 0.06);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.15);
        }

        .node-details {
            flex-grow: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .detail-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.04);
            padding: 18px;
            border-radius: 16px;
            transition: all 0.3s ease;
        }

        .detail-card:hover {
            background: rgba(255, 255, 255, 0.04);
            border-color: rgba(255, 255, 255, 0.08);
        }

        .detail-label {
            font-size: 10px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
        }

        .detail-value {
            font-size: 13.5px;
            line-height: 1.6;
        }

        .badge {
            display: inline-block;
            font-size: 10px;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .badge-godmode {
            background: rgba(0, 242, 254, 0.1);
            color: var(--accent-teal);
            border: 1px solid rgba(0, 242, 254, 0.25);
        }

        .badge-project {
            background: rgba(189, 0, 255, 0.1);
            color: #BD00FF;
            border: 1px solid rgba(189, 0, 255, 0.25);
        }

        /* Helper controls overlay */
        .controls-overlay {
            position: absolute;
            bottom: 24px;
            left: 24px;
            font-size: 10px;
            color: var(--text-secondary);
            display: flex;
            gap: 15px;
            background: var(--dark-surface);
            backdrop-filter: blur(12px);
            padding: 10px 16px;
            border-radius: 20px;
            border: 1px solid var(--glass-border);
            pointer-events: none;
            letter-spacing: 0.5px;
        }

        .controls-overlay span {
            display: flex;
            align-items: center;
            gap: 6px;
        }
    </style>
</head>
<body>

    <header>
        <h1>memB OS SuperBrain</h1>
        <div class="subtitle">Neural Knowledge Graph</div>
    </header>

    <div id="graph-container">
        <canvas id="graph-canvas"></canvas>
    </div>

    <div class="controls-overlay">
        <span>🖱️ Drag to pan / nodes</span>
        <span>🔍 Scroll to zoom</span>
        <span>🔴 Click node to inspect</span>
    </div>

    <div class="sidebar">
        <div class="sidebar-header">
            <span>Graph Inspector</span>
        </div>
        
        <div class="search-box">
            <input type="text" id="search-input" class="search-input" placeholder="Search memories...">
        </div>

        <div class="node-details" id="details">
            <div style="color: var(--text-secondary); text-align: center; margin-top: 60px; font-size: 13px;">
                Select a node to inspect payload details.
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("graph-canvas");
        const ctx = canvas.getContext("2d");
        let width = canvas.clientWidth;
        let height = canvas.clientHeight;

        // Resize handler
        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            
            // Adjust for HighDPI screens
            const dpr = window.devicePixelRatio || 1;
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);
        }
        window.addEventListener("resize", resize);
        resize();

        let transform = d3.zoomIdentity;
        let nodes = [];
        let links = [];
        let simulation;
        let selectedNode = null;
        let hoveredNode = null;
        let searchFilter = "";

        // Set up zoom behavior
        const zoomBehavior = d3.zoom()
            .scaleExtent([0.15, 3])
            .on("zoom", (event) => {
                transform = event.transform;
                ticked();
            });
        d3.select(canvas).call(zoomBehavior);

        // Fetch graph data
        fetch('/api/graph')
            .then(res => res.json())
            .then(data => {
                nodes = data.nodes;
                links = data.links;
                initSimulation();
            });

        function initSimulation() {
            // Pre-calculate node degrees
            nodes.forEach(n => {
                n.degree = links.filter(l => l.source === n.id || l.target === n.id).length;
            });

            // Set up forces following Technical Architect formulas
            simulation = d3.forceSimulation(nodes)
                .force("charge", d3.forceManyBody()
                    .strength(d => -300 * Math.pow((d.degree || 1) + 1, 1.1)) // Repulsion scaled by degree
                    .distanceMax(600)
                )
                .force("link", d3.forceLink(links)
                    .id(d => d.id)
                    .distance(link => {
                        const srcNode = nodes.find(n => n.id === link.source || n.id === link.source.id);
                        const tgtNode = nodes.find(n => n.id === link.target || n.id === link.target.id);
                        const srcD = srcNode ? srcNode.degree : 1;
                        const tgtD = tgtNode ? tgtNode.degree : 1;
                        return 120 + 15 * (srcD + tgtD); // Expanded distances to prevent tight balling
                    })
                    .strength(link => {
                        const srcNode = nodes.find(n => n.id === link.source || n.id === link.source.id);
                        const tgtNode = nodes.find(n => n.id === link.target || n.id === link.target.id);
                        const srcD = srcNode ? srcNode.degree : 1;
                        const tgtD = tgtNode ? tgtNode.degree : 1;
                        return 0.85 / Math.min(srcD, tgtD); // Softer attraction on complex links
                    })
                )
                .force("collide", d3.forceCollide()
                    .radius(d => {
                        const baseR = d.type === 'hub' ? 18 : 8;
                        return baseR + 25; // Dynamic boundary separation padding
                    })
                    .iterations(2)
                )
                .force("x", d3.forceX(width / 2).strength(0.04))
                .force("y", d3.forceY(height / 2).strength(0.04))
                .on("tick", ticked);

            // Pre-warm the simulation ticks to prevent chaotic jiggling at startup
            simulation.stop();
            for (let i = 0; i < 110; ++i) {
                simulation.tick();
            }
            simulation.alpha(0.08).restart();

            // Set up event handlers
            setupEventHandlers();
        }

        // Render Canvas Tick Frame
        function ticked() {
            ctx.save();
            ctx.clearRect(0, 0, width, height);
            ctx.translate(transform.x, transform.y);
            ctx.scale(transform.k, transform.k);

            // 1. Draw Connection Links
            ctx.lineWidth = 1;
            links.forEach(l => {
                const source = typeof l.source === 'object' ? l.source : nodes.find(n => n.id === l.source);
                const target = typeof l.target === 'object' ? l.target : nodes.find(n => n.id === l.target);
                if (!source || !target) return;

                // Edge transparency / highlight focus
                let alpha = 0.08;
                if (selectedNode) {
                    const isConnected = (source.id === selectedNode.id || target.id === selectedNode.id);
                    alpha = isConnected ? 0.35 : 0.02;
                } else if (hoveredNode) {
                    const isConnected = (source.id === hoveredNode.id || target.id === hoveredNode.id);
                    alpha = isConnected ? 0.45 : 0.03;
                }

                ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
                ctx.beginPath();
                ctx.moveTo(source.x, source.y);
                ctx.lineTo(target.x, target.y);
                ctx.stroke();
            });

            // 2. Draw Nodes
            nodes.forEach(n => {
                const isHub = n.type === 'hub';
                const isSelected = selectedNode && selectedNode.id === n.id;
                const isHovered = hoveredNode && hoveredNode.id === n.id;
                const isSearchMatch = searchFilter && n.payload && n.payload.data.toLowerCase().includes(searchFilter.toLowerCase());

                let radius = isHub ? 10 : 5;
                if (isHovered) radius *= 1.25;
                if (isSelected) radius *= 1.35;

                // Fading unselected nodes
                let opacity = 1.0;
                if (selectedNode) {
                    const isConnected = n.id === selectedNode.id || links.some(l => 
                        (l.source.id === selectedNode.id && l.target.id === n.id) ||
                        (l.target.id === selectedNode.id && l.source.id === n.id)
                    );
                    opacity = isConnected ? 1.0 : 0.25;
                }

                ctx.save();
                ctx.globalAlpha = opacity;

                // Draw neon glow for search matches or selected nodes
                if (isSearchMatch || isSelected || isHovered) {
                    ctx.shadowBlur = isSearchMatch ? 20 : 12;
                    ctx.shadowColor = isSearchMatch ? "#ff007f" : (isHub ? "#00F2FE" : "#BD00FF");
                }

                // Draw Shape Fills
                ctx.fillStyle = isSearchMatch ? "#ff007f" : n.color;
                ctx.beginPath();
                ctx.arc(n.x, n.y, radius, 0, 2 * Math.PI);
                ctx.fill();

                // Inner core for hub nodes
                if (isHub) {
                    ctx.strokeStyle = "rgba(255, 255, 255, 0.8)";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                }

                ctx.restore();
            });

            // 3. Draw Labels (Layered on top of nodes to avoid overlapping rendering artifacts)
            nodes.forEach(n => {
                const isHub = n.type === 'hub';
                const isSelected = selectedNode && selectedNode.id === n.id;
                const isHovered = hoveredNode && hoveredNode.id === n.id;
                const isSearchMatch = searchFilter && n.payload && n.payload.data.toLowerCase().includes(searchFilter.toLowerCase());
                
                // Visibility rules: Hubs and Search Matches always show, leaf labels show only on hover/select
                const showLabel = isHub || isHovered || isSelected || isSearchMatch;

                if (showLabel) {
                    let opacity = 1.0;
                    if (selectedNode && !isHub && !isSelected) {
                        const isConnected = links.some(l => 
                            (l.source.id === selectedNode.id && l.target.id === n.id) ||
                            (l.target.id === selectedNode.id && l.source.id === n.id)
                        );
                        opacity = isConnected ? 1.0 : 0.2;
                    }

                    ctx.save();
                    ctx.globalAlpha = opacity;
                    ctx.font = isHub ? "bold 11px 'Inter'" : "400 10.5px 'Inter'";
                    ctx.fillStyle = isHub ? "#ffffff" : "#cbd5e0";

                    // Text bounds sizing
                    const text = n.label;
                    const textWidth = ctx.measureText(text).width;

                    // Draw clean dark back pill behind the text to avoid overlaps with edge lines
                    ctx.fillStyle = "rgba(10, 10, 15, 0.85)";
                    ctx.beginPath();
                    ctx.roundRect(n.x + 12 - 6, n.y - 8, textWidth + 12, 16, 8);
                    ctx.fill();

                    // Render text
                    ctx.fillStyle = isHub ? "#00F2FE" : "#ffffff";
                    ctx.fillText(text, n.x + 12, n.y + 3);
                    ctx.restore();
                }
            });

            ctx.restore();
        }

        // Dragging & Click Event Handler Setup
        function setupEventHandlers() {
            // Drag configurations
            d3.select(canvas).call(d3.drag()
                .container(canvas)
                .subject(getEventNode)
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended)
            );

            // Node selection on click
            canvas.addEventListener("click", (event) => {
                const rect = canvas.getBoundingClientRect();
                const mouseX = event.clientX - rect.left;
                const mouseY = event.clientY - rect.top;

                // Map screen coordinate to canvas coordinate space
                const x = (mouseX - transform.x) / transform.k;
                const y = (mouseY - transform.y) / transform.k;

                const node = simulation.find(x, y, 30);
                if (node) {
                    selectedNode = node;
                    showDetails(node);
                } else {
                    selectedNode = null;
                    resetDetails();
                }
                ticked();
            });

            // Hover node trigger
            canvas.addEventListener("mousemove", (event) => {
                const rect = canvas.getBoundingClientRect();
                const mouseX = event.clientX - rect.left;
                const mouseY = event.clientY - rect.top;

                const x = (mouseX - transform.x) / transform.k;
                const y = (mouseY - transform.y) / transform.k;

                const node = simulation.find(x, y, 20);
                if (node !== hoveredNode) {
                    hoveredNode = node;
                    ticked();
                }
            });

            // Search Filter updates
            document.getElementById("search-input").addEventListener("input", (e) => {
                searchFilter = e.target.value;
                ticked();
            });
        }

        function getEventNode(event) {
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.sourceEvent.clientX - rect.left;
            const mouseY = event.sourceEvent.clientY - rect.top;

            const x = (mouseX - transform.x) / transform.k;
            const y = (mouseY - transform.y) / transform.k;

            return simulation.find(x, y, 25);
        }

        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.1).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        function showDetails(d) {
            const detailsDiv = document.getElementById("details");
            if (d.type === 'hub') {
                detailsDiv.innerHTML = `
                    <div class="detail-card">
                        <div class="detail-label">Cluster Category</div>
                        <div class="detail-value">
                            <span class="badge badge-godmode">${d.label}</span>
                        </div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">Node Type</div>
                        <div class="detail-value" style="font-weight: 600; color: var(--accent-teal);">Topic Group</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">Connections</div>
                        <div class="detail-value">Linked to ${d.degree} memory statements. Click a connected leaf node to inspect individual facts.</div>
                    </div>
                `;
            } else {
                detailsDiv.innerHTML = `
                    <div class="detail-card">
                        <div class="detail-label">Memory Statement</div>
                        <div class="detail-value" style="font-size: 14.5px; font-weight: 600; color: #fff;">${d.payload.data}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">Scope Tag</div>
                        <div class="detail-value">
                            <span class="badge ${d.payload.category === 'godmode' ? 'badge-godmode' : 'badge-project'}">
                                ${d.payload.category}
                            </span>
                        </div>
                    </div>
                    ${d.payload.project_id ? `
                        <div class="detail-card">
                            <div class="detail-label">Project Base</div>
                            <div class="detail-value" style="color: var(--accent-teal); font-weight: 700;">${d.payload.project_id}</div>
                        </div>
                    ` : ''}
                    <div class="detail-card">
                        <div class="detail-label">Memory ID</div>
                        <div class="detail-value" style="font-family: monospace; font-size: 11px; color: var(--text-secondary); word-break: break-all;">${d.id}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">Import Time</div>
                        <div class="detail-value" style="font-size: 11px; color: var(--text-secondary);">${d.payload.created_at || 'N/A'}</div>
                    </div>
                `;
            }
        }

        function resetDetails() {
            document.getElementById("details").innerHTML = `
                <div style="color: var(--text-secondary); text-align: center; margin-top: 60px; font-size: 13px;">
                    Select a node to inspect payload details.
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE

@app.get("/api/graph")
def get_graph():
    if not os.path.exists(db_path):
        return {"nodes": [], "links": []}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, payload FROM memb_vectors")
        rows = cursor.fetchall()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    
    nodes = []
    links = []
    
    # Static hub nodes
    hubs = {
        "hub_godmode": {"id": "hub_godmode", "label": "General Knowledge", "type": "hub", "color": "#00F2FE", "size": 18},
    }
    
    for row_id, payload_str in rows:
        try:
            payload = json.loads(payload_str)
        except Exception:
            continue
            
        category = payload.get("category", "godmode")
        project_id = payload.get("project_id")
        text = payload.get("data", "Memory record")
        
        # Determine mapping leaf
        leaf_node = {
            "id": row_id,
            "label": text,
            "type": "leaf",
            "color": "#a0a0a0",
            "size": 6,
            "payload": payload
        }
        nodes.append(leaf_node)
        
        # Link to Hub
        if category == "godmode":
            links.append({"source": "hub_godmode", "target": row_id})
            leaf_node["color"] = "#00F2FE" # Cyan accent for global
        else:
            # Map dynamic project leaves
            proj_key = f"hub_{project_id}" if project_id else "hub_other"
            proj_label = project_id if project_id else "Other Projects"
            
            if proj_key not in hubs:
                hubs[proj_key] = {
                    "id": proj_key,
                    "label": proj_label,
                    "type": "hub",
                    "color": "#BD00FF", # Purple neon accent for projects
                    "size": 14
                }
            
            links.append({"source": proj_key, "target": row_id})
            leaf_node["color"] = "#BD00FF" # Purple/pink accent for project facts
            
    # Combine hubs and leaf nodes
    combined_nodes = list(hubs.values()) + nodes
    
    # Add a root link between Project hubs and Godmode center to form the flower layout
    for h_id in hubs:
        if h_id != "hub_godmode":
            links.append({"source": "hub_godmode", "target": h_id})
            
    return {"nodes": combined_nodes, "links": links}

if __name__ == "__main__":
    print("=== memB Brain Graph Web Server ===")
    print("Dashboard address: http://localhost:8088")
    uvicorn.run(app, host="127.0.0.1", port=8088, log_level="info")
