/**
 * Illacme Plenipes Dashboard 2.0 - Intelligence Panorama Controller
 * 核心职责：3D 银河渲染、实时数据对齐、交互逻辑管理。
 */

let galaxyGraph = null;
const AUDIT_LIMIT = 50;

// 🚀 初始化 3D 知识银河
function initGalaxy() {
    const elem = document.getElementById('galaxy-3d');
    galaxyGraph = ForceGraph3D()(elem)
        .backgroundColor('#00000000') // 透明背景，使用 CSS 渐变
        .showNavInfo(false)
        .nodeColor(node => node.is_manual ? '#ffd700' : '#8a2be2')
        .nodeLabel('title')
        .nodeOpacity(0.9)
        .nodeRelSize(4)
        .linkColor(link => link.is_manual ? 'rgba(255, 215, 0, 0.5)' : 'rgba(0, 210, 255, 0.3)')
        .linkWidth(1)
        .onNodeClick(node => {
            // 点击节点聚焦并展示详情
            const distance = 100;
            const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
            galaxyGraph.cameraPosition(
                { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
                node,
                3000
            );
            showNodeDetails(node);
        });

    // 适配窗口大小
    window.addEventListener('resize', () => {
        galaxyGraph.width(document.getElementById('galaxy-viewport').clientWidth);
        galaxyGraph.height(document.getElementById('galaxy-viewport').clientHeight);
    });
}

// 📡 实时数据同步
async function syncData() {
    try {
        // 1. 获取图谱数据
        const graphRes = await fetch('/api/galaxy/graph');
        const graphData = await graphRes.json();
        if (graphData && graphData.nodes) {
            galaxyGraph.graphData(graphData);
            document.getElementById('conn-count').innerText = graphData.links.length;
            document.getElementById('density-val').innerText = (graphData.links.length / (graphData.nodes.length || 1)).toFixed(2);
        }

        // 2. 获取引擎脉冲
        const statsRes = await fetch('/api/billing/stats');
        const statsData = await statsRes.json();
        if (statsData) {
            document.getElementById('roi-val').innerText = statsData.weekly_trend ? '$' + statsData.weekly_trend.toFixed(2) : '--';
        }

        // 3. 模拟获取审计流 (后续对接 WebSocket)
        updateAuditFeed();

    } catch (err) {
        console.error("❌ [Sync] 失败:", err);
    }
}

function updateAuditFeed() {
    const feed = document.getElementById('audit-feed');
    // 逻辑：向 feed 注入最新的审计项，保持滚动到底部
}

function showNodeDetails(node) {
    const overlay = document.getElementById('node-info-overlay');
    overlay.style.display = 'block';
    overlay.innerHTML = `
        <div class="glass-card" style="padding: 15px; border: 1px solid var(--accent-secondary);">
            <h3 style="color: var(--accent-secondary);">${node.title}</h3>
            <p style="font-size: 0.8rem; color: var(--text-dim); margin-top: 5px;">ID: ${node.id}</p>
            <div style="margin-top: 10px;">
                <span class="tag">Entities Found: ${node.entities ? Object.keys(node.entities).length : 0}</span>
            </div>
        </div>
    `;
}

// 🚀 启动
window.onload = () => {
    initGalaxy();
    syncData();
    setInterval(syncData, 5000); // 5秒心跳对齐
    
    // 修正 canvas 大小
    setTimeout(() => {
        galaxyGraph.width(document.getElementById('galaxy-viewport').clientWidth);
        galaxyGraph.height(document.getElementById('galaxy-viewport').clientHeight);
    }, 500);
};
