/**
 * 🎨 Illacme Compute Center - UI Rendering Shard
 * 职责：负责算力中心的视觉渲染、DOM 构造与状态勋章对齐。
 */

window.ComputeUI = {
    /**
     * 🏗️ 渲染基础架构 Tab
     */
    renderInfrastructureTab(nodes, primaryId, fallbackId) {
        const container = document.getElementById('compute-grid');
        if (!container) return;

        window._activeNodeIds = Object.keys(nodes);
        
        container.innerHTML = Object.entries(nodes).map(([id, node]) => {
            const isPrimary = (id === primaryId);
            const isFallback = (id === fallbackId);
            const typeLabel = (node.type || 'Unknown').toUpperCase();
            
            return `
                <div class="compute-card p-4 border rounded shadow-sm mb-3" data-node-id="${id}" data-endpoint="${node.base_url}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="mb-1">${id} <small class="text-muted">[${typeLabel}]</small></h5>
                            <code class="small text-truncate d-block" style="max-width: 200px;">${node.base_url}</code>
                        </div>
                        <div class="badge-group">
                            ${isPrimary ? '<span class="badge bg-primary">PRIMARY</span>' : ''}
                            ${isFallback ? '<span class="badge bg-secondary">FALLBACK</span>' : ''}
                        </div>
                    </div>
                    <div class="mt-3 d-flex align-items-center justify-content-between">
                        <div id="probe-status-${id}" class="small text-muted">
                            <span class="dot pulse"></span> 等待探测
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="window.ComputeHandlers.editNode('${id}')">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <div class="dropdown">
                                <button class="btn btn-outline-info dropdown-toggle" type="button" 
                                        data-bs-toggle="dropdown" onclick="window.ComputeAPI.discoverModels('${id}', '${node.base_url}', '${node.type}')">
                                    <i class="bi bi-broadcast"></i> 感应
                                </button>
                                <ul class="dropdown-menu shadow" id="asset-discovery-menu">
                                    <li><a class="dropdown-item disabled">正在感应...</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    /**
     * 🎖️ 同步策略勋章
     */
    syncStrategyBadge() {
        const badge = document.getElementById('active-strategy-badge');
        if (!badge) return;

        const strategy = document.getElementById('compute-strategy-select')?.value || 'primary';
        const primary = document.getElementById('primary-node-select')?.value || 'None';
        
        badge.innerHTML = `<i class="bi bi-shield-check me-1"></i> ${strategy.toUpperCase()}: ${primary}`;
        
        // 🚀 [V74.81] 视觉反馈：给保存按钮增加抖动提醒
        const saveBtn = document.getElementById('save-strategy-btn');
        if (saveBtn) saveBtn.classList.add('pulse-alert');
    },

    /**
     * 📥 搜索框动态注入 (L74.83)
     */
    injectSearchHeader() {
        const header = document.getElementById('compute-header-actions-top');
        if (!header) return;

        header.innerHTML = `
            <div class="input-group input-group-sm" style="width: 250px;">
                <span class="input-group-text bg-transparent border-end-0">
                    <i class="bi bi-search text-muted"></i>
                </span>
                <input type="text" id="compute-search" class="form-control border-start-0" 
                       placeholder="搜索算力单元..." oninput="window.ComputeHandlers.filterNodes(this.value)">
            </div>
        `;
    },

    /**
     * 弹出新增/编辑节点模态框 (Swal)
     */
    async showNodeModal(nodeId = null) {
        const isEdit = !!nodeId;
        const config = window.settingsData?.translation?.compute_nodes || {};
        const node = isEdit ? config[nodeId] : { type: 'openai', base_url: '', api_key: '', model: '' };

        // 获取支持的协议列表
        const res = await apiFetch('/api/plugins/list');
        const protocols = res.plugins.filter(p => p.category === 'protocol');

        const { value: formValues } = await Swal.fire({
            title: isEdit ? '🔧 修正算力参数' : '➕ 划定新算力单元',
            html: `
                <div class="text-start">
                    <label class="small text-muted mb-1">节点标识 (ID)</label>
                    <input id="swal-input-id" class="swal2-input mt-0" placeholder="e.g. cloudflare-ai" value="${nodeId || ''}" ${isEdit ? 'disabled' : ''}>
                    
                    <label class="small text-muted mb-1 mt-3">通信协议</label>
                    <select id="swal-input-type" class="swal2-select w-100 m-0" onchange="window.ComputeHandlers.selectProvider(this.value)">
                        ${protocols.map(p => `<option value="${p.id}" ${p.id === node.type ? 'selected' : ''}>${p.name}</option>`).join('')}
                    </select>

                    <label class="small text-muted mb-1 mt-3">Endpoint (URL)</label>
                    <input id="swal-input-url" class="swal2-input mt-0" placeholder="https://api..." value="${node.base_url}">
                    
                    <label class="small text-muted mb-1 mt-3">API Key</label>
                    <input id="swal-input-key" type="password" class="swal2-input mt-0" placeholder="密钥已脱敏" value="${node.api_key}">
                </div>
            `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: '执行固化',
            preConfirm: () => {
                return {
                    id: document.getElementById('swal-input-id').value,
                    type: document.getElementById('swal-input-type').value,
                    base_url: document.getElementById('swal-input-url').value,
                    api_key: document.getElementById('swal-input-key').value
                }
            }
        });

        if (formValues) {
            window.ComputeHandlers.saveNode(formValues);
        }
    }
};
