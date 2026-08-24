/**
 * 🔒 [I5] Illacme Plenipes Translation Review - Translation Trigger & Pipeline Polling Shard
 * 职责：分栏视图切换、后台并发翻译管线推送、分阶段线性映射进度算法与轮询调度。
 */

(function () {
    window.toggleReviewSource = function () {
        window._reviewState.showSource = !window._reviewState.showSource;
        if (typeof _reviewRenderBody === 'function') _reviewRenderBody();
    };

    window.toggleReviewPreview = function () {
        window._reviewState.showPreview = !window._reviewState.showPreview;
        if (typeof _reviewRenderBody === 'function') _reviewRenderBody();
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

        if (typeof _reviewRender === 'function') _reviewRender();
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
                    if (typeof _reviewRender === 'function') _reviewRender();
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
                            if (typeof _reviewRender === 'function') _reviewRender();
                            window._showToast?.(`✅ 译文已全量成功就绪 (${finishedNames})！`, 'success');
                            return;
                        } else {
                            // 🛡️ [V114.5] 智能防抖与正确作用域计算：计算 activeIsRunning 变量，严防 ReferenceError
                            const activeEntry = window._reviewState.activeLang && window._reviewState.wantedLangMap && window._reviewState.wantedLangMap[window._reviewState.activeLang];
                            const activeIsRunning = activeEntry && activeEntry.status === 'running';

                            if (hasStatusChanged) {
                                if (typeof _reviewRender === 'function') _reviewRender();
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
            if (typeof _reviewRender === 'function') _reviewRender();
        }
    };
})();
