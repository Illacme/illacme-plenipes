/**
 * 🚀 [V87.0] Illacme Plenipes Markdown Parser & Sync Scroll Shard
 * 职责：Obsidian 双链、Wiki 联动路径对齐、Markdown 渲染及编辑器同步滚动。
 */

// 🎬 [V88.0] 多媒体预览格式化引擎 (支持 Video/Audio/Image 与在线视频 iframe)
const PREVIEW_VIDEO_EXTS = new Set(['mp4', 'webm', 'mov', 'm4v', 'ogv']);
const PREVIEW_AUDIO_EXTS = new Set(['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'opus']);

window.formatMediaHtml = (url, alt = '', extra = '', onErr = '') => {
    const cleanUrl = (url || '').trim();
    // 1. 在线视频平台识别 (B站 / YouTube)
    const bMatch = cleanUrl.match(/(?:bilibili\.com\/video\/|b23\.tv\/)(BV[a-zA-Z0-9]+)/i);
    if (bMatch) {
        return `<div class="preview-media-container preview-bilibili" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="//player.bilibili.com/player.html?bvid=${bMatch[1]}&page=1&high_quality=1&as_wide=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;
    }
    const yMatch = cleanUrl.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/i);
    if (yMatch) {
        return `<div class="preview-media-container preview-youtube" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="https://www.youtube-nocookie.com/embed/${yMatch[1]}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;
    }
    // 2. 音视频与图片扩展名判定
    const target = cleanUrl.split('?')[0].toLowerCase();
    const altTarget = (alt || '').toLowerCase();
    const ext = target.split('.').pop() || altTarget.split('.').pop() || '';
    if (PREVIEW_VIDEO_EXTS.has(ext)) {
        return `<div class="preview-media-container preview-video" style="margin:12px 0;"><video controls preload="metadata" style="max-width:100%;border-radius:8px;box-shadow:0 4px 14px rgba(0,0,0,0.15);background:#000;" src="${cleanUrl}"></video>${alt ? `<div style="font-size:12px;color:var(--text-muted,#888);margin-top:4px;">📹 ${alt}</div>` : ''}</div>`;
    }
    if (PREVIEW_AUDIO_EXTS.has(ext)) {
        return `<div class="preview-media-container preview-audio" style="margin:12px 0;"><audio controls preload="metadata" style="width:100%;max-width:540px;" src="${cleanUrl}"></audio>${alt ? `<div style="font-size:12px;color:var(--text-muted,#888);margin-top:4px;">🎵 ${alt}</div>` : ''}</div>`;
    }
    // 3. 常规图片渲染
    const errAttr = onErr ? ` onerror="${onErr}"` : '';
    const widthAttr = (extra && !isNaN(extra.trim())) ? ` width="${extra.trim()}"` : '';
    return `<img src="${cleanUrl}" alt="${alt}" loading="lazy"${widthAttr}${errAttr} style="max-width:100%;border-radius:6px;" />`;
};

window.updateEditorPreview = () => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    if (!body || !preview) return;

    let mdContent = body.value;

    // 🚀 [主权修正] 1. 代码块与行内代码保护（挖空）
    // 收集所有 ```...``` 块以及 `...` 块，防止其内部的双链等控制符被无脑替换
    const codeBlocks = [];
    const codeReg = /(```[\s\S]*?```|`[^`\n]*?`)/g;
    mdContent = mdContent.replace(codeReg, (match) => {
        const placeholder = `__PLENIPES_CODE_PROTECT_${codeBlocks.length}__`;
        codeBlocks.push(match);
        return placeholder;
    });

    // 0. 在线视频独立直链解析 (B站/YouTube 单独成行)
    const standaloneVideoReg = /(^|\n)(https?:\/\/(?:(?:www\.)?bilibili\.com\/video\/BV[a-zA-Z0-9]+|(?:www\.)?youtube\.com\/watch\?v=[a-zA-Z0-9_-]{11}|youtu\.be\/[a-zA-Z0-9_-]{11})[^\s\n]*)(?=$|\n)/gi;
    mdContent = mdContent.replace(standaloneVideoReg, (m, pfx, url) => {
        return pfx + window.formatMediaHtml(url);
    });

    // 1. 物理资源解析：替换 Obsidian 双链媒体 ![[media.ext]] 或 ![[media.ext|extra]]
    mdContent = mdContent.replace(/!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, extra) => {
        const cleanPath = decodeURIComponent(path.trim());
        const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(window.activeDocId || '')}`;
        return window.formatMediaHtml(url, cleanPath, extra);
    });

    // 2. 物理资源解析：替换 Obsidian 双链普通附件 [[file.pdf]] 或 [[file.pdf|display]] (排除了带 ! 前缀的情况)
    mdContent = mdContent.replace(/(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, display) => {
        const cleanPath = decodeURIComponent(path.trim());
        const displayName = (display || cleanPath).trim();
        const extMatch = cleanPath.match(/\.([a-zA-Z0-9]+)$/);
        if (extMatch && !['md', 'mdx', 'markdown'].includes(extMatch[1].toLowerCase())) {
            const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(window.activeDocId || '')}`;
            return `<a href="${url}" target="_blank" class="attachment-link">📎 ${displayName}</a>`;
        } else {
            const cleanDocPath = cleanPath.replace(/\.mdx?$/, '');
            return `<a href="#" onclick="openEditorFromPreview('${cleanDocPath.replace(/'/g, "\\'")}', event)" class="wiki-doc-link">📄 ${displayName}</a>`;
        }
    });

    // 3. 物理资源解析：替换标准 Markdown 图片与多媒体 ![alt](path)
    mdContent = mdContent.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('data:')) {
            return window.formatMediaHtml(cleanUrl, alt);
        }
        const decodedUrl = decodeURIComponent(cleanUrl);
        const resolvedUrl = `/api/vault-assets/${encodeURIComponent(decodedUrl)}?relative_to=${encodeURIComponent(window.activeDocId || '')}`;
        return window.formatMediaHtml(resolvedUrl, alt);
    });

    // 4. 物理资源解析：替换标准 Markdown 链接 [text](path) (排除了带 ! 前缀的图片链接，防止二次污染)
    mdContent = mdContent.replace(/(?<!\!)\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('data:') || cleanUrl.startsWith('#')) {
            return match;
        }
        const decodedUrl = decodeURIComponent(cleanUrl);
        const extMatch = decodedUrl.match(/\.([a-zA-Z0-9]+)$/);
        if (extMatch && !['md', 'mdx', 'markdown'].includes(extMatch[1].toLowerCase())) {
            const resolvedUrl = `/api/vault-assets/${encodeURIComponent(decodedUrl)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
            return `<a href="${resolvedUrl}" target="_blank" class="attachment-link">📎 ${text}</a>`;
        } else {
            const cleanDocPath = decodedUrl.replace(/\.mdx?$/, '');
            return `<a href="#" onclick="openEditorFromPreview('${cleanDocPath.replace(/'/g, "\\'")}', event)" class="wiki-doc-link">📄 ${text}</a>`;
        }
    });

    // 🚀 [主权修正] 2. 还原受保护的代码块
    for (let i = 0; i < codeBlocks.length; i++) {
        const placeholder = `__PLENIPES_CODE_PROTECT_${i}__`;
        mdContent = mdContent.replace(placeholder, codeBlocks[i]);
    }

    // 🚀 [V87.0] 实时解析 Markdown (依赖 vendor/marked.js)
    // [AEL-2026-06-14] 在渲染时动态读取 hard_line_break 配置（settingsData 在加载时可能尚未就绪，
    // 因此必须在每次渲染时取值，而非在脚本初始化时一次性读取）。
    if (typeof marked !== 'undefined') {
        const _breaks = window.settingsData?.ingress_settings?.hard_line_break ?? false;
        preview.innerHTML = marked.parse(mdContent, { breaks: _breaks });
    } else {
        preview.innerText = "Markdown 引擎尚未就绪...";
    }
};

// 📄 相对路径物理对齐与降级解析器 (JavaScript 版 Path.resolve)
const resolveRelativePath = (basePath, relPath) => {
    if (!relPath.startsWith('.')) return relPath; // 非相对路径直接返回
    
    const baseParts = basePath.split('/');
    baseParts.pop(); // 移除文件名，保留目录结构
    
    const relParts = relPath.split('/');
    for (const part of relParts) {
        if (part === '.' || part === '') continue;
        if (part === '..') {
            baseParts.pop();
        } else {
            baseParts.push(part);
        }
    }
    return baseParts.join('/');
};

// 📄 [NEW] 双链编辑器联动跳转引擎
window.openEditorFromPreview = async (wikiName, event) => {
    if (event) event.preventDefault();
    try {
        // 🚀 高能对齐：先进行 URL-decode（将 %20 等符号还原为真实的物理路径空格）
        const decodedWikiName = decodeURIComponent(wikiName);
        
        // 🚀 兼容性护航：分离出 Obsidian 标题锚点（如 [[Doc#Heading]]）或块引用（如 [[Doc#^block]]）
        let docPathOnly = decodedWikiName;
        let anchor = "";
        const hashIndex = decodedWikiName.indexOf('#');
        if (hashIndex !== -1) {
            docPathOnly = decodedWikiName.substring(0, hashIndex);
            anchor = decodedWikiName.substring(hashIndex + 1);
        }
        
        // 再进行相对路径物理对正（支持 ../ 等相对路径）
        const normalizedName = resolveRelativePath(window.activeDocId, docPathOnly);
        console.log(`[Wiki Navigation] Original: ${wikiName} -> Decoded: ${decodedWikiName} -> Normalized: ${normalizedName} (Anchor: ${anchor})`);

        // 全量联邦检索定位目标相对路径
        const res = await apiFetch(`/api/vault/search?q=${encodeURIComponent(normalizedName)}&limit=1`);
        if (res && res.items && res.items.length > 0) {
            const doc = res.items[0];
            // 平滑进入下一份资产编辑，刷新编辑器面板
            openEditor(doc.rel_path);
        } else {
            Swal.fire({
                title: '未发现该资产',
                text: `系统在原稿库中未能定位匹配到 "${normalizedName}"。`,
                icon: 'warning',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
        }
    } catch (e) {
        console.error("Open editor from preview error:", e);
    }
};

// 🔄 [V87.1] 同步滚动引擎 (Synchronized Scroll Engine)
let isSyncingScroll = false;
window.initSyncScroll = () => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    if (!body || !preview || body._syncBound) return;

    body._syncBound = true;

    const sync = (source, target) => {
        if (isSyncingScroll) return;
        const btnSplit = document.getElementById('mode-split');
        if (!btnSplit?.classList.contains('active')) return;

        isSyncingScroll = true;
        const sourceMax = source.scrollHeight - source.clientHeight;
        const targetMax = target.scrollHeight - target.clientHeight;

        if (sourceMax > 0) {
            const percentage = source.scrollTop / sourceMax;
            target.scrollTop = percentage * targetMax;
        }

        // 使用 requestAnimationFrame 确保平滑度并防止死循环
        requestAnimationFrame(() => {
            isSyncingScroll = false;
        });
    };

    body.addEventListener('scroll', () => sync(body, preview), { passive: true });
    preview.addEventListener('scroll', () => sync(preview, body), { passive: true });
};

// 🌓 [V87.6] Obsidian Callouts Support globally for marked.js
if (typeof marked !== 'undefined') {
    // [AEL-2026-06-14] breaks 配置已迁移至每次渲染时动态读取（在 updateEditorPreview 的
    // marked.parse(content, { breaks }) 调用中），以解决脚本加载时 settingsData 尚未就绪的时序问题。
    marked.use({
        renderer: {
            blockquote(token) {
                const raw = token.raw || '';
                // Matches Obsidian callout syntax: > [!type] or > [!type] Title (use [ \t] to avoid matching across lines!)
                const match = raw.match(/^\s*>\s*\[\!([a-zA-Z0-9_-]+)\]([+-]?)(?:[ \t]+(.*))?/);
                if (match) {
                    const type = match[1].toLowerCase();
                    const titleMarkdown = match[3] ? match[3].trim() : (type.charAt(0).toUpperCase() + type.slice(1));
                    const titleHtml = marked.parseInline(titleMarkdown);
                    
                    // Strip the first line (the callout header) from raw markdown body
                    const lines = raw.split('\n');
                    const cleanedLines = lines.map(line => line.replace(/^\s*>\s?/, ''));
                    cleanedLines.shift(); // Remove the header line
                    const bodyMarkdown = cleanedLines.join('\n');
                    
                    // Parse the body using the same marked instance
                    const bodyTokens = marked.lexer(bodyMarkdown);
                    const bodyHtml = this.parser.parse(bodyTokens);
                    
                    // Select a premium emoji icon based on type
                    let icon = 'ℹ️';
                    if (['tip', 'hint'].includes(type)) icon = '💡';
                    else if (['note', 'info'].includes(type)) icon = '📝';
                    else if (['important', 'attention'].includes(type)) icon = '⚠️';
                    else if (['warning', 'caution'].includes(type)) icon = '🔥';
                    else if (['danger', 'error', 'failure', 'bug'].includes(type)) icon = '🛑';
                    else if (['todo', 'checklist'].includes(type)) icon = '☑️';
                    else if (type === 'example') icon = '🧪';
                    else if (['quote', 'cite'].includes(type)) icon = '💬';
                    
                    return `
<div class="obsidian-callout callout-${type}" data-callout="${type}">
  <div class="callout-title">
    <span class="callout-icon">${icon}</span>
    <span class="callout-title-text">${titleHtml}</span>
  </div>
  <div class="callout-content">
    ${bodyHtml}
  </div>
</div>`;
                }
                
                // Fallback to default blockquote rendering
                return `<blockquote>\n${this.parser.parse(token.tokens)}</blockquote>\n`;
            }
        }
    });
}
