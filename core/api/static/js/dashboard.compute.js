/**
 * 🧠 [V55.0] Illacme Plenipes Compute Sovereignty Module
 * 职责：算力调度矩阵渲染、模型发现、连通性探测。
 */

// 1. 获取节点的模型列表 (包装器)
window.getModelsForNode = (nodeId, providers) => {
    const node = providers[nodeId] || {};
    
    // 🚀 [V53.8] 优雅化包装错误
    if (window.discoveryErrors[nodeId]) {
        const currentModel = node.model || 'gpt-4o-mini';
        const err = window.discoveryErrors[nodeId];
        const shortErr = err.length > 25 ? err.substring(0, 25) + '...' : err;
        return [{ 
            value: currentModel, 
            text: `${currentModel} (❌ ${shortErr})`,
            title: `物理故障详情: ${err}`
        }];
    }

    // 🚀 [V53.4] 模型资产视图
    if (Object.prototype.hasOwnProperty.call(window.discoveredModels, nodeId)) {
        const cached = window.discoveredModels[nodeId];
        if (cached && cached.length > 0) {
            return cached.map(m => ({ value: m, text: m }));
        }
    }

    // 回退方案
    return [{ value: node.model || 'gpt-4o-mini', text: node.model || 'gpt-4o-mini' }];
};

// 2. 执行算力探针
window.testNodeAvailability = async (nodeId, btn = null) => {
    const originalText = btn ? btn.innerText : '';
    if (btn) {
        btn.innerText = '⚡ 探测中...';
        btn.disabled = true;
    }
    
    addAudit(`⚡ 正在探测算力节点 [${nodeId}] 的物理连通性...`);
    
    try {
        const res = await apiFetch('/api/compute/nodes/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                id: nodeId,
                config: window.settingsData?.translation // 发送实时配置
            })
        });

        if (res && res.status === 'success') {
            addAudit(`✅ 节点 [${nodeId}] 探测成功: ${res.message || '响应正常'} (延迟: ${res.latency}ms)`, "success");
            if (btn) {
                btn.innerText = `✅ ${res.latency}ms`;
                btn.style.borderColor = 'var(--primary)';
            }

            // 探测成功后自动同步发现模型列表
            if (window.fetchNodeModels) {
                fetchNodeModels(nodeId, true, window.settingsData?.translation?.providers);
            }
        } else {
            const error = res ? res.error : "Unknown Error";
            addAudit(`🛑 节点 [${nodeId}] 探测失败: ${error}`, "error");
            if (btn) {
                btn.innerText = '❌ 失败';
                btn.style.borderColor = '#ff4d4d';
            }
        }
    } catch (e) {
        addAudit(`🚨 探测任务崩溃: ${e.message}`, "error");
    } finally {
        if (btn) {
            setTimeout(() => {
                btn.innerText = originalText;
                btn.disabled = false;
                btn.style.borderColor = '';
            }, 3000);
        }
    }
};

// 3. 执行模型发现
window.fetchNodeModels = async (nodeId, silent = false, providers) => {
    const node = providers ? (providers[nodeId] || {}) : (window.settingsData?.translation?.providers?.[nodeId] || {});
    if (!node.api_key && !(node.type || '').includes('local') && !(node.type || '').includes('ollama')) {
        if (!silent) addAudit(`⚠️ 节点 [${nodeId}] 缺少密钥，无法发起发现任务。`, "warning");
        window.discoveredModels[nodeId] = window.discoveredModels[nodeId] || [];
        return [];
    }
    
    const res = await apiFetch(`/api/compute/models?node_id=${nodeId}&provider=${node.type || ''}&api_key=${node.api_key || ''}&base_url=${encodeURIComponent(node.base_url || '')}`);
    
    if (res && res.models && res.models.length > 0) {
        window.discoveredModels[nodeId] = res.models;
        delete window.discoveryErrors[nodeId];
        if (!silent) {
            addAudit(`✅ 节点 [${nodeId}] 模型发现成功: [${res.models.slice(0,3).join(', ')}...]`, "success");
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('compute_strategy'); 
        }
        return res.models;
    } else {
        const errMsg = res ? (res.error || "接口返回空列表") : "网络请求异常";
        window.discoveryErrors[nodeId] = errMsg;
        window.discoveredModels[nodeId] = [];
        if (!silent) {
            addAudit(`❌ 节点 [${nodeId}] 模型发现失败: ${errMsg}`, "error");
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('compute_strategy');
        }
    }
    return [];
};

// 4. 算力底座全景渲染器 (Settings Tab)
window.renderComputeStrategy = (settingsData) => {
    const translation = settingsData.translation || {};
    const providers = translation.providers || {};
    const providerKeys = Object.keys(providers);

    return `
        <div class="full-width">
            <div class="section-header" style="margin-bottom: 0.5rem; margin-top: 1rem;"><h3>🧠 算力底座 (AI Compute Strategy)</h3></div>
            <p style="color: var(--text-dim); font-size: 0.85rem; margin-bottom: 1.5rem;">定义全局算力调度 logic，支持主力与备用节点的物理对正。</p>
            
            <div class="settings-grid">
                <div class="settings-group">
                    <h4>⚖️ 调度逻辑 (Dispatch Logic)</h4>
                    ${renderSettingsItem('节点调度策略', 'translation.strategy', translation.strategy || 'single', 'select', {
                        items: [
                            {value: 'single', text: 'Single (单点直连) - 仅使用主力节点'},
                            {value: 'fallback', text: 'Fallback (主备容灾) - 自动切至备用'},
                            {value: 'concurrent', text: 'Concurrent (并发竞速) - 取最快响应'}
                        ]
                    })}
                </div>

                <div class="settings-group">
                    <h4>🛰️ 核心节点绑定 (Core Node Binding)</h4>
                    <div class="settings-grid" style="grid-template-columns: 1fr 1fr; gap: 15px;">
                        ${renderSettingsItem('主力节点', 'translation.primary_node', translation.primary_node || 'default', 'select', {
                            items: providerKeys.filter(k => providers[k]?.enabled !== false).map(k => ({ value: k, text: k }))
                        })}
                        ${renderSettingsItem('主力模型', `translation.providers.${translation.primary_node || 'default'}.model`, providers[translation.primary_node || 'default']?.model || '', 'select', {
                            items: getModelsForNode(translation.primary_node || 'default', providers)
                        })}
                        ${renderSettingsItem('备用节点', 'translation.fallback_node', translation.fallback_node || '', 'select', {
                            items: [{value: '', text: '无 (None)'}, ...providerKeys.filter(k => providers[k]?.enabled !== false).map(k => ({ value: k, text: k }))]
                        })}
                        ${translation.fallback_node ? renderSettingsItem('备用模型', `translation.providers.${translation.fallback_node}.model`, providers[translation.fallback_node]?.model || '', 'select', {
                            items: getModelsForNode(translation.fallback_node, providers)
                        }) : `<div class="setting-row"><label>备用模型 (未启用)</label><select disabled><option>N/A</option></select></div>`}
                    </div>
                </div>
            </div>
            
            <div class="section-header" style="margin-top: 2.5rem; margin-bottom: 1rem;"><h3>🛡️ 环境感应 (Sovereign Node Awareness)</h3></div>
            
            <div class="settings-grid">
                ${providerKeys
                    .filter(p => providers[p]?.enabled !== false) 
                    .map(p => {
                    const node = providers[p] || {};
                    const isConfigured = !!node.api_key || (node.type || '').includes('local') || (node.type || '').includes('ollama');
                    return `
                        <div class="settings-group">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <div style="display:flex; align-items:center; gap:12px;">
                                    <span class="status-dot-mini ${isConfigured ? 'healthy' : 'blocked'}" id="status-${p}"></span>
                                    <h4 style="margin:0; border:none; padding:0; font-size:1.1rem; color:#fff;">${p.toUpperCase()}</h4>
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <button class="action-btn mini-btn" type="button" onclick="fetchNodeModels('${p}', false)">🔍 发现</button>
                                    <button class="action-btn mini-btn" type="button" onclick="testNodeAvailability('${p}', this)">⚡ 探测</button>
                                </div>
                            </div>
                            
                            <div class="settings-grid" style="grid-template-columns: 1fr 1.2fr; gap:15px;">
                                ${renderSettingsItem('接入密钥', `translation.providers.${p}.api_key`, node.api_key || '', 'password', { placeholder: 'Key/Token' })}
                                <div class="setting-row">
                                    <div class="setting-info">
                                        <div class="setting-label">感应模型</div>
                                    </div>
                                    <div class="setting-control">
                                        <select class="setting-input" style="width:100%;">
                                            ${getModelsForNode(p, providers).map(m => `<option value="${m.value}" title="${m.title || m.text}">${m.text}</option>`).join('')}
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
};

// 5. 算力视图加载器 (Compute View Tab)
window.loadComputeNodes = async () => {
    const grid = document.getElementById('compute-grid');
    if (!grid) return;
    grid.innerHTML = '<div class="loading">正在同步全球算力矩阵...</div>';

    const data = await apiFetch('/api/compute/nodes');
    if (!data || !data.nodes) return;

    grid.innerHTML = data.nodes.map(node => `
        <div class="shield-pod node-pod ${node.is_primary ? 'primary-active' : ''}">
            <div class="shield-status">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span class="status-dot-mini healthy"></span>
                    <span class="shield-id">${(node.provider || 'AI').toUpperCase()} NODE</span>
                </div>
                ${node.is_primary ? '<span class="log-tag info">PRIMARY</span>' : ''}
            </div>
            <div class="shield-body">
                <h4 style="font-size:1.1rem; color:#fff;">${node.id.toUpperCase()}</h4>
                <div style="font-family:var(--font-mono); font-size:0.7rem; color:var(--accent-secondary); margin-bottom:15px; opacity:0.8;">
                    ${node.model || 'AUTO-SELECT'} @ ${node.base_url || 'DEFAULT'}
                </div>
                
                <div class="pod-telemetry" style="display:flex; gap:15px; margin-bottom:20px;">
                    <div class="telemetry-item">
                        <div class="tiny-label">LATENCY</div>
                        <div class="mono" style="color:#00ff88;">--ms</div>
                    </div>
                    <div class="telemetry-item">
                        <div class="tiny-label">LOAD</div>
                        <div class="mono">STABLE</div>
                    </div>
                </div>

                <div class="p-control-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                    <button class="action-btn" onclick="testNodeAvailability('${node.id}', this)">⚡ PROBE</button>
                    ${!node.is_primary ? `<button class="action-btn" onclick="switchPrimaryNode('${node.id}')">🔄 SWITCH</button>` : ''}
                    <button class="action-btn" onclick="editComputeNode('${node.id}')">⚙️ CONFIG</button>
                    ${!node.is_primary ? `<button class="action-btn danger" onclick="deleteComputeNode('${node.id}')">🗑️ REMOVE</button>` : ''}
                </div>
            </div>
        </div>
    `).join('');
};

window.switchPrimaryNode = async (id) => {
    if (!confirm(`确认要将主算力切换至 [${id}] 吗？\n系统将自动热重载翻译管线。`)) return;

    addAudit(`🔄 正在请求算力重心迁移: ${id}...`);
    const res = await apiFetch('/api/compute/primary/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_id: id })
    });

    if (res && res.success) {
        addAudit(`✅ [主权迁移完成] 算力重心已对正至 ${id}`, "success");
        loadComputeNodes();
        const ctxAi = document.getElementById('ctx-ai');
        if (ctxAi) ctxAi.innerText = id;
    } else {
        addAudit("❌ 切换失败，请检查后端链路。", "error");
    }
};

window.editComputeNode = async (id) => {
    addAudit(`⚙️ 正在提取节点 [${id}] 的物理配置...`);
    const config = await apiFetch('/api/system/config');
    if (!config || !config.translation.providers[id]) return;

    const nodeData = config.translation.providers[id];
    const modal = document.getElementById('editor-modal');
    const body = document.getElementById('editor-body');
    const title = document.getElementById('editor-title');
    const saveBtn = document.getElementById('btn-save-doc');
    const configTabs = document.getElementById('config-tabs');

    title.innerText = `⚙️ 配置算力节点: ${id}`;
    body.value = JSON.stringify(nodeData, null, 4);
    modal.style.display = 'flex';
    if (configTabs) configTabs.style.display = 'none';

    saveBtn.onclick = async () => {
        try {
            const updated = JSON.parse(body.value);
            updated.id = id;
            const res = await apiFetch('/api/compute/nodes/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updated)
            });
            if (res && res.success) {
                addAudit(`✅ 节点 [${id}] 配置已持久化。`, "success");
                modal.style.display = 'none';
                loadComputeNodes();
            }
        } catch (e) {
            alert("JSON 格式错误: " + e.message);
        }
    };
};

window.deleteComputeNode = async (id) => {
    if (!confirm(`🚨 危险操作！\n确认要物理移除算力节点 [${id}] 吗？`)) return;

    addAudit(`🪓 正在移除算力节点: ${id}...`);
    const res = await apiFetch('/api/compute/nodes/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });

    if (res && res.success) {
        addAudit(`✅ 节点 [${id}] 已从矩阵中抹除。`, "warning");
        loadComputeNodes();
    } else {
        addAudit(`❌ 移除失败: ${res ? res.error : '物理链路异常'}`, "error");
    }
};
