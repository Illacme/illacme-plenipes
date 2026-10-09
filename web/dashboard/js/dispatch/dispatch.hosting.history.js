/**
 * 📜 [V125.3] Illacme Plenipes - Hosting Deploy History & Pagination Controller
 * 职责：负责网站发布历史记录表格渲染、物理分页切换、页容量调整及状态联动。
 * 🛡️ [SOP-02 模块规范] 单文件严格保持在 300 行以内。
 */

window._hostingHistoryCurrentPage = 1;
window._hostingHistoryPageSize = 10;
window._hostingHistoryTotal = 0;
window._hostingHistoryTotalPages = 1;

/**
 * 战区三：渲染网站发布历史记录表格与分页控制器
 */
window.renderHostingBatchLedger = function (batches, pagination = null) {
    const box = document.getElementById('hosting-batch-container');
    if (!box) return;

    if (pagination && typeof pagination === 'object') {
        window._hostingHistoryCurrentPage = pagination.page || 1;
        window._hostingHistoryPageSize = pagination.page_size || 10;
        window._hostingHistoryTotal = pagination.total || 0;
        window._hostingHistoryTotalPages = Math.max(1, pagination.total_pages || 1);
    }

    if (!Array.isArray(batches) || batches.length === 0) {
        box.innerHTML = `
            <div style="padding: 36px 16px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
                <span style="font-size: 1.6rem; display: block; margin-bottom: 8px; opacity: 0.6;">📜</span>
                暂无网站发布历史记录，点击上方「立即发布」即可发起发布。
            </div>`;
        return;
    }

    const statusMap = {
        'SUCCESS': { label: '✅ 成功', cls: 'badge-success' },
        'PARTIAL_SUCCESS': { label: '⚠️ 部分成功', cls: 'badge-warning' },
        'RUNNING': { label: '⏳ 发布中', cls: 'badge-running' },
        'FAILED': { label: '❌ 失败', cls: 'badge-failed' },
        'PENDING': { label: '⏸️ 待命', cls: 'badge-idle' }
    };
    const platformNames = {
        github_pages: 'GitHub Pages', vercel: 'Vercel', cloudflare_pages: 'Cloudflare Pages',
        cloudflare: 'Cloudflare Pages', netlify: 'Netlify', firebase_hosting: 'Firebase Hosting',
        supabase_storage: 'Supabase Storage', render: 'Render', railway: 'Railway',
        gitlab_pages: 'GitLab Pages', gitee_pages: 'Gitee Pages', s3_compatible: 'S3 存储'
    };

    const rowsHtml = batches.map(b => {
        const st = statusMap[b.overall_status] || { label: b.overall_status || '未知', cls: 'badge-idle' };
        const rawId = b.batch_id || '';
        const shortId = rawId.includes('_') ? '#' + rawId.split('_').pop() : (rawId ? '#' + rawId.slice(-6) : '--');
        const timeFmt = (b.started_at || '--').replace(/^\d{4}-/, '');
        const sizeText = b.bundle_size_kb != null
            ? (b.bundle_size_kb < 1024 ? `${Number(b.bundle_size_kb).toFixed(1)} KB` : `${(b.bundle_size_kb / 1024).toFixed(1)} MB`)
            : '--';
        const theme = (window.getThemeDisplayName ? window.getThemeDisplayName(b.theme) : b.theme) || 'Sovereign';
        const pagesVal = b.pages_count ?? 0;
        const targets = b.targets || {};
        const priId = (window.settingsData?.publish_control?.primary_hosting_id || window.settingsData?.publish_control?.direct_upload?.primary_hosting_id || window._primaryHostingId || 'github_pages').toLowerCase();
        const targetKeys = Object.keys(targets).filter(k => !k.startsWith('_')).sort((a, b) => (a.toLowerCase() === priId ? -1 : (b.toLowerCase() === priId ? 1 : 0)));
        const docId = b.doc_id || (b.trigger_source && b.trigger_source.startsWith('vault_drawer:') ? b.trigger_source.split('vault_drawer:')[1] : (targets._trigger_doc || null));
        const pagesTip = docId ? (pagesVal > 1 ? `原稿 [${docId}] 编译生成 ${pagesVal} 个网页 (含多语言版本)` : `原稿 [${docId}] 发布页面 (1 页)`) : `编译生成 ${pagesVal} 个网页产物`;
        const esc = window.escapeHtml || (s => s);
        const docTitle = b.doc_title || (docId ? docId.split('/').pop().replace(/\.md$/i, '') : '');
        const scopeIcon = docId
            ? `<span class="hosting-scope-icon doc" title="📄 单篇发布: ${esc(docTitle || docId)}\n原稿: ${esc(docId)}\n(点击查看该文档部署流水)" onclick="event.stopPropagation(); window.openHostingDeployLogDrawer('${rawId}');">📄</span>`
            : `<span class="hosting-scope-icon site" title="🌐 全站发布 (整站所有页面与全域索引)" onclick="event.stopPropagation(); window.openHostingDeployLogDrawer('${rawId}');">🌐</span>`;
        let tagsHtml = `<span class="target-res-tag muted">全部平台</span>`;
        if (targetKeys.length > 0) {
            tagsHtml = targetKeys.map(k => {
                const item = targets[k] || {};
                const flt = (window._lastHostingOverview?.fleet || []).find(f => f && f.id === k);
                const name = flt?.name || platformNames[k] || k;
                const rawUrl = item.url || (item.status === 'SUCCESS' ? flt?.site_url : '') || '';
                const cls = item.status === 'SUCCESS' ? 'ok' : 'err';
                const hasUrl = Boolean(rawUrl && (rawUrl.startsWith('http://') || rawUrl.startsWith('https://')));
                if (hasUrl) {
                    const tip = docId
                        ? `📄 ${name} 原稿文章公网地址:\n${rawUrl}\n点击直接打开该文章页面`
                        : `🌐 ${name} 主站公网地址:\n${rawUrl}\n点击直接打开站点`;
                    return `<a href="${esc(rawUrl)}" target="_blank" rel="noopener noreferrer" class="target-res-tag ${cls}" title="${esc(tip)}" onclick="event.stopPropagation();">${esc(name)} <span class="tag-link-arrow">↗</span></a>`;
                }
                const tip = item.error ? `${name} 失败: ${item.error}` : (item.url || name);
                return `<span class="target-res-tag ${cls}" title="${esc(tip)}">${esc(name)}</span>`;
            }).join(' ');
        }

        const redeployTitle = targetKeys.length === 1
            ? (docId ? `重新发布该文档至 ${targetKeys[0]}` : `重新发布整站至 ${targetKeys[0]}`)
            : (docId ? `重新发布该文档至所有渠道` : `重新发布整站至所有渠道`);

        return `
            <tr class="ledger-row">
                <td class="col-id">
                    <div style="display: inline-flex; align-items: center; justify-content: center; gap: 5px; white-space: nowrap;">
                        ${scopeIcon}
                        <span class="batch-short-code" title="批次编号: ${rawId} (点击查看日志)" onclick="window.openHostingDeployLogDrawer('${rawId}');">${shortId}</span>
                    </div>
                </td>
                <td class="col-time" style="font-size: 0.76rem; color: var(--text-main); white-space: nowrap;" title="${b.started_at || ''}">${timeFmt}</td>
                <td class="col-theme" style="font-size: 0.76rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="装帧主题: ${theme}">🎨 ${window.escapeHtml ? window.escapeHtml(theme) : theme}</td>
                <td class="col-pages" style="font-size: 0.76rem; white-space: nowrap;" title="${pagesTip}"><strong>${pagesVal} 页</strong></td>
                <td class="col-size" style="font-size: 0.76rem; color: var(--text-muted); white-space: nowrap;">${sizeText}</td>
                <td class="col-status"><span class="ledger-badge ${st.cls}">${st.label}</span></td>
                <td class="col-duration" style="font-size: 0.76rem; color: var(--text-muted); white-space: nowrap; text-align: center;">${b.duration_sec != null ? `${Math.round(b.duration_sec)}s` : '--'}</td>
                <td class="col-targets"><div style="display: flex; gap: 4px; flex-wrap: wrap; align-items: center; justify-content: center;">${tagsHtml}</div></td>
                <td class="col-actions" style="text-align: center; white-space: nowrap;"><div style="display: inline-flex; gap: 5px; justify-content: center; align-items: center;"><button type="button" class="hosting-action-icon-btn" onclick="window.openHostingDeployLogDrawer('${rawId}');" title="查看部署流水与控制台日志">📋</button><button type="button" class="hosting-action-icon-btn" onclick="window.triggerFullHostingDeploy(${targetKeys.length === 1 ? `'${targetKeys[0]}'` : 'null'}, { isRedeploy: true, docId: ${docId ? `'${docId}'` : 'null'} });" title="${esc(redeployTitle)}">🔄</button></div></td>
            </tr>`;
    }).join('');

    const curPage = window._hostingHistoryCurrentPage;
    const totPages = window._hostingHistoryTotalPages;
    const totItems = window._hostingHistoryTotal;
    const curSize = window._hostingHistoryPageSize;

    const isFirst = curPage <= 1;
    const isLast = curPage >= totPages;

    const paginationHtml = `
        <div class="pagination-container dispatch-ledger-pagination hosting-history-pagination">
            <div class="ledger-pag-meta">
                <span>第 <strong class="ledger-pag-active-page">${curPage}</strong> / ${totPages} 页</span>
                <span class="ledger-pag-divider">·</span>
                <span>共 <strong class="ledger-pag-total-items">${totItems}</strong> 次发布</span>
                <div class="ledger-pag-size-selector">
                    <span class="ledger-pag-label">每页</span>
                    <select class="mini-select ledger-page-size-select" onchange="window.changeHostingHistoryPageSize(this.value)">
                        <option value="10" ${curSize === 10 ? 'selected' : ''}>10</option>
                        <option value="20" ${curSize === 20 ? 'selected' : ''}>20</option>
                        <option value="50" ${curSize === 50 ? 'selected' : ''}>50</option>
                    </select>
                    <span class="ledger-pag-label">条</span>
                </div>
            </div>
            <div class="ledger-pag-actions">
                <button type="button" class="mini-btn ${isFirst ? 'is-disabled' : ''}" 
                    ${isFirst ? 'disabled' : 'onclick="window.changeHostingHistoryPage(1)"'} 
                    title="跳转至第一页">⏮️ 首页</button>
                <button type="button" class="mini-btn ${isFirst ? 'is-disabled' : ''}" 
                    ${isFirst ? 'disabled' : `onclick="window.changeHostingHistoryPage(${curPage - 1})"`} 
                    title="上一页">◀️ 上一页</button>
                <button type="button" class="mini-btn ${isLast ? 'is-disabled' : ''}" 
                    ${isLast ? 'disabled' : `onclick="window.changeHostingHistoryPage(${curPage + 1})"`} 
                    title="下一页">▶️ 下一页</button>
                <button type="button" class="mini-btn ${isLast ? 'is-disabled' : ''}" 
                    ${isLast ? 'disabled' : `onclick="window.changeHostingHistoryPage(${totPages})"`} 
                    title="跳转至最后一页">⏭️ 尾页</button>
            </div>
        </div>
    `;

    box.innerHTML = `
        <table class="dispatch-ledger-table hosting-table-compact">
            <thead>
                <tr>
                    <th class="col-id" style="width: 12%; min-width: 100px; text-align: center;">编号</th>
                    <th class="col-time" style="width: 12%; min-width: 88px; text-align: center;">发布时间</th>
                    <th class="col-theme" style="width: 12%; min-width: 85px; text-align: center;">网站主题</th>
                    <th class="col-pages" style="width: 8.5%; min-width: 60px; text-align: center;">页面数量</th>
                    <th class="col-size" style="width: 8.5%; min-width: 60px; text-align: center;">打包体积</th>
                    <th class="col-status" style="width: 9%; min-width: 65px; text-align: center;">状态</th>
                    <th class="col-duration" style="width: 6%; min-width: 45px; text-align: center;">用时</th>
                    <th class="col-targets" style="width: 22%; min-width: 130px; text-align: center;">发布平台</th>
                    <th class="col-actions" style="width: 10%; min-width: 75px; text-align: center;">操作</th>
                </tr>
            </thead>
            <tbody>${rowsHtml}</tbody>
        </table>
        ${paginationHtml}`;
};

/**
 * 切换网站发布历史记录分页
 */
window.changeHostingHistoryPage = async function (page) {
    const targetPage = Math.max(1, Math.min(page, window._hostingHistoryTotalPages || 1));
    window._hostingHistoryCurrentPage = targetPage;

    if (typeof apiFetch !== 'function') return;
    try {
        const res = await apiFetch(`/api/dispatch/hosting/batches?page=${targetPage}&page_size=${window._hostingHistoryPageSize}`);
        if (!res || res.status !== 'success') return;
        window.renderHostingBatchLedger(res.batches || [], res.pagination || null);
    } catch (e) {
        console.error("🛑 切换发布历史分页失败:", e);
    }
};

/**
 * 切换网站发布历史记录每页容量
 */
window.changeHostingHistoryPageSize = async function (pageSize) {
    const size = parseInt(pageSize, 10) || 10;
    window._hostingHistoryPageSize = size;
    await window.changeHostingHistoryPage(1);
};
