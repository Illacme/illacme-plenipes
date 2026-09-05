/**
 * 🎓 [V120.0] Illacme Plenipes - Launchpad Onboarding Shard
 * 职责：首次启动双轨引导向导 (Onboarding)
 * 承载功能：
 * 1. 官方示范工程双轨卡片 (32篇中英双语示范手稿、旗舰主题母本、增量翻译极速分发闭环)
 * 2. 实战建站 3 步引导栈 (原稿文库关联、专属品牌创建、AI 算力与托管点火)
 * 3. 示范预览与品牌建站向导无缝唤起流转
 */

/**
 * 渲染首次启动双轨引导向导视图
 */
function _renderOnboarding(area, ctx) {
    var sampleFeatures = [
        {
            icon: '📂',
            name: '官方示范原稿文库',
            desc: '预置 32 篇中英双语创作指南示范原稿，开箱即用体验全套排版语法。'
        },
        {
            icon: '🎨',
            name: 'Sovereign 旗舰装帧',
            desc: '内置官方旗舰主题母本与全套精美排版组件，打造沉浸式私人出版版面。'
        },
        {
            icon: '⚡',
            name: '增量翻译与极速分发',
            desc: '贯通段落块缓存、多语增量翻译、装帧构建到全域托管的完整闭环链条。'
        }
    ];

    var featureListHtml = sampleFeatures.map(function(feat) {
        return '<div class="lpwiz-step-item">' +
            '<div class="lpwiz-step-num sample">' + feat.icon + '</div>' +
            '<div class="lpwiz-step-info">' +
                '<div class="lpwiz-step-name">' + feat.name + '</div>' +
                '<div class="lpwiz-step-desc">' + feat.desc + '</div>' +
            '</div>' +
            '</div>';
    }).join('');

    var steps = [
        {
            num: 1,
            name: '关联原稿文库',
            desc: '指定本地 Markdown 笔记库目录，由系统建立出版资产账本与双链图谱。'
        },
        {
            num: 2,
            name: '创建专属出版品牌',
            desc: '为独立站配置品牌标识、域名、作者合规信息与专属装帧风格。'
        },
        {
            num: 3,
            name: '接入 AI 算力与托管点火',
            desc: '接入大模型开启多语种增量翻译，一键构建并部署至 GitHub Pages / 局域网。'
        }
    ];

    var stepListHtml = steps.map(function(s) {
        return '<div class="lpwiz-step-item">' +
            '<div class="lpwiz-step-num custom">' + s.num + '</div>' +
            '<div class="lpwiz-step-info">' +
                '<div class="lpwiz-step-name">' + s.name + '</div>' +
                '<div class="lpwiz-step-desc">' + s.desc + '</div>' +
            '</div>' +
            '</div>';
    }).join('');

    area.innerHTML =
        '<div class="lpwiz-container">' +
            '<div class="lpwiz-hero-section">' +
                '<h2 class="lpwiz-hero-title">🚀 开启您的数字出版与全球分发之旅</h2>' +
                '<p class="lpwiz-hero-subtitle">从一份 Markdown 文档出发，打造沉浸式私人出版社。请选择适合您当前出版阶段的启航路径：</p>' +
            '</div>' +
            '<div class="lpwiz-dual-track">' +
                '<div class="lpwiz-track-card sample-track">' +
                    '<div class="lpwiz-track-header">' +
                        '<div class="lpwiz-track-badge sample">📖 示范工程 · 即刻启航</div>' +
                        '<h3 class="lpwiz-track-title">体验创作者指南工作台</h3>' +
                        '<p class="lpwiz-track-desc">零配置直接进入系统预置的官方示范出版物，体验完整的数字出版生命周期：</p>' +
                    '</div>' +
                    '<div class="lpwiz-steps-stack">' + featureListHtml + '</div>' +
                    '<div class="lpwiz-track-actions">' +
                        '<button class="lpwiz-btn sample-preview-btn" onclick="window.toggleHub(\'hide\'); if (typeof window.startDashboardTour === \'function\') { window.startDashboardTour(); } else if (typeof window.openPreviewSite === \'function\') { window.openPreviewSite(); } else { window.triggerPublishAndPreview(); }">🧭 开启工作台功能导览与发布预览 →</button>' +
                    '</div>' +
                '</div>' +
                '<div class="lpwiz-track-card custom-track">' +
                    '<div class="lpwiz-track-header">' +
                        '<div class="lpwiz-track-badge custom">🏛️ 实战建站 · 3步发布</div>' +
                        '<h3 class="lpwiz-track-title">创建我的专属出版品牌</h3>' +
                        '<p class="lpwiz-track-desc">开启一站式建站向导，将您的本地 Markdown 文档打造为全球多语种独立网站：</p>' +
                    '</div>' +
                    '<div class="lpwiz-steps-stack">' + stepListHtml + '</div>' +
                    '<div class="lpwiz-track-actions">' +
                        '<button class="lpwiz-btn custom-action-btn glow-action" onclick="if (typeof window.showImprintWizard === \'function\') { window.showImprintWizard(); } else if (typeof window.launchFullImprintWizard === \'function\') { window.launchFullImprintWizard(); }">✨ 开启品牌创建向导 (开始建站) →</button>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
}

// 全局导出，兼容单测沙箱与 Hub
window._renderOnboarding = _renderOnboarding;
