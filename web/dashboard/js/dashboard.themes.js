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
                    const iconMap = { 'starlight': '🌟', 'docusaurus': '🦖', 'sovereign': '👑', 'default': '👑', 'vitepress': '⚡', 'nextra': '📖' };
                    const icon = iconMap[t.id] || (t.origin === 'core' ? '🎨' : '🧩');
                    
                    let statusLabel = "";
                    let actionButton = "";
                    
                    if (isActive) {
                        statusLabel = '<span class="badge active">🟢 当前选用</span>';
                        actionButton = '<button class="action-btn active" disabled>已就绪</button>';
                    } else if (t.location === 'native') {
                        statusLabel = '<span class="badge warning">NATIVE</span>';
                        actionButton = `<button class="action-btn glow-btn" onclick="bootstrapTheme('${t.id}')">⚡ 下载并切换</button>`;
                    } else if (t.location === 'global') {
                        statusLabel = `<span class="badge info">${t.location.toUpperCase()}</span>`;
                        actionButton = `<button class="action-btn glow-btn" onclick="switchTheme('${t.id}')">🎬 同步并切换</button>`;
                    } else {
                        statusLabel = `<span class="badge info">${t.location.toUpperCase()}</span>`;
                        actionButton = `<button class="action-btn glow-btn" onclick="switchTheme('${t.id}')">🎬 切换主题</button>`;
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
                                <button class="action-btn secondary" onclick="openPluginConfig('${t.id}')" ${t.location !== 'local' ? 'disabled' : ''} title="${t.location === 'local' ? '主题配置' : '请先部署或切换此主题为当前版图主题，启用后即可配置属性'}">⚙️</button>
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
                        <button class="secondary-btn" onclick="invokeServiceAction('install')" style="font-size: 0.8rem;">🏗️ 自动安装主题依赖</button>
                        <button class="secondary-btn" onclick="addAudit('📡 正在重新同步并对齐样式与脚本资源索引...')">🎨 重新生成资产索引</button>
                    </div>
                </div>
            </div>
        </div>
    `;
};

window.switchTheme = async (themeId) => {
    const result = await Swal.fire({
        title: '🎨 确认切换装帧主题？',
        html: `确定要将当前版图的主题切换为 <b style="color:var(--accent-secondary);">${themeId.toUpperCase()}</b> 吗？<br/><span style="font-size:0.75rem;color:var(--text-dim);">系统将自动重新对齐内容路径与编译依赖。</span>`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: '确定切换',
        cancelButtonText: '取消',
        background: 'rgba(10, 15, 25, 0.98)',
        color: 'var(--text-bright)',
        confirmButtonColor: 'var(--accent-secondary)',
        cancelButtonColor: '#444'
    });
    
    if (!result.isConfirmed) {
        if (typeof addAudit === 'function') addAudit(`🎬 已取消主题切换。`);
        return;
    }

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
        
        // 🚀 [V80.3 Premium Scroll-to-Top] 物理容器优雅平滑上滚回顶部，配合重排对齐
        const container = document.querySelector('.tab-content-area');
        if (container) {
            container.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        // 🚀 [V80.3 Neon Breath Glow] 延迟触发霓虹呼吸闪烁高亮动效
        setTimeout(() => {
            const activeCard = document.querySelector('.theme-card.active') || document.querySelector('.shield-pod.active-duty');
            if (activeCard) {
                activeCard.style.boxShadow = '0 0 35px rgba(0, 242, 255, 0.45)';
                activeCard.style.borderColor = 'var(--accent-secondary)';
                activeCard.style.transition = 'all 1.5s cubic-bezier(0.16, 1, 0.3, 1)';
                setTimeout(() => {
                    activeCard.style.boxShadow = '';
                    activeCard.style.borderColor = '';
                }, 1500);
            }
        }, 400);
    } else {
        if (typeof addAudit === 'function') addAudit(`🚨 切换失败: ${res ? res.error : '网络链路阻塞'}`, "error");
    }
};

window.bootstrapTheme = async (themeId) => {
    const result = await Swal.fire({
        title: '🚀 确认下载并初始化主题？',
        html: `确定要部署并启用主题 <b style="color:var(--accent-secondary);">${themeId.toUpperCase()}</b> 吗？<br/><span style="font-size:0.75rem;color:var(--text-dim);">这可能需要从网络或本地缓存拉取高保真依赖，并自动设置为当前选用主题。</span>`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '开始部署',
        cancelButtonText: '取消',
        background: 'rgba(10, 15, 25, 0.98)',
        color: 'var(--text-bright)',
        confirmButtonColor: '#ffb700',
        cancelButtonColor: '#444'
    });
    
    if (!result.isConfirmed) {
        if (typeof addAudit === 'function') addAudit(`🚀 已取消主题部署初始化。`);
        return;
    }

    if (typeof addAudit === 'function') addAudit(`🚀 正在部署并启用主题: ${themeId.toUpperCase()}...`);
    try {
        const res = await apiFetch('/api/themes/bootstrap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'id': themeId })
        });
        if (res && res.status === 'success') {
            if (typeof addAudit === 'function') addAudit(`✅ [部署启用] 主题 '${themeId.toUpperCase()}' 已部署成功并启用。`, "success");
            if (typeof loadPlugins === 'function') await loadPlugins();
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
            
            // 🚀 [V80.3 Premium Scroll-to-Top] 物理容器优雅平滑上滚回顶部，配合重排对齐
            const container = document.querySelector('.tab-content-area');
            if (container) {
                container.scrollTo({ top: 0, behavior: 'smooth' });
            }
            
            // 🚀 [V80.3 Neon Breath Glow] 延迟触发霓虹呼吸闪烁高亮动效
            setTimeout(() => {
                const activeCard = document.querySelector('.theme-card.active') || document.querySelector('.shield-pod.active-duty');
                if (activeCard) {
                    activeCard.style.boxShadow = '0 0 35px rgba(0, 242, 255, 0.45)';
                    activeCard.style.borderColor = 'var(--accent-secondary)';
                    activeCard.style.transition = 'all 1.5s cubic-bezier(0.16, 1, 0.3, 1)';
                    setTimeout(() => {
                        activeCard.style.boxShadow = '';
                        activeCard.style.borderColor = '';
                    }, 1500);
                }
            }, 400);
        }
    } catch (e) {
        if (typeof addAudit === 'function') addAudit(`🚨 [网络故障] 无法连接至引导服务器: ${e.message}`, "error");
    }
};

// ⚙️ [V74.8] 动态载入插件配置编辑器依赖，100% 物理防止配置齿轮按钮失效
window.openPluginConfig = window.openPluginConfig || async function(id) {
    if (typeof window.openPluginConfig === 'function' && window.openPluginConfig !== arguments.callee) {
        return window.openPluginConfig(id);
    }
    
    // 动态拉起脚本依赖
    const scriptId = 'sovereign-plugin-editor-script';
    if (!document.getElementById(scriptId)) {
        await new Promise((resolve) => {
            const script = document.createElement('script');
            script.id = scriptId;
            script.src = '/dashboard/js/plugins/plugins.editor.js';
            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);
            document.body.appendChild(script);
        });
    }
    
    // 再次尝试触发
    if (typeof window.openPluginConfig === 'function' && window.openPluginConfig !== arguments.callee) {
        return window.openPluginConfig(id);
    }
    
    // 降级兜底 Swal
    Swal.fire({
        title: `⚙️ 主题配置: ${id.toUpperCase()}`,
        text: '请前往 [PLUGINS / 插件中心] 进行完整物理管道参数划定与热重载配置。',
        icon: 'info',
        background: 'rgba(10, 15, 25, 0.98)',
        color: 'var(--text-bright)',
        confirmButtonText: '确定'
    });
};
