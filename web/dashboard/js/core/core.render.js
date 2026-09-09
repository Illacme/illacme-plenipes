/**
 * 🛰️ [V55.9] Illacme Plenipes Dashboard Core - Render Component
 * 职责：治理层级智能匹配决议、通用表单配置项拼接渲染与特权边界指示器加载。
 */

window.resolveFieldLevel = (key) => {
    if (!window.governanceRules) return 'imprint';
    try {
        for (const [level, patterns] of Object.entries(window.governanceRules)) {
            if (!Array.isArray(patterns)) continue;
            for (const pattern of patterns) {
                const regex = new RegExp(pattern);
                if (regex.test(key)) return level;
            }
        }
    } catch(e) {}
    return 'imprint';
};

window.resolveFieldEffectiveness = (key) => {
    if (!key) return 'live';
    const rebuildPatterns = [
        /^i18n_settings/i,
        /^imprint_/i,
        /^site_(name|slogan|description|url)/i,
        /^logo_path/i,
        /^favicon_path/i,
        /^frontmatter_defaults/i,
        /^ingress_settings/i,
        /^slug_/i,
        /^route_matrix/i,
        /^theme_/i,
        /^custom_theme/i,
        /^translation\.(governance|prompts|style)/i,
        /^(append_credit|credit_text)/i,
        /^(publishing_mode|seo_strategy)/i
    ];
    for (const pattern of rebuildPatterns) {
        if (pattern.test(key)) return 'rebuild';
    }
    return 'live';
};

window.renderSettingsItem = (label, path, value, type = 'text', options = {}, tierOverride = null) => {
    const tier = tierOverride || window.resolveFieldLevel(path);
    const badgeMap = {
        'local': '<span class="tier-icon tier-local" title="📁 配置层级：本地专属配置 (config.local.yaml)">💻</span>',
        'imprint': '<span class="tier-icon tier-imprint" title="🏷️ 配置层级：出版品牌专属配置 (config.imprint.yaml)">🏷️</span>',
        'global': '<span class="tier-icon tier-global" title="🏛️ 配置层级：全局基线配置 (config.yaml)">🏛️</span>'
    };

    const effectiveness = options.effectiveness || window.resolveFieldEffectiveness(path);
    const effectBadge = (effectiveness === 'rebuild')
        ? '<span class="effect-icon effect-rebuild" title="⚡ 生效时机：装帧编译属性，保存后需执行「发布预览」或「全网发布」编译生效">⚡</span>'
        : '<span class="effect-icon effect-live" title="🟢 生效时机：运行基座属性，保存后后台即刻热更新生效">🟢</span>';

    let inputHtml = '';
    const id = `cfg-${path.replace(/\./g, '-')}`;
    const description = options.description || `配置主权链路中的 ${label} 参数。`;

    const safeValue = (value === undefined || value === null) ? '' : value;
    const requiredAttr = options.required ? 'required data-required="true"' : '';
    const reqStar = options.required ? '<span style="color: #ff4d4f; font-weight: bold; margin-left: 2px;">*</span>' : '';

    if (type === 'select') {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        const disabledAttr = options.disabled ? 'disabled' : '';
        inputHtml = `<select id="${id}" data-path="${path}" data-label="${label}" class="setting-input" onchange="${onchange}" ${disabledAttr} ${requiredAttr}>
            ${(options.items || []).map(item => `<option value="${item.value}" ${item.value === safeValue ? 'selected' : ''} title="${item.title || item.text || ''}">${item.text}</option>`).join('')}
        </select>`;
    } else if (type === 'checkbox') {
        const onchange = options.onchange || `updateConfigField('${path}', this.checked)`;
        const disabledAttr = options.disabled ? 'disabled' : '';
        inputHtml = `<label class="p-switch"><input type="checkbox" id="${id}" data-path="${path}" data-label="${label}" ${safeValue ? 'checked' : ''} onchange="${onchange}" ${disabledAttr}><span class="p-slider"></span></label>`;
    } else if (type === 'password') {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        inputHtml = `
            <div class="pwd-input-wrapper" style="position: relative; display: flex; align-items: center; width: 100%;">
                <input type="password" id="${id}" data-path="${path}" data-label="${label}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}" ${requiredAttr} style="padding-right: 36px; width: 100%;">
                <button type="button" class="pwd-toggle-btn" onclick="window.togglePasswordVisibility(this)" title="切换明文/密文" style="position: absolute; right: 8px; background: transparent; border: none; cursor: pointer; font-size: 0.85rem; opacity: 0.7; transition: opacity 0.2s; padding: 2px 4px; color: var(--neon-cyan, #00f2fe);">👁️</button>
            </div>
        `;
    } else if (type === 'number') {
        const onchange = options.onchange || `updateConfigField('${path}', parseFloat(this.value))`;
        const minAttr = options.min !== undefined ? `min="${options.min}"` : '';
        const maxAttr = options.max !== undefined ? `max="${options.max}"` : '';
        const stepAttr = options.step !== undefined ? `step="${options.step}"` : '';
        const unitHtml = options.unit ? `<span class="setting-unit" style="font-size: 0.78rem; color: var(--text-dim); flex-shrink: 0; font-family: monospace; user-select: none;">${options.unit}</span>` : '';
        inputHtml = `
            <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end; width: 100%;">
                <input type="number" id="${id}" data-path="${path}" data-label="${label}" class="setting-input setting-input-number" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}" ${minAttr} ${maxAttr} ${stepAttr} ${requiredAttr} style="max-width: 96px; text-align: right; font-variant-numeric: tabular-nums; padding: 8px 10px;">
                ${unitHtml}
            </div>
        `;
    } else if (type === 'static') {
        inputHtml = `<div id="${id}" class="setting-static-value" style="padding: 10px 12px; background: rgba(0,0,0,0.15); border-radius: 6px; border: 1px dashed var(--border-color); color: var(--text-dim); font-family: monospace; word-break: break-all;">${safeValue}</div>`;
    } else if (type === 'color') {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        const hexVal = (safeValue && safeValue.startsWith('#')) ? safeValue : (safeValue ? `#${safeValue}` : '#0070f3');
        const pickerId = `${id}-picker`;
        const presets = [
            { name: '极客青', hex: '#00f0ff' },
            { name: '翡翠绿', hex: '#00dc82' },
            { name: '赛博紫', hex: '#a855f7' },
            { name: '琥珀金', hex: '#f59e0b' },
            { name: '极光粉', hex: '#ec4899' },
            { name: '深海蓝', hex: '#0070f3' },
            { name: '极简墨', hex: '#64748b' }
        ];
        const presetsHtml = `
            <div class="color-preset-pills" style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px;">
                ${presets.map(p => `
                    <button type="button" class="color-pill-btn" onclick="window.applyColorPreset('${id}', '${p.hex}', '${path}')" title="${p.name} (${p.hex})" style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); cursor: pointer; color: var(--text-dim); transition: all 0.2s ease;">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: ${p.hex}; display: inline-block; box-shadow: 0 0 4px ${p.hex};"></span>
                        <span>${p.name}</span>
                    </button>
                `).join('')}
            </div>
        `;
        inputHtml = `
            <div class="color-input-container" style="display: flex; flex-direction: column; width: 100%;">
                <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                    <div style="position: relative; width: 34px; height: 34px; flex-shrink: 0; border-radius: 6px; overflow: hidden; border: 1px solid var(--glass-border); box-shadow: 0 1px 3px rgba(0,0,0,0.3);">
                        <input type="color" id="${pickerId}" value="${hexVal}" oninput="window.syncColorPickerToText('${id}', this.value, '${path}')" class="setting-color-picker" style="position: absolute; top: -8px; left: -8px; width: 50px; height: 50px; cursor: pointer; border: none; padding: 0; background: transparent;">
                    </div>
                    <input type="text" id="${id}" data-path="${path}" data-label="${label}" class="setting-input color-hex-input" value="${safeValue}" oninput="window.syncColorTextToPicker('${id}', this.value, '${path}')" onchange="${onchange}" placeholder="${options.placeholder || '#0070f3'}" ${requiredAttr} style="font-family: monospace; font-weight: 600; text-transform: lowercase; flex: 1;">
                </div>
                ${presetsHtml}
            </div>
        `;
    } else {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        inputHtml = `<input type="text" id="${id}" data-path="${path}" data-label="${label}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}" ${options.readonly ? 'readonly' : ''} ${requiredAttr}>`;
    }

    if (path && path.toLowerCase().includes('proxy')) {
        const presetsHtml = typeof window.renderProxyPresetsHtml === 'function' ? window.renderProxyPresetsHtml() : '';
        inputHtml += presetsHtml;
    }

    const alignStyle = (type === 'checkbox' || type === 'select' || type === 'number') ? 'align-items: flex-end;' : 'align-items: stretch;';
    return `
        <div class="setting-row level-${tier}">
            <div class="setting-info" style="flex: 2; min-width: 280px; max-width: 70%;">
                <div class="setting-label">
                    <span>${label}${reqStar}</span>
                    <span class="badge-group">${badgeMap[tier] || ''}${effectBadge}</span>
                </div>
                <div class="setting-desc">${description}</div>
            </div>
            <div class="setting-control" style="display: flex; flex-direction: column; ${alignStyle} flex: 1; min-width: 160px; max-width: 45%;">
                ${inputHtml}
            </div>
        </div>
    `;
};

window.togglePasswordVisibility = (btn) => {
    if (!btn) return;
    const wrapper = btn.closest('.pwd-input-wrapper') || btn.parentElement;
    if (!wrapper) return;
    const input = wrapper.querySelector('input');
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.innerText = '🙈';
        btn.title = '切换为密文隐藏';
        btn.style.opacity = '1';
    } else {
        input.type = 'password';
        btn.innerText = '👁️';
        btn.title = '切换为明文显示';
        btn.style.opacity = '0.7';
    }
};

window.syncColorPickerToText = (baseId, val, path) => {
    const textInput = document.getElementById(baseId);
    if (textInput) {
        textInput.value = val;
        textInput.dispatchEvent(new Event('input', { bubbles: true }));
        textInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
};

window.syncColorTextToPicker = (baseId, val, path) => {
    const pickerInput = document.getElementById(`${baseId}-picker`);
    if (pickerInput && /^#[0-9a-fA-F]{6}$/.test(val)) {
        pickerInput.value = val;
    }
};

window.applyColorPreset = (baseId, hex, path) => {
    const textInput = document.getElementById(baseId);
    const pickerInput = document.getElementById(`${baseId}-picker`);
    if (textInput) {
        textInput.value = hex;
        textInput.dispatchEvent(new Event('input', { bubbles: true }));
        textInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
    if (pickerInput) {
        pickerInput.value = hex;
    }
};

