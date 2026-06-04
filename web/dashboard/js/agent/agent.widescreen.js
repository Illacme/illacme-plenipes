/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) Widescreen Engine - SOP Compliant
 * 职责：负责大屏模式（极光视界）的 DOM 挂载、背景氛围遮罩、动态双轨并列分发及还原时序排重。
 * 遵循 SOP-01 核心复杂度红线与 SOP-02 模块拆分协议。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.widescreen.js initializing');

    let messageOrderCounter = 0;

    window.initAgentWidescreen = function(agentPod, agentFeed, widescreenToggleBtn, rightSidebar, settingsPanel, settingsToggleBtn) {
        if (!widescreenToggleBtn || !agentPod || !agentFeed) return;

        let isWidescreen = false;
        let backdropEl = null;

        function exitWidescreen() {
            if (!isWidescreen) return;
            isWidescreen = false;

            // 🚀 恢复原生 appendChild 方法，撤销代理分发器
            if (agentFeed && agentFeed._originalAppendChild) {
                agentFeed.appendChild = agentFeed._originalAppendChild;
                
                const leftCol = document.getElementById('agent-feed-left-col');
                const rightCol = document.getElementById('agent-feed-right-col');
                if (leftCol && rightCol) {
                    const allMsgs = [
                        ...Array.from(leftCol.children),
                        ...Array.from(rightCol.children)
                    ].filter(el => el.id !== 'agent-cot-placeholder');
                    
                    leftCol.remove();
                    rightCol.remove();

                    // 按物理时序标记升序重排，完美重塑扁平时间线
                    allMsgs.sort((a, b) => {
                        const orderA = parseInt(a.getAttribute('data-order') || 0, 10);
                        const orderB = parseInt(b.getAttribute('data-order') || 0, 10);
                        return orderA - orderB;
                    });

                    allMsgs.forEach(msg => {
                        if (msg.classList.contains('system-msg')) {
                            if (msg.classList.contains('welcome-fade-archive')) {
                                msg.classList.remove('welcome-fade-archive');
                                msg.style.display = '';
                            }
                        }
                        agentFeed.appendChild(msg);
                    });
                }
            }
            
            if (agentPod) {
                agentPod.classList.remove('active');
                setTimeout(() => {
                    agentPod.classList.remove('widescreen-mode');
                    if (rightSidebar) {
                        rightSidebar.insertBefore(agentPod, rightSidebar.firstChild);
                    }
                }, 300);
            }
            
            if (widescreenToggleBtn) {
                widescreenToggleBtn.textContent = '⛶';
                widescreenToggleBtn.style.color = '';
                widescreenToggleBtn.style.textShadow = '';
                setTimeout(() => {
                    if (widescreenToggleBtn && !isWidescreen) {
                        widescreenToggleBtn.title = '切换宽屏大屏模式';
                    }
                }, 250);
            }
            
            if (backdropEl) {
                backdropEl.classList.remove('active');
                setTimeout(() => {
                    if (backdropEl && backdropEl.parentNode) {
                        backdropEl.parentNode.removeChild(backdropEl);
                    }
                    backdropEl = null;
                }, 300);
            }
            
            document.body.style.overflow = '';
        }

        function enterWidescreen() {
            if (isWidescreen) return;
            isWidescreen = true;

            if (settingsPanel && settingsPanel.classList.contains('expanded')) {
                settingsPanel.classList.remove('expanded');
                if (settingsToggleBtn) {
                    settingsToggleBtn.style.color = '';
                    settingsToggleBtn.style.textShadow = '';
                }
            }

            backdropEl = document.createElement('div');
            backdropEl.className = 'agent-widescreen-backdrop';
            document.body.appendChild(backdropEl);
            
            backdropEl.getBoundingClientRect();
            backdropEl.classList.add('active');

            if (agentPod) {
                document.body.appendChild(agentPod);
                agentPod.classList.add('widescreen-mode');
                agentPod.getBoundingClientRect();
                agentPod.classList.add('active');
            }

            // 🚀 实装宽屏双轨并列的动态分流代理 (Dispatcher)
            if (agentFeed) {
                let leftCol = document.getElementById('agent-feed-left-col');
                let rightCol = document.getElementById('agent-feed-right-col');
                if (!leftCol) {
                    leftCol = document.createElement('div');
                    leftCol.id = 'agent-feed-left-col';
                    leftCol.className = 'agent-feed-column left-col';
                    
                    rightCol = document.createElement('div');
                    rightCol.id = 'agent-feed-right-col';
                    rightCol.className = 'agent-feed-column right-col';

                    // 📡 注入左侧 AI 深度推理轨空状态占位灯
                    const cotPlaceholder = document.createElement('div');
                    cotPlaceholder.id = 'agent-cot-placeholder';
                    cotPlaceholder.className = 'agent-cot-placeholder-glow';
                    cotPlaceholder.innerHTML = `<span class="pulse-icon">📡</span> AI 深度推理轨已准备就绪，等待指令唤醒...`;

                    const originalChildren = Array.from(agentFeed.children);
                    let hasCot = false;
                    originalChildren.forEach(child => {
                        if (!child.getAttribute('data-order')) {
                            child.setAttribute('data-order', messageOrderCounter++);
                        }
                        const isCot = child.classList.contains('thinking-msg') || child.classList.contains('tool-msg');
                        if (isCot) {
                            hasCot = true;
                            leftCol.appendChild(child);
                        } else {
                            rightCol.appendChild(child);
                        }
                    });

                    if (!hasCot) {
                        leftCol.appendChild(cotPlaceholder);
                    }

                    agentFeed.appendChild(leftCol);
                    agentFeed.appendChild(rightCol);
                }

                const originalAppendChild = agentFeed._originalAppendChild || agentFeed.appendChild;
                agentFeed._originalAppendChild = originalAppendChild;
                
                agentFeed.appendChild = function(child) {
                    if (!child.getAttribute('data-order')) {
                        child.setAttribute('data-order', messageOrderCounter++);
                    }
                    const isCot = child.classList.contains('thinking-msg') || child.classList.contains('tool-msg');

                    // ⚡ 1. 动态淡出左侧占位符
                    const placeholder = document.getElementById('agent-cot-placeholder');
                    if (isCot && placeholder) {
                        placeholder.classList.add('fade-out');
                        setTimeout(() => {
                            if (placeholder.parentNode) {
                                placeholder.parentNode.removeChild(placeholder);
                            }
                        }, 250);
                    }

                    // ⚡ 2. 动态淡出右侧就绪欢迎卡片
                    const welcomeCard = rightCol.querySelector('.system-msg');
                    if (welcomeCard && !child.classList.contains('system-msg')) {
                        welcomeCard.classList.add('welcome-fade-archive');
                        setTimeout(() => {
                            welcomeCard.style.display = 'none';
                        }, 300);
                    }

                    const targetCol = isCot ? leftCol : rightCol;
                    const res = targetCol.appendChild(child);
                    targetCol.scrollTop = targetCol.scrollHeight;
                    return res;
                };
            }

            if (widescreenToggleBtn) {
                widescreenToggleBtn.textContent = '🗗';
                widescreenToggleBtn.style.color = 'var(--accent-secondary)';
                widescreenToggleBtn.style.textShadow = '0 0 8px var(--accent-secondary)';
                setTimeout(() => {
                    if (widescreenToggleBtn && isWidescreen) {
                        widescreenToggleBtn.title = '退出大屏模式';
                    }
                }, 250);
            }

            backdropEl.addEventListener('click', exitWidescreen);
            document.body.style.overflow = 'hidden';
        }

        widescreenToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            widescreenToggleBtn.title = '';
            widescreenToggleBtn.blur();
            
            if (isWidescreen) {
                exitWidescreen();
            } else {
                enterWidescreen();
            }
        });

        // 绑定全局 Esc 按键退出监听
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isWidescreen) {
                exitWidescreen();
            }
        });
    };
})();
