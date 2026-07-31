/**
 * ⌨️ [V80.1] Command Palette - Subtab & Action Commands Registry
 * 职责：独立承载 Command Palette 的全量控制指令注册表与动作处理。
 */

(function () {
    function notify(message, type = 'info') {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else if (window.Swal) {
            const Toast = window.Swal.mixin({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2200,
                timerProgressBar: true,
                background: 'rgba(20, 20, 20, 0.9)',
                color: '#fff',
                customClass: { popup: 'swal2-glass-toast' }
            });
            Toast.fire({ icon: type === 'error' ? 'error' : (type === 'warning' ? 'warning' : 'success'), title: message });
        } else {
            // 静默安全兜底
        }
    }

    window.getPaletteCommandsList = function() {
        return [
            {
                id: 'publish',
                title: '🚀 全域发布 (Trigger Full Syndication)',
                icon: '🚀',
                shortcut: 'Enter',
                action: () => {
                    if (typeof window.triggerPublish === 'function') {
                        window.triggerPublish();
                    } else {
                        notify('发布接口未就绪', 'error');
                    }
                }
            },
            {
                id: 'open_dispatch_hub',
                title: '📡 打开分发枢纽 (Open Dispatch Hub Drawer)',
                icon: '📡',
                shortcut: 'Enter',
                action: () => {
                    if (typeof window.openVaultDrawer === 'function') {
                        window.openVaultDrawer();
                        notify('已打开分发枢纽抽屉', 'info');
                    } else {
                        notify('分发枢纽组件未加载', 'warning');
                    }
                }
            },
            {
                id: 'subtab_identity',
                title: '🏷️ 基础运维 ➔ 身份标识 (Imprint & Site Identity)',
                icon: '🏷️',
                shortcut: 'Tab 2-1',
                action: () => {
                    if (typeof window.switchGeneralSubTab === 'function') {
                        window.switchGeneralSubTab('identity');
                        notify('已切换至【身份标识】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_compliance',
                title: '📖 基础运维 ➔ 出版合规 (Publishing Compliance & Metadata)',
                icon: '📖',
                shortcut: 'Tab 2-2',
                action: () => {
                    if (typeof window.switchGeneralSubTab === 'function') {
                        window.switchGeneralSubTab('compliance');
                        notify('已切换至【出版合规】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_storage',
                title: '📂 基础运维 ➔ 存储缓存 (Storage & LRU Janitor GC)',
                icon: '📂',
                shortcut: 'Tab 2-3',
                action: () => {
                    if (typeof window.switchGeneralSubTab === 'function') {
                        window.switchGeneralSubTab('storage');
                        notify('已切换至【存储缓存】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_engine',
                title: '⚙️ 基础运维 ➔ 系统基座 (Engine Base & Logs)',
                icon: '⚙️',
                shortcut: 'Tab 2-4',
                action: () => {
                    if (typeof window.switchGeneralSubTab === 'function') {
                        window.switchGeneralSubTab('engine');
                        notify('已切换至【系统基座】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_imprints',
                title: '🏷️ 品牌外观 ➔ 版图管理 (Imprints Management)',
                icon: '🏷️',
                shortcut: 'Tab 1-1',
                action: () => {
                    if (typeof window.switchLayoutSubTab === 'function') {
                        window.switchLayoutSubTab('imprints');
                        notify('已切换至【版图管理】画廊', 'success');
                    }
                }
            },
            {
                id: 'subtab_themes',
                title: '🎭 品牌外观 ➔ 装帧主题 (Themes Gallery)',
                icon: '🎭',
                shortcut: 'Tab 1-2',
                action: () => {
                    if (typeof window.switchLayoutSubTab === 'function') {
                        window.switchLayoutSubTab('themes');
                        notify('已切换至【装帧主题】画廊', 'success');
                    }
                }
            },
            {
                id: 'subtab_modes',
                title: '📋 品牌外观 ➔ 出版模式 (Publishing Modes)',
                icon: '📋',
                shortcut: 'Tab 1-3',
                action: () => {
                    if (typeof window.switchLayoutSubTab === 'function') {
                        window.switchLayoutSubTab('modes');
                        notify('已切换至【出版模式】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_localization',
                title: '🌍 多语路由 ➔ 翻译矩阵 (Localization Matrix)',
                icon: '🌍',
                shortcut: 'Tab 3-1',
                action: () => {
                    if (typeof window.switchI18nRoutingSubTab === 'function') {
                        window.switchI18nRoutingSubTab('localization');
                        notify('已切换至【翻译矩阵】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_translation_style',
                title: '🎭 多语路由 ➔ 翻译风格 (Translation Style)',
                icon: '🎭',
                shortcut: 'Tab 3-2',
                action: () => {
                    if (typeof window.switchI18nRoutingSubTab === 'function') {
                        window.switchI18nRoutingSubTab('translation_style');
                        notify('已切换至【翻译风格】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_slug_settings',
                title: '📝 多语路由 ➔ 网址路径 (Slug Settings)',
                icon: '📝',
                shortcut: 'Tab 3-3',
                action: () => {
                    if (typeof window.switchI18nRoutingSubTab === 'function') {
                        window.switchI18nRoutingSubTab('slug_settings');
                        notify('已切换至【网址路径】面板', 'success');
                    }
                }
            },
            {
                id: 'subtab_route_matrix',
                title: '🧭 多语路由 ➔ 频道映射 (Route Matrix)',
                icon: '🧭',
                shortcut: 'Tab 3-4',
                action: () => {
                    if (typeof window.switchI18nRoutingSubTab === 'function') {
                        window.switchI18nRoutingSubTab('route_matrix');
                        notify('已切换至【频道映射】面板', 'success');
                    }
                }
            },
            {
                id: 'toggle_preview',
                title: '👁️ 开启预览服务 (Live Preview Engine)',
                icon: '👁️',
                shortcut: 'Enter',
                action: () => {
                    if (typeof window.toggleThemeLab === 'function') {
                        window.toggleThemeLab();
                        notify('预览服务调起指令已发送', 'info');
                    } else {
                        notify('预览服务组件未加载', 'warning');
                    }
                }
            },
            {
                id: 'clean_orphans',
                title: '🧹 清理段落与临时缓存 (Clean Janitor Cache)',
                icon: '🧹',
                shortcut: 'Enter',
                action: () => {
                    if (typeof window.apiFetch === 'function') {
                        window.apiFetch('/api/governance/gc', { method: 'POST' })
                            .then(res => {
                                notify('✨ 成功触发算力与段落缓存清理！', 'success');
                                if (typeof window.addAudit === 'function') {
                                    window.addAudit("已触发悬空资产清理指令", "INFO");
                                }
                            })
                            .catch(err => {
                                console.error(err);
                                notify('清理指令发送失败', 'error');
                            });
                    } else {
                        notify('API 模块未就绪', 'error');
                    }
                }
            },
            {
                id: 'heal_and_reload',
                title: '🏥 一键环境自愈并软重载 (Auto-Heal & Reload System)',
                icon: '🏥',
                shortcut: 'Shift+R',
                action: () => {
                    notify('正在清理缓存并重启网关...', 'warning');
                    setTimeout(() => {
                        localStorage.clear();
                        sessionStorage.clear();
                        window.location.reload();
                    }, 400);
                }
            }
        ];
    };
})();
