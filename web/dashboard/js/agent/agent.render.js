/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) UI Render Layer - Main Hub
 * 职责：调度子模块、处理通用消息追加日志等。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规重组。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.render.js initializing');

    const renderMarkdown = text => (typeof window.renderMarkdown === 'function' ? window.renderMarkdown(text) : text);

    window.SovereignAgent = window.SovereignAgent || {};
    window.SovereignAgent.render = window.SovereignAgent.render || {};

    /**
     * 向控制面板的 feed 容器追加特定样式的消息
     * @param {string} text 
     * @param {string} typeClass 
     */
    window.SovereignAgent.render.appendMessage = function(text, typeClass) {
        const agentFeed = document.getElementById('agent-feed');
        if (!agentFeed) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = `agent-msg ${typeClass}`;
        msgDiv.innerHTML = renderMarkdown(text);
        agentFeed.appendChild(msgDiv);
        agentFeed.scrollTop = agentFeed.scrollHeight;
    };
})();
