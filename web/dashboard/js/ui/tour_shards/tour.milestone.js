/**
 * 🧭 [V82.0] Illacme Plenipes Tour System - Milestone & Copilot Actions Shard
 * 职责：导览完结启航仪式弹窗、Copilot 对话流迎新贺卡注入、原稿文库/遥测控制塔直达与品牌切换引导。
 */

(function () {
    'use strict';

    /**
     * 🤖 触发创作者启航仪式里程碑弹窗并联动唤醒 Copilot 助手
     */
    function _showTourMilestoneAndActivateCopilot() {
        // 1. 展开右侧边栏（若此前折叠）
        var appContainer = document.getElementById('app-container');
        if (appContainer && appContainer.classList.contains('right-collapsed')) {
            appContainer.classList.remove('right-collapsed');
            if (typeof window.syncSidebarToggles === 'function') {
                window.syncSidebarToggles();
            }
        }

        // 2. 向右侧 Copilot 对话流注入迎新贺卡
        var agentFeed = document.getElementById('agent-feed');
        if (agentFeed) {
            var msgDiv = document.createElement('div');
            msgDiv.className = 'agent-msg system-msg tour-milestone-msg';
            msgDiv.style.borderLeft = '3px solid var(--neon-green, #10b981)';
            msgDiv.style.background = 'rgba(16, 185, 129, 0.08)';
            msgDiv.style.padding = '12px 14px';
            msgDiv.style.borderRadius = '10px';
            msgDiv.style.boxShadow = '0 4px 18px rgba(16, 185, 129, 0.15)';
            msgDiv.style.marginTop = '8px';
            msgDiv.style.display = 'flex';
            msgDiv.style.flexDirection = 'column';
            msgDiv.style.gap = '8px';

            msgDiv.innerHTML =
                '<div style="font-weight: 800; color: var(--neon-green, #10b981); font-size: 0.74rem; display: flex; align-items: center; gap: 6px;">' +
                '🎉 创作者漫游导览圆满完成！' +
                '</div>' +
                '<p style="margin: 0; line-height: 1.5; color: var(--text-bright); font-size: 0.69rem;">' +
                '恭喜您已全面熟悉独立数字出版系统的核心流程！我是您的专属 AI 协作者 <b>Sovereign Copilot</b>，已全面就绪为您服务。' +
                '</p>' +
                '<div style="display: flex; flex-direction: column; gap: 6px; font-size: 0.66rem; margin-top: 4px;">' +
                '<span style="font-weight: 700; color: var(--accent-secondary); font-size: 0.68rem;">🚀 推荐第一步操作（点击直接打开对应窗口）：</span>' +
                '<div class="tour-copilot-actions-grid" style="display: flex; flex-direction: column; gap: 6px;">' +
                '<button class="tour-copilot-action-btn action-vault" onclick="event.stopPropagation(); window._tourOpenVaultLibrary()" style="text-align: left; background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.28); color: var(--neon-purple); padding: 7px 10px; border-radius: 6px; font-size: 0.66rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: space-between; font-weight: 600;" title="打开示范品牌「创作者指南」原稿文库，浏览 30+ 篇示例原稿">' +
                '<span>📂 浏览示范品牌「创作者指南」原稿</span>' +
                '<span style="opacity: 0.7; font-size: 0.6rem; background: rgba(168, 85, 247, 0.15); padding: 2px 6px; border-radius: 4px;">浏览文库 ↗</span>' +
                '</button>' +
                '<button class="tour-copilot-action-btn action-tower" onclick="event.stopPropagation(); window._tourOpenSystemTelemetry()" style="text-align: left; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.28); color: var(--neon-green); padding: 7px 10px; border-radius: 6px; font-size: 0.66rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: space-between; font-weight: 600;">' +
                '<span>🗼 检查系统微服务与运行负载</span>' +
                '<span style="opacity: 0.7; font-size: 0.6rem; background: rgba(16, 185, 129, 0.15); padding: 2px 6px; border-radius: 4px;">打开遥测 ↗</span>' +
                '</button>' +
                '<button class="tour-copilot-action-btn action-preview" onclick="event.stopPropagation(); window._tourTriggerPreviewFromCopilot()" style="text-align: left; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.28); color: var(--accent-secondary); padding: 7px 10px; border-radius: 6px; font-size: 0.66rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: space-between; font-weight: 600;">' +
                '<span>⚡ 立即体验发布预览 (本地编译与网页渲染)</span>' +
                '<span style="opacity: 0.7; font-size: 0.6rem; background: rgba(0, 242, 255, 0.15); padding: 2px 6px; border-radius: 4px;">启动服务 ↗</span>' +
                '</button>' +
                '</div>' +
                '</div>';

            agentFeed.appendChild(msgDiv);
            agentFeed.scrollTop = agentFeed.scrollHeight;
        }

        // 3. Copilot 输入框微动效唤醒
        var agentInput = document.getElementById('agent-command-input') || document.getElementById('agent-input');
        if (agentInput) {
            agentInput.placeholder = '输入指令，如“开始构建”或“文库检查”...';
            agentInput.classList.add('pulse-glow');
            setTimeout(function () {
                agentInput.classList.remove('pulse-glow');
            }, 2500);
        }

        // 4. SweetAlert2 创作者启航仪式里程碑弹窗（产品专家级：超紧凑尺寸 · 3栏横向微卡片）
        if (window.Swal) {
            var isLight = document.documentElement.getAttribute('data-theme') === 'light';
            window.Swal.fire({
                html:
                    '<div class="tour-milestone-compact-panel">' +
                        '<div class="milestone-badge-wrap">' +
                            '<span class="milestone-badge">🎉 漫游导览达成</span>' +
                        '</div>' +
                        '<h3 class="milestone-compact-title">出版发行工作台已就绪</h3>' +
                        '<p class="milestone-compact-lead">核心骨架已全盘掌握，随时开启高效的多语种数字出版：</p>' +
                        '<div class="milestone-tri-cards">' +
                            '<div class="tri-card">' +
                                '<div class="tri-icon">🏷️</div>' +
                                '<div class="tri-text">' +
                                    '<b>多品牌管理</b>' +
                                    '<span>独立装帧，算力复用，无缝切换工作空间</span>' +
                                '</div>' +
                            '</div>' +
                            '<div class="tri-card">' +
                                '<div class="tri-icon">⚡</div>' +
                                '<div class="tri-text">' +
                                    '<b>全渠道发行</b>' +
                                    '<span>网站网页、社媒平台、电子书多端同步</span>' +
                                '</div>' +
                            '</div>' +
                            '<div class="tri-card">' +
                                '<div class="tri-icon">🤖</div>' +
                                '<div class="tri-text">' +
                                    '<b>AI 协同助手</b>' +
                                    '<span>文库创作辅助、答疑、排查与操作指引</span>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                        '<div class="milestone-compact-hint">' +
                            '<span>💡 建议先点击<b>「体验发布预览」</b>，感受网页即刻生成的效果</span>' +
                        '</div>' +
                    '</div>',
                confirmButtonText: '⚡ 立即体验发布预览',
                showCancelButton: true,
                cancelButtonText: '🚀 开始自主探索',
                buttonsStyling: false,
                customClass: {
                    popup: 'tour-milestone-swal-popup ' + (isLight ? 'theme-light' : 'theme-dark'),
                    confirmButton: 'tour-swal-btn-confirm',
                    cancelButton: 'tour-swal-btn-cancel',
                    actions: 'tour-swal-actions'
                }
            }).then(function (result) {
                if (result.isConfirmed) {
                    window._tourTriggerPreviewFromCopilot();
                }
            });
        }
    }
    window._showTourMilestoneAndActivateCopilot = _showTourMilestoneAndActivateCopilot;

    /**
     * ⚡ 从 Copilot 或里程碑弹窗触发本地发布预览
     */
    window._tourTriggerPreviewFromCopilot = function () {
        if (typeof window.triggerPublishAndPreview === 'function') {
            window.triggerPublishAndPreview();
        } else if (typeof window.triggerPreview === 'function') {
            window.triggerPreview();
        } else if (typeof window.showToast === 'function') {
            window.showToast('⚡ 正在启动本地预览服务...', 'info');
        }
    };

    /**
     * 🚀 向 Sovereign Copilot 发送快捷指令（带功能窗口智能直达与兜底路由）
     */
    window._tourSendCopilotPrompt = function (promptText) {
        if (!promptText) return;

        // 🛡️ 物理直达守卫：如果指令是检索示范品牌原稿或打开文库，直接物理打开示范品牌【原稿文库】窗口
        if (promptText.indexOf('创作者指南') !== -1 || promptText.indexOf('原稿') !== -1 || promptText.indexOf('文库') !== -1) {
            window._tourOpenVaultLibrary();
            return;
        }

        // 🛡️ 物理直达守卫：如果指令是检查微服务或系统负载，直接物理打开【实时系统遥测】控制塔
        if (promptText.indexOf('微服务') !== -1 || promptText.indexOf('负载') !== -1 || promptText.indexOf('遥测') !== -1 || promptText.indexOf('系统状态') !== -1) {
            window._tourOpenSystemTelemetry();
            return;
        }

        var input = document.getElementById('agent-command-input') || document.getElementById('agent-input');
        if (input) {
            input.value = promptText;
            input.focus();
        }
        if (typeof window.sendAgentMessage === 'function') {
            window.sendAgentMessage(promptText);
        } else {
            var sendBtn = document.getElementById('agent-send-btn');
            if (sendBtn) sendBtn.click();
        }
    };

    /**
     * 📂 打开示范品牌「创作者指南」的原稿文库窗口（展示全量文稿列表，供创作者纯净浏览）
     */
    window._tourOpenVaultLibrary = function () {
        // 1. 物理切换至原稿文库视图
        if (typeof window.showView === 'function') {
            window.showView('vault');
        }

        // 2. 清空搜索框历史残留，展示示范品牌的完整原稿列表（30+ 篇），严禁强行激活聚焦搜索框
        setTimeout(function () {
            var searchInput = document.getElementById('vault-search');
            if (searchInput) {
                searchInput.value = ''; // 保持空检索，展示全部原稿
                // 🛡️ 纯净浏览体验：确保不抢占激活焦点，解除可能存在的光标聚焦
                if (document.activeElement === searchInput) {
                    searchInput.blur();
                }
            }
            if (typeof window.loadVault === 'function') {
                window.loadVault('', 1);
            }
        }, 150);

        if (typeof window.showToast === 'function') {
            window.showToast('📂 已为您打开示范品牌「创作者指南」原稿文库', 'success');
        }
        if (typeof window.addAudit === 'function') {
            window.addAudit('📂 导航直达：已打开示范品牌「创作者指南」原稿文库，展示全量原稿列表。', 'info');
        }
    };
    window._tourOpenVaultSearch = window._tourOpenVaultLibrary; // 兼容别名

    /**
     * 🗼 打开【实时系统遥测】控制塔功能窗口
     */
    window._tourOpenSystemTelemetry = function () {
        if (typeof window.showView === 'function') {
            window.showView('tower');
        }
        if (typeof window.showToast === 'function') {
            window.showToast('🗼 已为您打开【实时系统遥测】控制塔', 'success');
        }
        if (typeof window.addAudit === 'function') {
            window.addAudit('🗼 导航直达：已打开实时系统遥测控制塔查看微服务与运行负载。', 'info');
        }
    };

    window._tourAlertSwitchBrand = function () {
        if (typeof window.showToast === 'function') {
            window.showToast('↖️ 请先点击左上角【出版品牌 ▾】下拉列表，切换至「创作者指南」', 'warning');
        } else if (typeof window.addAudit === 'function') {
            window.addAudit('⚠️ 请先在左上角【出版品牌 ▾】下拉列表中切换至「创作者指南」，再继续工作台漫游。', 'warning');
        }
        var tooltipEl = window._tourTooltipEl || document.querySelector('.tour-tooltip-card');
        if (tooltipEl) {
            tooltipEl.classList.remove('tour-shake');
            void tooltipEl.offsetWidth;
            tooltipEl.classList.add('tour-shake');
        }
        var spotlightEl = window._tourSpotlightEl || document.querySelector('.tour-spotlight-box');
        if (spotlightEl) {
            spotlightEl.classList.remove('attention');
            void spotlightEl.offsetWidth;
            spotlightEl.classList.add('attention');
        }
    };

    window._tourOpenImprintDropdown = function () {
        var trigger = document.getElementById('imprint-selector-trigger');
        if (trigger) {
            trigger.click();
        } else if (typeof window.toggleImprintDropdown === 'function') {
            window.toggleImprintDropdown();
        }
        var spotlightEl = window._tourSpotlightEl || document.querySelector('.tour-spotlight-box');
        if (spotlightEl) {
            spotlightEl.classList.remove('attention');
            void spotlightEl.offsetWidth;
            spotlightEl.classList.add('attention');
        }
    };

})();
