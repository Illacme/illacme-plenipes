/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - Workflow Deep Integration Shard
 * 职责：跨抽屉工作流深度串联（一键直达插件配置、直达译文校对工作台、0ms 无缝接力返回）。
 */

(function () {
    // 🚀 [右上角返回/关闭分流处理器]
    window.handleReviewDrawerCloseClick = function () {
        if (window._syndicateReturnContext) {
            window.returnToSyndicateDrawer();
        } else {
            if (typeof window.closeTranslationReview === 'function') {
                window.closeTranslationReview();
            }
        }
    };

    window.handlePluginDrawerCloseClick = function () {
        if (window._syndicateReturnContext) {
            window.returnToSyndicateDrawer();
        } else if (window._vaultReturnContext) {
            if (typeof window.returnToVaultDrawer === 'function') {
                window.returnToVaultDrawer();
            } else {
                if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
            }
        } else {
            if (typeof window.closePluginDrawer === 'function') {
                window.closePluginDrawer();
            }
        }
    };

    window.updateDrawerReturnButtons = function () {
        const isFromSyndicate = !!window._syndicateReturnContext;
        const isFromVault = !!window._vaultReturnContext;
        const hasReturnContext = isFromSyndicate || isFromVault;

        // 1. 译文校对工作台右上角关闭按钮动态变身
        const reviewCloseBtn = document.getElementById('btn-close-review-drawer') || document.querySelector('#review-drawer .close-btn');
        if (reviewCloseBtn) {
            if (hasReturnContext) {
                reviewCloseBtn.innerHTML = '‹‹ 返回';
                reviewCloseBtn.style.cssText = 'padding: 4px 10px; font-size: 0.75rem; font-weight: 600; background: rgba(0, 242, 255, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
            } else {
                reviewCloseBtn.innerHTML = '✕';
                reviewCloseBtn.style.cssText = 'background: none; border: none; color: var(--text-dim); font-size: 1.3rem; cursor: pointer; line-height: 1; padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
            }
        }

        // 2. 插件配置抽屉右上角关闭按钮动态变身
        const pluginCloseBtn = document.getElementById('close-p-drawer');
        if (pluginCloseBtn) {
            if (hasReturnContext) {
                pluginCloseBtn.innerHTML = '‹‹ 返回';
                pluginCloseBtn.style.cssText = 'padding: 4px 10px; font-size: 0.75rem; font-weight: 600; background: rgba(0, 242, 255, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
            } else {
                pluginCloseBtn.innerHTML = '×';
                pluginCloseBtn.style.cssText = 'background: transparent; border: none; color: var(--text-dim); font-size: 1.3rem; cursor: pointer; line-height: 1; padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;';
            }
        }
    };

    // 🚀 [一键直达插件配置编辑器 (带工作流深度串联返回)]
    window.goToPluginConfig = async function (pluginId, category = 'publisher') {
        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();

        // 记录返回上下文，形成工作流深度闭环
        window._syndicateReturnContext = {
            relPath: window.currentSyndicatingRelPath,
            title: window.currentSyndicatingTitle,
            selectedLang: selectedLang
        };

        // 平滑收起广播抽屉
        if (typeof window.closeArticleSyndicationDrawer === 'function') {
            window.closeArticleSyndicationDrawer();
        }

        if (typeof window.openPluginConfig === 'function') {
            try {
                await window.openPluginConfig(pluginId, category, 'syndicate');
                window.updateDrawerReturnButtons();
            } catch (e) {
                console.warn(`[Syndicate Drawer] Unable to open config for ${pluginId}:`, e);
                if (typeof window.showToast === 'function') {
                    window.showToast(`⚙️ 请前往「🔌 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
                }
            }
        } else {
            if (typeof window.showToast === 'function') {
                window.showToast(`⚙️ 请前往「🔌 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
            }
        }
    };

    // 🚀 [一键直达译文人工校对工作台 (带工作流深度串联返回)]
    window.jumpToReviewDrawer = function (relPath, articleTitle) {
        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();

        window._syndicateReturnContext = {
            relPath: relPath || window.currentSyndicatingRelPath,
            title: articleTitle || window.currentSyndicatingTitle,
            selectedLang: selectedLang
        };

        // 平滑收起广播抽屉
        if (typeof window.closeArticleSyndicationDrawer === 'function') {
            window.closeArticleSyndicationDrawer();
        }

        // 唤醒译文校对工作台并切换到目标语种
        if (typeof window.openTranslationReview === 'function') {
            window.openTranslationReview(relPath || window.currentSyndicatingRelPath);
            window.updateDrawerReturnButtons();
            setTimeout(() => {
                if (typeof window.switchReviewLang === 'function') {
                    window.switchReviewLang(selectedLang);
                }
                window.updateDrawerReturnButtons();
            }, 250);
        }
    };

    // 🚀 [工作流深度串联：一键无缝接力返回社媒分发抽屉]
    window.returnToSyndicateDrawer = async function () {
        const ctx = window._syndicateReturnContext;
        if (!ctx) return;
        window._syndicateReturnContext = null;

        window.updateDrawerReturnButtons();

        // ⚡ 静默刷新全局设置数据，保证刚在插件抽屉保存的凭据立即生效
        try {
            const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
            const cfgRes = await fetchApi('/api/settings/get');
            if (cfgRes && cfgRes.config) {
                window.settingsData = cfgRes.config;
            }
        } catch (_) {}

        // 🛡️ 瞬态防误触防线：1. 立即无缝拉起社媒分发抽屉（保持遮罩常驻，彻底阻断底层主页面暴露）
        if (typeof window.openArticleSyndicationDrawer === 'function') {
            await window.openArticleSyndicationDrawer(ctx.relPath, ctx.title);
            if (ctx.selectedLang) {
                setTimeout(() => {
                    const targetRadio = document.querySelector(`input[name="syndicate_lang"][value="${ctx.selectedLang}"]`);
                    if (targetRadio) {
                        targetRadio.checked = true;
                        if (typeof window.onSyndicateLangChange === 'function') {
                            window.onSyndicateLangChange(targetRadio, ctx.relPath);
                        }
                    }
                }, 50);
            }
        }

        // 2. 紧接着平滑收起上层的校对或插件抽屉，达成 0ms 视觉缝隙平滑过渡
        if (typeof window.closeTranslationReview === 'function') {
            window.closeTranslationReview();
        }
        if (typeof window.closePluginDrawer === 'function') {
            window.closePluginDrawer();
        }
    };
})();
