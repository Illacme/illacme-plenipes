/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics - Context Shard
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
                    `[备用] ${fal.provider} (${fal.node} / ${fal.model}) ➔ 🟡 STANDBY\n` +
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
            const isEnabled = data.i18n.enabled !== false;
            if (isEnabled) {
                const targets = data.i18n.targets || [];
                const targetsStr = targets.length > 0 ? targets.join(', ') : 'NONE';
                i18nEl.innerText = `${data.i18n.source} ➔ ${targetsStr}`;
                i18nEl.style.color = '';
                i18nEl.style.textDecoration = '';
                i18nEl.style.opacity = '';
            } else {
                i18nEl.innerText = '已禁用 (Disabled)';
                i18nEl.style.color = 'var(--text-dim)';
                i18nEl.style.textDecoration = 'line-through';
                i18nEl.style.opacity = '0.6';
            }
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
