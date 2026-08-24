/**
 * 🛰️ [V105.0] Illacme Plenipes Plugin Editor - Step Focus & Dynamic Scroll Shard
 * 职责：3 步向导点击联动、任务指引 Banner 状态机更新、卡片高光状态切换与精准平滑滚动。
 */

(function () {
    // 🚀 [V105.0] 3 步向导点击联动与任务指引更新算子 (常驻大卡片焦点高亮)
    window.handleWizardStepClick = (stepIdx, pluginId, category, clickedBtn = null) => {
        const drawer = document.getElementById('plugin-drawer') || document;
        const missionBanner = drawer.querySelector('#wiz-mission-banner');

        // 1. 切换视觉 Active 高光状态
        const steps = drawer.querySelectorAll('.wiz-step');
        steps.forEach((st, idx) => {
            if (idx === stepIdx) {
                st.classList.add('active');
                st.style.background = 'rgba(0, 242, 255, 0.18)';
                st.style.color = 'var(--neon-cyan)';
                st.style.border = '1px solid var(--neon-cyan)';
                st.style.fontWeight = '700';
            } else {
                st.classList.remove('active');
                st.style.background = 'rgba(255, 255, 255, 0.04)';
                st.style.color = 'var(--text-dim)';
                st.style.border = '1px solid rgba(255, 255, 255, 0.1)';
                st.style.fontWeight = '500';
            }
        });

        // 2. 获取大卡片节点
        const card0 = drawer.querySelector('#wiz-card-step-0');
        const card1 = drawer.querySelector('#wiz-card-step-1');
        const footerContainer = drawer.querySelector('#p-drawer-footer') || drawer.querySelector('.drawer-footer') || (drawer.querySelector('#btn-save-plugin-cfg')?.parentElement);

        // 重置所有大卡片样式为暗淡未聚焦状态
        if (card0) {
            card0.style.border = '1px dashed rgba(255, 255, 255, 0.15)';
            card0.style.background = 'rgba(255, 255, 255, 0.02)';
            card0.style.boxShadow = 'none';
            const tag = card0.querySelector('.card-status-tag');
            if (tag) tag.style.display = 'none';
            const title = card0.querySelector('span');
            if (title) title.style.color = 'var(--text-dim)';
        }
        if (card1) {
            card1.style.border = '1px dashed rgba(255, 255, 255, 0.15)';
            card1.style.background = 'rgba(255, 255, 255, 0.02)';
            card1.style.boxShadow = 'none';
            const tag = card1.querySelector('.card-status-tag');
            if (tag) tag.style.display = 'none';
            const title = card1.querySelector('span');
            if (title) title.style.color = 'var(--text-dim)';
        }
        if (footerContainer) {
            footerContainer.style.border = '';
            footerContainer.style.outline = '';
            footerContainer.style.boxShadow = '';
            footerContainer.style.background = '';
        }

        // 3. 辅助函数：物理精准滚动至目标大卡片的外框顶部（保留 14px 完美发光边距）
        const scrollToCardTop = (targetCard) => {
            if (!targetCard) return;
            const drawerBody = document.getElementById('p-drawer-body');
            if (drawerBody) {
                const cardRect = targetCard.getBoundingClientRect();
                const bodyRect = drawerBody.getBoundingClientRect();
                const relativeTop = cardRect.top - bodyRect.top;
                const targetScrollTop = drawerBody.scrollTop + relativeTop - 14;
                drawerBody.scrollTo({ top: Math.max(0, targetScrollTop), behavior: 'smooth' });
            } else {
                targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        };

        if (stepIdx === 0) {
            if (missionBanner) {
                missionBanner.innerHTML = '<span>🎯 当前步骤 [1/3]：请在下方【步骤 1 专属卡片】中填写凭据或使用一键复用</span>';
                missionBanner.style.color = '#00ff88';
                missionBanner.style.borderColor = 'rgba(0, 255, 136, 0.3)';
                missionBanner.style.background = 'rgba(0, 255, 136, 0.06)';
            }
            if (card0) {
                card0.style.border = '1.5px solid var(--neon-cyan)';
                card0.style.background = 'rgba(0, 242, 255, 0.05)';
                card0.style.boxShadow = '0 0 25px rgba(0, 242, 255, 0.3)';
                const tag = card0.querySelector('.card-status-tag');
                if (tag) {
                    tag.style.display = 'inline-block';
                    tag.style.background = 'rgba(0, 242, 255, 0.2)';
                    tag.style.color = 'var(--neon-cyan)';
                }
                const title = card0.querySelector('span');
                if (title) title.style.color = 'var(--neon-cyan)';
                const firstInput = card0.querySelector('input');
                if (firstInput) firstInput.focus();
                // 🛡️ 延迟 80ms 覆盖 focus() 触发的浏览器自动滚动，精准对齐卡片顶部
                setTimeout(() => scrollToCardTop(card0), 80);
            }
        } else if (stepIdx === 1) {
            if (missionBanner) {
                const step2Hint = (category || '').toLowerCase() === 'notification'
                    ? '<span>🎯 当前步骤 [2/3]：请在下方配置消息渲染样式、@被提醒人或自定义扩展参数</span>'
                    : '<span>🎯 当前步骤 [2/3]：请在下方【步骤 2 专属卡片】中配置仓库、Bucket或自定义域名等核心参数</span>';
                missionBanner.innerHTML = step2Hint;
                missionBanner.style.color = 'var(--neon-cyan)';
                missionBanner.style.borderColor = 'rgba(0, 242, 255, 0.3)';
                missionBanner.style.background = 'rgba(0, 242, 255, 0.06)';
            }
            if (card1) {
                card1.style.border = '1.5px solid #00ff88';
                card1.style.background = 'rgba(0, 255, 136, 0.05)';
                card1.style.boxShadow = '0 0 25px rgba(0, 255, 136, 0.3)';
                const tag = card1.querySelector('.card-status-tag');
                if (tag) {
                    tag.style.display = 'inline-block';
                    tag.style.background = 'rgba(0, 255, 136, 0.2)';
                    tag.style.color = '#00ff88';
                }
                const title = card1.querySelector('span');
                if (title) title.style.color = '#00ff88';
                const firstInput = card1.querySelector('input');
                if (firstInput) firstInput.focus();
                // 🛡️ 延迟 80ms 覆盖 focus() 触发的浏览器自动滚动，精准将步骤 2 卡片滚至抽屉顶部
                setTimeout(() => scrollToCardTop(card1), 80);
            }
        } else if (stepIdx === 2) {
            if (missionBanner) {
                missionBanner.innerHTML = '<span>🎯 当前步骤 [3/3]：请在底部点击【测试连接】验证物理链路，确认无误后点击【保存配置】</span>';
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
                // 🚀 匹配抽屉最底部圆角 (16px)，呈现完美具有弧度的金黄极光外框
                footerContainer.style.borderRadius = '12px 12px 16px 16px';
                footerContainer.style.border = '1.5px solid #ffb700';
                footerContainer.style.outline = 'none';
                footerContainer.style.boxShadow = '0 0 25px rgba(255, 183, 0, 0.45), inset 0 0 15px rgba(255, 183, 0, 0.15)';
                footerContainer.style.background = 'rgba(255, 183, 0, 0.06)';
            }
        }
    };
})();
