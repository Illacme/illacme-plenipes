/**
 * 🖼️ [V2.0] Illacme Plenipes Article Syndication - Cover Studio Shard
 * 职责：社媒分发抽屉封面凭据管理、多语种标题联动与渠道画幅自适应 (16:9 / 2.35:1 / 1:1)。
 * 🛡️ [SOP-01] 物理行数保持在 300 行以内。
 */
(function () {
    let _currentRelPath = '', _currentTitle = '', _currentOffset = 0, _currentMode = 'global', _currentCoverUrl = '', _currentLangCode = 'auto', _currentAspectRatio = '16:9', _userManualRatio = false;
    const STRAT_MAP = { 'auto': '🤖 智能回退矩阵 (Auto)', 'og_card': '🃏 技术卡片 (OG Card)', 'brand_presets': '🎭 品牌母本图库轮巡', 'minimal_badge': '🔤 极简首字徽章', 'first_image': '🖼️ 正文首图优先', 'ai_generation': '🎨 AI 意境生图', 'ai_generator': '🎨 AI 意境生图' };

    window.initSyndicateCoverStudio = function (relPath, articleTitle) {
        _currentRelPath = relPath; _currentTitle = articleTitle || relPath; _currentOffset = 0; _currentMode = 'global'; _currentCoverUrl = ''; _currentLangCode = 'auto'; _currentAspectRatio = '16:9'; _userManualRatio = false;
        window.currentSyndicateCover = { mode: _currentMode, url: '', offset: _currentOffset, aspect_ratio: _currentAspectRatio };

        const container = document.getElementById('syndicate-cover-studio-container');
        if (!container) return;
        const globalPolicy = (window.settingsData && window.settingsData.image_policy) || {};
        const defaultStrategy = globalPolicy.default_strategy || 'auto';

        container.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <label style="font-size:0.82rem;font-weight:600;color:var(--accent-primary,#00f2fe);display:flex;align-items:center;gap:6px;margin:0;">
                    <span>🖼️ 封面视觉凭据</span><span style="font-size:0.68rem;color:#a5b4fc;background:rgba(99,102,241,0.18);padding:1px 6px;border-radius:4px;">社媒必填</span>
                </label>
                <div style="display:flex;align-items:center;gap:6px;"><span id="syndicate-cover-badge" style="font-size:0.68rem;color:var(--text-dim);">策略: ${STRAT_MAP[defaultStrategy] || defaultStrategy}</span><span id="syndicate-finetune-badge-slot"></span></div>
            </div>
            <div style="display:flex;gap:10px;align-items:center;">
                <div style="display:flex;flex-direction:column;gap:4px;align-items:center;">
                    <div id="syndicate-cover-thumb-wrapper" style="position:relative;width:140px;height:78px;border-radius:6px;overflow:hidden;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.1);flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:all 0.2s ease;">
                        <div id="syndicate-cover-loading" style="font-size:0.7rem;color:var(--accent-secondary,#00f2fe);display:flex;flex-direction:column;align-items:center;gap:4px;">
                            <span class="spinner-gear" style="display:inline-block;animation:spin 1s infinite linear;">⚙️</span><span>渲染凭据中...</span>
                        </div>
                        <img id="syndicate-cover-thumb-img" src="" alt="封面缩略图" style="width:100%;height:100%;object-fit:cover;display:none;cursor:pointer;" onclick="window.previewSyndicateFullCover()" title="点击查看大图" />
                        <div id="syndicate-cover-safezone" style="position:absolute;inset:0;pointer-events:none;display:none;"></div>
                    </div>
                    <div style="display:flex;gap:3px;align-items:center;justify-content:center;width:140px;">
                        <button type="button" class="sz-btn active" data-mode="none" onclick="window.setCoverSafeZone('none',this,true)" style="padding:1px 4px;font-size:0.6rem;background:rgba(255,255,255,0.2);border:1px solid rgba(255,255,255,0.2);color:#fff;border-radius:3px;cursor:pointer;">全画幅</button>
                        <button type="button" class="sz-btn" data-mode="wechat" onclick="window.setCoverSafeZone('wechat',this,true)" style="padding:1px 4px;font-size:0.6rem;background:rgba(0,242,254,0.06);border:1px solid rgba(0,242,254,0.2);color:var(--accent-secondary,#00f2fe);border-radius:3px;cursor:pointer;" title="对齐微信公众号首条列表 2.35:1 画幅">微信2.35</button>
                        <button type="button" class="sz-btn" data-mode="square" onclick="window.setCoverSafeZone('square',this,true)" style="padding:1px 4px;font-size:0.6rem;background:rgba(168,85,247,0.06);border:1px solid rgba(168,85,247,0.2);color:#c084fc;border-radius:3px;cursor:pointer;" title="对齐小红书或次条 1:1 方图画幅">1:1方图</button>
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:6px;flex:1;min-width:0;">
                    <select id="syndicate-cover-mode-picker" onchange="window.onSyndicateCoverModeChange(this.value)" style="width:100%;background:rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.15);color:#fff;font-size:0.74rem;padding:4px 6px;border-radius:4px;outline:none;cursor:pointer;">
                        <option value="global">🌐 跟随全局默认 (${STRAT_MAP[defaultStrategy] || '智能矩阵'})</option>
                        <option value="doc_frontmatter" id="syndicate-cover-opt-doc" style="display:none;">📌 文章设定封面 (Frontmatter)</option>
                        <option value="asset_picker">🗃️ 从媒体资产库挑选...</option>
                        <option value="og_card">🃏 动态技术卡片 (OG Card)</option>
                        <option value="brand_presets">🎭 品牌母本轮巡</option>
                        <option value="minimal_badge">🔤 极简首字文字徽章</option>
                        <option value="first_image">🖼️ 优先提取正文首图</option>
                        <option value="ai_generation">🤖 AI 智能生图</option>
                    </select>
                    <div style="display:flex;gap:5px;">
                        <button type="button" class="mini-btn" onclick="window.shuffleSyndicateCover()" style="flex:1;padding:4px 5px;font-size:0.68rem;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:4px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:3px;" title="根据相移轮巡色彩或概念">🔄 换一张</button>
                        <button type="button" class="mini-btn" onclick="window.jumpToStudioFromSyndicate()" style="padding:4px 8px;font-size:0.68rem;background:rgba(0,242,254,0.12);border:1px solid rgba(0,242,254,0.3);color:var(--accent-secondary,#00f2fe);border-radius:4px;cursor:pointer;display:flex;align-items:center;gap:2px;" title="前往智能生图工作台精细调试模型、画幅与Prompt">🪄 生图工作台</button>
                        <button type="button" class="mini-btn" onclick="window.openSyndicateAssetPickerModal()" style="padding:4px 8px;font-size:0.68rem;background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);color:#a5b4fc;border-radius:4px;cursor:pointer;display:flex;align-items:center;gap:2px;" title="从设计中心视觉资产库中选取">🗄️ 资产库</button>
                    </div>
                </div>
            </div>`;
        window.loadSyndicateCoverPreview();
    };

    window.setCoverSafeZone = function (mode, btn, isManual = false) {
        if (isManual) _userManualRatio = true;
        const szEl = document.getElementById('syndicate-cover-safezone');
        const wrapper = document.getElementById('syndicate-cover-thumb-wrapper');
        document.querySelectorAll('.sz-btn').forEach(b => { b.classList.remove('active'); b.style.background = 'rgba(255,255,255,0.06)'; });

        const activeBtn = btn || document.querySelector(`.sz-btn[data-mode="${mode}"]`);
        if (activeBtn) { activeBtn.classList.add('active'); activeBtn.style.background = 'rgba(255,255,255,0.2)'; }

        if (mode === 'wechat') {
            _currentAspectRatio = '2.35:1';
            if (wrapper) { wrapper.style.width = '140px'; wrapper.style.height = '60px'; }
            if (szEl) { szEl.style.display = 'block'; szEl.innerHTML = `<span style="position:absolute;bottom:2px;right:4px;font-size:0.52rem;color:#00f2fe;background:rgba(0,0,0,0.7);padding:0 3px;border-radius:2px;">2.35:1</span>`; }
        } else if (mode === 'square') {
            _currentAspectRatio = '1:1';
            if (wrapper) { wrapper.style.width = '80px'; wrapper.style.height = '80px'; }
            if (szEl) { szEl.style.display = 'block'; szEl.innerHTML = `<span style="position:absolute;bottom:2px;right:4px;font-size:0.52rem;color:#c084fc;background:rgba(0,0,0,0.7);padding:0 3px;border-radius:2px;">1:1</span>`; }
        } else {
            _currentAspectRatio = '16:9';
            if (wrapper) { wrapper.style.width = '140px'; wrapper.style.height = '78px'; }
            if (szEl) { szEl.style.display = 'none'; szEl.innerHTML = ''; }
        }

        if (window.currentSyndicateCover) window.currentSyndicateCover.aspect_ratio = _currentAspectRatio;
        if (isManual || _currentCoverUrl) window.loadSyndicateCoverPreview();
    };

    window.adaptCoverForSelection = function (checkedPlatformIds) {
        if (_userManualRatio || !checkedPlatformIds || checkedPlatformIds.length === 0) return;
        const onlyWechat = checkedPlatformIds.length === 1 && checkedPlatformIds[0] === 'wechat';
        const onlyXhs = checkedPlatformIds.length === 1 && (checkedPlatformIds[0] === 'xiaohongshu' || checkedPlatformIds[0] === 'rednote');

        if (onlyWechat && _currentAspectRatio !== '2.35:1') {
            window.setCoverSafeZone('wechat', null, false);
        } else if (onlyXhs && _currentAspectRatio !== '1:1') {
            window.setCoverSafeZone('square', null, false);
        } else if (!onlyWechat && !onlyXhs && _currentAspectRatio !== '16:9') {
            window.setCoverSafeZone('none', null, false);
        }
    };

    window.onSyndicateCoverLangChange = function (langCode) {
        _currentLangCode = langCode || 'auto';
        if (_currentMode !== 'custom') window.loadSyndicateCoverPreview();
    };

    window.loadSyndicateCoverPreview = async function () {
        const loadingEl = document.getElementById('syndicate-cover-loading');
        const imgEl = document.getElementById('syndicate-cover-thumb-img');
        if (loadingEl) loadingEl.style.display = 'flex';
        if (imgEl) imgEl.style.display = 'none';

        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        const activeBrand = (window.settingsData && window.settingsData.current_brand) || 'default';
        const payload = {
            strategy: _currentMode === 'global' ? 'auto' : _currentMode,
            title: _currentTitle,
            doc_id: _currentRelPath,
            brand_id: activeBrand,
            aspect_ratio: _currentAspectRatio,
            lang_code: _currentLangCode,
            offset: _currentOffset
        };

        try {
            const res = await fetchApi('/api/design/cover/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const coverUrl = (res && res.success && (res.url || res.cover_url)) ? (res.url || res.cover_url) : null;
            if (coverUrl) {
                _currentCoverUrl = coverUrl;
                if (window.currentSyndicateCover) {
                    window.currentSyndicateCover.url = coverUrl;
                    window.currentSyndicateCover.mode = _currentMode;
                    window.currentSyndicateCover.strategy = res.strategy_used || res.strategy;
                    window.currentSyndicateCover.offset = _currentOffset;
                    window.currentSyndicateCover.aspect_ratio = _currentAspectRatio;
                }
                if (imgEl) {
                    imgEl.src = `${coverUrl}?t=${Date.now()}`;
                    imgEl.title = `封面预览: ${res.title || _currentTitle} (${_currentAspectRatio})`;
                    imgEl.onload = () => { if (loadingEl) loadingEl.style.display = 'none'; imgEl.style.display = 'block'; };
                }
                const badgeEl = document.getElementById('syndicate-cover-badge'), optDoc = document.getElementById('syndicate-cover-opt-doc'), picker = document.getElementById('syndicate-cover-mode-picker');
                if (res.strategy_used === 'doc_frontmatter') {
                    if (badgeEl) badgeEl.innerText = `生效: 文章已设封面 (${_currentAspectRatio})`;
                    if (optDoc) optDoc.style.display = '';
                    if (picker && (_currentMode === 'global' || _currentMode === 'doc_frontmatter')) picker.value = 'doc_frontmatter';
                } else if (badgeEl && (res.strategy_used || res.strategy)) {
                    badgeEl.innerText = `生效: ${res.strategy_used || res.strategy} (${_currentAspectRatio})`;
                }
            } else { throw new Error((res && res.message) || '生成失败'); }
        } catch (e) {
            console.warn("[Syndicate Cover Studio] Failed to render preview:", e);
            if (loadingEl) loadingEl.innerHTML = `<span style="font-size:0.65rem; color:#f87171;">渲染异常</span>`;
        }
    };

    window.onSyndicateCoverModeChange = function (newMode) {
        if (newMode === 'asset_picker') { window.openSyndicateAssetPickerModal(); return; }
        _currentMode = newMode;
        _currentOffset = 0;
        return window.loadSyndicateCoverPreview();
    };

    window.shuffleSyndicateCover = function () {
        _currentOffset = (_currentOffset + 1) % 8;
        window.loadSyndicateCoverPreview();
    };

    window.showImageModal = function (imgUrl, title, meta = {}) {
        let modal = document.getElementById('global-image-detail-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'global-image-detail-modal';
            modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.82);backdrop-filter:blur(10px);z-index:999999;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;';
            modal.onclick = (e) => { if (e.target === modal) modal.style.display = 'none'; };
            document.body.appendChild(modal);
            document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && modal.style.display !== 'none') modal.style.display = 'none'; });
        }
        modal.style.display = 'flex';
        const displayTitle = title || '封面图片详情';
        const ratio = meta.ratio || _currentAspectRatio || '16:9';
        const strat = meta.strategy || (_currentMode === 'global' ? '智能矩阵' : _currentMode);
        modal.innerHTML = `
            <div class="glass-panel" style="max-width:90vw;max-height:90vh;display:flex;flex-direction:column;border-radius:12px;overflow:hidden;border:1px solid rgba(0,242,254,0.3);box-shadow:0 25px 60px rgba(0,0,0,0.9);background:rgba(15,17,26,0.96);">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 18px;border-bottom:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.02);">
                    <div style="font-size:0.88rem;font-weight:700;color:var(--accent-primary,#00f2fe);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70vw;">🖼️ ${displayTitle}</div>
                    <button type="button" onclick="document.getElementById('global-image-detail-modal').style.display='none'" style="background:none;border:none;color:var(--text-dim);cursor:pointer;font-size:1.3rem;line-height:1;">✕</button>
                </div>
                <div style="flex:1;display:flex;align-items:center;justify-content:center;padding:16px;overflow:hidden;background:rgba(0,0,0,0.5);">
                    <img src="${imgUrl}" style="max-width:82vw;max-height:68vh;object-fit:contain;border-radius:8px;border:1px solid rgba(255,255,255,0.1);box-shadow:0 8px 30px rgba(0,0,0,0.6);" alt="${displayTitle}" />
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 18px;border-top:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.02);font-size:0.75rem;color:var(--text-dim);">
                    <div style="display:flex;gap:12px;align-items:center;">
                        <span>画幅比例: <b style="color:#fff;">${ratio}</b></span>
                        <span>生效策略: <b style="color:#a5b4fc;">${strat}</b></span>
                    </div>
                    <div style="display:flex;gap:8px;">
                        <a href="${imgUrl}" download="${displayTitle}.jpg" style="padding:4px 10px;border-radius:5px;background:rgba(0,242,254,0.15);border:1px solid rgba(0,242,254,0.3);color:#00f2fe;text-decoration:none;font-size:0.72rem;cursor:pointer;">📥 下载原图</a>
                        <button type="button" onclick="document.getElementById('global-image-detail-modal').style.display='none'" style="padding:4px 10px;border-radius:5px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#fff;font-size:0.72rem;cursor:pointer;">关闭</button>
                    </div>
                </div>
            </div>`;
    };

    window.previewSyndicateFullCover = function () {
        if (_currentCoverUrl) window.showImageModal(_currentCoverUrl, `封面详情 - ${_currentTitle}`, { ratio: _currentAspectRatio, strategy: _currentMode });
    };

    window.openSyndicateAssetPickerModal = async function () {
        let modal = document.getElementById('syndicate-asset-picker-modal');
        if (!modal) {
            modal = document.createElement('div'); modal.id = 'syndicate-asset-picker-modal';
            modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.78);backdrop-filter:blur(8px);z-index:999999;display:flex;align-items:center;justify-content:center;';
            document.body.appendChild(modal);
        }
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="glass-panel" style="width:840px;max-width:92vw;height:80vh;max-height:820px;border-radius:14px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,0.85);border:1px solid rgba(0,242,254,0.35);">
                <div style="padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.08);display:flex;justify-content:space-between;align-items:center;background:rgba(0,0,0,0.25);flex-shrink:0;">
                    <div>
                        <div style="font-size:0.95rem;font-weight:700;color:var(--accent-primary,#00f2fe);">🗄️ 挑选视觉物权资产为封面</div>
                        <div style="font-size:0.72rem;color:var(--text-dim);margin-top:2px;">点击任意历史生成或沉淀的图像资产，即时绑定为本篇分发封面。</div>
                    </div>
                    <div style="display:flex;gap:8px;align-items:center;">
                        <button type="button" class="mini-btn" style="padding:5px 12px;font-size:0.75rem;color:#00f2fe;border-color:rgba(0,242,254,0.4);" onclick="window.jumpToStudioFromSyndicate()">🪄 前往生图定制</button>
                        <button type="button" class="mini-btn" onclick="document.getElementById('syndicate-asset-picker-modal').style.display='none'" style="padding:4px 8px;font-size:0.8rem;">✕</button>
                    </div>
                </div>
                <div style="flex:1;overflow-y:auto;padding:16px 20px;min-height:0;" id="syndicate-asset-picker-scroll-view">
                    <div id="syndicate-asset-picker-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;">
                        <div style="grid-column:1/-1;display:flex;align-items:center;justify-content:center;color:var(--text-dim);font-size:0.8rem;padding:40px;">正在加载资产账本...</div>
                    </div>
                </div>
                <div id="syndicate-asset-picker-pagination" style="padding:10px 20px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;background:rgba(0,0,0,0.2);flex-shrink:0;"></div>
            </div>`;
        window.loadAssetsForCoverPicker(1);
    };

    window.loadAssetsForCoverPicker = async function (page = 1) {
        const grid = document.getElementById('syndicate-asset-picker-grid');
        const pag = document.getElementById('syndicate-asset-picker-pagination');
        if (!grid) return;
        try {
            grid.innerHTML = `<div style="grid-column:1/-1;display:flex;align-items:center;justify-content:center;color:var(--text-dim);font-size:0.8rem;padding:40px;">正在加载第 ${page} 页资产...</div>`;
            const fetchApi = window.apiFetch || (async (u) => (await fetch(u)).json());
            const pageSize = 18;
            const res = await fetchApi(`/api/design/assets?page=${page}&limit=${pageSize}`);
            const assets = (res && res.assets) || [];
            const total = (res && typeof res.total === 'number') ? res.total : assets.length;
            const totalPages = (res && typeof res.total_pages === 'number') ? res.total_pages : Math.max(1, Math.ceil(total / pageSize));

            if (assets.length === 0) {
                grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;color:var(--text-dim);padding:40px;font-size:0.8rem;">暂无可用资产，请前往设计中心创作。</div>`;
                if (pag) pag.innerHTML = '';
                return;
            }
            grid.innerHTML = assets.map(a => {
                const eng = ((a.engine || a.strategy || '物权').replace(/^ai_/, '')).toUpperCase();
                return `<div class="glass-panel doc-cover-item" onclick="window.onSelectAssetForCover('${a.url}','${a.engine}')" style="cursor:pointer;border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);background:rgba(10,14,24,0.6);display:flex;flex-direction:column;transition:all 0.2s;" onmouseover="this.style.borderColor='#00f2fe';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.08)';this.style.transform='translateY(0)'">
                    <div class="skeleton-shimmer" style="width:100%;height:105px;background:#05070f;position:relative;overflow:hidden;flex-shrink:0;">
                        <img src="${a.url}" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='/api/design/assets/default-cover.jpg';" style="width:100%;height:100%;object-fit:cover;display:block;" />
                        <div style="position:absolute;top:4px;left:4px;font-size:0.6rem;color:#fff;background:rgba(0,0,0,0.65);padding:1px 6px;border-radius:3px;backdrop-filter:blur(2px);">${eng}</div>
                    </div>
                    <div style="padding:7px 10px;font-size:0.68rem;display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02);flex-shrink:0;">
                        <span style="color:#a5b4fc;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:95px;" title="${a.engine || '视觉物权'}">${a.engine || '视觉物权'}</span>
                        <span style="color:var(--text-dim);font-size:0.62rem;font-family:monospace;">${(a.created_at || '').substring(5, 16)}</span>
                    </div>
                </div>`;
            }).join('');

            if (pag) {
                pag.innerHTML = `
                    <div style="font-size:0.72rem;color:var(--text-dim);">第 <strong style="color:#00f2fe;">${page}</strong> / ${totalPages} 页 (共 ${total} 项)</div>
                    <div style="display:flex;gap:6px;">
                        <button type="button" class="mini-btn" ${page <= 1 ? 'disabled style="opacity:0.35;cursor:not-allowed;"' : `onclick="window.loadAssetsForCoverPicker(${page - 1})"`}>◀️ 上一页</button>
                        <button type="button" class="mini-btn" ${page >= totalPages ? 'disabled style="opacity:0.35;cursor:not-allowed;"' : `onclick="window.loadAssetsForCoverPicker(${page + 1})"`}>下一页 ▶️</button>
                    </div>
                `;
            }
        } catch (e) { console.warn("Failed to load assets for picker:", e); }
    };

    window.onSelectAssetForCover = function (assetUrl, engineName) {
        if (window._pickingCoverForChannel) {
            const chan = window._pickingCoverForChannel; window._pickingCoverForChannel = null;
            const modal = document.getElementById('syndicate-asset-picker-modal');
            if (modal) modal.style.display = 'none';
            if (typeof window.applyChannelCoverOverride === 'function') window.applyChannelCoverOverride(chan, assetUrl);
            return;
        }
        _currentCoverUrl = assetUrl; _currentMode = 'custom';
        if (window.currentSyndicateCover) {
            window.currentSyndicateCover.url = assetUrl; window.currentSyndicateCover.mode = 'custom';
            window.currentSyndicateCover.strategy = `资产库 (${engineName || '物权'})`; window.currentSyndicateCover.offset = 0;
            window.currentSyndicateCover.aspect_ratio = _currentAspectRatio;
        }
        const imgEl = document.getElementById('syndicate-cover-thumb-img'), loadingEl = document.getElementById('syndicate-cover-loading');
        if (imgEl) { imgEl.src = `${assetUrl}?t=${Date.now()}`; if (loadingEl) loadingEl.style.display = 'none'; imgEl.style.display = 'block'; }
        const badgeEl = document.getElementById('syndicate-cover-badge'), picker = document.getElementById('syndicate-cover-mode-picker'), modal = document.getElementById('syndicate-asset-picker-modal');
        if (badgeEl) badgeEl.innerText = `生效: 资产库 (${engineName || '物权'})`;
        if (picker) picker.value = 'asset_picker';
        if (modal) modal.style.display = 'none';
        if (typeof window.showToast === 'function') window.showToast(`已选定资产作为本篇封面`, 'success');
    };

    window.jumpToStudioFromSyndicate = async function () {
        if (typeof window.closeArticleSyndicationDrawer === 'function') window.closeArticleSyndicationDrawer();
        if (typeof window.jumpToStudioFromDocModal === 'function') {
            await window.jumpToStudioFromDocModal(_currentTitle, _currentRelPath, true);
        } else {
            if (typeof window.showView === 'function') await window.showView('design'); else window.location.hash = '#/design';
            if (typeof window.switchDesignSubTab === 'function') window.switchDesignSubTab('workspace');
        }
        window._designTargetDoc = { title: _currentTitle, relPath: _currentRelPath, fromSyndicate: true };
        if (typeof window.renderDesignSubTab === 'function') window.renderDesignSubTab('workspace');
    }; })();
