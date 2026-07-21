window.getPinnedPlugins = () => {
    try {
        return JSON.parse(localStorage.getItem('pinned_plugins') || '[]');
    } catch(e) {
        return [];
    }
};

window.togglePinPlugin = (id, event) => {
    if (event) event.stopPropagation();
    let pins = window.getPinnedPlugins();
    if (pins.includes(id)) {
        pins = pins.filter(x => x !== id);
        if (window.showToast) window.showToast(`已取消置顶 [${id.toUpperCase()}]`, 'info');
    } else {
        pins.push(id);
        if (window.showToast) window.showToast(`已成功将 [${id.toUpperCase()}] 置顶至常用能力`, 'success');
    }
    localStorage.setItem('pinned_plugins', JSON.stringify(pins));
    if (typeof window.renderPlugins === 'function') window.renderPlugins();
};

window.searchQuery = '';
window.filterPluginsBySearch = (query) => {
    window.searchQuery = (query || '').trim().toLowerCase();
    if (typeof window.renderPlugins === 'function') window.renderPlugins();
    const input = document.getElementById('plugin-search-input');
    if (input) {
        input.focus();
        const len = input.value.length;
        input.setSelectionRange(len, len);
    }
};

window.exportConfigBackup = () => {
    const data = window.settingsData || {};
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `illacme_plenipes_config_backup_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    if (window.showToast) window.showToast("🟢 配置备份文件导出成功！", "success");
};

window.importConfigBackup = (event) => {
    const file = event.target.files ? event.target.files[0] : null;
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (e) => {
        try {
            const parsed = JSON.parse(e.target.result);
            if (!parsed || typeof parsed !== 'object') throw new Error("无效的 JSON 配置格式");
            
            if (confirm("确认使用导入的文件恢复全站插件与平台配置？这将覆盖当前保存数据！")) {
                const fetchFunc = window.apiFetch || (async (url, init) => {
                    const r = await fetch(url, init);
                    return r.json();
                });
                const res = await fetchFunc('/api/system/config/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ config: parsed })
                });
                if (res && (res.status === 'success' || res.success)) {
                    window.settingsData = parsed;
                    if (window.loadPlugins) await window.loadPlugins(true);
                    if (window.showToast) window.showToast("🟢 成功导入配置备份！全站配置已自动同步。", "success");
                } else {
                    alert("导入保存失败: " + (res ? (res.error || res.message) : "未知错误"));
                }
            }
        } catch(err) {
            alert("解析配置文件失败: " + err.message);
        }
    };
    reader.readAsText(file);
};

// 4. 能力矩阵渲染器
window.loadPlugins = async (silent = false) => {
    const gridEl = document.getElementById('plugins-grid');
    const tabsEl = document.querySelector('.side-tabs'); // 🚀 适配统一类名
    if (!gridEl || !tabsEl) return;

    const container = document.querySelector('.view-panel.active .tab-content-area') || document.querySelector('.tab-content-area');
    const scrollPos = container ? container.scrollTop : 0;

    if (!silent) {
        gridEl.innerHTML = `
            <div class="skeleton-grid">
                ${Array(6).fill('<div class="plugin-card skeleton" style="height: 180px;"></div>').join('')}
            </div>
        `;
    }

    const data = await apiFetch('/api/plugins/list');
    if (!data || !data.plugins) {
        gridEl.innerHTML = '<div class="empty-state">⚠️ 无法感应全球能力矩阵，请检查核心链路。</div>';
        return;
    }

    window.allPlugins = data.plugins;

    const categories = [
        { id: 'ingress', name: '📥 内容接入' },
        { id: 'transformer', name: '🛠️ 文稿加工' },
        { id: 'masker', name: '🛡️ 安全防护' },
        { id: 'protocol', name: '🧠 AI 协议' },
        { id: 'theme', name: '🎨 视觉装帧' },
        { id: 'hosting', name: '🌐 全站托管' },
        { id: 'image_hosting', name: '📷 图床服务' },
        { id: 'publisher', name: '🚀 分发渠道' },
        { id: 'editorial', name: '🧬 流程审计' }
    ];

    const catCountMap = {};
    window.allPlugins.forEach(p => {
        if (p.category === 'imprint') return;
        let catKey = p.category;
        if (catKey === 'ingress_source' || catKey === 'ingress_dialect') catKey = 'ingress';
        catCountMap[catKey] = (catCountMap[catKey] || 0) + 1;
    });
    const totalCount = window.allPlugins.filter(p => p.category !== 'imprint').length;

    let tabsHtml = `<div class="tab-item cap-tab ${window.activePluginCategory === 'all' ? 'active' : ''}" data-cat="all"><span class="tab-icon">🌈</span> 全部能力 <span class="tab-badge" style="font-size: 0.68rem; opacity: 0.75; margin-left: 4px;">(${totalCount})</span></div>`;

    categories.forEach(cat => {
        const icon = cat.name.substring(0, 2);
        const name = cat.name.substring(3);
        const count = catCountMap[cat.id] || 0;
        tabsHtml += `
            <div class="tab-item cap-tab ${window.activePluginCategory === cat.id ? 'active' : ''}" data-cat="${cat.id}">
                <span class="tab-icon">${icon}</span> ${name} <span class="tab-badge" style="font-size: 0.68rem; opacity: 0.75; margin-left: 4px;">(${count})</span>
            </div>
        `;
    });
    tabsEl.innerHTML = tabsHtml;

    document.querySelectorAll('.cap-tab').forEach(tab => {
        tab.onclick = () => {
            document.querySelectorAll('.cap-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            window.activePluginCategory = tab.dataset.cat;
            renderPlugins();
            const container = document.querySelector('.view-panel.active .tab-content-area');
            if (container) container.scrollTop = 0;
        };
    });

    renderPlugins();

    if (container) {
        container.scrollTop = scrollPos;
    }
};

window.isPluginConfigurable = (p) => {
    if (!p) return false;
    if (p.has_config === false || p.is_configurable === false) return false;
    if (p.is_manageable === false) return false;

    const configurableCategories = ['hosting', 'image_hosting', 'publisher', 'theme', 'protocol', 'masker', 'ingress_source'];
    if (configurableCategories.includes(p.category)) {
        return true;
    }
    return false;
};

window.checkPluginConfiguredStatus = (p) => {
    if (!p) return { label: '未激活', class: 'blocked', style: 'color: var(--text-dim); margin-right: 0 !important;' };
    const canConfig = window.isPluginConfigurable ? window.isPluginConfigurable(p) : false;
    if (!canConfig) {
        return { label: '⚡ 免配置', class: 'info', style: 'background: rgba(255, 255, 255, 0.05); color: var(--text-dim); border: 1px solid rgba(255, 255, 255, 0.15); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    }

    if (!p.is_enabled) {
        return { label: '🚫 全局禁用', class: 'warning', style: 'background: rgba(255, 77, 77, 0.08); color: #ff4d4d; border: 1px solid rgba(255, 77, 77, 0.2); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    }

    const cfgData = window.settingsData || {};
    let settings = {};
    if (p.category === 'hosting') {
        settings = cfgData.publish_control?.direct_upload?.[p.id] || {};
    } else if (p.category === 'image_hosting') {
        settings = cfgData.image_hosting?.[p.id] || {};
    } else {
        settings = cfgData.syndication?.[p.id] || {};
    }

    const hasKeys = Object.entries(settings).some(([k, v]) => {
        if (['enabled', 'proxy', 'force_push', 'git_user_name', 'git_user_email', 'branch'].includes(k)) return false;
        return v !== undefined && v !== null && String(v).trim().length > 0;
    });

    if (hasKeys) {
        return { label: '🟢 配置齐全', class: 'info', style: 'background: rgba(0, 255, 136, 0.08); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    } else {
        return { label: '⚠️ 待填凭据', class: 'warning', style: 'background: rgba(245, 158, 11, 0.08); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    }
};

window.renderPlugins = () => {
    const gridEl = document.getElementById('plugins-grid');
    const pinnedIds = window.getPinnedPlugins();
    const query = window.searchQuery || '';

    let filtered = window.activePluginCategory === 'all'
        ? window.allPlugins.filter(p => p.category !== 'imprint')
        : window.allPlugins.filter(p => {
            if (window.activePluginCategory === 'ingress') {
                return p.category === 'ingress_source' || p.category === 'ingress_dialect';
            }
            return p.category === window.activePluginCategory && p.category !== 'imprint';
        });

    if (query) {
        filtered = filtered.filter(p => {
            const nameMatch = (p.name || '').toLowerCase().includes(query);
            const idMatch = (p.id || '').toLowerCase().includes(query);
            const catMatch = (p.category_name || p.category || '').toLowerCase().includes(query);
            const descMatch = (p.description || '').toLowerCase().includes(query);
            return nameMatch || idMatch || catMatch || descMatch;
        });
    }

    const catNameMap = {
        'all': '🌈 全部能力矩阵',
        'ingress': '📥 内容接入',
        'transformer': '🛠️ 文稿加工',
        'masker': '🛡️ 安全防护',
        'protocol': '🧠 AI 协议',
        'theme': '🎨 视觉装帧',
        'hosting': '🌐 全站托管',
        'image_hosting': '📷 图床服务',
        'publisher': '🚀 分发渠道',
        'editorial': '🧬 流程审计'
    };

    const catDescMap = {
        'all': '全站全球能力矩阵中枢，支持全自动一键授权、独立网络代理与物理通道探针自检。',
        'ingress': '感知本地 Markdown/HTML 稿件与物理文件变动，自动逆向生成语法树与解析元素。',
        'transformer': '负责 Markdown 逆向渲染加工、排版指纹识别与段落结构装帧引擎。',
        'masker': '内置敏感词过滤、EXIF 地理指纹脱敏与图像安全隐私掩码保护屏障。',
        'protocol': '连接底座大语言模型，提供语义润色、智能提炼与多语言翻译中枢协议。',
        'theme': '定制全站出版物装帧主题、CSS 样式排版与视觉渲染模版引擎。',
        'hosting': '支持 Cloudflare, GitHub Pages, Vercel 等平台自动化构建与部署。',
        'image_hosting': '集成 AWS S3, 七牛云, 又拍云, Lsky Pro 等公共与自建图床上传与外链转换。',
        'publisher': '聚合微信公众号, 知乎, CSDN, Dev.to 等主流创作者社交平台的同步分发渠道。',
        'editorial': '记录全站稿件版本演化指纹、发布履历与全生命周期审计追溯日志。'
    };

    const activeCatTitle = catNameMap[window.activePluginCategory] || '🌈 全部能力矩阵';
    const activeCatDesc = catDescMap[window.activePluginCategory] || '支持全自动一键授权、独立网络代理与物理通道探针自检。';

    const toolbarHtml = `
        <div class="plugin-matrix-toolbar" style="width: 100%; box-sizing: border-box; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.12)); display: flex; flex-direction: column; gap: 6px;">
            <div class="matrix-title-group" style="display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
                <h2 style="margin: 0; font-size: 1.35rem; color: var(--text-bright, #ffffff); font-weight: 700; display: flex; align-items: center; gap: 10px;">
                    ${activeCatTitle}
                    <span style="font-size: 0.72rem; color: var(--neon-cyan, #00f2fe); background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.2); padding: 2px 8px; border-radius: 12px; font-weight: 600;">${filtered.length} 个节点</span>
                </h2>
            </div>
            <div class="matrix-cat-description" style="font-size: 0.82rem; color: var(--text-dim, rgba(255, 255, 255, 0.65)); line-height: 1.5; margin-top: 2px;">
                ${activeCatDesc}
            </div>
        </div>
    `;

    const categories = {};
    const pinnedItems = [];

    filtered.forEach(p => {
        if (pinnedIds.includes(p.id)) {
            pinnedItems.push(p);
        }
        if (!categories[p.category]) {
            categories[p.category] = {
                name: p.category_name || p.category,
                items: []
            };
        }
        categories[p.category].items.push(p);
    });

    let html = toolbarHtml;

    // 🚀 [V105.0] 链路冲突与配置一致性智能诊断 Banner
    if (typeof window.runCrossPluginDiagnostics === 'function') {
        html += window.runCrossPluginDiagnostics();
    }
    if (pinnedItems.length > 0) {
        html += `
            <div class="plugins-category-section pinned-category-section" style="margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px dashed var(--glass-border);">
                <div class="plugins-category-header"><h3 style="color: #ffb700;">⭐ 常用置顶能力 (${pinnedItems.length})</h3></div>
                <div class="shield-matrix">
                ${pinnedItems.map(p => window.buildPluginPodHtml(p, true)).join('')}
                </div>
            </div>
        `;
    }

    const categoryOrder = ['ingress_source', 'ingress_dialect', 'transformer', 'masker', 'protocol', 'theme', 'hosting', 'image_hosting', 'publisher', 'editorial'];

    const activeSections = categoryOrder.filter(catId => categories[catId] && categories[catId].items.length > 0);
    const hideSectionHeader = window.activePluginCategory !== 'all' && activeSections.length <= 1;

    categoryOrder.forEach(catId => {
        const cat = categories[catId];
        if (cat && cat.items.length > 0) {
            html += `
                <div class="plugins-category-section" style="${hideSectionHeader ? 'margin-top: 5px;' : ''}">
                    ${hideSectionHeader ? '' : `
                    <div class="plugins-category-header">
                        <h3 style="display: flex; align-items: center; gap: 10px;">
                            ${cat.name}
                            <span style="font-size: 0.72rem; color: var(--neon-cyan); background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.2); padding: 1px 8px; border-radius: 12px; font-weight: 600;">${cat.items.length} 个节点</span>
                        </h3>
                    </div>
                    `}
                    <div class="shield-matrix">
                    ${cat.items.map(p => window.buildPluginPodHtml(p, pinnedIds.includes(p.id))).join('')}
                    </div>
                </div>
            `;
        }
    });

    gridEl.innerHTML = html || `<div class="empty-state">${query ? `🔍 未搜索到包含 "${query}" 的相关能力。` : '⚠️ 未在该能级发现任何活跃组件。'}</div>`;
    if (typeof window.init3DHoverPhysics === 'function') {
        setTimeout(window.init3DHoverPhysics, 50);
    }
};

window.buildPluginPodHtml = (p, isPinned) => {
    const portalInfo = window.PLATFORM_PORTAL_LINKS ? window.PLATFORM_PORTAL_LINKS[p.id] : null;
    const homeUrl = portalInfo ? portalInfo.home : null;

    const canConfig = window.isPluginConfigurable(p);
    const canTest = ['hosting', 'image_hosting', 'publisher'].includes(p.category) && p.is_manageable;
    const statusBadge = window.checkPluginConfiguredStatus(p);

    let controlBtnsHtml = '';
    if (canConfig && canTest) {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                <button class="action-btn" onclick="openPluginConfig('${p.id}', '${p.category}')">⚙️ CONFIG</button>
                <button class="action-btn p-btn-test-direct" data-id="${p.id}" data-category="${p.category}" onclick="window.fastTestPluginConnectivity('${p.id}', '${p.category}', this)">⚡ 测试连接</button>
            </div>
        `;
    } else if (canConfig && !canTest) {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                <button class="action-btn" onclick="openPluginConfig('${p.id}', '${p.category}')">⚙️ CONFIG</button>
            </div>
        `;
    } else if (!canConfig && canTest) {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                <button class="action-btn p-btn-test-direct" data-id="${p.id}" data-category="${p.category}" onclick="window.fastTestPluginConnectivity('${p.id}', '${p.category}', this)">⚡ 测试连接</button>
            </div>
        `;
    } else {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:block; text-align:center; padding: 4px 0;">
                <span style="font-size:0.7rem; color:var(--text-dim); opacity:0.7; font-weight:500;">⚡ 物理内置驱动 (免配置)</span>
            </div>
        `;
    }

    return `
    <div class="shield-pod plugin-pod ${p.is_in_use ? 'active-duty' : ''}">
        <div class="shield-status">
            <div style="display:flex; align-items:center; gap:8px;">
                <button type="button" onclick="window.togglePinPlugin('${p.id}', event)" title="${isPinned ? '取消常用置顶' : '置顶为常用能力'}" style="background: transparent; border: none; cursor: pointer; font-size: 0.85rem; padding: 0; line-height: 1; opacity: ${isPinned ? '1' : '0.35'}; transition: all 0.2s;" onmouseover="this.style.opacity='1';">⭐</button>
                <span class="status-dot-mini ${p.is_enabled ? 'healthy' : 'blocked'}" id="dot-${p.category}-${p.id}"></span>
                <span class="shield-id">RELEASE ${p.version.split(' ')[0]}</span>
            </div>
            ${p.is_manageable
                ? `<div class="log-tag ${statusBadge.class}" style="${statusBadge.style}">${statusBadge.label}</div>`
                : `<div class="log-tag info" style="margin-right: 0 !important;">${p.status.toUpperCase()}</div>`
            }
        </div>
        
        <div class="shield-body" style="flex:1; display:flex; flex-direction:column;">
            <h4 style="font-size:1.1rem; color:var(--text-bright); margin-bottom:5px; display:flex; align-items:center; justify-content:space-between; gap:8px;">
                <span>${p.name || p.id}</span>
                ${homeUrl ? `<a href="${homeUrl}" target="_blank" onclick="event.stopPropagation()" title="访问 ${p.name || p.id} 官方网站" style="font-size:0.68rem; color:var(--neon-cyan); text-decoration:none; opacity:0.9; font-weight:500; border:1px solid rgba(0, 242, 255, 0.35); padding:2px 8px; border-radius:6px; background:rgba(0, 242, 255, 0.08); display:inline-flex; align-items:center; gap:4px; flex-shrink:0; margin-right: 0 !important; transition:all 0.2s;" onmouseover="this.style.background='rgba(0,242,255,0.2)'; this.style.borderColor='var(--neon-cyan)';" onmouseout="this.style.background='rgba(0,242,255,0.08)'; this.style.borderColor='rgba(0, 242, 255, 0.35)';">🌐 官网 ↗</a>` : ''}
            </h4>
            <p style="margin-bottom:15px; flex:1; font-size:0.75rem; color:var(--text-dim);">${p.description || 'Capability syncing...'}</p>
            
            ${p.is_manageable ? `
              <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center; justify-content:space-between; ${!p.is_enabled ? 'opacity:0.45; filter:grayscale(1); cursor:not-allowed;' : ''}">
                  <span class="tiny-label" style="display:inline-flex; align-items:center; gap:6px; font-weight:600; color:var(--text-bright);">
                      ${p.is_enabled ? '<span style="color:#00ff88; font-size:0.8rem; line-height:1;">●</span>' : '<span style="color:#ff4d4d; font-size:0.8rem; line-height:1;">●</span>'}
                      当前品牌启用
                  </span>
                  <label class="p-switch" style="${!p.is_enabled ? 'pointer-events:none;' : ''}">
                      <input type="checkbox" ${p.is_in_use ? 'checked' : ''} onchange="toggleBrandActivation('${p.id}', this.checked, '${p.category}')" ${!p.is_enabled ? 'disabled' : ''}>
                      <span class="p-slider round"></span>
                  </label>
              </div>
              ` : `
              <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center;">
                  ${p.is_in_use ? '<span class="tiny-label" style="color:#00ff88; display:flex; align-items:center; gap:6px;"><span class="heartbeat-indicator pulsing" style="background:#00ff88; width:6px; height:6px;"></span>品牌已绑定</span>' : '<span class="tiny-label" style="color:var(--text-dim);">系统基础节点</span>'}
              </div>
            `}

            ${controlBtnsHtml}
        </div>
    </div>
`;
};

// ⚡ [V90.0] 卡片上快捷一键测试连接
window.fastTestPluginConnectivity = async (id, category, btn) => {
    if (!btn || btn.disabled) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 测试中...";
    btn.style.opacity = "0.7";

    const cardEl = btn.closest('.plugin-pod');
    const statusDot = cardEl.querySelector('.status-dot-mini');
    const logTagEl = cardEl.querySelector('.log-tag');
    let originalDotClass = "";
    if (statusDot) {
        originalDotClass = statusDot.className;
        statusDot.className = 'status-dot-mini pulsing-orange'; // 闪烁黄色加载动画
    }

    let settings = {};
    if (window.settingsData) {
        settings = {
            ...(window.settingsData.image_hosting?.[id] || {}),
            ...(window.settingsData.publish_control?.direct_upload?.[id] || {}),
            ...(window.settingsData.syndication?.[id] || {})
        };
    }

    const currentDrawer = document.getElementById('plugin-drawer');
    const drawerTitle = document.getElementById('p-drawer-title');
    const isEditingThisPlugin = drawerTitle && drawerTitle.innerText && drawerTitle.innerText.toLowerCase().includes(id.toLowerCase());

    if (currentDrawer && isEditingThisPlugin) {
        currentDrawer.querySelectorAll('input, select, textarea').forEach(input => {
            const path = input.getAttribute('data-path') || input.name;
            if (path && input.value !== undefined) {
                const parts = path.split('.');
                const key = parts[parts.length - 1];
                let val = input.value;
                if (input.type === 'checkbox') val = input.checked;
                else if (input.type === 'number') val = parseFloat(input.value) || 0;
                settings[key] = val;
            }
        });
    }

    try {
        const fetchFunc = window.apiFetch || (async (url, init) => {
            const r = await fetch(url, init);
            return r.json();
        });

        const res = await fetchFunc('/api/plugins/dry-run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, parentId: category, settings })
        });

        btn.disabled = false;
        btn.innerText = originalText;
        btn.style.opacity = "1";

        if (res && res.success) {
            window.probePassState = window.probePassState || {};
            window.probePassState[id] = true;

            if (statusDot) statusDot.className = 'status-dot-mini healthy';
            if (logTagEl) {
                logTagEl.style.background = 'rgba(0, 255, 136, 0.08)';
                logTagEl.style.color = '#00ff88';
                logTagEl.style.border = '1px solid rgba(0, 255, 136, 0.2)';
                logTagEl.innerText = "🟢 通道畅通";
            }

            // 🚀 [5-Star UX] 全自动静默保存
            if (typeof window.savePluginConfig === 'function') {
                try { await window.savePluginConfig(true); } catch(e) {}
            }

            if (window.showToast) {
                window.showToast(`🟢 [${id.toUpperCase()}] 物理连接测试成功！已全自动保存配置。`, 'success');
            }
        } else {
            const errMsg = (res && (res.error || res.message || res.detail || (Array.isArray(res.logs) && res.logs.length ? res.logs.filter(l => typeof l === 'string' && (l.includes('ERROR') || l.includes('WARN'))).pop() : null))) || "物理通道无法连通，请检查凭据或代理参数。";
            
            if (res && res.logs) {
                window.lastTestLogs = window.lastTestLogs || {};
                window.lastTestLogs[id] = res.logs;
            }

            if (statusDot) statusDot.className = 'status-dot-mini blocked';
            if (logTagEl) {
                logTagEl.style.background = 'rgba(255, 77, 77, 0.12)';
                logTagEl.style.color = '#ff4d4d';
                logTagEl.style.border = '1px solid rgba(255, 77, 77, 0.3)';
                logTagEl.style.cursor = 'pointer';
                logTagEl.title = '点击查看完整调试日志';
                logTagEl.innerText = "❌ 连接失败 (查看日志)";
                logTagEl.onclick = (e) => {
                    e.stopPropagation();
                    window.showPluginLogDrawer(id, id.toUpperCase(), 'error', res ? res.logs : null);
                };
            }

            // 🚀 [5-Star UX] 自动检测并高亮定位错误输入框
            if (typeof window.focusErrorField === 'function') {
                for (let field of ['account_id', 'token', 'key', 'proxy', 'project_name', 'bucket']) {
                    if (errMsg.toLowerCase().includes(field)) {
                        window.focusErrorField(field);
                        break;
                    }
                }
            }

            // 🚀 优雅高档单条 Toast 提醒，绝不上报原生阻塞 alert/confirm 弹窗
            if (window.showToast) {
                window.showToast(`❌ [${id.toUpperCase()}] 物理测试失败: ${errMsg}`, 'error');
            }
        }
    } catch (err) {
        btn.disabled = false;
        btn.innerText = originalText;
        btn.style.opacity = "1";
        if (statusDot && originalDotClass) statusDot.className = originalDotClass;
        if (window.showToast) {
            window.showToast(`❌ 测试异常: ${err.message || err}`, 'error');
        }
    }
};

// 3. 📋 物理测试连通性日志抽屉 (Connectivity Log Drawer)
window.showPluginLogDrawer = (id, title, status, logs) => {
    let drawer = document.getElementById('log-terminal-drawer');
    if (!drawer) {
        drawer = document.createElement('div');
        drawer.id = 'log-terminal-drawer';
        drawer.style.cssText = 'position: fixed; top: 0; right: -520px; width: 480px; height: 100vh; background: rgba(10, 10, 15, 0.95); backdrop-filter: blur(16px); border-left: 1px solid var(--glass-border); box-shadow: -10px 0 30px rgba(0,0,0,0.6); z-index: 9999; transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1); display: flex; flex-direction: column; font-family: monospace;';
        document.body.appendChild(drawer);
    }

    const rawLogs = logs || window.lastTestLogs?.[id] || ['暂无详细的诊断日志'];
    const logsArray = Array.isArray(rawLogs) ? rawLogs : (typeof rawLogs === 'string' ? [rawLogs] : [rawLogs]);
    const cleanLogTexts = [];
    const formattedLogs = logsArray.map(l => {
        let str = "";
        if (typeof l === 'object' && l !== null) {
            const msg = l.message || l.text || l.msg || l.detail || l.content || JSON.stringify(l);
            const level = l.level || l.type || '';
            str = level ? `[${String(level).toUpperCase()}] ${msg}` : String(msg);
        } else {
            str = String(l);
        }
        cleanLogTexts.push(str);

        if (str.includes('ERROR') || str.includes('❌') || str.includes('失败')) {
            return `<div style="color: #ff4d4d; margin-bottom: 3px; font-family: monospace;">${str}</div>`;
        } else if (str.includes('WARN') || str.includes('⚠️')) {
            return `<div style="color: #f59e0b; margin-bottom: 3px; font-family: monospace;">${str}</div>`;
        } else if (str.includes('SUCCESS') || str.includes('🟢') || str.includes('成功')) {
            return `<div style="color: #00ff88; margin-bottom: 3px; font-family: monospace;">${str}</div>`;
        }
    }).join('');

    window.lastCleanLogText = cleanLogTexts.join('\n');

    drawer.innerHTML = `
        <div style="padding: 16px 20px; border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3);">
            <div>
                <h3 style="margin: 0; font-size: 1.05rem; color: #fff;">📋 物理连通性日志</h3>
                <span style="font-size: 0.72rem; color: var(--text-dim);">${title || id.toUpperCase()} 通道演练诊断信息</span>
            </div>
            <button type="button" onclick="document.getElementById('log-terminal-drawer').style.right = '-520px'" style="background: transparent; border: none; color: #888; font-size: 1.2rem; cursor: pointer;">✕</button>
        </div>
        <div style="flex: 1; padding: 16px; overflow-y: auto; font-size: 0.78rem; line-height: 1.6; background: #07070a; color: #d1d5db; word-break: break-all;">
            ${formattedLogs}
        </div>
        <div style="padding: 12px 16px; border-top: 1px solid var(--glass-border); display: flex; gap: 8px; justify-content: flex-end; background: rgba(0,0,0,0.3);">
            <button type="button" onclick="window.copyLogTerminalContent(this)" style="font-size: 0.75rem; background: rgba(0, 242, 255, 0.1); border: 1px solid rgba(0, 242, 255, 0.3); color: var(--neon-cyan); padding: 5px 12px; border-radius: 6px; cursor: pointer; transition: all 0.25s ease;">📋 一键复制日志</button>
            <button type="button" onclick="document.getElementById('log-terminal-drawer').style.right = '-520px'" style="font-size: 0.75rem; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 5px 12px; border-radius: 6px; cursor: pointer;">关闭</button>
        </div>
    `;

    setTimeout(() => { drawer.style.right = '0px'; }, 10);
};

// 🚀 [5-Star UX] 全局日志终端复制与即时微交互提示
window.copyLogTerminalContent = async (btn) => {
    const textToCopy = window.lastCleanLogText || '';
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(textToCopy);
        } else {
            const ta = document.createElement('textarea');
            ta.value = textToCopy;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }

        if (btn) {
            const originalText = btn.innerHTML;
            const originalBg = btn.style.background;
            const originalBorder = btn.style.border;
            const originalColor = btn.style.color;

            btn.innerHTML = '✅ 已成功复制到剪贴板！';
            btn.style.background = 'rgba(0, 255, 136, 0.25)';
            btn.style.border = '1px solid rgba(0, 255, 136, 0.6)';
            btn.style.color = '#00ff88';

            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = originalBg;
                btn.style.border = originalBorder;
                btn.style.color = originalColor;
            }, 1500);
        }

        if (window.showToast) {
            window.showToast('🟢 诊断日志已成功复制到剪贴板！', 'success');
        }
    } catch(err) {
        if (btn) btn.innerText = '❌ 复制失败';
    }
};

// 4. 📋 剪贴板凭据智能感知与一秒导入 (Smart Clipboard Credentials Sense)
window.senseClipboardCredentials = async () => {
    try {
        if (!navigator.clipboard || !navigator.clipboard.readText) {
            if (window.showToast) window.showToast("当前浏览器未开放剪贴板读取权限", "warning");
            return;
        }
        const text = (await navigator.clipboard.readText() || '').trim();
        if (!text || text.length < 8) {
            if (window.showToast) window.showToast("未在剪贴板中检测到有效凭据字符串", "info");
            return;
        }

        const activeDrawer = document.getElementById('plugin-drawer');
        const drawerTitle = document.getElementById('p-drawer-title');
        const isDrawerOpen = activeDrawer && activeDrawer.style.display !== 'none' && activeDrawer.offsetHeight > 0;

        // 🎯 场景 A：当前配置抽屉已打开，直接精准回填当前抽屉！
        if (isDrawerOpen) {
            const tokenInput = activeDrawer.querySelector('input[data-path*="token"], input[data-path*="api_key"], input[data-path*="secret_key"], input[data-path*="password"], input[name*="token"], input[type="password"]');
            if (tokenInput) {
                tokenInput.value = text;
                tokenInput.dispatchEvent(new Event('input', { bubbles: true }));
                tokenInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                tokenInput.focus();
                tokenInput.style.transition = 'all 0.3s';
                tokenInput.style.outline = '2px solid #00ff88';
                tokenInput.style.boxShadow = '0 0 15px rgba(0, 255, 136, 0.6)';
                setTimeout(() => {
                    tokenInput.style.outline = '';
                    tokenInput.style.boxShadow = '';
                }, 1500);

                const pluginName = drawerTitle ? drawerTitle.innerText.replace('⚙️ 配置能力:', '').trim() : '当前平台';
                if (window.showToast) window.showToast(`🟢 已成功将剪贴板凭据智能填入 [${pluginName}]！`, "success");
                return;
            }
        }

        // 🎯 场景 B：在矩阵主视图页面，智能识别 Token 格式并自动引导
        let detectedProvider = null;
        if (text.startsWith('ghp_') || text.startsWith('github_pat_')) {
            detectedProvider = { id: 'github_pages', name: 'GitHub Token', category: 'hosting' };
        } else if (text.startsWith('glpat-')) {
            detectedProvider = { id: 'gitlab_pages', name: 'GitLab Token', category: 'hosting' };
        } else if (text.startsWith('wrangler_')) {
            detectedProvider = { id: 'cloudflare_pages', name: 'Cloudflare Token', category: 'hosting' };
        } else if (text.startsWith('Bearer ')) {
            detectedProvider = { id: 'lsky_pro', name: 'Lsky Pro Token', category: 'image_hosting' };
        }

        if (detectedProvider && typeof window.openPluginDrawer === 'function') {
            window.openPluginDrawer(detectedProvider.id, detectedProvider.category);
            setTimeout(() => {
                const drawer = document.getElementById('plugin-drawer');
                if (drawer) {
                    const input = drawer.querySelector('input[data-path*="token"], input[data-path*="api_key"], input[type="password"]');
                    if (input) {
                        input.value = text;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.focus();
                        if (window.showToast) window.showToast(`🟢 已自动打开 [${detectedProvider.name}] 并回填凭据！`, "success");
                    }
                }
            }, 200);
        } else {
            if (window.showToast) {
                window.showToast(`💡 已从剪贴板捕获 Key (${text.slice(0, 8)}...)，请打开目标插件抽屉自动填充。`, "info");
            }
        }
    } catch(err) {
        if (window.showToast) window.showToast(`读取剪贴板提示: ${err.message || err}`, "warning");
    }
};

// 5. 🎨 VisionOS 级 3D 悬浮视差与光影微动效 (Dynamic 3D Hover & Glass Dynamics)
window.init3DHoverPhysics = () => {
    document.querySelectorAll('.shield-pod').forEach(pod => {
        if (pod.dataset.has3DPhysics) return;
        pod.dataset.has3DPhysics = 'true';

        pod.addEventListener('mousemove', (e) => {
            const rect = pod.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const tiltX = (y - centerY) / 16;
            const tiltY = -(x - centerX) / 16;

            pod.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateZ(4px)`;
            pod.style.setProperty('--mouse-x', `${(x / rect.width) * 100}%`);
            pod.style.setProperty('--mouse-y', `${(y / rect.height) * 100}%`);
        });

        pod.addEventListener('mouseleave', () => {
            pod.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        });
    });
};

// 窗口获得焦点时自动触发剪贴板感应探测
window.addEventListener('focus', () => {
    const pluginsPanel = document.getElementById('view-plugins');
    if (pluginsPanel && pluginsPanel.classList.contains('active')) {
        window.senseClipboardCredentials();
    }
});

// 🚀 [V105.0] 全站跨插件链路诊断算子
window.runCrossPluginDiagnostics = () => {
    const issues = [];
    const cfgData = window.settingsData || {};
    const plugins = window.allPlugins || [];

    // 1. 扫描处于开启状态 (is_enabled: true) 但核心凭据为空的插件
    plugins.forEach(p => {
        if (p.is_enabled && p.is_manageable && ['hosting', 'image_hosting', 'publisher'].includes(p.category)) {
            let platformCfg = {};
            if (p.category === 'hosting') platformCfg = cfgData.publish_control?.direct_upload?.[p.id] || {};
            else if (p.category === 'image_hosting') platformCfg = cfgData.image_hosting?.[p.id] || {};
            else platformCfg = cfgData.syndication?.[p.id] || {};

            const tokenVal = platformCfg.token || platformCfg.api_key || platformCfg.access_token || platformCfg.api_token || platformCfg.secret_key || platformCfg.integration_token || platformCfg.cookie || platformCfg.password || platformCfg.private_key || '';
            if (!tokenVal && !['sftp', 'local_fs'].includes(p.id)) {
                issues.push({
                    type: 'warning',
                    title: `⚠️ [${p.name || p.id.toUpperCase()}] 物理凭据丢失警示`,
                    desc: `该通道处于开启状态但未充填有效鉴权 Token，可能导致物理分发失败。`,
                    actionText: '🎯 补全凭据',
                    action: `openPluginConfig('${p.id}', '${p.category}')`
                });
            }
        }
    });

    // 2. 扫描 GitHub Pages 与 GitHub 图床同源凭据共享机会
    const ghPagesToken = cfgData.publish_control?.direct_upload?.github_pages?.token || cfgData.publish_control?.direct_upload?.github_pages?.access_token;
    const ghImgToken = cfgData.image_hosting?.github?.token || cfgData.image_hosting?.github?.access_token;

    if (ghPagesToken && !ghImgToken) {
        issues.push({
            type: 'info',
            title: `💡 [GitHub 图床] 可复用 GitHub Pages 凭据`,
            desc: `检测到 GitHub Pages 已配置有效 Token，建议一键共享给 GitHub 图床。`,
            actionText: '📋 一键同源复用',
            action: `window.autoReuseSameOriginCredential('${ghPagesToken}', 'github', 'image_hosting')`
        });
    }

    if (issues.length === 0) return '';

    const firstIssue = issues[0];
    return `
        <div class="cross-plugin-diagnostics-banner" style="width: 100%; box-sizing: border-box; margin-bottom: 16px; padding: 12px 16px; border-radius: 10px; border: 1px dashed ${firstIssue.type === 'warning' ? 'rgba(255, 183, 0, 0.4)' : 'var(--neon-cyan)'}; background: ${firstIssue.type === 'warning' ? 'rgba(255, 183, 0, 0.06)' : 'rgba(0, 242, 255, 0.05)'}; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 0.85rem; font-weight: 700; color: ${firstIssue.type === 'warning' ? '#ffb700' : 'var(--neon-cyan)'};">${firstIssue.title}</span>
                <span style="font-size: 0.78rem; color: var(--text-dim);">${firstIssue.desc}</span>
            </div>
            <button type="button" onclick="${firstIssue.action}" style="font-size: 0.72rem; background: ${firstIssue.type === 'warning' ? 'rgba(255, 183, 0, 0.15)' : 'rgba(0, 242, 255, 0.12)'}; border: 1px solid ${firstIssue.type === 'warning' ? 'rgba(255, 183, 0, 0.35)' : 'rgba(0, 242, 255, 0.3)'}; color: ${firstIssue.type === 'warning' ? '#ffb700' : 'var(--neon-cyan)'}; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-weight: 600;">${firstIssue.actionText}</button>
        </div>
    `;
};

// 🚀 [V105.0] 自动快速同源凭据复用算子
window.autoReuseSameOriginCredential = (sourceToken, targetId, targetCategory) => {
    if (typeof window.openPluginDrawer === 'function') {
        window.openPluginDrawer(targetId, targetCategory);
        setTimeout(() => {
            const drawer = document.getElementById('plugin-drawer');
            if (drawer && sourceToken) {
                const input = drawer.querySelector('input[name*="token"], input[name*="access_token"], input[data-path*="token"]');
                if (input) {
                    input.value = sourceToken;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    input.focus();
                    if (window.showToast) window.showToast("✅ 已全自动同步并填入同源 Token！", "success");
                }
            }
        }, 150);
    } else if (typeof window.openPluginConfig === 'function') {
        window.openPluginConfig(targetId, targetCategory);
        setTimeout(() => {
            const drawer = document.getElementById('plugin-drawer');
            if (drawer && sourceToken) {
                const input = drawer.querySelector('input[name*="token"], input[name*="access_token"], input[data-path*="token"]');
                if (input) {
                    input.value = sourceToken;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    input.focus();
                    if (window.showToast) window.showToast("✅ 已全自动同步并填入同源 Token！", "success");
                }
            }
        }, 150);
    }
};
