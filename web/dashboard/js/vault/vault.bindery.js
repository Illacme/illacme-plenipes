/**
 * 📚 [V125.0] Illacme Plenipes Vault - Book Bindery Modal Controller Shard
 * 职责：数字出版物全卷装订弹窗控制器、范围探测、EPUB 3.0 打包与安全流式下载。
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
    window.openBinderyModal = async function(preselectedScope = 'all') {
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
        const defaultTitle = scopesData.site_name ? `${scopesData.site_name} · 数字出版集` : '数字出版合集';

        _binderyModalEl.innerHTML = tpl.buildModalCardHtml(scopesData, currentScope, defaultTitle);

        // 绑定输入与选择防抖联动刷新封面
        let debounceTimer = null;
        const triggerDebouncedPreview = () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(window.refreshCoverPreview, 250);
        };

        const titleInput = document.getElementById('bindery-input-title');
        const authorInput = document.getElementById('bindery-input-author');
        const scopeSelect = document.getElementById('bindery-select-scope');
        const langSelect = document.getElementById('bindery-select-lang');

        if (titleInput) titleInput.addEventListener('input', triggerDebouncedPreview);
        if (authorInput) authorInput.addEventListener('input', triggerDebouncedPreview);
        if (scopeSelect) scopeSelect.addEventListener('change', window.refreshCoverPreview);
        if (langSelect) langSelect.addEventListener('change', window.refreshCoverPreview);

        // 初始拉取封面预览与货架
        window._binderyMatrixMode = false;
        window.refreshCoverPreview();
        if (typeof window.fetchBinderyShelf === 'function') window.fetchBinderyShelf();

        // 监听矩阵复选框变动
        const cbs = document.querySelectorAll('.bindery-matrix-cb');
        cbs.forEach(cb => {
            cb.addEventListener('change', window.updateMatrixSubmitBtn);
        });
    };

    /**
    /**
     * 切换出版语种模式（单语 / 多语合卷 / 多语套书）
     */
    window.onBinderyLangModeChange = function(val) {
        const chipsRow = document.getElementById('bindery-matrix-chips-row');
        const badge = document.getElementById('bindery-lang-hint-badge');
        const submitBtn = document.getElementById('btn-execute-binding');

        if (val === 'polyglot') {
            if (chipsRow) chipsRow.style.display = 'flex';
            if (badge) { badge.textContent = '📑 多语合卷'; badge.style.color = '#10b981'; }
            if (submitBtn) submitBtn.innerHTML = '<span>📑 装订多语合卷研读版</span>';
        } else if (val === 'matrix_batch') {
            if (chipsRow) chipsRow.style.display = 'flex';
            if (badge) { badge.textContent = '📦 套书并发'; badge.style.color = '#38bdf8'; }
            const count = document.querySelectorAll('.bindery-matrix-cb:checked').length || 3;
            if (submitBtn) submitBtn.innerHTML = `<span>🌍 矩阵并发装订 (${count} 册)</span>`;
        } else {
            if (chipsRow) chipsRow.style.display = 'none';
            if (badge) { badge.textContent = '单语典籍'; badge.style.color = ''; }
            const langMap = { 'zh': '中文版', 'en': '英文版', 'ja': '日文版' };
            const langName = langMap[val] || val.toUpperCase();
            if (submitBtn) submitBtn.innerHTML = `<span>🚀 立即装订 (${langName})</span>`;
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

    /**
     * 联动更新提交装订按钮文案
     */
    window.updateMatrixSubmitBtn = function() {
        const langVal = document.getElementById('bindery-select-lang')?.value;
        const count = document.querySelectorAll('.bindery-matrix-cb:checked').length;
        const submitBtn = document.getElementById('btn-execute-binding');
        if (!submitBtn) return;
        if (langVal === 'polyglot') {
            submitBtn.innerHTML = `<span>📑 装订多语合卷研读版 (${count} 语并列)</span>`;
        } else if (langVal === 'matrix_batch') {
            submitBtn.innerHTML = `<span>🌍 矩阵并发装订 (${count} 册独立典籍)</span>`;
        }
    };


    /**
     * 实时拉取并更新封面预览
     */
    window.refreshCoverPreview = async function() {
        const titleInput = document.getElementById('bindery-input-title');
        const authorInput = document.getElementById('bindery-input-author');
        const scopeSelect = document.getElementById('bindery-select-scope');
        const langSelect = document.getElementById('bindery-select-lang');
        const modeSelect = document.getElementById('bindery-select-cover-mode');
        const styleSelect = document.getElementById('bindery-select-cover-style');
        const imgEl = document.getElementById('bindery-cover-img');
        const badgeEl = document.getElementById('bindery-cover-badge');

        if (!imgEl) return;

        const payload = {
            title: titleInput ? titleInput.value.trim() : '',
            author: authorInput ? authorInput.value.trim() : '',
            scope: scopeSelect ? scopeSelect.value : 'all',
            lang: langSelect ? langSelect.value : 'zh',
            cover_mode: modeSelect ? modeSelect.value : 'auto',
            style: styleSelect ? styleSelect.value : 'dark_emerald'
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

    /**
     * 切换装订中枢 Tab (build: 装订新版 / shelf: 典籍货架)
     */
    window.switchBinderyTab = function(tab) {
        const pBuild = document.getElementById('bindery-panel-build');
        const pShelf = document.getElementById('bindery-panel-shelf');
        const tBuild = document.getElementById('btn-bindery-tab-build');
        const tShelf = document.getElementById('btn-bindery-tab-shelf');
        if (pBuild) pBuild.style.display = tab === 'build' ? 'flex' : 'none';
        if (pShelf) pShelf.style.display = tab === 'shelf' ? 'flex' : 'none';
        if (tBuild) tBuild.classList.toggle('active', tab === 'build');
        if (tShelf) tShelf.classList.toggle('active', tab === 'shelf');
        if (tab === 'shelf' && typeof window.fetchBinderyShelf === 'function') {
            window.fetchBinderyShelf();
        }
    };

    window._activeBinderyFormat = 'epub';
    window.selectBinderyFormat = function(fmtId) {
        window._activeBinderyFormat = fmtId;
        const e1 = document.getElementById('btn-driver-epub');
        const e2 = document.getElementById('btn-driver-webbook');
        if (e1) e1.classList.toggle('active', fmtId === 'epub');
        if (e2) e2.classList.toggle('active', fmtId === 'webbook');
    };
})();

