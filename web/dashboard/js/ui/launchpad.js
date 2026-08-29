/**
 * 🚀 [V80.0] Illacme Plenipes - 出版工作台 (Launchpad) 智能控制器
 * 职责：判断用户状态（首次启动 vs 日常使用），动态渲染
 *        「首次引导向导」或「智能仪表盘」两种工作台模式。
 * 核心原则：零新轮子——所有操作入口 100% 调用已有全局函数。
 */

// ══════════════════════════════════════════════════════
// 🧭 模式判断 & 总入口
// ══════════════════════════════════════════════════════

/**
 * 每次打开出版工作台时调用，自动判断进入哪种模式。
 */
window.initLaunchpad = async function () {
    const area = document.getElementById('hub-dynamic-area');
    if (!area) return;

    // 先用缓存的 context 快速渲染，避免白屏闪烁
    let ctx = window.governanceContext;

    // 如果没有缓存，静默拉取（失败时降级为 dashboard 模式）
    if (!ctx) {
        try {
            ctx = await apiFetch('/api/system/context');
            window.governanceContext = ctx;
        } catch (e) {
            console.warn('[Launchpad] context fetch failed, using dashboard fallback.', e);
        }
    }

    const imprints = window.settingsData?._imprints || [];
    const onboardingRequired = !!(ctx?.onboarding_required) || imprints.length === 0;

    if (onboardingRequired) {
        _renderOnboarding(area, ctx);
    } else {
        _renderDashboard(area, ctx);
    }
};

// ══════════════════════════════════════════════════════
// 🎓 模式 A：首次启动引导向导 (Onboarding)
// ══════════════════════════════════════════════════════

/**
 * 计算当前向导应高亮哪一步（基于创作者真实心智链路：文库 -> 品牌 -> 算力）。
 * 返回 1 / 2 / 3。
 */
function _calcOnboardingStep(ctx) {
    const hasVault = !!(ctx?.vault?.root);
    if (!hasVault) return 1;

    const imprints = (window.settingsData && window.settingsData._imprints) || [];
    const hasCustomImprint = imprints.some(function(imp) { return imp.id && imp.id !== 'default'; });
    if (!hasCustomImprint) return 2;

    const hasAI = ctx && ctx.ai && ctx.ai.status !== 'offline' && ctx.ai.status !== 'degraded';
    if (!hasAI) return 3;

    return 3;
}

/**
 * 渲染首次启动双轨引导向导 (Dual-Track Onboarding)。
 * 提供「极速体验官方示例」与「创建专属品牌 3 步流水线」双分支。
 */
function _renderOnboarding(area, ctx) {
    const steps = [
        {
            icon: '📂',
            num: 1,
            label: '关联原稿文库',
            desc: '选择本地 Obsidian / Typora 笔记目录，智能扫描并建立内容账本。'
        },
        {
            icon: '🏛️',
            num: 2,
            label: '品牌名称与装帧',
            desc: '命名专属出版社，挑选 Universal / Docusaurus 等精美主题版式。'
        },
        {
            icon: '🤖',
            num: 3,
            label: '算力底座与分发',
            desc: '接入 AI 大模型，开启多语言全自动翻译与全网托管渠道。'
        }
    ];

    const stepListHtml = steps.map(function(s) {
        return (
            '<div class="lpwiz-step-item">' +
                '<div class="lpwiz-step-num">' + s.num + '</div>' +
                '<div class="lpwiz-step-info">' +
                    '<div class="lpwiz-step-name">' + s.icon + ' ' + s.label + '</div>' +
                    '<div class="lpwiz-step-desc">' + s.desc + '</div>' +
                '</div>' +
            '</div>'
        );
    }).join('');

    area.innerHTML =
        '<div class="lpwiz-container">' +
            '<div class="lpwiz-welcome">' +
                '<div class="lpwiz-welcome-badge">🎉 欢迎开启您的本地化全球出版发行之旅</div>' +
                '<p class="lpwiz-welcome-text">系统已为您预置官方示范品牌<strong>「Illacme Press 创作者指南」</strong>，您可以选择<strong>零门槛极速体验</strong>，或<strong>创建专属品牌</strong>开启本地文档全域分发：</p>' +
            '</div>' +
            '<div class="lpwiz-dual-track">' +
                '<!-- 轨道 A: 极速体验官方示例 -->' +
                '<div class="lpwiz-track-card sample-track">' +
                    '<div class="lpwiz-track-header">' +
                        '<div class="lpwiz-track-badge sample">⚡ 极速体验 · 0门槛</div>' +
                        '<h3 class="lpwiz-track-title">体验创作者指南工作台</h3>' +
                        '<p class="lpwiz-track-desc">无需任何外部配置，直接使用预置文库与官方主题模板，感受从原稿到全球站点的全自动化出版发行流程：</p>' +
                    '</div>' +
                    '<div class="lpwiz-track-features">' +
                        '<div class="lpwiz-feature-item"><span>📖</span> 预置 32 篇多语种创作指南示范原稿（中英双语）</div>' +
                        '<div class="lpwiz-feature-item"><span>🎭</span> 官方 Sovereign 旗舰装帧主题与全套排版组件</div>' +
                        '<div class="lpwiz-feature-item"><span>⚡</span> 完整贯通原稿、AI 翻译、装帧到全域托管分发链</div>' +
                    '</div>' +
                    '<div class="lpwiz-track-actions">' +
                        '<button class="lpwiz-btn sample-preview-btn" onclick="window.toggleHub(\'hide\'); if (typeof window.startDashboardTour === \'function\') { window.startDashboardTour(); } else if (typeof window.triggerPreview === \'function\') { window.triggerPreview(); } else { window.triggerPublishAndPreview(); }">🧭 开启工作台功能导览与发布预览 →</button>' +
                    '</div>' +
                '</div>' +
                '<!-- 轨道 B: 实战定制专属品牌 -->' +
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
            '<div class="lpwiz-footer-note">' +
                '已完成配置？<a href="#" onclick="event.preventDefault(); window.governanceContext=null; window.initLaunchpad();" style="color: var(--accent-secondary);">点击刷新检测</a> · ' +
                '<a href="#" onclick="event.preventDefault(); window.toggleHub(\'hide\');" style="color: var(--text-dim);">稍后再说，先去探索主界面</a>' +
            '</div>' +
        '</div>';
}

// ══════════════════════════════════════════════════════
// 📊 模式 B：日常智能仪表盘 (Dashboard)
// ══════════════════════════════════════════════════════

function _renderDashboard(area, ctx) {
    var statsHtml   = _buildStatsStrip(ctx);
    var pipeHtml    = _buildPipelineRow();
    var suggestHtml = _buildSuggestions(ctx);
    var actionsHtml = _buildQuickActions();

    area.innerHTML =
        '<div class="lpdash-container">' +
            statsHtml +
            '<div class="lpdash-grid-split">' +
                '<div class="lpdash-col-diag">' +
                    pipeHtml +
                    suggestHtml +
                '</div>' +
                '<div class="lpdash-col-actions">' +
                    actionsHtml +
                '</div>' +
            '</div>' +
        '</div>';
}

function _buildStatsStrip(ctx) {
    var imprints  = (window.settingsData && window.settingsData._imprints) || [];
    var docCount  = (ctx && ctx.vault && typeof ctx.vault.doc_count === 'number') ? ctx.vault.doc_count : 0;
    var langCount = (ctx && ctx.i18n && Array.isArray(ctx.i18n.targets)) ? ctx.i18n.targets.length : 0;
    var activeId  = (window.settingsData && window.settingsData._active_imprint) || 'default';
    var syncDone  = localStorage.getItem('sync_completed_' + activeId) === 'true' || localStorage.getItem('sync_completed') === 'true';

    var stats = [
        { icon: '📄', value: docCount,          label: '篇原稿',  tip: '已扫描到的 Markdown 文稿总数' },
        { icon: '🏛️', value: imprints.length,   label: '个品牌',  tip: '已创建的品牌出版容器数量' },
        { icon: '🌍', value: langCount,          label: '目标语种', tip: '配置的多语言翻译目标数量（0 = 仅母语出版）' },
        { icon: syncDone ? '✅' : '📡', value: syncDone ? '已同步' : '待同步', label: '发布状态', tip: syncDone ? '当前内容已全量发布' : '有内容尚未完成发布同步' }
    ];

    return '<div class="lpdash-stats-strip">' +
        stats.map(function(s) {
            return '<div class="lpdash-stat-item" title="' + s.tip + '">' +
                '<span class="lpdash-stat-icon">' + s.icon + '</span>' +
                '<span class="lpdash-stat-value">' + s.value + '</span>' +
                '<span class="lpdash-stat-label">' + s.label + '</span>' +
                '</div>';
        }).join('') +
        '</div>';
}

function _buildPipelineRow() {
    var cache = {};
    try {
        var raw = sessionStorage.getItem('_illacme_pipe_cache');
        if (raw) cache = JSON.parse(raw);
    } catch (_) {}

    var nodes = [
        { key: 'vault',       icon: '📂', label: '原稿' },
        { key: 'i18n',        icon: '🌍', label: '翻译' },
        { key: 'theme',       icon: '🎭', label: '主题' },
        { key: 'routing',     icon: '🧭', label: '网址' },
        { key: 'hosting',     icon: '🌐', label: '托管' },
        { key: 'syndication', icon: '📡', label: '分发' }
    ];

    function dotClass(className) {
        if (!className) return 'lpdot-unknown';
        if (className.indexOf('healthy') !== -1)  return 'lpdot-healthy';
        if (className.indexOf('warning') !== -1)  return 'lpdot-warning';
        if (className.indexOf('offline') !== -1)  return 'lpdot-offline';
        if (className.indexOf('standby') !== -1)  return 'lpdot-standby';
        return 'lpdot-unknown';
    }

    var nodesHtml = nodes.map(function(n, i) {
        var nodeData = cache[n.key] || {};
        var statusClass = dotClass(nodeData.dot || '');
        return '<div class="lpdash-pipe-node">' +
            '<span class="lpdash-pipe-icon">' + n.icon + '</span>' +
            '<span class="lpdash-pipe-dot ' + statusClass + '"></span>' +
            '<span class="lpdash-pipe-label">' + n.label + '</span>' +
            (i < nodes.length - 1 ? '<span class="lpdash-pipe-arrow">›</span>' : '') +
            '</div>';
    }).join('');

    return '<div class="lpdash-pipeline-wrap">' +
        '<div class="lpdash-pipeline-title">📊 出版流水线状态 — 共 6 个关键环节</div>' +
        '<div class="lpdash-pipeline-row">' + nodesHtml + '</div>' +
        '</div>';
}

function _buildSuggestions(ctx) {
    var suggestions = [];
    var activeId = (window.settingsData && window.settingsData._active_imprint) || 'default';
    var syncDone = localStorage.getItem('sync_completed_' + activeId) === 'true' || localStorage.getItem('sync_completed') === 'true';

    var cache = {};
    try {
        var raw = sessionStorage.getItem('_illacme_pipe_cache');
        if (raw) cache = JSON.parse(raw);
    } catch (_) {}

    function isOffline(key) { return (cache[key] && cache[key].dot || '').indexOf('offline') !== -1; }

    // 优先级 1: AI 算力未就绪
    if ((ctx && ctx.ai_status === 'offline') || isOffline('i18n')) {
        suggestions.push({
            icon: '🤖',
            title: '接入 AI 大模型',
            desc: '系统暂时以纯规则模式运行，无法进行自动翻译和智能 SEO 优化。接入 DeepSeek / OpenAI 等大模型后，可一键实现全语种自动出版。',
            btn: '前往配置算力',
            action: "window.toggleHub('hide'); window.showView('compute');"
        });
    }

    // 优先级 2: 文库未配置
    if (!(ctx && ctx.vault && ctx.vault.root) || isOffline('vault')) {
        suggestions.push({
            icon: '📂',
            title: '绑定您的稿件文库',
            desc: '请指定存放 Markdown 笔记的文件夹路径，系统将自动扫描并建立出版管道。支持 Obsidian、Typora、VS Code 等工具的文件。',
            btn: '前往绑定文库',
            action: "window.toggleHub('hide'); window.showView('settings', 'general');"
        });
    }

    // 优先级 3: 无托管渠道
    if (isOffline('hosting') && suggestions.length < 2) {
        suggestions.push({
            icon: '🌐',
            title: '开启独立站托管',
            desc: '配置 GitHub Pages、Vercel 等托管平台后，系统可自动将网站上传到云端，全世界的读者都能通过域名访问您的内容。',
            btn: '前往开启托管',
            action: "window.toggleHub('hide'); window.showView('plugins', 'publisher');"
        });
    }

    // 优先级 4: 有待发布内容
    var docCount = (ctx && ctx.vault && ctx.vault.doc_count) || 0;
    if (!syncDone && docCount > 0 && suggestions.length < 2) {
        suggestions.push({
            icon: '🚀',
            title: '发布您的最新内容',
            desc: '检测到文库中有内容尚未完成全域发布同步。启动出版流水线后，系统自动处理翻译、构建和分发，全程无需手动干预。',
            btn: '立即一键发布',
            action: "window.toggleHub('hide'); window.triggerPublish();"
        });
    }

    // 全绿庆祝状态
    if (suggestions.length === 0) {
        return '<div class="lpdash-celebrate">' +
            '<span class="lpdash-celebrate-icon">🎉</span>' +
            '<div class="lpdash-celebrate-text">' +
                '<strong>全链路就绪，运转正常！</strong><br>' +
                '您的出版社所有流水线节点均处于健康状态，内容正在持续分发中。' +
            '</div>' +
            '</div>';
    }

    return '<div class="lpdash-suggestions">' +
        '<div class="lpdash-suggest-title">💡 建议您完成以下配置</div>' +
        suggestions.map(function(s) {
            return '<div class="lpdash-suggest-item">' +
                '<span class="lpdash-suggest-icon">' + s.icon + '</span>' +
                '<div class="lpdash-suggest-body">' +
                    '<div class="lpdash-suggest-name">' + s.title + '</div>' +
                    '<div class="lpdash-suggest-desc">' + s.desc + '</div>' +
                '</div>' +
                '<button class="lpdash-suggest-btn" onclick="' + s.action.replace(/"/g, '&quot;') + '">' + s.btn + ' →</button>' +
                '</div>';
        }).join('') +
        '</div>';
}

function _buildQuickActions() {
    var cards = [
        {
            icon: '🌐',
            title: '本地预览',
            desc: '先在本机预览完整网站效果，检查样式与内容后再正式发布。',
            action: "window.toggleHub('hide'); if (typeof window.triggerPreview === 'function') { window.triggerPreview(); } else { window.triggerPublishAndPreview(); }"
        },
        {
            icon: '🚀',
            title: '全域发布',
            desc: '一键启动完整出版流水线：翻译 → 构建 → 托管上传 → 社媒同步。',
            action: "window.toggleHub('hide'); window.triggerPublish();"
        },
        {
            icon: '📦',
            title: '文稿管理',
            desc: '浏览、编辑文库中的所有 Markdown 文稿，查看发布状态与元数据。',
            action: "window.toggleHub('hide'); window.showView('vault');"
        },
        {
            icon: '⚙️',
            title: '系统设置',
            desc: '配置品牌信息、主题风格、翻译语种、分发渠道等核心参数。',
            action: "window.toggleHub('hide'); window.showView('settings');"
        },
        {
            icon: '🧭',
            title: '漫游导览',
            desc: '随时重温工作台 6 步漫游导览，温习各区域功能与快捷交互。',
            action: "window.toggleHub('hide'); if (typeof window.startDashboardTour === 'function') { window.startDashboardTour(); }"
        }
    ];

    return '<div class="lpdash-actions-title">⚡ 快捷操作</div>' +
        '<div class="lpdash-quick-actions">' +
        cards.map(function(c) {
            return '<div class="lpdash-action-card" onclick="' + c.action.replace(/"/g, '&quot;') + '">' +
                '<div class="lpdash-action-icon">' + c.icon + '</div>' +
                '<div class="lpdash-action-body">' +
                    '<h4 class="lpdash-action-title">' + c.title + '</h4>' +
                    '<p class="lpdash-action-desc">' + c.desc + '</p>' +
                '</div>' +
                '</div>';
        }).join('') +
        '</div>';
}
