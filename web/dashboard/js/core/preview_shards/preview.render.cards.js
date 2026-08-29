/**
 * ⚡ [V100.9] Illacme Plenipes Preview UI Renderers & Component Cards
 * 职责：
 * 1. 渲染 4 步流光步骤条工具栏 DOM；
 * 2. 渲染新手友好发布预览向导说明卡片 DOM；
 * 3. 渲染发布预览成果看板卡片 DOM。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
 */

// 渲染 4 步流光步骤条工具栏
window.renderPreviewStepperToolbar = function () {
    return `
        <div class="preview-stepper-bar">
            <div class="step-item" id="step-prev-1"><span class="step-icon">🔍</span> <span class="step-name">1. 原稿预检</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-prev-2"><span class="step-icon">✍️</span> <span class="step-name">2. 智能排版</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-prev-3"><span class="step-icon">🎨</span> <span class="step-name">3. 站点装配</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-prev-4"><span class="step-icon">🚀</span> <span class="step-name">4. 开启预览</span></div>
        </div>
    `;
};

// 渲染新手友好向导说明卡片 (阶段 1)
window.renderPreviewIntroCard = function (activeTheme) {
    return `
        <div class="preview-intro-card" style="padding: 12px 14px; line-height: 1.6; color: var(--text-bright);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid var(--glass-border); padding-bottom: 8px;">
                <div style="font-size: 0.95rem; font-weight: 700; color: var(--neon-cyan); display: flex; align-items: center; gap: 8px;">
                    <span>💡</span> 「发布预览」工作流向导
                </div>
                <span class="version-tag tiny" style="background: rgba(0, 240, 255, 0.1); color: var(--neon-cyan); border: 1px solid rgba(0, 240, 255, 0.3);">装帧主题: ${activeTheme}</span>
            </div>
            
            <div style="font-size: 0.82rem; color: #ccc; margin-bottom: 14px;">
                系统将在您的设备本地快速完成原稿排版与站点装配，让您在正式全网发布前<b>完整体验最终上线效果</b>。
            </div>

            <div class="preview-step-cards-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">🔍 1. 原稿预检</div>
                    <div style="color: #888; font-size: 0.76rem;">扫描原稿文库，检查图片、双向链接完整性与合规性。</div>
                </div>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">✍️ 2. 智能排版</div>
                    <div style="color: #888; font-size: 0.76rem;">增量解析 Markdown 正文，快速生成高质感网页文档。</div>
                </div>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">🎨 3. 站点装配</div>
                    <div style="color: #888; font-size: 0.76rem;">自动打包全站导航目录、双链全息图谱与主题外观。</div>
                </div>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">🚀 4. 开启预览</div>
                    <div style="color: #888; font-size: 0.76rem;">启动本地预览服务容器，自动在浏览器新标签页打开。</div>
                </div>
            </div>

            <div style="background: rgba(0, 240, 255, 0.05); border: 1px dashed rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 12px; font-size: 0.76rem; color: #a29bfe; display: flex; flex-direction: column; gap: 4px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span>💡</span> <span><b>装帧编译</b>：本次发布将全量编译并应用所有已保存的<b>装帧参数、语种路由拓扑与主题外观</b>。</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; color: #00ffaa;">
                    <span>🔒</span> <span><b>安全承诺</b>：本地预览全程在您的设备本地极速运行，<b>不会向任何外部平台推流</b>。</span>
                </div>
            </div>
        </div>
    `;
};

// 渲染发布预览成果看板卡片
window.renderPreviewSuccessCard = function (finalUrl, finalPort) {
    return `
        <div style="background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px; padding: 14px 18px; margin: 14px 0 6px 0; line-height: 1.6; box-shadow: 0 0 16px rgba(0, 240, 255, 0.1);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #00ffaa; font-weight: bold; font-size: 0.95rem;">🎉 本地智能排版与装配已就绪！</span>
                <span style="font-size: 0.75rem; color: #00f0ff; background: rgba(0,240,255,0.15); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0,240,255,0.3);">HTTP 200 OK</span>
            </div>
            <div style="color: #ccc; font-size: 0.82rem; margin-bottom: 4px;">✔ <b>原稿合规</b>：已通过资产与双链审计（0 外部推流）</div>
            <div style="color: #ccc; font-size: 0.82rem; margin-bottom: 12px;">✔ <b>预览服务</b>：<a id="preview-site-link" href="${finalUrl}" target="_blank" style="color: #00f0ff; text-decoration: underline; font-weight: bold;">${finalUrl}</a> (端口 <span id="preview-site-port">${finalPort}</span>)</div>
            <div style="background: rgba(162, 155, 254, 0.08); border: 1px dashed rgba(162, 155, 254, 0.35); border-radius: 6px; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 10px;">
                <div style="font-size: 0.8rem; color: #dfe6e9; line-height: 1.4;">
                    <span style="font-weight: 600; color: #a29bfe;">🏛️ 下一步建议：</span>已熟悉示范站出版流程？准备好将您自己的本地 Markdown 知识文库打造为全球多语种独立网站了吗？
                </div>
                <button onclick="if (typeof window.closeTerminalModal === 'function') window.closeTerminalModal(); if (typeof window.showImprintWizard === 'function') window.showImprintWizard();" style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); color: #fff; border: none; border-radius: 6px; padding: 7px 14px; font-size: 0.8rem; font-weight: 600; cursor: pointer; white-space: nowrap; box-shadow: 0 2px 10px rgba(108, 92, 231, 0.35); transition: all 0.2s; flex-shrink: 0;">
                    ✨ 开启专属品牌创建向导 →
                </button>
            </div>
        </div>
    `;
};
