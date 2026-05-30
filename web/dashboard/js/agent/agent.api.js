/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) API Layer - SOP Compliant
 * 负责大模型能力探测及任务执行的前端底层网络 API 交互封装。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.api.js initializing');

    // 初始化全局 SovereignAgent 命名空间
    window.SovereignAgent = window.SovereignAgent || {};

    window.SovereignAgent.api = {
        /**
         * 🆕 动态获取大模型的元数据及能力配置
         * @returns {Promise<Object>}
         */
        async fetchModelInfo() {
            const r = await fetch('/api/agent/model_info');
            if (!r.ok) throw new Error(`HTTP Error: ${r.status}`);
            return await r.json();
        },

        /**
         * 🚀 异步向大模型协同主循环提交任务，获取 SSE 流式数据源
         * @param {Object} payload 任务负载
         * @returns {Promise<Response>}
         */
        async submitTask(payload) {
            const response = await fetch('/api/agent/task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
            return response;
        },

        /**
         * 🛡️ 提交人类在环 (HITL) 物理决策授权结果
         * @param {string} hitlId 会话ID
         * @param {string} decision 授权决策 ('approve' | 'reject')
         * @returns {Promise<Object>}
         */
        async sendHitlDecision(hitlId, decision) {
            const r = await fetch('/api/agent/authorize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hitl_id: hitlId, decision: decision })
            });
            if (!r.ok) throw new Error(`HTTP Error: ${r.status}`);
            return await r.json();
        }
    };
})();
