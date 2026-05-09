/**
 * Illacme-plenipes Sovereign Theme - Core Logic
 * 🛡️ [AEL-Iter-v11.8]：主权交互引擎核心。
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSearch();
    initReadingProgress();
    initDynamicTOC();
    initMobileEnhancements();
});

/**
 * 💡 主题管理系统
 */
function initTheme() {
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateToggleUI(savedTheme);

    toggleBtn.addEventListener('click', () => {
        const theme = document.documentElement.getAttribute('data-theme');
        const targetTheme = theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', targetTheme);
        localStorage.setItem('theme', targetTheme);
        updateToggleUI(targetTheme);
    });
}

function updateToggleUI(theme) {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    const icon = btn.querySelector('.btn-icon');
    const label = btn.querySelector('.btn-label');
    if (theme === 'dark') {
        if (icon) icon.textContent = '☀️';
        if (label) label.textContent = 'Light';
    } else {
        if (icon) icon.textContent = '🌙';
        if (label) label.textContent = 'Dark';
    }
}

/**
 * 📈 阅读进度条系统
 */
function initReadingProgress() {
    const progressBar = document.getElementById('reading-progress');
    if (!progressBar) return;

    window.addEventListener('scroll', () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        progressBar.style.width = scrolled + "%";
    });
}

/**
 * 🌲 动态目录生成与 ScrollSpy
 */
function initDynamicTOC() {
    const article = document.querySelector('.prose-sovereign');
    const tocContainer = document.getElementById('toc-container');
    if (!article || !tocContainer) return;

    const headings = article.querySelectorAll('h2, h3');
    if (headings.length === 0) {
        document.getElementById('dynamic-toc').style.display = 'none';
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
            document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
        });

        li.appendChild(a);
        tocList.appendChild(li);
    });

    tocContainer.appendChild(tocList);

    // ScrollSpy 逻辑
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

/**
 * 📱 移动端交互增强
 */
function initMobileEnhancements() {
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar-pioneer');
    if (!mobileToggle || !sidebar) return;

    mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        const icon = mobileToggle.querySelector('.btn-icon');
        icon.textContent = sidebar.classList.contains('active') ? '✕' : '☰';
    });
}

/**
 * 🔍 搜索交互系统
 */
let searchIndex = null;
async function initSearch() {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('search-results');
    if (!searchInput || !resultsContainer) return;

    // 🚀 [V15.0] 智能路径回归
    const pathParts = window.location.pathname.split('/').filter(p => p);
    const depth = pathParts.length;
    const rootPrefix = depth > 1 ? '../'.repeat(depth - 1) : './';
    const indexPath = `${rootPrefix}static/search_index.json`;

    searchInput.addEventListener('focus', async () => {
        if (!searchIndex) {
            try {
                const resp = await fetch(indexPath);
                searchIndex = await resp.json();
                console.log('📡 搜索索引已加载:', searchIndex.length);
            } catch (e) {
                console.error('🛑 搜索索引加载失败:', e);
            }
        }
    });

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (query.length < 2) {
            resultsContainer.classList.remove('active');
            return;
        }

        const matches = searchIndex.filter(item => 
            item.title.toLowerCase().includes(query) || 
            item.description.toLowerCase().includes(query) ||
            item.keywords.some(k => k.toLowerCase().includes(query))
        ).slice(0, 10);

        renderResults(matches, resultsContainer);
    });

    // 点击外部关闭
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.classList.remove('active');
        }
    });

    // 🚀 [V15.5] 搜索键盘交互增强
    let selectedIndex = -1;

    searchInput.addEventListener('keydown', (e) => {
        const items = resultsContainer.querySelectorAll('.search-item');
        if (!resultsContainer.classList.contains('active') || items.length === 0) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = (selectedIndex + 1) % items.length;
            updateSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = (selectedIndex - 1 + items.length) % items.length;
            updateSelection(items);
        } else if (e.key === 'Enter') {
            if (selectedIndex >= 0) {
                e.preventDefault();
                items[selectedIndex].click();
            }
        } else if (e.key === 'Escape') {
            resultsContainer.classList.remove('active');
            searchInput.blur();
        }
    });

    function updateSelection(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    // 🚀 [V15.5] 移动端响应式交互
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar-pioneer');
    const searchHub = document.querySelector('.search-hub');

    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            mobileToggle.classList.toggle('active');
            const icon = mobileToggle.querySelector('.btn-icon');
            icon.textContent = sidebar.classList.contains('active') ? '✕' : '☰';
        });
    }

    // 点击搜索框图标在移动端展开
    searchInput.addEventListener('focus', () => {
        if (window.innerWidth <= 768) {
            searchHub.classList.add('expanded');
        }
    });

    document.addEventListener('click', (e) => {
        if (!searchHub.contains(e.target) && searchHub.classList.contains('expanded')) {
            searchHub.classList.remove('expanded');
        }
        if (mobileToggle && !mobileToggle.contains(e.target) && sidebar && !sidebar.contains(e.target)) {
            sidebar.classList.remove('active');
            const icon = mobileToggle.querySelector('.btn-icon');
            if (icon) icon.textContent = '☰';
        }
    });

    // 🚀 [V15.5] 侧边栏折叠逻辑
    const groups = document.querySelectorAll('.nav-group');
    groups.forEach(group => {
        const title = group.querySelector('.group-title');
        title.addEventListener('click', (e) => {
            e.stopPropagation();
            group.classList.toggle('collapsed');
            const toggle = title.querySelector('.group-toggle');
            if (toggle) {
                toggle.textContent = group.classList.contains('collapsed') ? '▶' : '▼';
            }
        });
    });
}

function renderResults(matches, container) {
    if (matches.length === 0) {
        container.innerHTML = '<div class="search-no-results">未发现相关文档...</div>';
    } else {
        container.innerHTML = matches.map(m => `
            <a href="${m.url}" class="search-item">
                <div class="search-item-title">${m.title}</div>
                <div class="search-item-desc">${m.description || '无详细描述'}</div>
            </a>
        `).join('');
    }
    container.classList.add('active');
}
