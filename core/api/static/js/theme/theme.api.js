/**
 * 🎨 Illacme Themes - API Logic Shard
 * 职责：封装装帧主题的固化切换与物理自愈 (Bootstrap) 请求逻辑。
 */

window.ThemeAPI = {
    /**
     * 🎬 启用装帧：持久化活跃主题配置
     */
    async switchTheme(themeId) {
        try {
            const res = await apiFetch('/api/config/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'active_theme': themeId })
            });
            
            if (res && res.status === 'success') {
                if (typeof addAudit === 'function') addAudit(`✅ [装帧对正] 成功切换至主题: ${themeId.toUpperCase()}`, "success");
                window.settingsData.active_theme = themeId;
                return true;
            }
            return false;
        } catch (err) {
            console.error('Theme switch failed:', err);
            return false;
        }
    },

    /**
     * 🚀 物理自愈：执行主题引导固化
     */
    async bootstrapTheme(themeId) {
        try {
            const res = await apiFetch('/api/themes/bootstrap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'id': themeId })
            });
            return res && res.status === 'success';
        } catch (err) {
            console.error('Theme bootstrap failed:', err);
            return false;
        }
    }
};
