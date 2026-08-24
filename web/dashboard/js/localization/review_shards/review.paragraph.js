/**
 * 🔒 [I5] Illacme Plenipes Translation Review - Paragraph Inline Editor & Retranslate Shard
 * 职责：段落块点击就地编辑、段落内容保存退出与单段落 AI 重新翻译。
 */

(function () {
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

        const escapeFunc = typeof _escapeHtml === 'function' ? _escapeHtml : (s => (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'));
        block.innerHTML = `<span class="review-para-num">#${idx + 1}</span><textarea class="review-para-textarea" onblur="window.reviewSaveParagraph(${idx}, this.value)">${escapeFunc(para.text)}</textarea>`;
        block.querySelector('textarea')?.focus();
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
        if (block && typeof _renderParaBlock === 'function') {
            block.dataset.editing = '0';
            block.innerHTML = _renderParaBlock(paras[idx]);
        }
        // 🚀 实时同步渲染预览分栏中的对应段落（渲染逻辑委托给 review.render.js）
        if (typeof _reviewRenderPreviewPara === 'function') {
            _reviewRenderPreviewPara(idx, state);
        }
        if (typeof window.saveReviewDraft === 'function') {
            window.saveReviewDraft(lc);
        }
        if (typeof window.updateReviewDirtyUI === 'function') {
            window.updateReviewDirtyUI();
        }
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
            const fetchFunc = window.apiFetch || (async (url, init) => {
                const r = await fetch(url, init);
                return r.json();
            });

            const res = await fetchFunc('/api/translation/review/retranslate-paragraph', {
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
})();
