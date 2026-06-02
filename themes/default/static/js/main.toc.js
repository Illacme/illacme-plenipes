/**
 * Illacme-plenipes Sovereign Theme - Dynamic TOC & Reading Progress
 * 职责：负责文章动态目录生成（ScrollSpy）及高频滚动进度条更新。
 * 🛡️ [AEL-Iter-v11.8]：高内聚 TOC 模块。实装动画帧（rAF）物理节流阀，杜绝重排掉帧。
 */

(function (window) {
    'use strict';

    /**
     * 初始化阅读进度条，并使用 requestAnimationFrame 进行高频滚动节流
     */
    function initReadingProgress() {
        const progressBar = document.getElementById('reading-progress');
        if (!progressBar) return;

        let scrollTicking = false;

        window.addEventListener('scroll', () => {
            if (!scrollTicking) {
                window.requestAnimationFrame(() => {
                    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
                    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                    if (height > 0) {
                        const scrolled = (winScroll / height) * 100;
                        progressBar.style.width = scrolled + '%';
                    }
                    scrollTicking = false;
                });
                scrollTicking = true;
            }
        });
    }

    /**
     * 🌲 动态目录生成与 ScrollSpy 导航系统
     */
    function initDynamicTOC() {
        const article = document.querySelector('.prose-sovereign');
        const tocContainer = document.getElementById('toc-container');
        if (!article || !tocContainer) return;

        const headings = article.querySelectorAll('h2, h3');
        if (headings.length === 0) {
            const tocWidget = document.getElementById('dynamic-toc');
            if (tocWidget) tocWidget.style.display = 'none';
            return;
        }

        const tocList = document.createElement('ul');
        tocList.className = 'toc-list';

        headings.forEach((heading, index) => {
            const id = heading.id || `heading-${index}`;
            heading.id = id;

            const li = document.createElement('li');
            li.className = `toc-item toc-level-${heading.tagName.toLowerCase()}`;
            
            const a = document.createElement('a');
            a.href = `#${id}`;
            a.className = 'toc-link';
            a.textContent = heading.textContent.replace('#', '').trim();
            
            a.addEventListener('click', (e) => {
                e.preventDefault();
                const targetEl = document.getElementById(id);
                if (targetEl) {
                    targetEl.scrollIntoView({ behavior: 'smooth' });
                }
            });

            li.appendChild(a);
            tocList.appendChild(li);
        });

        tocContainer.appendChild(tocList);

        // ScrollSpy 逻辑 (基于 IntersectionObserver)
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -80% 0px',
            threshold: 0
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    document.querySelectorAll('.toc-link').forEach(link => {
                        link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
                    });
                }
            });
        }, observerOptions);

        headings.forEach(h => observer.observe(h));
    }

    // 挂载至全局 window 状态总线
    window.initReadingProgress = initReadingProgress;
    window.initDynamicTOC = initDynamicTOC;

})(window);
