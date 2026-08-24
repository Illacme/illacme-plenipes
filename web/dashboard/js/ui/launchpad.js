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
 * 计算当前向导应高亮哪一步（基于系统实际配置完成度）。
 * 返回 1 / 2 / 3。
 */
function _calcOnboardingStep(ctx) {
    const hasAI = ctx && ctx.ai && ctx.ai.status !== 'offline' && ctx.ai.status !== 'degraded';
    if (!hasAI) return 1;
    const hasVault = !!(ctx?.vault?.root);
    if (!hasVault) return 2;
    return 3;
}

/**
 * 渲染 3 步引导向导。
 */
function _renderOnboarding(area, ctx) {
    const step = _calcOnboardingStep(ctx);

    const steps = [
        {
            icon: '🤖',
            num: 1,
            label: '配置 AI 算力',
            title: '第一步：接入 AI 大模型',
            desc: '出版工作台的核心能力——自动翻译、SEO 优化、多语言内容分发——都需要一个 AI 大模型来驱动。您可以选择 OpenAI、DeepSeek、Ollama 等主流大模型，只需填入 API Key 即可完成接入。',
            hint: '💡 没有 API Key？进入算力中心后，我们会引导您申请试用资格。',
            btnText: '🤖 前往配置算力底座',
            btnAction: "window.toggleHub('hide'); window.showView('compute');"
        },
        {
            icon: '📂',
            num: 2,
            label: '绑定文库',
            title: '第二步：指定您的稿件存放位置',
            desc: '请告诉系统您的 Markdown 笔记文件存放在哪里（例如 Obsidian 笔记本的根目录）。系统会自动扫描该目录下的所有 .md 文件，并将它们纳入出版管道。',
            hint: '💡 文库路径就是您在电脑上存放文章的文件夹，例如：/Users/yourname/Documents/Notes',
            btnText: '📂 前往绑定文稿文库',
            btnAction: "window.toggleHub('hide'); window.showView('settings', 'general');"
        },
        {
            icon: '🏛️',
            num: 3,
            label: '创建品牌',
            title: '第三步：创建您的第一个出版品牌',
            desc: '「品牌 (Imprint)」是您出版社的品牌容器——每个品牌对应一个独立的网站，拥有自己的主题风格、目标语言和分发渠道。您可以先创建一个默认品牌，后续随时添加更多。',
            hint: '💡 您可以把品牌理解为"一个品牌网站"，例如："我的技术博客"或"公司官方知识库"。',
            btnText: '🏛️ 创建我的第一个品牌',
            btnAction: "if (typeof window.showImprintWizard === 'function') { window.showImprintWizard(); } else if (typeof window.launchFullImprintWizard === 'function') { window.launchFullImprintWizard(); }"
        }
    ];

    const stepIndicator = steps.map(function(s, i) {
        const n = i + 1;
        const isDone = n < step;
        const isActive = n === step;
        return (
            '<div class="lpwiz-step-node' + (isDone ? ' done' : '') + (isActive ? ' active' : '') + '">' +
                '<div class="lpwiz-step-circle">' + (isDone ? '✓' : n) + '</div>' +
                '<span class="lpwiz-step-label">' + s.label + '</span>' +
            '</div>' +
            (i < steps.length - 1 ? '<div class="lpwiz-step-connector' + (isDone ? ' done' : '') + '"></div>' : '')
        );
    }).join('');

    const cur = steps[step - 1];

    area.innerHTML =
        '<div class="lpwiz-container">' +
            '<div class="lpwiz-welcome">' +
                '<p class="lpwiz-welcome-text">欢迎使用全球私人出版社！以下 3 个步骤帮您完成初始化，全程约需 5 分钟。</p>' +
            '</div>' +
            '<div class="lpwiz-steps-track">' + stepIndicator + '</div>' +
            '<div class="lpwiz-panel">' +
                '<div class="lpwiz-panel-icon">' + cur.icon + '</div>' +
                '<div class="lpwiz-panel-body">' +
                    '<h3 class="lpwiz-panel-title">' + cur.title + '</h3>' +
                    '<p class="lpwiz-panel-desc">' + cur.desc + '</p>' +
                    '<div class="lpwiz-panel-hint">' + cur.hint + '</div>' +
                    '<button class="lpwiz-action-btn" onclick="' + cur.btnAction.replace(/"/g, '&quot;') + '">' + cur.btnText + '</button>' +
                '</div>' +
            '</div>' +
            '<div class="lpwiz-footer-note">' +
                '已完成配置？<a href="#" onclick="event.preventDefault(); window.governanceContext=null; window.initLaunchpad();" style="color: var(--accent-secondary);">点击刷新检测</a> · ' +
                '<a href="#" onclick="event.preventDefault(); window.toggleHub(\'hide\');" style="color: var(--text-dim);">稍后再说，先去探索</a>' +
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
            pipeHtml +
            suggestHtml +
            actionsHtml +
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
