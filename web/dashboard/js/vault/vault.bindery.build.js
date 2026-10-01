/**
 * 📚 [V125.2] Illacme Plenipes Vault - Book Bindery Build & Packaging Shard
 * 职责：独立承载数字装订执行、参数收集、异步进度反馈、多语言矩阵构建与安全流式下载。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */
(function() {
    'use strict';

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
     * 🚀 执行装订编译流水线
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

        if (modeSelect && modeSelect.value === 'custom' && !window._binderyCustomCoverDataUri) {
            if (typeof window.showToast === 'function') window.showToast('请先选择或拖拽上传自定义封面图片', 'warning');
            return;
        }

        const payload = {
            format: window._activeBinderyFormat || 'epub',
            scope: scopeSelect ? scopeSelect.value : 'all',
            title: titleInput.value.trim() || undefined,
            author: authorInput ? authorInput.value.trim() || undefined : undefined,
            cover_mode: modeSelect ? modeSelect.value : 'auto',
            cover_style: styleSelect ? styleSelect.value : 'dark_emerald',
            custom_cover_image: (modeSelect && modeSelect.value === 'custom') ? window._binderyCustomCoverDataUri : undefined
        };

        const langMode = langSelect ? langSelect.value : 'zh';
        if (langMode === 'polyglot') {
            let checkedLangs = Array.from(document.querySelectorAll('.bindery-poly-cb:checked')).map(cb => cb.value);
            if (!checkedLangs.length) checkedLangs = ['zh', 'en'];
            else if (checkedLangs.length === 1) checkedLangs.push(checkedLangs[0] === 'zh' ? 'en' : 'zh');
            payload.languages = checkedLangs;
            payload.polyglot_mode = true;
            payload.target_lang = checkedLangs[0];
        } else if (langMode === 'matrix_batch') {
            const selectedLangs = Array.from(document.querySelectorAll('.bindery-matrix-cb:checked')).map(cb => cb.value);
            if (selectedLangs.length === 0) {
                if (typeof window.showToast === 'function') window.showToast('请至少勾选一个目标语种', 'warning');
                return;
            }
            payload.languages = selectedLangs;
        } else {
            payload.lang = langMode;
        }

        const formatMap = {
            epub: 'EPUB',
            webbook: 'WebBook',
            pdf: 'PDF 印本',
            docx: 'Word 文档',
            markdown: 'Markdown 合集',
            txt: 'TXT 便携文本'
        };
        const currentFmtName = formatMap[payload.format] || (payload.format ? payload.format.toUpperCase() : '电子书');

        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.innerHTML = payload.polyglot_mode 
            ? `<span>⚙️ 正在制作多语对照${currentFmtName}...</span>` 
            : (payload.languages ? `<span>⚙️ 正在并发制作 (${payload.languages.length} 本)...</span>` : `<span>⚙️ 正在制作 ${currentFmtName}...</span>`);

        const isLight = document.documentElement.getAttribute('data-theme') === 'light';

        if (statusArea) {
            statusArea.style.display = 'block';
            statusArea.style.background = isLight ? 'rgba(2, 132, 199, 0.08)' : 'rgba(0, 242, 254, 0.08)';
            statusArea.style.border = isLight ? '1px solid rgba(2, 132, 199, 0.25)' : '1px solid rgba(0, 242, 254, 0.25)';
            statusArea.style.color = isLight ? '#0284c7' : '#00f2fe';
            statusArea.innerHTML = payload.polyglot_mode 
                ? `⏳ 正在按整篇并列对齐 ${payload.languages.map(l => l.toUpperCase()).join(' ⇋ ')} 多语对照内容并生成 ${currentFmtName}...` 
                : (payload.languages ? `⏳ 正在并发制作 ${payload.languages.map(l => l.toUpperCase()).join(', ')} 多语言${currentFmtName}...` : `⏳ 正在遍历文库章节、提取元数据并生成 ${currentFmtName}...`);
        }

        if (typeof window.addAudit === 'function') {
            const desc = window._binderyMatrixMode ? `多语言[${payload.languages.join(',')}]` : payload.lang;
            window.addAudit(`📚 开始制作${currentFmtName}: [${payload.title || '默认书名'}] (${desc})`);
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
                    Object.assign(statusArea.style, {
                        background: isLight ? '#f0fdf4' : 'rgba(16, 185, 129, 0.12)',
                        border: isLight ? '1px solid #86efac' : '1px solid rgba(16, 185, 129, 0.35)',
                        color: isLight ? '#15803d' : '#10b981'
                    });
                    statusArea.innerHTML = tpl.buildSuccessStatusHtml(result, formattedSize);
                    const bCard = document.querySelector('.bindery-modal-card');
                    if (bCard) bCard.scrollTop = 0;
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
                } else {
                    if (typeof window.addAudit === 'function') window.addAudit(`✅ 电子书已落盘: ${result.filename} (${formattedSize})`);
                    if (typeof window.showToast === 'function') window.showToast(`电子书 ${result.filename} 装订成功！`, 'success');
                }
            } else {
                throw new Error((result && (result.detail || result.error || result.message)) || '装订返回异常');
            }
        } catch (err) {
            console.error('[Bindery] 装订流程异常:', err);
            if (statusArea) {
                statusArea.style.display = 'block';
                Object.assign(statusArea.style, {
                    background: isLight ? 'rgba(239, 68, 68, 0.08)' : 'rgba(239, 68, 68, 0.12)',
                    border: isLight ? '1px solid rgba(239, 68, 68, 0.25)' : '1px solid rgba(239, 68, 68, 0.35)',
                    color: isLight ? '#dc2626' : '#ff6b6b'
                });
                statusArea.innerHTML = `❌ 装订失败：${tpl.esc(err.message || '系统内部异常')}`;
            }
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
            submitBtn.innerHTML = `<span>重新装订</span>`;
        }
    };
})();
