/**
 * 🌍 [V55.5] Illacme Plenipes Localization Sync Module
 * 职责：全球分发源语种落盘固化、目标语种阵列点选与升降级置换、翻译风格三位一体 Prompt 策略发布、以及特定物理频道方言模板对正。
 */

window.syncI18nSource = async (val) => {
    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) {
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('localization');
            return;
        }
    }

    if (typeof addAudit === 'function') addAudit(`🌍 正在固化源内容语种: ${val}...`);

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'i18n_settings.source.lang_code': val })
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 源语种主权已确立。`, "success");
        // 物理拉取最新状态
        const freshConfig = await apiFetch('/api/system/config?level=merged');
        if (freshConfig) {
            window.settingsData = freshConfig;
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('localization');
        }
    }
};

window.toggleI18nTarget = async (el, code) => {
    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) {
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('localization');
            return;
        }
    }

    // 🚀 [V55.7] 权威数据源：直接从内存抓取
    const i18n = window.settingsData.i18n_settings || {};
    const currentTargets = (i18n.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
    const isLicensed = window.settingsData._is_licensed || false;

    console.log("[I18n Sync] Current Targets:", currentTargets, "Toggling:", code, "Licensed:", isLicensed);

    let nextTargets;
    if (currentTargets.includes(code)) {
        // 取消选择
        nextTargets = currentTargets.filter(c => c !== code);
    } else {
        // 新增/置换
        if (!isLicensed && currentTargets.length >= 1) {
            if (typeof addAudit === 'function') addAudit(`🔄 [社区版] 自动置换目标语种为: ${code}`, "info");
            nextTargets = [code];
        } else {
            nextTargets = [...currentTargets, code];
        }
    }

    if (typeof addAudit === 'function') addAudit(`🌍 正在同步分发矩阵...`);

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'i18n_settings.targets': nextTargets })
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 分发矩阵已同步。`, "success");

        // 🚀 [V55.7] 物理拉取最新状态
        const freshConfig = await apiFetch('/api/system/config?level=merged');
        if (freshConfig) {
            window.settingsData = freshConfig;
            // 🚀 [V55.7] 使用官方算子重绘
            if (typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('localization');
            }
            // 🛡️ [UI 即时对正] 同步刷新侧边栏 TRANSLATION ARRAY 显示，
            // 使语种点选操作后无需手动刷新页面即可看到最新配置。
            if (typeof window.refreshGovernanceContext === 'function') {
                window.refreshGovernanceContext();
            }
        }

    } else {
        const errMsg = res ? (res.error || res.message) : '物理链路超时';
        if (typeof addAudit === 'function') addAudit(`❌ 同步失败: ${errMsg}`, "error");
    }
};

const promptMapping = {
    'prompt-preview-translate-system': 'translate_system',
    'prompt-preview-translate-user': 'translate_user',
    'prompt-preview-title-system': 'title_system',
    'prompt-preview-title-user': 'title_user',
    'prompt-preview-meta-system': 'metadata_system',
    'prompt-preview-meta-user': 'metadata_user',
    'prompt-preview-slug-system': 'slug_system',
    'prompt-preview-slug-user': 'slug_user',
    'prompt-preview-seo-system': 'seo_system',
    'prompt-preview-seo-user': 'seo_user'
};

window.updateStylePreview = (styleKey) => {
    const style = window.translationStyles?.[styleKey];
    const descEl = document.getElementById('style-description-box');

    if (!style) {
        // 自定义 Prompt 处理
        if (descEl) {
            descEl.innerHTML = `<span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">自定义</span> <p style="margin: 0; font-weight: 500;">正在使用专属于该品牌的个性化翻译 Prompt 模板。</p>`;
        }
        
        const prompts = window.settingsData.translation?.prompts || {};
        
        // 移出只读限制，展现可编辑样式，并将内存中的值回填到输入框中
        Object.entries(promptMapping).forEach(([domId, propName]) => {
            const ta = document.getElementById(domId);
            if (!ta) return;
            ta.value = prompts[propName] || '';
            ta.removeAttribute('readonly');
            ta.style.background = 'var(--bg-agent-input)';
            ta.style.borderColor = 'rgba(var(--accent-primary-rgb), 0.25)';
            ta.style.cursor = 'text';
        });
        return;
    }
    
    // 更新描述卡片并触发平滑发光淡入动画
    if (descEl) {
        descEl.innerHTML = `
            <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">${style.badge}</span>
            <p style="margin: 0; font-weight: 500;">${style.desc}</p>
        `;
    }
    
    // 动态回填 8 个 Prompt 预览文本框，并设置为只读且淡化样式，同时更新内存中的 settingsData
    Object.entries(promptMapping).forEach(([domId, propName]) => {
        const ta = document.getElementById(domId);
        const val = style[propName] || '';
        if (ta) {
            ta.value = val;
            ta.setAttribute('readonly', 'true');
            ta.style.background = 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)';
            ta.style.borderColor = 'var(--glass-border)';
            ta.style.cursor = 'default';
        }
        // 同步修改内存配置
        window.updateConfigField(`translation.prompts.${propName}`, val);
    });
};

window.checkStyleMatch = () => {
    const selector = document.getElementById('style-selector');
    if (!selector) return;

    let matchKey = 'custom';
    
    const vals = {};
    Object.entries(promptMapping).forEach(([domId, propName]) => {
        const ta = document.getElementById(domId);
        vals[propName] = ta ? ta.value : '';
    });

    for (const [key, tpl] of Object.entries(window.translationStyles)) {
        const isMatch = (
            (tpl.translate_system || '') === (vals.translate_system || '') &&
            (tpl.translate_user || '') === (vals.translate_user || '') &&
            (tpl.title_system || '') === (vals.title_system || '') &&
            (tpl.title_user || '') === (vals.title_user || '') &&
            (tpl.metadata_system || '') === (vals.metadata_system || '') &&
            (tpl.metadata_user || '') === (vals.metadata_user || '') &&
            (tpl.slug_system || '') === (vals.slug_system || '') &&
            (tpl.slug_user || '') === (vals.slug_user || '')
        );
        if (isMatch) {
            matchKey = key;
            break;
        }
    }

    selector.value = matchKey;

    const descEl = document.getElementById('style-description-box');
    if (descEl) {
        if (matchKey === 'custom') {
            descEl.innerHTML = `
                <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">自定义</span>
                <p style="margin: 0; font-weight: 500;">正在使用专属于该品牌的个性化翻译 Prompt 模板。</p>
            `;
        } else {
            const style = window.translationStyles[matchKey];
            descEl.innerHTML = `
                <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">${style.badge}</span>
                <p style="margin: 0; font-weight: 500;">${style.desc}</p>
            `;
        }
    }
};

// 🚀 [V57.2] 物理多语言总闸即时同步落盘
window.syncI18nEnabled = async (val) => {
    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) {
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('localization');
            return;
        }
    }

    if (typeof addAudit === 'function') addAudit(`🌍 正在${val ? '开启' : '关闭'}多语言翻译矩阵...`);

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'i18n_settings.enabled': val })
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 多语言状态已物理固化为: ${val ? '已启用' : '已禁用'}.`, "success");
        // 物理拉取最新状态进行对正
        const freshConfig = await apiFetch('/api/system/config?level=merged');
        if (freshConfig) {
            window.settingsData = freshConfig;
            if (typeof window.updateSettingsTabsStatus === 'function') {
                window.updateSettingsTabsStatus();
            }
            if (typeof window.refreshGovernanceContext === 'function') {
                window.refreshGovernanceContext();
            }
            if (typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('localization');
            }
            // 🚀 [V57.5] 开启多语言翻译矩阵时，平滑滚动使“多语言翻译矩阵开关模块”对准视口上方露出
            if (val) {
                setTimeout(() => {
                    const targetEl = document.getElementById('i18n-enable-control-group');
                    if (targetEl) {
                        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }, 100);
            }
        }
    } else {
        const errMsg = res ? (res.error || res.message) : '物理链路超时';
        if (typeof addAudit === 'function') addAudit(`❌ 更新失败: ${errMsg}`, "error");
    }
};

// 🚀 [V57.3] 主语言路径前缀强制化即时同步落盘
window.syncI18nForcePrefix = async (val) => {
    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) {
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('localization');
            return;
        }
    }

    if (typeof addAudit === 'function') addAudit(`🌍 正在${val ? '开启' : '关闭'}主出版语种路径前缀强制化...`);

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'i18n_settings.force_source_prefix': val })
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 主语种路径前缀强制化状态已同步。`, "success");
        // 物理拉取最新状态进行对正
        const freshConfig = await apiFetch('/api/system/config?level=merged');
        if (freshConfig) {
            window.settingsData = freshConfig;
            if (typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('localization');
            }
        }
    } else {
        const errMsg = res ? (res.error || res.message) : '物理链路超时';
        if (typeof addAudit === 'function') addAudit(`❌ 更新失败: ${errMsg}`, "error");
    }
};

