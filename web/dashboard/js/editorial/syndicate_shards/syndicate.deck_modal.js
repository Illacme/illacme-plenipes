/**
 * 📑 [V2.1] Illacme Plenipes - Multi-Ratio Knowledge Card Deck Studio
 * 职责：知识卡片海报多画幅生成 (3:4 / 1:1 / 16:9)、胶卷平滑切换、ZIP 全套导出与分发图集装配。
 * 🛡️ [SOP-01] 物理行数保持在 300 行以内。
 */

(function () {
    let _currentRelPath = '', _currentDeckData = null, _currentActiveIndex = 0;
    let _currentOffset = 0, _currentAspectRatio = '3:4', _isGenerating = false;

    const _esc = (s) => (s === null || s === undefined ? '' : String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'));

    window.openKnowledgeCardDeckModal = async function (relPath) {
        _currentRelPath = relPath || window.currentSyndicatingRelPath || (window.currentPreviewDoc && window.currentPreviewDoc.rel_path) || '';
        if (!_currentRelPath) {
            if (typeof window.showToast === 'function') window.showToast('请先选择一篇文库稿件', 'warning');
            return;
        }
        _ensureModalDom();
        const backdrop = document.getElementById('syndicate-deck-modal-backdrop');
        if (backdrop) backdrop.style.display = 'flex';
        await _loadOrGenerateDeck();
    };

    window.closeKnowledgeCardDeckModal = function () {
        const backdrop = document.getElementById('syndicate-deck-modal-backdrop');
        if (backdrop) backdrop.style.display = 'none';
    };

    window.deckCardPrev = function () {
        if (!_currentDeckData || !_currentDeckData.cards?.length) return;
        _currentActiveIndex = (_currentActiveIndex - 1 + _currentDeckData.cards.length) % _currentDeckData.cards.length;
        _renderActiveCard();
    };
    window.deckCardNext = function () {
        if (!_currentDeckData || !_currentDeckData.cards?.length) return;
        _currentActiveIndex = (_currentActiveIndex + 1) % _currentDeckData.cards.length;
        _renderActiveCard();
    };
    window.switchDeckCardIndex = function (index) {
        if (!_currentDeckData || !_currentDeckData.cards?.length) return;
        _currentActiveIndex = (index + _currentDeckData.cards.length) % _currentDeckData.cards.length;
        _renderActiveCard();
    };

    window.switchDeckAspectRatio = async function (ratio) {
        if (_isGenerating || _currentAspectRatio === ratio) return;
        _currentAspectRatio = ratio || '3:4';
        _updateRatioButtons();
        await _loadOrGenerateDeck();
    };

    window.regenerateDeckWithOffset = async function () {
        if (_isGenerating) return;
        _currentOffset = (_currentOffset + 1) % 8;
        await _triggerDeckGeneration();
    };

    window.applyDeckToSyndication = function () {
        if (!_currentDeckData || !_currentDeckData.cards || _currentDeckData.cards.length === 0) return;
        const total = _currentDeckData.cards.length;
        window.currentSyndicateDeck = {
            rel_path: _currentRelPath,
            aspect_ratio: _currentAspectRatio,
            cards: _currentDeckData.cards,
            total: total,
            zip_url: _currentDeckData.zip_url
        };
        // 1. 同步首张卡片到分发抽屉封面缩略图
        const firstCard = _currentDeckData.cards[0];
        if (firstCard && firstCard.url) {
            const thumbImg = document.getElementById('syndicate-cover-thumb-img');
            const loadingEl = document.getElementById('syndicate-cover-loading');
            if (thumbImg) { thumbImg.src = `${firstCard.url}?t=${Date.now()}`; thumbImg.style.display = 'block'; }
            if (loadingEl) loadingEl.style.display = 'none';
            if (window.currentSyndicateCover) {
                window.currentSyndicateCover.url = firstCard.url;
                window.currentSyndicateCover.deck_ratio = _currentAspectRatio;
            }
            const badgeEl = document.getElementById('syndicate-cover-badge');
            if (badgeEl) badgeEl.innerText = `已装配图集 (${_currentAspectRatio} 共 ${total} 张)`;
        }
        // 2. 更新排版入口旁的指示徽章
        _updateDeckAttachedBadge();
        if (typeof window.showToast === 'function') {
            window.showToast(`✨ 成功装配 ${total} 张 ${_currentAspectRatio} 知识卡片为分发图集！`, 'success');
        }
        window.closeKnowledgeCardDeckModal();
    };

    function _updateDeckAttachedBadge() {
        const badgeSlot = document.getElementById('syndicate-deck-attached-pill');
        if (badgeSlot && window.currentSyndicateDeck && window.currentSyndicateDeck.total) {
            badgeSlot.style.display = 'inline-flex';
            badgeSlot.innerHTML = `🟢 已装配 ${window.currentSyndicateDeck.aspect_ratio} (${window.currentSyndicateDeck.total}张)`;
        }
    }

    function _updateRatioButtons() {
        document.querySelectorAll('.deck-ratio-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-ratio') === _currentAspectRatio);
        });
    }

    async function _loadOrGenerateDeck() {
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            _showLoading(`正在检测 ${_currentAspectRatio} 知识卡片状态...`);
            const info = await fetchApi(`/api/design/cards/info?rel_path=${encodeURIComponent(_currentRelPath)}&aspect_ratio=${encodeURIComponent(_currentAspectRatio)}`);
            if (info && info.exists && info.cards && info.cards.length > 0) {
                _currentDeckData = info;
                _currentActiveIndex = 0;
                _renderFullModal();
            } else {
                await _triggerDeckGeneration();
            }
        } catch (e) {
            console.warn('[CardDeck] Load deck info failed, generate fallback:', e);
            await _triggerDeckGeneration();
        }
    }

    async function _triggerDeckGeneration() {
        if (_isGenerating) return;
        _isGenerating = true;
        _showLoading(`正在切片并渲染 ${_currentAspectRatio} 极光知识海报...`);
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const result = await fetchApi('/api/design/cards/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rel_path: _currentRelPath,
                    offset: _currentOffset,
                    aspect_ratio: _currentAspectRatio,
                    max_cards: 6
                })
            });
            if (result && result.status === 'ok' && result.cards) {
                _currentDeckData = result;
                _currentActiveIndex = 0;
                _renderFullModal();
                if (typeof window.showToast === 'function') window.showToast(`✨ 成功生成 ${result.total} 张 ${_currentAspectRatio} 知识卡片！`, 'success');
            } else {
                _showError(result?.detail || '生成卡片海报失败');
            }
        } catch (err) {
            _showError(err.message || '网络通信异常');
        } finally {
            _isGenerating = false;
        }
    }

    function _renderFullModal() {
        const loadingEl = document.getElementById('syndicate-deck-loading-state');
        const contentEl = document.getElementById('syndicate-deck-content-state');
        if (loadingEl) loadingEl.style.display = 'none';
        if (contentEl) contentEl.style.display = 'flex';

        const titleEl = document.getElementById('syndicate-deck-modal-title');
        if (titleEl) {
            const shortName = _currentRelPath.split('/').pop().replace(/\.md$/, '');
            titleEl.innerHTML = `📑 知识卡片海报工坊 · <span style="color:var(--neon-cyan);">${_esc(shortName)}</span> <span class="syndicate-step-meta" style="margin-left:8px;">${_currentAspectRatio} 共 ${_currentDeckData.cards.length} 张</span>`;
        }

        const zipBtn = document.getElementById('syndicate-deck-zip-btn');
        if (zipBtn && _currentDeckData && _currentDeckData.zip_url) {
            zipBtn.href = _currentDeckData.zip_url;
            zipBtn.download = _currentDeckData.zip_filename || `deck_cards_${_currentAspectRatio.replace(':', 'x')}.zip`;
            zipBtn.style.display = 'inline-flex';
        }
        _updateRatioButtons();
        _renderActiveCard();
        _renderFilmstrip();
    }

    function _renderActiveCard() {
        if (!_currentDeckData || !_currentDeckData.cards || !_currentDeckData.cards[_currentActiveIndex]) return;
        const card = _currentDeckData.cards[_currentActiveIndex];
        const imgEl = document.getElementById('syndicate-deck-active-img');
        const badgeEl = document.getElementById('syndicate-deck-card-type-badge');
        const pageEl = document.getElementById('syndicate-deck-page-indicator');
        const metaTitleEl = document.getElementById('syndicate-deck-card-title-preview');

        if (imgEl) imgEl.src = `${card.url}?t=${Date.now()}`;
        if (badgeEl) {
            badgeEl.innerText = card.card_type === 'cover' ? '🚩 封面卡' : (card.card_type === 'closing' ? '🏁 结语速记卡' : '💡 核心要点卡');
        }
        if (pageEl) pageEl.innerText = `${_currentActiveIndex + 1} / ${_currentDeckData.cards.length}`;
        if (metaTitleEl) metaTitleEl.innerText = card.title || `第 ${_currentActiveIndex + 1} 页`;

        document.querySelectorAll('.deck-filmstrip-item').forEach((item, idx) => {
            if (idx === _currentActiveIndex) {
                item.classList.add('active');
                item.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            } else {
                item.classList.remove('active');
            }
        });
    }

    function _renderFilmstrip() {
        const stripEl = document.getElementById('syndicate-deck-filmstrip-track');
        if (!stripEl || !_currentDeckData || !_currentDeckData.cards) return;
        const ratioCls = `ratio-${_currentAspectRatio.replace(':', 'x')}`;
        stripEl.innerHTML = _currentDeckData.cards.map((c, idx) => `
            <div class="deck-filmstrip-item ${ratioCls} ${idx === _currentActiveIndex ? 'active' : ''}" onclick="window.switchDeckCardIndex(${idx})" title="${_esc(c.title || '')}">
                <img src="${c.url}?t=${Date.now()}" alt="Page ${idx + 1}" />
                <span class="deck-filmstrip-badge">${idx + 1}</span>
            </div>
        `).join('');
    }

    function _showLoading(msg) {
        const loadingEl = document.getElementById('syndicate-deck-loading-state');
        const contentEl = document.getElementById('syndicate-deck-content-state');
        const msgEl = document.getElementById('syndicate-deck-loading-msg');
        if (contentEl) contentEl.style.display = 'none';
        if (loadingEl) loadingEl.style.display = 'flex';
        if (msgEl) msgEl.innerText = msg;
    }

    function _showError(msg) {
        const loadingEl = document.getElementById('syndicate-deck-loading-state');
        if (loadingEl) {
            loadingEl.innerHTML = `<div style="text-align:center;padding:40px;"><div style="font-size:2rem;margin-bottom:12px;">⚠️</div><div style="color:#ef4444;font-size:0.9rem;margin-bottom:16px;">${_esc(msg)}</div><button type="button" class="mini-btn" onclick="window.openKnowledgeCardDeckModal('${_esc(_currentRelPath)}')">重试</button></div>`;
        }
    }

    function _ensureModalDom() {
        if (document.getElementById('syndicate-deck-modal-backdrop')) return;
        const html = `
        <div id="syndicate-deck-modal-backdrop" class="syndicate-modal-backdrop" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,0.5);backdrop-filter:blur(12px);z-index:99999;align-items:center;justify-content:center;">
            <div id="syndicate-deck-modal-panel" class="deck-modal-panel" style="width:1020px;max-width:96vw;height:840px;max-height:92vh;border-radius:18px;display:flex;flex-direction:column;overflow:hidden;">
                <div class="deck-modal-header" style="display:flex;align-items:center;justify-content:space-between;padding:16px 24px;">
                    <div id="syndicate-deck-modal-title" class="deck-title" style="font-size:1.05rem;font-weight:600;display:flex;align-items:center;">📑 知识卡片海报工坊 (Card Deck Studio)</div>
                    <button type="button" class="syndicate-modal-close-btn deck-sub" onclick="window.closeKnowledgeCardDeckModal()" style="background:transparent;border:none;font-size:1.3rem;cursor:pointer;">&times;</button>
                </div>
                <div id="syndicate-deck-loading-state" class="deck-sub" style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;">
                    <span class="spinner-gear" style="font-size:2rem;animation:spin 1s infinite linear;">⚙️</span>
                    <span id="syndicate-deck-loading-msg" style="font-size:0.9rem;">正在切片生成知识海报...</span>
                </div>
                <div id="syndicate-deck-content-state" style="flex:1;display:none;flex-direction:column;overflow:hidden;">
                    <div style="flex:1;display:flex;gap:20px;padding:20px 24px;overflow:hidden;min-height:0;">
                        <div id="syndicate-deck-stage" class="deck-stage" style="flex:1.4;display:flex;align-items:center;justify-content:center;border-radius:12px;position:relative;padding:16px;overflow:hidden;min-width:0;min-height:0;box-sizing:border-box;">
                            <button type="button" class="deck-nav-btn" onclick="window.deckCardPrev()" style="position:absolute;left:14px;top:50%;transform:translateY(-50%);background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.2);color:#fff;border-radius:50%;width:40px;height:40px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:1.2rem;z-index:2;box-shadow:0 4px 12px rgba(0,0,0,0.35);">‹</button>
                            <img id="syndicate-deck-active-img" src="" alt="Active Card" style="max-width:100%;max-height:480px;width:auto;height:auto;object-fit:contain;border-radius:8px;box-shadow:0 12px 30px rgba(0,0,0,0.25);" />
                            <button type="button" class="deck-nav-btn" onclick="window.deckCardNext()" style="position:absolute;right:14px;top:50%;transform:translateY(-50%);background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.2);color:#fff;border-radius:50%;width:40px;height:40px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:1.2rem;z-index:2;box-shadow:0 4px 12px rgba(0,0,0,0.35);">›</button>
                        </div>
                        <div style="flex:1;display:flex;flex-direction:column;justify-content:space-between;padding:4px 0;min-width:320px;">
                            <div>
                                <div class="deck-ratio-bar" style="display:flex;gap:6px;margin-bottom:14px;padding:4px;border-radius:8px;">
                                    <button type="button" class="deck-ratio-btn active" data-ratio="3:4" onclick="window.switchDeckAspectRatio('3:4')">3:4 竖屏</button>
                                    <button type="button" class="deck-ratio-btn" data-ratio="1:1" onclick="window.switchDeckAspectRatio('1:1')">1:1 方形</button>
                                    <button type="button" class="deck-ratio-btn" data-ratio="16:9" onclick="window.switchDeckAspectRatio('16:9')">16:9 宽屏</button>
                                </div>
                                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                                    <span id="syndicate-deck-card-type-badge" style="padding:4px 10px;border-radius:6px;background:rgba(14,165,233,0.14);color:#0284c7;font-size:0.75rem;font-weight:600;border:1px solid rgba(14,165,233,0.3);">💡 核心要点卡</span>
                                    <span id="syndicate-deck-page-indicator" class="deck-sub" style="font-size:0.85rem;font-weight:600;">01 / 05</span>
                                </div>
                                <div id="syndicate-deck-card-title-preview" class="deck-title" style="font-size:1.05rem;font-weight:600;margin-bottom:14px;line-height:1.4;">-</div>
                                <div class="deck-info-box deck-sub" style="border-radius:10px;padding:12px;font-size:0.78rem;line-height:1.6;">
                                    <p class="deck-title" style="margin:0 0 6px 0;font-weight:500;">📱 全域多图社交与知识衍生场景：</p>
                                    <ul style="margin:0;padding-left:16px;"><li><b>3:4 竖屏</b>：小红书、朋友圈、即刻移动信息流满屏首选；</li><li><b>1:1 方形</b>：Instagram Carousel、朋友圈九宫格、微博；</li><li><b>16:9 宽屏</b>：Twitter/X 轮播、演示文稿 (Pitch Deck)。</li></ul>
                                </div>
                            </div>
                            <div style="display:flex;flex-direction:column;gap:8px;">
                                <button type="button" class="mini-btn" onclick="window.regenerateDeckWithOffset()" style="padding:9px;background:rgba(124,58,237,0.14);border:1px solid rgba(124,58,237,0.35);color:#9333ea;border-radius:8px;font-size:0.8rem;font-weight:600;cursor:pointer;">🔄 换一套极光配色方案 (相移)</button>
                                <a id="syndicate-deck-zip-btn" href="#" class="mini-btn" style="display:none;padding:9px;background:rgba(16,185,129,0.14);border:1px solid rgba(16,185,129,0.35);color:#059669;border-radius:8px;font-size:0.8rem;font-weight:600;text-align:center;text-decoration:none;cursor:pointer;">💾 打包下载全套高清卡片 (ZIP)</a>
                                <button type="button" class="mini-btn glow-btn" onclick="window.applyDeckToSyndication()" style="padding:9px;background:linear-gradient(135deg,#ec4899,#8b5cf6);color:#fff;border:none;border-radius:8px;font-size:0.8rem;font-weight:600;cursor:pointer;">✨ 应用为当前稿件分发图集</button>
                            </div>
                        </div>
                    </div>
                    <div class="deck-filmstrip-bar" style="padding:10px 24px;">
                        <div id="syndicate-deck-filmstrip-track" style="display:flex;gap:12px;overflow-x:auto;padding-bottom:4px;scrollbar-width:thin;"></div>
                    </div>
                </div>
            </div>
        </div>
        <style>
            .deck-modal-panel{background:rgba(12,18,34,0.96);border:1px solid rgba(255,255,255,0.12);box-shadow:0 24px 60px rgba(0,0,0,0.8);} .deck-modal-header{border-bottom:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.02);}
            .deck-title{color:#f8fafc;} .deck-sub{color:#94a3b8;} .deck-stage{background:rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.08);} .deck-ratio-bar,.deck-info-box{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);} .deck-filmstrip-bar{border-top:1px solid rgba(255,255,255,0.08);background:rgba(0,0,0,0.3);}
            [data-theme="light"] .deck-modal-panel{background:#ffffff;border-color:#e2e8f0;box-shadow:0 24px 60px rgba(15,23,42,0.18);} [data-theme="light"] .deck-modal-header{background:#f8fafc;border-bottom-color:#e2e8f0;}
            [data-theme="light"] .deck-title{color:#0f172a;} [data-theme="light"] .deck-sub{color:#64748b;} [data-theme="light"] .deck-stage{background:#f1f5f9;border-color:#e2e8f0;} [data-theme="light"] .deck-ratio-bar,[data-theme="light"] .deck-info-box{background:#f8fafc;border-color:#e2e8f0;} [data-theme="light"] .deck-filmstrip-bar{border-top-color:#e2e8f0;background:#f8fafc;}
            .deck-ratio-btn{flex:1;padding:6px 0;border:none;background:transparent;color:#64748b;font-size:0.75rem;border-radius:6px;cursor:pointer;transition:all 0.2s ease;}
            .deck-ratio-btn.active{background:rgba(14,165,233,0.15);color:#0284c7;font-weight:600;border:1px solid rgba(14,165,233,0.35);}
            .deck-filmstrip-item{flex-shrink:0;height:56px;border-radius:6px;overflow:hidden;position:relative;cursor:pointer;border:2px solid transparent;opacity:0.6;transition:all 0.2s ease;}
            .deck-filmstrip-item.ratio-3x4{width:42px;} .deck-filmstrip-item.ratio-1x1{width:56px;} .deck-filmstrip-item.ratio-16x9{width:100px;}
            .deck-filmstrip-item:hover{opacity:0.9;transform:translateY(-2px);} .deck-filmstrip-item.active{border-color:#0284c7;opacity:1;}
            .deck-filmstrip-item img{width:100%;height:100%;object-fit:cover;} .deck-filmstrip-badge{position:absolute;bottom:2px;right:2px;background:rgba(0,0,0,0.7);color:#fff;font-size:0.65rem;padding:1px 4px;border-radius:3px;font-weight:600;}
        </style>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    }
})();
