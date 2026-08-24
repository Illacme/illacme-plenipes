/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - Drawer Shell & Lifecycle Shard
 * 职责：社交广播抽屉整体 DOM 骨架构建、生命周期管理、互斥遮罩与选择计数器。
 */

(function () {
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
        const syndicationCfg = cfgData.syndication || {};
        const availableLangs = window.getAvailableSyndicateLangs ? window.getAvailableSyndicateLangs(cfgData) : [];

        // 2. 🚀 物理感应全量分发渠道及其多因子凭据就绪状态
        const platformMetadata = window.platformMetadata || {};
        const activePlatforms = [];
        Object.keys(platformMetadata).forEach(key => {
            const itemCfg = syndicationCfg[key] || syndicationCfg[key.replace('_', '')] || {};
            const status = window.evaluateSyndicateChannelStatus ? window.evaluateSyndicateChannelStatus(key, itemCfg) : { isReady: false, isBrandActive: false, credLabel: '待填凭据', credReady: false };
            const meta = platformMetadata[key] || { name: key, icon: '📡', desc: '' };

            activePlatforms.push({
                id: key,
                name: meta.name,
                icon: meta.icon,
                desc: meta.desc,
                isReady: status.isReady,
                isBrandActive: status.isBrandActive,
                credLabel: status.credLabel,
                credReady: status.credReady,
                isChecked: status.isReady && status.isBrandActive
            });
        });
        window.currentActivePlatforms = activePlatforms;

        // 3. 🔍 探查文章各语种的翻译与就绪状态
        let docStatusData = null;
        try {
            docStatusData = await fetchApi(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
        } catch (e) {
            console.warn("[Article Syndication] Unable to fetch doc dispatch status:", e);
        }
        window.currentArticleDispatchStatus = docStatusData;

        // 🚀 [全局抽屉互斥排他] 自动平滑收起其他可能已打开的抽屉
        if (typeof window.closeVaultDrawer === 'function') window.closeVaultDrawer();
        if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
        const reviewOverlay = document.getElementById('review-drawer-overlay');
        if (reviewOverlay) {
            reviewOverlay.style.opacity = '0';
            setTimeout(() => { reviewOverlay.style.display = 'none'; }, 200);
        }

        // 🚀 [半透明毛玻璃背景遮罩]
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
                position: fixed; top: 0; right: -480px; width: 460px; height: 100vh;
                background: rgba(15, 17, 26, 0.96); backdrop-filter: blur(16px);
                border-left: 1px solid var(--glass-border, rgba(255, 255, 255, 0.12));
                box-shadow: -10px 0 35px rgba(0, 0, 0, 0.6); z-index: 9999;
                transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
                padding: 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;
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

            <!-- 2. 勾选社交分发平台 -->
            <div style="display: flex; flex-direction: column; gap: 8px; flex: 1; min-height: 0; overflow-y: auto;">
                <label style="font-size: 0.82rem; font-weight: 600; color: var(--accent-primary, #00f2fe); display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span>2. 勾选目标社媒分发渠道</span>
                    <span id="syndicate-channel-status-badge" style="font-size: 0.68rem; color: ${readyPlatformsCount > 0 ? '#00ff88' : '#f59e0b'}; font-weight: 600; white-space: nowrap; flex-shrink: 0;">
                        ${readyPlatformsCount > 0 ? `🟢 ${readyPlatformsCount} 个渠道就绪 (当前选中 ${checkedPlatformsCount} 个)` : '⚠️ 暂无已就绪渠道，请先配置'}
                    </span>
                </label>

                <div style="display: flex; flex-direction: column; gap: 8px;" id="syndicate-platform-list-container">
                    <!-- 动态平台卡片由 updateSyndicatePlatformCards 填充 -->
                </div>
            </div>

            <!-- 3. 富文本广播卡片实时预览 -->
            <details class="glass-panel" id="syndicate-live-preview-details" style="padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(0, 242, 255, 0.2); background: rgba(0, 242, 255, 0.02);">
                <summary style="font-size: 0.78rem; font-weight: 600; color: var(--accent-secondary, #00f2fe); cursor: pointer; display: flex; align-items: center; justify-content: space-between; user-select: none;">
                    <span>👁️ 实时广播卡片视觉预览</span>
                    <span style="font-size: 0.68rem; color: var(--text-dim); font-weight: normal;">展开查看各平台真实排版 ▾</span>
                </summary>
                <div style="margin-top: 10px; display: flex; flex-direction: column; gap: 8px;" id="syndicate-preview-content-box">
                    <div style="display: flex; gap: 6px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;" id="syndicate-preview-tabs">
                        <button type="button" class="mini-btn preview-tab-btn active" data-ptarget="discord" onclick="window.switchSyndicatePreviewTarget('discord')" style="padding: 2px 8px; font-size: 0.68rem; border-radius: 4px; background: rgba(0, 242, 255, 0.2); color: #fff; border: 1px solid rgba(0, 242, 255, 0.4); cursor: pointer;">💬 Discord Embed</button>
                        <button type="button" class="mini-btn preview-tab-btn" data-ptarget="telegram" onclick="window.switchSyndicatePreviewTarget('telegram')" style="padding: 2px 8px; font-size: 0.68rem; border-radius: 4px; background: rgba(255,255,255,0.04); color: var(--text-dim); border: 1px solid rgba(255,255,255,0.1); cursor: pointer;">✈️ Telegram Card</button>
                        <button type="button" class="mini-btn preview-tab-btn" data-ptarget="devto" onclick="window.switchSyndicatePreviewTarget('devto')" style="padding: 2px 8px; font-size: 0.68rem; border-radius: 4px; background: rgba(255,255,255,0.04); color: var(--text-dim); border: 1px solid rgba(255,255,255,0.1); cursor: pointer;">👩‍💻 Dev.to 文章</button>
                    </div>
                    <div id="syndicate-card-preview-renderer" style="min-height: 100px;"></div>
                </div>
            </details>

            <!-- 4. 实时传输与进度指示卡片 -->
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
        window.updateSyndicateSelectionCounter = function () {
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

        if (typeof window.updateSyndicatePlatformCards === 'function') {
            await window.updateSyndicatePlatformCards(relPath);
        }

        document.querySelectorAll('.syndicate-platform-checkbox').forEach(cb => {
            cb.onchange = function () {
                window.updateSyndicateSelectionCounter();
            };
        });

        window.updateSyndicateSelectionCounter();
        if (typeof window.renderSyndicateCardPreview === 'function') {
            window.renderSyndicateCardPreview('discord');
        }

        setTimeout(() => {
            drawerEl.style.right = '0px';
        }, 10);
    };
})();
