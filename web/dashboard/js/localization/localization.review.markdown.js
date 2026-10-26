/**
 * 🔒 [I5] Illacme Plenipes Review Markdown Rewriter Module
 * 职责：翻译人工校对工作台的 Markdown 资源路径改写与 Wikilinks 对齐。
 *        符合 SOP-02 300 行物理限制要求。
 */

function _reviewRewriteMarkdown(text, docId, sourceText) {
    if (!text) return '';
    let md = text;

    const fallbackFormatMedia = (url, alt = '', extra = '', onErr = '') => {
        const clean = (url || '').trim();
        const bMatch = clean.match(/(?:bilibili\.com\/video\/|b23\.tv\/)(BV[a-zA-Z0-9]+)/i);
        if (bMatch) return `<div class="preview-media-container preview-bilibili" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="//player.bilibili.com/player.html?bvid=${bMatch[1]}&page=1&high_quality=1&as_wide=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;

        const yMatch = clean.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/i);
        if (yMatch) return `<div class="preview-media-container preview-youtube" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="https://www.youtube-nocookie.com/embed/${yMatch[1]}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;

        const vMatch = clean.match(/vimeo\.com\/([0-9]+)/i);
        if (vMatch) return `<div class="preview-media-container preview-vimeo" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="https://player.vimeo.com/video/${vMatch[1]}" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;

        const qMatch = clean.match(/v\.qq\.com\/x\/(?:cover\/[a-zA-Z0-9]+\/|page\/)([a-zA-Z0-9]+)\.html/i);
        if (qMatch) return `<div class="preview-media-container preview-qqvideo" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="https://v.qq.com/txp/iframe/player.html?vid=${qMatch[1]}" allowFullScreen="true" frameborder="0" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;

        const nMatch = clean.match(/music\.163\.com\/(?:#\/)?song\?id=([0-9]+)/i);
        if (nMatch) return `<div class="preview-media-container preview-netease" style="margin:12px 0;"><iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="100%" height="86" src="//music.163.com/outchain/player?type=2&id=${nMatch[1]}&auto=0&height=66" style="border:none;"></iframe></div>`;

        const sMatch = clean.match(/open\.spotify\.com\/(track|episode|album)\/([a-zA-Z0-9]+)/i);
        if (sMatch) return `<div class="preview-media-container preview-spotify" style="margin:12px 0;"><iframe style="border-radius:12px;border:none;" src="https://open.spotify.com/embed/${sMatch[1]}/${sMatch[2]}" width="100%" height="152" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe></div>`;

        const cMatch = clean.match(/codepen\.io\/([a-zA-Z0-9_-]+)\/pen\/([a-zA-Z0-9_-]+)/i);
        if (cMatch) return `<div class="preview-media-container preview-codepen" style="margin:12px 0;"><iframe height="360" style="width:100%;border-radius:8px;border:none;" scrolling="no" title="CodePen Embed" src="https://codepen.io/${cMatch[1]}/embed/${cMatch[2]}?default-tab=result" frameborder="no" loading="lazy" allowtransparency="true" allowfullscreen="true"></iframe></div>`;

        const cleanNoQuery = clean.split('?')[0].toLowerCase();
        const ext = cleanNoQuery.split('.').pop() || (alt || '').toLowerCase().split('.').pop() || '';
        if (['mp4', 'webm', 'mov', 'm4v', 'ogv'].includes(ext)) {
            return `<div class="preview-media-container preview-video" style="margin:12px 0;"><video controls preload="metadata" style="max-width:100%;border-radius:8px;box-shadow:0 4px 14px rgba(0,0,0,0.15);background:#000;" src="${clean}"></video>${alt ? `<div style="font-size:12px;color:var(--text-muted,#888);margin-top:4px;">📹 ${alt}</div>` : ''}</div>`;
        }
        if (['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'opus'].includes(ext)) {
            return `<div class="preview-media-container preview-audio" style="margin:12px 0;"><audio controls preload="metadata" style="width:100%;max-width:540px;" src="${clean}"></audio>${alt ? `<div style="font-size:12px;color:var(--text-muted,#888);margin-top:4px;">🎵 ${alt}</div>` : ''}</div>`;
        }
        const err = onErr ? ` onerror="${onErr}"` : '';
        const w = (extra && !isNaN(extra.trim())) ? ` width="${extra.trim()}"` : '';
        return `<img src="${clean}" alt="${alt}" loading="lazy"${w}${err} style="max-width:100%;border-radius:6px;" />`;
    };

    const formatMedia = (typeof window !== 'undefined' && typeof window.formatMediaHtml === 'function')
        ? window.formatMediaHtml
        : fallbackFormatMedia;

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

