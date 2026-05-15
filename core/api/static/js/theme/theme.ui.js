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
            <div class="full-width fade-in">
                <div class="section-header"><h3>🎨 装帧主题 (Binding Themes)</h3></div>
                <p class="section-desc text-muted mb-4">选择并配置您的数字出版物视觉装帧样式。内核将根据所选主题自动对正物理路径与依赖。</p>
                
                <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                    ${themes.length > 0 ? themes.map(t => this.createThemeCard(t, activeTheme === t.id)).join('') : `
                        <div class="col-12 text-center p-5 text-muted italic">
                            <div class="spinner-border spinner-border-sm me-2"></div>正在同步装帧资产库...
                        </div>
                    `}
                </div>

                <div class="mt-5 pt-4 border-top">
                    <h5 class="mb-3">🛠️ 主题治理工具</h5>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-secondary" onclick="window.ThemeHandlers.invokeGlobalAction('install')">🏗️ 补全主题依赖</button>
                        <button class="btn btn-sm btn-outline-info" onclick="addAudit('📡 正在触发全量资产索引重新对正...')">🎨 重新生成资产索引</button>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 🃏 构造单个主题卡片
     */
    createThemeCard(t, isActive) {
        const iconMap = { 'starlight': '🌟', 'docusaurus': '🦖', 'sovereign': '🏛️', 'vitepress': '⚡', 'nextra': '📖' };
        const icon = iconMap[t.id] || (t.origin === 'core' ? '🎨' : '🧩');
        
        let statusBadge = "";
        let actionBtn = "";
        
        if (isActive) {
            statusBadge = '<span class="badge bg-success">CURRENT</span>';
            actionBtn = '<button class="btn btn-sm btn-success w-100" disabled>已就绪</button>';
        } else if (t.location === 'native') {
            statusBadge = '<span class="badge bg-warning text-dark">NATIVE</span>';
            actionBtn = `<button class="btn btn-sm btn-primary w-100 glow-btn" onclick="window.ThemeHandlers.bootstrapTheme('${t.id}')">🚀 物理初始化</button>`;
        } else {
            const locLabel = (t.location || 'UNKNOWN').toUpperCase();
            statusBadge = `<span class="badge bg-info text-dark">${locLabel}</span>`;
            actionBtn = `<button class="btn btn-sm btn-outline-primary w-100" onclick="window.ThemeHandlers.switchTheme('${t.id}')">🎬 启用装帧</button>`;
        }

        const displayId = (t.id || 'UNKNOWN').toUpperCase();

        return `
            <div class="col">
                <div class="card h-100 glass-panel theme-card ${isActive ? 'active-border' : ''}">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="fs-2 me-3">${icon}</div>
                            <div>
                                <h6 class="card-title mb-0">${displayId}</h6>
                                ${statusBadge}
                            </div>
                        </div>
                        <p class="card-text small text-muted">${t.description || '自定义装帧主题'}</p>
                    </div>
                    <div class="card-footer bg-transparent border-0 pt-0 pb-3">
                        <div class="d-flex gap-2">
                            ${actionBtn}
                            <button class="btn btn-sm btn-outline-secondary" onclick="openPluginConfig('${t.id}')" title="主题配置">⚙️</button>
                        </div>
                    </div>
                    <div class="card-meta px-3 pb-2" style="font-size: 0.65rem; opacity: 0.5;">
                        <span>ORIGIN: ${(t.origin || 'CUSTOM').toUpperCase()}</span>
                        <span class="ms-2">VER: ${t.version || '0.0.1'}</span>
                    </div>
                </div>
            </div>
        `;
    }
};
