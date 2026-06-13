/**
 * 🔒 [I5] Illacme Plenipes Translation Review Rendering Module
 * 职责：翻译人工校对回流工作台的 HTML 结构组装与渲染。
 *        本文件由 localization.review.js 拆分而来，符合 SOP-02 降解要求。
 */

/* ─── 内部：渲染整个抽屉 ─────────────────────────────── */
function _reviewRender() {
    const state = window._reviewState;
    const data = state.data;
    if (!data) return;
    const drawer = document.getElementById('review-drawer');
    if (!drawer) return;
    const langs = Object.keys(data.langs || {});

    // 语种标签 tabs
    const tabsHtml = langs.map(lc => {
        const ld = data.langs[lc];
        const isDirty = window._isReviewDirty && window._isReviewDirty(lc);
        const badge = ld.human_approved ? (ld.review_is_stale ? '⚠️' : '🔒') : '🤖';
        const dirtyMark = isDirty ? '<span class="review-dirty-dot" style="color:#ffb300; margin-left:4px; font-size:0.9rem;">●</span>' : '';
        const isActive = lc === state.activeLang;
        return `<button class="review-lang-tab ${isActive ? 'active' : ''}" id="review-tab-${lc}" onclick="window.switchReviewLang('${lc}')" style="padding:6px 14px;border-radius:20px;border:1px solid var(--glass-border);background:${isActive ? 'var(--accent-primary)' : 'transparent'};color:${isActive ? '#000' : 'var(--text-dim)'};cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;">${badge} ${lc.toUpperCase()}${dirtyMark}</button>`;
    }).join('');

    document.getElementById('review-drawer-title').textContent = `🔍 译文校对工作台 — ${data.doc_title || state.docId}`;
    document.getElementById('review-lang-tabs').innerHTML = tabsHtml;
    _reviewRenderBody();
}

function _reviewRenderBody() {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!state.data) return;

    // Reset review-body padding so split view can go edge to edge
    document.getElementById('review-body').style.padding = '0';
    document.getElementById('review-body').style.gap = '0';

    // Synchronize toggle buttons style based on layout state
    const btnSource = document.getElementById('btn-view-source');
    const btnPreview = document.getElementById('btn-view-preview');
    if (btnSource) {
        btnSource.style.background = state.showSource ? 'rgba(255,255,255,0.1)' : 'transparent';
        btnSource.style.color = state.showSource ? 'var(--text-bright)' : 'var(--text-dim)';
        btnSource.style.border = state.showSource ? '1px solid var(--accent-primary)' : '1px solid transparent';
    }
    if (btnPreview) {
        btnPreview.style.background = state.showPreview ? 'rgba(255,255,255,0.1)' : 'transparent';
        btnPreview.style.color = state.showPreview ? 'var(--text-bright)' : 'var(--text-dim)';
        btnPreview.style.border = state.showPreview ? '1px solid var(--accent-primary)' : '1px solid transparent';
    }

    const ld = state.data.langs[lc] || {};
    const edit = state.edits[lc] || {};
    const isMissing = ld.is_missing;
    const sourceParas = state.data.source_paragraphs || [];
    const targetParas = edit.paragraphs || [];
    const markdownParser = (window.marked && window.marked.parse) ? window.marked.parse : (t) => t;

    // 1. 构建译文主栏 (Target Column)
    let targetHtml = '';
    if (isMissing) {
        targetHtml = `<div style="padding:20px;"><div class="review-status-bar"><span class="review-badge ai">ℹ️ 无可用译文快照</span></div><div class="review-error" style="color:var(--text-dim); text-align:center; padding: 40px 0;">当前文档可能尚未完成 AI 译文的物理写入，或物理缓存已被清理。<br><br><button onclick="window.triggerSingleTranslation('current')" style="margin-top:20px; margin-right:12px; padding:10px 20px; background:var(--accent-primary); color:#000; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:0.9rem; box-shadow:0 4px 15px rgba(255, 171, 0, 0.3); transition:transform 0.2s;">🚀 仅生成当前语种译文</button><button onclick="window.triggerSingleTranslation('all')" style="margin-top:20px; padding:10px 20px; background:var(--bg-glass-heavy, rgba(255,255,255,0.05)); color:var(--text-bright, #fff); border:1px solid var(--glass-border, rgba(255,255,255,0.1)); border-radius:6px; font-weight:bold; cursor:pointer; font-size:0.9rem; transition:transform 0.2s;">🌍 生成所有目标语种译文</button></div></div>`;
    } else {
        let statusHtml = ld.human_approved
            ? (ld.review_is_stale ? `<span class="review-badge stale">⚠️ 原稿已变更，建议复核 · 锁定于 ${new Date(ld.reviewed_at).toLocaleDateString('zh-CN')}</span>` : `<span class="review-badge locked">🔒 人工锁定 · ${new Date(ld.reviewed_at).toLocaleDateString('zh-CN')} · ${ld.reviewed_by || 'commander'}</span>`)
            : `<span class="review-badge ai">🤖 AI 生成，未校对</span>`;

        const isDirty = window._isReviewDirty && window._isReviewDirty(lc);
        if (isDirty) statusHtml += `<span class="review-badge dirty" style="background:var(--accent-secondary, #ffb300); color:#000; font-weight:bold; margin-left:8px; padding:2px 8px; border-radius:4px; font-size:0.75rem; display:inline-block; box-shadow:0 0 8px rgba(255,179,0,0.2);">⚠️ 未保存修改</span>`;

        const saveStyle = isDirty ? 'box-shadow: 0 0 12px rgba(255, 179, 0, 0.4); border: 1.5px solid var(--accent-primary, #ffab00);' : '';
        const actionBtns = ld.human_approved
            ? `<button class="review-btn unlock" onclick="window.unlockTranslationReview()">🗑️ 重置为 AI 重译</button><button class="review-btn save active" style="${saveStyle}" onclick="window.saveTranslationReview()">🔒 更新锁定内容</button>`
            : `<button class="review-btn unlock" style="margin-right: auto;" onclick="window.triggerSingleTranslation('current')">🔄 重新生成当前语种译文</button><button class="review-btn save" style="${saveStyle}" onclick="window.saveTranslationReview()">🔒 保存并锁定（语种级）</button>`;

        targetHtml = `<div style="padding:20px; display:flex; flex-direction:column; gap:16px;"><div class="review-status-bar">${statusHtml}</div><div class="review-field"><label>📌 译文标题 (Title)</label><input type="text" id="review-title-input" value="${_escapeHtml(edit.title || '')}" oninput="window._reviewState.edits['${lc}'].title = this.value; window.updateReviewDirtyUI();" class="review-input" placeholder="输入校对后的标题..."></div><div class="review-field"><label>🏷️ 译文描述 (Description)</label><textarea id="review-desc-input" rows="3" class="review-input" oninput="window._reviewState.edits['${lc}'].desc = this.value; window.updateReviewDirtyUI();" placeholder="输入校对后的 SEO 描述...">${_escapeHtml(edit.desc || '')}</textarea></div><div class="review-field"><label>📄 正文段落 <small style="color:var(--text-dim)">(点击段落编辑，代码块只读)</small></label><div class="review-paras-container" id="target-paras-container">${targetParas.map(p => `<div id="review-para-${p.index}" data-editing="0" class="review-para-block ${p.type === 'code' ? 'code-block' : ''} ${p._edited ? 'edited' : ''}" onclick="window.reviewEditParagraph(${p.index})" title="${p.type === 'code' ? '代码块（只读）' : '点击编辑此段落'}">${_renderParaBlock(p)}</div>`).join('')}</div></div><div class="review-actions">${actionBtns}</div></div>`;
    }

    // 2. 构建预览分栏 (Preview Column)
    let previewHtml = '';
    if (!isMissing) {
        const renderPreviewTitle = edit.title ? markdownParser(`# ${edit.title}`) : '';
        previewHtml = `<div style="padding:20px; display:flex; flex-direction:column; gap:16px;"><div class="review-field" style="margin:0;"><label>👁️ 译文预览 (Preview)</label></div><div class="preview-markdown-content" style="color:var(--text-bright);"><div class="preview-title" style="margin-bottom:20px;">${renderPreviewTitle}</div><div id="preview-paras-container">${targetParas.map(p => `<div id="preview-para-${p.index}" class="preview-para-item">${markdownParser(_reviewRewriteMarkdown(p.text || '', state.docId))}</div>`).join('')}</div></div></div>`;
    }

    // 3. 构建原文参考分栏 (Source Column)
    const sourceHtml = `<div style="padding:20px; display:flex; flex-direction:column; gap:16px;"><div class="review-field" style="margin:0;"><label>📜 原文参考 (Source)</label></div><div class="review-field"><label>📌 原文标题 (Source Title)</label><div style="background:rgba(255,255,255,0.02); opacity:0.8; padding:10px 14px; border-radius:6px; font-size:0.84rem; color:var(--text-dim); border:1px solid var(--glass-border); line-height:1.5;">${_escapeHtml(state.data.source_title || '无标题')}</div></div><div class="review-field"><label>🏷️ 原文描述 (Source Description)</label><div style="background:rgba(255,255,255,0.02); opacity:0.8; padding:10px 14px; border-radius:6px; font-size:0.84rem; color:var(--text-dim); border:1px solid var(--glass-border); line-height:1.5; white-space:pre-wrap;">${_escapeHtml(state.data.source_desc || '无描述')}</div></div><div class="review-field"><label>📄 原文正文段落 (Source Paragraphs)</label><div class="review-paras-container" id="source-paras-container">${sourceParas.map((sp, idx) => `<div id="source-para-${idx}" class="review-para-block source-only" style="background:rgba(255,255,255,0.02); opacity:0.8; margin-bottom:6px; padding:6px 12px; border-radius:6px;"><div class="review-para-text" style="color:var(--text-dim); font-size:0.85rem; line-height:1.6; font-family:inherit; white-space:pre-wrap; margin:0;">${_escapeHtml(sp.text)}</div></div>`).join('')}</div></div></div>`;

    const displayPreview = state.showPreview ? 'block' : 'none';
    const displaySource = state.showSource ? 'block' : 'none';
    const borderTarget = (state.showPreview || state.showSource) ? '1px solid var(--glass-border)' : 'none';
    const borderPreview = (state.showPreview && state.showSource) ? '1px solid var(--glass-border)' : 'none';

    document.getElementById('review-body').innerHTML = `
        <div style="display:flex; height:100%; width:100%; overflow:hidden;">
            <div style="flex:1; min-width:0; border-right:${borderTarget}; overflow-y:auto;" id="col-target">${targetHtml}</div>
            <div style="flex:1; min-width:0; border-right:${borderPreview}; overflow-y:auto; display:${displayPreview};" id="col-preview">${previewHtml}</div>
            <div style="flex:1; min-width:0; overflow-y:auto; display:${displaySource};" id="col-source">${sourceHtml}</div>
        </div>
    `;

    const colTarget = document.getElementById('col-target');
    const colPreview = document.getElementById('col-preview');
    const colSource = document.getElementById('col-source');
    if (colTarget && colPreview && colSource && !isMissing) {
        let activeScrollSource = null, scrollTimeout = null;
        const onScrollHandler = (e) => {
            const target = e.currentTarget;
            if (activeScrollSource && activeScrollSource !== target) return;
            activeScrollSource = target;
            const pct = target.scrollTop / (target.scrollHeight - target.clientHeight || 1);
            const visibleCols = [colTarget, colPreview, colSource].filter(col => col && col.style.display !== 'none');
            visibleCols.forEach(col => {
                if (col !== target) col.scrollTop = pct * (col.scrollHeight - col.clientHeight);
            });
            if (scrollTimeout) clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => { activeScrollSource = null; }, 80);
        };
        colTarget.addEventListener('scroll', onScrollHandler);
        colPreview.addEventListener('scroll', onScrollHandler);
        colSource.addEventListener('scroll', onScrollHandler);

        // 🚀 绑定段落鼠标划过联动高亮效果
        const targetBlocks = colTarget.querySelectorAll('.review-para-block');
        targetBlocks.forEach(block => {
            block.addEventListener('mouseenter', () => {
                const idAttr = block.id;
                if (!idAttr) return;
                const idx = idAttr.replace('review-para-', '');
                const srcBlock = document.getElementById(`source-para-${idx}`);
                if (srcBlock) srcBlock.classList.add('linked-hover');
                const prevBlock = document.getElementById(`preview-para-${idx}`);
                if (prevBlock) prevBlock.classList.add('linked-hover');
            });
            block.addEventListener('mouseleave', () => {
                const idAttr = block.id;
                if (!idAttr) return;
                const idx = idAttr.replace('review-para-', '');
                const srcBlock = document.getElementById(`source-para-${idx}`);
                if (srcBlock) srcBlock.classList.remove('linked-hover');
                const prevBlock = document.getElementById(`preview-para-${idx}`);
                if (prevBlock) prevBlock.classList.remove('linked-hover');
            });
        });
    }
}

function _renderParaBlock(p) {
    const editedMark = p._edited ? '<span class="edited-mark">✏️ 已修改</span>' : '';
    return `${editedMark}<div class="review-para-text">${_escapeHtml(p.text)}</div>`;
}

/* ─── 抽屉显隐控制 ───────────────────────────────────── */
function _reviewShowDrawer() {
    const drawer = document.getElementById('review-drawer-overlay');
    if (drawer) {
        drawer.style.display = 'flex';
        requestAnimationFrame(() => { drawer.style.opacity = '1'; });
    }
}

function _reviewSetLoading(on) {
    const body = document.getElementById('review-body');
    if (body && on) body.innerHTML = '<div class="review-loading">⏳ 正在加载译文快照...</div>';
}

function _reviewShowError(msg) {
    const body = document.getElementById('review-body');
    if (body) body.innerHTML = `<div class="review-error">❌ ${msg}</div>`;
}

function _escapeHtml(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ─── 脏态交互的增量 DOM 更新 ─────────────────────────── */
window.updateReviewDirtyUI = function () {
    const state = window._reviewState;
    if (!state.data) return;
    const lc = state.activeLang;
    if (!lc) return;
    const isDirty = window._isReviewDirty && window._isReviewDirty(lc);

    const tabBtn = document.getElementById(`review-tab-${lc}`);
    if (tabBtn) {
        const oldDot = tabBtn.querySelector('.review-dirty-dot');
        if (isDirty && !oldDot) tabBtn.insertAdjacentHTML('beforeend', '<span class="review-dirty-dot" style="color:#ffb300; margin-left:4px; font-size:0.9rem;">●</span>');
        else if (!isDirty && oldDot) oldDot.remove();
    }

    const statusBar = document.querySelector('.review-status-bar');
    if (statusBar) {
        const oldBadge = statusBar.querySelector('.review-badge.dirty');
        if (isDirty && !oldBadge) statusBar.insertAdjacentHTML('beforeend', '<span class="review-badge dirty" style="background:var(--accent-secondary, #ffb300); color:#000; font-weight:bold; margin-left:8px; padding:2px 8px; border-radius:4px; font-size:0.75rem; display:inline-block; box-shadow:0 0 8px rgba(255,179,0,0.2);">⚠️ 未保存修改</span>');
        else if (!isDirty && oldBadge) oldBadge.remove();
    }

    const saveBtn = document.querySelector('.review-actions .review-btn.save');
    if (saveBtn) {
        saveBtn.style.boxShadow = isDirty ? '0 0 12px rgba(255, 179, 0, 0.4)' : '';
        saveBtn.style.border = isDirty ? '1.5px solid var(--accent-primary, #ffab00)' : '';
    }
};

/* ─── 物理资源路径校正与重写（与 vault.parser.js 对准） ───────────────────── */
function _reviewRewriteMarkdown(text, docId) {
    if (!text) return '';
    let md = text;
    // 1. 替换 Obsidian 双链图片 ![[image.png]]
    md = md.replace(/!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, extra) => {
        const cleanPath = decodeURIComponent(path.trim());
        const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(docId)}`;
        const alt = cleanPath;
        if (extra && !isNaN(extra.trim())) {
            return `<img src="${url}" alt="${alt}" width="${extra.trim()}" />`;
        }
        return `![${alt}](${url})`;
    });
    // 2. 替换 Obsidian 双链普通附件
    md = md.replace(/(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, display) => {
        const cleanPath = decodeURIComponent(path.trim());
        const displayName = (display || cleanPath).trim();
        const extMatch = cleanPath.match(/\.([a-zA-Z0-9]+)$/);
        if (extMatch && !['md', 'mdx', 'markdown'].includes(extMatch[1].toLowerCase())) {
            const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(docId)}`;
            return `<a href="${url}" target="_blank" class="attachment-link">📎 ${displayName}</a>`;
        }
        return match;
    });
    // 3. 替换标准 Markdown 图片
    md = md.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('data:')) {
            return match;
        }
        const decodedUrl = decodeURIComponent(cleanUrl);
        const resolvedUrl = `/api/vault-assets/${encodeURIComponent(decodedUrl)}?relative_to=${encodeURIComponent(docId)}`;
        return `![${alt}](${resolvedUrl})`;
    });
    // 4. 替换标准 Markdown 链接
    md = md.replace(/(?<!\!)\[([^\]]+)\]\(([^)]+)\)/g, (match, textVal, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('data:') || cleanUrl.startsWith('#')) {
            return match;
        }
        const decodedUrl = decodeURIComponent(cleanUrl);
        const extMatch = decodedUrl.match(/\.([a-zA-Z0-9]+)$/);
        if (extMatch && !['md', 'mdx', 'markdown'].includes(extMatch[1].toLowerCase())) {
            const resolvedUrl = `/api/vault-assets/${encodeURIComponent(decodedUrl)}?relative_to=${encodeURIComponent(docId)}`;
            return `<a href="${resolvedUrl}" target="_blank" class="attachment-link">📎 ${textVal}</a>`;
        }
        return match;
    });
    return md;
}
