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

        // 📱 移动端大纲浮动按钮与抽屉 (Mobile TOC Drawer)
        initMobileTOCDrawer(headings, tocList);

        // ScrollSpy 逻辑 (基于 IntersectionObserver 与滚动触底双重判定)
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -75% 0px',
            threshold: 0
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    updateActiveTOCLink(id);
                }
            });
        }, observerOptions);

        headings.forEach(h => observer.observe(h));

        // 触底自愈：滚动至页面底部时自动激活最后一个标题
        window.addEventListener('scroll', () => {
            if ((window.innerHeight + window.scrollY) >= (document.documentElement.scrollHeight - 30)) {
                if (headings.length > 0) {
                    const lastId = headings[headings.length - 1].id;
                    updateActiveTOCLink(lastId);
                }
            }
        }, { passive: true });
    }

    function updateActiveTOCLink(id) {
        document.querySelectorAll('.toc-link').forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
        });
    }

    /**
     * 📱 初始化移动端大纲浮动气泡与抽屉面板
     */
    function initMobileTOCDrawer(headings, tocList) {
        let mobileTOCBtn = document.getElementById('mobile-toc-fab');
        let mobileTOCDrawer = document.getElementById('mobile-toc-drawer');
        if (!mobileTOCBtn) {
            mobileTOCBtn = document.createElement('button');
            mobileTOCBtn.id = 'mobile-toc-fab';
            mobileTOCBtn.className = 'mobile-toc-fab';
            mobileTOCBtn.type = 'button';
            mobileTOCBtn.setAttribute('aria-label', '目录大纲');
            mobileTOCBtn.innerHTML = '<span class="fab-icon">🌲</span><span class="fab-text">大纲</span>';
            document.body.appendChild(mobileTOCBtn);

            mobileTOCDrawer = document.createElement('div');
            mobileTOCDrawer.id = 'mobile-toc-drawer';
            mobileTOCDrawer.className = 'mobile-toc-drawer';
            mobileTOCDrawer.innerHTML = `
                <div class="drawer-backdrop"></div>
                <div class="drawer-content">
                    <div class="drawer-header">
                        <span class="drawer-title">🌲 目录大纲</span>
                        <button class="drawer-close" type="button" aria-label="关闭">✕</button>
                    </div>
                    <div class="drawer-body"></div>
                </div>
            `;
            document.body.appendChild(mobileTOCDrawer);

            const drawerBody = mobileTOCDrawer.querySelector('.drawer-body');
            const clonedList = tocList.cloneNode(true);
            
            // 为克隆的大纲绑定点击自动平滑滚动并关闭抽屉
            clonedList.querySelectorAll('.toc-link').forEach(a => {
                a.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = a.getAttribute('href').replace('#', '');
                    const targetEl = document.getElementById(targetId);
                    if (targetEl) {
                        targetEl.scrollIntoView({ behavior: 'smooth' });
                    }
                    mobileTOCDrawer.classList.remove('active');
                });
            });
            drawerBody.appendChild(clonedList);

            const closeBtn = mobileTOCDrawer.querySelector('.drawer-close');
            const backdrop = mobileTOCDrawer.querySelector('.drawer-backdrop');

            const toggleDrawer = (show) => {
                mobileTOCDrawer.classList.toggle('active', show);
            };

            mobileTOCBtn.addEventListener('click', () => toggleDrawer(true));
            closeBtn.addEventListener('click', () => toggleDrawer(false));
            backdrop.addEventListener('click', () => toggleDrawer(false));
        }
    }

    // 挂载至全局 window 状态总线
    window.initReadingProgress = initReadingProgress;
    window.initDynamicTOC = initDynamicTOC;

})(window);
