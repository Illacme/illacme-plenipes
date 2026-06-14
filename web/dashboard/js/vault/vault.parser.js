/**
 * 🚀 [V87.0] Illacme Plenipes Markdown Parser & Sync Scroll Shard
 * 职责：Obsidian 双链、Wiki 联动路径对齐、Markdown 渲染及编辑器同步滚动。
 */

window.updateEditorPreview = () => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    if (!body || !preview) return;

    let mdContent = body.value;

    // 1. 物理资源解析：替换 Obsidian 双链图片 ![[image.png]] 或 ![[image.png|width]]
    mdContent = mdContent.replace(/!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, extra) => {
        const cleanPath = decodeURIComponent(path.trim());
        const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
        const alt = cleanPath;
        if (extra && !isNaN(extra.trim())) {
            return `<img src="${url}" alt="${alt}" width="${extra.trim()}" />`;
        }
        return `![${alt}](${url})`;
    });

    // 2. 物理资源解析：替换 Obsidian 双链普通附件 [[file.pdf]] 或 [[file.pdf|display]] (排除了带 ! 前缀的情况)
    mdContent = mdContent.replace(/(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, display) => {
        const cleanPath = decodeURIComponent(path.trim());
        const displayName = (display || cleanPath).trim();
        const extMatch = cleanPath.match(/\.([a-zA-Z0-9]+)$/);
        if (extMatch && !['md', 'mdx', 'markdown'].includes(extMatch[1].toLowerCase())) {
            const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
            return `<a href="${url}" target="_blank" class="attachment-link">📎 ${displayName}</a>`;
        } else {
            const cleanDocPath = cleanPath.replace(/\.mdx?$/, '');
            return `<a href="#" onclick="openEditorFromPreview('${cleanDocPath.replace(/'/g, "\\'")}', event)" class="wiki-doc-link">📄 ${displayName}</a>`;
        }
    });

    // 3. 物理资源解析：替换标准 Markdown 图片 ![alt](path)
    mdContent = mdContent.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('data:')) {
            return match;
        }
        const decodedUrl = decodeURIComponent(cleanUrl);
        const resolvedUrl = `/api/vault-assets/${encodeURIComponent(decodedUrl)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
        return `![${alt}](${resolvedUrl})`;
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

    // 🚀 [V87.0] 实时解析 Markdown (依赖 vendor/marked.js)
    if (typeof marked !== 'undefined') {
        preview.innerHTML = marked.parse(mdContent);
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
    // [AEL-2026-06-14] 激活 GFM 换行模式：使段落内的单个换行符渲染为 <br>，
    // 解决预览区文本与编辑器原稿区换行视觉不一致的问题（Soft-break → Hard-break）。
    marked.use({ breaks: true });
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
