/**
 * 🚀 [V55.9] Dashboard WebSocket Logic
 * 模块职责：仅负责实时信号的捕获与路由分发。
 * ❌ 不再包含任何 UI 渲染或状态机逻辑，避免与 Core 层冲突。
 */

window.initWebSocket = () => {
    window.lastMsgId = window.lastMsgId || 0;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws?last_msg_id=${window.lastMsgId}`;
    
    console.log(`🔌 [WS] 正在连接主权链路: ${wsUrl}`);
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log('✅ [WS] 主权链路已激活');
    };

    const routeMessage = (data) => {
        if (!data || !data.type) return;

        // 提升客户端消息序号
        if (data.msg_id && data.msg_id > window.lastMsgId) {
            window.lastMsgId = data.msg_id;
        }

        // 🚀 [V55.9] 信号路由分发
        if (data.type === 'UI_TERMINAL_DATA') {
            // 转发给核心终端处理器
            if (typeof handleTerminalData === 'function') {
                handleTerminalData(data.payload);
            }
        } else if (data.type === 'AUDIT_LOG') {
            // 🚀 [V78.7] 白盒化进度流：拦截后端 tlog 投递至终端
            const modal = document.getElementById('terminal-modal');
            if (modal && modal.style.display !== 'none') {
                if (typeof window.appendTerminalLog === 'function') {
                    const msg = data.payload.message || '';
                    const level = data.payload.level || 'INFO';
                    let color = null;
                    if (level === 'ERROR' || level === 'CRITICAL') color = '#ff4d4d';
                    else if (level === 'WARNING') color = '#ffaa00';
                    window.appendTerminalLog(`[${level}] ${msg}`, color);
                }
            }
        } else if (data.type === 'SYSTEM_HEALTH') {
            // 转发给健康矩阵模块
            if (typeof refreshHealthMatrix === 'function') {
                refreshHealthMatrix();
            }
            if (typeof updateHealthUI === 'function') {
                updateHealthUI(data.payload);
            }
        } else if (data.type === 'UI_PROGRESS_START') {
            if (typeof showGlobalProgressBar === 'function') {
                showGlobalProgressBar(data.payload.total, data.payload.description);
            }
        } else if (data.type === 'UI_PROGRESS_ADVANCE') {
            if (typeof advanceGlobalProgressBar === 'function') {
                advanceGlobalProgressBar(data.payload.amount);
            }
        } else if (data.type === 'UI_PROGRESS_STOP') {
            if (typeof hideGlobalProgressBar === 'function') {
                hideGlobalProgressBar();
            }
        } else if (data.type === 'IMPRINT_CHANGED') {
            // 转发给上下文同步模块
            if (typeof refreshGovernanceContext === 'function') {
                refreshGovernanceContext();
            }
        } else if (data.type === 'KNOWLEDGE_BATCH_READY') {
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
        } else if (data.type === 'FILE_SYNCED') {
            if (typeof window.showBreathingToast === 'function' && data.payload && data.payload.file_name) {
                window.showBreathingToast(`✨ 《${data.payload.file_name}》已物理备份`);
            }
        } else if (data.type === 'SYNC_COMPLETED') {
            // 🪐 [混合渐进式] 同步完成 — 拉取最终全量图谱确保一致性
            console.log('✅ [WS] 同步完成，拉取最终全量图谱...');
            if (typeof window.addAudit === 'function') {
                window.addAudit('网站发布流程已全部完成！', 'success');
            }
            if (typeof window.refreshGalaxy === 'function') {
                window.refreshGalaxy();
            }
            // 🚀 [V78.7] 白盒化进度流：显示流水线完成并点亮确认按钮
            const modal = document.getElementById('terminal-modal');
            if (modal && modal.style.display !== 'none') {
                if (typeof window.appendTerminalLog === 'function') {
                    window.appendTerminalLog('✅ 同步流水线执行完毕，资产已全量生成！', '#00ff88');
                }
                const okBtn = document.getElementById('btn-terminal-ok');
                if (okBtn) okBtn.style.display = 'block';
                const statusEl = document.getElementById('terminal-status');
                if (statusEl) {
                    statusEl.innerText = 'COMPLETED';
                    statusEl.className = 'online';
                }
            }
        } else if (data.type === 'UI_AI_BREAKER_TRIPPED') {
            console.warn('🚨 [WS] 收到 AI 熔断通知:', data.payload);
            if (typeof window.handleAiBreakerTripped === 'function') {
                window.handleAiBreakerTripped(data.payload);
            }
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
        console.warn('❌ [WS] 主权链路已断开，正在尝试重连...');
        setTimeout(initWebSocket, 3000);
    };

    socket.onerror = (err) => {
        console.error('🚨 [WS] 链路异常:', err);
    };
};
