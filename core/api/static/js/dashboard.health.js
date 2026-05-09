/**
 * 🩺 [V55.0] Illacme Plenipes Health & Operations Module
 * 职责：处理系统机能矩阵、健康状态、服务控制与物理关机。
 */

window.refreshGovernanceContext = async () => {
    const data = await apiFetch('/api/system/context');
    if (data && !data.error) {
        const badge = document.getElementById('active-imprint-name');
        if (badge) badge.innerText = (data.imprint_name || data.imprint || 'UNKNOWN').toUpperCase();

        const sidebarBadge = document.getElementById('sidebar-imprint-display');
        if (sidebarBadge) sidebarBadge.innerText = data.imprint_name || data.imprint || 'DEFAULT';

        const displayImprint = document.getElementById('display-imprint');
        if (displayImprint) displayImprint.innerText = (data.imprint_name || data.imprint || 'DEFAULT').toUpperCase();

        const displayTheme = document.getElementById('display-theme');
        if (displayTheme) displayTheme.innerText = (data.theme || 'NONE').toUpperCase();

        const aiEl = document.getElementById('ctx-ai');
        const i18nEl = document.getElementById('ctx-i18n');
        
        if (aiEl && data.ai) aiEl.innerText = `${data.ai.provider} / ${data.ai.model}`;
        if (i18nEl && data.i18n) {
            const targets = data.i18n.targets || [];
            const targetsStr = targets.length > 0 ? targets.join(', ') : 'NONE';
            i18nEl.innerText = `${data.i18n.source} ➔ ${targetsStr}`;
        }
        
        // 🚀 [V52.11] 依赖安装自动化
        if (data.needs_install && typeof triggerThemeInstall === 'function') {
            triggerThemeInstall();
        }
    }

    // 🚀 [V55.0] 全局主权感知：同步版图列表，确保切换器在非设置页面也可用
    const imprintsData = await apiFetch('/api/imprints');
    if (imprintsData && imprintsData.imprints) {
        if (!window.settingsData) window.settingsData = {};
        window.settingsData._imprints = imprintsData.imprints;
        window.settingsData._active_imprint = imprintsData.active;
    }
};

window.refreshHealthMatrix = async () => {
    const container = document.getElementById('health-matrix-container');
    if (!container) return;

    const matrix = await apiFetch('/api/system/health/matrix');
    
    // 🚀 [V55.0] 增强型防抖与容错：如果接口返回异常，保持上一次的状态而不是清空
    if (!matrix || Object.keys(matrix).length === 0) {
        if (container.innerHTML === "" || container.querySelector('.loading')) {
            container.innerHTML = `<div class="health-node"><div class="node-status">DISCONNECTED</div></div>`;
        }
        return;
    }

    const html = Object.entries(matrix).map(([id, info]) => {
        let actions = '';
        if (id === 'preview') {
            actions = `
                <div class="node-actions">
                    <button class="mini-action-btn" title="服务管理" onclick="showServiceManager('preview')">⚙️</button>
                    <button class="mini-action-btn" title="打开预览" onclick="window.open('http://localhost:' + (window.settingsData.system?.serve_port || 43213), '_blank')">🌐</button>
                </div>
            `;
        } else if (id === 'onboarding') {
            const isActive = info.status === 'active';
            actions = `
                <div class="node-actions">
                    ${isActive ? 
                        `<button class="mini-action-btn" title="停止向导" onclick="controlWizard('stop')">⏹️</button>
                         <button class="mini-action-btn" title="进入向导" onclick="window.open('http://localhost:43211', '_blank')">🚀</button>` : 
                        `<button class="mini-action-btn" title="版图向导" onclick="controlWizard('start')">▶️</button>`
                    }
                </div>
            `;
        }
        return `
            <div class="health-node">
                <div class="status-dot-mini status-${info.status || 'offline'} ${id === 'dashboard' ? 'pulsing' : ''}"></div>
                <div class="node-info">
                    <div class="node-label">${info.label || id}</div>
                    <div class="node-status">${info.status || 'offline'}</div>
                </div>
                ${actions}
            </div>
        `;
    }).join('');
    
    if (container.innerHTML !== html) {
        container.innerHTML = html;
    }

};

window.updateHealthUI = (health) => {
    if (!health) return;
    const statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.innerText = `健康度: ${health.status?.toUpperCase()} (${health.imprint || 'N/A'})`;
    }
};

window.showServiceManager = (service) => {
    if (service === 'preview') {
        // 🚀 [V55.9] 物理对正：打开全功能指挥中心
        const modal = document.getElementById('terminal-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.getElementById('terminal-title').innerText = "🛰️ 预览服务主权指挥中心";
            const out = document.getElementById('terminal-output');
            if (out && out.innerHTML.trim() === "") {
                out.innerHTML = `<div class="term-line" style="color:#888">[${new Date().toLocaleTimeString()}] 控制台已就绪，请选择上方治理指令。</div>`;
            }
            
            // 实时同步当前节点状态至终端状态栏
            const labels = Array.from(document.querySelectorAll('.node-label'));
            const previewLabel = labels.find(el => el.innerText.includes("预览服务"));
            const container = previewLabel ? previewLabel.closest('.health-node') : null;
            const currentStatus = container ? container.querySelector('.node-status').innerText.toUpperCase() : 'OFFLINE';
            
            const statusEl = document.getElementById('terminal-status');
            if (statusEl) statusEl.innerText = currentStatus;
        }
    }
};

window.invokeServiceAction = async (action) => {
    const out = document.getElementById('terminal-output');
    if (action === 'restart') {
        // 🚀 [V55.9] 内部确认逻辑
        const statusEl = document.getElementById('terminal-status');
        if (statusEl && (statusEl.innerText === 'ONLINE' || statusEl.innerText === 'RUNNING')) {
            const confirmed = confirm("⚠️ 预览服务器正在运行中。重启将强制中断当前的预览会话，是否继续？");
            if (!confirmed) return;
        }

        if (statusEl) {
            statusEl.innerText = (action === 'install') ? 'INSTALLING...' : 'IGNITING...';
            statusEl.className = 'busy';
        }

        if (out) out.innerHTML += `<div class="term-line" style="color:var(--accent-primary)">[${new Date().toLocaleTimeString()}] 🚀 正在向底层引擎下达${action === 'install' ? '补全依赖' : '重启服务'}指令...</div>`;
        const res = await apiFetch(`/api/system/preview/${action}`, { method: 'POST' });
        
        if (res && res.status === 'success') {
            addAudit("✅ 预览服务器重启指令已送达。", "success");
        } else {
            const errorMsg = (res && res.detail) ? res.detail : '未知冲突';
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] 重启失败: ${errorMsg}`, "#ff4d4d");
            }
        }
    } else if (action === 'install') {
        if (out) out.innerHTML += `<div class="term-line" style="color:var(--accent-secondary)">[${new Date().toLocaleTimeString()}] 🏗️ 正在启动物理依赖补全管线 (npm install)...</div>`;
        const res = await apiFetch('/api/system/theme/install', { method: 'POST' });
        if (res && res.status === 'started') {
            addAudit("🏗️ 物理安装管线已开启。", "success");
        } else {
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] 安装启动失败`, "#ff4d4d");
            }
        }
    } else if (action === 'upgrade') {
        if (out) out.innerHTML += `<div class="term-line" style="color:var(--neon-cyan)">[${new Date().toLocaleTimeString()}] 🔄 正在向 Astro 引擎发起版本对正指令 (@astrojs/upgrade)...</div>`;
        const res = await apiFetch('/api/system/theme/upgrade', { method: 'POST' });
        if (res && res.status === 'started') {
            addAudit("🔄 主题版本升级管线已开启。", "success");
        } else {
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] 升级指令下达失败`, "#ff4d4d");
            }
        }
    } else if (action === 'rollback') {
        if (out) out.innerHTML += `<div class="term-line" style="color:#ffaa00">[${new Date().toLocaleTimeString()}] ⏪ 正在发起物理环境复原指令 (Environment Restoration)...</div>`;
        const res = await apiFetch('/api/system/theme/rollback', { method: 'POST' });
        if (res && res.status === 'success') {
            addAudit("⏪ 物理回滚成功，已恢复备份配置。", "success");
        } else {
            const msg = (res && res.message) ? res.message : '未发现可用的备份快照';
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n⚠️ [系统提示] 回滚跳过: ${msg}`, "#ffaa00");
            }
        }
    }
};

window.controlWizard = async (action) => {
    addAudit(`📡 正在向版图向导下达 [${action === 'start' ? '点火' : '销毁'}] 指令...`, "info");
    const res = await apiFetch(`/api/system/wizard/${action}`, { method: 'POST' });
    if (res && (res.status === 'started' || res.status === 'stopped' || res.status === 'already_running')) {
        addAudit(`✅ 指令已送达：向导服务已${action === 'start' ? '在线' : '下线'}。`, "success");
        setTimeout(refreshHealthMatrix, 1000);
        if (action === 'start') {
            setTimeout(() => window.open('http://localhost:43211', '_blank'), 1500);
        }
    } else {
        addAudit(`🛑 指令执行失败: ${res ? res.message : '未知错误'}`, "error");
    }
};

/**
 * 🚀 [V55.0] 紧急关机指令
 * 职责：向核心引擎发起 SIGINT 信号，安全关闭所有出版管线并停机。
 */
window.shutdownSystem = async () => {
    const confirmed = confirm("⚠️ 警告：正在执行物理级紧急关机指令！\\n\\n这将立即中断所有正在进行的出版任务、同步进程和 API 服务。是否继续？");
    if (!confirmed) return;

    try {
        addAudit("🛑 正在发起紧急停机指令...");
        // 🚀 [V55.0] 预留最后一次心跳上报
        const res = await apiFetch('/api/system/shutdown', { method: 'POST' });
        
        // 瞬间切换 UI 状态为离线
        document.body.innerHTML = `
            <div style="height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #000; color: #ff4d4d; font-family: 'Inter', sans-serif;">
                <h1 style="font-size: 3rem; margin-bottom: 1rem;">SYSTEM OFFLINE</h1>
                <p style="color: #666;">主权出版中心已安全关闭。请在终端执行 python3 plenipes.py 重新点火。</p>
                <div style="margin-top: 2rem; padding: 10px 20px; border: 1px solid #333; border-radius: 5px; cursor: pointer;" onclick="location.reload()">重新连接</div>
            </div>
        `;
    } catch (err) {
        // 关机成功通常会导致连接中断，这也是预期的
        console.log("System shutting down...");
    }
};
