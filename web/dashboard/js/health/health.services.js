/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics - Services Shard
 */

window.invokeServiceAction = async (action) => {
    const out = document.getElementById('terminal-output');
    const statusEl = document.getElementById('terminal-status');

    if (action === 'restart') {
        // 🚀 [V55.9] 内部确认逻辑
        if (statusEl && (statusEl.innerText === 'ONLINE' || statusEl.innerText === 'RUNNING')) {
            const confirmed = confirm("⚠️ 预览服务器正在运行中。重启将强制中断当前的预览会话，是否继续？");
            if (!confirmed) return;
        }

        if (statusEl) {
            statusEl.innerText = (action === 'install') ? 'INSTALLING...' : 'IGNITING...';
            statusEl.className = 'busy';
        }

        if (out) out.innerHTML += `<div class="term-line" style="color:var(--accent-primary)">[${new Date().toLocaleTimeString()}] 🚀 正在向底层引擎下达${action === 'install' ? '补全依赖' : '重启服务'}指令...</div>`;
        
        try {
            const res = await apiFetch(`/api/system/preview/${action}`, { method: 'POST' });

            if (res && res.status === 'success') {
                addAudit("✅ 预览服务器重启指令已送达。", "success");
            } else {
                const errorMsg = (res && res.detail) ? res.detail : '未知冲突';
                if (typeof appendTerminalLog === 'function') {
                    appendTerminalLog(`\n❌ [系统错误] 重启失败: ${errorMsg}`, "#ff4d4d");
                }
            }
        } catch (err) {
            console.error('[Health Service] Restart Error:', err);
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] 重启网关连接失败: ${err.message || '网关未响应'}`, "#ff4d4d");
            }
            if (typeof addAudit === 'function') addAudit(`❌ 预览服务重启指令遭遇物理阻塞`, "error");
            if (statusEl) {
                statusEl.innerText = 'ERROR';
                statusEl.className = 'error';
            }
        }
    } else if (action === 'stop') {
        if (statusEl && statusEl.innerText.trim().toUpperCase() === 'OFFLINE') return;
        if (statusEl) {
            statusEl.innerText = 'STOPPING...';
            statusEl.className = 'busy';
        }
        if (out) out.innerHTML += `<div class="term-line" style="color:#ff4d4d">[${new Date().toLocaleTimeString()}] ⏹️ 正在向底层引擎下达停止服务指令...</div>`;
        
        try {
            const res = await apiFetch('/api/system/preview/stop', { method: 'POST' });
            if (res && res.status === 'success') {
                addAudit("✅ 预览服务器已成功停止。", "success");
                if (statusEl) {
                    statusEl.innerText = 'OFFLINE';
                    statusEl.className = 'error';
                }
                if (typeof refreshHealthMatrix === 'function') {
                    setTimeout(refreshHealthMatrix, 500);
                }
            } else {
                const errorMsg = (res && res.detail) ? res.detail : '未知冲突';
                if (typeof appendTerminalLog === 'function') {
                    appendTerminalLog(`\n❌ [系统错误] 停止失败: ${errorMsg}`, "#ff4d4d");
                }
            }
        } catch (err) {
            console.error('[Health Service] Stop Error:', err);
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] 停机指令下达失败: ${err.message || '网络连接中断'}`, "#ff4d4d");
            }
            if (typeof addAudit === 'function') addAudit(`❌ 停止物理服务失败: 接口未响应`, "error");
            if (statusEl) {
                statusEl.innerText = 'ERROR';
                statusEl.className = 'error';
            }
        }
    } else if (action === 'install') {
        if (out) out.innerHTML += `<div class="term-line" style="color:var(--accent-secondary)">[${new Date().toLocaleTimeString()}] 🏗️ 正在启动物理依赖补全管线 (npm install)...</div>`;
        try {
            const res = await apiFetch('/api/system/theme/install', { method: 'POST' });
            if (res && res.status === 'started') {
                addAudit("🏗️ 物理安装管线已开启。", "success");
            } else {
                if (typeof appendTerminalLog === 'function') {
                    appendTerminalLog(`\n❌ [系统错误] 安装启动失败`, "#ff4d4d");
                }
            }
        } catch (err) {
            console.error('[Health Service] Install Error:', err);
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] npm依赖补全失败: ${err.message || '网关连接中断'}`, "#ff4d4d");
            }
            if (typeof addAudit === 'function') addAudit("❌ 物理安装管线开启失败", "error");
        }
    } else if (action === 'upgrade') {
        if (out) out.innerHTML += `<div class="term-line" style="color:var(--neon-cyan)">[${new Date().toLocaleTimeString()}] 🔄 正在向 Astro 引擎发起版本对正指令 (@astrojs/upgrade)...</div>`;
        try {
            const res = await apiFetch('/api/system/theme/upgrade', { method: 'POST' });
            if (res && res.status === 'started') {
                addAudit("🔄 主题版本升级管线已开启。", "success");
            } else {
                if (typeof appendTerminalLog === 'function') {
                    appendTerminalLog(`\n❌ [系统错误] 升级指令下达失败`, "#ff4d4d");
                }
            }
        } catch (err) {
            console.error('[Health Service] Upgrade Error:', err);
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] astro升级指令执行失败: ${err.message || '网络连接中断'}`, "#ff4d4d");
            }
            if (typeof addAudit === 'function') addAudit("❌ 版本对正升级失败", "error");
        }
    } else if (action === 'rollback') {
        if (out) out.innerHTML += `<div class="term-line" style="color:#ffaa00">[${new Date().toLocaleTimeString()}] ⏪ 正在发起物理环境复原指令 (Environment Restoration)...</div>`;
        try {
            const res = await apiFetch('/api/system/theme/rollback', { method: 'POST' });
            if (res && res.status === 'success') {
                addAudit("⏪ 物理回滚成功，已恢复备份配置。", "success");
            } else {
                const msg = (res && res.message) ? res.message : '未发现可用的备份快照';
                if (typeof appendTerminalLog === 'function') {
                    appendTerminalLog(`\n⚠️ [系统提示] 回滚跳过: ${msg}`, "#ffaa00");
                }
            }
        } catch (err) {
            console.error('[Health Service] Rollback Error:', err);
            if (typeof appendTerminalLog === 'function') {
                appendTerminalLog(`\n❌ [系统错误] 环境复原指令失败: ${err.message || '连接超时'}`, "#ff4d4d");
            }
            if (typeof addAudit === 'function') addAudit("❌ 物理环境复原回滚遭遇错误", "error");
        }
    }
};

window.controlWizard = async (action) => {
    addAudit(`📡 正在向品牌向导下达 [${action === 'start' ? '启动' : '停机'}] 指令...`, "info");
    try {
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
    } catch (err) {
        console.error('[Health Service] Wizard Control Error:', err);
        addAudit(`🛑 网关未响应，向导指令发送失败: ${err.message || '网络连接故障'}`, "error");
    }
};
