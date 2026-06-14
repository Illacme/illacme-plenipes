/**
 * 🔒 [I5] Illacme Plenipes Translation Review Module
 * 职责：翻译人工校对回流工作台 — 段落级编辑（Q1=C）、语种级锁定（Q2=A）、
 *        原稿变更警告（Q3=B）、从 MetadataManager 账本读取数据（Q6=B）。
 */

/* ─── 状态 ─────────────────────────────────────────── */
window._reviewState = {
    docId: null,
    data: null,          // 服务端返回的快照
    activeLang: null,
    showSource: true,
    showPreview: true,
    edits: {}            // { lang: { title, desc, paragraphs: [{index, type, text}] } }
};

/* ─── 入口：从 Vault 文稿列表打开校对抽屉（Q5=B） ──── */
window.openTranslationReview = async function (docId) {
    const isAiEnabled = !window.governanceContext || 
                       (window.governanceContext.ai && window.governanceContext.ai.status !== 'disabled');
    if (!isAiEnabled) {
        Swal.fire({
            title: '🔒 协同服务已离线',
            text: '当前 AI 算力总控已关闭，译文校对工作台不可用。若要进行译文人工校对与锁定，请前往算力中心重新开启 AI 算力。',
            icon: 'warning',
            background: 'rgba(20, 20, 25, 0.95)',
            color: '#fff',
            confirmButtonText: '确定',
            confirmButtonColor: 'var(--accent-primary)'
        });
        return;
    }

    const state = window._reviewState;
    state.docId = docId;
    state.edits = {};

    _reviewShowDrawer();
    _reviewSetLoading(true);

    try {
        const res = await fetch(`/api/translation/review/${encodeURIComponent(docId)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        state.data = await res.json();

        const langs = Object.keys(state.data.langs || {});
        state.activeLang = langs[0] || null;
        langs.forEach(lc => {
            const ld = state.data.langs[lc];
            state.edits[lc] = {
                title: ld.title || '',
                desc: ld.desc || '',
                paragraphs: (ld.paragraphs || []).map(p => ({ ...p }))
            };
        });

        _reviewRender();
    } catch (e) {
        _reviewShowError('加载译文快照失败: ' + e.message);
    } finally {
        _reviewSetLoading(false);
    }
};

/* ─── 保存并锁定（Q2=A：语种级整体锁定） ────────────── */
window.saveTranslationReview = async function () {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc || !state.docId) return;

    const edit = state.edits[lc] || {};
    const payload = {
        doc_id: state.docId,
        lang_code: lc,
        paragraphs: edit.paragraphs || [],
        title: edit.title || null,
        desc: edit.desc || null
    };

    try {
        const res = await fetch('/api/translation/review/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        // 更新本地状态为已锁定，并同步原始快照以清除脏态
        if (state.data && state.data.langs[lc]) {
            const ld = state.data.langs[lc];
            ld.title = edit.title;
            ld.desc = edit.desc;
            ld.paragraphs = edit.paragraphs.map(p => ({ ...p, _edited: false }));
            ld.human_approved = true;
            ld.review_is_stale = false;
            ld.reviewed_at = new Date().toISOString();
        }
        _reviewRender();
        window._showToast?.('🔒 校对结果已保存并锁定', 'success');
    } catch (e) {
        window._showToast?.('保存失败: ' + e.message, 'error');
    }
};

/* ─── 解除锁定（Q3=B：用户主动操作） ────────────────── */
window.unlockTranslationReview = async function () {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc || !state.docId) return;
    if (!confirm(`确认解除「${lc.toUpperCase()}」的人工锁定？下次同步时 AI 将重新翻译此文档。`)) return;

    try {
        const res = await fetch('/api/translation/review/unlock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_id: state.docId, lang_code: lc })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        if (state.data && state.data.langs[lc]) {
            state.data.langs[lc].human_approved = false;
            state.data.langs[lc].review_is_stale = false;
        }
        _reviewRender();
        window._showToast?.('🗑️ 校对锁已解除，下次同步将重新 AI 翻译', 'info');
    } catch (e) {
        window._showToast?.('解锁失败: ' + e.message, 'error');
    }
};


window.toggleReviewSource = function () {
    window._reviewState.showSource = !window._reviewState.showSource;
    _reviewRenderBody();
};
window.toggleReviewPreview = function () {
    window._reviewState.showPreview = !window._reviewState.showPreview;
    _reviewRenderBody();
};

window.triggerSingleTranslation = async function (targetMode = 'current') {
    const docId = window._reviewState.docId;
    if (!docId) return;
    
    const lc = window._reviewState.activeLang;
    const targetLangs = targetMode === 'current' ? [lc] : null;
    
    window._showToast?.('🚀 已推送后台翻译管线，正在处理中...', 'info');
    
    // 显示加载状态
    const targetCol = document.getElementById('col-target');
    if (targetCol) {
        targetCol.innerHTML = '<div style="padding:40px; text-align:center; color:var(--text-dim);">⏳ 翻译引擎正在飞速生成中，请不要关闭抽屉，稍候片刻...</div>';
    }

    try {
        const res = await fetch('/api/publish/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: 'static', paths: [docId], force: true, target_langs: targetLangs })
        });
        const d = await res.json();
        if (d.status === 'error') throw new Error(d.message);

        // 轮询快照直到翻译完成
        let attempts = 0;
        const poll = async () => {
            if (attempts > 300) {
                window._showToast?.('翻译耗时超出预期，请稍后重新打开抽屉查看', 'warning');
                _reviewRender(); // 🚀 [V10.3] 恢复原状，避免一直转圈
                return;
            }
            try {
                const checkRes = await fetch(`/api/translation/review/${encodeURIComponent(docId)}`);
                const checkData = await checkRes.json();
                
                const lc = window._reviewState.activeLang;
                if (checkData && checkData.langs && checkData.langs[lc] && !checkData.langs[lc].is_missing) {
                    window._reviewState.data = checkData;
                    const ld = checkData.langs[lc];
                    window._reviewState.edits[lc] = {
                        title: ld.title || '',
                        desc: ld.desc || '',
                        paragraphs: (ld.paragraphs || []).map(p => ({ ...p }))
                    };
                    _reviewRender();
                    window._showToast?.(`✅ ${lc.toUpperCase()} 翻译已就绪！`, 'success');
                    return;
                }
            } catch (err) {
                console.error("Polling error", err);
            }
            attempts++;
            setTimeout(poll, 2000);
        };
        setTimeout(poll, 2000);

    } catch (e) {
        window._showToast?.('分发触发失败: ' + e.message, 'error');
        _reviewRender(); // 恢复原状
    }
};

/* ─── 切换语种标签 ───────────────────────────────────── */
window.switchReviewLang = function (lc) {
    window._reviewState.activeLang = lc;
    _reviewRender();
};

/* ─── 段落块点击编辑（Q1=C） ──────────────────────────── */
window.reviewEditParagraph = function (idx) {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc) return;
    const para = (state.edits[lc]?.paragraphs || [])[idx];
    if (!para || para.type === 'code') return; // 代码块只读

    const block = document.getElementById(`review-para-${idx}`);
    if (!block || block.dataset.editing === '1') return;
    block.dataset.editing = '1';

    const prev = block.innerHTML;
    block.innerHTML = `
        <textarea class="review-para-textarea" onblur="window.reviewSaveParagraph(${idx}, this.value)"
            style="width:100%;min-height:80px;background:var(--bg-agent-input);color:var(--text-bright);
                   border:1.5px solid var(--accent-primary);border-radius:6px;padding:10px;
                   font-size:0.82rem;line-height:1.6;resize:vertical;outline:none;box-sizing:border-box;
                   font-family:inherit;">${_escapeHtml(para.text)}</textarea>
    `;
    block.querySelector('textarea').focus();
};

window.reviewSaveParagraph = function (idx, newText) {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc) return;
    const paras = state.edits[lc]?.paragraphs || [];
    if (paras[idx]) {
        paras[idx].text = newText;
        paras[idx]._edited = true;
    }
    // 重新渲染该段落块（退出编辑模式）
    const block = document.getElementById(`review-para-${idx}`);
    if (block) {
        block.dataset.editing = '0';
        block.innerHTML = _renderParaBlock(paras[idx]);
    }
    // 🚀 实时同步渲染预览分栏中的对应段落（渲染逻辑委托给 review.render.js）
    _reviewRenderPreviewPara(idx, state);
    window.updateReviewDirtyUI();
};

/* ─── 脏态检测与增量 UI 交互 (I5) ────────────────────────── */
window._isReviewDirty = function (lc) {
    const state = window._reviewState;
    if (!state.data || !state.data.langs || !state.data.langs[lc]) return false;
    const original = state.data.langs[lc];
    const current = state.edits[lc];
    if (!current) return false;

    if ((current.title || '') !== (original.title || '')) return true;
    if ((current.desc || '') !== (original.desc || '')) return true;

    const origParas = original.paragraphs || [];
    const currParas = current.paragraphs || [];
    if (origParas.length !== currParas.length) return true;
    for (let i = 0; i < origParas.length; i++) {
        if (origParas[i].text !== currParas[i].text) return true;
    }
    return false;
};


window.closeTranslationReview = function () {
    const state = window._reviewState;
    let hasDirty = false;
    if (state.data && state.data.langs) {
        for (const lc of Object.keys(state.data.langs)) {
            if (window._isReviewDirty(lc)) {
                hasDirty = true;
                break;
            }
        }
    }
    
    if (hasDirty) {
        if (!confirm('⚠️ 当前有未保存的校对修改，确定要关闭并丢弃这些修改吗？')) {
            return;
        }
    }

    const overlay = document.getElementById('review-drawer-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => { overlay.style.display = 'none'; }, 250);
    }
};
