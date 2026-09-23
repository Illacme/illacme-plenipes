/**
 * 📚 [V125.0] Illacme Plenipes Vault - Book Bindery Modal Controller Shard
 * 职责：数字出版物全卷装订弹窗控制器、范围探测、EPUB / WebBook / PDF 多格式打包与安全流式下载。
 * 规范：100% 遵守 SOP-03 前端视觉主权与双主题自适应规范，模板由 BinderyTemplates 分离承载。
 */

(function() {
    'use strict';

    let _binderyModalEl = null;

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
     * 唤醒数字装订对话框
     * @param {string} preselectedScope 预选栏目 (可选，如 'Docs', 'Blog' 或 'all')
     */
    window.openBinderyModal = async function(preselectedScope = 'all', singleDoc = null) {
        const tpl = _getTemplates();
        tpl.ensureStyles();

        if (!_binderyModalEl) {
            _binderyModalEl = document.getElementById('bindery-modal-root');
            if (!_binderyModalEl) {
                _binderyModalEl = document.createElement('div');
                _binderyModalEl.id = 'bindery-modal-root';
                _binderyModalEl.className = 'modal-backdrop bindery-modal-backdrop';
                document.body.appendChild(_binderyModalEl);
            }
        }

        // 显示加载态
        _binderyModalEl.style.opacity = '1';
        _binderyModalEl.style.pointerEvents = 'auto';
        _binderyModalEl.innerHTML = tpl.buildLoadingHtml();

        let scopesData = {
            site_name: 'Illacme Plenipes',
            default_author: 'Illacme Editorial Team',
            categories: [{ id: 'all', name: '全部原稿 (全库总集)' }],
            formats: [{ id: 'epub', name: 'EPUB 3.0 流式电子书', ext: '.epub', recommended: true }]
        };

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/scopes');
            if (res && res.ok) {
                scopesData = await res.json();
            } else if (res && res.success) {
                scopesData = res;
            }
        } catch (e) {
            console.warn('[Bindery] 获取装订范围失败，降级使用预设:', e);
        }

        const currentScope = preselectedScope || 'all';
        if (singleDoc) {
            scopesData.single_doc = singleDoc;
        } else if (currentScope.startsWith('single:')) {
            const relPath = currentScope.slice(7);
            scopesData.single_doc = { rel_path: relPath, title: relPath };
        }
        const defaultTitle = (scopesData.single_doc && scopesData.single_doc.title) ? scopesData.single_doc.title : (scopesData.site_name ? `${scopesData.site_name} · 数字出版集` : '数字出版合集');

        _binderyModalEl.innerHTML = tpl.buildModalCardHtml(scopesData, currentScope, defaultTitle);

        // 绑定输入与选择防抖联动刷新封面与重置按钮状态
        let debounceTimer = null;
        const triggerDebouncedPreview = () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                window.refreshCoverPreview();
                if (typeof window.resetBinderySubmitBtn === 'function') window.resetBinderySubmitBtn();
            }, 250);
        };
        ['bindery-input-title', 'bindery-input-author'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('input', triggerDebouncedPreview);
        });
        ['bindery-select-scope', 'bindery-select-lang'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('change', () => {
                window.refreshCoverPreview();
                if (typeof window.resetBinderySubmitBtn === 'function') window.resetBinderySubmitBtn();
            });
        });

        // 初始拉取封面预览与货架
        window._binderyMatrixMode = false;
        if (window._binderySuccessTimer) {
            clearTimeout(window._binderySuccessTimer);
            window._binderySuccessTimer = null;
        }
        window.refreshCoverPreview();
        if (typeof window.fetchBinderyShelf === 'function') window.fetchBinderyShelf();

        document.querySelectorAll('.bindery-matrix-cb').forEach(cb => {
            cb.addEventListener('change', () => {
                window.updateMatrixSubmitBtn();
                if (typeof window.resetBinderySubmitBtn === 'function') window.resetBinderySubmitBtn();
            });
        });
    };

    /** 切换出版语种模式（单语 / 多语合卷 / 多语套书） */
    window.onBinderyLangModeChange = function(val) {
        const chipsRow = document.getElementById('bindery-matrix-chips-row');
        const badge = document.getElementById('bindery-lang-hint-badge');
        const submitBtn = document.getElementById('btn-execute-binding');
        const toggleBtn = document.getElementById('bindery-matrix-toggle-btn');

        if (val === 'polyglot') {
            if (chipsRow) chipsRow.style.display = 'flex';
            if (toggleBtn) toggleBtn.style.display = 'inline-block';
            if (badge) { badge.textContent = '📑 多语对照版'; badge.style.color = '#10b981'; }
            if (submitBtn) submitBtn.innerHTML = '<span>📑 制作多语对照电子书</span>';
        } else if (val === 'matrix_batch') {
            if (chipsRow) chipsRow.style.display = 'flex';
            if (toggleBtn) toggleBtn.style.display = 'inline-block';
            if (badge) { badge.textContent = '📦 多版本并发'; badge.style.color = '#38bdf8'; }
            const count = document.querySelectorAll('.bindery-matrix-cb:checked').length || 3;
            if (submitBtn) submitBtn.innerHTML = `<span>🌍 并发制作多语电子书 (${count} 本)</span>`;
        } else {
            if (chipsRow) chipsRow.style.display = 'none';
            if (toggleBtn) toggleBtn.style.display = 'none';
            if (badge) { badge.textContent = '单语言版'; badge.style.color = ''; }
            const langMap = { 'zh': '中文版', 'en': '英文版', 'ja': '日文版' };
            const langName = langMap[val] || val.toUpperCase();
            if (submitBtn) submitBtn.innerHTML = `<span>🚀 立即制作 (${langName})</span>`;
        }
        if (typeof window.refreshCoverPreview === 'function') window.refreshCoverPreview();
    };

    /**
     * 全选/反选矩阵语种
     */
    window.toggleAllBinderyMatrixLangs = function() {
        const cbs = document.querySelectorAll('.bindery-matrix-cb');
        if (!cbs.length) return;
        const allChecked = Array.from(cbs).every(cb => cb.checked);
        cbs.forEach(cb => { cb.checked = !allChecked; });
        window.updateMatrixSubmitBtn();
    };

    /** 联动更新提交装订按钮文案 */
    window.updateMatrixSubmitBtn = function() {
        const langVal = document.getElementById('bindery-select-lang')?.value;
        const count = document.querySelectorAll('.bindery-matrix-cb:checked').length;
        const submitBtn = document.getElementById('btn-execute-binding');
        if (!submitBtn) return;
        if (langVal === 'polyglot') submitBtn.innerHTML = `<span>📑 制作多语对照电子书 (${count} 语并列)</span>`;
        else if (langVal === 'matrix_batch') submitBtn.innerHTML = `<span>🌍 并发制作多语电子书 (${count} 本独立版本)</span>`;
    };

    /** 实时拉取并更新封面预览 */
    window.refreshCoverPreview = async function() {
        const imgEl = document.getElementById('bindery-cover-img');
        if (!imgEl) return;
        const badgeEl = document.getElementById('bindery-cover-badge');
        const gVal = id => document.getElementById(id)?.value || '';
        const payload = {
            title: gVal('bindery-input-title').trim(),
            author: gVal('bindery-input-author').trim(),
            scope: gVal('bindery-select-scope') || 'all',
            lang: gVal('bindery-select-lang') || 'zh',
            cover_mode: gVal('bindery-select-cover-mode') || 'auto',
            style: gVal('bindery-select-cover-style') || 'dark_emerald'
        };

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/cover-preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;

            if (data && data.success) {
                if (data.mode === 'none' || !data.data_uri) {
                    imgEl.src = '';
                    imgEl.style.display = 'none';
                    if (badgeEl) {
                        badgeEl.textContent = '🚫 禁用封面';
                        badgeEl.style.color = '#94a3b8';
                        badgeEl.style.borderColor = 'rgba(148, 163, 184, 0.3)';
                    }
                } else {
                    imgEl.style.display = 'block';
                    imgEl.src = data.data_uri;
                    if (badgeEl) {
                        if (data.mode === 'native') {
                            badgeEl.textContent = '📂 文库原图';
                            badgeEl.style.color = '#38bdf8';
                            badgeEl.style.borderColor = 'rgba(56, 189, 248, 0.4)';
                        } else {
                            badgeEl.textContent = '✨ 艺术排版';
                            badgeEl.style.color = '#10b981';
                            badgeEl.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                        }
                    }
                }
            }
        } catch (e) {
            console.warn('[Bindery] 刷新封面预览失败:', e);
        }
    };

    /**
     * 关闭装订对话框
     */
    window.closeBinderyModal = function() {
        if (_binderyModalEl) {
            _binderyModalEl.style.opacity = '0';
            _binderyModalEl.style.pointerEvents = 'none';
        }
    };

    window.switchBinderyTab = function(tab) {
        const pBuild = document.getElementById('bindery-panel-build'), pShelf = document.getElementById('bindery-panel-shelf');
        const tBuild = document.getElementById('btn-bindery-tab-build'), tShelf = document.getElementById('btn-bindery-tab-shelf');
        if (pBuild) pBuild.style.display = tab === 'build' ? 'flex' : 'none';
        if (pShelf) pShelf.style.display = tab === 'shelf' ? 'flex' : 'none';
        if (tBuild) tBuild.classList.toggle('active', tab === 'build');
        if (tShelf) tShelf.classList.toggle('active', tab === 'shelf');
        if (tab === 'shelf' && typeof window.fetchBinderyShelf === 'function') window.fetchBinderyShelf();
    };

    /** 📂 在操作系统文件管理器中高亮定位物理文件 (Show in Finder / Explorer) */
    window.revealBookInFolder = async function(filename) {
        if (!filename) return;
        const targetPath = filename.startsWith('dist/') ? filename : `dist/books/${filename}`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/system/reveal-file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: targetPath })
            });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (data && data.success) {
                if (typeof window.showToast === 'function') window.showToast(data.message || '📂 已在系统文件管理器中定位', 'success');
            } else {
                const err = (data && data.error) ? data.error : '未能打开系统所在文件夹';
                if (typeof window.showToast === 'function') window.showToast(`⚠️ ${err}`, 'warning');
                else alert(err);
            }
        } catch (e) {
            console.error('[Bindery] 唤起文件管理器异常:', e);
            if (typeof window.showToast === 'function') window.showToast('⚠️ 唤起系统文件管理器失败', 'error');
        }
    };

    window._activeBinderyFormat = 'epub';
    window.selectBinderyFormat = function(fmtId) {
        window._activeBinderyFormat = fmtId;
        ['epub', 'webbook', 'pdf'].forEach(f => {
            const el = document.getElementById(`btn-driver-${f}`);
            if (el) el.classList.toggle('active', fmtId === f);
        });
        if (typeof window.resetBinderySubmitBtn === 'function') window.resetBinderySubmitBtn();
    };

    window.resetBinderySubmitBtn = function() {
        if (window._binderySuccessTimer) {
            clearTimeout(window._binderySuccessTimer);
            window._binderySuccessTimer = null;
        }
        const submitBtn = document.getElementById('btn-execute-binding');
        const cancelBtn = document.getElementById('btn-bindery-cancel');
        if (cancelBtn) cancelBtn.textContent = '取消';
        if (!submitBtn) return;
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        const langVal = document.getElementById('bindery-select-lang')?.value || 'zh';
        if (langVal === 'polyglot' || langVal === 'matrix_batch') {
            window.updateMatrixSubmitBtn();
        } else {
            const langMap = { 'zh': '中文版', 'en': '英文版', 'ja': '日文版' };
            submitBtn.innerHTML = `<span>🚀 立即装订 (${langMap[langVal] || langVal.toUpperCase()})</span>`;
        }
    };
})();

