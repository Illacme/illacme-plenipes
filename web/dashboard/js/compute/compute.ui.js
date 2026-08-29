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
        const activeImprintId = window.settingsData?._active_imprint || 'default';
        const imprintsList = window.settingsData?._imprints || [];
        const activeImprintObj = imprintsList.find(im => im.id === activeImprintId);
        const activeImprintDisplayName = activeImprintObj?.name ? `${activeImprintObj.name} (${activeImprintId})` : activeImprintId;

        let html = `
            <div class="strategy-command-deck-wrap fade-in">
                ${isAiDisabled ? `
                <div class="tactical-info-pod" style="padding: 12px 16px; margin-bottom: 18px; border-radius: 8px; border: 1px solid rgba(255, 77, 77, 0.3); background: rgba(255, 77, 77, 0.04); display: flex; align-items: center; justify-content: space-between;">
                    <div style="font-size: 0.8rem; color: #ff6b6b; font-weight: 600;">⚠️ 算力总控已关闭：全域 AI 出版流处于离线状态，大模型推理已暂停。</div>
                </div>
                ` : `
                <!-- 💡 顶部轻量说明栏：与下方配置卡片彻底拉开层级差距 -->
                <div class="strategy-top-memo" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; margin-bottom: 16px; background: rgba(255, 255, 255, 0.015); border: 1px dashed var(--glass-border); border-radius: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 0.9rem;">🧠</span>
                        <span style="font-size: 0.78rem; color: var(--text-dim);">为当前出版品牌配置生成、翻译与润色时的主力与备用算力单元</span>
                    </div>
                    <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2); padding: 3px 10px; border-radius: 6px;">
                        <span style="font-size: 0.68rem; color: var(--text-dim);">生效品牌:</span>
                        <span style="font-size: 0.74rem; font-weight: 700; color: var(--accent-secondary);">🏷️ ${activeImprintDisplayName}</span>
                    </div>
                </div>
                `}

                <div class="strategy-command-deck" style="margin-top: 0 !important; padding: 24px; border-radius: 20px;">
                    <!-- ⚡ 主备算力工作台：双栏对立 + 流向通道 -->
                    <div class="strategy-binding-matrix" style="margin-top: 0; margin-bottom: 25px; gap: 20px;">
                        <!-- 主力计算节点 -->
                        <div class="binding-terminal primary" id="primary-terminal-pod" style="transition: all 0.3s; ${(isAiDisabled || trans.strategy === 'global_smart') ? 'opacity: 0.3; pointer-events: none;' : ''}">
                            <div class="terminal-header-row">
                                <div class="terminal-badge primary-badge">
                                    <span>⚡ 主力计算节点</span>
                                    <span class="pulse-dot"></span>
                                </div>
                                <span class="terminal-subtag">PRIMARY EXECUTION</span>
                            </div>

                            <div class="terminal-field-group">
                                <label class="field-label">1. 选择主力底座算力 (Compute Provider)</label>
                                <select id="primary_node_selector" class="terminal-select"
                                        onchange="window.ComputeHandlers.updateStrategy('primary_node', this.value); window.ComputeHandlers.fetchNodeModels(this.value, 'primary_model')"
                                        ${(isAiDisabled || trans.strategy === 'global_smart') ? 'disabled' : ''}>
                                    <option value="">-- 请选择主力算力单元 --</option>
                                    ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.primary_node ? 'selected' : ''} data-model="${n.model || ''}">${nid} (${n.provider || 'custom'})</option>`).join('')}
                                </select>
                            </div>

                            <div class="terminal-field-group">
                                <label class="field-label">2. 执行大模型名称 (Model Identifier)</label>
                                <div class="input-vessel" style="position: relative;">
                                    <input type="text" id="primary_model_input" class="terminal-input"
                                           value="${trans.primary_model || ''}" 
                                           placeholder="👈 选择算力单元后自动探测，或直接输入模型名..." 
                                           onchange="window.ComputeHandlers.updateStrategy('primary_model', this.value)"
                                           ${(isAiDisabled || trans.strategy === 'global_smart') ? 'disabled' : ''}>
                                    <div id="primary_model_suggestions" class="discovery-suggestions"></div>
                                </div>
                            </div>
                        </div>

                        <!-- 中间流向连接通道 -->
                        <div class="binding-vessel" style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;">
                            <div class="vessel-icon-circle" title="主力节点故障时，能量自动秒级流向容灾节点">
                                <span class="vessel-pulse-icon">⚡</span>
                            </div>
                            <span class="vessel-flow-text">FAILOVER</span>
                        </div>

                        <!-- 容灾备用节点 -->
                        <div class="binding-terminal fallback" id="fallback-terminal-pod" style="transition: all 0.3s; ${(isAiDisabled || ['single', 'global_smart'].includes(trans.strategy)) ? 'opacity: 0.35; filter: grayscale(0.6); pointer-events: none;' : ''}">
                            <div class="terminal-header-row">
                                <div class="terminal-badge fallback-badge">
                                    <span>🛡️ 容灾备用节点</span>
                                    <span class="standby-tag">STANDBY</span>
                                </div>
                                <span class="terminal-subtag">FALLBACK RESILIENCE</span>
                            </div>

                            <div class="terminal-field-group">
                                <label class="field-label">1. 选择容灾底座算力 (Fallback Provider)</label>
                                <select id="fallback_node_selector" class="terminal-select"
                                        onchange="window.ComputeHandlers.updateStrategy('fallback_node', this.value); window.ComputeHandlers.fetchNodeModels(this.value, 'fallback_model')"
                                        ${(isAiDisabled || ['single', 'global_smart'].includes(trans.strategy)) ? 'disabled' : ''}>
                                    <option value="">-- 请选择容灾备用单元 --</option>
                                    ${Object.entries(nodes).map(([nid, n]) => `<option value="${nid}" ${nid === trans.fallback_node ? 'selected' : ''} data-model="${n.model || ''}">${nid} (${n.provider || 'custom'})</option>`).join('')}
                                </select>
                            </div>

                            <div class="terminal-field-group">
                                <label class="field-label">2. 容灾大模型名称 (Fallback Model)</label>
                                <div class="input-vessel" style="position: relative;">
                                    <input type="text" id="fallback_model_input" class="terminal-input"
                                           value="${trans.fallback_model || ''}" 
                                           placeholder="👈 选择容灾单元后自动探测，或直接输入模型名..." 
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
                    <div class="concurrency-guide-deck">
                        <div class="guide-header">
                            <div class="guide-title">
                                <span>💡 算力并发控制与全流程出版业务流对齐向导</span>
                            </div>
                            <span class="guide-badge">流程图解与最佳实践</span>
                        </div>

                        <div class="guide-content">
                            <p class="guide-intro">以同步 <b>10 篇文档</b> 并翻译为 <b>3 个目标语种</b> 的标准出版流程为例，4 维并发控制参数的物理协作机制如下：</p>
                            
                            <div class="guide-grid-4">
                                <div class="guide-step-card step-1">
                                    <div class="step-title">1. ⚡ 全局文档流水线并发</div>
                                    <div class="step-desc">控制同时开启加工的<b>原稿文档数</b>。<br><code>Global Workers=2</code> 表示同时并行加工 2 篇文档。</div>
                                </div>
                                <div class="guide-step-card step-2">
                                    <div class="step-title">2. 🤖 AI 算力隔离池并发</div>
                                    <div class="step-desc">控制允许提交给 AI 算力网关的<b>最高任务数</b>。<br><code>AI Workers=2</code> 限制全局同时向 AI 提问的线程数。</div>
                                </div>
                                <div class="guide-step-card step-3">
                                    <div class="step-title">3. 🌐 单文档多语种并发</div>
                                    <div class="step-desc">控制单篇文档在翻译为多个语种时的<b>语种并行度</b>。<br><code>LLM Concurrency=1</code> 表示单文档多语种串行翻译。</div>
                                </div>
                                <div class="guide-step-card step-4">
                                    <div class="step-title">4. 📂 磁盘 I/O 编译并发</div>
                                    <div class="step-desc">控制最终静态 HTML / MD 产物的<b>物理落盘线程数</b>。<br><code>I/O Workers=4</code> 实现多文件高速磁盘写入。</div>
                                </div>
                            </div>

                            <div class="guide-scene-box">
                                <div class="scene-col">
                                    <span class="scene-title local">🏠 本地算力场景 (LM Studio / Ollama)</span>
                                    <div class="scene-desc">建议均设为 <code>1</code>（或开启 <b>[SINGLE MODE]</b>），实现全链路纯串行，彻底杜绝本地显存溢出与 500 报错。</div>
                                </div>
                                <div class="scene-divider"></div>
                                <div class="scene-col">
                                    <span class="scene-title cloud">☁️ 云端 API 场景 (OpenAI / DeepSeek)</span>
                                    <div class="scene-desc">建议设为 <code>Global=4~8</code>, <code>AI=4~8</code>, <code>LLM=2~4</code>，发挥云端无限吞吐，几秒内极速收割全站静态编译。</div>
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

