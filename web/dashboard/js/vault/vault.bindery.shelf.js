/**
 * Illacme Plenipes - Vault Bindery Shelf Manager
 * 模块职责：管理已编排出版物货架 (Book Shelf)，支持在线即时翻阅、下载、沿用配置重新装订与归档删除。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */
(function() {
    'use strict';

    window._binderyShelfBooks = [];
    window._binderyShelfFilter = 'all';
    window._binderyShelfQuery = '';

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
            window.renderBinderyShelfHtml();
        } catch (e) {
            console.error('[BinderyShelf] 拉取书架异常:', e);
            shelfContainer.innerHTML = `<div style="text-align:center; padding:20px; color:#ef4444; font-size:0.85rem;">⚠️ 加载书架网络异常</div>`;
        }
    };

    window.setBinderyShelfFilter = function(filter) {
        window._binderyShelfFilter = filter || 'all';
        window.renderBinderyShelfHtml();
    };

    window.setBinderyShelfQuery = function(query) {
        window._binderyShelfQuery = (query || '').trim().toLowerCase();
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
        const chipStyle = (isActive) => `padding:3px 9px; font-size:0.75rem; border-radius:6px; cursor:pointer; border:1px solid ${isActive ? 'var(--accent, #10b981)' : 'var(--glass-border, rgba(255,255,255,0.12))'}; background:${isActive ? 'rgba(16,185,129,0.18)' : 'rgba(255,255,255,0.04)'}; color:${isActive ? 'var(--accent, #10b981)' : 'var(--text-dim, rgba(255,255,255,0.6))'}; font-weight:${isActive ? '700' : '500'}; transition:all 0.2s;`;

        const toolbarHtml = `
            <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:10px; flex-wrap:wrap;">
                <div style="display:flex; gap:6px; align-items:center;">
                    <button type="button" onclick="window.setBinderyShelfFilter('all')" style="${chipStyle(activeFl === 'all')}">全部 (${all.length})</button>
                    <button type="button" onclick="window.setBinderyShelfFilter('webbook')" style="${chipStyle(activeFl === 'webbook')}">🌐 网页书 (${wbCount})</button>
                    <button type="button" onclick="window.setBinderyShelfFilter('epub')" style="${chipStyle(activeFl === 'epub')}">📖 电子书 (${epubCount})</button>
                    <button type="button" onclick="window.setBinderyShelfFilter('pdf')" style="${chipStyle(activeFl === 'pdf')}">📄 PDF 印本 (${pdfCount})</button>
                </div>
                <div style="min-width:140px; flex:1; max-width:200px;">
                    <input type="text" placeholder="🔍 过滤书名/语言..." value="${window._binderyShelfQuery || ''}" oninput="window.setBinderyShelfQuery(this.value)" style="width:100%; box-sizing:border-box; padding:4px 8px; font-size:0.75rem; background:rgba(0,0,0,0.22); border:1px solid var(--glass-border, rgba(255,255,255,0.14)); border-radius:6px; color:#fff; outline:none;" />
                </div>
            </div>
        `;

        if (filtered.length === 0) {
            shelfContainer.innerHTML = toolbarHtml + `<div style="text-align:center; padding:30px; color:var(--text-dim, rgba(255,255,255,0.5)); font-size:0.8rem;">🔍 未找到匹配的电子书或出版物</div>`;
            return;
        }

        const itemsHtml = filtered.map(b => {
            const isWb = b.format === 'webbook', isPdf = b.format === 'pdf';
            const icon = isWb ? '🌐' : (isPdf ? '📄' : '📖');
            let fmtBadge = '<span style="font-size:0.68rem; padding:2px 6px; border-radius:4px; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); font-weight:700;">EPUB 3.0</span>';
            if (isWb) fmtBadge = '<span style="font-size:0.68rem; padding:2px 6px; border-radius:4px; background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3); font-weight:700;">WebBook</span>';
            if (isPdf) fmtBadge = '<span style="font-size:0.68rem; padding:2px 6px; border-radius:4px; background:rgba(168,85,247,0.15); color:#a855f7; border:1px solid rgba(168,85,247,0.3); font-weight:700;">PDF 印本</span>';

            const previewBtn = isWb
                ? `<a href="${b.preview_url}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn" title="在线翻阅 (WebBook)" style="padding:4px 8px; font-size:0.85rem; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; border-radius:6px; background:#0284c7; color:#fff;">👁️</a>`
                : '';

            return `
                <div class="bindery-shelf-card" style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); border:1px solid var(--glass-border, rgba(255,255,255,0.09)); border-radius:8px; padding:10px 14px; margin-bottom:8px; transition:all 0.2s ease;">
                    <div style="display:flex; align-items:center; gap:12px; min-width:0; flex:1;">
                        <span style="font-size:1.4rem; flex-shrink:0;">${icon}</span>
                        <div style="min-width:0; flex:1;">
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px;">
                                <div style="font-size:0.88rem; font-weight:700; color:var(--text-bright, #fff); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${b.filename}">${b.filename}</div>
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
                        <button onclick="window.rebindBookFromShelf('${b.filename}')" class="secondary-btn" title="沿用此配置重新装订" style="padding:4px 8px; font-size:0.85rem; border:1px solid var(--glass-border, rgba(255,255,255,0.12)); display:inline-flex; align-items:center; justify-content:center; border-radius:6px; color:var(--text-bright, #fff); cursor:pointer;">🔄</button>
                        <button onclick="window.deleteBookFromShelf('${b.filename}')" class="bindery-del-btn" title="从书架中删除" style="background:none; border:none; color:var(--text-dim, rgba(255,255,255,0.4)); font-size:0.9rem; cursor:pointer; padding:4px 6px; border-radius:4px; transition:color 0.2s;">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');

        shelfContainer.innerHTML = toolbarHtml + `<div style="max-height:330px; overflow-y:auto; padding-right:4px;">${itemsHtml}</div>`;
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

    function _getTemplates() {
        return window.BinderyTemplates || {
            ensureStyles: () => {}, esc: s => s || '', formatSize: b => `${b} B`,
            buildLoadingHtml: () => '<div>正在加载...</div>', buildModalCardHtml: () => '<div>装订面板</div>', buildSuccessStatusHtml: () => '<div>装订成功</div>'
        };
    }

    window.executeBookBinding = async function() {
        const tpl = _getTemplates(), titleInput = document.getElementById('bindery-input-title');
        const authorInput = document.getElementById('bindery-input-author'), scopeSelect = document.getElementById('bindery-select-scope');
        const langSelect = document.getElementById('bindery-select-lang'), modeSelect = document.getElementById('bindery-select-cover-mode');
        const styleSelect = document.getElementById('bindery-select-cover-style'), statusArea = document.getElementById('bindery-status-area');
        const submitBtn = document.getElementById('btn-execute-binding');
        if (!titleInput || !submitBtn) return;

        const payload = {
            format: window._activeBinderyFormat || 'epub', scope: scopeSelect ? scopeSelect.value : 'all',
            title: titleInput.value.trim() || undefined, author: authorInput ? authorInput.value.trim() || undefined : undefined,
            cover_mode: modeSelect ? modeSelect.value : 'auto', cover_style: styleSelect ? styleSelect.value : 'dark_emerald'
        };
        const langMode = langSelect ? langSelect.value : 'zh';
        if (langMode === 'polyglot' || langMode === 'matrix_batch') {
            const selectedLangs = Array.from(document.querySelectorAll('.bindery-matrix-cb:checked')).map(cb => cb.value);
            if (selectedLangs.length === 0) {
                if (typeof window.showToast === 'function') window.showToast('请至少勾选一个目标语种', 'warning');
                return;
            }
            payload.languages = selectedLangs;
            if (langMode === 'polyglot') payload.polyglot_mode = true;
        } else {
            payload.lang = langMode;
        }

        submitBtn.disabled = true; submitBtn.style.opacity = '0.7';
        submitBtn.innerHTML = payload.polyglot_mode ? `<span>⚙️ 正在制作多语对照电子书...</span>` : (payload.languages ? `<span>⚙️ 正在并发制作 (${payload.languages.length} 本)...</span>` : `<span>⚙️ 正在制作...</span>`);
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';

        if (statusArea) {
            statusArea.style.display = 'block';
            statusArea.style.background = isLight ? 'rgba(2, 132, 199, 0.08)' : 'rgba(0, 242, 254, 0.08)';
            statusArea.style.border = isLight ? '1px solid rgba(2, 132, 199, 0.25)' : '1px solid rgba(0, 242, 254, 0.25)';
            statusArea.style.color = isLight ? '#0284c7' : '#00f2fe';
            statusArea.innerHTML = payload.polyglot_mode ? `⏳ 正在按整篇并列对齐 ${payload.languages.map(l => l.toUpperCase()).join(' ⇋ ')} 多语对照内容并生成 WebBook...` : (payload.languages ? `⏳ 正在并发制作 ${payload.languages.map(l => l.toUpperCase()).join(', ')} 多语言电子书...` : `⏳ 正在遍历文库章节、提取元数据并生成电子书...`);
        }

        if (typeof window.addAudit === 'function') {
            const desc = window._binderyMatrixMode ? `多语言[${payload.languages.join(',')}]` : payload.lang;
            window.addAudit(`📚 开始制作电子书: [${payload.title || '默认书名'}] (${desc})`);
        }

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/build', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            let result = (res && typeof res.json === 'function') ? await res.json() : res;

            if (result && result.success) {
                const formattedSize = tpl.formatSize(result.file_size || 0);
                if (statusArea) {
                    statusArea.style.background = isLight ? 'rgba(16, 185, 129, 0.08)' : 'rgba(16, 185, 129, 0.12)';
                    statusArea.style.border = isLight ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(16, 185, 129, 0.35)';
                    statusArea.style.color = isLight ? '#047857' : '#10b981';
                    statusArea.innerHTML = tpl.buildSuccessStatusHtml(result, formattedSize);
                }
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.85';
                submitBtn.innerHTML = `<span>✨ 制作成功</span>`;
                const cancelBtn = document.getElementById('btn-bindery-cancel');
                if (cancelBtn) cancelBtn.textContent = '关闭';
                if (window._binderySuccessTimer) clearTimeout(window._binderySuccessTimer);
                window._binderySuccessTimer = setTimeout(() => {
                    const btn = document.getElementById('btn-execute-binding');
                    if (btn) {
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        btn.innerHTML = `<span>🔄 重新装订</span>`;
                    }
                }, 1800);
                if (typeof window.fetchBinderyShelf === 'function') window.fetchBinderyShelf();

                if (result.mode === 'matrix' && Array.isArray(result.results)) {
                    const count = result.total_built || result.results.length;
                    if (typeof window.addAudit === 'function') window.addAudit(`✅ 多语言电子书制作完成: 共 ${count} 本`);
                    if (typeof window.showToast === 'function') window.showToast(`🎉 成功制作 ${count} 本多语言电子书！`, 'success');
                    if (result.results.length > 0 && result.results[0].download_url) {
                        const first = result.results[0], dlLink = document.createElement('a');
                        dlLink.href = first.download_url; dlLink.download = first.filename;
                        document.body.appendChild(dlLink); dlLink.click(); setTimeout(() => dlLink.remove(), 1000);
                    }
                } else {
                    if (typeof window.addAudit === 'function') window.addAudit(`✅ 电子书已落盘: ${result.filename} (${formattedSize})`);
                    if (typeof window.showToast === 'function') window.showToast(`电子书 ${result.filename} 装订成功！`, 'success');
                    const dlLink = document.createElement('a');
                    dlLink.href = result.download_url; dlLink.download = result.filename;
                    document.body.appendChild(dlLink); dlLink.click(); setTimeout(() => dlLink.remove(), 1000);
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
            submitBtn.disabled = false; submitBtn.style.opacity = '1'; submitBtn.innerHTML = `<span>重新装订</span>`;
        }
    };
})();
