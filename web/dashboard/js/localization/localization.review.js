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
window.saveReviewDraft = function (lc) {
    const state = window._reviewState;
    if (!state.docId || !lc) return;
    const edit = state.edits[lc];
    if (edit) {
        localStorage.setItem(`plenipes_review_draft_${state.docId}_${lc}`, JSON.stringify({
            title: edit.title,
            desc: edit.desc,
            paragraphs: edit.paragraphs
        }));
    }
};
window.clearReviewDraft = function (lc) {
    const state = window._reviewState;
    if (!state.docId || !lc) return;
    localStorage.removeItem(`plenipes_review_draft_${state.docId}_${lc}`);
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

    // Ensure settingsData is loaded
    if (!window.settingsData || !window.settingsData.ingress_settings) {
        try {
            const configRes = await fetch('/api/system/config');
            if (configRes.ok) {
                const configData = await configRes.json();
                window.settingsData = { ...window.settingsData, ...(configData.config || configData) };
            }
        } catch (err) {
            console.error("Failed to load settingsData:", err);
        }
    }

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
            try {
                const draftStr = localStorage.getItem(`plenipes_review_draft_${docId}_${lc}`);
                if (draftStr) {
                    const draft = JSON.parse(draftStr);
                    if (draft) {
                        state.edits[lc].title = draft.title ?? state.edits[lc].title;
                        state.edits[lc].desc = draft.desc ?? state.edits[lc].desc;
                        if (draft.paragraphs) {
                            state.edits[lc].paragraphs = draft.paragraphs.map(p => ({ ...p }));
                        }
                    }
                }
            } catch (err) {
                console.error("Failed to restore draft:", err);
            }
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
        window.clearReviewDraft(lc);
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
        window.clearReviewDraft(lc);
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
    
    // 确定本次操作我们关心的目标语种列表，如果是生成所有则需要等待全部激活的目标语种
    let wantedLangs = [];
    if (targetMode === 'current') {
        wantedLangs = [lc];
    } else {
        wantedLangs = (window.settingsData?.i18n_settings?.targets || []).map(t => t.lang_code);
        if (!wantedLangs || wantedLangs.length === 0) {
            // 🚀 [双重兜底] 如果 settingsData 里未能读取到 targets，从当前工作台已加载的语种中自动补齐，防止 wantedLangs 为空导致轮询秒退
            wantedLangs = Object.keys(window._reviewState.data?.langs || {});
        }
    }

    // 🚀 记录正在翻译的目标语种队列，驱动声明式进度呈现
    window._reviewState.wantedLangs = wantedLangs;
    window._reviewState.langProgress = {};
    wantedLangs.forEach(lang => {
        window._reviewState.langProgress[lang] = 5;
    });

    // 🚀 [UI 自愈与状态清理]
    // 在重新生成之前，预先将关注的目标语种在前端置为 is_missing = true 并清空 edits 缓存。
    // 这能够物理级避免：在已就绪的语种下点击生成全部时，因旧快照存在导致轮询在第一轮就误判为就绪并立刻退出的致命 Bug。
    wantedLangs.forEach(lang => {
        if (window._reviewState.data && window._reviewState.data.langs && window._reviewState.data.langs[lang]) {
            window._reviewState.data.langs[lang].is_missing = true;
        }
        if (window._reviewState.edits && window._reviewState.edits[lang]) {
            delete window._reviewState.edits[lang];
        }
    });

    _reviewRender();
    window._showToast?.('🚀 已推送后台翻译管线，正在处理中...', 'info');

    try {
        const res = await fetch('/api/publish/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: 'static', paths: [docId], force: true, target_langs: targetLangs })
        });
        const d = await res.json();
        if (d.status === 'error') throw new Error(d.message);

        // 轮询快照直到所有请求的语种都完成翻译
        let attempts = 0;
        const poll = async () => {
            if (attempts > 300) {
                window._reviewState.wantedLangs = null;
                window._reviewState.langProgress = null;
                window._showToast?.('翻译耗时超出预期，请稍后重新打开抽屉查看', 'warning');
                _reviewRender();
                return;
            }
            try {
                const checkRes = await fetch(`/api/translation/review/${encodeURIComponent(docId)}`);
                const checkData = await checkRes.json();
                
                if (checkData && checkData.langs) {
                    window._reviewState.data = checkData;
                    
                    // 推进并更新各语种的真实物理进度
                    wantedLangs.forEach(lang => {
                        const ld = checkData.langs[lang];
                        if (ld) {
                            if (!ld.is_missing) {
                                window._reviewState.langProgress[lang] = 100;
                            } else if (ld.progress) {
                                const tParas = ld.progress.translated_paras || 0;
                                const totalParas = ld.progress.total_paras || 1;
                                window._reviewState.langProgress[lang] = Math.min(99, Math.floor((tParas / totalParas) * 100));
                            } else {
                                window._reviewState.langProgress[lang] = Math.min(99, window._reviewState.langProgress[lang] || 5);
                            }
                        }
                    });

                    // 同步更新所有已就绪目标语种 of edits 缓存，防止切换标签时出现空译文状态
                    Object.keys(checkData.langs).forEach(lc_key => {
                        const ld = checkData.langs[lc_key];
                        if (ld && !ld.is_missing) {
                            window._reviewState.edits[lc_key] = {
                                title: ld.title || '',
                                desc: ld.desc || '',
                                paragraphs: (ld.paragraphs || []).map(p => ({ ...p }))
                            };
                        }
                    });
                    
                    // 检查 wantedLangs 里的所有语种是否全部就绪（非 missing）
                    const allDone = wantedLangs.every(lang => checkData.langs[lang] && !checkData.langs[lang].is_missing);
                    
                    if (allDone) {
                        window._reviewState.wantedLangs = null;
                        window._reviewState.langProgress = null;
                        _reviewRender();
                        window._showToast?.(`✅ 所选翻译已全部就绪！`, 'success');
                        return;
                    } else {
                        // 每次轮询有新状态都执行 _reviewRender()，保持全 Tab 进度与百分比实时刷新
                        _reviewRender();
                    }
                }
            } catch (err) {
                console.error("Polling error", err);
            }
            attempts++;
            setTimeout(poll, 2000);
        };
        setTimeout(poll, 2000);

    } catch (e) {
        window._reviewState.wantedLangs = null;
        window._reviewState.langProgress = null;
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
        const originalText = state.data?.langs?.[lc]?.paragraphs?.[idx]?.text ?? '';
        paras[idx].text = newText;
        paras[idx]._edited = (newText !== originalText);
    }
    // 重新渲染该段落块（退出编辑模式）
    const block = document.getElementById(`review-para-${idx}`);
    if (block) {
        block.dataset.editing = '0';
        block.innerHTML = _renderParaBlock(paras[idx]);
    }
    // 🚀 实时同步渲染预览分栏中的对应段落（渲染逻辑委托给 review.render.js）
    _reviewRenderPreviewPara(idx, state);
    window.saveReviewDraft?.(lc);
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
        if (state.data && state.data.langs) {
            Object.keys(state.data.langs).forEach(lc => {
                window.clearReviewDraft?.(lc);
            });
        }
    }

    const overlay = document.getElementById('review-drawer-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => { overlay.style.display = 'none'; }, 250);
    }
};

/* ─── 集中绑定三栏交互：三向联动高亮与锚定滚动同步 ───────────────── */
window._bindReviewInteractions = function () {
    const colTarget = document.getElementById('col-target');
    const colPreview = document.getElementById('col-preview');
    const colSource = document.getElementById('col-source');
    if (!colTarget || !colPreview || !colSource) return;

    // 1. 三向段落高亮联动
    const highlightPara = (idx, add) => {
        ['review-para', 'source-para', 'preview-para'].forEach(prefix => {
            const el = document.getElementById(`${prefix}-${idx}`);
            if (el) {
                if (add) el.classList.add('linked-hover');
                else el.classList.remove('linked-hover');
            }
        });
    };

    [colTarget, colPreview, colSource].forEach(col => {
        col.addEventListener('mouseover', (e) => {
            const block = e.target.closest('[id^="review-para-"], [id^="source-para-"], [id^="preview-para-"]');
            if (block) highlightPara(block.id.split('-').pop(), true);
        });
        col.addEventListener('mouseout', (e) => {
            const block = e.target.closest('[id^="review-para-"], [id^="source-para-"], [id^="preview-para-"]');
            if (block) highlightPara(block.id.split('-').pop(), false);
        });
    });

    // 2. 基于可视段落锚定的滚动同步
    let activeScrollSource = null;
    let scrollTimeout = null;

    const onScrollHandler = (e) => {
        const target = e.currentTarget;
        if (activeScrollSource && activeScrollSource !== target) return;
        activeScrollSource = target;

        const targetRect = target.getBoundingClientRect();
        const blocks = Array.from(target.querySelectorAll('[id^="review-para-"], [id^="source-para-"], [id^="preview-para-"]'));
        let activeIdx = null, diff = 0;

        for (const b of blocks) {
            const rect = b.getBoundingClientRect();
            if (rect.bottom - targetRect.top > 10) {
                activeIdx = b.id.split('-').pop();
                diff = rect.top - targetRect.top;
                break;
            }
        }

        if (activeIdx !== null) {
            const prefixes = { 'col-target': 'review-para', 'col-preview': 'preview-para', 'col-source': 'source-para' };
            const visibleCols = [colTarget, colPreview, colSource].filter(c => c && c.style.display !== 'none');
            visibleCols.forEach(c => {
                if (c !== target) {
                    const targetEl = c.querySelector(`#${prefixes[c.id]}-${activeIdx}`);
                    if (targetEl) {
                        const colRect = c.getBoundingClientRect();
                        const elRect = targetEl.getBoundingClientRect();
                        c.scrollTop += (elRect.top - colRect.top) - diff;
                    }
                }
            });
        }

        if (scrollTimeout) clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => { activeScrollSource = null; }, 80);
    };

    colTarget.addEventListener('scroll', onScrollHandler);
    colPreview.addEventListener('scroll', onScrollHandler);
    colSource.addEventListener('scroll', onScrollHandler);
};
