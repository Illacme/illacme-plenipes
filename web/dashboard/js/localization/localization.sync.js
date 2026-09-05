/**
 * 🌍 [V55.5] Illacme Plenipes Localization Sync Module (Central Hub)
 * 职责：全球分发源语种落盘固化、目标语种阵列点选与升降级置换、多语言总闸与路径前缀同步、高级治理配置通用落盘门面。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
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
    const i18n = window.settingsData?.i18n_settings || {};
    const currentTargets = (i18n.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
    const isLicensed = window.settingsData?._is_licensed || false;

    console.log("[I18n Sync] Current Targets:", currentTargets, "Toggling:", code, "Licensed:", isLicensed);

    let nextTargets;
    if (currentTargets.includes(code)) {
        // 取消选择
        nextTargets = currentTargets.filter(c => c !== code);
    } else {
        // 新增/置换
        const maxTargets = window.settingsData?._license_info?.max_i18n_targets || (isLicensed ? 999 : 1);
        if (maxTargets === 1 && currentTargets.length >= 1) {
            if (typeof addAudit === 'function') addAudit(`🔄 [免费社区版] 自动置换目标语种为: ${code}`, "info");
            nextTargets = [code];
        } else if (currentTargets.length >= maxTargets) {
            const tierName = window.settingsData?._license_info?.tier_name || '当前版本';
            if (typeof showNotification === 'function') {
                showNotification(`【${tierName}】最多支持配置 ${maxTargets} 个目标语种，如需更多请升级授权`, 'warning');
            }
            if (typeof addAudit === 'function') addAudit(`⚠️ 目标语种数量已达【${tierName}】上限 (${maxTargets})`, "warning");
            return;
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
            // 因此必须等待 >120ms 后再执行滚动，否则 DOM 元素会被二次 innerHTML 销毁重建导致 scrollTop 归零 (Rule 12)
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

// 🚀 [V75.0] 高级治理配置即时落盘 (支持精细化更新，绝不破坏用户当前交互焦点与 Sub-Tab 状态)
window.syncTranslationGovernanceField = async (path, value, shouldRerender = false) => {
    if (typeof addAudit === 'function') addAudit(`🛡️ 正在同步高级翻译治理配置: ${path}...`);

    // 即时更新内存 settingsData，支持深度 dotted 键路径
    if (typeof window.updateConfigField === 'function') {
        window.updateConfigField(path, value);
    }

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
            if (shouldRerender) {
                const curSub = window.currentActiveSettingsSubCat || 'block_rules';
                const panelEl = document.getElementById(`loc-panel-${curSub}`);
                if (curSub === 'glossary' && panelEl && typeof window.renderGlossaryCategory === 'function') {
                    panelEl.innerHTML = window.renderGlossaryCategory();
                } else if (curSub === 'block_rules' && panelEl && typeof window.renderBlockRulesCategory === 'function') {
                    panelEl.innerHTML = window.renderBlockRulesCategory();
                } else if (typeof renderSettingsCategory === 'function') {
                    renderSettingsCategory(curSub);
                }
            }
        }
    } else {
        const errMsg = res ? (res.error || res.message) : '物理链路超时';
        if (typeof addAudit === 'function') addAudit(`❌ 更新失败: ${errMsg}`, "error");
    }
};
