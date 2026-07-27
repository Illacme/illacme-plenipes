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
    const tabsHtml = langs.map(lc => {
        const ld = data.langs[lc];
        const isDirty = window._isReviewDirty && window._isReviewDirty(lc);
        const cleanLc = lc.toLowerCase();
        const langObj = (window.availableLangs || []).find(l => l.code === cleanLc) || (window.availableLangs || []).find(l => l.code === cleanLc.split('-')[0]);
        const icon = langObj ? langObj.icon : '🌍';
        const dirtyMark = isDirty ? '<span class="review-dirty-dot" style="color:#ffb300; margin-left:4px; font-size:0.9rem;">●</span>' : '';
        const isActive = lc === state.activeLang;
        let langName = langObj ? langObj.name : lc.toUpperCase();
        if (!langObj) {
            try { langName = new Intl.DisplayNames(['en'], { type: 'language' }).of(cleanLc === 'zh' ? 'zh-Hans' : cleanLc) || langName; } catch (e) {}
        }
        let progressSuffix = '';
        if (state.wantedLangs && state.wantedLangs.includes(lc)) {
            const pVal = state.langProgress ? (state.langProgress[lc] || 5) : 5;
            progressSuffix = pVal < 100 
                ? ` <span style="color:#ffb300;font-size:0.75rem;font-weight:normal;">⏳${pVal}%</span>`
                : ` <span style="color:#4caf50;font-size:0.75rem;font-weight:bold;">✅就绪</span>`;
        }
        return `<button class="review-lang-tab ${isActive ? 'active' : ''}" id="review-tab-${lc}" onclick="window.switchReviewLang('${lc}')" style="padding:6px 14px;border-radius:20px;border:1px solid var(--glass-border);background:${isActive ? 'var(--accent-primary)' : 'transparent'};color:${isActive ? '#000' : 'var(--text-dim)'};cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;">${icon} ${langName}${progressSuffix}${dirtyMark}</button>`;
    }).join('');
    document.getElementById('review-drawer-title').textContent = `🔍 译文校对工作台 — ${data.doc_title || state.docId}`;
    document.getElementById('review-lang-tabs').innerHTML = tabsHtml;

    // 🚀 [V79.2] 动态显示出版模式警告横幅
    const mode = data.publishing_mode || 'basic';
    const alertEl = document.getElementById('review-mode-alert');
    if (alertEl) {
        if (mode === 'basic') {
            alertEl.style.display = 'block';
            alertEl.className = 'review-alert-banner';
            alertEl.innerHTML = `⚠️ <b>主权透传中 (基础模式)</b>：当前版图未开启 AI 全文翻译，下方展现的目标语种译文为<b>源语种（中文）物理透传内容</b>。如需启用大模型自动翻译，请前往 <a href="#/settings" onclick="window.closeTranslationReview();">系统设置</a> 将出版模式切换为 <b>全球模式 (Global)</b> 并重新同步。`;
        } else if (mode === 'enhanced') {
            alertEl.style.display = 'block';
            alertEl.className = 'review-alert-banner alert-enhanced';
            alertEl.innerHTML = `⚠️ <b>局部翻译中 (增强模式)</b>：当前处于增强模式，AI 仅用于文档的 SEO 元数据属性（Description/Keywords）润色，<b>文档正文跳过全文翻译</b>。如需开启全文自动翻译，请前往 <a href="#/settings" onclick="window.closeTranslationReview();">系统设置</a> 切换为 <b>全球模式 (Global)</b>。`;
        } else {
            alertEl.style.display = 'none';
        }
    }

    _reviewRenderBody();
}
function _reviewRenderBody() {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!state.data) return;
    document.getElementById('review-body').style.padding = '0';
    document.getElementById('review-body').style.gap = '0';
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
    const markdownParser = (window.marked && window.marked.parse)
        ? (t) => window.marked.parse(t, { breaks: window.settingsData?.ingress_settings?.hard_line_break ?? false })
        : (t) => t;

    // 1. 构建译文主栏 (Target Column)
    let targetHtml = '';
    const isTranslating = isMissing && state.wantedLangs && state.wantedLangs.includes(lc);
    if (isTranslating) {
        const progress = state.langProgress ? (state.langProgress[lc] || 5) : 5;
        const pInfo = state.data?.langs?.[lc]?.progress;
        const pDesc = pInfo ? ` (${pInfo.translated_paras} / ${pInfo.total_paras} 段已就绪)` : '';
        const steps = [
            { p: 10, name: '任务调度', desc: '初始化翻译管线引擎' },
            { p: 25, name: '文本切片', desc: '解析段落与元数据结构' },
            { p: 40, name: 'AI 物理翻译', desc: '大语言模型正在翻译' },
            { p: 85, name: '自愈比对', desc: '校验图片与双链媒体路径' },
            { p: 95, name: '装配落盘', desc: '写入物理缓存与账本' }
        ];
        const stepList = steps.map(s => {
            let icon = '💤 排队中', style = 'color:var(--text-dim); opacity:0.5;';
            if (progress >= s.p) { icon = '✅ 已完成'; style = 'color:#4caf50; font-weight:bold;'; }
            else if (progress >= (s.p - 15) || (s.p === 10 && progress >= 5)) {
                icon = '⏳ 进行中';
                style = 'color:var(--accent-primary); font-weight:bold; animation: reviewPulse 1.5s infinite;';
            }
            return `<div style="display:flex; justify-content:space-between; padding:8px 12px; margin-bottom:8px; border-radius:6px; background:rgba(255,255,255,0.02); font-size:0.85rem; ${style}"><span>${s.name} <small style="opacity:0.8;font-size:0.75rem;">(${s.desc})</small></span><span>${icon}</span></div>`;
        }).join('');
        targetHtml = `<div style="padding:20px;">
            <div style="font-size:0.95rem; font-weight:bold; margin-bottom:8px;">🌍 全局翻译管线处理中 - ${lc.toUpperCase()}</div>
            <div style="font-size:0.82rem; color:var(--text-dim); margin-bottom:12px;">当前进度: ${progress}%${pDesc}</div>
            <div style="background:rgba(255,255,255,0.05); border-radius:8px; height:8px; width:100%; overflow:hidden; margin-bottom:20px;">
                <div style="background:linear-gradient(90deg, var(--accent-primary) 0%, #ffc107 100%); width:${progress}%; height:100%; transition:width 0.4s ease;"></div>
            </div>
            <style>
                @keyframes reviewPulse { 0% { opacity:0.6; } 50% { opacity:1; } 100% { opacity:0.6; } }
            </style>
            <div>${stepList}</div>
        </div>`;
    } else if (isMissing) {
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

        targetHtml = `<div style="padding:20px; display:flex; flex-direction:column; gap:16px;"><div class="review-status-bar">${statusHtml}</div><div class="review-field"><label>📌 译文标题 (Title)</label><input type="text" id="review-title-input" value="${_escapeHtml(edit.title || '')}" oninput="window._reviewState.edits['${lc}'].title = this.value; window.updateReviewDirtyUI(); window.saveReviewDraft?.('${lc}');" class="review-input" placeholder="输入校对后的标题..."></div><div class="review-field"><label>🏷️ 译文描述 (Description)</label><textarea id="review-desc-input" rows="3" class="review-input" oninput="window._reviewState.edits['${lc}'].desc = this.value; window.updateReviewDirtyUI(); window.saveReviewDraft?.('${lc}');" placeholder="输入校对后的 SEO 描述...">${_escapeHtml(edit.desc || '')}</textarea></div><div class="review-field"><label>📄 正文段落 <small style="color:var(--text-dim)">(点击段落编辑，代码块只读)</small></label><div class="review-paras-container" id="target-paras-container">${targetParas.map(p => `<div id="review-para-${p.index}" data-editing="0" class="review-para-block ${p.type === 'code' ? 'code-block' : ''} ${p._edited ? 'edited' : ''}" onclick="window.reviewEditParagraph(${p.index})" title="${p.type === 'code' ? '代码块（只读）' : '点击编辑此段落'}">${_renderParaBlock(p)}</div>`).join('')}</div></div><div class="review-actions">${actionBtns}</div></div>`;
    }

    // 2. 构建预览分栏 (Preview Column)
    let previewHtml = '';
    if (!isMissing) {
        const renderPreviewTitle = edit.title ? markdownParser(`# ${edit.title}`) : '';
        // 构建 index → source段落 映射，用于图片路径降级回退
        const sourceParaByIndex = {};
        (sourceParas || []).forEach(sp => { sourceParaByIndex[sp.index] = sp.text || ''; });
        previewHtml = `<div style="padding:20px; display:flex; flex-direction:column; gap:16px;"><div class="review-field" style="margin:0;"><label>👁️ 译文预览 (Preview)</label></div><div class="preview-markdown-content" style="color:var(--text-bright);"><div class="preview-title" style="margin-bottom:20px;">${renderPreviewTitle}</div><div id="preview-paras-container">${targetParas.map(p => `<div id="preview-para-${p.index}" class="preview-para-item">${markdownParser(_reviewRewriteMarkdown(p.text || '', state.docId, sourceParaByIndex[p.index] || ''))}</div>`).join('')}</div></div></div>`;
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

    if (!isMissing) {
        window._bindReviewInteractions?.();
    }
}
function _renderParaBlock(p) {
    const retransBtn = p.type !== 'code' ? `<button class="para-retrans-btn" onclick="event.stopPropagation(); window.retranslateSingleParagraph(${p.index});" style="float:right; padding:2px 8px; font-size:0.7rem; background:rgba(255,255,255,0.06); border:1px solid var(--glass-border); color:var(--accent-primary); border-radius:4px; cursor:pointer;" title="使用 AI 单独重译当前段落">🪄 仅重译此段</button>` : '';
    return `${retransBtn}${p._edited ? '<span class="edited-mark">✏️ 已修改</span>' : ''}<div class="review-para-text">${_escapeHtml(p.text)}</div>`;
}
function _reviewShowDrawer() {
    const d = document.getElementById('review-drawer-overlay');
    if (d) { d.style.display = 'flex'; requestAnimationFrame(() => d.style.opacity = '1'); }
}
function _reviewSetLoading(on) {
    const b = document.getElementById('review-body');
    if (b && on) b.innerHTML = '<div class="review-loading">⏳ 正在加载译文...</div>';
}
function _reviewShowError(msg) {
    const b = document.getElementById('review-body');
    if (b) b.innerHTML = `<div class="review-error">❌ ${msg}</div>`;
}
function _escapeHtml(s) { return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
/* ─── 脏态交互的增量 DOM 更新 ─────────────────────────── */
window.updateReviewDirtyUI = function () {
    const state = window._reviewState;
    if (!state.data || !state.activeLang) return;
    const lc = state.activeLang, isDirty = window._isReviewDirty && window._isReviewDirty(lc);
    const tabBtn = document.getElementById(`review-tab-${lc}`), statusBar = document.querySelector('.review-status-bar'), saveBtn = document.querySelector('.review-actions .review-btn.save');
    if (tabBtn) {
        const dot = tabBtn.querySelector('.review-dirty-dot');
        if (isDirty && !dot) tabBtn.insertAdjacentHTML('beforeend', '<span class="review-dirty-dot" style="color:#ffb300; margin-left:4px; font-size:0.9rem;">●</span>');
        else if (!isDirty && dot) dot.remove();
    }
    if (statusBar) {
        const badge = statusBar.querySelector('.review-badge.dirty');
        if (isDirty && !badge) statusBar.insertAdjacentHTML('beforeend', '<span class="review-badge dirty" style="background:var(--accent-secondary, #ffb300); color:#000; font-weight:bold; margin-left:8px; padding:2px 8px; border-radius:4px; font-size:0.75rem; display:inline-block; box-shadow:0 0 8px rgba(255,179,0,0.2);">⚠️ 未保存修改</span>');
        else if (!isDirty && badge) badge.remove();
    }
    if (saveBtn) {
        saveBtn.style.boxShadow = isDirty ? '0 0 12px rgba(255, 179, 0, 0.4)' : '';
        saveBtn.style.border = isDirty ? '1.5px solid var(--accent-primary, #ffab00)' : '';
    }
};

window.openReviewForDoc = async function(targetDocId) {
    if (document.activeElement && typeof document.activeElement.blur === 'function') {
        document.activeElement.blur();
    }
    if (typeof window.openTranslationReview === 'function') {
        window.openTranslationReview(targetDocId);
    }
};

/* ─── 物理资源路径校正与重写（与 vault.parser.js 对准） ───────────────────── */
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
            return `<a href="javascript:void(0)" onclick="window.openReviewForDoc('${clean.replace(/'/g, "\\'")}')" class="wiki-doc-link" style="color:var(--accent-primary, #ffab00); text-decoration:underline; font-weight:600; cursor:pointer;">📄 ${name}</a>`;
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
            return `<a href="javascript:void(0)" onclick="window.openReviewForDoc('${decoded.replace(/'/g, "\\'")}')" class="wiki-doc-link" style="color:var(--accent-primary, #ffab00); text-decoration:underline; font-weight:600; cursor:pointer;">📄 ${textVal}</a>`;
        }
        return `<a href="/api/vault-assets/${encodeURIComponent(decoded)}?relative_to=${encodeURIComponent(docId)}" target="_blank" class="attachment-link">📎 ${textVal}</a>`;
    });
    return md;
}

/* ─── 预览分栏单段落增量渲染（供 reviewSaveParagraph 调用） ─ */
// [AEL-2026-06-14] 保证退出编辑后的增量更新与全量渲染走相同路径：
// _reviewRewriteMarkdown → marked.parse({ breaks })，防止图片路径丢失。
function _reviewRenderPreviewPara(idx, state) {
    const previewBlock = document.getElementById(`preview-para-${idx}`);
    if (!previewBlock || !state) return;
    const lc = state.activeLang;
    const paras = state.edits[lc]?.paragraphs || [];
    if (!paras[idx]) return;
    const sourceParas = state.data?.source_paragraphs || [];
    const sourcePara  = sourceParas.find(sp => sp.index === idx);
    const sourceText  = sourcePara?.text || '';
    const _breaks = window.settingsData?.ingress_settings?.hard_line_break ?? false;
    const rewritten = _reviewRewriteMarkdown(paras[idx].text || '', state.docId, sourceText);
    previewBlock.innerHTML = window.marked.parse(rewritten, { breaks: _breaks });
}
