/**
 * 🚀 [V10.5] Illacme Plenipes Full-Site Publish Stepper & Workflow Driver
 * 职责：
 * 1. 渲染全站发布 4 步流光步骤条工具栏 DOM (原稿预检 -> 智能排版 -> 站点装配 -> 部署上线)；
 * 2. 驱动全站发布 Stepper 步骤状态机（active / completed）；
 * 3. 监听白盒日志并实时推进发布阶段。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

// 渲染 4 步全站发布流光步骤条工具栏
window.renderPublishStepperToolbar = function () {
    return `
        <div class="preview-stepper-bar publish-stepper-bar">
            <div class="step-item active" id="step-pub-1"><span class="step-icon">🔍</span> <span class="step-name">1. 原稿预检</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-pub-2"><span class="step-icon">🌐</span> <span class="step-name">2. 智能排版</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-pub-3"><span class="step-icon">🎨</span> <span class="step-name">3. 站点装配</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-pub-4"><span class="step-icon">🚀</span> <span class="step-name">4. 部署上线</span></div>
        </div>
    `;
};

window._fullSitePublishState = {
    isPublishing: false,
    stage: 0, // 0: 待命, 1: 原稿预检, 2: 智能排版, 3: 站点装配, 4: 部署上线, 5: 发布完成
    stageName: '就绪',
    lastUpdate: 0
};

window.setPublishStage = function (stage, stageName) {
    window._fullSitePublishState.stage = stage;
    window._fullSitePublishState.stageName = stageName;
    window._fullSitePublishState.isPublishing = stage >= 1 && stage <= 4;
    window._fullSitePublishState.lastUpdate = Date.now();

    // 联动刷新指示器徽章与浮层
    if (typeof window.updateDispatchIndicator === 'function') {
        window.updateDispatchIndicator(window._lastDispatchOverview || {});
    }
    if (window._isPopoverOpen && typeof window.renderPopoverContent === 'function') {
        window.renderPopoverContent(window._lastDispatchOverview || {});
    }
};

// 辅助步骤状态切换器
window.setPublishStepState = function (stepNum, state) {
    const el = document.getElementById(`step-pub-${stepNum}`);
    if (!el) return;
    el.classList.remove('active', 'completed');
    if (state === 'active') el.classList.add('active');
    if (state === 'completed') el.classList.add('completed');
};

// 重置全站发布 Stepper
window.resetPublishStepper = function () {
    for (let i = 1; i <= 4; i++) {
        window.setPublishStepState(i, null);
    }
    window.setPublishStepState(1, 'active');
    window.setPublishStage(1, '原稿预检');
};

// 标记全站发布 Stepper 全部完成
window.markAllPublishStepsCompleted = function () {
    for (let i = 1; i <= 4; i++) {
        window.setPublishStepState(i, 'completed');
    }
    window.setPublishStage(5, '发布完成');
};

// 动态日志驱动全站发布步骤条状态推进
window.updatePublishStepperFromLog = function (msg) {
    if (!msg || typeof msg !== 'string') return;
    const modal = document.getElementById('terminal-modal');
    if (!modal || modal.dataset.context !== 'publish') return;

    // 阶段 1 -> 阶段 2：预检完成，开始智能排版与翻译
    if (msg.includes('正在扫描') || msg.includes('合规预检') || msg.includes('主权审计完成') || msg.includes('验证资产完整性') || msg.includes('预检通过')) {
        window.setPublishStepState(1, 'completed');
        window.setPublishStepState(2, 'active');
        window.setPublishStage(2, '智能排版');
    } else if (msg.includes('正在向 AI') || msg.includes('增量解析') || msg.includes('Title Polish') || msg.includes('正在智能排版') || msg.includes('AI 翻译同步') || msg.includes('多语种') || msg.includes('段落') || msg.includes('追踪开始')) {
        window.setPublishStepState(1, 'completed');
        window.setPublishStepState(2, 'active');
        window.setPublishStage(2, '智能排版');
    } else if (msg.includes('DigitalGardenPlugin') || msg.includes('JanitorPlugin') || msg.includes('清道夫') || msg.includes('博客合成器') || msg.includes('双链图谱') || msg.includes('全息关系图谱') || msg.includes('主题钩子') || msg.includes('执行资产合成') || msg.includes('静态发布目录')) {
        window.setPublishStepState(1, 'completed');
        window.setPublishStepState(2, 'completed');
        window.setPublishStepState(3, 'active');
        window.setPublishStage(3, '站点装配');
    } else if (msg.includes('SovereignDeploymentPlugin') || msg.includes('渠道投递') || msg.includes('托管部署') || msg.includes('正在推流') || msg.includes('推送至托管平台') || msg.includes('GitHub Pages') || msg.includes('Vercel') || msg.includes('Netlify') || msg.includes('Cloudflare')) {
        window.setPublishStepState(1, 'completed');
        window.setPublishStepState(2, 'completed');
        window.setPublishStepState(3, 'completed');
        window.setPublishStepState(4, 'active');
        window.setPublishStage(4, '部署上线');
    } else if (msg.includes('全域分发汇总') || msg.includes('DEPLOY_SUMMARY') || msg.includes('所有算力调度已闭环') || msg.includes('全原文库编译与排版已全量闭环') || msg.includes('同步完成') || msg.includes('全息同步流水线圆满完成')) {
        window.markAllPublishStepsCompleted();
    }
};
