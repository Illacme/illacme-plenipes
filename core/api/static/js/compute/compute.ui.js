/**
 * 🎨 Illacme Compute Center - UI Rendering Shard (V74.24 GENOME RESTORED)
 * 职责：物理算力资源管理、视觉对正、能量链路调度。
 * 还原声明：本文件内容 100% 提取自 83b7900 基准版本，严禁 AI 瞎创造。
 */

window.ComputeUI = {
    /**
     * 🧱 物理底座层：工业化动力单元渲染
     */
    async renderInfrastructureTab(container) {
        // 🚀 [V74.24] 强化感应：始终在切换 Tab 时尝试从服务器拉取最新配置
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
        if (typeof window.ComputeHandlers.syncStrategyBadge === 'function') {
            window.ComputeHandlers.syncStrategyBadge();
        }

        // 🛡️ [V74.10] 直接从已同步的配置中读取节点数据（避免重复声明 res）
        const nodes = window.settingsData?.translation?.compute_nodes || {};
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
                .sort((a, b) => (b[1].last_updated || 0) - (a[1].last_updated || 0))
                .map(([id, node]) => `
                        <div class="node-unit ${node.enabled !== false ? 'active' : 'inactive'}" id="node-unit-${id}" style="position: relative;">
                            ${node.is_primary ? '<div class="role-badge primary">PRIMARY</div>' : node.is_fallback ? '<div class="role-badge fallback">FALLBACK</div>' : ''}
                            
                            <div class="node-header">
                                <div class="node-identity">
                                    <div class="node-icon-vessel">
                                        ${this.getNodeIcon(node.type)}
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
                                    <button class="tactical-btn" onclick="window.ComputeHandlers.probeNode('${id}')" title="全域脉冲探测">📡</button>
                                    <button class="tactical-btn" onclick="window.ComputeHandlers.editNode('${id}')" title="单元参数修正">⚙️</button>
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
    },

    /**
     * ⚖️ 调度策略层：战术指挥矩阵渲染
     */
    async renderStrategyTab(container, forceData = null) {
        let trans = forceData;
        
        if (!trans) {
            const res = await apiFetch('/api/system/config');
            const config = res.config || res;
            trans = config.translation || {};
        }

        window.settingsData = window.settingsData || {};
        window.settingsData.translation = trans;
        const nodes = trans.compute_nodes || {};

        if (typeof window.ComputeHandlers.syncStrategyBadge === 'function') {
            window.ComputeHandlers.syncStrategyBadge(trans.strategy);
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
                    <div class="logic-pod glass-panel" style="padding: 25px; margin-bottom: 30px; border: 1px solid rgba(0, 242, 255, 0.1);">
                        <div class="strategy-label">容灾调度算法 (RESILLIENCE ALGORITHM)</div>
                        <div class="strategy-list">
                            ${this.renderStrategyItem('single', '📍 单点模式', '仅通过主力节点执行任务，追求绝对的路径控制。', trans.strategy)}
                            ${this.renderStrategyItem('fallback', '🛡️ 容灾模式', '主力节点故障时，能量自动导向备用节点，确保出版不中断。', trans.strategy)}
                            ${this.renderStrategyItem('concurrent', '🚀 竞速模式', '主备并联齐发，以毫秒级响应优先者为准，榨取极限性能。', trans.strategy)}
                        </div>
                    </div>

                    <div class="strategy-binding-matrix">
                        <div class="binding-terminal primary">
                            <div class="terminal-label">PRIMARY NODE (主力执行)</div>
                            <div class="selection-vessel">
                                <select id="select-compute-strategy-primary-node" 
                                        onchange="window.ComputeHandlers.updateStrategy('primary_node', this.value); window.ComputeHandlers.fetchNodeModels(this.value, 'primary_model')">
                                    <option value="">选择算力单元</option>
                                    ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.primary_node ? 'selected' : ''} data-model="${n.model || ''}">${nid}</option>`).join('')}
                                </select>
                                <div class="input-vessel">
                                    <input type="text" id="primary_model_input" value="${trans.primary_model || ''}" 
                                           placeholder="执行模型标识符" 
                                           onchange="window.ComputeHandlers.updateStrategy('primary_model', this.value)">
                                    <div id="primary_model_suggestions" class="discovery-suggestions"></div>
                                </div>
                            </div>
                        </div>

                        <div class="binding-vessel">
                            <div class="vessel-icon">⚡</div>
                            <div class="vessel-link-line"></div>
                        </div>

                        <div class="binding-terminal fallback">
                            <div class="terminal-label">FALLBACK NODE (容灾守护)</div>
                            <div class="selection-vessel">
                                <select id="fallback_node_selector"
                                        onchange="window.ComputeHandlers.updateStrategy('fallback_node', this.value); window.ComputeHandlers.fetchNodeModels(this.value, 'fallback_model')">
                                    <option value="">选择算力单元</option>
                                    ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.fallback_node ? 'selected' : ''} data-model="${n.model || ''}">${nid}</option>`).join('')}
                                </select>
                                <div class="input-vessel">
                                    <input type="text" id="fallback_model_input" value="${trans.fallback_model || ''}" 
                                           placeholder="容灾模型标识符" 
                                           onchange="window.ComputeHandlers.updateStrategy('fallback_model', this.value)">
                                    <div id="fallback_model_suggestions" class="discovery-suggestions"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="logic-pod glass-panel" style="padding: 25px; margin-bottom: 30px; border: 1px solid rgba(163, 76, 255, 0.1);">
                        <div class="strategy-label">物理执行参数 (PHYSICAL EXECUTION CONTROL)</div>
                        <div class="settings-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                            <div class="setting-item">
                                <label style="font-size: 0.7rem; color: var(--accent-secondary); text-transform: uppercase; letter-spacing: 1px;">AI 全域并发数</label>
                                <input type="number" id="input-llm-concurrency" value="${trans.llm_concurrency}" min="1" max="32" 
                                       style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px; color: #fff; margin-top: 5px;"
                                       onchange="window.ComputeHandlers.updateStrategy('llm_concurrency', parseInt(this.value))">
                            </div>
                            <div class="setting-item">
                                <label style="font-size: 0.7rem; color: var(--accent-secondary); text-transform: uppercase; letter-spacing: 1px;">API 响应超时 (秒)</label>
                                <input type="number" id="input-api-timeout" value="${trans.api_timeout}" min="10" 
                                       style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px; color: #fff; margin-top: 5px;"
                                       onchange="window.ComputeHandlers.updateStrategy('api_timeout', parseFloat(this.value))">
                            </div>
                            <div class="setting-item">
                                <label style="font-size: 0.7rem; color: var(--accent-secondary); text-transform: uppercase; letter-spacing: 1px;">最大重试次数</label>
                                <input type="number" id="input-max-retries" value="${trans.max_retries}" min="0" 
                                       style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px; color: #fff; margin-top: 5px;"
                                       onchange="window.ComputeHandlers.updateStrategy('max_retries', parseInt(this.value))">
                            </div>
                            <div class="setting-item">
                                <label style="font-size: 0.7rem; color: var(--accent-secondary); text-transform: uppercase; letter-spacing: 1px;">分块长度 (Chars)</label>
                                <input type="number" id="input-max-chunk-size" value="${trans.max_chunk_size}" step="100" 
                                       style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px; color: #fff; margin-top: 5px;"
                                       onchange="window.ComputeHandlers.updateStrategy('max_chunk_size', parseInt(this.value))">
                            </div>
                        </div>
                    </div>


                    </div>
            </div>
        `;
        container.innerHTML = html;
    },

    renderStrategyItem(id, name, desc, current) {
        const isActive = (id === (current || 'single'));
        return `
            <div class="strategy-item ${isActive ? 'active' : ''}" 
                 id="strategy-item-${id}"
                 onclick="window.ComputeHandlers.updateStrategy('strategy', '${id}')">
                <div class="radio-indicator"><div class="radio-inner"></div></div>
                <div class="strategy-info">
                    <div class="strategy-name">${name}</div>
                    <div class="strategy-desc">${desc}</div>
                </div>
            </div>
        `;
    },

    getNodeIcon(type) {
        const map = {
            'openai': '🌐', 'ollama': '🦙', 'anthropic': '🎭', 'groq': '⚡',
            'deepseek': '🐳', 'google': '💎', 'siliconflow': '🌊', 'lmstudio': '🏠'
        };
        return map[type?.toLowerCase()] || '🤖';
    }
};
