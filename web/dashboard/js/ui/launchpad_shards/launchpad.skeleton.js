/**
 * 🏛️ [V120.0] Illacme Plenipes - Launchpad Skeleton & Top Trio Bar Shard
 * 职责：三栏合一顶栏 Trio Bar 骨架构建与公网独立站链接复制中枢
 * 承载功能：
 * 1. 智能品牌名解析 (优先展示中文品牌名，严禁向创作者暴露裸露的底层目录名 'default')
 * 2. 顶栏三栏布局 (左侧品牌徽标、中间双模穿梭胶囊、右侧独立站公网链接)
 * 3. 安全复制线上站点网址 (双轨降级机制，支持非 HTTPS 局域网环境)
 */

/**
 * 安全复制线上站点网址（双轨降级机制，支持非 HTTPS 局域网）。
 */
window.copySiteUrlSafe = function (url) {
    if (!url) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () {
            if (typeof notify === 'function') notify('已复制线上独立站网址！', 'success');
        }).catch(function () {
            _copyFallback(url);
        });
    } else {
        _copyFallback(url);
    }
};

function _copyFallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
        document.execCommand('copy');
        if (typeof notify === 'function') notify('已复制线上独立站网址！', 'success');
    } catch (err) {
        if (typeof notify === 'function') notify('复制失败，请手动复制网址', 'warning');
    }
    document.body.removeChild(ta);
}

/**
 * 构建顶栏右侧独立站直达链接 HTML
 */
function _buildSiteLinkHtml() {
    var rawUrl = (window.settingsData && window.settingsData.compliance && window.settingsData.compliance.site_url) ||
                 (window.settingsData && window.settingsData.site_url) || '';
    var isValid = /^https?:\/\/[a-zA-Z0-9\-\.]+(:\d+)?(\/.*)?$/.test(rawUrl);

    if (isValid) {
        return '<a href="' + rawUrl + '" target="_blank" rel="noopener noreferrer" class="lpdash-site-btn" title="在新标签页中访问您的公网独立站">' +
               '🌐 访问线上独立站 ↗' +
               '</a>' +
               '<button class="lpdash-copy-btn" onclick="window.copySiteUrlSafe(\'' + rawUrl + '\')" title="一键复制独立站公网网址">📋</button>';
    } else {
        return '<button class="lpdash-site-btn unconfigured" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\', \'compliance\');" title="尚未绑定独立公网域名，点击前往出版合规配置">' +
               '🌐 未绑定线上域名 (去配置)' +
               '</button>';
    }
}

/**
 * 刷新外链容器
 */
function _updateSiteLinkContainer() {
    var wrap = document.getElementById('hub-site-link-container');
    if (wrap) wrap.innerHTML = _buildSiteLinkHtml();
}

/**
 * 装配三栏合一顶栏结构与子视图挂载点
 */
function _mountLaunchpadSkeleton(area, initialMode) {
    var imprints = (window.settingsData && window.settingsData._imprints) || [];
    var activeId = (window.settingsData && window.settingsData._active_imprint) || 'default';
    var activeImprint = imprints.find(function (imp) { return imp.id === activeId; });
    var ctx = window.governanceContext;
    var badgeEl = document.getElementById('active-imprint-name');
    var headerName = (badgeEl && badgeEl.innerText && badgeEl.innerText !== 'LOADING...' && badgeEl.innerText !== 'UNKNOWN') ? badgeEl.innerText.trim() : null;

    // 🏷️ 智能品牌名解析：优先取真实中文品牌名，严禁向创作者暴露裸露的底层目录名 'default'
    var activeName = (activeImprint && activeImprint.name && activeImprint.name !== activeId) ? activeImprint.name :
                     (ctx && ctx.imprint_name && ctx.imprint_name !== 'default') ? ctx.imprint_name :
                     (headerName && headerName !== 'default' && headerName !== 'DEFAULT') ? headerName :
                     (window.settingsData && window.settingsData.imprint_name && window.settingsData.imprint_name !== 'default') ? window.settingsData.imprint_name :
                     (activeId === 'default' ? '创作者指南' : activeId);

    var trioHtml =
        '<div class="hub-top-trio-bar">' +
            '<div class="hub-trio-left">' +
                '<span class="hub-brand-badge" title="当前出版品牌 (如需切换请在主界面左上角操作)">' +
                    '🏷️ 当前品牌：<strong>' + activeName + '</strong>' +
                '</span>' +
            '</div>' +
            '<div class="hub-trio-center">' +
                '<div class="hub-mode-capsule">' +
                    '<button class="hub-capsule-btn ' + (initialMode === 'onboarding' ? 'active' : '') + '" data-mode="onboarding" onclick="window.switchLaunchpadMode(\'onboarding\')">🌱 创作者起步</button>' +
                    '<button class="hub-capsule-btn ' + (initialMode === 'dashboard' ? 'active' : '') + '" data-mode="dashboard" onclick="window.switchLaunchpadMode(\'dashboard\')">📊 运行仪表盘</button>' +
                '</div>' +
            '</div>' +
            '<div class="hub-trio-right">' +
                '<div id="hub-site-link-container" class="hub-site-link-wrap" style="' + (initialMode === 'onboarding' ? 'display:none;' : '') + '">' +
                    _buildSiteLinkHtml() +
                '</div>' +
            '</div>' +
        '</div>' +
        '<div id="hub-mode-subview"></div>';

    area.innerHTML = trioHtml;
}

// 全局导出，兼容单测沙箱与 Hub
window._mountLaunchpadSkeleton = _mountLaunchpadSkeleton;
window._buildSiteLinkHtml = _buildSiteLinkHtml;
window._updateSiteLinkContainer = _updateSiteLinkContainer;
