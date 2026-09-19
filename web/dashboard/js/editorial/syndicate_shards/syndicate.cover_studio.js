/**
 * 🖼️ [V2.0] Illacme Plenipes Article Syndication - Cover Studio Shard
 * 职责：社媒分发抽屉封面凭据管理、多语种标题联动与渠道画幅自适应 (16:9 / 2.35:1 / 1:1)。
 * 🛡️ [SOP-01] 物理行数保持在 300 行以内。
 */
(function () {
    const _esc = (s) => (s === null || s === undefined ? '' : String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'));
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
            <div class="syndicate-cover-studio-header">
                <label class="syndicate-step-label" style="margin:0;"><span>🖼️ 封面视觉凭据</span><span class="lang-tag-target">社媒必填</span></label>
                <div style="display:flex;align-items:center;gap:6px;"><span id="syndicate-cover-badge" class="syndicate-step-meta">策略: ${STRAT_MAP[defaultStrategy] || defaultStrategy}</span><span id="syndicate-finetune-badge-slot"></span></div>
            </div>
            <div class="syndicate-cover-studio-row">
                <div class="syndicate-cover-preview-col">
                    <div id="syndicate-cover-thumb-wrapper" class="syndicate-cover-thumb-wrapper">
                        <div id="syndicate-cover-loading" class="syndicate-cover-loading"><span class="spinner-gear" style="display:inline-block;animation:spin 1s infinite linear;">⚙️</span><span>渲染凭据中...</span></div>
                        <img id="syndicate-cover-thumb-img" class="syndicate-cover-img" src="" alt="封面缩略图" onclick="window.previewSyndicateFullCover()" title="点击查看大图" />
                        <div id="syndicate-cover-safezone" class="syndicate-cover-safezone-tag"></div>
                    </div>
                    <div class="syndicate-sz-btn-group">
                        <button type="button" class="sz-btn active" data-mode="none" onclick="window.setCoverSafeZone('none',this,true)">全画幅</button>
                        <button type="button" class="sz-btn" data-mode="wechat" onclick="window.setCoverSafeZone('wechat',this,true)" title="对齐微信公众号首条列表 2.35:1 画幅">微信2.35:1</button>
                        <button type="button" class="sz-btn" data-mode="square" onclick="window.setCoverSafeZone('square',this,true)" title="小红书/Instagram 方形封面">方形1:1</button>
                    </div>
                </div>
                <div class="syndicate-cover-controls-col syndicate-cover-meta-col">
                    <select id="syndicate-cover-mode-picker" class="syndicate-cover-mode-select" onchange="window.onSyndicateCoverModeChange(this.value)">
                        <option value="global">🌐 跟随全局默认 (${STRAT_MAP[defaultStrategy] || '智能矩阵'})</option>
                        <option value="doc_frontmatter" id="syndicate-cover-opt-doc" style="display:none;">📌 文章设定封面 (Frontmatter)</option>
                        <option value="asset_picker">🗃️ 从媒体资产库挑选...</option>
                        <option value="og_card">🃏 动态技术卡片 (OG Card)</option>
                        <option value="brand_presets">🎭 品牌母本轮巡</option>
                        <option value="minimal_badge">🔤 极简首字文字徽章</option>
                        <option value="first_image">🖼️ 优先提取正文首图</option>
                        <option value="ai_generation">🤖 AI 智能生图</option>
                    </select>
                    <div class="syndicate-cover-actions">
                        <button type="button" class="mini-btn syndicate-cover-btn-shuffle" onclick="window.shuffleSyndicateCover()" title="根据相移轮巡色彩或概念">🔄 换一张</button>
                        <button type="button" class="mini-btn syndicate-cover-btn-studio" onclick="window.jumpToStudioFromSyndicate()" title="前往智能生图工作台精细调试模型、画幅与Prompt">🪄 生图工作台</button>
                        <button type="button" class="mini-btn syndicate-cover-btn-asset" onclick="window.openSyndicateAssetPickerModal()" title="从设计中心视觉资产库中选取">🗄️ 资产库</button>
                    </div>
                </div>
            </div>`;
        window.loadSyndicateCoverPreview();
    };

    window.setCoverSafeZone = function (mode, btn, isManual = false) {
        if (isManual) _userManualRatio = true;
        const szEl = document.getElementById('syndicate-cover-safezone'), wrapper = document.getElementById('syndicate-cover-thumb-wrapper');
        document.querySelectorAll('.sz-btn').forEach(b => { b.classList.remove('active'); });
        const activeBtn = btn || document.querySelector(`.sz-btn[data-mode="${mode}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        if (mode === 'wechat') {
            _currentAspectRatio = '2.35:1';
            if (wrapper) { wrapper.style.width = '140px'; wrapper.style.height = '60px'; }
            if (szEl) { szEl.style.display = 'block'; szEl.innerHTML = `<span class="syndicate-sz-tag syndicate-sz-tag--wechat">2.35:1</span>`; }
        } else if (mode === 'square') {
            _currentAspectRatio = '1:1';
            if (wrapper) { wrapper.style.width = '80px'; wrapper.style.height = '80px'; }
            if (szEl) { szEl.style.display = 'block'; szEl.innerHTML = `<span class="syndicate-sz-tag syndicate-sz-tag--square">1:1</span>`; }
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
        if (onlyWechat && _currentAspectRatio !== '2.35:1') window.setCoverSafeZone('wechat', null, false);
        else if (onlyXhs && _currentAspectRatio !== '1:1') window.setCoverSafeZone('square', null, false);
        else if (!onlyWechat && !onlyXhs && _currentAspectRatio !== '16:9') window.setCoverSafeZone('none', null, false);
    };

    window.onSyndicateCoverLangChange = function (langCode) {
        _currentLangCode = langCode || 'auto';
        if (_currentMode !== 'custom') window.loadSyndicateCoverPreview();
    };

    window.loadSyndicateCoverPreview = async function () {
        const loadingEl = document.getElementById('syndicate-cover-loading'), imgEl = document.getElementById('syndicate-cover-thumb-img');
        if (loadingEl) loadingEl.style.display = 'flex';
        if (imgEl) imgEl.style.display = 'none';

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        const activeBrand = (window.settingsData && window.settingsData.current_brand) || 'default';
        const payload = {
            strategy: _currentMode === 'global' ? 'auto' : _currentMode, title: _currentTitle,
            doc_id: _currentRelPath, brand_id: activeBrand, aspect_ratio: _currentAspectRatio,
            lang_code: _currentLangCode, offset: _currentOffset
        };

        try {
            const res = await fetchApi('/api/design/cover/preview', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
            });
            const coverUrl = (res && res.success && (res.url || res.cover_url)) ? (res.url || res.cover_url) : null;
            if (coverUrl) {
                _currentCoverUrl = coverUrl;
                if (window.currentSyndicateCover) {
                    window.currentSyndicateCover.url = coverUrl; window.currentSyndicateCover.mode = _currentMode;
                    window.currentSyndicateCover.strategy = res.strategy_used || res.strategy;
                    window.currentSyndicateCover.offset = _currentOffset; window.currentSyndicateCover.aspect_ratio = _currentAspectRatio;
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
            if (loadingEl) loadingEl.innerHTML = `<span class="syndicate-cover-error-text">渲染异常</span>`;
        }
    };

    window.onSyndicateCoverModeChange = function (newMode) {
        if (newMode === 'asset_picker') { window.openSyndicateAssetPickerModal(); return; }
        _currentMode = newMode; _currentOffset = 0; return window.loadSyndicateCoverPreview();
    };
    window.shuffleSyndicateCover = function () {
        _currentOffset = (_currentOffset + 1) % 8; window.loadSyndicateCoverPreview();
    };
    function _getOrCreateModal(id, cls, closeFn) {
        let el = document.getElementById(id);
        if (!el) {
            el = document.createElement('div'); el.id = id; el.className = cls;
            el.onclick = (e) => { if (e.target === el) closeFn(); };
            document.body.appendChild(el);
            document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeFn(); });
        }
        el.style.display = 'flex';
        if (el.classList) el.classList.add('is-open'); else el.className = ((el.className || '') + ' is-open').trim();
        return el;
    }
    function _closeModal(id) {
        const m = document.getElementById(id);
        if (m) {
            if (m.classList) m.classList.remove('is-open'); else m.className = (m.className || '').replace(/\bis-open\b/g, '').trim();
            setTimeout(() => { if (m && !m.classList.contains('is-open')) m.style.display = 'none'; }, 220);
        }
    }

    window.showImageModal = function (imgUrl, title, meta = {}) {
        const modal = _getOrCreateModal('global-image-detail-modal', 'syndicate-image-detail-backdrop', window.closeGlobalImageDetailModal);
        const displayTitle = title || '封面图片详情', ratio = meta.ratio || _currentAspectRatio || '16:9', strat = meta.strategy || (_currentMode === 'global' ? '智能矩阵' : _currentMode);
        modal.innerHTML = `
            <div class="glass-panel syndicate-image-detail-card">
                <div class="syndicate-image-detail-header">
                    <div class="syndicate-image-detail-title">🖼️ ${_esc(displayTitle)}</div>
                    <button type="button" class="syndicate-image-detail-close-btn" onclick="window.closeGlobalImageDetailModal()">✕</button>
                </div>
                <div class="syndicate-image-detail-viewport"><img src="${imgUrl}" class="syndicate-image-detail-img" alt="${_esc(displayTitle)}" /></div>
                <div class="syndicate-image-detail-footer">
                    <div class="syndicate-image-detail-meta">
                        <span>画幅比例: <b class="syndicate-image-detail-meta-val">${ratio}</b></span>
                        <span>生效策略: <b class="syndicate-image-detail-meta-val--purple">${strat}</b></span>
                    </div>
                    <div class="syndicate-image-detail-actions">
                        <a href="${imgUrl}" download="${_esc(displayTitle)}.jpg" class="syndicate-image-detail-download-btn">📥 下载原图</a>
                        <button type="button" class="syndicate-image-detail-btn" onclick="window.closeGlobalImageDetailModal()">关闭</button>
                    </div>
                </div>
            </div>`;
    };

    window.closeGlobalImageDetailModal = () => _closeModal('global-image-detail-modal');

    window.previewSyndicateFullCover = function () {
        if (_currentCoverUrl) window.showImageModal(_currentCoverUrl, `封面详情 - ${_currentTitle}`, { ratio: _currentAspectRatio, strategy: _currentMode });
    };

    window.openSyndicateAssetPickerModal = async function () {
        const modal = _getOrCreateModal('syndicate-asset-picker-modal', 'syndicate-asset-picker-backdrop', window.closeSyndicateAssetPickerModal);
        modal.innerHTML = `
            <div class="glass-panel syndicate-asset-picker-card">
                <div class="syndicate-asset-picker-header">
                    <div class="syndicate-asset-picker-title-group">
                        <div class="syndicate-asset-picker-title">🗄️ 挑选视觉物权资产为封面</div>
                        <div class="syndicate-asset-picker-desc">点击任意历史生成或沉淀的图像资产，即时绑定为本篇分发封面。</div>
                    </div>
                    <div class="syndicate-asset-picker-actions">
                        <button type="button" class="mini-btn syndicate-asset-picker-studio-btn" onclick="window.jumpToStudioFromSyndicate()">🪄 前往生图定制</button>
                        <button type="button" class="syndicate-asset-picker-close-btn" onclick="window.closeSyndicateAssetPickerModal()">✕</button>
                    </div>
                </div>
                <div class="syndicate-asset-picker-scroll-view" id="syndicate-asset-picker-scroll-view">
                    <div id="syndicate-asset-picker-grid" class="syndicate-asset-picker-grid">
                        <div class="syndicate-asset-picker-loading">正在加载资产账本...</div>
                    </div>
                </div>
                <div id="syndicate-asset-picker-pagination" class="syndicate-asset-picker-pagination"></div>
            </div>`;
        window.loadAssetsForCoverPicker(1);
    };

    window.closeSyndicateAssetPickerModal = () => _closeModal('syndicate-asset-picker-modal');

    window.loadAssetsForCoverPicker = async function (page = 1) {
        const grid = document.getElementById('syndicate-asset-picker-grid'), pag = document.getElementById('syndicate-asset-picker-pagination');
        if (!grid) return;
        try {
            grid.innerHTML = Array.from({ length: 6 }).map(() => `<div class="glass-panel syndicate-asset-item syndicate-asset-item--skeleton"><div class="skeleton-shimmer syndicate-asset-thumb-box"></div><div class="syndicate-asset-meta-row"><span class="skeleton-shimmer" style="width:60px;height:10px;border-radius:3px;"></span><span class="skeleton-shimmer" style="width:36px;height:10px;border-radius:3px;"></span></div></div>`).join('');
            const fetchApi = window.apiFetch || (async (u) => (await fetch(u)).json()), pageSize = 18;
            const res = await fetchApi(`/api/design/assets?page=${page}&limit=${pageSize}`);
            const assets = (res && res.assets) || [], total = (res && typeof res.total === 'number') ? res.total : assets.length;
            const totalPages = (res && typeof res.total_pages === 'number') ? res.total_pages : Math.max(1, Math.ceil(total / pageSize));

            if (assets.length === 0) {
                grid.innerHTML = `<div class="syndicate-asset-picker-empty"><div class="syndicate-asset-picker-empty-icon">📭</div><div class="syndicate-asset-picker-empty-title">视觉资产库暂无已沉淀内容</div><div class="syndicate-asset-picker-empty-desc">前往设计中心生成或上传海报，沉淀后即可在此一键复用为各平台封面。</div><button type="button" class="mini-btn syndicate-asset-picker-empty-btn" onclick="window.closeSyndicateAssetPickerModal();window.jumpToStudioFromSyndicate();">🪄 前往生图工作台定制</button></div>`;
                if (pag) pag.innerHTML = '';
                return;
            }
            grid.innerHTML = assets.map(a => {
                const eng = ((a.engine || a.strategy || '物权').replace(/^ai_/, '')).toUpperCase();
                return `<div class="glass-panel syndicate-asset-item doc-cover-item" onclick="window.onSelectAssetForCover('${a.url}','${a.engine}',this)">
                    <div class="skeleton-shimmer syndicate-asset-thumb-box">
                        <img src="${a.url}" class="syndicate-asset-img" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='/api/design/assets/default-cover.jpg';" />
                        <div class="syndicate-asset-engine-tag">${eng}</div>
                    </div>
                    <div class="syndicate-asset-meta-row">
                        <span class="syndicate-asset-engine-name" title="${_esc(a.engine || '视觉物权')}">${_esc(a.engine || '视觉物权')}</span>
                        <span class="syndicate-asset-date">${(a.created_at || '').substring(5, 16)}</span>
                    </div>
                </div>`;
            }).join('');

            if (pag) {
                pag.innerHTML = `<div class="syndicate-asset-picker-page-info">第 <strong class="syndicate-asset-picker-page-current">${page}</strong> / ${totalPages} 页 (共 ${total} 项)</div>
                    <div class="syndicate-asset-picker-page-actions">
                        <button type="button" class="mini-btn syndicate-asset-picker-page-btn" ${page <= 1 ? 'disabled' : `onclick="window.loadAssetsForCoverPicker(${page - 1})"`}>◀️ 上一页</button>
                        <button type="button" class="mini-btn syndicate-asset-picker-page-btn" ${page >= totalPages ? 'disabled' : `onclick="window.loadAssetsForCoverPicker(${page + 1})"`}>下一页 ▶️</button>
                    </div>`;
            }
        } catch (e) { console.warn("Failed to load assets for picker:", e); }
    };

    window.onSelectAssetForCover = function (assetUrl, engineName, itemEl) {
        if (itemEl && itemEl.classList) itemEl.classList.add('is-selected');
        if (window._pickingCoverForChannel) {
            const chan = window._pickingCoverForChannel; window._pickingCoverForChannel = null;
            window.closeSyndicateAssetPickerModal();
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
        const badgeEl = document.getElementById('syndicate-cover-badge'), picker = document.getElementById('syndicate-cover-mode-picker');
        if (badgeEl) badgeEl.innerText = `生效: 资产库 (${engineName || '物权'})`;
        if (picker) picker.value = 'asset_picker';
        window.closeSyndicateAssetPickerModal();
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
