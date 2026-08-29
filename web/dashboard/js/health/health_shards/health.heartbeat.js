/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics - Heartbeat & Onboarding Shard
 * 职责：系统体征状态刷新、心跳指示器点亮、Onboarding 自动引导弹窗、品牌感知与主入口门面
 * 架构：由 health.context.js 拆分而来 (SOP-02 模块拆分标准)
 */

window.refreshGovernanceContext = async () => {
    const heartbeat = document.querySelector('.heartbeat-indicator');
    let data;
    try {
        data = await apiFetch('/api/system/context');
        window.governanceContext = data;
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

        // 自动探测并补全全局配置数据，防止首屏竞态
        if (!window.settingsData || Object.keys(window.settingsData).length === 0) {
            try {
                const cfgRes = await apiFetch('/api/system/config');
                if (cfgRes) {
                    window.settingsData = { ...window.settingsData, ...(cfgRes.config || cfgRes) };
                }
            } catch (_) {}
        }

        // 📡 后台非阻塞环境凭据与免密连通嗅探 (利用 sessionStorage 极速预热，后台静默校准)
        if (typeof window.ensureEnvSensing === 'function') {
            window.ensureEnvSensing().catch(() => {});
        }

        const pubMode = data.publishing_mode || (window.settingsData && window.settingsData.governance && window.settingsData.governance.publishing_mode) || 'basic';
        const s = window.settingsData || {};

        // 官方出版模式标准定义字典
        const modeDictionary = {
            'global': { title: '全球多语言分发', short: '全球多语言', icon: '🌍', en: 'Global Distribution' },
            'enhanced': { title: '智能母语增强', short: '智能母语增强', icon: '🛰️', en: 'Enhanced Native' },
            'basic': { title: '基础物理出版', short: '基础物理出版', icon: '📜', en: 'Basic Rule' }
        };
        const currentModeMeta = modeDictionary[pubMode] || modeDictionary['basic'];

        // 渲染 6 节点流水线全景感知
        if (typeof window.renderPipelineSenses === 'function') {
            window.renderPipelineSenses(data, s, pubMode, currentModeMeta);
        }
    }

    // 🚀 [V55.0] 全局主权感知：同步品牌列表，确保切换器在非设置页面也可用
    const imprintsData = await apiFetch('/api/imprints');
    if (imprintsData && imprintsData.imprints) {
        if (!window.settingsData) window.settingsData = {};
        window.settingsData._imprints = imprintsData.imprints;
        window.settingsData._active_imprint = imprintsData.active;
    }
};
