/**
 * ⚙️ [V55.0] Illacme Plenipes Imprints Management Module
 * 职责：出版版图增删改查及 UI 渲染。
 */

window.switchImprint = async (id) => {
    if (!id) return;
    addAudit(`🛰️ 正在申请出版身份切换: ${id}...`, "info");

    const res = await apiFetch('/api/imprints/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imprint_id: id })
    });

    if (res && res.success) {
        addAudit(`🔄 [对正] 成功切换至品牌: ${id}`, "success");
        // 🚀 [V55.9] 物理断路：禁止自动刷新，改为增量同步，彻底切断循环重定向
        if (typeof refreshGovernanceContext === 'function') refreshGovernanceContext();
        if (typeof closeTerminalModal === 'function') closeTerminalModal();
    } else {
        addAudit(`🚨 切换失败: ${res ? res.error : '物理链路异常'}`, "error");
    }
};

window.addNewImprint = async () => {
    // 🚀 [V55.8] 前端预审计：在用户填写表单前即触发授权栅栏校验
    const isLicensed = window.settingsData?._is_licensed || false;
    const currentCount = window.settingsData?._imprints?.length || 0;

    if (!isLicensed && currentCount >= 1) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '🛡️ 准入拦截',
                html: '<div style="text-align:left; font-size: 0.9rem; line-height: 1.6;">' +
                      '您当前处于 <b>社区标准版</b>。<br><br>' +
                      '• 版图限额: 1/1 (已满)<br>' +
                      '• 治理限制: 无法添加更多出版版图。<br><br>' +
                      '<span style="color:var(--accent-secondary)">💡 建议：升级至 [专业版] 以开启无限版图管理。</span>' +
                      '</div>',
                icon: 'warning',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert("🛡️ [准入拦截]\n社区版限额 1 个版图，无法继续添加。");
        }
        return;
    }

    const id = prompt("🏛️ 请输入新出版品牌的【唯一标识】 (ID, 建议英文/数字):");
    if (!id) return;
    const press_name = prompt("📝 请输入【出版社/品牌展示名称】:", id);
    if (!press_name) return;
    const path = prompt("📂 请输入该品牌关联的内容库 (Vault) 【绝对路径】:", "/Volumes/Notebook/omni-hub/content-vault");
    if (!path) return;

    addAudit(`🏗️ 正在为品牌 [${press_name}] 创建版图区域...`);
    const res = await apiFetch('/api/imprints/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id, path: path, press_name: press_name })
    });

    if (res && res.success) {
        addAudit(`✅ [创建成功] 品牌 ${press_name} 已成功加入矩阵。`, "success");
        loadSettings();
    } else {
        addAudit(`❌ [创建失败] ${res ? res.error : '存在物理命名冲突'}`, "error");
    }
};

window.deleteImprint = async (id) => {
    if (!confirm(`🚨 危险操作！\n确认要物理抹除出版身份 [${id}] 吗？`)) return;

    const res = await apiFetch('/api/imprints/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id })
    });

    if (res && res.success) {
        addAudit(`🗑️ 出版身份已撤销: ${id}`, "warning");
        loadSettings();
    }
};

window.handleImprintInlineEdit = async (element, id, field) => {
    const newValue = element.innerText.trim();
    const im = window.settingsData._imprints.find(item => item.id === id);
    if (!im) return;
    const currentValue = (field === 'imprint_name' || field === 'name') ? (im.name || im.id) : (im.description || '');

    if (newValue === currentValue) return;

    addAudit(`🖊️ 正在原地固化 [${id}] 的 ${field.includes('name') ? '名称' : '简介'}...`, "info");

    const payload = {};
    payload[field] = newValue;

    const res = await apiFetch(`/api/config/update?imprint_id=${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        addAudit(`✅ 原地固化成功: ${newValue}`, "success");
        if (field.includes('name')) im.name = newValue;
        else im.description = newValue;
    } else {
        addAudit(`❌ 固化失败: ${res ? res.error : '物理链路冲突'}`, "error");
        element.innerText = currentValue;
    }
};

window.renderImprintDropdown = () => {
    const dropdown = document.getElementById('imprint-dropdown');
    if (!dropdown) return;
    
    const imprints = [...(window.settingsData?._imprints || [])];
    const activeId = window.settingsData?._active_imprint;

    // 🚀 [V55.10] 优先级对正：将当前激活的品牌置顶
    imprints.sort((a, b) => {
        if (a.id === activeId) return -1;
        if (b.id === activeId) return 1;
        return 0;
    });

    dropdown.innerHTML = `<div class="dropdown-header">出版品牌矩阵 (Brands)</div>` + imprints.map(im => `
        <div class="dropdown-item ${im.id === activeId ? 'active' : ''}" onclick="switchImprint('${im.id}')">
            <div class="imprint-item-header">
                <span class="imprint-title">${im.name || im.id}</span>
                <span class="imprint-id-tag">${im.id}</span>
                ${im.id === activeId ? '<span class="active-dot">●</span>' : ''}
            </div>
            <div class="imprint-path-row">${im.path}</div>
        </div>
    `).join('') + `
        <div class="dropdown-item add-new" onclick="showView('settings', 'imprints'); document.getElementById('imprint-dropdown').style.display='none';">
            <div class="imprint-title" style="color: var(--accent-primary);">⚙️ 版图管理</div>
        </div>
    `;
};

window.renderImprintsCategory = function() {
    const imprints = [...(window.settingsData?._imprints || [])];
    const activeId = window.settingsData?._active_imprint;

    // 🚀 [V55.11] 矩阵对正：激活品牌置顶
    imprints.sort((a, b) => {
        if (a.id === activeId) return -1;
        if (b.id === activeId) return 1;
        return 0;
    });

    return `
        <div class="full-width">
            <div class="section-header"><h3>🏗️ 品牌版图矩阵 (Press Brands)</h3></div>
            <p class="section-desc">全局掌控您的出版帝国。每个版图代表一个独立的品牌项目，具备独立的运行配置。</p>
            
            <div class="shield-matrix">
                ${imprints.map(im => {
                    const stat = window.settingsData._imprint_stats[im.id] || { doc_count: 0 };
                    const isActive = im.id === activeId;
                    return `
                        <div class="shield-pod territory-pod ${isActive ? 'primary-active' : ''}">
                            <div class="shield-status">
                                <div class="shield-status-inner">
                                    <span class="status-dot-mini ${stat.healthy !== false ? 'healthy' : 'blocked'}"></span>
                                    <span class="shield-id">ID: ${im.id}</span>
                                </div>
                                ${isActive ? '<div class="log-tag info">使用中</div>' : ''}
                            </div>
                            <div class="shield-body">
                                <h4 contenteditable="true" onblur="handleImprintInlineEdit(this, '${im.id}', 'name')">${im.name || im.id}</h4>
                                <div class="pod-telemetry">
                                    <span class="tiny-label">内容资产数量</span>
                                    <span class="tiny-label mono">${stat.doc_count} 项</span>
                                </div>
                                
                                <div class="path-preview">
                                    📂 ${im.path}
                                </div>

                                <div class="p-control-group">
                                    ${isActive ? 
                                        '<button class="action-btn" disabled style="opacity:0.5;">使用中</button>' : 
                                        `<button class="action-btn glow-btn" onclick="switchImprint('${im.id}')">🔄 切换出版身份</button>`}
                                    ${im.id !== 'default' && !isActive ? 
                                        `<button class="action-btn danger" onclick="deleteImprint('${im.id}')">🗑️</button>` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
                <div class="shield-pod add-card" onclick="addNewImprint()" style="border-style:dashed; cursor:pointer; justify-content:center; align-items:center; display:flex; min-height:220px;">
                    <div style="text-align:center;">
                        <div style="font-size:2rem; margin-bottom:10px; opacity:0.5;">＋</div>
                        <p class="tiny-label">添加新版图</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}
