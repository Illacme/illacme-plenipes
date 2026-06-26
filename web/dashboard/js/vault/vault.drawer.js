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
    if (!relPath) return;
    const matrixContainer = document.getElementById('hub-sync-matrix');

    // 🚀 [V68.0] 请求 Mock 契约接口
    const data = await apiFetch(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
    if (!data) return;

    const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';

    // 动态调整 Global Sync Matrix 标题和按钮布局
    const matrixTitle = document.querySelector('.dispatch-hub-panel .sector-header');
    if (matrixTitle) {
        matrixTitle.innerText = pubMode === 'global' ? 'GLOBAL SYNC MATRIX' : 'LOCAL SYNC MATRIX';
    }

    const reDispatchBtn = document.querySelector('.sovereign-action-grid button[onclick*="triggerReDispatch(\'all\', false)"]');
    const forceReTranslateBtn = document.querySelector('.sovereign-action-grid button[onclick*="triggerReDispatch(\'all\', true)"]');
    
    if (reDispatchBtn) {
        reDispatchBtn.innerHTML = pubMode === 'global' 
            ? '<span class="btn-icon">♻️</span> 重新分发' 
            : '<span class="btn-icon">♻️</span> 重新物理发布';
        reDispatchBtn.title = pubMode === 'global' 
            ? '对当前文档执行多语种重新分发（复用段落翻译缓存）' 
            : '重新编译并发布此原稿';
    }
    if (forceReTranslateBtn) {
        forceReTranslateBtn.style.display = pubMode === 'global' ? 'flex' : 'none';
        const actionGrid = document.querySelector('.sovereign-action-grid');
        if (actionGrid) {
            actionGrid.style.gridTemplateColumns = pubMode === 'global' ? '1fr 1fr' : '1fr';
            const deleteBtn = document.querySelector('.sovereign-action-grid button[onclick*="confirmPhysicalDelete()"]');
            if (deleteBtn) {
                deleteBtn.style.gridColumn = pubMode === 'global' ? 'span 2' : 'span 1';
            }
        }
    }

    // 渲染分发矩阵
    if (matrixContainer) {
        const filteredMatrix = pubMode === 'global' 
            ? data.sync_matrix 
            : data.sync_matrix.filter((item, idx) => idx === 0);

        matrixContainer.innerHTML = filteredMatrix.map((item, idx) => {
            const showProgress = idx > 0 && item.cache_info !== '无需翻译 (主权透传)' && 
                (item.progress < 100 || item.status === 'syncing' || item.status === 'pending');
            return `
                <div class="matrix-item status-${item.status} ${idx === 0 ? 'source-lang' : 'target-lang'}">
                    <div class="m-info">
                        <span class="m-locale">
                            ${item.locale}${item.lang_code ? ` <span class="locale-code-badge">${item.lang_code}</span>` : ''}
                            ${item.status === 'published' ? `
                                <a href="${item.artifact_url}" target="_blank" class="preview-link" style="margin-top: 0; margin-left: 8px; padding: 1px 6px; font-size: 0.65rem; display: inline-flex !important; vertical-align: middle;">👁️ 预览</a>
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
                    ` : ''}
                    <div class="bottom-progress-bar ${showProgress ? 'active' : ''}">
                        <div class="fill" style="width: ${item.progress}%"></div>
                    </div>
                </div>
            `;
        }).join('');
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
        // 升级所有预览链接为 Live 模式
        document.querySelectorAll('.preview-link').forEach(link => {
            link.innerText = "⚡ 实时 (LIVE)";
            link.classList.add('live-pulse');
        });
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
};
window.openVaultDrawer = async (relPath) => {
    window.currentDocId = relPath;
    const drawer = document.getElementById('vault-drawer');
    const hubDocId = document.getElementById('hub-doc-id');

    if (hubDocId) hubDocId.innerText = relPath.toUpperCase();
    drawer.style.display = 'flex';
    // 🚀 [V75.3] 每次打开前，先物理销毁可能残留的旧定时器
    if (window.vaultDrawerTimer) {
        clearInterval(window.vaultDrawerTimer);
        window.vaultDrawerTimer = null;
    }
    // 立即执行一次获取与渲染
    await window.refreshVaultDrawerStatus(relPath);
    // 启动定时刷新，实时更新各语种的完成进度
    window.vaultDrawerTimer = setInterval(async () => {
        if (drawer && drawer.style.display !== 'none' && window.currentDocId === relPath) {
            await window.refreshVaultDrawerStatus(relPath);
        } else {
            clearInterval(window.vaultDrawerTimer);
            window.vaultDrawerTimer = null;
        }
    }, 2000);
};
window.triggerReDispatch = async (scope, clearCache = false) => {
    if (!window.currentDocId) return;
    addAudit(`🚀 [Dispatch] 手动触发重调度请求: ${scope} (清除缓存: ${clearCache})`, "info");
    
    const res = await apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(window.currentDocId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locales: scope === 'all' ? [] : [scope], force: true, clear_cache: clearCache })
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
        // 🚀 [V75.3] 立即手动触发一次刷新，提供即时状态反馈
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
