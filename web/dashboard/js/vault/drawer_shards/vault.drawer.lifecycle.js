/**
 * 📡 [V68.0] Illacme Plenipes Vault - Drawer Lifecycle & Safe Timer Shard
 * 职责：抽屉互斥平滑展开/收起、全局调用令牌防线、安全防泄漏轮询定时器启动与智能自退。
 */

(function () {
    window.closeVaultDrawer = () => {
        const drawer = document.getElementById('vault-drawer');
        if (drawer) {
            drawer.style.right = '-480px';
        }
        const backdrop = document.getElementById('vault-drawer-backdrop');
        if (backdrop) {
            backdrop.style.opacity = '0';
            backdrop.style.pointerEvents = 'none';
        }
        // 🚀 [V75.3] 离开时自动销毁定时器以防内存泄露
        if (window.vaultDrawerTimer) {
            clearInterval(window.vaultDrawerTimer);
            window.vaultDrawerTimer = null;
        }
    };

    // 🚀 [V105.1] 统一安全的定时器启动器，彻底隔绝由于异步竞态导致的孤儿定时器泄漏
    window.safeStartDrawerTimer = (relPath) => {
        const drawer = document.getElementById('vault-drawer');
        if (!drawer || drawer.style.display === 'none' || window.currentDocId !== relPath) {
            return;
        }
        if (window.vaultDrawerTimer) {
            clearInterval(window.vaultDrawerTimer);
            window.vaultDrawerTimer = null;
        }
        window.vaultDrawerTimer = setInterval(async () => {
            if (drawer && drawer.style.display !== 'none' && window.currentDocId === relPath) {
                const stillRunning = typeof window.refreshVaultDrawerStatus === 'function' ? await window.refreshVaultDrawerStatus(relPath) : false;
                if (!stillRunning) {
                    clearInterval(window.vaultDrawerTimer);
                    window.vaultDrawerTimer = null;
                    console.info("🔌 [Drawer] 侦测到所有分发卡片状态均已稳定，定时状态更新器已智能自退销毁。");
                }
            } else {
                clearInterval(window.vaultDrawerTimer);
                window.vaultDrawerTimer = null;
            }
        }, 2000);
    };

    window.openVaultDrawer = async (relPath) => {
        // 🚀 [全局抽屉互斥排他] 自动平滑收起其他抽屉
        if (typeof window.closeArticleSyndicationDrawer === 'function') window.closeArticleSyndicationDrawer();
        if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
        const reviewOverlay = document.getElementById('review-drawer-overlay');
        if (reviewOverlay) {
            reviewOverlay.style.opacity = '0';
            setTimeout(() => { reviewOverlay.style.display = 'none'; }, 200);
        }

        window.currentDocId = relPath;
        const drawer = document.getElementById('vault-drawer');
        const backdrop = document.getElementById('vault-drawer-backdrop');
        const hubDocId = document.getElementById('hub-doc-id');

        if (hubDocId) hubDocId.innerText = relPath.toUpperCase();
        if (backdrop) {
            requestAnimationFrame(() => {
                backdrop.style.opacity = '1';
                backdrop.style.pointerEvents = 'auto';
            });
        }
        if (drawer) {
            setTimeout(() => {
                drawer.style.right = '0px';
            }, 10);
        }

        // 🚀 [数据先验与自主就绪] 无论之前是否打开过其他抽屉，立即自主并发预热全域能力矩阵
        if (!window.allPlugins || window.allPlugins.length === 0) {
            try {
                const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url) => (await fetch(url)).json());
                const pluginRes = await fetchFunc('/api/plugins/list');
                if (pluginRes && pluginRes.plugins) window.allPlugins = pluginRes.plugins;
            } catch (e) {
                console.warn("[Vault Drawer] openVaultDrawer prefetch failed:", e);
            }
        }

        // 物理清理并设置调用标记防线
        if (window.vaultDrawerTimer) {
            clearInterval(window.vaultDrawerTimer);
            window.vaultDrawerTimer = null;
        }
        const myCallToken = Math.random();
        window.vaultDrawerCallToken = myCallToken;

        // 立即执行一次获取与渲染，若状态已全部稳定，则不启动轮询器
        const needsLoop = typeof window.refreshVaultDrawerStatus === 'function' ? await window.refreshVaultDrawerStatus(relPath) : false;

        // 异步返回后校验令牌时效性
        if (window.vaultDrawerCallToken !== myCallToken) {
            console.warn("🔌 [Drawer] 侦测到更有时效性的打开指令，当前过期的初始化任务已安全熔断。");
            return;
        }

        if (needsLoop) {
            window.safeStartDrawerTimer(relPath);
        }
    };
})();
