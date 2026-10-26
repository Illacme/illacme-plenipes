/**
 * 🎬 [V1.0] Illacme Plenipes Vault Media Embed Formatter Shard
 * 职责：负责原稿预览与译文校对工作台的多媒体外链（B站、YouTube、Vimeo、QQ视频、网易云、Spotify、CodePen等）及音视频/图片渲染。
 * 🛡️ [SOP-01] 物理行数严格 ≤ 300 行。
 */

(function () {
    'use strict';

    const PREVIEW_VIDEO_EXTS = new Set(['mp4', 'webm', 'mov', 'm4v', 'ogv']);
    const PREVIEW_AUDIO_EXTS = new Set(['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'opus']);

    window.formatMediaHtml = (url, alt = '', extra = '', onErr = '') => {
        const cleanUrl = (url || '').trim();
        // 1. 在线流媒体与交互平台识别 (B站 / YouTube / Vimeo / QQ视频 / 网易云音乐 / Spotify / CodePen)
        const bMatch = cleanUrl.match(/(?:bilibili\.com\/video\/|b23\.tv\/)(BV[a-zA-Z0-9]+)/i);
        if (bMatch) {
            let p = '1';
            const pMatch = cleanUrl.match(/[?&](?:p|page)=([0-9]+)/i);
            if (pMatch) p = pMatch[1];
            return `<div class="preview-media-container preview-bilibili" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="//player.bilibili.com/player.html?bvid=${bMatch[1]}&page=${p}&high_quality=1&as_wide=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;
        }

        const yMatch = cleanUrl.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/i);
        if (yMatch) {
            let extraQuery = '';
            const tMatch = cleanUrl.match(/[?&](?:t|start)=([0-9]+)s?/i);
            if (tMatch) extraQuery = `?start=${tMatch[1]}`;
            return `<div class="preview-media-container preview-youtube" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="https://www.youtube-nocookie.com/embed/${yMatch[1]}${extraQuery}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;
        }

        const vMatch = cleanUrl.match(/vimeo\.com\/([0-9]+)/i);
        if (vMatch) return `<div class="preview-media-container preview-vimeo" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="https://player.vimeo.com/video/${vMatch[1]}" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;

        const qMatch = cleanUrl.match(/v\.qq\.com\/x\/(?:cover\/[a-zA-Z0-9]+\/|page\/)([a-zA-Z0-9]+)\.html/i);
        if (qMatch) return `<div class="preview-media-container preview-qqvideo" style="position:relative;width:100%;max-width:720px;aspect-ratio:16/9;margin:12px 0;border-radius:8px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);background:#000;"><iframe src="https://v.qq.com/txp/iframe/player.html?vid=${qMatch[1]}" allowFullScreen="true" frameborder="0" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe></div>`;

        const nMatch = cleanUrl.match(/music\.163\.com\/(?:#\/)?song\?id=([0-9]+)/i);
        if (nMatch) return `<div class="preview-media-container preview-netease" style="margin:12px 0;"><iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="100%" height="86" src="//music.163.com/outchain/player?type=2&id=${nMatch[1]}&auto=0&height=66" style="border:none;"></iframe></div>`;

        const sMatch = cleanUrl.match(/open\.spotify\.com\/(track|episode|album)\/([a-zA-Z0-9]+)/i);
        if (sMatch) return `<div class="preview-media-container preview-spotify" style="margin:12px 0;"><iframe style="border-radius:12px;border:none;" src="https://open.spotify.com/embed/${sMatch[1]}/${sMatch[2]}" width="100%" height="152" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe></div>`;

        const cMatch = cleanUrl.match(/codepen\.io\/([a-zA-Z0-9_-]+)\/pen\/([a-zA-Z0-9_-]+)/i);
        if (cMatch) return `<div class="preview-media-container preview-codepen" style="margin:12px 0;"><iframe height="360" style="width:100%;border-radius:8px;border:none;" scrolling="no" title="CodePen Embed" src="https://codepen.io/${cMatch[1]}/embed/${cMatch[2]}?default-tab=result" frameborder="no" loading="lazy" allowtransparency="true" allowfullscreen="true"></iframe></div>`;

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

    window.formatSharedMediaHtml = window.formatMediaHtml;
})();
