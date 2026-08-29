/**
 * 🔒 [I5] Illacme Plenipes Translation Review Progress & Helpers Module
 * 职责：翻译校对工作台的进度无痕推流、辅助工具函数与状态交互增量 DOM 更新。
 * 架构：由 localization.review.render.js 拆分而来 (SOP-02 标准)。
 */

/* ─── 日期与字符串转义工具 ────────────────────────────────── */
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

function _escapeHtml(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function _getSaveBtnText(ld, isDirty) {
    return (ld && ld.human_approved)
        ? (isDirty ? '🛡️ 更新精校 (⚠️ 未保存)' : '🛡️ 更新精校内容')
        : (isDirty ? '🛡️ 保存精校 (⚠️ 未保存)' : '🛡️ 保存精校 (跳过 AI 重译)');
}

/* ─── 抽屉基础控制与错误态 ────────────────────────────────── */
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

/* ─── 预览分栏单段落增量渲染（供 reviewSaveParagraph 调用） ─ */
function _reviewRenderPreviewPara(idx, state) {
    const previewBlock = document.getElementById(`preview-para-${idx}`);
    if (!previewBlock || !state) return;
    const lc = state.activeLang, paras = state.edits[lc]?.paragraphs || [];
    if (!paras[idx]) return;
    const sourceParas = state.data?.source_paragraphs || [], sourcePara = sourceParas.find(sp => sp.index === idx), sourceText = sourcePara?.text || '';
    const _breaks = window.settingsData?.ingress_settings?.hard_line_break ?? false;
    const rewritten = (typeof _reviewRewriteMarkdown === 'function')
        ? _reviewRewriteMarkdown(paras[idx].text || '', state.docId, sourceText)
        : (paras[idx].text || '');
    if (window.marked && window.marked.parse) {
        previewBlock.innerHTML = window.marked.parse(rewritten, { breaks: _breaks });
    } else {
        previewBlock.innerHTML = rewritten;
    }
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
