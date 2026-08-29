/**
 * 🕹️ Illacme Compute Center - Event Handlers Shard (V74.24 DECOUPLED)
 * 职责：负责算力中心的核心事件路由、策略同步与桥接兼容。
 */

window.ComputeHandlers = window.ComputeHandlers || {};

/**
 * 🛰️ 策略勋章同步中枢
 */
window.ComputeHandlers.syncStrategyBadge = function(forcedValue = null) {
    const strategy = forcedValue || window.settingsData?.translation?.strategy || 'single';
    const badgeSlot = document.getElementById('compute-strategy-badge-slot');
    if (badgeSlot) {
        badgeSlot.innerHTML = `<div class="strategy-mode-badge badge active" style="font-size: 0.65rem; padding: 4px 12px;">[${strategy.toUpperCase()} MODE]</div>`;
    }
};

/**
 * 🕹️ 调度策略联动更新
 */
window.ComputeHandlers.updateStrategy = function(key, value) {
    if (!window.settingsData.translation) window.settingsData.translation = {};
    window.settingsData.translation[key] = value;

    // 🚀 [V73.6] 智能对正逻辑：切换节点时自动补全模型信息
    if (key.endsWith('_node')) {
        const type = key.split('_')[0]; 
        const selector = document.getElementById(`${key}_selector`);
        const selectedOption = selector.options[selector.selectedIndex];
        const defaultModel = selectedOption.getAttribute('data-model');

        if (defaultModel) {
            const input = document.getElementById(`${type}_model_input`);
            if (input) {
                input.value = defaultModel;
                window.settingsData.translation[`${type}_model`] = defaultModel;
                if (typeof addAudit === 'function') addAudit(`📡 已自动锚定单元 [${value}] 的物理默认模型: ${defaultModel}`, "info");
            }
        }
    }

    if (key === 'strategy') {
        document.querySelectorAll('.strategy-item').forEach(el => el.classList.remove('active'));
        const items = document.querySelectorAll('.strategy-item');
        items.forEach(item => {
            if (item.getAttribute('onclick').includes(`'${value}'`)) {
                item.classList.add('active');
            }
        });
        this.syncStrategyBadge(value);
        if (typeof addAudit === 'function') addAudit(`⚖️ 算力调度模式已实时切换为: ${value.toUpperCase()}`, "info");

        // 🛡️ 实时联动：处理单点、容灾与智能模式的主备节点显示状态
        const primaryPod = document.getElementById('primary-terminal-pod');
        const primarySelect = document.getElementById('primary_node_selector');
        const primaryInput = document.getElementById('primary_model_input');
        const fallbackPod = document.getElementById('fallback-terminal-pod');
        const fallbackSelect = document.getElementById('fallback_node_selector');
        const fallbackInput = document.getElementById('fallback_model_input');

        if (value === 'global_smart') {
            if (primaryPod) primaryPod.style = "transition: all 0.3s; opacity: 0.3; pointer-events: none;";
            if (primarySelect) primarySelect.disabled = true;
            if (primaryInput) primaryInput.disabled = true;
            
            if (fallbackPod) fallbackPod.style = "transition: all 0.3s; opacity: 0.3; pointer-events: none;";
            if (fallbackSelect) fallbackSelect.disabled = true;
            if (fallbackInput) fallbackInput.disabled = true;
        } else if (value === 'single') {
            if (primaryPod) primaryPod.style = "transition: all 0.3s; opacity: 1; pointer-events: auto;";
            if (primarySelect) primarySelect.disabled = false;
            if (primaryInput) primaryInput.disabled = false;

            if (fallbackPod) fallbackPod.style = "transition: all 0.3s; opacity: 0.3; pointer-events: none;";
            if (fallbackSelect) fallbackSelect.disabled = true;
            if (fallbackInput) fallbackInput.disabled = true;
        } else {
            // fallback, concurrent 等模式
            if (primaryPod) primaryPod.style = "transition: all 0.3s; opacity: 1; pointer-events: auto;";
            if (primarySelect) primarySelect.disabled = false;
            if (primaryInput) primaryInput.disabled = false;

            if (fallbackPod) fallbackPod.style = "transition: all 0.3s; opacity: 1; pointer-events: auto;";
            if (fallbackSelect) fallbackSelect.disabled = false;
            if (fallbackInput) fallbackInput.disabled = false;
        }
    }

    const saveBtn = document.getElementById('btn-save-compute-strategy');
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.classList.add('pulse-alert');
        saveBtn.innerHTML = '🛡️ 配置已变更，请保存';
    }
};

/**
 * 🕹️ 系统级并发矩阵联动更新
 */
window.ComputeHandlers.updateSystemConcurrency = function(key, value) {
    if (!window.settingsData.system) window.settingsData.system = {};
    if (!window.settingsData.system.concurrency) window.settingsData.system.concurrency = {};
    window.settingsData.system.concurrency[key] = value;

    const saveBtn = document.getElementById('btn-save-compute-strategy');
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.classList.add('pulse-alert');
        saveBtn.innerHTML = '🛡️ 配置已变更，请保存';
    }
};

/**
 * 🔍 算力单元实时过滤
 */
let _filterTimer = null;
window.ComputeHandlers.filterNodes = function(query) {
    if (_filterTimer) clearTimeout(_filterTimer);
    _filterTimer = setTimeout(() => {
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

        const grid = document.querySelector('.node-grid');
        const hintId = 'no-nodes-hint';
        if (visibleCount === 0) {
            if (!document.getElementById(hintId)) {
                const hint = document.createElement('div');
                hint.id = hintId;
                hint.style.cssText = 'grid-column: 1/-1; padding: 100px; text-align: center; color: var(--text-dim); font-style: italic;';
                hint.innerHTML = '🕳️ 未发现匹配的算力单元';
                grid.appendChild(hint);
            }
        } else {
            const hint = document.getElementById(hintId);
            if (hint) hint.remove();
        }
    }, 150);
};

/**
 * 🕹️ 视图切换调度 (职责归位)
 */
window.ComputeHandlers.switchComputeTab = async function(tab) {
    window.currentActiveComputeTab = tab;
    try {
        localStorage.setItem('illacme_plenipes_current_compute_tab', tab);
    } catch (e) {}
    const container = document.getElementById('compute-tab-viewport');
    if (!container) return;

    // 切换 Tab 激活状态
    document.querySelectorAll('.tactical-tabs .t-tab').forEach(btn => {
        const isTarget = btn.getAttribute('onclick').includes(`'${tab}'`);
        btn.classList.toggle('active', isTarget);
    });

    // 动态调整顶部工具栏
    const topActions = document.getElementById('compute-header-actions-top');
    const navActions = document.getElementById('compute-nav-actions-slot');
    if (topActions) {
        const saveBtn = document.getElementById('btn-save-compute-strategy');
        const addNodeBtn = document.getElementById('btn-add-node');
        const probeNodesBtn = document.getElementById('btn-probe-nodes');
        const refreshBtn = document.getElementById('btn-refresh-compute');
        const resetBtn = document.getElementById('id-btn-reset-compute-strategy');

        if (tab === 'infrastructure') {
            topActions.style.display = 'flex';
            if (navActions) navActions.style.display = 'flex';
            if (saveBtn) saveBtn.style.display = 'none';
            if (resetBtn) resetBtn.style.display = 'none';
            if (addNodeBtn) addNodeBtn.style.display = 'flex';
            if (probeNodesBtn) probeNodesBtn.style.display = 'flex';
            if (refreshBtn) refreshBtn.style.display = 'flex';
        } else {
            topActions.style.display = 'none';
            if (navActions) navActions.style.display = 'flex';
            if (saveBtn) saveBtn.style.display = 'flex';
            if (resetBtn) resetBtn.style.display = 'flex';
            if (addNodeBtn) addNodeBtn.style.display = 'none';
            if (probeNodesBtn) probeNodesBtn.style.display = 'none';
            if (refreshBtn) refreshBtn.style.display = 'none';
        }
    }

    // 注入加载动画与卡片骨架屏 (V74.36)
    if (tab === 'infrastructure') {
        container.innerHTML = `
            <div class="loading-scanner">
                <div class="scan-line"></div>
                <p>正在扫描 算力资源...</p>
            </div>
            <div class="node-grid" style="margin-top: 20px;">
                ${Array(3).fill(0).map(() => `
                    <div class="node-unit active" style="opacity: 0.7;">
                        <div class="node-header">
                            <div class="node-identity" style="width: 100%;">
                                <div class="node-icon-vessel skeleton" style="width: 32px; height: 32px; border-radius: 50%;"></div>
                                <div class="node-name-group" style="flex: 1; display: flex; flex-direction: column; gap: 6px; margin-left: 8px;">
                                    <div class="skeleton" style="width: 120px; height: 16px;"></div>
                                    <div class="skeleton" style="width: 60px; height: 12px;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="node-telemetry" style="margin-top: 15px;">
                            <div class="t-item"><div class="skeleton" style="width: 40px; height: 12px; margin-bottom: 4px;"></div><div class="skeleton" style="width: 30px; height: 16px;"></div></div>
                            <div class="t-item"><div class="skeleton" style="width: 40px; height: 12px; margin-bottom: 4px;"></div><div class="skeleton" style="width: 30px; height: 16px;"></div></div>
                            <div class="t-item"><div class="skeleton" style="width: 40px; height: 12px; margin-bottom: 4px;"></div><div class="skeleton" style="width: 30px; height: 16px;"></div></div>
                            <div class="t-item"><div class="skeleton" style="width: 40px; height: 12px; margin-bottom: 4px;"></div><div class="skeleton" style="width: 30px; height: 16px;"></div></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="loading-scanner">
                <div class="scan-line"></div>
                <p>正在扫描 全域配置...</p>
            </div>
        `;
    }

    if (tab === 'infrastructure') {
        await window.ComputeUI.renderInfrastructureTab(container);
    } else {
        await window.ComputeUI.renderStrategyTab(container);
    }
};

/**
 * 🎨 全局通知助手
 */
window.ComputeHandlers.showNotification = function(text, type = 'success') {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });
    Toast.fire({ icon: type, title: text });
};

/**
 * 🛰️ 桥接器：保持 HTML inline 事件绑定 100% 兼容
 */
window.probeNode = (id) => window.ComputeHandlers.probeNode(id);
window.editNode = (id) => window.ComputeHandlers.editNode(id);
window.switchComputeTab = (tab) => window.ComputeHandlers.switchComputeTab(tab);
window.showAddNodeModal = (proto) => window.ComputeHandlers.showAddNodeModal(proto);
window.probeAllNodes = () => window.ComputeHandlers.probeAllNodes();
window.filterNodes = (q) => window.ComputeHandlers.filterNodes(q);
window.saveComputeStrategy = (e) => window.ComputeHandlers.saveComputeStrategy(e);
