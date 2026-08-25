/**
 * 🚀 [V55.9] Dashboard WebSocket Logic - Main Skeleton
 * 模块职责：WebSocket 连接管理、消息解析与信号分发调度器。
 * ❌ 不再包含任何 UI 渲染或状态机逻辑，避免与 Core 层冲突。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 信号处理器已纵切至 socket_shards/ 子分片。
 */

let _wsReconnectTimer = null;
window._wsReconnectDelay = 3000;
window._wsInstance = null;

window.initWebSocket = () => {
    // 🛡️ [V87.0] 清理现存旧实例，防止多路复用与多实例并存冲突
    if (window._wsInstance) {
        console.log('🔌 [WS] 发现现存旧实例，正在主动关闭...');
        try {
            window._wsInstance.onopen = null;
            window._wsInstance.onmessage = null;
            window._wsInstance.onclose = null;
            window._wsInstance.onerror = null;
            window._wsInstance.close();
        } catch (e) {
            console.error('⚠️ [WS] 主动清理旧连接时发生异常:', e);
        }
        window._wsInstance = null;
    }

    window.lastMsgId = window.lastMsgId || 0;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws?last_msg_id=${window.lastMsgId}`;
    
    console.log(`🔌 [WS] 正在连接主权链路: ${wsUrl}`);
    const socket = new WebSocket(wsUrl);
    window._wsInstance = socket;

    socket.onopen = () => {
        console.log('✅ [WS] 主权链路已激活');
        window._wsReconnectDelay = 3000; // 重置重连延迟
    };

    /**
     * 信号分发调度器：将 WebSocket 消息委托给各子分片处理器。
     * 🛡️ [SOP-02] 各处理器定义在 socket_shards/ 目录下的独立文件中。
     */
    const routeMessage = (data) => {
        if (!data || !data.type) return;

        // 提升客户端消息序号
        if (data.msg_id && data.msg_id > window.lastMsgId) {
            window.lastMsgId = data.msg_id;
        }

        // 🚀 轻量信号路由 (9 种信号类型) — socket.signal_router.js
        if (typeof window._wsRouteSignal === 'function') {
            const handled = window._wsRouteSignal(data);
            if (handled) return;
        }

        // 🪐 AI 织网增量合并 — socket.galaxy_sync.js
        if (data.type === 'KNOWLEDGE_BATCH_READY') {
            if (typeof window._wsHandleGalaxySync === 'function') {
                window._wsHandleGalaxySync(data);
            }
            return;
        }

        // ✅ 发布完成 + 社媒分发引导 — socket.publish_complete.js
        if (data.type === 'SYNC_COMPLETED') {
            if (typeof window._wsHandlePublishComplete === 'function') {
                window._wsHandlePublishComplete(data);
            }
            return;
        }
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'SYSTEM_CONNECTED') {
            const oldInstanceId = localStorage.getItem('ws_server_instance_id');
            if (oldInstanceId && data.server_instance_id && String(oldInstanceId) !== String(data.server_instance_id)) {
                console.log('🔄 [WS] 检测到后端实例变更，重置 lastMsgId 为 0');
                window.lastMsgId = 0;
            }
            if (data.server_instance_id) {
                localStorage.setItem('ws_server_instance_id', data.server_instance_id);
            }
            if (typeof addAudit === 'function') {
                addAudit("🛰️ 治理链路已建立实时连接。", "success");
            }
        } else if (data.type === 'REPLAY_EVENTS') {
            console.log(`🔄 [WS] 收到离线重放事件包，共 ${data.events.length} 条事件`);
            (data.events || []).forEach(evt => {
                routeMessage(evt);
            });
        } else {
            routeMessage(data);
        }
    };

    socket.onclose = () => {
        console.warn(`❌ [WS] 主权链路已断开，将在 ${window._wsReconnectDelay}ms 后尝试重连...`);
        if (_wsReconnectTimer) {
            console.warn('⚠️ [WS] 现存重连定时器已在队列中，跳过本次触发。');
            return;
        }
        _wsReconnectTimer = setTimeout(() => {
            _wsReconnectTimer = null;
            // 指数退避：每次增加延迟 1.5 倍，最大 30 秒
            window._wsReconnectDelay = Math.min(window._wsReconnectDelay * 1.5, 30000);
            window.initWebSocket();
        }, window._wsReconnectDelay);
    };

    socket.onerror = (err) => {
        console.error('🚨 [WS] 链路异常:', err);
    };
};
