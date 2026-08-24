/**
 * 🔒 [I5] Illacme Plenipes Translation Review - Lock Management Shard
 * 职责：保存并精校锁定（Q2=A）、解除精校锁定（Q3=B）与快照脏态清除。
 */

(function () {
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
            if (typeof window.clearReviewDraft === 'function') window.clearReviewDraft(lc);
            if (typeof _reviewRender === 'function') _reviewRender();
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
            if (typeof window.clearReviewDraft === 'function') window.clearReviewDraft(lc);
            if (typeof _reviewRender === 'function') _reviewRender();
            window._showToast?.('🔓 精校保护已解除，下次同步将由 AI 重新翻译', 'info');
        } catch (e) {
            window._showToast?.('解锁失败: ' + e.message, 'error');
        }
    };
})();
