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

window.applyTranslationStyle = async () => {
    const selector = document.getElementById('style-selector');
    if (!selector) return;
    const style = selector.value;

    const templates = {
        professional: {
            translate: "You are a professional translator. Translate the following Markdown content from {source_lang} to {target_lang}. Keep all Markdown syntax, frontmatter keys, and LaTeX formulas intact. Use formal tone and professional vocabulary. Do not add any explanations.",
            title: "You are a professional editor. Translate and polish the following title into {target_lang}. Keep it concise, formal, and professional. Output ONLY the title.",
            meta: "You are a professional editor. Translate and polish the provided metadata into {target_lang} using formal terminology. Output ONLY the result."
        },
        casual: {
            translate: "You are a friendly translator. Translate the following Markdown content from {source_lang} to {target_lang} in a natural, conversational tone. Keep all Markdown syntax and frontmatter intact. Do not add any explanations.",
            title: "You are a creative editor. Translate the following title into {target_lang} in a catchy, natural, and conversational way. Output ONLY the title.",
            meta: "You are a creative editor. Translate the provided metadata into {target_lang} using natural, modern language. Output ONLY the result."
        },
        literal: {
            translate: "You are a precise translator. Translate the following Markdown content from {source_lang} to {target_lang} literally, preserving the original structure and word choice as much as possible. Keep all Markdown syntax intact. Do not add any explanations.",
            title: "You are a precise translator. Translate the following title into {target_lang} as literally as possible. Output ONLY the title.",
            meta: "You are a precise translator. Translate the provided metadata into {target_lang} literally. Output ONLY the result."
        }
    };

    const tpl = templates[style];
    if (!tpl) return;

    if (typeof addAudit === 'function') addAudit(`🎭 正在向全域（正文+标题+元数据）应用 [${style.toUpperCase()}] 风格...`, "info");

    const payload = {
        'translation.prompts.translate_system': tpl.translate,
        'translation.prompts.title_system': tpl.title,
        'translation.prompts.metadata_system': tpl.meta
    };

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 全域翻译风格已固化: ${style.toUpperCase()}`, "success");
        if (window.settingsData && window.settingsData.translation) {
            if (!window.settingsData.translation.prompts) window.settingsData.translation.prompts = {};
            window.settingsData.translation.prompts.translate_system = tpl.translate;
            window.settingsData.translation.prompts.title_system = tpl.title;
            window.settingsData.translation.prompts.metadata_system = tpl.meta;
        }
        const pTranslate = document.getElementById('prompt-preview-translate');
        const pTitle = document.getElementById('prompt-preview-title');
        const pMeta = document.getElementById('prompt-preview-meta');
        if (pTranslate) pTranslate.innerText = tpl.translate;
        if (pTitle) pTitle.innerText = tpl.title;
        if (pMeta) pMeta.innerText = tpl.meta;
    } else {
        if (typeof addAudit === 'function') addAudit(`❌ 风格应用失败: ${res ? res.error : '物理链路冲突'}`, "error");
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

