/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - Drawer Shell & Lifecycle Shard
 * 职责：社交广播抽屉整体 DOM 骨架构建、生命周期管理、互斥遮罩与选择计数器。
 */

(function () {
    window.closeArticleSyndicationDrawer = function () {
        const drawerEl = document.getElementById('article-syndicate-drawer');
        const backdropEl = document.getElementById('article-syndicate-drawer-backdrop');
        if (drawerEl) drawerEl.style.right = '-480px';
        if (backdropEl) {
            backdropEl.style.opacity = '0';
            backdropEl.style.pointerEvents = 'none';
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
                padding: 20px; box-sizing: border-box; display: flex; flex-direction: column;
                color: var(--text-bright, #fff); font-family: system-ui, -apple-system, sans-serif;
            `;
            document.body.appendChild(drawerEl);
        }

        const displayTitle = articleTitle || relPath || '未命名文章';
        const readyPlatformsCount = activePlatforms.filter(p => p.isReady).length;
        const checkedPlatformsCount = activePlatforms.filter(p => p.isChecked).length;

        drawerEl.innerHTML = `
            <div id="article-syndicate-drawer-header" style="flex-shrink:0;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.08);display:flex;flex-direction:column;gap:8px;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <h3 style="margin:0;font-size:1.05rem;color:var(--accent-secondary,#00f2fe);display:flex;align-items:center;gap:8px;">📢 社交媒体分发</h3>
                    <button type="button" onclick="window.closeArticleSyndicationDrawer()" style="background:transparent;border:none;color:var(--text-dim);font-size:1.4rem;cursor:pointer;line-height:1;">×</button>
                </div>
                <div style="font-size:0.76rem;color:var(--text-dim);background:rgba(255,255,255,0.03);padding:6px 10px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    目标原稿：<b style="color:#fff;">${displayTitle}</b>
                </div>
            </div>

            <div id="article-syndicate-drawer-body" style="flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:10px 2px 10px 0;display:flex;flex-direction:column;gap:12px;">
                <div id="syndicate-config-stage-view" style="display:flex;flex-direction:column;gap:12px;width:100%;">
                    <div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0;">
                        <label style="font-size:0.8rem;font-weight:600;color:var(--accent-primary,#00f2fe);display:flex;align-items:center;justify-content:space-between;">
                            <span>1. 选择广播语种</span><span style="font-size:0.68rem;color:var(--text-dim);">共 ${availableLangs.length} 语种</span>
                        </label>
                        <div style="display:flex;gap:6px;flex-wrap:wrap;" id="syndicate-lang-picker">
                            ${availableLangs.map((l, idx) => `
                                <label class="lang-radio-btn ${idx === 0 ? 'active' : ''}" style="padding:4px 9px;border-radius:20px;font-size:0.74rem;cursor:pointer;display:flex;align-items:center;gap:5px;">
                                    <input type="radio" name="syndicate_lang" value="${l.code}" ${idx === 0 ? 'checked' : ''} style="display:none;" onchange="window.onSyndicateLangChange(this, '${relPath}')">
                                    ${l.icon} ${l.name} ${l.isSource ? '<span class="lang-tag-source" style="font-size:0.6rem;padding:1px 3px;border-radius:3px;">(母语)</span>' : '<span class="lang-tag-target" style="font-size:0.6rem;padding:1px 3px;border-radius:3px;">(译文)</span>'}
                                </label>
                            `).join('')}
                        </div>
                        <div id="syndicate-translation-readiness-tip" style="font-size:0.7rem;padding:4px 8px;border-radius:6px;">🟢 当前选中的是原稿母语，无需翻译，启动后直达平台。</div>
                    </div>

                    <div id="syndicate-cover-studio-container" class="glass-panel" style="flex-shrink:0;padding:10px 12px;border-radius:8px;border:1px solid rgba(0,242,255,0.15);background:rgba(255,255,255,0.02);display:flex;flex-direction:column;gap:8px;"></div>

                    <div class="syndicate-preview-entry-card" style="flex-shrink:0;display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-radius:8px;background:rgba(0,242,254,0.04);border:1px solid rgba(0,242,254,0.2);gap:10px;">
                        <div style="display:flex;align-items:center;gap:8px;min-width:0;">
                            <span style="font-size:1.1rem;flex-shrink:0;">👁️</span>
                            <div style="min-width:0;">
                                <div style="font-size:0.78rem;font-weight:700;color:#fff;">全渠道高保真排版审查</div>
                                <div style="font-size:0.68rem;color:var(--text-dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">微信真机 · 知乎 · 掘金 · CSDN · 小红书 · 海外 18 矩阵</div>
                            </div>
                        </div>
                        <button type="button" class="mini-btn glow-btn" onclick="window.openSyndicateLivePreviewModal()" style="padding:4px 10px;font-size:0.72rem;font-weight:700;background:rgba(0,242,254,0.15);color:#00f2fe;border:1px solid rgba(0,242,254,0.35);border-radius:6px;cursor:pointer;flex-shrink:0;">🖥️ 展开 ↗</button>
                    </div>

                    <div style="display:flex;flex-direction:column;gap:8px;flex-shrink:0;">
                        <label style="font-size:0.8rem;font-weight:600;color:var(--accent-primary,#00f2fe);display:flex;align-items:center;justify-content:space-between;gap:8px;">
                            <span>2. 勾选目标社媒渠道</span>
                            <span id="syndicate-channel-status-badge" style="font-size:0.68rem;color:${readyPlatformsCount > 0 ? '#00ff88' : '#f59e0b'};font-weight:600;white-space:nowrap;">
                                ${readyPlatformsCount > 0 ? `🟢 ${readyPlatformsCount} 就绪 (已选 ${checkedPlatformsCount})` : '⚠️ 暂无就绪渠道'}
                            </span>
                        </label>
                        <div style="display:flex;flex-direction:column;gap:8px;" id="syndicate-platform-list-container"></div>
                    </div>
                </div>

                <div id="syndicate-telemetry-stage-view" style="display:none;flex-direction:column;gap:12px;width:100%;">
                    <div id="syndicate-telemetry-summary-capsule" style="flex-shrink:0;padding:8px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:8px;display:flex;justify-content:space-between;align-items:center;font-size:0.72rem;color:var(--text-dim);"><span>正在初始化...</span></div>
                    <div id="syndicate-progress-panel" style="flex-shrink:0;display:none;padding:10px 12px;background:rgba(0,242,255,0.06);border:1px solid rgba(0,242,255,0.25);border-radius:8px;flex-direction:column;gap:6px;">
                        <div style="font-size:0.78rem;font-weight:700;color:var(--accent-secondary);display:flex;align-items:center;justify-content:space-between;">
                            <span id="syndicate-progress-title">⚙️ 正在处理分发管线...</span><span id="syndicate-progress-percent" style="font-size:0.72rem;">0%</span>
                        </div>
                        <div style="width:100%;height:5px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden;">
                            <div id="syndicate-progress-bar" style="width:0%;height:100%;background:var(--accent-secondary,#00f2fe);transition:width 0.3s ease;"></div>
                        </div>
                        <div id="syndicate-progress-desc" style="font-size:0.68rem;color:var(--text-dim);line-height:1.4;">准备启动任务...</div>
                    </div>
                    <div id="syndicate-results-panel-slot" style="display:flex;flex-direction:column;gap:10px;width:100%;"></div>
                </div>
            </div>

            <div id="article-syndicate-drawer-footer" style="flex-shrink:0;padding-top:10px;border-top:1px solid rgba(255,255,255,0.08);">
                <button type="button" class="mini-btn glow-btn" id="btn-start-article-syndicate" ${readyPlatformsCount === 0 ? 'disabled style="opacity:0.5;cursor:not-allowed;"' : ''} style="width:100%;padding:10px;font-size:0.86rem;font-weight:700;border-radius:8px;background:var(--accent-secondary,#00f2fe);color:#000;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;" onclick="window.dispatchArticleSyndication('${relPath.replace(/'/g, "\\'")}')">
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
                badgeEl.style.color = selectedCount > 0 ? '#00ff88' : '#f59e0b';
            }

            if (startBtn) {
                startBtn.disabled = selectedCount === 0;
                startBtn.style.opacity = selectedCount === 0 ? '0.5' : '1';
                startBtn.style.cursor = selectedCount === 0 ? 'not-allowed' : 'pointer';
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

        setTimeout(() => { drawerEl.style.right = '0px'; }, 10);
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
            footerEl.innerHTML = `<button type="button" class="mini-btn glow-btn" id="btn-start-article-syndicate" style="width:100%;padding:10px;font-size:0.86rem;font-weight:700;border-radius:8px;background:var(--accent-secondary,#00f2fe);color:#000;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;" onclick="window.dispatchArticleSyndication('${relPath.replace(/'/g, "\\'")}')">🚀 开始社媒渠道分发</button>`;
            if (typeof window.updateSyndicateSelectionCounter === 'function') window.updateSyndicateSelectionCounter();
        } else if (stage === 'running') {
            configView.style.display = 'none';
            telemetryView.style.display = 'flex';
            if (summaryCapsule) {
                summaryCapsule.innerHTML = `<div style="display:flex;align-items:center;gap:6px;"><span>🌐 语种: <b style="color:#fff;">${(ctx.lang || 'ZH').toUpperCase()}</b></span><span>·</span><span>目标: <b style="color:#00f2fe;">${ctx.platformCount || 1} 个渠道</b></span></div><span class="badge" style="background:rgba(0,242,254,0.12);color:#00f2fe;">广播调度中</span>`;
            }
            footerEl.innerHTML = `<button type="button" class="mini-btn" disabled style="width:100%;padding:10px;font-size:0.86rem;font-weight:700;border-radius:8px;background:rgba(255,255,255,0.08);color:#888;border:1px solid rgba(255,255,255,0.1);cursor:not-allowed;display:flex;align-items:center;justify-content:center;gap:8px;"><span class="spinner-gear">⚙️</span> 分发管线推流中...</button>`;
        } else if (stage === 'telemetry') {
            configView.style.display = 'none';
            telemetryView.style.display = 'flex';
            const hasFailed = (ctx.failedCount || 0) > 0;
            const escapedChannels = (ctx.failedChannelsJson || '[]').replace(/"/g, '&quot;');
            footerEl.innerHTML = `
                <div style="display:flex;gap:8px;width:100%;">
                    <button type="button" class="mini-btn" onclick="window.switchSyndicateDrawerStage('config')" style="flex:1;padding:9px;font-size:0.76rem;font-weight:600;border-radius:8px;background:rgba(255,255,255,0.08);color:#fff;border:1px solid var(--glass-border);cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px;">↩️ 修改配置</button>
                    ${hasFailed ? `<button type="button" class="mini-btn glow-btn" onclick="window.retryAllFailedPlatforms('${relPath.replace(/'/g, "\\'")}', ${escapedChannels})" style="flex:1.5;padding:9px;font-size:0.76rem;font-weight:700;border-radius:8px;background:#ff4d4f;color:#fff;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;">⚡ 一键重试失败 (${ctx.failedCount})</button>` : `<button type="button" class="mini-btn glow-btn" onclick="window.closeArticleSyndicationDrawer()" style="flex:1.5;padding:9px;font-size:0.76rem;font-weight:700;border-radius:8px;background:#00ff88;color:#000;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;">✅ 完成并关闭</button>`}
                </div>
            `;
        }
    };
})();
