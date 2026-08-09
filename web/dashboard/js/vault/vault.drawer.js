/**
 * 📡 [V68.0] Illacme Plenipes Vault - Dispatch Drawer & Telemetry Shard
 * 职责：分发枢纽 Drawer 生命周期管理、分发矩阵遥测渲染、重调度操作。
 * 🛡️ [V88.0 Split] 从 dashboard.vault.js 域 B+C (L171-L348) 物理克隆搬迁。
 */

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
// 3. 📡 分发枢纽 (Dispatch Hub) 监控引擎状态刷新器
window.refreshVaultDrawerStatus = async (relPath) => {
    if (!relPath) return false;
    const matrixContainer = document.getElementById('hub-sync-matrix');

    // 🚀 自主预热全域能力矩阵数据，防范直接进入抽屉时 window.allPlugins 尚未加载的竞态断裂
    if (!window.allPlugins || window.allPlugins.length === 0) {
        try {
            const pluginRes = await apiFetch('/api/plugins/list');
            if (pluginRes && pluginRes.plugins) {
                window.allPlugins = pluginRes.plugins;
            }
        } catch (e) {
            console.warn("[Vault Drawer] Autonomous fetch plugin list failed:", e);
        }
    }

    const data = await apiFetch(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
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

        // 🚀 纯净全站托管过滤：彻底剥离社交媒体渠道（集中在专门的社交分发抽屉中），仅保留多语种网页装帧产物与全站托管平台
        const cleanHostingMatrix = (data.sync_matrix || []).filter((item, idx) => {
            const code = (item.lang_code || '').toUpperCase();
            if (code === 'SYNDICATION') return false; // 彻底剥离社媒渠道
            if (pubMode !== 'global' && idx > 0 && code !== 'HOSTING') return false;
            return true;
        });

        // 真实 10 大全站托管平台元数据字典 (与后端 PublisherRegistry 100% 物理对齐)
        const hostingPlatformMetadata = {
            'github_pages': { name: 'GitHub Pages', icon: '🐙', desc: 'GitHub 官方静态网页托管 (Git 自动化部署)' },
            'cloudflare_pages': { name: 'Cloudflare Pages', icon: '⚡', desc: 'Cloudflare 全球边缘 CDN 静态托管加速' },
            'vercel': { name: 'Vercel', icon: '▲', desc: '全球前端云平台 (现代 SSG 极速部署)' },
            'netlify': { name: 'Netlify', icon: '🌐', desc: '专业静态站点托管平台 (全自动 CI/CD)' },
            'firebase': { name: 'FIREBASE', icon: '🌐', desc: '全站静态站点托管发布平台' },
            'sftp': { name: 'SFTP 物理主机', icon: '🖥️', desc: 'Linux / VPS 自建服务器物理部署' },
            'render': { name: 'Render', icon: '🚀', desc: '云端全栈静态站点部署平台' },
            'railway': { name: 'Railway', icon: '🚂', desc: 'Railway 云服务自动化部署 Hook' },
            'zeabur': { name: 'Zeabur', icon: '⚡', desc: '无服务器容器化托管平台' },
            'gitee_pages': { name: 'Gitee Pages', icon: '🔴', desc: '国内 Gitee 代码托管平台 Pages 静态服务' }
        };

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

            // 2. 检测关键配置是否已填入 (例如 repo_url, token, api_token, project_name 等)
            const hasConfiguredKeys = Object.entries(hostingCfg).some(([k, v]) => {
                if (['enabled', 'proxy', 'force_push', 'git_user_name', 'git_user_email', 'branch'].includes(k)) return false;
                return v !== undefined && v !== null && String(v).trim().length > 0;
            });

            const isGloballyEnabled = pluginDef.is_enabled !== false;
            const isBrandInUse = !!(pluginDef.is_in_use || pluginDef.status === 'In-Use' || hostingCfg.enabled === true);

            // 3. 🎯 真正的主权与就绪判定：
            // isReady: 只要插件全局未禁用，且已配置好参数或当前品牌已开启，即为就绪可用（解除 disabled）
            const isReady = isGloballyEnabled && (hasConfiguredKeys || isBrandInUse || !!hostingRecord);

            // isChecked: 严格以插件中心的当前品牌启用默认值 (isBrandInUse) 为准！未在当前品牌启用的默认不勾选！
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

        // 1. 渲染本地多语种静态产物卡片
        const localArtifactsHtml = localDocMatrix.map((item, idx) => {
            let previewClass = 'preview-link local-preview-link';
            const statusLower = (item.status || '').toLowerCase();
            const isSuccess = ['published', 'success', 'done', 'synced'].includes(statusLower);
            const hasValidUrl = item.artifact_url && item.artifact_url !== '#' && item.artifact_url !== 'javascript:void(0)';
            const showPreview = isSuccess || hasValidUrl;

            let targetHref = item.artifact_url;
            let previewLabel = '🌐 网页预览';
            if (isLabActive) {
                previewLabel = '⚡ 实时预览';
                previewClass += ' live-pulse';
                if (item.live_url && item.live_url !== '#') {
                    targetHref = item.live_url;
                } else if (hasValidUrl) {
                    targetHref = `${labUrl}${item.artifact_url.startsWith('/') ? '' : '/'}${item.artifact_url}`;
                }
            }

            let friendlyStatus = '🟢 装帧完成';
            if (item.status === 'pending') friendlyStatus = item.progress > 0 ? `⏳ 发布中 (${item.progress}%)` : '⏳ 待发布';
            else if (item.status === 'syncing') friendlyStatus = '⚡ 正在发布...';
            else if (item.status === 'failed') friendlyStatus = '🔴 装帧异常';

            return `
                <div class="matrix-item status-${item.status} ${idx === 0 ? 'source-lang' : 'target-lang'}" style="margin-bottom: 6px;">
                    <div class="m-info">
                        <span class="m-locale">
                            ${item.locale}${item.lang_code ? ` <span class="locale-code-badge">${item.lang_code}</span>` : ''}
                            ${showPreview && hasValidUrl ? `
                                <a href="${targetHref}" target="_blank" class="${previewClass}" style="margin-top: 0; margin-left: 8px; padding: 2px 8px; font-size: 0.68rem; font-weight: 600; display: inline-flex !important; align-items: center; gap: 4px; vertical-align: middle; color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.35); background: rgba(0, 255, 136, 0.1); border-radius: 4px; text-decoration: none; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 255, 136, 0.25)';" onmouseout="this.style.background='rgba(0, 255, 136, 0.1)';">${previewLabel}</a>
                            ` : ''}
                        </span>
                        <span class="m-status-text">${friendlyStatus}</span>
                    </div>
                    <div class="m-meta">
                        <span class="m-time">${item.last_sync || '本地装帧产物'}</span>
                        ${item.tokens ? `<span class="m-tokens">${item.tokens} tokens</span>` : ''}
                        ${item.cache_info ? `<span class="m-tokens" style="opacity:0.75; margin-left:8px;">${item.cache_info}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        // 2. 渲染全站托管平台管理卡片列表 (与社媒分发抽屉一致的勾选与品牌启用管理模式)
        const hostingCardsHtml = hostingPlatformsList.map(p => {
            const rec = p.record;
            const isFailed = !!(rec && rec.status === 'failed');
            const targetUrl = rec ? rec.artifact_url : null;
            const hasValidUrl = targetUrl && targetUrl !== '#' && targetUrl !== 'javascript:void(0)';

            let statusTagHtml = p.isReady 
                ? (p.isBrandInUse 
                    ? '<span style="font-size: 0.65rem; color: #00ff88; font-weight: 600;">🟢 已启用</span>' 
                    : '<span style="font-size: 0.65rem; color: #f59e0b; font-weight: 600;">🟡 配置就绪 (待启用)</span>')
                : '<span style="font-size: 0.65rem; color: var(--text-dim);">⚪ 待填凭据</span>';
            if (isFailed) statusTagHtml = '<span style="font-size: 0.65rem; color: #ff4d4f; font-weight: 600;">🔴 部署异常</span>';

            return `
                <div class="glass-panel" style="padding: 10px 12px; border-radius: 8px; border: 1px solid ${p.isReady ? (p.isBrandInUse ? 'rgba(0, 255, 136, 0.25)' : 'rgba(0, 242, 254, 0.2)') : 'rgba(255, 255, 255, 0.06)'}; display: flex; flex-direction: column; gap: 8px; opacity: ${p.isReady ? '1' : '0.65'}; background: ${p.isReady ? (p.isBrandInUse ? 'rgba(0, 255, 136, 0.03)' : 'rgba(0, 242, 254, 0.02)') : 'rgba(255, 255, 255, 0.01)'}; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <input type="checkbox" value="${p.id}" class="vault-hosting-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'} onchange="window.updateVaultHostingSelectionCounter()" style="accent-color: var(--accent-secondary); width: 16px; height: 16px; cursor: ${p.isReady ? 'pointer' : 'not-allowed'};">
                            <div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 0.82rem; font-weight: 600; color: ${p.isReady ? '#fff' : 'var(--text-dim)'};">${p.icon} ${p.name}</span>
                                    ${statusTagHtml}
                                </div>
                                <div style="font-size: 0.68rem; color: var(--text-dim);">${p.desc}</div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            ${p.isReady ? `
                                ${hasValidUrl ? `
                                    <a href="${targetUrl}" target="_blank" style="padding: 2px 7px; font-size: 0.65rem; font-weight: 600; color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.35); background: rgba(0, 255, 136, 0.1); border-radius: 4px; text-decoration: none; display: inline-flex; align-items: center; gap: 3px;">🔗 托管站 ↗</a>
                                ` : ''}
                                <button type="button" onclick="window.triggerChannelDispatch('${relPath}', '${p.id}')" title="单独重新发布此平台" style="padding: 2px 7px; font-size: 0.65rem; font-weight: 600; color: var(--neon-cyan); border: 1px solid rgba(0, 242, 254, 0.35); background: rgba(0, 242, 254, 0.08); border-radius: 4px; cursor: pointer;">🔄 发布</button>
                                <button type="button" onclick="window.goToHostingPluginConfig('${p.id}')" title="修改此平台的 Token 密钥或仓库参数" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">⚙️</button>
                            ` : `
                                <button type="button" onclick="window.goToHostingPluginConfig('${p.id}')" title="前往配置并激活此托管平台" style="background: rgba(0, 242, 255, 0.15); border: 1px solid rgba(0, 242, 255, 0.35); color: var(--neon-cyan, #00f2fe); border-radius: 4px; padding: 3px 8px; font-size: 0.68rem; font-weight: 600; cursor: pointer; white-space: nowrap;">⚙️ 去配置/激活</button>
                            `}
                        </div>
                    </div>
                    ${rec && rec.status === 'failed' ? `
                        <div class="error-msg" style="margin-top: 4px;">${rec.reason || '部署超时或凭据无效'}</div>
                    ` : ''}
                </div>
            `;
        }).join('');

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
    document.getElementById('hub-cost').innerText = data.telemetry.total_cost;
    document.getElementById('hub-node').innerText = data.telemetry.node;
    // 🚀 [V68.0] 环境自感应：实验室模式
    const labBadge = document.getElementById('hub-lab-badge');
    const labBtn = document.getElementById('btn-toggle-lab');
    window.isLivePreviewActive = data.environment.is_lab_active;
    if (data.environment.is_lab_active) {
        labBadge.innerText = "ACTIVE (LIVE)";
        labBadge.className = "badge active";
        labBtn.innerText = "🛑 关闭实时预览引擎";
        labBtn.className = "engine-btn stop-mode";
    } else {
        labBadge.innerText = "OFFLINE";
        labBadge.className = "badge";
        labBtn.innerText = "🔌 启动实时预览引擎 (LIVE PREVIEW)";
        labBtn.className = "engine-btn start-mode";
    }

    const auditBadge = document.getElementById('hub-audit-status');
    const auditError = document.getElementById('hub-audit-error');
    if (auditBadge) {
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
            const stillRunning = await window.refreshVaultDrawerStatus(relPath);
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
            const pluginRes = await apiFetch('/api/plugins/list');
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
    const needsLoop = await window.refreshVaultDrawerStatus(relPath);
    
    // 异步返回后校验令牌时效性
    if (window.vaultDrawerCallToken !== myCallToken) {
        console.warn("🔌 [Drawer] 侦测到更有时效性的打开指令，当前过期的初始化任务已安全熔断。");
        return;
    }

    if (needsLoop) {
        window.safeStartDrawerTimer(relPath);
    }
};

window.triggerReDispatch = async (scope, clearCache = false) => {
    if (!window.currentDocId) return;
    
    const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';
    if (clearCache && pubMode !== 'global') {
        const confirmSwitch = await Swal.fire({
            title: '🌐 需要开启全球出版模式',
            html: `强制重新 AI 翻译正文需要将出版模式设置为 <b style="color:var(--accent-secondary);">全球多语言分发模式 (global)</b>。<br/><span style="font-size:0.75rem;color:var(--text-dim);">是否自动将当前出版模式升级为全球模式并立即执行全量重译？</span>`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: '一键升级模式并重译',
            cancelButtonText: '取消',
            background: 'hsla(220, 43%, 7%, 0.98)',
            color: 'var(--text-bright)',
            confirmButtonColor: 'var(--accent-secondary)',
            cancelButtonColor: 'hsla(0, 0%, 27%, 1)'
        });

        if (!confirmSwitch.isConfirmed) return;
        
        // 自动升级模式
        if (window.settingsData && window.settingsData.governance) {
            window.settingsData.governance.publishing_mode = 'global';
        }
        await apiFetch('/api/gov/save-settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: 'modes', config: { publishing_mode: 'global' } })
        });
        window._showToast?.('✨ 已成功自动升级为全球多语言出版模式！', 'success');
    }

    addAudit(`🚀 [Dispatch] 手动触发重调度请求: ${scope} (清除缓存: ${clearCache})`, "info");
    
    const res = await apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(window.currentDocId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locales: scope === 'all' ? [] : [scope], force: true, clear_cache: clearCache, skip_syndication: clearCache })
    });

    if (res && res.success) {
        // 🚀 [V75.6] 即刻将所有目标语种卡片（排除主权透传的"无需翻译"）设为 redispatching 状态
        document.querySelectorAll('.matrix-item.target-lang').forEach(item => {
            const cacheMeta = item.innerHTML;
            if (!cacheMeta.includes('无需翻译')) {
                item.classList.add('redispatching');
            }
        });

        console.info(`✅ [Dispatch] 重调度指令已由管线受理: ${window.currentDocId}`);
        Swal.fire({
            title: '重调度已受理',
            text: res.message,
            icon: 'success',
            toast: true,
            position: 'top-end',
            timer: 3000,
            showConfirmButton: false
        });
        
        window.safeStartDrawerTimer(window.currentDocId);
        
        setTimeout(() => window.refreshVaultDrawerStatus(window.currentDocId), 1000);
    } else {
        const errorMsg = res ? (res.message || res.reason || "未知异常") : "网络连接或系统异常";
        addAudit(`❌ 重调度失败: ${errorMsg}`, "error");
        if (window.Swal) {
            Swal.fire({
                title: '重调度失败',
                text: errorMsg,
                icon: 'error'
            });
        }
    }
};

// 🛡️ [V89.8] 防呆辅助：自愈式 Toast 弹窗渲染器，防止在某些子视图下打断异步链路
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

window.triggerChannelDispatch = async (relPath, channelId) => {
    if (!relPath || !channelId) return;
    
    // 给触发的按钮临时加上加载中样式
    const btn = event?.target;
    if (btn) {
        btn.style.opacity = '0.5';
        btn.innerText = "🔄 同步中...";
    }
    
    showToast(`🔄 正在向渠道 ${channelId} 进行单篇物理同步部署...`, "info");

    const res = await apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_channel: channelId })
    });
    
    if (res && res.success) {
        showToast(`✅ 已向渠道 ${channelId} 完成物理同步部署！`, "success");
        
        // 自动拉起重调度追踪定时器，监控状态变更
        window.safeStartDrawerTimer(relPath);
        
        setTimeout(() => window.refreshVaultDrawerStatus(relPath), 1000);
    } else {
        const errorMsg = res ? (res.message || res.reason || "未知异常") : "网络连接或系统异常";
        showToast(`❌ 渠道同步失败: ${errorMsg}`, "error");
        if (btn) {
            btn.style.opacity = '1';
            btn.innerText = "🔄 发布";
        }
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

    // 1. 先触发一次全量重新装帧编译
    await apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(targetDoc)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locales: [], force: true, clear_cache: false })
    });

    // 2. 并行触发所有已勾选的托管平台推送
    const publishPromises = selectedChannels.map(channelId => {
        return apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(targetDoc)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_channel: channelId })
        });
    });

    await Promise.all(publishPromises);
    showToast(`✅ 已向 ${selectedChannels.length} 个全站托管平台触发同步请求！正在云端部署...`, "success");

    window.safeStartDrawerTimer(targetDoc);
    setTimeout(() => window.refreshVaultDrawerStatus(targetDoc), 1200);
};

// 🚀 [V89.9] 全渠道一键并行同步事件处理器
window.triggerSyncAllChannels = async () => {
    if (!window.currentDocId) return;
    
    // 找出所有同步按钮并并行触发
    const syncBtns = document.querySelectorAll('.sync-channel-btn');
    if (syncBtns.length === 0) {
        showToast("⚠️ 当前未配置或未启用任何全站托管平台。", "warning");
        return;
    }

    showToast(`🚀 正在发起全渠道 (${syncBtns.length} 个) 并行同步中...`, "info");

    const promises = Array.from(syncBtns).map(btn => {
        // 解析 onclick 中的参数
        // onclick 格式如: window.triggerChannelDispatch('relPath', 'channel_id')
        const onclickAttr = btn.getAttribute('onclick') || "";
        const match = onclickAttr.match(/window\.triggerChannelDispatch\('(.*?)',\s*'(.*?)'\)/);
        if (match && match[2]) {
            const channelId = match[2];
            return window.triggerChannelDispatch(window.currentDocId, channelId);
        }
        return Promise.resolve();
    });

    await Promise.all(promises);
    showToast("✅ 全渠道同步请求全部触发成功！正在后台并行推送...", "success");
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
            if (typeof window.showToast === 'function') {
                window.showToast(`⚙️ 请前往「🧩 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
            }
        }
    } else {
        if (typeof window.showToast === 'function') {
            window.showToast(`⚙️ 请前往「🧩 插件中心」配置 [${pluginId.toUpperCase()}]`, 'info');
        }
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

