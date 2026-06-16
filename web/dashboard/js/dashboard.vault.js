/**
 * 📂 [V55.0] Illacme Plenipes Vault & Editor Component Hub
 * 职责：稿件仓库加载调度、分发矩阵遥测，对外进行逻辑控制。
 * 🛡️ [V75.2 Decoupled] 模块化重构：Obsidian 目录树、Markdown 编辑器及磁盘 Ops 已分离至 vault 子目录原子文件中。
 */

// 1. 状态矩阵
window.currentDocId = null;
window.activeDocId = null;
window.vaultSearchTimeout = null;
window.vaultCurrentPage = 1;
window.vaultCurrentQuery = '';
window.vaultPageSize = 20;
window.vaultActiveFolder = '';
window.vaultTreeInitialized = false;

// 2. 稿件仓库加载器
window.loadVault = async (query = null, page = null) => {
    if (query !== null) {
        window.vaultCurrentQuery = query;
        if (page === null) window.vaultCurrentPage = 1; // 新搜索默认回到第一页
    }
    if (page !== null) window.vaultCurrentPage = page;

    // 🚀 [V87.6] 维持侧边栏折叠/展开状态记忆对正
    const sidebar = document.getElementById('vault-tree-sidebar');
    const toggleBtn = document.getElementById('toggle-vault-sidebar-btn');
    if (sidebar && toggleBtn) {
        const wasCollapsed = localStorage.getItem('vaultSidebarCollapsed') === 'true';
        if (wasCollapsed) {
            sidebar.classList.add('collapsed');
            toggleBtn.innerHTML = '📑 展开侧栏';
        } else {
            sidebar.classList.remove('collapsed');
            toggleBtn.innerHTML = '📑 隐藏侧栏';
        }
    }

    if (!window.vaultTreeInitialized) {
        await window.initializeVaultTree();
    }
    const listEl = document.getElementById('vault-list');
    if (!listEl) return;

    // 预更新分页 UI
    const pageInfo = document.getElementById('vault-page-info');
    if (pageInfo) pageInfo.innerText = `第 ${window.vaultCurrentPage} 页`;
    const prevBtn = document.getElementById('vault-prev-btn');
    const nextBtn = document.getElementById('vault-next-btn');
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;
    listEl.innerHTML = Array(5).fill(0).map(() => `
        <tr>
            <td><div class="skeleton" style="width: 140px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 200px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 60px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 80px; height: 30px;"></div></td>
        </tr>
    `).join('');
    try {
        // 🚀 [V74.8] 物理检索：利用后端索引引擎进行全量过滤，带分页与文件夹过滤参数
        const res = await apiFetch(`/api/vault/search?q=${encodeURIComponent(window.vaultCurrentQuery)}&limit=${window.vaultPageSize}&page=${window.vaultCurrentPage}&folder=${encodeURIComponent(window.vaultActiveFolder || '')}&_t=${Date.now()}`);
        
        if (!res || !res.items) {
            listEl.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:2rem; opacity:0.5;">⚠️ 仓库扫描失败，请核验物理链路。</td></tr>';
            return;
        }
        const manuscripts = res.items;

        // 更新分页按钮可用性
        if (prevBtn) prevBtn.disabled = window.vaultCurrentPage <= 1;
        if (nextBtn) nextBtn.disabled = manuscripts.length < window.vaultPageSize;

        if (manuscripts.length === 0) {
            listEl.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:2rem; opacity:0.5;">📭 仓库空空如也，未发现合规稿件。</td></tr>';
            return;
        }
        listEl.innerHTML = manuscripts.map(m => {
            const wc = (m.seo_data && m.seo_data.word_count) ? m.seo_data.word_count : 0;
            // 🆕 [I5] 检测是否存在已翻译语种，仅当有翻译且 AI 算力开启时显示校对按钮（Q5=B）
            const transLangs = Object.keys(m.translations || {});
            const isAiEnabled = !window.governanceContext || 
                               (window.governanceContext.ai && window.governanceContext.ai.status !== 'disabled');
            const hasTranslations = transLangs.length > 0 && isAiEnabled;
            const humanLockedLangs = transLangs.filter(lc => (m.translations[lc] || {}).human_approved);
            const isStale = transLangs.some(lc => (m.translations[lc] || {}).review_is_stale);
            const reviewBtnTitle = transLangs.length > 0
                ? '译文校对工作台'
                : '译文校对工作台 (未初始化 AI 译文)';
            const reviewBtnIcon = humanLockedLangs.length > 0
                ? (isStale ? '⚠️' : '🔒')
                : '🌍';
            return `
            <tr>
                <td><div style="font-weight:600; color:var(--text-bright);">${m.title}</div>${m.slug && m.slug !== 'null' ? `<div style="font-size:0.7rem; opacity:0.4;">/${m.slug}</div>` : ''}</td>
                <td><code class="path-tag" title="${m.rel_path}">${m.rel_path.length > 40 ? '...' + m.rel_path.slice(-37) : m.rel_path}</code></td>
                <td style="text-align: center;"><span class="mono">${wc.toLocaleString()}</span></td>
                <td>
                    <div style="display:flex; gap:8px;">
                        <button class="mini-action-btn" title="快速编辑原稿 (Edit)" onclick="openEditor('${m.rel_path}')">📝</button>
                        <button class="mini-action-btn" title="重命名与移动原稿 (Rename / Relocate)" onclick="window.triggerMoveDocument('${m.rel_path}')">📤</button>
                        ${isAiEnabled ? `<button class="mini-action-btn" title="${reviewBtnTitle}" onclick="window.openTranslationReview('${m.rel_path}')" style="font-size:0.9rem;${transLangs.length === 0 ? ' filter: grayscale(100%); opacity: 0.4;' : ''}">${reviewBtnIcon}</button>` : ''}
                        <button class="mini-action-btn" title="打开分发枢纽与遥测监控 (Dispatch Hub)" onclick="openVaultDrawer('${m.rel_path}')">📡</button>
                    </div>
                </td>
            </tr>
            `;
        }).join('');

    } catch (e) {
        console.error("Vault load error:", e);
        listEl.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:2rem; color:var(--accent-primary);">🚨 物理链路异常: ${e.message}</td></tr>`;
    }
};

window.changeVaultPage = (delta) => {
    const newPage = window.vaultCurrentPage + delta;
    if (newPage < 1) return;
    window.loadVault(null, newPage);
};
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

    // 渲染分发矩阵
    if (matrixContainer) {
        matrixContainer.innerHTML = data.sync_matrix.map((item, idx) => {
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
        // 🚀 [V75.6] 即刻将所有目标语种卡片（排除主权透传的“无需翻译”）设为 redispatching 状态
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
