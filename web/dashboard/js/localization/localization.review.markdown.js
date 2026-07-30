/**
 * 🔒 [I5] Illacme Plenipes Review Markdown Rewriter Module
 * 职责：翻译人工校对工作台的 Markdown 资源路径改写与 Wikilinks 对齐。
 *        符合 SOP-02 300 行物理限制要求。
 */

function _reviewRewriteMarkdown(text, docId, sourceText) {
    if (!text) return '';
    let md = text;
    md = md.replace(/!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, extra) => {
        const clean = decodeURIComponent(path.trim()), url = `/api/vault-assets/${encodeURIComponent(clean)}?relative_to=${encodeURIComponent(docId)}`;
        const err = `this.onerror=null;this.src='${url}';`;
        return (extra && !isNaN(extra.trim())) ? `<img src="${url}" alt="${clean}" width="${extra.trim()}" onerror="${err}" />` : `<img src="${url}" alt="${clean}" onerror="${err}" />`;
    });
    md = md.replace(/(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, display) => {
        const clean = decodeURIComponent(path.trim()), ext = clean.match(/\.([a-zA-Z0-9]+)$/);
        if (!ext || ['md', 'mdx', 'markdown'].includes(ext[1].toLowerCase())) {
            const name = (display || clean).trim();
            return `<a href="javascript:void(0)" onclick="window.openReviewForDoc('${clean.replace(/'/g, "\\'")}')" class="wiki-doc-link" style="color:var(--accent-primary); text-decoration:underline; font-weight:600; cursor:pointer;">📄 ${name}</a>`;
        }
        return `<a href="/api/vault-assets/${encodeURIComponent(clean)}?relative_to=${encodeURIComponent(docId)}" target="_blank" class="attachment-link">📎 ${(display || clean).trim()}</a>`;
    });
    const _srcImgUrls = [];
    if (sourceText) {
        const re = /!\[[^\]]*\]\(([^)]+)\)/g; let m;
        while ((m = re.exec(sourceText)) !== null) {
            const clean = decodeURIComponent(m[1].trim());
            if (!clean.startsWith('http') && !clean.startsWith('data:')) _srcImgUrls.push(`/api/vault-assets/${encodeURIComponent(clean)}?relative_to=${encodeURIComponent(docId)}`);
        }
    }
    let _imgIdx = 0;
    md = md.replace(/!\[\[?([^\]]*)\]?\]\(([^)]+)\)/g, (match, alt, url) => {
        const clean = url.trim();
        if (clean.startsWith('http://') || clean.startsWith('https://') || clean.startsWith('data:')) return match;
        const decoded = decodeURIComponent(clean), resolved = `/api/vault-assets/${encodeURIComponent(decoded)}?relative_to=${encodeURIComponent(docId)}`;
        const filename = decoded.split('/').pop().split('\\').pop(), flatUrl = `/api/vault-assets/${encodeURIComponent(filename)}`;
        const srcUrl = _srcImgUrls[_imgIdx] || ''; _imgIdx++;
        const onErr = `if(!this.dataset.t1){this.dataset.t1='1';this.src='${flatUrl}';} else if(!this.dataset.t2 && '${srcUrl}'){this.dataset.t2='1';this.src='${srcUrl}';}`;
        return `<img src="${resolved}" alt="${alt}" loading="lazy" onerror="${onErr}" style="max-width:100%;border-radius:6px;" />`;
    });
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
