document.addEventListener('DOMContentLoaded', async () => {
    const width = window.innerWidth;
    const height = window.innerHeight;

    const svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .call(d3.zoom().scaleExtent([0.1, 4]).on('zoom', (event) => {
            container.attr('transform', event.transform);
        }))
        .on('click', () => {
            // Click on background resets
            resetHighlight();
        });

    const container = svg.append('g');

    let nodes = [];
    let edges = [];
    
    // Fetch data
    try {
        const nodesRes = await fetch('/api/nodes');
        const edgesRes = await fetch('/api/edges');
        
        if (nodesRes.ok && edgesRes.ok) {
            nodes = await nodesRes.json();
            edges = await edgesRes.json();
        } else {
            console.warn("API returned error, using mock data for demonstration");
            generateMockData();
        }
    } catch (e) {
        console.warn("API unavailable, using mock data for demonstration", e);
        generateMockData();
    }

    function generateMockData() {
        const mockCategories = ['Core', 'Plugins', 'UI', 'Database', 'Auth', 'Network', 'AI'];
        for (let i = 0; i < 120; i++) {
            nodes.push({
                id: `node_${i}`,
                label: `Node ${i}`,
                category: mockCategories[i % mockCategories.length],
                size: Math.random() * 6 + 3,
                description: `This is a mock description for node ${i}.`
            });
        }
        for (let i = 0; i < 150; i++) {
            const source = nodes[Math.floor(Math.random() * nodes.length)].id;
            const target = nodes[Math.floor(Math.random() * nodes.length)].id;
            if (source !== target) {
                edges.push({ source, target, value: Math.random() * 3 });
            }
        }
    }

    // Process nodes for Symmetric Flower Radial Layout
    const groups = {};
    nodes.forEach(n => {
        const groupKey = n.category || n.project || n.type || 'default';
        if (!groups[groupKey]) {
            groups[groupKey] = [];
        }
        groups[groupKey].push(n);
        n.groupKey = groupKey;
    });

    const groupKeys = Object.keys(groups);
    const numGroups = groupKeys.length || 1;
    
    // Calculate focal points for each group to form petals of the flower
    const focalPoints = {};
    const radius = Math.min(width, height) * 0.35;
    
    groupKeys.forEach((key, i) => {
        const angle = (i / numGroups) * 2 * Math.PI;
        focalPoints[key] = {
            x: width / 2 + Math.cos(angle) * radius,
            y: height / 2 + Math.sin(angle) * radius
        };
    });

    // Map edges to source and target objects
    const linkData = edges.map(d => Object.create({
        ...d,
        source: nodes.find(n => n.id === d.source) || d.source,
        target: nodes.find(n => n.id === d.target) || d.target
    })).filter(l => typeof l.source === 'object' && typeof l.target === 'object');

    // D3 Simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(linkData).id(d => d.id).distance(40).strength(0.5))
        .force('charge', d3.forceManyBody().strength(-250))
        .force('collide', d3.forceCollide().radius(d => (d.size || 5) + 8).iterations(3))
        // Radial forces pulling towards group focal points
        .force('x', d3.forceX(d => focalPoints[d.groupKey]?.x || width/2).strength(0.12))
        .force('y', d3.forceY(d => focalPoints[d.groupKey]?.y || height/2).strength(0.12))
        // Gentle pull to center to keep it unified
        .force('center', d3.forceCenter(width / 2, height / 2).strength(0.02));

    // Draw Links
    const link = container.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(linkData)
        .join('line')
        .attr('class', 'link')
        .attr('stroke-width', d => Math.max(1, Math.sqrt(d.value || 1)));

    // Draw Nodes
    const node = container.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('class', 'node')
        .call(drag(simulation));

    node.append('circle')
        .attr('r', d => (d.size || 5) + 3);

    node.append('text')
        .attr('class', 'node-label')
        .attr('dx', d => (d.size || 5) + 8)
        .attr('dy', 4)
        .text(d => d.label || d.name || d.id);

    // Interaction State
    let activeNode = null;

    node.on('mouseover', function(event, d) {
        if (activeNode && activeNode !== d) return;
        highlightNode(d);
    });

    node.on('mouseout', function(event, d) {
        if (activeNode) return;
        resetHighlight();
    });

    node.on('click', function(event, d) {
        event.stopPropagation();
        if (activeNode === d) {
            activeNode = null;
            resetHighlight();
            hideInfo();
        } else {
            activeNode = d;
            highlightNode(d, true);
            showInfo(d);
        }
    });

    function highlightNode(d, isClick = false) {
        // Dim all
        d3.selectAll('.node').classed('dimmed', true).classed('active-hover', false);
        d3.selectAll('.link').classed('dimmed', true).classed('active', false);

        // Find connected neighbors
        const connectedNodes = new Set([d.id]);
        linkData.forEach(l => {
            if (l.source.id === d.id) connectedNodes.add(l.target.id);
            if (l.target.id === d.id) connectedNodes.add(l.source.id);
        });

        // Highlight neighbors and active node
        d3.selectAll('.node')
            .filter(n => connectedNodes.has(n.id))
            .classed('dimmed', false)
            .classed('active-hover', n => n.id === d.id || isClick);

        // Always apply active glow to the hovered node specifically
        d3.select(event.currentTarget).classed('active-hover', true);

        // Highlight connected links
        d3.selectAll('.link')
            .filter(l => l.source.id === d.id || l.target.id === d.id)
            .classed('dimmed', false)
            .classed('active', true);
    }

    function resetHighlight() {
        activeNode = null;
        d3.selectAll('.node').classed('dimmed', false).classed('active-hover', false);
        d3.selectAll('.link').classed('dimmed', false).classed('active', false);
        hideInfo();
    }

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
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
        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }
    
    // Info Panel Logic
    const infoPanel = document.getElementById('info-panel');
    const infoTitle = document.getElementById('info-title');
    const infoDesc = document.getElementById('info-desc');
    
    function showInfo(d) {
        infoTitle.textContent = d.label || d.name || d.id;
        
        const details = [];
        if (d.category || d.project) details.push(`<strong style="color:#aaa">Group:</strong> ${d.category || d.project}`);
        if (d.type) details.push(`<strong style="color:#aaa">Type:</strong> ${d.type}`);
        
        let descHtml = details.join('<br>');
        if (d.description) {
            descHtml += `<br><br>${d.description}`;
        }
        
        infoDesc.innerHTML = descHtml || 'No further details available.';
        infoPanel.classList.add('visible');
    }
    
    function hideInfo() {
        infoPanel.classList.remove('visible');
    }

    // Handle Window Resize
    window.addEventListener('resize', () => {
        const w = window.innerWidth;
        const h = window.innerHeight;
        svg.attr('width', w).attr('height', h);
        
        const r = Math.min(w, h) * 0.35;
        groupKeys.forEach((key, i) => {
            const angle = (i / numGroups) * 2 * Math.PI;
            focalPoints[key] = {
                x: w / 2 + Math.cos(angle) * r,
                y: h / 2 + Math.sin(angle) * r
            };
        });
        
        simulation.force('center', d3.forceCenter(w / 2, h / 2));
        simulation.alpha(0.3).restart();
    });
});
