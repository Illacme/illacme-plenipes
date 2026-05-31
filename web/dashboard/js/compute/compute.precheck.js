/**
 * 🏢 Illacme Compute Center - Sovereign Startup Precheck Shard (V77.14)
 * 职责：负责系统启动时全量自检主备算力通道连通性与模型可用性，
 * 并对异常情况提供极致友好的人性化诊断报告与一键式直达配置操作引导。
 * 🛡️ [Sovereign Edge Check]：在探测异常时强制隐藏 AI 欢迎与推荐提示模块，禁用输入，只显式保留诊断交互卡片。
 */

(function() {
    if (window._dbgLog) window._dbgLog('📦 compute.precheck.js initializing');

    window.ComputePrecheck = {
        /**
         * 🚀 启动全量可用性扫描探针
         * @param {Function} onSuccess 检测完全通过后的回调
         */
        async run(onSuccess) {
            try {
                // 🚀 [AEL-Iter-v77.14] 自检启动时标为 CHECKING 状态
                const agentStatus = document.getElementById('agent-status-tag');
                if (agentStatus) {
                    agentStatus.textContent = 'CHECKING';
                    agentStatus.style.color = 'var(--neon-amber, #ffb300)';
                    agentStatus.style.borderColor = 'rgba(255, 179, 0, 0.4)';
                    agentStatus.style.textShadow = '0 0 6px rgba(255, 179, 0, 0.4)';
                }

                // 1. 获取主备节点元数据
                const nodesRes = await apiFetch('/api/compute/nodes');
                const primaryId = nodesRes.primary;
                const fallbackId = nodesRes.fallback;
                
                if (!primaryId) {
                    this.renderDiagnosticCard('none', fallbackId, '系统配置中未指定任何主算力节点！', 'no_primary');
                    return;
                }

                // 2. 发起主算力探针连通性测试
                const testRes = await apiFetch('/api/compute/nodes/test', {
                    method: 'POST',
                    body: JSON.stringify({ id: primaryId })
                });

                if (testRes.status === 'success') {
                    // 3. 主算力连通，进一步检查是否能成功感应到活跃模型列表
                    const modelsRes = await apiFetch(`/api/compute/models?node_id=${primaryId}`);
                    if (modelsRes.models && modelsRes.models.length > 0) {
                        // 主备双轨完全健康，静默恢复/清扫 UI 状态并就绪
                        this.restoreNormalUI();
                        console.log("✅ [Sovereign Precheck] Primary compute node & models verified online.");
                        if (typeof onSuccess === 'function') onSuccess();
                    } else {
                        // 连通但未装载任何可用模型
                        const err = modelsRes.error || "未在节点中感应到任何活跃模型资产。";
                        this.renderDiagnosticCard(primaryId, fallbackId, err, "models_empty");
                    }
                } else {
                    // 主算力故障，尝试嗅探备用节点进行接管
                    let fallbackWorking = false;
                    if (fallbackId) {
                        const fallbackTest = await apiFetch('/api/compute/nodes/test', {
                            method: 'POST',
                            body: JSON.stringify({ id: fallbackId })
                        });
                        if (fallbackTest.status === 'success') fallbackWorking = true;
                    }
                    
                    const err = testRes.error || "本地算力服务未响应或网络连接被拒绝 (Connection Refused)";
                    this.renderDiagnosticCard(primaryId, fallbackId, err, fallbackWorking ? "fallback_active" : "offline");
                }
            } catch (err) {
                console.warn("⚠️ [Sovereign Precheck] Precheck executed with errors:", err);
            }
        },

        /**
         * ⚙️ 探测通过时还原正常的 AI 指令交互界面与提示模块
         */
        restoreNormalUI() {
            const welcomeEl = document.getElementById('agent-default-welcome');
            const agentInput = document.getElementById('agent-command-input');
            const diagCard = document.getElementById('agent-compute-diagnostic-card');
            const agentStatus = document.getElementById('agent-status-tag');
            
            if (welcomeEl) welcomeEl.style.display = 'flex';
            if (diagCard) diagCard.remove();
            
            if (agentInput) {
                agentInput.disabled = false;
                agentInput.placeholder = '输入指令，如“系统状态” (Cmd+K)...';
                agentInput.style.opacity = '1';
                agentInput.style.pointerEvents = 'auto';
            }

            if (agentStatus) {
                agentStatus.textContent = 'STANDBY';
                agentStatus.style.color = '';
                agentStatus.style.borderColor = '';
                agentStatus.style.textShadow = '';
            }
        },

        /**
         * 🆕 渲染极富玻璃美学质感的诊断报告与操作引导卡片 (SOP-03 Compliant)
         */
        renderDiagnosticCard(primaryId, fallbackId, rawError, type) {
            const agentFeed = document.getElementById('agent-feed');
            const welcomeEl = document.getElementById('agent-default-welcome');
            const agentInput = document.getElementById('agent-command-input');
            if (!agentFeed) return;
            
            // 🛡️ [算力离线安全防护] 移除已存在的任何诊断残留
            const oldCard = document.getElementById('agent-compute-diagnostic-card');
            if (oldCard) oldCard.remove();
            
            // 🚀 若并非轻量级的备用代偿状态，而是真正的连通挂起 (Both Failed / Empty)
            // 则强制隐藏 AI 提示欢迎大模块，只显示诊断卡片
            const isFallbackActive = type === "fallback_active";
            if (welcomeEl) {
                welcomeEl.style.display = isFallbackActive ? 'flex' : 'none';
            }
            
            // 联动更新右侧边栏顶部的大副状态标签，呈现极高发光的真实物理状态
            const agentStatus = document.getElementById('agent-status-tag');
            if (agentStatus) {
                if (isFallbackActive) {
                    agentStatus.textContent = 'FALLBACK';
                    agentStatus.style.color = '#00f2ff';
                    agentStatus.style.borderColor = 'rgba(0, 242, 255, 0.4)';
                    agentStatus.style.textShadow = '0 0 6px rgba(0, 242, 255, 0.4)';
                } else {
                    agentStatus.textContent = 'OFFLINE';
                    agentStatus.style.color = '#ff8080';
                    agentStatus.style.borderColor = 'rgba(239, 83, 80, 0.4)';
                    agentStatus.style.textShadow = '0 0 6px rgba(239, 83, 80, 0.4)';
                }
            }
            
            // 挂起指令输入功能，防止误报和盲目指令调用
            if (agentInput) {
                if (isFallbackActive) {
                    agentInput.disabled = false;
                    agentInput.placeholder = '输入指令，如“系统状态” (Cmd+K)...';
                    agentInput.style.opacity = '1';
                    agentInput.style.pointerEvents = 'auto';
                } else {
                    agentInput.disabled = true;
                    agentInput.placeholder = '❌ 算力中心已挂起，指令功能暂时关闭...';
                    agentInput.style.opacity = '0.45';
                    agentInput.style.pointerEvents = 'none';
                }
            }
            
            let errorMsg = rawError;
            let guideSteps = "";
            let borderGlow = "rgba(239, 83, 80, 0.45) !important";
            let cardBg = "linear-gradient(135deg, rgba(30, 0, 5, 0.7), rgba(60, 10, 15, 0.5)) !important";
            let titleColor = "#ff8080";
            let titleText = "算力底座连通性异常诊断报告";
            
            // 根据具体错误类型精细化提取人性化解决步骤
            const errLower = rawError.toLowerCase();
            if (type === "no_primary") {
                borderGlow = "rgba(255, 157, 0, 0.45) !important";
                cardBg = "linear-gradient(135deg, rgba(30, 15, 0, 0.7), rgba(60, 30, 0, 0.5)) !important";
                titleColor = "var(--accent-orange, #ff9d00)";
                titleText = "未配置主算力单元警告";
                guideSteps = `
                    <li>点击下方 **“配置算力单元”** 按钮。</li>
                    <li>在弹出的算力单元配置框中划定并固化一个主节点。</li>
                    <li>划定完成后，点击下方 **“重新检测”** 按钮即可唤醒大副。</li>
                `;
            } else if (type === "models_empty") {
                borderGlow = "rgba(255, 157, 0, 0.45) !important";
                cardBg = "linear-gradient(135deg, rgba(30, 15, 0, 0.7), rgba(60, 30, 0, 0.5)) !important";
                titleColor = "var(--accent-orange, #ff9d00)";
                titleText = "算力就绪但未装载模型警告";
                errorMsg = "算力通道已物理接通，但该节点当前未加载任何模型资产（Model List 为空）。";
                guideSteps = `
                    <li>打开您的本地算力程序（如 LM Studio 或 Ollama）。</li>
                    <li>在应用内**手动载入或拉取一个可用模型**（例如 <code>qwen/qwen3.5-9b</code> 或 <code>deepseek-r1</code>）。</li>
                    <li>确认模型加载完成后，点击下方的 **“重新检测”** 按钮即可。</li>
                `;
            } else if (type === "fallback_active") {
                borderGlow = "rgba(0, 242, 255, 0.4) !important";
                cardBg = "linear-gradient(135deg, rgba(0, 15, 30, 0.7), rgba(0, 30, 60, 0.5)) !important";
                titleColor = "var(--accent-secondary)";
                titleText = "主算力故障已无缝热接管";
                errorMsg = `主节点 [${primaryId}] 连通失败：${rawError}。`;
                guideSteps = `
                    <li>**容灾接管已生效**：大副 Agent 当前已**无缝热切换至备用算力节点 [${fallbackId}]**。</li>
                    <li>您现在可以照常输入指令进行协同创作，不受此故障影响。</li>
                    <li>建议您在闲暇时确认本地 [${primaryId}] 算力程序状态是否正常。</li>
                `;
            } else {
                // offline - 主备皆休眠
                if (errLower.includes("refused") || errLower.includes("connect")) {
                    guideSteps = `
                        <li>确认您的本地算力程序（Ollama / LM Studio）**已打开并正在后台运行**。</li>
                        <li>如果您使用的是 Ollama，请在终端运行 <code>ollama serve</code>。</li>
                        <li>若是 LM Studio，确认其“Local Server”选项卡下的 **“Start Server”** 已点亮。</li>
                        <li>核对端点地址配置是否符合本机的 <code>http://localhost:1234/v1</code> 或 <code>11434</code>。</li>
                    `;
                } else if (errLower.includes("timeout") || errLower.includes("timed out")) {
                    guideSteps = `
                        <li>**网络超时检测**：大模型服务若在云端（如 Gemini / OpenAI 官方），需要科学上网环境。</li>
                        <li>请检查您的代理工具状态，或在系统设置里更换为国内高速兼容网关（如 SiliconFlow ）。</li>
                        <li>核对您的物理密钥 (API Key) 是否正确。</li>
                    `;
                } else {
                    guideSteps = `
                        <li>检查该节点的端点地址与物理密钥 (API Key) 是否有效。</li>
                        <li>点击下方的 **“配置算力单元”** 按钮，一键唤醒算力编辑器核对参数。</li>
                        <li>您可以在本地算力挂起时，配置一个稳定的云端提供商作为容灾备用节点。</li>
                    `;
                }
            }
            
            const card = document.createElement('div');
            card.id = "agent-compute-diagnostic-card";
            card.className = "agent-msg system-msg patch-diff-card";
            card.style.cssText = `border: 1px solid ${borderGlow}; background: ${cardBg}; animation: fadeIn 0.45s cubic-bezier(0.25, 0.8, 0.25, 1);`;
            
            card.innerHTML = `
                <div class="patch-diff-header" style="border-bottom: 1px solid hsla(0, 0%, 100%, 0.1); padding-bottom: 6px;">
                    <span class="patch-icon" style="filter: drop-shadow(0 0 4px ${titleColor});">📡</span>
                    <span class="patch-title" style="color: ${titleColor}; font-weight: bold; font-size: 0.74rem;">${titleText}</span>
                </div>
                <div style="font-size: 0.7rem; line-height: 1.5; color: var(--text-bright); margin-top: 8px;">
                    <p style="margin: 0 0 6px 0; opacity: 0.9;">
                        <strong>算力节点：</strong> 
                        <code style="color: var(--accent-secondary); background: hsla(0, 0%, 100%, 0.05); padding: 2px 6px; border-radius: 4px; border: 1px solid hsla(0, 0%, 100%, 0.1); font-family: var(--font-mono); font-size: 0.64rem;">${primaryId.toUpperCase()}</code>
                    </p>
                    <p style="margin: 6px 0 6px 0; opacity: 0.9;"><strong>诊断详情：</strong></p>
                    <p style="margin: 4px 0 8px 0; font-family: var(--font-mono); background: hsla(0, 0%, 0%, 0.35); padding: 8px; border-radius: 6px; border: 1px solid hsla(0, 0%, 100%, 0.05); color: #ffbbbb; word-break: break-all; font-size: 0.66rem;">
                        ${errorMsg}
                    </p>
                    <div style="margin-top: 8px;">
                        <strong style="color: var(--accent-secondary);">💡 专家排查与操作引导：</strong>
                        <ul style="margin: 6px 0 0 16px; padding: 0; list-style-type: decimal; color: var(--text-normal); display: flex; flex-direction: column; gap: 4px;">
                            ${guideSteps}
                        </ul>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; border-top: 1px solid hsla(0, 0%, 100%, 0.05); padding-top: 8px;">
                    <button class="btn-rollback" id="btn-precheck-retry" style="border-color: var(--accent-secondary); color: var(--accent-secondary); background: hsla(180, 100%, 50%, 0.02);">
                        🔄 重新扫描
                    </button>
                    <button class="btn-rollback" id="btn-precheck-fix" style="border-color: var(--accent-orange, #ff9d00); color: var(--accent-orange, #ff9d00); background: hsla(37, 100%, 50%, 0.02);">
                        ⚙️ 配置算力单元
                    </button>
                </div>
            `;
            
            agentFeed.appendChild(card);
            agentFeed.scrollTop = agentFeed.scrollHeight;
            
            // 绑定交互按钮事件
            const btnRetry = card.querySelector('#btn-precheck-retry');
            const btnFix = card.querySelector('#btn-precheck-fix');
            
            if (btnRetry) {
                btnRetry.addEventListener('click', () => {
                    card.remove();
                    if (typeof window.SovereignAgent.initModelCapabilities === 'function') {
                        window.SovereignAgent.initModelCapabilities();
                    }
                });
            }
            
            if (btnFix) {
                btnFix.addEventListener('click', () => {
                    if (window.ComputeHandlers && typeof window.ComputeHandlers.editNode === 'function' && primaryId !== 'none') {
                        window.ComputeHandlers.editNode(primaryId);
                    } else {
                        // 兜底一键切换到算力中心配置页
                        const tabBtn = document.querySelector('[data-tab="compute"]');
                        if (tabBtn) tabBtn.click();
                    }
                });
            }
        }
    };
})();
