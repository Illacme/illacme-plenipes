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
                el.classList.toggle('active', !!active);
                el.classList.toggle('disabled', !active);
                if (badgeTooltips[id]) el.title = active ? badgeTooltips[id].active : badgeTooltips[id].disabled;
            };

            ['cot', 'tools', 'stream', 'vision'].forEach(k => updateBadge(`badge-${k}`, data.capabilities[k]));

            // 🧠 物理联动对齐：当大模型不支持原生思维链时，强制置灰禁用开关和深度，防止误操作
            const rToggle = document.getElementById('agent-reasoning-toggle'), rDepthContainer = document.getElementById('agent-reasoning-depth-container');
            if (rToggle && rDepthContainer) {
                const switchLabel = rToggle.closest('.setting-item'), hasCot = !!data.capabilities.cot;
                rToggle.disabled = !hasCot; rToggle.checked = hasCot;
                const op = hasCot ? '1' : '0.4', pe = hasCot ? 'auto' : 'none';
                if (switchLabel) { switchLabel.style.opacity = op; switchLabel.style.pointerEvents = pe; }
                rDepthContainer.style.opacity = op; rDepthContainer.style.pointerEvents = pe;
            }
        },

        /**
         * ⚙️ 显示大模型元数据获取失败的“未就绪”状态
         */
        showNotReadyState() {
            const el = document.getElementById('active-model-name'), s = document.getElementById('agent-status-tag');
            if (el) el.textContent = '未就绪';
            if (s) {
                s.textContent = '🔴 离线';
                s.style.color = 'var(--neon-red, #ff4d4d)';
                s.style.borderColor = 'hsla(0, 100%, 65%, 0.4)';
                s.style.textShadow = '0 0 6px hsla(0, 100%, 65%, 0.4)';
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
         * 🛠️ 动态渲染微创补丁 Visual Diff 对照卡片与撤销物理按钮 (V76.8)
         * @param {Object} data 包含 patch_id, relative_path, search_content, replace_content, message 的数据包
         */
        renderPatchDiff(data) {
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
                if (summary) summary.innerHTML = `🧠 AI 深度推理链 (分析完毕)`;
            }
        }
    };
})();
