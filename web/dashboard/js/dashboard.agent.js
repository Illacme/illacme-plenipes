/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) Logic - SOP Compliant
 */
document.addEventListener('DOMContentLoaded', () => {
    if (window._dbgLog) window._dbgLog('📦 agent.js DOMContentLoaded fired');
    const agentInput = document.getElementById('agent-command-input');
    const agentFeed = document.getElementById('agent-feed');
    const agentPod = document.querySelector('.agent-pod');
    const agentStatus = document.getElementById('agent-status-tag');
    const rightSidebar = document.getElementById('right-sidebar');

    if (!agentInput || !agentFeed) {
        if (window._dbgLog) window._dbgLog('<span style="color:#f00">⛔ agent-input/feed NOT FOUND</span>');
        return;
    }

    // 🧠 思维链 Toggle 与深度选择框的联动
    const reasoningToggle = document.getElementById('agent-reasoning-toggle');
    const reasoningDepthContainer = document.getElementById('agent-reasoning-depth-container');
    if (reasoningToggle && reasoningDepthContainer) {
        reasoningToggle.addEventListener('change', () => {
            const isChecked = reasoningToggle.checked;
            reasoningDepthContainer.style.opacity = isChecked ? '1' : '0.4';
            reasoningDepthContainer.style.pointerEvents = isChecked ? 'auto' : 'none';
        });
    }

    // ⚙️ 思维链面板点击收折切换
    const settingsToggleBtn = document.getElementById('agent-settings-toggle-btn');
    const settingsPanel = document.querySelector('.agent-engine-settings');
    if (settingsToggleBtn && settingsPanel) {
        settingsToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            settingsPanel.classList.toggle('expanded');
            const isExpanded = settingsPanel.classList.contains('expanded');
            settingsToggleBtn.style.color = isExpanded ? 'var(--accent-secondary)' : '';
            settingsToggleBtn.style.textShadow = isExpanded ? '0 0 8px var(--accent-secondary)' : '';
        });
    }

    // 🆕 动态获取大模型元数据并改变徽章状态 (V76.3)
    async function refreshModelCapability() {
        const modelNameTag = document.getElementById('active-model-name');
        if (!modelNameTag) return;
        try {
            const r = await fetch('/api/agent/model_info');
            if (!r.ok) throw new Error();
            const data = await r.json();
            modelNameTag.textContent = data.model_name || 'Unknown';
            const updateBadge = (id, active) => {
                const el = document.getElementById(id);
                if (!el) return;
                if (active) {
                    el.classList.remove('disabled'); el.classList.add('active');
                } else {
                    el.classList.remove('active'); el.classList.add('disabled');
                }
            };
            updateBadge('badge-cot', data.capabilities.cot);
            updateBadge('badge-tools', data.capabilities.tools);
            updateBadge('badge-stream', data.capabilities.stream);
            updateBadge('badge-vision', data.capabilities.vision);
        } catch (e) {
            modelNameTag.textContent = '未就绪';
        }
    }
    refreshModelCapability();

    // 点击推荐指令直接填入并聚焦
    if (agentFeed) {
        agentFeed.addEventListener('click', (e) => {
            const codeEl = e.target.closest('.clickable-suggestion');
            if (codeEl && agentInput) {
                agentInput.value = codeEl.textContent.trim();
                agentInput.focus();
                agentInput.style.boxShadow = '0 0 12px rgba(0, 242, 255, 0.4)';
                setTimeout(() => { agentInput.style.boxShadow = ''; }, 400);
            }
        });
    }

    // 全局快捷键 Cmd+K / Ctrl+K 唤醒
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            if (rightSidebar && rightSidebar.classList.contains('collapsed')) {
                rightSidebar.classList.remove('collapsed');
            }
            if (agentInput) agentInput.focus();
            if (agentPod) {
                agentPod.style.boxShadow = 'inset 0 0 30px rgba(0, 242, 255, 0.4)';
                setTimeout(() => { agentPod.style.boxShadow = ''; }, 300);
            }
        }
    });

    // 提交指令
    agentInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const command = agentInput.value.trim();
            if (command) submitAgentTask(command);
        }
    });

    function appendMessage(text, typeClass) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `agent-msg ${typeClass}`;
        msgDiv.innerHTML = text.replace(/\n/g, '<br/>');
        agentFeed.appendChild(msgDiv);
        agentFeed.scrollTop = agentFeed.scrollHeight;
    }

    async function submitAgentTask(command) {
        agentInput.value = ''; agentInput.disabled = true; agentInput.placeholder = 'AI 助手思考中...';
        if (agentPod) agentPod.classList.add('processing');
        if (agentStatus) { agentStatus.textContent = 'EXECUTING'; agentStatus.style.color = 'var(--neon-amber)'; }

        appendMessage(`> ${command}`, 'user-msg');
        const thinkingId = 'agent-thinking-' + Date.now();
        const thinkingDiv = document.createElement('div');
        thinkingDiv.id = thinkingId;
        thinkingDiv.className = 'agent-msg system-msg';
        thinkingDiv.style.opacity = '0.7';
        thinkingDiv.innerHTML = '🧠 AI 协同链路已接通，正在解析指令...';
        agentFeed.appendChild(thinkingDiv);
        agentFeed.scrollTop = agentFeed.scrollHeight;

        await new Promise(resolve => setTimeout(resolve, 60));

        const rToggle = document.getElementById('agent-reasoning-toggle');
        const rDepth = document.getElementById('agent-reasoning-depth');
        const aToggle = document.getElementById('agent-autopilot-toggle');
        const maxIterSelect = document.getElementById('agent-max-iterations');

        const isReasoningEnabled = rToggle ? rToggle.checked : true;
        const selectedReasoningEffort = rDepth ? rDepth.value : 'medium';
        const isAutopilotEnabled = aToggle ? aToggle.checked : false;
        const maxIterations = maxIterSelect ? parseInt(maxIterSelect.value, 10) : 10;

        let firstEventReceived = false, activeThinkingDetails = null, activeThinkingContent = null;
        let activeContentDiv = null, fullContentText = "";

        try {
            const response = await fetch('/api/agent/task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_prompt: command,
                    max_iterations: maxIterations,
                    reasoning_enabled: isReasoningEnabled,
                    reasoning_effort: selectedReasoningEffort,
                    autopilot_enabled: isAutopilotEnabled
                })
            });

            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                
                let boundary = buffer.indexOf('\n\n');
                while (boundary !== -1) {
                    const chunk = buffer.slice(0, boundary);
                    buffer = buffer.slice(boundary + 2);

                    if (chunk.startsWith('data: ')) {
                        if (!firstEventReceived) {
                            firstEventReceived = true;
                            const tDiv = document.getElementById(thinkingId);
                            if (tDiv) tDiv.remove();
                        }
                        try {
                            const data = JSON.parse(chunk.slice(6));
                            if (data.type === 'thinking_chunk') {
                                if (!activeThinkingDetails) {
                                    const msgDiv = document.createElement('div');
                                    msgDiv.className = 'agent-msg thinking-msg';
                                    msgDiv.innerHTML = `<details open><summary><span class="thinking-badge-pulse"></span>🧠 脑网思维链 analysis中...</summary><div class="thinking-content"></div></details>`;
                                    agentFeed.appendChild(msgDiv);
                                    activeThinkingDetails = msgDiv.querySelector('details');
                                    activeThinkingContent = msgDiv.querySelector('.thinking-content');
                                }
                                if (activeThinkingContent) {
                                    activeThinkingContent.textContent += data.delta;
                                    activeThinkingContent.scrollTop = activeThinkingContent.scrollHeight;
                                }
                                agentFeed.scrollTop = agentFeed.scrollHeight;
                            } else if (data.type === 'content_chunk') {
                                if (activeThinkingDetails && activeThinkingDetails.hasAttribute('open')) {
                                    activeThinkingDetails.removeAttribute('open');
                                    const summary = activeThinkingDetails.querySelector('summary');
                                    if (summary) summary.innerHTML = `🧠 脑网思维链 (分析完毕)`;
                                }
                                if (!activeContentDiv) {
                                    activeContentDiv = document.createElement('div');
                                    activeContentDiv.className = 'agent-msg final-msg';
                                    agentFeed.appendChild(activeContentDiv);
                                }
                                fullContentText += data.delta;
                                activeContentDiv.innerHTML = fullContentText.replace(/\n/g, '<br/>');
                                agentFeed.scrollTop = agentFeed.scrollHeight;
                            } else {
                                renderStreamEvent(data);
                            }
                        } catch (err) {
                            console.warn("Failed to parse SSE chunk:", chunk);
                        }
                    }
                    boundary = buffer.indexOf('\n\n');
                }
            }
        } catch (error) {
            appendMessage(`[ERROR] 脑裂链路中断: ${error.message}`, 'system-msg');
        } finally {
            const leftover = document.getElementById(thinkingId);
            if (leftover) leftover.remove();

            if (activeThinkingDetails && activeThinkingDetails.hasAttribute('open')) {
                activeThinkingDetails.removeAttribute('open');
                const summary = activeThinkingDetails.querySelector('summary');
                if (summary) summary.innerHTML = `🧠 脑网思维链 (分析完毕)`;
            }

            agentInput.disabled = false;
            agentInput.placeholder = '输入指令，如“系统状态” (Cmd+K)...';
            if (agentPod) agentPod.classList.remove('processing');
            if (agentStatus) {
                agentStatus.textContent = 'STANDBY';
                agentStatus.style.color = '';
            }
            agentInput.focus();
        }
    }

    // HITL Dialog 状态控制
    const hitlDialog = document.getElementById('agent-hitl-dialog'), hitlToolName = document.getElementById('hitl-tool-name'), hitlToolArgs = document.getElementById('hitl-tool-args');
    const hitlApproveBtn = document.getElementById('hitl-approve-btn'), hitlRejectBtn = document.getElementById('hitl-reject-btn'), hitlCloseBtn = document.getElementById('hitl-close-btn');
    let currentHitlId = null;
    if (hitlDialog) {
        const closeHitl = () => { hitlDialog.close(); currentHitlId = null; };
        if (hitlCloseBtn) hitlCloseBtn.addEventListener('click', closeHitl);
        const submitHitlDecision = async (decision) => {
            if (!currentHitlId) return;
            const hitlId = currentHitlId;
            closeHitl();
            appendMessage(`[HITL] Human decision: ${decision.toUpperCase()}`, 'system-msg');
            try {
                await fetch('/api/agent/authorize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ hitl_id: hitlId, decision: decision })
                });
            } catch (err) {
                appendMessage(`[ERROR] Failed to send HITL decision: ${err.message}`, 'system-msg');
            }
        };
        if (hitlApproveBtn) hitlApproveBtn.addEventListener('click', () => submitHitlDecision('approve'));
        if (hitlRejectBtn) hitlRejectBtn.addEventListener('click', () => submitHitlDecision('reject'));
    }

    function renderStreamEvent(data) {
        if (data.type === 'status') appendMessage(data.message, 'system-msg');
        else if (data.type === 'step') appendMessage(data.message, 'tool-msg');
        else if (data.type === 'final') appendMessage(data.message, 'final-msg');
        else if (data.type === 'hitl_required') {
            appendMessage(data.message, 'system-msg');
            if (hitlDialog) {
                currentHitlId = data.hitl_id;
                if (hitlToolName) hitlToolName.textContent = data.tool;
                if (hitlToolArgs) hitlToolArgs.textContent = JSON.stringify(data.args, null, 2);
                hitlDialog.showModal();
            }
        }
    }
});
