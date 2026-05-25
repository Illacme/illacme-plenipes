/**
 * 🕹️ Illacme Themes - Event Handlers Shard
 * 职责：负责主题模块的所有用户交互分发、联动逻辑与业务处理。
 */

window.ThemeHandlers = {
    /**
     * 🎬 切换主题
     */
    async switchTheme(themeId) {
        if (typeof addAudit === 'function') addAudit(`🎨 正在执行装帧切换: ${themeId.toUpperCase()}...`);
        const success = await window.ThemeAPI.switchTheme(themeId);
        
        if (success) {
            // 重新渲染当前分类以更新 UI 状态
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
            if (typeof refreshGovernanceContext === 'function') await refreshGovernanceContext();
        }
    },

    /**
     * 🚀 引导初始化
     */
    async bootstrapTheme(themeId) {
        if (typeof addAudit === 'function') addAudit(`🚀 正在部署并启用主题: ${themeId.toUpperCase()}...`);
        const success = await window.ThemeAPI.bootstrapTheme(themeId);
        
        if (success) {
            if (typeof addAudit === 'function') addAudit(`✅ [部署启用] 主题 '${themeId.toUpperCase()}' 已部署成功并启用。`, "success");
            if (typeof loadPlugins === 'function') await loadPlugins();
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
        }
    },

    /**
     * 🏗️ 调用全局服务动作
     */
    async invokeGlobalAction(action) {
        if (typeof invokeServiceAction === 'function') {
            await invokeServiceAction(action);
        }
    }
};

window.renderThemesCategory = () => {
    // 🚀 [V80.2] 全息状态自愈：每次进入主题分类时自动静默触发物理探测刷新，解决列表首次加载空引用 race condition
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
    const themes = allPlugins.filter(p => p.category === 'theme' && p.is_enabled);
    const activeTheme = window.settingsData?.active_theme || 'default';
    
    return window.ThemeUI.renderThemesGallery(themes, activeTheme);
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
            script.src = '/dashboard/js/plugins/plugins.editor.js?v=80.1';
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
