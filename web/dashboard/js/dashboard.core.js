/**
 * 🚀 Illacme Plenipes Dashboard Core Command Module
 * 职责：核心指挥覆盖层切换、品牌上下文下拉绑定，及全球出版点火链路。
 */

// 1. 核心指挥中枢控制 (全局单例)
window.toggleHub = (forceState) => {
    const hub = document.getElementById('command-hub-overlay');
    if (!hub) return;

    // 强制状态或切换
    if (forceState === 'show') {
        hub.style.display = 'flex';
    } else if (forceState === 'hide') {
        hub.style.display = 'none';
    } else {
        const isHidden = window.getComputedStyle(hub).display === 'none';
        hub.style.display = isHidden ? 'flex' : 'none';
    }
};

window.toggleImprintDropdown = (e) => {
    if (e) e.stopPropagation();
    const dropdown = document.getElementById('imprint-dropdown');
    if (!dropdown) return;
    const isHidden = dropdown.style.display === 'none';
    dropdown.style.display = isHidden ? 'block' : 'none';
    if (isHidden && typeof renderImprintDropdown === 'function') renderImprintDropdown();
};

// 🛰️ [V55.1] 核级事件委派：确保指挥中心关闭按钮在任何层级冲突下都能被捕获
document.addEventListener('click', (e) => {
    // 寻找最近的关闭按钮，且必须在指挥中心覆盖层内
    const closeBtn = e.target.closest('.overview-overlay .close-btn');
    if (closeBtn) {
        e.preventDefault();
        e.stopPropagation();
        window.toggleHub('hide');
    }
});

// 2. 统一出版点火接口
window.triggerPublish = async function (force = false, bypassCompletedCheck = false) {
    if (typeof window.triggerSystemPulse === 'function') {
        window.triggerSystemPulse();
    }
    
    if (typeof window.addAudit === 'function') {
        window.addAudit('正在准备发布流水线...', 'info');
    }

    try {
        if (typeof apiFetch !== 'function') {
            throw new Error('apiFetch 核心未加载完毕');
        }

        // 🚀 [V10.4] 100% 发布状态检测：如果检测到已完成发布且未跳过检查，弹出重新发布选项终端
        if (!bypassCompletedCheck && localStorage.getItem('sync_completed') === 'true') {
            const modal = document.getElementById('terminal-modal');
            if (modal) {
                modal.style.display = 'flex';
                const title = document.getElementById('terminal-title');
                if (title) title.innerText = '🚀 全域全息同步 (已完成)';
                const toolbar = document.getElementById('terminal-toolbar');
                if (toolbar) toolbar.style.display = 'none';
                
                const out = document.getElementById('terminal-output');
                if (out) {
                    out.innerHTML = '';
                    modal.dataset.context = 'republish_prompt';
                }
                
                if (typeof window.appendTerminalLog === 'function') {
                    window.appendTerminalLog('📡 [系统] 检测到当前同步已 100% 完成。', '#00ff88');
                    window.appendTerminalLog('💡 您可以点击下方按钮选择“重新发布”以强行重新生成和分发所有资产。', '#ffffff');
                }
                
                const okBtn = document.getElementById('btn-terminal-ok');
                if (okBtn) okBtn.style.display = 'none';
                
                const abortBtn = document.getElementById('btn-terminal-abort');
                if (abortBtn) abortBtn.style.display = 'none';
                
                const republishBtn = document.getElementById('btn-terminal-republish');
                if (republishBtn) republishBtn.style.display = 'block';

                const statusEl = document.getElementById('terminal-status');
                if (statusEl) {
                    statusEl.innerText = 'COMPLETED';
                    statusEl.className = 'online';
                }
            }
            if (typeof window.addAudit === 'function') {
                window.addAudit('网站已处于100%发布状态，已弹出重新发布选项。', 'info');
            }
            return;
        }

        // 🚀 [V78.8] 热态抢占防御：先查询当前是否已有正在运行的同步任务
        const statusRes = await apiFetch('/api/system/sync/status');
        if (statusRes && statusRes.is_publishing) {
            if (typeof window.addAudit === 'function') {
                window.addAudit('已有同步任务正在运行，已自动投射实时日志终端。', 'warning');
            }

            // 🚀 [V79.0] 恢复显示后台同步终端视图
            const modal = document.getElementById('terminal-modal');
            if (modal) {
                modal.style.display = 'flex';
                const title = document.getElementById('terminal-title');
                if (title) title.innerText = '🚀 全域全息同步流水线 (恢复视图)';
                const toolbar = document.getElementById('terminal-toolbar');
                if (toolbar) toolbar.style.display = 'none';
                
                const okBtn = document.getElementById('btn-terminal-ok');
                if (okBtn) okBtn.style.display = 'none';
                
                const abortBtn = document.getElementById('btn-terminal-abort');
                if (abortBtn) {
                    abortBtn.style.display = 'block';
                    abortBtn.disabled = false;
                    abortBtn.innerText = '🛑 中止同步';
                }

                const statusEl = document.getElementById('terminal-status');
                if (statusEl) {
                    statusEl.innerText = 'SYNCING';
                    statusEl.className = 'online';
                }
                if (typeof window.appendTerminalLog === 'function') {
                    window.appendTerminalLog('📡 已连接至后台活跃的出版同步流，正在恢复日志投射...', '#00ffff');
                }
            }

            if (window.Swal) {
                window.Swal.fire({
                    title: '同步进行中',
                    text: '已有发布任务正在后台运行，已自动为您投射实时日志终端。',
                    icon: 'info',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 4000
                });
            }
            return;
        }

        // 🚀 [V78.6] 挂起监控狗：防止下面强制落盘时触发自动同步抢占预检
        try {
            await apiFetch('/api/system/watchdog/suspend', { method: 'POST' });
        } catch (e) {
            console.warn('[Publish] 挂起监控狗失败:', e);
        }

        // 强制将编辑器里的脏数据保存落盘，避免预检扫不到最新修改
        if (typeof window.saveDocument === 'function') {
            try {
                await window.saveDocument();
            } catch (e) {
                console.warn('[Publish] 预保存文档失败:', e);
            }
        }

        if (typeof window.addAudit === 'function') {
            window.addAudit('正在进行发布前置预检...', 'info');
        }

        let precheckRes = null;
        // 🚀 [V78.5] 双段式预检：执行物理环境与资产完整性核查
        if (!force) {
            precheckRes = await apiFetch('/api/system/sync/precheck', { method: 'POST' });
            if (precheckRes) {
                // 强阻断 (Critical)
                if (precheckRes.critical_errors && precheckRes.critical_errors.length > 0) {
                    if (window.Swal) {
                        await window.Swal.fire({
                            title: '🚨 致命环境损坏',
                            html: `无法启动发布流水线，发现严重环境问题：<br><br><div style="text-align:left;color:#d33;font-size:0.9em;background:#fee;padding:10px;border-radius:4px;">${precheckRes.critical_errors.join('<br>')}</div><br>请修复后重试！`,
                            icon: 'error',
                            confirmButtonText: '我知道了',
                            confirmButtonColor: '#3085d6'
                        });
                    }
                    if (typeof window.addAudit === 'function') window.addAudit('预检失败：系统环境损坏，已强行拦截发布！', 'error');
                    try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch(e) {}
                    return;
                }
                
                // 弱阻断 (Warnings)
                if (precheckRes.warnings && precheckRes.warnings.length > 0) {
                    if (window.Swal) {
                        const warningsListHtml = precheckRes.warnings.map(w => {
                            const docPath = w.doc_id ? (w.doc_id.startsWith('*') ? w.doc_id.substring(1) : w.doc_id) : '';
                            const docLinkHtml = docPath && docPath !== 'Unknown'
                                ? `<a href="javascript:void(0)" onclick="if (window.Swal) window.Swal.close(); if (typeof window.openEditor === 'function') { window.openEditor('${docPath.replace(/'/g, "\\\\'")}') } else { console.warn('openEditor not found') }" style="color: var(--accent-secondary, #3085d6); text-decoration: underline; cursor: pointer; font-weight: bold;">${docPath}</a>`
                                : '未知文档';
                            return `<div style="padding: 6px 0; border-bottom: 1px solid rgba(0,0,0,0.06); text-align: left; word-break: break-all; line-height: 1.4;">
                                <span style="color: var(--accent-orange, #e67e22); font-weight: 600; font-family: monospace;">• ${w.asset}</span>
                                <br>
                                <span style="font-size: 0.85em; color: #888; padding-left: 10px;">引用源: ${docLinkHtml}</span>
                            </div>`;
                        }).join('');

                        const mode = precheckRes.publishing_mode || (window.settingsData && window.settingsData.governance && window.settingsData.governance.publishing_mode) || 'basic';
                        let modeTipHtml = '';
                        if (mode === 'basic') {
                            modeTipHtml = `<div style="margin-top: 10px; padding: 10px; border-radius: 6px; background: rgba(230, 126, 34, 0.1); border: 1px solid rgba(230, 126, 34, 0.2); text-align: left; font-size: 0.9em; color: #d35400;">
                                💡 <b>当前印记模式：基础模式 (Basic)</b><br>
                                此模式下不启用 AI 翻译，多语言译文直接透传中文原文，校对工作台将显示中文原文。
                            </div>`;
                        } else if (mode === 'enhanced') {
                            modeTipHtml = `<div style="margin-top: 10px; padding: 10px; border-radius: 6px; background: rgba(52, 152, 219, 0.1); border: 1px solid rgba(52, 152, 219, 0.2); text-align: left; font-size: 0.9em; color: #2980b9;">
                                💡 <b>当前印记模式：增强模式 (Enhanced)</b><br>
                                此模式下仅对 SEO 信息执行 AI 翻译，正文直接透传中文原文，校对工作台正文区域将显示中文。
                            </div>`;
                        } else {
                            modeTipHtml = `<div style="margin-top: 10px; padding: 10px; border-radius: 6px; background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.2); text-align: left; font-size: 0.9em; color: #27ae60;">
                                💡 <b>当前印记模式：全球出版模式 (Global)</b><br>
                                已启用全量 AI 多语言翻译及主权隔离防护。
                            </div>`;
                        }

                        const warningHtml = `
                            预检探测到 <b>${precheckRes.warnings.length}</b> 处本地物理资产文件丢失或路径错误。<br>
                            若强制发布，静态网站极大概率会出现破图。<br><br>
                            ${modeTipHtml}
                            <br>
                            <details style="text-align: left; background: rgba(0, 0, 0, 0.03); padding: 10px; border-radius: 6px; border: 1px solid rgba(0, 0, 0, 0.08);">
                                <summary style="cursor: pointer; font-weight: bold; color: var(--accent-secondary, #3085d6); outline: none; user-select: none;">
                                    查看具体的丢失资产清单
                                </summary>
                                <div style="max-height: 180px; overflow-y: auto; margin-top: 8px; font-size: 0.95em;">
                                    ${warningsListHtml}
                                </div>
                            </details>
                            <br>
                            是否忽略警告，强行点火发布？
                        `;

                        const result = await window.Swal.fire({
                            title: '⚠️ 物理资产丢失预警',
                            html: warningHtml,
                            icon: 'warning',
                            showCancelButton: true,
                            confirmButtonText: '强行发布 (忽略破图)',
                            cancelButtonText: '取消并去修复',
                            confirmButtonColor: '#d33',
                            cancelButtonColor: '#3085d6'
                        });
                        if (!result.isConfirmed) {
                            if (typeof window.addAudit === 'function') window.addAudit('已取消发布，请检查并补齐丢失的物理资产。', 'info');
                            try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch(e) {}
                            return;
                        }
                    } else {
                        const ok = confirm(`预检探测到 ${precheckRes.warnings.length} 处资产丢失。确定要强行发布吗？`);
                        if (!ok) {
                            try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch(e) {}
                            return;
                        }
                    }
                }
            }
        }

        if (typeof window.addAudit === 'function') {
            window.addAudit('预检通过，正在为您准备网站文件...', 'info');
        }

        // 🚀 [V74.8] 物理点火：连接重构后的编排中枢 (V10.4 修复：正确传入 force 选项以保证重新发布时重跑翻译管线)
        const res = await apiFetch(`/api/system/sync/trigger?force=${force ? 'true' : 'false'}`, { method: 'POST' });

        if (res && res.status === 'started') {
            if (typeof window.addAudit === 'function') {
                window.addAudit(`网站发布流程已启动 (流水线 ID: ${res.future_id})`, 'success');
            }

            // 🚀 [V78.7] 白盒化进度流：开启黑客终端视窗
            const modal = document.getElementById('terminal-modal');
            if (modal) {
                modal.style.display = 'flex';
                const title = document.getElementById('terminal-title');
                if (title) title.innerText = '🚀 全域全息同步流水线';
                const toolbar = document.getElementById('terminal-toolbar');
                if (toolbar) toolbar.style.display = 'none';
                
                const out = document.getElementById('terminal-output');
                if (out && modal.dataset.context !== 'publish') {
                    out.innerHTML = '';
                    modal.dataset.context = 'publish';
                } else if (out && out.innerHTML.trim() === '') {
                    out.innerHTML = '';
                }
                const okBtn = document.getElementById('btn-terminal-ok');
                if (okBtn) okBtn.style.display = 'none';
                
                // 🛡️ [Abort] 显示中止按钮并激活状态
                const abortBtn = document.getElementById('btn-terminal-abort');
                if (abortBtn) {
                    abortBtn.style.display = 'block';
                    abortBtn.disabled = false;
                    abortBtn.innerText = '🛑 中止同步';
                }

                const statusEl = document.getElementById('terminal-status');
                if (statusEl) {
                    statusEl.innerText = 'SYNCING';
                    statusEl.className = 'online';
                }
                if (typeof window.appendTerminalLog === 'function') {
                    const currentMode = (res && res.publishing_mode) || (precheckRes && precheckRes.publishing_mode) || (window.settingsData && window.settingsData.governance && window.settingsData.governance.publishing_mode) || 'basic';
                    const modeText = currentMode === 'basic' ? '基础模式 (Basic)' :
                                     currentMode === 'enhanced' ? '增强模式 (Enhanced)' : '全球出版模式 (Global)';
                    window.appendTerminalLog(`📡 [点火] 当前出版模式: ${modeText}`, '#a29bfe');
                    window.appendTerminalLog('🚀 正在启动全域全息同步流水线...', '#00ff88');
                }
            }

            if (window.Swal) {
                window.Swal.fire({
                    title: '网站发布流程已启动',
                    text: '正在后台为您生成并部署网站，实时日志已投射至终端。',
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
            }
        } else if (res && res.status === 'rejected') {
            if (typeof window.addAudit === 'function') {
                window.addAudit('已有同步任务正在运行，已自动投射实时日志终端。', 'warning');
            }

            // 🚀 [V79.0] 恢复显示后台同步终端视图
            const modal = document.getElementById('terminal-modal');
            if (modal) {
                modal.style.display = 'flex';
                const title = document.getElementById('terminal-title');
                if (title) title.innerText = '🚀 全域全息同步流水线 (恢复视图)';
                const toolbar = document.getElementById('terminal-toolbar');
                if (toolbar) toolbar.style.display = 'none';
                
                const okBtn = document.getElementById('btn-terminal-ok');
                if (okBtn) okBtn.style.display = 'none';
                
                const abortBtn = document.getElementById('btn-terminal-abort');
                if (abortBtn) {
                    abortBtn.style.display = 'block';
                    abortBtn.disabled = false;
                    abortBtn.innerText = '🛑 中止同步';
                }

                const statusEl = document.getElementById('terminal-status');
                if (statusEl) {
                    statusEl.innerText = 'SYNCING';
                    statusEl.className = 'online';
                }
                if (typeof window.appendTerminalLog === 'function') {
                    window.appendTerminalLog('📡 已连接至后台活跃的出版同步流，正在恢复日志投射...', '#00ffff');
                }
            }

            if (window.Swal) {
                window.Swal.fire({
                    title: '同步进行中',
                    text: '已有发布任务正在后台运行，已自动为您投射实时日志终端。',
                    icon: 'info',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 4000
                });
            }
            try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch(e) {}
        } else {
            throw new Error(res ? res.reason : '后端拒绝点火');
        }
    } catch (err) {
        if (typeof window.addAudit === 'function') {
            window.addAudit(`发布失败: ${err.message}`, 'error');
        }
        if (window.Swal) {
            window.Swal.fire('点火失败', err.message, 'error');
        }
        try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch(e) {}
    }
};

// 🛡️ [Abort] 全局中止同步交互逻辑
window.abortSync = async () => {
    if (!window.Swal) {
        // 退回降级保护机制
        const confirmAbort = confirm("确定要中止当前的全域同步任务吗？这会取消所有排队中的任务。");
        if (!confirmAbort) return;
        return executeAbortAction();
    }

    const result = await window.Swal.fire({
        title: '🛑 确定要中止同步吗？',
        text: '这会立即清空调度池任务并中止所有排队中的翻译/同步管线。',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '确定中止',
        cancelButtonText: '继续同步',
        confirmButtonColor: '#ff4d4d',
        cancelButtonColor: '#3085d6'
    });

    if (result.isConfirmed) {
        return executeAbortAction();
    }
};

async function executeAbortAction() {
    if (typeof window.appendTerminalLog === 'function') {
        window.appendTerminalLog('🛑 正在向服务器发送中止指令...', '#ff4d4d');
    }

    const btn = document.getElementById('btn-terminal-abort');
    if (btn) {
        btn.disabled = true;
        btn.innerText = '正在中止...';
    }

    const res = await apiFetch('/api/system/sync/abort', { method: 'POST' });
    if (res && res.status === 'aborted') {
        if (typeof window.appendTerminalLog === 'function') {
            window.appendTerminalLog('🛑 中止指令已成功接收。后续任务已取消，正在进行收尾收割...', '#ff4d4d');
        }
        if (window.Swal) {
            window.Swal.fire({
                title: '同步已中止',
                text: '已成功中止全量同步并清空调度池任务。',
                icon: 'info',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
        }
    } else {
        if (window.Swal) {
            window.Swal.fire('发送失败', '中止同步指令发送失败或未被接受。', 'error');
        } else {
            alert("中止同步指令发送失败或未被接受。");
        }
        const btn = document.getElementById('btn-terminal-abort');
        if (btn) {
            btn.disabled = false;
            btn.innerText = '🛑 中止同步';
        }
    }
}

// 🚀 [V10.4] 从终端触发重新发布
window.republishFromTerminal = async function () {
    const republishBtn = document.getElementById('btn-terminal-republish');
    if (republishBtn) republishBtn.style.display = 'none';
    
    // 清理已完成状态，避免下次触发再次拦截
    localStorage.removeItem('sync_completed');
    
    if (typeof window.appendTerminalLog === 'function') {
        window.appendTerminalLog('🔄 正在重新初始化全域同步流程...', '#ffaa00');
    }
    
    // 重新调用触发同步流程，传入 force = true, bypassCompletedCheck = true
    await window.triggerPublish(true, true);
};

