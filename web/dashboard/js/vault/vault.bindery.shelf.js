/**
 * Illacme Plenipes - Vault Bindery Shelf Manager
 * 模块职责：管理已编排出版物货架 (Book Shelf)，支持在线即时翻阅、下载、系统定位、沿用配置重新装订、归档删除、优雅分页与多选批量管理控制。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */
(function() {
    'use strict';

    window._binderyShelfBooks = [];
    window._binderyShelfFilter = 'all';
    window._binderyShelfQuery = '';
    window._binderyShelfPage = 1;
    window._binderyShelfPageSize = 5;
    window._binderyShelfBatchMode = false;
    window._binderyShelfSelected = new Set();
    window._binderyShelfTotalSize = '';

    function formatTime(mtime) {
        if (!mtime) return '刚刚';
        const d = new Date(mtime * 1000), diffSec = Math.floor((Date.now() - d.getTime()) / 1000);
        if (diffSec < 60) return '刚刚';
        if (diffSec < 3600) return `${Math.floor(diffSec / 60)} 分钟前`;
        if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} 小时前`;
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    }

    window.fetchBinderyShelf = async function() {
        const shelfContainer = document.getElementById('bindery-shelf-list');
        if (!shelfContainer) return;
        shelfContainer.innerHTML = `<div style="text-align:center; padding:30px; color:var(--text-dim, rgba(255,255,255,0.6)); font-size:0.85rem;"><span class="pulse-spin" style="display:inline-block; font-size:1.2rem; margin-bottom:8px;">⏳</span><div>正在加载我的书架...</div></div>`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/shelf');
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (!data || !data.success) {
                shelfContainer.innerHTML = `<div style="text-align:center; padding:20px; color:#ef4444; font-size:0.85rem;">❌ 获取书架失败</div>`;
                return;
            }
            const badgeCount = document.getElementById('bindery-shelf-badge');
            if (badgeCount) badgeCount.textContent = String(data.count || 0);
            window._binderyShelfBooks = data.books || [];
            window._binderyShelfTotalSize = data.total_size_display || '';
            window.renderBinderyShelfHtml();
        } catch (e) {
            console.error('[BinderyShelf] 拉取书架异常:', e);
            shelfContainer.innerHTML = `<div style="text-align:center; padding:20px; color:#ef4444; font-size:0.85rem;">⚠️ 加载书架网络异常</div>`;
        }
    };

    window.setBinderyShelfFilter = function(filter) {
        window._binderyShelfFilter = filter || 'all';
        window._binderyShelfPage = 1;
        window.renderBinderyShelfHtml();
    };

    window.setBinderyShelfQuery = function(query) {
        window._binderyShelfQuery = (query || '').trim().toLowerCase();
        window._binderyShelfPage = 1;
        window.renderBinderyShelfHtml();
    };

    window.changeBinderyShelfPage = function(newPage) {
        window._binderyShelfPage = Math.max(1, newPage);
        window.renderBinderyShelfHtml();
    };

    window.toggleBinderyShelfBatchMode = function() {
        window._binderyShelfBatchMode = !window._binderyShelfBatchMode;
        if (!window._binderyShelfBatchMode) window._binderyShelfSelected.clear();
        window.renderBinderyShelfHtml();
    };

    window.toggleBinderyShelfSelect = function(filename, checked) {
        if (checked) window._binderyShelfSelected.add(filename);
        else window._binderyShelfSelected.delete(filename);
        window.renderBinderyShelfHtml();
    };

    window.toggleAllBinderyShelfSelect = function(pageFilenames) {
        const allChecked = pageFilenames.every(f => window._binderyShelfSelected.has(f));
        pageFilenames.forEach(f => {
            if (allChecked) window._binderyShelfSelected.delete(f);
            else window._binderyShelfSelected.add(f);
        });
        window.renderBinderyShelfHtml();
    };

    window.renderBinderyShelfHtml = function(books) {
        const shelfContainer = document.getElementById('bindery-shelf-list');
        if (!shelfContainer) return;
        if (books && Array.isArray(books)) window._binderyShelfBooks = books;
        const all = window._binderyShelfBooks || [];
        const wbCount = all.filter(b => b.format === 'webbook').length;
        const epubCount = all.filter(b => b.format === 'epub').length;
        const pdfCount = all.filter(b => b.format === 'pdf').length;

        if (all.length === 0) {
            shelfContainer.innerHTML = `<div style="text-align:center; padding:40px 20px; color:var(--text-dim, rgba(255,255,255,0.55)); font-size:0.85rem;"><div style="font-size:2rem; margin-bottom:10px; opacity:0.7;">📚</div><div style="font-weight:600; color:var(--text-bright, #fff); margin-bottom:4px;">书架上暂无已制作的电子书</div><div style="font-size:0.75rem;">切换至上方「装订新版」生成第一本电子书！</div></div>`;
            return;
        }

        const filtered = all.filter(b => {
            if (window._binderyShelfFilter === 'webbook' && b.format !== 'webbook') return false;
            if (window._binderyShelfFilter === 'epub' && b.format !== 'epub') return false;
            if (window._binderyShelfFilter === 'pdf' && b.format !== 'pdf') return false;
            if (window._binderyShelfQuery && !b.filename.toLowerCase().includes(window._binderyShelfQuery)) return false;
            return true;
        });

        const activeFl = window._binderyShelfFilter || 'all';
        const chipStyle = (isActive) => `padding:3px 8px; font-size:0.75rem; border-radius:6px; cursor:pointer; border:1px solid ${isActive ? 'var(--accent, #10b981)' : 'var(--glass-border, rgba(255,255,255,0.12))'}; background:${isActive ? 'rgba(16,185,129,0.18)' : 'rgba(255,255,255,0.04)'}; color:${isActive ? 'var(--accent, #10b981)' : 'var(--text-dim, rgba(255,255,255,0.6))'}; font-weight:${isActive ? '700' : '500'}; transition:all 0.2s;`;

        const totalItems = filtered.length;
        const pageSize = window._binderyShelfPageSize || 5;
        const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
        if (window._binderyShelfPage > totalPages) window._binderyShelfPage = totalPages;
        if (window._binderyShelfPage < 1) window._binderyShelfPage = 1;
        const currentPage = window._binderyShelfPage;

        const startIdx = (currentPage - 1) * pageSize;
        const pagedBooks = filtered.slice(startIdx, startIdx + pageSize);
        const isBatch = window._binderyShelfBatchMode;
        const selectedCount = window._binderyShelfSelected.size;

        const hActions = document.getElementById('bindery-shelf-header-actions');
        if (hActions) {
            const szBadge = window._binderyShelfTotalSize ? `<span style="font-size:0.7rem; color:var(--text-dim, rgba(255,255,255,0.6)); background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; border:1px solid var(--glass-border, rgba(255,255,255,0.1));" title="已编译出版物物理占用磁盘总容量">💾 占用 ${window._binderyShelfTotalSize}</span>` : '';
            const bBtn = `<button type="button" onclick="window.toggleBinderyShelfBatchMode()" style="padding:2px 8px; font-size:0.72rem; border-radius:6px; cursor:pointer; border:1px solid ${isBatch ? 'var(--accent, #10b981)' : 'var(--glass-border, rgba(255,255,255,0.14))'}; background:${isBatch ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.06)'}; color:${isBatch ? 'var(--accent, #10b981)' : 'var(--text-bright, #fff)'}; font-weight:600;">${isBatch ? '✖️ 退出批量' : '☑️ 批量管理'}</button>`;
            hActions.innerHTML = `${szBadge}${bBtn}`;
        }

        const pagedFnamesJson = JSON.stringify(pagedBooks.map(b => b.filename)).replace(/"/g, '&quot;');

        const toolbarHtml = `
            <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:8px; flex-wrap:wrap;">
                <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                    <button type="button" onclick="window.setBinderyShelfFilter('all')" style="${chipStyle(activeFl === 'all')}">全部 (${all.length})</button>
                    <button type="button" onclick="window.setBinderyShelfFilter('webbook')" style="${chipStyle(activeFl === 'webbook')}">🌐 网页书 (${wbCount})</button>
                    <button type="button" onclick="window.setBinderyShelfFilter('epub')" style="${chipStyle(activeFl === 'epub')}">📖 电子书 (${epubCount})</button>
                    <button type="button" onclick="window.setBinderyShelfFilter('pdf')" style="${chipStyle(activeFl === 'pdf')}">📄 PDF 印本 (${pdfCount})</button>
                </div>
                <div style="min-width:140px; max-width:200px;">
                    <input type="text" placeholder="🔍 过滤书名/语言..." value="${window._binderyShelfQuery || ''}" oninput="window.setBinderyShelfQuery(this.value)" style="width:100%; box-sizing:border-box; padding:4px 8px; font-size:0.75rem; background:rgba(0,0,0,0.22); border:1px solid var(--glass-border, rgba(255,255,255,0.14)); border-radius:6px; color:#fff; outline:none;" />
                </div>
            </div>
            ${isBatch ? `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 10px; margin-bottom:8px; background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:6px; font-size:0.75rem;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <button type="button" onclick="window.toggleAllBinderyShelfSelect(${pagedFnamesJson})" style="background:rgba(255,255,255,0.08); border:1px solid var(--glass-border, rgba(255,255,255,0.15)); color:#fff; border-radius:4px; padding:2px 8px; font-size:0.72rem; cursor:pointer;">☑️ 全选/取消当前页</button>
                        <span style="color:var(--text-dim, rgba(255,255,255,0.7));">已选 <strong style="color:var(--accent, #10b981);">${selectedCount}</strong> 本</span>
                    </div>
                    <button type="button" onclick="window.deleteBatchBooksFromShelf()" ${selectedCount === 0 ? 'disabled style="opacity:0.4; cursor:not-allowed; background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); color:#ef4444; border-radius:4px; padding:2px 10px; font-size:0.72rem; font-weight:700;"' : 'style="background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); color:#ef4444; border-radius:4px; padding:2px 10px; font-size:0.72rem; font-weight:700; cursor:pointer;"'}>🗑️ 批量清理 (${selectedCount})</button>
                </div>
            ` : ''}
        `;

        if (filtered.length === 0) {
            shelfContainer.innerHTML = toolbarHtml + `<div style="text-align:center; padding:30px; color:var(--text-dim, rgba(255,255,255,0.5)); font-size:0.8rem;">🔍 未找到匹配的电子书或出版物</div>`;
            return;
        }

        const itemsHtml = pagedBooks.map(b => {
            const isWb = b.format === 'webbook', isPdf = b.format === 'pdf';
            const icon = isWb ? '🌐' : (isPdf ? '📄' : '📖');
            const badgeBase = 'font-size:0.68rem; padding:2px 6px; border-radius:4px; font-weight:700; white-space:nowrap; flex-shrink:0; display:inline-flex; align-items:center;';
            let fmtBadge = `<span style="${badgeBase} background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3);">EPUB 3.0</span>`;
            if (isWb) fmtBadge = `<span style="${badgeBase} background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3);">WebBook</span>`;
            if (isPdf) fmtBadge = `<span style="${badgeBase} background:rgba(168,85,247,0.15); color:#a855f7; border:1px solid rgba(168,85,247,0.3);">PDF 印本</span>`;

            const previewBtn = isWb
                ? `<a href="${b.preview_url}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn" title="在线翻阅 (WebBook)" style="padding:4px 8px; font-size:0.85rem; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; border-radius:6px; background:#0284c7; color:#fff;">👁️</a>`
                : '';

            const isSelected = window._binderyShelfSelected.has(b.filename);
            const checkboxHtml = isBatch
                ? `<input type="checkbox" ${isSelected ? 'checked' : ''} onchange="window.toggleBinderyShelfSelect('${b.filename}', this.checked)" style="accent-color:#10b981; width:15px; height:15px; cursor:pointer; flex-shrink:0; margin-right:4px;" />`
                : '';

            return `
                <div class="bindery-shelf-card" style="display:flex; justify-content:space-between; align-items:center; background:${isSelected ? 'rgba(16,185,129,0.08)' : 'rgba(255,255,255,0.03)'}; border:1px solid ${isSelected ? 'rgba(16,185,129,0.35)' : 'var(--glass-border, rgba(255,255,255,0.09))'}; border-radius:8px; padding:10px 14px; margin-bottom:8px; transition:all 0.2s ease;">
                    <div style="display:flex; align-items:center; gap:10px; min-width:0; flex:1;">
                        ${checkboxHtml}
                        <span style="font-size:1.4rem; flex-shrink:0;">${icon}</span>
                        <div style="min-width:0; flex:1;">
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px; min-width:0;">
                                <div style="font-size:0.88rem; font-weight:700; color:var(--text-bright, #fff); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; min-width:0; max-width:calc(100% - 85px);" title="${b.filename}">${b.filename}</div>
                                ${fmtBadge}
                            </div>
                            <div style="font-size:0.72rem; color:var(--text-dim, rgba(255,255,255,0.55)); display:flex; gap:12px;">
                                <span>📦 ${b.size_display}</span>
                                <span>🕒 ${formatTime(b.mtime)}</span>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; flex-shrink:0; margin-left:12px;">
                        ${previewBtn}
                        <a href="${b.download_url}" download="${b.filename}" class="secondary-btn" title="下载出版物" style="padding:4px 8px; font-size:0.85rem; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; border-radius:6px; color:var(--text-bright, #fff);">⬇️</a>
                        <button onclick="window.revealBookInFolder('${b.filename}')" class="secondary-btn" title="在系统文件夹中显示" style="padding:4px 8px; font-size:0.85rem; border:1px solid var(--glass-border, rgba(255,255,255,0.12)); display:inline-flex; align-items:center; justify-content:center; border-radius:6px; color:var(--text-bright, #fff); cursor:pointer;">📂</button>
                        <button onclick="window.openBinderyQrModal('${b.filename}')" class="secondary-btn" title="📱 局域网扫码直传 (手机/平板/Kindle)" style="padding:4px 8px; font-size:0.85rem; border:1px solid var(--glass-border, rgba(255,255,255,0.12)); display:inline-flex; align-items:center; justify-content:center; border-radius:6px; color:var(--text-bright, #fff); cursor:pointer;">📱</button>
                        <button onclick="window.rebindBookFromShelf('${b.filename}')" class="secondary-btn" title="沿用此配置重新装订" style="padding:4px 8px; font-size:0.85rem; border:1px solid var(--glass-border, rgba(255,255,255,0.12)); display:inline-flex; align-items:center; justify-content:center; border-radius:6px; color:var(--text-bright, #fff); cursor:pointer;">🔄</button>
                        <button onclick="window.deleteBookFromShelf('${b.filename}')" class="bindery-del-btn" title="从书架中删除" style="background:none; border:none; color:var(--text-dim, rgba(255,255,255,0.4)); font-size:0.9rem; cursor:pointer; padding:4px 6px; border-radius:4px; transition:color 0.2s;">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');

        const paginationHtml = `
            <div class="pagination-container" style="display:flex; justify-content:space-between; align-items:center; padding:10px 4px 4px 4px; margin-top:8px; border-top:1px solid var(--glass-border, rgba(255,255,255,0.08)); font-size:0.75rem;">
                <div style="color:var(--text-dim, rgba(255,255,255,0.55));">
                    第 <span style="color:var(--accent, #10b981); font-weight:700;">${currentPage}</span> / ${totalPages} 页 · 共 <strong style="color:var(--text-bright, #fff);">${totalItems}</strong> 本出版物
                </div>
                <div style="display:flex; align-items:center; gap:4px;">
                    <button type="button" class="mini-btn" ${currentPage <= 1 ? 'disabled style="opacity:0.35; cursor:not-allowed; padding:3px 7px; font-size:0.72rem;"' : 'onclick="window.changeBinderyShelfPage(1)" style="padding:3px 7px; font-size:0.72rem; cursor:pointer;"'} title="首页">⏮️ 首页</button>
                    <button type="button" class="mini-btn" ${currentPage <= 1 ? 'disabled style="opacity:0.35; cursor:not-allowed; padding:3px 7px; font-size:0.72rem;"' : `onclick="window.changeBinderyShelfPage(${currentPage - 1})" style="padding:3px 7px; font-size:0.72rem; cursor:pointer;"`} title="上一页">◀️ 上一页</button>
                    <button type="button" class="mini-btn" ${currentPage >= totalPages ? 'disabled style="opacity:0.35; cursor:not-allowed; padding:3px 7px; font-size:0.72rem;"' : `onclick="window.changeBinderyShelfPage(${currentPage + 1})" style="padding:3px 7px; font-size:0.72rem; cursor:pointer;"`} title="下一页">▶️ 下一页</button>
                    <button type="button" class="mini-btn" ${currentPage >= totalPages ? 'disabled style="opacity:0.35; cursor:not-allowed; padding:3px 7px; font-size:0.72rem;"' : `onclick="window.changeBinderyShelfPage(${totalPages})" style="padding:3px 7px; font-size:0.72rem; cursor:pointer;"`} title="尾页">⏭️ 尾页</button>
                </div>
            </div>
        `;

        shelfContainer.innerHTML = toolbarHtml + `<div style="max-height:330px; overflow-y:auto; padding-right:4px;">${itemsHtml}</div>` + paginationHtml;
    };

    window.rebindBookFromShelf = function(filename) {
        if (!filename) return;
        const fmt = filename.endsWith('.html') ? 'webbook' : (filename.endsWith('.pdf') ? 'pdf' : 'epub');
        if (typeof window.switchBinderyTab === 'function') window.switchBinderyTab('build');
        else if (typeof window.switchBinderyModalTab === 'function') window.switchBinderyModalTab('build');
        if (typeof window.selectBinderyFormat === 'function') window.selectBinderyFormat(fmt);

        let clean = filename.replace(/\.(html|epub|pdf|md)$/i, '');
        const isPoly = clean.includes('-polyglot') || clean.includes('多语');
        let lang = 'zh';
        const m = clean.match(/_([a-z]{2,5})$/i) || clean.match(/-([a-z]{2,5})-edition/i);
        if (m && !isPoly) lang = m[1].toLowerCase();

        let title = clean.replace(/^illacme-press-/i, '').replace(/-polyglot-edition.*$/i, '').replace(/-[a-z]{2,5}-edition.*$/i, '').replace(/_[a-z]{2,5}$/i, '');
        const titleInput = document.getElementById('bindery-input-title'), langSelect = document.getElementById('bindery-select-lang');
        const scopeSelect = document.getElementById('bindery-select-scope');
        if (titleInput && title) titleInput.value = title;
        if (langSelect) {
            langSelect.value = isPoly ? 'polyglot' : (langSelect.querySelector(`option[value="${lang}"]`) ? lang : 'zh');
            langSelect.dispatchEvent(new Event('change'));
        }
        if (scopeSelect && title) {
            for (let opt of scopeSelect.options) {
                if (opt.value !== 'all' && (opt.text.includes(title) || opt.value.toLowerCase() === title.toLowerCase())) {
                    scopeSelect.value = opt.value; break;
                }
            }
        }
        if (typeof window.showToast === 'function') window.showToast(`正在沿用历史配置重新装订「${title || filename}」...`, 'info');
        setTimeout(() => {
            if (typeof window.executeBookBinding === 'function') window.executeBookBinding();
        }, 150);
    };

    window.deleteBookFromShelf = async function(filename) {
        if (!confirm(`确定要从书架中删除 "${filename}" 吗？此操作不可撤销。`)) return;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename }) });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (data && data.success) {
                window.fetchBinderyShelf();
                if (typeof window.showToast === 'function') window.showToast(`已从书架移除: ${filename}`, 'success');
            } else {
                alert(`删除失败: ${(data && data.detail) || '未知错误'}`);
            }
        } catch (e) {
            console.error('[BinderyShelf] 删除异常:', e);
            alert(`删除失败: ${e.message}`);
        }
    };

    window.deleteBatchBooksFromShelf = async function() {
        const files = Array.from(window._binderyShelfSelected);
        if (!files.length) return window.showToast?.('请先勾选需要清理的出版物', 'warning');
        if (!confirm(`确定要批量永久删除选中的 ${files.length} 本出版物吗？此操作不可撤销。`)) return;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filenames: files }) });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (data && data.success) {
                window._binderyShelfSelected.clear();
                window._binderyShelfBatchMode = false;
                window.fetchBinderyShelf();
                if (typeof window.showToast === 'function') window.showToast(`已成功批量清理 ${data.count || files.length} 本出版物`, 'success');
            } else {
                alert(`批量删除失败: ${(data && data.detail) || '未知错误'}`);
            }
        } catch (e) {
            console.error('[BinderyShelf] 批量删除异常:', e);
            alert(`批量删除异常: ${e.message}`);
        }
    };
})();
