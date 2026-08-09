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

    const updatePayload = {
        'i18n_settings.enabled': val,
        'governance.publishing_mode': val ? 'global' : 'enhanced'
    };

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatePayload)
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
            // 🚀 [V57.5] 物理防线：必须在所有级联 DOM 重塑完成后（renderSettingsCategory → 20ms switchLocalizationGovSubTab → panelEl.innerHTML）再驱动滚动
            // 级联链路：renderSettingsCategory() → formEl.innerHTML → 20ms setTimeout → switchLocalizationGovSubTab → renderLocalizationCategory → panelEl.innerHTML
            // 因此必须等待 >120ms 后再执行滚动，否则 DOM 元素会被二次 innerHTML 销毁重建导致 scrollTop 归零
            setTimeout(() => {
                const scrollContainer = document.querySelector('#view-settings .tab-content-area') ||
                                        document.querySelector('.view-panel.active .tab-content-area') ||
                                        document.querySelector('.tab-content-area');
                const targetEl = document.getElementById('i18n-enable-control-group');
                console.log('[Scroll Debug] container:', scrollContainer, 'target:', targetEl);
                if (scrollContainer && targetEl) {
                    const containerRect = scrollContainer.getBoundingClientRect();
                    const targetRect = targetEl.getBoundingClientRect();
                    const offset = targetRect.top - containerRect.top;
                    console.log('[Scroll Debug] scrollTop:', scrollContainer.scrollTop, 'offset:', offset, 'newTop:', scrollContainer.scrollTop + offset - 15);
                    scrollContainer.scrollTo({
                        top: scrollContainer.scrollTop + offset - 15,
                        behavior: 'smooth'
                    });
                } else {
                    console.warn('[Scroll Debug] ❌ 未找到滚动容器或目标元素');
                }
            }, 300);
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

// 🚀 [V75.0] 高级治理配置即时落盘
window.syncTranslationGovernanceField = async (path, value) => {
    if (typeof addAudit === 'function') addAudit(`🛡️ 正在同步高级翻译治理配置: ${path}...`);

    // 即时更新内存 settingsData，支持深度 dotted 键路径
    window.updateConfigField(path, value);

    const payload = {};
    payload[path] = value;

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 高级翻译治理配置已固化落盘。`, "success");
        // 物理拉取最新状态进行对准
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

// 🚀 [V75.0] 切换提示词微调抽屉显示状态
window.togglePromptOverride = (key) => {
    const el = document.getElementById(`override-drawer-${key}`);
    if (el) {
        el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }
};

// 🚀 [V75.0] 新增专有名词保护词 (适配多语种对准)
window.addGlossaryItem = async () => {
    const srcInput = document.getElementById('glossary-src-input');
    const dstInput = document.getElementById('glossary-dst-input');
    if (!srcInput || !dstInput) return;

    const src = srcInput.value.trim();
    const dst = dstInput.value.trim();

    if (!src || !dst) {
        if (typeof showNotification === 'function') {
            showNotification('⚠️ 原稿词汇与保护译词均不能为空', 'warning');
        } else {
            alert('⚠️ 原稿词汇与保护译词均不能为空');
        }
        return;
    }

    const currentLang = window.currentGlossaryLang || 'en';
    const gov = window.settingsData.translation?.governance || {};
    const glossary = { ...(gov.glossary || {}) };

    if (!glossary[currentLang]) {
        glossary[currentLang] = {};
    } else {
        glossary[currentLang] = { ...glossary[currentLang] };
    }
    glossary[currentLang][src] = dst;

    await window.syncTranslationGovernanceField('translation.governance.glossary', glossary);

    srcInput.value = '';
    dstInput.value = '';
};

// 🚀 [V75.0] 删除专有名词保护词 (适配多语种对准)
window.removeGlossaryItem = async (src) => {
    const currentLang = window.currentGlossaryLang || 'en';
    const gov = window.settingsData.translation?.governance || {};
    const glossary = { ...(gov.glossary || {}) };

    if (glossary[currentLang]) {
        glossary[currentLang] = { ...glossary[currentLang] };
        delete glossary[currentLang][src];
    }

    await window.syncTranslationGovernanceField('translation.governance.glossary', glossary);
};

// 🚀 [V75.5] 切换专有名词术语编辑的语种 Tab
window.switchGlossaryLang = (code) => {
    window.currentGlossaryLang = code;
    window.currentGlossarySearchQuery = "";
    window.currentGlossaryPage = 1;
    if (typeof renderSettingsCategory === 'function') {
        renderSettingsCategory('localization');
    }
};

// 🚀 [V75.7] 块级动作选择切换处理器：若是 bypass 或 strip 动作，清空 prompt_override 以保整洁
window.handleBlockActionChange = async (key, action) => {
    const updates = {};
    updates[`translation.governance.block_rules.${key}.action`] = action;

    // 如果不是需要 AI 翻译的动作，则自动把该块的 prompt_override 清空
    if (action !== 'translate' && action !== 'parse_comments_only') {
        updates[`translation.governance.block_rules.${key}.prompt_override`] = null;
        window.updateConfigField(`translation.governance.block_rules.${key}.prompt_override`, null);
    }

    if (typeof addAudit === 'function') addAudit(`🛡️ 正在同步块级分流动作: ${key} -> ${action}...`);
    window.updateConfigField(`translation.governance.block_rules.${key}.action`, action);

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
            if (typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('localization');
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
        await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, null);
    } else {
        if (textarea) {
            textarea.focus();
            // 如果原本没有值，自动填充第一个预设
            if (!textarea.value.trim()) {
                const presets = window.blockPresets?.[key] || [];
                if (presets.length > 0) {
                    const defaultPreset = presets[0].value;
                    textarea.value = defaultPreset;
                    await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, defaultPreset);
                } else {
                    // 没有预设时，输入提示词，但为了保持勾选先同步一个点位字符
                    await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, "Translate");
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

    await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, val || null);
};

// 🚀 [V75.6] 应用提示词微调推荐预设
window.applyOverridePreset = async (key, presetVal) => {
    const textarea = document.getElementById(`textarea-override-${key}`);
    const checkbox = document.getElementById(`checkbox-override-${key}`);
    const drawer = document.getElementById(`override-drawer-${key}`);

    if (textarea) textarea.value = presetVal;
    if (checkbox) checkbox.checked = true;
    if (drawer) drawer.style.display = 'block';

    await window.syncTranslationGovernanceField(`translation.governance.block_rules.${key}.prompt_override`, presetVal);
};

// 🚀 [V75.6] 一键清空当前选定语种下的所有名词防护术语
window.clearGlossaryCurrentLang = async () => {
    if (typeof Swal === 'undefined') return;
    const currentLang = window.currentGlossaryLang || 'en';
    const result = await Swal.fire({
        title: '🧹 确认清空术语表？',
        text: `确定要彻底清空当前语种 [${currentLang.toUpperCase()}] 下的所有专有名词防护术语吗？此操作无法撤销。`,
        icon: 'warning',
        showCancelButton: true,
        background: 'hsla(236, 37%, 8%, 0.95)',
        color: 'var(--text-bright, #ffffff)',
        confirmButtonText: '💥 确定清空',
        cancelButtonText: '❌ 取消',
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'danger-btn glow-btn',
            cancelButton: 'primary-btn'
        }
    });

    if (result.isConfirmed) {
        const gov = window.settingsData.translation?.governance || {};
        const glossary = { ...(gov.glossary || {}) };
        glossary[currentLang] = {};

        if (typeof addAudit === 'function') addAudit(`🧹 正在清空 [${currentLang.toUpperCase()}] 的防护术语表...`);
        await window.syncTranslationGovernanceField('translation.governance.glossary', glossary);
        window.currentGlossaryPage = 1;
        if (typeof window.refreshGlossaryUI === 'function') {
            window.refreshGlossaryUI();
        }

        Swal.fire({
            title: '🎉 已清空',
            text: `当前语种 [${currentLang.toUpperCase()}] 的保护词表已成功清空！`,
            icon: 'success',
            background: 'hsla(236, 37%, 8%, 0.95)',
            color: 'var(--text-bright, #ffffff)',
            timer: 1500,
            showConfirmButton: false
        });
    }
};




