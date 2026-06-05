/**
 * 🌍 [V55.5] Illacme Plenipes Localization Sync Module
 * 职责：全球分发源语种落盘固化、目标语种阵列点选与升降级置换、翻译风格三位一体 Prompt 策略发布、以及特定物理频道方言模板对正。
 */

window.syncI18nSource = async (val) => {
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
        }
    } else {
        const errMsg = res ? (res.error || res.message) : '物理链路超时';
        if (typeof addAudit === 'function') addAudit(`❌ 同步失败: ${errMsg}`, "error");
    }
};

window.updateStylePreview = (styleKey) => {
    const style = window.translationStyles?.[styleKey];
    
    const pTranslate = document.getElementById('prompt-preview-translate');
    const pTitle = document.getElementById('prompt-preview-title');
    const pMeta = document.getElementById('prompt-preview-meta');

    if (!style) {
        // 自定义 Prompt 处理
        const descEl = document.getElementById('style-description-box');
        if (descEl) {
            descEl.innerHTML = `<span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">自定义</span> <p style="margin: 0; font-weight: 500;">正在使用专属于该品牌的个性化翻译 Prompt 模板。</p>`;
        }
        const prompts = window.settingsData.translation?.prompts || {};
        if (pTranslate) pTranslate.value = prompts.translate_system || '';
        if (pTitle) pTitle.value = prompts.title_system || '';
        if (pMeta) pMeta.value = prompts.metadata_system || '';

        // 移出只读限制，展现可编辑样式
        [pTranslate, pTitle, pMeta].forEach(ta => {
            if (!ta) return;
            ta.removeAttribute('readonly');
            ta.style.background = 'var(--bg-agent-input)';
            ta.style.borderColor = 'rgba(var(--accent-primary-rgb), 0.25)';
            ta.style.cursor = 'text';
        });
        return;
    }
    
    // 更新描述卡片并触发平滑发光淡入动画
    const descEl = document.getElementById('style-description-box');
    if (descEl) {
        descEl.innerHTML = `
            <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">${style.badge}</span>
            <p style="margin: 0; font-weight: 500;">${style.desc}</p>
        `;
    }
    
    // 动态回填三个 Prompt 预览文本框，并设置为只读且淡化样式
    if (pTranslate) {
        pTranslate.value = style.translate;
        pTranslate.setAttribute('readonly', 'true');
        pTranslate.style.background = 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)';
        pTranslate.style.borderColor = 'var(--glass-border)';
        pTranslate.style.cursor = 'default';
    }
    if (pTitle) {
        pTitle.value = style.title;
        pTitle.setAttribute('readonly', 'true');
        pTitle.style.background = 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)';
        pTitle.style.borderColor = 'var(--glass-border)';
        pTitle.style.cursor = 'default';
    }
    if (pMeta) {
        pMeta.value = style.meta;
        pMeta.setAttribute('readonly', 'true');
        pMeta.style.background = 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)';
        pMeta.style.borderColor = 'var(--glass-border)';
        pMeta.style.cursor = 'default';
    }
};

window.checkStyleMatch = () => {
    const selector = document.getElementById('style-selector');
    if (selector) {
        let hasCustomOpt = Array.from(selector.options).some(opt => opt.value === 'custom');
        if (!hasCustomOpt) {
            const opt = document.createElement('option');
            opt.value = 'custom';
            opt.text = '✍️ 自定义风格 (Custom Prompt)';
            selector.appendChild(opt);
        }
        selector.value = 'custom';
    }

    // 更新描述区为自定义
    const descEl = document.getElementById('style-description-box');
    if (descEl) {
        descEl.innerHTML = `
            <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">自定义</span>
            <p style="margin: 0; font-weight: 500;">正在使用专属于该品牌的个性化翻译 Prompt 模板。</p>
        `;
    }
};

window.applyTranslationStyle = async () => {
    const pTranslate = document.getElementById('prompt-preview-translate');
    const pTitle = document.getElementById('prompt-preview-title');
    const pMeta = document.getElementById('prompt-preview-meta');
    
    if (!pTranslate || !pTitle || !pMeta) return;

    const translatePrompt = pTranslate.value;
    const titlePrompt = pTitle.value;
    const metaPrompt = pMeta.value;

    const selector = document.getElementById('style-selector');
    const style = selector ? selector.value : 'custom';

    if (typeof addAudit === 'function') {
        addAudit(`🎭 正在向全域（正文+标题+元数据）固化应用所选翻译 Prompt...`, "info");
    }

    const payload = {
        'translation.prompts.translate_system': translatePrompt,
        'translation.prompts.title_system': titlePrompt,
        'translation.prompts.metadata_system': metaPrompt
    };

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') {
            addAudit(`✅ 全域翻译风格已固化应用，当前显示为: ${style.toUpperCase()}`, "success");
        }
        if (window.settingsData && window.settingsData.translation) {
            if (!window.settingsData.translation.prompts) window.settingsData.translation.prompts = {};
            window.settingsData.translation.prompts.translate_system = translatePrompt;
            window.settingsData.translation.prompts.title_system = titlePrompt;
            window.settingsData.translation.prompts.metadata_system = metaPrompt;
        }
    } else {
        if (typeof addAudit === 'function') {
            addAudit(`❌ 风格应用失败: ${res ? (res.error || res.message) : '物理链路冲突'}`, "error");
        }
    }
};

// 🚀 [V57.2] 物理多语言总闸即时同步落盘
window.syncI18nEnabled = async (val) => {
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

