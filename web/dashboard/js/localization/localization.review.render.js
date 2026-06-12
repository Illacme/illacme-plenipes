/**
 * 🔒 [I5] Illacme Plenipes Translation Review Rendering Module
 * 职责：翻译人工校对回流工作台的 HTML 结构组装与渲染。
 *        本文件由 localization.review.js 拆分而来，符合 SOP-02 降解要求，小于 300 行。
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
        const badge = ld.human_approved
            ? (ld.review_is_stale ? '⚠️' : '🔒')
            : '🤖';
        const dirtyMark = isDirty ? '<span class="review-dirty-dot" style="color:#ffb300; margin-left:4px; font-size:0.9rem;">●</span>' : '';
        const isActive = lc === state.activeLang;
        return `<button class="review-lang-tab ${isActive ? 'active' : ''}"
            id="review-tab-${lc}"
            onclick="window.switchReviewLang('${lc}')"
            style="padding:6px 14px;border-radius:20px;border:1px solid var(--glass-border);
                   background:${isActive ? 'var(--accent-primary)' : 'transparent'};
                   color:${isActive ? '#000' : 'var(--text-dim)'};cursor:pointer;font-size:0.8rem;
                   font-weight:600;transition:all 0.2s;">
            ${badge} ${lc.toUpperCase()}${dirtyMark}
        </button>`;
    }).join('');

    document.getElementById('review-drawer-title').textContent =
        `🔍 译文校对工作台 — ${data.doc_title || state.docId}`;
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

    // Synchronize toggle button style based on layout state
    const btnSplit = document.getElementById('btn-view-split');
    if (btnSplit) {
        btnSplit.style.background = state.layoutMode === 'split' ? 'rgba(255,255,255,0.1)' : 'transparent';
        btnSplit.style.color = state.layoutMode === 'split' ? 'var(--text-bright)' : 'var(--text-dim)';
    }

    const ld = state.data.langs[lc] || {};
    const edit = state.edits[lc] || {};
    const isMissing = ld.is_missing;
    const sourceParas = state.data.source_paragraphs || [];
    const targetParas = edit.paragraphs || [];

    let targetHtml = '';
    if (isMissing) {
        targetHtml = `
            <div style="padding:20px;">
                <div class="review-status-bar"><span class="review-badge ai">ℹ️ 无可用译文快照</span></div>
                <div class="review-error" style="color:var(--text-dim); text-align:center; padding: 40px 0;">
                    当前文档可能尚未完成 AI 译文的物理写入，或物理缓存已被清理。<br><br>
                    <button onclick="window.triggerSingleTranslation('current')" style="margin-top:20px; margin-right:12px; padding:10px 20px; background:var(--accent-primary); color:#000; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:0.9rem; box-shadow:0 4px 15px rgba(255, 171, 0, 0.3); transition:transform 0.2s;">
                        🚀 仅生成当前语种译文
                    </button>
                    <button onclick="window.triggerSingleTranslation('all')" style="margin-top:20px; padding:10px 20px; background:var(--bg-glass-heavy, rgba(255,255,255,0.05)); color:var(--text-bright, #fff); border:1px solid var(--glass-border, rgba(255,255,255,0.1)); border-radius:6px; font-weight:bold; cursor:pointer; font-size:0.9rem; transition:transform 0.2s;">
                        🌍 生成所有目标语种译文
                    </button>
                </div>
            </div>
        `;
    } else {
        let statusHtml = '';
        if (ld.human_approved) {
            const reviewedAt = ld.reviewed_at ? new Date(ld.reviewed_at).toLocaleDateString('zh-CN') : '';
            if (ld.review_is_stale) {
                statusHtml = `<span class="review-badge stale">⚠️ 原稿已变更，建议复核 · 锁定于 ${reviewedAt}</span>`;
            } else {
                statusHtml = `<span class="review-badge locked">🔒 人工锁定 · ${reviewedAt} · ${ld.reviewed_by || 'commander'}</span>`;
            }
        } else {
            statusHtml = `<span class="review-badge ai">🤖 AI 生成，未校对</span>`;
        }

        const isDirty = window._isReviewDirty && window._isReviewDirty(lc);
        if (isDirty) {
            statusHtml += `<span class="review-badge dirty" style="background:var(--accent-secondary, #ffb300); color:#000; font-weight:bold; margin-left:8px; padding:2px 8px; border-radius:4px; font-size:0.75rem; display:inline-block; box-shadow:0 0 8px rgba(255,179,0,0.2);">⚠️ 未保存修改</span>`;
        }

        const saveStyle = isDirty
            ? 'box-shadow: 0 0 12px rgba(255, 179, 0, 0.4); border: 1.5px solid var(--accent-primary, #ffab00);'
            : '';

        const actionBtns = ld.human_approved
            ? `<button class="review-btn unlock" onclick="window.unlockTranslationReview()">🗑️ 重置为 AI 重译</button>
               <button class="review-btn save active" style="${saveStyle}" onclick="window.saveTranslationReview()">🔒 更新锁定内容</button>`
            : `<button class="review-btn unlock" style="margin-right: auto;" onclick="window.triggerSingleTranslation('current')">🔄 重新生成当前语种译文</button>
               <button class="review-btn save" style="${saveStyle}" onclick="window.saveTranslationReview()">🔒 保存并锁定（语种级）</button>`;

        targetHtml = `
            <div style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div class="review-status-bar">${statusHtml}</div>

                <div class="review-field">
                    <label>📌 标题 (Title)</label>
                    <input type="text" id="review-title-input" value="${_escapeHtml(edit.title || '')}"
                        oninput="window._reviewState.edits['${lc}'].title = this.value; window.updateReviewDirtyUI();"
                        class="review-input" placeholder="输入校对后的标题...">
                </div>

                <div class="review-field">
                    <label>🏷️ SEO 描述 (Description)</label>
                    <textarea id="review-desc-input" rows="3" class="review-input"
                        oninput="window._reviewState.edits['${lc}'].desc = this.value; window.updateReviewDirtyUI();"
                        placeholder="输入校对后的 SEO 描述...">${_escapeHtml(edit.desc || '')}</textarea>
                </div>

                <div class="review-field">
                    <label>📄 正文段落 <small style="color:var(--text-dim)">(点击段落编辑，代码块只读)</small></label>
                    <div class="review-paras-container" id="target-paras-container">
                        ${targetParas.map(p => {
            return `
                                <div id="review-para-${p.index}" data-editing="0"
                                     class="review-para-block ${p.type === 'code' ? 'code-block' : ''} ${p._edited ? 'edited' : ''}"
                                     onclick="window.reviewEditParagraph(${p.index})"
                                     title="${p.type === 'code' ? '代码块（只读）' : '点击编辑此段落'}">${_renderParaBlock(p)}</div>
                            `;
        }).join('')}
                    </div>
                </div>

                <div class="review-actions">${actionBtns}</div>
            </div>
        `;
    }

    if (state.layoutMode === 'split') {
        const sourceHtml = `
            <div style="padding:20px; display:flex; flex-direction:column; gap:16px;">
                <div class="review-field" style="margin:0;">
                    <label>📜 原文参考 (Source)</label>
                </div>

                <div class="review-field">
                    <label>📌 原文标题 (Source Title)</label>
                    <div style="background:rgba(255,255,255,0.02); opacity:0.8; padding:10px 14px; border-radius:6px; font-size:0.84rem; color:var(--text-dim); border:1px solid var(--glass-border); line-height:1.5;">
                        ${_escapeHtml(state.data.source_title || '无标题')}
                    </div>
                </div>

                <div class="review-field">
                    <label>🏷️ 原文描述 (Source Description)</label>
                    <div style="background:rgba(255,255,255,0.02); opacity:0.8; padding:10px 14px; border-radius:6px; font-size:0.84rem; color:var(--text-dim); border:1px solid var(--glass-border); line-height:1.5; white-space:pre-wrap;">${_escapeHtml(state.data.source_desc || '无描述')}</div>
                </div>

                <div class="review-field">
                    <label>📄 原文正文段落 (Source Paragraphs)</label>
                    <div class="review-paras-container" id="source-paras-container">
                        ${sourceParas.map((sp, idx) => `
                            <div id="source-para-${idx}" class="review-para-block source-only" style="background:rgba(255,255,255,0.02); opacity:0.8; margin-bottom:6px; padding:6px 12px; border-radius:6px;"><div class="review-para-text" style="color:var(--text-dim); font-size:0.85rem; line-height:1.6; font-family:inherit; white-space:pre-wrap; margin:0;">${_escapeHtml(sp.text)}</div></div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('review-body').innerHTML = `
            <div style="display:flex; height:100%; overflow:hidden;">
                <div style="flex:1; border-right:1px solid var(--glass-border); overflow-y:auto;" id="col-target">
                    ${targetHtml}
                </div>
                <div style="flex:1; overflow-y:auto;" id="col-source">
                    ${sourceHtml}
                </div>
            </div>
        `;

        // Sync Scroll
        const colSource = document.getElementById('col-source');
        const colTarget = document.getElementById('col-target');
        if (colSource && colTarget && !isMissing) {
            let syncingSource = false;
            let syncingTarget = false;
            colSource.addEventListener('scroll', () => {
                if (!syncingSource) {
                    syncingTarget = true;
                    colTarget.scrollTop = colSource.scrollTop * (colTarget.scrollHeight - colTarget.clientHeight) / (colSource.scrollHeight - colSource.clientHeight || 1);
                    setTimeout(() => syncingTarget = false, 50);
                }
            });
            colTarget.addEventListener('scroll', () => {
                if (!syncingTarget) {
                    syncingSource = true;
                    colSource.scrollTop = colTarget.scrollTop * (colSource.scrollHeight - colSource.clientHeight) / (colTarget.scrollHeight - colTarget.clientHeight || 1);
                    setTimeout(() => syncingSource = false, 50);
                }
            });
        }
    } else {
        document.getElementById('review-body').innerHTML = `
            <div style="overflow-y:auto; height:100%;" id="col-target">
                ${targetHtml}
            </div>
        `;
    }
}

function _renderParaBlock(p) {
    const icon = p.type === 'code' ? '🟠' : (p.type === 'callout' ? '🔷' : '');
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

    // 1. Tab 圆点更新
    const tabBtn = document.getElementById(`review-tab-${lc}`);
    if (tabBtn) {
        const oldDot = tabBtn.querySelector('.review-dirty-dot');
        if (isDirty && !oldDot) {
            tabBtn.insertAdjacentHTML('beforeend', '<span class="review-dirty-dot" style="color:#ffb300; margin-left:4px; font-size:0.9rem;">●</span>');
        } else if (!isDirty && oldDot) {
            oldDot.remove();
        }
    }

    // 2. 状态栏更新
    const statusBar = document.querySelector('.review-status-bar');
    if (statusBar) {
        const oldBadge = statusBar.querySelector('.review-badge.dirty');
        if (isDirty && !oldBadge) {
            statusBar.insertAdjacentHTML('beforeend', '<span class="review-badge dirty" style="background:var(--accent-secondary, #ffb300); color:#000; font-weight:bold; margin-left:8px; padding:2px 8px; border-radius:4px; font-size:0.75rem; display:inline-block; box-shadow:0 0 8px rgba(255,179,0,0.2);">⚠️ 未保存修改</span>');
        } else if (!isDirty && oldBadge) {
            oldBadge.remove();
        }
    }

    // 3. 保存按钮高亮更新
    const saveBtn = document.querySelector('.review-actions .review-btn.save');
    if (saveBtn) {
        saveBtn.style.boxShadow = isDirty ? '0 0 12px rgba(255, 179, 0, 0.4)' : '';
        saveBtn.style.border = isDirty ? '1.5px solid var(--accent-primary, #ffab00)' : '';
    }
};

