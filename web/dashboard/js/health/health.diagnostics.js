/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics & Service Action Module
 * 职责：系统上下文状态诊断加载、Onboarding 未初始化友好引导、预览服务治理长效命令投递与 Onboarding 进程调控。
 */

window.refreshGovernanceContext = async () => {
    const heartbeat = document.querySelector('.heartbeat-indicator');
    let data;
    try {
        data = await apiFetch('/api/system/context');
    } catch (e) {
        console.error("Failed to fetch governance context:", e);
    }

    if (heartbeat) {
        heartbeat.classList.remove('healthy', 'warning', 'blocked', 'status-offline', 'status-standby');
        if (!data || data.error) {
            heartbeat.classList.add('blocked');
            heartbeat.title = "系统体征：断开或阻塞 (Blocked / Offline)";
        } else if (data.onboarding_required) {
            heartbeat.classList.add('warning');
            heartbeat.title = "系统体征：文库未对正 (Warning: Onboarding Required)";
        } else if (data.ai && data.ai.status === 'degraded') {
            heartbeat.classList.add('warning');
            heartbeat.title = "系统体征：算力降级 (Warning: AI Degraded)";
        } else {
            heartbeat.classList.add('healthy');
            heartbeat.title = "系统体征：健康 (Healthy)";
        }
    }

    if (data && !data.error) {
        // 🚀 [V74.9] Onboarding 极简自动引导自愈
        if (data.onboarding_required) {
            // 如果不是设置页面，且尚未提示过，则自动弹出 SweetAlert2 友好弹窗引导
            if (window.currentView !== 'settings' && !window._onboarding_prompt_shown) {
                window._onboarding_prompt_shown = true;
                Swal.fire({
                    title: '🧱 原稿文库未配置',
                    text: '系统已成功启动，目前处于降级运行模式。为了使自动出版管线完整闭环，需要指定您本地 Markdown 文稿文库的绝对物理路径。',
                    icon: 'info',
                    background: 'rgba(20, 20, 25, 0.95)',
                    color: '#fff',
                    confirmButtonText: '立即对正配置',
                    confirmButtonColor: 'var(--accent-primary)',
                    allowOutsideClick: false,
                    allowEscapeKey: false
                }).then((result) => {
                    if (result.isConfirmed) {
                        // 跳转至系统治理设置页面，加载基础信息子面板
                        window.showView('settings', 'general');
                        // 稍作延时，确保系统配置子面板完全渲染完毕，然后高亮发光文库输入框！
                        setTimeout(() => {
                            const input = document.getElementById('cfg-vault_root');
                            if (input) {
                                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                input.focus();
                                // 添加极致科技感的冰蓝色呼吸发光视觉效果
                                input.style.outline = 'none';
                                input.style.boxShadow = '0 0 15px var(--accent-primary)';
                                input.style.borderColor = 'var(--accent-primary)';
                                input.style.transition = 'all 0.5s ease-in-out';
                                
                                // 创建发光动画
                                let pulse = true;
                                const interval = setInterval(() => {
                                    const el = document.getElementById('cfg-vault_root');
                                    if (!el) {
                                        clearInterval(interval);
                                        return;
                                    }
                                    if (pulse) {
                                        el.style.boxShadow = '0 0 5px var(--accent-primary)';
                                    } else {
                                        el.style.boxShadow = '0 0 20px var(--accent-primary)';
                                    }
                                    pulse = !pulse;
                                }, 800);
                                
                                // 用户一输入或者失焦，立即清除发光效果
                                const cleanUp = () => {
                                    clearInterval(interval);
                                    const targetEl = document.getElementById('cfg-vault_root');
                                    if (targetEl) {
                                        targetEl.style.boxShadow = '';
                                        targetEl.style.borderColor = '';
                                    }
                                };
                                input.addEventListener('input', cleanUp, { once: true });
                                input.addEventListener('blur', cleanUp, { once: true });
                            }
                        }, 500);
                    }
                });
            }
        }

        const badge = document.getElementById('active-imprint-name');
        if (badge) badge.innerText = data.imprint_name || data.imprint || 'UNKNOWN';

        const sidebarTheme = document.getElementById('sidebar-theme-display');
        if (sidebarTheme && data.theme) {
            sidebarTheme.innerText = data.theme;
        }

        const sidebarVault = document.getElementById('sidebar-vault-display');
        if (sidebarVault && data.vault) {
            const rawPath = data.vault.root || '-';
            sidebarVault.innerText = rawPath;
            sidebarVault.title = rawPath;
        }

        const displayImprint = document.getElementById('display-imprint');
        if (displayImprint) displayImprint.innerText = (data.imprint_name || data.imprint || 'DEFAULT').toUpperCase();

        const displayTheme = document.getElementById('display-theme');
        if (displayTheme) displayTheme.innerText = (data.theme || 'NONE').toUpperCase();

        const aiEl = document.getElementById('ctx-ai');
        const i18nEl = document.getElementById('ctx-i18n');
        const dialectEl = document.getElementById('ctx-dialect');


        if (dialectEl && data.vault) {
            dialectEl.innerText = data.vault.dialect || '-';
        }
        
        if (aiEl && data.ai) {
            const isDegraded = data.ai.status === 'degraded';
            aiEl.innerText = `${data.ai.provider} / ${data.ai.model}${isDegraded ? ' (⚠️ 容灾中)' : ''}`;
            
            // 📡 算力控制塔主备与容灾拓扑对正 (V75.12)
            const aiCapsule = aiEl.closest('.context-capsule');
            if (aiCapsule && data.ai.strategy) {
                const strategy = data.ai.strategy;
                const pri = data.ai.primary;
                const fal = data.ai.fallback;
                const activeLabel = isDegraded ? '⚠️ MOCK/DEGRADED' : '🟢 ACTIVE';
                
                aiCapsule.title = `算力控制塔 ───\n` +
                                  `[主力] ${pri.provider} (${pri.node} / ${pri.model}) ➔ ${activeLabel}\n` +
                                  `[备用] ${fal.provider} (${fal.node} / ${fal.model}) ➔ STANDBY 🟡\n` +
                                  `[策略] ${strategy} (自动故障切换)\n\n` +
                                  `点击一键直达算力中心 - 调度策略`;
            }

            if (isDegraded) {
                aiEl.style.color = 'var(--accent-secondary)';
                aiEl.style.fontWeight = 'bold';
                
                // 🚀 [V74.8] 友好的物理告警：仅在非设置页面且第一次感应时提示
                if (window.currentView !== 'settings' && !window._ai_warning_shown) {
                    window._ai_warning_shown = true;
                    Swal.fire({
                        title: '🛰️ 算力节点对正失败',
                        text: data.ai.warning,
                        icon: 'warning',
                        background: 'rgba(20, 20, 25, 0.95)',
                        color: '#fff',
                        confirmButtonText: '前往算力策略',
                        confirmButtonColor: 'var(--accent-primary)',
                        showCancelButton: true,
                        cancelButtonText: '暂时忽略'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.showView('compute', 'strategy');
                        }
                    });
                }
            } else {
                aiEl.style.color = '';
                aiEl.style.fontWeight = '';
            }
        }
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
    addAudit(`📡 正在向版图向导下达 [${action === 'start' ? '启动' : '停机'}] 指令...`, "info");
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

window.triggerSystemGC = async () => {
    const btn = document.getElementById('btn-system-gc');
    if (btn) {
        btn.disabled = true;
        btn.innerText = "🧹 清洗中...";
    }
    
    addAudit("🧹 正在发起 [清洗路由] 指令，物理回收失效资产...", "info");
    
    try {
        const res = await apiFetch('/api/governance/gc', { method: 'POST' });
        if (res && res.status === 'success') {
            addAudit("✅ 清洗路由成功：失效的幽灵路由与冗余文件回收完毕！", "success");
            Swal.fire({
                title: '🧹 清洗路由成功',
                text: '系统已安全唤醒清道夫 Janitor 引擎，彻底回收了出版版图内已失效的幽灵路由、过期页面和冗余垃圾资产。',
                icon: 'success',
                background: 'rgba(20, 20, 25, 0.95)',
                color: '#fff',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            const msg = (res && res.message) ? res.message : '未知异常';
            addAudit(`🛑 清洗路由失败: ${msg}`, "error");
            Swal.fire({
                title: '🚨 清洗路由失败',
                text: `清道夫引擎响应异常: ${msg}`,
                icon: 'error',
                background: 'rgba(20, 20, 25, 0.95)',
                color: '#fff',
                confirmButtonColor: 'var(--accent-primary)'
            });
        }
    } catch (e) {
        addAudit(`🛑 清洗路由请求崩溃: ${e.message || e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "🧹 清洗路由";
        }
    }
};
