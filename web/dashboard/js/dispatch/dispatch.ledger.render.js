/**
 * 🚀 [V122.0] Illacme Plenipes - Dispatch Ledger & Dead-Letter Rendering
 * 职责：分发成果账本表格渲染（含真实线上访问链接直达）与死信异常自愈卡片交互。
 * 🛡️ [SOP-01 / SOP-02 模块规范] 单文件严格保持在 300 行以内。
 */

const _resolveLedgerLang = (c, n, i) => {
    const clean = String(c || '').trim().toLowerCase();
    if (!clean || clean === 'docs' || clean === 'doc') {
        return { name: '简体中文', icon: '🇨🇳', code: 'zh-Hans' };
    }
    // 归一化简体中文
    if (['zh', 'zh-hans', 'zh-cn', 'zh-sg', 'cmn', 'cmn-hans'].includes(clean)) {
        return { name: '简体中文', icon: '🇨🇳', code: 'zh-Hans' };
    }
    // 归一化繁体中文
    if (['zh-hant', 'zh-tw', 'zh-hk', 'cmn-hant'].includes(clean)) {
        return { name: '繁體中文', icon: '🇭🇰', code: 'zh-Hant' };
    }

    // 只有当传入的名称不是单纯的大写代码、且不等于 code 时，才视作显式自定义母语名称
    const isCodeLike = n && (String(n).trim().toLowerCase() === clean || String(n).trim().toLowerCase() === clean.replace(/[-_]/g, ''));
    if (n && n !== c && !isCodeLike && i && i !== '🌐') {
        return { name: n, icon: i, code: c };
    }

    // 权威语种库查询 (SSOT)
    if (typeof window.getLanguageMeta === 'function') {
        const m = window.getLanguageMeta(clean);
        if (m && m.name && m.name.toLowerCase() !== clean) {
            return { name: m.name, icon: m.icon || '🌐', code: m.code || c };
        }
    }

    const base = clean.split(/[-_]/)[0];
    const matched = (window.availableLangs || []).find(l => {
        const lc = (l.code || '').toLowerCase();
        return lc === clean || lc === base;
    });
    if (matched) {
        return { name: matched.name, icon: matched.icon || '🌐', code: matched.code || c };
    }

    return {
        name: (n && !isCodeLike) ? n : clean.toUpperCase(),
        icon: (i && i !== '🌐') ? i : '🌐',
        code: c
    };
};

const _resolveLedgerChannel = (id, n, i) => {
    const tid = String(id || '').trim().toLowerCase();
    const badge = (typeof window.getPlatformBrandBadge === 'function') ? window.getPlatformBrandBadge(tid) : null;
    const finalIcon = (badge && badge.icon && badge.icon !== '🌐') ? badge.icon : (i || (badge && badge.icon) || '🏷️');
    if (n && n !== id) return { name: n, icon: finalIcon };
    if (typeof window.getSyndicateChannelMeta === 'function') {
        const m = window.getSyndicateChannelMeta(id);
        if (m && m.name && m.name !== id) return { name: m.name, icon: finalIcon || m.icon };
    }
    return { name: String(id || '').replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()), icon: finalIcon };
};

const _fallbackPaginationHtml = (totalItems, currentPage, totalPages, pageSize) => {
    if (totalItems <= 0) return '';
    const isFirst = currentPage <= 1, isLast = currentPage >= totalPages;
    return `<div class="pagination-container dispatch-ledger-pagination">
        <div class="ledger-pag-meta">
            <span>第 <strong class="ledger-pag-active-page">${currentPage}</strong> / ${totalPages} 页</span><span class="ledger-pag-divider">·</span><span>共 <strong class="ledger-pag-total-items">${totalItems}</strong> 项任务</span>
            <div class="ledger-pag-size-selector"><span class="ledger-pag-label">每页</span><select class="mini-select ledger-page-size-select" onchange="window.changeDispatchLedgerPageSize(this.value)"><option value="10" ${pageSize === 10 ? 'selected' : ''}>10</option><option value="25" ${pageSize === 25 ? 'selected' : ''}>25</option><option value="50" ${pageSize === 50 ? 'selected' : ''}>50</option></select><span class="ledger-pag-label">条</span></div>
        </div>
        <div class="ledger-pag-actions">
            <button type="button" class="mini-btn ${isFirst ? 'is-disabled' : ''}" ${isFirst ? 'disabled' : 'onclick="window.changeDispatchLedgerPage(1)"'} title="首页">⏮️ 首页</button>
            <button type="button" class="mini-btn ${isFirst ? 'is-disabled' : ''}" ${isFirst ? 'disabled' : `onclick="window.changeDispatchLedgerPage(${currentPage - 1})"`} title="上一页">◀️ 上一页</button>
            <button type="button" class="mini-btn ${isLast ? 'is-disabled' : ''}" ${isLast ? 'disabled' : `onclick="window.changeDispatchLedgerPage(${currentPage + 1})"`} title="下一页">▶️ 下一页</button>
            <button type="button" class="mini-btn ${isLast ? 'is-disabled' : ''}" ${isLast ? 'disabled' : `onclick="window.changeDispatchLedgerPage(${totalPages})"`} title="尾页">⏭️ 尾页</button>
        </div>
    </div>`;
};

if (typeof window.changeDispatchLedgerPage !== 'function') {
    window.changeDispatchLedgerPage = function (p) {
        window._dispatchLedgerCurrentPage = Number(p) || 1;
        const data = window._lastDispatchOverview || {};
        window.renderDispatchLedger(data.recent_records || []);
    };
}
if (typeof window.changeDispatchLedgerPageSize !== 'function') {
    window.changeDispatchLedgerPageSize = function (s) {
        window._dispatchLedgerPageSize = Number(s) || 10;
        window._dispatchLedgerCurrentPage = 1;
        const data = window._lastDispatchOverview || {};
        window.renderDispatchLedger(data.recent_records || []);
    };
}

/**
 * 渲染全域分发成果账本表格入口（优先调度物理分页中枢，无缝自愈兜底）
 */
window.renderDispatchLedger = function (records) {
    if (typeof window.initDispatchLedgerPagination === 'function') {
        window.initDispatchLedgerPagination(records);
        return;
    }
    const all = Array.isArray(records) ? records : [];
    const size = window._dispatchLedgerPageSize || 10;
    const cur = window._dispatchLedgerCurrentPage || 1;
    const totalPages = Math.max(1, Math.ceil(all.length / size));
    const page = Math.min(Math.max(1, cur), totalPages);
    const paged = all.slice((page - 1) * size, page * size);
    window.renderDispatchLedgerTable(paged, all.length, page, totalPages);
};

/**
 * 切换展开或收起失败任务的折叠诊断面板
 */
window.toggleLedgerDiagnostic = function (id) {
    const row = document.getElementById(id);
    if (!row) return;
    const isHidden = (row.style.display === 'none' || !row.style.display);
    row.style.display = isHidden ? 'table-row' : 'none';
};

/**
 * 物理渲染全域统一流水大表与底部分页栏
 */
window.renderDispatchLedgerTable = function (records, totalItems, currentPage, totalPages, query = '') {
    const container = document.getElementById('dispatch-ledger-container');
    const badge = document.getElementById('tab-badge-ledger');
    if (!container) return;
    if (badge) badge.innerText = String(totalItems ?? (records ? records.length : 0));

    if (!records || records.length === 0) {
        const dock = document.getElementById('dispatch-pagination-dock');
        if (dock) {
            dock.innerHTML = '';
            dock.style.display = 'none';
        }
        container.innerHTML = `
            <div style="padding: 40px 20px; text-align: center; color: var(--text-muted, #9ca3af);">
                <div style="font-size: 2rem; margin-bottom: 8px;">${query ? '🔍' : '📖'}</div>
                <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-bright, #ffffff);">${query ? '未检索到匹配的分发作业' : '尚无分发任务记录'}</div>
                <div style="font-size: 0.8rem; margin-top: 4px;">${query ? '请尝试调整筛选条件或搜索关键词。' : '点击右上角【全域发布】或在文库中选择笔记即可发起分发。'}</div>
            </div>`;
        return;
    }

    let html = `<table class="ledger-table">
        <thead>
            <tr>
                <th style="width: 36%; white-space: nowrap;">稿件标题与路径</th>
                <th style="width: 12%; white-space: nowrap;">发布语种</th>
                <th style="width: 14%; white-space: nowrap;">目标分发渠道</th>
                <th style="width: 13%; white-space: nowrap;">发布状态</th>
                <th style="width: 13%; white-space: nowrap;">发布时间</th>
                <th style="width: 12%; text-align: right; white-space: nowrap;">操作</th>
            </tr>
        </thead>
        <tbody>`;

    records.forEach((rec, idx) => {
        const isFailed = (rec.status === 'failed' || Boolean(rec.error || rec.last_error));
        const hasUrl = Boolean(rec.remote_url);
        const safePath = window.escapeHtml ? window.escapeHtml(rec.rel_path) : rec.rel_path;
        const rawTitle = rec.title || rec.rel_path;
        const safeTitle = window.escapeHtml ? window.escapeHtml(rawTitle) : rawTitle;
        const isPathOnly = (safeTitle === safePath);
        const targetId = window.escapeHtml ? window.escapeHtml(rec.target_id) : rec.target_id;
        const langCode = window.escapeHtml ? window.escapeHtml(rec.lang_code || 'zh-CN') : (rec.lang_code || 'zh-CN');
        const langMeta = _resolveLedgerLang(rec.lang_code, rec.lang_name, rec.lang_icon);
        const chMeta = _resolveLedgerChannel(rec.target_id, rec.target_name, rec.target_icon);
        const rawTime = rec.display_time || rec.updated_at || rec.failed_at;
        const timeText = window.formatDispatchTime ? window.formatDispatchTime(rawTime) : (rawTime || '刚刚');
        const fullTime = window.formatDispatchFullTime ? window.formatDispatchFullTime(rawTime) : (rawTime || '刚刚');

        const diag = rec.diagnostic || {};
        const safeError = window.escapeHtml ? window.escapeHtml(rec.error || rec.last_error || '') : (rec.error || rec.last_error || '');
        const friendlyMsg = window.escapeHtml ? window.escapeHtml(diag.friendly_message || safeError) : (diag.friendly_message || safeError);
        const suggestion = window.escapeHtml ? window.escapeHtml(diag.suggestion || '请检查渠道密钥配置并重新触发。') : (diag.suggestion || '请检查渠道密钥配置并重新触发。');
        const diagRowId = `ledger-diag-${idx}`;
        const retryBtnId = `ledger-retry-btn-${idx}`;
        const rowId = `ledger-row-${idx}`;

        // 🌊 智能流式感知：判断任务是否处于正在重新发布中，或刚刚自愈完成
        const taskKey = `${rec.rel_path}::${rec.target_id}`;
        const isRunning = Boolean(
            (window._dispatchActiveRunningSet && window._dispatchActiveRunningSet.has(taskKey)) ||
            rec.status === 'syncing'
        );
        const isJustCompleted = Boolean(window._dispatchRecentlyCompletedSet && window._dispatchRecentlyCompletedSet.has(taskKey));

        // 状态徽标渲染
        let statusBadgeHtml = '';
        if (isRunning) {
            statusBadgeHtml = `<span class="dispatch-status-badge is-running"><span class="spinner-spin">🔄</span> 正在发布...</span>`;
        } else if (isFailed) {
            if (window.DispatchCooldownManager) {
                window.DispatchCooldownManager.clearCooldown(rec.rel_path, rec.target_id);
            }
            const retryCount = rec.retry_count || 0;
            statusBadgeHtml = `<span class="dispatch-status-badge is-failed" onclick="window.toggleLedgerDiagnostic('${diagRowId}')" style="cursor: pointer;" title="发布受阻，点击就地展开故障诊断与自愈指南：${friendlyMsg}">⚠️ 待自愈${retryCount > 0 ? ` (${retryCount}次)` : ''} 🔍</span>`;
        } else if (rec.is_stale) {
            statusBadgeHtml = `<span class="dispatch-status-badge is-stale" onclick="if(typeof window.openDispatchDiffModal==='function') window.openDispatchDiffModal('${safePath}', '${targetId}', '${langCode}', '${chMeta.name}');" style="cursor: pointer;" title="本地原稿有新修改，点击查看改动差异与决策">🟡 待更新 🔍</span>`;
        } else {
            statusBadgeHtml = `<span class="dispatch-status-badge is-success" title="已成功发布上线">✓ 成功</span>`;
        }

        // 操作区渲染
        let actionsHtml = '';
        if (isRunning) {
            actionsHtml = `
                <div class="ledger-actions-cell">
                    <button class="secondary-btn ledger-icon-btn" onclick="if(typeof window.openSyndicateLivePreviewModal==='function') window.openSyndicateLivePreviewModal('${safePath}', '${targetId}');" title="前置排版工坊与一键复制"><span>👁️</span></button>
                    <button class="secondary-btn ledger-icon-btn is-diag-btn" onclick="window.toggleLedgerDiagnostic('${diagRowId}')" title="查看自愈建议与故障诊断"><span>🩺</span></button>
                    <button class="primary-btn glow-btn ledger-icon-btn is-retry-btn" id="${retryBtnId}" disabled title="正在重新发布推流中..."><span class="spinner-spin">🔄</span></button>
                </div>
            `;
        } else if (isFailed) {
            actionsHtml = `
                <div class="ledger-actions-cell">
                    <button class="secondary-btn ledger-icon-btn" onclick="if(typeof window.openSyndicateLivePreviewModal==='function') window.openSyndicateLivePreviewModal('${safePath}', '${targetId}');" title="前置排版工坊与一键复制"><span>👁️</span></button>
                    <button class="secondary-btn ledger-icon-btn is-diag-btn" onclick="window.toggleLedgerDiagnostic('${diagRowId}')" title="查看自愈建议与故障诊断"><span>🩺</span></button>
                    <button class="primary-btn glow-btn ledger-icon-btn is-retry-btn" id="${retryBtnId}" onclick="window.retrySingleLedgerTask('${safePath}', '${targetId}', '${langCode}', '${retryBtnId}', '${rowId}', '${diagRowId}')" title="立即自愈重发当前任务"><span>🔄</span></button>
                </div>
            `;
        } else {
            const remCooldown = (window.DispatchCooldownManager && window.DispatchCooldownManager.getRemaining(rec.rel_path, rec.target_id)) || 0;
            const isCooling = remCooldown > 0;
            const republishTitle = isCooling
                ? `🛡️ 平台安全频控保护中：建议间隔等待，剩余 ${remCooldown}s`
                : (rec.is_stale ? '本地原稿已发生修改，点击立即向此渠道广播推流更新' : '向此渠道重新广播推流');
            const republishClass = `secondary-btn ledger-icon-btn is-republish-btn ${isCooling ? 'is-cooling-btn' : (rec.is_stale ? 'is-stale-republish' : '')}`;
            const republishContent = isCooling ? `<span>🛡️ ${remCooldown}s</span>` : '<span>📡</span>';
            const republishDisabled = isCooling ? 'disabled' : '';

            actionsHtml = `
                <div class="ledger-actions-cell">
                    <button class="secondary-btn ledger-icon-btn" onclick="if(typeof window.openSyndicateLivePreviewModal==='function') window.openSyndicateLivePreviewModal('${safePath}', '${targetId}');" title="前置排版工坊与一键复制"><span>👁️</span></button>
                    <button class="${republishClass}" id="${retryBtnId}" ${republishDisabled} data-cooldown-task="${taskKey}" onclick="window.republishSingleSyndicationDoc('${safePath}', '${targetId}', '${langCode}', '${retryBtnId}', '${rowId}')" title="${republishTitle}">${republishContent}</button>
                    ${hasUrl ? `<a href="${rec.remote_url}" target="_blank" rel="noopener noreferrer" class="magic-deep-link ledger-icon-btn" title="在新标签页中访问线上真实文章"><span>🌐</span></a>` : '<span class="ledger-online-badge" title="已成功发布上线">✓</span>'}
                </div>
            `;
        }

        let rowStateClass = '';
        if (isRunning) rowStateClass = 'is-running-row';
        else if (isJustCompleted) rowStateClass = 'ledger-row--success-glow';
        else if (isFailed) rowStateClass = 'is-failed-row';

        html += `<tr id="${rowId}" class="ledger-row ${rowStateClass}" data-title="${safeTitle.toLowerCase()}" data-path="${safePath.toLowerCase()}" data-target="${targetId.toLowerCase()}" data-target-name="${chMeta.name.toLowerCase()}" data-lang="${langMeta.name.toLowerCase()} ${langCode.toLowerCase()}">
            <td>
                <div style="font-weight: 700; color: var(--text-bright, #ffffff); font-size: 0.88rem; line-height: 1.35; margin-bottom: 3px; display: flex; align-items: center; gap: 6px;" title="${safeTitle}">
                    ${isFailed ? '<span style="font-size: 0.85rem;" title="发布异常">⚠️</span>' : ''}
                    <span>${safeTitle}</span>
                </div>
                ${!isPathOnly ? `<div style="font-size: 0.72rem; color: var(--text-muted, #9ca3af); font-family: var(--font-mono, monospace); display: flex; align-items: center; gap: 4px; opacity: 0.85;" title="${safePath}"><span>📄</span><span>${safePath}</span></div>` : ''}
            </td>
            <td style="white-space: nowrap;">
                <div style="display: flex; flex-direction: column; gap: 2px;" title="${langMeta.name} (${langMeta.code || langCode})">
                    <div style="display: flex; align-items: center; gap: 5px;"><span style="font-size: 0.95rem; line-height: 1;">${langMeta.icon}</span><span style="font-weight: 600; color: var(--text-bright, #ffffff); font-size: 0.82rem; line-height: 1.2;">${langMeta.name}</span></div>
                    <div style="font-family: var(--font-mono, monospace); font-size: 0.70rem; color: var(--text-muted, #9ca3af); opacity: 0.8; padding-left: 2px; line-height: 1;">${langMeta.code || langCode}</div>
                </div>
            </td>
            <td style="white-space: nowrap;"><span class="platform-pill" title="渠道标识: ${targetId}"><span>${chMeta.icon}</span><span style="font-weight: 600;">${chMeta.name}</span></span></td>
            <td style="white-space: nowrap;">${statusBadgeHtml}</td>
            <td><span style="font-size: 0.78rem; color: var(--text-muted, #9ca3af);" title="${fullTime}">${timeText || '刚刚'}</span></td>
            <td style="text-align: right; white-space: nowrap;">${actionsHtml}</td>
        </tr>`;

        // 失败项的就地折叠展开诊断抽屉行
        if (isFailed) {
            const ipMatch = (diag.extracted_ip) || (safeError && safeError.match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/) ? safeError.match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/)[0] : '');
            const ipChipHtml = ipMatch ? `
                <div style="margin-top: 6px; display: inline-flex; align-items: center; gap: 8px; padding: 4px 10px; background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; font-size: 0.76rem;">
                    <span style="color: var(--neon-cyan); font-weight: 700;">📡 出口 IP:</span>
                    <code style="color: var(--text-bright); font-family: var(--font-mono, monospace); font-weight: 700;">${ipMatch}</code>
                    <button class="secondary-btn" onclick="if(navigator.clipboard){navigator.clipboard.writeText('${ipMatch}');} if(typeof showToast==='function') showToast('✅ 已复制出口 IP: ${ipMatch}', 'success');" style="padding: 2px 8px; font-size: 0.70rem; line-height: 1.2;">📋 一键复制</button>
                </div>` : '';

            html += `
                <tr id="${diagRowId}" class="ledger-diagnostic-row" style="display: none;">
                    <td colspan="6" style="padding: 0;">
                        <div class="ledger-diag-card">
                            <div class="ledger-diag-header">
                                <div class="ledger-diag-title">
                                    <span style="font-size: 1rem;">🩺</span>
                                    <span style="font-weight: 700; color: var(--neon-red);">分发异常诊断与自愈中枢</span>
                                </div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <button class="secondary-btn" onclick="window.navToChannelConfig('${targetId}')" style="padding: 3px 10px; font-size: 0.74rem;"><span>🔑 检查渠道授权</span></button>
                                    <button class="secondary-btn danger" onclick="window.clearSingleDeadLetterTask('${safePath}', '${targetId}'); if(typeof window.toggleLedgerDiagnostic==='function') window.toggleLedgerDiagnostic('${diagRowId}');" title="清除并忽略当前异常状态" style="padding: 3px 10px; font-size: 0.74rem;"><span>🧹 忽略异常</span></button>
                                    <button class="primary-btn glow-btn" id="diag-${retryBtnId}" onclick="window.retrySingleLedgerTask('${safePath}', '${targetId}', '${langCode}', '${retryBtnId}', '${rowId}', '${diagRowId}')" style="padding: 3px 12px; font-size: 0.74rem; font-weight: 700;"><span>🔄 立即重发此任务</span></button>
                                </div>
                            </div>
                            <div class="ledger-diag-body">
                                <div><strong style="color: var(--neon-red);">故障归因:</strong> ${friendlyMsg}</div>
                                <div style="color: var(--neon-cyan); margin-top: 4px;"><strong style="font-weight: 700;">💡 自愈建议:</strong> ${suggestion}</div>
                                ${ipChipHtml}
                                <details style="margin-top: 6px; font-size: 0.72rem; color: var(--text-muted, #9ca3af);">
                                    <summary style="cursor: pointer; opacity: 0.85;">查看底层原始错误栈</summary>
                                    <pre class="ledger-error-pre">${safeError}</pre>
                                </details>
                            </div>
                        </div>
                    </td>
                </tr>
            `;
        }
    });
    html += '</tbody></table>';

    // 挂载分页栏（优先渲染至专属固定底栏 dock，紧贴底部状态栏且固定不随表格滚动；无缝自愈兜底）
    const pagHtml = (typeof window.buildDispatchLedgerPaginationHtml === 'function')
        ? window.buildDispatchLedgerPaginationHtml(totalItems, currentPage, totalPages, window._dispatchLedgerPageSize || 10)
        : _fallbackPaginationHtml(totalItems, currentPage, totalPages, window._dispatchLedgerPageSize || 10);
    
    const dock = document.getElementById('dispatch-pagination-dock');
    if (dock) {
        dock.innerHTML = pagHtml;
        dock.style.display = pagHtml ? 'block' : 'none';
        container.innerHTML = html;
    } else {
        html += pagHtml;
        container.innerHTML = html;
    }
};

/**
 * 渲染死信异常自愈卡片列表
 */
window.renderDispatchDeadLetters = function (tasks) {
    const container = document.getElementById('dispatch-deadletter-container');
    const badge = document.getElementById('tab-badge-deadletter');
    if (!container) return;
    if (badge) badge.innerText = String(tasks ? tasks.length : 0);
    if (!tasks || tasks.length === 0) {
        container.innerHTML = `<div class="glass-panel" style="padding: 40px 20px; text-align: center; border-radius: 12px;"><div style="font-size: 2rem; margin-bottom: 8px;">🎉</div><div style="font-weight: 700; font-size: 0.95rem; color: #00ff88;">队列健康 · 0 项死信异常</div><div style="font-size: 0.8rem; color: var(--text-muted, #9ca3af); margin-top: 4px;">所有渠道同步任务均已圆满完成或就绪。</div></div>`;
        return;
    }
    container.innerHTML = tasks.map((t, idx) => {
        const safePath = window.escapeHtml ? window.escapeHtml(t.rel_path) : t.rel_path;
        const rawTitle = t.title || t.rel_path;
        const safeTitle = window.escapeHtml ? window.escapeHtml(rawTitle) : rawTitle;
        const targetId = window.escapeHtml ? window.escapeHtml(t.target_id) : t.target_id;
        const langMeta = _resolveLedgerLang(t.lang_code, t.lang_name, t.lang_icon);
        const chMeta = _resolveLedgerChannel(t.target_id, t.target_name, t.target_icon);
        const safeError = window.escapeHtml ? window.escapeHtml(t.last_error || '未知网络或认证异常') : (t.last_error || '未知网络或认证异常');
        const diag = t.diagnostic || {};
        const badgeText = window.escapeHtml ? window.escapeHtml(diag.badge || '⚠️ 异常待自愈') : (diag.badge || '⚠️ 异常待自愈');
        const badgeColor = diag.badge_color || '#ff6b6b';
        const friendlyMsg = window.escapeHtml ? window.escapeHtml(diag.friendly_message || safeError) : (diag.friendly_message || safeError);
        const suggestion = window.escapeHtml ? window.escapeHtml(diag.suggestion || '请检查渠道密钥配置并重新触发。') : (diag.suggestion || '请检查渠道密钥配置并重新触发。');
        const ipMatch = (diag.extracted_ip) || (safeError && safeError.match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/) ? safeError.match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/)[0] : '');
        const ipChipHtml = ipMatch ? `
            <div style="margin-top: 6px; display: inline-flex; align-items: center; gap: 8px; padding: 4px 10px; background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; font-size: 0.76rem;">
                <span style="color: var(--neon-cyan); font-weight: 700;">📡 出口 IP:</span>
                <code style="color: var(--text-bright); font-family: var(--font-mono, monospace); font-weight: 700;">${ipMatch}</code>
                <button class="secondary-btn" onclick="if(navigator.clipboard){navigator.clipboard.writeText('${ipMatch}');} if(typeof showToast==='function') showToast('✅ 已复制出口 IP: ${ipMatch}', 'success');" style="padding: 2px 8px; font-size: 0.70rem; line-height: 1.2;">📋 一键复制</button>
            </div>` : '';
        const cardId = `dl-card-${idx}`, btnRetryId = `dl-retry-btn-${idx}`;
        return `
            <div class="deadletter-card" id="${cardId}" data-title="${safeTitle.toLowerCase()}" data-path="${safePath.toLowerCase()}" data-target="${targetId.toLowerCase()}" data-target-name="${chMeta.name.toLowerCase()}" data-lang="${langMeta.name.toLowerCase()} ${(t.lang_code || '').toLowerCase()}">
                <div class="dl-header">
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <span style="font-size: 1.1rem;">⚠️</span>
                        <span class="dl-title" title="${safePath}">${safeTitle}</span>
                        ${safeTitle !== safePath ? `<span style="font-size: 0.72rem; color: var(--text-muted, #9ca3af); font-family: var(--font-mono, monospace);">(${safePath})</span>` : ''}
                        <span class="platform-pill" style="border-color: rgba(var(--neon-red-rgb), 0.4); color: var(--neon-red);" title="渠道标识: ${targetId}"><span>${chMeta.icon}</span><span>${chMeta.name}</span></span>
                        <span style="font-size: 0.72rem; padding: 2px 7px; border-radius: 4px; background: rgba(255,255,255,0.06); color: var(--text-bright); display: inline-flex; align-items: center; gap: 4px;"><span>${langMeta.icon}</span><span>${langMeta.name}</span></span>
                        <span style="font-size: 0.72rem; padding: 2px 7px; border-radius: 4px; background: rgba(255,255,255,0.06); border: 1px solid ${badgeColor}; color: ${badgeColor}; font-weight: 600;">${badgeText}</span>
                    </div>
                    <span style="font-size: 0.76rem; color: var(--text-muted, #9ca3af);">已重试 ${t.retry_count || 0} 次</span>
                </div>
                <div class="dl-reason" style="display: flex; flex-direction: column; gap: 4px; line-height: 1.45;">
                    <div><span style="color: var(--neon-red); font-weight: 700;">故障归因:</span> ${friendlyMsg}</div>
                    <div style="color: var(--neon-cyan); font-size: 0.78rem;"><span style="font-weight: 700;">💡 自愈建议:</span> ${suggestion}</div>
                    ${ipChipHtml}
                    <details style="margin-top: 4px; font-size: 0.72rem; color: var(--text-muted, #9ca3af);">
                        <summary style="cursor: pointer; opacity: 0.8;">查看底层原始错误栈</summary>
                        <pre style="margin-top: 4px; padding: 6px 8px; background: rgba(0,0,0,0.3); border-radius: 4px; font-family: var(--font-mono, monospace); white-space: pre-wrap; word-break: break-all;">${safeError}</pre>
                    </details>
                </div>
                <div class="dl-actions">
                    <button class="secondary-btn" onclick="if(typeof window.openSyndicateLivePreviewModal==='function') window.openSyndicateLivePreviewModal('${safePath}', '${targetId}');" style="padding: 5px 12px; font-size: 0.78rem;"><span>👁️ 预览排版</span></button>
                    <button class="secondary-btn" onclick="window.navToChannelConfig('${targetId}')" style="padding: 5px 12px; font-size: 0.78rem;"><span>🔑 检查渠道授权</span></button>
                    <button class="secondary-btn danger" onclick="window.clearSingleDeadLetterTask('${safePath}', '${targetId}')" style="padding: 5px 12px; font-size: 0.78rem;"><span>🗑️ 移出死信</span></button>
                    <button class="primary-btn glow-btn" id="${btnRetryId}" onclick="window.retrySingleDeadLetterTask('${safePath}', '${targetId}', '${btnRetryId}', '${cardId}', '${t.lang_code || "zh-CN"}')" style="padding: 5px 14px; font-size: 0.78rem;"><span>🔄 立即重试</span></button>
                </div>
            </div>`;
    }).join('');
};

/**
 * 智能直达对应渠道配置抽屉
 */
window.navToChannelConfig = function (targetId) {
    if (typeof window.openPluginConfig === 'function') window.openPluginConfig(targetId);
    else if (typeof window.showView === 'function') window.showView('plugins', 'publisher');
};

/**
 * 🔄 [V122.5] 分发总账行就地重试自愈算子 (In-Place Self-Healing)
 */
window.retrySingleLedgerTask = async function (relPath, targetId, langCode = 'zh-CN', btnId = null, rowId = null, diagRowId = null) {
    const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (u, i) => (await fetch(u, i)).json());
    const btn = btnId ? document.getElementById(btnId) : null;
    const diagBtn = btnId ? document.getElementById(`diag-${btnId}`) : null;
    const row = rowId ? document.getElementById(rowId) : null;
    const badgeEl = row ? row.querySelector('.dispatch-status-badge') : null;

    const taskKey = `${relPath}::${targetId}`;
    if (window._dispatchActiveRunningSet) {
        window._dispatchActiveRunningSet.add(taskKey);
    }
    if (typeof window.startDispatchLedgerPolling === 'function') {
        window.startDispatchLedgerPolling();
    }

    // 1. 瞬态交互反馈 (禁用按钮、显示转圈与重发态)
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-spin">🔄</span>';
        btn.title = '正在重新发布中...';
    }
    if (diagBtn) {
        diagBtn.disabled = true;
        diagBtn.innerHTML = '<span class="spinner-spin">🔄</span> 正在发布...';
    }
    if (badgeEl) {
        badgeEl.className = 'dispatch-status-badge is-running';
        badgeEl.innerHTML = '<span class="spinner-spin">🔄</span> 正在重发...';
    }
    if (row) {
        row.classList.add('is-running-row');
    }

    if (typeof showToast === 'function') {
        showToast(`🚀 已下发 [${(targetId || '').toUpperCase()}] 自愈重发指令，正在调起管线...`, 'info');
    }

    try {
        const res = await fetchFunc('/api/dispatch/deadletter/retry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rel_path: relPath, target_id: targetId, lang_code: langCode })
        });

        if (res && res.status === 'error') {
            throw new Error(res.message || '重发请求未被接受');
        }

        // 2. 调度受理与持续流式跟踪
        if (window._dispatchTaskStartTimes) {
            window._dispatchTaskStartTimes.set(taskKey, Date.now());
        }
        if (typeof window.startDispatchLedgerPolling === 'function') {
            window.startDispatchLedgerPolling();
        }
        if (typeof showToast === 'function') {
            showToast(`🚀 [${(targetId || '').toUpperCase()}] 自愈任务已受理，正在执行重推...`, 'info');
        }
        setTimeout(async () => {
            if (typeof window.loadDispatchCenter === 'function') {
                await window.loadDispatchCenter('ledger');
            }
        }, 500);
    } catch (err) {
        console.error('[Retry Ledger Task Error]:', err);
        if (window._dispatchActiveRunningSet) {
            window._dispatchActiveRunningSet.delete(taskKey);
        }
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span>🔄</span>';
        }
        if (diagBtn) {
            diagBtn.disabled = false;
            diagBtn.innerHTML = '<span>🔄 立即重发此任务</span>';
        }
        if (badgeEl) {
            badgeEl.className = 'dispatch-status-badge is-failed';
            badgeEl.innerHTML = '⚠️ 重发失败';
        }
        if (row) {
            row.classList.remove('is-running-row');
        }
        if (typeof showToast === 'function') {
            showToast('重发失败: ' + (err.message || '网络异常'), 'error');
        }
    }
};

/**
 * 🚀 [V123.0] 单篇稿件重新推送到指定社交媒体渠道 (定向重推)
 */
window.republishSingleSyndicationDoc = async function (relPath, targetId, langCode = 'zh-CN', btnId = null, rowId = null) {
    const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (u, i) => (await fetch(u, i)).json());
    const btn = btnId ? document.getElementById(btnId) : null;
    const row = rowId ? document.getElementById(rowId) : null;
    const badgeEl = row ? row.querySelector('.dispatch-status-badge') : null;

    const taskKey = `${relPath}::${targetId}`;
    if (window._dispatchActiveRunningSet) {
        window._dispatchActiveRunningSet.add(taskKey);
    }
    if (typeof window.startDispatchLedgerPolling === 'function') {
        window.startDispatchLedgerPolling();
    }

    // 1. 瞬态交互反馈 (禁用按钮、显示旋转刷新与推流中状态)
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-spin">🔄</span>';
        btn.title = '正在重新发布推流中...';
    }
    if (badgeEl) {
        badgeEl.className = 'dispatch-status-badge is-running';
        badgeEl.innerHTML = '<span class="spinner-spin">🔄</span> 正在推送...';
    }
    if (row) {
        row.classList.add('is-running-row');
    }

    if (typeof showToast === 'function') {
        showToast(`📡 已下发 [${(targetId || '').toUpperCase()}] 定向广播推流任务，正在调起分发管线...`, 'info');
    }

    try {
        const res = await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_channel: targetId,
                target_slot: langCode,
                skip_syndication: false,
                clear_cache: false
            })
        });

        if (res && res.rate_limited) {
            if (window._dispatchActiveRunningSet) {
                window._dispatchActiveRunningSet.delete(taskKey);
            }
            if (row) row.classList.remove('is-running-row');
            if (badgeEl) {
                badgeEl.className = 'dispatch-status-badge is-stale';
                badgeEl.innerHTML = '🟡 待更新 🔍';
            }
            if (window.DispatchCooldownManager) {
                window.DispatchCooldownManager.startCooldown(relPath, targetId, res.retry_after || 30);
            }
            if (typeof showToast === 'function') {
                showToast(res.message || '触发平台安全频控保护，请稍候重试', 'warning');
            }
            return;
        }

        if (res && res.success === false) {
            throw new Error(res.message || '重推请求未被受理');
        }

        // 🛡️ [V127.0] 启动平台级频控安全冷却中枢
        if (window.DispatchCooldownManager) {
            window.DispatchCooldownManager.startCooldown(relPath, targetId, res.cooldown_total || null);
        }

        // 2. 调度受理与持续流式跟踪
        if (window._dispatchTaskStartTimes) {
            window._dispatchTaskStartTimes.set(taskKey, Date.now());
        }
        if (typeof window.startDispatchLedgerPolling === 'function') {
            window.startDispatchLedgerPolling();
        }
        setTimeout(async () => {
            if (typeof window.loadDispatchCenter === 'function') {
                await window.loadDispatchCenter('ledger');
            }
        }, 500);
    } catch (err) {
        console.error('[Republish Single Syndication Error]:', err);
        if (window._dispatchActiveRunningSet) {
            window._dispatchActiveRunningSet.delete(taskKey);
        }
        if (window.DispatchCooldownManager) {
            window.DispatchCooldownManager.clearCooldown(relPath, targetId);
        }
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span>📡</span>';
            btn.title = '向此渠道重新广播推流';
        }
        if (badgeEl) {
            badgeEl.className = 'dispatch-status-badge is-failed';
            badgeEl.innerHTML = '⚠️ 推送失败';
        }
        if (row) {
            row.classList.remove('is-running-row');
        }
        if (typeof showToast === 'function') {
            showToast('重新推送失败: ' + (err.message || '网络异常'), 'error');
        }
        if (typeof window.loadDispatchCenter === 'function') {
            await window.loadDispatchCenter('ledger');
        }
    }
};

/**
 * 重试单篇死信任务（带瞬态反馈）
 */
window.retrySingleDeadLetterTask = async function (relPath, targetId, btnId = null, cardId = null, langCode = 'zh-CN') {
    if (typeof apiFetch !== 'function') return;
    const btn = btnId ? document.getElementById(btnId) : null;
    const card = cardId ? document.getElementById(cardId) : null;
    if (btn) { btn.disabled = true; btn.innerHTML = '<span>⏳ 自愈重试中...</span>'; }
    if (card) { card.style.opacity = '0.7'; card.style.borderColor = 'var(--neon-cyan)'; }
    try {
        await apiFetch('/api/dispatch/deadletter/retry', {
            method: 'POST', body: JSON.stringify({ rel_path: relPath, target_id: targetId, lang_code: langCode })
        });
        if (typeof showToast === 'function') showToast('已下发自愈指令，正在连通目标渠道...', 'info');
        setTimeout(async () => {
            if (typeof window.loadDispatchCenter === 'function') await window.loadDispatchCenter('deadletter');
            if (typeof showToast === 'function') showToast('已同步最新分发大盘状态', 'success');
        }, 1200);
    } catch (e) {
        if (btn) { btn.disabled = false; btn.innerHTML = '<span>🔄 立即重试</span>'; }
        if (card) card.style.opacity = '1';
        if (typeof showToast === 'function') showToast('重试请求失败: ' + e.message, 'error');
    }
};

window.retryAllFailedTasks = async function () {
    if (typeof apiFetch !== 'function') return;
    const btn = document.getElementById('btn-batch-retry-all');
    if (btn) { btn.disabled = true; btn.innerHTML = '<span>⏳ 正在全量重试...</span>'; }
    try {
        await apiFetch('/api/dispatch/deadletter/retry', { method: 'POST', body: JSON.stringify({}) });
        if (typeof showToast === 'function') showToast('已加入全量自愈队列，正在调度...', 'info');
        setTimeout(async () => {
            if (typeof window.loadDispatchCenter === 'function') await window.loadDispatchCenter('deadletter');
            if (btn) { btn.disabled = false; btn.innerHTML = '<span id="btn-batch-retry-text">🔄 自愈</span>'; }
        }, 1500);
    } catch (e) {
        if (btn) { btn.disabled = false; btn.innerHTML = '<span id="btn-batch-retry-text">🔄 自愈</span>'; }
        if (typeof showToast === 'function') showToast('批量重试请求失败: ' + e.message, 'error');
    }
};

window.clearSingleDeadLetterTask = async function (relPath, targetId) {
    if (typeof apiFetch !== 'function') return;
    try {
        await apiFetch('/api/dispatch/deadletter/clear', {
            method: 'DELETE', body: JSON.stringify({ rel_path: relPath, target_id: targetId })
        });
        if (typeof showToast === 'function') showToast('已移出死信队列', 'info');
        if (typeof window.loadDispatchCenter === 'function') window.loadDispatchCenter('deadletter');
    } catch (e) {
        if (typeof showToast === 'function') showToast('清理失败: ' + e.message, 'error');
    }
};

/**
 * 本地实时过滤账本或死信（联动物理分页切片）
 */
window.filterDispatchLedger = function () {
    if (typeof window.initDispatchLedgerPagination === 'function' && window._dispatchLedgerCachedRecords) {
        window._dispatchLedgerCurrentPage = 1;
        window.initDispatchLedgerPagination();
    }
    const input = document.getElementById('dispatch-search-input');
    const filterLang = document.getElementById('dispatch-filter-lang');
    const filterChannel = document.getElementById('dispatch-filter-channel');
    
    const q = (input && input.value) ? input.value.trim().toLowerCase() : '';
    const selLang = (filterLang && filterLang.value) ? filterLang.value.trim().toLowerCase() : '';
    const selCh = (filterChannel && filterChannel.value) ? filterChannel.value.trim().toLowerCase() : '';

    if (filterLang) filterLang.classList.toggle('is-active', Boolean(selLang));
    if (filterChannel) filterChannel.classList.toggle('is-active', Boolean(selCh));

    document.querySelectorAll('.deadletter-card').forEach(c => {
        const title = c.getAttribute('data-title') || '', p = c.getAttribute('data-path') || '';
        const t = c.getAttribute('data-target') || '', tn = c.getAttribute('data-target-name') || '', l = c.getAttribute('data-lang') || '';
        
        let match = true;
        if (selLang && !l.includes(selLang)) match = false;
        if (selCh && t !== selCh) match = false;
        if (q && !(title.includes(q) || p.includes(q) || t.includes(q) || tn.includes(q) || l.includes(q))) match = false;

        c.style.display = match ? 'flex' : 'none';
    });
};

/**
 * 📥 [V123.0] 导出当前分发成果总账报表 (CSV 格式，UTF-8 带 BOM)
 */
window.exportDispatchLedgerCsv = function () {
    const list = window._dispatchLedgerCurrentFiltered || window._dispatchLedgerCachedRecords || [];
    if (!Array.isArray(list) || list.length === 0) {
        if (typeof showToast === 'function') {
            showToast('⚠️ 当前无分发成果记录可供导出', 'warning');
        }
        return;
    }

    // 1. 构建标准 CSV 表头
    const headers = [
        '稿件标题',
        '相对路径',
        '发布语种代码',
        '发布语种名称',
        '目标分发渠道ID',
        '目标分发渠道名称',
        '发布状态',
        '原稿更新状态',
        '线上文章链接',
        '发布时间',
        '异常排查信息'
    ];

    // CSV 安全转义处理
    const escapeCsv = (val) => {
        if (val === null || val === undefined) return '""';
        const str = String(val);
        if (str.includes('"') || str.includes(',') || str.includes('\n') || str.includes('\r')) {
            return `"${str.replace(/"/g, '""')}"`;
        }
        return `"${str}"`;
    };

    // 2. 逐行填充数据
    const rows = [headers.map(h => `"${h}"`).join(',')];

    list.forEach(rec => {
        const isFailed = (rec.status === 'failed' || Boolean(rec.error || rec.last_error));
        const statusText = isFailed ? '异常待自愈' : (rec.is_stale ? '待更新(原稿有新改动)' : '成功已发布');
        const staleText = rec.is_stale ? '本地原稿有更新' : '与原稿一致';
        const langMeta = (typeof _resolveLedgerLang === 'function')
            ? _resolveLedgerLang(rec.lang_code, rec.lang_name, rec.lang_icon)
            : { name: rec.lang_name || rec.lang_code, code: rec.lang_code };
        const chMeta = (typeof _resolveLedgerChannel === 'function')
            ? _resolveLedgerChannel(rec.target_id, rec.target_name, rec.target_icon)
            : { name: rec.target_name || rec.target_id };

        const row = [
            escapeCsv(rec.title || rec.rel_path || ''),
            escapeCsv(rec.rel_path || ''),
            escapeCsv(langMeta.code || rec.lang_code || ''),
            escapeCsv(langMeta.name || rec.lang_name || ''),
            escapeCsv(rec.target_id || ''),
            escapeCsv(chMeta.name || rec.target_name || ''),
            escapeCsv(statusText),
            escapeCsv(staleText),
            escapeCsv(rec.remote_url || ''),
            escapeCsv(rec.display_time || rec.updated_at || rec.failed_at || ''),
            escapeCsv(rec.error || rec.last_error || '')
        ];
        rows.push(row.join(','));
    });

    // 3. 生成带 UTF-8 BOM 的 CSV 字符串 (解决 Windows Excel 中文乱码)
    const csvContent = '\uFEFF' + rows.join('\r\n');
    if (typeof Blob === 'function' && typeof URL !== 'undefined' && typeof URL.createObjectURL === 'function') {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        
        // 生成带时间戳的文件名
        const d = new Date();
        const pad = (n) => String(n).padStart(2, '0');
        const dateStr = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
        const filename = `illacme_syndication_ledger_${dateStr}.csv`;

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    if (typeof showToast === 'function') {
        showToast(`✅ 已成功导出 ${list.length} 条分发总账记录至 CSV 报表！`, 'success');
    }
};
