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
    ['vault-first-btn', 'vault-prev-btn', 'vault-next-btn', 'vault-last-btn'].forEach(id => {
        const b = document.getElementById(id); if (b) b.disabled = true;
    });
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
        const isFirst = window.vaultCurrentPage <= 1, isLast = window.vaultCurrentPage >= totalPages;
        const fb = document.getElementById('vault-first-btn'), pb = document.getElementById('vault-prev-btn');
        const nb = document.getElementById('vault-next-btn'), lb = document.getElementById('vault-last-btn');
        if (fb) fb.disabled = isFirst; if (pb) pb.disabled = isFirst;
        if (nb) nb.disabled = isLast; if (lb) lb.disabled = isLast;

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
            const transLangs = Object.keys(m.translations || {});
            const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';
            let reviewBtnTitle = '译文校对工作台', reviewBtnIcon = '🌍';
            if (pubMode === 'basic') {
                reviewBtnTitle = '译文校对工作台 (基础模式：未启用翻译管线，将透传中文)'; reviewBtnIcon = '🌐';
            } else if (pubMode === 'enhanced') {
                reviewBtnTitle = '译文校对工作台 (增强模式：AI 仅优化 SEO 元数据)'; reviewBtnIcon = '📝';
            } else {
                const humanLocked = transLangs.some(lc => (m.translations[lc] || {}).human_approved);
                const isStale = transLangs.some(lc => (m.translations[lc] || {}).review_is_stale);
                reviewBtnTitle = transLangs.length > 0 ? '译文校对工作台' : '译文校对工作台 (未初始化 AI 译文)';
                reviewBtnIcon = humanLocked ? (isStale ? '⚠️' : '🔒') : '🌍';
            }
            const escapedRelPath = (m.rel_path || '').replace(/'/g, "\\'");
            const escapedTitle = (m.title || '').replace(/'/g, "\\'");
            const escapedCover = (m.cover || '').replace(/'/g, "\\'");
            const coverThumb = m.cover
                ? `<div class="skeleton-shimmer" style="width:38px; height:24px; border-radius:4px; overflow:hidden; border:1px solid rgba(0,242,254,0.3); background:#05070f; cursor:pointer; flex-shrink:0;" title="点击更换文章封面" onclick="window.openDocCoverPickerModal('${escapedRelPath}', '${escapedTitle}', '${escapedCover}')"><img src="${m.cover}" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='/api/design/assets/default-cover.jpg';" style="width:100%; height:100%; object-fit:cover; transition:transform 0.2s; display:block;" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'" /></div>`
                : `<div style="width:38px; height:24px; border-radius:4px; border:1px dashed rgba(255,255,255,0.18); display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0; background:rgba(255,255,255,0.02); opacity:0.6; font-size:0.7rem;" title="未设封面，点击快速挑选或生成" onclick="window.openDocCoverPickerModal('${escapedRelPath}', '${escapedTitle}', '')">🖼️+</div>`;
            const displayTitle = (m.seo_data && m.seo_data.title && m.seo_data.title !== m.slug) ? m.seo_data.title : (m.title || m.rel_path);
            const escapedDisplayTitle = displayTitle.replace(/'/g, "\\'");
            const docUrl = (typeof window.resolveDocUrlString === 'function') ? window.resolveDocUrlString(m.rel_path, m.slug) : (m.slug || m.rel_path.replace(/\.(md|markdown)$/i, '.html'));
            const slugHint = (m.slug && m.slug !== 'null' && m.slug !== 'undefined') ? ` (Slug: ${m.slug})` : '';
            return `
            <tr>
                <td style="overflow:hidden;">
                    <div style="display:flex; align-items:center; gap:8px; min-width:0;">
                        ${coverThumb}
                        <div style="overflow:hidden; min-width:0; flex:1;">
                            <div style="font-weight:600; color:var(--text-bright); text-overflow:ellipsis; overflow:hidden; white-space:nowrap;" title="${displayTitle}">${displayTitle}</div>
                            ${docUrl ? `<div style="font-size:0.7rem; opacity:0.45; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; font-family:var(--font-mono, monospace);" title="预估网页路径: /${docUrl}${slugHint}">/${docUrl}</div>` : ''}
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
                            <button class="vault-more-item" onclick="window.quickBindSingleDoc('${escapedRelPath}', '${escapedDisplayTitle}')">⚡ 单篇极速装订 (EPUB / WebBook / PDF)</button>
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
        menu.classList.toggle('dropup', window.innerHeight - rect.bottom < 230);
        menu.classList.add('show');
    }
};

if (!window._vaultMenuListenerBound) {
    window._vaultMenuListenerBound = true;
    document.addEventListener('click', () => document.querySelectorAll('.vault-more-menu.show').forEach(m => m.classList.remove('show')));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') document.querySelectorAll('.vault-more-menu.show').forEach(m => m.classList.remove('show')); });
}

// 🚀 [快捷动作算子 1] 实时网页渲染预览（智能推导路径 + 预览服务在线探针与自动点火唤醒）
window.openArticleLivePreview = async (relPath, slug) => {
    const docUrl = (typeof window.resolveDocUrlString === 'function')
        ? window.resolveDocUrlString(relPath, slug)
        : (relPath.replace(/\.(md|markdown)$/i, '.html'));
    const cleanDocUrl = (docUrl || '').replace(/^\/+/, '');
    let port = window.settingsData?.system?.serve_port || 43213;
    const activeImp = window.settingsData?._active_imprint || 'default';
    const impName = document.getElementById('active-imprint-name')?.innerText?.trim() || (activeImp === 'default' ? '默认品牌 (创作者指南)' : activeImp);
    const themeId = window.settingsData?.active_theme || window.settingsData?._theme || 'default';
    const themeName = (typeof window.getThemeDisplayName === 'function') ? window.getThemeDisplayName(themeId) : themeId;
    const estUrl = `http://localhost:${port}/${cleanDocUrl}`;

    // 1. 同步交互瞬间预先打开新标签页，彻底击穿浏览器异步弹窗拦截 (Popup Blocker)
    const previewTab = window.open('about:blank', '_blank');
    if (previewTab) {
        try {
            previewTab.document.write(`<!DOCTYPE html><html><head><title>正在启动实时预览: ${cleanDocUrl}</title><meta charset="utf-8"><style>body{margin:0;background:#070a12;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;}.card{background:rgba(13,19,33,0.95);border:1px solid rgba(0,242,255,0.3);border-radius:14px;padding:24px 28px;width:480px;max-width:90%;box-shadow:0 20px 50px rgba(0,0,0,0.8),0 0 25px rgba(0,242,255,0.12);}.grid{display:grid;grid-template-columns:84px 1fr;gap:8px 12px;font-size:0.8rem;background:rgba(255,255,255,0.02);padding:12px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);margin:14px 0;}.val{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all;color:#00f2ff;}.dot{width:6px;height:6px;border-radius:50%;background:#00f2ff;box-shadow:0 0 8px #00f2ff;display:inline-block;animation:p 1.2s infinite;}@keyframes p{0%,100%{opacity:0.3;transform:scale(0.8)}50%{opacity:1;transform:scale(1.2)}}</style></head><body><div class="card"><h3 style="margin:0 0 4px 0;color:#00f2ff;font-size:1.15rem;">🚀 正在唤醒实时渲染预览...</h3><p style="margin:0;color:#718096;font-size:0.78rem;">服务点火就绪后将全自动载入页面，请稍候</p><div class="grid"><span style="color:#a0aec0;font-weight:600;">🏛️ 出版品牌</span><span style="color:#f7fafc;">${impName}</span><span style="color:#a0aec0;font-weight:600;">🎨 装帧主题</span><span style="color:#f7fafc;">${themeName}</span><span style="color:#a0aec0;font-weight:600;">📝 原稿路径</span><span class="val" style="color:#f7fafc;">${relPath}</span><span style="color:#a0aec0;font-weight:600;">🌐 预览地址</span><span class="val" id="preview-url-val">${estUrl}</span></div><div style="font-size:0.75rem;color:#00f2ff;display:flex;align-items:center;gap:8px;"><span class="dot"></span><span id="preview-status-tip">正在执行端口探活与服务点火编排...</span></div></div></body></html>`);
            previewTab.document.close();
        } catch (_) {}
    }

    try {
        const st = await apiFetch('/api/system/preview/status');
        if (st && st.port) port = st.port;
        if (!st || !st.is_alive) {
            if (typeof window.showToast === 'function') window.showToast('🚀 预览服务未运行，正在自动点火唤醒...', 'info');
            const rst = await apiFetch('/api/system/preview/restart', { method: 'POST' });
            if (rst && (rst.status === 'success' || rst.port)) {
                if (rst.port) port = rst.port;
                if (typeof window.showToast === 'function') window.showToast('✨ 预览服务已就绪，正在打开页面...', 'success');
                await new Promise(r => setTimeout(r, 600));
            } else {
                throw new Error(rst?.detail || rst?.message || '自动点火启动失败');
            }
        }
    } catch (e) {
        console.warn('⚠️ 预览服务探活/点火警告:', e);
        if (typeof window.showToast === 'function') window.showToast(`⚠️ 预览唤醒提示: ${e.message}`, 'warning');
        if (previewTab && !previewTab.closed) {
            try { previewTab.document.body.innerHTML = `<div style="text-align:center;"><h3 style="color:#ff4d4f;margin-bottom:8px;">❌ 预览服务启动失败</h3><p style="color:#bbb;font-size:13px;margin:0;">${e.message}</p></div>`; } catch (_) {}
        }
    }

    const targetUrl = `http://localhost:${port}/${cleanDocUrl}`;
    if (typeof window.showToast === 'function') window.showToast(`🌐 正在打开实时预览: /${cleanDocUrl}`, 'info');
    if (previewTab && !previewTab.closed) {
        try {
            const uEl = previewTab.document.getElementById('preview-url-val');
            if (uEl) uEl.innerText = targetUrl;
            const tipEl = previewTab.document.getElementById('preview-status-tip');
            if (tipEl) tipEl.innerText = '✨ 渲染服务已就绪，正在跳转呈现...';
        } catch (_) {}
        previewTab.location.href = targetUrl;
    } else {
        window.open(targetUrl, '_blank');
    }
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
            icon: 'warning', showCancelButton: true, confirmButtonColor: 'var(--neon-red, #ff4d4f)', confirmButtonText: '🔥 确认销毁', cancelButtonText: '取消', background: 'var(--card-bg)', color: 'var(--text-bright)'
        }).then(async (result) => {
            if (!result.isConfirmed) return;
            if (typeof addAudit === 'function') addAudit(`🗑️ 正在物理销毁资产 [${relPath}]...`, "warning");
            const res = await apiFetch(`/api/vault/destroy/${encodeURIComponent(relPath)}`, { method: 'DELETE' });
            if (res && res.success) {
                window.showToast?.(`🗑️ 原稿 [${displayTitle}] 已物理销毁`, 'success');
                window.loadVault?.();
            } else {
                window.showToast?.(`❌ 销毁失败: ${res ? res.detail || res.message : '销毁失败'}`, 'error');
            }
        });
    } else if (confirm(`确认物理销毁 [${displayTitle}] 吗？不可撤销！`)) {
        window.confirmPhysicalDelete?.();
    }
};

window.changeVaultPage = (delta) => {
    const totalPages = Math.max(1, Math.ceil(window.vaultTotalItems / window.vaultPageSize));
    const newPage = window.vaultCurrentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) window.loadVault(null, newPage);
};

window.changeVaultPageDirect = (page) => {
    const totalPages = Math.max(1, Math.ceil(window.vaultTotalItems / window.vaultPageSize));
    const targetPage = (page === -1) ? totalPages : page;
    if (targetPage >= 1 && targetPage <= totalPages) window.loadVault(null, targetPage);
};

window.goVaultPage = () => {
    const goInput = document.getElementById('vault-go-page-input');
    if (!goInput) return;
    const val = parseInt(goInput.value, 10);
    const totalPages = Math.max(1, Math.ceil(window.vaultTotalItems / window.vaultPageSize));
    if (isNaN(val) || val < 1 || val > totalPages) {
        window.Swal?.fire({ title: '无效的页码', text: `请输入 1 至 ${totalPages} 之间的有效页码`, icon: 'warning', timer: 2000, showConfirmButton: false });
        return;
    }
    window.loadVault(null, val);
};

window.quickBindSingleDoc = (relPath, title) => {
    document.querySelectorAll('.vault-more-menu.show').forEach(m => m.classList.remove('show'));
    if (typeof window.openBinderyModal === 'function') {
        window.openBinderyModal(`single:${relPath}`, { rel_path: relPath, title: title || relPath });
    } else {
        window.showToast?.('装订模块正在加载中...', 'info');
    }
};
