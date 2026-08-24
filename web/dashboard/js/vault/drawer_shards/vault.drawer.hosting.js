/**
 * 📡 [V68.0] Illacme Plenipes Vault - Batch Hosting Dispatch & Interop Shard
 * 职责：勾选全站托管平台并行发布算子、直达托管插件配置编辑器与工作流深度串联无缝返回。
 */

(function () {
    // 🛡️ [V89.8] 防呆辅助：自愈式 Toast 弹窗渲染器
    const showToast = (message, icon = 'success') => {
        if (window.Swal) {
            window.Swal.fire({
                title: message,
                icon: icon,
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
        } else if (window._showToast) {
            window._showToast(message, icon);
        } else {
            console.log(`[Toast] ${icon}: ${message}`);
        }
    };

    // 🚀 [V106.5] 勾选全站托管平台并行发布算子 (与社媒分发抽屉 100% 体验对齐)
    window.dispatchVaultHostingSelection = async (relPath) => {
        const targetDoc = relPath || window.currentDocId;
        if (!targetDoc) return;

        const checkedBoxes = document.querySelectorAll('.vault-hosting-platform-checkbox:checked');
        if (!checkedBoxes || checkedBoxes.length === 0) {
            showToast("⚠️ 请先勾选至少一个已就绪的全站托管平台", "warning");
            return;
        }

        const selectedChannels = Array.from(checkedBoxes).map(cb => cb.value);
        showToast(`🚀 正在向选中的 ${selectedChannels.length} 个托管平台并行发布中...`, "info");

        const mainBtn = document.querySelector('.sovereign-action-grid .primary-hub-btn');
        if (mainBtn) {
            mainBtn.disabled = true;
            mainBtn.style.opacity = '0.5';
            mainBtn.innerHTML = '<span class="btn-icon">⚡</span> 正在发布中...';
        }

        const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url, init) => (await fetch(url, init)).json());

        // 1. 先触发一次全量重新装帧编译
        await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(targetDoc)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ locales: [], force: true, clear_cache: false })
        });

        // 2. 并行触发所有已勾选的托管平台推送
        const publishPromises = selectedChannels.map(channelId => {
            return fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(targetDoc)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_channel: channelId })
            });
        });

        await Promise.all(publishPromises);
        showToast(`✅ 已向 ${selectedChannels.length} 个全站托管平台触发同步请求！正在云端部署...`, "success");

        if (typeof window.safeStartDrawerTimer === 'function') window.safeStartDrawerTimer(targetDoc);
        setTimeout(() => {
            if (typeof window.refreshVaultDrawerStatus === 'function') window.refreshVaultDrawerStatus(targetDoc);
        }, 1200);
    };

    // 🚀 [一键直达全站托管插件配置编辑器 (带工作流深度串联返回)]
    window.goToHostingPluginConfig = async function (pluginId = 'github_pages') {
        // 记录网页托管发布返回上下文
        window._vaultReturnContext = {
            relPath: window.currentDocId
        };

        // 平滑收起网页托管抽屉
        const drawer = document.getElementById('vault-drawer');
        if (drawer) drawer.style.right = '-480px';
        const backdrop = document.getElementById('vault-drawer-backdrop');
        if (backdrop) {
            backdrop.style.opacity = '0';
            backdrop.style.pointerEvents = 'none';
        }

        if (typeof window.openPluginConfig === 'function') {
            try {
                await window.openPluginConfig(pluginId, 'hosting', 'vault');
                if (typeof window.updateDrawerReturnButtons === 'function') {
                    window.updateDrawerReturnButtons();
                }
            } catch (e) {
                console.warn(`[Vault Drawer] Unable to open config for ${pluginId}:`, e);
                showToast(`⚙️ 请前往「🧩 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
            }
        } else {
            showToast(`⚙️ 请前往「🧩 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
        }
    };

    // 🚀 [工作流深度串联：从插件配置抽屉保存/返回时无缝接力拉起并刷新网页托管发布抽屉]
    window.returnToVaultDrawer = async function () {
        const ctx = window._vaultReturnContext;
        if (!ctx || !ctx.relPath) {
            if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
            return;
        }
        const targetRelPath = ctx.relPath;
        window._vaultReturnContext = null;

        // 🛡️ 瞬态防误触防线：先无缝拉起目标网页托管抽屉（保持背景遮罩常驻，彻底阻断底层主页面暴露）
        if (typeof window.openVaultDrawer === 'function') {
            await window.openVaultDrawer(targetRelPath);
        }

        // 紧接着平滑隐藏上层插件配置抽屉，达成 0ms 视觉缝隙平滑过渡
        if (typeof window.closePluginDrawer === 'function') {
            window.closePluginDrawer();
        }

        // 立即自愈感应并刷新状态
        if (typeof window.refreshVaultDrawerStatus === 'function') {
            await window.refreshVaultDrawerStatus(targetRelPath);
        }
    };
})();
