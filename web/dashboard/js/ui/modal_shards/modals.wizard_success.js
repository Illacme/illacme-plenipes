/**
 * 🧩 [V1.0] UI Modals - Imprint Wizard Success Shard
 * 职责：承载向导成功就绪确认页组件 (imprint-success-modal & Workbench Handoff)。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.getWizardSuccessModalHTML = () => {
        return `
        <!-- 🏛️ [V75.2] 品牌出版物创建成功就绪确认页组件 (Success Modal & Workbench Handoff) -->
        <div id="imprint-success-modal" class="modal-overlay fade-in" style="display: none; position: fixed; inset: 0; backdrop-filter: blur(12px); z-index: 10000; align-items: center; justify-content: center; padding: 16px;">
            <div class="glass-card modal-content" style="max-width: 620px; width: 92%; border: 1px solid var(--glass-border); border-radius: 12px; padding: 18px 22px; display: flex; flex-direction: column; gap: 12px; animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);">
                
                <!-- 头部庆祝横幅 -->
                <div style="display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <div style="width: 38px; height: 38px; border-radius: 50%; background: rgba(0, 242, 255, 0.12); border: 1px solid var(--accent-secondary); display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
                        🎉
                    </div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.15rem; color: var(--text-bright); font-weight: 700; display: flex; align-items: center; gap: 8px;">
                            <span>出版品牌创建就绪！</span>
                            <span class="tier-tag tier-local" style="font-size: 0.62rem; padding: 1px 6px;">READY</span>
                        </h2>
                        <p style="margin: 2px 0 0 0; font-size: 0.72rem; color: var(--text-dim); line-height: 1.3;">
                            恭喜！您的独立数字出版品牌已全自动初始化完成，核心配置如下：
                        </p>
                    </div>
                </div>

                <!-- 品牌信息完整配置清单 -->
                <div class="wiz-form-card" style="background: var(--card-subtle-bg, rgba(255,255,255,0.02)); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px 14px; display: flex; flex-direction: column; gap: 8px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                        <!-- 品牌标识 -->
                        <div class="wiz-summary-item" style="padding: 8px 10px; border-radius: 6px; border: 1px solid var(--glass-border); background: var(--card-subtle-bg, rgba(0,0,0,0.04));">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🏷️ 出版品牌</div>
                            <div id="succ-imprint-brand" style="font-size: 0.8rem; font-weight: 700; color: var(--accent-secondary);">--</div>
                        </div>
                        <!-- 装帧主题 -->
                        <div class="wiz-summary-item" style="padding: 8px 10px; border-radius: 6px; border: 1px solid var(--glass-border); background: var(--card-subtle-bg, rgba(0,0,0,0.04));">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🎭 装帧主题引擎</div>
                            <div id="succ-imprint-theme" style="font-size: 0.8rem; font-weight: 700; color: var(--accent-primary);">--</div>
                        </div>
                        <!-- 原稿文库物理路径 -->
                        <div class="wiz-summary-item" style="padding: 8px 10px; border-radius: 6px; border: 1px solid var(--glass-border); background: var(--card-subtle-bg, rgba(0,0,0,0.04)); grid-column: 1 / -1;">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">📂 内容文库物理路径</div>
                            <div id="succ-imprint-vault" style="font-size: 0.74rem; font-family: var(--font-mono); color: var(--text-bright); word-break: break-all;">--</div>
                        </div>
                        <!-- 翻译算力底座 (独立展示) -->
                        <div class="wiz-summary-item" style="padding: 8px 10px; border-radius: 6px; border: 1px solid var(--glass-border); background: var(--card-subtle-bg, rgba(0,0,0,0.04));">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🤖 翻译算力底座</div>
                            <div id="succ-imprint-compute" style="font-size: 0.74rem; font-weight: 600; color: var(--text-bright);">--</div>
                        </div>
                        <!-- 首发翻译语种 (独立展示) -->
                        <div class="wiz-summary-item" style="padding: 8px 10px; border-radius: 6px; border: 1px solid var(--glass-border); background: var(--card-subtle-bg, rgba(0,0,0,0.04));">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🌍 首发翻译语种</div>
                            <div id="succ-imprint-lang" style="font-size: 0.74rem; font-weight: 600; color: var(--text-bright);">--</div>
                        </div>
                        <!-- 托管与在线发布 (跨全列，支持本地与云端双行展示) -->
                        <div class="wiz-summary-item" style="padding: 8px 10px; border-radius: 6px; border: 1px solid var(--glass-border); background: var(--card-subtle-bg, rgba(0,0,0,0.04)); grid-column: 1 / -1; display: flex; flex-direction: column; gap: 4px;">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 1px;">🚀 网站托管与分发</div>
                            <div id="succ-imprint-dispatch" style="font-size: 0.72rem; color: var(--text-bright); line-height: 1.45;">--</div>
                        </div>
                    </div>
                </div>

                <!-- 工作台导向选择提示 -->
                <div class="sovereign-memo glass-panel" style="padding: 6px 12px; border-left: 3px solid var(--accent-primary); background: rgba(163, 76, 255, 0.04); border-radius: 6px;">
                    <p style="font-size: 0.7rem; color: var(--text-dim); margin: 0; line-height: 1.35;">
                        💡 <b>工作台导向</b>：您可以立即切换进入新品牌工作台开始创作，也可以返回继续当前工作台体验（稍后随时可在顶栏切换）。
                    </p>
                </div>

                <!-- 底部双向操作按钮 (左右两端对齐) -->
                <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--glass-border); padding-top: 10px; margin-top: 2px;">
                    <button class="secondary-btn" onclick="window.dismissImprintSuccessStay()" style="font-size: 0.78rem; padding: 7px 16px;">
                        ← 返回继续当前工作台
                    </button>
                    <button class="primary-btn glow-btn" onclick="window.dismissImprintSuccessSwitch()" style="font-size: 0.78rem; padding: 7px 18px;">
                        切换到新品牌工作台 →
                    </button>
                </div>
            </div>
        </div>
        `;
    };

})();
