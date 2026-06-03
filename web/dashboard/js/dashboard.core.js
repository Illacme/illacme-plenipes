/**
 * 🚀 Illacme Plenipes Dashboard Core Command Module
 * 职责：核心指挥覆盖层切换、印记上下文下拉绑定，及全球出版点火链路。
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
window.triggerPublish = async function (force = false) {
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

        // 🚀 [V78.5] 双段式预检：执行物理环境与资产完整性核查
        if (!force) {
            const precheckRes = await apiFetch('/api/system/sync/precheck', { method: 'POST' });
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
                        const result = await window.Swal.fire({
                            title: '⚠️ 物理资产丢失预警',
                            html: `预检探测到 <b>${precheckRes.warnings.length}</b> 处本地物理资产文件丢失或路径错误。<br>若强制发布，静态网站极大概率会出现破图。<br><br>是否忽略警告，强行点火发布？`,
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

        // 🚀 [V74.8] 物理点火：连接重构后的编排中枢
        const res = await apiFetch('/api/system/sync/trigger', { method: 'POST' });

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
                const statusEl = document.getElementById('terminal-status');
                if (statusEl) {
                    statusEl.innerText = 'SYNCING';
                    statusEl.className = 'online';
                }
                if (typeof window.appendTerminalLog === 'function') {
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
                window.addAudit('已有发布任务正在运行，请稍候。', 'warning');
            }
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
