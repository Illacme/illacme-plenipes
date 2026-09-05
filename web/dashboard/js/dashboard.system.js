/**
 * ⚙️ [V57.4] Illacme Plenipes System & Governance Module (Hub & Controller)
 * 职责：系统设置、基础信息管理与安全审计主中枢。
 * 注：页面视图渲染逻辑已物理拆分至 system.render.js；段落缓存运维操作已物理拆分至 system.cache.js。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规重组。
 */

const getParentCat = (cat) => {
    if (['imprints', 'themes', 'modes'].includes(cat)) return 'layout';
    if (['localization', 'block_rules', 'glossary', 'translation_style'].includes(cat)) return 'localization_gov';
    if (['slug_settings', 'route_matrix'].includes(cat)) return 'dissemination_routing';
    if (['security', 'guardrails'].includes(cat)) return 'security_audit';
    if (['license', 'activation', 'comparison', 'docs'].includes(cat)) return 'license';
    if (cat === 'i18n_routing') return 'localization_gov';
    // 父级分类名自身传入时直接返回自身，防止 fall through 到 general
    if (['layout', 'localization_gov', 'dissemination_routing', 'security_audit', 'general', 'license'].includes(cat)) return cat;
    return 'general';
};

window.switchToSettingsTab = (catName) => {
    const parentCat = getParentCat(catName);
    const tab = document.querySelector(`.s-tab[data-cat="${parentCat}"]`);
    if (tab) {
        document.querySelectorAll('.s-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        renderSettingsCategory(catName);
    }
};

// 1. 系统设置加载器
window.loadSettings = async (targetCat = 'layout') => {
    // 🚀 [V55.21] 物理状态先行：在异步加载前先对正侧边栏标签状态
    const parentCat = getParentCat(targetCat);
    document.querySelectorAll('.s-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.cat === parentCat);
        tab.onclick = () => {
            const dot = tab.querySelector('.alert-dot');
            if (dot) dot.remove();

            document.querySelectorAll('.s-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // 点击大 Tab 时，默认跳转到对应的第一个子页面
            let target = tab.dataset.cat;
            if (target === 'layout') target = 'imprints';
            else if (target === 'general') target = 'identity';
            else if (target === 'localization_gov' || target === 'i18n_routing') target = 'localization';
            else if (target === 'dissemination_routing') target = 'slug_settings';
            else if (target === 'security_audit') target = 'security';
            else if (target === 'license') target = 'license';

            renderSettingsCategory(target);
            if (target === 'general' && typeof window.refreshCacheStats === 'function') {
                window.refreshCacheStats();
            }
            const c = document.querySelector('.view-panel.active .tab-content-area');
            if (c) c.scrollTop = 0;
        };
    });

    const formEl = document.getElementById('settings-form');
    if (formEl) formEl.innerHTML = '<div class="loading">正在拉取全量主权配置与治理元数据...</div>';

    const res = await apiFetch('/api/system/config');
    const imprints = await apiFetch('/api/imprints');
    const slotsRes = await apiFetch('/api/system/theme/slots');
    const vaultRes = await apiFetch('/api/vault/list');
    if (!res) return;

    window.settingsData = res.config || res;
    window.governanceRules = res.governance_rules || res._governance_rules;
    window.settingsData._imprints = imprints ? imprints.imprints : [];
    window._existingImprintList = window.settingsData._imprints;
    if (typeof window.updateWizardQuotaNotice === 'function') {
        window.updateWizardQuotaNotice(window.settingsData._imprints);
    }
    window.settingsData._active_imprint = imprints ? imprints.active : 'default';
    window.settingsData._is_licensed = res._is_licensed || false;
    const headerProBadge = document.getElementById('header-pro-badge');
    if (headerProBadge) {
        headerProBadge.innerText = window.settingsData._is_licensed ? '💎 PRO' : '🌱 LITE';
        headerProBadge.className = window.settingsData._is_licensed ? 'header-pro-badge pro-active' : 'header-pro-badge lite-active';
        headerProBadge.style.display = 'inline-flex';
    }
    window.settingsData._theme_slots = (slotsRes && slotsRes.slots) ? slotsRes.slots : {};
    window.settingsData._directories = (vaultRes && vaultRes.directories) ? vaultRes.directories : [];
    window.settingsData._vault_files = (vaultRes && (vaultRes.manuscripts || vaultRes.vault_list)) ? (vaultRes.manuscripts || vaultRes.vault_list) : [];
    window.settingsData._imprint_stats = window.settingsData._imprint_stats || {};

    const stats = await apiFetch('/api/imprints/stats');
    window.settingsData._imprint_stats = stats || {};

    // 🚀 [V57.1] 初始化基准状态快照，用于脏检查
    if (typeof window.getCleanConfig === 'function') {
        window.initialSettingsState = window.getCleanConfig(window.settingsData);
        if (typeof window.checkSettingsDirty === 'function') {
            window.checkSettingsDirty();
        }
    }

    // 🚀 [V57.3] 动态同步刷新侧边栏子项多语言指示器与锁定锁
    if (typeof window.updateSettingsTabsStatus === 'function') {
        window.updateSettingsTabsStatus();
    }

    renderSettingsCategory(targetCat);
    if (targetCat === 'general' && typeof window.refreshCacheStats === 'function') {
        window.refreshCacheStats();
    }
    if (window.feBus) {
        window.feBus.emit('SETTINGS_DATA_LOADED', window.settingsData);
    }
};

// 🚀 [V57.3] 动态更新设置选项卡的多语言状态信标与锁标识
window.updateSettingsTabsStatus = () => {
    const isEnabled = window.settingsData?.i18n_settings?.enabled !== false;
    document.querySelectorAll('.s-tab').forEach(tab => {
        if (tab.dataset.cat === 'localization_gov') {
            tab.innerHTML = isEnabled ? '<span class="tab-icon">🌍</span> 多语翻译' : '<span class="tab-icon" style="opacity: 0.5;">🌍</span> <span style="opacity: 0.7;">多语翻译 (已关闭)</span>';
        }
    });
};

window.renderSettingsCategory = (cat) => {
    const formEl = document.getElementById('settings-form');
    if (!formEl) return;

    let actualCat = cat;
    if (cat === 'layout') actualCat = 'imprints';
    else if (cat === 'general' || ['identity', 'compliance', 'storage', 'engine'].includes(cat)) actualCat = 'general';
    else if (cat === 'localization_gov' || cat === 'i18n_routing') actualCat = 'localization';
    else if (cat === 'dissemination_routing') actualCat = 'slug_settings';
    else if (cat === 'security_audit') actualCat = 'security';
    else if (cat === 'license' || ['activation', 'comparison', 'docs'].includes(cat)) actualCat = 'license';

    window.currentActiveSettingsSubCat = actualCat;

    const layoutCats = ['imprints', 'themes', 'modes'];
    const locGovCats = ['localization', 'block_rules', 'glossary', 'translation_style'];
    const routingCats = ['slug_settings', 'route_matrix'];

    let html = '';
    if (actualCat === 'general') {
        html = typeof renderGeneralCategory === 'function' ? renderGeneralCategory() : '<div class="empty-state">模块加载中...</div>';
    } else if (layoutCats.includes(actualCat)) {
        html = typeof renderLayoutCategory === 'function' ? renderLayoutCategory() : '<div class="empty-state">模块加载中...</div>';
    } else if (locGovCats.includes(actualCat)) {
        html = typeof renderLocalizationGovCategory === 'function' ? renderLocalizationGovCategory() : '<div class="empty-state">模块加载中...</div>';
    } else if (routingCats.includes(actualCat)) {
        html = typeof renderDisseminationRoutingCategory === 'function' ? renderDisseminationRoutingCategory() : '<div class="empty-state">模块加载中...</div>';
    } else if (actualCat === 'security') {
        html = typeof renderSecurityCategory === 'function' ? renderSecurityCategory() : '<div class="empty-state">模块加载中...</div>';
    } else if (actualCat === 'license') {
        html = typeof renderLicenseCategory === 'function' ? renderLicenseCategory() : '<div class="empty-state">模块加载中...</div>';
    } else if (actualCat === 'guardrails') {
        renderSettingsCategory('security');
        return;
    } else if (actualCat === 'compute_strategy') {
        if (typeof renderComputeStrategy === 'function') {
            html = renderComputeStrategy(window.settingsData);
        }
    }

    formEl.innerHTML = html;

    // 动态在渲染后激活点亮二级 Sub-Tab 对应的面板
    if (layoutCats.includes(actualCat)) {
        const btn = document.querySelector(`#layout-sub-tab-bar .sub-tab-btn[onclick*="${actualCat}"]`);
        if (typeof window.switchLayoutSubTab === 'function') {
            window.switchLayoutSubTab(actualCat, btn);
        }
    } else if (locGovCats.includes(actualCat)) {
        const btn = document.querySelector(`#loc-gov-sub-tab-bar .sub-tab-btn[onclick*="${actualCat}"]`);
        if (typeof window.switchLocalizationGovSubTab === 'function') {
            window.switchLocalizationGovSubTab(actualCat, btn);
        }
    } else if (routingCats.includes(actualCat)) {
        const btn = document.querySelector(`#dissemination-routing-sub-tab-bar .sub-tab-btn[onclick*="${actualCat}"]`);
        if (typeof window.switchDisseminationRoutingSubTab === 'function') {
            window.switchDisseminationRoutingSubTab(actualCat, btn);
        }
    } else if (actualCat === 'general') {
        let activeSub = window.currentActiveGeneralSubTab || 'identity';
        const btn = document.querySelector(`#general-sub-tab-bar .sub-tab-btn[onclick*="${activeSub}"]`);
        if (typeof window.switchGeneralSubTab === 'function') {
            window.switchGeneralSubTab(activeSub, btn);
        }
    } else if (actualCat === 'security') {
        let activeSub = window.currentActiveSecuritySubTab || 'policy';
        if (activeSub === 'guardrails') activeSub = 'policy';
        const btn = document.querySelector(`#security-sub-tab-bar .sub-tab-btn[onclick*="${activeSub}"]`);
        if (typeof window.switchSecuritySubTab === 'function') {
            window.switchSecuritySubTab(activeSub, btn);
        }
    }

    if (window._shouldScrollToTopAfterThemeSwitch) {
        window._shouldScrollToTopAfterThemeSwitch = false;
        setTimeout(() => {
            const container = document.querySelector('.view-panel.active .tab-content-area');
            if (container) {
                container.scrollTop = 0;
                container.scrollTo({ top: 0, behavior: 'smooth' });
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;
        }, 80);
    }

    // 🚀 [V55.8] 核心能见度治理：统一管理不需要显示“全局保存”按钮的页面
    if (!window.updateSaveButtonVisibility) {
        window.updateSaveButtonVisibility = (catOrSub) => {
            const saveBtn = document.getElementById('btn-save-settings');
            if (!saveBtn) return;
            const noSaveTabs = ['imprints', 'themes', 'modes', 'layout', 'topology', 'logs', 'lessons'];
            saveBtn.style.display = noSaveTabs.includes(catOrSub) ? 'none' : 'flex';
        };
    }
    window.updateSaveButtonVisibility(actualCat);

    if (window.feBus) {
        window.feBus.emit('SETTINGS_RENDERED', actualCat);
    }
};

// 2. 配置保存
window.saveAllSettings = async () => {
    // 🛡️ [V106.0] 频道路由冲突前置拦截守卫 (防止保存损坏路由矩阵)
    if (typeof window.validateRouteMatrixBeforeSave === 'function') {
        const isValid = window.validateRouteMatrixBeforeSave();
        if (!isValid) return;
    }

    const saveBtn = document.getElementById('btn-save-settings');
    if (saveBtn) {
        if (saveBtn.disabled) return;
        saveBtn.disabled = true;
        saveBtn.dataset.originalText = saveBtn.innerText;
        saveBtn.innerText = '💾 保存中...';
    }

    try {
        addAudit("💾 正在打包全量主权配置快照...");

        // 🚚 [BlockCache] 检测缓存分级或目录变更
        let migrateCache = false;
        if (window.initialSettingsState) {
            try {
                const initialObj = JSON.parse(window.initialSettingsState);
                const oldShardLevels = initialObj['block_cache_shard_levels'];
                const newShardLevels = window.settingsData.block_cache_shard_levels;
                const oldCacheDir = initialObj['block_cache_dir'];
                const newCacheDir = window.settingsData.block_cache_dir;

                const levelsChanged = oldShardLevels !== undefined && oldShardLevels !== newShardLevels;
                const dirChanged = oldCacheDir !== undefined && oldCacheDir !== newCacheDir;

                if (levelsChanged || dirChanged) {
                    if (typeof Swal !== 'undefined') {
                        const result = await Swal.fire({
                            title: '⚠️ 检测到缓存配置变更',
                            html: `您已修改段落缓存配置：<br>` +
                                (levelsChanged ? `• 目录分级: <b>${oldShardLevels}级</b> ➡️ <b>${newShardLevels}级</b><br>` : '') +
                                (dirChanged ? `• 存储目录: <b>${oldCacheDir || '默认'}</b> ➡️ <b>${newCacheDir || '默认'}</b><br>` : '') +
                                `<br>为了避免已有翻译缓存失效导致重复请求大模型，建议对已有缓存进行物理迁移。是否执行迁移？`,
                            icon: 'warning',
                            showCancelButton: true,
                            showDenyButton: true,
                            background: 'hsla(236, 37%, 8%, 0.95)',
                            color: 'var(--text-bright, #ffffff)',
                            confirmButtonText: '🚚 迁移并保存 (推荐)',
                            denyButtonText: '⚙️ 仅保存配置',
                            cancelButtonText: '❌ 取消',
                            customClass: {
                                popup: 'glass-panel',
                                confirmButton: 'primary-btn glow-btn',
                                denyButton: 'secondary-btn',
                                cancelButton: 'danger-btn'
                            }
                        });

                        if (result.isDismissed) {
                            addAudit("❌ 已取消保存配置。", 'info');
                            return;
                        }
                        if (result.isConfirmed) {
                            migrateCache = true;
                        }
                    } else {
                        migrateCache = confirm("⚠️ 检测到段落缓存配置变更。是否在保存的同时物理迁移已有缓存文件？\n\n【确定】：迁移并保存\n【取消】：仅保存配置（原缓存会失效）");
                    }
                }
            } catch (err) {
                console.error('[BlockCache] 预检变更异常:', err);
            }
        }

        // 🔍 检测本次保存是否包含需重新编译装帧的属性变更
        let rebuildKeysChanged = [];
        if (window.initialSettingsState) {
            try {
                const initialObj = JSON.parse(window.initialSettingsState);
                const currentFlat = window.flattenObject(window.settingsData);
                for (const [k, v] of Object.entries(currentFlat)) {
                    if (initialObj[k] !== v && !k.split('.').some(p => p.startsWith('_'))) {
                        if (typeof window.resolveFieldEffectiveness === 'function' && window.resolveFieldEffectiveness(k) === 'rebuild') {
                            rebuildKeysChanged.push(k);
                        }
                    }
                }
            } catch(e) {}
        }

        const full = window.flattenObject(window.settingsData), payload = {};
        Object.keys(full).forEach(k => {
            if (!k.split('.').some(p => p.startsWith('_'))) payload[k] = full[k];
        });

        const url = `/api/config/update?migrate_cache=${migrateCache}`;
        const res = await apiFetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res && res.status === 'success') {
            if (rebuildKeysChanged.length > 0) {
                addAudit(`✅ 主权配置已持久化保存：检测到 ${rebuildKeysChanged.length} 项装帧与路由属性发生变更，将在下次「发布预览」或「全网发布」时编译生效。`, 'warning');
                if (typeof window.showToast === 'function') {
                    window.showToast(`💡 配置已保存！检测到装帧参数变更，需执行「发布预览」编译生效。`, 'info');
                } else if (window._showToast) {
                    window._showToast(`💡 配置已保存！检测到装帧参数变更，需执行「发布预览」编译生效。`, 'info');
                }
            } else {
                addAudit("✅ 全局主权配置已成功保存并即刻生效。", 'success');
                if (typeof window.showToast === 'function') {
                    window.showToast("✅ 配置已保存并即时热更新生效！", 'success');
                } else if (window._showToast) {
                    window._showToast("✅ 配置已保存并即时热更新生效！", 'success');
                }
            }
            if (res.active_config) {
                window.settingsData = { ...window.settingsData, ...res.active_config };

                // 🚀 [V57.1] 同步新的基准状态并重置按钮
                if (typeof window.getCleanConfig === 'function') {
                    window.initialSettingsState = window.getCleanConfig(window.settingsData);
                    if (typeof window.checkSettingsDirty === 'function') {
                        window.checkSettingsDirty();
                    }
                }

                if (window.currentActiveSettingsSubCat && typeof renderSettingsCategory === 'function') {
                    renderSettingsCategory(window.currentActiveSettingsSubCat);
                    if (window.currentActiveSettingsSubCat === 'general' && typeof window.refreshCacheStats === 'function') {
                        window.refreshCacheStats();
                    }
                }
                // 🚀 [V74.9] 全域对正：即时刷新侧边栏上下文
                if (typeof refreshGovernanceContext === 'function') {
                    await refreshGovernanceContext();
                }
                if (window.SovereignAgent && typeof window.SovereignAgent.initModelCapabilities === 'function') {
                    window.SovereignAgent.initModelCapabilities();
                }
            }
        } else {
            addAudit(`❌ 配置保存失败: ${res ? res.error : '未知故障'}`, 'error');
        }
    } finally {
        if (saveBtn) {
            saveBtn.innerText = saveBtn.dataset.originalText || '💾 保存配置';
            saveBtn.disabled = false;
        }
    }
};
