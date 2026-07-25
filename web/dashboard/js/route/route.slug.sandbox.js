/**
 * 🛣️ [V90.0] Illacme Plenipes Route & Slug Sandbox Module
 * 职责：别名策略视觉卡片切换、真实 Obsidian 金库文稿全量感知与物理 URL 模拟器。
 */

window.selectSlugDirModeCard = function(mode) {
    if (!window.settingsData.translation) {
        window.settingsData.translation = {};
    }
    window.settingsData.translation.slug_dir_mode = mode;

    // UI 卡片激活状态同步
    const cards = document.querySelectorAll('.slug-dir-card');
    cards.forEach(card => {
        if (card.getAttribute('data-mode') === mode) {
            card.classList.add('active');
            card.style.borderColor = 'var(--accent-secondary, #00f2fe)';
            card.style.background = 'rgba(0, 242, 255, 0.06)';
            card.style.boxShadow = '0 0 15px rgba(0, 242, 255, 0.15)';
        } else {
            card.classList.remove('active');
            card.style.borderColor = 'var(--glass-border, rgba(255,255,255,0.08))';
            card.style.background = 'rgba(255, 255, 255, 0.02)';
            card.style.boxShadow = 'none';
        }
    });

    if (typeof addAudit === 'function') {
        const labels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀', 'nested': '复刻 Obsidian 目录树' };
        addAudit(`📝 网址路径形态已更新为【${labels[mode] || mode}】`);
    }

    // 触发沙盒实时推导更新
    window.updateSlugSandboxPreview();
};

window.realManuscriptCache = [];

// 🚀 物理拉取金库全量真实原稿注入下拉框
window.populateSandboxRealFiles = async function() {
    const selector = document.getElementById('sandbox-file-select');
    if (!selector) return;

    try {
        let manuscripts = window.realManuscriptCache;
        if (!manuscripts || manuscripts.length === 0) {
            const res = await apiFetch('/api/vault/list');
            if (res && res.manuscripts) {
                manuscripts = res.manuscripts;
                window.realManuscriptCache = manuscripts;
            }
        }

        if (manuscripts && manuscripts.length > 0) {
            selector.innerHTML = '';
            manuscripts.forEach(m => {
                const path = m.rel_path || m.path;
                if (!path) return;
                const opt = document.createElement('option');
                opt.value = path;
                opt.text = `📄 ${path}`;
                opt.dataset.slug = m.slug || '';
                opt.dataset.title = m.title || '';
                selector.appendChild(opt);
            });

            // 附带自定义输入项
            const customOpt = document.createElement('option');
            customOpt.value = '_custom';
            customOpt.text = '✏️ 手动输入自定义相对路径...';
            selector.appendChild(customOpt);

            // 刷新计算
            window.updateSlugSandboxPreview();
        }
    } catch (e) {
        console.warn("Populate sandbox real files warning:", e);
    }
};

window.updateSlugSandboxPreview = function() {
    const selector = document.getElementById('sandbox-file-select');
    const customInput = document.getElementById('sandbox-custom-input');
    const previewWebUrl = document.getElementById('sandbox-preview-web-url');
    const previewDiskPath = document.getElementById('sandbox-preview-disk-path');

    if (!previewWebUrl || !previewDiskPath) return;

    let samplePath = "tech/guide/e2e_slug_test.md";
    let sampleTitle = "安装与部署指南";
    let existingSlug = "";

    if (selector && selector.value && selector.value !== '_custom') {
        samplePath = selector.value;
        const selectedOpt = selector.options[selector.selectedIndex];
        existingSlug = selectedOpt ? selectedOpt.dataset.slug : '';
        sampleTitle = selectedOpt ? (selectedOpt.dataset.title || samplePath.split('/').pop().replace(/\.mdx?$/i, '')) : samplePath.split('/').pop().replace(/\.mdx?$/i, '');
    } else if (customInput && customInput.value.trim()) {
        samplePath = customInput.value.trim();
        sampleTitle = samplePath.split('/').pop().replace(/\.mdx?$/i, '');
    }

    const translation = window.settingsData.translation || {};
    const dirMode = translation.slug_dir_mode || 'flat';
    const slugMode = translation.slug_mode || 'ai';
    const isAi = (slugMode === 'ai');

    // 计算父级相对路径与文件名
    const filename = samplePath.split('/').pop().replace(/\.mdx?$/i, '');
    const parts = samplePath.split('/');
    parts.pop(); // 移除文件名
    const subDir = parts.join('/');

    // 若文档已有已有真实计算好的 Slug，优先使用，否则生成
    let finalSlug = existingSlug;
    if (!finalSlug) {
        if (isAi) {
            finalSlug = filename.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '') || "document";
        } else {
            finalSlug = sampleTitle.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, '');
            if (!finalSlug) finalSlug = "document";
        }
    }

    let physicalHtmlPath = "";
    let webUrlPath = "";

    if (dirMode === 'flat') {
        physicalHtmlPath = `dist/github_pages/${finalSlug}.html`;
        webUrlPath = `${finalSlug}.html`;
    } else if (dirMode === 'prefix') {
        const safePrefix = subDir ? subDir.replace(/\//g, '-') + '-' : '';
        const prefixedSlug = `${safePrefix}${finalSlug}`;
        physicalHtmlPath = `dist/github_pages/${prefixedSlug}.html`;
        webUrlPath = `${prefixedSlug}.html`;
    } else if (dirMode === 'nested') {
        const nestedSub = subDir ? `${subDir}/` : '';
        physicalHtmlPath = `dist/github_pages/docs/${nestedSub}${finalSlug}.html`;
        webUrlPath = `docs/${nestedSub}${finalSlug}.html`;
    }

    // 🚀 提取真实的托管 Base URL
    let baseUrl = "https://illacme.github.io/obsidian_vortex/";
    const platforms = window.settingsData.platforms || {};

    if (platforms.github_pages && platforms.github_pages.cname && platforms.github_pages.cname.trim()) {
        let cname = platforms.github_pages.cname.trim();
        if (!cname.startsWith('http://') && !cname.startsWith('https://')) cname = 'https://' + cname;
        baseUrl = cname.replace(/\/+$/, '') + '/';
    } else if (platforms.github_pages && platforms.github_pages.repo_url) {
        let clean = platforms.github_pages.repo_url.trim().replace(/\.git$/, '');
        let owner = "", repo = "";
        if (clean.includes("github.com/")) {
            const p = clean.split("github.com/")[1].split("/");
            if (p.length >= 2) { owner = p[0]; repo = p[1]; }
        } else if (clean.includes("github.com:")) {
            const p = clean.split("github.com:")[1].split("/");
            if (p.length >= 2) { owner = p[0]; repo = p[1]; }
        } else if (clean.includes("/")) {
            const p = clean.split("/");
            if (p.length === 2) { owner = p[0]; repo = p[1]; }
        }
        if (owner && repo) {
            baseUrl = `https://${owner.toLowerCase()}.github.io/${repo}/`;
        }
    } else if (platforms.netlify && platforms.netlify.site_url) {
        let siteUrl = platforms.netlify.site_url.trim();
        if (!siteUrl.startsWith('http')) siteUrl = 'https://' + siteUrl;
        baseUrl = siteUrl.replace(/\/+$/, '') + '/';
    }

    const fullWebUrl = `${baseUrl}${webUrlPath}`;

    previewWebUrl.innerHTML = `<a href="${fullWebUrl}" target="_blank" style="color: var(--accent-primary, #00f2fe); font-weight: 600; text-decoration: underline;">${fullWebUrl}</a>`;
    previewDiskPath.innerHTML = `<span style="color: var(--text-dim, #aaa);">${physicalHtmlPath}</span>`;
};
