/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) UI Render Layer - Capabilities
 * 职责：大模型能力标签展示、思维链及自动驾驶控制面板的置灰联动与离线状态刷新。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规物理平移。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.render.capabilities.js initializing');

    window.SovereignAgent = window.SovereignAgent || {};
    window.SovereignAgent.render = window.SovereignAgent.render || {};

    let originalWelcomeHtml = '';

    /**
     * 🆕 动态刷新控制面板的大模型徽章状态、悬停提示及思维链开关/深度的置灰联动
     * @param {Object} data 大模型元数据
     */
    window.SovereignAgent.render.updateCapabilities = function(data) {
        const modelNameTag = document.getElementById('active-model-name');
        if (!modelNameTag) return;

        modelNameTag.textContent = data.model_name || 'Unknown';

        const badgeTooltips = {
            'badge-cot': { active: '当前模型已点亮原生思维链或深度推理能力 (Reasoning CoT)', disabled: '当前模型不支持或未开启原生思维链及深度推理' },
            'badge-tools': { active: '当前模型已打通本地文件读写、指令执行等工具自治权限', disabled: '当前算力底座处于模拟状态，或适配器不支持物理工具调用' },
            'badge-stream': { active: '当前模型已开启高吞吐、零延迟 SSE 流式极速响应', disabled: '当前模型不支持流式极速响应' },
            'badge-vision': { active: '当前模型已开启图像及多模态输入理解能力 (Vision)', disabled: '当前模型不支持图像或多模态输入' }
        };

        const updateBadge = (id, active) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.classList.toggle('active', !!active);
            el.classList.toggle('disabled', !active);
            if (badgeTooltips[id]) el.title = active ? badgeTooltips[id].active : badgeTooltips[id].disabled;
        };

        ['cot', 'tools', 'stream', 'vision'].forEach(k => updateBadge(`badge-${k}`, data.capabilities[k]));

        // 🧠 配置面板联动与物理置灰（思维链、自动驾驶等）
        const isDisabled = data.disabled || data.model_name === '已关闭' || data.model_name === '已禁用';
        const engineSettings = document.querySelector('.agent-engine-settings');
        if (engineSettings) {
            if (isDisabled) {
                engineSettings.style.opacity = '0.4';
                engineSettings.style.pointerEvents = 'none';
                engineSettings.querySelectorAll('input, select').forEach(el => {
                    el.disabled = true;
                });
            } else {
                engineSettings.style.opacity = '1';
                engineSettings.style.pointerEvents = 'auto';
                
                const autopilotToggle = document.getElementById('agent-autopilot-toggle');
                const maxIter = document.getElementById('agent-max-iterations');
                if (autopilotToggle) autopilotToggle.disabled = false;
                if (maxIter) maxIter.disabled = false;

                const rToggle = document.getElementById('agent-reasoning-toggle');
                const rDepth = document.getElementById('agent-reasoning-depth');
                const rDepthContainer = document.getElementById('agent-reasoning-depth-container');
                const hasCot = !!data.capabilities.cot;
                
                if (rToggle) {
                    rToggle.disabled = !hasCot;
                    if (!hasCot) {
                        rToggle.checked = false;
                    }
                    const switchLabel = rToggle.closest('.setting-item');
                    if (switchLabel) {
                        switchLabel.style.opacity = hasCot ? '1' : '0.4';
                        switchLabel.style.pointerEvents = hasCot ? 'auto' : 'none';
                        switchLabel.title = hasCot ? '开启/关闭模型思维链推理' : '当前所选 AI 模型不支持 CoT 思维链推理';
                    }
                    if (rDepthContainer) {
                        const isDepthActive = hasCot && rToggle.checked;
                        rDepthContainer.style.opacity = isDepthActive ? '1' : '0.4';
                        rDepthContainer.style.pointerEvents = isDepthActive ? 'auto' : 'none';
                        rDepthContainer.title = hasCot ? '针对云端/标准模型调控推理深度(Low/Medium/High)；本地模型(LMStudio/Ollama)由洗涤网关自动转译对准' : '当前所选 AI 模型不支持 CoT 思维链推理';
                    }
                }
                if (rDepth) {
                    rDepth.disabled = !(hasCot && rToggle.checked);
                }
            }
        }

        // 🔒 AI 算力总控已关闭联动逻辑
        const agentInput = document.getElementById('agent-command-input');
        const agentStatus = document.getElementById('agent-status-tag');
        const welcomeEl = document.getElementById('agent-default-welcome');
        if (welcomeEl && !originalWelcomeHtml) {
            originalWelcomeHtml = welcomeEl.innerHTML;
        }

        if (isDisabled) {
            const diagCard = document.getElementById('agent-compute-diagnostic-card');
            if (diagCard) diagCard.remove();

            if (welcomeEl) {
                welcomeEl.style.display = 'flex';
                welcomeEl.style.borderLeft = '2px solid rgba(255, 255, 255, 0.15)';
                welcomeEl.style.background = 'rgba(255, 255, 255, 0.02)';
                welcomeEl.style.boxShadow = 'none';
                welcomeEl.innerHTML = `
                    <div style="font-weight: bold; color: var(--text-dim); font-size: 0.72rem; display: flex; align-items: center; gap: 6px; letter-spacing: 0.5px;">
                        🔴 协同服务已离线
                    </div>
                    <p style="margin: 0; line-height: 1.45; color: var(--text-dim); font-size: 0.68rem;">
                        AI 算力总控当前处于关闭状态，智能协同助手已下线。
                    </p>
                    <div style="font-size: 0.65rem; color: var(--text-dim); line-height: 1.5; margin-top: 4px; display: flex; flex-direction: column; gap: 8px;">
                        <span style="display: block; font-weight: bold; color: var(--text-dim); font-size: 0.68rem;">💡 如何重新启用：</span>
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            <span>• 请前往左侧菜单的 <strong>「算力中心」</strong>，在调度策略选项卡中勾选开启 <strong>“AI 算力总控”</strong> 并保存配置。</span>
                            <span>• 或者前往 <strong>「系统设置」</strong> -> 「语言与 AI」面板重新激活 AI 算力底座。</span>
                        </div>
                    </div>
                `;
            }

            if (agentInput) {
                agentInput.disabled = true;
                agentInput.placeholder = 'AI 算力已关闭，Copilot 离线';
                agentInput.value = '';
                agentInput.style.opacity = '0.45';
                agentInput.style.pointerEvents = 'none';
            }
            if (agentStatus) {
                agentStatus.textContent = '🔴 已禁用';
                agentStatus.style.color = 'var(--text-dim)';
                agentStatus.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                agentStatus.style.textShadow = 'none';
            }
        } else {
            if (welcomeEl && originalWelcomeHtml) {
                welcomeEl.style.borderLeft = '2px solid var(--accent-secondary)';
                welcomeEl.style.background = 'var(--neon-cyan-03)';
                welcomeEl.style.boxShadow = 'var(--shadow-glow)';
                welcomeEl.innerHTML = originalWelcomeHtml;
            }
            if (agentInput && agentInput.placeholder === 'AI 算力已关闭，Copilot 离线') {
                agentInput.disabled = false;
                agentInput.placeholder = '输入指令，如“系统状态” (Cmd+K)...';
                agentInput.style.opacity = '1';
                agentInput.style.pointerEvents = 'auto';
            }
            if (agentStatus && agentStatus.textContent === '🔴 已禁用') {
                agentStatus.textContent = '🟢 待命';
                agentStatus.style.color = '';
                agentStatus.style.borderColor = '';
                agentStatus.style.textShadow = '';
            }
        }
    };

    /**
     * ⚙️ 显示大模型元数据获取失败的“未就绪”状态
     */
    window.SovereignAgent.render.showNotReadyState = function() {
        const el = document.getElementById('active-model-name'), s = document.getElementById('agent-status-tag');
        if (el) el.textContent = '未就绪';
        if (s) {
            s.textContent = '🔴 离线';
            s.style.color = 'var(--neon-red, #ff4d4d)';
            s.style.borderColor = 'hsla(0, 100%, 65%, 0.4)';
            s.style.textShadow = '0 0 6px hsla(0, 100%, 65%, 0.4)';
        }
    };
})();
