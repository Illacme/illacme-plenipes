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
     * 触发异步合卷装订并下载
     */
    window.executeBookBinding = async function() {
        const tpl = _getTemplates();
        const titleInput = document.getElementById('bindery-input-title');
        const authorInput = document.getElementById('bindery-input-author');
        const scopeSelect = document.getElementById('bindery-select-scope');
        const langSelect = document.getElementById('bindery-select-lang');
        const statusArea = document.getElementById('bindery-status-area');
        const submitBtn = document.getElementById('btn-execute-binding');

        if (!titleInput || !submitBtn) return;

        const payload = {
            format: 'epub',
            scope: scopeSelect ? scopeSelect.value : 'all',
            lang: langSelect ? langSelect.value : 'zh',
            title: titleInput.value.trim() || undefined,
            author: authorInput ? authorInput.value.trim() || undefined : undefined
        };

        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.innerHTML = `<span>⚙️ 正在装订...</span>`;

        const isLight = document.documentElement.getAttribute('data-theme') === 'light';

        if (statusArea) {
            statusArea.style.display = 'block';
            statusArea.style.background = isLight ? 'rgba(2, 132, 199, 0.08)' : 'rgba(0, 242, 254, 0.08)';
            statusArea.style.border = isLight ? '1px solid rgba(2, 132, 199, 0.25)' : '1px solid rgba(0, 242, 254, 0.25)';
            statusArea.style.color = isLight ? '#0284c7' : '#00f2fe';
            statusArea.innerHTML = `⏳ 正在遍历文库章节、提取 Frontmatter 并编译 EPUB 3.0 实体...`;
        }

        if (typeof window.addAudit === 'function') {
            window.addAudit(`📚 开始执行数字装订: [${payload.title || '默认书名'}] (${payload.scope})`);
        }

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/build', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let result = null;
            if (res && typeof res.json === 'function') {
                result = await res.json();
            } else {
                result = res;
            }

            if (result && result.success) {
                const formattedSize = tpl.formatSize(result.file_size);

                if (statusArea) {
                    statusArea.style.background = isLight ? 'rgba(16, 185, 129, 0.08)' : 'rgba(16, 185, 129, 0.12)';
                    statusArea.style.border = isLight ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(16, 185, 129, 0.35)';
                    statusArea.style.color = isLight ? '#047857' : '#10b981';
                    statusArea.innerHTML = tpl.buildSuccessStatusHtml(result, formattedSize);
                }

                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
                submitBtn.innerHTML = `<span>✨ 装订成功</span>`;

                if (typeof window.addAudit === 'function') {
                    window.addAudit(`✅ 电子书已落盘: ${result.filename} (${formattedSize})`);
                }
                if (typeof window.showToast === 'function') {
                    window.showToast(`电子书 ${result.filename} 装订成功！`, 'success');
                }

                const dlLink = document.createElement('a');
                dlLink.href = result.download_url;
                dlLink.download = result.filename;
                document.body.appendChild(dlLink);
                dlLink.click();
                setTimeout(() => dlLink.remove(), 1000);

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
