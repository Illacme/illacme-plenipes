/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - Drawer Shell & Lifecycle Shard
 * 职责：社交广播抽屉整体 DOM 骨架构建、生命周期管理、互斥遮罩与选择计数器。
 */

(function () {
    window.closeArticleSyndicationDrawer = function () {
        const drawerEl = document.getElementById('article-syndicate-drawer');
        const backdropEl = document.getElementById('article-syndicate-drawer-backdrop');
        if (drawerEl) {
            drawerEl.classList.remove('is-open');
            drawerEl.style.right = '';
        }
        if (backdropEl) {
            backdropEl.classList.remove('is-open');
            backdropEl.style.opacity = '';
            backdropEl.style.pointerEvents = '';
        }
        // 🪐 [V107.8] 若在知识星谱视图下操作，关闭推流抽屉后自动平滑复原星球控制仪与 3D 聚焦
        if (typeof window.restoreGalaxyDirectorIfActive === 'function') {
            window.restoreGalaxyDirectorIfActive();
        }
    };

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

        // 2. 🚀 动态感应插件中心中所有真实注册的社媒分发渠道 (publisher 类别)
        const publisherPlugins = (window.allPlugins || []).filter(p => p.category === 'publisher');
        const activePlatforms = publisherPlugins.map(p => {
            const itemCfg = syndicationCfg[p.id] || syndicationCfg[p.id.replace('_', '')] || {};
            const status = window.evaluateSyndicateChannelStatus 
                ? window.evaluateSyndicateChannelStatus(p.id, itemCfg) 
                : { isReady: false, isBrandActive: false, credLabel: '待填凭据', credReady: false };

            const slaTier = p.sla_tier || (['zhihu', 'xiaohongshu', 'juejin', 'csdn', 'bilibili', 'toutiao', 'cnblogs', 'oschina', 'segmentfault'].includes((p.id || '').toLowerCase()) ? 'tier2' : 'tier1');
            const slaLabel = p.sla_label || (slaTier === 'tier2' ? 'Cookie辅助' : '官方直连');
            const slaDesc = p.sla_desc || (slaTier === 'tier2' ? '依赖平台 Web 登录凭据，建议定期校验有效性' : '官方开放 API 直连，企业级高可用');

            const brand = (typeof window.getPlatformBrandBadge === 'function') ? window.getPlatformBrandBadge(p.id, p.category || 'publisher') : { icon: '📡' };
            return {
                id: p.id,
                name: p.name || p.id,
                icon: p.icon || brand.icon || '📡',
                desc: p.description || p.desc || '',
                sla_tier: slaTier,
                sla_label: slaLabel,
                sla_desc: slaDesc,
                isReady: status.isReady,
                isBrandActive: status.isBrandActive,
                credLabel: status.credLabel,
                credReady: status.credReady,
                isChecked: status.isReady && status.isBrandActive
            };
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
            backdropEl.className = 'syndicate-drawer-backdrop';
            backdropEl.onclick = () => window.closeArticleSyndicationDrawer();
            document.body.appendChild(backdropEl);
        }
        requestAnimationFrame(() => {
            backdropEl.classList.add('is-open');
        });

        let drawerEl = document.getElementById('article-syndicate-drawer');
        if (!drawerEl) {
            drawerEl = document.createElement('div');
            drawerEl.id = 'article-syndicate-drawer';
            drawerEl.className = 'syndicate-drawer-overlay syndicate-drawer-shell drawer-shell';
            document.body.appendChild(drawerEl);
        }

        const displayTitle = articleTitle || relPath || '未命名文章';
        const readyPlatformsCount = activePlatforms.filter(p => p.isReady).length;
        const checkedPlatformsCount = activePlatforms.filter(p => p.isChecked).length;

        drawerEl.innerHTML = `
            <div id="article-syndicate-drawer-header" class="syndicate-drawer-header">
                <div class="drawer-header-row">
                    <h3 class="syndicate-drawer-title">📢 社交媒体分发</h3>
                    <button type="button" class="drawer-close-btn" onclick="window.closeArticleSyndicationDrawer()">×</button>
                </div>
                <div class="drawer-doc-card">
                    目标原稿：<b class="drawer-doc-id">${displayTitle}</b>
                </div>
            </div>

            <div id="article-syndicate-drawer-body" class="syndicate-drawer-body">
                <div id="syndicate-config-stage-view" class="syndicate-stage-view">
                    <div class="syndicate-step-group">
                        <label class="syndicate-step-label">
                            <span>1. 选择广播语种</span><span class="syndicate-step-meta">共 ${availableLangs.length} 语种</span>
                        </label>
                        <div class="syndicate-lang-picker" id="syndicate-lang-picker">
                            ${availableLangs.map((l, idx) => `
                                <label class="lang-radio-btn ${idx === 0 ? 'active' : ''}">
                                    <input type="radio" name="syndicate_lang" value="${l.code}" ${idx === 0 ? 'checked' : ''} class="syndicate-radio-hidden" onchange="window.onSyndicateLangChange(this, '${relPath}')">
                                    ${l.icon} ${l.name} ${l.isSource ? '<span class="lang-tag-source">(母语)</span>' : '<span class="lang-tag-target">(译文)</span>'}
                                </label>
                            `).join('')}
                        </div>
                        <div id="syndicate-translation-readiness-tip" class="syndicate-tip-box syndicate-tip-box--source">🟢 当前选中的是原稿母语，无需翻译，启动后直达平台。</div>
                    </div>

                    <div id="syndicate-cover-studio-container" class="glass-panel syndicate-cover-studio"></div>

                    <div class="syndicate-preview-entry">
                        <div class="syndicate-preview-info">
                            <span style="font-size:1.1rem;flex-shrink:0;">👁️</span>
                            <div style="min-width:0;">
                                <div class="syndicate-preview-title">全渠道高保真排版审查</div>
                                <div class="syndicate-preview-desc">微信真机 · 知乎 · 掘金 · CSDN · 小红书 · 海外 18 矩阵</div>
                            </div>
                        </div>
                        <button type="button" class="mini-btn glow-btn syndicate-preview-btn" onclick="window.openSyndicateLivePreviewModal()">🖥️ 展开 ↗</button>
                    </div>

                    <div class="syndicate-step-group">
                        <label class="syndicate-step-label">
                            <span>2. 勾选目标社媒渠道</span>
                            <span id="syndicate-channel-status-badge" class="${readyPlatformsCount > 0 ? 'hosting-status-badge--ready' : 'hosting-status-badge--empty'}">
                                ${readyPlatformsCount > 0 ? `🟢 ${readyPlatformsCount} 就绪 (已选 ${checkedPlatformsCount})` : '⚠️ 暂无就绪渠道'}
                            </span>
                        </label>
                        <div class="syndicate-stage-view" id="syndicate-platform-list-container"></div>
                    </div>
                </div>

                <div id="syndicate-telemetry-stage-view" class="syndicate-stage-view" style="display:none;">
                    <div id="syndicate-telemetry-summary-capsule" class="syndicate-telemetry-capsule"><span>正在初始化...</span></div>
                    <div id="syndicate-progress-panel" class="syndicate-progress-panel" style="display:none;">
                        <div class="syndicate-progress-header">
                            <span id="syndicate-progress-title">⚙️ 正在处理分发管线...</span><span id="syndicate-progress-percent">0%</span>
                        </div>
                        <div class="syndicate-progress-track">
                            <div id="syndicate-progress-bar" class="syndicate-progress-bar"></div>
                        </div>
                        <div id="syndicate-progress-desc" class="syndicate-progress-desc">准备启动任务...</div>
                    </div>
                    <div id="syndicate-results-panel-slot" class="syndicate-stage-view"></div>
                </div>
            </div>

            <div id="article-syndicate-drawer-footer" class="syndicate-drawer-footer">
                <button type="button" class="mini-btn glow-btn syndicate-start-btn" id="btn-start-article-syndicate" ${readyPlatformsCount === 0 ? 'disabled' : ''} onclick="window.dispatchArticleSyndication('${relPath.replace(/'/g, "\\'")}')">
                    🚀 开始社媒渠道分发
                </button>
            </div>
        `;

        window.updateSyndicateSelectionCounter = function () {
            const badgeEl = document.getElementById('syndicate-channel-status-badge');
            const startBtn = document.getElementById('btn-start-article-syndicate');
            const checkedBoxes = document.querySelectorAll('.syndicate-platform-checkbox:checked');
            const selectedCount = checkedBoxes ? checkedBoxes.length : 0;

            if (badgeEl) {
                badgeEl.innerHTML = readyPlatformsCount > 0
                    ? `🟢 ${readyPlatformsCount} 就绪 (已选 ${selectedCount})`
                    : '⚠️ 暂无就绪渠道';
                badgeEl.className = selectedCount > 0 ? 'hosting-status-badge--ready' : 'hosting-status-badge--empty';
            }

            if (startBtn) {
                startBtn.disabled = selectedCount === 0;
                if (selectedCount > 0) {
                    startBtn.innerText = `🚀 开始社媒渠道分发 (已选 ${selectedCount} 个)`;
                } else {
                    startBtn.innerText = '🚀 开始社媒渠道分发';
                }
            }

            if (typeof window.adaptCoverForSelection === 'function') {
                const checkedIds = Array.from(checkedBoxes).map(b => b.value);
                window.adaptCoverForSelection(checkedIds);
            }
        };

        if (typeof window.updateSyndicatePlatformCards === 'function') {
            await window.updateSyndicatePlatformCards(relPath);
        }

        document.querySelectorAll('.syndicate-platform-checkbox').forEach(cb => {
            cb.onchange = function () { window.updateSyndicateSelectionCounter(); };
        });

        window.updateSyndicateSelectionCounter();
        if (typeof window.initSyndicateCoverStudio === 'function') {
            window.initSyndicateCoverStudio(relPath, articleTitle);
        }

        setTimeout(() => {
            drawerEl.classList.add('is-open');
            drawerEl.style.right = '';
        }, 10);
    };

    window.switchSyndicateDrawerStage = function (stage, ctx = {}) {
        const configView = document.getElementById('syndicate-config-stage-view');
        const telemetryView = document.getElementById('syndicate-telemetry-stage-view');
        const footerEl = document.getElementById('article-syndicate-drawer-footer');
        const summaryCapsule = document.getElementById('syndicate-telemetry-summary-capsule');
        if (!configView || !telemetryView || !footerEl) return;
        const relPath = window.currentSyndicatingRelPath || '';

        if (stage === 'config') {
            configView.style.display = 'flex';
            telemetryView.style.display = 'none';
            footerEl.innerHTML = `<button type="button" class="mini-btn glow-btn syndicate-start-btn" id="btn-start-article-syndicate" onclick="window.dispatchArticleSyndication('${relPath.replace(/'/g, "\\'")}')">🚀 开始社媒渠道分发</button>`;
            if (typeof window.updateSyndicateSelectionCounter === 'function') window.updateSyndicateSelectionCounter();
        } else if (stage === 'running') {
            configView.style.display = 'none';
            telemetryView.style.display = 'flex';
            if (summaryCapsule) {
                summaryCapsule.innerHTML = `<div style="display:flex;align-items:center;gap:6px;"><span>🌐 语种: <b class="drawer-doc-id">${(ctx.lang || 'ZH').toUpperCase()}</b></span><span>·</span><span>目标: <b style="color:var(--neon-cyan);">${ctx.platformCount || 1} 个渠道</b></span></div><span class="badge" style="background:var(--neon-cyan-12);color:var(--neon-cyan);">广播调度中</span>`;
            }
            footerEl.innerHTML = `<button type="button" class="mini-btn syndicate-running-btn" disabled style="width:100%;padding:10px;font-size:0.86rem;font-weight:700;border-radius:8px;display:flex;align-items:center;justify-content:center;gap:8px;"><span class="spinner-gear">⚙️</span> 分发管线推流中...</button>`;
        } else if (stage === 'telemetry') {
            configView.style.display = 'none';
            telemetryView.style.display = 'flex';
            const hasFailed = (ctx.failedCount || 0) > 0;
            const escapedChannels = (ctx.failedChannelsJson || '[]').replace(/"/g, '&quot;');
            footerEl.innerHTML = `
                <div style="display:flex;gap:8px;width:100%;">
                    <button type="button" class="mini-btn syndicate-back-btn" onclick="window.switchSyndicateDrawerStage('config')" style="flex:1;padding:9px;font-size:0.76rem;font-weight:600;border-radius:8px;display:flex;align-items:center;justify-content:center;gap:4px;">↩️ 修改配置</button>
                    ${hasFailed ? `<button type="button" class="mini-btn glow-btn syndicate-retry-btn" onclick="window.retryAllFailedPlatforms('${relPath.replace(/'/g, "\\'")}', ${escapedChannels})" style="flex:1.5;padding:9px;font-size:0.76rem;font-weight:700;border-radius:8px;display:flex;align-items:center;justify-content:center;gap:6px;">⚡ 一键重试失败 (${ctx.failedCount})</button>` : `<button type="button" class="mini-btn glow-btn syndicate-complete-btn" onclick="window.closeArticleSyndicationDrawer()" style="flex:1.5;padding:9px;font-size:0.76rem;font-weight:700;border-radius:8px;display:flex;align-items:center;justify-content:center;gap:6px;">✅ 完成并关闭</button>`}
                </div>
            `;
        }
    };
})();
