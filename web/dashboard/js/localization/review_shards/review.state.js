/**
 * 🔒 [I5] Illacme Plenipes Translation Review - State & Draft Persistence Shard
 * 职责：客户端校对状态机、本地草稿 LocalStorage 读写与脏检查计算。
 */

(function () {
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
})();
