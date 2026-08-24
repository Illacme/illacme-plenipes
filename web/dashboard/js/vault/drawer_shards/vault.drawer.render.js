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

        // 动态调整 Global Sync Matrix 标题和按钮布局
        const matrixTitle = document.querySelector('.dispatch-hub-panel .sector-header');
        if (matrixTitle) {
            matrixTitle.innerText = pubMode === 'global' ? 'GLOBAL SYNC MATRIX' : 'LOCAL SYNC MATRIX';
        }

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

            // 2. 提取全量托管平台并精准匹配当前品牌启用与就绪状态 (严格 10 个已注册托管平台)
            const exact10HostingKeys = [
                'sftp', 'vercel', 'render', 'railway', 'gitee_pages',
                'github_pages', 'netlify', 'firebase', 'zeabur', 'cloudflare_pages'
            ];

            const hostingPlatformMetadata = window.vaultHostingPlatformMetadata || {};
            const hostingPlugins = (window.allPlugins || []).filter(p => p.category === 'hosting');
            const activeHostingPlugins = hostingPlugins.length > 0
                ? hostingPlugins
                : exact10HostingKeys.map(k => ({
                    id: k,
                    name: hostingPlatformMetadata[k]?.name || k.toUpperCase(),
                    category: 'hosting',
                    is_in_use: false,
                    is_enabled: true
                }));

            const hostingPlatformsList = activeHostingPlugins.map(pluginDef => {
                const key = pluginDef.id;
                const pMeta = hostingPlatformMetadata[key] || { name: pluginDef.name || key.toUpperCase(), icon: '🌐', desc: '全站静态站点托管发布平台' };

                // 查找后端返回的当前平台同步记录
                const hostingRecord = (data.sync_matrix || []).find(item => {
                    const code = (item.lang_code || '').toUpperCase();
                    return code === 'HOSTING' && (item.channel_id === key || (item.locale || '').toLowerCase().includes(key));
                });

                // 1. 获取当前品牌与全局配置对象
                const cfgData = window.settingsData || {};
                const hostingCfg = cfgData.publish_control?.direct_upload?.[key] || pluginDef.cfg || {};

                // 2. 检测关键配置是否已填入
                const hasConfiguredKeys = Object.entries(hostingCfg).some(([k, v]) => {
                    if (['enabled', 'proxy', 'force_push', 'git_user_name', 'git_user_email', 'branch'].includes(k)) return false;
                    return v !== undefined && v !== null && String(v).trim().length > 0;
                });

                const isGloballyEnabled = pluginDef.is_enabled !== false;
                const isBrandInUse = !!(pluginDef.is_in_use || pluginDef.status === 'In-Use' || hostingCfg.enabled === true);

                // 3. 🎯 真正的主权与就绪判定
                const isReady = isGloballyEnabled && (hasConfiguredKeys || isBrandInUse || !!hostingRecord);
                const isChecked = isReady && isBrandInUse;

                return {
                    id: key,
                    name: pMeta.name,
                    icon: pMeta.icon,
                    desc: pMeta.desc,
                    isReady: isReady,
                    isChecked: isChecked,
                    isBrandInUse: isBrandInUse,
                    hasConfiguredKeys: hasConfiguredKeys,
                    record: hostingRecord,
                    status: hostingRecord ? hostingRecord.status : (isReady ? 'ready' : 'unconfigured')
                };
            });

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
                <div style="margin-bottom: 14px;">
                    <div style="font-size: 0.78rem; font-weight: 600; color: var(--accent-primary, #00f2fe); margin-bottom: 6px;">1. 本地多语种装帧产物</div>
                    <div>${localArtifactsHtml}</div>
                </div>

                <!-- 2. 勾选目标全站托管平台 -->
                <div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 0.78rem; font-weight: 600; color: var(--accent-primary, #00f2fe);">2. 勾选目标全站托管平台</span>
                        <span id="vault-hosting-status-badge" style="font-size: 0.68rem; color: ${readyCount > 0 ? '#00ff88' : '#f59e0b'}; font-weight: 600;">
                            ${readyCount > 0 ? `🟢 ${readyCount} 个平台就绪 (当前选中 ${checkedCount} 个)` : '⚠️ 暂无就绪平台，请先激活'}
                        </span>
                    </div>
                    <div>${hostingCardsHtml}</div>
                </div>
            `;

            // 联动更新全站托管勾选计数与按钮使能
            window.updateVaultHostingSelectionCounter = function () {
                const badgeEl = document.getElementById('vault-hosting-status-badge');
                const mainBtn = document.querySelector('.sovereign-action-grid .primary-hub-btn');
                const checkedBoxes = document.querySelectorAll('.vault-hosting-platform-checkbox:checked');
                const currentSelectedCount = checkedBoxes ? checkedBoxes.length : 0;

                if (badgeEl) {
                    badgeEl.innerHTML = readyCount > 0
                        ? `🟢 ${readyCount} 个平台就绪 (当前选中 ${currentSelectedCount} 个)`
                        : '⚠️ 暂无就绪平台，请先激活';
                    badgeEl.style.color = currentSelectedCount > 0 ? '#00ff88' : '#f59e0b';
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
        // 填充遥测数据
        const costEl = document.getElementById('hub-cost');
        if (costEl && data.telemetry) costEl.innerText = data.telemetry.total_cost;
        const nodeEl = document.getElementById('hub-node');
        if (nodeEl && data.telemetry) nodeEl.innerText = data.telemetry.node;
        // 🚀 [V68.0] 环境自感应：实验室模式
        const labBadge = document.getElementById('hub-lab-badge');
        const labBtn = document.getElementById('btn-toggle-lab');
        if (data.environment) {
            window.isLivePreviewActive = data.environment.is_lab_active;
            if (data.environment.is_lab_active) {
                if (labBadge) {
                    labBadge.innerText = "ACTIVE (LIVE)";
                    labBadge.className = "badge active";
                }
                if (labBtn) {
                    labBtn.innerText = "🛑 关闭实时预览引擎";
                    labBtn.className = "engine-btn stop-mode";
                }
            } else {
                if (labBadge) {
                    labBadge.innerText = "OFFLINE";
                    labBadge.className = "badge";
                }
                if (labBtn) {
                    labBtn.innerText = "🔌 启动实时预览引擎 (LIVE PREVIEW)";
                    labBtn.className = "engine-btn start-mode";
                }
            }
        }

        const auditBadge = document.getElementById('hub-audit-status');
        const auditError = document.getElementById('hub-audit-error');
        if (auditBadge && data.telemetry) {
            if (data.telemetry.pipeline && data.telemetry.pipeline.status === 'RUNNING') {
                const pStage = data.telemetry.pipeline.stage || '正在处理分发管线...';
                auditBadge.className = 'pipeline-stage-box';
                auditBadge.innerHTML = `<span class="spinner-gear">⚙️</span> <span id="hub-pipeline-text">${pStage}</span>`;

                // 🚀 [V75.7] 若管线在运行，前端也自动给所有未完成的目标语种卡片继续保持流光呼吸状态
                document.querySelectorAll('.matrix-item.target-lang').forEach(item => {
                    const isMatch = item.innerHTML.includes('无需翻译');
                    const progressText = item.querySelector('.m-status-text')?.innerText || '';
                    const hasFinished = progressText.includes('100%') || item.classList.contains('status-published');
                    if (!isMatch && !hasFinished) {
                        item.classList.add('redispatching');
                    }
                });
            } else {
                if (data.telemetry.last_audit === 'FAIL') {
                    const errMsg = data.telemetry.error_detail || '文档存在格式或资源问题';
                    auditBadge.innerText = `❌ 校验失败：${errMsg}`;
                    auditBadge.className = 'audit-badge fail';
                } else if (data.telemetry.last_audit === 'PASS') {
                    auditBadge.innerText = `✅ 校验通过：文档及资源完整`;
                    auditBadge.className = 'audit-badge pass';
                } else if (data.telemetry.last_audit === 'PENDING') {
                    auditBadge.innerText = `🔍 尚未分发：等待首次发布`;
                    auditBadge.className = 'audit-badge pending';
                } else {
                    auditBadge.innerText = `AUDIT: ${data.telemetry.last_audit}`;
                    auditBadge.className = `audit-badge ${data.telemetry.last_audit ? data.telemetry.last_audit.toLowerCase() : ''}`;
                }
            }
        }
        if (auditError) {
            auditError.style.display = 'none';
        }

        // 🚀 [V89.2] 智能流控自感应：检测是否还有未完工的后台发布与翻译任务
        const pipelineRunning = data.telemetry?.pipeline?.status === 'RUNNING';
        const anySyncing = data.sync_matrix && data.sync_matrix.some(item => {
            const st = (item.status || '').toLowerCase();
            return st === 'syncing';
        });
        return pipelineRunning || anySyncing;
    };
})();
