/**
 * 📂 [V55.0] Illacme Plenipes Vault - List & Pagination Shard
 * 职责：稿件仓库列表加载与分页控制逻辑。
 * 🛡️ [V88.0 Split] 从 dashboard.vault.js 域 A (L19-L170) 物理克隆搬迁。
 */

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
    const firstBtn = document.getElementById('vault-first-btn');
    const prevBtn = document.getElementById('vault-prev-btn');
    const nextBtn = document.getElementById('vault-next-btn');
    const lastBtn = document.getElementById('vault-last-btn');
    if (firstBtn) firstBtn.disabled = true;
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;
    if (lastBtn) lastBtn.disabled = true;
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

        window.vaultTotalItems = res.total || 0;
        const totalPages = Math.max(1, Math.ceil(window.vaultTotalItems / window.vaultPageSize));

        // 更新分页信息和按钮可用性
        if (pageInfo) {
            pageInfo.innerText = `第 ${window.vaultCurrentPage} / ${totalPages} 页 (共 ${window.vaultTotalItems} 条原稿)`;
        }
        if (firstBtn) firstBtn.disabled = window.vaultCurrentPage <= 1;
        if (prevBtn) prevBtn.disabled = window.vaultCurrentPage <= 1;
        if (nextBtn) nextBtn.disabled = window.vaultCurrentPage >= totalPages;
        if (lastBtn) lastBtn.disabled = window.vaultCurrentPage >= totalPages;

        const goInput = document.getElementById('vault-go-page-input');
        if (goInput) {
            goInput.max = totalPages;
            goInput.value = window.vaultCurrentPage;
        }

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
    const totalPages = Math.max(1, Math.ceil(window.vaultTotalItems / window.vaultPageSize));
    const newPage = window.vaultCurrentPage + delta;
    if (newPage < 1 || newPage > totalPages) return;
    window.loadVault(null, newPage);
};

window.changeVaultPageDirect = (page) => {
    const totalPages = Math.max(1, Math.ceil(window.vaultTotalItems / window.vaultPageSize));
    let targetPage = page;
    if (page === -1) {
        targetPage = totalPages; // 尾页
    }
    if (targetPage < 1 || targetPage > totalPages) return;
    window.loadVault(null, targetPage);
};

window.goVaultPage = () => {
    const goInput = document.getElementById('vault-go-page-input');
    if (!goInput) return;
    const val = parseInt(goInput.value, 10);
    const totalPages = Math.max(1, Math.ceil(window.vaultTotalItems / window.vaultPageSize));
    if (isNaN(val) || val < 1 || val > totalPages) {
        if (window.Swal) {
            Swal.fire({
                title: '无效的页码',
                text: `请输入 1 至 ${totalPages} 之间的有效页码`,
                icon: 'warning',
                timer: 2000,
                showConfirmButton: false
            });
        }
        return;
    }
    window.loadVault(null, val);
};
