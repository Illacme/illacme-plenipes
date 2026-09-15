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
            modalEl.style.cssText = 'position:fixed;inset:0;z-index:9999;background:rgba(4,6,12,0.88);backdrop-filter:blur(16px);display:flex;align-items:center;justify-content:center;padding:16px;';
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
            const opts = items.map(c => `<option value="${c.id}" ${c.id === initialTarget ? 'selected' : ''}>${c.icon} ${c.name}</option>`).join('');
            return `<optgroup label="── ${grp} ──">${opts}</optgroup>`;
        }).join('');

        modalEl.innerHTML = `
            <div class="syndicate-preview-modal-card glass-panel" style="width:1040px;max-width:96vw;height:92vh;max-height:880px;background:rgba(15,19,30,0.98);border:1px solid rgba(255,255,255,0.12);border-radius:18px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,0.75);">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 20px;border-bottom:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.02);gap:16px;flex-wrap:nowrap;">
                    <div style="display:flex;align-items:center;gap:10px;min-width:0;flex-shrink:1;">
                        <span style="font-size:1.3rem;flex-shrink:0;">👁️</span>
                        <div style="min-width:0;">
                            <div style="font-size:0.92rem;font-weight:700;color:#fff;white-space:nowrap;">全渠道高保真排版即时审查</div>
                            <div style="font-size:0.7rem;color:var(--text-dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:280px;">稿件：${_esc(title)}</div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
                        <div id="syndicate-modal-preview-tabs" style="display:flex;align-items:center;gap:4px;background:rgba(0,0,0,0.35);padding:3px 4px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);"></div>
                        <select id="syndicate-modal-channel-select" onchange="window.switchSyndicatePreviewTarget(this.value)" style="padding:5px 10px;font-size:0.74rem;background:rgba(0,242,254,0.08);color:#00f2fe;border:1px solid rgba(0,242,254,0.3);border-radius:7px;cursor:pointer;outline:none;font-weight:600;white-space:nowrap;">
                            <option value="" disabled>全矩阵拓展 ▾</option>
                            ${selectOptions}
                        </select>
                        <button type="button" onclick="window.closeSyndicateLivePreviewModal()" style="width:28px;height:28px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:var(--text-dim);font-size:1.2rem;cursor:pointer;line-height:1;margin-left:4px;" title="关闭 (Esc)">×</button>
                    </div>
                </div>
                <div id="syndicate-modal-toolbar-slot" style="display:flex;justify-content:space-between;align-items:center;padding:8px 20px;background:rgba(0,0,0,0.25);border-bottom:1px solid rgba(255,255,255,0.06);gap:10px;flex-wrap:nowrap;">
                    <div id="syndicate-modal-stats-capsule" style="display:flex;align-items:center;gap:8px;font-size:0.72rem;color:var(--text-dim);"><span>正在初始化合规分析...</span></div>
                    <div id="syndicate-modal-actions-slot" style="display:flex;align-items:center;gap:8px;flex-shrink:0;"></div>
                </div>
                <div id="syndicate-modal-body-container" style="flex:1;overflow-y:auto;padding:24px 20px;background:radial-gradient(circle at top, rgba(18,24,38,0.8), rgba(8,11,18,0.95));display:flex;justify-content:center;align-items:flex-start;">
                    <div id="syndicate-card-preview-renderer" style="width:100%;display:flex;justify-content:center;"></div>
                </div>
            </div>
        `;
        modalEl.style.display = 'flex';

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
            return `<button type="button" class="mini-btn ${isActive ? 'active' : ''}" onclick="window.switchSyndicatePreviewTarget('${tid}')" style="padding:4px 10px;font-size:0.72rem;border-radius:6px;border:none;cursor:pointer;white-space:nowrap;background:${isActive ? 'rgba(0,242,254,0.18)' : 'transparent'};color:${isActive ? '#00f2fe' : 'var(--text-dim)'};font-weight:${isActive ? '700' : '500'};border:${isActive ? '1px solid rgba(0,242,254,0.35)' : '1px solid transparent'};">${meta.icon} ${meta.name}</button>`;
        }).join('');
    };

    window.closeSyndicateLivePreviewModal = function () {
        const modalEl = document.getElementById('syndicate-live-preview-modal-root');
        if (modalEl) modalEl.style.display = 'none';
    };

    window.switchSyndicatePreviewTarget = function (target) {
        if (!target) return;
        window.currentSyndicatePreviewTarget = target;
        window.updatePreviewTabCapsules(target);
        const selectEl = document.getElementById('syndicate-modal-channel-select');
        if (selectEl) selectEl.value = target;
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

        container.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;padding:60px 0;color:var(--text-dim);gap:8px;"><span class="pulse-icon">⚙️</span><span style="font-size:0.82rem;">正在编译 ${target.toUpperCase()} 高保真排版...</span></div>`;

        const data = await window.fetchSyndicatePreviewData(relPath, target, selectedLang);
        if (!data) {
            container.innerHTML = `<div style="padding:40px;text-align:center;color:var(--text-dim);font-size:0.82rem;">⚠️ 暂未获取到稿件排版数据</div>`;
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
                <span class="badge" style="background:rgba(0,242,254,0.1);color:#00f2fe;border:1px solid rgba(0,242,254,0.25);">📊 约 ${stats.word_count || 0} 字</span>
                <span class="badge" style="background:rgba(255,255,255,0.05);color:var(--text-dim);">⏱️ 约 ${stats.reading_time_min || 1} 分钟</span>
                ${isWechat ? `<span class="badge" style="background:rgba(163,76,255,0.12);color:#c084fc;border:1px solid rgba(163,76,255,0.3);">🔗 脚注: ${stats.footnotes_count || 0}</span>` : ''}
                <span class="badge" style="background:${stats.title_length <= 32 ? 'rgba(74,222,128,0.12)' : 'rgba(255,183,0,0.12)'};color:${stats.title_length <= 32 ? '#4ade80' : '#ffb700'};">🏷️ 标题: ${stats.title_length || 0} 字</span>
            `;
        }

        window._previewViewport = window._previewViewport || 'auto';
        const isForceMobile = window._previewViewport === 'mobile';
        const isForceDesktop = window._previewViewport === 'desktop';
        const activeMobile = isForceMobile || (window._previewViewport === 'auto' && isMobile);

        if (actionsSlot) {
            actionsSlot.innerHTML = `
                <div style="display:flex;align-items:center;gap:2px;background:rgba(255,255,255,0.06);padding:2px 3px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);">
                    <button type="button" onclick="window._previewViewport='mobile';window.renderSyndicateCardPreview()" style="padding:3px 7px;font-size:0.68rem;border:none;border-radius:4px;cursor:pointer;background:${activeMobile ? 'rgba(0,242,254,0.22)' : 'transparent'};color:${activeMobile ? '#00f2fe' : '#aaa'};font-weight:${activeMobile ? '700' : '400'};">📱 手机</button>
                    <button type="button" onclick="window._previewViewport='desktop';window.renderSyndicateCardPreview()" style="padding:3px 7px;font-size:0.68rem;border:none;border-radius:4px;cursor:pointer;background:${!activeMobile ? 'rgba(0,242,254,0.22)' : 'transparent'};color:${!activeMobile ? '#00f2fe' : '#aaa'};font-weight:${!activeMobile ? '700' : '400'};">💻 宽屏</button>
                </div>
                ${isWechat ? `<button type="button" class="mini-btn glow-btn" onclick="window.copyWeChatRichText()" style="padding:5px 12px;font-size:0.74rem;font-weight:700;background:#07c160;color:#fff;border:none;border-radius:6px;cursor:pointer;">📋 复制公众号富文本</button>` : ''}
                <button type="button" class="mini-btn" onclick="window.copyPlatformMarkdown()" style="padding:5px 10px;font-size:0.74rem;border-radius:6px;background:rgba(255,255,255,0.08);color:#fff;border:1px solid rgba(255,255,255,0.15);cursor:pointer;">📑 复制适配 Markdown</button>
            `;
        }

        const chassisWidth = activeMobile ? (isXhs ? '390px' : '440px') : '780px';
        const chassisBg = '#ffffff';
        const chassisColor = '#1a1a1a';
        let displayHtml = (data.rendered_html || '').replace(/<h1[^>]*>[\s\S]*?<\/h1>/i, '').trim();

        // 🖼️ 动态模拟社交媒体信息流大图卡片与真机封面微调工作台
        const coverImgUrl = (window.currentSyndicateCover && window.currentSyndicateCover.url) || data.cover_url || '';
        const feedCardHtml = '<div id="syndicate-feed-card-slot" style="width:100%;"></div>';

        container.innerHTML = `
            <div style="display:flex;flex-direction:column;align-items:center;width:100%;gap:14px;">
                ${compliance.platform_rules ? `<div style="width:${chassisWidth};max-width:100%;font-size:0.72rem;color:var(--text-dim);background:rgba(255,255,255,0.03);padding:8px 14px;border-radius:8px;border-left:3px solid var(--accent-secondary,#00f2fe);">💡 <b>${target.toUpperCase()} 规则</b>：${_esc(compliance.platform_rules)}</div>` : ''}
                <div class="preview-viewport-chassis" style="width:${chassisWidth};max-width:100%;background:${chassisBg};color:${chassisColor};border-radius:${activeMobile ? '36px' : '14px'};padding:${activeMobile ? '22px 20px 28px' : '28px 36px 40px'};border:${activeMobile ? '8px solid #232838' : '1px solid rgba(255,255,255,0.1)'};box-shadow:${activeMobile ? '0 28px 70px rgba(0,0,0,0.65)' : '0 12px 40px rgba(0,0,0,0.35)'};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
                    ${activeMobile ? `<div style="width:70px;height:4px;background:#e5e7eb;border-radius:2px;margin:0 auto 16px;"></div>` : ''}
                    ${feedCardHtml}
                    ${isWechat ? `
                    <div style="margin-bottom:16px;border-bottom:1px solid #ebebeb;padding-bottom:12px;">
                        <h2 style="font-size:21px;font-weight:700;color:#111;line-height:1.4;margin:0 0 8px;">${_esc(data.clean_title || data.title)}</h2>
                        <div style="display:flex;align-items:center;gap:6px;font-size:13px;color:#888;"><span style="color:#576b95;font-weight:600;">创作者文库</span><span>·</span><span>今天</span><span>·</span><span style="background:rgba(0,0,0,0.06);padding:1px 5px;border-radius:3px;font-size:11px;">原创</span></div>
                    </div>` : ''}
                    ${isXhs ? `
                    <div style="margin-bottom:14px;border-bottom:1px solid #f2f2f2;padding-bottom:10px;">
                        <div style="font-size:12px;color:#ff2442;font-weight:700;margin-bottom:4px;">📕 小红书竖屏图文</div>
                        <h3 style="font-size:18px;font-weight:700;color:#111;margin:0;">${_esc(data.clean_title || data.title)}</h3>
                    </div>` : ''}
                    ${!isWechat && !isXhs ? `
                    <div style="margin-bottom:20px;border-bottom:1px solid #ebebeb;padding-bottom:14px;">
                        <h1 style="font-size:24px;font-weight:800;color:#111;line-height:1.4;margin:0 0 8px;">${_esc(data.clean_title || data.title)}</h1>
                        <div style="font-size:13px;color:#8590a6;">专栏预览模式 · ${target.toUpperCase()} 渠道自适应排版</div>
                    </div>` : ''}
                    <div class="preview-rendered-body" id="preview-rendered-body-slot" style="line-height:1.8;word-break:break-word;">
                        ${displayHtml}
                    </div>
                    ${activeMobile ? `<div style="width:110px;height:4px;background:#e5e7eb;border-radius:2px;margin:24px auto 0;"></div>` : ''}
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

