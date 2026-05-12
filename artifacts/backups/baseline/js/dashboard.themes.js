/**
 * 🎨 [V57.0] Illacme Plenipes Themes Module
 * 职责：装帧主题渲染、物理自愈与主题切换逻辑。
 */

window.renderThemesCategory = () => {
    // 🚀 [V55.18] 实时感应：每次进入分类都静默探测物理目录变动
    if (!window._isRefreshingThemes) {
        window._isRefreshingThemes = true;
        setTimeout(async () => {
            try {
                if (typeof loadPlugins === 'function') await loadPlugins();
                if (typeof renderSettingsCategory === 'function') {
                    const activeItem = document.querySelector('.s-tab.active');
                    if (activeItem && activeItem.dataset.cat === 'themes') {
                        renderSettingsCategory('themes');
                    }
                }
            } finally {
                window._isRefreshingThemes = false;
            }
        }, 10);
    }

    const allPlugins = window.allPlugins || [];
    const themes = allPlugins.filter(p => p.category === 'theme');
    const activeTheme = window.settingsData.active_theme || 'default';
    themes.sort((a, b) => (activeTheme === a.id ? -1 : (activeTheme === b.id ? 1 : 0)));

    return `
        <div class="full-width">
            <div class="section-header"><h3>🎨 装帧主题 (Binding Themes)</h3></div>
            <p class="section-desc">选择并配置您的数字出版物视觉装帧样式。内核将根据所选主题自动对正物理路径与依赖。</p>
            
            <div class="card-gallery">
                ${themes.length > 0 ? themes.map(t => {
                    const isActive = activeTheme === t.id;
                    const iconMap = { 'starlight': '🌟', 'docusaurus': '🦖', 'sovereign': '🏛️', 'vitepress': '⚡', 'nextra': '📖' };
                    const icon = iconMap[t.id] || (t.origin === 'core' ? '🎨' : '🧩');
                    
                    let statusLabel = "";
                    let actionButton = "";
                    
                    if (isActive) {
                        statusLabel = '<span class="badge active">🟢 当前选用</span>';
                        actionButton = '<button class="action-btn active" disabled>已就绪</button>';
                    } else if (t.location === 'native') {
                        statusLabel = '<span class="badge warning">NATIVE</span>';
                        actionButton = `<button class="action-btn glow-btn" onclick="bootstrapTheme('${t.id}')">🚀 物理初始化</button>`;
                    } else {
                        statusLabel = `<span class="badge info">${t.location.toUpperCase()}</span>`;
                        actionButton = `<button class="action-btn glow-btn" onclick="switchTheme('${t.id}')">🎬 启用装帧</button>`;
                    }

                    return `
                        <div class="theme-card ${isActive ? 'active' : ''}">
                            <div class="card-header">
                                <div class="card-icon">${icon}</div>
                                <div class="card-body">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <h4>${t.id.toUpperCase()}</h4>
                                        ${statusLabel}
                                    </div>
                                    <p>${t.description || '自定义装帧主题'}</p>
                                </div>
                            </div>
                            <div class="card-footer">
                                ${actionButton}
                                <button class="action-btn secondary" onclick="openPluginConfig('${t.id}')" title="主题配置">⚙️</button>
                            </div>
                            <div class="card-meta">
                                <span>ORIGIN: ${t.origin.toUpperCase()}</span>
                                <span class="dot-separator"></span>
                                <span>VER: ${t.version}</span>
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

            <div class="settings-grid" style="margin-top: 2rem; border-top: 1px solid var(--glass-border); padding-top: 2rem;">
                <div class="settings-group">
                    <h4>🛠️ 主题治理工具</h4>
                    <div style="display: flex; gap: 10px; margin-top: 1rem;">
                        <button class="secondary-btn" onclick="invokeServiceAction('install')" style="font-size: 0.8rem;">🏗️ 补全主题依赖 (Physical Install)</button>
                        <button class="secondary-btn" onclick="addAudit('📡 正在触发全量 CSS/JS 重新物理对正...')">🎨 重新生成资产索引</button>
                    </div>
                </div>
            </div>
        </div>
    `;
};

window.switchTheme = async (themeId) => {
    if (typeof addAudit === 'function') addAudit(`🎨 正在执行装帧切换: ${themeId.toUpperCase()}...`);
    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'active_theme': themeId })
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ [装帧对正] 成功切换至主题: ${themeId.toUpperCase()}`, "success");
        window.settingsData.active_theme = themeId;
        if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
        if (typeof refreshGovernanceContext === 'function') await refreshGovernanceContext();
    } else {
        if (typeof addAudit === 'function') addAudit(`🚨 切换失败: ${res ? res.error : '物理链路阻塞'}`, "error");
    }
};

window.bootstrapTheme = async (themeId) => {
    if (typeof addAudit === 'function') addAudit(`🚀 正在启动主题物理自愈 (Bootstrap): ${themeId.toUpperCase()}...`);
    try {
        const res = await apiFetch('/api/themes/bootstrap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'id': themeId })
        });
        if (res && res.status === 'success') {
            if (typeof addAudit === 'function') addAudit(`✅ [物理自愈] 主题 '${themeId.toUpperCase()}' 已成功固化。`, "success");
            if (typeof loadPlugins === 'function') await loadPlugins();
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
        }
    } catch (e) {
        if (typeof addAudit === 'function') addAudit(`🚨 [网络故障] 无法连接至引导服务器: ${e.message}`, "error");
    }
};
