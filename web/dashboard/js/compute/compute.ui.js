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

        const isAiDisabled = trans.enable_ai === false;

        let html = `
            <div class="strategy-command-deck-wrap fade-in">
                ${isAiDisabled ? `
                <div class="tactical-info-pod glass-panel" style="padding: 20px; margin-bottom: 25px; border-left: 4px solid var(--neon-red, #ff4d4d); background: rgba(255, 77, 77, 0.05);">
                    <div class="pod-label" style="font-size: 0.65rem; font-weight: 900; color: var(--neon-red, #ff4d4d); letter-spacing: 2px; margin-bottom: 8px;">⚠️ 算力总控已关闭 (COMPUTE DISABLED)</div>
                    <div class="pod-desc" style="font-size: 0.85rem; color: var(--text-bright, #ffffff); line-height: 1.5;">
                        检测到 AI 算力总控处于关闭状态，右侧 Sovereign Copilot 及全域 AI 出版流已处于离线或纯本地物理降级模式。如需恢复大模型辅助，请在下方启用“AI 算力总控”并点击保存。
                    </div>
                </div>
                ` : `
                <div class="tactical-info-pod glass-panel" style="padding: 20px; margin-bottom: 25px; border-left: 4px solid var(--accent-primary); background: hsla(269, 100%, 65%, 0.02);">
                    <div class="pod-label" style="font-size: 0.65rem; font-weight: 900; color: var(--accent-primary); letter-spacing: 2px; margin-bottom: 8px;">算力分配策略 (ALLOCATION STRATEGY)</div>
                    <div class="pod-desc" style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.5;">
                        配置系统如何分配出版任务。您可以指定主力与备用单元的联动逻辑，确保在任何环境下都能保持高可用输出。
                    </div>
                </div>
                `}

                <div class="strategy-command-deck" style="margin-top: 0 !important;">
                    <div class="strategy-binding-matrix">
                        <div class="binding-terminal primary" id="primary-terminal-pod" style="transition: all 0.3s; ${(isAiDisabled || trans.strategy === 'global_smart') ? 'opacity: 0.3; pointer-events: none;' : ''}">
                            <div class="terminal-label">PRIMARY NODE (主力执行)</div>
                            <div class="selection-vessel">
                                <select id="primary_node_selector" 
                                        onchange="window.ComputeHandlers.updateStrategy('primary_node', this.value); window.ComputeHandlers.fetchNodeModels(this.value, 'primary_model')"
                                        ${(isAiDisabled || trans.strategy === 'global_smart') ? 'disabled' : ''}>
                                    <option value="">选择算力单元</option>
                                    ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.primary_node ? 'selected' : ''} data-model="${n.model || ''}">${nid}</option>`).join('')}
                                </select>
                                <div class="input-vessel">
                                    <input type="text" id="primary_model_input" value="${trans.primary_model || ''}" 
                                           placeholder="执行模型标识符" 
                                           onchange="window.ComputeHandlers.updateStrategy('primary_model', this.value)"
                                           ${(isAiDisabled || trans.strategy === 'global_smart') ? 'disabled' : ''}>
                                    <div id="primary_model_suggestions" class="discovery-suggestions"></div>
                                </div>
                            </div>
                        </div>

                        <div class="binding-vessel">
                            <div class="vessel-icon">⚡</div>
                            <div class="vessel-link-line"></div>
                        </div>

                        <div class="binding-terminal fallback" id="fallback-terminal-pod" style="transition: all 0.3s; ${(isAiDisabled || ['single', 'global_smart'].includes(trans.strategy)) ? 'opacity: 0.3; pointer-events: none;' : ''}">
                            <div class="terminal-label">FALLBACK NODE (容灾守护)</div>
                            <div class="selection-vessel">
                                <select id="fallback_node_selector"
                                        onchange="window.ComputeHandlers.updateStrategy('fallback_node', this.value); window.ComputeHandlers.fetchNodeModels(this.value, 'fallback_model')"
                                        ${(isAiDisabled || ['single', 'global_smart'].includes(trans.strategy)) ? 'disabled' : ''}>
                                    <option value="">选择算力单元</option>
                                    ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.fallback_node ? 'selected' : ''} data-model="${n.model || ''}">${nid}</option>`).join('')}
                                </select>
                                <div class="input-vessel">
                                    <input type="text" id="fallback_model_input" value="${trans.fallback_model || ''}" 
                                           placeholder="容灾模型标识符" 
                                           onchange="window.ComputeHandlers.updateStrategy('fallback_model', this.value)"
                                           ${(isAiDisabled || ['single', 'global_smart'].includes(trans.strategy)) ? 'disabled' : ''}>
                                    <div id="fallback_model_suggestions" class="discovery-suggestions"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="logic-pod glass-panel" style="padding: 25px; margin-bottom: 35px; border: 1px solid hsla(183, 100%, 50%, 0.1); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                        <div class="strategy-label">容灾调度算法 (RESILLIENCE ALGORITHM)</div>
                        <div class="strategy-list">
                            ${this.renderStrategyItem('single', '📍 单点模式 (Single)', '仅通过主力节点执行任务，追求绝对的路径控制。', trans.strategy)}
                            ${this.renderStrategyItem('fallback', '🛡️ 容灾模式 (Fallback)', '主力节点故障时，能量自动导向备用节点，确保出版不中断。', trans.strategy)}
                            ${this.renderStrategyItem('concurrent', '🚀 竞速模式 (Concurrent)', '主备并联齐发，以毫秒级响应优先者为准，榨取极限性能。', trans.strategy)}
                            ${this.renderStrategyItem('global_smart', '🧠 智能模式 (Global Smart)', '全域健康监控，自动将任何任务派发给当前最健康的算力节点。', trans.strategy)}
                        </div>
                    </div>

                    <!-- 🤖 区域 1: AI 算力推理与并发管控 -->
                    <div class="logic-pod glass-panel" style="padding: 22px; margin-bottom: 20px; border: 1px solid rgba(0, 242, 254, 0.15); border-radius: 12px;">
                        <div class="strategy-label" style="display: flex; align-items: center; gap: 8px; color: var(--neon-cyan, #00f2fe); font-size: 0.85rem; font-weight: 700;">
                            <span>🤖 AI 算力推理与并发管控 (AI EXECUTION & CONCURRENCY)</span>
                        </div>
                        <div class="settings-grid" style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border);">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">AI 算力总控 (Enable AI)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">控制全局是否允许调用大模型算力。</div>
                                </div>
                                <div style="flex: 1; max-width: 200px; display: flex; justify-content: flex-end;">
                                    <select id="input-enable-ai" class="setting-input"
                                           style="width: 100%; max-width: 180px;"
                                           onchange="window.ComputeHandlers.updateStrategy('enable_ai', this.value === 'true')">
                                        <option value="false" ${trans.enable_ai === false ? 'selected' : ''}>❌ 关闭 AI 算力</option>
                                        <option value="true" ${trans.enable_ai === true ? 'selected' : ''}>🟢 开启 AI 算力</option>
                                    </select>
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">全局思维链推理 (CoT)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">是否全局允许大语言模型输出内部深度思考过程。</div>
                                </div>
                                <div style="flex: 1; max-width: 200px; display: flex; justify-content: flex-end;">
                                    <select id="input-enable-thinking" class="setting-input"
                                           style="width: 100%; max-width: 180px;"
                                           onchange="window.ComputeHandlers.updateStrategy('enable_thinking', this.value === 'true')">
                                        <option value="false" ${trans.enable_thinking === false ? 'selected' : ''}>❌ 压制思维链</option>
                                        <option value="true" ${trans.enable_thinking === true ? 'selected' : ''}>🛡️ 启用思维链</option>
                                    </select>
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">🤖 AI 算力隔离池并发 (AI Workers)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">限制 AI 请求的最大全局并发进程数。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-ai-workers" class="setting-input setting-input-number" value="${window.settingsData?.system?.concurrency?.ai_workers ?? 2}" min="1" max="128" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateSystemConcurrency('ai_workers', parseInt(this.value))">
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">🌐 单文档多语种 AI 并发 (LLM Concurrency)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">单篇长文内向多目标语言分发时的最大瞬时并发。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-llm-concurrency" class="setting-input setting-input-number" value="${trans.llm_concurrency}" min="1" max="32" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateStrategy('llm_concurrency', parseInt(this.value))">
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">AI 并发排队超时 (秒)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">请求在算力信号量队列中等待获取令牌的最大超时秒数。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-ai-semaphore-timeout" class="setting-input setting-input-number" value="${trans.ai_semaphore_timeout ?? 3600}" min="1" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateStrategy('ai_semaphore_timeout', parseInt(this.value))">
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">API 响应超时 (秒)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">单次 HTTP 请求大模型服务的最大网络响应等待时间。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-api-timeout" class="setting-input setting-input-number" value="${trans.api_timeout}" min="10" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateStrategy('api_timeout', parseFloat(this.value))">
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">最大重试次数</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">遇到瞬时网络异常或限流时触发热接力重试的最大次数。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-max-retries" class="setting-input setting-input-number" value="${trans.max_retries}" min="0" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateStrategy('max_retries', parseInt(this.value))">
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border); ${isAiDisabled ? 'opacity: 0.3; pointer-events: none;' : ''}">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">分块长度 (Chars)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">单段落安全切片的最大字符阈值。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-max-chunk-size" class="setting-input setting-input-number" value="${trans.max_chunk_size}" step="100" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateStrategy('max_chunk_size', parseInt(this.value))">
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- ⚡ 区域 2: 系统管线与通用编译配置 -->
                    <div class="logic-pod glass-panel" style="padding: 22px; margin-bottom: 24px; border: 1px solid rgba(163, 76, 255, 0.15); border-radius: 12px;">
                        <div class="strategy-label" style="display: flex; align-items: center; gap: 8px; color: #a34cff; font-size: 0.85rem; font-weight: 700;">
                            <span>⚡ 系统管线与通用编译配置 (SYSTEM PIPELINE & GENERAL CONTROL)</span>
                        </div>
                        <div class="settings-grid" style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border);">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">⚡ 全局文档流水线并发 (Global Workers)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">全站出版流水线同时处理原稿文档的最大协程数。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-global-workers" class="setting-input setting-input-number" value="${window.settingsData?.system?.concurrency?.global_workers ?? 2}" min="1" max="64" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateSystemConcurrency('global_workers', parseInt(this.value))">
                                </div>
                            </div>
                            <div class="setting-item glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 10px; border: 1px solid var(--glass-border);">
                                <div style="flex: 2; min-width: 280px;">
                                    <div style="font-size: 0.85rem; font-weight: 600; color: var(--color-white);">📂 磁盘 I/O 编译并发 (I/O Workers)</div>
                                    <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">静态站点生成与多语言文件写入的最大并发线程数。</div>
                                </div>
                                <div style="flex: 1; max-width: 120px; display: flex; justify-content: flex-end;">
                                    <input type="number" id="input-io-workers" class="setting-input setting-input-number" value="${window.settingsData?.system?.concurrency?.io_workers ?? 4}" min="1" max="32" 
                                           style="max-width: 90px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;"
                                           onchange="window.ComputeHandlers.updateSystemConcurrency('io_workers', parseInt(this.value))">
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 💡 算力并发控制与全流程出版业务流对齐向导卡片（已下移至参数区下方） -->
                    <div class="logic-pod glass-panel" style="padding: 20px 24px; margin-bottom: 30px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.03); border-radius: 12px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                            <div style="font-size: 0.85rem; font-weight: 700; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 8px;">
                                <span>💡 算力并发控制与全流程出版业务流对齐向导</span>
                            </div>
                            <span style="font-size: 0.68rem; padding: 2px 8px; border-radius: 4px; background: rgba(0, 242, 254, 0.15); color: var(--neon-cyan); border: 1px solid rgba(0, 242, 254, 0.3);">流程图解与最佳实践</span>
                        </div>

                        <div style="font-size: 0.78rem; line-height: 1.6; color: var(--text-bright, #fff); opacity: 0.9;">
                            <p style="margin: 0 0 10px 0;">以同步 <b>10 篇文档</b> 并翻译为 <b>3 个目标语种</b> 的标准出版流程为例，4 维并发控制参数的物理协作机制如下：</p>
                            
                            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 12px 0 16px 0;">
                                <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px;">
                                    <div style="color: #a34cff; font-size: 0.72rem; font-weight: 700; margin-bottom: 4px;">1. ⚡ 全局文档流水线并发</div>
                                    <div style="font-size: 0.7rem; opacity: 0.8; line-height: 1.4;">控制同时开启加工的<b>原稿文档数</b>。<br><code>Global Workers=2</code> 表示同时并行加工 2 篇文档。</div>
                                </div>
                                <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px;">
                                    <div style="color: #00f2fe; font-size: 0.72rem; font-weight: 700; margin-bottom: 4px;">2. 🤖 AI 算力隔离池并发</div>
                                    <div style="font-size: 0.7rem; opacity: 0.8; line-height: 1.4;">控制允许提交给 AI 算力网关的<b>最高任务数</b>。<br><code>AI Workers=2</code> 限制全局同时向 AI 提问的线程数。</div>
                                </div>
                                <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px;">
                                    <div style="color: #00ff88; font-size: 0.72rem; font-weight: 700; margin-bottom: 4px;">3. 🌐 单文档多语种并发</div>
                                    <div style="font-size: 0.7rem; opacity: 0.8; line-height: 1.4;">控制单篇文档在翻译为多个语种时的<b>语种并行度</b>。<br><code>LLM Concurrency=1</code> 表示单文档多语种串行翻译。</div>
                                </div>
                                <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px;">
                                    <div style="color: #ffaa00; font-size: 0.72rem; font-weight: 700; margin-bottom: 4px;">4. 📂 磁盘 I/O 编译并发</div>
                                    <div style="font-size: 0.7rem; opacity: 0.8; line-height: 1.4;">控制最终静态 HTML / MD 产物的<b>物理落盘线程数</b>。<br><code>I/O Workers=4</code> 实现多文件高速磁盘写入。</div>
                                </div>
                            </div>

                            <div style="display: flex; gap: 12px; background: rgba(0,0,0,0.25); padding: 10px 14px; border-radius: 8px; font-size: 0.74rem;">
                                <div style="flex: 1;">
                                    <span style="color: #00ff88; font-weight: 700;">🏠 本地算力场景 (LM Studio / Ollama)</span>
                                    <div style="opacity: 0.8; margin-top: 2px;">建议均设为 <code>1</code>（或开启 <b>[SINGLE MODE]</b>），实现全链路纯串行，彻底杜绝本地显存溢出与 500 报错。</div>
                                </div>
                                <div style="width: 1px; background: rgba(255,255,255,0.1);"></div>
                                <div style="flex: 1;">
                                    <span style="color: #00f2fe; font-weight: 700;">☁️ 云端 API 场景 (OpenAI / DeepSeek)</span>
                                    <div style="opacity: 0.8; margin-top: 2px;">建议设为 <code>Global=4~8</code>, <code>AI=4~8</code>, <code>LLM=2~4</code>，发挥云端无限吞吐，几秒内极速收割全站静态编译。</div>
                                </div>
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

