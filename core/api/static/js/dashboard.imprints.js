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
        if (typeof renderImprintDropdown === 'function') renderImprintDropdown();
        
        // 🚀 [V74.15] 全域主权对正：品牌切换是重量级上下文切换，强制刷新以确保所有视图与后端引擎同步
        setTimeout(() => {
            location.reload();
        }, 800);
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

    if (typeof showImprintWizard === 'function') {
        showImprintWizard();
    }
};

// 🏛️ [V75.6] 版图配置向导多步骤控制器生命周期管理
let currentWizStep = 1;

window.showImprintWizard = () => {
    currentWizStep = 1;
    
    // 重置输入框
    document.getElementById('wiz-imprint-id').value = '';
    document.getElementById('wiz-imprint-name').value = '';
    document.getElementById('wiz-vault-path').value = '';
    document.getElementById('wiz-bootstrap-vault').checked = true;
    
    // 隐藏所有历史行内错误
    document.getElementById('wiz-error-id').style.display = 'none';
    document.getElementById('wiz-error-name').style.display = 'none';
    document.getElementById('wiz-error-path').style.display = 'none';
    
    // 显示步骤1，隐藏步骤2, 3
    document.getElementById('wiz-step-1').style.display = 'block';
    document.getElementById('wiz-step-2').style.display = 'none';
    document.getElementById('wiz-step-3').style.display = 'none';
    
    // 进度条归零
    document.getElementById('wiz-progress-line').style.width = '0%';
    
    // 更新步骤指示器节点
    updateStepNodesUI();
    
    // 更新页脚按钮
    document.getElementById('btn-wiz-prev').style.visibility = 'hidden';
    const nextBtn = document.getElementById('btn-wiz-next');
    nextBtn.disabled = false;
    nextBtn.innerText = '下一步';
    nextBtn.onclick = () => window.navigateWizard(1);
    
    // 展现模态框
    document.getElementById('imprint-wizard-modal').style.display = 'flex';
};

window.closeImprintWizard = () => {
    document.getElementById('imprint-wizard-modal').style.display = 'none';
};

const updateStepNodesUI = () => {
    for (let i = 1; i <= 3; i++) {
        const node = document.getElementById(`wiz-node-${i}`);
        if (!node) continue;
        const circle = node.querySelector('.circle');
        const text = node.querySelector('span');
        
        if (i < currentWizStep) {
            // 已完成步骤
            circle.style.border = '2px solid var(--accent-secondary)';
            circle.style.background = 'var(--accent-secondary)';
            circle.style.color = '#000';
            circle.innerHTML = '✓';
            text.style.color = 'var(--text-bright)';
        } else if (i === currentWizStep) {
            // 当前活跃步骤
            circle.style.border = '2px solid var(--accent-primary)';
            circle.style.background = 'var(--card-bg)';
            circle.style.color = 'var(--text-bright)';
            circle.innerHTML = i;
            text.style.color = 'var(--text-bright)';
        } else {
            // 未到达步骤
            circle.style.border = '2px solid rgba(255,255,255,0.1)';
            circle.style.background = 'var(--card-bg)';
            circle.style.color = 'var(--text-dim)';
            circle.innerHTML = i;
            text.style.color = 'var(--text-dim)';
        }
    }
};

window.navigateWizard = (dir) => {
    // 隐藏所有行内错误提醒
    document.getElementById('wiz-error-id').style.display = 'none';
    document.getElementById('wiz-error-name').style.display = 'none';
    document.getElementById('wiz-error-path').style.display = 'none';

    // 校验当前步骤输入
    if (dir === 1) {
        if (currentWizStep === 1) {
            const id = document.getElementById('wiz-imprint-id').value.trim();
            const name = document.getElementById('wiz-imprint-name').value.trim();
            let hasErr = false;

            if (!id) {
                const idErr = document.getElementById('wiz-error-id');
                idErr.innerText = '⚠️ 物理唯一标识符 (ID) 不能为空';
                idErr.style.display = 'block';
                hasErr = true;
            } else {
                // ID正则校验：只允许英文、数字、中划线、下划线
                const idRegex = /^[a-zA-Z0-9\-_]+$/;
                if (!idRegex.test(id)) {
                    const idErr = document.getElementById('wiz-error-id');
                    idErr.innerText = '⚠️ 标识符格式错误：只允许英文字母、数字、下划线(_)或中划线(-)';
                    idErr.style.display = 'block';
                    hasErr = true;
                }
            }

            if (!name) {
                const nameErr = document.getElementById('wiz-error-name');
                nameErr.innerText = '⚠️ 版图展示名称不能为空';
                nameErr.style.display = 'block';
                hasErr = true;
            }

            if (hasErr) return;
        } else if (currentWizStep === 2) {
            const path = document.getElementById('wiz-vault-path').value.trim();
            if (!path) {
                const pathErr = document.getElementById('wiz-error-path');
                pathErr.innerText = '⚠️ 关联的文库 (Vault) 绝对物理路径不能为空';
                pathErr.style.display = 'block';
                return;
            }
        }
    }
    
    currentWizStep += dir;
    if (currentWizStep < 1) currentWizStep = 1;
    if (currentWizStep > 3) currentWizStep = 3;
    
    // 更新内容面板显示
    document.getElementById('wiz-step-1').style.display = currentWizStep === 1 ? 'block' : 'none';
    document.getElementById('wiz-step-2').style.display = currentWizStep === 2 ? 'block' : 'none';
    document.getElementById('wiz-step-3').style.display = currentWizStep === 3 ? 'block' : 'none';
    
    // 进度条宽度
    const progressWidth = ((currentWizStep - 1) / 2) * 100 + '%';
    document.getElementById('wiz-progress-line').style.width = progressWidth;
    
    // 更新节点样式
    updateStepNodesUI();
    
    // 更新上一步按钮可见性
    document.getElementById('btn-wiz-prev').style.visibility = currentWizStep > 1 ? 'visible' : 'hidden';
    
    // 更新下一步/提交按钮
    const nextBtn = document.getElementById('btn-wiz-next');
    if (currentWizStep === 3) {
        // 渲染概要数据
        document.getElementById('summary-id').innerText = document.getElementById('wiz-imprint-id').value.trim();
        document.getElementById('summary-name').innerText = document.getElementById('wiz-imprint-name').value.trim();
        document.getElementById('summary-path').innerText = document.getElementById('wiz-vault-path').value.trim();
        document.getElementById('summary-bootstrap').innerText = document.getElementById('wiz-bootstrap-vault').checked ? '🌱 自动创建 Obsidian 文库树并生成首篇文章' : '❌ 不进行初始化，使用原有空间目录';
        
        nextBtn.innerText = '🚀 激活并诞生';
        nextBtn.onclick = () => window.submitImprintWizard();
    } else {
        nextBtn.innerText = '下一步';
        nextBtn.onclick = () => window.navigateWizard(1);
    }
};

window.submitImprintWizard = async () => {
    const id = document.getElementById('wiz-imprint-id').value.trim();
    const press_name = document.getElementById('wiz-imprint-name').value.trim();
    const path = document.getElementById('wiz-vault-path').value.trim();
    const bootstrap_vault = document.getElementById('wiz-bootstrap-vault').checked;
    
    addAudit(`🏗️ 正在为事业部 [${press_name}] 创建全域空间并校验主权结构...`);
    
    // 禁用发射按钮，防止重入
    const nextBtn = document.getElementById('btn-wiz-next');
    nextBtn.disabled = true;
    nextBtn.innerText = '📡 正在发射...';
    
    try {
        const res = await apiFetch('/api/imprints/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: id,
                path: path,
                press_name: press_name,
                bootstrap_vault: bootstrap_vault
            })
        });
        
        if (res && res.success) {
            addAudit(`✅ [创建成功] 新事业部 [${press_name}] 物理主权已落地激活。`, "success");
            
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '🏛️ 版图诞生成功',
                    text: `恭喜！您的全新出版事业部 [${press_name}] 已经物理创立，配置、方言模板及文库结构均已完成自愈！`,
                    icon: 'success',
                    confirmButtonText: '立即查看',
                    background: 'var(--card-bg)',
                    color: 'var(--text-bright)',
                    confirmButtonColor: 'var(--accent-primary)'
                });
            }
            
            // 关闭模态框
            closeImprintWizard();
            
            // 重新载入列表
            if (typeof loadSettings === 'function') {
                loadSettings('imprints');
            }
        } else {
            const errMsg = res ? res.error : '标识物理冲突或路径无写权限';
            addAudit(`❌ [创建失败] ${errMsg}`, "error");
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '❌ 创建失败',
                    text: errMsg,
                    icon: 'error',
                    confirmButtonText: '修改配置',
                    background: 'var(--card-bg)',
                    color: 'var(--text-bright)',
                    confirmButtonColor: 'var(--accent-primary)'
                });
            }
            // 允许重载
            nextBtn.disabled = false;
            nextBtn.innerText = '🚀 激活并诞生';
        }
    } catch (err) {
        addAudit(`❌ [连接崩溃] ${err.message}`, "error");
        if (typeof Swal !== 'undefined') {
            Swal.fire('❌ 错误', err.message, 'error');
        }
        nextBtn.disabled = false;
        nextBtn.innerText = '🚀 激活并诞生';
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

    dropdown.innerHTML = `<div class="dropdown-header">品牌/版图 矩阵</div>` + imprints.map(im => `
        <div class="dropdown-item imprint-node ${im.id === activeId ? 'active' : ''}" onclick="event.stopPropagation(); switchImprint('${im.id}'); document.getElementById('imprint-dropdown').style.display='none';">
            <div class="imprint-item-header">
                <span class="imprint-title">${im.name || im.id}</span>
                <div style="display:flex; align-items:center; gap:10px;">
                    <span class="imprint-id-tag">${im.id}</span>
                    ${im.id === activeId ? '<span class="active-badge">ACTIVE</span>' : ''}
                </div>
            </div>
            <div class="imprint-path-row">📂 ${im.path}</div>
        </div>
    `).join('') + `
        <div class="dropdown-item imprint-node add-new" onclick="event.stopPropagation(); window.showView('settings', 'imprints'); document.getElementById('imprint-dropdown').style.display='none';">
            <div class="imprint-title" style="color: var(--accent-primary);">⚙️ 出版版图管理</div>
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
            <div class="section-header"><h3>🏢 出版版图管理 (Press Imprints Management)</h3></div>
            
            <!-- 🏛️ Industrial Memo: Imprint as an Independent Studio -->
            <div class="sovereign-memo glass-panel" style="margin-bottom: 30px; padding: 25px; border-left: 4px solid var(--accent-primary); background: rgba(163, 76, 255, 0.03);">
                <h4 style="color: var(--accent-primary); margin-bottom: 12px; font-weight: 900; letter-spacing: 1px;">🏢 工业识见：将版图视为您的“独立出版单元”</h4>
                <p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.7;">
                    在专业的出版工业中，<b>版图 (Imprint)</b> 是集团旗下的独立运作单元。在 Illacme 中：<br>
                    • <b>物理独立</b>：每个版图拥有专属的原稿文库（Vault），物理隔离，确保全域安全。<br>
                    • <b>意志独立</b>：每个版图可以绑定不同的算力底座，拥有独特的编辑逻辑和指令矩阵。<br>
                    • <b>分发独立</b>：每个版图可以拥有独立的主题、SEO 策略和全球分发通道。<br>
                    <span style="color: var(--accent-secondary); font-size: 0.75rem; font-weight: 800;">💡 您可以像管理出版集团一样，在此处调度、切换您的多个出版版图。</span>
                </p>
            </div>

            <p class="section-desc">全局掌控您的数字出版帝国。在这里，您可以一键在不同的出版版图之间切换意志。</p>
            
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
                                    <span class="tiny-label">文库文稿数量</span>
                                    <span class="tiny-label mono">${stat.doc_count} 项</span>
                                </div>
                                
                                <div class="path-preview">
                                    📂 ${im.path}
                                </div>

                                <div class="p-control-group">
                                    ${isActive ? 
                                        '<button class="action-btn" disabled style="opacity:0.5;">执行中</button>' : 
                                        `<button class="action-btn glow-btn" onclick="switchImprint('${im.id}')">🔄 切换版图</button>`}
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
