/**
 * 🕹️ Illacme Themes - Event Handlers Shard
 * 职责：负责主题模块的所有用户交互分发、联动逻辑与业务处理。
 */

window.ThemeHandlers = {
    /**
     * 🎬 切换主题
     */
    async switchTheme(themeId) {
        const result = await Swal.fire({
            title: '🎨 确认切换装帧主题？',
            html: `确定要将当前版图的主题切换为 <b style="color:var(--accent-secondary);">${themeId.toUpperCase()}</b> 吗？<br/><span style="font-size:0.75rem;color:var(--text-dim);">系统将自动重新对齐内容路径与编译依赖。</span>`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: '确定切换',
            cancelButtonText: '取消',
            background: 'hsla(220, 43%, 7%, 0.98)',
            color: 'var(--text-bright)',
            confirmButtonColor: 'var(--accent-secondary)',
            cancelButtonColor: 'hsla(0, 0%, 27%, 1)'
        });
        if (!result.isConfirmed) { if (typeof addAudit === 'function') addAudit(`🎬 已取消主题切换。`); return; }
        if (typeof addAudit === 'function') addAudit(`🎨 正在执行装帧切换: ${themeId.toUpperCase()}...`);
        const success = await window.ThemeAPI.switchTheme(themeId);
        
        if (success) {
            // 重新渲染当前分类以更新 UI 状态
            window._shouldScrollToTopAfterThemeSwitch = true;
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
            if (typeof refreshGovernanceContext === 'function') await refreshGovernanceContext();
            
            // 🚀 [V80.3 Neon Breath Glow] 延迟触发霓虹呼吸闪烁高亮动效
            setTimeout(() => {
                const activeCard = document.querySelector('.shield-pod.active-duty');
                if (activeCard) {
                    activeCard.style.boxShadow = '0 0 35px hsla(183, 100%, 50%, 0.45)';
                    activeCard.style.borderColor = 'var(--accent-secondary)';
                    activeCard.style.transition = 'all 1.5s cubic-bezier(0.16, 1, 0.3, 1)';
                    setTimeout(() => {
                        activeCard.style.boxShadow = '';
                        activeCard.style.borderColor = '';
                    }, 1500);
                }
            }, 400);
        }
    },

    /**
     * 🚀 引导初始化
     */
    async bootstrapTheme(themeId) {
        const result = await Swal.fire({
            title: '🚀 确认下载并初始化主题？',
            html: `确定要部署并启用主题 <b style="color:var(--accent-secondary);">${themeId.toUpperCase()}</b> 吗？<br/><span style="font-size:0.75rem;color:var(--text-dim);">这可能需要从网络或本地缓存拉取高保真依赖，并自动设置为当前选用主题。</span>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: '开始部署',
            cancelButtonText: '取消',
            background: 'hsla(220, 43%, 7%, 0.98)',
            color: 'var(--text-bright)',
            confirmButtonColor: 'var(--neon-amber, #ffb300)',
            cancelButtonColor: 'hsla(0, 0%, 27%, 1)'
        });
        if (!result.isConfirmed) { if (typeof addAudit === 'function') addAudit(`🚀 已取消主题部署初始化。`); return; }
        if (typeof addAudit === 'function') addAudit(`🚀 正在部署并启用主题: ${themeId.toUpperCase()}...`);
        const success = await window.ThemeAPI.bootstrapTheme(themeId);
        
        if (success) {
            if (typeof addAudit === 'function') addAudit(`✅ [部署启用] 主题 '${themeId.toUpperCase()}' 已部署成功并启用。`, "success");
            if (typeof loadPlugins === 'function') await loadPlugins();
            window._shouldScrollToTopAfterThemeSwitch = true;
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
            
            // 🚀 [V80.3 Neon Breath Glow] 延迟触发霓虹呼吸闪烁高亮动效
            setTimeout(() => {
                const activeCard = document.querySelector('.shield-pod.active-duty');
                if (activeCard) {
                    activeCard.style.boxShadow = '0 0 35px hsla(183, 100%, 50%, 0.45)';
                    activeCard.style.borderColor = 'var(--accent-secondary)';
                    activeCard.style.transition = 'all 1.5s cubic-bezier(0.16, 1, 0.3, 1)';
                    setTimeout(() => {
                        activeCard.style.boxShadow = '';
                        activeCard.style.borderColor = '';
                    }, 1500);
                }
            }, 400);
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
                if (window.currentActiveSettingsSubCat === 'themes') {
                    renderSettingsCategory('themes');
                    if (window._shouldScrollToTopAfterThemeSwitch) {
                        window._shouldScrollToTopAfterThemeSwitch = false;
                        setTimeout(() => {
                            const c = document.querySelector('.view-panel.active .tab-content-area');
                            if (c) { c.scrollTop = 0; c.scrollTo({ top: 0, behavior: 'smooth' }); }
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                            document.documentElement.scrollTop = 0;
                            document.body.scrollTop = 0;
                        }, 100);
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
        background: 'hsla(220, 43%, 7%, 0.98)',
        color: 'var(--text-bright)',
        confirmButtonText: '确定'
    });
};







