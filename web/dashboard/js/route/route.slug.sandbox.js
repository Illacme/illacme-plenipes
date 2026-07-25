/**
 * 🛣️ [V89.0] Illacme Plenipes Route & Slug Sandbox Module
 * 职责：别名策略视觉卡片切换、实时 URL 沙盒推导模拟器与配置同步。
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

window.updateSlugSandboxPreview = function() {
    const selector = document.getElementById('sandbox-file-select');
    const customInput = document.getElementById('sandbox-custom-input');
    const previewWebUrl = document.getElementById('sandbox-preview-web-url');
    const previewDiskPath = document.getElementById('sandbox-preview-disk-path');

    if (!previewWebUrl || !previewDiskPath) return;

    let samplePath = "tech/guide/安装与部署指南.md";
    let sampleTitle = "安装与部署指南";
    let sampleSlug = "install-guide";

    if (selector && selector.value && selector.value !== '_custom') {
        samplePath = selector.value;
        const filename = samplePath.split('/').pop().replace(/\.mdx?$/i, '');
        sampleTitle = filename;
        sampleSlug = filename.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '') || "document";
    } else if (customInput && customInput.value.trim()) {
        samplePath = customInput.value.trim();
        const filename = samplePath.split('/').pop().replace(/\.mdx?$/i, '');
        sampleTitle = filename;
        sampleSlug = filename.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '') || "document";
    }

    const translation = window.settingsData.translation || {};
    const dirMode = translation.slug_dir_mode || 'flat';
    const slugMode = translation.slug_mode || 'ai';
    const isAi = (slugMode === 'ai');

    // 计算映射子目录
    const parts = samplePath.split('/');
    parts.pop(); // 移除文件名
    const subDir = parts.join('/');

    let finalSlug = isAi ? sampleSlug : sampleTitle.toLowerCase().replace(/\s+/g, '-');
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

    const activeRepoName = (window.settingsData.platforms?.github_pages?.repo_url || "obsidian_vortex").split('/').pop().replace(/\.git$/, '') || "obsidian_vortex";
    const fullWebUrl = `https://username.github.io/${activeRepoName}/${webUrlPath}`;

    previewWebUrl.innerHTML = `<span style="color: var(--accent-primary, #00f2fe); font-weight: 600;">${fullWebUrl}</span>`;
    previewDiskPath.innerHTML = `<span style="color: var(--text-dim, #aaa);">${physicalHtmlPath}</span>`;
};
