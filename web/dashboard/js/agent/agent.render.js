/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) UI Render Layer - SOP Compliant
 * 负责控制面板的 DOM 状态更新、大模型能力标签展示、思维链置灰联动及 SSE 流式字符动画渲染。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.render.js initializing');

    // 🔗 [SOP-02] 解析与寻址辅助逻辑已安全物理拆分至 agent.helper.js，此处配置全局安全代理以防双重污染并缩减行数
    const renderMarkdown = text => (typeof window.renderMarkdown === 'function' ? window.renderMarkdown(text) : text);

    window.SovereignAgent = window.SovereignAgent || {};

    window.SovereignAgent.render = {
        /**
         * 🆕 动态刷新控制面板的大模型徽章状态、悬停提示及思维链开关/深度的置灰联动
         * @param {Object} data 大模型元数据
         */
        updateCapabilities(data) {
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
                if (active) {
                    el.classList.remove('disabled');
                    el.classList.add('active');
                    if (badgeTooltips[id]) el.title = badgeTooltips[id].active;
                } else {
                    el.classList.remove('active');
                    el.classList.add('disabled');
                    if (badgeTooltips[id]) el.title = badgeTooltips[id].disabled;
                }
            };

            updateBadge('badge-cot', data.capabilities.cot);
            updateBadge('badge-tools', data.capabilities.tools);
            updateBadge('badge-stream', data.capabilities.stream);
            updateBadge('badge-vision', data.capabilities.vision);

            // 🧠 物理联动对齐：当大模型不支持原生思维链时，强制置灰禁用开关和深度，防止误操作
            const rToggle = document.getElementById('agent-reasoning-toggle'), rDepthContainer = document.getElementById('agent-reasoning-depth-container');
            if (rToggle && rDepthContainer) {
                const switchLabel = rToggle.closest('.setting-item');
                if (data.capabilities.cot) {
                    rToggle.disabled = false;
                    rToggle.checked = true;
                    if (switchLabel) {
                        switchLabel.style.opacity = '1';
                        switchLabel.style.pointerEvents = 'auto';
                    }
                    rDepthContainer.style.opacity = '1';
                    rDepthContainer.style.pointerEvents = 'auto';
                } else {
                    rToggle.disabled = true;
                    rToggle.checked = false;
                    if (switchLabel) {
                        switchLabel.style.opacity = '0.4';
                        switchLabel.style.pointerEvents = 'none';
                    }
                    rDepthContainer.style.opacity = '0.4';
                    rDepthContainer.style.pointerEvents = 'none';
                }
            }
        },

        /**
         * ⚙️ 显示大模型元数据获取失败的“未就绪”状态
         */
        showNotReadyState() {
            const modelNameTag = document.getElementById('active-model-name');
            if (modelNameTag) {
                modelNameTag.textContent = '未就绪';
            }
        },

        /**
         * 向控制面板的 feed 容器追加特定样式的消息
         * @param {string} text 
         * @param {string} typeClass 
         */
        appendMessage(text, typeClass) {
            const agentFeed = document.getElementById('agent-feed');
            if (!agentFeed) return;
            const msgDiv = document.createElement('div');
            msgDiv.className = `agent-msg ${typeClass}`;
            msgDiv.innerHTML = renderMarkdown(text);
            agentFeed.appendChild(msgDiv);
            agentFeed.scrollTop = agentFeed.scrollHeight;
        },

        /**
         * 渲染 SSE 流式打字机动画
         * @param {Response} response API 的 fetch Response
         * @param {string} thinkingId 等待动画容器 ID
         * @param {Function} onStreamEvent 其他类型事件的回调函数
         * @returns {Promise<Object>} 返回生成块的 DOM 引用供清理使用
         */
        async renderStream(response, thinkingId, onStreamEvent) {
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
                                    activeThinkingDiv.innerHTML = `<details open><summary><span class="thinking-badge-pulse"></span>🧠 脑网思维链 (深度分析中...)</summary><div class="thinking-content"></div></details>`;
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
                                        if (summary) summary.innerHTML = `🧠 脑网思维链 (分析完毕)`;
                                    }
                                    if (!activeContentDiv) {
                                        activeContentDiv = document.createElement('div');
                                        activeContentDiv.className = 'agent-msg final-msg';
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

            return { activeThinkingDiv, activeThinkingDetails };
        },

        /**
         * ⚙️ SSE 交互结束后对思维链等挂起 DOM 块执行物理打扫与状态合拢
         */
        cleanupStream(thinkingId, activeThinkingDiv, activeThinkingDetails) {
            const leftover = document.getElementById(thinkingId);
            if (leftover) leftover.remove();

            if (activeThinkingDiv && activeThinkingDiv.classList.contains('streaming')) {
                activeThinkingDiv.classList.remove('streaming');
            }
            if (activeThinkingDetails) {
                const summary = activeThinkingDetails.querySelector('summary');
                if (summary) summary.innerHTML = `🧠 脑网思维链 (分析完毕)`;
            }
        }
    };
})();
