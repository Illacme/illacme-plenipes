/**
 * 🎨 Illacme Themes - UI Rendering Shard
 * 职责：负责装帧主题画廊的渲染、卡片状态映射与视觉对齐。
 */

const THEME_DISPLAY_NAMES = {
    'sovereign': 'Sovereign',
    'default': 'Sovereign',
    'docusaurus': 'Docusaurus',
    'starlight': 'Starlight',
    'vitepress': 'VitePress',
    'nextra': 'Nextra',
    'universal': 'Universal',
    'hexo': 'Hexo',
    'hugo': 'Hugo'
};

window.getThemeDisplayName = (id) => {
    if (!id) return '';
    const key = String(id).toLowerCase();
    return THEME_DISPLAY_NAMES[key] || (id.charAt(0).toUpperCase() + id.slice(1));
};

// 🏛️ 官方装帧母本确定性空间排布权重 (Cognitive Ladder: 旗舰 ➔ 通用 ➔ 主流 ➔ 前沿)
const THEME_ORDER_WEIGHTS = {
    'sovereign': 10,
    'default': 10,
    'universal': 20,
    'vitepress': 30,
    'nextra': 40,
    'docusaurus': 50,
    'starlight': 60
};

window.ThemeUI = {
    /**
     * 🏗️ 渲染主题画廊 (位置绝对确定，空间记忆永不跳跃)
     */
    renderThemesGallery(themes, activeTheme) {
        const normalizedActive = (activeTheme === 'default' || !activeTheme) ? 'sovereign' : activeTheme;

        // 确定性稳定排序：按母本梯队权重排序，第三方主题排在其后按名称排序
        const orderedThemes = [...themes].sort((a, b) => {
            const wa = THEME_ORDER_WEIGHTS[a.id] || (a.origin === 'core' ? 80 : 100);
            const wb = THEME_ORDER_WEIGHTS[b.id] || (b.origin === 'core' ? 80 : 100);
            if (wa !== wb) return wa - wb;
            return (a.name || a.id).localeCompare(b.name || b.id);
        });

        return `
            <div class="full-width">
                <div class="settings-group" style="margin-top: 2px;">
                    <div class="card-gallery theme-card-gallery">
                    ${orderedThemes.length > 0 ? orderedThemes.map(t => {
            const isActive = normalizedActive === t.id;
            const iconMap = { 'starlight': '🌟', 'docusaurus': '🦖', 'sovereign': '👑', 'default': '👑', 'vitepress': '⚡', 'nextra': '📖', 'universal': '🌐', 'hexo': '🎨', 'hugo': '🐹' };
            const icon = iconMap[t.id] || (t.origin === 'core' ? '🎨' : '🧩');

            let actionButton = "";
            const location = t.location || 'native';

            if (isActive) {
                actionButton = `<button class="action-btn glow-btn" style="height: 28px; line-height: 18px; white-space: nowrap; padding: 0 14px; background: linear-gradient(135deg, #059669 0%, #0d9488 100%); border-color: #10b981; color: #ffffff; box-shadow: 0 2px 10px rgba(5, 150, 105, 0.35);" onclick="if(typeof window.openPreviewSite === 'function'){ window.openPreviewSite(); } else { window.open('http://localhost:' + (window.settingsData?.system?.serve_port || 43213) + '/?t=' + Date.now(), '_blank'); }">🌐 实时站点预览</button>`;
            } else {
                if (location === 'native' || location === 'global') {
                    actionButton = `<button class="action-btn glow-btn" style="height: 28px; line-height: 18px; white-space: nowrap; padding: 0 14px;" onclick="window.ThemeHandlers.bootstrapAndLaunchTheme('${t.id}')">⚡ 部署并启动预览</button>`;
                } else {
                    actionButton = `<button class="action-btn glow-btn" style="height: 28px; line-height: 18px; white-space: nowrap; padding: 0 14px;" onclick="window.ThemeHandlers.switchAndLaunchTheme('${t.id}')">⚡ 切换并启动预览</button>`;
                }
            }

            const dotColor = t.is_enabled ? 'healthy' : 'blocked';
            const previewImage = t.preview_image || t.cover || t.preview || '';
            const mockupInner = (window.getThemeVerticalMockupContent ? window.getThemeVerticalMockupContent(t.id) : '');

            const previewHtml = previewImage
                ? `<img src="${previewImage}" alt="${t.id}" loading="lazy" decoding="async" style="width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; display:block;" class="theme-preview-img" />`
                : `<div class="mock-browser-window" style="width: 100%; height: 100%; display: flex; flex-direction: column;">
                                <div class="browser-header-bar" style="height: 22px; background: rgba(0,0,0,0.45); border-bottom: 1px solid var(--glass-border); display: flex; align-items: center; padding: 0 10px; gap: 5px; flex-shrink: 0; z-index: 2; backdrop-filter: blur(4px);">
                                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #ff5f56; display: inline-block;"></span>
                                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #ffbd2e; display: inline-block;"></span>
                                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #27c93f; display: inline-block;"></span>
                                    <span style="margin-left: 8px; font-size: 8.5px; color: var(--text-dim); font-family: monospace; letter-spacing: 0.2px;">https://${t.id}.illacme.internal</span>
                                </div>
                                <div class="browser-body-viewport" style="flex: 1; overflow: hidden; position: relative;">
                                    ${mockupInner}
                                </div>
                              </div>`;

            return `
                <div class="shield-pod theme-showcase-pod ${isActive ? 'active-duty' : ''}">
                    <!-- 🪟 顶部沉浸式全宽视窗舞台 (全宽展示装帧设计) -->
                    <div class="theme-stage-viewport" 
                         ${isActive ? `onclick="if(typeof window.openPreviewSite === 'function'){ window.openPreviewSite(); } else { window.open('http://localhost:' + (window.settingsData?.system?.serve_port || 43213) + '/?t=' + Date.now(), '_blank'); }"` : ''}
                         title="${isActive ? '🟢 当前生效主题：点击新标签页直接打开本地网页预览' : `${t.id} 尚未激活为当前品牌主题`}">
                        
                        ${isActive ? `
                            <div class="theme-stage-badge">
                                <div class="active-sovereign-tag" style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: 800; font-size: 0.68rem; padding: 4px 10px; border-radius: 6px; box-shadow: 0 4px 14px rgba(5, 150, 105, 0.45); display: flex; align-items: center; gap: 5px; letter-spacing: 0.3px; backdrop-filter: blur(8px);">
                                    <span>👑</span> <span>当前生效主题</span>
                                </div>
                            </div>
                        ` : ''}
                        
                        ${previewHtml}
                    </div>

                    <!-- 📋 底部呼吸感信息控制栏 (信息与按钮 100% 舒展平铺，彻底告别挤压折行) -->
                    <div class="theme-meta-panel">
                        <div class="theme-meta-header">
                            <div class="theme-title-group">
                                <span class="card-icon" style="font-size: 1.35rem; flex-shrink: 0;">${icon}</span>
                                <div>
                                    <h4 style="font-size: 1.05rem; color: var(--text-bright, #ffffff); margin: 0; display: flex; align-items: center; gap: 8px;">
                                        <span style="font-weight: 700;">${window.getThemeDisplayName(t.id)}</span>
                                        ${t.name && t.name.toLowerCase() !== (t.id || '').toLowerCase() && t.name !== window.getThemeDisplayName(t.id) ? `<span style="font-size: 0.65rem; font-weight: normal; color: var(--accent-secondary); background: hsla(183, 100%, 50%, 0.08); border: 1px solid hsla(183, 100%, 50%, 0.15); padding: 1px 6px; border-radius: 4px;">${t.name}</span>` : ''}
                                    </h4>
                                </div>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px; flex-shrink: 0;">
                                <span class="status-dot-mini ${dotColor}" id="dot-${t.id}"></span>
                                <span class="shield-id" style="font-size: 0.68rem; font-family: monospace; color: var(--text-dim);">RELEASE ${t.version || 'V1.0'}</span>
                            </div>
                        </div>

                        <p class="theme-meta-desc">${t.description || '自定义装帧主题'}</p>

                        <div class="theme-control-bar">
                            <div class="theme-telemetry-status">
                                ${isActive
                                    ? '<span class="tiny-label" style="color:var(--neon-green, #00ff88); display:flex; align-items:center; gap:6px; font-weight:800; font-size: 0.74rem;"><span class="heartbeat-indicator pulsing" style="background:var(--neon-green, #00ff88); width:7px; height:7px;"></span>🟢 全站正在使用中</span>'
                                    : (location === 'local'
                                        ? '<span class="tiny-label" style="color:var(--text-muted); font-weight:600; font-size: 0.72rem;">🔘 本地就绪</span>'
                                        : (location === 'global'
                                            ? '<span class="tiny-label" style="color:var(--neon-amber, #ffb300); font-weight:600; font-size: 0.72rem;">⚠️ 需同步</span>'
                                            : '<span class="tiny-label" style="color:var(--neon-amber, #ffb300); font-weight:600; font-size: 0.72rem;">⚠️ 需下载</span>'))}
                            </div>

                            <div class="theme-action-buttons">
                                ${actionButton}
                                <button class="action-btn secondary" style="height: 28px; line-height: 18px; white-space: nowrap; padding: 0 12px;" onclick="window.openPluginConfig('${t.id}', 'theme', 'governance')" ${(!t.is_enabled || location !== 'local') ? 'disabled' : ''} title="${!t.is_enabled ? '主题已被禁用' : (location === 'local' ? '自定义配置此主题的细节属性' : '请先部署或切换此主题为当前品牌主题，启用后即可配置属性')}">⚙️ CONFIG</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('') : `
                        <div class="empty-state" style="grid-column: 1/-1;">
                            <div class="spinner">📡</div>
                            <p>正在同步装帧资产库，请稍候...</p>
                        </div>
                    `}
                </div>
                </div>
            </div>
        `;
    }
};
