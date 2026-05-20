/**
 * 🛰️ [V55.9] Illacme Plenipes Dashboard Core - Dirty-check Component
 * 职责：大配置对象深度 dotted 修改写入、脏状态差异指纹生成、保存按钮物理联动与对象扁平化。
 */

window.updateConfigField = (path, value) => {
    const keys = path.split('.');
    let current = window.settingsData;
    for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    if (typeof addAudit === 'function') addAudit(`📝 配置变更: ${path} = ${value}`);
    
    if (typeof window.checkSettingsDirty === 'function') {
        window.checkSettingsDirty();
    }
};

window.getCleanConfig = (obj) => {
    const flat = window.flattenObject(obj);
    const clean = {};
    Object.keys(flat).sort().forEach(key => {
        if (!key.split('.').some(part => part.startsWith('_'))) {
            clean[key] = flat[key];
        }
    });
    return JSON.stringify(clean);
};

window.checkSettingsDirty = () => {
    const saveBtn = document.getElementById('btn-save-settings');
    if (!saveBtn) return;
    
    if (!window.initialSettingsState) {
        saveBtn.disabled = true;
        saveBtn.style.opacity = '0.5';
        return;
    }

    const currentState = window.getCleanConfig(window.settingsData);
    const isDirty = currentState !== window.initialSettingsState;
    
    saveBtn.disabled = !isDirty;
    saveBtn.style.opacity = isDirty ? '1' : '0.5';
    if (isDirty) {
        saveBtn.classList.add('glow-btn');
    } else {
        saveBtn.classList.remove('glow-btn');
    }
};

window.flattenObject = (obj, prefix = '') => {
    let result = {};
    for (let key in obj) {
        if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
            Object.assign(result, window.flattenObject(obj[key], prefix + key + '.'));
        } else {
            result[prefix + key] = obj[key];
        }
    }
    return result;
};
