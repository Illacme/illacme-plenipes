/**
 * ⚙️ [V55.0] Illacme Plenipes Imprints Management Module
 * 职责：出版版图增删改查及 UI 渲染。
 */

window.switchImprint = async (id) => {
    if (!id) return;
    addAudit(`🛰️ 正在申请主权切换: ${id}...`, "info");

    const res = await apiFetch('/api/imprints/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imprint_id: id })
    });

    if (res && res.success) {
        addAudit(`🔄 [主权对正] 成功切换至身份: ${id}`, "success");
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
                      '• 治理限制: 无法划定更多主权版图。<br><br>' +
                      '<span style="color:var(--accent-secondary)">💡 建议：升级至 [主权专业版] 以开启无限版图治理。</span>' +
                      '</div>',
                icon: 'warning',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert("🛡️ [准入拦截]\n社区版限额 1 个版图，无法继续划定。");
        }
        return;
    }

    const id = prompt("🏛️ 请输入新出版品牌的【唯一标识】 (ID, 建议英文/数字):");
    if (!id) return;
    const press_name = prompt("📝 请输入【出版社/品牌展示名称】:", id);
    if (!press_name) return;
    const path = prompt("📂 请输入该品牌关联的内容库 (Vault) 【绝对路径】:", "/Volumes/Notebook/omni-hub/content-vault");
    if (!path) return;

    addAudit(`🏗️ 正在为品牌 [${press_name}] 划定主权疆域...`);
    const res = await apiFetch('/api/imprints/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id, path: path, press_name: press_name })
    });

    if (res && res.success) {
        addAudit(`✅ [主权划定] 品牌 ${press_name} 已成功加入矩阵。`, "success");
        loadSettings();
    } else {
        addAudit(`❌ [划定失败] ${res ? res.error : '存在物理命名冲突'}`, "error");
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
    
    const imprints = window.settingsData?._imprints || [];
    const activeId = window.settingsData?._active_imprint;

    dropdown.innerHTML = `<div class="dropdown-header">Sovereign Territories Map</div>` + imprints.map(im => `
        <div class="dropdown-item ${im.id === activeId ? 'active' : ''}" onclick="switchImprint('${im.id}')">
            <div class="imprint-item-header">
                <span class="imprint-title">${im.name || im.id}</span>
                <span class="imprint-id-tag">${im.id}</span>
                ${im.id === activeId ? '<span class="active-dot">●</span>' : ''}
            </div>
            <div class="imprint-path-row">${im.path}</div>
        </div>
    `).join('') + `
        <div class="dropdown-item add-new" onclick="showView('settings'); document.getElementById('imprint-dropdown').style.display='none';">
            <div class="imprint-title" style="color: var(--accent-primary);">⚙️ 版图主权管理</div>
        </div>
    `;
};

window.renderImprintsCategory = function() {
    return `
        <div class="full-width">
            <div class="section-header"><h3>🏗️ SOVEREIGN TERRITORIES MAP</h3></div>
            <p class="section-desc">Global oversight of your publishing empire. Each territory operates in physical isolation.</p>
            
            <div class="shield-matrix">
                ${window.settingsData._imprints.map(im => {
                    const stat = window.settingsData._imprint_stats[im.id] || { doc_count: 0 };
                    const isActive = im.id === window.settingsData._active_imprint;
                    return `
                        <div class="shield-pod territory-pod ${isActive ? 'primary-active' : ''}">
                            <div class="shield-status">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span class="status-dot-mini ${stat.healthy !== false ? 'healthy' : 'blocked'}"></span>
                                    <span class="shield-id">ID: ${im.id}</span>
                                </div>
                                ${isActive ? '<div class="log-tag info">ACTIVE COMMAND</div>' : ''}
                            </div>
                            <div class="shield-body" style="flex:1; display:flex; flex-direction:column;">
                                <h4 contenteditable="true" onblur="handleImprintInlineEdit(this, '${im.id}', 'name')" style="font-size:1.1rem; color:#fff; margin-bottom:5px;">${im.name || im.id}</h4>
                                <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center;">
                                    <span class="tiny-label" style="color:var(--accent-primary);">VAULT ASSETS</span>
                                    <span class="tiny-label mono" style="margin-left:auto; color:#fff;">${stat.doc_count} UNITS</span>
                                </div>
                                
                                <div class="path-preview" style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-dim); margin-bottom:15px; background:rgba(0,0,0,0.2); padding:8px; border-radius:4px; border:1px solid rgba(255,255,255,0.05); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                                    📂 ${im.path}
                                </div>

                                <div class="p-control-group" style="display:grid; grid-template-columns: 1fr auto; gap:8px;">
                                    ${isActive ? 
                                        '<button class="action-btn" disabled style="opacity:0.5;">CURRENTLY DEPLOYED</button>' : 
                                        `<button class="action-btn glow-btn" onclick="switchImprint('${im.id}')">🔄 SWITCH SOVEREIGNTY</button>`}
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
                        <p class="tiny-label">MAP NEW TERRITORY</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}
