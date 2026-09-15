/**
 * 🎨 [V1.0] Illacme Plenipes Design Studio - Document Cover Modal Shard
 * 职责：为指定文库原稿快速点选媒体资产作为封面、清除封面、以及直通智能生图创作。
 * 🛡️ [SOP-01] 物理行数严格控制在 300 行以内。
 */

(function () {
    let _activeTargetDoc = null;
    let _modalCurrentPage = 1;
    let _modalPageSize = 18;
    let _modalTotal = 0;
    let _modalTotalPages = 1;

    window.openDocCoverPickerModal = async function (relPath, title, currentCover) {
        _activeTargetDoc = { relPath, title, currentCover: currentCover || '' };
        _modalCurrentPage = 1;
        
        // 移除已存在的弹层
        const existing = document.getElementById('doc-cover-picker-modal');
        if (existing) existing.remove();

        const safeTitle = (title || relPath || '未命名文档').replace(/'/g, "\\'");
        const hasCover = !!(currentCover && currentCover !== 'null' && currentCover !== 'undefined');

        const modalHtml = `
            <div id="doc-cover-picker-modal" class="modal-overlay active" style="z-index:99999; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.8); backdrop-filter:blur(8px); position:fixed; inset:0;" onclick="if(event.target===this)this.remove()">
                <div class="glass-panel" style="width:840px; max-width:94vw; max-height:90vh; border-radius:14px; border:1px solid rgba(0,242,254,0.35); display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,0.85); background:#0b0f19;" onclick="event.stopPropagation()">
                    <!-- 顶栏：目标原稿与操作动作 -->
                    <div style="padding:16px 22px; border-bottom:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center; background:rgba(0,242,254,0.03);">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.1rem;">🖼️</span>
                            <div>
                                <div style="font-weight:700; color:#fff; font-size:0.95rem;">挑选视觉物权资产为封面</div>
                                <div style="font-size:0.72rem; color:var(--text-dim); margin-top:2px;">
                                    正在为：<span style="color:var(--text-bright); font-weight:600;">${title || relPath}</span> 设置专属封面
                                </div>
                            </div>
                        </div>
                        <div style="display:flex; gap:8px; align-items:center;">
                            <button type="button" class="mini-btn" style="padding:4px 8px; font-size:0.85rem;" onclick="document.getElementById('doc-cover-picker-modal').remove()">✕</button>
                        </div>
                    </div>

                    <!-- 当前封面展示与重置栏 -->
                    <div style="padding:10px 22px; background:rgba(255,255,255,0.02); border-bottom:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:8px;" id="doc-cover-status-bar">
                            <span style="font-size:0.75rem; color:var(--text-dim);">当前状态：</span>
                            ${hasCover ? `
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <img src="${currentCover}" style="width:48px; height:28px; object-fit:cover; border-radius:4px; border:1px solid rgba(0,242,254,0.4);" />
                                    <span style="font-size:0.72rem; color:#10b981;">已配置封面</span>
                                    <button type="button" class="mini-btn" style="padding:2px 6px; font-size:0.65rem; color:#f87171; border-color:rgba(248,113,113,0.3);" onclick="window.removeDocCoverDirect()">清空解绑</button>
                                </div>
                            ` : `<span style="font-size:0.72rem; color:#f59e0b;">未配置封面 (将在分发时使用系统默认模板)</span>`}
                        </div>
                        <button type="button" class="mini-btn glow-btn" style="padding:4px 12px; font-size:0.74rem; background:rgba(0,242,254,0.15); border-color:rgba(0,242,254,0.4); color:#00f2fe;" onclick="window.jumpToStudioFromDocModal('${safeTitle}', '${relPath.replace(/'/g, "\\'")}')">
                            🪄 智能生成新图
                        </button>
                    </div>

                    <!-- 资产网格选择区 -->
                    <div style="padding:18px 22px; overflow-y:auto; flex:1; min-height:280px;" id="doc-cover-assets-grid">
                        <div style="color:var(--text-dim); text-align:center; padding:40px 0; font-size:0.82rem;">正在加载媒体资产候选库...</div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        await window.loadDocCoverCandidates(1);
    };

    window.loadDocCoverCandidates = async function (page = 1) {
        _modalCurrentPage = page;
        const grid = document.getElementById('doc-cover-assets-grid');
        if (!grid) return;

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            grid.innerHTML = '<div style="color:var(--text-dim); text-align:center; padding:40px 0; font-size:0.82rem;">正在加载第 ' + _modalCurrentPage + ' 页资产...</div>';
            const res = await fetchApi(`/api/design/assets?page=${_modalCurrentPage}&limit=${_modalPageSize}`);
            const assets = (res && res.assets) || [];
            _modalTotal = (res && typeof res.total === 'number') ? res.total : assets.length;
            _modalTotalPages = (res && typeof res.total_pages === 'number') ? res.total_pages : Math.max(1, Math.ceil(_modalTotal / _modalPageSize));
            _modalCurrentPage = (res && typeof res.page === 'number') ? res.page : _modalCurrentPage;

            if (assets.length === 0) {
                grid.innerHTML = `
                    <div style="text-align:center; padding:50px 20px; color:var(--text-dim);">
                        <div style="font-size:2.4rem; opacity:0.4; margin-bottom:10px;">🗃️</div>
                        <div style="font-size:0.88rem; margin-bottom:6px;">媒体资产库暂无图片</div>
                        <button type="button" class="mini-btn" style="padding:6px 14px; font-size:0.76rem; color:#00f2fe; margin-top:8px;" onclick="window.jumpToStudioFromDocModal('${(_activeTargetDoc?.title || '').replace(/'/g, "\\'")}', '${(_activeTargetDoc?.relPath || '').replace(/'/g, "\\'")}')">
                            🪄 立即前往「智能生图」为本文生成一张
                        </button>
                    </div>
                `;
                return;
            }

            const paginationHtml = `
                <div style="display:flex; justify-content:space-between; align-items:center; padding-top:14px; margin-top:14px; border-top:1px solid rgba(255,255,255,0.06); font-size:0.72rem;">
                    <span style="color:var(--text-dim);">第 <strong style="color:#00f2fe;">${_modalCurrentPage}</strong> / ${_modalTotalPages} 页 (共 ${_modalTotal} 项资产)</span>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <button type="button" class="mini-btn" ${_modalCurrentPage <= 1 ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : `onclick="window.loadDocCoverCandidates(${_modalCurrentPage - 1})"`}>◀️ 上一页</button>
                        <button type="button" class="mini-btn" ${_modalCurrentPage >= _modalTotalPages ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : `onclick="window.loadDocCoverCandidates(${_modalCurrentPage + 1})"`}>下一页 ▶️</button>
                    </div>
                </div>
            `;

            grid.innerHTML = `
                <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                    <span>👇 点击下方任意图片，即可一键设为当前文章封面：</span>
                    <span>候选资产共 ${_modalTotal} 张</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:12px;">
                    ${assets.map(a => {
                        const eng = (a.strategy || 'cover').replace(/^ai_/, '').toUpperCase();
                        const isCurrent = _activeTargetDoc && _activeTargetDoc.currentCover === a.source_url;
                        return `
                        <div class="glass-panel doc-cover-item" style="border-radius:8px; overflow:hidden; border:1px solid ${isCurrent ? '#00f2fe' : 'rgba(255,255,255,0.08)'}; cursor:pointer; position:relative; transition:all 0.2s;"
                             onmouseover="this.style.borderColor='#00f2fe'; this.style.transform='translateY(-2px)'"
                             onmouseout="this.style.borderColor='${isCurrent ? '#00f2fe' : 'rgba(255,255,255,0.08)'}'; this.style.transform='translateY(0)'"
                             onclick="window.applyDocCoverDirect('${a.source_url}')">
                            <div class="skeleton-shimmer" style="width:100%; height:110px; background:#05070f; position:relative; overflow:hidden;">
                                <img src="${a.source_url}" loading="lazy" decoding="async" style="width:100%; height:100%; object-fit:cover; display:block;" />
                                <div style="position:absolute; top:4px; left:4px; font-size:0.6rem; color:#fff; background:rgba(0,0,0,0.65); padding:1px 6px; border-radius:3px;">
                                    ${eng}
                                </div>
                                ${isCurrent ? `<div style="position:absolute; top:4px; right:4px; font-size:0.6rem; background:#00f2fe; color:#000; font-weight:700; padding:1px 6px; border-radius:3px;">当前封面</div>` : ''}
                            </div>
                            <div style="padding:6px 8px; font-size:0.68rem; color:var(--text-dim); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${a.prompt || a.rel_path || ''}">
                                ${a.prompt || a.rel_path || '默认封面模板'}
                            </div>
                        </div>`;
                    }).join('')}
                </div>
                ${paginationHtml}
            `;
        } catch (e) {
            grid.innerHTML = `<div style="color:#f87171; text-align:center; padding:30px;">读取媒体资产库失败: ${e.message}</div>`;
        }
    };

    window.applyDocCoverDirect = async function (coverUrl) {
        if (!_activeTargetDoc) return;
        const { relPath, title } = _activeTargetDoc;

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/apply-cover', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: relPath, cover_url: coverUrl })
            });

            if (res && res.success) {
                if (typeof window.showToast === 'function') {
                    window.showToast(`✨ 已成功将图片应用为《${title || relPath}》的封面`, 'success');
                }
                const modal = document.getElementById('doc-cover-picker-modal');
                if (modal) modal.remove();

                if (typeof window.loadVault === 'function') {
                    window.loadVault(null, window.vaultCurrentPage || 1);
                }
            } else {
                throw new Error((res && res.message) || '应用封面失败');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 设为封面失败: ${e.message}`, 'error');
        }
    };

    window.clearDocCover = async function (relPath) {
        if (!confirm('确定要清空该文章的封面设置吗？\n清空后将移除原稿 Frontmatter 中的 cover 属性。')) return;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/apply-cover', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: relPath, cover_url: '' })
            });
            if (res && res.success) {
                if (typeof window.showToast === 'function') window.showToast('🗑️ 封面已成功清空', 'success');
                const modal = document.getElementById('doc-cover-picker-modal');
                if (modal) modal.remove();
                if (typeof window.loadVault === 'function') {
                    window.loadVault(null, window.vaultCurrentPage || 1);
                }
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 清除失败: ${e.message}`, 'error');
        }
    };

    window.jumpToStudioFromDocModal = async function (title, relPath, fromSyndicate = false) {
        const targetDoc = {
            title: title || _activeTargetDoc?.title || '',
            relPath: relPath || _activeTargetDoc?.relPath || '',
            fromSyndicate: !!fromSyndicate
        };
        window._designTargetDoc = targetDoc;

        const modal = document.getElementById('doc-cover-picker-modal');
        if (modal) modal.remove();

        if (typeof window.showView === 'function') {
            await window.showView('design');
        } else {
            window.location.hash = '#/design';
        }

        if (typeof window.switchDesignSubTab === 'function') {
            window.switchDesignSubTab('workspace');
        }

        let attempts = 0;
        const checkAndFill = () => {
            const ipt = document.getElementById('studio-prompt-input');
            if (ipt) {
                const docTitle = targetDoc.title || '当前文章';
                ipt.value = `为文章《${docTitle}》创作科技现代风格封面，视觉震撼，极简光影，高分辨率，富有未来感`;
                ipt.dispatchEvent(new Event('input', { bubbles: true }));
                ipt.focus();
                if (typeof window.showToast === 'function') {
                    window.showToast(`✨ 已为您准备好《${docTitle}》的生图意境提示词`, 'success');
                }
            } else if (attempts < 20) {
                attempts++;
                setTimeout(checkAndFill, 50);
            }
        };
        setTimeout(checkAndFill, 60);
    };

    window.openStudioImageModal = function (url, prompt, provider, ratio) {
        const old = document.getElementById('studio-image-detail-modal');
        if (old) old.remove();

        const safeUrl = url || '';
        const safePrompt = (prompt || '').replace(/"/g, '&quot;');
        const safeProvider = provider || '视觉引擎';
        const safeRatio = ratio || '16:9';

        const targetBtn = window._designTargetDoc ? `
            <button type="button" class="mini-btn glow-btn" style="padding:6px 14px; font-size:0.75rem; background:var(--accent-secondary,#00f2fe); color:#000; font-weight:700; border:none; border-radius:6px; cursor:pointer;" onclick="window.applyTargetDocCover('${safeUrl}'); const m=document.getElementById('studio-image-detail-modal'); if(m)m.remove();">
                🎯 一键设为《${window._designTargetDoc.title || '当前文章'}》封面
            </button>
        ` : '';

        const modalHtml = `
            <div id="studio-image-detail-modal" class="modal-overlay active" style="z-index:100002; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.85); backdrop-filter:blur(12px); position:fixed; inset:0; padding:16px;" onclick="if(event.target===this)this.remove()">
                <div class="glass-panel" style="max-width:92vw; max-height:92vh; border-radius:14px; border:1px solid rgba(0,242,254,0.35); display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,0.95); background:#0c1017;" onclick="event.stopPropagation()">
                    <div style="padding:12px 18px; border-bottom:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.02);">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:1.1rem;">🔍</span>
                            <span style="font-weight:700; color:#fff; font-size:0.92rem;">图像高清检视与物权详情</span>
                            <span style="font-size:0.68rem; color:#00f2fe; background:rgba(0,242,254,0.12); padding:1px 6px; border-radius:4px; border:1px solid rgba(0,242,254,0.25);">${safeProvider} · ${safeRatio}</span>
                        </div>
                        <button type="button" class="mini-btn" style="padding:4px 8px; font-size:0.8rem;" onclick="document.getElementById('studio-image-detail-modal').remove()">✕</button>
                    </div>
                    <div style="flex:1; overflow:auto; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:16px; min-height:220px; background:radial-gradient(circle at 50% 50%, rgba(0,242,254,0.05), transparent 70%);">
                        <img src="${safeUrl}" alt="高清大图" style="max-width:86vw; max-height:64vh; object-fit:contain; border-radius:8px; box-shadow:0 12px 35px rgba(0,0,0,0.7); border:1px solid rgba(255,255,255,0.1);" />
                    </div>
                    <div style="padding:12px 18px; border-top:1px solid rgba(255,255,255,0.08); background:rgba(0,0,0,0.35); display:flex; flex-direction:column; gap:10px;">
                        ${safePrompt ? `
                        <div style="font-size:0.75rem; color:var(--text-dim); display:flex; gap:8px; align-items:center; line-height:1.4;">
                            <span style="color:#00f2fe; flex-shrink:0;">💬 提示词:</span>
                            <span style="color:#e2e8f0; word-break:break-all; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${safePrompt}">${safePrompt}</span>
                            <button type="button" class="mini-btn" style="font-size:0.68rem; padding:2px 8px; flex-shrink:0;" onclick="navigator.clipboard.writeText('${safePrompt}').then(()=>window.showToast&&window.showToast('📋 提示词已复制','success'))">复制词</button>
                        </div>` : ''}
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                                ${targetBtn}
                                <button type="button" class="mini-btn" style="font-size:0.74rem; padding:5px 12px; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.openAssetApplyCoverModal('${safeUrl}'); const m=document.getElementById('studio-image-detail-modal'); if(m)m.remove();">🖼️ 设为文章封面</button>
                                <button type="button" class="mini-btn" style="font-size:0.74rem; padding:5px 12px; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.copyStudioResultMarkdown('${safeUrl}')">📋 复制 Markdown</button>
                                <button type="button" class="mini-btn" style="font-size:0.74rem; padding:5px 12px; color:#38bdf8; border-color:rgba(56,189,248,0.4);" onclick="window.openAssetHostingModal(null, '${safeUrl}'); const m=document.getElementById('studio-image-detail-modal'); if(m)m.remove();">☁️ 托管图床</button>
                                <a href="${safeUrl}" download class="mini-btn" style="font-size:0.74rem; padding:5px 12px; text-decoration:none;">⬇️ 下载原图</a>
                            </div>
                            <button type="button" class="mini-btn" style="padding:5px 14px; font-size:0.74rem;" onclick="document.getElementById('studio-image-detail-modal').remove()">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    };
})();
