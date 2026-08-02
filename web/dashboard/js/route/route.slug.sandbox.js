/**
 * 🛣️ [V95.0] Illacme Plenipes Route & Slug Sandbox Module
 * 职责：别名策略视觉卡片切换、真实原稿全量感知、物理状态即时探测、云端 GitHub 仓库点击直达与本机 Finder 定位高亮。
 */

window.selectSlugDirModeCard = function (mode) {
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
        const labels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀', 'nested': '复刻目录树' };
        addAudit(`📝 网址路径形态已更新为【${labels[mode] || mode}】`);
    }

    // 触发沙盒实时推导更新
    window.updateSlugSandboxPreview();
};

window.realManuscriptCache = [];

// 🚀 物理拉取金库全量真实原稿注入下拉框
window.populateSandboxRealFiles = async function () {
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

// 🚀 物理唤醒本机 Finder / 文件资源管理器
window.openLocalWorkspaceFolder = async function (relPath) {
    try {
        const res = await apiFetch('/api/vault/open-local-folder', {
            method: 'POST',
            body: JSON.stringify({ rel_path: relPath })
        });
        if (res && res.status === 'ok') {
            if (typeof addAudit === 'function') addAudit(`📂 已成功物理唤醒本机 Finder 定位至: ${res.opened_path}`);
        } else {
            console.warn("Open local folder response:", res);
        }
    } catch (e) {
        console.error("Open local folder error:", e);
    }
};

window.updateSlugSandboxPreview = async function () {
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

    let cleanRelPath = "";
    let webUrlPath = "";

    // 🚀 [物理主权适配] 优先匹配 route_matrix 中的专区/频道重定向映射
    const routeMatrix = window.settingsData.route_matrix || [];
    let matchedRoute = null;
    if (subDir) {
        matchedRoute = routeMatrix.find(r => r.source && (subDir === r.source || subDir.startsWith(r.source + '/')));
    }

    if (matchedRoute && matchedRoute.prefix) {
        let cleanP = matchedRoute.prefix.replace(/^\/+|\/+$/g, '');
        cleanRelPath = `docs/${cleanP}/${finalSlug}.html`;
        webUrlPath = `docs/${cleanP}/${finalSlug}.html`;
    } else {
        if (dirMode === 'flat') {
            cleanRelPath = `${finalSlug}.html`;
            webUrlPath = `${finalSlug}.html`;
        } else if (dirMode === 'prefix') {
            const safePrefix = subDir ? subDir.replace(/\//g, '-') + '-' : '';
            const prefixedSlug = `${safePrefix}${finalSlug}`;
            cleanRelPath = `${prefixedSlug}.html`;
            webUrlPath = `${prefixedSlug}.html`;
        } else if (dirMode === 'nested') {
            const nestedSub = subDir ? `${subDir}/` : '';
            cleanRelPath = `docs/${nestedSub}${finalSlug}.html`;
            webUrlPath = `docs/${nestedSub}${finalSlug}.html`;
        }
    }

    // 🚀 提取真实的托管 Base URL 与 GitHub Cloud 直达文件路径
    let baseUrl = "https://illacme.github.io/obsidian_vortex/";
    let owner = "Illacme", repo = "obsidian_vortex";

    const platforms = window.settingsData.platforms || {};
    const egress = window.settingsData.egress || {};

    const ghConfig = platforms.github_pages || egress.github_pages || {};

    if (ghConfig.cname && ghConfig.cname.trim()) {
        let cname = ghConfig.cname.trim();
        if (!cname.startsWith('http://') && !cname.startsWith('https://')) cname = 'https://' + cname;
        baseUrl = cname.replace(/\/+$/, '') + '/';
    }

    if (ghConfig.repo_url) {
        let clean = ghConfig.repo_url.trim().replace(/\.git$/, '');
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
        if (owner && repo && !ghConfig.cname) {
            baseUrl = `https://${owner.toLowerCase()}.github.io/${repo}/`;
        }
    }

    // 云端物理 GitHub 源码链接 (gh-pages 分支)
    const githubFileUrl = `https://github.com/${owner}/${repo}/blob/gh-pages/${webUrlPath}`;

    const fullWebUrl = `${baseUrl}${webUrlPath}`;
    const activeImprint = window.settingsData._active_imprint || "obsidian_vortex";

    // 纯正通用 SSG 本地构建落盘路径 (已抹去 github_pages 前缀)
    const localDiskPath = `imprints/${activeImprint}/themes/default/dist/${cleanRelPath}`;

    // 1. 🌐 线上访问 URL（在新标签页打开网页）
    previewWebUrl.innerHTML = `<a href="${fullWebUrl}" target="_blank" style="color: var(--accent-primary, #00f2fe); font-weight: 600; text-decoration: underline;" title="在浏览器中访问线上真实网页">${fullWebUrl}</a>`;

    // 2. ☁️ 云端托管平台文件路径（在 GitHub 上查看该物理文件）
    const cloudEl = document.getElementById('sandbox-preview-cloud-path');
    if (cloudEl) {
        cloudEl.innerHTML = `<a href="${githubFileUrl}" target="_blank" style="color: #00ffaa; font-weight: 600; text-decoration: underline;" title="点击在 GitHub 云端仓库 gh-pages 分支中直接查看此物理文件源码">☁️ gh-pages / ${webUrlPath}</a>`;
    }

    // 3. 💻 本机磁盘构建位置（唤醒 Mac Finder / 本地文件管理器高亮定位）
    previewDiskPath.innerHTML = `
        <a href="javascript:void(0)" onclick="window.openLocalWorkspaceFolder('${localDiskPath}')" style="color: var(--text-dim, #aaa); text-decoration: underline; cursor: pointer; font-weight: 500;" title="点击物理唤醒 Mac Finder / 本地资源管理器高亮选中该文件">
            📂 ${localDiskPath}
        </a>
    `;

    // 🚀 [V91.0] 物理即时探测与重新发布提醒机制
    if (previewStatusBox) {
        previewStatusBox.innerHTML = `<span style="color: #bbb; font-size: 0.75rem;">⏳ 正在物理感应线上存在状态...</span>`;

        let isOnlineExist = false;
        try {
            // 尝试带时间戳穿透 CDN 节点物理探测线上 URL 存在状态
            const probeUrl = fullWebUrl.includes('?') ? `${fullWebUrl}&_t=${Date.now()}` : `${fullWebUrl}?_t=${Date.now()}`;
            const res = await fetch(probeUrl, { method: 'HEAD', cache: 'no-store' });
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
                        <span style="color: #aaa; font-size: 0.75rem;">该路径已在 GitHub Pages 云端节点部署成功并可公网访问</span>
                    </div>
                </div>
            `;
        } else {
            previewStatusBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255, 180, 0, 0.08); border: 1px solid rgba(255, 180, 0, 0.3); padding: 10px 12px; border-radius: 6px;">
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #ffb400; font-weight: 600; font-size: 0.8rem;">🟡 待全域发布生效 (未物理就绪/404)</span>
                            <span style="color: #888; font-size: 0.72rem;">当前选择形态为【${currentModeName}】</span>
                        </div>
                        <div style="color: #bbb; font-size: 0.73rem; line-height: 1.4;">
                            💡 <b>常见原因</b>：1. GitHub Pages / CDN 部署刷新需 1 ~ 3 分钟物理时延； 2. 此原稿为最新更改，尚未执行「🚀 全域发布」。
                        </div>
                    </div>
                    <button class="mini-btn glow-btn" onclick="if(document.getElementById('btn-publish')) document.getElementById('btn-publish').click();" style="padding: 5px 12px; font-size: 0.75rem; background: var(--accent-primary, #00f2fe); color: #000; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; flex-shrink: 0; margin-left: 10px;">
                        🚀 重新发布全站
                    </button>
                </div>
            `;
        }
    }
};
