/**
 * 🕹️ Illacme Themes - Preview & Launch Orchestrator Shard
 * 职责：DevServer 预览点火、多语言脚手架检查、端口防冲突管理与原位重启编排。
 */

(function () {
    'use strict';

    if (!window.ThemeHandlers) {
        window.ThemeHandlers = {};
    }

    /**
     * ⚡ 切换并启动预览（一键闭环）
     */
    window.ThemeHandlers.switchAndLaunchTheme = async function (themeId) {
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
    };

    /**
     * ⚡ 部署并启动预览（针对母本或全局中心主题）
     */
    window.ThemeHandlers.bootstrapAndLaunchTheme = async function (themeId) {
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
    };

    /**
     * 🔄 当前激活主题原位重新点火
     */
    window.ThemeHandlers.relaunchActivePreview = async function () {
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
    };

})();
