/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Lifecycle Shard
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");

// 🚀 [V74.96] 脏状态感应机制
window.initDrawerDirtySensing = () => {
    const body = document.getElementById('p-drawer-body');
    if (!body) return;
    
    window.isDrawerDirty = false;
    const indicator = document.getElementById('drawer-dirty-indicator');
    if (indicator) indicator.style.display = 'none';
    
    const saveBtn = document.getElementById('btn-save-plugin-cfg');
    if (saveBtn) saveBtn.classList.remove('glow-active');

    const serializeState = () => {
        const obj = {};
        body.querySelectorAll('input, select, textarea').forEach(el => {
            if (el.name) {
                obj[el.name] = el.type === 'checkbox' ? el.checked : el.value;
            }
        });
        return JSON.stringify(obj);
    };

    window.initialDrawerState = serializeState();

    body.querySelectorAll('input, select, textarea').forEach(el => {
        const handler = () => {
            const currentState = serializeState();
            if (currentState !== window.initialDrawerState) {
                if (saveBtn) saveBtn.classList.add('glow-active');
                if (indicator) indicator.style.display = 'inline-flex';
                window.isDrawerDirty = true;
            } else {
                if (saveBtn) saveBtn.classList.remove('glow-active');
                if (indicator) indicator.style.display = 'none';
                window.isDrawerDirty = false;
            }
        };
        el.addEventListener('input', handler);
        el.addEventListener('change', handler);
    });
};

// 🚀 [V74.96] 一键恢复出厂默认值 (Restore Defaults)
window.restoreThemeDefaults = async (themeId) => {
    const result = await Swal.fire({
        title: '🧹 恢复出厂设置？',
        text: '这将会把当前主题的所有配置选项抹除，并还原为官方定义的原始默认值！',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '确定还原',
        cancelButtonText: '取消',
        background: 'rgba(10, 15, 25, 0.98)',
        color: 'var(--text-bright)'
    });
    
    if (result.isConfirmed) {
        const plugins = window.allPlugins || [];
        const theme = plugins.find(p => p.id === themeId);
        if (!theme || !theme.schema) {
             Swal.fire('🛑 错误', '未找到该主题的自描述定义，无法定位默认值！', 'error');
             return;
        }
        
        const props = theme.schema.properties || {};
        const payload = {};
        
        Object.keys(props).forEach(key => {
             if ('default' in props[key]) {
                 const defaultVal = props[key].default;
                 payload[`theme_options.${themeId}.options.${key}`] = defaultVal;
                 
                 const inputEl = document.querySelector(`[name="theme_options.${themeId}.options.${key}"]`);
                 if (inputEl) {
                     if (inputEl.type === 'checkbox') {
                         inputEl.checked = defaultVal;
                     } else {
                         inputEl.value = defaultVal;
                     }
                 }
             }
        });
        
        const res = await apiFetch('/api/config/update', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        if (res && res.status === 'success') {
            window.settingsData = { ...window.settingsData, ...res.active_config };
            window.isDrawerDirty = false;
            Swal.fire('✅ 已恢复', '主题已成功恢复出厂默认配置！', 'success');
            
            window.closePluginDrawer();
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
        } else {
            Swal.fire('🛑 恢复失败', res ? res.error : '网络链路阻塞', 'error');
        }
    }
};
