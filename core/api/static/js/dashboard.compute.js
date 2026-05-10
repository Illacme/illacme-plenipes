/**
 * 🧠 [V67.0] Illacme Plenipes Sovereign Compute Command Center
 * 职责：物理算力资源管理、版图意志对正、能量链路调度。
 * 产品设计：产品设计专家级重构，引入工业级指挥中心交互美学。
 */
window.showNotification = (text, type = 'success') => {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer);
            toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
    });
    Toast.fire({
        icon: type,
        title: text
    });
};

// 🛰️ [V71.1] Global Sovereign Dropdown Controller
window.toggleSovereignDropdown = (event, menuId, searchInputId) => {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const menu = document.getElementById(menuId);
    if (!menu) return;

    // 关闭所有其他下拉菜单以保持 UI 纯净
    document.querySelectorAll('.custom-dropdown-menu').forEach(m => {
        if (m.id !== menuId) m.classList.remove('show');
    });

    menu.classList.toggle('show');
    
    if (menu.classList.contains('show') && searchInputId) {
        setTimeout(() => {
            const searchInput = document.getElementById(searchInputId);
            if (searchInput) searchInput.focus();
        }, 50);
    }
};

window.filterProtocols = (term, listId) => {
    const lowerTerm = term.toLowerCase();
    const items = document.querySelectorAll(`#${listId} .dropdown-item`);
    items.forEach(item => {
        const name = (item.getAttribute('data-name') || '').toLowerCase();
        item.style.display = name.includes(lowerTerm) ? 'flex' : 'none';
    });
};

// 🛰️ [V72.5] Integrated Field Error Controller
window.showFieldError = (fieldId, message) => {
    const errorSpan = document.getElementById(`error-${fieldId}`);
    const input = document.getElementById(`swal-input-${fieldId}`) || document.getElementById(`provider-trigger-${fieldId}`);
    
    if (errorSpan) {
        errorSpan.innerText = message;
        errorSpan.classList.add('active');
        setTimeout(() => errorSpan.classList.remove('active'), 3000);
    }
    
    if (input) {
        input.classList.add('shake-hint');
        setTimeout(() => input.classList.remove('shake-hint'), 500);
        if (input.focus) input.focus();
    }
};

window.loadComputeCenter = async () => {
    const root = document.getElementById('compute-center-root');
    if (!root) return;

    root.innerHTML = `
        <div class="compute-center-container fade-in">
            <!-- 🛰️ Command Deck Header -->
            <div class="center-header-vessel glass-panel">
                <div class="deck-branding">
                    <div class="deck-icon-orbit">
                        <span class="icon">🧠</span>
                        <div class="orbit-ring"></div>
                    </div>
                    <div class="deck-meta">
                        <h2>算力中心</h2>
                        <p class="subtitle">物理资产全域感应与版图调度矩阵</p>
                    </div>
                </div>
                <div class="deck-navigation">
                    <nav class="tactical-tabs">
                        <button class="t-tab active" onclick="switchComputeTab('infrastructure')">
                            <span class="t-icon">🧱</span> 物理底座 (Infrastructure)
                        </button>
                        <button class="t-tab" onclick="switchComputeTab('strategy')">
                            <span class="t-icon">⚖️</span> 调度策略 (Strategy Matrix)
                        </button>
                    </nav>
                </div>
            </div>

            <!-- 🌌 Dynamic Tactical Content -->
            <div id="compute-tab-content" class="compute-viewport">
                <div class="loading-scanner">
                    <div class="scan-line"></div>
                    <p>正在同步物理主权频率...</p>
                </div>
            </div>
        </div>
    `;

    // 默认启动物理感应
    await switchComputeTab('infrastructure');
};

window.switchComputeTab = async (tab) => {
    const container = document.getElementById('compute-tab-content');
    if (!container) return;

    // 视觉反馈：切换 Tab 激活状态
    document.querySelectorAll('.tactical-tabs .t-tab').forEach(btn => {
        btn.classList.toggle('active', btn.onclick.toString().includes(tab));
    });

    // 注入加载动画
    container.innerHTML = `
        <div class="loading-scanner">
            <div class="scan-line"></div>
            <p>正在扫描 ${tab === 'infrastructure' ? '物理资产' : '版图意志'}...</p>
        </div>
    `;

    if (tab === 'infrastructure') {
        await renderInfrastructureTab(container);
    } else {
        await renderStrategyTab(container);
    }
};

// --- 🧱 物理底座层：工业化动力单元渲染 ---
async function renderInfrastructureTab(container) {
    const res = await apiFetch('/api/system/config?level=local');
    const nodes = res.config?.translation?.compute_nodes || {};
    window._activeNodeIds = Object.keys(nodes); 

    let html = `
        <div class="infrastructure-hub">
            <!-- 🛡️ Sovereignty Alert -->
            <div class="license-banner">
                <div class="license-info">
                    <h4>🛡️ 物理主权屏障已激活</h4>
                    <p>当前环境密钥与端点已物理隔离在 <code>config.local.yaml</code>，绝不参与版图分发。</p>
                </div>
                <button class="mini-btn glow-btn" onclick="showAddNodeModal()">+ 新增物理单元</button>
            </div>
            
            <div class="node-grid">
                ${Object.entries(nodes)
            .sort((a, b) => {
                const aId = a[0];
                const bId = b[0];
                const aNode = a[1];
                const bNode = b[1];
                
                // 🚀 [V72.7] 时间主权优先级 (最新编辑在上)
                const aTime = aNode.last_updated || 0;
                const bTime = bNode.last_updated || 0;
                if (aTime !== bTime) return bTime - aTime;

                // 1. 活跃状态优先级 (Enabled > Disabled)
                const aActive = aNode.enabled !== false;
                const bActive = bNode.enabled !== false;
                if (aActive !== bActive) return bActive - aActive;
                
                // 2. 协议家族优先级 (Native > Anthropic > Standard > Others)
                const familyPriority = { 'native': 3, 'anthropic': 2, 'standard': 1 };
                const aPrio = familyPriority[aNode.protocol_family] || 0;
                const bPrio = familyPriority[bNode.protocol_family] || 0;
                if (aPrio !== bPrio) return bPrio - aPrio;
                
                // 3. 标识名 A-Z 排序
                return aId.localeCompare(bId);
            })
            .map(([id, node]) => `
                    <div class="node-unit ${node.enabled !== false ? 'active' : 'inactive'}" id="node-unit-${id}">
                        <div class="node-header">
                            <div class="node-identity">
                                <div class="node-icon-vessel">
                                    ${getNodeIcon(node.type)}
                                </div>
                                <div class="node-name-group">
                                    <div class="node-name">${id}</div>
                                    <div class="node-type">算力单元 | ${node.provider_name || node.type?.toUpperCase() || 'UNSPECIFIED'}</div>
                                    <div class="protocol-badge ${node.protocol_family}">
                                        ${node.protocol_family === 'standard' ? 'Standard (V1)' :
                    node.protocol_family === 'anthropic' ? 'Anthropic (V2)' : 'Native Protocol'}
                                    </div>
                                </div>
                            </div>
                            <div class="node-actions">
                                <button class="tactical-btn" onclick="probeNode('${id}')" title="全域脉冲探测">📡</button>
                                <button class="tactical-btn" onclick="editNode('${id}')" title="单元参数修正">⚙️</button>
                            </div>
                        </div>

                        <!-- 📡 Telemetry Data -->
                        <div class="node-telemetry">
                            <div class="t-item">
                                <div class="label">工作状态</div>
                                <div class="value ${node.enabled !== false ? 'healthy' : ''}">
                                    ${node.enabled !== false ? '已就绪 (Ready)' : '已停机'}
                                </div>
                            </div>
                            <div class="t-item">
                                <div class="label">健康分 (Score)</div>
                                <div class="value ${node.health?.score > 80 ? 'healthy' : 'warning'}">${node.health?.score || 100}</div>
                            </div>
                            <div class="t-item">
                                <div class="label">平均延迟</div>
                                <div class="value">${node.health?.avg_latency || 0}ms</div>
                            </div>
                            <div class="t-item">
                                <div class="label">成功率</div>
                                <div class="value">${node.health?.success_rate || 100}%</div>
                            </div>
                            <div class="t-item">
                                <div class="label">物理延迟</div>
                                <div class="value" id="latency-${id}">-- ms</div>
                            </div>
                            <div class="t-item" style="grid-column: span 2; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 10px;">
                                <div class="label">端点地址</div>
                                <div class="value mono" style="font-size: 0.8rem; opacity: 0.7;">${node.base_url || 'NATIVE'}</div>
                            </div>
                        </div>

                        <!-- 🧠 Model Capacity Bubble -->
                        <div class="model-matrix-wrap">
                            <span class="model-chip active">${node.model || '未绑定模型'}</span>
                        </div>
                        
                        <div class="node-status-line" id="probe-status-${id}">等待指令反馈...</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    container.innerHTML = html;
}

// --- ⚖️ 调度策略层：战术指挥矩阵渲染 ---
async function renderStrategyTab(container) {
    const res = await apiFetch('/api/system/config');
    const config = res.config || res;
    const trans = config.translation || {};
    
    // 🚀 [V73.5] 同步至全局状态中枢，确保后续更新可追踪
    window.settingsData = window.settingsData || {};
    window.settingsData.translation = trans;
    const nodes = trans.compute_nodes || {};

    let html = `
        <div class="strategy-command-deck fade-in">
            <div class="deck-header">
                <div class="deck-title-group">
                    <h2>调度意志对正</h2>
                    <p>为版图 <b>${config.imprint_name || 'Current'}</b> 建立专属算力链路</p>
                </div>
                <div class="strategy-mode-badge badge active">${(trans.strategy || 'single').toUpperCase()} MODE</div>
            </div>

            <!-- ⚖️ The Binding Matrix: Visual Linkage -->
            <div class="strategy-binding-matrix">
                <!-- PRIMARY NODE -->
                <div class="binding-terminal primary">
                    <div class="terminal-label">PRIMARY NODE (主力执行)</div>
                    <div class="selection-vessel">
                        <select id="primary_node_selector" 
                                onchange="updateStrategy('primary_node', this.value); fetchNodeModels(this.value, 'primary_model')">
                            <option value="">选择物理底座</option>
                            ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.primary_node ? 'selected' : ''} data-model="${n.model || ''}">${nid}</option>`).join('')}
                        </select>
                        <div class="input-vessel">
                            <input type="text" id="primary_model_input" value="${trans.primary_model || ''}" 
                                   placeholder="执行模型标识符" 
                                   onchange="updateStrategy('primary_model', this.value)">
                            <div id="primary_model_suggestions" class="discovery-suggestions"></div>
                        </div>
                    </div>
                </div>

                <!-- ⚡ Energy Vessel -->
                <div class="binding-vessel">
                    <div class="vessel-icon">⚡</div>
                    <div class="vessel-link-line"></div>
                </div>

                <!-- FALLBACK NODE -->
                <div class="binding-terminal fallback">
                    <div class="terminal-label">FALLBACK NODE (容灾守护)</div>
                    <div class="selection-vessel">
                        <select id="fallback_node_selector"
                                onchange="updateStrategy('fallback_node', this.value); fetchNodeModels(this.value, 'fallback_model')">
                            <option value="">选择物理底座</option>
                            ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.fallback_node ? 'selected' : ''} data-model="${n.model || ''}">${nid}</option>`).join('')}
                        </select>
                        <div class="input-vessel">
                            <input type="text" id="fallback_model_input" value="${trans.fallback_model || ''}" 
                                   placeholder="容灾模型标识符" 
                                   onchange="updateStrategy('fallback_model', this.value)">
                            <div id="fallback_model_suggestions" class="discovery-suggestions"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 🧬 Logic Control Panel -->
            <div class="logic-pod glass-panel" style="padding: 25px; margin-bottom: 30px; border: 1px solid rgba(0, 242, 255, 0.1);">
                <div class="strategy-label">容灾调度算法 (RESILLIENCE ALGORITHM)</div>
                <div class="strategy-list">
                    ${renderStrategyItem('single', '📍 单点模式', '仅通过主力节点执行任务，追求绝对的主权路径控制。', trans.strategy)}
                    ${renderStrategyItem('fallback', '🛡️ 容灾模式', '主力节点故障时，能量自动导向备用节点，确保出版不中断。', trans.strategy)}
                    ${renderStrategyItem('concurrent', '🚀 竞速模式', '主备并联齐发，以毫秒级响应优先者为准，榨取极限性能。', trans.strategy)}
                </div>
            </div>

            <div class="action-deck">
                <button class="primary-btn glow-btn" onclick="saveComputeStrategy()" style="padding: 15px 40px; font-size: 1rem;">
                    固化版图算力意志
                </button>
            </div>
        </div>
    `;
    container.innerHTML = html;
}

function renderStrategyItem(id, name, desc, current) {
    const isActive = (id === (current || 'single'));
    return `
        <div class="strategy-item ${isActive ? 'active' : ''}" onclick="updateStrategy('strategy', '${id}')">
            <div class="radio-indicator"><div class="radio-inner"></div></div>
            <div class="strategy-info">
                <div class="strategy-name">${name}</div>
                <div class="strategy-desc">${desc}</div>
            </div>
        </div>
    `;
}

function getNodeIcon(type) {
    const map = {
        'openai': '🌐',
        'ollama': '🦙',
        'anthropic': '🎭',
        'groq': '⚡',
        'deepseek': '🐳',
        'google': '💎',
        'siliconflow': '🌊',
        'lmstudio': '🏠'
    };
    return map[type?.toLowerCase()] || '🤖';
}

// --- 🕹️ 交互控制核心 ---

window.updateStrategy = (key, value) => {
    if (!window.settingsData.translation) window.settingsData.translation = {};
    window.settingsData.translation[key] = value;
    
    // 🚀 [V73.6] 智能对正逻辑：切换节点时自动补全模型信息
    if (key.endsWith('_node')) {
        const type = key.split('_')[0]; // 'primary' or 'fallback'
        const selector = document.getElementById(`${key}_selector`);
        const selectedOption = selector.options[selector.selectedIndex];
        const defaultModel = selectedOption.getAttribute('data-model');
        
        if (defaultModel) {
            const input = document.getElementById(`${type}_model_input`);
            if (input) {
                input.value = defaultModel;
                window.settingsData.translation[`${type}_model`] = defaultModel;
                addAudit(`📡 已自动锚定节点 [${value}] 的物理默认模型: ${defaultModel}`, "info");
            }
        }
    }

    // 视觉联动：如果是切换调度模式，实时更新 UI 状态
    if (key === 'strategy') {
        document.querySelectorAll('.strategy-item').forEach(el => el.classList.remove('active'));
        // 寻找包含该 ID 的选项并激活
        const items = document.querySelectorAll('.strategy-item');
        items.forEach(item => {
            if (item.getAttribute('onclick').includes(`'${value}'`)) {
                item.classList.add('active');
            }
        });
        
        // 更新顶部勋章文字
        const badge = document.querySelector('.strategy-mode-badge');
        if (badge) badge.innerText = `${value.toUpperCase()} MODE`;
        
        addAudit(`⚖️ 算力调度模式已实时切换为: ${value.toUpperCase()}`, "info");
    }

    // 🚀 [V73.7] 视觉唤醒：提醒需要点击固化按钮
    const saveBtn = document.querySelector('.strategy-command-deck .primary-btn');
    if (saveBtn) {
        saveBtn.classList.add('pulse-alert');
        saveBtn.innerHTML = '🛡️ 捕获到新意志: 请固化';
    }
};

window.probeNode = async (id) => {
    const statusEl = document.getElementById(`probe-status-${id}`);
    const latencyEl = document.getElementById(`latency-${id}`);
    if (statusEl) statusEl.innerHTML = '<span class="pulsing">发射脉冲探测中...</span>';

    const startTime = Date.now();
    const res = await apiFetch('/api/compute/nodes/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    });
    const duration = Date.now() - startTime;

    if (statusEl) {
        if (res?.status === 'success') {
            statusEl.innerHTML = `<span class="online">✅ 物理响应正常 | 链路固化完毕</span>`;
            if (latencyEl) latencyEl.innerHTML = `<span class="healthy">${res.latency || duration}ms</span>`;
            document.getElementById(`node-unit-${id}`)?.classList.add('pulse-glow');
        } else {
            statusEl.innerHTML = `<span class="offline">❌ 感应丢失: ${res.error || '信号断裂'}</span>`;
            if (latencyEl) latencyEl.innerHTML = `<span class="offline">TIMEOUT</span>`;
        }
    }
};

window.saveComputeStrategy = async () => {
    // 逻辑保持不变，但增加视觉反馈
    const btn = event.target;
    const originalText = btn.innerText;
    btn.innerText = "正在固化意志...";

    const t = window.settingsData?.translation || {};
    const payload = {
        'translation.primary_node': t.primary_node,
        'translation.primary_model': t.primary_model,
        'translation.fallback_node': t.fallback_node,
        'translation.fallback_model': t.fallback_model,
        'translation.strategy': t.strategy
    };

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    btn.innerText = originalText;
    if (res?.status === 'success') {
        showNotification('✅ 算力意志固化成功', 'success');
        btn.classList.remove('pulse-alert'); // 移除告警状态
    } else {
        showNotification('❌ 固化失败: ' + (res?.error || '物理链路异常'), 'error');
    }
};

window.editNode = async (id) => {
    addAudit(`⚙️ 正在从物理层提取单元 [${id}] 的参数...`, "info");

    try {
        const res = await apiFetch('/api/system/config?level=local');
        const nodes = res.config?.translation?.compute_nodes || {};
        const node = nodes[id] || {};

        const pluginRes = await apiFetch('/api/plugins/list');
        const protocols = (pluginRes.plugins || [])
            .filter(p => p.category === 'protocol')
            .sort((a, b) => {
                if (a.protocol_family !== b.protocol_family) {
                    return a.protocol_family === 'native' ? -1 : 1;
                }
                return a.name.localeCompare(b.name);
            });

        const activeProtocol = protocols.find(p => p.id === node.type) || { name: '请选择协议驱动...' };

        const { value: formValues } = await Swal.fire({
            title: `⚙️ 修正算力单元: ${id}`,
            html: `
                <div class="swal-edit-grid sovereign-form">
                    <label>算力驱动 (Provider)</label>
                    <div class="sovereign-select-vessel">
                        <input type="hidden" id="swal-input-type" value="${node.type || ''}">
                        <div class="sovereign-input-field custom-select-trigger" id="provider-trigger-edit"
                             onclick="toggleSovereignDropdown(event, 'provider-menu-edit', 'provider-search-input-edit')">
                            ${activeProtocol.name}
                        </div>
                        <div class="custom-dropdown-menu" id="provider-menu-edit">
                            <div class="dropdown-search-vessel" onclick="event.stopPropagation()">
                                <input type="text" class="dropdown-search-input" id="provider-search-input-edit" 
                                       oninput="filterProtocols(this.value, 'provider-list-items-edit')"
                                       placeholder="🔍 搜索驱动名称或协议..." autocomplete="off">
                            </div>
                            <div id="provider-list-items-edit">
                                ${protocols.map(p => `
                                    <div class="dropdown-item ${p.id === node.type ? 'selected' : ''}" 
                                         data-name="${p.name.toLowerCase()}"
                                         onclick="selectProvider('${p.id}', '${p.name.replace(/'/g, "\\'")}', '${p.default_url || ''}')">
                                        <span>${p.name}</span>
                                        <span class="badge">${p.protocol_family.toUpperCase()}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    
                    <label>端点地址 (Endpoint)</label>
                    <input id="swal-input-url" class="swal2-input" value="${node.base_url || ''}" placeholder="e.g. https://api.openai.com/v1">
                    
                    <label>物理密钥 (API Key)</label>
                    <input id="swal-input-key" class="swal2-input" type="password" value="${node.api_key || ''}" placeholder="sk-...">

                    <div style="grid-column: span 2; margin-top: 5px;">
                        <label>活跃模型感应 (Model Discovery)</label>
                        <div class="sovereign-select-vessel" style="margin-top: 8px;">
                            <div style="display: flex; gap: 0;">
                                <input id="swal-input-model" class="swal2-input" style="margin:0; flex:1; border-top-right-radius:0; border-bottom-right-radius:0;" 
                                       value="${node.model || ''}" placeholder="选择或输入模型 ID">
                                <button type="button" class="mini-btn glow-btn" style="border-top-left-radius:0; border-bottom-left-radius:0;" 
                                        onclick="discoverModels(event, '${id}'); return false;">📡 感应</button>
                            </div>
                            <div id="asset-discovery-menu" class="custom-dropdown-menu asset-dropdown"></div>
                        </div>
                    </div>
                </div>
            `,
            width: '600px',
            confirmButtonText: '🏗️ 固化算力配置',
            didOpen: () => {
                const closeMenu = (e) => {
                    if (!e.target.closest('.sovereign-select-vessel')) {
                        document.querySelectorAll('.custom-dropdown-menu').forEach(m => m.classList.remove('show'));
                    }
                };
                document.addEventListener('click', closeMenu);
                window._currentSwalCloseMenu = closeMenu;
            },
            focusConfirm: false,
            confirmButtonText: '🏗️ 固化算力配置',
            showCancelButton: true,
            cancelButtonText: '放弃',
            willClose: () => {
                if (window._currentSwalCloseMenu) {
                    document.removeEventListener('click', window._currentSwalCloseMenu);
                    delete window._currentSwalCloseMenu;
                }
            },
            preConfirm: () => {
                return {
                    base_url: document.getElementById('swal-input-url').value,
                    api_key: document.getElementById('swal-input-key').value,
                    type: document.getElementById('swal-input-type').value,
                    model: document.getElementById('swal-input-model').value
                }
            }
        });

        if (formValues) {
            addAudit(`🖊️ 正在原地修正单元 [${id}] 的物理参数...`, "info");
            const payload = {};
            payload[`translation.compute_nodes.${id}.base_url`] = formValues.base_url;
            payload[`translation.compute_nodes.${id}.api_key`] = formValues.api_key;
            payload[`translation.compute_nodes.${id}.type`] = formValues.type;
            payload[`translation.compute_nodes.${id}.model`] = formValues.model;
            payload[`translation.compute_nodes.${id}.last_updated`] = Date.now(); // 🚀 [V72.7] 时间主权标记

            const updateRes = await apiFetch('/api/config/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (updateRes?.status === 'success') {
                addAudit(`✅ 单元 [${id}] 参数已物理固化。`, "success");
                loadComputeCenter();
            } else {
                addAudit(`❌ 固化失败: ${updateRes?.error || '物理链路冲突'}`, "error");
            }
        }
    } catch (e) {
        addAudit(`🚨 交互逻辑断裂: ${e.message}`, "error");
        console.error(e);
    }
};

window.selectProvider = (id, name, defaultUrl) => {
    const input = document.getElementById('swal-input-type');
    const tAdd = document.getElementById('provider-trigger-add');
    const tEdit = document.getElementById('provider-trigger-edit');
    const mAdd = document.getElementById('provider-menu-add');
    const mEdit = document.getElementById('provider-menu-edit');
    const urlInput = document.getElementById('swal-input-url');

    if (input) input.value = id;
    if (tAdd) tAdd.innerText = name;
    if (tEdit) tEdit.innerText = name;
    
    if (mAdd) mAdd.classList.remove('show');
    if (mEdit) mEdit.classList.remove('show');

    // 🚀 [V67.6] 感应式 URL 注入：如果当前没有填 URL，则自动补齐官方端点
    if (urlInput && defaultUrl && (!urlInput.value || urlInput.value.includes('example.com') || urlInput.value.includes('localhost'))) {
        urlInput.value = defaultUrl;
        addAudit(`📡 已自动感应并锚定协议 [${name}] 的官方端点。`, "info");
    }
};

window.discoverModels = async (event, nodeId) => {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const btn = event ? (event.currentTarget || event.target) : null;
    // 如果没有按钮，尝试从 DOM 获取（作为后备）
    const fallbackBtn = document.querySelector('button[onclick*="discoverModels"]');
    const activeBtn = btn || fallbackBtn;

    const originalText = btn.innerText;
    const type = document.getElementById('swal-input-type').value;
    const key = document.getElementById('swal-input-key').value;
    const url = document.getElementById('swal-input-url').value;
    const resultsContainer = document.getElementById('asset-discovery-menu');

    const typeTrigger = document.getElementById('provider-trigger-add') || document.getElementById('provider-trigger-edit');

    if (!type || type === "") {
        if (typeTrigger) {
            typeTrigger.classList.add('shake-hint');
            setTimeout(() => typeTrigger.classList.remove('shake-hint'), 500);
        }
        addAudit(`⚠️ 物理链路握手失败：请先选择有效的算力驱动协议。`, "warning");
        return;
    }

    btn.innerText = "正在感应...";
    btn.disabled = true;
    resultsContainer.innerHTML = '<div class="loading-mini">全域扫描中...</div>';

    try {
        const query = new URLSearchParams({
            node_id: nodeId,
            provider: type,
            api_key: key,
            base_url: url
        });
        const res = await apiFetch(`/api/compute/models?${query}`);

        if (res.models && res.models.length > 0) {
            resultsContainer.innerHTML = `
                <div class="dropdown-search-vessel">
                    <input type="text" class="dropdown-search-input" placeholder="🔍 检索感应资产..." 
                           oninput="filterDiscoveredModels(this.value)" onclick="event.stopPropagation()">
                </div>
                <div id="discovered-models-scroll" style="max-height: 200px; overflow-y: auto;">
                    ${res.models.map(m => `
                        <div class="dropdown-item" onclick="selectDiscoveredModel('${m}')">
                            <span>💎 ${m}</span>
                        </div>
                    `).join('')}
                </div>
            `;
            resultsContainer.classList.add('show');
            if (typeof addAudit === 'function') {
                addAudit(`✅ 单元 [${nodeId}] 感应到 ${res.models.length} 个可用模型。`, "success");
            }
        }
    } catch (e) {
        resultsContainer.innerHTML = `<div class="error-text">感应失败: ${e.message}</div>`;
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
};

window.selectDiscoveredModel = (model) => {
    const input = document.getElementById('swal-input-model');
    const resultsContainer = document.getElementById('asset-discovery-menu');
    if (input) {
        input.value = model;
        if (resultsContainer) resultsContainer.classList.remove('show');
        if (typeof addAudit === 'function') {
            addAudit(`💎 已在物理层锁定模型: ${model}`, "info");
        }
    }
};

window.showAddNodeModal = async () => {
    addAudit(`🏗️ 正在准备物理算力单元初始化环境...`, "info");

    try {
        const pluginRes = await apiFetch('/api/plugins/list');
        const protocols = (pluginRes.plugins || [])
            .filter(p => p.category === 'protocol')
            .sort((a, b) => {
                if (a.protocol_family !== b.protocol_family) {
                    return a.protocol_family === 'native' ? -1 : 1;
                }
                return a.name.localeCompare(b.name);
            });

        const { value: formValues } = await Swal.fire({
            title: '🏗️ 新增物理算力单元',
            html: `
                <div class="swal-edit-grid sovereign-form">
                    <label>单元唯一标识 (Node ID) <span id="error-id" class="label-error"></span></label>
                    <input id="swal-input-id" class="swal2-input" placeholder="e.g. my_new_node">

                    <label>算力驱动 (Provider) <span id="error-type" class="label-error"></span></label>
                    <div class="sovereign-select-vessel">
                        <input type="hidden" id="swal-input-type" value="">
                        <div class="sovereign-input-field custom-select-trigger" id="provider-trigger-add"
                             onclick="toggleSovereignDropdown(event, 'provider-menu-add', 'provider-search-input-add')">
                            请选择协议驱动...
                        </div>
                        <div class="custom-dropdown-menu" id="provider-menu-add">
                            <div class="dropdown-search-vessel" onclick="event.stopPropagation()">
                                <input type="text" class="dropdown-search-input" id="provider-search-input-add" 
                                       oninput="filterProtocols(this.value, 'provider-list-items-add')"
                                       placeholder="🔍 搜索驱动名称或协议..." autocomplete="off">
                            </div>
                            <div id="provider-list-items-add">
                                ${protocols.map(p => `
                                    <div class="dropdown-item" 
                                         data-name="${p.name.toLowerCase()}"
                                         onclick="selectProvider('${p.id}', '${p.name.replace(/'/g, "\\'")}', '${p.default_url || ''}')">
                                        <span>${p.name}</span>
                                        <span class="badge">${p.protocol_family.toUpperCase()}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    
                    <label>端点地址 (Endpoint)</label>
                    <input id="swal-input-url" class="swal2-input" placeholder="e.g. https://api.openai.com/v1">
                    
                    <label>物理密钥 (API Key)</label>
                    <input id="swal-input-key" class="swal2-input" type="password" placeholder="sk-...">

                    <div style="grid-column: span 2; margin-top: 5px;">
                        <label>活跃模型感应 (Model Discovery)</label>
                        <div class="sovereign-select-vessel" style="margin-top: 8px;">
                            <div style="display: flex; gap: 0;">
                                <input id="swal-input-model" class="swal2-input" style="margin:0; flex:1; border-top-right-radius:0; border-bottom-right-radius:0;" placeholder="选择或输入模型 ID">
                                <button type="button" class="mini-btn glow-btn" style="border-top-left-radius:0; border-bottom-left-radius:0;" 
                                        onclick="discoverModels(event, 'new_node_temp'); return false;">📡 感应</button>
                            </div>
                            <div id="asset-discovery-menu" class="custom-dropdown-menu asset-dropdown"></div>
                        </div>
                    </div>
                </div>
            `,
            width: '600px',
            confirmButtonText: '🏗️ 初始化并固化算力单元',
            didOpen: () => {
                const closeMenu = (e) => {
                    if (!e.target.closest('.sovereign-select-vessel')) {
                        document.querySelectorAll('.custom-dropdown-menu').forEach(m => m.classList.remove('show'));
                    }
                };
                document.addEventListener('click', closeMenu);
                window._currentSwalCloseMenu = closeMenu;
            },
            focusConfirm: false,
            background: 'rgba(10, 15, 25, 0.98)',
            backdrop: `rgba(0,0,0,0.4) blur(10px)`,
            color: 'var(--text-bright)',
            showCancelButton: true,
            cancelButtonText: '放弃',
            willClose: () => {
                if (window._currentSwalCloseMenu) {
                    document.removeEventListener('click', window._currentSwalCloseMenu);
                    delete window._currentSwalCloseMenu;
                }
            },
            preConfirm: () => {
                const nid = document.getElementById('swal-input-id').value;
                const type = document.getElementById('swal-input-type').value;

                if (!nid) {
                    showFieldError('id', '不能为空');
                    return false;
                }

                // 🚀 [V72.2] 格式校验：Slug 规范
                const idRegex = /^[a-z0-9_-]+$/i;
                if (!idRegex.test(nid)) {
                    showFieldError('id', '格式非法 (限字母/数字/下划线/-)');
                    return false;
                }

                // 🚀 [V72.2] 查重校验
                if (window._activeNodeIds && window._activeNodeIds.includes(nid)) {
                    showFieldError('id', 'ID 已存在，请更换');
                    return false;
                }

                if (!type) {
                    showFieldError('type', '请选择协议');
                    return false;
                }

                return {
                    id: nid,
                    base_url: document.getElementById('swal-input-url').value,
                    api_key: document.getElementById('swal-input-key').value,
                    type: document.getElementById('swal-input-type').value,
                    model: document.getElementById('swal-input-model').value
                }
            }
        });

        if (formValues) {
            addAudit(`🚀 正在物理层划定新单元 [${formValues.id}]...`, "info");
            const payload = {};
            const prefix = `translation.compute_nodes.${formValues.id}`;
            payload[`${prefix}.base_url`] = formValues.base_url;
            payload[`${prefix}.api_key`] = formValues.api_key;
            payload[`${prefix}.type`] = formValues.type;
            payload[`${prefix}.model`] = formValues.model;
            payload[`${prefix}.last_updated`] = Date.now(); // 🚀 [V72.7] 时间主权标记
            payload[`${prefix}.enabled`] = true;

            const updateRes = await apiFetch('/api/config/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (updateRes?.status === 'success') {
                addAudit(`✅ 新单元 [${formValues.id}] 已物理固化。`, "success");
                loadComputeCenter();
            } else {
                addAudit(`❌ 划定失败: ${updateRes?.error || '物理链路冲突'}`, "error");
            }
        }
    } catch (e) {
        addAudit(`🚨 划定流程中断: ${e.message}`, "error");
    }
};

// 🚀 [V67.0] 实时模型感应与策略联动
window.fetchNodeModels = async (nodeId, targetField) => {
    const suggestions = document.getElementById(`${targetField}_suggestions`);
    if (!nodeId || !suggestions) return;

    suggestions.innerHTML = '<div class="suggestion-item loading">📡 正在感应单元模型...</div>';

    try {
        const res = await apiFetch(`/api/compute/models?node_id=${nodeId}`);
        if (res?.models?.length > 0) {
            suggestions.innerHTML = res.models.map(m => `
                <div class="suggestion-item" onclick="applyModelSuggestion('${targetField}', '${m}')">
                    <span class="icon">💎</span> ${m}
                </div>
            `).join('');
        } else {
            suggestions.innerHTML = '<div class="suggestion-item error">⚠️ 未感应到活跃模型</div>';
        }
    } catch (e) {
        suggestions.innerHTML = '<div class="suggestion-item error">🛑 感应链路中断</div>';
    }
};

window.applyModelSuggestion = (targetField, model) => {
    const input = document.getElementById(`${targetField}_input`);
    const suggestions = document.getElementById(`${targetField}_suggestions`);
    if (input) input.value = model;
    if (suggestions) suggestions.innerHTML = '';

    // 更新内存状态
    updateStrategy(targetField, model);
    window.showNotification(`已同步算力意志: ${model}`, 'success');
};

window.filterDiscoveredModels = (term) => {
    const items = document.querySelectorAll('#discovered-models-scroll .dropdown-item');
    const lowerTerm = term.toLowerCase();
    items.forEach(item => {
        const name = item.innerText.toLowerCase();
        item.style.display = name.includes(lowerTerm) ? 'flex' : 'none';
    });
};

// 点击外部关闭感应列表
document.addEventListener('mousedown', (e) => {
    if (!e.target.closest('.input-vessel')) {
        document.querySelectorAll('.discovery-suggestions').forEach(el => el.innerHTML = '');
    }
});
