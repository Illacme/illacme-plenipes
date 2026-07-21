/**
 * 🎨 Illacme Themes - UI Rendering Shard
 * 职责：负责装帧主题画廊的渲染、卡片状态映射与视觉对齐。
 */

window.ThemeUI = {
    /**
     * 🏗️ 渲染主题画廊
     */
    renderThemesGallery(themes, activeTheme) {
        themes.sort((a, b) => (activeTheme === a.id ? -1 : (activeTheme === b.id ? 1 : 0)));

        return `
            <div class="full-width">
                <div class="settings-group">
                    <h4>🎨 装帧画廊</h4>
                    <p class="section-desc" style="font-size: 0.8rem; margin-bottom: 15px; opacity: 0.85;">选用符合您站点风格的数字出版视觉装帧主题，系统将自动对正前端物理路径与资产依赖。</p>
                    
                    <div class="card-gallery">
                    ${themes.length > 0 ? themes.map(t => {
                        const isActive = activeTheme === t.id;
                        const iconMap = { 'starlight': '🌟', 'docusaurus': '🦖', 'sovereign': '👑', 'default': '👑', 'vitepress': '⚡', 'nextra': '📖' };
                        const icon = iconMap[t.id] || (t.origin === 'core' ? '🎨' : '🧩');
                        
                        let statusLabelPill = "";
                        let actionButton = "";
                        const location = t.location || 'native';
                        
                        const locationMap = { 'native': '主题官方库', 'global': '主题中心库', 'local': '当前版图库' };
                        const locationText = locationMap[location] || location.toUpperCase();

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

                        // 🚀 [V80.2] 全息状态对齐：展示状态指示灯
                        const dotColor = t.is_enabled ? 'healthy' : 'blocked';

                        return `
                            <div class="shield-pod plugin-pod ${isActive ? 'active-duty' : ''}" style="display: flex; flex-direction: column; height: 100%;">
                                <div class="shield-status" style="margin-bottom: 8px;">
                                    <div style="display:flex; align-items:center; gap:10px;">
                                        <span class="status-dot-mini ${dotColor}" id="dot-${t.id}"></span>
                                        <span class="shield-id">RELEASE ${t.version || 'V1.0'}</span>
                                    </div>
                                    ${statusLabelPill}
                                </div>
                                <div class="shield-body" style="flex:1; display:flex; flex-direction:column; margin-top: 5px;">
                                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                                        <div class="card-icon" style="font-size: 1.5rem; flex-shrink: 0; margin-top: 2px;">${icon}</div>
                                        <div style="flex: 1;">
                                            <h4 style="font-size: 1.1rem; color: var(--text-bright, #ffffff); margin: 0 0 5px 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                                <span>${(t.id || '').toUpperCase()}</span>
                                                ${t.name ? `<span style="font-size: 0.65rem; font-weight: normal; color: var(--accent-secondary); background: hsla(183, 100%, 50%, 0.08); border: 1px solid hsla(183, 100%, 50%, 0.15); padding: 1px 6px; border-radius: 4px;">${t.name}</span>` : ''}
                                            </h4>
                                            <p style="margin: 0; font-size: 0.75rem; color: var(--text-dim); line-height: 1.4;">${t.description || '自定义装帧主题'}</p>
                                        </div>
                                    </div>
                                    
                                    <div class="pod-telemetry" style="margin: 15px 0; padding: 8px 12px; display: flex; align-items: center; font-size: 0.65rem; height: 32px;">
                                        ${isActive 
                                            ? '<span class="tiny-label" style="color:var(--neon-green, #00ff88); display:flex; align-items:center; gap:6px; font-weight:700;"><span class="heartbeat-indicator pulsing" style="background:var(--neon-green, #00ff88); width:6px; height:6px;"></span>🟢 当前版图已绑定</span>' 
                                            : (location === 'local' 
                                                ? '<span class="tiny-label" style="color:var(--accent-secondary); font-weight:700;">🔘 本地就绪：可直接切换</span>' 
                                                : (location === 'global' 
                                                    ? '<span class="tiny-label" style="color:var(--neon-amber, #ffb300); font-weight:700;">⚠️ 需同步：请点击同步并切换</span>' 
                                                    : '<span class="tiny-label" style="color:var(--neon-amber, #ffb300); font-weight:700;">⚠️ 需下载：请点击下载并切换</span>'))}
                                    </div>

                                    <div class="p-control-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: auto; margin-bottom: 8px;">
                                        ${actionButton}
                                        <button class="action-btn secondary" style="height: 28px; line-height: 18px;" onclick="window.openPluginConfig('${t.id}')" ${(!t.is_enabled || location !== 'local') ? 'disabled' : ''} title="${!t.is_enabled ? '主题已被禁用' : (location === 'local' ? '自定义配置此主题的细节属性' : '请先部署或切换此主题为当前版图主题，启用后即可配置属性')}">⚙️ CONFIG</button>
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

                <div class="settings-grid" style="margin-top: 2rem; border-top: 1px solid var(--glass-border); padding-top: 2rem;">
                    <div class="settings-group">
                        <h4>🛠️ 主题治理工具</h4>
                        <p class="section-desc" style="font-size: 0.8rem; margin-bottom: 12px; opacity: 0.85;">执行主题底层物理依赖的安装，并重新生成全局静态资产索引。</p>
                        <div style="display: flex; gap: 10px; margin-top: 1rem;">
                            <button class="secondary-btn" onclick="window.ThemeHandlers.invokeGlobalAction('install')" style="font-size: 0.8rem;">🏗️ 自动安装主题依赖</button>
                            <button class="secondary-btn" onclick="addAudit('📡 正在重新同步并对齐样式与脚本资源索引...')">🎨 重新生成资产索引</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
};
