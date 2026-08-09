/**
 * 🛰️ [V103.0] Illacme Plenipes Single-Article Single-Language Syndication Drawer Component
 * 职责：单篇文章单语种社交广播控制面板。
 * 🚀 [全站配置联动无缝流]：
 *   1. 语种全量解包：完整合并呈现母语 (source.lang_code) + 所有已激活的目标语种 (i18n_settings.targets / i18n_routing)。
 *   2. 渠道一键去配置：对未配置/未启用的渠道提供「⚙️ 去配置/激活」直达按钮，一键调起 openPluginConfig 插件编辑器。
 *   3. 物理极速流控：对接后端 /api/vault/redispatch 底层分发管线，实时显示 LLM 翻译与分发全流。
 */

window.openArticleSyndicationDrawer = async function (relPath, articleTitle) {
    window.currentSyndicatingRelPath = relPath;
    window.currentSyndicatingTitle = articleTitle;

    // 🚀 [V120.0] 预热抓取该文档在各语种下的远程文章物权记录 (syndication_records)
    window.currentSyndicationRecords = [];
    const fetchApi = window.apiFetch || (async (url, opts) => {
        const r = await fetch(url, opts);
        return r.json();
    });

    try {
        const recordsData = await fetchApi(`/api/syndication/records/${encodeURIComponent(relPath)}`);
        if (recordsData && recordsData.records) {
            window.currentSyndicationRecords = recordsData.records;
        }
    } catch (e) {
        console.warn("[Article Syndication] Fetch syndication records failed:", e);
    }

    // 预热全域能力矩阵数据，防范从非插件页面直接唤起 openPluginConfig 时元数据缺失
    if (!window.allPlugins || window.allPlugins.length === 0) {
        try {
            const res = await fetchApi('/api/plugins/list');
            if (res && res.plugins) window.allPlugins = res.plugins;
        } catch (e) {
            console.warn("[Article Syndication] Prefetch plugin list failed:", e);
        }
    }

    const cfgData = window.settingsData || {};
    const i18n = cfgData.i18n_settings || {};
    const syndicationCfg = cfgData.syndication || {};

    // 1. 🌐 物理解包合规语种字典
    const langMap = {
        'zh': { name: '中文 (ZH)', icon: '🇨🇳' },
        'en': { name: 'English (EN)', icon: '🇬🇧' },
        'ja': { name: '日本語 (JA)', icon: '🇯🇵' },
        'ko': { name: '한국어 (KO)', icon: '🇰🇷' },
        'de': { name: 'Deutsch (DE)', icon: '🇩🇪' },
        'fr': { name: 'Français (FR)', icon: '🇫🇷' },
        'es': { name: 'Español (ES)', icon: '🇪🇸' },
        'ru': { name: 'Русский (RU)', icon: '🇷🇺' },
        'ar': { name: 'العربية (AR)', icon: '🇸🇦' }
    };

    const sourceLangCode = (i18n.source?.lang_code || cfgData.source?.lang_code || 'zh').toLowerCase();
    const rawTargets = i18n.targets || cfgData.translation?.targets || cfgData.i18n_routing?.targets || ['en'];
    const targetLangCodes = Array.isArray(rawTargets)
        ? rawTargets.map(t => (typeof t === 'string' ? t : t.lang_code || t.code || '').toLowerCase()).filter(Boolean)
        : [];

    const allConfiguredCodes = Array.from(new Set([sourceLangCode, ...targetLangCodes]));
    const availableLangs = allConfiguredCodes.map(code => {
        const info = langMap[code] || { name: code.toUpperCase(), icon: '🌍' };
        return {
            code: code,
            name: info.name,
            icon: info.icon,
            isSource: code === sourceLangCode
        };
    });

    // 2. 🚀 物理感应全量分发渠道及其凭据就绪状态 (Credential & Plugin Matrix Full Probe)
    const platformMetadata = window.platformMetadata || {
        'devto': { name: 'Dev.to', icon: '👩‍💻', desc: '开发者社区 (支持 Markdown / Canonical URL 注入)' },
        'medium': { name: 'Medium', icon: '📝', desc: '高权重长文平台' },
        'hashnode': { name: 'Hashnode', icon: '🔷', desc: '技术博客平台' },
        'substack': { name: 'Substack', icon: '📮', desc: 'Newsletter 通讯平台' },
        'zhihu': { name: '知乎', icon: '💡', desc: '中文知识社区' },
        'wechat': { name: '微信公众号', icon: '💬', desc: '微信图文矩阵' },
        'ghost': { name: 'Ghost CLI', icon: '👻', desc: '独立 Ghost 站点 API' },
        'wordpress': { name: 'WordPress', icon: '📰', desc: 'WordPress 自动打标发布' },
        'juejin': { name: '掘金', icon: '🧱', desc: '掘金技术社区' },
        'linkedin': { name: 'LinkedIn', icon: '💼', desc: '职场社交平台' },
        'telegram': { name: 'Telegram', icon: '✈️', desc: 'Telegram 频道与群组 Bot' },
        'discord': { name: 'Discord', icon: '💬', desc: 'Discord Webhook 社区频道' }
    };
    window.platformMetadata = platformMetadata;

    // 辅助断言 1：物理检测某个渠道是否已满足全局总开关开启且配置就绪 (is_enabled === true)
    const checkChannelReadiness = (key, itemCfg) => {
        // 1. 优先查验全域能力矩阵中的全局总开关状态 target.is_enabled
        if (window.allPlugins && Array.isArray(window.allPlugins)) {
            const cleanKey = key.toLowerCase().replace('_', '');
            const target = window.allPlugins.find(p => p.id === key || p.id.replace('_', '') === cleanKey);
            if (target) {
                // 只有全局总开关已开启 (is_enabled === true)，才表示该插件已被激活并就绪
                return !!target.is_enabled;
            }
        }
        // 2. 备选在配置对象中探查 enabled
        if (itemCfg && typeof itemCfg === 'object') {
            return itemCfg.enabled === true;
        }
        return false;
    };

    // 辅助断言 2：检测在当前品牌版图设置中该分发渠道是否已被激活启用 (Brand In-Use Active)
    const checkBrandActive = (key, itemCfg) => {
        // 1. 优先查验全域能力矩阵中的物理品牌激活状态 target.is_in_use (对应 Pod 卡片 Switch)
        if (window.allPlugins && Array.isArray(window.allPlugins)) {
            const cleanKey = key.toLowerCase().replace('_', '');
            const target = window.allPlugins.find(p => p.id === key || p.id.replace('_', '') === cleanKey);
            if (target) {
                return !!target.is_in_use;
            }
        }
        // 2. 备选在品牌配置对象中探查 enabled / is_in_use 字段
        if (itemCfg && typeof itemCfg === 'object') {
            if (itemCfg.enabled === true || itemCfg.is_in_use === true) return true;
        }
        return false;
    };

    const activePlatforms = [];
    // 遍历所有已知平台清单
    Object.keys(platformMetadata).forEach(key => {
        const itemCfg = syndicationCfg[key] || syndicationCfg[key.replace('_', '')] || {};
        const isReady = checkChannelReadiness(key, itemCfg);
        const isBrandActive = checkBrandActive(key, itemCfg);
        const meta = platformMetadata[key];

        activePlatforms.push({
            id: key,
            name: meta.name,
            icon: meta.icon,
            desc: meta.desc,
            isReady: isReady,
            isBrandActive: isBrandActive,
            isChecked: isReady && isBrandActive
        });
    });
    window.currentActivePlatforms = activePlatforms;

    // 3. 🔍 探查文章各语种的翻译与就绪状态
    let docStatusData = null;
    try {
        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        docStatusData = await fetchApi(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
    } catch (e) {
        console.warn("[Article Syndication] Unable to fetch doc dispatch status:", e);
    }

    window.currentArticleDispatchStatus = docStatusData;

    // 🚀 [全局抽屉互斥排他] 自动平滑收起其他可能已打开的抽屉，保证当前单篇广播专注度
    if (typeof window.closeVaultDrawer === 'function') window.closeVaultDrawer();
    if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
    const reviewOverlay = document.getElementById('review-drawer-overlay');
    if (reviewOverlay) {
        reviewOverlay.style.opacity = '0';
        setTimeout(() => { reviewOverlay.style.display = 'none'; }, 200);
    }

    // 🚀 [半透明毛玻璃背景遮罩] 阻断背景列表误触，点击空白区自动平滑关闭
    let backdropEl = document.getElementById('article-syndicate-drawer-backdrop');
    if (!backdropEl) {
        backdropEl = document.createElement('div');
        backdropEl.id = 'article-syndicate-drawer-backdrop';
        backdropEl.style.cssText = `
            position: fixed; inset: 0;
            background: rgba(0, 0, 0, 0.45); backdrop-filter: blur(2px);
            z-index: 9998; opacity: 0; pointer-events: none;
            transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        `;
        backdropEl.onclick = () => window.closeArticleSyndicationDrawer();
        document.body.appendChild(backdropEl);
    }
    requestAnimationFrame(() => {
        backdropEl.style.opacity = '1';
        backdropEl.style.pointerEvents = 'auto';
    });

    let drawerEl = document.getElementById('article-syndicate-drawer');
    if (!drawerEl) {
        drawerEl = document.createElement('div');
        drawerEl.id = 'article-syndicate-drawer';
        drawerEl.className = 'syndicate-drawer-overlay';
        drawerEl.style.cssText = `
            position: fixed; top: 0; right: -440px; width: 420px; height: 100vh;
            background: rgba(15, 17, 26, 0.96); backdrop-filter: blur(16px);
            border-left: 1px solid var(--glass-border, rgba(255, 255, 255, 0.12));
            box-shadow: -10px 0 35px rgba(0, 0, 0, 0.6); z-index: 9999;
            transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            padding: 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px;
            color: var(--text-bright, #fff); font-family: system-ui, -apple-system, sans-serif;
        `;
        document.body.appendChild(drawerEl);
    }

    const displayTitle = articleTitle || relPath || '未命名文章';
    const readyPlatformsCount = activePlatforms.filter(p => p.isReady).length;
    const checkedPlatformsCount = activePlatforms.filter(p => p.isChecked).length;

    drawerEl.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px;">
            <h3 style="margin: 0; font-size: 1.08rem; color: var(--accent-secondary, #00f2fe); display: flex; align-items: center; gap: 8px;">
                📢 社交媒体分发
            </h3>
            <button type="button" onclick="window.closeArticleSyndicationDrawer()" style="background: transparent; border: none; color: var(--text-dim); font-size: 1.4rem; cursor: pointer; line-height: 1;">×</button>
        </div>

        <div style="font-size: 0.8rem; color: var(--text-dim); line-height: 1.4; background: rgba(255, 255, 255, 0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);">
            目标原稿：<b style="color: #fff; word-break: break-all;">${displayTitle}</b>
        </div>

        <!-- 1. 选择广播语种 (母语 + 目标语种矩阵) -->
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="font-size: 0.82rem; font-weight: 600; color: var(--accent-primary, #00f2fe); display: flex; align-items: center; justify-content: space-between;">
                <span>1. 选择广播语种 (母语 + 目标语种矩阵)</span>
                <span style="font-size: 0.68rem; color: var(--text-dim); opacity: 0.8;">共 ${availableLangs.length} 个受控语种</span>
            </label>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;" id="syndicate-lang-picker">
                ${availableLangs.map((l, idx) => `
                    <label class="lang-radio-btn" style="padding: 6px 12px; border: 1px solid ${idx === 0 ? 'var(--accent-secondary)' : 'rgba(255, 255, 255, 0.15)'}; border-radius: 20px; font-size: 0.75rem; cursor: pointer; display: flex; align-items: center; gap: 6px; background: ${idx === 0 ? 'rgba(0, 242, 255, 0.15)' : 'rgba(255, 255, 255, 0.02)'};">
                        <input type="radio" name="syndicate_lang" value="${l.code}" ${idx === 0 ? 'checked' : ''} style="display: none;" onchange="window.onSyndicateLangChange(this, '${relPath}')">
                        ${l.icon} ${l.name} ${l.isSource ? '<span style="font-size:0.62rem; background:rgba(0,242,255,0.2); padding:1px 4px; border-radius:4px;">(母语)</span>' : '<span style="font-size:0.62rem; background:rgba(187,134,252,0.2); padding:1px 4px; border-radius:4px; color:#bb86fc;">(译文)</span>'}
                    </label>
                `).join('')}
            </div>
            <!-- 译文就绪提示卡片 -->
            <div id="syndicate-translation-readiness-tip" style="font-size: 0.72rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px solid rgba(0, 255, 136, 0.2); padding: 6px 10px; border-radius: 6px; margin-top: 2px;">
                🟢 当前选中的是原稿母语，无需翻译，启动后可直达社交分发平台。
            </div>
        </div>

        <!-- 2. 勾选社交分发平台 (支持一键点击 ⚙️ 去配置/激活 直达插件配置面板) -->
        <div style="display: flex; flex-direction: column; gap: 8px; flex: 1; min-height: 0; overflow-y: auto;">
            <label style="font-size: 0.82rem; font-weight: 600; color: var(--accent-primary, #00f2fe); display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <span>2. 勾选目标社媒分发渠道</span>
                <span id="syndicate-channel-status-badge" style="font-size: 0.68rem; color: ${readyPlatformsCount > 0 ? '#00ff88' : '#f59e0b'}; font-weight: 600; white-space: nowrap; flex-shrink: 0;">
                    ${readyPlatformsCount > 0 ? `🟢 ${readyPlatformsCount} 个渠道就绪 (当前选中 ${checkedPlatformsCount} 个)` : '⚠️ 暂无已就绪渠道，请先配置'}
                </span>
            </label>

            <div style="display: flex; flex-direction: column; gap: 8px;" id="syndicate-platform-list-container">
                ${activePlatforms.length > 0 ? activePlatforms.map(p => {
                    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
                    const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();
                    const record = (window.currentSyndicationRecords || []).find(r => 
                        (r.target_id || '').toLowerCase() === p.id.toLowerCase() &&
                        (r.lang_code || '').toLowerCase() === selectedLang
                    );
                    const hasRemoteRecord = !!(record && record.remote_article_id);
                    const remoteUrl = record ? record.remote_url : null;
                    const noUpdateSupport = ['medium', 'substack', 'zhihu'].includes(p.id.toLowerCase());

                    let statusBadgeHtml = '🟢 已就绪';
                    let actionBadgeHtml = '🚀 首次发布 (Create)';
                    let actionBadgeBg = 'rgba(0, 242, 255, 0.12)';
                    let actionBadgeColor = '#00f2fe';

                    if (hasRemoteRecord) {
                        if (noUpdateSupport) {
                            actionBadgeHtml = '⚠️ 降级新建 (Re-create)';
                            actionBadgeBg = 'rgba(251, 191, 36, 0.12)';
                            actionBadgeColor = '#fbbf24';
                        } else {
                            actionBadgeHtml = '🔄 覆写更新 (Update)';
                            actionBadgeBg = 'rgba(187, 134, 252, 0.18)';
                            actionBadgeColor = '#bb86fc';
                        }
                    }

                    return `
                    <div class="glass-panel" style="padding: 10px 12px; border-radius: 8px; border: 1px solid ${hasRemoteRecord ? 'rgba(187, 134, 252, 0.35)' : (p.isReady ? 'rgba(0, 255, 136, 0.25)' : 'rgba(255,255,255,0.06)')}; display: flex; flex-direction: column; gap: 8px; opacity: ${p.isReady ? '1' : '0.65'}; background: ${hasRemoteRecord ? 'rgba(187, 134, 252, 0.04)' : (p.isReady ? 'rgba(0, 255, 136, 0.03)' : 'rgba(255,255,255,0.01)')};">
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <input type="checkbox" value="${p.id}" class="syndicate-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'} style="accent-color: var(--accent-secondary); width: 16px; height: 16px; cursor: ${p.isReady ? 'pointer' : 'not-allowed'};">
                                <div>
                                    <div style="font-size: 0.82rem; font-weight: 600; color: ${p.isReady ? '#fff' : 'var(--text-dim)'};">${p.icon} ${p.name}</div>
                                    <div style="font-size: 0.68rem; color: var(--text-dim);">${p.desc}</div>
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 6px;">
                                ${p.isReady ? `
                                    <span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; white-space: nowrap; background: ${actionBadgeBg}; color: ${actionBadgeColor}; border: 1px solid ${actionBadgeColor}55; font-weight: 600;">${actionBadgeHtml}</span>
                                    <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="修改此渠道的 Token 密钥或配置" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">⚙️</button>
                                ` : `
                                    <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="前往配置并激活此渠道" style="background: rgba(0, 242, 255, 0.15); border: 1px solid rgba(0, 242, 255, 0.35); color: var(--neon-cyan, #00f2fe); border-radius: 4px; padding: 3px 8px; font-size: 0.68rem; font-weight: 600; cursor: pointer; white-space: nowrap;">⚙️ 去配置/激活</button>
                                `}
                            </div>
                        </div>
                        ${hasRemoteRecord ? `
                            <div style="padding-top: 6px; border-top: 1px dashed rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: space-between; font-size: 0.68rem; color: var(--text-dim);">
                                <div style="display: flex; align-items: center; gap: 6px; overflow: hidden;">
                                    <span>🆔 ID: <code>${record.remote_article_id}</code></span>
                                    ${remoteUrl ? `<a href="${remoteUrl}" target="_blank" style="color: #00f2fe; text-decoration: none;">🔗 对端文章 ↗</a>` : ''}
                                </div>
                                <div style="display: flex; gap: 4px;">
                                    <button type="button" onclick="window.deleteRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}')" style="background: rgba(255, 77, 79, 0.15); border: 1px solid rgba(255, 77, 79, 0.35); color: #ff4d4f; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">🗑️ 远程下架</button>
                                    <button type="button" onclick="window.unlinkRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}')" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #aaa; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;" title="仅在本地解绑，不删除对端文章">🔗 解绑</button>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;}).join('') : `
                    <div style="padding: 20px; text-align: center; font-size: 0.8rem; color: var(--text-dim); background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.1); border-radius: 8px; line-height: 1.6;">
                        💡 <b>当前未检测到就绪的社交渠道</b><br>
                        请点击右侧<b>「⚙️ 去配置/激活」</b>按钮或前往<b>「🔌 插件中心」</b>配置 Token 密钥。
                    </div>
                `}
            </div>
        </div>

        <!-- 3. 实时传输与进度指示卡片 -->
        <div id="syndicate-progress-panel" style="display: none; padding: 12px; background: rgba(0, 242, 255, 0.06); border: 1px solid rgba(0, 242, 255, 0.25); border-radius: 8px; flex-direction: column; gap: 8px;">
            <div style="font-size: 0.78rem; font-weight: 700; color: var(--accent-secondary); display: flex; align-items: center; justify-content: space-between;">
                <span id="syndicate-progress-title">⚙️ 正在处理分发管线...</span>
                <span id="syndicate-progress-percent" style="font-size: 0.72rem;">0%</span>
            </div>
            <div style="width: 100%; height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden;">
                <div id="syndicate-progress-bar" style="width: 0%; height: 100%; background: var(--accent-secondary, #00f2fe); transition: width 0.3s ease;"></div>
            </div>
            <div id="syndicate-progress-desc" style="font-size: 0.7rem; color: var(--text-dim); line-height: 1.4;">
                准备启动任务...
            </div>
        </div>

        <button type="button" class="mini-btn glow-btn" id="btn-start-article-syndicate" ${readyPlatformsCount === 0 ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''} style="width: 100%; padding: 11px; font-size: 0.88rem; font-weight: 700; border-radius: 8px; background: var(--accent-secondary, #00f2fe); color: #000; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;" onclick="window.dispatchArticleSyndication('${relPath.replace(/'/g, "\\'")}')">
            🚀 开始社媒渠道分发
        </button>
    `;

    // 动态绑定选中计数更新及按钮使能
    window.updateSyndicateSelectionCounter = function() {
        const badgeEl = document.getElementById('syndicate-channel-status-badge');
        const startBtn = document.getElementById('btn-start-article-syndicate');
        const checkedBoxes = document.querySelectorAll('.syndicate-platform-checkbox:checked');
        const selectedCount = checkedBoxes ? checkedBoxes.length : 0;

        if (badgeEl) {
            badgeEl.innerHTML = readyPlatformsCount > 0
                ? `🟢 ${readyPlatformsCount} 个渠道就绪 (当前选中 ${selectedCount} 个)`
                : '⚠️ 暂无已就绪渠道，请先配置';
            badgeEl.style.color = selectedCount > 0 ? '#00ff88' : '#f59e0b';
        }

        if (startBtn) {
            if (selectedCount === 0) {
                startBtn.disabled = true;
                startBtn.style.opacity = '0.5';
                startBtn.style.cursor = 'not-allowed';
            } else {
                startBtn.disabled = false;
                startBtn.style.opacity = '1';
                startBtn.style.cursor = 'pointer';
            }
        }
    };

    document.querySelectorAll('.syndicate-platform-checkbox').forEach(cb => {
        cb.onchange = function() {
            window.updateSyndicateSelectionCounter();
        };
    });

    window.updateSyndicateSelectionCounter();

    setTimeout(() => {
        drawerEl.style.right = '0px';
    }, 10);
};

// 🚀 [右上角返回/关闭分流处理器]
window.handleReviewDrawerCloseClick = function () {
    if (window._syndicateReturnContext) {
        window.returnToSyndicateDrawer();
    } else {
        if (typeof window.closeTranslationReview === 'function') {
            window.closeTranslationReview();
        }
    }
};

window.handlePluginDrawerCloseClick = function () {
    if (window._syndicateReturnContext) {
        window.returnToSyndicateDrawer();
    } else if (window._vaultReturnContext) {
        if (typeof window.returnToVaultDrawer === 'function') {
            window.returnToVaultDrawer();
        } else {
            if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
        }
    } else {
        if (typeof window.closePluginDrawer === 'function') {
            window.closePluginDrawer();
        }
    }
};

window.updateDrawerReturnButtons = function () {
    const isFromSyndicate = !!window._syndicateReturnContext;
    const isFromVault = !!window._vaultReturnContext;
    const hasReturnContext = isFromSyndicate || isFromVault;
    
    // 1. 译文校对工作台右上角关闭按钮动态变身
    const reviewCloseBtn = document.getElementById('btn-close-review-drawer') || document.querySelector('#review-drawer .close-btn');
    if (reviewCloseBtn) {
        if (hasReturnContext) {
            reviewCloseBtn.innerHTML = '‹‹ 返回';
            reviewCloseBtn.style.cssText = 'padding: 4px 10px; font-size: 0.75rem; font-weight: 600; background: rgba(0, 242, 255, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
        } else {
            reviewCloseBtn.innerHTML = '✕';
            reviewCloseBtn.style.cssText = 'background: none; border: none; color: var(--text-dim); font-size: 1.3rem; cursor: pointer; line-height: 1; padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
        }
    }

    // 2. 插件配置抽屉右上角关闭按钮动态变身
    const pluginCloseBtn = document.getElementById('close-p-drawer');
    if (pluginCloseBtn) {
        if (hasReturnContext) {
            pluginCloseBtn.innerHTML = '‹‹ 返回';
            pluginCloseBtn.style.cssText = 'padding: 4px 10px; font-size: 0.75rem; font-weight: 600; background: rgba(0, 242, 255, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
        } else {
            pluginCloseBtn.innerHTML = '×';
            pluginCloseBtn.style.cssText = 'background: transparent; border: none; color: var(--text-dim); font-size: 1.3rem; cursor: pointer; line-height: 1; padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
        }
    }
};

// 🚀 [一键直达插件配置编辑器 (带工作流深度串联返回)]
window.goToPluginConfig = async function (pluginId, category = 'publisher') {
    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
    const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();

    // 记录返回上下文，形成工作流深度闭环
    window._syndicateReturnContext = {
        relPath: window.currentSyndicatingRelPath,
        title: window.currentSyndicatingTitle,
        selectedLang: selectedLang
    };

    // 平滑收起广播抽屉
    window.closeArticleSyndicationDrawer();

    if (typeof window.openPluginConfig === 'function') {
        try {
            await window.openPluginConfig(pluginId, category, 'syndicate');
            window.updateDrawerReturnButtons();
        } catch (e) {
            console.warn(`[Syndicate Drawer] Unable to open config for ${pluginId}:`, e);
            if (typeof window.showToast === 'function') {
                window.showToast(`⚙️ 请前往「🔌 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
            }
        }
    } else {
        if (typeof window.showToast === 'function') {
            window.showToast(`⚙️ 请前往「🔌 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
        }
    }
};

// 🚀 [一键直达译文人工校对工作台 (带工作流深度串联返回)]
window.jumpToReviewDrawer = function (relPath, articleTitle) {
    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
    const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();

    window._syndicateReturnContext = {
        relPath: relPath || window.currentSyndicatingRelPath,
        title: articleTitle || window.currentSyndicatingTitle,
        selectedLang: selectedLang
    };

    // 平滑收起广播抽屉
    window.closeArticleSyndicationDrawer();

    // 唤醒译文校对工作台并切换到目标语种
    if (typeof window.openTranslationReview === 'function') {
        window.openTranslationReview(relPath || window.currentSyndicatingRelPath);
        window.updateDrawerReturnButtons();
        setTimeout(() => {
            if (typeof window.switchReviewLang === 'function') {
                window.switchReviewLang(selectedLang);
            }
            window.updateDrawerReturnButtons();
        }, 250);
    }
};

// 🚀 [工作流深度串联：一键无缝接力返回社媒分发抽屉]
window.returnToSyndicateDrawer = async function () {
    const ctx = window._syndicateReturnContext;
    if (!ctx) return;
    window._syndicateReturnContext = null;

    window.updateDrawerReturnButtons();

    // 🛡️ 瞬态防误触防线：1. 立即无缝拉起社媒分发抽屉（保持遮罩常驻，彻底阻断底层主页面暴露）
    if (typeof window.openArticleSyndicationDrawer === 'function') {
        await window.openArticleSyndicationDrawer(ctx.relPath, ctx.title);
        if (ctx.selectedLang) {
            setTimeout(() => {
                const targetRadio = document.querySelector(`input[name="syndicate_lang"][value="${ctx.selectedLang}"]`);
                if (targetRadio) {
                    targetRadio.checked = true;
                    window.onSyndicateLangChange(targetRadio, ctx.relPath);
                }
            }, 50);
        }
    }

    // 2. 紧接着平滑收起上层的校对或插件抽屉，达成 0ms 视觉缝隙平滑过渡
    if (typeof window.closeTranslationReview === 'function') {
        window.closeTranslationReview();
    }
    if (typeof window.closePluginDrawer === 'function') {
        window.closePluginDrawer();
    }
};

window.closeArticleSyndicationDrawer = function () {
    const drawerEl = document.getElementById('article-syndicate-drawer');
    if (drawerEl) {
        drawerEl.style.right = '-440px';
    }
    const backdropEl = document.getElementById('article-syndicate-drawer-backdrop');
    if (backdropEl) {
        backdropEl.style.opacity = '0';
        backdropEl.style.pointerEvents = 'none';
    }
    if (window.syndicateProgressTimer) {
        clearInterval(window.syndicateProgressTimer);
        window.syndicateProgressTimer = null;
    }
};

window.onSyndicateLangChange = function (radioInput, relPath) {
    const labels = document.querySelectorAll('#syndicate-lang-picker .lang-radio-btn');
    labels.forEach(l => {
        l.style.background = 'rgba(255, 255, 255, 0.02)';
        l.style.borderColor = 'rgba(255, 255, 255, 0.15)';
    });
    if (radioInput && radioInput.parentElement) {
        radioInput.parentElement.style.background = 'rgba(0, 242, 255, 0.15)';
        radioInput.parentElement.style.borderColor = 'var(--accent-secondary)';
    }

    const selectedLang = radioInput ? radioInput.value : 'zh';
    const tipEl = document.getElementById('syndicate-translation-readiness-tip');
    if (!tipEl) return;

    const sourceLangCode = (window.settingsData?.i18n_settings?.source?.lang_code || window.settingsData?.source?.lang_code || 'zh').toLowerCase();

    if (selectedLang.toLowerCase() === sourceLangCode) {
        tipEl.style.cssText = 'font-size: 0.72rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px solid rgba(0, 255, 136, 0.2); padding: 6px 10px; border-radius: 6px; margin-top: 2px;';
        tipEl.innerHTML = '🟢 当前选中的是原稿母语，无需翻译，启动后可直达社交分发平台。';
    } else {
        const docStatus = window.currentArticleDispatchStatus;
        const matrixItem = docStatus?.sync_matrix?.find(m => (m.lang_code || '').toLowerCase() === selectedLang.toLowerCase());

        const statusLower = (matrixItem?.status || '').toLowerCase();
        const cacheInfo = matrixItem?.cache_info || '';
        const progress = matrixItem?.progress || 0;
        const isReady = statusLower === 'published' || statusLower === 'success' || statusLower === 'synced' || statusLower === 'done' || progress === 100 || (cacheInfo.includes('已缓存') && !cacheInfo.includes(' 0/'));
        
        const currentTitle = window.currentSyndicatingTitle || relPath || '';
        const jumpBtnHtml = `<button type="button" onclick="window.jumpToReviewDrawer('${(relPath || '').replace(/'/g, "\\'")}', '${currentTitle.replace(/'/g, "\\'")}')" style="padding: 2px 8px; font-size: 0.68rem; font-weight: 600; background: rgba(187, 134, 252, 0.18); color: #bb86fc; border: 1px solid rgba(187, 134, 252, 0.38); border-radius: 4px; cursor: pointer; white-space: nowrap; flex-shrink: 0; display: inline-flex; align-items: center; gap: 3px;">🔍 译文精校 ↗</button>`;

        if (isReady) {
            tipEl.style.cssText = 'font-size: 0.72rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px solid rgba(0, 255, 136, 0.2); padding: 6px 10px; border-radius: 6px; margin-top: 2px; display: flex; align-items: center; justify-content: space-between; gap: 8px;';
            const detailText = cacheInfo ? ` (${cacheInfo})` : '';
            tipEl.innerHTML = `<span>🟢 目标语种 [${selectedLang.toUpperCase()}] 译文已就绪${detailText}，启动后直接分发。</span>${jumpBtnHtml}`;
        } else {
            tipEl.style.cssText = 'font-size: 0.72rem; color: #fbbf24; background: rgba(251, 191, 36, 0.08); border: 1px solid rgba(251, 191, 36, 0.25); padding: 6px 10px; border-radius: 6px; margin-top: 2px; display: flex; align-items: center; justify-content: space-between; gap: 8px;';
            tipEl.innerHTML = `<span>⚡ 目标语种 [${selectedLang.toUpperCase()}] 译文尚未就绪，启动后将由 AI 自动翻译！</span>${jumpBtnHtml}`;
        }
    }

    // 🚀 [语种切换数据隔离] 清理上一语种的执行进度条与分发终态卡片，避免状态跨语种污染
    const oldResults = document.getElementById('syndicate-results-panel');
    if (oldResults) oldResults.remove();

    const progressPanel = document.getElementById('syndicate-progress-panel');
    if (progressPanel) progressPanel.style.display = 'none';

    if (window.syndicateProgressTimer) {
        clearInterval(window.syndicateProgressTimer);
        window.syndicateProgressTimer = null;
    }

    const btn = document.getElementById('btn-start-article-syndicate');
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '🚀 启动社交广播';
    }

    if (typeof window.updateSyndicatePlatformCards === 'function') {
        window.updateSyndicatePlatformCards(relPath || window.currentSyndicatingRelPath);
    }
};

window.updateSyndicatePlatformCards = async function (relPath) {
    relPath = relPath || window.currentSyndicatingRelPath;
    const container = document.getElementById('syndicate-platform-list-container');
    if (!container || !window.currentActivePlatforms || !relPath) return;

    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
    const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();

    try {
        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        const recordsData = await fetchApi(`/api/syndication/records/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}`);
        if (recordsData && recordsData.records) {
            window.currentSyndicationRecords = recordsData.records;
        }
    } catch (e) {
        console.warn("[Article Syndication] Refresh syndication records failed:", e);
    }

    container.innerHTML = window.currentActivePlatforms.map(p => {
        const record = (window.currentSyndicationRecords || []).find(r => 
            (r.target_id || '').toLowerCase() === p.id.toLowerCase() &&
            (r.lang_code || '').toLowerCase() === selectedLang
        );
        const hasRemoteRecord = !!(record && record.remote_article_id);
        const remoteUrl = record ? record.remote_url : null;
        const noUpdateSupport = ['medium', 'substack', 'zhihu'].includes(p.id.toLowerCase());
        const isOutdated = !!(record && record.is_outdated);

        let actionBadgeHtml = '🚀 首次发布 (Create)';
        let actionBadgeBg = 'rgba(0, 242, 255, 0.12)';
        let actionBadgeColor = '#00f2fe';

        if (hasRemoteRecord) {
            if (isOutdated) {
                actionBadgeHtml = '⚠️ 内容已变更 (Outdated)';
                actionBadgeBg = 'rgba(245, 158, 11, 0.18)';
                actionBadgeColor = '#f59e0b';
            } else if (noUpdateSupport) {
                actionBadgeHtml = '⚠️ 降级新建 (Re-create)';
                actionBadgeBg = 'rgba(251, 191, 36, 0.12)';
                actionBadgeColor = '#fbbf24';
            } else {
                actionBadgeHtml = '🔄 覆写更新 (Update)';
                actionBadgeBg = 'rgba(187, 134, 252, 0.18)';
                actionBadgeColor = '#bb86fc';
            }
        }

        return `
        <div class="glass-panel" style="padding: 10px 12px; border-radius: 8px; border: 1px solid ${hasRemoteRecord ? (isOutdated ? 'rgba(245, 158, 11, 0.45)' : 'rgba(187, 134, 252, 0.35)') : (p.isReady ? 'rgba(0, 255, 136, 0.25)' : 'rgba(255,255,255,0.06)')}; display: flex; flex-direction: column; gap: 8px; opacity: ${p.isReady ? '1' : '0.65'}; background: ${hasRemoteRecord ? (isOutdated ? 'rgba(245, 158, 11, 0.05)' : 'rgba(187, 134, 252, 0.04)') : (p.isReady ? 'rgba(0, 255, 136, 0.03)' : 'rgba(255,255,255,0.01)')};">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <input type="checkbox" value="${p.id}" class="syndicate-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'} style="accent-color: var(--accent-secondary); width: 16px; height: 16px; cursor: ${p.isReady ? 'pointer' : 'not-allowed'};">
                    <div>
                        <div style="font-size: 0.82rem; font-weight: 600; color: ${p.isReady ? '#fff' : 'var(--text-dim)'};">${p.icon} ${p.name}</div>
                        <div style="font-size: 0.68rem; color: var(--text-dim);">${p.desc}</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    ${p.isReady ? `
                        <span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; white-space: nowrap; background: ${actionBadgeBg}; color: ${actionBadgeColor}; border: 1px solid ${actionBadgeColor}55; font-weight: 600;">${actionBadgeHtml}</span>
                        <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="修改此渠道的 Token 密钥或配置" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">⚙️</button>
                    ` : `
                        <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="前往配置并激活此渠道" style="background: rgba(0, 242, 255, 0.15); border: 1px solid rgba(0, 242, 255, 0.35); color: var(--neon-cyan, #00f2fe); border-radius: 4px; padding: 3px 8px; font-size: 0.68rem; font-weight: 600; cursor: pointer; white-space: nowrap;">⚙️ 去配置/激活</button>
                    `}
                </div>
            </div>
            ${hasRemoteRecord ? `
                <div style="padding-top: 6px; border-top: 1px dashed rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: space-between; font-size: 0.68rem; color: var(--text-dim);">
                    <div style="display: flex; align-items: center; gap: 6px; overflow: hidden;">
                        <span>🆔 ID: <code>${record.remote_article_id}</code></span>
                        ${remoteUrl ? `<a href="${remoteUrl}" target="_blank" style="color: #00f2fe; text-decoration: none;">🔗 对端文章 ↗</a>` : ''}
                    </div>
                    <div style="display: flex; gap: 4px;">
                        <button type="button" onclick="window.deleteRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}')" style="background: rgba(255, 77, 79, 0.15); border: 1px solid rgba(255, 77, 79, 0.35); color: #ff4d4f; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">🗑️ 远程下架</button>
                        <button type="button" onclick="window.unlinkRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}')" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #aaa; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;" title="仅在本地解绑，不删除对端文章">🔗 解绑</button>
                    </div>
                </div>
            ` : ''}
        </div>
        `;
    }).join('');
};

window.dispatchArticleSyndication = async function (relPath) {
    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
    const selectedLang = langRadio ? langRadio.value : 'zh';

    const platformCheckboxes = document.querySelectorAll('.syndicate-platform-checkbox:checked');
    const selectedPlatforms = Array.from(platformCheckboxes).map(cb => cb.value);

    if (selectedPlatforms.length === 0) {
        window.showToast('⚠️ 请至少勾选 1 个已就绪的社媒分发渠道', 'warning');
        return;
    }

    const btn = document.getElementById('btn-start-article-syndicate');
    const progressPanel = document.getElementById('syndicate-progress-panel');
    const progressTitle = document.getElementById('syndicate-progress-title');
    const progressPercent = document.getElementById('syndicate-progress-percent');
    const progressBar = document.getElementById('syndicate-progress-bar');
    const progressDesc = document.getElementById('syndicate-progress-desc');

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-gear">⚙️</span> 分发管线运行中...';
    }

    if (progressPanel) {
        progressPanel.style.display = 'flex';
        progressTitle.innerText = `⚙️ 正在启动 [${selectedLang.toUpperCase()}] 分发管线...`;
        progressPercent.innerText = '15%';
        progressBar.style.width = '15%';
        progressDesc.innerText = '正在调起后端智能编译与分发中心...';
    }

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    let currentProgress = 20;

    if (window.syndicateProgressTimer) clearInterval(window.syndicateProgressTimer);
    window.syndicateProgressTimer = setInterval(async () => {
        try {
            const statusData = await fetchFunc(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
            if (statusData && statusData.telemetry && statusData.telemetry.pipeline) {
                const pipe = statusData.telemetry.pipeline;
                if (pipe.status === 'RUNNING') {
                    currentProgress = Math.min(90, currentProgress + 10);
                    if (progressPercent) progressPercent.innerText = `${currentProgress}%`;
                    if (progressBar) progressBar.style.width = `${currentProgress}%`;
                    if (progressDesc) progressDesc.innerText = `⚙️ [底层实时日志] ${pipe.stage || '正在处理 AST 结构与外部接口...'}`;
                }
            }
        } catch (e) {
        }
    }, 1200);

    const oldPanel = document.getElementById('syndicate-results-panel');
    if (oldPanel) oldPanel.remove();

    let successCount = 0;
    let failCount = 0;

    for (let i = 0; i < selectedPlatforms.length; i++) {
        const channelId = selectedPlatforms[i];
        if (progressDesc) progressDesc.innerText = `📡 [${i + 1}/${selectedPlatforms.length}] 正在向 [${channelId.toUpperCase()}] 进行广播推流调度...`;

        try {
            const res = await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_slot: selectedLang,
                    target_channel: channelId,
                    skip_syndication: false,
                    clear_cache: false
                })
            });

            if (res && (res.status === 'ok' || res.success || res.task_id)) {
                successCount++;
            } else {
                failCount++;
                console.error(`[Syndication Error] ${channelId}:`, res);
            }
        } catch (e) {
            failCount++;
            console.error(`[Syndication Network Error] ${channelId}:`, e);
        }
    }

    if (window.syndicateProgressTimer) {
        clearInterval(window.syndicateProgressTimer);
        window.syndicateProgressTimer = null;
    }

    // 🚀 [V107.0] 物理终态凭证回填：拉取后端最新传感数据并动态渲染渠道直达卡片 (带多周期平滑长轮询与物权对正)
    let cardSuccessCount = 0;
    let cardFailCount = 0;
    let lastSyncMatrix = [];

    const renderResultsPanel = async (retryCount = 0) => {
        try {
            const timestamp = Date.now();
            const finalStatus = await fetchFunc(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}&_t=${timestamp}`);
            const syncMatrix = (finalStatus && finalStatus.sync_matrix) ? finalStatus.sync_matrix : [];
            lastSyncMatrix = syncMatrix;

            // 🚀 实时同步拉取物权账本（精准按 selectedLang 语种物理隔离并防 HTTP 缓存）
            try {
                const recordsData = await fetchFunc(`/api/syndication/records/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}&_t=${timestamp}`);
                if (recordsData && recordsData.records) {
                    window.currentSyndicationRecords = recordsData.records;
                }
            } catch (re) {
                console.warn("[Syndicate Drawer] Refresh records failed:", re);
            }

            let hasLiveLink = false;
            let allCompleted = true;
            cardSuccessCount = 0;
            cardFailCount = 0;

            let resultsHtml = `
                <div id="syndicate-results-panel" style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px; border: 1px solid var(--accent-secondary, #00f2fe); background: rgba(0, 242, 255, 0.04); padding: 12px; border-radius: 10px;">
                    <div style="font-size: 0.85rem; font-weight: 700; color: var(--accent-secondary, #00f2fe); display: flex; align-items: center; justify-content: space-between;">
                        <span>📡 广播物理凭证终态分布</span>
                        <span style="font-size: 0.68rem; color: var(--text-dim);">${new Date().toTimeString().split(' ')[0]}</span>
                    </div>
            `;

            selectedPlatforms.forEach(chanId => {
                const chanMeta = platformMetadata[chanId] || { name: chanId.toUpperCase(), icon: '📡' };
                const cleanChanId = chanId.toLowerCase().replace(/[_-\s]/g, '');
                const statusItem = syncMatrix.find(m => (m.channel_id || '').toLowerCase().replace(/[_-\s]/g, '') === cleanChanId) || {};
                
                // 优先从当前选中语种的物权账本中获取真实 remote_url
                const langRecord = (window.currentSyndicationRecords || []).find(r => 
                    (r.target_id || '').toLowerCase().replace(/[_-\s]/g, '') === cleanChanId &&
                    (r.lang_code || '').toLowerCase() === selectedLang.toLowerCase()
                );
                
                const liveLink = (langRecord && langRecord.remote_url) 
                    ? langRecord.remote_url 
                    : (statusItem.artifact_url && statusItem.artifact_url !== '#' ? statusItem.artifact_url : null);
                
                if (liveLink) hasLiveLink = true;
                
                const statusLower = (statusItem.status || '').toLowerCase();
                const isFailed = statusLower === 'failed' || statusLower === 'error' || !!statusItem.reason;
                const isSyncing = !isFailed && (statusLower === 'syncing' || statusLower === 'running');
                const isDraft = !isFailed && statusLower === 'draft';
                const isSkipped = !isFailed && !isSyncing && (statusLower === 'skipped' || statusLower === 'same_content');
                const isSuccess = !isFailed && !isSyncing && !isDraft && (isSkipped || statusLower === 'published' || statusLower === 'success' || statusLower === 'synced' || statusLower === 'done' || (!!liveLink && !isFailed));
                const errorMsg = statusItem.reason || '网络传输中断或未配置凭据';

                // 🚀 智能长轮询收敛：若仍在推流中，或处于刚提交且未达终态的过渡期 (retryCount < 8)，持续轮询
                if (isSyncing || (!isFailed && !isSuccess && !isDraft && !isSkipped && retryCount < 8)) {
                    allCompleted = false;
                } else if (isDraft) {
                    cardSuccessCount++;
                } else if (isSuccess) {
                    cardSuccessCount++;
                } else if (isFailed) {
                    cardFailCount++;
                } else {
                    // 处于待分发态 (已达到终态但未执行)
                }

                // 🎨 五态渲染：推流中 (青蓝) / 已对正跳过 (青) / 草稿 (琥珀) / 成功 (绿) / 失败 (红)
                const cardBg = isSyncing ? 'rgba(0, 242, 255, 0.05)' : (isSkipped ? 'rgba(0, 242, 255, 0.08)' : (isDraft ? 'rgba(255, 193, 7, 0.08)' : (isSuccess ? 'rgba(0, 255, 136, 0.08)' : (isFailed ? 'rgba(255, 77, 77, 0.08)' : 'rgba(255, 255, 255, 0.02)'))));
                const cardBorder = isSyncing ? 'rgba(0, 242, 255, 0.25)' : (isSkipped ? 'rgba(0, 242, 255, 0.35)' : (isDraft ? 'rgba(255, 193, 7, 0.35)' : (isSuccess ? 'rgba(0, 255, 136, 0.35)' : (isFailed ? 'rgba(255, 77, 77, 0.35)' : 'rgba(255, 255, 255, 0.1)'))));
                const statusColor = isSyncing ? '#00f2fe' : (isSkipped ? '#00f2fe' : (isDraft ? '#ffc107' : (isSuccess ? '#00ff88' : (isFailed ? '#ff4d4d' : '#888'))));
                const statusText = isSyncing
                    ? '⚙️ 正在向平台进行广播推流与物权绑定...'
                    : (isSkipped
                        ? '✨ 内容一致自动对正 (已跳过重复网络推流)'
                        : (isDraft
                            ? '🟡 已推送，但平台强制降级为草稿（需手动发布）'
                            : (isSuccess ? '🟢 已成功广播分发' : (isFailed ? `❌ ${errorMsg}` : '⚪ 尚未分发至该渠道'))));

                let actionHtml = '';
                if (isSyncing) {
                    actionHtml = `
                        <span style="font-size: 0.68rem; color: #00f2fe; background: rgba(0, 242, 255, 0.12); border: 1px solid rgba(0, 242, 255, 0.25); padding: 4px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px;">⚙️ 推流中...</span>
                    `;
                } else if (isSkipped && liveLink) {
                    actionHtml = `
                        <a href="${liveLink}" target="_blank" style="padding: 6px 12px; font-size: 0.72rem; font-weight: 700; background: rgba(0, 242, 255, 0.2); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.4); border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; box-shadow: 0 0 10px rgba(0, 242, 255, 0.2);">
                            ✨ 保持对正 ↗
                        </a>
                    `;
                } else if (isDraft && liveLink) {
                    actionHtml = `
                        <a href="${liveLink}" target="_blank" style="padding: 6px 12px; font-size: 0.72rem; font-weight: 700; background: #ffc107; color: #000; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; box-shadow: 0 0 10px rgba(255, 193, 7, 0.4);">
                            📝 前往手动发布 ↗
                        </a>
                    `;
                } else if (liveLink) {
                    actionHtml = `
                        <a href="${liveLink}" target="_blank" style="padding: 6px 12px; font-size: 0.72rem; font-weight: 700; background: var(--accent-secondary, #00f2fe); color: #000; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; box-shadow: 0 0 10px rgba(0, 242, 255, 0.4);">
                            🌐 线上文章 ↗
                        </a>
                    `;
                } else if (isSkipped) {
                    actionHtml = `
                        <span style="font-size: 0.68rem; color: #00f2fe; background: rgba(0, 242, 255, 0.12); border: 1px solid rgba(0, 242, 255, 0.25); padding: 4px 8px; border-radius: 4px;">✨ 自动跳过</span>
                    `;
                } else if (isSuccess) {
                    actionHtml = `
                        <span style="font-size: 0.68rem; color: #00ff88; background: rgba(0, 255, 136, 0.12); border: 1px solid rgba(0, 255, 136, 0.25); padding: 4px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px;">⚙️ 已发送推流</span>
                    `;
                } else if (isFailed) {
                    actionHtml = `
                        <button type="button" onclick="window.retrySinglePlatform('${relPath.replace(/'/g, "\\'")}', '${chanId}')" style="padding: 4px 10px; font-size: 0.72rem; font-weight: 600; background: rgba(0, 242, 255, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">🔄 重试</button>
                    `;
                } else {
                    actionHtml = `
                        <span style="font-size: 0.68rem; color: #888; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 4px 8px; border-radius: 4px; white-space: nowrap;">⚪ 待分发</span>
                    `;
                }

                resultsHtml += `
                    <div style="padding: 10px 12px; border-radius: 8px; background: ${cardBg}; border: 1px solid ${cardBorder}; display: flex; flex-direction: column; gap: 6px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                            <div style="display: flex; align-items: center; gap: 8px; min-width: 0;">
                                <span style="font-size: 1.1rem; flex-shrink: 0;">${chanMeta.icon}</span>
                                <span style="font-size: 0.85rem; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${chanMeta.name}</span>
                            </div>
                            <div style="flex-shrink: 0; display: flex; align-items: center; gap: 6px;">
                                ${actionHtml}
                            </div>
                        </div>
                        ${isFailed ? `
                            <div style="font-size: 0.72rem; color: #ff7875; background: rgba(255, 77, 79, 0.08); border: 1px solid rgba(255, 77, 79, 0.25); border-left: 3px solid #ff4d4f; border-radius: 4px; padding: 6px 10px; line-height: 1.45; word-break: break-word;">
                                ${statusText}
                            </div>
                        ` : (statusText && statusText !== '⚪ 尚未分发至该渠道' && !isSuccess && !isSkipped ? `
                            <div style="font-size: 0.7rem; color: ${statusColor}; padding-left: 28px; line-height: 1.35;">
                                ${statusText}
                            </div>
                        ` : '')}
                    </div>
                `;
            });
            resultsHtml += `</div>`;

            const oldPanel = document.getElementById('syndicate-results-panel');
            if (oldPanel) oldPanel.remove();

            const progressPanel = document.getElementById('syndicate-progress-panel');
            if (progressPanel) {
                progressPanel.insertAdjacentHTML('afterend', resultsHtml);
                // 🚀 物理自动平滑滚动：确保结果卡片自动拉入可视视口区
                const drawerBody = document.getElementById('article-syndicate-drawer');
                if (drawerBody) {
                    drawerBody.scrollTo({ top: drawerBody.scrollHeight, behavior: 'smooth' });
                }
            }

            // 🚀 物理实时刷新 Section 2 渠道选择卡片：实时对正最新 Remote ID 与徽章
            if (typeof window.updateSyndicatePlatformCards === 'function') {
                await window.updateSyndicatePlatformCards(relPath);
            }

            // 🚀 物理长轮询对正：只要仍有渠道在推流中或尚未获取终态，继续轮询 (最高 20 次 / 25 秒)
            if (!allCompleted && retryCount < 20) {
                setTimeout(() => renderResultsPanel(retryCount + 1), 1200);
            } else {
                if (progressPercent) progressPercent.innerText = '100%';
                if (progressBar) progressBar.style.width = '100%';
                if (progressDesc) {
                    progressDesc.innerText = cardFailCount > 0 
                        ? '⚠️ 广播管线已处理完成（含错误告警，详见下方分布卡片）' 
                        : '🎉 广播与自动翻译管线已全部闭环处理完成！';
                }
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = '🚀 重新启动社交广播';
                }
            }
        } catch (e) {
            console.warn("[Syndication Telemetry Error]:", e);
        }
    };

    await renderResultsPanel(0);
};

// 🛡️ [V120.0] 全局主权确认弹窗中枢 (Sovereign Action Confirm Modal Hub)
// 彻底淘汰原生 confirm()/alert() 死穴逻辑，优先调起 Swal.fire，若无则注入 z-index 999999 的毛玻璃 Modal，永不受 DOM 刷写或焦点遮挡影响
window.confirmSovereignAction = async function ({
    title = '⚠️ 物理安全确认',
    text = '确定要执行此物理操作吗？',
    icon = 'warning',
    confirmText = '确定执行',
    confirmColor = '#ff4d4f',
    cancelText = '取消'
} = {}) {
    if (typeof window.Swal !== 'undefined' || typeof Swal !== 'undefined') {
        const swalInst = window.Swal || Swal;
        const res = await swalInst.fire({
            title: title,
            html: `<div style="font-size: 0.9rem; color: rgba(255,255,255,0.85); margin-top: 8px; line-height: 1.6;">${text}</div>`,
            icon: icon,
            showCancelButton: true,
            confirmButtonColor: confirmColor,
            cancelButtonColor: 'rgba(255, 255, 255, 0.15)',
            confirmButtonText: confirmText,
            cancelButtonText: cancelText,
            background: '#12131e',
            color: '#ffffff'
        });
        return res.isConfirmed;
    }

    return new Promise((resolve) => {
        const modalId = 'sovereign-confirm-modal-' + Date.now();
        const backdrop = document.createElement('div');
        backdrop.id = modalId;
        backdrop.style.cssText = `
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.82);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        backdrop.innerHTML = `
            <div class="glass-panel" style="width: 440px; max-width: 90vw; padding: 24px; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.2); background: rgba(18, 19, 30, 0.96); box-shadow: 0 20px 60px rgba(0,0,0,0.9); display: flex; flex-direction: column; gap: 16px;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px;">
                    ${title}
                </div>
                <div style="font-size: 0.88rem; color: rgba(255, 255, 255, 0.85); line-height: 1.6;">
                    ${text}
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px;">
                    <button type="button" id="${modalId}-cancel" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); color: #ccc; padding: 8px 16px; border-radius: 8px; font-size: 0.82rem; cursor: pointer;">${cancelText}</button>
                    <button type="button" id="${modalId}-confirm" style="background: ${confirmColor}; border: none; color: #fff; padding: 8px 18px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 14px ${confirmColor}55;">${confirmText}</button>
                </div>
            </div>
        `;

        document.body.appendChild(backdrop);

        const close = (result) => {
            if (backdrop && backdrop.parentNode) {
                backdrop.parentNode.removeChild(backdrop);
            }
            resolve(result);
        };

        document.getElementById(`${modalId}-cancel`).onclick = () => close(false);
        document.getElementById(`${modalId}-confirm`).onclick = () => close(true);
    });
};

window.deleteRemoteArticle = async function(relPath, targetId) {
    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
    const selectedLang = langRadio ? langRadio.value : 'zh';

    const isConfirmed = await window.confirmSovereignAction({
        title: '🗑️ 物理远程下架确认',
        text: `确定要调用 <b>${targetId.toUpperCase()}</b> API 彻底远程下架该文章吗？<br><span style="color: #ff4d4f; font-size: 0.8rem; display: block; margin-top: 6px;">⚠️ 此操作将在对端社交平台物理销毁该文章，操作不可逆！</span>`,
        icon: 'warning',
        confirmText: '🗑️ 确认彻底下架',
        confirmColor: '#ff4d4f',
        cancelText: '取消'
    });
    if (!isConfirmed) return;

    try {
        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        const res = await fetchApi('/api/syndication/remote-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rel_path: relPath, lang_code: selectedLang, target_id: targetId, action: 'delete' })
        });
        if (res && res.ok) {
            if (typeof window.showToast === 'function') window.showToast(`🗑️ ${res.message || '文章下架成功'}`, 'success');
            await window.updateSyndicatePlatformCards(relPath);
        } else {
            if (typeof window.showToast === 'function') window.showToast(`🛑 下架失败: ${res ? (res.error || res.detail) : '对端接口异常'}`, 'error');
        }
    } catch (e) {
        if (typeof window.showToast === 'function') window.showToast(`🛑 网络错误: ${e}`, 'error');
    }
};

window.unlinkRemoteArticle = async function(relPath, targetId) {
    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
    const selectedLang = langRadio ? langRadio.value : 'zh';

    const isConfirmed = await window.confirmSovereignAction({
        title: '🔗 本地物权解绑确认',
        text: `确定要解除本地与 <b>${targetId.toUpperCase()}</b> 的文章物权绑定吗？<br><span style="color: #00f2fe; font-size: 0.8rem; display: block; margin-top: 6px;">💡 注意：这仅会清空本地物权账本，不会删除对端社交平台上的已发布文章。</span>`,
        icon: 'question',
        confirmText: '🔗 确认解除绑定',
        confirmColor: '#3085d6',
        cancelText: '取消'
    });
    if (!isConfirmed) return;

    try {
        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        const res = await fetchApi('/api/syndication/remote-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rel_path: relPath, lang_code: selectedLang, target_id: targetId, action: 'unlink' })
        });
        if (res && res.ok) {
            if (typeof window.showToast === 'function') window.showToast(`🔗 ${res.message || '已成功解绑'}`, 'info');
            await window.updateSyndicatePlatformCards(relPath);
        } else {
            if (typeof window.showToast === 'function') window.showToast(`🛑 解绑失败: ${res ? (res.error || res.detail) : '接口异常'}`, 'error');
        }
    } catch (e) {
        if (typeof window.showToast === 'function') window.showToast(`🛑 网络错误: ${e}`, 'error');
    }
};

window.retrySinglePlatform = async function(relPath, channelId) {
    const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
    const selectedLang = langRadio ? langRadio.value : 'zh';

    if (typeof window.showToast === 'function') {
        window.showToast(`📡 正在向 [${channelId.toUpperCase()}] 发起单独重试推流...`, 'info');
    }

    try {
        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        await fetchApi(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_slot: selectedLang,
                target_channel: channelId,
                skip_syndication: false,
                clear_cache: false
            })
        });

        if (typeof window.updateSyndicatePlatformCards === 'function') {
            await window.updateSyndicatePlatformCards(relPath);
        }
        const resultsEl = document.getElementById('syndicate-results-panel');
        if (resultsEl) {
            resultsEl.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (e) {
        if (typeof window.showToast === 'function') {
            window.showToast(`🛑 单独重试请求失败: ${e}`, 'error');
        }
    }
};
