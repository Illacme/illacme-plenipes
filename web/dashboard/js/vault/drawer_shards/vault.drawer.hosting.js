/**
 * 📡 [V68.0] Illacme Plenipes Vault - Batch Hosting Dispatch & Interop Shard
 * 职责：勾选全站托管平台并行发布算子、直达托管插件配置编辑器与工作流深度串联无缝返回。
 */

(function () {
    let _vaultHostingDeployPoller = null;
    let _vaultHostingActiveBatchId = null;
    let _vaultHostingStartTime = 0;
    let _vaultHostingActiveDoc = null;

    // 🛡️ [V89.8] 防呆辅助：自愈式纯净轻量 Toast 弹窗渲染器
    const showToast = (message, icon = 'success') => {
        if (window.Swal) {
            window.Swal.fire({
                title: message,
                icon: icon,
                toast: true,
                position: 'top-end',
                timer: 2500,
                showConfirmButton: false
            });
        } else if (window._showToast) {
            window._showToast(message, icon);
        } else {
            console.log(`[Toast] ${icon}: ${message}`);
        }
    };

    // 🎨 [V126.0] 渲染抽屉底部实时发布态势卡片 (Live Deploy Pod)
    function renderLivePodHtml(state) {
        const pod = document.getElementById('vault-hosting-live-deploy-pod');
        if (!pod) return;

        const { batchId, status, durationSec, targets, channels } = state;
        const shortId = batchId.includes('_') ? '#' + batchId.split('_').pop() : '#' + batchId.slice(-6);

        let badgeClass = 'running';
        let badgeText = '⏳ 正在部署';
        if (status === 'SUCCESS') {
            badgeClass = 'success';
            badgeText = '✅ 部署完成';
        } else if (status === 'PARTIAL_SUCCESS') {
            badgeClass = 'failed';
            badgeText = '⚠️ 部分成功';
        } else if (status === 'FAILED') {
            badgeClass = 'failed';
            badgeText = '❌ 部署失败';
        }

        const isRunning = (status === 'RUNNING' || status === 'PENDING');
        const durText = `${typeof durationSec === 'number' ? Math.round(durationSec) : (durationSec || 0)}s`;

        // 渲染平台渠道标签行
        const chList = (channels && channels.length > 0) ? channels : Object.keys(targets || {});
        const targetsHtml = chList.map(ch => {
            const meta = typeof window.getVaultHostingMeta === 'function' ? window.getVaultHostingMeta(ch) : { name: ch, icon: '🌐' };
            const tInfo = (targets && targets[ch]) || {};
            const tStatus = tInfo.status || (isRunning ? 'RUNNING' : 'PENDING');
            const url = tInfo.url || '';

            if (url && (tStatus === 'SUCCESS' || !isRunning)) {
                return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="vault-live-target-pill link-ready" title="在新窗口访问线上页面: ${url}"><span>${meta.icon}</span> <span>${meta.name}</span> <span style="font-size:0.68rem;">↗</span></a>`;
            }
            if (tStatus === 'SUCCESS') {
                return `<span class="vault-live-target-pill" style="color:var(--neon-emerald);border-color:rgba(var(--neon-emerald-rgb),0.35);"><span>${meta.icon}</span> <span>${meta.name}</span> <span>✅</span></span>`;
            }
            if (tStatus === 'FAILED') {
                return `<span class="vault-live-target-pill" style="color:var(--neon-red);border-color:rgba(var(--neon-red-rgb),0.35);" title="${tInfo.error || '推送失败'}"><span>${meta.icon}</span> <span>${meta.name}</span> <span>❌</span></span>`;
            }
            return `<span class="vault-live-target-pill"><span>${meta.icon}</span> <span>${meta.name}</span> <span class="mono">⏳</span></span>`;
        }).join('');

        pod.style.display = 'flex';
        pod.innerHTML = `
            <div class="vault-live-deploy-header">
                <div class="vault-live-deploy-status-wrap">
                    <span class="vault-live-deploy-badge ${badgeClass}">${badgeText}</span>
                    <span class="vault-live-deploy-code mono" title="批次编号: ${batchId}">${shortId}</span>
                    <span class="vault-live-deploy-dur">⏱️ ${durText}</span>
                </div>
                <button type="button" class="vault-live-deploy-btn-log" onclick="window.openHostingDeployLogDrawer('${batchId}')" title="打开全屏部署控制台流水抽屉">📋 控制台流水</button>
            </div>
            <div class="vault-live-deploy-targets-row">${targetsHtml}</div>
        `;
    }

    // 🚀 [V126.0] 启动抽屉专属部署态势轮询器
    window.startVaultHostingLiveTracking = function (batchId, targetDoc, selectedChannels) {
        window.stopVaultHostingLiveTracking(false);
        _vaultHostingActiveBatchId = batchId;
        _vaultHostingActiveDoc = targetDoc;
        _vaultHostingStartTime = Date.now();

        // 初始立即渲染 RUNNING
        renderLivePodHtml({ batchId, status: 'RUNNING', durationSec: 0, targets: {}, channels: selectedChannels });

        const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url) => (await fetch(url)).json());

        _vaultHostingDeployPoller = setInterval(async () => {
            const curBatchId = _vaultHostingActiveBatchId;
            if (!curBatchId) return;

            const curElapsed = Math.floor((Date.now() - _vaultHostingStartTime) / 1000);

            try {
                const res = await fetchFunc('/api/dispatch/hosting/batch/' + encodeURIComponent(curBatchId));
                const batchData = (res && res.batch) ? res.batch : res;
                if (!batchData || batchData.batch_id !== curBatchId) return;

                const overallStatus = batchData.overall_status || 'RUNNING';
                const dur = batchData.duration_sec != null ? batchData.duration_sec : curElapsed;
                const targets = batchData.targets || {};

                renderLivePodHtml({
                    batchId: curBatchId,
                    status: overallStatus,
                    durationSec: dur,
                    targets: targets,
                    channels: selectedChannels
                });

                if (overallStatus !== 'RUNNING' && overallStatus !== 'PENDING') {
                    // 任务已完成，自动收敛停止轮询
                    window.stopVaultHostingLiveTracking(false);
                    // 恢复主按钮状态
                    const mainBtn = document.querySelector('.sovereign-action-grid .primary-hub-btn');
                    if (mainBtn) {
                        mainBtn.disabled = false;
                        mainBtn.style.opacity = '1';
                        mainBtn.innerHTML = `<span class="btn-icon">🚀</span> 开始全站托管发布 (${selectedChannels.length} 个平台)`;
                    }
                    if (typeof window.refreshVaultDrawerStatus === 'function') {
                        window.refreshVaultDrawerStatus(_vaultHostingActiveDoc);
                    }
                }
            } catch (err) {
                console.warn('[Vault Hosting Tracking] Poll error:', err);
            }
        }, 1500);
    };

    // 🛑 停止抽屉部署态势轮询器
    window.stopVaultHostingLiveTracking = function (clearDom = false) {
        if (_vaultHostingDeployPoller) {
            clearInterval(_vaultHostingDeployPoller);
            _vaultHostingDeployPoller = null;
        }
        if (clearDom) {
            _vaultHostingActiveBatchId = null;
            const pod = document.getElementById('vault-hosting-live-deploy-pod');
            if (pod) {
                pod.style.display = 'none';
                pod.innerHTML = '';
            }
        }
    };

    // 🔄 重置态势卡片（换文档时调用）
    window.resetVaultHostingLivePod = function () {
        window.stopVaultHostingLiveTracking(true);
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

        // 1. 先触发一次全量重新装帧编译（确保当前原稿最新生成并进入 bundle，跳过外部社交分发）
        await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(targetDoc)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ locales: [], force: true, clear_cache: false, skip_syndication: true })
        });

        // 2. 统一调用全站托管发布接口，生成批次与控制台日志流水
        const deployRes = await fetchFunc('/api/dispatch/hosting/deploy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_channels: selectedChannels,
                trigger_source: 'vault_drawer',
                doc_id: targetDoc
            })
        });

        if (deployRes && deployRes.status === 'success') {
            const batchId = deployRes.batch_id;
            // 启动抽屉原地实时部署态势追踪与公网外链呈现
            window.startVaultHostingLiveTracking(batchId, targetDoc, selectedChannels);

            const shortCode = batchId.includes('_') ? '#' + batchId.split('_').pop() : '#' + batchId.slice(-6);
            showToast(`✅ 已启动托管发布 (${shortCode})！`, "success");

            if (typeof window.loadHostingDeployCenter === 'function') window.loadHostingDeployCenter();
            if (typeof window.startHostingDeployPolling === 'function') window.startHostingDeployPolling();
        } else {
            showToast(`⚠️ 托管部署任务提交返回: ${(deployRes && (deployRes.detail || deployRes.message)) || '请查看控制台'}`, "warning");
            if (mainBtn) {
                mainBtn.disabled = false;
                mainBtn.style.opacity = '1';
                mainBtn.innerHTML = `<span class="btn-icon">🚀</span> 开始全站托管发布 (${selectedChannels.length} 个平台)`;
            }
        }

        if (typeof window.safeStartDrawerTimer === 'function') window.safeStartDrawerTimer(targetDoc);
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
