/**
 * 📡 [V68.0] Illacme Plenipes Vault - Dispatch Drawer & Telemetry Shard
 * 职责：分发枢纽 Drawer 生命周期管理、分发矩阵遥测渲染、重调度操作。
 * 🛡️ [V88.0 Split] 从 dashboard.vault.js 域 B+C (L171-L348) 物理克隆搬迁。
 */

window.closeVaultDrawer = () => {
    document.getElementById('vault-drawer').style.display = 'none';
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
            ? '<span class="btn-icon">♻️</span> 翻译并分发全网' 
            : '<span class="btn-icon">♻️</span> 分发全网';
        reDispatchBtn.title = needsTranslation 
            ? '重新翻译此文章，并在本地重新编译和一键向分发渠道同步' 
            : '在本地重新编译此文章，并一键向已绑定的分发渠道同步更新';
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

        // 🚀 [V89.0] 主权过滤：在 Basic 模式下，保留主语种卡片，并允许展示 Hosting (网页部署) 与 Syndication (分发渠道) 卡片
        const filteredMatrix = pubMode === 'global' 
            ? data.sync_matrix 
            : data.sync_matrix.filter((item, idx) => {
                const code = (item.lang_code || '').toUpperCase();
                return idx === 0 || code === 'HOSTING' || code === 'SYNDICATION';
            });

        matrixContainer.innerHTML = filteredMatrix.map((item, idx) => {
            const codeUpper = (item.lang_code || '').toUpperCase();
            const isHosting = codeUpper === 'HOSTING';
            const isSyndication = codeUpper === 'SYNDICATION';
            const isLocalDoc = !isHosting && !isSyndication;

            const badgeStyle = isHosting 
                ? 'background: rgba(0,242,254,0.12); border: 1px solid rgba(0,242,254,0.25); color: #00f2fe; text-shadow: 0 0 6px rgba(0,242,254,0.3); font-size: 0.6rem;' 
                : isSyndication 
                ? 'background: rgba(187,134,252,0.12); border: 1px solid rgba(187,134,252,0.25); color: #bb86fc; text-shadow: 0 0 6px rgba(187,134,252,0.3); font-size: 0.6rem;' 
                : '';
                
            const showProgress = idx > 0 && !isHosting && !isSyndication && item.cache_info !== '无需翻译 (主权透传)' && 
                (item.progress < 100 || item.status === 'syncing' || item.status === 'pending');

            // 🚀 [V89.6] 自适应发光边线：本地语种显示绿色系，全站托管显示青蓝色系，分发渠道显示紫色系，发生故障时保持红色警示
            let borderLeftStyle = '';
            if (item.status === 'failed') {
                borderLeftStyle = 'border-left: 3px solid var(--neon-red) !important;';
            } else if (isHosting) {
                borderLeftStyle = item.status === 'syncing' 
                    ? 'border-left: 3px solid rgba(0,242,254,0.6) !important;' 
                    : 'border-left: 3px solid #00f2fe !important;';
            } else if (isSyndication) {
                borderLeftStyle = item.status === 'syncing' 
                    ? 'border-left: 3px solid rgba(187,134,252,0.6) !important;' 
                    : 'border-left: 3px solid #bb86fc !important;';
            }

            // 仅对本地文件（非 Hosting、非 Syndication 渠道）附带 local-preview-link class
            let previewClass = isLocalDoc ? 'preview-link local-preview-link' : 'preview-link';

            const statusLower = (item.status || '').toLowerCase();
            const isSuccess = ['published', 'success', 'done', 'synced'].includes(statusLower);
            const hasValidUrl = item.artifact_url && item.artifact_url !== '#' && item.artifact_url !== 'javascript:void(0)';
            const showPreview = isSuccess || hasValidUrl;

            let targetHref = item.artifact_url;
            let previewLabel = '👁️ 预览';
            if (isSyndication) {
                previewLabel = '🔗 浏览';
            } else if (isHosting) {
                previewLabel = '🌐 浏览';
            } else if (isLocalDoc && isLabActive) {
                previewLabel = '⚡ 实时 (LIVE)';
                previewClass += ' live-pulse';
                if (item.live_url && item.live_url !== '#') {
                    targetHref = item.live_url;
                } else if (hasValidUrl) {
                    targetHref = `${labUrl}${item.artifact_url.startsWith('/') ? '' : '/'}${item.artifact_url}`;
                }
            }

            return `
                <div class="matrix-item status-${item.status} ${idx === 0 ? 'source-lang' : 'target-lang'}" style="${borderLeftStyle}">
                    <div class="m-info">
                        <span class="m-locale">
                            ${item.locale}${item.lang_code ? ` <span class="locale-code-badge" style="${badgeStyle}">${item.lang_code}</span>` : ''}
                            ${showPreview && hasValidUrl ? `
                                <a href="${targetHref}" target="_blank" class="${previewClass}" style="margin-top: 0; margin-left: 8px; padding: 2px 8px; font-size: 0.68rem; font-weight: 600; display: inline-flex !important; align-items: center; gap: 4px; vertical-align: middle; color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.35); background: rgba(0, 255, 136, 0.1); border-radius: 4px; text-decoration: none; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 255, 136, 0.25)';" onmouseout="this.style.background='rgba(0, 255, 136, 0.1)';">${previewLabel}</a>
                            ` : ''}
                            ${(isHosting || isSyndication) ? `
                                <a href="javascript:void(0)" onclick="window.triggerChannelDispatch('${relPath}', '${item.channel_id}')" class="sync-channel-btn" style="margin-top: 0; margin-left: 6px; padding: 2px 8px; font-size: 0.68rem; font-weight: 600; display: inline-flex !important; align-items: center; gap: 4px; vertical-align: middle; color: var(--neon-cyan); border: 1px solid rgba(0, 242, 254, 0.3); background: rgba(0, 242, 254, 0.08); border-radius: 4px; text-decoration: none; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 242, 254, 0.25)';" onmouseout="this.style.background='rgba(0, 242, 254, 0.08)';">🔄 同步</a>
                            ` : ''}
                        </span>
                        <span class="m-status-text">${item.status.toUpperCase()}${item.status === 'pending' && item.progress > 0 ? ` (${item.progress}%)` : ''}</span>
                    </div>
                    <div class="m-meta">
                        <span class="m-time">${item.last_sync}</span>
                        ${item.tokens ? `<span class="m-tokens">${item.tokens} tokens</span>` : ''}
                        ${item.cache_info ? `<span class="m-tokens" style="opacity:0.75; margin-left:8px;">${item.cache_info}</span>` : ''}
                    </div>
                    ${item.status === 'failed' ? `
                        <div class="error-msg">${item.reason}</div>
                        ${item.channel_id === 'cloudflare_pages' ? `
                            <div class="deployment-self-healing-tip" style="margin-top: 8px; padding: 10px; background: rgba(0, 242, 254, 0.08); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 6px; font-size: 0.72rem; color: #a5f3fc; line-height: 1.5; text-shadow: 0 0 4px rgba(0, 242, 254, 0.2); text-align: left;">
                                💡 <strong>网络自愈建议</strong>：若本地网络直连 Cloudflare 接口超时，强烈建议您登录 <strong>Cloudflare 控制台</strong>，直接将您的 Pages 项目绑定到当前已成功同步的 <strong>GitHub 仓库</strong>。此后只需本地推送至 GitHub，Cloudflare 将在云端完成自动部署，100% 规避本地网络拦截阻碍。
                            </div>
                        ` : ''}
                    ` : ''}
                    <div class="bottom-progress-bar ${showProgress ? 'active' : ''}">
                        <div class="fill" style="width: ${item.progress}%"></div>
                    </div>
                </div>
            `;
        }).join('');

        // 🚀 [V89.9] 动态控制“一键同步全渠道”按钮的交互状态与用户易理解引导
        const syncAllBtn = document.getElementById('btn-sync-all-channels');
        if (syncAllBtn) {
            const hasChannels = filteredMatrix.some(item => {
                const code = (item.lang_code || '').toUpperCase();
                return code === 'HOSTING' || code === 'SYNDICATION';
            });
            syncAllBtn.style.display = 'block'; // 保持永久展示，向用户明确展示产品的核心分发能力
            if (hasChannels) {
                syncAllBtn.disabled = false;
                syncAllBtn.style.opacity = '1';
                syncAllBtn.style.cursor = 'pointer';
                syncAllBtn.style.background = 'var(--accent-secondary)';
                syncAllBtn.style.color = '#000';
                syncAllBtn.title = "🚀 一键并行同步当前选中的原稿/站点到所有已配置并启用的托管与分发渠道";
            } else {
                syncAllBtn.disabled = true;
                syncAllBtn.style.opacity = '0.5';
                syncAllBtn.style.cursor = 'not-allowed';
                syncAllBtn.style.background = 'rgba(255, 255, 255, 0.08)';
                syncAllBtn.style.color = 'rgba(255, 255, 255, 0.35)';
                syncAllBtn.title = "💡 提示：您当前尚未配置或启用任何网页托管（Hosting）或分发渠道（Syndication）。请先在下方「插件广场」中启用并测试通过任意分发插件，即可解锁一键多渠道分发！";
            }
        }
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
    window.currentDocId = relPath;
    const drawer = document.getElementById('vault-drawer');
    const hubDocId = document.getElementById('hub-doc-id');

    if (hubDocId) hubDocId.innerText = relPath.toUpperCase();
    drawer.style.display = 'flex';
    
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
            btn.innerText = "🔄 同步";
        }
    }
};

// 🚀 [V89.9] 全渠道一键并行同步事件处理器
window.triggerSyncAllChannels = async () => {
    if (!window.currentDocId) return;
    
    // 找出所有同步按钮并并行触发
    const syncBtns = document.querySelectorAll('.sync-channel-btn');
    if (syncBtns.length === 0) {
        showToast("⚠️ 当前未配置或未启用任何全站托管与分发渠道。", "warning");
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
