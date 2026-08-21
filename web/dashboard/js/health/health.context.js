/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics - Context Shard
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

        // ══════════════════════════════════════════════════════════════
        // 🗺️ [6 节点因果出版流水线] 全景状态感知与左边栏胶囊数据回填
        // ══════════════════════════════════════════════════════════════

        // 阶段 1: 原稿文库
        const pipeValVault = document.getElementById('pipe-val-vault');
        const pipeDotVault = document.getElementById('pipe-dot-vault');
        const pipeCapVault = document.getElementById('pipe-cap-vault');
        if (pipeValVault && data.vault) {
            let docCount = 0;
            if (window.realManuscriptCache && window.realManuscriptCache.length > 0) {
                docCount = window.realManuscriptCache.length;
            } else if (typeof data.vault.doc_count === 'number') {
                docCount = data.vault.doc_count;
            }
            const hasVault = Boolean(data.vault.root);
            pipeValVault.innerText = hasVault ? (docCount > 0 ? `${docCount} 篇原稿` : '文库空空如也') : '未配置文库';
            if (pipeDotVault) pipeDotVault.className = hasVault && docCount > 0 ? 'pipe-dot healthy' : (hasVault ? 'pipe-dot warning' : 'pipe-dot offline');
            if (pipeCapVault) {
                pipeCapVault.title = `📂 1. 原稿文库 (Manuscript Library)\n────────────────────────\n• 收录原稿：${docCount} 篇 Markdown 文稿\n• 解析方言：${data.vault.dialect || 'Standard CommonMark'}\n• 物理文库：${data.vault.root || '暂未绑定'}\n\n💡 点击一键直达文库管理与原稿创作`;
            }
        }

        // 阶段 2: 多语言翻译
        const pipeValI18n = document.getElementById('pipe-val-i18n');
        const pipeDotI18n = document.getElementById('pipe-dot-i18n');
        const pipeCapI18n = document.getElementById('pipe-cap-i18n');
        if (pipeValI18n && data.i18n) {
            const sourceLang = data.i18n.source || 'zh';
            const targets = data.i18n.targets || [];
            const aiProvider = data.ai?.provider || 'AI';
            const isAiOnline = data.ai_status !== 'degraded' && data.ai_status !== 'offline';

            if (pubMode === 'basic') {
                pipeValI18n.innerText = `母语 (${sourceLang}) · 基础物理离线`;
                if (pipeDotI18n) pipeDotI18n.className = 'pipe-dot standby';
            } else if (pubMode === 'enhanced') {
                pipeValI18n.innerText = `母语 (${sourceLang}) · 智能 SEO 增强`;
                if (pipeDotI18n) pipeDotI18n.className = isAiOnline ? 'pipe-dot healthy' : 'pipe-dot warning';
            } else {
                pipeValI18n.innerText = targets.length > 0 ? `母语 (${sourceLang}) ➔ ${targets.length} 目标语种` : `母语 (${sourceLang}) · 全球分发待命`;
                if (pipeDotI18n) pipeDotI18n.className = isAiOnline ? 'pipe-dot healthy' : 'pipe-dot warning';
            }

            if (pipeCapI18n) {
                pipeCapI18n.title = `🌍 2. 多语言翻译 (Multilingual Translation)\n────────────────────────\n• 出版模式：${currentModeMeta.icon} ${currentModeMeta.title} (${currentModeMeta.en})\n• 母语言：${sourceLang.toUpperCase()}\n• 目标语种：${targets.length > 0 ? targets.join(', ').toUpperCase() : '未配置目标语种 (仅母语出版)'}\n• 算力基座：${aiProvider} (${isAiOnline ? '🟢 在线' : '🟡 待命'})\n\n💡 点击一键直达多语种治理与翻译风格配置`;
            }
        }

        // 阶段 3: 网站主题
        const pipeValTheme = document.getElementById('pipe-val-theme');
        const pipeDotTheme = document.getElementById('pipe-dot-theme');
        const pipeCapTheme = document.getElementById('pipe-cap-theme');
        if (pipeValTheme) {
            const rawTheme = data.theme || s.active_theme || 'SOVEREIGN';
            const cleanThemeName = rawTheme.replace(/\s*\([^)]*\)/g, '').trim().toUpperCase() || 'SOVEREIGN';
            pipeValTheme.innerText = `${cleanThemeName} · ${currentModeMeta.short}`;
            if (pipeDotTheme) pipeDotTheme.className = 'pipe-dot healthy';

            // 动态解析当前模式下的 SEO 策略
            const seoStrategy = s.governance?.seo_strategy || (pubMode === 'basic' ? 'heuristic' : (pubMode === 'enhanced' ? 'ai_alignment' : 'ai_sync'));
            const strategyLabels = {
                'ai_sync': 'AI 翻译同步 (精确语义翻译)',
                'ai_localized': 'AI 区域搜索对齐 (本地化检索优化)',
                'ai_alignment': 'AI 标题与点击率调优 (提升 CTR)',
                'ai_authority': 'AI 核心概念标记 (权威实体提取)',
                'heuristic': '结构化提取 (H1与正文规则抓取)',
                'protocol': '社交协议增强 (JSON-LD / Open Graph)'
            };
            const strategyDesc = strategyLabels[seoStrategy] || seoStrategy;

            if (pipeCapTheme) {
                pipeCapTheme.title = `🎭 3. 网站主题 (Visual Theme & Layout)\n────────────────────────\n• 装帧主题：${cleanThemeName} ${rawTheme.includes('DEFAULT') ? '(系统默认)' : ''}\n• 出版模式：${currentModeMeta.icon} ${currentModeMeta.title} (${currentModeMeta.en})\n• SEO 策略：${strategyDesc}\n\n💡 点击一键直达视觉主题与出版模式设置`;
            }
        }

        // 阶段 4: 网址路径
        const pipeValRouting = document.getElementById('pipe-val-routing');
        const pipeDotRouting = document.getElementById('pipe-dot-routing');
        const pipeCapRouting = document.getElementById('pipe-cap-routing');
        if (pipeValRouting) {
            const dirMode = s.translation?.slug_dir_mode || 'flat';
            const slugMode = s.translation?.slug_mode || 'ai';
            const dirLabels = { 'flat': '极简根目录', 'prefix': 'SEO 语言前缀', 'nested': '文库目录树' };
            const slugLabels = { 'ai': 'AI 语义 Slug', 'filename': '原文件名清洗' };
            pipeValRouting.innerText = `${dirLabels[dirMode] || '极简根目录'} · ${slugLabels[slugMode] || 'AI 语义'}`;
            if (pipeDotRouting) pipeDotRouting.className = 'pipe-dot healthy';
            if (pipeCapRouting) {
                const sampleUrl = dirMode === 'prefix' ? '/en/hello-world' : '/hello-world';
                pipeCapRouting.title = `🧭 4. 网址路径 (URL Routing & Slug)\n────────────────────────\n• 路径结构：${dirLabels[dirMode] || dirMode}\n• 生成法则：${slugLabels[slugMode] || slugMode}\n• 访问范例：https://yourdomain.com${sampleUrl}\n\n💡 点击一键直达网址路径定制与全息沙盒`;
            }
        }

        // 阶段 5: 独立站托管 (优先于社媒分发)
        const pipeValHosting = document.getElementById('pipe-val-hosting');
        const pipeDotHosting = document.getElementById('pipe-dot-hosting');
        const pipeCapHosting = document.getElementById('pipe-cap-hosting');
        if (pipeValHosting) {
            const platforms = s.platforms || {};
            const egress = s.egress || {};
            const direct = s.publish_control?.direct_upload || {};

            let hostingId = '';
            let hostingName = '';
            let isHostingActive = false;
            let isHostingReady = false;
            let hostingCredLabel = '凭据就绪';
            let hostingDetail = '';
            let hostingCfg = {};

            const hostingLabels = {
                'github_pages': 'GitHub Pages',
                'gitee_pages': 'Gitee Pages',
                'cloudflare_pages': 'Cloudflare Pages',
                'netlify': 'Netlify',
                'vercel': 'Vercel',
                'render': 'Render',
                'railway': 'Railway',
                'sftp': 'SFTP / SSH',
                's3': 'AWS S3'
            };

            // 1. 严格以插件中心/当前品牌的激活态 (is_in_use) 为准
            if (Array.isArray(data.plugins)) {
                const activeHostingPlugin = data.plugins.find(p => p.category === 'hosting' && p.is_in_use === true);
                if (activeHostingPlugin) {
                    hostingId = activeHostingPlugin.id;
                    hostingName = activeHostingPlugin.name || hostingLabels[hostingId] || hostingId;
                    isHostingActive = true;
                    hostingCfg = activeHostingPlugin.cfg || direct[hostingId] || {};
                }
            }

            // 2. 兜底从当前品牌的配置直读 (仅当 direct[id].enabled === true 或 platforms[id].enabled === true 时)
            if (!isHostingActive) {
                for (const [id, label] of Object.entries(hostingLabels)) {
                    const dCfg = direct[id];
                    const pCfg = platforms[id];
                    const eCfg = egress[id];
                    if ((dCfg && dCfg.enabled === true) || (pCfg && pCfg.enabled === true) || (eCfg && eCfg.enabled === true)) {
                        hostingId = id;
                        hostingName = label;
                        isHostingActive = true;
                        hostingCfg = dCfg || pCfg || eCfg || {};
                        break;
                    }
                }
            }

            if (isHostingActive) {
                if (window.isPluginCredentialReady) {
                    const cred = window.isPluginCredentialReady(hostingId, 'hosting', hostingCfg);
                    isHostingReady = cred.ready;
                    hostingCredLabel = cred.label || (isHostingReady ? '凭据就绪' : '待填凭据');
                } else {
                    const hasCredentials = Boolean(hostingCfg.token || hostingCfg.repo || hostingCfg.host || hostingCfg.access_key_id);
                    isHostingReady = hasCredentials;
                    hostingCredLabel = isHostingReady ? '凭据就绪' : '待填凭据';
                }

                if (hostingCfg.repo) hostingDetail = `部署目标：${hostingCfg.repo}`;
                else if (hostingCfg.host) hostingDetail = `主机：${hostingCfg.host}`;

                pipeValHosting.innerText = `${hostingName} · ${hostingCredLabel}`;
                if (pipeDotHosting) pipeDotHosting.className = isHostingReady ? 'pipe-dot healthy' : 'pipe-dot warning';
            } else {
                pipeValHosting.innerText = '未开启独立站托管';
                if (pipeDotHosting) pipeDotHosting.className = 'pipe-dot offline';
            }

            if (pipeCapHosting) {
                if (isHostingActive) {
                    pipeCapHosting.title = `🌐 5. 独立站托管 (Static Site Hosting)\n────────────────────────\n• 首选平台：${hostingName}\n• 鉴权状态：${isHostingReady ? `✅ ${hostingCredLabel}` : '⚠️ 缺失 (请补全 Token 或仓库配置)'}\n${hostingDetail ? `• ${hostingDetail}\n` : ''}\n💡 点击一键直达独立站全站托管与部署配置`;
                } else {
                    pipeCapHosting.title = `🌐 5. 独立站托管 (Static Site Hosting)\n────────────────────────\n• 平台状态：暂未开启任何主站托管服务\n• 能力说明：开启后，系统在编译完成后自动将全语种独立站同步发布至云端。\n\n💡 点击一键前往插件中心开启托管平台`;
                }
            }
        }

        // 阶段 6: 社交平台同步 (独立站上线后全网广播)
        const pipeValSyndication = document.getElementById('pipe-val-syndication');
        const pipeDotSyndication = document.getElementById('pipe-dot-syndication');
        const pipeCapSyndication = document.getElementById('pipe-cap-syndication');
        if (pipeValSyndication) {
            const synd = s.syndication || {};
            const activePlatforms = [];
            const platformNames = {
                'devto': 'Dev.to',
                'hashnode': 'Hashnode',
                'medium': 'Medium',
                'x_twitter': 'X (Twitter)',
                'linkedin': 'LinkedIn',
                'zhihu': '知乎',
                'juejin': '稀土掘金',
                'ghost': 'Ghost'
            };

            // 1. 严格检查当前品牌 settingsData 中的显式启用状态
            Object.keys(platformNames).forEach(k => {
                const pCfg = synd[k];
                if (pCfg && pCfg.enabled === true) {
                    const hasToken = Boolean(pCfg.api_key || pCfg.token || pCfg.access_token);
                    activePlatforms.push({ id: k, name: platformNames[k], ready: hasToken });
                }
            });

            // 2. 联动感知 data.plugins 矩阵 (严格且仅匹配当前品牌激活状态 is_in_use === true)
            if (Array.isArray(data.plugins)) {
                data.plugins.filter(p => p.category === 'publisher' && p.is_in_use === true).forEach(p => {
                    if (!activePlatforms.some(a => a.id === p.id)) {
                        activePlatforms.push({ id: p.id, name: p.name || platformNames[p.id] || p.id, ready: p.status === 'READY' || Boolean(p.cfg?.token || p.cfg?.api_key) });
                    }
                });
            }

            if (activePlatforms.length > 0) {
                const names = activePlatforms.map(p => p.name).join(', ');
                const allReady = activePlatforms.every(p => p.ready);
                pipeValSyndication.innerText = `${names} (${activePlatforms.length} 渠道就绪)`;
                if (pipeDotSyndication) pipeDotSyndication.className = allReady ? 'pipe-dot healthy' : 'pipe-dot warning';
            } else {
                pipeValSyndication.innerText = '未开启社交分发';
                if (pipeDotSyndication) pipeDotSyndication.className = 'pipe-dot offline';
            }

            if (pipeCapSyndication) {
                if (activePlatforms.length > 0) {
                    const readyCount = activePlatforms.filter(p => p.ready).length;
                    pipeCapSyndication.title = `🚀 6. 社交平台同步 (Social Media Syndication)\n────────────────────────\n• 已启用平台：${activePlatforms.map(p => p.name).join(', ')} (共 ${activePlatforms.length} 个)\n• 凭据齐备数：${readyCount} / ${activePlatforms.length} 个渠道\n• 同步策略：Canonical 原创版权保护 + 社交平台自动化广播\n\n💡 点击一键唤起多平台社交媒体同步与广播中枢`;
                } else {
                    pipeCapSyndication.title = `🚀 6. 社交平台同步 (Social Media Syndication)\n────────────────────────\n• 渠道状态：暂未开启任何社交媒体同步渠道\n• 能力说明：开启后，单篇文稿可一键多语言分发至 Dev.to / Medium / 知乎等社交平台。\n\n💡 点击一键前往插件中心开启社交分发平台`;
                }
            }
        }

        // 💾 [Zero-Flicker 状态快照缓存]
        try {
            const pipelineSnapshot = {
                vault: { val: pipeValVault?.innerText, dot: pipeDotVault?.className },
                i18n: { val: pipeValI18n?.innerText, dot: pipeDotI18n?.className },
                theme: { val: pipeValTheme?.innerText, dot: pipeDotTheme?.className },
                routing: { val: pipeValRouting?.innerText, dot: pipeDotRouting?.className },
                hosting: { val: pipeValHosting?.innerText, dot: pipeDotHosting?.className },
                syndication: { val: pipeValSyndication?.innerText, dot: pipeDotSyndication?.className }
            };
            sessionStorage.setItem('_illacme_pipe_cache', JSON.stringify(pipelineSnapshot));
        } catch (_) {}

        // 兼容旧版选择器回填 (如有)
        const aiEl = document.getElementById('ctx-ai');
        const i18nEl = document.getElementById('ctx-i18n');
        const dialectEl = document.getElementById('ctx-dialect');
        if (dialectEl && data.vault) dialectEl.innerText = data.vault.dialect || '-';
        if (aiEl && data.ai) aiEl.innerText = `${data.ai.provider || 'AI'} / ${data.ai.model || 'READY'}`;
        if (i18nEl && data.i18n) i18nEl.innerText = `${data.i18n.source || 'zh'} ➔ ${(data.i18n.targets || []).join(', ') || 'NONE'}`;

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
