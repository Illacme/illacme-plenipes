/**
 * 🛰️ [V105.0] Illacme Plenipes Article Syndication - Live Preview Modal Shard
 * 职责：全渠道高保真排版沉浸式审查视窗 (Modal) 与一键富文本剪贴板导出。
 * 🛡️ [SOP-01 规范]：严格收敛于 300 行以内。
 */

(function () {
    window.currentSyndicatePreviewTarget = 'wechat';
    window._syndicatePreviewCache = {};

    const _esc = (s) => (s === null || s === undefined ? '' : String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'));

    function getPreviewChannels() {
        const publisherPlugins = (window.allPlugins || []).filter(p => p.category === 'publisher');
        if (publisherPlugins.length > 0) {
            return publisherPlugins.map(p => {
                const meta = (typeof window.getSyndicateChannelMeta === 'function')
                    ? window.getSyndicateChannelMeta(p.id)
                    : { name: p.name || p.id, icon: p.icon || '📡' };
                const id = p.id.toLowerCase();
                let group = '国内专栏';
                if (['devto', 'medium', 'hashnode', 'substack', 'ghost', 'wordpress'].includes(id)) {
                    group = '海外发布';
                } else if (['telegram', 'discord'].includes(id)) {
                    group = '社交渠道';
                } else if (['xiaohongshu', 'red'].includes(id)) {
                    group = '短图文';
                }
                return { id: p.id, name: meta.name, icon: meta.icon, group };
            });
        }
        if (window.currentActivePlatforms && window.currentActivePlatforms.length > 0) {
            return window.currentActivePlatforms.map(p => ({
                id: p.id, name: p.name, icon: p.icon, group: '分发渠道'
            }));
        }
        return [
            { id: 'wechat', name: '微信公众号', icon: '💬', group: '国内专栏' }
        ];
    }

    window.openSyndicateLivePreviewModal = function () {
        let modalEl = document.getElementById('syndicate-live-preview-modal-root');
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.id = 'syndicate-live-preview-modal-root';
            modalEl.className = 'syndicate-modal-backdrop';
            document.body.appendChild(modalEl);
        }

        const title = window.currentSyndicatingTitle || window.currentSyndicatingRelPath || '未命名文稿';
        const checkedBoxes = document.querySelectorAll('.syndicate-platform-checkbox:checked');
        let sensedTargets = Array.from(checkedBoxes).map(cb => cb.value.toLowerCase());
        if (!sensedTargets.length) sensedTargets = ['wechat', 'zhihu', 'juejin', 'devto'];
        const initialTarget = sensedTargets[0] || 'wechat';
        window.currentSyndicatePreviewTarget = initialTarget;
        window._sensedPreviewTargets = sensedTargets.slice(0, 4);

        const channels = getPreviewChannels();
        const groupMap = {};
        channels.forEach(c => {
            if (!groupMap[c.group]) groupMap[c.group] = [];
            groupMap[c.group].push(c);
        });
        const selectOptions = Object.entries(groupMap).map(([grp, items]) => {
            const opts = items.map(c => `<option value="${c.id}">${c.icon} ${c.name}</option>`).join('');
            return `<optgroup label="── ${grp} ──">${opts}</optgroup>`;
        }).join('');

        modalEl.innerHTML = `
            <div class="syndicate-preview-modal-card glass-panel">
                <div class="syndicate-modal-header">
                    <div class="syndicate-modal-title-group">
                        <span class="syndicate-modal-title-icon">👁️</span>
                        <div class="syndicate-modal-title-text">
                            <div class="syndicate-modal-title">全渠道高保真排版即时审查</div>
                            <div class="syndicate-modal-subtitle">稿件：${_esc(title)}</div>
                        </div>
                    </div>
                    <div class="syndicate-modal-header-actions">
                        <div id="syndicate-modal-preview-tabs" class="syndicate-modal-tabs"></div>
                        <select id="syndicate-modal-channel-select" class="syndicate-modal-channel-select" onchange="window.switchSyndicatePreviewTarget(this.value)">
                            <option value="" selected disabled>🌐 更多渠道 ▾</option>
                            ${selectOptions}
                        </select>
                        <button type="button" class="syndicate-modal-close-btn" onclick="window.closeSyndicateLivePreviewModal()" title="关闭 (Esc)">×</button>
                    </div>
                </div>
                <div id="syndicate-modal-toolbar-slot" class="syndicate-modal-toolbar">
                    <div id="syndicate-modal-stats-capsule" class="syndicate-modal-stats"><span>正在初始化合规分析...</span></div>
                    <div id="syndicate-modal-actions-slot" class="syndicate-modal-actions"></div>
                </div>
                <div id="syndicate-modal-body-container" class="syndicate-modal-body">
                    <div id="syndicate-card-preview-renderer" class="syndicate-card-preview-renderer"></div>
                </div>
            </div>
        `;
        if (modalEl.classList) {
            modalEl.classList.add('is-open');
        } else {
            modalEl.className = ((modalEl.className || '') + ' is-open').trim();
        }

        const escHandler = (e) => {
            if (e.key === 'Escape') {
                window.closeSyndicateLivePreviewModal();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        modalEl.onclick = (e) => { if (e.target === modalEl) window.closeSyndicateLivePreviewModal(); };
        window.updatePreviewTabCapsules(initialTarget);
        window.renderSyndicateCardPreview(initialTarget);
    };

    window.updatePreviewTabCapsules = function (currentTarget) {
        const container = document.getElementById('syndicate-modal-preview-tabs');
        if (!container) return;
        const sensed = window._sensedPreviewTargets || ['wechat', 'zhihu', 'juejin'];
        const displayTargets = [...sensed];
        if (!displayTargets.includes(currentTarget)) displayTargets.push(currentTarget);

        container.innerHTML = displayTargets.map(tid => {
            const meta = (typeof window.getSyndicateChannelMeta === 'function')
                ? window.getSyndicateChannelMeta(tid)
                : { name: tid.toUpperCase(), icon: '📡' };
            const isActive = tid === currentTarget;
            return `<button type="button" class="syndicate-modal-tab-btn ${isActive ? 'is-active' : ''}" onclick="window.switchSyndicatePreviewTarget('${tid}')">${meta.icon} ${meta.name}</button>`;
        }).join('');
    };

    window.closeSyndicateLivePreviewModal = function () {
        const modalEl = document.getElementById('syndicate-live-preview-modal-root');
        if (modalEl) {
            if (modalEl.classList) {
                modalEl.classList.remove('is-open');
            } else {
                modalEl.className = (modalEl.className || '').replace(/\bis-open\b/g, '').trim();
            }
        }
    };

    window.switchSyndicatePreviewTarget = function (target) {
        if (!target) return;
        window.currentSyndicatePreviewTarget = target;
        window.updatePreviewTabCapsules(target);
        const selectEl = document.getElementById('syndicate-modal-channel-select');
        if (selectEl) selectEl.value = "";
        window.renderSyndicateCardPreview(target);
    };

    window.fetchSyndicatePreviewData = async function (relPath, platform, lang) {
        const cacheKey = `${relPath}_${platform}_${lang}`;
        if (window._syndicatePreviewCache[cacheKey]) return window._syndicatePreviewCache[cacheKey];
        try {
            const fetchFn = window.apiFetch || (async (u, o) => { const r = await fetch(u, o); return r.json(); });
            const res = await fetchFn('/api/syndication/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rel_path: relPath, target_platform: platform, lang: lang, convert_footnotes: true })
            });
            if (res && res.status === 'success') {
                window._syndicatePreviewCache[cacheKey] = res;
                return res;
            }
            return null;
        } catch (e) {
            console.warn("⚠️ [SyndicatePreview] 获取排版失败:", e);
            return null;
        }
    };

    window.renderSyndicateCardPreview = async function (target) {
        target = target || window.currentSyndicatePreviewTarget || 'wechat';
        const container = document.getElementById('syndicate-card-preview-renderer');
        const statsSlot = document.getElementById('syndicate-modal-stats-capsule');
        const actionsSlot = document.getElementById('syndicate-modal-actions-slot');
        if (!container) return;

        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();
        const relPath = window.currentSyndicatingRelPath || '';

        container.innerHTML = `<div class="syndicate-preview-loading"><span class="pulse-icon">⚙️</span><span>正在编译 ${target.toUpperCase()} 高保真排版...</span></div>`;

        const data = await window.fetchSyndicatePreviewData(relPath, target, selectedLang);
        if (!data) {
            container.innerHTML = `<div class="syndicate-preview-empty">⚠️ 暂未获取到稿件排版数据</div>`;
            return;
        }

        const stats = data.stats || {};
        const compliance = data.compliance || {};
        const isWechat = target === 'wechat';
        const isXhs = target === 'xiaohongshu';
        const isMobile = isWechat || isXhs;

        window._currentRenderedHtml = data.rendered_html || '';
        window._currentRenderedMarkdown = data.rendered_markdown || '';

        if (statsSlot) {
            statsSlot.innerHTML = `
                <span class="badge syndicate-stat-badge--cyan">📊 约 ${stats.word_count || 0} 字</span>
                <span class="badge syndicate-stat-badge--dim">⏱️ 约 ${stats.reading_time_min || 1} 分钟</span>
                ${isWechat ? `<span class="badge syndicate-stat-badge--purple">🔗 脚注: ${stats.footnotes_count || 0}</span>` : ''}
                <span class="badge ${stats.title_length <= 32 ? 'syndicate-stat-badge--green' : 'syndicate-stat-badge--amber'}">🏷️ 标题: ${stats.title_length || 0} 字</span>
            `;
        }

        window._previewViewport = window._previewViewport || 'auto';
        const isForceMobile = window._previewViewport === 'mobile';
        const isForceDesktop = window._previewViewport === 'desktop';
        const activeMobile = isForceMobile || (window._previewViewport === 'auto' && isMobile);

        if (actionsSlot) {
            actionsSlot.innerHTML = `
                <div class="syndicate-viewport-switcher">
                    <button type="button" class="syndicate-viewport-btn ${activeMobile ? 'is-active' : ''}" onclick="window._previewViewport='mobile';window.renderSyndicateCardPreview()">📱 手机</button>
                    <button type="button" class="syndicate-viewport-btn ${!activeMobile ? 'is-active' : ''}" onclick="window._previewViewport='desktop';window.renderSyndicateCardPreview()">💻 宽屏</button>
                </div>
                ${isWechat ? `<button type="button" class="syndicate-copy-wechat-btn glow-btn" onclick="window.copyWeChatRichText()">📋 复制公众号富文本</button>` : ''}
                <button type="button" class="syndicate-copy-markdown-btn" onclick="window.copyPlatformMarkdown()">📑 复制适配 Markdown</button>
            `;
        }

        const chassisWidth = activeMobile ? (isXhs ? '390px' : '440px') : '780px';
        const chassisClass = activeMobile ? 'preview-viewport-chassis--mobile' : 'preview-viewport-chassis--desktop';
        let displayHtml = (data.rendered_html || '').replace(/<h1[^>]*>[\s\S]*?<\/h1>/i, '').trim();

        // 🖼️ 动态模拟社交媒体信息流大图卡片与真机封面微调工作台
        const coverImgUrl = (window.currentSyndicateCover && window.currentSyndicateCover.url) || data.cover_url || '';
        const feedCardHtml = '<div id="syndicate-feed-card-slot" style="width:100%;"></div>';

        container.innerHTML = `
            <div class="preview-viewport-wrapper">
                ${compliance.platform_rules ? `<div class="syndicate-compliance-banner" style="width:${chassisWidth};">💡 <b>${target.toUpperCase()} 规则</b>：${_esc(compliance.platform_rules)}</div>` : ''}
                <div class="preview-viewport-chassis ${chassisClass}" style="width:${chassisWidth};">
                    ${activeMobile ? `<div class="preview-chassis-speaker"></div>` : ''}
                    ${feedCardHtml}
                    ${isWechat ? `
                    <div class="preview-wechat-header">
                        <h2 class="preview-wechat-title">${_esc(data.clean_title || data.title)}</h2>
                        <div class="preview-wechat-meta"><span class="preview-wechat-author">创作者文库</span><span>·</span><span>今天</span><span>·</span><span class="preview-wechat-origin-tag">原创</span></div>
                    </div>` : ''}
                    ${isXhs ? `
                    <div class="preview-xhs-header">
                        <div class="preview-xhs-badge">📕 小红书竖屏图文</div>
                        <h3 class="preview-xhs-title">${_esc(data.clean_title || data.title)}</h3>
                    </div>` : ''}
                    ${!isWechat && !isXhs ? `
                    <div class="preview-general-header">
                        <h1 class="preview-general-title">${_esc(data.clean_title || data.title)}</h1>
                        <div class="preview-general-meta">专栏预览模式 · ${target.toUpperCase()} 渠道自适应排版</div>
                    </div>` : ''}
                    <div class="preview-rendered-body" id="preview-rendered-body-slot">
                        ${displayHtml}
                    </div>
                    ${activeMobile ? `<div class="preview-chassis-home-bar"></div>` : ''}
                </div>
            </div>
        `;
        const fSlot = document.getElementById('syndicate-feed-card-slot');
        if (fSlot && typeof window.renderChannelCoverStudio === 'function') {
            window.renderChannelCoverStudio(target, fSlot, coverImgUrl);
        }
    };

    window.copyWeChatRichText = async function () {
        const html = window._currentRenderedHtml;
        if (!html) return;
        const notify = (typeof window.showToast === 'function') ? window.showToast : alert;
        try {
            if (navigator.clipboard && window.ClipboardItem) {
                const plainText = document.getElementById('preview-rendered-body-slot')?.innerText || html;
                await navigator.clipboard.write([new ClipboardItem({ 'text/html': new Blob([html], { type: 'text/html' }), 'text/plain': new Blob([plainText], { type: 'text/plain' }) })]);
            } else {
                const ta = document.createElement('textarea'); ta.value = html; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
            }
            notify('📋 公众号富文本已复制！可直接在公众号后台粘贴 (Cmd+V)', 'success');
        } catch (err) {
            notify('🛑 复制失败，请手动选取复制', 'error');
        }
    };

    window.copyPlatformMarkdown = async function () {
        const md = window._currentRenderedMarkdown;
        if (!md) return;
        const notify = (typeof window.showToast === 'function') ? window.showToast : alert;
        try {
            if (navigator.clipboard) await navigator.clipboard.writeText(md);
            notify('📑 渠道适配 Markdown 已复制！', 'success');
        } catch (err) {
            notify('🛑 复制失败', 'error');
        }
    };
})();

