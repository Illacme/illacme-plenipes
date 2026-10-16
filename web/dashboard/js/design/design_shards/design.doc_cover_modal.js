/**
 * 🎨 [V1.1] Illacme Plenipes Design Studio - Document Cover Modal Shard
 * 职责：为指定文库原稿快速点选媒体资产作为封面、免跳转一键极速配图(OG/商用图库)、清除封面与直通生图工坊。
 * 🛡️ [SOP-01] 物理行数严格控制在 300 行以内。
 */
(function () {
    let _activeTargetDoc = null, _modalCurrentPage = 1, _modalPageSize = 12, _modalTotal = 0, _modalTotalPages = 1;

    const _quickCoverOffsets = {};

    window.closeDocCoverPickerModal = function () {
        const m = document.getElementById('doc-cover-picker-modal'); if (m) m.remove();
        if (typeof window.restoreGalaxyDirectorIfActive === 'function') window.restoreGalaxyDirectorIfActive();
    };

    window.openDocCoverPickerModal = async function (relPath, title, currentCover) {
        _activeTargetDoc = { relPath, title, currentCover: currentCover || '' };
        _modalCurrentPage = 1;
        const existing = document.getElementById('doc-cover-picker-modal'); if (existing) existing.remove();

        const safeTitle = (title || relPath || '未命名文档').replace(/'/g, "\\'");
        const hasCover = !!(currentCover && currentCover !== 'null' && currentCover !== 'undefined');
        const ogBtnText = hasCover ? '🃏 换一套 OG 配色' : '🃏 极速 OG 卡片';
        const stockBtnText = hasCover ? '📸 换一张商用图' : '📸 极速商用图库';

        const modalHtml = `
            <div id="doc-cover-picker-modal" class="modal-overlay active doc-cover-modal-backdrop" style="z-index:99999; display:flex; align-items:center; justify-content:center; position:fixed; inset:0;" onclick="if(event.target===this)window.closeDocCoverPickerModal()">
                <div class="glass-panel doc-cover-modal-card" style="width:860px; max-width:94vw; max-height:90vh; border-radius:14px; display:flex; flex-direction:column; overflow:hidden;" onclick="event.stopPropagation()">
                    <div class="doc-cover-modal-header" style="padding:14px 20px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.1rem;">🖼️</span>
                            <div>
                                <div class="doc-cover-modal-title" style="font-weight:700; font-size:0.95rem;">文章封面装帧与资产点选</div>
                                <div class="doc-cover-modal-sub" style="font-size:0.72rem; color:var(--text-dim); margin-top:2px;">正在为《<span style="color:var(--text-bright); font-weight:600;">${title || relPath}</span>》配置封面凭据</div>
                            </div>
                        </div>
                        <button type="button" class="mini-btn doc-cover-close-btn" style="padding:4px 8px; font-size:0.85rem;" onclick="window.closeDocCoverPickerModal()">✕</button>
                    </div>

                    <div class="doc-cover-status-bar" style="padding:10px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div style="display:flex; align-items:center; gap:8px;" id="doc-cover-status-bar">
                            <span style="font-size:0.75rem; color:var(--text-dim);">当前状态：</span>
                            ${hasCover ? `
                                <div style="display:flex; align-items:center; gap:8px;">
                                    <div class="skeleton-shimmer" style="width:50px; height:30px; border-radius:4px; overflow:hidden; border:1px solid rgba(0,242,254,0.45); cursor:pointer; flex-shrink:0;" onmouseenter="window.showVaultCoverHoverPreview(this, '${currentCover}', '当前封面: ${safeTitle}')" onmouseleave="window.hideVaultCoverHoverPreview()" onclick="window.openStudioImageModal('${currentCover}', '《${safeTitle}》当前封面', '当前封面', '16:9')">
                                        <img src="${currentCover}" style="width:100%; height:100%; object-fit:cover; display:block;" />
                                    </div>
                                    <span style="font-size:0.72rem; color:#10b981; font-weight:600;">已生效</span>
                                    <button type="button" class="mini-btn" style="padding:2px 8px; font-size:0.65rem; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.openStudioImageModal('${currentCover}', '《${safeTitle}》当前封面', '当前封面', '16:9')">🔍 查看</button>
                                    <button type="button" class="mini-btn" style="padding:2px 6px; font-size:0.65rem; color:#f87171; border-color:rgba(248,113,113,0.3);" onclick="window.removeDocCoverDirect()">移除</button>
                                </div>
                            ` : `<span style="font-size:0.72rem; color:#f59e0b;">暂无封面（分发将使用母本保底）</span>`}
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <button type="button" class="mini-btn glow-btn" style="padding:4px 10px; font-size:0.72rem; background:rgba(0,242,254,0.12); color:#00f2fe; border:1px solid rgba(0,242,254,0.35);" onclick="window.quickGenerateAndApplyCover('local_og', this)" title="切换 8 档赛博极光配色方案并毫秒级生成应用">${ogBtnText}</button>
                            <button type="button" class="mini-btn glow-btn" style="padding:4px 10px; font-size:0.72rem; background:rgba(167,139,250,0.12); color:#c084fc; border:1px solid rgba(167,139,250,0.35);" onclick="window.quickGenerateAndApplyCover('unsplash', this)" title="轮巡免Key商用摄影图库匹配全新主题照片">${stockBtnText}</button>
                            <button type="button" class="mini-btn glow-btn" style="padding:4px 10px; font-size:0.72rem; background:linear-gradient(135deg, rgba(0,242,254,0.2), rgba(0,255,136,0.2)); color:#fff; border:1px solid rgba(0,242,254,0.4);" onclick="window.jumpToStudioFromDocModal('${safeTitle}', '${relPath.replace(/'/g, "\\'")}')" title="前往工坊调试大模型、自选尺寸与Prompt">🪄 生图工坊</button>
                        </div>
                    </div>

                    <div class="doc-cover-grid-wrap" style="padding:16px 20px; overflow-y:auto; flex:1; min-height:280px;" id="doc-cover-assets-grid">
                        <div style="color:var(--text-dim); text-align:center; padding:40px 0; font-size:0.82rem;">正在加载媒体图库封面...</div>
                    </div>
                </div>
            </div>`;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        await window.loadDocCoverCandidates(1);
    };

    window.quickGenerateAndApplyCover = async function (providerId, btn) {
        const target = _activeTargetDoc || window._designTargetDoc; if (!target) return;
        const { relPath, title } = target, docTitle = title || relPath || '当前文章';
        const docKey = relPath || 'default';
        _quickCoverOffsets[docKey] = (_quickCoverOffsets[docKey] || 0) + 1;
        const offset = _quickCoverOffsets[docKey];
        const origText = btn ? btn.innerHTML : '';
        if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-gear">⚙️</span> 生成中...'; }
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            let prompt = docTitle;
            if (providerId === 'unsplash') {
                const en = (docTitle.match(/[a-zA-Z]{3,}/g) || []).filter(w => !/^(cinematic|render|hd)$/i.test(w));
                prompt = en.length ? en.slice(0, 2).join(' ') : (relPath.replace(/\.md$/, '').split('/').pop() || 'technology minimal');
            }
            const tip = providerId === 'local_og' ? `🎨 正在切换至第 ${(offset % 8) + 1} 档极光配色...` : `📸 正在轮巡探索第 ${offset} 款摄影大片...`;
            if (window.showToast) window.showToast(tip, 'info');
            const genRes = await fetchApi('/api/design/generate', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider_id: providerId, prompt, offset, aspect_ratio: '16:9', style: 'vivid' })
            });
            if (genRes && genRes.success && genRes.url) {
                await window.applyDocCoverDirect(genRes.url);
            } else throw new Error(genRes?.message || '生成失败');
        } catch (e) {
            if (window.showToast) window.showToast('🛑 极速配图失败: ' + e.message, 'error');
            if (btn) { btn.disabled = false; btn.innerHTML = origText; }
        }
    };

    window.loadDocCoverCandidates = async function (page = 1) {
        _modalCurrentPage = page;
        const grid = document.getElementById('doc-cover-assets-grid'); if (!grid) return;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            grid.innerHTML = '<div style="color:var(--text-dim); text-align:center; padding:40px 0; font-size:0.82rem;">正在加载第 ' + _modalCurrentPage + ' 页封面...</div>';
            const res = await fetchApi(`/api/design/assets?page=${_modalCurrentPage}&limit=${_modalPageSize}`);
            const assets = (res && res.assets) || [];
            _modalTotal = (res && typeof res.total === 'number') ? res.total : assets.length;
            _modalTotalPages = (res && typeof res.total_pages === 'number') ? res.total_pages : Math.max(1, Math.ceil(_modalTotal / _modalPageSize));
            _modalCurrentPage = (res && typeof res.page === 'number') ? res.page : _modalCurrentPage;

            if (assets.length === 0) {
                grid.innerHTML = `<div style="text-align:center; padding:50px 20px; color:var(--text-dim);"><div style="font-size:2.4rem; opacity:0.4; margin-bottom:10px;">🗃️</div><div style="font-size:0.88rem; margin-bottom:6px;">媒体图库暂无封面图片</div><div style="display:flex; justify-content:center; gap:8px; margin-top:10px;"><button type="button" class="mini-btn glow-btn" style="padding:6px 14px; font-size:0.76rem; color:#00f2fe;" onclick="window.quickGenerateAndApplyCover('local_og', this)">🃏 一键生成 OG 卡片</button><button type="button" class="mini-btn glow-btn" style="padding:6px 14px; font-size:0.76rem; color:#c084fc;" onclick="window.quickGenerateAndApplyCover('unsplash', this)">📸 一键匹配商用图库</button></div></div>`;
                return;
            }

            const paginationHtml = `
                <div class="doc-cover-pagination" style="display:flex; justify-content:space-between; align-items:center; padding-top:14px; margin-top:14px; font-size:0.72rem;">
                    <span style="color:var(--text-dim);">第 <strong style="color:var(--accent-secondary,#00f2fe);">${_modalCurrentPage}</strong> / ${_modalTotalPages} 页 (共 ${_modalTotal} 张封面)</span>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <button type="button" class="mini-btn" ${_modalCurrentPage <= 1 ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : `onclick="window.loadDocCoverCandidates(${_modalCurrentPage - 1})"`}>◀️ 上一页</button>
                        <button type="button" class="mini-btn" ${_modalCurrentPage >= _modalTotalPages ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : `onclick="window.loadDocCoverCandidates(${_modalCurrentPage + 1})"`}>下一页 ▶️</button>
                    </div>
                </div>`;

            grid.innerHTML = `
                <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                    <span>👇 点击图片即可设为封面，或点击右上角极速生成：</span><span>共 ${_modalTotal} 张可用封面</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:10px;">
                    ${assets.map(a => {
                const eng = (a.strategy || 'cover').replace(/^ai_/, '').toUpperCase();
                const isCurrent = Boolean(_activeTargetDoc && _activeTargetDoc.currentCover && _activeTargetDoc.currentCover === a.source_url);
                const escPrompt = (a.prompt || a.rel_path || '').replace(/'/g, "\\'");
                return `
                        <div class="glass-panel doc-cover-item" style="border-radius:8px; overflow:hidden; border:1px solid ${isCurrent ? '#00f2fe' : 'rgba(255,255,255,0.08)'}; cursor:pointer; position:relative; transition:all 0.2s;"
                             onmouseover="this.style.borderColor='#00f2fe'; this.style.transform='translateY(-2px)'"
                             onmouseout="this.style.borderColor='${isCurrent ? '#00f2fe' : 'rgba(255,255,255,0.08)'}'; this.style.transform='translateY(0)'"
                             onmouseenter="window.showVaultCoverHoverPreview(this, '${a.source_url}', '${escPrompt}')"
                             onmouseleave="window.hideVaultCoverHoverPreview()"
                             onclick="window.applyDocCoverDirect('${a.source_url}')">
                            <div class="skeleton-shimmer doc-cover-thumb-wrap" style="width:100%; height:96px; position:relative; overflow:hidden;">
                                <img src="${a.source_url}" loading="lazy" decoding="async" style="width:100%; height:100%; object-fit:cover; display:block;" />
                                <div style="position:absolute; top:4px; left:4px; font-size:0.6rem; color:#fff; background:rgba(0,0,0,0.65); padding:1px 6px; border-radius:3px;">${eng}</div>
                                ${isCurrent ? '<div style="position:absolute; top:4px; right:4px; font-size:0.6rem; background:#00f2fe; color:#000; font-weight:700; padding:1px 6px; border-radius:3px;">当前封面</div>' : ''}
                                <button type="button" class="mini-btn" title="查看高清大图与详情" style="position:absolute; right:4px; bottom:4px; font-size:0.62rem; padding:2px 6px; background:rgba(0,0,0,0.78); color:#00f2fe; border:1px solid rgba(0,242,254,0.4); border-radius:4px; cursor:pointer;" onclick="event.stopPropagation(); window.openStudioImageModal('${a.source_url}', '${escPrompt}', '${eng}', '16:9')">🔍 查看大图</button>
                            </div>
                            <div class="doc-cover-prompt-text" style="padding:6px 8px; font-size:0.68rem; color:var(--text-dim); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${a.prompt || a.rel_path || ''}">
                                ${a.prompt || a.rel_path || '默认封面模板'}
                            </div>
                        </div>`;
            }).join('')}
                </div>
                ${paginationHtml}`;
        } catch (e) { grid.innerHTML = '<div style="color:#f87171; text-align:center; padding:30px;">读取媒体资产库失败: ' + e.message + '</div>'; }
    };

    window.applyDocCoverDirect = async function (coverUrl) {
        const target = _activeTargetDoc || window._designTargetDoc; if (!target) return;
        const { relPath, title } = target;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/apply-cover', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: relPath, cover_url: coverUrl })
            });
            if (res && res.success) {
                if (typeof window.showToast === 'function') window.showToast(`✨ 已成功将图片应用为《${title || relPath}》的封面`, 'success');
                const modal = document.getElementById('doc-cover-picker-modal'); if (modal) modal.remove();
                if (typeof window.loadVault === 'function') window.loadVault(null, window.vaultCurrentPage || 1);
                if (window._designTargetDoc) {
                    window._designTargetDoc = null;
                    if (typeof window.renderStudioTargetBanner === 'function') window.renderStudioTargetBanner();
                }
            } else throw new Error(res?.message || '应用封面失败');
        } catch (e) { if (typeof window.showToast === 'function') window.showToast(`🛑 设为封面失败: ${e.message}`, 'error'); }
    };

    window.clearDocCover = async function (relPath) {
        if (typeof window.confirmSovereignAction === 'function') {
            const ok = await window.confirmSovereignAction({
                title: '🗑️ 清空文章封面', text: '确定要清空该文章的封面设置吗？<br>清空后将从原稿 Frontmatter 中移除 cover 属性。',
                icon: 'warning', confirmText: '确定清空', confirmColor: '#ff4d4f'
            });
            if (!ok) return;
        } else if (!confirm('确定要清空该文章的封面设置吗？\n清空后将移除原稿 Frontmatter 中的 cover 属性。')) return;

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/apply-cover', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: relPath, cover_url: '' })
            });
            if (res && res.success) {
                if (typeof window.showToast === 'function') window.showToast('🗑️ 封面已成功清空', 'success');
                const modal = document.getElementById('doc-cover-picker-modal'); if (modal) modal.remove();
                if (typeof window.loadVault === 'function') window.loadVault(null, window.vaultCurrentPage || 1);
            }
        } catch (e) { if (typeof window.showToast === 'function') window.showToast(`🛑 清除失败: ${e.message}`, 'error'); }
    };
    window.removeDocCoverDirect = () => window.clearDocCover(_activeTargetDoc?.relPath);

    window.jumpToStudioFromDocModal = async function (title, relPath, fromSyndicate = false) {
        const targetDoc = { title: title || _activeTargetDoc?.title || '', relPath: relPath || _activeTargetDoc?.relPath || '', fromSyndicate: !!fromSyndicate, fromVaultModal: !fromSyndicate };
        window._designTargetDoc = targetDoc;
        const modal = document.getElementById('doc-cover-picker-modal'); if (modal) modal.remove();
        if (typeof window.showView === 'function') await window.showView('design'); else window.location.hash = '#/design';
        if (typeof window.switchDesignSubTab === 'function') window.switchDesignSubTab('workspace');
        let attempts = 0;
        const checkAndFill = () => {
            if (typeof window.fillTargetDocPrompt === 'function' && document.getElementById('studio-prompt-input')) {
                window.fillTargetDocPrompt();
            } else if (attempts < 20) { attempts++; setTimeout(checkAndFill, 50); }
        };
        setTimeout(checkAndFill, 60);
    };

    window.openStudioImageModal = function (url, prompt, provider, ratio) {
        const old = document.getElementById('studio-image-detail-modal'); if (old) old.remove();
        const safeUrl = url || '', safePrompt = (prompt || '').replace(/"/g, '&quot;'), safeProvider = provider || '视觉引擎', safeRatio = ratio || '16:9';
        const activeDoc = _activeTargetDoc || window._designTargetDoc;
        const targetBtn = activeDoc ? `<button type="button" class="mini-btn glow-btn" style="padding:6px 14px; font-size:0.75rem; background:var(--accent-secondary,#00f2fe); color:#000; font-weight:700; border:none; border-radius:6px; cursor:pointer;" onclick="window.applyDocCoverDirect('${safeUrl}'); const m=document.getElementById('studio-image-detail-modal'); if(m)m.remove();">🎯 一键设为《${activeDoc.title || '当前文章'}》封面</button>` : '';

        const modalHtml = `
            <div id="studio-image-detail-modal" class="modal-overlay active studio-detail-modal-backdrop" style="z-index:100002; display:flex; align-items:center; justify-content:center; position:fixed; inset:0; padding:16px;" onclick="if(event.target===this)this.remove()">
                <div class="glass-panel studio-detail-modal-card" style="max-width:92vw; max-height:92vh; border-radius:14px; display:flex; flex-direction:column; overflow:hidden;" onclick="event.stopPropagation()">
                    <div class="studio-detail-modal-header" style="padding:12px 18px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:1.1rem;">🔍</span>
                            <span class="studio-detail-modal-title" style="font-weight:700; font-size:0.92rem;">封面高清大图预览</span>
                            <span style="font-size:0.68rem; color:#00f2fe; background:rgba(0,242,254,0.12); padding:1px 6px; border-radius:4px; border:1px solid rgba(0,242,254,0.25);">${safeProvider} · ${safeRatio}</span>
                        </div>
                        <button type="button" class="mini-btn" style="padding:4px 8px; font-size:0.8rem;" onclick="document.getElementById('studio-image-detail-modal').remove()">✕</button>
                    </div>
                    <div class="studio-detail-modal-body" style="flex:1; overflow:auto; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:16px; min-height:220px;">
                        <img src="${safeUrl}" alt="高清大图" style="max-width:86vw; max-height:64vh; object-fit:contain; border-radius:8px; box-shadow:0 12px 35px rgba(0,0,0,0.7); border:1px solid rgba(255,255,255,0.1);" />
                    </div>
                    <div class="studio-detail-modal-footer" style="padding:12px 18px; display:flex; flex-direction:column; gap:10px;">
                        ${safePrompt ? `<div style="font-size:0.75rem; color:var(--text-dim); display:flex; gap:8px; align-items:center; line-height:1.4;"><span class="studio-detail-prompt-label" style="color:#00f2fe; flex-shrink:0;">💬 提示词:</span><span class="studio-detail-prompt-text" style="color:#e2e8f0; word-break:break-all; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${safePrompt}">${safePrompt}</span><button type="button" class="mini-btn" style="font-size:0.68rem; padding:2px 8px; flex-shrink:0;" onclick="navigator.clipboard.writeText('${safePrompt}').then(()=>window.showToast&&window.showToast('📋 提示词已复制','success'))">复制词</button></div>` : ''}
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                                ${activeDoc ? targetBtn : `<button type="button" class="mini-btn" style="font-size:0.74rem; padding:5px 12px; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.openAssetApplyCoverModal('${safeUrl}'); const m=document.getElementById('studio-image-detail-modal'); if(m)m.remove();">🖼️ 设为文章封面</button>`}
                                <button type="button" class="mini-btn" style="font-size:0.74rem; padding:5px 12px; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.copyStudioResultMarkdown('${safeUrl}')">📋 复制 Markdown</button>
                                <button type="button" class="mini-btn" style="font-size:0.74rem; padding:5px 12px; color:#38bdf8; border-color:rgba(56,189,248,0.4);" onclick="window.openAssetHostingModal(null, '${safeUrl}'); const m=document.getElementById('studio-image-detail-modal'); if(m)m.remove();">☁️ 托管图床</button>
                                <a href="${safeUrl}" download class="mini-btn" style="font-size:0.74rem; padding:5px 12px; text-decoration:none;">⬇️ 下载原图</a>
                            </div>
                            <button type="button" class="mini-btn" style="padding:5px 14px; font-size:0.74rem;" onclick="document.getElementById('studio-image-detail-modal').remove()">关闭</button>
                        </div>
                    </div>
                </div>
            </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    };
})();