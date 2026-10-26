/**
 * 🔒 [I5] Illacme Plenipes Review Markdown Rewriter Module
 * 职责：翻译人工校对工作台的 Markdown 资源路径改写与 Wikilinks 对齐。
 *        符合 SOP-02 300 行物理限制要求。
 */

function _reviewRewriteMarkdown(text, docId, sourceText) {
    if (!text) return '';
    let md = text;

    const formatMedia = (url, alt = '', extra = '', onErr = '') => {
        if (typeof window !== 'undefined' && typeof window.formatSharedMediaHtml === 'function') {
            return window.formatSharedMediaHtml(url, alt, extra, onErr);
        }
        if (typeof window !== 'undefined' && typeof window.formatMediaHtml === 'function') {
            return window.formatMediaHtml(url, alt, extra, onErr);
        }
        return `<img src="${(url || '').trim()}" alt="${alt}" loading="lazy" style="max-width:100%;border-radius:6px;" />`;
    };

    // 0. 在线流媒体独立直链解析 (单独成行)
    const standaloneVideoReg = /(^|\n)(https?:\/\/(?:(?:www\.)?bilibili\.com\/video\/BV[a-zA-Z0-9]+|(?:www\.)?youtube\.com\/watch\?v=[a-zA-Z0-9_-]{11}|youtu\.be\/[a-zA-Z0-9_-]{11}|vimeo\.com\/[0-9]+|v\.qq\.com\/x\/[^\s\n]+|music\.163\.com\/[^\s\n]+|open\.spotify\.com\/[^\s\n]+|codepen\.io\/[^\s\n]+)[^\s\n]*)(?=$|\n)/gi;
    md = md.replace(standaloneVideoReg, (m, pfx, url) => {
        return pfx + formatMedia(url);
    });

    // 1. Obsidian 双链媒体替换
    md = md.replace(/!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, extra) => {
        const clean = decodeURIComponent(path.trim()), url = `/api/vault-assets/${encodeURIComponent(clean)}?relative_to=${encodeURIComponent(docId)}`;
        const err = `this.onerror=null;this.src='${url}';`;
        return formatMedia(url, clean, extra, err);
    });

    // 2. Obsidian 双链普通附件/跳转
    md = md.replace(/(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, display) => {
        const clean = decodeURIComponent(path.trim()), ext = clean.match(/\.([a-zA-Z0-9]+)$/);
        if (!ext || ['md', 'mdx', 'markdown'].includes(ext[1].toLowerCase())) {
            const name = (display || clean).trim();
            return `<a href="javascript:void(0)" onclick="window.openReviewForDoc('${clean.replace(/'/g, "\\'")}')" class="wiki-doc-link" style="color:var(--accent-primary); text-decoration:underline; font-weight:600; cursor:pointer;">📄 ${name}</a>`;
        }
        return `<a href="/api/vault-assets/${encodeURIComponent(clean)}?relative_to=${encodeURIComponent(docId)}" target="_blank" class="attachment-link">📎 ${(display || clean).trim()}</a>`;
    });

    // 3. 收集原文图片路径辅助回填
    const _srcImgUrls = [];
    if (sourceText) {
        const re = /!\[[^\]]*\]\(([^)]+)\)/g; let m;
        while ((m = re.exec(sourceText)) !== null) {
            const clean = decodeURIComponent(m[1].trim());
            if (!clean.startsWith('http') && !clean.startsWith('data:')) _srcImgUrls.push(`/api/vault-assets/${encodeURIComponent(clean)}?relative_to=${encodeURIComponent(docId)}`);
        }
    }
    let _imgIdx = 0;

    // 4. 标准 Markdown 媒体替换
    md = md.replace(/!\[\[?([^\]]*)\]?\]\(([^)]+)\)/g, (match, alt, url) => {
        const clean = url.trim();
        if (clean.startsWith('http://') || clean.startsWith('https://') || clean.startsWith('data:')) return formatMedia(clean, alt);
        const decoded = decodeURIComponent(clean), resolved = `/api/vault-assets/${encodeURIComponent(decoded)}?relative_to=${encodeURIComponent(docId)}`;
        const filename = decoded.split('/').pop().split('\\').pop(), flatUrl = `/api/vault-assets/${encodeURIComponent(filename)}`;
        const srcUrl = _srcImgUrls[_imgIdx] || ''; _imgIdx++;
        const onErr = `if(!this.dataset.t1){this.dataset.t1='1';this.src='${flatUrl}';} else if(!this.dataset.t2 && '${srcUrl}'){this.dataset.t2='1';this.src='${srcUrl}';}`;
        return formatMedia(resolved, alt, '', onErr);
    });

    // 5. 标准 Markdown 链接替换
    md = md.replace(/(?<!\!)\[([^\]]+)\]\(([^)]+)\)/g, (match, textVal, url) => {
        const clean = url.trim();
        if (clean.startsWith('http://') || clean.startsWith('https://') || clean.startsWith('data:') || clean.startsWith('#')) return match;
        const decoded = decodeURIComponent(clean), ext = decoded.match(/\.([a-zA-Z0-9]+)$/);
        if (!ext || ['md', 'mdx', 'markdown'].includes(ext[1].toLowerCase())) {
            return `<a href="javascript:void(0)" onclick="window.openReviewForDoc('${decoded.replace(/'/g, "\\'")}')" class="wiki-doc-link" style="color:var(--accent-primary); text-decoration:underline; font-weight:600; cursor:pointer;">📄 ${textVal}</a>`;
        }
        return `<a href="/api/vault-assets/${encodeURIComponent(decoded)}?relative_to=${encodeURIComponent(docId)}" target="_blank" class="attachment-link">📎 ${textVal}</a>`;
    });
    return md;
}

