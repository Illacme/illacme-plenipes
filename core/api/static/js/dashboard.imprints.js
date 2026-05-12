/**
 * ⚙️ [V74.0] Illacme Plenipes Imprints Management Module
 * 职责：出版集团指挥中心、事业部（版图）矩阵渲染、物理隔离。
 */

window.switchImprint = async (id) => {
    if (!id) return;
    addAudit(`🛰️ 正在申请事业部切换: ${id}...`, "info");

    const res = await apiFetch('/api/imprints/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imprint_id: id })
    });

    if (res && res.success) {
        addAudit(`🔄 [对正] 成功切换至事业部: ${id}`, "success");
        if (typeof refreshGovernanceContext === 'function') await refreshGovernanceContext();
        
        if (typeof loadSettings === 'function' && window.currentView === 'settings') {
            loadSettings('imprints');
        }
        if (typeof renderImprintDropdown === 'function') renderImprintDropdown();
        if (typeof closeTerminalModal === 'function') closeTerminalModal();
    } else {
        addAudit(`🚨 切换失败: ${res ? res.error : '物理链路异常'}`, "error");
    }
};

window.addNewImprint = async () => {
    const isLicensed = window.settingsData?._is_licensed || false;
    const currentCount = window.settingsData?._imprints?.length || 0;

    if (!isLicensed && currentCount >= 1) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '🛡️ 准入拦截',
                html: '<div style="text-align:left; font-size: 0.9rem; line-height: 1.6;">' +
                      '您当前处于 <b>社区标准版</b>。<br><br>' +
                      '• 事业部限额: 1/1 (已满)<br>' +
                      '• 治理限制: 无法添加更多出版事业部。<br><br>' +
                      '<span style="color:var(--accent-secondary)">💡 建议：升级至 [专业版] 以开启无限事业部管理。</span>' +
                      '</div>',
                icon: 'warning',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert("🛡️ [准入拦截]\n社区版限额 1 个事业部，无法继续添加。");
        }
        return;
    }

    const id = prompt("🏛️ 请输入新事业部的【物理标识】 (ID, 建议英文/数字):");
    if (!id) return;
    const press_name = prompt("📝 请输入【事业部展示名称】:", id);
    if (!press_name) return;
    const path = prompt("📂 请输入关联的内容库 (Vault) 【绝对路径】:", "/Volumes/Notebook/omni-hub/content-vault");
    if (!path) return;

    addAudit(`🏗️ 正在为事业部 [${press_name}] 创建全域空间...`);
    const res = await apiFetch('/api/imprints/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id, path: path, press_name: press_name })
    });

    if (res && res.success) {
        addAudit(`✅ [创建成功] 事业部 ${press_name} 已成功加入矩阵。`, "success");
        loadSettings('imprints');
    } else {
        addAudit(`❌ [创建失败] ${res ? res.error : '存在物理命名冲突'}`, "error");
    }
};

window.deleteImprint = async (id) => {
    if (!confirm(`🚨 危险操作！\n确认要物理抹除出版事业部 [${id}] 吗？`)) return;

    const res = await apiFetch('/api/imprints/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id })
    });

    if (res && res.success) {
        addAudit(`🗑️ 事业部已撤销: ${id}`, "warning");
        loadSettings('imprints');
    }
};

window.handleImprintInlineEdit = async (element, id, field) => {
    const newValue = element.innerText.trim();
    const im = window.settingsData._imprints.find(item => item.id === id);
    if (!im) return;
    const currentValue = (field === 'imprint_name' || field === 'name') ? (im.name || im.id) : (im.description || '');

    if (newValue === currentValue) return;

    addAudit(`🖊️ 正在原地固化 [${id}] 的标识信息...`, "info");

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

    imprints.sort((a, b) => {
        if (a.id === activeId) return -1;
        if (b.id === activeId) return 1;
        return 0;
    });

    dropdown.innerHTML = `<div class="dropdown-header">出版集团事业部矩阵</div>` + imprints.map(im => `
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
            <div class="imprint-title" style="color: var(--accent-primary);">⚙️ 集团指挥中心</div>
        </div>
    `;
};

window.renderImprintsCategory = function() {
    const imprints = [...(window.settingsData?._imprints || [])];
    const activeId = window.settingsData?._active_imprint;

    imprints.sort((a, b) => {
        if (a.id === activeId) return -1;
        if (b.id === activeId) return 1;
        return 0;
    });

    return `
        <div class="full-width fade-in">
            <div class="section-header"><h3>🏢 出版集团指挥中心 (Press Group Command)</h3></div>
            
            <!-- 🏛️ Industrial Memo: Imprint as an Independent Studio -->
            <div class="sovereign-memo glass-panel" style="margin-bottom: 30px; padding: 25px; border-left: 4px solid var(--accent-primary); background: rgba(163, 76, 255, 0.03);">
                <h4 style="color: var(--accent-primary); margin-bottom: 12px; font-weight: 900; letter-spacing: 1px;">🏢 工业识见：将事业部视为您的“独立出版单元”</h4>
                <p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.7;">
                    在专业的出版工业中，<b>事业部 (Imprint)</b> 是集团旗下的独立运作单元。在 Illacme 中：<br>
                    • <b>物理独立</b>：每个事业部拥有专属的资产仓库（Vault），物理隔离，确保全域安全。<br>
                    • <b>意志独立</b>：每个事业部可以绑定不同的算力底座，拥有独特的编辑逻辑和指令矩阵。<br>
                    • <b>分发独立</b>：每个事业部可以拥有独立的主题、SEO 策略和全球分发通道。<br>
                    <span style="color: var(--accent-secondary); font-size: 0.75rem; font-weight: 800;">💡 您可以像管理出版集团一样，在此处调度、切换您的多个出版事业部（版图）。</span>
                </p>
            </div>

            <p class="section-desc">全局掌控您的数字出版帝国。在这里，您可以一键在不同的事业部（版图）之间切换意志。</p>
            
            <div class="shield-matrix">
                ${imprints.map(im => {
                    const stat = window.settingsData._imprint_stats[im.id] || { doc_count: 0 };
                    const isActive = im.id === activeId;
                    return `
                        <div class="shield-pod territory-pod ${isActive ? 'primary-active' : ''}">
                            <div class="shield-status">
                                <div class="shield-status-inner">
                                    <span class="shield-id">ID: ${im.id}</span>
                                    <span class="status-dot-mini ${stat.healthy !== false ? 'healthy' : 'blocked'}"></span>
                                </div>
                                ${isActive ? '<div class="log-tag info">执行中</div>' : ''}
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
                                        '<button class="action-btn" disabled style="opacity:0.5;">执行中</button>' : 
                                        `<button class="action-btn glow-btn" onclick="switchImprint('${im.id}')">🔄 切换事业部</button>`}
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
                        <p class="tiny-label">新增出版事业部</p>
                    </div>
                </div>
            </div>
        </div>
    `;
};
