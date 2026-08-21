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

    const settingsData = window.settingsData || {};
    const translation = settingsData.translation || {};
    const i18nSettings = settingsData.i18n_settings || {};
    const dirMode = translation.slug_dir_mode || 'flat';
    const slugMode = translation.slug_mode || 'ai';
    const isAi = (slugMode === 'ai');

    // 🛡️ [防御性解构] 统一提取纯净字符串语种代码与友好名称
    const extractLangCode = (item, fallback = 'en') => {
        if (!item) return fallback;
        if (typeof item === 'string') return item.trim().toLowerCase();
        if (typeof item === 'object') {
            const code = item.lang_code || item.code || item.id || item.lang || fallback;
            return typeof code === 'string' ? code.trim().toLowerCase() : fallback;
        }
        return String(item).trim().toLowerCase();
    };

    // 语种矩阵与前缀开关感知 (支持字符串及对象字典双模态)
    const rawSource = i18nSettings.source || 'zh';
    const sourceLang = extractLangCode(rawSource, 'zh');

    let targetLangs = ['en'];
    if (i18nSettings.targets && Array.isArray(i18nSettings.targets) && i18nSettings.targets.length > 0) {
        targetLangs = i18nSettings.targets.map(t => extractLangCode(t, 'en')).filter(Boolean);
    }
    const forceDefaultLangPrefix = !!i18nSettings.force_default_lang_prefix;

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

    // 🚀 [物理主权适配] 优先匹配 route_matrix 中的专区/频道重定向映射
    const routeMatrix = settingsData.route_matrix || [];
    let matchedRoute = null;
    if (subDir) {
        matchedRoute = routeMatrix.find(r => r.source && (subDir === r.source || subDir.startsWith(r.source + '/')));
    }

    // 提取真实的托管 Base URL 与 GitHub Cloud 仓库信息
    let baseUrl = "https://illacme.github.io/obsidian_vortex/";
    let owner = "Illacme", repo = "obsidian_vortex";

    const platforms = settingsData.platforms || {};
    const egress = settingsData.egress || {};
    const ghConfig = platforms.github_pages || egress.github_pages || (settingsData.publish_control?.direct_upload?.github_pages) || {};

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

    const activeImprint = settingsData.active_imprint || settingsData._active_imprint || "default";
    const activeTheme = settingsData.active_theme || "default";

    // 辅助函数：根据语种计算最终的 URL 路径与本地磁盘落盘路径
    const computeLangPaths = (langCode, isSource) => {
        const cleanCode = typeof langCode === 'string' ? langCode.trim().toLowerCase() : 'en';
        let langPrefix = "";
        if (isSource) {
            langPrefix = forceDefaultLangPrefix ? `${cleanCode}/` : "";
        } else {
            langPrefix = `${cleanCode}/`;
        }

        let channelRelPath = "";
        if (matchedRoute && matchedRoute.prefix) {
            let cleanP = matchedRoute.prefix.replace(/^\/+|\/+$/g, '');
            channelRelPath = `docs/${cleanP}/${finalSlug}.html`;
        } else {
            if (dirMode === 'flat') {
                channelRelPath = `${finalSlug}.html`;
            } else if (dirMode === 'prefix') {
                const safePrefix = subDir ? subDir.replace(/\//g, '-') + '-' : '';
                channelRelPath = `${safePrefix}${finalSlug}.html`;
            } else if (dirMode === 'nested') {
                const nestedSub = subDir ? `${subDir}/` : '';
                channelRelPath = `docs/${nestedSub}${finalSlug}.html`;
            }
        }

        const relativeWebPath = `${langPrefix}${channelRelPath}`.replace(/^\/+/, '');
        const fullWebUrl = `${baseUrl}${relativeWebPath}`;
        const githubFileUrl = `https://github.com/${owner}/${repo}/blob/gh-pages/${relativeWebPath}`;
        const localDiskPath = `imprints/${activeImprint}/themes/${activeTheme}/dist/${relativeWebPath}`;

        return {
            langCode: cleanCode,
            isSource,
            relativeWebPath,
            fullWebUrl,
            githubFileUrl,
            localDiskPath
        };
    };

    // 计算母语及所有目标翻译语种路径
    const sourceInfo = computeLangPaths(sourceLang, true);
    const targetInfos = targetLangs.filter(l => l !== sourceLang).map(l => computeLangPaths(l, false));
    const allLangInfos = [sourceInfo, ...targetInfos];

    // 语种名称与国旗映射字典
    const langFlags = {
        'zh': { flag: '🇨🇳', name: '中文 (母语)' },
        'en': { flag: '🇺🇸', name: '英文 (English)' },
        'ja': { flag: '🇯🇵', name: '日文 (日本語)' },
        'es': { flag: '🇪🇸', name: '西班牙文 (Español)' },
        'fr': { flag: '🇫🇷', name: '法文 (Français)' },
        'de': { flag: '🇩🇪', name: '德文 (Deutsch)' },
        'ru': { flag: '🇷🇺', name: '俄文 (Русский)' },
        'ko': { flag: '🇰🇷', name: '韩文 (한국어)' },
        'az': { flag: '🇦🇿', name: '阿塞拜疆文 (Azərbaycan)' },
        'pt': { flag: '🇵🇹', name: '葡萄牙文 (Português)' }
    };

    // 渲染全息多语种并列 URL 矩阵列表
    const matrixBox = document.getElementById('sandbox-multilingual-matrix');
    if (matrixBox) {
        matrixBox.innerHTML = allLangInfos.map((info, idx) => {
            const codeStr = typeof info.langCode === 'string' ? info.langCode : String(info.langCode || 'en');
            const langMeta = langFlags[codeStr] || { flag: '🌐', name: codeStr.toUpperCase() };
            const isSource = info.isSource;
            const prefixTag = isSource
                ? (forceDefaultLangPrefix ? '<span style="font-size: 0.65rem; color: #00f2fe; background: rgba(0,242,254,0.12); border: 1px solid rgba(0,242,254,0.3); padding: 1px 6px; border-radius: 4px; font-weight: 600;">🏷️ 强制母语前缀</span>' : '<span style="font-size: 0.65rem; color: #00ff88; background: rgba(0,255,136,0.12); border: 1px solid rgba(0,255,136,0.3); padding: 1px 6px; border-radius: 4px; font-weight: 600;">👑 默认根路径</span>')
                : '<span style="font-size: 0.65rem; color: #a34cff; background: rgba(163,76,255,0.12); border: 1px solid rgba(163,76,255,0.3); padding: 1px 6px; border-radius: 4px; font-weight: 600;">🌍 目标语种译本</span>';

            return `
                <div style="background: ${idx === 0 ? 'rgba(0, 242, 254, 0.04)' : 'rgba(255, 255, 255, 0.015)'}; border: 1px solid ${idx === 0 ? 'rgba(0, 242, 254, 0.25)' : 'rgba(255, 255, 255, 0.06)'}; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; transition: all 0.2s;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 0.82rem; font-weight: 600; color: #fff;">${langMeta.flag} ${langMeta.name}</span>
                            ${prefixTag}
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <a href="${info.fullWebUrl}" target="_blank" style="padding: 2px 8px; font-size: 0.68rem; font-weight: 600; color: var(--neon-cyan, #00f2fe); border: 1px solid rgba(0, 242, 254, 0.35); background: rgba(0, 242, 254, 0.08); border-radius: 4px; text-decoration: none; display: inline-flex; align-items: center; gap: 3px;" title="在浏览器新标签页访问此语种线上网页">🔗 访问 ↗</a>
                            <a href="${info.githubFileUrl}" target="_blank" style="padding: 2px 8px; font-size: 0.68rem; font-weight: 600; color: #00ffaa; border: 1px solid rgba(0, 255, 170, 0.35); background: rgba(0, 255, 170, 0.08); border-radius: 4px; text-decoration: none; display: inline-flex; align-items: center; gap: 3px;" title="在 GitHub 云端仓库 gh-pages 分支直接查看此物理文件">☁️ GitHub ↗</a>
                            <a href="javascript:void(0)" onclick="window.openLocalWorkspaceFolder('${info.localDiskPath}')" style="padding: 2px 8px; font-size: 0.68rem; font-weight: 500; color: var(--text-dim, #aaa); border: 1px solid rgba(255, 255, 255, 0.12); background: rgba(255, 255, 255, 0.04); border-radius: 4px; text-decoration: none; cursor: pointer;" title="物理唤醒 Mac Finder / 资源管理器高亮选中该文件">📂 Finder</a>
                        </div>
                    </div>
                    <div style="font-family: monospace; font-size: 0.76rem; color: ${idx === 0 ? 'var(--neon-cyan, #00f2fe)' : '#d0d8e8'}; word-break: break-all; line-height: 1.4;">
                        ${info.fullWebUrl}
                    </div>
                </div>
            `;
        }).join('');
    }

    // 兼容回填旧版单行选择器 (如有)
    if (previewWebUrl) {
        previewWebUrl.innerHTML = `<a href="${sourceInfo.fullWebUrl}" target="_blank" style="color: var(--accent-primary, #00f2fe); font-weight: 600; text-decoration: underline;">${sourceInfo.fullWebUrl}</a>`;
    }
    const cloudEl = document.getElementById('sandbox-preview-cloud-path');
    if (cloudEl) {
        cloudEl.innerHTML = `<a href="${sourceInfo.githubFileUrl}" target="_blank" style="color: #00ffaa; font-weight: 600; text-decoration: underline;">☁️ gh-pages / ${sourceInfo.relativeWebPath}</a>`;
    }
    if (previewDiskPath) {
        previewDiskPath.innerHTML = `
            <a href="javascript:void(0)" onclick="window.openLocalWorkspaceFolder('${sourceInfo.localDiskPath}')" style="color: var(--text-dim, #aaa); text-decoration: underline; cursor: pointer; font-weight: 500;">
                📂 ${sourceInfo.localDiskPath}
            </a>
        `;
    }

    // 动态解析诊断徽标栏
    const diagnosticBox = document.getElementById('sandbox-preview-diagnostic-bar');
    if (diagnosticBox) {
        const modeLabels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀', 'nested': '目录树复刻' };
        const routeHint = matchedRoute ? `🎯 命中频道: ${matchedRoute.source} ➔ /${matchedRoute.prefix}/` : '📁 默认频道';
        const prefixHint = forceDefaultLangPrefix ? '🏷️ 母语前缀: 强制开启' : '👑 母语前缀: 默认根路径';

        diagnosticBox.innerHTML = `
            <div style="display: flex; gap: 8px; flex-wrap: wrap; font-size: 0.68rem; margin-top: 8px;">
                <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; color: var(--text-dim);">${routeHint}</span>
                <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; color: var(--text-dim);">📝 命名: ${modeLabels[dirMode] || dirMode} (${slugMode === 'ai' ? 'AI 语义' : '文件名'})</span>
                <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; color: var(--text-dim);">🎭 主题: ${activeTheme}</span>
                <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; color: var(--text-dim);">${prefixHint}</span>
                <span style="background: rgba(0,255,136,0.08); border: 1px solid rgba(0,255,136,0.25); padding: 2px 8px; border-radius: 4px; color: #00ff88;">🌍 多语矩阵: ${1 + targetInfos.length} 个版本实时同步</span>
            </div>
        `;
    }

    // 🚀 物理即时探测与重新发布提醒机制
    if (previewStatusBox) {
        previewStatusBox.innerHTML = `<span style="color: #bbb; font-size: 0.72rem;">⏳ 正在感应线上多语言云端可达状态...</span>`;

        let isOnlineExist = false;
        try {
            const probeUrl = sourceInfo.fullWebUrl.includes('?') ? `${sourceInfo.fullWebUrl}&_t=${Date.now()}` : `${sourceInfo.fullWebUrl}?_t=${Date.now()}`;
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
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(0, 255, 170, 0.08); border: 1px solid rgba(0, 255, 170, 0.3); padding: 8px 12px; border-radius: 6px; margin-top: 10px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #00ffaa; font-weight: 600; font-size: 0.78rem;">🟢 线上母语版本已就绪 (200 OK)</span>
                        <span style="color: #aaa; font-size: 0.72rem;">多语种译本已在 GitHub Pages 云端节点部署完成</span>
                    </div>
                </div>
            `;
        } else {
            previewStatusBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255, 180, 0, 0.08); border: 1px solid rgba(255, 180, 0, 0.3); padding: 10px 12px; border-radius: 6px; margin-top: 10px;">
                    <div style="display: flex; flex-direction: column; gap: 3px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #ffb400; font-weight: 600; font-size: 0.78rem;">🟡 待全域发布生效 (推导就绪)</span>
                            <span style="color: #888; font-size: 0.72rem;">当前形态为【${currentModeName}】</span>
                        </div>
                        <div style="color: #bbb; font-size: 0.72rem; line-height: 1.4;">
                            💡 更改前缀、频道或 Slug 命名后，点击「🚀 重新发布全站」即可立即按此全息路径推流上线。
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
