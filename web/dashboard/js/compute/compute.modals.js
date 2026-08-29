/**
 * 🕹️ Illacme Compute Center - Modal Interaction Shard (V74.24 DECOUPLED)
 * 职责：承载算力单元的新增、编辑、校验及下拉选择模态框逻辑。
 * 🚀 物理对正：隶属于 window.ComputeHandlers 命名空间。
 */

(function() {
    const Modals = {
        /**
         * ➕ 弹出新增算力单元模态框 (像素级还原)
         */
        async showAddNodeModal(preselectedProtocol = null) {
            try {
                const pluginRes = await apiFetch('/api/plugins/list');
                const protocols = (pluginRes.plugins || [])
                    .filter(p => p.category === 'protocol')
                    .sort((a, b) => (a.name || '').localeCompare(b.name || ''));

                const preselected = protocols.find(p => p.id === preselectedProtocol);
                const initialType = preselected ? preselected.id : '';
                const initialName = preselected ? preselected.name : '请选择算力渠道...';
                const initialUrl = preselected ? (preselected.default_url || '') : '';
                const initialId = preselected ? `${preselected.id}-node` : '';

                const { value: formValues } = await Swal.fire({
                    title: '➕ 新增算力单元',
                    html: `
                        <div class="swal-edit-grid sovereign-form">
                            <label>节点标识 (Unique ID)</label>
                            <input id="swal-input-id" class="swal2-input" value="${initialId}" placeholder="e.g. deepseek-node">
                            <div id="error-id" class="field-error-hint"></div>

                            <label>算力渠道 (Channel)</label>
                            <div class="sovereign-select-vessel">
                                <input type="hidden" id="swal-input-type" value="${initialType}">
                                <div class="sovereign-input-field custom-select-trigger" id="provider-trigger-add"
                                     onclick="window.ComputeHandlers.toggleSovereignDropdown(event, 'provider-menu-add', 'provider-search-input-add')">
                                    ${initialName}
                                </div>
                                <div class="custom-dropdown-menu" id="provider-menu-add">
                                    <div class="dropdown-search-vessel" onclick="event.stopPropagation()">
                                        <input type="text" class="dropdown-search-input" id="provider-search-input-add" 
                                               oninput="window.ComputeHandlers.filterProtocols(this.value, 'provider-list-items-add')"
                                               placeholder="🔍 搜索算力渠道名称..." autocomplete="off">
                                    </div>
                                    <div id="provider-list-items-add">
                                        ${protocols.map(p => `
                                            <div class="dropdown-item ${p.id === initialType ? 'selected' : ''}" 
                                                 data-name="${p.name.toLowerCase()}"
                                                 onclick="window.ComputeHandlers.selectProvider('${p.id}', '${p.name.replace(/'/g, "\\'")}', '${p.default_url || ''}')">
                                                <span>${p.name}</span>
                                                <span class="badge">${(p.protocol_family || 'standard').toUpperCase()}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            <div id="error-type" class="field-error-hint"></div>
                            
                            <label>端点地址 (Endpoint)</label>
                            <input id="swal-input-url" class="swal2-input" value="${initialUrl}" placeholder="e.g. https://api.openai.com/v1">
                            
                            <label>物理密钥 (API Key)</label>
                            <input id="swal-input-key" class="swal2-input" type="password" placeholder="sk-...">

                            <label>独立代理 (Proxy)</label>
                            <input id="swal-input-proxy" class="swal2-input" placeholder="e.g. http://127.0.0.1:10809 或 direct (可选)">

                            <div style="grid-column: span 2; margin-top: 5px;">
                                <label>默认推荐 / 基准探针模型 (Default & Probe Model)</label>
                                <div class="sovereign-select-vessel" style="margin-top: 8px;">
                                    <div style="display: flex; gap: 0;">
                                        <input id="swal-input-model" class="swal2-input" style="margin:0; flex:1; border-top-right-radius:0; border-bottom-right-radius:0;" placeholder="输入探针基准模型 (调度策略将默认选用)">
                                        <button type="button" class="mini-btn glow-btn" style="border-top-left-radius:0; border-bottom-left-radius:0;" 
                                                onclick="window.ComputeHandlers.discoverModels(event, 'new_node_temp'); return false;">📡 感应</button>
                                    </div>
                                    <div id="asset-discovery-menu" class="custom-dropdown-menu asset-dropdown"></div>
                                </div>
                                <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 5px; line-height: 1.4;">
                                    💡 此模型既用于硬件连通性与网络时延探针，也是调度策略装配时的默认选用模型；在各品牌的「调度策略」中可随时切换为其他模型。
                                </div>
                            </div>
                        </div>
                    `,
                    width: '600px',
                    confirmButtonText: '💾 保存算力单元',
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
                    background: 'hsla(220, 43%, 7%, 0.98)',
                    backdrop: `var(--black-40) blur(10px)`,
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
                        // 每次提交前先静默清空表单报错
                        document.querySelectorAll('.field-error-hint').forEach(el => {
                            el.innerText = '';
                            el.style.display = 'none';
                        });

                        const nid = document.getElementById('swal-input-id').value;
                        const type = document.getElementById('swal-input-type').value;

                        if (!nid) {
                            window.ComputeHandlers.showFieldError('id', '不能为空');
                            return false;
                        }
                        if (!type) {
                            window.ComputeHandlers.showFieldError('type', '请选择算力渠道');
                            return false;
                        }

                        return {
                            id: nid,
                            base_url: document.getElementById('swal-input-url').value,
                            api_key: document.getElementById('swal-input-key').value,
                            proxy: document.getElementById('swal-input-proxy')?.value || '',
                            type: type,
                            model: document.getElementById('swal-input-model').value
                        }
                    }
                });

                if (formValues) {
                    if (typeof addAudit === 'function') addAudit(`🚀 正在新增算力单元 [${formValues.id}]...`, "info");
                    const payload = {};
                    const prefix = `translation.compute_nodes.${formValues.id}`;
                    payload[`${prefix}.base_url`] = formValues.base_url;
                    payload[`${prefix}.api_key`] = formValues.api_key;
                    payload[`${prefix}.proxy`] = formValues.proxy;
                    payload[`${prefix}.type`] = formValues.type;
                    payload[`${prefix}.model`] = formValues.model;
                    payload[`${prefix}.last_updated`] = Date.now();
                    payload[`${prefix}.enabled`] = true;

                    const updateRes = await apiFetch('/api/config/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (updateRes?.status === 'success') {
                        if (typeof addAudit === 'function') addAudit(`✅ 算力单元 [${formValues.id}] 已保存。`, "success");
                        if (typeof window.loadComputeCenter === 'function') window.loadComputeCenter();
                    }
                }
            } catch (e) {
                console.error(e);
            }
        },

        /**
         * ⚙️ 弹出编辑算力单元模态框
         */
        async editNode(id) {
            try {
                const res = await apiFetch('/api/system/config?level=local');
                const nodes = res.config?.translation?.compute_nodes || {};
                const node = nodes[id] || {};

                const pluginRes = await apiFetch('/api/plugins/list');
                const protocols = (pluginRes.plugins || [])
                    .filter(p => p.category === 'protocol')
                    .sort((a, b) => (a.name || '').localeCompare(b.name || ''));

                const activeProtocol = protocols.find(p => p.id === node.type) || { name: '请选择算力渠道...' };

                const { value: formValues } = await Swal.fire({
                    title: `⚙️ 编辑算力单元: ${id}`,
                    html: `
                        <div class="swal-edit-grid sovereign-form">
                            <label>算力渠道 (Channel)</label>
                            <div class="sovereign-select-vessel">
                                <input type="hidden" id="swal-input-type" value="${node.type || ''}">
                                <div class="sovereign-input-field custom-select-trigger" id="provider-trigger-edit"
                                     onclick="window.ComputeHandlers.toggleSovereignDropdown(event, 'provider-menu-edit', 'provider-search-input-edit')">
                                    ${activeProtocol.name}
                                </div>
                                <div class="custom-dropdown-menu" id="provider-menu-edit">
                                    <div class="dropdown-search-vessel" onclick="event.stopPropagation()">
                                        <input type="text" class="dropdown-search-input" id="provider-search-input-edit" 
                                               oninput="window.ComputeHandlers.filterProtocols(this.value, 'provider-list-items-edit')"
                                               placeholder="🔍 搜索算力渠道名称..." autocomplete="off">
                                    </div>
                                    <div id="provider-list-items-edit">
                                        ${protocols.map(p => `
                                            <div class="dropdown-item ${p.id === node.type ? 'selected' : ''}" 
                                                 onclick="window.ComputeHandlers.selectProvider('${p.id}', '${p.name.replace(/'/g, "\\'")}', '${p.default_url || ''}')">
                                                <span>${p.name}</span>
                                                <span class="badge">${(p.protocol_family || 'standard').toUpperCase()}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            <div id="error-type" class="field-error-hint"></div>
                            
                            <label>端点地址 (Endpoint)</label>
                            <input id="swal-input-url" class="swal2-input" value="${node.base_url || ''}">
                            
                            <label>物理密钥 (API Key)</label>
                            <input id="swal-input-key" class="swal2-input" type="password" value="${node.api_key || ''}">

                            <label>独立代理 (Proxy)</label>
                            <input id="swal-input-proxy" class="swal2-input" value="${node.proxy || ''}" placeholder="e.g. http://127.0.0.1:10809 或 direct (可选)">

                            <div style="grid-column: span 2; margin-top: 5px;">
                                <label>默认推荐 / 基准探针模型 (Default & Probe Model)</label>
                                <div class="sovereign-select-vessel" style="margin-top: 8px;">
                                    <div style="display: flex; gap: 0;">
                                        <input id="swal-input-model" class="swal2-input" style="margin:0; flex:1; border-top-right-radius:0; border-bottom-right-radius:0;" 
                                               value="${node.model || ''}" placeholder="输入探针基准模型 (调度策略将默认选用)">
                                        <button type="button" class="mini-btn glow-btn" style="border-top-left-radius:0; border-bottom-left-radius:0;" 
                                                onclick="window.ComputeHandlers.discoverModels(event, '${id}'); return false;">📡 感应</button>
                                    </div>
                                    <div id="asset-discovery-menu" class="custom-dropdown-menu asset-dropdown"></div>
                                </div>
                                <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 5px; line-height: 1.4;">
                                    💡 此模型既用于硬件连通性与网络时延探针，也是调度策略装配时的默认选用模型；在各品牌的「调度策略」中可随时切换为其他模型。
                                </div>
                            </div>
                        </div>
                    `,
                    width: '600px',
                    confirmButtonText: '💾 保存算力单元',
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
                    preConfirm: () => {
                        // 每次提交前先静默清空表单报错
                        document.querySelectorAll('.field-error-hint').forEach(el => {
                            el.innerText = '';
                            el.style.display = 'none';
                        });

                        const type = document.getElementById('swal-input-type').value;
                        if (!type) {
                            window.ComputeHandlers.showFieldError('type', '请选择算力渠道');
                            return false;
                        }

                        return {
                            base_url: document.getElementById('swal-input-url').value,
                            api_key: document.getElementById('swal-input-key').value,
                            proxy: document.getElementById('swal-input-proxy')?.value || '',
                            type: type,
                            model: document.getElementById('swal-input-model').value
                        }
                    }
                });

                if (formValues) {
                    const payload = {};
                    payload[`translation.compute_nodes.${id}.base_url`] = formValues.base_url;
                    payload[`translation.compute_nodes.${id}.api_key`] = formValues.api_key;
                    payload[`translation.compute_nodes.${id}.proxy`] = formValues.proxy;
                    payload[`translation.compute_nodes.${id}.type`] = formValues.type;
                    payload[`translation.compute_nodes.${id}.model`] = formValues.model;
                    payload[`translation.compute_nodes.${id}.last_updated`] = Date.now();

                    await apiFetch('/api/config/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (typeof window.loadComputeCenter === 'function') window.loadComputeCenter();
                }
            } catch (e) {
                console.error(e);
            }
        },
    };

    // 🚀 [V74.24] 物理挂载至全局总线
    Object.assign(window.ComputeHandlers, Modals);
})();
