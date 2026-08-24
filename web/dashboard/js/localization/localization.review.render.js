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
            try { langName = new Intl.DisplayNames(['en'], { type: 'language' }).of(cleanLc === 'zh' ? 'zh-Hans' : cleanLc) || langName; } catch (e) { }
        }
        let progressSuffix = '';
        if (state.wantedLangMap && state.wantedLangMap[lc]) {
            const langState = state.wantedLangMap[lc];
            const pVal = langState.progress || 5;
            progressSuffix = langState.status === 'running'
                ? ` <span style="color:#ffb300;font-size:0.75rem;font-weight:normal;">⏳${pVal}%</span>`
                : ` <span style="color:#4caf50;font-size:0.75rem;font-weight:bold;">✅就绪</span>`;
        } else if (state.wantedLangs && state.wantedLangs.includes(lc)) {
            progressSuffix = ` <span style="color:#ffb300;font-size:0.75rem;font-weight:normal;">⏳排队中</span>`;
        }
        return `<button class="review-lang-tab ${isActive ? 'active' : ''}" id="review-tab-${lc}" onclick="window.switchReviewLang('${lc}')" style="padding:6px 14px;border-radius:20px;border:1px solid var(--glass-border);background:${isActive ? 'var(--accent-primary)' : 'transparent'};color:${isActive ? '#000' : 'var(--text-dim)'};cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;">${icon} ${langName}${progressSuffix}${dirtyMark}</button>`;
    }).join('');
    document.getElementById('review-drawer-title').textContent = `🔍 译文校对工作台 — ${data.doc_title || state.docId}`;
    document.getElementById('review-lang-tabs').innerHTML = tabsHtml;
    const mode = data.publishing_mode || 'basic', alertEl = document.getElementById('review-mode-alert');
    if (alertEl) {
        if (mode === 'basic') {
            alertEl.style.display = 'block'; alertEl.className = 'review-alert-banner';
            alertEl.innerHTML = `⚠️ <b>主权透传中 (基础模式)</b>：当前品牌未开启 AI 全文翻译，下方展现的目标语种译文为<b>源语种（中文）物理透传内容</b>。如需启用大模型自动翻译，请前往 <a href="#/settings" onclick="window.closeTranslationReview();">系统设置</a> 将出版模式切换为 <b>全球模式 (Global)</b> 并重新同步。`;
        } else if (mode === 'enhanced') {
            alertEl.style.display = 'block'; alertEl.className = 'review-alert-banner alert-enhanced';
            alertEl.innerHTML = `⚠️ <b>局部翻译中 (增强模式)</b>：当前处于增强模式，AI 仅用于文档的 SEO 元数据属性（Description/Keywords）润色，<b>文档正文跳过全文翻译</b>。如需开启全文自动翻译，请前往 <a href="#/settings" onclick="window.closeTranslationReview();">系统设置</a> 切换为 <b>全球模式 (Global)</b>。`;
        } else { alertEl.style.display = 'none'; }
    }
    _reviewRenderBody();
}

function _formatReviewDate(isoStr) {
    if (!isoStr) return '';
    try {
        const d = new Date(isoStr);
        if (isNaN(d.getTime())) return isoStr;
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        return `${year}/${month}/${day} ${hours}:${minutes}`;
    } catch (e) {
        return isoStr;
    }
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
    const isTranslating = isMissing && state.wantedLangMap && state.wantedLangMap[lc] && state.wantedLangMap[lc].status === 'running';
    if (isTranslating) {
        const langTask = state.wantedLangMap[lc] || {};
        const progress = langTask.progress || 5;
        const pInfo = state.data?.langs?.[lc]?.progress;
        const useLiveProgress = pInfo && pInfo.running;
        const tParas = useLiveProgress ? (pInfo.translated_paras || 0) : (langTask.translated_paras || 0);
        const validSourceParasCount = sourceParas.filter(p => p.index >= 0).length || 1;
        const totalParas = useLiveProgress ? (pInfo.total_paras || validSourceParasCount) : (langTask.total_paras || validSourceParasCount);
        const pDesc = useLiveProgress ? ` (${tParas} / ${totalParas} 段已就绪)` : ` (0 / ${totalParas} 段排队中...)`;

        const paraPercent = Math.min(100, Math.round((tParas / Math.max(1, totalParas)) * 100));
        const isBodyDone = tParas >= totalParas && totalParas > 0;
        const metaStatus = isBodyDone ? (progress >= 85 ? '✅ 已完成润色' : '⏳ 正在润色') : '💤 等待正文后执行';
        const metaStyle = isBodyDone ? (progress >= 85 ? 'color:#4caf50;' : 'color:var(--accent-primary);') : 'color:var(--text-dim);';

        const steps = [
            { p: 10, name: '任务调度', desc: '初始化翻译管线引擎', check: progress >= 10 },
            { p: 25, name: '文本切片', desc: '解析段落与元数据结构', check: progress >= 25 },
            { p: 65, name: '正文段落翻译', desc: '大模型分段算力收割', check: isBodyDone },
            { p: 85, name: '元数据生成润色', desc: 'SEO 标题、描述与标签优化', check: isBodyDone && progress >= 85 },
            { p: 95, name: '合规自愈比对', desc: '校验图片与双链媒体路径', check: isBodyDone && progress >= 95 },
            { p: 100, name: '装配落盘', desc: '写入物理缓存与账本', check: progress >= 100 }
        ];
        let activeFound = false;
        const stepList = steps.map(s => {
            let icon = '💤 排队中', style = 'color:var(--text-dim); opacity:0.5;';
            if (s.check) {
                icon = '✅ 已完成';
                style = 'color:#4caf50; font-weight:bold;';
            } else if (!activeFound) {
                activeFound = true;
                icon = '⏳ 进行中';
                style = 'color:var(--accent-primary); font-weight:bold; animation: reviewPulse 1.5s infinite;';
            }
            return `<div style="display:flex; justify-content:space-between; padding:8px 12px; margin-bottom:8px; border-radius:6px; background:rgba(255,255,255,0.02); font-size:0.85rem; ${style}"><span>${s.name} <small style="opacity:0.8;font-size:0.75rem;">(${s.desc})</small></span><span>${icon}</span></div>`;
        }).join('');

        targetHtml = `<div style="padding:20px;">
            <div style="font-size:0.95rem; font-weight:bold; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <span>🌍 全局翻译管线处理中 - ${lc.toUpperCase()}</span>
                <span id="review-main-progress-percent" style="font-size:0.82rem; color:var(--accent-primary); font-family:monospace;">${progress}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.05); border-radius:8px; height:8px; width:100%; overflow:hidden; margin-bottom:16px;">
                <div id="review-main-progress-bar" style="background:linear-gradient(90deg, var(--accent-primary) 0%, #ffc107 100%); width:${progress}%; height:100%; transition:width 0.4s ease;"></div>
            </div>

            <!-- 📊 双轨处理进度卡片 -->
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:20px;">
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:12px;">
                    <div style="font-size:0.8rem; font-weight:bold; color:var(--text-bright); margin-bottom:6px;">📄 正文段落翻译</div>
                    <div id="review-para-progress-text" style="font-size:0.78rem; color:var(--text-dim); margin-bottom:8px;">${tParas} / ${totalParas} 段已就绪 (${paraPercent}%)</div>
                    <div style="background:rgba(255,255,255,0.05); border-radius:4px; height:4px; width:100%; overflow:hidden;">
                        <div id="review-para-progress-bar" style="background:var(--accent-primary); width:${paraPercent}%; height:100%; transition:width 0.3s ease;"></div>
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:12px;">
                    <div style="font-size:0.8rem; font-weight:bold; color:var(--text-bright); margin-bottom:6px;">🏷️ 元数据生成与润色</div>
                    <div id="review-meta-progress-text" style="font-size:0.78rem; ${metaStyle} font-weight:bold; margin-bottom:8px;">${metaStatus}</div>
                    <div style="font-size:0.72rem; color:var(--text-dim);">包含 Title, Description 与 Tags</div>
                </div>
            </div>

            <style>
                @keyframes reviewPulse { 0% { opacity:0.6; } 50% { opacity:1; } 100% { opacity:0.6; } }
            </style>
            <div id="review-step-list-container">${stepList}</div>
        </div>`;
    } else if (isMissing) {
        const cleanLc = lc.toLowerCase();
        const langObj = (window.availableLangs || []).find(l => l.code === cleanLc) || (window.availableLangs || []).find(l => l.code === cleanLc.split('-')[0]);
        const curLangName = langObj ? langObj.name : lc.toUpperCase();
        const otherRunningLangs = state.wantedLangMap ? Object.keys(state.wantedLangMap).filter(l => state.wantedLangMap[l].status === 'running' && l !== lc) : [];
        const activeOtherTrans = (otherRunningLangs.length > 0)
            ? `<div style="margin-top:12px; padding:8px 12px; background:rgba(255, 171, 0, 0.1); border:1px solid rgba(255, 171, 0, 0.3); border-radius:6px; font-size:0.8rem; color:var(--accent-primary, #ffab00); display:inline-block;">⚡ 提示：后台当前正在单独处理 [${otherRunningLangs.join(', ').toUpperCase()}] 语种的 AI 翻译...</div>`
            : '';

        targetHtml = `<div style="padding:20px;">
            <div class="review-status-bar"><span class="review-badge ai">ℹ️ 无可用译文快照</span></div>
            <div class="review-error" style="color:var(--text-dim); text-align:center; padding: 30px 0;">
                当前【${curLangName}】文档可能尚未完成 AI 译文的物理写入，或物理缓存已被清理。
                ${activeOtherTrans}
                <br><br>
                <button onclick="window.triggerSingleTranslation('current')" style="margin-top:16px; margin-right:12px; padding:10px 20px; background:var(--accent-primary); color:#000; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:0.9rem; box-shadow:0 4px 15px rgba(255, 171, 0, 0.3); transition:transform 0.2s;">🚀 仅生成【${curLangName}】译文</button>
                <button onclick="window.triggerSingleTranslation('all')" style="margin-top:16px; padding:10px 20px; background:var(--bg-glass-heavy, rgba(255,255,255,0.05)); color:var(--text-bright, #fff); border:1px solid var(--glass-border, rgba(255,255,255,0.1)); border-radius:6px; font-weight:bold; cursor:pointer; font-size:0.9rem; transition:transform 0.2s;">🌍 生成所有目标语种译文 (${Object.keys(state.data.langs || {}).length}个语种)</button>
            </div>
        </div>`;
    } else {
        let statusHtml = ld.human_approved
            ? (ld.review_is_stale ? `<span class="review-badge stale" data-tooltip="中文原稿发生变更，建议复核校对内容">⚠️ 原稿已更新 · 建议复核 (${_formatReviewDate(ld.reviewed_at)})</span>` : `<span class="review-badge locked" data-tooltip="已开启精校保护：全站发布时将跳过 AI 重新翻译，直接保留并发布您人工校对的译文">🛡️ 已人工精校 (保留校对，跳过 AI 重译) · ${_formatReviewDate(ld.reviewed_at)}</span>`)
            : `<span class="review-badge ai" data-tooltip="当前语种为 AI 初代翻译，尚未保存人工校对保护">🤖 AI 初始翻译 (未保护)</span>`;

        const isDirty = window._isReviewDirty && window._isReviewDirty(lc);
        const saveStyle = isDirty ? 'box-shadow: 0 0 14px rgba(255, 179, 0, 0.5); border: 1.5px solid var(--accent-primary, #ffab00);' : '';
        const saveBtnLabel = _getSaveBtnText(ld, isDirty);

        const actionBtns = ld.human_approved
            ? `<button class="review-btn unlock" onclick="window.unlockTranslationReview()" data-tooltip="解除保护后，下次发布时 AI 将重新翻译此语种；当前校对内容将被覆盖">🔓 解除保护</button><button class="review-btn save active" style="${saveStyle}" onclick="window.saveTranslationReview()">${saveBtnLabel}</button>`
            : `<button class="review-btn unlock" style="margin-right: auto;" onclick="window.triggerSingleTranslation('current')" data-tooltip="重新请求 AI 翻译当前语种">🔄 重新生成当前语种译文</button><button class="review-btn save" style="${saveStyle}" onclick="window.saveTranslationReview()">${saveBtnLabel}</button>`;

        const validSourceCount = sourceParas.filter(p => p.index >= 0).length;
        const validTargetCount = targetParas.filter(p => p.index >= 0).length;
        const countMismatchBanner = (ld.paragraph_count_mismatch || (validSourceCount > 0 && validTargetCount > 0 && validSourceCount !== validTargetCount))
            ? `<div style="padding:8px 12px; background:rgba(255, 171, 0, 0.1); border:1px solid rgba(255, 171, 0, 0.3); border-radius:6px; font-size:0.78rem; color:var(--accent-primary, #ffab00); margin-bottom:8px;">⚠️ 提示：此语种切片段落数 (${validTargetCount} 段) 与原文 (${validSourceCount} 段) 存在不一致，建议人工复核段落结构。</div>`
            : '';

        targetHtml = `<div style="padding:20px 20px 20px 30px; display:flex; flex-direction:column; gap:16px;">
            <div class="review-status-bar">${statusHtml}</div>
            <div class="review-field">
                <div class="review-field-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <label style="margin:0;">📌 译文标题 (Title)</label>
                    <div style="display:flex; gap:6px;">
                        <button onclick="window.polishFieldWithAI('title', this)" class="mini-field-btn" data-tooltip="AI 重新润色标题">🪄</button>
                        <button onclick="window.resetFieldToDefault('title', this)" class="mini-field-btn" data-tooltip="恢复为初始标题">🔄</button>
                    </div>
                </div>
                <input type="text" id="review-title-input" value="${_escapeHtml(edit.title || '')}" oninput="window._reviewState.edits['${lc}'].title = this.value; window.updateReviewDirtyUI(); window.saveReviewDraft?.('${lc}');" class="review-input" placeholder="输入校对后的标题...">
            </div>
            <div class="review-field">
                <div class="review-field-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <label style="margin:0;">🏷️ 译文描述 (Description)</label>
                    <div style="display:flex; gap:6px;">
                        <button onclick="window.polishFieldWithAI('desc', this)" class="mini-field-btn" data-tooltip="AI 重新润色描述">🪄</button>
                        <button onclick="window.resetFieldToDefault('desc', this)" class="mini-field-btn" data-tooltip="恢复为初始描述">🔄</button>
                    </div>
                </div>
                <textarea id="review-desc-input" rows="3" class="review-input" oninput="window._reviewState.edits['${lc}'].desc = this.value; window.updateReviewDirtyUI(); window.saveReviewDraft?.('${lc}');" placeholder="输入校对后的 SEO 描述...">${_escapeHtml(edit.desc || '')}</textarea>
            </div>
            <div class="review-field">
                <label style="margin-bottom:6px; display:block;">📄 正文段落 <small style="color:var(--text-dim)">(点击段落编辑，代码块只读)</small></label>
                ${countMismatchBanner}
                <div class="review-paras-container" id="target-paras-container">${targetParas.map(p => (p.type === 'spacer' || p.index < 0) ? `<div class="review-para-block spacer" style="background:transparent; border:none; margin:4px 0;">${_renderParaBlock(p)}</div>` : `<div id="review-para-${p.index}" data-editing="0" class="review-para-block ${p.type === 'code' ? 'code-block' : ''} ${p._edited ? 'edited' : ''}" onclick="window.reviewEditParagraph(${p.index})">${_renderParaBlock(p)}</div>`).join('')}</div>
            </div>
            <div class="review-actions">${actionBtns}</div>
        </div>`;
    }

    // 2. 构建预览分栏 (Preview Column)
    let previewHtml = '';
    if (!isMissing) {
        const renderPreviewTitle = edit.title ? markdownParser(`# ${edit.title}`) : '';
        // 构建 index → source段落 映射，用于图片路径降级回退
        const sourceParaByIndex = {};
        (sourceParas || []).forEach(sp => { if (sp.index >= 0) sourceParaByIndex[sp.index] = sp.text || ''; });
        previewHtml = `<div style="padding:20px; display:flex; flex-direction:column; gap:16px;"><div class="review-field" style="margin:0;"><label>👁️ 译文预览 (Preview)</label></div><div class="preview-markdown-content" style="color:var(--text-bright);"><div class="preview-title" style="margin-bottom:20px;">${renderPreviewTitle}</div><div id="preview-paras-container">${targetParas.map((p, idx) => `<div id="preview-para-${p.index >= 0 ? p.index : 'spacer-' + idx}" class="preview-para-item">${markdownParser(_reviewRewriteMarkdown(p.text || '', state.docId, p.index >= 0 ? (sourceParaByIndex[p.index] || '') : ''))}</div>`).join('')}</div></div></div>`;
    }

    // 3. 构建原文参考分栏 (Source Column)
    const sourceHtml = `<div style="padding:20px 20px 20px 30px; display:flex; flex-direction:column; gap:16px;"><div class="review-field" style="margin:0;"><label>📜 原文参考 (Source)</label></div><div class="review-field"><label>📌 原文标题 (Source Title)</label><div style="background:rgba(255,255,255,0.02); opacity:0.8; padding:10px 14px; border-radius:6px; font-size:0.84rem; color:var(--text-dim); border:1px solid var(--glass-border); line-height:1.5;">${_escapeHtml(state.data.source_title || '无标题')}</div></div><div class="review-field"><label>🏷️ 原文描述 (Source Description)</label><div style="background:rgba(255,255,255,0.02); opacity:0.8; padding:10px 14px; border-radius:6px; font-size:0.84rem; color:var(--text-dim); border:1px solid var(--glass-border); line-height:1.5; white-space:pre-wrap;">${_escapeHtml(state.data.source_desc || '无描述')}</div></div><div class="review-field"><label>📄 原文正文段落 (Source Paragraphs)</label><div class="review-paras-container" id="source-paras-container">${sourceParas.map(sp => (sp.type === 'spacer' || sp.index < 0) ? `<div class="review-para-block spacer-only" style="background:transparent; border:none; margin:4px 0; opacity:0.5;"><div class="review-para-text" style="color:var(--text-dim); font-size:0.8rem; font-family:monospace; margin:0;">${_escapeHtml(sp.text)}</div></div>` : `<div id="source-para-${sp.index}" class="review-para-block source-only" style="background:rgba(255,255,255,0.02); opacity:0.8; margin-bottom:6px; padding:6px 12px; border-radius:6px;"><div class="review-para-top-bar" style="border:none; margin-bottom:2px;"><span class="review-para-num">#${sp.index + 1}</span></div><div class="review-para-text" style="color:var(--text-dim); font-size:0.85rem; line-height:1.6; font-family:inherit; white-space:pre-wrap; margin:0;">${_escapeHtml(sp.text)}</div></div>`).join('')}</div></div></div>`;

    const displayPreview = state.showPreview ? 'block' : 'none';
    const displaySource = state.showSource ? 'block' : 'none';
    const borderTarget = (state.showPreview || state.showSource) ? '1px solid var(--glass-border)' : 'none';
    const borderPreview = (state.showPreview && state.showSource) ? '1px solid var(--glass-border)' : 'none';

    document.getElementById('review-body').innerHTML = `
        <div style="display:flex; height:100%; width:100%; overflow:hidden;">
            <div style="flex:1; min-width:0; border-right:${borderTarget}; overflow-y:auto;" id="col-target"></div>
            <div style="flex:1; min-width:0; border-right:${borderPreview}; overflow-y:auto; display:${displayPreview};" id="col-preview"></div>
            <div style="flex:1; min-width:0; overflow-y:auto; display:${displaySource};" id="col-source"></div>
        </div>
    `;

    // 🛡️ [DOM Isolation Gate] 分栏独立注入，防止段落中未平衡的 HTML 标签逃逸并破坏外部三栏 Flex 容器
    const elTarget = document.getElementById('col-target');
    const elPreview = document.getElementById('col-preview');
    const elSource = document.getElementById('col-source');
    if (elTarget) elTarget.innerHTML = targetHtml;
    if (elPreview) elPreview.innerHTML = previewHtml;
    if (elSource) elSource.innerHTML = sourceHtml;

    if (!isMissing) {
        window._bindReviewInteractions?.();
    }
}
function _renderParaBlock(p) {
    if (p.type === 'spacer' || p.index < 0) {
        return `<div class="review-para-spacer" style="padding:4px 8px; color:var(--text-dim); opacity:0.5; font-size:0.8rem; font-family:monospace; border-top:1px dashed var(--glass-border); margin:4px 0;">${_escapeHtml(p.text)}</div>`;
    }
    const isCode = p.type === 'code';
    const editedBadge = p._edited ? '<span class="edited-icon-badge" data-tooltip="已人工校对修改">✏️</span>' : '';
    const retransBtn = !isCode ? `<button class="para-retrans-btn mini-field-btn" onclick="event.stopPropagation(); window.retranslateSingleParagraph(${p.index});" data-tooltip="仅重译此段">🪄</button>` : '';
    return `<span class="review-para-num">#${p.index + 1}</span><div class="review-para-actions">${editedBadge}${retransBtn}</div><div class="review-para-text">${_escapeHtml(p.text)}</div>`;
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
function _getSaveBtnText(ld, isDirty) {
    return (ld && ld.human_approved)
        ? (isDirty ? '🛡️ 更新精校 (⚠️ 未保存)' : '🛡️ 更新精校内容')
        : (isDirty ? '🛡️ 保存精校 (⚠️ 未保存)' : '🛡️ 保存精校 (跳过 AI 重译)');
}

/* ─── 脏态交互的增量 DOM 更新 ─────────────────────────── */
window.updateReviewDirtyUI = function () {
    const state = window._reviewState;
    if (!state.data || !state.activeLang) return;
    const lc = state.activeLang, isDirty = window._isReviewDirty && window._isReviewDirty(lc);
    const ld = state.data.langs ? state.data.langs[lc] : {};
    const tabBtn = document.getElementById(`review-tab-${lc}`), saveBtn = document.querySelector('.review-actions .review-btn.save');
    if (tabBtn) {
        const dot = tabBtn.querySelector('.review-dirty-dot');
        if (isDirty && !dot) tabBtn.insertAdjacentHTML('beforeend', '<span class="review-dirty-dot" style="color:#ffb300; margin-left:4px; font-size:0.9rem;">●</span>');
        else if (!isDirty && dot) dot.remove();
    }
    if (saveBtn) {
        saveBtn.innerHTML = _getSaveBtnText(ld, isDirty);
        saveBtn.style.boxShadow = isDirty ? '0 0 14px rgba(255, 179, 0, 0.5)' : '';
        saveBtn.style.border = isDirty ? '1.5px solid var(--accent-primary, #ffab00)' : '';
    }
};

window.openReviewForDoc = async function (targetDocId) {
    if (document.activeElement && typeof document.activeElement.blur === 'function') document.activeElement.blur();
    if (typeof window.openTranslationReview === 'function') window.openTranslationReview(targetDocId);
};

/* ─── 预览分栏单段落增量渲染（供 reviewSaveParagraph 调用） ─ */
function _reviewRenderPreviewPara(idx, state) {
    const previewBlock = document.getElementById(`preview-para-${idx}`);
    if (!previewBlock || !state) return;
    const lc = state.activeLang, paras = state.edits[lc]?.paragraphs || [];
    if (!paras[idx]) return;
    const sourceParas = state.data?.source_paragraphs || [], sourcePara = sourceParas.find(sp => sp.index === idx), sourceText = sourcePara?.text || '';
    const _breaks = window.settingsData?.ingress_settings?.hard_line_break ?? false;
    const rewritten = _reviewRewriteMarkdown(paras[idx].text || '', state.docId, sourceText);
    previewBlock.innerHTML = window.marked.parse(rewritten, { breaks: _breaks });
}

/* 🚀 [V114.4] 静默无痕进度更新函数：在轮询翻译进度时仅对进度条 ID 节点与 6 大步骤卡片进行物理修改，绝不清空/销毁正文与原文 DOM，兼顾 100% 流畅滚动与 100% 动态推流图示 */
window.updateReviewProgressOnly = function() {
    const state = window._reviewState;
    if (!state || !state.wantedLangMap) return;
    const data = state.data;
    if (!data) return;

    // 1. 更新顶部语种 Tab 的进度后缀数字
    Object.keys(state.wantedLangMap).forEach(lc => {
        const tabBtn = document.getElementById(`review-tab-${lc}`);
        if (!tabBtn) return;
        const langState = state.wantedLangMap[lc];
        if (!langState) return;
        const span = tabBtn.querySelector('span');
        if (span) {
            const pVal = langState.progress || 5;
            span.innerHTML = langState.status === 'running' ? `⏳${pVal}%` : `✅就绪`;
            span.style.color = langState.status === 'running' ? '#ffb300' : '#4caf50';
        }
    });

    // 2. 精准修改可视区域的进度卡片 DOM
    const activeLc = state.activeLang;
    if (activeLc && state.wantedLangMap[activeLc] && state.wantedLangMap[activeLc].status === 'running') {
        const langTask = state.wantedLangMap[activeLc];
        const progress = langTask.progress || 5;
        const pInfo = data?.langs?.[activeLc]?.progress;
        const useLive = pInfo && pInfo.running;
        const tParas = useLive ? (pInfo.translated_paras || 0) : (langTask.translated_paras || 0);
        const validSourceCount = (data?.source_paragraphs || []).filter(p => p.index >= 0).length || 1;
        const totalParas = useLive ? (pInfo.total_paras || validSourceCount) : (langTask.total_paras || validSourceCount);

        const mainBar = document.getElementById('review-main-progress-bar');
        const mainPercent = document.getElementById('review-main-progress-percent');
        const paraBar = document.getElementById('review-para-progress-bar');
        const paraText = document.getElementById('review-para-progress-text');
        const metaText = document.getElementById('review-meta-progress-text');
        const stepContainer = document.getElementById('review-step-list-container');

        const paraPercent = Math.min(100, Math.round((tParas / Math.max(1, totalParas)) * 100));

        if (mainBar) mainBar.style.width = `${progress}%`;
        if (mainPercent) mainPercent.textContent = `${progress}%`;
        if (paraBar) paraBar.style.width = `${paraPercent}%`;
        if (paraText) paraText.textContent = `${tParas} / ${totalParas} 段已就绪 (${paraPercent}%)`;

        const isBodyDone = tParas >= totalParas && totalParas > 0;

        if (metaText) {
            const metaStatus = isBodyDone ? (progress >= 85 ? '✅ 已完成润色' : '⏳ 正在润色') : '💤 等待正文后执行';
            const metaColor = isBodyDone ? (progress >= 85 ? '#4caf50' : 'var(--accent-primary)') : 'var(--text-dim)';
            metaText.textContent = metaStatus;
            metaText.style.color = metaColor;
        }

        // 3. 重新推算 6 大步骤的高亮显示状态并物理替换 stepContainer 内容
        if (stepContainer) {
            const steps = [
                { p: 10, name: '任务调度', desc: '初始化翻译管线引擎', check: progress >= 10 },
                { p: 25, name: '文本切片', desc: '解析段落与元数据结构', check: progress >= 25 },
                { p: 65, name: '正文段落翻译', desc: '大模型分段算力收割', check: isBodyDone },
                { p: 85, name: '元数据生成润色', desc: 'SEO 标题、描述与标签优化', check: isBodyDone && progress >= 85 },
                { p: 95, name: '合规自愈比对', desc: '校验图片与双链媒体路径', check: isBodyDone && progress >= 95 },
                { p: 100, name: '装配落盘', desc: '写入物理缓存与账本', check: progress >= 100 }
            ];
            let activeFound = false;
            const newStepsHtml = steps.map(s => {
                let icon = '💤 排队中', style = 'color:var(--text-dim); opacity:0.5;';
                if (s.check) {
                    icon = '✅ 已完成';
                    style = 'color:#4caf50; font-weight:bold;';
                } else if (!activeFound) {
                    activeFound = true;
                    icon = '⏳ 进行中';
                    style = 'color:var(--accent-primary); font-weight:bold; animation: reviewPulse 1.5s infinite;';
                }
                return `<div style="display:flex; justify-content:space-between; padding:8px 12px; margin-bottom:8px; border-radius:6px; background:rgba(255,255,255,0.02); font-size:0.85rem; ${style}"><span>${s.name} <small style="opacity:0.8;font-size:0.75rem;">(${s.desc})</small></span><span>${icon}</span></div>`;
            }).join('');
            stepContainer.innerHTML = newStepsHtml;
        }
    }
};
