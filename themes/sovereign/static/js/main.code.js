/**
 * Illacme-plenipes Sovereign Theme - Code Block Enhancements
 * 职责：为 Markdown 代码块注入一键复制按钮、语言标识与交互微动效。
 * 🛡️ [AEL-Iter-v11.8]：独立高内聚模块，完全遵循零外部依赖与无障碍交互标准。
 */

(function (window) {
    'use strict';

    /**
     * 初始化代码块增强功能
     */
    function initCodeBlocks() {
        const prose = document.querySelector('.prose-sovereign');
        if (!prose) return;

        const lang = (document.documentElement.getAttribute('lang') || 'zh').toLowerCase();
        const isChinese = lang.startsWith('zh');
        const copyLabel = isChinese ? '复制' : 'Copy';
        const copiedLabel = isChinese ? '已复制!' : 'Copied!';

        const codeBlocks = prose.querySelectorAll('pre');

        codeBlocks.forEach((pre) => {
            if (pre.dataset.enhanced) return;
            if (pre.classList.contains('mermaid') || pre.closest('.sovereign-mermaid-diagram')) return;
            pre.dataset.enhanced = 'true';

            // 提取代码语言
            const codeEl = pre.querySelector('code');
            let detectedLang = 'text';
            if (codeEl) {
                const classes = Array.from(codeEl.classList);
                const langClass = classes.find(c => c.startsWith('language-') || c.startsWith('lang-'));
                if (langClass) {
                    detectedLang = langClass.replace(/^(language-|lang-)/, '').toLowerCase();
                } else if (pre.className) {
                    const match = pre.className.match(/(?:language-|lang-|codehilite\s+)(\w+)/);
                    if (match) detectedLang = match[1].toLowerCase();
                }
            }

            // 构建外层包裹容器
            const wrapper = document.createElement('div');
            wrapper.className = 'code-block-wrapper';

            // 构建代码块顶部工具栏
            const header = document.createElement('div');
            header.className = 'code-block-header';

            const langBadge = document.createElement('span');
            langBadge.className = 'code-lang-badge';
            langBadge.textContent = detectedLang.toUpperCase();

            const copyBtn = document.createElement('button');
            copyBtn.type = 'button';
            copyBtn.className = 'code-copy-btn';
            copyBtn.innerHTML = `<span class="copy-icon">📋</span><span class="copy-text">${copyLabel}</span>`;
            copyBtn.setAttribute('aria-label', copyLabel);

            copyBtn.addEventListener('click', async () => {
                const textToCopy = codeEl ? codeEl.innerText : pre.innerText;
                try {
                    await navigator.clipboard.writeText(textToCopy);
                    copyBtn.innerHTML = `<span class="copy-icon">✅</span><span class="copy-text">${copiedLabel}</span>`;
                    copyBtn.classList.add('copied');
                    setTimeout(() => {
                        copyBtn.innerHTML = `<span class="copy-icon">📋</span><span class="copy-text">${copyLabel}</span>`;
                        copyBtn.classList.remove('copied');
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy code: ', err);
                }
            });

            header.appendChild(langBadge);
            header.appendChild(copyBtn);

            // 替换结构
            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(header);
            wrapper.appendChild(pre);
        });
    }

    // 挂载至全局 window 状态总线
    window.initCodeBlocks = initCodeBlocks;

})(window);
