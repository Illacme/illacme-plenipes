/**
 * 📡 [V55.9] Dashboard WebSocket - Signal Router Shard
 * 模块职责：轻量级 WebSocket 信号路由处理器。
 * 处理：UI_TERMINAL_DATA, AUDIT_LOG, SYSTEM_HEALTH, UI_PROGRESS_*, IMPRINT_CHANGED,
 *       UI_RESOURCE_THROTTLE, SECURITY_ALERT, FILE_SYNCED, UI_AI_BREAKER_TRIPPED。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 从 dashboard.socket.js 纵切分离。
 */

/**
 * 尝试路由轻量级信号。已处理返回 true，未匹配返回 false。
 * @param {object} data - WebSocket 消息体
 * @returns {boolean} 是否已处理
 */
window._wsRouteSignal = (data) => {
    const type = data.type;

    if (type === 'UI_TERMINAL_DATA') {
        // 转发给核心终端处理器
        if (typeof handleTerminalData === 'function') {
            handleTerminalData(data.payload);
        }
        return true;
    }

    if (type === 'AUDIT_LOG') {
        // 🚀 [V78.7] 白盒化进度流：拦截后端 tlog 投递至终端
        const modal = document.getElementById('terminal-modal');
        if (modal && modal.style.display !== 'none') {
            const msg = data.payload.message || '';
            const level = data.payload.level || 'INFO';
            
            if (modal.dataset.context === 'publish_preview' && typeof window.updatePreviewStepperFromLog === 'function') {
                // 发布预览模式：由专用过滤器输出精简友好的创作者日志
                window.updatePreviewStepperFromLog(msg);
            } else if (typeof window.appendTerminalLog === 'function') {
                // 全网发布/通用模式：输出详细工程日志
                let color = null;
                if (level === 'ERROR' || level === 'CRITICAL') color = '#ff4d4d';
                else if (level === 'WARNING') color = '#ffaa00';
                window.appendTerminalLog(`[${level}] ${msg}`, color);
            }
        }
        return true;
    }

    if (type === 'SYSTEM_HEALTH') {
        // 转发给健康矩阵模块
        if (typeof refreshHealthMatrix === 'function') {
            refreshHealthMatrix();
        }
        if (typeof updateHealthUI === 'function') {
            updateHealthUI(data.payload);
        }
        return true;
    }

    if (type === 'UI_PROGRESS_START') {
        if (typeof showGlobalProgressBar === 'function') {
            showGlobalProgressBar(data.payload.total, data.payload.description);
        }
        return true;
    }

    if (type === 'UI_PROGRESS_ADVANCE') {
        if (typeof advanceGlobalProgressBar === 'function') {
            advanceGlobalProgressBar(data.payload.amount);
        }
        return true;
    }

    if (type === 'UI_PROGRESS_STOP') {
        if (typeof hideGlobalProgressBar === 'function') {
            hideGlobalProgressBar();
        }
        return true;
    }

    if (type === 'IMPRINT_CHANGED') {
        // 转发给上下文同步模块
        if (typeof refreshGovernanceContext === 'function') {
            refreshGovernanceContext();
        }
        return true;
    }

    if (type === 'UI_RESOURCE_THROTTLE') {
        if (data._is_replay) {
            // 🛡️ [UI 防重放] 离线历史事件包中的物理削峰/恢复无需在重连/刷新时回放弹窗
            return true;
        }
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
            // 🛡️ [UI 防误报] 仅当当前界面上确实存在生效中的削峰告警时，状态回落才弹出“恢复正常”提示；
            // 避免刷新页面建立 WebSocket 重放历史消息时产生突兀的假恢复提示。
            let hadActiveThrottle = false;
            if (typeof window.clearThrottleAlert === 'function') {
                hadActiveThrottle = window.clearThrottleAlert();
            }
            if (hadActiveThrottle && typeof window.triggerDynamicAlert === 'function') {
                window.triggerDynamicAlert(
                    'restore',
                    '物理负载恢复正常',
                    '物理指标已安全回落，全域算力并发已恢复满血运转！',
                    3000
                );
            }
        }
        return true;
    }

    if (type === 'SECURITY_ALERT') {
        const cat = data.payload.category || 'UNKNOWN';
        const msg = data.payload.message || '';
        let title = '安全合规拦截';
        if (cat === 'API_TOKEN_EXPIRED') title = '身份认证拦截';
        else if (cat === 'LICENSE_LIMIT') title = '功能准入受限';
        
        if (!data._is_replay && typeof window.triggerDynamicAlert === 'function') {
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
        return true;
    }

    if (type === 'FILE_SYNCED') {
        if (typeof window.showBreathingToast === 'function' && data.payload && data.payload.file_name) {
            window.showBreathingToast(`✨ 《${data.payload.file_name}》已物理备份`);
        }
        return true;
    }

    if (type === 'UI_AI_BREAKER_TRIPPED') {
        console.warn('🚨 [WS] 收到 AI 熔断通知:', data.payload);
        if (typeof window.handleAiBreakerTripped === 'function') {
            window.handleAiBreakerTripped(data.payload);
        }
        return true;
    }

    return false;
};
