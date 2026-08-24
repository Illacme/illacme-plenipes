/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) HITL Layer - SOP Compliant
 * 负责人类在环 (HITL) 授权模态对话框的生命周期状态扭转与用户审批决策收集。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.hitl.js initializing');

    window.SovereignAgent = window.SovereignAgent || {};

    let currentHitlId = null;
    let onDecisionSubmit = null;

    function ensureHitlDialogMounted() {
        let hitlDialog = document.getElementById('agent-hitl-dialog');
        if (hitlDialog) return hitlDialog;

        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <dialog id="agent-hitl-dialog" class="glass-dialog alert-dialog hitl-dialog"
                style="z-index: 10000; border: 1px solid var(--neon-amber); padding: 20px; background: rgba(10, 0, 0, 0.9);">
                <div class="dialog-header critical-header"
                    style="color: var(--neon-amber); border-bottom: 1px solid var(--neon-amber); padding-bottom: 10px; margin-bottom: 15px;">
                    <h3 style="margin:0;"><span class="icon">⚠️</span> PHYSICAL AUTHORIZATION REQUIRED</h3>
                </div>
                <div class="dialog-content" style="color: var(--text-bright);">
                    <p><strong>Sovereign Agent</strong> requests permission to execute a destructive physical operation.</p>
                    <div class="hitl-details"
                        style="background: rgba(var(--neon-amber-rgb), 0.1); padding: 15px; border-radius: 4px; margin: 15px 0;">
                        <p style="margin:0 0 10px 0;"><strong>Tool:</strong> <span id="hitl-tool-name"
                                style="color: var(--neon-amber); font-weight: bold;">write_document</span></p>
                        <pre class="hitl-args-box" id="hitl-tool-args"
                            style="background: rgba(0,0,0,0.5); padding: 10px; overflow-x: auto; font-family: var(--font-mono); font-size: 0.8rem; margin:0; border-left: 2px solid var(--neon-amber);"></pre>
                    </div>
                    <p class="warning-text" style="color: var(--text-dim); font-size: 0.9rem;">Are you sure you want to authorize this operation?</p>
                </div>
                <div class="dialog-footer" style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                    <button class="glass-btn btn-danger" id="hitl-reject-btn"
                        style="border-color: var(--neon-amber); color: var(--neon-amber);">OVERRIDE (Reject)</button>
                    <button class="glass-btn btn-success" id="hitl-approve-btn"
                        style="border-color: var(--text-bright); color: var(--text-bright);">AUTHORIZE</button>
                </div>
            </dialog>
        `;
        document.body.appendChild(wrapper.firstElementChild);
        return document.getElementById('agent-hitl-dialog');
    }

    window.SovereignAgent.hitl = {
        /**
         * 🛡️ 初始化并绑定 HITL 弹窗按钮事件，与主控制流程对齐
         * @param {Function} onDecision 决策提交时的回调，签名: async (hitlId, decision) => {}
         */
        init(onDecision) {
            const hitlDialog = ensureHitlDialogMounted();
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
            const hitlDialog = ensureHitlDialogMounted();
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
