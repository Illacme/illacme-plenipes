/**
 * 🌍 [V55.5] Illacme Plenipes Localization Sync - Block Rules & Prompt Overrides Shard
 * 职责：块级分流动作切换、提示词微调抽屉开关、预设推荐注入与自定义 Prompt 实时同步。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

// 🚀 [V75.0] 切换提示词微调抽屉显示状态
window.togglePromptOverride = (key) => {
    const el = document.getElementById(`override-drawer-${key}`);
    if (el) {
        el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }
};

// 🚀 [V75.7] 块级动作选择切换处理器：若是 bypass 或 strip 动作，清空 prompt_override 以保整洁
window.handleBlockActionChange = async (key, action) => {
    const updates = {};
    updates[`translation.governance.block_rules.${key}.action`] = action;

    // 如果不是需要 AI 翻译的动作，则自动把该块的 prompt_override 清空
    if (action !== 'translate' && action !== 'parse_comments_only') {
        updates[`translation.governance.block_rules.${key}.prompt_override`] = null;
        if (typeof window.updateConfigField === 'function') {
            window.updateConfigField(`translation.governance.block_rules.${key}.prompt_override`, null);
        }
    }

    if (typeof addAudit === 'function') addAudit(`🛡️ 正在同步块级分流动作: ${key} -> ${action}...`);
    if (typeof window.updateConfigField === 'function') {
        window.updateConfigField(`translation.governance.block_rules.${key}.action`, action);
    }

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 块级分流配置已同步。`, "success");
        const freshConfig = await apiFetch('/api/system/config?level=merged');
        if (freshConfig) {
            window.settingsData = freshConfig;
            const panelEl = document.getElementById('loc-panel-block_rules');
            if (panelEl && typeof window.renderBlockRulesCategory === 'function') {
                panelEl.innerHTML = window.renderBlockRulesCategory();
            } else if (typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('block_rules');
            }
        }
    } else {
        const errMsg = res ? (res.error || res.message) : '物理链路超时';
        if (typeof addAudit === 'function') addAudit(`❌ 同步失败: ${errMsg}`, "error");
    }
};

// 🚀 [V75.6] 提示词微调启用/禁用切换处理器 (重构版：直接开启输入框，空内容自动载入首个预设)
window.handleOverrideToggle = async (key, checked) => {
    const drawer = document.getElementById(`override-drawer-${key}`);
    const textarea = document.getElementById(`textarea-override-${key}`);

    if (drawer) drawer.style.display = checked ? 'block' : 'none';

    if (!checked) {
        if (textarea) textarea.value = '';
        if (typeof window.syncTranslationGovernanceField === 'function') {
            await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, null);
        }
    } else {
        if (textarea) {
            textarea.focus();
            // 如果原本没有值，自动填充第一个预设
            if (!textarea.value.trim()) {
                const presets = window.blockPresets?.[key] || [];
                if (presets.length > 0) {
                    const defaultPreset = presets[0].value;
                    textarea.value = defaultPreset;
                    if (typeof window.syncTranslationGovernanceField === 'function') {
                        await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, defaultPreset);
                    }
                } else {
                    // 没有预设时，输入提示词，但为了保持勾选先同步一个点位字符
                    if (typeof window.syncTranslationGovernanceField === 'function') {
                        await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, "Translate");
                    }
                }
            }
        }
    }
};

// 🚀 [V75.6] 提示词微调内容修改变更处理器
window.handleOverrideChange = async (key, value) => {
    const val = value.trim();
    const checkbox = document.getElementById(`checkbox-override-${key}`);
    const drawer = document.getElementById(`override-drawer-${key}`);

    if (val && checkbox && !checkbox.checked) {
        checkbox.checked = true;
        if (drawer) drawer.style.display = 'block';
    }

    if (typeof window.syncTranslationGovernanceField === 'function') {
        await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, val || null);
    }
};

// 🚀 [V75.6] 应用提示词微调推荐预设
window.applyOverridePreset = async (key, presetVal) => {
    const textarea = document.getElementById(`textarea-override-${key}`);
    const checkbox = document.getElementById(`checkbox-override-${key}`);
    const drawer = document.getElementById(`override-drawer-${key}`);

    if (textarea) textarea.value = presetVal;
    if (checkbox) checkbox.checked = true;
    if (drawer) drawer.style.display = 'block';

    if (typeof window.syncTranslationGovernanceField === 'function') {
        await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, presetVal);
    }
};
