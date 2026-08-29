/**
 * 🛰️ [V108.0] Illacme Plenipes Plugin Editor - Step Focus & Dynamic Scroll Shard
 * 职责：自适应 2~4 步向导点击联动、任务指引 Banner 状态机更新、高级折叠自动展开与终点连通测试保存高亮。
 */

(function () {
    // 🚀 [V108.0] 自适应向导点击联动与任务指引更新算子 (常驻大卡片焦点高亮与精准滚动)
    window.handleWizardStepClick = (stepIdx, pluginId, category, clickedBtn = null) => {
        const drawer = document.getElementById('plugin-drawer') || document;
        const missionBanner = drawer.querySelector('#wiz-mission-banner');
        const steps = window.getPluginWizardSteps ? window.getPluginWizardSteps(pluginId, category) : ['1. 鉴权身份凭据', '2. 目标与扩展', '3. 连通测试与保存'];
        const totalSteps = steps.length;
        const currentStepTitle = steps[stepIdx] || '';

        // 1. 切换 Header 步骤视觉 Active 高光状态
        const stepElements = drawer.querySelectorAll('.wiz-step');
        stepElements.forEach((st, idx) => {
            if (idx === stepIdx) {
                st.classList.add('active');
                st.style.background = '';
                st.style.color = '';
                st.style.border = '';
                st.style.fontWeight = '';
            } else {
                st.classList.remove('active');
                st.style.background = '';
                st.style.color = '';
                st.style.border = '';
                st.style.fontWeight = '';
            }
        });

        // 2. 获取各步骤大卡片与底栏容器节点
        const card0 = drawer.querySelector('#wiz-card-step-0');
        const card1 = drawer.querySelector('#wiz-card-step-1');
        const card2 = drawer.querySelector('#wiz-card-step-2');
        const footerContainer = drawer.querySelector('#p-drawer-footer') || drawer.querySelector('.drawer-footer') || (drawer.querySelector('#btn-save-plugin-cfg')?.parentElement);

        const resetCardStyle = (card) => {
            if (!card) return;
            card.classList.remove('active');
            card.style.border = '';
            card.style.background = '';
            card.style.boxShadow = '';
            const tag = card.querySelector('.card-status-tag');
            if (tag) tag.style.display = 'none';
            const title = card.querySelector('.step-title-text, span');
            if (title) title.style.color = '';
        };

        // 重置所有卡片为暗淡状态
        resetCardStyle(card0);
        resetCardStyle(card1);
        resetCardStyle(card2);

        if (footerContainer) {
            footerContainer.style.border = '';
            footerContainer.style.outline = '';
            footerContainer.style.boxShadow = '';
            footerContainer.style.background = '';
        }

        // 3. 辅助函数：物理精准滚动至目标大卡片的外框顶部（感知 sticky 吸顶向导高度并保留 12px 舒适发光边距）
        const scrollToCardTop = (targetCard) => {
            if (!targetCard) return;
            const drawerBody = document.getElementById('p-drawer-body');
            if (drawerBody) {
                const wizardHeader = drawerBody.querySelector('.plugin-wizard-header');
                const headerHeight = wizardHeader ? wizardHeader.offsetHeight : 0;
                const cardRect = targetCard.getBoundingClientRect();
                const bodyRect = drawerBody.getBoundingClientRect();
                const relativeTop = cardRect.top - bodyRect.top;
                const targetScrollTop = drawerBody.scrollTop + relativeTop - headerHeight - 12;
                drawerBody.scrollTo({ top: Math.max(0, targetScrollTop), behavior: 'smooth' });
            } else {
                targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        };

        const isFinalStep = (stepIdx === totalSteps - 1);

        if (stepIdx === 0) {
            // === 步骤 1：我是谁 (鉴权身份凭据) ===
            if (missionBanner) {
                missionBanner.innerHTML = `<span>🎯 当前步骤 [1/${totalSteps}]：请在下方【步骤 1 专属卡片】中填写凭据或使用一键免密/感应</span>`;
                missionBanner.style.color = '';
                missionBanner.style.borderColor = '';
                missionBanner.style.background = '';
            }
            if (card0) {
                card0.classList.add('active');
                card0.style.border = '';
                card0.style.background = '';
                card0.style.boxShadow = '';
                const tag = card0.querySelector('.card-status-tag');
                if (tag) tag.style.display = 'inline-block';
                const firstInput = card0.querySelector('input, textarea');
                if (firstInput) firstInput.focus();
                setTimeout(() => scrollToCardTop(card0), 60);
            }
        } else if (isFinalStep) {
            // === 最终步：连通测试与保存 ===
            if (missionBanner) {
                missionBanner.innerHTML = `<span>🎯 当前步骤 [${totalSteps}/${totalSteps}]：请在底部点击【测试连接】验证物理链路，确认无误后点击【保存配置】</span>`;
                missionBanner.style.color = '#ffb700';
                missionBanner.style.borderColor = 'rgba(255, 183, 0, 0.3)';
                missionBanner.style.background = 'rgba(255, 183, 0, 0.06)';
            }
            const drawerBody = document.getElementById('p-drawer-body');
            if (drawerBody) {
                drawerBody.scrollTo({ top: drawerBody.scrollHeight, behavior: 'smooth' });
            }
            if (footerContainer) {
                footerContainer.style.transition = 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                footerContainer.style.borderRadius = '12px 12px 16px 16px';
                footerContainer.style.border = '1.5px solid #ffb700';
                footerContainer.style.outline = 'none';
                footerContainer.style.boxShadow = '0 0 25px rgba(255, 183, 0, 0.45), inset 0 0 15px rgba(255, 183, 0, 0.15)';
                footerContainer.style.background = 'rgba(255, 183, 0, 0.06)';
            }
        } else if (stepIdx === 1) {
            // === 步骤 2：目标地址 / 发布偏好 / 事件订阅 ===
            if (missionBanner) {
                missionBanner.innerHTML = `<span>🎯 当前步骤 [2/${totalSteps}]：请在下方【步骤 2 专属卡片】中配置目标路径、偏好或订阅策略</span>`;
                missionBanner.style.color = '';
                missionBanner.style.borderColor = '';
                missionBanner.style.background = '';
            }
            if (card1) {
                card1.classList.add('active');
                card1.style.border = '';
                card1.style.background = '';
                card1.style.boxShadow = '';
                const tag = card1.querySelector('.card-status-tag');
                if (tag) tag.style.display = 'inline-block';

                // 自动展开内部折叠面板
                const internalDetails = card1.querySelector('details');
                if (internalDetails) internalDetails.open = true;

                const firstInput = card1.querySelector('input, select, textarea');
                if (firstInput) firstInput.focus();
                setTimeout(() => scrollToCardTop(card1), 60);
            }
        } else if (stepIdx === 2 && totalSteps === 4) {
            // === 4 步流程中的步骤 3：高级调参 / 静态托管 / 代理 / 事件订阅 ===
            if (missionBanner) {
                missionBanner.innerHTML = `<span>🎯 当前步骤 [3/${totalSteps}]：可选高级调参（默认值可用，如 CNAME/独立代理/前缀/ACL/订阅等）</span>`;
                missionBanner.style.color = '';
                missionBanner.style.borderColor = '';
                missionBanner.style.background = '';
            }
            if (card2) {
                card2.classList.add('active');
                card2.style.border = '';
                card2.style.background = '';
                card2.style.boxShadow = '';
                const tag = card2.querySelector('.card-status-tag');
                if (tag) tag.style.display = 'inline-block';

                // 自动展开内部高级折叠面板
                const internalDetails = card2.querySelector('details');
                if (internalDetails) internalDetails.open = true;

                const firstInput = card2.querySelector('input, select, textarea');
                if (firstInput) firstInput.focus();
                setTimeout(() => scrollToCardTop(card2), 60);
            }
        }
    };
})();
