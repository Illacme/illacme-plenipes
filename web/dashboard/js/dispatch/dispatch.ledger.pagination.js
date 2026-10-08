/**
 * 🚀 [V123.0] Illacme Plenipes - Dispatch Ledger Pagination Controller
 * 职责：分发成果账本物理分页、页容量切换（10/25/50）、搜索过滤联动与分页指示器渲染。
 * 🛡️ [SOP-01 / SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

window._dispatchLedgerCurrentPage = 1;
window._dispatchLedgerPageSize = 10;
window._dispatchLedgerCachedRecords = [];

const _canonicalLangKey = (code) => {
    if (!code) return '';
    const c = String(code).trim().toLowerCase();
    // 过滤已知非法语种代码 / 目录名脏数据
    if (['docs', 'doc', 'blog', 'blogs', 'pages', 'unknown', 'undefined', 'null'].includes(c)) return '';
    // 归一化简体中文
    if (['zh', 'zh-hans', 'zh-cn', 'zh-sg', 'cmn', 'cmn-hans'].includes(c)) return 'zh-hans';
    // 归一化繁体中文
    if (['zh-hant', 'zh-tw', 'zh-hk', 'cmn-hant'].includes(c)) return 'zh-hant';
    return c;
};

const HOSTING_TARGET_IDS = new Set([
    'github_pages', 'cloudflare_pages', 'vercel', 'netlify', 
    'sftp', 'render', 'railway', 'zeabur', 'supabase', 'aws_s3', 'oss', 'cos', 'upyun_uss',
    'gitee_pages', 'gitlab_pages', 'coding_pages', 'firebase'
]);

const _resolveChannelType = (targetId, explicitType) => {
    if (explicitType === 'hosting' || explicitType === 'social') return explicitType;
    const tid = String(targetId || '').trim().toLowerCase();
    if (HOSTING_TARGET_IDS.has(tid)) return 'hosting';
    return 'social';
};

/**
 * 🛰️ 从全域插件中心矩阵与品牌徽章字典动态萃取官方名称与图标 (SSOT)
 */
const _resolvePluginChannelMeta = (targetId, targetType, rawName, rawIcon) => {
    const tid = String(targetId || '').trim().toLowerCase();
    const cleanId = tid.replace(/[_-\s]/g, '');
    const cType = _resolveChannelType(tid, targetType);

    // 1. 优先从全局插件底座 window.allPlugins 中精准匹配
    let pluginObj = null;
    if (Array.isArray(window.allPlugins) && window.allPlugins.length > 0) {
        pluginObj = window.allPlugins.find(p => {
            const pid = (p.id || '').toLowerCase();
            return pid === tid || pid.replace(/[_-\s]/g, '') === cleanId;
        });
    }

    // 2. 调取平台品牌专属徽章字典 (getPlatformBrandBadge)
    const brand = (typeof window.getPlatformBrandBadge === 'function')
        ? window.getPlatformBrandBadge(tid, cType === 'hosting' ? 'hosting' : 'publisher')
        : null;

    // 3. 调取全域社媒分发元数据字典 (getSyndicateChannelMeta)
    const synMeta = (typeof window.getSyndicateChannelMeta === 'function')
        ? window.getSyndicateChannelMeta(tid)
        : null;

    // 确定官方名称：优先 plugin.name -> rawName -> synMeta.name -> 格式化回退
    let finalName = (pluginObj && pluginObj.name) || rawName || (synMeta && synMeta.name);
    if (!finalName || finalName === tid) {
        finalName = tid.replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    // 确定官方图标：优先从品牌徽章字典解析专属图标，杜绝被泛用 🌐 / 🏷️ 覆盖
    let finalIcon = (brand && brand.icon && brand.icon !== '🌐') ? brand.icon : null;
    if (!finalIcon && pluginObj && pluginObj.icon && pluginObj.icon !== '🌐') {
        finalIcon = pluginObj.icon;
    }
    if (!finalIcon && synMeta && synMeta.icon && synMeta.icon !== '📡') {
        finalIcon = synMeta.icon;
    }
    if (!finalIcon && rawIcon && rawIcon !== '🌐' && rawIcon !== '🏷️') {
        finalIcon = rawIcon;
    }
    if (!finalIcon) {
        finalIcon = (brand && brand.icon) || (cType === 'hosting' ? '🌐' : '📡');
    }

    return {
        id: tid,
        name: finalName,
        icon: finalIcon,
        type: cType
    };
};

/**
 * 动态提取并填充账本可筛选的语种与渠道选项（保持选中状态）
 */
window.populateDispatchFilters = function (records) {
    const langSelect = document.getElementById('dispatch-filter-lang');
    const chSelect = document.getElementById('dispatch-filter-channel');
    if (!langSelect || !chSelect) return;

    // 异步触发全域插件底座静默预载
    if (!window.allPlugins || window.allPlugins.length === 0) {
        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        fetchApi('/api/plugins/list').then(res => {
            if (res && Array.isArray(res.plugins)) {
                window.allPlugins = res.plugins;
            }
        }).catch(() => {});
    }

    const currentLang = (langSelect.value || '').trim();
    const currentCh = (chSelect.value || '').trim();

    const langMap = new Map();
    const chMap = new Map();

    // 1. 优先从全局渠道健康矩阵中收集所有已启用的渠道（100% 走插件矩阵元数据解析）
    const overview = window._lastDispatchOverview || {};
    const health = overview.channel_health || [];
    health.forEach(c => {
        if (c.id) {
            const meta = _resolvePluginChannelMeta(c.id, c.type, c.name, c.icon);
            chMap.set(c.id, meta);
        }
    });

    // 2. 从分发成果记录中提取语种与渠道（严格执行标准代码归一化去重与插件矩阵对齐）
    const all = Array.isArray(records) ? records : (window._dispatchLedgerCachedRecords || []);
    all.forEach(r => {
        if (r.lang_code) {
            const canonicalKey = _canonicalLangKey(r.lang_code);
            if (canonicalKey && !langMap.has(canonicalKey)) {
                const meta = (typeof window.getLanguageMeta === 'function')
                    ? window.getLanguageMeta(canonicalKey)
                    : null;
                const name = (meta && meta.name) || r.lang_name || canonicalKey;
                const icon = (meta && meta.icon) || r.lang_icon || '🌐';
                langMap.set(canonicalKey, { code: canonicalKey, name, icon });
            }
        }
        if (r.target_id && !chMap.has(r.target_id)) {
            const meta = _resolvePluginChannelMeta(r.target_id, r.target_type, r.target_name, r.target_icon);
            chMap.set(r.target_id, meta);
        }
    });

    // 3. 从死信任务中补充提取语种与渠道
    const deadLetters = overview.dead_letter_tasks || [];
    deadLetters.forEach(d => {
        if (d.lang_code) {
            const canonicalKey = _canonicalLangKey(d.lang_code);
            if (canonicalKey && !langMap.has(canonicalKey)) {
                const meta = (typeof window.getLanguageMeta === 'function') ? window.getLanguageMeta(canonicalKey) : null;
                const name = (meta && meta.name) || d.lang_name || canonicalKey;
                const icon = (meta && meta.icon) || d.lang_icon || '🌐';
                langMap.set(canonicalKey, { code: canonicalKey, name, icon });
            }
        }
        if (d.target_id && !chMap.has(d.target_id)) {
            const meta = _resolvePluginChannelMeta(d.target_id, d.target_type, d.target_name, d.target_icon);
            chMap.set(d.target_id, meta);
        }
    });

    window._dispatchChannelTypeMap = chMap;

    let langHtml = '<option value="">🌐 全部语种</option>';
    const canonicalCurrentLang = _canonicalLangKey(currentLang) || currentLang.toLowerCase();
    Array.from(langMap.values()).sort((a, b) => a.name.localeCompare(b.name)).forEach(item => {
        const isSel = (item.code.toLowerCase() === canonicalCurrentLang);
        langHtml += `<option value="${item.code}" ${isSel ? 'selected' : ''}>${item.icon} ${item.name}</option>`;
    });
    langSelect.innerHTML = langHtml;

    // 统计当前流水中两类渠道的任务数量
    let hostingCount = 0;
    let socialCount = 0;
    all.forEach(r => {
        const cType = _resolveChannelType(r.target_id, r.target_type || chMap.get(r.target_id)?.type);
        if (cType === 'hosting') hostingCount++;
        else socialCount++;
    });

    const hostingList = [];
    const socialList = [];
    chMap.forEach(ch => {
        if (ch.type === 'hosting') hostingList.push(ch);
        else socialList.push(ch);
    });
    hostingList.sort((a, b) => a.name.localeCompare(b.name));
    socialList.sort((a, b) => a.name.localeCompare(b.name));

    let chHtml = '<option value="">🏷️ 全部渠道</option>';
    chHtml += `<option value="__type:hosting" ${currentCh === '__type:hosting' ? 'selected' : ''}>🌐 仅看全站托管 (${hostingCount})</option>`;
    chHtml += `<option value="__type:social" ${currentCh === '__type:social' ? 'selected' : ''}>📡 仅看社媒分发 (${socialCount})</option>`;

    if (hostingList.length > 0) {
        chHtml += '<optgroup label="── 🌐 全站托管 (Hosting) ──">';
        hostingList.forEach(item => {
            const isSel = (item.id.toLowerCase() === currentCh.toLowerCase());
            chHtml += `<option value="${item.id}" ${isSel ? 'selected' : ''}>${item.icon} ${item.name}</option>`;
        });
        chHtml += '</optgroup>';
    }

    if (socialList.length > 0) {
        chHtml += '<optgroup label="── 📡 社媒分发 (Syndication) ──">';
        socialList.forEach(item => {
            const isSel = (item.id.toLowerCase() === currentCh.toLowerCase());
            chHtml += `<option value="${item.id}" ${isSel ? 'selected' : ''}>${item.icon} ${item.name}</option>`;
        });
        chHtml += '</optgroup>';
    }
    chSelect.innerHTML = chHtml;
};

/**
 * 初始化或重刷账本物理分页（支持多维交集组合筛选）
 */
window.initDispatchLedgerPagination = function (records) {
    if (Array.isArray(records)) {
        window._dispatchLedgerCachedRecords = records;
        window.populateDispatchFilters(records);
    }
    const all = window._dispatchLedgerCachedRecords || [];
    
    // 获取当前检索关键词与多维筛选项
    const input = document.getElementById('dispatch-search-input');
    const query = (input && input.value) ? input.value.trim().toLowerCase() : '';

    const langSelect = document.getElementById('dispatch-filter-lang');
    const chSelect = document.getElementById('dispatch-filter-channel');
    const statusSelect = document.getElementById('dispatch-filter-status');
    const btnBatchRetry = document.getElementById('btn-batch-retry-all');

    const selLang = (langSelect && langSelect.value) ? langSelect.value.trim().toLowerCase() : '';
    const selChannel = (chSelect && chSelect.value) ? chSelect.value.trim().toLowerCase() : '';
    const selStatus = (statusSelect && statusSelect.value) ? statusSelect.value.trim().toLowerCase() : '';

    // 动态高亮处于激活态的筛选项
    if (langSelect) langSelect.classList.toggle('is-active', Boolean(selLang));
    if (chSelect) chSelect.classList.toggle('is-active', Boolean(selChannel));
    if (statusSelect) statusSelect.classList.toggle('is-active', Boolean(selStatus));
    
    const filtered = all.filter(r => {
        // 1. 发布状态过滤（success / failed）
        if (selStatus) {
            const rStatus = (r.status || (r.error ? 'failed' : 'success')).toLowerCase();
            if (rStatus !== selStatus) return false;
        }

        // 2. 语种精准或前缀匹配（引入归一化双向兼容，兼容历史 zh / zh-hans / zh-cn 数据）
        if (selLang) {
            const rLang = (r.lang_code || '').toLowerCase();
            const rCanonical = _canonicalLangKey(rLang);
            const rName = (r.lang_name || '').toLowerCase();
            const isMatch = (rCanonical === selLang) ||
                            (rLang === selLang) ||
                            (rLang.startsWith(selLang)) ||
                            (selLang.startsWith(rLang)) ||
                            (rName.includes(selLang));
            if (!isMatch) {
                return false;
            }
        }

        // 3. 目标渠道匹配（支持宏观分类 __type:hosting / __type:social 以及具体渠道 ID）
        if (selChannel) {
            const rTarget = (r.target_id || '').toLowerCase();
            const rType = _resolveChannelType(r.target_id, r.target_type || (window._dispatchChannelTypeMap && window._dispatchChannelTypeMap.get(r.target_id)?.type));
            if (selChannel === '__type:hosting') {
                if (rType !== 'hosting') return false;
            } else if (selChannel === '__type:social') {
                if (rType !== 'social') return false;
            } else {
                if (rTarget !== selChannel) return false;
            }
        }

        // 4. 关键词模糊检索（标题、路径、渠道名、语种名、错误原因）
        if (query) {
            const title = (r.title || '').toLowerCase();
            const p = (r.rel_path || '').toLowerCase();
            const t = (r.target_id || '').toLowerCase();
            const tn = (r.target_name || '').toLowerCase();
            const l = (r.lang_code || '').toLowerCase();
            const ln = (r.lang_name || '').toLowerCase();
            const err = (r.error || r.last_error || '').toLowerCase();
            if (!title.includes(query) && !p.includes(query) && !t.includes(query) && !tn.includes(query) && !l.includes(query) && !ln.includes(query) && !err.includes(query)) {
                return false;
            }
        }

        return true;
    });

    // 动态显隐【一键重试所有失败】按钮
    if (btnBatchRetry) {
        const hasFailedInFiltered = filtered.some(r => r.status === 'failed' || Boolean(r.error));
        btnBatchRetry.style.display = hasFailedInFiltered ? 'inline-flex' : 'none';
    }

    const totalItems = filtered.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / window._dispatchLedgerPageSize));
    
    if (window._dispatchLedgerCurrentPage > totalPages) {
        window._dispatchLedgerCurrentPage = totalPages;
    }
    if (window._dispatchLedgerCurrentPage < 1) {
        window._dispatchLedgerCurrentPage = 1;
    }

    const startIdx = (window._dispatchLedgerCurrentPage - 1) * window._dispatchLedgerPageSize;
    const endIdx = startIdx + window._dispatchLedgerPageSize;
    const pagedRecords = filtered.slice(startIdx, endIdx);

    // 触发实际的表格渲染器
    if (typeof window.renderDispatchLedgerTable === 'function') {
        window.renderDispatchLedgerTable(pagedRecords, totalItems, window._dispatchLedgerCurrentPage, totalPages, query || selLang || selChannel);
    }
};

/**
 * 切换当前页码
 */
window.changeDispatchLedgerPage = function (page) {
    const p = Number(page);
    if (isNaN(p) || p < 1) return;
    window._dispatchLedgerCurrentPage = p;
    window.initDispatchLedgerPagination();
};

/**
 * 切换每页展示条数
 */
window.changeDispatchLedgerPageSize = function (size) {
    const s = Number(size) || 10;
    window._dispatchLedgerPageSize = s;
    window._dispatchLedgerCurrentPage = 1;
    window.initDispatchLedgerPagination();
};

/**
 * 生成高保真分页控制中枢 HTML
 */
window.buildDispatchLedgerPaginationHtml = function (totalItems, currentPage, totalPages, pageSize) {
    if (totalItems <= 0) return '';

    const isFirst = currentPage <= 1;
    const isLast = currentPage >= totalPages;

    return `
        <div class="pagination-container dispatch-ledger-pagination">
            <div class="ledger-pag-meta">
                <span>第 <strong class="ledger-pag-active-page">${currentPage}</strong> / ${totalPages} 页</span>
                <span class="ledger-pag-divider">·</span>
                <span>共 <strong class="ledger-pag-total-items">${totalItems}</strong> 项任务</span>
                <div class="ledger-pag-size-selector">
                    <span class="ledger-pag-label">每页</span>
                    <select class="mini-select ledger-page-size-select" onchange="window.changeDispatchLedgerPageSize(this.value)">
                        <option value="10" ${pageSize === 10 ? 'selected' : ''}>10</option>
                        <option value="25" ${pageSize === 25 ? 'selected' : ''}>25</option>
                        <option value="50" ${pageSize === 50 ? 'selected' : ''}>50</option>
                    </select>
                    <span class="ledger-pag-label">条</span>
                </div>
            </div>
            <div class="ledger-pag-actions">
                <button type="button" class="mini-btn ${isFirst ? 'is-disabled' : ''}" 
                    ${isFirst ? 'disabled' : 'onclick="window.changeDispatchLedgerPage(1)"'} 
                    title="跳转至第一页">⏮️ 首页</button>
                <button type="button" class="mini-btn ${isFirst ? 'is-disabled' : ''}" 
                    ${isFirst ? 'disabled' : `onclick="window.changeDispatchLedgerPage(${currentPage - 1})"`} 
                    title="上一页">◀️ 上一页</button>
                <button type="button" class="mini-btn ${isLast ? 'is-disabled' : ''}" 
                    ${isLast ? 'disabled' : `onclick="window.changeDispatchLedgerPage(${currentPage + 1})"`} 
                    title="下一页">▶️ 下一页</button>
                <button type="button" class="mini-btn ${isLast ? 'is-disabled' : ''}" 
                    ${isLast ? 'disabled' : `onclick="window.changeDispatchLedgerPage(${totalPages})"`} 
                    title="跳转至最后一页">⏭️ 尾页</button>
            </div>
        </div>
    `;
};
