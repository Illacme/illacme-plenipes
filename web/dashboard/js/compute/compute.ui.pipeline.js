/**
 * 🎨 Illacme Compute Center - Pipeline Concurrency & Guide Shard
 * 职责：AI 翻译与推理管线高级并发参数、系统通用编译并发参数及全流程出版对齐向导卡片渲染。
 */

(function () {
    'use strict';

    if (!window.ComputeUI) {
        window.ComputeUI = {};
    }

    /**
     * ⚡ 渲染算力并发参数与业务流对齐向导
     */
    window.ComputeUI.renderPipelineSettingsAndGuide = function (trans, isAiDisabled) {
        return `
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

    <!-- 💡 算力并发控制与全流程出版业务流对齐向导卡片 -->
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
        `;
    };

})();
