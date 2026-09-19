/**
 * ⚙️ [V1.0] Illacme Plenipes System & Governance - Save Settings Shard
 * 职责：主权配置保存、段落缓存分级迁移预检、装帧重新编译检测与即时热生效。
 */

(function () {
    'use strict';

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
            if (typeof addAudit === 'function') addAudit("💾 正在打包全量主权配置快照...");

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
                                if (typeof addAudit === 'function') addAudit("❌ 已取消保存配置。", 'info');
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
                    const currentFlat = window.flattenObject ? window.flattenObject(window.settingsData) : {};
                    for (const [k, v] of Object.entries(currentFlat)) {
                        if (initialObj[k] !== v && !k.split('.').some(p => p.startsWith('_'))) {
                            if (typeof window.resolveFieldEffectiveness === 'function' && window.resolveFieldEffectiveness(k) === 'rebuild') {
                                rebuildKeysChanged.push(k);
                            }
                        }
                    }
                } catch(e) {}
            }

            const full = window.flattenObject ? window.flattenObject(window.settingsData) : window.settingsData;
            const payload = {};
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
                    if (typeof addAudit === 'function') addAudit(`✅ 主权配置已持久化保存：检测到 ${rebuildKeysChanged.length} 项装帧与路由属性发生变更，将在下次「发布预览」或「全网发布」时编译生效。`, 'warning');
                    if (typeof window.showToast === 'function') {
                        window.showToast(`💡 配置已保存！检测到装帧参数变更，需执行「发布预览」编译生效。`, 'info');
                    } else if (window._showToast) {
                        window._showToast(`💡 配置已保存！检测到装帧参数变更，需执行「发布预览」编译生效。`, 'info');
                    }
                } else {
                    if (typeof addAudit === 'function') addAudit("✅ 全局主权配置已成功保存并即刻生效。", 'success');
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
                if (typeof addAudit === 'function') addAudit(`❌ 配置保存失败: ${res ? res.error : '未知故障'}`, 'error');
            }
        } finally {
            if (saveBtn) {
                saveBtn.innerText = saveBtn.dataset.originalText || '💾 保存配置';
                saveBtn.disabled = false;
            }
        }
    };

})();
