/**
 * 🔒 [I5] Illacme Plenipes Translation Review Module
 * 职责：翻译人工校对回流工作台 — 段落级编辑（Q1=C）、语种级锁定（Q2=A）、
 *        原稿变更警告（Q3=B）、从 MetadataManager 账本读取数据（Q6=B）。
 */

/* ─── 状态 ─────────────────────────────────────────── */
/* ─── 状态 ─────────────────────────────────────────── */
window._reviewState = {
    docId: null,
    data: null,          // 服务端返回的快照
    activeLang: null,
    showSource: true,
    showPreview: true,
    edits: {},           // { lang: { title, desc, paragraphs: [{index, type, text}] } }
    wantedLangMap: {},   // 🚀 [V81.0] 多语种独立并发状态字典 { [lang]: { status, progress } }
    wantedLangs: null
};
window.saveReviewDraft = function (lc) {
    const state = window._reviewState;
    if (!state.docId || !lc) return;
    const edit = state.edits[lc];
    if (edit) {
        localStorage.setItem(`plenipes_review_draft_${state.docId}_${lc}`, JSON.stringify({
            title: edit.title,
            desc: edit.desc,
            paragraphs: edit.paragraphs,
            source_hash: state.data?.source_hash || ''
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
    const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';
    if (pubMode === 'basic' || pubMode === 'enhanced') {
        const modeText = pubMode === 'basic' ? '基础物理出版模式' : '智能母语增强模式';
        Swal.fire({
            title: '🔒 译文校对不可用',
            text: `当前版图处于 ${modeText}，不进行正文 AI 翻译，因此译文校对工作台已挂起。若要使用多语言翻译与校对，请先将印记出版模式切换为“全球多语言分发模式”。`,
            icon: 'warning',
            background: 'rgba(20, 20, 25, 0.95)',
            color: '#fff',
            confirmButtonText: '确定',
            confirmButtonColor: 'var(--accent-primary)'
        });
        return;
    }

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
    state.wantedLangMap = {};
    state.wantedLangs = null;

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
        if (state.data && state.data.doc_id) {
            state.docId = state.data.doc_id;
        }

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
                    if (draft && draft.source_hash === state.data.source_hash) {
                        state.edits[lc].title = draft.title ?? state.edits[lc].title;
                        state.edits[lc].desc = draft.desc ?? state.edits[lc].desc;
                        if (draft.paragraphs) {
                            state.edits[lc].paragraphs = draft.paragraphs.map(p => ({ ...p }));
                        }
                    } else if (draft && draft.source_hash !== state.data.source_hash) {
                        // 🚀 原稿 Hash 已更新，清理已过期的旧草稿
                        localStorage.removeItem(`plenipes_review_draft_${docId}_${lc}`);
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
        window._showToast?.('🛡️ 校对结果已保存并锁定保护 (防 AI 覆盖)', 'success');
    } catch (e) {
        window._showToast?.('保存失败: ' + e.message, 'error');
    }
};

/* ─── 解除锁定（Q3=B：用户主动操作） ────────────────── */
window.unlockTranslationReview = async function () {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc || !state.docId) return;

    let confirmed = false;
    const titleMsg = `确认解除「${lc.toUpperCase()}」的精校保护？`;
    const textMsg = `解除保护后，下次全站同步或发布时 AI 将自动重新翻译此语种；您当前的人工校对内容将被覆盖。`;

    if (window.Swal) {
        const res = await window.Swal.fire({
            title: titleMsg,
            text: textMsg,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: '🔓 确认解除保护',
            cancelButtonText: '取消',
            confirmButtonColor: '#ff4d4f',
            cancelButtonColor: 'rgba(255, 255, 255, 0.15)',
            background: 'rgba(20, 20, 25, 0.95)',
            color: '#fff',
            target: document.getElementById('review-drawer') || document.body
        });
        confirmed = res.isConfirmed;
    } else {
        confirmed = confirm(`${titleMsg}\n\n${textMsg}`);
    }

    if (!confirmed) return;

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
        window._showToast?.('🔓 精校保护已解除，下次同步将由 AI 重新翻译', 'info');
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

    let wantedLangs = [];
    if (targetMode === 'current') {
        wantedLangs = [lc];
    } else {
        wantedLangs = (window.settingsData?.i18n_settings?.targets || []).map(t => t.lang_code);
        if (!wantedLangs || wantedLangs.length === 0) {
            wantedLangs = Object.keys(window._reviewState.data?.langs || {});
        }
    }

    if (!window._reviewState.wantedLangMap) {
        window._reviewState.wantedLangMap = {};
    }

    const validSourceParas = (window._reviewState.data?.source_paragraphs || []).filter(p => p.index >= 0);
    const sourceParasCount = validSourceParas.length || 1;
    wantedLangs.forEach(lang => {
        window._reviewState.wantedLangMap[lang] = {
            status: 'running',
            progress: 5,
            translated_paras: 0,
            total_paras: sourceParasCount,
            _triggeredAt: Date.now(),
            _confirmedRunning: false
        };
        if (window._reviewState.data && window._reviewState.data.langs && window._reviewState.data.langs[lang]) {
            window._reviewState.data.langs[lang].is_missing = true;
            // 物理重置旧的残余进度账本，杜绝旧数据污染新进度呈现
            window._reviewState.data.langs[lang].progress = {
                translated_paras: 0,
                total_paras: sourceParasCount
            };
        }
        if (window._reviewState.edits && window._reviewState.edits[lang]) {
            delete window._reviewState.edits[lang];
        }
    });

    if (targetMode === 'current' && lc) {
        window._reviewState.activeLang = lc;
    }

    window._reviewState.wantedLangs = Object.keys(window._reviewState.wantedLangMap).filter(l => window._reviewState.wantedLangMap[l].status === 'running');

    _reviewRender();
    const modeLabel = targetMode === 'current' ? `[${(lc || '').toUpperCase()}]` : '所有目标语种';
    window._showToast?.(`🚀 已推送后台 AI 翻译管线 (${modeLabel})，正在处理中...`, 'info');

    try {
        const res = await fetch('/api/publish/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: 'static', paths: [docId], force: true, clear_cache: true, target_langs: targetLangs })
        });
        const d = await res.json();
        if (d.status === 'error') throw new Error(d.message);

        // 如果已有轮询循环在运行，不再开启重复轮询
        if (window._reviewState._isPolling) return;
        window._reviewState._isPolling = true;

        let attempts = 0;
        const poll = async () => {
            if (attempts > 300 || !window._reviewState.wantedLangMap || Object.keys(window._reviewState.wantedLangMap).length === 0) {
                window._reviewState.wantedLangMap = {};
                window._reviewState.wantedLangs = null;
                window._reviewState._isPolling = false;
                window._showToast?.('翻译耗时超出预期，请稍后重新打开抽屉查看', 'warning');
                _reviewRender();
                return;
            }
            try {
                const checkRes = await fetch(`/api/translation/review/${encodeURIComponent(docId)}`);
                const checkData = await checkRes.json();

                if (checkData && checkData.langs) {
                    window._reviewState.data = checkData;

                    const runningLangs = Object.keys(window._reviewState.wantedLangMap).filter(l => window._reviewState.wantedLangMap[l].status === 'running');

                    runningLangs.forEach(lang => {
                        const ld = checkData.langs[lang];
                        if (!ld) return;
                        const langEntry = window._reviewState.wantedLangMap[lang];

                        // 🚀 [V114.7] 分阶段线性映射进度算法：正文段落翻译精准占用 25% - 85% 动态区间
                        if (ld.progress && ld.progress.running) {
                            langEntry._confirmedRunning = true;
                            const tParas = ld.progress.translated_paras || 0;
                            const totalParas = ld.progress.total_paras || 1;
                            langEntry.translated_paras = tParas;
                            langEntry.total_paras = totalParas;

                            const textRatio = Math.min(1.0, tParas / Math.max(1, totalParas));
                            if (textRatio < 1.0) {
                                langEntry.progress = Math.min(84, Math.floor(25 + textRatio * 60));
                            } else {
                                langEntry.progress = 85; // 正文完成，开启元数据润色
                            }
                        }

                        // 🚀 译文全量就绪检测：当且仅当后端管线完全跑完且已写入账本 (is_missing=false 且不在 running 中)，标记该语种翻译完成
                        if (!ld.is_missing && langEntry._confirmedRunning && (!ld.progress || !ld.progress.running)) {
                            langEntry.status = 'done';
                            langEntry.progress = 100;
                        }
                    });

                    // 同步更新已就绪目标语种的 edits 缓存（仅限非 running 语种，防止旧数据污染）
                    Object.keys(checkData.langs).forEach(lc_key => {
                        const ld = checkData.langs[lc_key];
                        const isLangRunning = window._reviewState.wantedLangMap && window._reviewState.wantedLangMap[lc_key] && window._reviewState.wantedLangMap[lc_key].status === 'running';
                        if (ld && !ld.is_missing && !isLangRunning) {
                            window._reviewState.edits[lc_key] = {
                                title: ld.title || '',
                                desc: ld.desc || '',
                                paragraphs: (ld.paragraphs || []).map(p => ({ ...p }))
                            };
                        }
                    });

                    const stillRunning = Object.keys(window._reviewState.wantedLangMap).filter(l => window._reviewState.wantedLangMap[l].status === 'running');
                    const hasStatusChanged = !window._reviewState.wantedLangs || window._reviewState.wantedLangs.length !== stillRunning.length;
                    window._reviewState.wantedLangs = stillRunning;

                    if (stillRunning.length === 0) {
                        const finishedNames = Object.keys(window._reviewState.wantedLangMap).map(l => l.toUpperCase()).join(', ');
                        window._reviewState.wantedLangMap = {};
                        window._reviewState.wantedLangs = null;
                        window._reviewState._isPolling = false;
                        _reviewRender();
                        window._showToast?.(`✅ 译文已全量成功就绪 (${finishedNames})！`, 'success');
                        return;
                    } else {
                        // 🛡️ [V114.5] 智能防抖与正确作用域计算：计算 activeIsRunning 变量，严防 ReferenceError
                        const activeEntry = window._reviewState.activeLang && window._reviewState.wantedLangMap && window._reviewState.wantedLangMap[window._reviewState.activeLang];
                        const activeIsRunning = activeEntry && activeEntry.status === 'running';

                        if (hasStatusChanged) {
                            _reviewRender();
                        } else if (activeIsRunning) {
                            if (typeof window.updateReviewProgressOnly === 'function') {
                                window.updateReviewProgressOnly();
                            }
                        }
                    }
                }
            } catch (err) {
                console.error("Polling error", err);
            }
            attempts++;
            setTimeout(poll, 1200);
        };
        setTimeout(poll, 300);

    } catch (e) {
        if (targetMode === 'current' && lc && window._reviewState.wantedLangMap) {
            delete window._reviewState.wantedLangMap[lc];
        } else {
            window._reviewState.wantedLangMap = {};
        }
        window._reviewState.wantedLangs = null;
        window._reviewState._isPolling = false;
        window._showToast?.('分发触发失败: ' + e.message, 'error');
        _reviewRender();
    }
};

/* ─── 切换语种标签 ───────────────────────────────────── */
window.switchReviewLang = function (lc) {
    window._reviewState.activeLang = lc;
    _reviewRender();
};

/* ─── 单字段 AI 润色与重置 ───────────────────────────── */
window.polishFieldWithAI = async function (fieldKey, btnEl) {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc || !state.docId) return;

    const fieldLabel = fieldKey === 'title' ? '标题' : '描述';
    const inputEl = document.getElementById(fieldKey === 'title' ? 'review-title-input' : 'review-desc-input');
    let currentVal = inputEl ? inputEl.value.trim() : (state.edits[lc]?.[fieldKey] || '').trim();

    let textToPolish = currentVal;
    if (!textToPolish || textToPolish === '无描述') {
        let originalText = fieldKey === 'title' ? state.data?.source_title : state.data?.source_desc;
        if (!originalText || !originalText.trim() || originalText.trim() === '无描述') {
            const sourceParas = state.data?.source_paragraphs || [];
            const firstPara = (sourceParas.find(p => p.text && !p.text.startsWith('#') && !p.text.startsWith('```'))?.text || '').slice(0, 150);
            originalText = `${state.data?.source_title || ''}: ${firstPara}`.trim();
        }
        textToPolish = originalText;
    }
    if (!textToPolish) {
        window._showToast?.('暂无有效文本或正文，无法发起 AI 润色', 'warning');
        return;
    }

    // 🚀 [UI 实时进度与状态倒流]
    let oldBtnHtml = '🪄';
    if (btnEl) {
        oldBtnHtml = btnEl.innerHTML;
        btnEl.disabled = true;
        btnEl.innerHTML = '⏳';
        btnEl.style.opacity = '0.7';
    }
    if (inputEl) {
        inputEl.style.transition = 'all 0.3s ease';
        inputEl.style.boxShadow = '0 0 10px rgba(255, 171, 0, 0.4)';
        inputEl.style.borderColor = 'var(--accent-primary, #ffab00)';
    }

    window._showToast?.(`🪄 正在使用 AI 为 [${lc.toUpperCase()}] 润色${fieldLabel}...`, 'info');
    try {
        const res = await fetch('/api/translation/review/retranslate-paragraph', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_id: state.docId,
                lang_code: lc,
                para_index: fieldKey === 'title' ? -1 : -2,
                source_text: textToPolish
            })
        });

        const data = await res.json();
        if (res.ok && data && data.translated_text) {
            if (!state.edits[lc]) state.edits[lc] = {};
            state.edits[lc][fieldKey] = data.translated_text;

            if (btnEl) {
                btnEl.innerHTML = '✅';
                setTimeout(() => {
                    btnEl.innerHTML = oldBtnHtml;
                    btnEl.disabled = false;
                    btnEl.style.opacity = '1';
                }, 1200);
            }

            _reviewRender();
            window._showToast?.(`✅ ${fieldLabel} AI 润色已完成！`, 'success');
            window.saveReviewDraft?.(lc);
            window.updateReviewDirtyUI?.();
        } else {
            if (btnEl) {
                btnEl.innerHTML = oldBtnHtml;
                btnEl.disabled = false;
                btnEl.style.opacity = '1';
            }
            window._showToast?.('润色失败: ' + (data?.error || data?.detail || '未知错误'), 'error');
        }
    } catch (e) {
        if (btnEl) {
            btnEl.innerHTML = oldBtnHtml;
            btnEl.disabled = false;
            btnEl.style.opacity = '1';
        }
        window._showToast?.('润色网络异常: ' + e.message, 'error');
    } finally {
        if (inputEl) {
            inputEl.style.boxShadow = '';
            inputEl.style.borderColor = '';
        }
    }
};

window.resetFieldToDefault = function (fieldKey, btnEl) {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc || !state.data?.langs?.[lc]) return;

    const defaultVal = state.data.langs[lc][fieldKey] || '';
    const fieldLabel = fieldKey === 'title' ? '标题' : '描述';
    const inputEl = document.getElementById(fieldKey === 'title' ? 'review-title-input' : 'review-desc-input');

    if (btnEl) {
        const oldHtml = btnEl.innerHTML;
        btnEl.innerHTML = '✅';
        btnEl.disabled = true;
        setTimeout(() => {
            btnEl.innerHTML = oldHtml;
            btnEl.disabled = false;
        }, 800);
    }

    if (inputEl) {
        inputEl.style.transition = 'all 0.3s ease';
        inputEl.style.boxShadow = '0 0 10px rgba(76, 175, 80, 0.4)';
        setTimeout(() => { if (inputEl) inputEl.style.boxShadow = ''; }, 800);
    }

    if (!state.edits[lc]) state.edits[lc] = {};
    state.edits[lc][fieldKey] = defaultVal;
    _reviewRender();
    window._showToast?.(`🔄 已恢复为初始 ${fieldLabel}`, 'info');
    window.saveReviewDraft?.(lc);
    window.updateReviewDirtyUI?.();
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
    block.innerHTML = `<span class="review-para-num">#${idx + 1}</span><textarea class="review-para-textarea" onblur="window.reviewSaveParagraph(${idx}, this.value)">${_escapeHtml(para.text)}</textarea>`;
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
    // 🛡️ 重入锁：防止 confirm 面板显示期间被反复调用
    if (window._closeReviewLocked) return;

    const state = window._reviewState;
    let hasDirty = false;
    if (state.data && state.data.langs) {
        for (const lc of Object.keys(state.data.langs)) {
            if (window._isReviewDirty && window._isReviewDirty(lc)) {
                hasDirty = true;
                break;
            }
        }
    }

    function _doClose() {
        window._closeReviewLocked = false;
        const overlay = document.getElementById('review-drawer-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => { overlay.style.display = 'none'; }, 250);
        }
        // 移除确认面板（如存在）
        const panel = document.getElementById('review-close-confirm-panel');
        if (panel) panel.remove();
    }

    if (hasDirty) {
        window._closeReviewLocked = true;

        // 移除已有的确认面板（防止重复）
        const existing = document.getElementById('review-close-confirm-panel');
        if (existing) existing.remove();

        // 🛡️ 自定义 DOM 内确认面板，彻底替代原生 confirm()
        const panel = document.createElement('div');
        panel.id = 'review-close-confirm-panel';
        panel.style.cssText = `
            position: fixed; inset: 0; z-index: 9999;
            display: flex; align-items: center; justify-content: center;
            background: rgba(0,0,0,0.5); backdrop-filter: blur(2px);
        `;
        panel.innerHTML = `
            <div style="
                background: rgb(var(--bg-modal-solid-rgb, 30,30,35));
                border: 1px solid var(--glass-border, rgba(255,255,255,0.1));
                border-radius: 12px; padding: 24px 28px; max-width: 400px;
                box-shadow: 0 8px 40px rgba(0,0,0,0.5);
                text-align: center; color: var(--text-bright, #eee);
            ">
                <div style="font-size: 1.5rem; margin-bottom: 12px;">⚠️</div>
                <div style="font-size: 0.92rem; line-height: 1.5; margin-bottom: 20px;">
                    当前有未保存的校对修改，确定要关闭并丢弃这些修改吗？
                </div>
                <div style="display: flex; gap: 12px; justify-content: center;">
                    <button id="review-confirm-cancel" style="
                        padding: 8px 20px; border-radius: 8px; border: 1px solid var(--glass-border, rgba(255,255,255,0.15));
                        background: var(--white-05, rgba(255,255,255,0.05));
                        color: var(--text-bright, #eee); cursor: pointer; font-size: 0.85rem;
                        transition: background 0.2s;
                    ">取消</button>
                    <button id="review-confirm-discard" style="
                        padding: 8px 20px; border-radius: 8px; border: none;
                        background: linear-gradient(135deg, #e53935, #ff7043);
                        color: #fff; cursor: pointer; font-size: 0.85rem; font-weight: 600;
                        box-shadow: 0 2px 8px rgba(229,57,53,0.3); transition: transform 0.15s;
                    ">丢弃并关闭</button>
                </div>
            </div>
        `;

        // 点击面板背景也视为取消
        panel.addEventListener('click', (e) => {
            if (e.target === panel) {
                window._closeReviewLocked = false;
                panel.remove();
            }
        });

        panel.querySelector('#review-confirm-cancel').addEventListener('click', () => {
            window._closeReviewLocked = false;
            panel.remove();
        });

        panel.querySelector('#review-confirm-discard').addEventListener('click', () => {
            if (state.data && state.data.langs) {
                Object.keys(state.data.langs).forEach(lc => {
                    window.clearReviewDraft?.(lc);
                });
            }
            _doClose();
        });

        document.body.appendChild(panel);
        return;
    }

    _doClose();
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

    // 2. 基于物理边界吸附与段落锚定的 3 轴同步联动滚动
    let activeScrollSource = null;
    let scrollTimeout = null;

    const onScrollHandler = (e) => {
        const target = e.currentTarget;
        if (activeScrollSource && activeScrollSource !== target) return;
        activeScrollSource = target;

        const maxScroll = target.scrollHeight - target.clientHeight;
        if (maxScroll <= 0) return;

        const isAtBottom = (maxScroll - target.scrollTop) < 15;
        const isAtTop = target.scrollTop < 15;
        const scrollRatio = target.scrollTop / maxScroll;

        const visibleCols = [colTarget, colPreview, colSource].filter(c => c && c.style.display !== 'none');

        if (isAtBottom) {
            // 🛡️ [边界吸附红线] 一栏到达最底部，强制所有分栏精准到达各自 100% 底部
            visibleCols.forEach(c => {
                if (c !== target) {
                    c.scrollTop = c.scrollHeight - c.clientHeight;
                }
            });
        } else if (isAtTop) {
            // 🛡️ [边界吸附红线] 一栏到达最顶部，强制所有分栏精准复位至 0
            visibleCols.forEach(c => {
                if (c !== target) {
                    c.scrollTop = 0;
                }
            });
        } else {
            // 🛡️ [中间区段段落锚定 + 比例补偿]
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

            const prefixes = { 'col-target': 'review-para', 'col-preview': 'preview-para', 'col-source': 'source-para' };
            visibleCols.forEach(c => {
                if (c !== target) {
                    if (activeIdx !== null) {
                        const targetEl = c.querySelector(`#${prefixes[c.id]}-${activeIdx}`);
                        if (targetEl) {
                            const colRect = c.getBoundingClientRect();
                            const elRect = targetEl.getBoundingClientRect();
                            c.scrollTop += (elRect.top - colRect.top) - diff;
                        } else {
                            const cMax = c.scrollHeight - c.clientHeight;
                            c.scrollTop = Math.round(scrollRatio * cMax);
                        }
                    } else {
                        const cMax = c.scrollHeight - c.clientHeight;
                        c.scrollTop = Math.round(scrollRatio * cMax);
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

/* ─── 🪄 单段落 AI 微粒度重译 ─────────────────────────────────── */
window.retranslateSingleParagraph = async function (idx) {
    const state = window._reviewState;
    const lc = state.activeLang;
    if (!lc || !state.docId) return;

    const sourceParas = state.data?.source_paragraphs || [];
    const sourcePara = sourceParas.find(sp => sp.index === idx);
    const sourceText = sourcePara?.text || '';
    if (!sourceText) return;

    const blockEl = document.getElementById(`review-para-${idx}`);
    const btnEl = blockEl?.querySelector('.para-retrans-btn');
    if (btnEl) {
        btnEl.innerText = "⏳ 翻译中...";
        btnEl.disabled = true;
    }

    try {
        const res = await apiFetch('/api/translation/review/retranslate-paragraph', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_id: state.docId,
                lang_code: lc,
                para_index: idx,
                source_text: sourceText
            })
        });

        if (res && res.ok && res.translated_text) {
            window.reviewSaveParagraph(idx, res.translated_text);
            window._showToast?.(`✅ 第 ${idx + 1} 段 AI 重译完成！`, 'success');
        } else {
            window._showToast?.('重译失败: ' + (res?.error || '未知错误'), 'error');
            if (btnEl) {
                btnEl.innerText = "🪄 仅重译此段";
                btnEl.disabled = false;
            }
        }
    } catch (e) {
        window._showToast?.('重译网络异常: ' + e.message, 'error');
        if (btnEl) {
            btnEl.innerText = "🪄 仅重译此段";
            btnEl.disabled = false;
        }
    }
};
