/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) HITL Layer - SOP Compliant
 * 负责人类在环 (HITL) 授权模态对话框的生命周期状态扭转与用户审批决策收集。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.hitl.js initializing');

    window.SovereignAgent = window.SovereignAgent || {};

    let currentHitlId = null;
    let onDecisionSubmit = null;

    window.SovereignAgent.hitl = {
        /**
         * 🛡️ 初始化并绑定 HITL 弹窗按钮事件，与主控制流程对齐
         * @param {Function} onDecision 决策提交时的回调，签名: async (hitlId, decision) => {}
         */
        init(onDecision) {
            const hitlDialog = document.getElementById('agent-hitl-dialog');
            if (!hitlDialog) return;

            onDecisionSubmit = onDecision;

            const hitlCloseBtn = document.getElementById('hitl-close-btn');
            if (hitlCloseBtn) {
                hitlCloseBtn.addEventListener('click', () => this.closeDialog());
            }

            const hitlApproveBtn = document.getElementById('hitl-approve-btn');
            if (hitlApproveBtn) {
                hitlApproveBtn.addEventListener('click', () => this.submitHitlDecision('approve'));
            }

            const hitlRejectBtn = document.getElementById('hitl-reject-btn');
            if (hitlRejectBtn) {
                hitlRejectBtn.addEventListener('click', () => this.submitHitlDecision('reject'));
            }
        },

        /**
         * ⚠️ 拉起人类在环决策授权弹窗，并展示对应的 Tool 与 arguments 参数
         * @param {Object} data 挂起事件的数据载荷
         */
        showDialog(data) {
            const hitlDialog = document.getElementById('agent-hitl-dialog');
            if (!hitlDialog) return;

            currentHitlId = data.hitl_id;

            const hitlToolName = document.getElementById('hitl-tool-name');
            if (hitlToolName) hitlToolName.textContent = data.tool;

            const hitlToolArgs = document.getElementById('hitl-tool-args');
            if (hitlToolArgs) {
                hitlToolArgs.textContent = JSON.stringify(data.args, null, 2);
            }

            hitlDialog.showModal();
        },

        /**
         * ⚙️ 关闭模态对话框
         */
        closeDialog() {
            const hitlDialog = document.getElementById('agent-hitl-dialog');
            if (hitlDialog) {
                hitlDialog.close();
            }
            currentHitlId = null;
        },

        /**
         * 收集并提交人类做出的物理授权或否决决策，回调给主装配层
         * @param {string} decision 决策结果 ('approve' | 'reject')
         */
        async submitHitlDecision(decision) {
            if (!currentHitlId) return;
            const hitlId = currentHitlId;
            this.closeDialog();
            if (onDecisionSubmit) {
                await onDecisionSubmit(hitlId, decision);
            }
        }
    };
})();
