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

    function _getTemplates() {
        return window.BinderyTemplates || {
            ensureStyles: () => {},
            esc: s => s || '',
            formatSize: b => `${b} B`,
            buildLoadingHtml: () => '<div>正在加载...</div>',
            buildModalCardHtml: () => '<div>装订面板</div>',
            buildSuccessStatusHtml: () => '<div>装订成功</div>'
        };
    }

    /**
     * 触发异步合卷装订并下载
     */
    window.executeBookBinding = async function() {
        const tpl = _getTemplates();
        const titleInput = document.getElementById('bindery-input-title');
        const authorInput = document.getElementById('bindery-input-author');
        const scopeSelect = document.getElementById('bindery-select-scope');
        const langSelect = document.getElementById('bindery-select-lang');
        const modeSelect = document.getElementById('bindery-select-cover-mode');
        const styleSelect = document.getElementById('bindery-select-cover-style');
        const statusArea = document.getElementById('bindery-status-area');
        const submitBtn = document.getElementById('btn-execute-binding');

        if (!titleInput || !submitBtn) return;

        const payload = {
            format: window._activeBinderyFormat || 'epub',
            scope: scopeSelect ? scopeSelect.value : 'all',
            title: titleInput.value.trim() || undefined,
            author: authorInput ? authorInput.value.trim() || undefined : undefined,
            cover_mode: modeSelect ? modeSelect.value : 'auto',
            cover_style: styleSelect ? styleSelect.value : 'dark_emerald'
        };

        const langMode = langSelect ? langSelect.value : 'zh';
        if (langMode === 'polyglot' || langMode === 'matrix_batch') {
            const cbs = document.querySelectorAll('.bindery-matrix-cb:checked');
            const selectedLangs = Array.from(cbs).map(cb => cb.value);
            if (selectedLangs.length === 0) {
                if (typeof window.showToast === 'function') {
                    window.showToast('请至少勾选一个目标语种', 'warning');
                }
                return;
            }
            payload.languages = selectedLangs;
            if (langMode === 'polyglot') {
                payload.polyglot_mode = true;
            }
        } else {
            payload.lang = langMode;
        }

        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.innerHTML = payload.polyglot_mode
            ? `<span>⚙️ 正在装订多语平行合卷...</span>`
            : (payload.languages ? `<span>⚙️ 正在并发装订 (${payload.languages.length} 册)...</span>` : `<span>⚙️ 正在装订...</span>`);

        const isLight = document.documentElement.getAttribute('data-theme') === 'light';

        if (statusArea) {
            statusArea.style.display = 'block';
            statusArea.style.background = isLight ? 'rgba(2, 132, 199, 0.08)' : 'rgba(0, 242, 254, 0.08)';
            statusArea.style.border = isLight ? '1px solid rgba(2, 132, 199, 0.25)' : '1px solid rgba(0, 242, 254, 0.25)';
            statusArea.style.color = isLight ? '#0284c7' : '#00f2fe';
            statusArea.innerHTML = payload.polyglot_mode
                ? `⏳ 正在按整篇并列对齐 ${payload.languages.map(l => l.toUpperCase()).join(' ⇋ ')} 多语平行对照矩阵并封装 WebBook...`
                : (payload.languages
                    ? `⏳ 正在并发装订 ${payload.languages.map(l => l.toUpperCase()).join(', ')} 多语种丛书矩阵...`
                    : `⏳ 正在遍历文库章节、提取 Frontmatter 并编译出版物实体...`);
        }

        if (typeof window.addAudit === 'function') {
            const desc = window._binderyMatrixMode ? `多语种矩阵[${payload.languages.join(',')}]` : payload.lang;
            window.addAudit(`📚 开始执行数字装订: [${payload.title || '默认书名'}] (${desc})`);
        }

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/build', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let result = (res && typeof res.json === 'function') ? await res.json() : res;

            if (result && result.success) {
                const formattedSize = tpl.formatSize(result.file_size || 0);

                if (statusArea) {
                    statusArea.style.background = isLight ? 'rgba(16, 185, 129, 0.08)' : 'rgba(16, 185, 129, 0.12)';
                    statusArea.style.border = isLight ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(16, 185, 129, 0.35)';
                    statusArea.style.color = isLight ? '#047857' : '#10b981';
                    statusArea.innerHTML = tpl.buildSuccessStatusHtml(result, formattedSize);
                }

                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
                submitBtn.innerHTML = `<span>✨ 装订成功</span>`;

                if (typeof window.fetchBinderyShelf === 'function') window.fetchBinderyShelf();

                if (result.mode === 'matrix' && Array.isArray(result.results)) {
                    const count = result.total_built || result.results.length;
                    if (typeof window.addAudit === 'function') window.addAudit(`✅ 多语种矩阵丛书落盘成功: 共 ${count} 册`);
                    if (typeof window.showToast === 'function') window.showToast(`🎉 成功装订 ${count} 册多语种典籍！`, 'success');
                    if (result.results.length > 0 && result.results[0].download_url) {
                        const first = result.results[0];
                        const dlLink = document.createElement('a');
                        dlLink.href = first.download_url;
                        dlLink.download = first.filename;
                        document.body.appendChild(dlLink);
                        dlLink.click();
                        setTimeout(() => dlLink.remove(), 1000);
                    }
                } else {
                    if (typeof window.addAudit === 'function') window.addAudit(`✅ 电子书已落盘: ${result.filename} (${formattedSize})`);
                    if (typeof window.showToast === 'function') window.showToast(`电子书 ${result.filename} 装订成功！`, 'success');
                    const dlLink = document.createElement('a');
                    dlLink.href = result.download_url;
                    dlLink.download = result.filename;
                    document.body.appendChild(dlLink);
                    dlLink.click();
                    setTimeout(() => dlLink.remove(), 1000);
                }
            } else {
                throw new Error((result && (result.detail || result.error || result.message)) || '装订返回异常');
            }
        } catch (err) {
            console.error('[Bindery] 装订流程异常:', err);
            if (statusArea) {
                statusArea.style.display = 'block';
                statusArea.style.background = isLight ? 'rgba(239, 68, 68, 0.08)' : 'rgba(239, 68, 68, 0.12)';
                statusArea.style.border = isLight ? '1px solid rgba(239, 68, 68, 0.25)' : '1px solid rgba(239, 68, 68, 0.35)';
                statusArea.style.color = isLight ? '#dc2626' : '#ff6b6b';
                statusArea.innerHTML = `❌ 装订失败：${tpl.esc(err.message || '系统内部异常')}`;
            }
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
            submitBtn.innerHTML = `<span>重新装订</span>`;
        }
    };
})();

