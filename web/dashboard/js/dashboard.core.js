/**
 * 🚀 Illacme Plenipes Dashboard Core Command Module (Central Hub)
 * 职责：全球出版点火中枢总调度、状态轮询与白盒终端流水线视窗联动。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

// 2. 统一出版点火接口
window.triggerPublish = async function (force = false, bypassCompletedCheck = false, clearCache = false) {
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

        // 🚀 [V10.4] 100% 发布状态检测：按当前活跃品牌 (active_imprint) 维度精准判定，避免跨品牌幽灵判定
        const activeId = window.settingsData?._active_imprint || 'default';
        const isCompletedForActiveImprint = localStorage.getItem(`sync_completed_${activeId}`) === 'true' || localStorage.getItem('sync_completed') === 'true';

        if (!bypassCompletedCheck && isCompletedForActiveImprint) {
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
                    window.appendTerminalLog('💡 您可以点击下方按钮选择“重新发布”以强行重新生成和分发所有资产。', '#38bdf8');
                }

                // 🛡️ 单例隔离
                if (typeof window.resetTerminalModalFooter === 'function') {
                    window.resetTerminalModalFooter();
                }

                const republishBtn = document.getElementById('btn-terminal-republish');
                if (republishBtn) republishBtn.style.display = 'inline-flex';

                const okBtn = document.getElementById('btn-terminal-ok');
                if (okBtn) {
                    okBtn.style.display = 'inline-flex';
                    okBtn.innerText = '关闭';
                }

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

                if (typeof window.resetTerminalModalFooter === 'function') {
                    window.resetTerminalModalFooter();
                }

                const abortBtn = document.getElementById('btn-terminal-abort');
                if (abortBtn) {
                    abortBtn.style.display = 'inline-flex';
                    abortBtn.disabled = false;
                    abortBtn.innerText = '🛑 中止同步';
                }

                const closeBtn = document.getElementById('btn-terminal-close');
                if (closeBtn) {
                    closeBtn.style.display = 'inline-flex';
                    closeBtn.innerText = '隐藏窗口 (后台继续)';
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

        // 🚀 [V78.5] 执行出版预检与确认弹窗
        let precheckRes = null;
        if (typeof window.runPublishPrecheck === 'function') {
            const checkResult = await window.runPublishPrecheck(force, activeId, bypassCompletedCheck);
            if (!checkResult.proceed) {
                return;
            }
            precheckRes = checkResult.precheckRes;
        }

        if (typeof window.addAudit === 'function') {
            window.addAudit('预检通过，正在为您准备网站文件...', 'info');
        }

        // 🚀 [V74.8] 物理点火：连接重构后的编排中枢 (V10.4 修复：彻底解耦 force 与 clear_cache，仅在明确指定 clear_cache 时才失效 AI 缓存)
        const res = await apiFetch(`/api/system/sync/trigger?force=${force ? 'true' : 'false'}&clear_cache=${clearCache ? 'true' : 'false'}`, { method: 'POST' });

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
            try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch (e) {}
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
        try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch (e) {}
    }
};
