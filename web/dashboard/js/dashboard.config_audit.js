/**
 * 🛡️ [V74.57] Illacme Plenipes Configuration Auditing & Topology Visualizer
 * 职责：负责在 Dashboard 渲染配置的三层继承关系、生效来源高亮与凭据明文脱敏安全警报。
 */

window.loadAndRenderConfigAudit = async () => {
    const container = document.getElementById('config-audit-topology-container');
    if (!container) return;

    container.innerHTML = '<div class="loading">正在全量嗅探三层配置继承拓扑并进行安全合规性审计...</div>';
    
    // 动态提取当前活跃品牌
    const activeImprint = window.settingsData?._active_imprint || 'default';
    const res = await apiFetch(`/api/config/audit?imprint_id=${activeImprint}`);
    
    if (!res || res.error) {
        container.innerHTML = `<div class="error-panel">❌ 拓扑审计加载失败: ${res ? res.error : '物理链路异常'}</div>`;
        return;
    }

    window.renderConfigAuditTopology(res, container);
};

window.renderConfigAuditTopology = (data, container) => {
    // 1. 安全警报卡片
    let alertHtml = '';
    if (data.summary.cleartext_issues > 0) {
        alertHtml = `
            <div class="glass-panel alert-card critical-alert mb-medium font-fade-in" style="border-left: 4px solid var(--accent-critical, #ff4d4d); background: rgba(255, 77, 77, 0.08); padding: 16px; border-radius: 8px;">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <span style="font-size: 1.5rem;">🚨</span>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 6px 0; color: var(--accent-critical, #ff4d4d); font-weight: 700;">严重凭据安全风险</h4>
                        <p style="margin: 0 0 10px 0; font-size: 0.8rem; line-height: 1.4; color: var(--text-primary);">
                            系统在当前继承配置中检测到 <strong>${data.summary.cleartext_issues}</strong> 处未加密的明文敏感密钥或凭据！这些密钥可能在协作或发布时意外泄露。
                        </p>
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <span style="font-size: 0.75rem; color: var(--text-dim);">建议立即在物理终端执行：</span>
                            <code style="background: var(--black-20); padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 0.75rem; color: var(--accent-secondary);">python3 plenipes.py --credentials</code>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // 2. 筛选项容器
    const filterHtml = `
        <div class="filter-section mb-medium" style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center; background: var(--black-10); padding: 12px; border-radius: 6px; border: 1px solid var(--glass-border);">
            <div style="flex: 1; min-width: 200px; position: relative;">
                <input type="text" id="audit-search-input" placeholder="🔍 输入关键字过滤配置路径..." style="width: 100%; background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 8px 12px; border-radius: 4px; font-size: 0.8rem;">
            </div>
            <div>
                <select id="audit-source-filter" style="background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">
                    <option value="all">📁 所有决策来源 (全部)</option>
                    <option value="global">🔵 GLOBAL (底座继承)</option>
                    <option value="local">🟢 LOCAL (本地覆盖)</option>
                    <option value="imprint">🔴 IMPRINT (品牌意志)</option>
                </select>
            </div>
            <div>
                <select id="audit-security-filter" style="background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">
                    <option value="all">🔒 所有安全状态 (全部)</option>
                    <option value="encrypted">🟢 🔒 已加密</option>
                    <option value="cleartext">🔴 ⚠️ 明文泄漏风险</option>
                    <option value="none">⚪ 普通配置字段</option>
                </select>
            </div>
        </div>
    `;

    // 3. 拓扑图对比表框架
    // 3. 拓扑图对比表框架
    const tableHtml = `
        <div style="overflow-x: auto; border: 1px solid var(--glass-border); border-radius: 8px; background: rgba(0,0,0,0.15); backdrop-filter: blur(10px);">
            <table style="width: 100%; min-width: 950px; border-collapse: collapse; font-size: 0.8rem; text-align: left; table-layout: fixed;" id="audit-topology-table">
                <thead>
                    <tr style="background: var(--black-20); border-bottom: 1px solid var(--glass-border); color: var(--text-dim);">
                        <th style="padding: 12px 16px; font-weight: 600; width: 230px;">配置键路径</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 100px;">决策来源</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 100px;">安全等级</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 130px;">GLOBAL 原始</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 130px;">IMPRINT 原始</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 130px;">LOCAL 原始</th>
                        <th style="padding: 12px 16px; font-weight: 600; width: 130px;">当前生效值</th>
                    </tr>
                </thead>
                <tbody id="audit-table-body">
                    <!-- 动态插入行 -->
                </tbody>
            </table>
        </div>
    `;

    let currentPage = 1;
    const PAGE_SIZE = 10;
    let filteredItems = [...data.items];

    container.innerHTML = `
        <div class="section-header mt-large"><h3>📡 配置拓扑与安全审计 (Configuration Auditing)</h3></div>
        <p class="section-desc">深度展现全局、品牌主权及本地物理层级合并的最终决策，识别安全隐患。</p>
        ${alertHtml}
        ${filterHtml}
        ${tableHtml}
        <div id="audit-pagination-container" class="pagination-container" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0 10px 0; flex-shrink: 0;"></div>
    `;

    // 绑定过滤处理器
    const searchInput = document.getElementById('audit-search-input');
    const sourceFilter = document.getElementById('audit-source-filter');
    const securityFilter = document.getElementById('audit-security-filter');

    const updateFilter = () => {
        const query = searchInput.value.toLowerCase().trim();
        const srcVal = sourceFilter.value;
        const secVal = securityFilter.value;

        filteredItems = data.items.filter(item => {
            const matchesQuery = item.key.toLowerCase().includes(query);
            const matchesSource = (srcVal === 'all' || item.source === srcVal);
            const matchesSecurity = (secVal === 'all' || item.security_status === secVal);
            return matchesQuery && matchesSource && matchesSecurity;
        });

        currentPage = 1;
        renderPage();
    };

    searchInput.addEventListener('input', updateFilter);
    sourceFilter.addEventListener('change', updateFilter);
    securityFilter.addEventListener('change', updateFilter);

    // 行渲染逻辑
    const renderRows = (items) => {
        const tbody = document.getElementById('audit-table-body');
        if (!tbody) return;

        if (items.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="padding: 32px; text-align: center; color: var(--text-dim);">
                        没有匹配到任何符合条件的配置路径。
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = items.map(item => {
            // 来源标签
            let srcBadge = '';
            if (item.source === 'global') {
                srcBadge = '<span style="background: rgba(0, 191, 255, 0.15); color: #00bfff; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(0, 191, 255, 0.3);">GLOBAL</span>';
            } else if (item.source === 'local') {
                srcBadge = '<span style="background: rgba(50, 205, 50, 0.15); color: #32cd32; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(50, 205, 50, 0.3);">LOCAL</span>';
            } else if (item.source === 'imprint') {
                srcBadge = '<span style="background: rgba(255, 0, 255, 0.15); color: #ff00ff; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(255, 0, 255, 0.3);">IMPRINT</span>';
            } else {
                srcBadge = `<span style="background: var(--black-20); color: var(--text-dim); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">${item.source.toUpperCase()}</span>`;
            }

            // 安全等级标签
            let secLabel = '';
            if (item.security_status === 'encrypted') {
                secLabel = '<span style="color: #32cd32; font-weight: 600;">🔒 已加密</span>';
            } else if (item.security_status === 'cleartext') {
                secLabel = '<span style="color: var(--accent-critical, #ff4d4d); font-weight: 700; animation: blink 1.5s infinite;">⚠️ 明文泄漏</span>';
            } else {
                secLabel = '<span style="color: var(--text-dim);">普通字段</span>';
            }

            // 高亮层级处理 (使用柔和的半透明高亮底色和色彩，摒弃生硬粗鲁的单元格 outline 边线)
            const hlStyle = 'background: rgba(0, 191, 255, 0.08); color: var(--accent-secondary, #00bfff); font-weight: 600;';
            const globalHl = item.source === 'global' ? hlStyle : '';
            const imprintHl = item.source === 'imprint' ? hlStyle : '';
            const localHl = item.source === 'local' ? hlStyle : '';

            // 安全防崩：若是明文敏感，显示红色
            const isCritical = item.security_status === 'cleartext';
            const rowStyle = isCritical ? 'background: rgba(255, 77, 77, 0.03); border-bottom: 1px solid rgba(255, 77, 77, 0.15);' : 'border-bottom: 1px solid var(--glass-border);';

            return `
                <tr style="${rowStyle}" class="table-row-hover">
                    <td style="padding: 12px 16px; font-family: monospace; font-size: 0.75rem; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${item.key}">${item.key}</td>
                    <td style="padding: 12px 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${srcBadge}</td>
                    <td style="padding: 12px 16px; font-size: 0.75rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${secLabel}</td>
                    <td style="padding: 12px 16px; font-family: monospace; font-size: 0.75rem; color: var(--text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; ${globalHl}" title="${item.global_val || '-'}">${item.global_val || '-'}</td>
                    <td style="padding: 12px 16px; font-family: monospace; font-size: 0.75rem; color: var(--text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; ${imprintHl}" title="${item.imprint_val || '-'}">${item.imprint_val || '-'}</td>
                    <td style="padding: 12px 16px; font-family: monospace; font-size: 0.75rem; color: var(--text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; ${localHl}" title="${item.local_val || '-'}">${item.local_val || '-'}</td>
                    <td style="padding: 12px 16px; font-family: monospace; font-size: 0.75rem; color: var(--accent-secondary, #00bfff); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${item.merged_val || '-'}">${item.merged_val || '-'}</td>
                </tr>
            `;
        }).join('');
    };

    // 渲染分页 DOM 的逻辑 (完全复刻原稿文库列表底栏的呈现和交互方式)
    const renderPaginationDOM = () => {
        const pagContainer = document.getElementById('audit-pagination-container');
        if (!pagContainer) return;

        const totalItems = filteredItems.length;
        const totalPages = Math.ceil(totalItems / PAGE_SIZE) || 1;

        if (totalItems === 0) {
            pagContainer.style.display = 'none';
            return;
        }
        pagContainer.style.display = 'flex';

        const startIdx = (currentPage - 1) * PAGE_SIZE + 1;
        const endIdx = Math.min(currentPage * PAGE_SIZE, totalItems);

        const firstDisabled = currentPage === 1 ? 'disabled' : '';
        const prevDisabled = currentPage === 1 ? 'disabled' : '';
        const nextDisabled = currentPage === totalPages ? 'disabled' : '';
        const lastDisabled = currentPage === totalPages ? 'disabled' : '';

        pagContainer.innerHTML = `
            <span style="font-size: 0.8rem; color: var(--text-dim);">
                第 ${currentPage} 页 / 共 ${totalPages} 页，共 <strong>${totalItems}</strong> 条配置项
            </span>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="display: flex; gap: 6px;">
                    <button id="audit-first-btn" class="mini-btn" ${firstDisabled}>首页</button>
                    <button id="audit-prev-btn" class="mini-btn" ${prevDisabled}>◀ 上一页</button>
                    <button id="audit-next-btn" class="mini-btn" ${nextDisabled}>下一页 ▶</button>
                    <button id="audit-last-btn" class="mini-btn" ${lastDisabled}>尾页</button>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 12px;">
                    <span style="font-size: 0.8rem; color: var(--text-dim);">跳转至</span>
                    <input type="number" id="audit-go-page-input" min="1" max="${totalPages}" value="${currentPage}" style="width: 55px; height: 28px; padding: 0 4px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.05); color: var(--text-bright); border-radius: 4px; text-align: center; font-size: 0.8rem; box-sizing: border-box; outline: none; transition: border-color 0.2s;" placeholder="页">
                    <button id="audit-go-page-btn" class="mini-btn" style="height: 28px; line-height: 14px;">跳转</button>
                </div>
            </div>
        `;

        // 绑定第一页/上一页/下一页/尾页事件
        document.getElementById('audit-first-btn').addEventListener('click', () => {
            if (currentPage !== 1) {
                currentPage = 1;
                renderPage();
            }
        });

        document.getElementById('audit-prev-btn').addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderPage();
            }
        });

        document.getElementById('audit-next-btn').addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderPage();
            }
        });

        document.getElementById('audit-last-btn').addEventListener('click', () => {
            if (currentPage !== totalPages) {
                currentPage = totalPages;
                renderPage();
            }
        });

        // 绑定跳转事件
        const goPage = () => {
            const input = document.getElementById('audit-go-page-input');
            const targetPage = parseInt(input.value);
            if (targetPage >= 1 && targetPage <= totalPages) {
                currentPage = targetPage;
                renderPage();
            }
        };

        document.getElementById('audit-go-page-btn').addEventListener('click', goPage);
        document.getElementById('audit-go-page-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                goPage();
            }
        });
    };

    // 渲染指定页的数据
    const renderPage = () => {
        const start = (currentPage - 1) * PAGE_SIZE;
        const pageItems = filteredItems.slice(start, start + PAGE_SIZE);
        renderRows(pageItems);
        renderPaginationDOM();
    };

    updateFilter();
};
