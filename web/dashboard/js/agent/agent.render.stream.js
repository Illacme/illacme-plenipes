/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) UI Render Layer - Stream
 * 职责：流式打字机动画渲染 (SSE)、深度思维链过程展示、以及微创补丁 Visual Diff 物理对照卡片渲染与交互。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规物理平移。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.render.stream.js initializing');

    window.SovereignAgent = window.SovereignAgent || {};
    window.SovereignAgent.render = window.SovereignAgent.render || {};

    const renderMarkdown = text => (typeof window.renderMarkdown === 'function' ? window.renderMarkdown(text) : text);

    /**
     * 🛠️ 动态渲染微创补丁 Visual Diff 对照卡片与撤销物理按钮 (V76.8)
     * @param {Object} data 包含 patch_id, relative_path, search_content, replace_content, message 的数据包
     */
    window.SovereignAgent.render.renderPatchDiff = function(data) {
        const agentFeed = document.getElementById('agent-feed');
        if (!agentFeed) return;

        const card = document.createElement('div');
        card.className = 'agent-msg patch-diff-card glass-panel';
        card.id = `patch-${data.patch_id}`;

        // 精准计算并折叠展示 diff 行
        const searchLines = (data.search_content || '').split('\n');
        const replaceLines = (data.replace_content || '').split('\n');

        let diffHtml = '';
        searchLines.forEach(line => {
            diffHtml += `<div class="patch-diff-line deletion"><span class="line-marker">-</span><span class="line-text">${escapeHtml(line)}</span></div>`;
        });
        replaceLines.forEach(line => {
            diffHtml += `<div class="patch-diff-line addition"><span class="line-marker">+</span><span class="line-text">${escapeHtml(line)}</span></div>`;
        });

        card.innerHTML = `
            <div class="patch-diff-header">
                <span class="patch-icon">🛠️</span>
                <span class="patch-title">微创补丁已安全落盘</span>
                <span class="patch-file" title="${escapeHtml(data.relative_path)}">${escapeHtml(data.relative_path.split('/').pop())}</span>
            </div>
            <div class="patch-diff-body">
                ${diffHtml}
            </div>
            <div class="patch-diff-actions">
                <button class="btn-rollback" id="btn-rollback-${data.patch_id}">
                    <span class="btn-icon">🔄</span>
                    <span class="btn-text">一键撤销 / Rollback</span>
                </button>
            </div>
        `;

        agentFeed.appendChild(card);
        agentFeed.scrollTop = agentFeed.scrollHeight;

        // 物理按钮防抖绑定
        const rollbackBtn = document.getElementById(`btn-rollback-${data.patch_id}`);
        if (rollbackBtn) {
            rollbackBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                if (rollbackBtn.disabled) return;

                rollbackBtn.disabled = true;
                rollbackBtn.classList.add('loading');
                rollbackBtn.querySelector('.btn-text').textContent = '正在物理回撤...';

                try {
                    const result = await window.SovereignAgent.api.rollbackPatch(data.patch_id);
                    
                    // 成功回滚：视觉高阶沉降，置为暗淡且禁用状态
                    rollbackBtn.classList.remove('loading');
                    rollbackBtn.classList.add('success');
                    rollbackBtn.querySelector('.btn-icon').textContent = '✅';
                    rollbackBtn.querySelector('.btn-text').textContent = '已成功物理回滚';
                    card.classList.add('rolled-back');
                    
                    // 在 Feed 中追加系统通知
                    if (typeof window.SovereignAgent.render.appendMessage === 'function') {
                        window.SovereignAgent.render.appendMessage(`[SUCCESS] ${result.message}`, 'system-msg');
                    }
                } catch (err) {
                    // 拦截性失败：展示红字报错，3.5秒后自动恢复可重试状态以自愈
                    console.error(err);
                    rollbackBtn.classList.remove('loading');
                    rollbackBtn.classList.add('failed');
                    rollbackBtn.querySelector('.btn-icon').textContent = '⚠️';
                    rollbackBtn.querySelector('.btn-text').textContent = `回滚失败: ${err.message || err}`;
                    
                    setTimeout(() => {
                        rollbackBtn.disabled = false;
                        rollbackBtn.classList.remove('failed');
                        rollbackBtn.querySelector('.btn-icon').textContent = '🔄';
                        rollbackBtn.querySelector('.btn-text').textContent = '一键撤销 / Rollback';
                    }, 3500);
                }
            });
        }

        // 极简的安全字符逃逸工具
        function escapeHtml(str) {
            if (!str) return '';
            return str
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
    };

    /**
     * 渲染 SSE 流式打字机动画
     * @param {Response} response API 的 fetch Response
     * @param {string} thinkingId 等待动画容器 ID
     * @param {Function} onStreamEvent 其他类型事件的回调函数
     * @returns {Promise<Object>} 返回生成块 of DOM 引用供清理使用
     */
    window.SovereignAgent.render.renderStream = async function(response, thinkingId, onStreamEvent) {
        const agentFeed = document.getElementById('agent-feed');
        if (!agentFeed) return {};

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let firstEventReceived = false;

        let activeThinkingDiv = null, activeThinkingDetails = null, activeThinkingContent = null;
        let activeContentDiv = null, fullContentText = "", fullThinkingText = "";

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
                                activeThinkingDiv = document.createElement('div');
                                activeThinkingDiv.className = 'agent-msg thinking-msg streaming';
                                activeThinkingDiv.innerHTML = `<details open><summary><span class="thinking-badge-pulse"></span>🧠 AI 深度推理链 (深度分析中...)</summary><div class="thinking-content"></div></details>`;
                                agentFeed.appendChild(activeThinkingDiv);
                                activeThinkingDetails = activeThinkingDiv.querySelector('details');
                                activeThinkingContent = activeThinkingDiv.querySelector('.thinking-content');
                            }
                            if (activeThinkingContent) {
                                const el = activeThinkingContent;
                                const isAtBottom = el.scrollHeight - el.clientHeight - el.scrollTop < 24;
                                fullThinkingText += data.delta;
                                el.innerHTML = renderMarkdown(fullThinkingText);
                                if (isAtBottom) el.scrollTop = el.scrollHeight;
                            }
                            agentFeed.scrollTop = agentFeed.scrollHeight;
                        } else if (data.type === 'content_chunk') {
                            // 🌟 物理防御：首个内容块如果只有空行或空白，忽略它，防止大模型前置换行符污染 UI 产生大片空白
                            if (fullContentText || data.delta.trim()) {
                                if (activeThinkingDiv && activeThinkingDiv.classList.contains('streaming')) {
                                    activeThinkingDiv.classList.remove('streaming');
                                }
                                if (activeThinkingDetails) {
                                    const summary = activeThinkingDetails.querySelector('summary');
                                    if (summary) summary.innerHTML = `🧠 AI 深度推理链 (分析完毕)`;
                                }
                                if (!activeContentDiv) {
                                    activeContentDiv = document.createElement('div');
                                    activeContentDiv.className = 'agent-msg final-msg streaming';
                                    agentFeed.appendChild(activeContentDiv);
                                }
                                fullContentText += data.delta;
                                activeContentDiv.innerHTML = renderMarkdown(fullContentText);
                                agentFeed.scrollTop = agentFeed.scrollHeight;
                            }
                        } else {
                            // 🌟 物理防御：如果已经通过 content_chunk 实时渲染了回答，则仅更新内容，防止重复添加 final-msg 盒子
                            if (data.type === 'final' && activeContentDiv) {
                                activeContentDiv.innerHTML = renderMarkdown(data.message);
                            } else {
                                if (onStreamEvent) onStreamEvent(data);
                            }
                        }
                    } catch (err) {
                        console.warn("Failed to parse SSE chunk:", chunk);
                    }
                }
                boundary = buffer.indexOf('\n\n');
            }
        }

        if (activeContentDiv && activeContentDiv.classList.contains('streaming')) {
            activeContentDiv.classList.remove('streaming');
        }

        return { activeThinkingDiv, activeThinkingDetails };
    };

    /**
     * ⚙️ SSE 交互结束后对思维链等挂起 DOM 块执行物理打扫与状态合拢
     */
    window.SovereignAgent.render.cleanupStream = function(thinkingId, activeThinkingDiv, activeThinkingDetails) {
        const leftover = document.getElementById(thinkingId);
        if (leftover) leftover.remove();

        if (activeThinkingDiv && activeThinkingDiv.classList.contains('streaming')) {
            activeThinkingDiv.classList.remove('streaming');
        }
        if (activeThinkingDetails) {
            const summary = activeThinkingDetails.querySelector('summary');
            if (summary) summary.innerHTML = `🧠 AI 深度推理链 (分析完毕)`;
        }
    };
})();
