/**
 * 🕹️ Illacme Themes - Event Handlers Shard
 * 职责：负责主题模块的所有用户交互分发、联动逻辑与业务处理。
 */

window.ThemeHandlers = {
    /**
     * 🎬 切换主题
     */
    async switchTheme(themeId) {
        const themeName = window.getThemeDisplayName ? window.getThemeDisplayName(themeId) : themeId;
        const result = await Swal.fire({
            title: '🎨 确认切换装帧主题？',
            html: `确定要将当前品牌的主题切换为 <b style="color:var(--accent-secondary);">${themeName}</b> 吗？<br/><span style="font-size:0.75rem;color:var(--text-dim);">系统将自动重新对齐内容路径与编译依赖。</span>`,
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
        if (typeof addAudit === 'function') addAudit(`🎨 正在执行装帧切换: ${themeName}...`);
        const success = await window.ThemeAPI.switchTheme(themeId);
        
        if (success) {
            // 重新渲染当前分类以更新 UI 状态
            window._shouldScrollToTopAfterThemeSwitch = true;
            if (typeof window.showToast === 'function') window.showToast(`✨ 装帧主题已成功切换为 ${themeName}`, 'success');
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
            if (typeof refreshGovernanceContext === 'function') await refreshGovernanceContext();
            if (typeof window.autoAlignRouteMatrixWithActiveTheme === 'function') await window.autoAlignRouteMatrixWithActiveTheme(themeId);
            
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
        const themeName = window.getThemeDisplayName ? window.getThemeDisplayName(themeId) : themeId;
        const result = await Swal.fire({
            title: '🚀 确认下载并初始化主题？',
            html: `确定要部署并启用主题 <b style="color:var(--accent-secondary);">${themeName}</b> 吗？<br/><span style="font-size:0.75rem;color:var(--text-dim);">这可能需要从网络或本地缓存拉取高保真依赖，并自动设置为当前选用主题。</span>`,
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
        if (typeof addAudit === 'function') addAudit(`🚀 正在部署并启用主题: ${themeName}...`);
        const success = await window.ThemeAPI.bootstrapTheme(themeId);
        
        if (success) {
            if (typeof addAudit === 'function') addAudit(`✅ [部署启用] 主题 '${themeName}' 已部署成功并启用。`, "success");
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
     * ⚡ 切换并启动预览（一键闭环）
     */
    async switchAndLaunchTheme(themeId) {
        const themeName = window.getThemeDisplayName ? window.getThemeDisplayName(themeId) : themeId;
        const confirmResult = await Swal.fire({
            title: `⚡ 确认切换并启动 ${themeName} 预览？`,
            html: `系统将执行工业级四步自愈流转：<br/>
                <div style="font-size:0.75rem; color:var(--text-dim); text-align:left; margin-top:8px; line-height:1.6; background:rgba(0,0,0,0.3); padding:8px 12px; border-radius:6px;">
                    1. 🔒 校验并收割端口 43213 上的幽灵进程<br/>
                    2. 📦 检查多语言骨架与内容就绪<br/>
                    3. 🚀 映射专用 CLI 参数拉起 DevServer<br/>
                    4. ✨ HTTP 就绪探活深度握手
                </div>`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: '立即切换并预览',
            cancelButtonText: '取消',
            background: 'hsla(220, 43%, 7%, 0.98)',
            color: 'var(--text-bright)',
            confirmButtonColor: 'var(--accent-secondary)',
            cancelButtonColor: 'hsla(0, 0%, 27%, 1)'
        });
        if (!confirmResult.isConfirmed) return;

        Swal.fire({
            title: `🚀 正在编排 ${themeName}...`,
            html: '<div style="font-size:0.85rem;color:var(--accent-secondary);" id="orchestrator-step">[1/4] 🔒 正在释放并锁定端口 43213...</div>',
            allowOutsideClick: false,
            showConfirmButton: false,
            background: 'hsla(220, 43%, 7%, 0.98)',
            color: 'var(--text-bright)',
            didOpen: () => { Swal.showLoading(); }
        });

        try {
            const token = window.settingsData?.system?.api_token || '';
            const stepEl = document.getElementById('orchestrator-step');
            if (stepEl) stepEl.innerText = '[2/4] 📦 正在检查多语言文档脚手架与依赖...';

            const resp = await fetch('/api/system/preview/switch-and-launch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Token': token
                },
                body: JSON.stringify({
                    theme_id: themeId,
                    imprint_id: window.currentActiveImprint || 'default',
                    port: 43213,
                    sync_vault: true
                })
            });

            if (stepEl) stepEl.innerText = '[3/4] ⚡ 正在点火 DevServer 与监听端口...';

            const data = await resp.json();
            if (!resp.ok || data.status === 'error') {
                const logs = (data.tail_logs || []).join('\n') || data.detail || '未知异常';
                await Swal.fire({
                    title: '❌ DevServer 启动失败',
                    html: `<div style="text-align:left; font-size:0.8rem; color:#ff5555; margin-bottom:8px;">${data.message || data.detail || '服务未能在预期时间内就绪'}</div>
                           <details style="text-align:left; background:#111; padding:8px; border-radius:4px; font-family:monospace; font-size:0.7rem; color:#ccc; max-height:160px; overflow-y:auto;">
                             <summary style="cursor:pointer; color:var(--accent-secondary);">📋 展开排查终端日志</summary>
                             <pre style="white-space:pre-wrap; margin-top:6px;">${logs}</pre>
                           </details>`,
                    icon: 'error',
                    background: 'hsla(220, 43%, 7%, 0.98)',
                    color: 'var(--text-bright)'
                });
                return;
            }

            if (stepEl) stepEl.innerText = '[4/4] 📚 文库笔记全自动同步中 (HMR 实时监听)...';

            if (window.settingsData) window.settingsData.active_theme = themeId;
            if (typeof window.showToast === 'function') window.showToast(`✨ ${themeName} 已成功上线并开始实时预览！`, 'success');
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
            if (typeof refreshGovernanceContext === 'function') await refreshGovernanceContext();
            if (typeof window.autoAlignRouteMatrixWithActiveTheme === 'function') await window.autoAlignRouteMatrixWithActiveTheme(themeId);

            const syncTip = data.sync_triggered
                ? '<span style="font-size:0.75rem; color:var(--accent-secondary);">📚 文库原稿已全自动同步，已启用实时热更新 (HMR)！</span>'
                : '';

            Swal.fire({
                title: '✨ 预览服务已就绪！',
                html: `主题 <b>${themeName}</b> 已成功在端口 <b>${data.port || 43213}</b> 上线运行。<br/>
                       <span style="font-size:0.75rem; color:var(--neon-green);">🟢 HTTP 就绪握手成功！</span><br/>
                       ${syncTip}`,
                icon: 'success',
                showCancelButton: true,
                confirmButtonText: '🌐 打开新标签页预览',
                cancelButtonText: '留在画廊',
                background: 'hsla(220, 43%, 7%, 0.98)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--neon-green, #00ff88)'
            }).then((res) => {
                if (res.isConfirmed) {
                    const finalTarget = data.final_url || data.url || `http://localhost:${data.port || 43213}`;
                    window.open(finalTarget + (finalTarget.includes('?') ? '&' : '?') + 't=' + Date.now(), '_blank');
                }
            });
        } catch (err) {
            Swal.fire({
                title: '❌ 网络或通信异常',
                text: String(err),
                icon: 'error',
                background: 'hsla(220, 43%, 7%, 0.98)',
                color: 'var(--text-bright)'
            });
        }
    },

    /**
     * ⚡ 部署并启动预览（针对母本或全局中心主题）
     */
    async bootstrapAndLaunchTheme(themeId) {
        const themeName = window.getThemeDisplayName ? window.getThemeDisplayName(themeId) : themeId;
        const confirmResult = await Swal.fire({
            title: `🚀 确认部署并启动 ${themeName} 预览？`,
            html: `主题尚未派生到当前品牌库，系统将：<br/>
                <div style="font-size:0.75rem; color:var(--text-dim); text-align:left; margin-top:8px; line-height:1.6; background:rgba(0,0,0,0.3); padding:8px 12px; border-radius:6px;">
                    1. 🧬 从官方母本安全派生克隆至当前品牌隔离区 (SOP-13 合规)<br/>
                    2. 🔗 软链共享核心依赖资产<br/>
                    3. ⚡ 启动 DevServer 并就绪预览<br/>
                    4. 📚 自动编译同步文库原稿并启用 HMR 热更新
                </div>`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: '开始部署并预览',
            cancelButtonText: '取消',
            background: 'hsla(220, 43%, 7%, 0.98)',
            color: 'var(--text-bright)',
            confirmButtonColor: 'var(--neon-amber, #ffb300)',
            cancelButtonColor: 'hsla(0, 0%, 27%, 1)'
        });
        if (!confirmResult.isConfirmed) return;
        return this.switchAndLaunchTheme(themeId);
    },

    /**
     * 🔄 当前激活主题原位重新点火
     */
    async relaunchActivePreview() {
        const activeTheme = window.settingsData?.active_theme || 'default';
        const themeName = window.getThemeDisplayName ? window.getThemeDisplayName(activeTheme) : activeTheme;
        Swal.fire({
            title: `🔄 正在为 ${themeName} 重新点火...`,
            html: '<div style="font-size:0.85rem;color:var(--accent-secondary);">🔒 正在安全重启并重连 HTTP 端口...</div>',
            allowOutsideClick: false,
            showConfirmButton: false,
            background: 'hsla(220, 43%, 7%, 0.98)',
            color: 'var(--text-bright)',
            didOpen: () => { Swal.showLoading(); }
        });

        try {
            const token = window.settingsData?.system?.api_token || '';
            const resp = await fetch('/api/system/preview/restart', {
                method: 'POST',
                headers: { 'X-Token': token }
            });
            const data = await resp.json();
            if (resp.ok && data.status === 'success') {
                Swal.fire({
                    title: '✅ 重新点火成功',
                    text: `预览服务已在线，端口: ${data.port || 43213}`,
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false,
                    background: 'hsla(220, 43%, 7%, 0.98)',
                    color: 'var(--text-bright)'
                });
            } else {
                throw new Error(data.detail || data.message || '重启失败');
            }
        } catch (e) {
            Swal.fire({
                title: '❌ 重新点火失败',
                text: String(e),
                icon: 'error',
                background: 'hsla(220, 43%, 7%, 0.98)',
                color: 'var(--text-bright)'
            });
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
    // 🚀 [V80.3] 物理防震荡修复：仅在插件数据未初始化时触发单次静默加载，严禁无限递归重绘
    if (!window._themesHasLoaded && !window._isRefreshingThemes) {
        window._isRefreshingThemes = true;
        setTimeout(async () => {
            try {
                if (typeof loadPlugins === 'function') await loadPlugins();
                window._themesHasLoaded = true;
                if (window.currentActiveSettingsSubCat === 'themes') {
                    const el = document.getElementById('layout-panel-themes');
                    if (el) {
                        const allPlugins = window.allPlugins || [];
                        const themes = allPlugins.filter(p => p.category === 'theme' && p.is_enabled);
                        const activeTheme = window.settingsData?.active_theme || 'default';
                        el.innerHTML = window.ThemeUI.renderThemesGallery(themes, activeTheme);
                    }
                    if (window._shouldScrollToTopAfterThemeSwitch) {
                        window._shouldScrollToTopAfterThemeSwitch = false;
                        setTimeout(() => {
                            const scrollContainer = document.querySelector('#view-settings .tab-content-area');
                            if (scrollContainer) scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
                        }, 50);
                    }
                }
            } finally {
                window._isRefreshingThemes = false;
            }
        }, 30);
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
    const themeName = window.getThemeDisplayName ? window.getThemeDisplayName(id) : id;
    Swal.fire({
        title: `⚙️ 主题配置: ${themeName}`,
        text: '请前往 [PLUGINS / 插件中心] 进行完整物理管道参数划定与热重载配置。',
        icon: 'info',
        background: 'hsla(220, 43%, 7%, 0.98)',
        color: 'var(--text-bright)',
        confirmButtonText: '确定'
    });
};







