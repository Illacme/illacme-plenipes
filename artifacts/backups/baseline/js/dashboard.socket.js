/**
 * 🚀 [V55.9] Dashboard WebSocket Logic
 * 模块职责：仅负责实时信号的捕获与路由分发。
 * ❌ 不再包含任何 UI 渲染或状态机逻辑，避免与 Core 层冲突。
 */

window.initWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws`;
    
    console.log(`🔌 [WS] 正在连接主权链路: ${wsUrl}`);
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log('✅ [WS] 主权链路已激活');
        if (typeof addAudit === 'function') {
            addAudit("🛰️ 治理链路已建立实时连接。", "success");
        }
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // 🚀 [V55.9] 信号路由分发
        if (data.type === 'UI_TERMINAL_DATA') {
            // 转发给核心终端处理器
            if (typeof handleTerminalData === 'function') {
                handleTerminalData(data.payload);
            }
        } else if (data.type === 'SYSTEM_HEALTH') {
            // 转发给健康矩阵模块
            if (typeof refreshHealthMatrix === 'function') {
                refreshHealthMatrix();
            }
            if (typeof updateHealthUI === 'function') {
                updateHealthUI(data.payload);
            }
        } else if (data.type === 'IMPRINT_CHANGED') {
            // 转发给上下文同步模块
            if (typeof refreshGovernanceContext === 'function') {
                refreshGovernanceContext();
            }
        }
    };

    socket.onclose = () => {
        console.warn('❌ [WS] 主权链路已断开，正在尝试重连...');
        setTimeout(initWebSocket, 3000);
    };

    socket.onerror = (err) => {
        console.error('🚨 [WS] 链路异常:', err);
    };
};
