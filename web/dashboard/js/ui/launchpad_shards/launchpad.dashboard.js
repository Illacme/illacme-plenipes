/**
 * 📊 [V120.0] Illacme Plenipes - Launchpad Dashboard View Shard
 * 职责：日常智能仪表盘 (Dashboard) 主视图渲染与核心快捷操作六宫格
 * 承载功能：
 * 1. 四项指标统计条 (稿件篇数、品牌个数、语种数量、同步状态)
 * 2. 核心快捷操作卡片组 (本地预览带端口在线探测、一键全域发布 Primary CTA、文稿管理、装帧主题、系统设置、导览手册)
 * 3. 实时预览服务器状态动态更新指示器 (updateLaunchpadPreviewStatus)
 * 4. 仪表盘双列布局切分与底栏辅助动作
 */

/**
 * 构建四项指标统计条
 */
function _buildStatsStrip(ctx) {
    var imprints  = (window.settingsData && window.settingsData._imprints) || [];
    var docCount  = (ctx && ctx.vault && typeof ctx.vault.doc_count === 'number') ? ctx.vault.doc_count : 0;
    var langCount = (ctx && ctx.i18n && Array.isArray(ctx.i18n.targets)) ? ctx.i18n.targets.length : 0;
    var activeId  = (window.settingsData && window.settingsData._active_imprint) || 'default';
    var syncDone  = localStorage.getItem('sync_completed_' + activeId) === 'true' || localStorage.getItem('sync_completed') === 'true';
    var lastPubTime = localStorage.getItem('_illacme_last_pub_' + activeId) || '今天 15:42';

    var docLabel = docCount === 0 ? '<span style="color: var(--neon-amber);">暂无稿件 (点击放入)</span>' : '篇原稿已就绪';
    var docClick = 'onclick="window.toggleHub(\'hide\'); window.showView(\'vault\');" style="cursor: pointer;"';

    var imprintLabel = imprints.length > 1 ? '多品牌独立管理' : '独立出版品牌';
    var langLabel = langCount > 0 ? '已开启多语翻译' : '单语发布 (未开启翻译)';

    return '<div class="lpdash-stats-strip">' +
        '<div class="lpdash-stat-item ' + (docCount === 0 ? 'warning-empty' : '') + '" ' + docClick + ' title="点击前往原稿文库查看 Markdown 笔记">' +
            '<span class="lpdash-stat-icon">📄</span>' +
            '<span class="lpdash-stat-value">' + docCount + ' <small>篇</small></span>' +
            '<span class="lpdash-stat-label">' + docLabel + '</span>' +
        '</div>' +
        '<div class="lpdash-stat-item" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\', \'imprints\');" style="cursor: pointer;" title="点击前往版图管理，查看或切换出版品牌">' +
            '<span class="lpdash-stat-icon">🏛️</span>' +
            '<span class="lpdash-stat-value">' + imprints.length + ' <small>个</small></span>' +
            '<span class="lpdash-stat-label">' + imprintLabel + '</span>' +
        '</div>' +
        '<div class="lpdash-stat-item" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\', \'localization\');" style="cursor: pointer;" title="点击前往语言翻译治理，配置多语种目标语言">' +
            '<span class="lpdash-stat-icon">🌍</span>' +
            '<span class="lpdash-stat-value">' + langCount + ' <small>语种</small></span>' +
            '<span class="lpdash-stat-label">' + langLabel + '</span>' +
        '</div>' +
        '<div class="lpdash-stat-item ' + (window._isPublishing ? 'is-publishing' : '') + '" onclick="window.toggleHub(\'hide\'); window.showView(\'plugins\', \'publisher\');" style="cursor: pointer;" title="点击前往全网分发渠道查看部署与同步状态">' +
            '<span class="lpdash-stat-icon">' + (window._isPublishing ? '⏳' : (syncDone ? '✅' : '📡')) + '</span>' +
            '<span class="lpdash-stat-value">' + (window._isPublishing ? '发布中' : (syncDone ? '已同步' : '待同步')) + '</span>' +
            '<span class="lpdash-stat-label">上次发布: ' + lastPubTime + '</span>' +
        '</div>' +
    '</div>';
}

/**
 * 实时预览服务器状态指示器
 */
window.updateLaunchpadPreviewStatus = function (matrix) {
    var indicatorEl = document.getElementById('lpdash-preview-status-indicator');
    if (!indicatorEl) return;
    var previewPort = (window.settingsData && window.settingsData.system && window.settingsData.system.serve_port) || 43213;
    var m = matrix || window._healthMatrix;
    var isOnline = false;
    if (m && m.preview) {
        isOnline = (m.preview.status === 'active' || m.preview.status === 'online');
    }
    if (isOnline) {
        indicatorEl.className = 'status-indicator online';
        indicatorEl.innerHTML = '● ' + previewPort + ' 在线';
    } else {
        indicatorEl.className = 'status-indicator offline';
        indicatorEl.innerHTML = '○ 点击拉起';
    }
};

/**
 * 构建核心快捷操作六宫格卡片
 */
function _buildQuickActions() {
    var previewPort = (window.settingsData && window.settingsData.system && window.settingsData.system.serve_port) || 43213;
    var isOnline = false;
    if (window._healthMatrix && window._healthMatrix.preview) {
        isOnline = (window._healthMatrix.preview.status === 'active' || window._healthMatrix.preview.status === 'online');
    }
    var previewStatusDot = isOnline
        ? '<span id="lpdash-preview-status-indicator" class="status-indicator online">● ' + previewPort + ' 在线</span>'
        : '<span id="lpdash-preview-status-indicator" class="status-indicator offline">○ 点击拉起</span>';

    // 智能预览动作：在线时直接打开网页，未拉起时先唤起发布预览点火容器
    var previewClick = 'window.toggleHub(\'hide\'); ' +
        'var m = window._healthMatrix;' +
        'var online = m && m.preview && (m.preview.status === \'active\' || m.preview.status === \'online\');' +
        'if (online && typeof window.openPreviewSite === \'function\') { window.openPreviewSite(); } ' +
        'else if (typeof window.triggerPublishAndPreview === \'function\') { window.triggerPublishAndPreview(); } ' +
        'else if (typeof window.triggerPreview === \'function\') { window.triggerPreview(); } ' +
        'else if (typeof window.openPreviewSite === \'function\') { window.openPreviewSite(); }';

    return '<div class="lpdash-quick-actions">' +
        // [1] 本地极速预览
        '<div class="lpdash-action-card" onclick="' + previewClick + '">' +
            '<span class="lpdash-action-icon">🌐</span>' +
            '<div class="lpdash-action-body">' +
                '<div class="lpdash-action-title">本地预览 ' + previewStatusDot + '</div>' +
                '<p class="lpdash-action-desc">先在本机预览完整网站效果，检查排版后再正式发布。</p>' +
            '</div>' +
        '</div>' +
        // [2] 一键全域发布 (Primary Core CTA 发光高亮)
        '<div class="lpdash-action-card primary-cta" onclick="window.toggleHub(\'hide\'); window.triggerPublish();">' +
            '<span class="lpdash-action-icon pulse-glow">🚀</span>' +
            '<div class="lpdash-action-body">' +
                '<div class="lpdash-action-title">全域发布 <span class="hot-badge">核心</span></div>' +
                '<p class="lpdash-action-desc">一键启动完整出版流水线：翻译、构建、托管与社媒。</p>' +
            '</div>' +
        '</div>' +
        // [3] 原稿文库管理
        '<div class="lpdash-action-card" onclick="window.toggleHub(\'hide\'); window.showView(\'vault\');">' +
            '<span class="lpdash-action-icon">📦</span>' +
            '<div class="lpdash-action-body">' +
                '<div class="lpdash-action-title">文稿管理</div>' +
                '<p class="lpdash-action-desc">浏览编辑文库 Markdown 文稿，管理状态与元数据。</p>' +
            '</div>' +
        '</div>' +
        // [4] Sovereign 旗舰装帧
        '<div class="lpdash-action-card" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\', \'themes\');">' +
            '<span class="lpdash-action-icon">🎭</span>' +
            '<div class="lpdash-action-body">' +
                '<div class="lpdash-action-title">装帧主题</div>' +
                '<p class="lpdash-action-desc">切换 Sovereign / Universal 主题，定制排版组件。</p>' +
            '</div>' +
        '</div>' +
        // [5] 出版合规与治理
        '<div class="lpdash-action-card" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\');">' +
            '<span class="lpdash-action-icon">⚙️</span>' +
            '<div class="lpdash-action-body">' +
                '<div class="lpdash-action-title">系统设置</div>' +
                '<p class="lpdash-action-desc">配置品牌合规、语种矩阵、网址规则与分发渠道。</p>' +
            '</div>' +
        '</div>' +
        // [6] 导览与速查手册 (老创作者全生命周期可用)
        '<div class="lpdash-action-card" onclick="window.toggleHub(\'hide\'); if(typeof window.startDashboardTour===\'function\'){window.startDashboardTour();}">' +
            '<span class="lpdash-action-icon">🧭</span>' +
            '<div class="lpdash-action-body">' +
                '<div class="lpdash-action-title">导览与手册</div>' +
                '<p class="lpdash-action-desc">随时重温 6 步工作台导览，或快速查阅排版规范。</p>' +
            '</div>' +
        '</div>' +
        '</div>';
}

/**
 * 渲染日常智能仪表盘 (Dashboard)
 */
function _renderDashboard(area, ctx) {
    var statsHtml   = _buildStatsStrip(ctx);
    var pipeHtml    = (typeof window._buildPipelineRow === 'function') ? window._buildPipelineRow(ctx) : '';
    var suggestHtml = (typeof window._buildSuggestions === 'function') ? window._buildSuggestions(ctx) : '';
    var actionsHtml = _buildQuickActions();

    var autoOpen = (typeof window.shouldAutoOpenLaunchpad === 'function') ? window.shouldAutoOpenLaunchpad() : true;

    area.innerHTML =
        '<div class="lpdash-container">' +
            statsHtml +
            '<div class="lpdash-grid-split">' +
                '<div class="lpdash-col-diag">' +
                    '<div class="lpdash-section-title">📊 流水线透视与诊断</div>' +
                    '<div class="lpdash-diag-grid">' +
                        pipeHtml +
                        suggestHtml +
                    '</div>' +
                '</div>' +
                '<div class="lpdash-col-actions">' +
                    '<div class="lpdash-section-title">⚡ 核心快捷操作</div>' +
                    actionsHtml +
                '</div>' +
            '</div>' +
            '<div class="lpwiz-footer-note" style="display: flex; justify-content: space-between; align-items: center; padding: 4px 12px; gap: 16px; flex-wrap: wrap;">' +
                '<div style="display: flex; align-items: center; gap: 8px; font-size: 0.76rem;">' +
                    '已在外部完成配置？<a href="#" onclick="event.preventDefault(); window.governanceContext=null; window.initLaunchpad();" style="color: var(--accent-secondary); font-weight: 600;">点击刷新检测</a> · ' +
                    '<a href="#" onclick="event.preventDefault(); window.toggleHub(\'hide\');" style="color: var(--text-dim);">按 Esc 关闭工作台 (快捷键 I 随时唤起)</a>' +
                '</div>' +
                '<label class="lp-auto-open-toggle" style="cursor: pointer; display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; color: var(--text-dim); user-select: none;">' +
                    '<input type="checkbox" class="chk-auto-open-launchpad" onchange="window.setLaunchpadAutoOpenPreference(this.checked)" ' + (autoOpen ? 'checked' : '') + ' style="cursor: pointer; accent-color: var(--accent-secondary, #00f2fe);" />' +
                    '<span>下次进入首页自动展开</span>' +
                '</label>' +
            '</div>' +
        '</div>';
}

// 全局导出，兼容单测沙箱与 Hub
window._renderDashboard = _renderDashboard;
window._buildStatsStrip = _buildStatsStrip;
window._buildQuickActions = _buildQuickActions;
