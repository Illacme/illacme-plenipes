/**
 * 🚀 [V55.9] Dashboard WebSocket Logic
 * 模块职责：仅负责实时信号的捕获与路由分发。
 * ❌ 不再包含任何 UI 渲染或状态机逻辑，避免与 Core 层冲突。
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
        } else if (data.type === 'UI_RESOURCE_THROTTLE') {
            const active = data.payload.active;
            if (active) {
                const cpu = data.payload.cpu || 0;
                const ram = data.payload.ram || 0;
                if (typeof window.triggerDynamicAlert === 'function') {
                    window.triggerDynamicAlert(
                        'throttle', 
                        '物理负载过高紧急削峰', 
                        `宿主机物理负载已超限 (CPU: ${cpu}% | RAM: ${ram}%)！系统已紧急限制并发以防崩溃。`
                    );
                }
            } else {
                if (typeof window.clearThrottleAlert === 'function') {
                    window.clearThrottleAlert();
                }
                if (typeof window.triggerDynamicAlert === 'function') {
                    window.triggerDynamicAlert(
                        'restore',
                        '物理负载恢复正常',
                        '物理指标已安全回落，全域算力并发已恢复满血运转！',
                        3000
                    );
                }
            }
        } else if (data.type === 'SECURITY_ALERT') {
            const cat = data.payload.category || 'UNKNOWN';
            const msg = data.payload.message || '';
            let title = '安全合规拦截';
            if (cat === 'API_TOKEN_EXPIRED') title = '身份认证拦截';
            else if (cat === 'LICENSE_LIMIT') title = '功能准入受限';
            
            if (typeof window.triggerDynamicAlert === 'function') {
                window.triggerDynamicAlert('security', title, msg, 5000);
            }
            
            const secTab = document.querySelector(`.s-tab[data-cat="security_audit"]`);
            if (secTab) {
                const isCurrentSec = secTab.classList.contains('active');
                if (!isCurrentSec) {
                    let dot = secTab.querySelector('.alert-dot');
                    if (!dot) {
                        dot = document.createElement('span');
                        dot.className = 'alert-dot';
                        dot.style.cssText = `
                            display: inline-block;
                            width: 8px;
                            height: 8px;
                            background: #ff3b30;
                            border-radius: 50%;
                            margin-left: 6px;
                            box-shadow: 0 0 8px #ff3b30;
                            animation: pulseRed 1.5s infinite;
                        `;
                        secTab.appendChild(dot);
                    }
                }
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
            // 🚀 [V10.4] 记录已完成发布状态，用于防重入提示及重新发布选项
            const activeId = window.settingsData?._active_imprint || 'default';
            localStorage.setItem(`sync_completed_${activeId}`, 'true');
            localStorage.setItem('sync_completed', 'true');

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

                const republishBtn = document.getElementById('btn-terminal-republish');
                if (republishBtn) republishBtn.style.display = 'none';

                // 🛡️ [Abort] 隐藏中止按钮
                const abortBtn = document.getElementById('btn-terminal-abort');
                if (abortBtn) abortBtn.style.display = 'none';

                const statusEl = document.getElementById('terminal-status');
                if (statusEl) {
                    statusEl.innerText = 'COMPLETED';
                    statusEl.className = 'online';
                }
            }

            // 🚀 [V89.0] 部署后置智能自愈引导：智能查询待同步分发资产并提供一键同步弹窗
            setTimeout(async () => {
                try {
                    // 🛡️ 免打扰自愈：如果用户点击过“不再提示”，则直接屏蔽后续弹窗
                    if (localStorage.getItem('ignore_syndication_sync_prompt') === 'true') {
                        return;
                    }

                    const syncInfo = await apiFetch('/api/vault/pending-syndication');
                    if (syncInfo && syncInfo.count > 0) {
                        Swal.fire({
                            title: '📢 发现待同步分发资产',
                            html: `全站网页部署已全部就绪。<br>检测到有 <b style="color: #00f2fe;">${syncInfo.count}</b> 篇新稿件尚未同步至分发渠道（如 Dev.to），是否需要一键并行同步？`,
                            icon: 'question',
                            showCancelButton: true,
                            showDenyButton: true, // 提供“不再提示”屏蔽开关
                            confirmButtonText: '🚀 一键同步',
                            denyButtonText: '🔕 不再提示',
                            cancelButtonText: '暂不同步',
                            background: 'rgba(20,20,30,0.95)',
                            color: '#e0e0e0',
                            confirmButtonColor: '#00f2fe',
                            denyButtonColor: '#e74c3c',
                            cancelButtonColor: '#555'
                        }).then(async (result) => {
                            if (result.isDenied) {
                                localStorage.setItem('ignore_syndication_sync_prompt', 'true');
                                if (typeof window.addAudit === 'function') {
                                    window.addAudit('已记录创作者偏好：后续发布完毕后不再主动弹出分发渠道同步提醒。', 'info');
                                }
                                return;
                            }

                            if (result.isConfirmed) {
                                Swal.fire({
                                    title: '📡 正在同步中...',
                                    html: '正在向激活的分发渠道网关分发资产，并实时追踪链路状态，请稍候...',
                                    allowOutsideClick: false,
                                    didOpen: () => {
                                        Swal.showLoading();
                                    }
                                });
                                
                                const pendingDocs = syncInfo.pending_docs || [];
                                
                                // 1. 发起所有文档的重新同步请求
                                for (const doc of pendingDocs) {
                                    try {
                                        await apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(doc.rel_path)}`, {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({ force: true })
                                        });
                                    } catch (e) {
                                        console.error('[Sync] 提交分发任务失败:', e);
                                    }
                                }
                                
                                // 2. 轮询各渠道状态，直到全部 syncing 结束
                                const maxPollAttempts = 40; // 最多轮询 60 秒 (40 * 1500ms)
                                let attempt = 0;
                                
                                while (attempt < maxPollAttempts) {
                                    await new Promise(resolve => setTimeout(resolve, 1500));
                                    attempt++;
                                    
                                    let allDone = true;
                                    for (const doc of pendingDocs) {
                                        try {
                                            const statusResp = await apiFetch(`/api/vault/dispatch-status/${encodeURIComponent(doc.rel_path)}`);
                                            if (statusResp && statusResp.sync_matrix) {
                                                const targetItems = statusResp.sync_matrix.filter(item => item.lang_code === 'SYNDICATION' || item.lang_code === 'HOSTING');
                                                for (const item of targetItems) {
                                                    if ((item.status || '').toLowerCase() === 'syncing') {
                                                        allDone = false;
                                                        break;
                                                    }
                                                }
                                            }
                                        } catch (e) {
                                            console.error('[Sync] 查询分发状态异常:', e);
                                        }
                                        if (!allDone) break;
                                    }
                                    
                                    if (allDone) {
                                        break;
                                    }
                                }
                                
                                // 3. 统计最终真实的成功与失败文档数
                                let successCount = 0;
                                let failCount = 0;
                                let failedDetails = [];
                                for (const doc of pendingDocs) {
                                    try {
                                        const finalResp = await apiFetch(`/api/vault/dispatch-status/${encodeURIComponent(doc.rel_path)}`);
                                        let docHasFailedChannel = false;
                                        let docHasSuccessChannel = false;
                                        let channelErrors = [];
                                        
                                        if (finalResp && finalResp.sync_matrix) {
                                            const targetItems = finalResp.sync_matrix.filter(item => item.lang_code === 'SYNDICATION' || item.lang_code === 'HOSTING');
                                            for (const item of targetItems) {
                                                const stat = (item.status || '').toLowerCase();
                                                if (stat === 'success' || stat === 'published' || stat === 'done' || stat === 'synced') {
                                                    docHasSuccessChannel = true;
                                                } else {
                                                    docHasFailedChannel = true;
                                                    channelErrors.push({
                                                        channel: item.locale.replace('📡 ', '').replace('🌐 ', ''),
                                                        reason: item.reason || '未提供具体错误信息'
                                                    });
                                                }
                                            }
                                        }
                                        if (docHasFailedChannel) {
                                            failCount++;
                                            failedDetails.push({
                                                title: doc.title || doc.rel_path,
                                                errors: channelErrors
                                            });
                                        } else if (docHasSuccessChannel) {
                                            successCount++;
                                        }
                                    } catch (e) {
                                        failCount++;
                                        failedDetails.push({
                                            title: doc.title || doc.rel_path,
                                            errors: [{ channel: '系统', reason: e.message || '查询分发状态超时' }]
                                        });
                                    }
                                }
                                
                                let htmlContent = `已成功将 <b style="color: #00ff88;">${successCount}</b> 篇稿件同步至目标渠道。`;
                                if (failCount > 0) {
                                    htmlContent += `<br><br><div style="text-align: left; background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(231, 76, 60, 0.25); max-height: 200px; overflow-y: auto; font-size: 0.8rem;">`;
                                    htmlContent += `<b style="color: #ff6b6b; display: block; margin-bottom: 8px;">🚨 同步失败详情 (${failCount} 篇)：</b>`;
                                    failedDetails.forEach(detail => {
                                        htmlContent += `<div style="margin-bottom: 6px; border-bottom: 1px dashed rgba(255,255,255,0.08); padding-bottom: 6px;">`;
                                        htmlContent += `📄 <b style="color: #fff;">${detail.title}</b>:`;
                                        detail.errors.forEach(err => {
                                            htmlContent += `<br>&nbsp;&nbsp;• <span style="color: #a5f3fc;">[${err.channel}]</span> <span style="color: #ffb7b7;">${err.reason}</span>`;
                                        });
                                        htmlContent += `</div>`;
                                    });
                                    htmlContent += `</div>`;
                                }

                                Swal.fire({
                                    title: successCount > 0 && failCount === 0 ? '✅ 一键同步完成' : '⚠️ 同步完成 (含失败)',
                                    html: htmlContent,
                                    icon: failCount === 0 ? 'success' : 'warning',
                                    background: 'rgba(20,20,30,0.95)',
                                    color: '#e0e0e0',
                                    confirmButtonColor: '#00f2fe'
                                });
                            }
                        });
                    }
                } catch (e) {
                    console.error('⚠️ [自愈引导] 检索待同步列表异常:', e);
                }
            }, 1500);
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
