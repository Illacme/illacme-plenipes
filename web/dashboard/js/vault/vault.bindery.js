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
            ensureStyles: () => {}, esc: s => s || '', formatSize: b => `${b} B`,
            buildLoadingHtml: () => '<div>正在加载...</div>',
            buildModalCardHtml: () => '<div>装订面板</div>',
            buildSuccessStatusHtml: () => '<div>装订成功</div>'
        };
    }

    /** 唤醒数字装订对话框 */
    window.openBinderyModal = async function(preselectedScope = 'all', singleDoc = null, initialFormat = null) {
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

        _binderyModalEl.style.opacity = '1';
        _binderyModalEl.style.pointerEvents = 'auto';
        _binderyModalEl.innerHTML = tpl.buildLoadingHtml();

        let scopesData = {
            site_name: 'Illacme Plenipes', default_author: 'Illacme Editorial Team',
            categories: [{ id: 'all', name: '全部原稿 (全库总集)' }],
            formats: [{ id: 'epub', name: 'EPUB 3.0 流式电子书', ext: '.epub', recommended: true }]
        };

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/scopes');
            if (res && res.ok) scopesData = await res.json();
            else if (res && res.success) scopesData = res;
        } catch (e) {
            console.warn('[Bindery] 获取装订范围失败，降级使用预设:', e);
        }

        const currentScope = preselectedScope || 'all';
        if (singleDoc) scopesData.single_doc = singleDoc;
        else if (currentScope.startsWith('single:')) scopesData.single_doc = { rel_path: currentScope.slice(7), title: currentScope.slice(7) };
        const defaultTitle = (scopesData.single_doc && scopesData.single_doc.title) ? scopesData.single_doc.title : (scopesData.site_name ? `${scopesData.site_name} · 数字出版集` : '数字出版合集');

        _binderyModalEl.innerHTML = tpl.buildModalCardHtml(scopesData, currentScope, defaultTitle);

        let debounceTimer = null;
        const triggerDebouncedPreview = () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                window.refreshCoverPreview();
                if (typeof window.resetBinderySubmitBtn === 'function') window.resetBinderySubmitBtn();
            }, 250);
        };
        ['bindery-input-title', 'bindery-input-author'].forEach(id => {
            const el = document.getElementById(id); if (el) el.addEventListener('input', triggerDebouncedPreview);
        });
        ['bindery-select-scope', 'bindery-select-lang'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('change', () => { window.refreshCoverPreview(); if (typeof window.resetBinderySubmitBtn === 'function') window.resetBinderySubmitBtn(); });
        });

        const coverBox = document.getElementById('bindery-cover-preview-box');
        if (coverBox) {
            coverBox.addEventListener('dragover', (e) => { e.preventDefault(); coverBox.style.borderColor = '#10b981'; });
            coverBox.addEventListener('dragleave', () => { coverBox.style.borderColor = 'rgba(16,185,129,0.35)'; });
            coverBox.addEventListener('drop', (e) => {
                e.preventDefault(); coverBox.style.borderColor = 'rgba(16,185,129,0.35)';
                if (e.dataTransfer?.files?.[0]) window.handleBinderyCoverUpload(e.dataTransfer.files[0]);
            });
        }

        window._binderyMatrixMode = false;
        if (window._binderySuccessTimer) { clearTimeout(window._binderySuccessTimer); window._binderySuccessTimer = null; }
        if (initialFormat && ['epub', 'webbook', 'pdf'].includes(initialFormat)) window.selectBinderyFormat(initialFormat);
        window.refreshCoverPreview();
        if (typeof window.fetchBinderyShelf === 'function') window.fetchBinderyShelf();

        document.querySelectorAll('.bindery-matrix-cb').forEach(cb => {
            cb.addEventListener('change', () => { window.updateMatrixSubmitBtn(); if (typeof window.resetBinderySubmitBtn === 'function') window.resetBinderySubmitBtn(); });
        });
    };

    /** 切换出版语种模式（单语 / 多语对照 / 多语批量） */
    window.onBinderyLangModeChange = function(val) {
        val = val || document.getElementById('bindery-select-lang')?.value || 'zh';
        const chipsRow = document.getElementById('bindery-matrix-chips-row'), polyChipsRow = document.getElementById('bindery-poly-chips-row');
        const badge = document.getElementById('bindery-lang-hint-badge'), submitBtn = document.getElementById('btn-execute-binding');
        const toggleBtn = document.getElementById('bindery-matrix-toggle-btn');
        if (chipsRow) chipsRow.style.display = val === 'matrix_batch' ? 'flex' : 'none';
        if (polyChipsRow) polyChipsRow.style.display = val === 'polyglot' ? 'flex' : 'none';
        if (toggleBtn) toggleBtn.style.display = val === 'matrix_batch' ? 'inline-block' : 'none';

        if (val === 'polyglot') {
            window.updatePolyglotSubmitBtn();
        } else if (val === 'matrix_batch') {
            if (badge) { badge.textContent = '📦 多版本并发'; badge.style.color = '#38bdf8'; }
            const count = document.querySelectorAll('.bindery-matrix-cb:checked').length || 3;
            if (submitBtn) submitBtn.innerHTML = `<span>🌍 并发制作多语电子书 (${count} 本)</span>`;
        } else {
            if (badge) { badge.textContent = '单语言版'; badge.style.color = ''; }
            const langMap = { 'zh': '中文版', 'en': '英文版', 'ja': '日文版' };
            if (submitBtn) submitBtn.innerHTML = `<span>🚀 立即制作 (${langMap[val] || (val || '').toUpperCase()})</span>`;
        }
        if (typeof window.refreshCoverPreview === 'function') window.refreshCoverPreview();
    };

    /** 联动更新多语对照复选芯片与提交按钮文案 */
    window.updatePolyglotSubmitBtn = function() {
        const checkedLangs = Array.from(document.querySelectorAll('.bindery-poly-cb:checked')).map(cb => cb.value);
        const badge = document.getElementById('bindery-lang-hint-badge'), submitBtn = document.getElementById('btn-execute-binding');
        if (badge) {
            if (checkedLangs.length <= 1) { badge.textContent = '⚠️ 请至少勾选2个语种'; badge.style.color = '#f59e0b'; }
            else if (checkedLangs.length === 2) { badge.textContent = `双语对照 (${checkedLangs.join(' ⇋ ').toUpperCase()})`; badge.style.color = '#10b981'; }
            else { badge.textContent = `多语对照 (${checkedLangs.length} 语并列)`; badge.style.color = '#10b981'; }
        }
        if (submitBtn && document.getElementById('bindery-select-lang')?.value === 'polyglot') {
            submitBtn.innerHTML = `<span>📑 制作多语对照电子书 (${Math.max(2, checkedLangs.length)} 栏并列)</span>`;
        }
    };

    /** 全选/反选矩阵语种 */
    window.toggleAllBinderyMatrixLangs = function() {
        const cbs = document.querySelectorAll('.bindery-matrix-cb'); if (!cbs.length) return;
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
        if (langVal === 'polyglot') { if (typeof window.updatePolyglotSubmitBtn === 'function') window.updatePolyglotSubmitBtn(); }
        else if (langVal === 'matrix_batch') submitBtn.innerHTML = `<span>🌍 并发制作多语电子书 (${count} 本独立版本)</span>`;
    };
    window.updatePolyglotColumnsUI = function() { if (typeof window.updatePolyglotSubmitBtn === 'function') window.updatePolyglotSubmitBtn(); };

    /** 实时拉取并更新封面预览与自定义封面联动 */
    window.refreshCoverPreview = async function() {
        const imgEl = document.getElementById('bindery-cover-img'); if (!imgEl) return;
        const badgeEl = document.getElementById('bindery-cover-badge'), phEl = document.getElementById('bindery-cover-none-ph');
        const styleSel = document.getElementById('bindery-select-cover-style'), uploadBtn = document.getElementById('btn-bindery-upload-cover');
        const gVal = id => document.getElementById(id)?.value || '';
        const coverMode = gVal('bindery-select-cover-mode') || 'auto';

        if (coverMode === 'custom') {
            if (styleSel) styleSel.style.display = 'none';
            if (uploadBtn) uploadBtn.style.display = 'inline-flex';
            const hasC = Boolean(window._binderyCustomCoverDataUri);
            if (phEl) { phEl.style.display = hasC ? 'none' : 'block'; if (!hasC) phEl.innerHTML = '📁<br/><span style="font-size:0.62rem; color:#10b981;">待上传</span>'; }
            imgEl.style.display = hasC ? 'block' : 'none';
            imgEl.src = hasC ? window._binderyCustomCoverDataUri : '';
            if (badgeEl) { badgeEl.textContent = hasC ? '📁 自定义封面' : '📁 待选图片'; badgeEl.style.color = hasC ? '#10b981' : '#f59e0b'; badgeEl.style.borderColor = hasC ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'; }
            return;
        }

        if (styleSel) styleSel.style.display = 'block';
        if (uploadBtn) uploadBtn.style.display = 'none';

        const payload = {
            title: gVal('bindery-input-title').trim(), author: gVal('bindery-input-author').trim(),
            scope: gVal('bindery-select-scope') || 'all', lang: gVal('bindery-select-lang') || 'zh',
            cover_mode: coverMode, style: gVal('bindery-select-cover-style') || 'dark_emerald'
        };

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/cover-preview', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
            });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (data && data.success) {
                if (data.mode === 'none' || !data.data_uri) {
                    imgEl.src = ''; imgEl.style.display = 'none';
                    if (phEl) { phEl.style.display = 'block'; phEl.innerHTML = '📰<br/><span style="font-size:0.62rem; color:#38bdf8;">纯净免封</span>'; }
                    if (badgeEl) { badgeEl.textContent = '📰 纯净免封'; badgeEl.style.color = '#38bdf8'; badgeEl.style.borderColor = 'rgba(56, 189, 248, 0.4)'; }
                } else {
                    if (phEl) phEl.style.display = 'none';
                    imgEl.style.display = 'block'; imgEl.src = data.data_uri;
                    if (badgeEl) {
                        const isNat = data.mode === 'native';
                        badgeEl.textContent = isNat ? '📂 文库原图' : '✨ 艺术排版';
                        badgeEl.style.color = isNat ? '#38bdf8' : '#10b981';
                        badgeEl.style.borderColor = isNat ? 'rgba(56, 189, 248, 0.4)' : 'rgba(16, 185, 129, 0.4)';
                    }
                }
            }
        } catch (e) { console.warn('[Bindery] 刷新封面预览失败:', e); }
    };

    /** 📁 处理用户自定义封面上传与即时预览，并全自动同步登记至设计中心媒体资产库 */
    window.handleBinderyCoverUpload = function(file) {
        if (!file || !file.type.startsWith('image/')) {
            if (typeof window.showToast === 'function') window.showToast('请选择有效的图片文件 (PNG/JPG/WEBP)', 'warning');
            return;
        }
        const reader = new FileReader();
        reader.onload = function(e) {
            window._binderyCustomCoverDataUri = e.target.result;
            const modeSel = document.getElementById('bindery-select-cover-mode');
            if (modeSel) modeSel.value = 'custom';
            window.refreshCoverPreview();
            if (typeof window.showToast === 'function') window.showToast(`已加载自定义封面: ${file.name}`, 'success');
            try {
                const fd = new FormData();
                fd.append('file', file);
                fd.append('prompt', `装订工坊自定义封面: ${file.name}`);
                const fetchFunc = window.authFetch || window.apiFetch || window.fetch;
                fetchFunc('/api/design/assets/upload', { method: 'POST', body: fd })
                    .then(r => r.json()).then(d => {
                        if (d?.success && typeof window.refreshDesignAssets === 'function') window.refreshDesignAssets();
                    }).catch(err => console.warn('[Bindery] 媒体资产预检:', err));
            } catch (err) { console.warn('[Bindery] 媒体资产异步入库:', err); }
        };
        reader.readAsDataURL(file);
    };

    window.closeBinderyModal = function() {
        if (_binderyModalEl) { _binderyModalEl.style.opacity = '0'; _binderyModalEl.style.pointerEvents = 'none'; }
    };

    window.switchBinderyTab = function(tab) {
        const pBuild = document.getElementById('bindery-panel-build'), pShelf = document.getElementById('bindery-panel-shelf'), tBuild = document.getElementById('btn-bindery-tab-build'), tShelf = document.getElementById('btn-bindery-tab-shelf'), hActions = document.getElementById('bindery-shelf-header-actions');
        if (pBuild) pBuild.style.display = tab === 'build' ? 'flex' : 'none';
        if (pShelf) pShelf.style.display = tab === 'shelf' ? 'flex' : 'none';
        tBuild?.classList.toggle('active', tab === 'build');
        tShelf?.classList.toggle('active', tab === 'shelf');
        if (hActions) hActions.style.display = tab === 'shelf' ? 'flex' : 'none';
        if (tab === 'shelf' && typeof window.fetchBinderyShelf === 'function') window.fetchBinderyShelf();
        if (tab === 'build' && window._binderyShelfBatchMode && typeof window.toggleBinderyShelfBatchMode === 'function') window.toggleBinderyShelfBatchMode();
    };

    /** 📂 在操作系统文件管理器中高亮定位物理文件 */
    window.revealBookInFolder = async function(filename) {
        if (!filename) return;
        const targetPath = filename.startsWith('dist/') ? filename : `dist/books/${filename}`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/system/reveal-file', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path: targetPath })
            });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (data?.success && typeof window.showToast === 'function') window.showToast(data.message || '📂 已在系统文件管理器中定位', 'success');
            else if (typeof window.showToast === 'function') window.showToast(`⚠️ ${data?.error || '未能打开系统所在文件夹'}`, 'warning');
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
        if (window._binderySuccessTimer) { clearTimeout(window._binderySuccessTimer); window._binderySuccessTimer = null; }
        const submitBtn = document.getElementById('btn-execute-binding'), cancelBtn = document.getElementById('btn-bindery-cancel');
        if (cancelBtn) cancelBtn.textContent = '取消';
        if (!submitBtn) return;
        submitBtn.disabled = false; submitBtn.style.opacity = '1';
        const langSelect = document.getElementById('bindery-select-lang'), langVal = langSelect?.value || 'zh';
        if (langVal === 'polyglot') { if (typeof window.updatePolyglotSubmitBtn === 'function') window.updatePolyglotSubmitBtn(); return; }
        if (langVal === 'matrix_batch') { if (typeof window.updateMatrixSubmitBtn === 'function') window.updateMatrixSubmitBtn(); return; }
        let langLabel = '';
        const opt = langSelect?.selectedOptions?.[0];
        if (opt) {
            const raw = (opt.textContent || '').replace(/^[^\w\u4e00-\u9fa5\u3040-\u30ff]+/u, '').replace(/\s*\(.*?\)\s*$/, '').trim();
            if (raw) langLabel = raw.includes('版') ? raw : raw + '版';
        }
        if (!langLabel) langLabel = { 'zh': '简体中文版', 'en': 'English版', 'ja': '日本語版' }[langVal] || (langVal.toUpperCase() + '版');
        submitBtn.innerHTML = `<span>🚀 立即装订 (${langLabel})</span>`;
    };
})();

