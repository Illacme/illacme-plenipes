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

window.ThemeUI = {
    /**
     * 🏗️ 渲染主题画廊
     */
    renderThemesGallery(themes, activeTheme) {
        const normalizedActive = (activeTheme === 'default' || !activeTheme) ? 'sovereign' : activeTheme;
        themes.sort((a, b) => (normalizedActive === a.id ? -1 : (normalizedActive === b.id ? 1 : 0)));

        return `
            <div class="full-width">
                <div class="settings-group">
                    <div class="card-gallery">
                    ${themes.length > 0 ? themes.map(t => {
            const isActive = normalizedActive === t.id;
            const iconMap = { 'starlight': '🌟', 'docusaurus': '🦖', 'sovereign': '👑', 'default': '👑', 'vitepress': '⚡', 'nextra': '📖', 'universal': '🌐', 'hexo': '🎨', 'hugo': '🐹' };
            const icon = iconMap[t.id] || (t.origin === 'core' ? '🎨' : '🧩');

            let statusLabelPill = "";
            let actionButton = "";
            const location = t.location || 'native';

            const locationMap = { 'native': '主题官方库', 'global': '主题中心库', 'local': '当前版图库' };
            const locationText = locationMap[location] || location;

            if (isActive) {
                statusLabelPill = `<div class="log-tag success" style="background: hsla(152, 100%, 50%, 0.08); color: var(--neon-green, #00ff88); border: 1px solid hsla(152, 100%, 50%, 0.2); font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px;">🟢 当前选用</div>`;
                actionButton = '<button class="action-btn active" style="height: 28px; line-height: 18px;" disabled>已就绪</button>';
            } else {
                statusLabelPill = `<div class="log-tag info" style="background: hsla(183, 100%, 50%, 0.08); color: var(--accent-secondary); border: 1px solid hsla(183, 100%, 50%, 0.2); font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px;">🔘 ${locationText}</div>`;
                if (location === 'native') {
                    actionButton = `<button class="action-btn glow-btn" style="height: 28px; line-height: 18px;" onclick="window.ThemeHandlers.bootstrapTheme('${t.id}')">⚡ 下载并切换</button>`;
                } else if (location === 'global') {
                    actionButton = `<button class="action-btn glow-btn" style="height: 28px; line-height: 18px;" onclick="window.ThemeHandlers.switchTheme('${t.id}')">🎬 同步并切换</button>`;
                } else {
                    actionButton = `<button class="action-btn glow-btn" style="height: 28px; line-height: 18px;" onclick="window.ThemeHandlers.switchTheme('${t.id}')">🎬 切换主题</button>`;
                }
            }

            const dotColor = t.is_enabled ? 'healthy' : 'blocked';
            const previewImage = t.preview_image || t.cover || t.preview || '';
            const mockupInner = (window.getThemeVerticalMockupContent ? window.getThemeVerticalMockupContent(t.id) : '');

            const previewHtml = previewImage
                ? `<img src="${previewImage}" alt="${t.id}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 6px; transition: transform 0.4s ease;" class="theme-preview-img" />`
                : `<div class="mock-browser-window" style="width: 100%; height: 100%; border-radius: 6px; overflow: hidden; display: flex; flex-direction: column; border: 1px solid rgba(255, 255, 255, 0.12); box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
                                <div class="browser-header-bar" style="height: 16px; background: #222225; border-bottom: 1px solid #333; display: flex; align-items: center; padding: 0 6px; gap: 4px; flex-shrink: 0; z-index: 2;">
                                    <span style="width: 6px; height: 6px; border-radius: 50%; background: #ff5f56; display: inline-block;"></span>
                                    <span style="width: 6px; height: 6px; border-radius: 50%; background: #ffbd2e; display: inline-block;"></span>
                                    <span style="width: 6px; height: 6px; border-radius: 50%; background: #27c93f; display: inline-block;"></span>
                                    <span style="margin-left: 6px; font-size: 7.5px; color: #aaa; font-family: monospace;">https://${t.id}.illacme.internal</span>
                                </div>
                                <div class="browser-body-viewport" style="flex: 1; overflow: hidden; position: relative;">
                                    ${mockupInner}
                                </div>
                              </div>`;

            return `
                            <div class="shield-pod plugin-pod ${isActive ? 'active-duty' : ''}" style="display: flex; gap: 16px; align-items: center; padding: 16px 18px;">
                                <!-- 👈 左侧精细 140px 高度自成体系区域 (顶平 RELEASE，底平 CONFIG 按钮，绝无空隙死角) -->
                                <div class="shield-main-content" style="flex: 1; min-width: 0; height: 140px; display: flex; flex-direction: column; justify-content: space-between;">
                                    <div>
                                        <div class="shield-status" style="margin-bottom: 4px;">
                                            <div style="display:flex; align-items:center; gap:10px;">
                                                <span class="status-dot-mini ${dotColor}" id="dot-${t.id}"></span>
                                                <span class="shield-id">RELEASE ${t.version || 'V1.0'}</span>
                                            </div>
                                            ${statusLabelPill}
                                        </div>

                                        <div style="display: flex; gap: 10px; align-items: flex-start; margin-top: 2px;">
                                            <div class="card-icon" style="font-size: 1.4rem; flex-shrink: 0; margin-top: 1px;">${icon}</div>
                                            <div style="flex: 1; min-width: 0;">
                                                <h4 style="font-size: 1.05rem; color: var(--text-bright, #ffffff); margin: 0 0 2px 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                                    <span style="font-weight: 700; letter-spacing: 0.2px;">${window.getThemeDisplayName(t.id)}</span>
                                                    ${t.name && t.name.toLowerCase() !== (t.id || '').toLowerCase() && t.name !== window.getThemeDisplayName(t.id) ? `<span style="font-size: 0.65rem; font-weight: normal; color: var(--accent-secondary); background: hsla(183, 100%, 50%, 0.08); border: 1px solid hsla(183, 100%, 50%, 0.15); padding: 1px 6px; border-radius: 4px;">${t.name}</span>` : ''}
                                                </h4>
                                                <p style="margin: 0; font-size: 0.73rem; color: var(--text-dim); line-height: 1.3; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${t.description || '自定义装帧主题'}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="pod-telemetry" style="margin: 2px 0; padding: 3px 10px; display: flex; align-items: center; font-size: 0.65rem; height: 24px; flex-shrink: 0;">
                                        ${isActive
                    ? '<span class="tiny-label" style="color:var(--neon-green, #00ff88); display:flex; align-items:center; gap:6px; font-weight:700;"><span class="heartbeat-indicator pulsing" style="background:var(--neon-green, #00ff88); width:6px; height:6px;"></span>🟢 当前版图已绑定</span>'
                    : (location === 'local'
                        ? '<span class="tiny-label" style="color:var(--accent-secondary); font-weight:700;">🔘 本地就绪：可直接切换</span>'
                        : (location === 'global'
                            ? '<span class="tiny-label" style="color:var(--neon-amber, #ffb300); font-weight:700;">⚠️ 需同步：请点击同步并切换</span>'
                            : '<span class="tiny-label" style="color:var(--neon-amber, #ffb300); font-weight:700;">⚠️ 需下载：请点击下载并切换</span>'))}
                                    </div>

                                    <div class="p-control-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; flex-shrink: 0;">
                                        ${actionButton}
                                        <button class="action-btn secondary" style="height: 28px; line-height: 18px;" onclick="window.openPluginConfig('${t.id}', 'theme', 'governance')" ${(!t.is_enabled || location !== 'local') ? 'disabled' : ''} title="${!t.is_enabled ? '主题已被禁用' : (location === 'local' ? '自定义配置此主题的细节属性' : '请先部署或切换此主题为当前版图主题，启用后即可配置属性')}">⚙️ CONFIG</button>
                                    </div>
                                </div>

                                <!-- 👉 右侧精致 Preview 预览视窗 (精确 160px × 140px，顶端平齐 RELEASE，底端平齐 CONFIG 按钮；默认展示上半部分，Hover 自动向上滑屏) -->
                                ${isActive ? `
                                    <div class="theme-preview-container card-right-preview active-preview" style="width: 160px; height: 140px; flex-shrink: 0; position: relative; cursor: pointer; overflow: hidden; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 1px solid rgba(0,255,136,0.3); display: flex; flex-direction: column;" onclick="window.open('http://localhost:' + (window.settingsData?.system?.serve_port || 43213), '_blank')" title="🟢 当前生效主题：点击新标签页直接打开本地网页预览 (http://localhost:${window.settingsData?.system?.serve_port || 43213})">
                                        <style>
                                            .theme-preview-container:hover .vertical-page-mockup {
                                                transform: translateY(-50%);
                                            }
                                        </style>
                                        ${previewHtml}
                                    </div>
                                ` : `
                                    <div class="theme-preview-container card-right-preview disabled-preview" style="width: 160px; height: 140px; flex-shrink: 0; position: relative; cursor: default; overflow: hidden; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); display: flex; flex-direction: column;" title="${t.id} 尚未激活为当前版图主题（激活后即可直接点击打开本地预览）">
                                        <style>
                                            .theme-preview-container:hover .vertical-page-mockup {
                                                transform: translateY(-50%);
                                            }
                                        </style>
                                        ${previewHtml}
                                    </div>
                                `}
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
