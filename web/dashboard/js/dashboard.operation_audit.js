/**
 * 📜 [V50.3] Illacme Plenipes Operation Audit Logs UI Component
 * 职责：从 /api/governance/audit-logs 获取合规操作审计流水，
 *       并在「系统安全」Tab 中渲染精美、带分页与多重过滤筛选的操作日志表格。
 * 对应重构拆分协议：SOP-01 (单文件 300 行限额) 物理分流。
 */

window.loadAndRenderOperationAuditLogs = async () => {
    const container = document.getElementById('operation-audit-logs-container');
    if (!container) return;

    container.innerHTML = '<div class="loading">正在拉取合规审计账本，恢复物理操作轨迹...</div>';
    
    const activeImprint = window.settingsData?._active_imprint || 'default';
    const res = await apiFetch(`/api/governance/audit-logs?imprint_id=${activeImprint}`);
    
    if (!res || res.error) {
        container.innerHTML = `<div class="error-panel">❌ 操作审计日志加载失败: ${res ? res.error : 'API 连接异常'}</div>`;
        return;
    }

    window.renderOperationAuditLogs(res.logs || [], container);
};

window.renderOperationAuditLogs = (logs, container) => {
    // 1. 过滤和搜索选项
    const filterHtml = `
        <div class="filter-section mb-medium" style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center; background: var(--black-10); padding: 12px; border-radius: 6px; border: 1px solid var(--glass-border);">
            <div style="flex: 1; min-width: 200px; position: relative;">
                <input type="text" id="op-search-input" placeholder="🔍 输入关键字过滤操作详情或元数据..." style="width: 100%; background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 8px 12px; border-radius: 4px; font-size: 0.8rem;">
            </div>
            <div>
                <select id="op-type-filter" style="background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">
                    <option value="all">📁 所有事件类型</option>
                    <option value="PUBLISH_LAYOUT_CHANGED">🗺️ PUBLISH_LAYOUT_CHANGED (配置变更)</option>
                    <option value="COMPUTE_NODE_CALLED">⚡ COMPUTE_NODE_CALLED (算力调用)</option>
                    <option value="ENGINE_START">🚀 ENGINE_START (引擎点火)</option>
                    <option value="CONFIG_RELOADED">🔄 CONFIG_RELOADED (参数重载)</option>
                    <option value="GLOBAL_DEPLOY">🌍 GLOBAL_DEPLOY (全渠道分发)</option>
                </select>
            </div>
            <div>
                <select id="op-severity-filter" style="background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">
                    <option value="all">🚨 所有严重级别</option>
                    <option value="INFO">🔵 INFO (常规信息)</option>
                    <option value="WARNING">🟡 WARNING (高危警告)</option>
                    <option value="ERROR">🔴 ERROR (严重故障)</option>
                </select>
            </div>
        </div>
    `;

    // 2. 表格框架
    const tableHtml = `
        <div style="overflow-x: auto; border: 1px solid var(--glass-border); border-radius: 8px; background: rgba(0,0,0,0.15); backdrop-filter: blur(10px);">
            <table style="width: 100%; min-width: 950px; border-collapse: collapse; font-size: 0.8rem; text-align: left; table-layout: fixed;" id="op-audit-table">
                <thead>
                    <tr style="background: var(--black-20); border-bottom: 1px solid var(--glass-border); color: var(--text-dim);">
                        <th style="padding: 12px 16px; font-weight: 600; width: 140px;">时间戳</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 180px;">事件类型</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 80px;">级别</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 100px;">执行人</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 300px;">详情描述</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 150px;">元数据</th>
                    </tr>
                </thead>
                <tbody id="op-table-body">
                    <!-- 动态插入行 -->
                </tbody>
            </table>
        </div>
    `;

    let currentPage = 1;
    const PAGE_SIZE = 10;
    let filteredLogs = [...logs];

    container.innerHTML = `
        <div class="section-header mt-large"><h3>📜 物理操作合规审计账本 (Audit Trails)</h3></div>
        <p class="section-desc">持久化记录全量算力调用事件与版图/配置变更履历，提供商业级合规追溯证据。</p>
        ${filterHtml}
        ${tableHtml}
        <div id="op-pagination-container" class="pagination-container" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0 10px 0; flex-shrink: 0;"></div>
    `;

    const searchInput = document.getElementById('op-search-input');
    const typeFilter = document.getElementById('op-type-filter');
    const severityFilter = document.getElementById('op-severity-filter');

    const updateFilter = () => {
        const query = searchInput.value.toLowerCase().trim();
        const typeVal = typeFilter.value;
        const sevVal = severityFilter.value;

        filteredLogs = logs.filter(log => {
            const detailsMatch = (log.details || '').toLowerCase().includes(query) || (log.metadata || '').toLowerCase().includes(query);
            const typeMatch = (typeVal === 'all' || log.event_type === typeVal);
            const sevMatch = (sevVal === 'all' || log.severity === sevVal);
            return detailsMatch && typeMatch && sevMatch;
        });

        currentPage = 1;
        renderPage();
    };

    searchInput.addEventListener('input', updateFilter);
    typeFilter.addEventListener('change', updateFilter);
    severityFilter.addEventListener('change', updateFilter);

    const renderRows = (pageLogs) => {
        const tbody = document.getElementById('op-table-body');
        if (!tbody) return;

        if (pageLogs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="padding: 32px; text-align: center; color: var(--text-dim);">
                        没有匹配到任何审计流水记录。
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = pageLogs.map(log => {
            let displayTime = log.timestamp || '-';
            try {
                const dt = new Date(log.timestamp.replace(' ', 'T') + (log.timestamp.includes('Z') ? '' : 'Z'));
                displayTime = dt.toLocaleString('zh-CN', {hour12: false});
            } catch(e) {}

            let typeBadge = '';
            if (log.event_type === 'COMPUTE_NODE_CALLED') {
                typeBadge = '<span style="background: rgba(0, 242, 255, 0.15); color: #00f2ff; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(0, 242, 255, 0.3);">⚡ COMPUTE_NODE</span>';
            } else if (log.event_type === 'PUBLISH_LAYOUT_CHANGED') {
                typeBadge = '<span style="background: rgba(255, 0, 255, 0.15); color: #ff00ff; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(255, 0, 255, 0.3);">🗺️ LAYOUT_CHANGED</span>';
            } else {
                typeBadge = `<span style="background: rgba(255,255,255,0.08); color: var(--text-bright); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; border: 1px solid rgba(255,255,255,0.15);">${log.event_type}</span>`;
            }

            let sevBadge = '';
            if (log.severity === 'ERROR') {
                sevBadge = '<span style="color: #ff4d4d; font-weight: 700; background: rgba(255,77,77,0.15); padding: 1px 4px; border-radius: 3px; border: 1px solid rgba(255,77,77,0.3);">ERROR</span>';
            } else if (log.severity === 'WARNING') {
                sevBadge = '<span style="color: #ffaa00; font-weight: 600; background: rgba(255,170,0,0.12); padding: 1px 4px; border-radius: 3px; border: 1px solid rgba(255,170,0,0.25);">WARN</span>';
            } else {
                sevBadge = '<span style="color: #32cd32; font-weight: 500;">INFO</span>';
            }

            let metaHtml = '-';
            if (log.metadata) {
                try {
                    const parsed = typeof log.metadata === 'string' ? JSON.parse(log.metadata) : log.metadata;
                    if (Object.keys(parsed).length > 0) {
                        const str = JSON.stringify(parsed, null, 2);
                        metaHtml = `
                            <details style="cursor: pointer; font-family: monospace; font-size: 0.65rem;">
                                <summary style="color: var(--accent-secondary, #00bfff); outline: none;">展开 (${Object.keys(parsed).length} 属性)</summary>
                                <pre style="background: rgba(0,0,0,0.3); padding: 6px; border-radius: 4px; margin-top: 4px; color: var(--text-dim); overflow-x: auto; white-space: pre-wrap; word-break: break-all;">${str}</pre>
                            </details>
                        `;
                    }
                } catch(e) {}
            }

            const rowStyle = log.severity === 'ERROR' ? 'background: rgba(255, 77, 77, 0.02); border-bottom: 1px solid rgba(255, 77, 77, 0.1);' : 'border-bottom: 1px solid var(--glass-border);';

            return `
                <tr style="${rowStyle}" class="table-row-hover">
                    <td style="padding: 12px 16px; color: var(--text-dim); font-size: 0.75rem;">${displayTime}</td>
                    <td style="padding: 12px 16px;">${typeBadge}</td>
                    <td style="padding: 12px 16px; font-size: 0.75rem;">${sevBadge}</td>
                    <td style="padding: 12px 16px; font-weight: 600; color: var(--text-bright); font-size: 0.75rem;">${log.actor}</td>
                    <td style="padding: 12px 16px; color: var(--text-primary); font-size: 0.75rem; word-break: break-all;" title="${log.details}">${log.details}</td>
                    <td style="padding: 12px 16px;">${metaHtml}</td>
                </tr>
            `;
        }).join('');
    };

    const renderPaginationDOM = () => {
        const pagContainer = document.getElementById('op-pagination-container');
        if (!pagContainer) return;

        const totalItems = filteredLogs.length;
        const totalPages = Math.ceil(totalItems / PAGE_SIZE) || 1;

        if (totalItems === 0) {
            pagContainer.style.display = 'none';
            return;
        }
        pagContainer.style.display = 'flex';

        const firstDisabled = currentPage === 1 ? 'disabled' : '';
        const prevDisabled = currentPage === 1 ? 'disabled' : '';
        const nextDisabled = currentPage === totalPages ? 'disabled' : '';
        const lastDisabled = currentPage === totalPages ? 'disabled' : '';

        pagContainer.innerHTML = `
            <span style="font-size: 0.8rem; color: var(--text-dim);">
                第 ${currentPage} 页 / 共 ${totalPages} 页，共 <strong>${totalItems}</strong> 条审计流水
            </span>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="display: flex; gap: 6px;">
                    <button id="op-first-btn" class="mini-btn" ${firstDisabled}>首页</button>
                    <button id="op-prev-btn" class="mini-btn" ${prevDisabled}>◀ 上一页</button>
                    <button id="op-next-btn" class="mini-btn" ${nextDisabled}>下一页 ▶</button>
                    <button id="op-last-btn" class="mini-btn" ${lastDisabled}>尾页</button>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 12px;">
                    <span style="font-size: 0.8rem; color: var(--text-dim);">跳转</span>
                    <input type="number" id="op-go-page-input" min="1" max="${totalPages}" value="${currentPage}" style="width: 55px; height: 28px; padding: 0 4px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.05); color: var(--text-bright); border-radius: 4px; text-align: center; font-size: 0.8rem; box-sizing: border-box; outline: none; transition: border-color 0.2s;" placeholder="页">
                    <button id="op-go-page-btn" class="mini-btn" style="height: 28px; line-height: 14px;">跳转</button>
                </div>
            </div>
        `;

        document.getElementById('op-first-btn').addEventListener('click', () => {
            if (currentPage !== 1) {
                currentPage = 1;
                renderPage();
            }
        });

        document.getElementById('op-prev-btn').addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderPage();
            }
        });

        document.getElementById('op-next-btn').addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderPage();
            }
        });

        document.getElementById('op-last-btn').addEventListener('click', () => {
            if (currentPage !== totalPages) {
                currentPage = totalPages;
                renderPage();
            }
        });

        const goPage = () => {
            const input = document.getElementById('op-go-page-input');
            const targetPage = parseInt(input.value);
            if (targetPage >= 1 && targetPage <= totalPages) {
                currentPage = targetPage;
                renderPage();
            }
        };

        document.getElementById('op-go-page-btn').addEventListener('click', goPage);
        document.getElementById('op-go-page-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                goPage();
            }
        });
    };

    const renderPage = () => {
        const start = (currentPage - 1) * PAGE_SIZE;
        const pageLogs = filteredLogs.slice(start, start + PAGE_SIZE);
        renderRows(pageLogs);
        renderPaginationDOM();
    };

    updateFilter();
};
