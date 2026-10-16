/**
 * 📚 [V125.0] Illacme Plenipes - Dispatch Shelf Releases Workbench Renderer
 * 职责：负责发布中心第一主轨「书架出版物 (Book Shelf Releases)」的大盘态势、格式矩阵、书目货架与分发下载交互。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */

(function () {
    'use strict';

    window._dispatchShelfBooks = [];
    window._dispatchShelfFilter = 'all'; window._dispatchShelfQuery = '';
    window._dispatchShelfPage = 1; window._dispatchShelfPageSize = 6;
    window._dispatchShelfBatchMode = false; window._dispatchShelfSelected = new Set();
    window._dispatchShelfTotalSize = '';

    function formatTime(mtime) {
        if (!mtime) return '刚刚';
        const d = new Date(mtime * 1000), diffSec = Math.floor((Date.now() - d.getTime()) / 1000);
        if (diffSec < 60) return '刚刚';
        if (diffSec < 3600) return `${Math.floor(diffSec / 60)} 分钟前`;
        if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} 小时前`;
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    }

    /**
     * 加载书架数据并触发大盘与货架渲染
     */
    window.loadDispatchShelfCenter = async function () {
        const consoleBox = document.getElementById('dispatch-shelf-console');
        const listBox = document.getElementById('dispatch-shelf-list-container');
        if (!listBox) return;

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/shelf');
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (!data || !data.success) {
                listBox.innerHTML = `<div style="text-align:center; padding:30px; color:var(--text-danger); font-size:0.85rem;">❌ 获取书架出版物失败</div>`;
                return;
            }

            window._dispatchShelfBooks = data.books || [];
            window._dispatchShelfTotalSize = data.total_size_display || '';

            // 更新导航 Tab 徽章数字
            const badge = document.getElementById('badge-shelf-books');
            if (badge) badge.innerText = String(data.count || window._dispatchShelfBooks.length);

            if (consoleBox) window.renderDispatchShelfConsole(data);
            window.renderDispatchShelfList();
        } catch (e) {
            console.error('🛑 [DispatchShelf] 加载书架出版物异常:', e);
            if (listBox) listBox.innerHTML = `<div style="text-align:center; padding:30px; color:var(--text-danger); font-size:0.85rem;">⚠️ 加载书架出版物网络异常</div>`;
        }
    };

    /**
     * 战区一：书架出版物四大态势感知卡片
     */
    window.renderDispatchShelfConsole = function (data) {
        const consoleBox = document.getElementById('dispatch-shelf-console');
        if (!consoleBox) return;

        const all = data.books || [], totalCount = data.count || all.length, totalSize = data.total_size_display || '0 MB';
        const epubCount = all.filter(b => b.format === 'epub').length, wbCount = all.filter(b => b.format === 'webbook').length, pdfCount = all.filter(b => b.format === 'pdf').length;

        consoleBox.innerHTML = `
            <div class="dispatch-metric-grid" style="margin-bottom: 0;">
                <div class="dispatch-metric-card interactive" onclick="window.setDispatchShelfFilter('all')" title="点击查看全部出版物">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="metric-label">电子出版物总数</span>
                        <span class="metric-filter-hint">全部 📚</span>
                    </div>
                    <span class="metric-val">${totalCount} <span style="font-size:0.85rem; font-weight:normal; color:var(--text-dim);">本</span></span>
                    <span class="metric-sub">${epubCount} EPUB · ${wbCount} 网页书 · ${pdfCount} 印本</span>
                </div>
                <div class="dispatch-metric-card">
                    <span class="metric-label">出版物物理容量</span>
                    <span class="metric-val">${totalSize}</span>
                    <span class="metric-sub">本地磁盘封装体积</span>
                </div>
                <div class="dispatch-metric-card interactive" onclick="window.setDispatchShelfFilter('webbook')" title="点击筛选网页独立书">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="metric-label">在线即时翻阅</span>
                        <span class="metric-filter-hint">即开 🌐</span>
                    </div>
                    <span class="metric-val">${wbCount + epubCount} <span style="font-size:0.85rem; font-weight:normal; color:var(--text-dim);">部</span></span>
                    <span class="metric-sub">双链互通 · 随时阅览</span>
                </div>
                <div class="dispatch-metric-card interactive" onclick="if(typeof window.openBinderyModal==='function') window.openBinderyModal();" title="唤起电子出版编排中枢生产新书" style="cursor:pointer; border-color:rgba(var(--neon-green-rgb), 0.35);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="metric-label" style="color:var(--accent);">电子出版工坊</span>
                        <span style="font-size:0.72rem; color:var(--accent); font-weight:700;">出版新书 ↗</span>
                    </div>
                    <span class="metric-val" style="color:var(--accent); font-size:1.3rem;">⚡ 一键编排</span>
                    <span class="metric-sub">EPUB / PDF / DOCX 生产</span>
                </div>
            </div>
        `;
    };

    /**
     * 战区二：出版物货架列表渲染与交互控制
     */
    window.renderDispatchShelfList = function () {
        const listBox = document.getElementById('dispatch-shelf-list-container');
        const headerActions = document.getElementById('dispatch-shelf-header-actions');
        if (!listBox) return;

        const all = window._dispatchShelfBooks || [];
        const wbCount = all.filter(b => b.format === 'webbook').length, epubCount = all.filter(b => b.format === 'epub').length, pdfCount = all.filter(b => b.format === 'pdf').length;
        const docxCount = all.filter(b => b.format === 'docx').length, mdCount = all.filter(b => b.format === 'markdown').length, txtCount = all.filter(b => b.format === 'txt').length;

        if (headerActions) {
            const isBatch = window._dispatchShelfBatchMode;
            headerActions.innerHTML = `
                <button type="button" class="secondary-btn btn-sm" onclick="window.exportDispatchShelfZip('all')" style="padding:4px 10px; font-size:0.74rem;">📦 导出全架</button>
                <button type="button" class="secondary-btn btn-sm" onclick="window.toggleDispatchShelfBatchMode()" style="padding:4px 10px; font-size:0.74rem; ${isBatch ? 'border-color:var(--accent); color:var(--accent);' : ''}">${isBatch ? '✖️ 退出批量' : '☑️ 批量管理'}</button>
                <button type="button" class="primary-btn glow-btn btn-sm" onclick="if(typeof window.openBinderyModal==='function') window.openBinderyModal();" style="padding:4px 12px; font-size:0.74rem; background:var(--accent);">⚡ 出版新书</button>
            `;
        }

        const filtered = all.filter(b => {
            if (window._dispatchShelfFilter !== 'all' && b.format !== window._dispatchShelfFilter) return false;
            if (window._dispatchShelfQuery && !b.filename.toLowerCase().includes(window._dispatchShelfQuery)) return false;
            return true;
        });

        const activeFl = window._dispatchShelfFilter || 'all';
        const chipBtn = (key, label, count) => {
            const active = activeFl === key;
            return `<button type="button" class="t-tab ${active ? 'active' : ''}" onclick="window.setDispatchShelfFilter('${key}')" style="padding:4px 10px; font-size:0.74rem; border-radius:6px; height:28px;">${label} (${count})</button>`;
        };

        const pageSize = window._dispatchShelfPageSize || 6;
        const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
        if (window._dispatchShelfPage > totalPages) window._dispatchShelfPage = totalPages;
        if (window._dispatchShelfPage < 1) window._dispatchShelfPage = 1;
        const curPage = window._dispatchShelfPage;
        const paged = filtered.slice((curPage - 1) * pageSize, curPage * pageSize);
        const isBatch = window._dispatchShelfBatchMode;
        const selectedCount = window._dispatchShelfSelected.size;
        const isAllChecked = paged.length > 0 && paged.every(b => window._dispatchShelfSelected.has(b.filename));

        const filterBarHtml = `
            <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:12px; padding-bottom:12px; border-bottom:1px solid var(--glass-border);">
                <nav class="tactical-tabs" style="gap:4px; flex-wrap:wrap;">
                    ${chipBtn('all', '全部', all.length)}
                    ${chipBtn('epub', '📖 电子书', epubCount)}
                    ${chipBtn('webbook', '🌐 网页书', wbCount)}
                    ${chipBtn('pdf', '📄 PDF', pdfCount)}
                    ${chipBtn('docx', '📑 Word', docxCount)}
                    ${chipBtn('markdown', '📝 MD', mdCount)}
                    ${chipBtn('txt', '📜 TXT', txtCount)}
                </nav>
                <div style="display:flex; align-items:center; gap:8px;">
                    <input type="text" placeholder="🔍 检索书名/语言..." value="${window._dispatchShelfQuery || ''}" oninput="window.setDispatchShelfQuery(this.value)" style="width:170px; padding:4px 8px; font-size:0.75rem; background:var(--white-05); border:1px solid var(--glass-border); border-radius:6px; color:var(--text-bright); outline:none;" />
                </div>
            </div>
            ${isBatch ? `
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px; padding:6px 12px; background:var(--white-03); border:1px solid var(--glass-border); border-radius:8px; font-size:0.75rem;">
                    <label style="display:inline-flex; align-items:center; gap:6px; cursor:pointer; user-select:none;">
                        <input type="checkbox" ${isAllChecked ? 'checked' : ''} onchange="window.toggleAllDispatchShelfSelect(${JSON.stringify(paged.map(b => b.filename)).replace(/"/g, '&quot;')})" style="accent-color:var(--accent); cursor:pointer;" />
                        <span>${isAllChecked ? '取消全选当前页' : '全选当前页'}</span>
                    </label>
                    <span style="color:var(--text-dim);">已选 <strong style="color:var(--accent);">${selectedCount}</strong> 本</span>
                    <button type="button" class="secondary-btn btn-sm" onclick="window.exportDispatchShelfZip('selected')" ${selectedCount === 0 ? 'disabled style="opacity:0.4;"' : ''}>📦 批量导出 (${selectedCount})</button>
                    <button type="button" class="secondary-btn btn-sm" onclick="window.batchDeleteDispatchShelf()" ${selectedCount === 0 ? 'disabled style="opacity:0.4; color:var(--text-danger);"' : 'style="color:var(--text-danger); border-color:rgba(239,68,68,0.4);"'}>🗑️ 批量清理 (${selectedCount})</button>
                </div>
            ` : ''}
        `;

        if (filtered.length === 0) {
            listBox.innerHTML = filterBarHtml + `<div style="text-align:center; padding:40px; color:var(--text-muted); font-size:0.86rem;">🔍 未找到符合条件的出版物，请调整筛选或装订新书。</div>`;
            return;
        }

        const cardsHtml = paged.map(b => {
            const isWb = b.format === 'webbook', isPdf = b.format === 'pdf', isDocx = b.format === 'docx', isMd = b.format === 'markdown', isTxt = b.format === 'txt';
            const icon = isWb ? '🌐' : (isPdf ? '📄' : (isDocx ? '📑' : (isMd ? '📝' : (isTxt ? '📜' : '📖'))));
            const badgeBase = 'font-size:0.68rem; padding:2px 6px; border-radius:4px; font-weight:700; display:inline-flex; align-items:center;';
            let fmtBadge = `<span style="${badgeBase} background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3);">EPUB 3.0</span>`;
            if (isWb) fmtBadge = `<span style="${badgeBase} background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3);">WebBook</span>`;
            else if (isPdf) fmtBadge = `<span style="${badgeBase} background:rgba(168,85,247,0.15); color:#a855f7; border:1px solid rgba(168,85,247,0.3);">PDF 印本</span>`;
            else if (isDocx) fmtBadge = `<span style="${badgeBase} background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3);">Word 文档</span>`;
            else if (isMd) fmtBadge = `<span style="${badgeBase} background:rgba(6,182,212,0.15); color:#06b6d4; border:1px solid rgba(6,182,212,0.3);">Markdown</span>`;
            else if (isTxt) fmtBadge = `<span style="${badgeBase} background:rgba(139,92,246,0.15); color:#a78bfa; border:1px solid rgba(139,92,246,0.3);">TXT</span>`;

            const isSelected = window._dispatchShelfSelected.has(b.filename);
            const fnEsc = b.filename.replace(/'/g, "\\'");

            return `
                <div class="dispatch-shelf-item" style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 14px; background:var(--white-03); border:1px solid ${isSelected ? 'var(--accent)' : 'var(--glass-border)'}; border-radius:10px; margin-bottom:8px; transition:all 0.2s;">
                    <div style="display:flex; align-items:center; gap:12px; min-width:0; flex:1;">
                        ${isBatch ? `<input type="checkbox" ${isSelected ? 'checked' : ''} onchange="window.toggleDispatchShelfSelect('${fnEsc}', this.checked)" style="accent-color:var(--accent); cursor:pointer;" />` : ''}
                        <span style="font-size:1.5rem; flex-shrink:0;">${icon}</span>
                        <div style="min-width:0; flex:1;">
                            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                                <span style="font-weight:700; font-size:0.86rem; color:var(--text-bright); word-break:break-all;">${b.filename}</span>
                                ${fmtBadge}
                            </div>
                            <div style="font-size:0.72rem; color:var(--text-dim); margin-top:3px; display:flex; gap:12px; font-family:var(--font-mono);">
                                <span>📦 ${b.size_display}</span>
                                <span>🕒 ${formatTime(b.mtime)}</span>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">
                        ${b.preview_url ? `<a href="${b.preview_url}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn btn-sm" title="在线翻阅与即时研读" style="padding:4px 8px; font-size:0.82rem; text-decoration:none;">👁️ 翻阅</a>` : ''}
                        <a href="${b.download_url}" download="${b.filename}" class="secondary-btn btn-sm" title="下载出版物文件" style="padding:4px 8px; font-size:0.82rem; text-decoration:none;">⬇️ 下载</a>
                        <button type="button" class="secondary-btn btn-sm" onclick="if(typeof window.revealBookInFolder==='function') window.revealBookInFolder('${fnEsc}'); else if(typeof window.revealBinderyBook==='function') window.revealBinderyBook('${fnEsc}');" title="在本地文件管理器中定位">📁</button>
                        <button type="button" class="secondary-btn btn-sm" onclick="if(typeof window.openBinderyQrModal==='function') window.openBinderyQrModal('${fnEsc}'); else if(typeof window.showBinderyQRPair==='function') window.showBinderyQRPair('${fnEsc}');" title="扫码投送至手机或平板">📱</button>
                        <button type="button" class="secondary-btn btn-sm" onclick="window.deleteDispatchShelfBook('${fnEsc}')" title="从货架归档删除此书" style="color:var(--text-danger);">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');

        const pageBarHtml = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; padding-top:10px; border-top:1px solid var(--glass-border); font-size:0.75rem; color:var(--text-dim);">
                <span>第 <strong>${curPage}</strong> / ${totalPages} 页 · 共 <strong>${filtered.length}</strong> 本出版物</span>
                <div style="display:flex; gap:6px;">
                    <button type="button" class="secondary-btn btn-sm" onclick="window.changeDispatchShelfPage(1)" ${curPage === 1 ? 'disabled style="opacity:0.4;"' : ''}>⏮️ 首页</button>
                    <button type="button" class="secondary-btn btn-sm" onclick="window.changeDispatchShelfPage(${curPage - 1})" ${curPage === 1 ? 'disabled style="opacity:0.4;"' : ''}>◀ 上页</button>
                    <button type="button" class="secondary-btn btn-sm" onclick="window.changeDispatchShelfPage(${curPage + 1})" ${curPage === totalPages ? 'disabled style="opacity:0.4;"' : ''}>下页 ▶</button>
                    <button type="button" class="secondary-btn btn-sm" onclick="window.changeDispatchShelfPage(${totalPages})" ${curPage === totalPages ? 'disabled style="opacity:0.4;"' : ''}>尾页 ⏭️</button>
                </div>
            </div>
        `;

        listBox.innerHTML = filterBarHtml + cardsHtml + pageBarHtml;
    };

    window.setDispatchShelfFilter = function (f) { window._dispatchShelfFilter = f || 'all'; window._dispatchShelfPage = 1; window.renderDispatchShelfList(); };
    window.setDispatchShelfQuery = function (q) { window._dispatchShelfQuery = (q || '').trim().toLowerCase(); window._dispatchShelfPage = 1; window.renderDispatchShelfList(); };
    window.changeDispatchShelfPage = function (p) { window._dispatchShelfPage = p; window.renderDispatchShelfList(); };
    window.toggleDispatchShelfBatchMode = function () {
        window._dispatchShelfBatchMode = !window._dispatchShelfBatchMode;
        if (!window._dispatchShelfBatchMode) window._dispatchShelfSelected.clear();
        window.renderDispatchShelfList();
    };
    window.toggleDispatchShelfSelect = function (fn, chk) { if (chk) window._dispatchShelfSelected.add(fn); else window._dispatchShelfSelected.delete(fn); window.renderDispatchShelfList(); };
    window.toggleAllDispatchShelfSelect = function (fns) { const all = fns.every(f => window._dispatchShelfSelected.has(f)); fns.forEach(f => { if (all) window._dispatchShelfSelected.delete(f); else window._dispatchShelfSelected.add(f); }); window.renderDispatchShelfList(); };
    window.exportDispatchShelfZip = function (scope) { if (typeof window.exportBatchBooksAsZip === 'function') window.exportBatchBooksAsZip(scope === 'all' ? 'all' : undefined); else window.open('/api/bindery/export_zip', '_blank'); };

    window.deleteDispatchShelfBook = async function (filename) {
        if (typeof window.confirmSovereignAction === 'function') {
            const ok = await window.confirmSovereignAction({
                title: '🗑️ 删除出版物', text: `确定要从书架删除出版物「${filename}」吗？物理文件将被清理。`,
                icon: 'warning', confirmText: '确定删除', confirmColor: '#ff4d4f'
            });
            if (!ok) return;
        } else if (!confirm(`确定要从书架删除出版物「${filename}」吗？物理文件将被清理。`)) return;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename }) });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (data && data.success) {
                if (typeof window.showToast === 'function') window.showToast(`✅ 已删除出版物: ${filename}`, 'success');
                window.loadDispatchShelfCenter();
            } else {
                const msg = `删除失败: ${(data && (data.detail || data.error)) || '未知错误'}`;
                window.showToast ? window.showToast(`❌ ${msg}`, 'error') : alert(msg);
            }
        } catch (e) {
            window.showToast ? window.showToast(`⚠️ 删除出版物网络异常: ${e.message || e}`, 'error') : alert(e.message || e);
        }
    };

    window.batchDeleteDispatchShelf = async function () {
        const files = Array.from(window._dispatchShelfSelected || []);
        if (!files.length) return window.showToast ? window.showToast('请先勾选需要清理的出版物', 'warning') : null;
        if (typeof window.confirmSovereignAction === 'function') {
            const ok = await window.confirmSovereignAction({
                title: '🗑️ 批量删除出版物', text: `确定要批量删除已选中的 ${files.length} 本出版物吗？此操作无法撤销。`,
                icon: 'warning', confirmText: '批量删除', confirmColor: '#ff4d4f'
            });
            if (!ok) return;
        } else if (!confirm(`确定要批量删除已选中的 ${files.length} 本出版物吗？此操作无法撤销。`)) return;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filenames: files }) });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (data && data.success) {
                window._dispatchShelfSelected.clear();
                if (typeof window.showToast === 'function') window.showToast(`✅ 成功移除 ${data.count || files.length} 本出版物`, 'success');
                window.loadDispatchShelfCenter();
            } else {
                const msg = `批量删除失败: ${(data && (data.detail || data.error)) || '未知错误'}`;
                window.showToast ? window.showToast(`❌ ${msg}`, 'error') : alert(msg);
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`⚠️ 批量删除异常: ${e.message || e}`, 'error');
        }
    };
})();
