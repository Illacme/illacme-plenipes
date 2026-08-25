/**
 * 🪐 [V55.9] Dashboard WebSocket - Galaxy Sync Shard
 * 模块职责：AI 织网增量批次合并处理器。
 * 处理：KNOWLEDGE_BATCH_READY 信号的节点/连线增量合并与幽灵链路过滤。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 从 dashboard.socket.js 纵切分离。
 */

/**
 * 处理 KNOWLEDGE_BATCH_READY 信号：增量合并 AI 织网批次数据至星系图谱。
 * @param {object} data - WebSocket 消息体
 */
window._wsHandleGalaxySync = (data) => {
    // 🪐 [混合渐进式] AI 织网分批完成 — 增量推送星系数据
    console.log(`📦 [WS] 收到 AI 增量批次: batch_index=${data.payload?.batch_index}`);
    if (window.galaxyGraph && data.payload) {
        const batch = data.payload;
        const currentData = window.galaxyGraph.graphData();

        // 增量合并新节点
        const nodeMap = {};
        currentData.nodes.forEach(n => { nodeMap[n.id] = n; });
        (batch.nodes || []).forEach(n => { nodeMap[n.id] = { ...nodeMap[n.id], ...n }; });

        // 增量合并新连线
        const linkMap = {};
        currentData.links.forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            linkMap[[src, tgt].sort().join('⇄')] = { source: src, target: tgt, ...l };
        });
        (batch.links || []).forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            linkMap[[src, tgt].sort().join('⇄')] = { source: src, target: tgt, ...l };
        });

        // 🛡️ 过滤幽灵链路：防止 WebSocket 增量批次中存在指向未知节点的幽灵边（如 STB_MASK_TRAP）
        const validNodeIds = new Set(Object.keys(nodeMap));
        const validLinks = Object.values(linkMap).filter(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            return validNodeIds.has(src) && validNodeIds.has(tgt);
        });

        const merged = {
            nodes: Object.values(nodeMap),
            links: validLinks
        };
        window.galaxyGraph.graphData(merged);
        window.galaxyGraph.cooldownTicks(15);
        if (typeof window.galaxyGraph.d3Reheat === 'function') {
            window.galaxyGraph.d3Reheat();
        } else if (typeof window.galaxyGraph.d3ReheatLayout === 'function') {
            window.galaxyGraph.d3ReheatLayout();
        } else if (typeof window.galaxyGraph.refresh === 'function') {
            window.galaxyGraph.refresh();
        }
        if (typeof window.updateGalaxyLabelElements === 'function') {
            window.updateGalaxyLabelElements(merged.nodes);
        }
        console.log(`🚀 [WS] 增量合并完成: ${merged.nodes.length} 节点, ${merged.links.length} 连线`);
    }
};
