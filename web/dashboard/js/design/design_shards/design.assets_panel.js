// -*- coding: utf-8 -*-
/**
 * 🎨 [V1.0] Illacme Plenipes Design Studio - Visual Assets Panel Shard
 * 职责：媒体资产检索过滤、渠道归一、批量管理多选删除与解绑、详情弹层与托管。
 * 🛡️ [SOP-01] 物理行数严格控制在 300 行以内。
 * 🛡️ [SOP-03] 商业级暗黑毛玻璃视觉主权。
 */

(function () {
    let _assetsList = [];
    let _activeFilter = 'all';
    let _statusFilter = 'all';
    let _isBatchManaging = false;
    let _batchSelectedIds = new Set();
    let _currentPage = 1;
    let _pageSize = 24;
    let _totalAssets = 0;
    let _totalPages = 1;

    const normalizeEngine = (strat) => {
        const clean = (strat || '').replace(/^ai_/, '').toLowerCase();
        return (clean === 'local_og' || clean === 'og_card' || clean === 'og') ? 'og_card' : clean;
    };

    window.loadAndRenderDesignAssets = async function (root, page = null) {
        if (page !== null) _currentPage = page;
        if (!root) root = document.getElementById('design-center-root');
        if (root) root.innerHTML = '<div style="color:var(--text-dim); padding:30px; text-align:center;">正在读取媒体资产库...</div>';
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const provParam = _activeFilter !== 'all' ? `&provider=${encodeURIComponent(_activeFilter)}` : '';
            const res = await fetchApi(`/api/design/assets?page=${_currentPage}&limit=${_pageSize}${provParam}`);
            _assetsList = (res && res.assets) || [];
            window._designAssetsList = _assetsList;
            _totalAssets = (res && typeof res.total === 'number') ? res.total : _assetsList.length;
            _totalPages = (res && typeof res.total_pages === 'number') ? res.total_pages : Math.max(1, Math.ceil(_totalAssets / _pageSize));
            _currentPage = (res && typeof res.page === 'number') ? res.page : _currentPage;
            _batchSelectedIds.clear();
            window.renderAssetsGrid(root);
        } catch (e) {
            if (root) root.innerHTML = `<div style="color:#f87171; padding:20px; text-align:center;">读取资产记录失败: ${e.message}</div>`;
        }
    };

    window.renderAssetsGrid = function (root) {
        if (!root) root = document.getElementById('design-center-root');
        if (!root) return;

        const usedCount = _assetsList.filter(a => (a.reference_count || (a.references && a.references.length) || 0) > 0).length;
        const idleCount = _assetsList.length - usedCount;

        const filtered = _assetsList.filter(a => {
            const refCount = a.reference_count || (a.references && a.references.length) || 0;
            return _statusFilter === 'all' || (_statusFilter === 'used' ? refCount > 0 : refCount === 0);
        });

        const engines = Array.from(new Set(_assetsList.map(a => normalizeEngine(a.strategy)))).filter(Boolean);

        const renderCdnBadge = (url) => {
            if (!url) return '';
            let label = url.includes('r2') ? '🟧 R2' : (url.includes('catbox') ? '🐱 Catbox' : (url.includes('github') ? '🐙 GitHub' : '☁️ CDN'));
            return `<div style="position:absolute; top:8px; left:80px; font-size:0.65rem; color:#38bdf8; background:rgba(56,189,248,0.2); backdrop-filter:blur(4px); padding:2px 6px; border-radius:4px; border:1px solid rgba(56,189,248,0.4); font-weight:600; cursor:pointer;" onclick="event.stopPropagation(); navigator.clipboard.writeText('${url}'); if(window.showToast) window.showToast('📋 已复制 ${label} 直链', 'success');" title="点击复制 CDN 直链">${label} 📋</div>`;
        };

        const batchBarHtml = _isBatchManaging ? `
            <div style="display:flex; align-items:center; gap:8px; background:rgba(0,242,254,0.06); padding:4px 10px; border-radius:6px; border:1px solid rgba(0,242,254,0.25); font-size:0.72rem;">
                <span style="color:var(--text-bright);">已选 <strong style="color:var(--accent-secondary);" id="batch-selected-num">${_batchSelectedIds.size}</strong> 项</span>
                <button type="button" class="mini-btn" style="padding:2px 7px; font-size:0.68rem;" onclick="window.toggleSelectAllFilteredAssets(true)">全选</button>
                <button type="button" class="mini-btn" style="padding:2px 7px; font-size:0.68rem;" onclick="window.toggleSelectAllFilteredAssets(false)">清空</button>
                <button type="button" class="mini-btn" style="padding:2px 9px; font-size:0.68rem; color:#f87171; border-color:rgba(248,113,113,0.35); background:rgba(248,113,113,0.1);" onclick="window.executeBatchDeleteAssets()">🗑️ 批量删除 (${_batchSelectedIds.size})</button>
            </div>
        ` : '';

        let filterHtml = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                    <div style="font-size:0.8rem; color:var(--text-dim); display:flex; align-items:center; gap:6px;">
                        <span>🗃️</span><span>共收录 <strong style="color:var(--accent-secondary);">${_totalAssets}</strong> 项媒体资产</span>
                    </div>
                    <button type="button" class="mini-btn glow-btn" style="padding:3px 10px; font-size:0.7rem; color:#000; background:var(--accent-secondary,#00f2fe); border:none; border-radius:4px; font-weight:700;" onclick="window.openAssetUploadModal()">📤 上传图片</button>
                    <button type="button" class="mini-btn" style="padding:3px 10px; font-size:0.7rem; color:#00f2fe; border-color:rgba(0,242,254,0.35); background:rgba(0,242,254,0.08); border-radius:4px;" onclick="window.openBatchCoverModal()">⚡ 批量配图</button>
                    <button type="button" class="mini-btn" style="padding:3px 10px; font-size:0.7rem; color:#10b981; border-color:rgba(16,185,129,0.35); background:rgba(16,185,129,0.08); border-radius:4px;" onclick="window.healMissingCovers()" title="一键扫描并自愈补齐磁盘缺失的封面图片">🩹 自愈缺失封面</button>
                    <button type="button" class="mini-btn ${_isBatchManaging ? 'active' : ''}" style="padding:3px 10px; font-size:0.7rem; color:${_isBatchManaging ? '#00f2fe' : 'var(--text-dim)'}; border-color:${_isBatchManaging ? 'rgba(0,242,254,0.4)' : 'rgba(255,255,255,0.12)'}; background:${_isBatchManaging ? 'rgba(0,242,254,0.12)' : 'transparent'}; border-radius:4px;" onclick="window.toggleAssetBatchMode()">
                        ${_isBatchManaging ? '✕ 退出管理' : '☑️ 批量管理'}
                    </button>
                    ${batchBarHtml}
                    ${idleCount > 0 && !_isBatchManaging ? `<button type="button" class="mini-btn" style="padding:3px 9px; font-size:0.7rem; color:#f87171; border-color:rgba(248,113,113,0.3); background:rgba(248,113,113,0.08); border-radius:4px;" onclick="window.cleanupIdleVisualAssets()">🧹 清理闲置 (${idleCount})</button>` : ''}
                </div>
                <div style="display:flex; gap:8px; align-items:center; flex-shrink:0;">
                    <div style="display:flex; gap:3px; align-items:center; background:rgba(255,255,255,0.03); padding:2px 4px; border-radius:6px; border:1px solid rgba(255,255,255,0.08);">
                        <button type="button" class="mini-btn ${_statusFilter === 'all' ? 'active' : ''}" style="padding:3px 9px; font-size:0.7rem;" onclick="window.filterAssetsStatus('all')">全部</button>
                        <button type="button" class="mini-btn ${_statusFilter === 'used' ? 'active' : ''}" style="padding:3px 9px; font-size:0.7rem; color:${_statusFilter==='used'?'#10b981':'var(--text-dim)'};" onclick="window.filterAssetsStatus('used')">🔗 在用</button>
                        <button type="button" class="mini-btn ${_statusFilter === 'idle' ? 'active' : ''}" style="padding:3px 9px; font-size:0.7rem; color:${_statusFilter==='idle'?'#f59e0b':'var(--text-dim)'};" onclick="window.filterAssetsStatus('idle')">⭕ 闲置</button>
                    </div>
                    <select class="studio-select assets-engine-select" style="width:auto !important; min-width:125px; padding:2px 8px; font-size:0.7rem; height:26px; border-radius:6px; cursor:pointer;" onchange="window.filterAssetsEngine(this.value)">
                        <option value="all" ${_activeFilter === 'all' ? 'selected' : ''}>⚙️ 引擎: 全部</option>
                        ${engines.map(eng => `<option value="${eng}" ${_activeFilter === eng ? 'selected' : ''}>${eng === 'og_card' ? '🎨 OG 技术卡片' : '⚙️ ' + eng.toUpperCase()}</option>`).join('')}
                    </select>
                </div>
            </div>
        `;

        if (filtered.length === 0) {
            root.innerHTML = filterHtml + `<div class="glass-panel" style="padding:60px 20px; text-align:center; color:var(--text-dim); border-radius:12px; border:1px solid rgba(255,255,255,0.06);"><div style="font-size:2.6rem; opacity:0.4; margin-bottom:12px;">🗃️</div><div>暂无符合条件的媒体资产</div></div>`;
            return;
        }

        const paginationHtml = `
            <div class="pagination-container" style="display:flex; justify-content:space-between; align-items:center; padding:18px 0 10px 0; margin-top:10px; border-top:1px solid rgba(255,255,255,0.06); flex-wrap:wrap; gap:12px;">
                <div style="font-size:0.75rem; color:var(--text-dim);">
                    第 <span style="color:var(--accent-secondary); font-weight:700;">${_currentPage}</span> / ${_totalPages} 页 · 每页 ${_pageSize} 项 · 共 <strong style="color:var(--text-bright);">${_totalAssets}</strong> 项媒体资产
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                    <button type="button" class="mini-btn" ${_currentPage <= 1 ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : 'onclick="window.changeAssetsPage(1)"'} title="首页">⏮️ 首页</button>
                    <button type="button" class="mini-btn" ${_currentPage <= 1 ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : `onclick="window.changeAssetsPage(${_currentPage - 1})"`} title="上一页">◀️ 上一页</button>
                    <button type="button" class="mini-btn" ${_currentPage >= _totalPages ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : `onclick="window.changeAssetsPage(${_currentPage + 1})"`} title="下一页">▶️ 下一页</button>
                    <button type="button" class="mini-btn" ${_currentPage >= _totalPages ? 'disabled style="opacity:0.35; cursor:not-allowed;"' : `onclick="window.changeAssetsPage(${_totalPages})"`} title="尾页">⏭️ 尾页</button>
                    <div style="display:flex; align-items:center; gap:4px; margin-left:6px;">
                        <input type="number" id="assets-go-page-input" class="assets-page-input" min="1" max="${_totalPages}" value="${_currentPage}" style="width:48px; height:24px; text-align:center; font-size:0.72rem; border-radius:4px; outline:none;" onkeydown="if(event.key==='Enter')window.jumpAssetsPage()" />
                        <button type="button" class="mini-btn" style="padding:2px 8px; font-size:0.7rem;" onclick="window.jumpAssetsPage()">跳转</button>
                    </div>
                </div>
            </div>
        `;

        const cardsHtml = `
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:16px; padding-bottom:10px;" id="assets-grid-container">
                ${filtered.map(a => {
                    const normEng = normalizeEngine(a.strategy);
                    const engLabel = normEng === 'og_card' ? '🎨 OG 卡片' : normEng.toUpperCase();
                    const promptText = a.prompt || a.rel_path || '默认封面模板';
                    const refCount = a.reference_count || (a.references && a.references.length) || 0;
                    const isSelected = _batchSelectedIds.has(a.id);
                    const refBadge = refCount > 0
                        ? `<div style="position:absolute; top:8px; right:8px; font-size:0.65rem; color:#10b981; background:rgba(16,185,129,0.25); backdrop-filter:blur(4px); padding:2px 8px; border-radius:4px; border:1px solid rgba(16,185,129,0.4); font-weight:600;">🔗 ${refCount} 篇引用</div>`
                        : `<div style="position:absolute; top:8px; right:8px; font-size:0.65rem; color:var(--text-dim); background:rgba(0,0,0,0.5); backdrop-filter:blur(4px); padding:2px 6px; border-radius:4px; border:1px solid rgba(255,255,255,0.1);">0 引用</div>`;
                    const checkMarkup = _isBatchManaging ? `
                        <div style="position:absolute; top:8px; left:8px; z-index:10; background:rgba(0,0,0,0.7); padding:3px 6px; border-radius:4px; border:1px solid rgba(0,242,254,0.4); display:flex; align-items:center;" onclick="event.stopPropagation()">
                            <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="window.toggleSingleAssetSelect(${a.id}, this.checked)" style="accent-color:#00f2fe; width:15px; height:15px; cursor:pointer;" />
                        </div>
                    ` : '';

                    return `
                    <div class="glass-panel asset-card-item" id="asset-card-${a.id}" style="border-radius:10px; overflow:hidden; border:1px solid ${isSelected ? 'rgba(0,242,254,0.4)' : 'rgba(255,255,255,0.08)'}; display:flex; flex-direction:column; position:relative; transition:all 0.2s cubic-bezier(0.16,1,0.3,1); background:${isSelected ? 'rgba(0,242,254,0.04)' : ''};">
                        <div class="skeleton-shimmer" style="position:relative; width:100%; height:160px; background:#05070f; cursor:pointer; overflow:hidden;" onclick="${_isBatchManaging ? `window.toggleSingleAssetSelect(${a.id}, !${isSelected})` : `window.openAssetDetailModal(${a.id})`}">
                            <img src="${a.source_url}" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='/api/design/assets/default-cover.jpg';" alt="资产" style="width:100%; height:100%; object-fit:cover; transition:transform 0.3s; display:block;" onmouseover="this.style.transform='scale(1.04)'" onmouseout="this.style.transform='scale(1)'" />
                            ${checkMarkup}
                            <div class="asset-engine-badge" style="position:absolute; top:8px; left:${_isBatchManaging ? '40px' : '8px'}; font-size:0.65rem; backdrop-filter:blur(4px); padding:2px 8px; border-radius:4px;">
                                🏷️ ${engLabel}
                            </div>
                            ${renderCdnBadge(a.cdn_url)}
                            ${refBadge}
                        </div>
                        <div style="padding:12px; display:flex; flex-direction:column; gap:6px; flex:1;">
                            <div style="font-size:0.75rem; color:var(--text-bright); line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;" title="${promptText}">
                                ${promptText}
                            </div>
                            <div style="font-size:0.68rem; color:var(--text-dim); margin-top:auto; display:flex; justify-content:space-between; align-items:center; padding-top:8px; border-top:1px solid rgba(255,255,255,0.05);">
                                <span>${(a.created_at || '').split(' ')[0] || '历史资产'}</span>
                                <span style="opacity:0.6;">#${a.id}</span>
                            </div>
                        </div>
                        <div style="padding:8px 12px; background:rgba(0,0,0,0.25); border-top:1px solid rgba(255,255,255,0.05); display:flex; gap:6px; align-items:center;">
                            <button type="button" class="mini-btn" style="flex:1; padding:5px 0; font-size:0.7rem;" onclick="window.copyAssetMarkdown('${a.cdn_url || a.source_url}')">📋 复制 MD</button>
                            <button type="button" class="mini-btn" style="flex:1; padding:5px 0; font-size:0.7rem; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.openAssetApplyCoverModal('${a.source_url}')">🖼️ 设为封面</button>
                            <button type="button" class="mini-btn" style="padding:5px 8px; font-size:0.7rem; color:#f87171;" onclick="window.deleteVisualAsset(${a.id})" title="删除该资产">🗑️</button>
                        </div>
                    </div>`;
                }).join('')}
            </div>
        `;
        root.innerHTML = filterHtml + cardsHtml + paginationHtml;
    };

    window.changeAssetsPage = function (newPage) {
        if (newPage < 1 || newPage > _totalPages || newPage === _currentPage) return;
        window.loadAndRenderDesignAssets(null, newPage);
    };

    window.jumpAssetsPage = function () {
        const inp = document.getElementById('assets-go-page-input');
        if (!inp) return;
        const p = parseInt(inp.value, 10);
        if (!isNaN(p) && p >= 1 && p <= _totalPages) {
            window.changeAssetsPage(p);
        } else if (window.showToast) {
            window.showToast(`请输入 1 至 ${_totalPages} 的有效页码`, 'warning');
        }
    };

    window.filterAssetsEngine = function (eng) { _activeFilter = eng; _currentPage = 1; window.loadAndRenderDesignAssets(null, 1); };
    window.filterAssetsStatus = function (st) { _statusFilter = st; window.renderAssetsGrid(); };
    window.toggleAssetBatchMode = function () { _isBatchManaging = !_isBatchManaging; if (!_isBatchManaging) _batchSelectedIds.clear(); window.renderAssetsGrid(); };
    window.toggleSingleAssetSelect = function (id, checked) { if (checked) _batchSelectedIds.add(id); else _batchSelectedIds.delete(id); window.renderAssetsGrid(); };
    window.toggleSelectAllFilteredAssets = function (selectAll) {
        if (selectAll) {
            _assetsList.forEach(a => {
                const refCount = a.reference_count || (a.references && a.references.length) || 0;
                const matchStatus = _statusFilter === 'all' || (_statusFilter === 'used' ? refCount > 0 : refCount === 0);
                if (matchStatus) _batchSelectedIds.add(a.id);
            });
        } else { _batchSelectedIds.clear(); }
        window.renderAssetsGrid();
    };

    window.executeBatchDeleteAssets = async function () {
        const count = _batchSelectedIds.size;
        if (count === 0) { if (window.showToast) window.showToast('⚠️ 请至少勾选一项待删除资产', 'warning'); return; }
        const selected = _assetsList.filter(a => _batchSelectedIds.has(a.id));
        const usedCount = selected.filter(a => (a.reference_count || (a.references && a.references.length) || 0) > 0).length;
        let msg = `确定要彻底物理删除选中的 ${count} 项媒体资产吗？\n\n落盘文件将被物理清除，账本记录同步注销。`;
        if (usedCount > 0) {
            msg += `\n\n⚠️ 检测到有 ${usedCount} 项图片正被文库原稿设为封面！\n系统将自动从对应原稿 Frontmatter 中解绑清空封面，彻底清理残留。`;
        }
        if (!confirm(msg)) return;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/batch-delete', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ asset_ids: Array.from(_batchSelectedIds), remove_from_docs: true })
            });
            if (res && res.success) {
                if (window.showToast) window.showToast(`🗑️ ${res.message || `成功删除 ${count} 项资产`}`, 'success');
                _batchSelectedIds.clear();
                _isBatchManaging = false;
                window.loadAndRenderDesignAssets();
                if (typeof window.loadVault === 'function') window.loadVault(null, window.vaultCurrentPage || 1);
            } else { throw new Error((res && res.message) || '批量删除失败'); }
        } catch (e) { if (window.showToast) window.showToast(`🛑 批量删除失败: ${e.message}`, 'error'); }
    };

    window.cleanupIdleVisualAssets = async function () {
        const idleCount = _assetsList.filter(a => (a.reference_count || (a.references && a.references.length) || 0) === 0).length;
        if (idleCount === 0) { if (window.showToast) window.showToast('✅ 当前暂无闲置资产', 'info'); return; }
        if (!confirm(`🧹 安全清理确认：\n\n检测到当前有 ${idleCount} 项闲置资产（0 引用）。\n确定彻底清理这 ${idleCount} 项闲置资产吗？`)) return;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/cleanup-idle', { method: 'POST' });
            if (res && res.success) {
                if (window.showToast) window.showToast(`🧹 闲置清理完成：已回收 ${res.cleaned_count || idleCount} 项`, 'success');
                window.loadAndRenderDesignAssets();
            } else { throw new Error((res && res.message) || '清理失败'); }
        } catch (e) { if (window.showToast) window.showToast(`🛑 清理失败: ${e.message}`, 'error'); }
    };

    window.copyAssetMarkdown = function (url) {
        const md = `![配图](${url})`;
        navigator.clipboard.writeText(md).then(() => window.showToast && window.showToast('📋 已复制 Markdown 语法', 'success')).catch(() => prompt('请手动复制:', md));
    };

    window.deleteVisualAsset = async function (assetId) {
        const a = _assetsList.find(x => x.id === assetId);
        const refCount = a && (a.reference_count || (a.references && a.references.length) || 0);
        let confirmMsg = `确定要永久删除媒体资产 #${assetId} 吗？`;
        if (refCount > 0) confirmMsg = `⚠️ 严重安全警示：该图片正被 ${refCount} 篇文库原稿引用！\n删除后将自动解绑封面，确定删除吗？`;
        if (!confirm(confirmMsg)) return;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/batch-delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asset_ids: [assetId], remove_from_docs: true }) });
            if (res && res.success) {
                if (window.showToast) window.showToast(`🗑️ 资产 #${assetId} 已成功删除`, 'success');
                window.loadAndRenderDesignAssets();
                if (typeof window.loadVault === 'function') window.loadVault(null, window.vaultCurrentPage || 1);
            } else { throw new Error((res && res.message) || '删除失败'); }
        } catch (e) { if (window.showToast) window.showToast(`🛑 删除失败: ${e.message}`, 'error'); }
    };
})();

