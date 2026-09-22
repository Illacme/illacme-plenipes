/**
 * Illacme Plenipes - Vault Bindery Shelf Manager
 * 模块职责：管理已编排出版物货架 (Book Shelf)，支持在线即时翻阅、下载与归档删除。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */
(function() {
    'use strict';

    /**
     * 格式化时间戳为相对时间或友好的日期字符串
     */
    function formatTime(mtime) {
        if (!mtime) return '刚刚';
        const d = new Date(mtime * 1000);
        const now = new Date();
        const diffSec = Math.floor((now - d) / 1000);
        if (diffSec < 60) return '刚刚';
        if (diffSec < 3600) return `${Math.floor(diffSec / 60)} 分钟前`;
        if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} 小时前`;
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    }

    /**
     * 拉取并更新货架视图
     */
    window.fetchBinderyShelf = async function() {
        const shelfContainer = document.getElementById('bindery-shelf-list');
        if (!shelfContainer) return;

        shelfContainer.innerHTML = `
            <div style="text-align:center; padding:30px; color:var(--text-dim, rgba(255,255,255,0.6)); font-size:0.85rem;">
                <span class="pulse-spin" style="display:inline-block; font-size:1.2rem; margin-bottom:8px;">⏳</span>
                <div>正在盘点典籍货架...</div>
            </div>
        `;

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/shelf');
            const data = (res && typeof res.json === 'function') ? await res.json() : res;

            if (!data || !data.success) {
                shelfContainer.innerHTML = `<div style="text-align:center; padding:20px; color:#ef4444; font-size:0.85rem;">❌ 获取货架失败</div>`;
                return;
            }

            const badgeCount = document.getElementById('bindery-shelf-badge');
            if (badgeCount) badgeCount.textContent = String(data.count || 0);

            window.renderBinderyShelfHtml(data.books || []);
        } catch (e) {
            console.error('[BinderyShelf] 拉取货架异常:', e);
            shelfContainer.innerHTML = `<div style="text-align:center; padding:20px; color:#ef4444; font-size:0.85rem;">⚠️ 加载货架网络异常</div>`;
        }
    };

    /**
     * 渲染货架列表卡片
     */
    window.renderBinderyShelfHtml = function(books) {
        const shelfContainer = document.getElementById('bindery-shelf-list');
        if (!shelfContainer) return;

        if (!books || books.length === 0) {
            shelfContainer.innerHTML = `
                <div style="text-align:center; padding:40px 20px; color:var(--text-dim, rgba(255,255,255,0.55)); font-size:0.85rem;">
                    <div style="font-size:2rem; margin-bottom:10px; opacity:0.7;">📚</div>
                    <div style="font-weight:600; color:var(--text-bright, #fff); margin-bottom:4px;">货架尚无已装订典籍</div>
                    <div style="font-size:0.75rem;">切换至上方「装订新版」生成第一部数字出版物！</div>
                </div>
            `;
            return;
        }

        const itemsHtml = books.map(b => {
            const isWebBook = b.format === 'webbook';
            const icon = isWebBook ? '🌐' : '📖';
            const fmtBadge = isWebBook
                ? '<span style="font-size:0.68rem; padding:2px 6px; border-radius:4px; background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3); font-weight:700;">WebBook</span>'
                : '<span style="font-size:0.68rem; padding:2px 6px; border-radius:4px; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); font-weight:700;">EPUB 3.0</span>';

            const previewBtn = isWebBook
                ? `<a href="${b.preview_url}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn" style="padding:4px 10px; font-size:0.75rem; text-decoration:none; display:inline-flex; align-items:center; gap:4px; border-radius:6px; background:#0284c7; color:#fff;">👁️ 翻阅</a>`
                : '';

            return `
                <div class="bindery-shelf-card" style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); border:1px solid var(--glass-border, rgba(255,255,255,0.09)); border-radius:8px; padding:10px 14px; margin-bottom:8px; transition:all 0.2s ease;">
                    <div style="display:flex; align-items:center; gap:12px; min-width:0; flex:1;">
                        <span style="font-size:1.4rem; flex-shrink:0;">${icon}</span>
                        <div style="min-width:0; flex:1;">
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px;">
                                <div style="font-size:0.88rem; font-weight:700; color:var(--text-bright, #fff); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${b.filename}">
                                    ${b.filename}
                                </div>
                                ${fmtBadge}
                            </div>
                            <div style="font-size:0.72rem; color:var(--text-dim, rgba(255,255,255,0.55)); display:flex; gap:12px;">
                                <span>📦 ${b.size_display}</span>
                                <span>🕒 ${formatTime(b.mtime)}</span>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; flex-shrink:0; margin-left:12px;">
                        ${previewBtn}
                        <a href="${b.download_url}" download="${b.filename}" class="secondary-btn" style="padding:4px 10px; font-size:0.75rem; text-decoration:none; display:inline-flex; align-items:center; gap:4px; border-radius:6px; color:var(--text-bright, #fff);">⬇️ 下载</a>
                        <button onclick="window.deleteBookFromShelf('${b.filename}')" class="bindery-del-btn" title="从货架归档删除" style="background:none; border:none; color:var(--text-dim, rgba(255,255,255,0.4)); font-size:0.9rem; cursor:pointer; padding:4px 6px; border-radius:4px; transition:color 0.2s;">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');

        shelfContainer.innerHTML = `<div style="max-height:360px; overflow-y:auto; padding-right:4px;">${itemsHtml}</div>`;
    };

    /**
     * 从货架删除指定书籍
     */
    window.deleteBookFromShelf = async function(filename) {
        if (!confirm(`确定要从出版货架中归档删除 "${filename}" 吗？此操作不可撤销。`)) {
            return;
        }

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename })
            });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;

            if (data && data.success) {
                window.fetchBinderyShelf();
            } else {
                alert(`删除失败: ${(data && data.detail) || '未知错误'}`);
            }
        } catch (e) {
            console.error('[BinderyShelf] 删除异常:', e);
            alert(`删除失败: ${e.message}`);
        }
    };
})();
