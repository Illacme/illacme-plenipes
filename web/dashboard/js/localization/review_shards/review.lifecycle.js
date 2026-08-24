/**
 * 🔒 [I5] Illacme Plenipes Translation Review - Lifecycle & Confirm Shard
 * 职责：抽屉主入口（模式/算力准入拦截）、语种切换与防丢弃关闭确认。
 */

(function () {
    /* ─── 入口：从 Vault 文稿列表打开校对抽屉（Q5=B） ──── */
    window.openTranslationReview = async function (docId) {
        if (typeof window.ensureReviewDrawerMounted === 'function') {
            window.ensureReviewDrawerMounted();
        }
        const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';
        if (pubMode === 'basic' || pubMode === 'enhanced') {
            const modeText = pubMode === 'basic' ? '基础物理出版模式' : '智能母语增强模式';
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '🔒 译文校对不可用',
                    text: `当前品牌处于 ${modeText}，不进行正文 AI 翻译，因此译文校对工作台已挂起。若要使用多语言翻译与校对，请先将印记出版模式切换为“全球多语言分发模式”。`,
                    icon: 'warning',
                    background: 'rgba(20, 20, 25, 0.95)',
                    color: '#fff',
                    confirmButtonText: '确定',
                    confirmButtonColor: 'var(--accent-primary)'
                });
            } else {
                alert(`🔒 译文校对不可用: 当前品牌处于 ${modeText}，不进行正文 AI 翻译。`);
            }
            return;
        }

        const isAiEnabled = !window.governanceContext ||
            (window.governanceContext.ai && window.governanceContext.ai.status !== 'disabled');
        if (!isAiEnabled) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '🔒 协同服务已离线',
                    text: '当前 AI 算力总控已关闭，译文校对工作台不可用。若要进行译文人工校对与锁定，请前往算力中心重新开启 AI 算力。',
                    icon: 'warning',
                    background: 'rgba(20, 20, 25, 0.95)',
                    color: '#fff',
                    confirmButtonText: '确定',
                    confirmButtonColor: 'var(--accent-primary)'
                });
            } else {
                alert('🔒 协同服务已离线: 当前 AI 算力总控已关闭，译文校对工作台不可用。');
            }
            return;
        }

        const state = window._reviewState;
        state.docId = docId;
        state.edits = {};
        state.wantedLangMap = {};
        state.wantedLangs = null;

        if (typeof _reviewShowDrawer === 'function') _reviewShowDrawer();
        if (typeof _reviewSetLoading === 'function') _reviewSetLoading(true);

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

            if (typeof _reviewRender === 'function') _reviewRender();
        } catch (e) {
            if (typeof _reviewShowError === 'function') _reviewShowError('加载译文快照失败: ' + e.message);
        } finally {
            if (typeof _reviewSetLoading === 'function') _reviewSetLoading(false);
        }
    };

    /* ─── 切换语种标签 ───────────────────────────────────── */
    window.switchReviewLang = function (lc) {
        window._reviewState.activeLang = lc;
        if (typeof _reviewRender === 'function') _reviewRender();
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
})();
