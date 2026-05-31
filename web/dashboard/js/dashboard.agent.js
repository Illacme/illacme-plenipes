/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) Logic - SOP Compliant
 * 负责控制面板主胶合层、快捷键监听、指令路由及子模块（api, render, hitl）的总装中心。
 */
document.addEventListener('DOMContentLoaded', () => {
    if (window._dbgLog) window._dbgLog('📦 agent.js DOMContentLoaded fired');

    // 检查核心依赖是否就绪
    const sa = window.SovereignAgent;
    if (!sa || !sa.api || !sa.render || !sa.hitl) {
        console.error("🚨 [Agent Glue] Failed to load sub-modules. Core namespace missing.");
        return;
    }

    // 🌟 引入状态执行锁与物理时序计数器，防止并发提交并支持大屏双轨还原排序 (SOP-01 Compliant)
    let isExecuting = false, messageOrderCounter = 0;

    const agentInput = document.getElementById('agent-command-input'), agentFeed = document.getElementById('agent-feed');
    const agentPod = document.querySelector('.agent-pod'), agentStatus = document.getElementById('agent-status-tag');
    const rightSidebar = document.getElementById('right-sidebar');

    if (!agentInput || !agentFeed) return;

    // 🧠 思维链 Toggle 与深度选择框的联动
    const rToggle = document.getElementById('agent-reasoning-toggle'), rDepthContainer = document.getElementById('agent-reasoning-depth-container');
    if (rToggle && rDepthContainer) {
        rToggle.addEventListener('change', () => {
            rDepthContainer.style.opacity = rToggle.checked ? '1' : '0.4';
            rDepthContainer.style.pointerEvents = rToggle.checked ? 'auto' : 'none';
        });
    }

    // ⚙️ 思维链面板点击收折切换
    const settingsToggleBtn = document.getElementById('agent-settings-toggle-btn'), settingsPanel = document.querySelector('.agent-engine-settings');
    if (settingsToggleBtn && settingsPanel) {
        settingsToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isExp = settingsPanel.classList.toggle('expanded');
            settingsToggleBtn.style.color = isExp ? 'var(--accent-secondary)' : '';
            settingsToggleBtn.style.textShadow = isExp ? '0 0 8px var(--accent-secondary)' : '';
        });
    }

    // ⛶ 初始化极光大屏模式分片引擎 (SOP-01 & SOP-02 Compliant)
    if (typeof window.initAgentWidescreen === 'function') {
        window.initAgentWidescreen(agentPod, agentFeed, document.getElementById('agent-widescreen-toggle-btn'), rightSidebar, settingsPanel, settingsToggleBtn);
    }

    // 🆕 初始化获取大模型元数据并渲染徽章状态
    async function initModelCapabilities() {
        try {
            const data = await sa.api.fetchModelInfo();
            sa.render.updateCapabilities(data);
        } catch (e) {
            sa.render.showNotReadyState();
        }
    }
    initModelCapabilities();

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
            if (rightSidebar && rightSidebar.classList.contains('collapsed')) rightSidebar.classList.remove('collapsed');
            if (agentInput) agentInput.focus();
            if (agentPod) {
                agentPod.style.boxShadow = 'inset 0 0 30px rgba(0, 242, 255, 0.4)';
                setTimeout(() => { agentPod.style.boxShadow = ''; }, 300);
            }
        }
    });

    // 提交指令监听
    agentInput.addEventListener('keydown', async (e) => {
        // 🌟 物理防火墙：过滤中文输入法 (IME) 合成未结束时的回车确认事件，防止发送未完成的脏指令
        if (e.isComposing || e.keyCode === 229) return;
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const command = agentInput.value.trim();
            if (command) submitAgentTask(command);
        }
    });

    // 🛡️ 初始化人类在环 (HITL) 决策收集器并建立粘合回调
    sa.hitl.init(async (hitlId, decision) => {
        sa.render.appendMessage(`[HITL] Human decision: ${decision.toUpperCase()}`, 'system-msg');
        try {
            await sa.api.sendHitlDecision(hitlId, decision);
        } catch (err) {
            sa.render.appendMessage(`[ERROR] Failed to send HITL decision: ${err.message}`, 'system-msg');
        }
    });

    // 🚀 主执行流程胶合控制
    async function submitAgentTask(command) {
        if (isExecuting) return; // 🌟 物理防御：防止因高频敲击或并发流引起执行实例重叠
        isExecuting = true;

        agentInput.value = ''; agentInput.disabled = true; agentInput.placeholder = 'AI 助手思考中...';
        if (agentPod) agentPod.classList.add('processing');
        if (agentStatus) { agentStatus.textContent = 'EXECUTING'; agentStatus.style.color = 'var(--neon-amber)'; }

        sa.render.appendMessage(`> ${command}`, 'user-msg');
        
        const thinkingId = 'agent-thinking-' + Date.now();
        const thinkingDiv = document.createElement('div');
        thinkingDiv.id = thinkingId;
        thinkingDiv.className = 'agent-msg system-msg';
        thinkingDiv.style.opacity = '0.7';
        thinkingDiv.innerHTML = '🧠 AI 协同链路已接通，正在解析指令...';
        agentFeed.appendChild(thinkingDiv);
        agentFeed.scrollTop = agentFeed.scrollHeight;

        await new Promise(resolve => setTimeout(resolve, 60));

        const rToggleBtn = document.getElementById('agent-reasoning-toggle'), rDepth = document.getElementById('agent-reasoning-depth');
        const aToggle = document.getElementById('agent-autopilot-toggle'), maxIterSelect = document.getElementById('agent-max-iterations');

        const isReasoningEnabled = rToggleBtn ? rToggleBtn.checked : true;
        const selectedReasoningEffort = rDepth ? rDepth.value : 'medium';
        const isAutopilotEnabled = aToggle ? aToggle.checked : false;
        const maxIterations = maxIterSelect ? parseInt(maxIterSelect.value, 10) : 10;

        let activeThinkingDiv = null, activeThinkingDetails = null;

        try {
            const response = await sa.api.submitTask({
                user_prompt: command,
                max_iterations: maxIterations,
                reasoning_enabled: isReasoningEnabled,
                reasoning_effort: selectedReasoningEffort,
                autopilot_enabled: isAutopilotEnabled
            });

            // 投喂给渲染层打字机 SSE 解析器进行流式刷新
            const result = await sa.render.renderStream(response, thinkingId, renderStreamEvent);
            activeThinkingDiv = result.activeThinkingDiv;
            activeThinkingDetails = result.activeThinkingDetails;

        } catch (error) {
            sa.render.appendMessage(`[ERROR] 脑裂链路中断: ${error.message}`, 'system-msg');
        } finally {
            sa.render.cleanupStream(thinkingId, activeThinkingDiv, activeThinkingDetails);

            agentInput.disabled = false;
            agentInput.placeholder = '输入指令，如“系统状态” (Cmd+K)...';
            if (agentPod) agentPod.classList.remove('processing');
            if (agentStatus) { agentStatus.textContent = 'STANDBY'; agentStatus.style.color = ''; }
            agentInput.focus();
            isExecuting = false; // 🌟 优雅解锁，允许下一次安全提交
        }
    }

    // 📡 [V76.9] 物理状态栏联动切换：点击底部状态栏审计日志，动态切换右边栏审计日志模块的显示与隐藏
    const summaryText = document.getElementById('audit-summary-text');
    const auditFeedPod = document.getElementById('audit-feed-pod');
    if (summaryText && auditFeedPod) {
        // 给状态栏文字追加 pointer 手势与悬浮气泡提示
        summaryText.style.cursor = 'pointer';
        summaryText.title = "点击以切换右边栏审计日志模块显示/隐藏";
        
        summaryText.addEventListener('click', (e) => {
            e.stopPropagation();
            const isHidden = auditFeedPod.style.display === 'none';
            if (isHidden) {
                // 展现审计模块，高度通过 flex 机制优雅折收
                auditFeedPod.style.display = 'flex';
                summaryText.style.textShadow = '0 0 10px var(--accent-secondary)';
                
                // 滚动到底部以展现最新日志
                const auditFeed = document.getElementById('audit-feed');
                if (auditFeed) auditFeed.scrollTop = 0;
            } else {
                // 重新收起隐藏，AI 模块独占 100%
                auditFeedPod.style.display = 'none';
                summaryText.style.textShadow = '';
            }
        });
    }

    // 渲染流式状态机事件
    function renderStreamEvent(data) {
        if (data.type === 'status') sa.render.appendMessage(data.message, 'system-msg');
        else if (data.type === 'step') sa.render.appendMessage(data.message, 'tool-msg');
        else if (data.type === 'final') sa.render.appendMessage(data.message, 'final-msg');
        else if (data.type === 'patch_applied') {
            sa.render.renderPatchDiff(data);
        }
        else if (data.type === 'hitl_required') {
            sa.render.appendMessage(data.message, 'system-msg');
            sa.hitl.showDialog(data);
        }
    }
});
