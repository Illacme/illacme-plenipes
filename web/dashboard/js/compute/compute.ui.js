/**
 * 🎨 Illacme Compute Center - UI Rendering Shard (V74.24 GENOME RESTORED)
 * 职责：物理算力资源管理、视觉对正、能量链路调度。
 * 还原声明：本文件内容 100% 提取自 83b7900 基准版本，严禁 AI 瞎创造。
 */

window.ComputeUI = {
    /**
     * 🧱 物理底座层：工业化动力单元渲染 (高内聚委派至原子渲染 Shard)
     */
    async renderInfrastructureTab(container) {
        if (typeof this.renderInfrastructureTabImpl === 'function') {
            return this.renderInfrastructureTabImpl(container);
        }
        console.warn("renderInfrastructureTabImpl is not loaded yet, fallback rendering triggered.");
    },

    /**
     * 🧱 获取节点类型对应的 Emoji 图标 (保留回退与兼容性)
     */
    getNodeIcon(type) {
        const map = {
            'openai': '🌐', 'ollama': '🦙', 'anthropic': '🎭', 'groq': '⚡',
            'deepseek': '🐳', 'google': '💎', 'siliconflow': '🌊', 'lmstudio': '🏠'
        };
        return map[type?.toLowerCase()] || '🤖';
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
                    <div class="strategy-binding-matrix">
                        <div class="binding-terminal primary">
                            <div class="terminal-label">PRIMARY NODE (主力执行)</div>
                            <div class="selection-vessel">
                                <select id="primary_node_selector" 
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

                        <div class="binding-terminal fallback" id="fallback-terminal-pod" style="transition: all 0.3s; ${trans.strategy === 'single' ? 'opacity: 0.3; pointer-events: none;' : ''}">
                            <div class="terminal-label">FALLBACK NODE (容灾守护)</div>
                            <div class="selection-vessel">
                                <select id="fallback_node_selector"
                                        onchange="window.ComputeHandlers.updateStrategy('fallback_node', this.value); window.ComputeHandlers.fetchNodeModels(this.value, 'fallback_model')"
                                        ${trans.strategy === 'single' ? 'disabled' : ''}>
                                    <option value="">选择算力单元</option>
                                    ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.fallback_node ? 'selected' : ''} data-model="${n.model || ''}">${nid}</option>`).join('')}
                                </select>
                                <div class="input-vessel">
                                    <input type="text" id="fallback_model_input" value="${trans.fallback_model || ''}" 
                                           placeholder="容灾模型标识符" 
                                           onchange="window.ComputeHandlers.updateStrategy('fallback_model', this.value)"
                                           ${trans.strategy === 'single' ? 'disabled' : ''}>
                                    <div id="fallback_model_suggestions" class="discovery-suggestions"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="logic-pod glass-panel" style="padding: 25px; margin-bottom: 30px; border: 1px solid rgba(0, 242, 255, 0.1);">
                        <div class="strategy-label">容灾调度算法 (RESILLIENCE ALGORITHM)</div>
                        <div class="strategy-list">
                            ${this.renderStrategyItem('single', '📍 单点模式', '仅通过主力节点执行任务，追求绝对的路径控制。', trans.strategy)}
                            ${this.renderStrategyItem('fallback', '🛡️ 容灾模式', '主力节点故障时，能量自动导向备用节点，确保出版不中断。', trans.strategy)}
                            ${this.renderStrategyItem('concurrent', '🚀 竞速模式', '主备并联齐发，以毫秒级响应优先者为准，榨取极限性能。', trans.strategy)}
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
    }
};

