/**
 * 🧠 [V74.20] Illacme Plenipes Compute Command Center
 * 职责：物理算力资源管理、全域配置对正、能量链路调度。
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

// 🛰️ [V74.22] 策略勋章同步中枢：确保在不同 Tab 切换时状态依然对正
window.syncStrategyBadge = (forcedValue = null) => {
    const strategy = forcedValue || window.settingsData?.translation?.strategy || 'single';
    const badgeSlot = document.getElementById('compute-strategy-badge-slot');
    if (badgeSlot) {
        badgeSlot.innerHTML = `<div class="strategy-mode-badge badge active" style="font-size: 0.65rem; padding: 4px 12px;">[${strategy.toUpperCase()} MODE]</div>`;
    }
};

// 🛰️ [V71.1] Global Dropdown Controller
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
    const topActions = document.getElementById('compute-header-actions-top');
    const navTabsSlot = document.getElementById('compute-nav-tabs-slot');
    const navActionsSlot = document.getElementById('compute-nav-actions-slot');
    const contentRoot = document.getElementById('compute-center-root');

    if (!topActions || !navTabsSlot || !navActionsSlot || !contentRoot) return;

    // 1. 清空顶部矩阵（将在 switchComputeTab 中按需注入搜索框）
    topActions.innerHTML = '';

    // 2. 注入导航标签与策略勋章
    navTabsSlot.innerHTML = `
        <div style="display: flex; align-items: center; gap: 24px;">
            <nav class="tactical-tabs">
                <button class="t-tab active" data-tab="infrastructure" onclick="switchComputeTab('infrastructure')">
                    <span class="t-icon">🧱</span> 算力单元
                </button>
                <button class="t-tab" data-tab="strategy" onclick="switchComputeTab('strategy')">
                    <span class="t-icon">⚖️</span> 调度策略
                </button>
            </nav>
            <div id="compute-strategy-badge-slot">
                <div class="strategy-mode-badge badge active" style="font-size: 0.65rem; padding: 4px 12px;">LOADING...</div>
            </div>
        </div>
    `;

    // 3. 注入操作动作
    navActionsSlot.innerHTML = `
        <div class="tactical-actions" style="display: flex; gap: 12px; align-items: center;">
            <button class="mini-btn glow-btn" onclick="showAddNodeModal()">+ 新增算力单元</button>
            <button class="mini-btn" onclick="probeAllNodes()">📡 全域脉冲</button>
            <button class="mini-btn" onclick="loadComputeCenter()">🔄 刷新</button>
        </div>
    `;

    // 🚀 [V74.24] 预加载全局配置并同步勋章，建立初始主权感应
    try {
        const res = await apiFetch('/api/system/config');
        const config = res.config || res; // 🛡️ 兼容不同层级的 API 响应结构
        window.settingsData = window.settingsData || {};
        window.settingsData.translation = config.translation || {};
        window.syncStrategyBadge();
    } catch (e) {
        console.error("Failed to pre-sync strategy badge:", e);
    }

    // 4. 清空内容区并准备加载
    contentRoot.innerHTML = `
        <div id="compute-tab-viewport" class="compute-viewport" style="margin-top: 0 !important; padding-top: 5px;">
            <div class="loading-scanner">
                <div class="scan-line"></div>
                <p>正在同步物理全域频率...</p>
            </div>
        </div>
    `;

    // 默认启动物理感应
    await switchComputeTab('infrastructure');
};

window.switchComputeTab = async (tab) => {
    const container = document.getElementById('compute-tab-viewport');
    if (!container) return;

    // 视觉反馈：切换 Tab 激活状态
    document.querySelectorAll('.tactical-tabs .t-tab').forEach(btn => {
        btn.classList.toggle('active', btn.onclick.toString().includes(tab));
    });

    // 动态调整顶部工具栏可见性
    const topActions = document.getElementById('compute-header-actions-top');
    const navActions = document.getElementById('compute-nav-actions-slot');
    if (topActions) {
        if (tab === 'infrastructure') {
            topActions.innerHTML = `
                <div class="search-box">
                    <input type="text" id="compute-search" placeholder="搜索单元、提供商或模型..." oninput="filterNodes(this.value)">
                </div>
            `;
            if (navActions) navActions.style.display = 'flex';
        } else {
            topActions.innerHTML = '';
            if (navActions) navActions.style.display = 'none';
        }
    }

    // 注入加载动画
    container.innerHTML = `
        <div class="loading-scanner">
            <div class="scan-line"></div>
            <p>正在扫描 ${tab === 'infrastructure' ? '算力资源' : '全域配置'}...</p>
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
    // 🚀 [V74.24] 强化感应：始终在切换 Tab 时尝试从服务器拉取最新配置，确保物理层与逻辑层同步
    try {
        const res = await apiFetch('/api/system/config');
        const config = res.config || res;
        if (config.translation) {
            window.settingsData = window.settingsData || {};
            window.settingsData.translation = config.translation;
        }
    } catch (e) {
        console.warn("Soft sync failed, falling back to memory:", e);
    }
    window.syncStrategyBadge();

    const res = await apiFetch('/api/system/config?level=local');
    const nodes = res.config?.translation?.compute_nodes || {};
    window._activeNodeIds = Object.keys(nodes);

    let html = `
        <div class="infrastructure-hub" data-version="V74.35_STABLE" style="margin-top: 5px;">
            <div class="tactical-info-pod glass-panel" style="padding: 20px; margin-bottom: 25px; border-left: 4px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.02);">
                <div class="pod-label" style="font-size: 0.65rem; font-weight: 900; color: var(--accent-secondary); letter-spacing: 2px; margin-bottom: 8px;">全域算力单元 (COMPUTE UNITS)</div>
                <div class="pod-desc" style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.5;">
                    管理核心的算力供应资源，包括本地大模型、云端 API 等原子生产力单元。在此处定义的单元可被调度策略引用。
                </div>
            </div>
            <div class="node-grid">
                ${Object.entries(nodes)
            .sort((a, b) => {
                const aNode = a[1];
                const bNode = b[1];
                const aTime = aNode.last_updated || 0;
                const bTime = bNode.last_updated || 0;
                return bTime - aTime;
            })
            .map(([id, node]) => `
                    <div class="node-unit ${node.enabled !== false ? 'active' : 'inactive'}" id="node-unit-${id}" style="position: relative;">
                        ${node.is_primary ? '<div class="role-badge primary">PRIMARY</div>' : node.is_fallback ? '<div class="role-badge fallback">FALLBACK</div>' : ''}
                        
                        <div class="node-header">
                            <div class="node-identity">
                                <div class="node-icon-vessel">
                                    ${getNodeIcon(node.type)}
                                </div>
                                <div class="node-name-group">
                                <div class="node-name-vessel">
                                    <div class="node-name" title="${id}">${id}</div>
                                </div>
                                    <div class="node-meta-line">
                                        <div class="text-marquee-wrapper" style="max-width: 120px;">
                                            <span class="node-type" title="${node.provider_name || node.type?.toUpperCase()}">${node.provider_name || node.type?.toUpperCase()}</span>
                                        </div>
                                        <div class="protocol-badge ${node.protocol_family}">
                                            ${node.protocol_family === 'standard' ? 'V1' : node.protocol_family === 'anthropic' ? 'V2' : 'NATIVE'}
                                        </div>
                                    </div>
                                    <div class="node-model-line">
                                        <div class="model-marquee-vessel">
                                            <span class="node-model-badge">
                                                <span class="brain-icon">🧠</span>
                                                <span class="model-name">${node.model || '未绑定模型'}</span>
                                            </span>
                                        </div>
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
                                <div class="label">健康分</div>
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
                        </div>

                        <div class="node-meta-footer" style="display: flex; justify-content: space-between; font-size: 0.6rem; color: var(--text-dim); margin-bottom: 8px; opacity: 0.6; font-family: var(--font-mono);">
                            <span>最后同步: ${node.last_updated ? new Date(node.last_updated).toLocaleString() : '从未感应'}</span>
                        </div>
                        
                        <div class="node-status-line" id="probe-status-${id}">📡 物理链路待命，准备感应...</div>
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

    // 同步更新导航栏勋章文字
    const badgeSlot = document.getElementById('compute-strategy-badge-slot');
    if (badgeSlot) {
        badgeSlot.innerHTML = `<div class="strategy-mode-badge badge active" style="font-size: 0.65rem; padding: 4px 12px;">[${(trans.strategy || 'SINGLE').toUpperCase()} MODE]</div>`;
    }

    let html = `
        <div class="strategy-command-deck-wrap fade-in">
            <div class="tactical-info-pod glass-panel" style="padding: 20px; margin-bottom: 25px; border-left: 4px solid var(--accent-primary); background: rgba(163, 76, 255, 0.02);">
                <div class="pod-label" style="font-size: 0.65rem; font-weight: 900; color: var(--accent-primary); letter-spacing: 2px; margin-bottom: 8px;">算力分配策略 (ALLOCATION STRATEGY)</div>
                <div class="pod-desc" style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.5;">
                    配置系统如何分配出版任务。您可以指定主力与备用单元的联动逻辑，确保在任何环境下都能保持高可用输出。
                </div>
            </div>

            <div class="strategy-command-deck" style="margin-top: 0 !important;">

            <!-- 🧬 Logic Control Panel -->
            <div class="logic-pod glass-panel" style="padding: 25px; margin-bottom: 30px; border: 1px solid rgba(0, 242, 255, 0.1);">
                <div class="strategy-label">容灾调度算法 (RESILLIENCE ALGORITHM)</div>
                <div class="strategy-list">
                    ${renderStrategyItem('single', '📍 单点模式', '仅通过主力节点执行任务，追求绝对的路径控制。', trans.strategy)}
                    ${renderStrategyItem('fallback', '🛡️ 容灾模式', '主力节点故障时，能量自动导向备用节点，确保出版不中断。', trans.strategy)}
                    ${renderStrategyItem('concurrent', '🚀 竞速模式', '主备并联齐发，以毫秒级响应优先者为准，榨取极限性能。', trans.strategy)}
                </div>
            </div>

            <!-- ⚖️ The Binding Matrix: Visual Linkage -->
            <div class="strategy-binding-matrix">
                <!-- PRIMARY NODE -->
                <div class="binding-terminal primary">
                    <div class="terminal-label">PRIMARY NODE (主力执行)</div>
                    <div class="selection-vessel">
                        <select id="primary_node_selector" 
                                onchange="updateStrategy('primary_node', this.value); fetchNodeModels(this.value, 'primary_model')">
                            <option value="">选择算力单元</option>
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
                            <option value="">选择算力单元</option>
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


            <div class="action-deck">
                <button class="primary-btn glow-btn" onclick="saveComputeStrategy(event)" style="padding: 15px 40px; font-size: 1rem;">
                    固化当前算力配置
                </button>
            </div>
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
                addAudit(`📡 已自动锚定单元 [${value}] 的物理默认模型: ${defaultModel}`, "info");
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

        // 实时同步导航栏勋章
        window.syncStrategyBadge(value);

        addAudit(`⚖️ 算力调度模式已实时切换为: ${value.toUpperCase()}`, "info");
    }

    // 🚀 [V73.7] 视觉唤醒：提醒需要点击固化按钮
    const saveBtn = document.querySelector('.strategy-command-deck .primary-btn');
    if (saveBtn) {
        saveBtn.classList.add('pulse-alert');
        saveBtn.innerHTML = '🛡️ 捕获到新配置: 请固化';
    }
};

window.probeNode = async (id) => {
    const statusEl = document.getElementById(`probe-status-${id}`);
    const latencyEl = document.getElementById(`latency-${id}`);
    if (statusEl) statusEl.innerHTML = '<span class="pulsing">发射脉冲探测中...</span>';

    try {
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
                return true;
            } else {
                statusEl.innerHTML = `<span class="offline">❌ 感应丢失: ${res.error || '信号断裂'}</span>`;
                if (latencyEl) latencyEl.innerHTML = `<span class="offline">TIMEOUT</span>`;
                return false;
            }
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span class="offline">❌ 探测崩溃: ${e.message}</span>`;
        return false;
    }
};

// 🚀 [V74.20] 全域脉冲：并行感应所有算力节点健康度
window.probeAllNodes = async () => {
    const nodes = document.querySelectorAll('.node-unit:not(.hidden)');
    if (nodes.length === 0) return;

    addAudit(`📡 正在启动全域脉冲感应，目标: ${nodes.length} 个算力单元...`, "info");

    const promises = Array.from(nodes).map(node => {
        const id = node.id.replace('node-unit-', '');
        return probeNode(id);
    });

    await Promise.all(promises);
    addAudit(`✅ 全域脉冲探测任务执行完毕。`, "success");
};

// 🚀 [V74.20] 意志过滤：实时检索算力底座
window.filterNodes = (query) => {
    const lowerQuery = query.toLowerCase();
    const nodes = document.querySelectorAll('.node-unit');
    let visibleCount = 0;

    nodes.forEach(node => {
        const id = node.id.replace('node-unit-', '').toLowerCase();
        const type = (node.querySelector('.node-type')?.innerText || '').toLowerCase();
        const model = (node.querySelector('.model-name')?.innerText || '').toLowerCase();

        const isMatch = id.includes(lowerQuery) || type.includes(lowerQuery) || model.includes(lowerQuery);
        node.classList.toggle('hidden', !isMatch);
        if (isMatch) visibleCount++;
    });

    // 视觉反馈
    const grid = document.querySelector('.node-grid');
    if (visibleCount === 0) {
        if (!document.getElementById('no-nodes-hint')) {
            const hint = document.createElement('div');
            hint.id = 'no-nodes-hint';
            hint.style.cssText = 'grid-column: 1/-1; padding: 100px; text-align: center; color: var(--text-dim); font-style: italic;';
            hint.innerHTML = '🕳️ 未发现匹配的算力单元';
            grid.appendChild(hint);
        }
    } else {
        const hint = document.getElementById('no-nodes-hint');
        if (hint) hint.remove();
    }
};

window.saveComputeStrategy = async (event) => {
    // 逻辑保持不变，但增加视觉反馈
    const btn = event?.target || document.querySelector('.strategy-command-deck .primary-btn');
    if (!btn) return; // 🛡️ 安全防御

    const originalText = btn.innerText;
    btn.innerText = "正在固化配置...";

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
        showNotification('✅ 算力配置固化成功', 'success');
        btn.classList.remove('pulse-alert'); // 移除告警状态
        btn.innerHTML = originalText; // 恢复原始文字

        // 🚀 [V74.24] 固化成功后强制执行一次全域同步，确保所有 Tab 看到的都是最新的物理现实
        const freshRes = await apiFetch('/api/system/config');
        const freshConfig = freshRes.config || freshRes;
        if (freshConfig.translation) {
            window.settingsData.translation = freshConfig.translation;
            window.syncStrategyBadge();
        }
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
                const famA = a.protocol_family || 'native';
                const famB = b.protocol_family || 'native';
                if (famA !== famB) {
                    return famA === 'native' ? -1 : 1;
                }
                const nameA = a.name || a.id || "";
                const nameB = b.name || b.id || "";
                return nameA.localeCompare(nameB);
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

            // 🚀 [V74.9] 意志同步：如果是主/副算力，同步更新全局策略层的模型锚点
            const res = await apiFetch('/api/compute/nodes');
            if (id === res.primary) {
                payload[`translation.primary_model`] = formValues.model;
                addAudit(`🎯 检测到主算力变更，正在同步 [primary_model] 配置...`, "info");
            } else if (id === res.fallback) {
                payload[`translation.fallback_model`] = formValues.model;
                addAudit(`🎯 检测到备用算力变更，正在同步 [fallback_model] 配置...`, "info");
            }

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

    // 🚀 [V67.6] 强制 URL 注入：选择协议后立即应用其标准官方端点
    if (urlInput && defaultUrl) {
        urlInput.value = defaultUrl;
        addAudit(`📡 已根据协议 [${name}] 物理对正官方端点。`, "info");
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
    if (!activeBtn) return; // 🛡️ 安全防御

    const originalText = activeBtn.innerText;
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

    activeBtn.innerText = "正在感应...";
    activeBtn.disabled = true;
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
        activeBtn.innerText = originalText;
        activeBtn.disabled = false;
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
    addAudit(`🏗️ 正在准备算力单元初始化环境...`, "info");

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
            title: '🏗️ 新增算力单元',
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
