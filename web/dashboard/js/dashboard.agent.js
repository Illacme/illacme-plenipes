/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) Logic
 * V75.0
 */

document.addEventListener('DOMContentLoaded', () => {
    if (window._dbgLog) window._dbgLog('📦 agent.js DOMContentLoaded fired');
    const agentInput = document.getElementById('agent-command-input');
    const agentFeed = document.getElementById('agent-feed');
    const agentPod = document.querySelector('.agent-pod');
    const agentStatus = document.getElementById('agent-status-tag');
    const rightSidebar = document.getElementById('right-sidebar');

    if (window._dbgLog) window._dbgLog('🔍 agentInput=' + !!agentInput + ' agentFeed=' + !!agentFeed + ' agentPod=' + !!agentPod);
    if (!agentInput || !agentFeed) {
        if (window._dbgLog) window._dbgLog('<span style="color:#f00">⛔ agent-input/feed NOT FOUND, aborting!</span>');
        return;
    }

    // 全局快捷键 Cmd+K / Ctrl+K 唤醒
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault(); // 阻止浏览器默认行为
            
            // 确保右侧栏是展开的（如果有折叠逻辑的话）
            if (rightSidebar.classList.contains('collapsed')) {
                rightSidebar.classList.remove('collapsed');
            }

            agentInput.focus();
            
            // 添加闪烁特效提醒
            agentPod.style.boxShadow = 'inset 0 0 30px rgba(0, 242, 255, 0.4)';
            setTimeout(() => {
                agentPod.style.boxShadow = '';
            }, 300);
        }
    });

    // 提交指令
    agentInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const command = agentInput.value.trim();
            if (window._dbgLog) window._dbgLog('⌨️ Enter pressed, command="' + command + '"');
            if (!command) return;

            submitAgentTask(command);
        }
    });

    function appendMessage(text, typeClass) {
        if (window._dbgLog) window._dbgLog('📝 appendMessage: type=' + typeClass + ' len=' + text.length);
        const msgDiv = document.createElement('div');
        msgDiv.className = `agent-msg ${typeClass}`;
        
        // 解析简单的换行
        msgDiv.innerHTML = text.replace(/\n/g, '<br/>');
        
        agentFeed.appendChild(msgDiv);
        if (window._dbgLog) window._dbgLog('✅ DOM appended, feed children=' + agentFeed.children.length + ' feedH=' + agentFeed.scrollHeight);
        // 自动滚动到底部
        agentFeed.scrollTop = agentFeed.scrollHeight;
    }

    async function submitAgentTask(command) {
        if (window._dbgLog) window._dbgLog('🚀 submitAgentTask START: "' + command + '"');

        // 1. 禁用输入，重置状态
        agentInput.value = '';
        agentInput.disabled = true;
        agentInput.placeholder = '主脑运算中...';
        agentPod.classList.add('processing');
        agentStatus.textContent = 'EXECUTING';
        agentStatus.style.color = '#ff9d00';

        // 2. 立即显示用户指令（永久保留在 feed 中）
        appendMessage(`> ${command}`, 'user-msg');
        console.log('[Agent UI] User message appended, feed children:', agentFeed.children.length);

        // 3. 显示过渡期的系统思考状态
        const thinkingId = 'agent-thinking-' + Date.now();
        const thinkingDiv = document.createElement('div');
        thinkingDiv.id = thinkingId;
        thinkingDiv.className = 'agent-msg system-msg';
        thinkingDiv.style.opacity = '0.7';
        thinkingDiv.innerHTML = '🧠 主脑链路已接通，正在解析指令...';
        agentFeed.appendChild(thinkingDiv);
        agentFeed.scrollTop = agentFeed.scrollHeight;
        console.log('[Agent UI] Thinking indicator appended');

        // 让出事件循环，确保浏览器立即重绘用户指令和思考状态
        await new Promise(resolve => setTimeout(resolve, 60));

        // 4. 发起请求并接收 SSE 流
        let firstEventReceived = false;
        try {
            console.log('[Agent UI] Sending fetch to /api/agent/task');
            const response = await fetch('/api/agent/task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_prompt: command,
                    max_iterations: 10
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            console.log('[Agent UI] Response received, reading SSE stream');

            // 读取 SSE 流
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                
                // 处理双换行分隔的 SSE 消息
                let boundary = buffer.indexOf('\n\n');
                while (boundary !== -1) {
                    const chunk = buffer.slice(0, boundary);
                    buffer = buffer.slice(boundary + 2);

                    if (chunk.startsWith('data: ')) {
                        // 首条流式事件到达时，移除"思考中"指示器
                        if (!firstEventReceived) {
                            firstEventReceived = true;
                            const tDiv = document.getElementById(thinkingId);
                            if (tDiv) tDiv.remove();
                            console.log('[Agent UI] First SSE event, thinking removed');
                        }
                        try {
                            const data = JSON.parse(chunk.slice(6));
                            renderStreamEvent(data);
                        } catch (err) {
                            console.warn("[Agent UI] Failed to parse SSE chunk:", chunk);
                        }
                    }
                    boundary = buffer.indexOf('\n\n');
                }
            }
        } catch (error) {
            appendMessage(`[ERROR] 脑裂链路中断: ${error.message}`, 'system-msg');
            console.error('[Agent UI] Execution error:', error);
        } finally {
            // 5. 清理残留思考指示器（如果从未收到流式事件）
            const leftover = document.getElementById(thinkingId);
            if (leftover) leftover.remove();

            // 6. 恢复就绪状态
            agentInput.disabled = false;
            agentInput.placeholder = 'CMD: 唤醒主脑 (Cmd+K)';
            agentPod.classList.remove('processing');
            agentStatus.textContent = 'STANDBY';
            agentStatus.style.color = '';
            agentInput.focus();
        }
    }

    // HITL Dialog State
    const hitlDialog = document.getElementById('agent-hitl-dialog');
    const hitlToolName = document.getElementById('hitl-tool-name');
    const hitlToolArgs = document.getElementById('hitl-tool-args');
    const hitlApproveBtn = document.getElementById('hitl-approve-btn');
    const hitlRejectBtn = document.getElementById('hitl-reject-btn');
    const hitlCloseBtn = document.getElementById('hitl-close-btn');
    let currentHitlId = null;

    if (hitlDialog) {
        const closeHitl = () => {
            hitlDialog.close();
            currentHitlId = null;
        };

        hitlCloseBtn.addEventListener('click', closeHitl);

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
                console.error("HITL authorization failed", err);
                appendMessage(`[ERROR] Failed to send HITL decision: ${err.message}`, 'system-msg');
            }
        };

        hitlApproveBtn.addEventListener('click', () => submitHitlDecision('approve'));
        hitlRejectBtn.addEventListener('click', () => submitHitlDecision('reject'));
    }

    function renderStreamEvent(data) {
        if (data.type === 'status') {
            appendMessage(data.message, 'system-msg');
        } else if (data.type === 'step') {
            appendMessage(data.message, 'tool-msg');
        } else if (data.type === 'final') {
            appendMessage(data.message, 'final-msg');
        } else if (data.type === 'hitl_required') {
            appendMessage(data.message, 'system-msg');
            if (hitlDialog) {
                currentHitlId = data.hitl_id;
                hitlToolName.textContent = data.tool;
                hitlToolArgs.textContent = JSON.stringify(data.args, null, 2);
                hitlDialog.showModal();
            } else {
                console.warn("HITL required but dialog not found.");
            }
        }
    }
});
