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

        // 同步更新左边栏 1. 原稿文库 实时篇数
        const pipeValVault = document.getElementById('pipe-val-vault');
        if (pipeValVault) {
            pipeValVault.innerText = `${window.vaultTotalItems} 篇原稿`;
        }

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

            // 🚀 [V79.2] 智能降级 Tooltip & Icon
            const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';
            let reviewBtnTitle = '译文校对工作台';
            let reviewBtnIcon = '🌍';
            
            if (pubMode === 'basic') {
                reviewBtnTitle = '译文校对工作台 (基础模式：未启用翻译管线，将透传中文)';
                reviewBtnIcon = '🌐';
            } else if (pubMode === 'enhanced') {
                reviewBtnTitle = '译文校对工作台 (增强模式：AI 仅优化 SEO 元数据)';
                reviewBtnIcon = '📝';
            } else {
                const humanLockedLangs = transLangs.filter(lc => (m.translations[lc] || {}).human_approved);
                const isStale = transLangs.some(lc => (m.translations[lc] || {}).review_is_stale);
                reviewBtnTitle = transLangs.length > 0
                    ? '译文校对工作台'
                    : '译文校对工作台 (未初始化 AI 译文)';
                reviewBtnIcon = humanLockedLangs.length > 0
                    ? (isStale ? '⚠️' : '🔒')
                    : '🌍';
            }
            const escapedRelPath = (m.rel_path || '').replace(/'/g, "\\'");
            const escapedTitle = (m.title || '').replace(/'/g, "\\'");
            const escapedCover = (m.cover || '').replace(/'/g, "\\'");
            const coverThumb = m.cover
                ? `<div class="skeleton-shimmer" style="width:38px; height:24px; border-radius:4px; overflow:hidden; border:1px solid rgba(0,242,254,0.3); background:#05070f; cursor:pointer; flex-shrink:0;" title="点击更换文章封面" onclick="window.openDocCoverPickerModal('${escapedRelPath}', '${escapedTitle}', '${escapedCover}')"><img src="${m.cover}" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='/api/design/assets/default-cover.jpg';" style="width:100%; height:100%; object-fit:cover; transition:transform 0.2s; display:block;" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'" /></div>`
                : `<div style="width:38px; height:24px; border-radius:4px; border:1px dashed rgba(255,255,255,0.18); display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0; background:rgba(255,255,255,0.02); opacity:0.6; font-size:0.7rem;" title="未设封面，点击快速挑选或生成" onclick="window.openDocCoverPickerModal('${escapedRelPath}', '${escapedTitle}', '')">🖼️+</div>`;
            const displayTitle = (m.seo_data && m.seo_data.title && m.seo_data.title !== m.slug) ? m.seo_data.title : (m.title || m.rel_path);
            const escapedDisplayTitle = displayTitle.replace(/'/g, "\\'");
            return `
            <tr>
                <td style="overflow:hidden;">
                    <div style="display:flex; align-items:center; gap:8px; min-width:0;">
                        ${coverThumb}
                        <div style="overflow:hidden; min-width:0; flex:1;">
                            <div style="font-weight:600; color:var(--text-bright); text-overflow:ellipsis; overflow:hidden; white-space:nowrap;" title="${displayTitle}">${displayTitle}</div>
                            ${m.slug && m.slug !== 'null' ? `<div style="font-size:0.7rem; opacity:0.4; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">/${m.slug}</div>` : ''}
                        </div>
                    </div>
                </td>
                <td style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"><code class="path-tag" title="${m.rel_path}">${m.rel_path.length > 40 ? '...' + m.rel_path.slice(-37) : m.rel_path}</code></td>
                <td style="text-align:center;"><span class="mono">${wc.toLocaleString()}</span></td>
                <td style="padding:8px; width:160px; min-width:160px; box-sizing:border-box; text-align:center;">
                    <div class="vault-action-wrapper" style="display:inline-flex; gap:5px; align-items:center; justify-content:center;">
                        <button class="mini-action-btn" title="快速编辑原稿 (Markdown 创作工作台)" onclick="openEditor('${escapedRelPath}')">📝</button>
                        <button class="mini-action-btn" title="实时渲染预览 (独立站真实效果)" onclick="window.openArticleLivePreview('${escapedRelPath}', '${m.slug || ''}')">👁️</button>
                        <button class="mini-action-btn" title="全域渠道分发与推流 (微信 · 知乎 · B站 · Dev.to 等)" onclick="window.openArticleSyndicationDrawer('${escapedRelPath}', '${escapedTitle}')">📢</button>
                        <button class="mini-action-btn vault-more-btn" title="更多操作 (独立站发布 · 译文校对 · 封面管理 · 重命名 · 物理销毁)" onclick="window.toggleVaultActionMenu(this, event)">···</button>
                        <div class="vault-more-menu custom-glass-dropdown">
                            <button class="vault-more-item" onclick="openVaultDrawer('${escapedRelPath}')">🌐 独立站发布与全网遥测</button>
                            <button class="vault-more-item" onclick="window.openTranslationReview('${escapedRelPath}')">${reviewBtnIcon} 多语种译文校对</button>
                            <button class="vault-more-item" onclick="window.openDocCoverPickerModal('${escapedRelPath}', '${escapedTitle}', '${escapedCover}')">🖼️ 更换或生成文章封面</button>
                            <button class="vault-more-item" onclick="window.triggerMoveDocument('${escapedRelPath}')">📤 重命名与分类迁移</button>
                            <div class="vault-more-divider"></div>
                            <button class="vault-more-item danger" onclick="window.triggerDirectDocDelete('${escapedRelPath}', '${escapedTitle}')">🗑️ 物理安全彻底销毁</button>
                        </div>
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

// 📂 [单例控制器] 原稿操作更多下拉菜单（支持底部视口智能反向避让 Dropup）
window.toggleVaultActionMenu = (btn, event) => {
    event.stopPropagation();
    const menu = btn.nextElementSibling;
    const isShow = menu && menu.classList.contains('show');
    document.querySelectorAll('.vault-more-menu.show').forEach(m => m.classList.remove('show'));
    if (!isShow && menu) {
        const rect = btn.getBoundingClientRect();
        const spaceBelow = window.innerHeight - rect.bottom;
        if (spaceBelow < 230) {
            menu.classList.add('dropup');
        } else {
            menu.classList.remove('dropup');
        }
        menu.classList.add('show');
    }
};

if (!window._vaultMenuListenerBound) {
    window._vaultMenuListenerBound = true;
    document.addEventListener('click', () => document.querySelectorAll('.vault-more-menu.show').forEach(m => m.classList.remove('show')));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') document.querySelectorAll('.vault-more-menu.show').forEach(m => m.classList.remove('show')); });
}

// 🚀 [快捷动作算子 1] 实时网页渲染预览
window.openArticleLivePreview = async (relPath, slug) => {
    const previewPort = window.settingsData?.system?.serve_port || 43213;
    let targetUrl = (slug && slug !== 'null' && slug !== 'undefined')
        ? `http://localhost:${previewPort}/${slug.startsWith('/') ? slug.substring(1) : slug}`
        : `http://localhost:${previewPort}/${relPath.replace(/\.md$/, '.html')}`;
    if (typeof window.showToast === 'function') window.showToast(`🌐 正在打开实时预览: ${relPath}`, 'info');
    window.open(targetUrl, '_blank');
};

// 🚀 [快捷动作算子 2] 一键复制文章路径 (兼容桩)
window.copyArticleMagicLink = async (relPath, slug) => {
    const copyText = (slug && slug !== 'null' && slug !== 'undefined') ? (slug.startsWith('/') ? slug : `/${slug}`) : relPath;
    if (navigator.clipboard) await navigator.clipboard.writeText(copyText).catch(() => {});
    if (typeof window.showToast === 'function') window.showToast(`📋 文章路径已复制: ${copyText}`, 'success');
};

// 🚀 [快捷动作算子 3] 单篇原稿安全快速销毁入口
window.triggerDirectDocDelete = (relPath, title) => {
    window.currentDocId = relPath;
    const displayTitle = title || relPath;
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '确认销毁该原稿吗？',
            html: `将物理抹除磁盘源文件 <b>${displayTitle}</b> 及其全网所有出版产物。<br><br><span style="color:#ff6b6b; font-size:0.82rem;">⚠️ 此物理销毁操作不可撤销！</span>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: 'var(--neon-red, #ff4d4f)',
            confirmButtonText: '🔥 确认销毁',
            cancelButtonText: '取消',
            background: 'var(--card-bg)',
            color: 'var(--text-bright)'
        }).then(async (result) => {
            if (result.isConfirmed) {
                if (typeof addAudit === 'function') addAudit(`🗑️ 正在物理销毁资产 [${relPath}]...`, "warning");
                const res = await apiFetch(`/api/vault/destroy/${encodeURIComponent(relPath)}`, { method: 'DELETE' });
                if (res && res.success) {
                    if (typeof window.showToast === 'function') {
                        window.showToast(`🗑️ 原稿 [${displayTitle}] 已物理销毁`, 'success');
                    }
                    if (typeof window.loadVault === 'function') {
                        window.loadVault();
                    }
                } else {
                    const err = res ? res.detail || res.message : '销毁失败';
                    if (typeof window.showToast === 'function') {
                        window.showToast(`❌ 销毁失败: ${err}`, 'error');
                    }
                }
            }
        });
    } else {
        if (confirm(`确认物理销毁 [${displayTitle}] 吗？不可撤销！`)) {
            if (typeof window.confirmPhysicalDelete === 'function') {
                window.confirmPhysicalDelete();
            }
        }
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
