/**
 * 🛣️ [V91.0] Illacme Plenipes Route & Slug Sandbox Module
 * 职责：别名策略视觉卡片切换、真实原稿全量感知、物理状态即时探测与重新发布提醒。
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

window.updateSlugSandboxPreview = async function() {
    const selector = document.getElementById('sandbox-file-select');
    const customInput = document.getElementById('sandbox-custom-input');
    const previewWebUrl = document.getElementById('sandbox-preview-web-url');
    const previewDiskPath = document.getElementById('sandbox-preview-disk-path');
    const previewStatusBox = document.getElementById('sandbox-preview-status-box');

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

    const filename = samplePath.split('/').pop().replace(/\.mdx?$/i, '');
    const parts = samplePath.split('/');
    parts.pop(); // 移除文件名
    const subDir = parts.join('/');

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
    const activeImprint = window.settingsData._active_imprint || "obsidian_vortex";
    const localDiskPath = `imprints/${activeImprint}/themes/default/${physicalHtmlPath}`;

    previewWebUrl.innerHTML = `<a href="${fullWebUrl}" target="_blank" style="color: var(--accent-primary, #00f2fe); font-weight: 600; text-decoration: underline;">${fullWebUrl}</a>`;

    const cloudEl = document.getElementById('sandbox-preview-cloud-path');
    if (cloudEl) cloudEl.innerHTML = `<span style="color: #00ffaa;">${webUrlPath}</span>`;

    previewDiskPath.innerHTML = `<span style="color: var(--text-dim, #aaa);">${localDiskPath}</span>`;

    // 🚀 [V91.0] 物理即时探测与重新发布提醒机制
    if (previewStatusBox) {
        previewStatusBox.innerHTML = `<span style="color: #bbb; font-size: 0.75rem;">⏳ 正在物理感应线上存在状态...</span>`;
        
        let isOnlineExist = false;
        try {
            // 尝试 HEAD 探测线上 URL 物理存在状态
            const res = await fetch(fullWebUrl, { method: 'HEAD', cache: 'no-cache' });
            if (res.status === 200) {
                isOnlineExist = true;
            }
        } catch (e) {
            isOnlineExist = false;
        }

        const modeLabels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀', 'nested': '目录树复刻' };
        const currentModeName = modeLabels[dirMode] || dirMode;

        if (isOnlineExist) {
            previewStatusBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(0, 255, 170, 0.08); border: 1px solid rgba(0, 255, 170, 0.3); padding: 8px 12px; border-radius: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #00ffaa; font-weight: 600; font-size: 0.8rem;">🟢 线上已物理就绪 (200 OK)</span>
                        <span style="color: #aaa; font-size: 0.75rem;">该路径当前已在云端部署成功并生效</span>
                    </div>
                </div>
            `;
        } else {
            previewStatusBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255, 180, 0, 0.08); border: 1px solid rgba(255, 180, 0, 0.3); padding: 8px 12px; border-radius: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #ffb400; font-weight: 600; font-size: 0.8rem;">🟡 待全域发布生效 (未物理就绪/404)</span>
                        <span style="color: #ddd; font-size: 0.75rem;">当前选择形态为【${currentModeName}】，需要点击右上角 <b>「🚀 全域发布」</b> 后即可上线生效！</span>
                    </div>
                    <button class="mini-btn glow-btn" onclick="if(document.getElementById('btn-publish')) document.getElementById('btn-publish').click();" style="padding: 3px 10px; font-size: 0.72rem; background: var(--accent-primary, #00f2fe); color: #000; border: none; border-radius: 4px; font-weight: 600; cursor: pointer;">
                        🚀 立即发布
                    </button>
                </div>
            `;
        }
    }
};
