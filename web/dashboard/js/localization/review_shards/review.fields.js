/**
 * 🔒 [I5] Illacme Plenipes Translation Review - Field Polishing & Resetting Shard
 * 职责：标题与 SEO 描述等元数据单字段 AI 润色与初始快照重置。
 */

(function () {
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

                if (typeof _reviewRender === 'function') _reviewRender();
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
        if (typeof _reviewRender === 'function') _reviewRender();
        window._showToast?.(`🔄 已恢复为初始 ${fieldLabel}`, 'info');
        window.saveReviewDraft?.(lc);
        window.updateReviewDirtyUI?.();
    };
})();
