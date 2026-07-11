import os
import sqlite3
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any

db_path = os.path.expanduser("~/.MemBDB/memb.db")

app = FastAPI(title="memB Semantic Brain Visualizer")

# D3.js interactive HTML5 Canvas dashboard template matching the flower-like clustered layout
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>memB OS Memory Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #050508;
            --dark-surface: rgba(10, 10, 15, 0.6);
            --accent-teal: #00F2FE;
            --accent-purple: #6B21A8;
            --accent-pink: #BD00FF;
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --glass-border: rgba(107, 33, 168, 0.2);
            --glow-color: rgba(107, 33, 168, 0.5);
        }

        body {
            margin: 0;
            padding: 0;
            background: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(107, 33, 168, 0.18), transparent 60%);
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
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            background: linear-gradient(to right, #ffffff, var(--accent-teal));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 9px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border: 1px solid var(--glass-border);
            padding: 4px 10px;
            border-radius: 20px;
            background: rgba(107, 33, 168, 0.1);
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
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            animation: borderPulse 8s infinite alternate;
        }

        @keyframes borderPulse {
            0% { border-color: rgba(107, 33, 168, 0.25); }
            50% { border-color: rgba(0, 242, 254, 0.25); }
            100% { border-color: rgba(107, 33, 168, 0.25); }
        }

        .sidebar-header {
            font-size: 13px;
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
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.03);
            padding: 18px;
            border-radius: 16px;
            transition: all 0.3s ease;
        }

        .detail-card:hover {
            background: rgba(255, 255, 255, 0.03);
            border-color: rgba(255, 255, 255, 0.06);
        }

        .detail-label {
            font-size: 9px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
        }

        .detail-value {
            font-size: 13px;
            line-height: 1.6;
        }

        .badge {
            display: inline-block;
            font-size: 9px;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .badge-godmode {
            background: rgba(107, 33, 168, 0.2);
            color: #b794f4;
            border: 1px solid rgba(107, 33, 168, 0.4);
        }

        .badge-project {
            background: rgba(0, 242, 254, 0.1);
            color: var(--accent-teal);
            border: 1px solid rgba(0, 242, 254, 0.25);
        }

        .controls-overlay {
            position: absolute;
            bottom: 24px;
            left: 24px;
            font-size: 9px;
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
    </style>
</head>
<body>

    <header>
        <h1>memB OS Neural Graph</h1>
        <div class="subtitle">Structured Flower Layout</div>
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

        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
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

        const zoomBehavior = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                transform = event.transform;
                ticked();
            });
        d3.select(canvas).call(zoomBehavior);

        // Fetch data
        fetch('/api/graph')
            .then(res => res.json())
            .then(data => {
                nodes = data.nodes;
                links = data.links;
                initSimulation();
            });

        function initSimulation() {
            const centerX = width / 2;
            const centerY = height / 2;

            // 1. Separate hub nodes (topics) and leaf nodes
            const hubNodes = nodes.filter(n => n.type === 'hub');
            const projectHubs = hubNodes.filter(h => h.id !== 'hub_godmode');
            const numProjects = projectHubs.length;

            // 2. Position Hubs radially around the center to force the flower petal anchors
            // Godmode hub sits directly at the center
            const centerHub = nodes.find(n => n.id === 'hub_godmode');
            if (centerHub) {
                centerHub.fx = centerX;
                centerHub.fy = centerY;
            }

            // Radial distribution of project hubs
            const radialDistance = 220; // Radius of the flower center
            projectHubs.forEach((hub, idx) => {
                const angle = (2 * Math.PI * idx) / (numProjects || 1);
                hub.fx = centerX + radialDistance * Math.cos(angle);
                hub.fy = centerY + radialDistance * Math.sin(angle);
            });

            // 3. Link each leaf node to its parent hub and coordinate radial pull coordinates
            nodes.forEach(n => {
                if (n.type === 'leaf') {
                    // Find which hub this leaf connects to
                    const link = links.find(l => l.target === n.id);
                    if (link) {
                        const parentHubId = typeof link.source === 'object' ? link.source.id : link.source;
                        const parentHub = nodes.find(h => h.id === parentHubId);
                        if (parentHub) {
                            n.hubX = parentHub.fx;
                            n.hubY = parentHub.fy;
                            n.parentHubId = parentHubId;
                        }
                    }
                }
            });

            // Calculate degrees
            nodes.forEach(n => {
                n.degree = links.filter(l => l.source === n.id || l.target === n.id).length;
            });

            // 4. Custom D3 forces configured for dense petal-like structures
            simulation = d3.forceSimulation(nodes)
                // Mild repulsion inside the petal cloud to keep them puffy
                .force("charge", d3.forceManyBody()
                    .strength(d => d.type === 'hub' ? -600 : -25)
                    .distanceMax(250)
                )
                // Links pull leaves tightly to their parent hub to form circular clusters
                .force("link", d3.forceLink(links)
                    .id(d => d.id)
                    .distance(link => {
                        const tgtNode = nodes.find(n => n.id === link.target || n.id === link.target.id);
                        return tgtNode && tgtNode.type === 'leaf' ? 35 : 180; // Short links inside clusters
                    })
                    .strength(0.85)
                )
                // Collision prevents nodes from directly layering over each other
                .force("collide", d3.forceCollide()
                    .radius(d => d.type === 'hub' ? 30 : 6.5)
                    .strength(0.9)
                )
                // Force X/Y pulling leaves towards their specific cluster sub-hub anchor
                .force("clusterX", d3.forceX(d => d.type === 'leaf' ? d.hubX : centerX).strength(d => d.type === 'leaf' ? 0.35 : 0.05))
                .force("clusterY", d3.forceY(d => d.type === 'leaf' ? d.hubY : centerY).strength(d => d.type === 'leaf' ? 0.35 : 0.05))
                .on("tick", ticked);

            // Pre-warm the simulation so the flower layout settles perfectly on load
            simulation.stop();
            for (let i = 0; i < 180; ++i) {
                simulation.tick();
            }
            simulation.alpha(0.05).restart();

            setupEventHandlers();
        }

        function ticked() {
            ctx.save();
            ctx.clearRect(0, 0, width, height);
            ctx.translate(transform.x, transform.y);
            ctx.scale(transform.k, transform.k);

            // 1. Draw Links
            ctx.lineWidth = 0.8;
            links.forEach(l => {
                const source = typeof l.source === 'object' ? l.source : nodes.find(n => n.id === l.source);
                const target = typeof l.target === 'object' ? l.target : nodes.find(n => n.id === l.target);
                if (!source || !target) return;

                // Ultra-translucent edges to emphasize the cluster cloud
                let alpha = 0.06;
                if (selectedNode) {
                    const isConnected = (source.id === selectedNode.id || target.id === selectedNode.id);
                    alpha = isConnected ? 0.4 : 0.01;
                } else if (hoveredNode) {
                    const isConnected = (source.id === hoveredNode.id || target.id === hoveredNode.id);
                    alpha = isConnected ? 0.45 : 0.015;
                }

                ctx.strokeStyle = source.type === 'hub' && target.type === 'hub'
                    ? `rgba(107, 33, 168, ${alpha * 2})` // Spine lines
                    : `rgba(255, 255, 255, ${alpha})`;  // Petal links

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

                // Nodes styled as dense silver-white glowing dots
                let radius = isHub ? (n.id === 'hub_godmode' ? 14 : 9) : 3.8;
                if (isHovered) radius *= 1.3;
                if (isSelected) radius *= 1.4;

                let opacity = isHub ? 0.95 : 0.8;
                if (selectedNode) {
                    const isConnected = n.id === selectedNode.id || links.some(l => 
                        (l.source.id === selectedNode.id && l.target.id === n.id) ||
                        (l.target.id === selectedNode.id && l.source.id === n.id)
                    );
                    opacity = isConnected ? 1.0 : 0.15;
                }

                ctx.save();
                ctx.globalAlpha = opacity;

                // Glowing shadows for hover, selection, and search matches
                if (isSearchMatch || isSelected || isHovered) {
                    ctx.shadowBlur = isSearchMatch ? 18 : 10;
                    ctx.shadowColor = isSearchMatch ? "#ff007f" : (isHub ? "#6B21A8" : "#ffffff");
                }

                // Core Fills matching Orca color scheme
                if (isHub) {
                    ctx.fillStyle = n.color;
                    ctx.beginPath();
                    ctx.arc(n.x, n.y, radius, 0, 2 * Math.PI);
                    ctx.fill();
                    
                    // Outer neon border ring for hubs
                    ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
                    ctx.lineWidth = 1;
                    ctx.stroke();
                } else {
                    // Leaf nodes are dense silver-white particles
                    ctx.fillStyle = isSearchMatch ? "#ff007f" : "rgba(240, 240, 255, 0.9)";
                    ctx.beginPath();
                    ctx.arc(n.x, n.y, radius, 0, 2 * Math.PI);
                    ctx.fill();
                }

                ctx.restore();
            });

            // 3. Draw Labels (Fades in on hover/select or search match)
            nodes.forEach(n => {
                const isHub = n.type === 'hub';
                const isSelected = selectedNode && selectedNode.id === n.id;
                const isHovered = hoveredNode && hoveredNode.id === n.id;
                const isSearchMatch = searchFilter && n.payload && n.payload.data.toLowerCase().includes(searchFilter.toLowerCase());
                
                // Show label only if hub or active hover/selection
                const showLabel = isHub || isHovered || isSelected || isSearchMatch;

                if (showLabel) {
                    let opacity = 1.0;
                    if (selectedNode && !isHub && !isSelected) {
                        const isConnected = links.some(l => 
                            (l.source.id === selectedNode.id && l.target.id === n.id) ||
                            (l.target.id === selectedNode.id && l.source.id === n.id)
                        );
                        opacity = isConnected ? 1.0 : 0.15;
                    }

                    ctx.save();
                    ctx.globalAlpha = opacity;
                    ctx.font = isHub ? "bold 10px 'Inter'" : "300 10px 'Inter'";
                    
                    const text = n.label;
                    const textWidth = ctx.measureText(text).width;

                    // Draw pill background
                    ctx.fillStyle = "rgba(5, 5, 8, 0.9)";
                    ctx.beginPath();
                    ctx.roundRect(n.x + 10 - 5, n.y - 7, textWidth + 10, 14, 6);
                    ctx.fill();

                    // Text fill colors
                    ctx.fillStyle = isHub 
                        ? (n.id === 'hub_godmode' ? "#b794f4" : "#00F2FE") 
                        : "#ffffff";
                    ctx.fillText(text, n.x + 10, n.y + 3);
                    ctx.restore();
                }
            });

            ctx.restore();
        }

        function setupEventHandlers() {
            d3.select(canvas).call(d3.drag()
                .container(canvas)
                .subject(getEventNode)
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended)
            );

            canvas.addEventListener("click", (event) => {
                const rect = canvas.getBoundingClientRect();
                const mouseX = event.clientX - rect.left;
                const mouseY = event.clientY - rect.top;

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
            if (!event.active) simulation.alphaTarget(0.05).restart();
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
        "hub_godmode": {"id": "hub_godmode", "label": "GODMODE ALL NODES", "type": "hub", "color": "#6B21A8", "size": 18}, # Purple center as in screenshot
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
            "color": "rgba(240, 240, 255, 0.95)", # Dense white particles
            "size": 4,
            "payload": payload
        }
        nodes.append(leaf_node)
        
        # Link to Hub
        if category == "godmode":
            links.append({"source": "hub_godmode", "target": row_id})
        else:
            proj_key = f"hub_{project_id}" if project_id else "hub_other"
            proj_label = project_id if project_id else "Other Projects"
            
            if proj_key not in hubs:
                hubs[proj_key] = {
                    "id": proj_key,
                    "label": proj_label,
                    "type": "hub",
                    "color": "#00F2FE", # Cyan sub-hubs (petals)
                    "size": 12
                }
            
            links.append({"source": proj_key, "target": row_id})
            
    # Combine hubs and leaf nodes
    combined_nodes = list(hubs.values()) + nodes
    
    # Add spine link between project sub-hubs and the central godmode core
    for h_id in hubs:
        if h_id != "hub_godmode":
            links.append({"source": "hub_godmode", "target": h_id})
            
    return {"nodes": combined_nodes, "links": links}

if __name__ == "__main__":
    print("=== memB Brain Graph Web Server ===")
    print("Dashboard address: http://localhost:8088")
    uvicorn.run(app, host="127.0.0.1", port=8088, log_level="info")
