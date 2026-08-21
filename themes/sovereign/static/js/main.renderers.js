/**
 * Illacme-plenipes Sovereign Theme - Dynamic Diagram & Math Renderers
 * 职责：按需惰性加载 Mermaid 架构图与 KaTeX 数学公式渲染器，实现 100% 零外部依赖本地化渲染。
 * 🛡️ [SOP-03 UI/UX Sovereignty]：100% 纯本地离线静态资产加载，彻底规避公网断网与脱机使用风险。
 */

(function (window) {
    'use strict';

    /**
     * 自动探测当前页面的 static/ 根目录相对路径
     */
    function getStaticRoot() {
        const selfScript = document.querySelector('script[src*="main.renderers.js"]');
        if (selfScript) {
            const src = selfScript.getAttribute('src') || '';
            const idx = src.indexOf('js/main.renderers.js');
            if (idx !== -1) {
                return src.substring(0, idx); // 例如 "../static/" 或 "./static/" 或 "static/"
            }
        }
        return 'static/';
    }

    /**
     * 动态加载脚本 (带本地优先与 CDN 降级)
     */
    function loadScript(src, fallbackSrc) {
        return new Promise((resolve, reject) => {
            const existing = document.querySelector(`script[src="${src}"]`);
            if (existing) {
                if (existing.dataset.loaded) return resolve();
                existing.addEventListener('load', resolve);
                existing.addEventListener('error', reject);
                return;
            }
            const script = document.createElement('script');
            script.src = src;
            script.async = true;
            script.onload = () => {
                script.dataset.loaded = 'true';
                resolve();
            };
            script.onerror = () => {
                if (fallbackSrc && fallbackSrc !== src) {
                    console.warn(`⚠️ [Sovereign] 本地资源载入异常，尝试降级: ${src} -> ${fallbackSrc}`);
                    loadScript(fallbackSrc).then(resolve).catch(reject);
                } else {
                    reject(new Error(`Failed to load script: ${src}`));
                }
            };
            document.head.appendChild(script);
        });
    }

    /**
     * 动态加载外部样式表
     */
    function loadCSS(href) {
        if (document.querySelector(`link[href="${href}"]`)) return;
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        document.head.appendChild(link);
    }

    /**
     * 📊 渲染 Mermaid 架构与流程图
     */
    async function initMermaidRenderers() {
        const prose = document.querySelector('.prose-sovereign');
        if (!prose) return;

        // 查找所有标识为 mermaid 的代码块与容器
        const mermaidNodes = prose.querySelectorAll('pre.mermaid, .sovereign-mermaid-diagram pre, pre code.language-mermaid, pre code.lang-mermaid');
        if (mermaidNodes.length === 0) return;

        const staticRoot = getStaticRoot();
        const localMermaid = `${staticRoot}vendor/mermaid/mermaid.min.js`;
        const cdnMermaid = 'https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js';

        try {
            // 🛡️ 100% 优先加载本地静态资产
            await loadScript(localMermaid, cdnMermaid);
            if (!window.mermaid) return;

            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            window.mermaid.initialize({
                startOnLoad: false,
                theme: isDark ? 'dark' : 'default',
                securityLevel: 'loose',
                themeVariables: isDark ? {
                    darkMode: true,
                    background: '#14141a',
                    primaryColor: '#00f5ff',
                    primaryTextColor: '#f8f8fc',
                    primaryBorderColor: 'rgba(0, 245, 255, 0.4)',
                    lineColor: '#a1a1b5'
                } : {
                    darkMode: false,
                    primaryColor: '#0071e3',
                    primaryTextColor: '#1a1a1e'
                }
            });

            for (let i = 0; i < mermaidNodes.length; i++) {
                const node = mermaidNodes[i];
                const rawCode = node.textContent.trim();
                if (!rawCode) continue;

                const existingContainer = node.closest('.sovereign-mermaid-diagram');
                const container = existingContainer || document.createElement('div');
                if (!existingContainer) {
                    container.className = 'sovereign-mermaid-diagram';
                    container.id = `mermaid-chart-${i}`;
                    node.parentNode.insertBefore(container, node);
                }
                node.style.display = 'none';

                try {
                    const { svg } = await window.mermaid.render(`mermaid-svg-${i}`, rawCode);
                    container.innerHTML = svg;
                } catch (renderErr) {
                    console.warn('⚠️ [Sovereign] Mermaid 渲染警告:', renderErr);
                    node.style.display = '';
                    if (!existingContainer) container.remove();
                }
            }
        } catch (e) {
            console.warn('⚠️ [Sovereign] 无法加载 Mermaid 渲染引擎:', e);
        }
    }

    /**
     * 📐 渲染 LaTeX 数学公式
     */
    async function initMathRenderers() {
        const prose = document.querySelector('.prose-sovereign');
        if (!prose) return;

        const content = prose.innerHTML;
        // 检测是否存在 $$ 或 $ 标识的公式语法
        if (!content.includes('$$') && !content.includes('\\(') && !content.includes('arithmatex')) return;

        const staticRoot = getStaticRoot();
        const localKatexCss = `${staticRoot}vendor/katex/katex.min.css`;
        const localKatexJs = `${staticRoot}vendor/katex/katex.min.js`;
        const localAutoRenderJs = `${staticRoot}vendor/katex/auto-render.min.js`;

        try {
            loadCSS(localKatexCss);
            await loadScript(localKatexJs, 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js');
            await loadScript(localAutoRenderJs, 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js');

            if (window.renderMathInElement) {
                window.renderMathInElement(prose, {
                    delimiters: [
                        { left: '$$', right: '$$', display: true },
                        { left: '$', right: '$', display: false },
                        { left: '\\(', right: '\\)', display: false },
                        { left: '\\[', right: '\\]', display: true }
                    ],
                    throwOnError: false
                });
            }
        } catch (e) {
            console.warn('⚠️ [Sovereign] 无法加载 KaTeX 公式渲染引擎:', e);
        }
    }

    /**
     * 总入口
     */
    function initCustomRenderers() {
        initMermaidRenderers();
        initMathRenderers();
    }

    // 挂载至全局 window 状态总线
    window.initCustomRenderers = initCustomRenderers;

})(window);
