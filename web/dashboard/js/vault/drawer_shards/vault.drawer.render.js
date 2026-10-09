/**
 * 📡 [V68.0] Illacme Plenipes Vault - Dispatch Matrix & Telemetry Render Shard
 * 职责：分发枢纽状态拉取、动态按钮与模式适配、遥测数据与审计状态填充、分发矩阵组装。
 */

(function () {
    // 3. 📡 分发枢纽 (Dispatch Hub) 监控引擎状态刷新器
    window.refreshVaultDrawerStatus = async (relPath) => {
        if (!relPath) return false;
        const matrixContainer = document.getElementById('hub-sync-matrix');

        // 🚀 自主预热全域能力矩阵数据，防范直接进入抽屉时 window.allPlugins 尚未加载的竞态断裂
        if (!window.allPlugins || window.allPlugins.length === 0) {
            try {
                const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url) => (await fetch(url)).json());
                const pluginRes = await fetchFunc('/api/plugins/list');
                if (pluginRes && pluginRes.plugins) {
                    window.allPlugins = pluginRes.plugins;
                }
            } catch (e) {
                console.warn("[Vault Drawer] Autonomous fetch plugin list failed:", e);
            }
        }

        const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url) => (await fetch(url)).json());
        const data = await fetchFunc(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
        if (!data) return false;

        const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';


        const reDispatchBtn = document.querySelector('.sovereign-action-grid .primary-hub-btn');
        const forceReTranslateBtn = document.querySelector('.sovereign-action-grid .warning-hub-btn');

        // 🚀 [V89.1] 动态感应：只有在全局多语种模式且确实存在需要 AI 翻译的目标语种时，才提示“翻译并分发”及显示“强制重译”
        const needsTranslation = pubMode === 'global' && data.sync_matrix && data.sync_matrix.some((item, idx) => {
            const code = (item.lang_code || '').toUpperCase();
            return idx > 0 && code !== 'HOSTING' && code !== 'SYNDICATION' && item.cache_info !== '无需翻译 (主权透传)';
        });

        if (reDispatchBtn) {
            reDispatchBtn.innerHTML = needsTranslation
                ? '<span class="btn-icon">♻️</span> 翻译并发布全站'
                : '<span class="btn-icon">♻️</span> 重新发布全站';
            reDispatchBtn.title = needsTranslation
                ? '重新翻译此文章，并在本地重新编译和一键发布全站托管'
                : '在本地重新编译此文章，并一键发布全站托管更新';
        }
        if (forceReTranslateBtn) {
            if (pubMode === 'global' && needsTranslation) {
                forceReTranslateBtn.style.setProperty('display', 'inline-flex', 'important');
            } else {
                forceReTranslateBtn.style.setProperty('display', 'none', 'important');
            }
        }

        // 渲染分发矩阵
        if (matrixContainer) {
            const isLabActive = !!(data.environment && data.environment.is_lab_active);
            const labUrl = (data.environment && data.environment.lab_url) || 'http://localhost:43213';

            // 1. 本地多语种装帧产物
            const localDocMatrix = (data.sync_matrix || []).filter(item => {
                const code = (item.lang_code || '').toUpperCase();
                return code !== 'HOSTING' && code !== 'SYNDICATION';
            });

            // 2. 动态从插件中心统一提取全量托管平台驱动 (SSOT 物理对齐，杜绝四处硬编码)
            const hostingPlugins = (window.allPlugins || []).filter(p => p.category === 'hosting');

            const hostingPlatformsList = hostingPlugins.map(pluginDef => {
                const key = pluginDef.id;
                const pMeta = (typeof window.getVaultHostingMeta === 'function')
                    ? window.getVaultHostingMeta(key)
                    : { name: pluginDef.name, icon: pluginDef.icon || '🌐', desc: pluginDef.description || '全站静态站点托管发布平台' };

                // 查找后端返回的当前平台同步记录
                const hostingRecord = (data.sync_matrix || []).find(item => {
                    const code = (item.lang_code || '').toUpperCase();
                    return code === 'HOSTING' && (item.channel_id === key || (item.locale || '').toLowerCase().includes(key));
                });

                // 1. 获取当前品牌与全局配置对象 (以插件中心 pluginDef.cfg 为基准合并品牌配置)
                const cfgData = window.settingsData || {};
                const hostingCfg = cfgData.publish_control?.direct_upload?.[key] || pluginDef.cfg || {};

                // 2. 🎯 核心对齐：调用插件中心统一凭据状态中央判决算子 (SSOT)
                const credState = (typeof window.isPluginCredentialReady === 'function')
                    ? window.isPluginCredentialReady(key, 'hosting', hostingCfg)
                    : { ready: false, mode: 'missing', label: '待填凭据' };

                const isGloballyEnabled = pluginDef.is_enabled !== false;
                const isBrandInUse = !!(pluginDef.is_in_use || pluginDef.status === 'In-Use' || hostingCfg.enabled === true);

                // 3. 🎯 真正的主权就绪判定：全局已启用 且 凭据算子断言真实就绪
                const isReady = isGloballyEnabled && Boolean(credState && credState.ready);
                const isChecked = isReady && isBrandInUse;

                return {
                    id: key,
                    name: pMeta.name || pluginDef.name,
                    icon: pMeta.icon || pluginDef.icon || '🌐',
                    desc: pMeta.desc || pluginDef.description || '',
                    isReady: isReady,
                    isChecked: isChecked,
                    isBrandInUse: isBrandInUse,
                    credState: credState,
                    credLabel: credState ? credState.label : '待填凭据',
                    record: hostingRecord,
                    status: hostingRecord ? hostingRecord.status : (isReady ? 'ready' : 'unconfigured')
                };
            });

            const priId = (window.settingsData?.publish_control?.primary_hosting_id || window.settingsData?.publish_control?.direct_upload?.primary_hosting_id || '').toLowerCase();
            hostingPlatformsList.forEach(p => { p.isPrimary = Boolean(priId && p.id.toLowerCase() === priId); });
            hostingPlatformsList.sort((a, b) => (a.isPrimary && !b.isPrimary ? -1 : (!a.isPrimary && b.isPrimary ? 1 : (a.isBrandInUse && !b.isBrandInUse ? -1 : (!a.isBrandInUse && b.isBrandInUse ? 1 : 0)))));

            const readyCount = hostingPlatformsList.filter(p => p.isReady).length;
            const checkedCount = hostingPlatformsList.filter(p => p.isChecked).length;

            const localArtifactsHtml = typeof window.renderVaultLocalArtifactsHtml === 'function'
                ? window.renderVaultLocalArtifactsHtml(localDocMatrix, isLabActive, labUrl)
                : '';

            const hostingCardsHtml = typeof window.renderVaultHostingCardsHtml === 'function'
                ? window.renderVaultHostingCardsHtml(hostingPlatformsList, relPath)
                : '';

            matrixContainer.innerHTML = `
                <!-- 1. 本地多语种装帧产物 -->
                <div class="hub-section-block">
                    <div class="vault-subsector-header">
                        <span class="vault-subsector-title">1. 本地多语种装帧产物</span>
                    </div>
                    <div>${localArtifactsHtml}</div>
                </div>

                <!-- 2. 勾选目标全站托管平台 -->
                <div class="hub-section-block">
                    <div class="vault-subsector-header">
                        <span class="vault-subsector-title">2. 勾选目标全站托管平台</span>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            ${readyCount > 0 ? `
                                <button type="button" class="vault-select-all-btn" id="btn-vault-select-all" onclick="window.toggleVaultHostingSelectAll()">
                                    ${checkedCount === readyCount && readyCount > 0 ? '取消全选' : '一键全选'}
                                </button>
                            ` : ''}
                            <span id="vault-hosting-status-badge" class="${readyCount > 0 ? 'hosting-status-badge--ready' : 'hosting-status-badge--empty'} vault-subsector-badge">
                                ${readyCount > 0 ? `🟢 ${readyCount} 个平台就绪 (已选 ${checkedCount})` : '⚠️ 暂无就绪平台，请先激活'}
                            </span>
                        </div>
                    </div>
                    <div>${hostingCardsHtml}</div>
                </div>
            `;

            // 全选 / 取消全选快捷操作
            window.toggleVaultHostingSelectAll = function () {
                const checkableBoxes = document.querySelectorAll('.vault-hosting-platform-checkbox:not(:disabled)');
                if (!checkableBoxes || checkableBoxes.length === 0) return;
                const allChecked = Array.from(checkableBoxes).every(cb => cb.checked);
                checkableBoxes.forEach(cb => {
                    cb.checked = !allChecked;
                });
                window.updateVaultHostingSelectionCounter();
            };

            // 联动更新全站托管勾选计数与按钮使能
            window.updateVaultHostingSelectionCounter = function () {
                const badgeEl = document.getElementById('vault-hosting-status-badge');
                const selectAllBtn = document.getElementById('btn-vault-select-all');
                const mainBtn = document.querySelector('.sovereign-action-grid .primary-hub-btn');
                const checkableBoxes = document.querySelectorAll('.vault-hosting-platform-checkbox:not(:disabled)');
                const checkedBoxes = document.querySelectorAll('.vault-hosting-platform-checkbox:checked');
                const currentSelectedCount = checkedBoxes ? checkedBoxes.length : 0;
                const totalReady = checkableBoxes ? checkableBoxes.length : readyCount;

                if (selectAllBtn) {
                    selectAllBtn.innerText = currentSelectedCount > 0 && currentSelectedCount === totalReady ? '取消全选' : '一键全选';
                }

                if (badgeEl) {
                    badgeEl.innerHTML = totalReady > 0
                        ? `🟢 ${totalReady} 个平台就绪 (已选 ${currentSelectedCount})`
                        : '⚠️ 暂无就绪平台，请先激活';
                    badgeEl.className = currentSelectedCount > 0 ? 'hosting-status-badge--ready vault-subsector-badge' : 'hosting-status-badge--empty vault-subsector-badge';
                }

                if (mainBtn) {
                    if (currentSelectedCount > 0) {
                        mainBtn.disabled = false;
                        mainBtn.style.opacity = '1';
                        mainBtn.style.cursor = 'pointer';
                        mainBtn.innerHTML = `<span class="btn-icon">🚀</span> 开始全站托管发布 (${currentSelectedCount} 个平台)`;
                    } else {
                        mainBtn.disabled = true;
                        mainBtn.style.opacity = '0.5';
                        mainBtn.style.cursor = 'not-allowed';
                        mainBtn.innerHTML = `<span class="btn-icon">🚀</span> 开始全站托管发布 (请先勾选)`;
                    }
                }
            };

            window.updateVaultHostingSelectionCounter();
        }
        // 🚀 [V89.2] 智能流控自感应：检测是否还有未完工的后台发布与翻译任务
        const pipelineRunning = data.telemetry?.pipeline?.status === 'RUNNING';
        if (pipelineRunning) {
            // 管线在后台运行中，保持未完成语种卡片的流光呼吸状态
            document.querySelectorAll('.matrix-item.target-lang').forEach(item => {
                const isMatch = item.innerHTML.includes('无需翻译');
                const progressText = item.querySelector('.m-status-text')?.innerText || '';
                const hasFinished = progressText.includes('100%') || item.classList.contains('status-published');
                if (!isMatch && !hasFinished) {
                    item.classList.add('redispatching');
                }
            });
        }

        if (data.environment) {
            window.isLivePreviewActive = Boolean(data.environment.is_lab_active);
        }

        const anySyncing = data.sync_matrix && data.sync_matrix.some(item => {
            const st = (item.status || '').toLowerCase();
            return st === 'syncing';
        });
        return pipelineRunning || anySyncing;
    };
})();
