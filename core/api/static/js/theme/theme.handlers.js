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
        if (typeof addAudit === 'function') addAudit(`🚀 正在启动主题物理自愈 (Bootstrap): ${themeId.toUpperCase()}...`);
        const success = await window.ThemeAPI.bootstrapTheme(themeId);
        
        if (success) {
            if (typeof addAudit === 'function') addAudit(`✅ [物理自愈] 主题 '${themeId.toUpperCase()}' 已成功固化。`, "success");
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

/**
 * 🛰️ 桥接全局 renderThemesCategory 以保持向后兼容性
 */
window.renderThemesCategory = () => {
    const allPlugins = window.allPlugins || [];
    const themes = allPlugins.filter(p => p.category === 'theme');
    const activeTheme = window.settingsData?.active_theme || 'default';
    
    return window.ThemeUI.renderThemesGallery(themes, activeTheme);
};
