/**
 * 🧩 [V87.0] Illacme Plenipes Plugins & Capability Module (Hub Controller)
 * 职责：能力矩阵核心状态矩阵声明、全局开关管控与物理链路通道探测调度。
 */

// 1. 状态矩阵
window.activePluginCategory = 'all';
window.allPlugins = [];

// 2. 插件开关控制
window.togglePlugin = async (id, enable, category = null) => {
    try {
        const response = await fetch('/api/plugins/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, enable, category })
        });
        const result = await response.json();
        if (result.status === 'success') {
            addAudit(`🛡️ 能力治理：已${enable ? '激活' : '封锁'}全局 [${id}] 物理驱动`);
            
            // 🚀 [V87.1] 同步更新全域配置，避免内存脏数据在保存时覆盖物理开关状态
            if (typeof apiFetch === 'function') {
                const res = await apiFetch('/api/system/config');
                if (res) {
                    window.settingsData = res.config || res;
                }
            }

            if (typeof loadPlugins === 'function') await loadPlugins(true);
            
            // 🚀 [V80.2] 全域联动重绘：若当前位于系统治理的装帧主题选项卡，智能触发实时渲染以同步呼吸灯和状态条
            if (window.currentActiveSettingsSubCat === 'themes' && typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('themes');
            }
            if (typeof window.refreshGovernanceContext === 'function') {
                await window.refreshGovernanceContext();
            }
        } else {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '⚠️ 物理锁定',
                    text: result.error || '无法切换物理驱动状态',
                    icon: 'warning',
                    allowOutsideClick: false,
                    allowEscapeKey: true,
                    background: 'var(--card-bg)',
                    color: 'var(--text-bright)',
                    confirmButtonText: '确定'
                });
            } else {
                alert(`操作失败: ${result.error}`);
            }
        }
    } catch (e) {
        console.error("Toggle error:", e);
    }
};

// 2b. 品牌激活快捷开关控制 (卡片外层一键切换)
window.toggleBrandActivation = async (id, checked, category) => {
    try {
        let path = "";
        if (category === 'hosting') {
            path = `publish_control.direct_upload.${id}.enabled`;
        } else if (category === 'publisher') {
            path = `syndication.${id}.enabled`;
        } else if (category === 'image_hosting') {
            path = `image_hosting.${id}.enabled`;
        } else if (category === 'notification') {
            path = `publish_control.webhook_endpoints.${id}.enabled`;
        } else {
            return;
        }

        // 🔒 [V80.2] 品牌激活探针守卫：与全局驱动启用门槛一致
        // 需要先通过「测试连接」确认配置有效，才允许品牌激活
        if (checked) {
            const needsProbe = ['hosting', 'publisher', 'image_hosting', 'notification'].includes(category);
            const isPassed = !!(window.probePassState && window.probePassState[id] === true);
            if (needsProbe && !isPassed) {
                // 回滚 checkbox 状态
                const el = document.querySelector(`input[onchange*="toggleBrandActivation('${id}'"]`);
                if (el) el.checked = false;
                setTimeout(() => {
                    const p = window.allPlugins ? window.allPlugins.find(x => x.id === id) : null;
                    const pluginName = p?.name || id;
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            title: '先验证一下配置 🔌',
                            html: `
                                <div style="text-align:left; line-height:1.75; font-size:0.92rem; color:var(--text-bright);">
                                    <p style="margin:0 0 12px 0;">启用 <b>${pluginName}</b> 之前，需要先确认它能够正常连接——这样才能保证发布时不会出错。</p>
                                    <div style="background:rgba(0,242,255,0.06); border:1px solid rgba(0,242,255,0.2); border-radius:8px; padding:10px 14px;">
                                        <b style="color:#00f2ff;">👇 下一步：</b>
                                        <span style="color:var(--text-dim);">点击「立即测试连接」，系统会自动帮你验证，通常只需几秒钟。</span>
                                    </div>
                                </div>`,
                            icon: 'info',
                            allowOutsideClick: true,
                            allowEscapeKey: true,
                            confirmButtonText: '⚡ 立即测试连接',
                            showCancelButton: true,
                            cancelButtonText: '稍后再说',
                            background: 'var(--card-bg)',
                            color: 'var(--text-bright)',
                            confirmButtonColor: 'var(--accent-secondary)',
                            showLoaderOnConfirm: true,
                            // 对话框内等待测试完成，通过后自动关闭
                            preConfirm: () => {
                                // 用 null 作「进行中」哨兵，与 false（失败）严格区分
                                window.probePassState = window.probePassState || {};
                                window.probePassState[id] = null;

                                // 触发卡片上的测试流程（传入真实按钮元素以获得进度反馈）
                                if (typeof window.fastTestPluginConnectivity === 'function') {
                                    const testBtn = document.querySelector(`.p-btn-test-direct[data-id="${id}"]`);
                                    window.fastTestPluginConnectivity(id, category, testBtn || null);
                                }

                                // 三态轮询：
                                //   null  → 测试进行中，继续等待
                                //   true  → 测试通过，立即 resolve 关闭弹窗
                                //   false → 测试失败（handler 写入），立即 reject 显示错误
                                return new Promise((resolve, reject) => {
                                    let _count = 0;
                                    const _poller = setInterval(() => {
                                        _count++;
                                        const state = window.probePassState?.[id];
                                        if (state === true) {
                                            clearInterval(_poller);
                                            resolve(true);
                                        } else if (state === false) {
                                            // 测试明确失败，立即结束等待
                                            clearInterval(_poller);
                                            reject('连接测试未通过，请进入 CONFIG 检查凭据配置后重试');
                                        } else if (_count > 100) { // 30 秒超时保护
                                            clearInterval(_poller);
                                            reject('连接测试超时，请检查网络或凭据后重试');
                                        }
                                    }, 300);
                                }).catch(msg => {
                                    Swal.showValidationMessage(`❌ ${msg}`);
                                    return false;
                                });
                            }

                        }).then((r) => {
                            // preConfirm resolve → r.value === true → 探针已通过，自动完成激活
                            if (r.isConfirmed && r.value === true) {
                                window.toggleBrandActivation(id, true, category);
                            }
                        });
                    } else if (window.showToast) {
                        window.showToast(`💡 请先点击 ${pluginName} 卡片底部的「⚡ 测试连接」，确认配置正常后再启用`, 'info');
                    }
                }, 30);
                return;
            }
        }

        // ⚡ [0ms 乐观即时响应] 同步修改内存中当前插件节点的 is_in_use 状态并即时刷新卡片
        if (window.allPlugins && Array.isArray(window.allPlugins)) {
            const targetP = window.allPlugins.find(p => p.id === id);
            if (targetP) {
                targetP.is_in_use = checked;
                if (typeof window.renderPlugins === 'function') {
                    window.renderPlugins();
                }
            }
        }

        if (!window.settingsData || Object.keys(window.settingsData).length === 0) {
            const res = await apiFetch('/api/system/config');
            if (res) {
                window.settingsData = res.config || res;
            }
        }

        // 修改内存中的扁平配置字段
        if (typeof window.updateConfigField === 'function') {
            window.updateConfigField(path, checked);
        }

        // 🏠 [V80.1] 全站托管插件自动主站分配逻辑
        // 规则：第一个被品牌启用的托管插件自动成为主站；停用主站时清空 primary_hosting_id
        if (category === 'hosting') {
            const primaryPath = 'publish_control.primary_hosting_id';
            if (!window.settingsData) window.settingsData = {};
            if (!window.settingsData.publish_control) window.settingsData.publish_control = {};
            const curPrimaryId = window.settingsData.publish_control.primary_hosting_id || '';

            if (checked && !curPrimaryId) {
                // 当前无主站 → 第一个启用者自动成为主站
                window.settingsData.publish_control.primary_hosting_id = id;
                if (typeof window.updateConfigField === 'function') {
                    window.updateConfigField(primaryPath, id);
                }
                await apiFetch('/api/config/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ [primaryPath]: id })
                });
                if (window.showToast) window.showToast(`🏠 [${id.toUpperCase()}] 已自动设为主站 (canonical)`, 'info');
            } else if (!checked && curPrimaryId === id) {
                // 停用的是主站 → 清空 primary_hosting_id
                window.settingsData.publish_control.primary_hosting_id = '';
                if (typeof window.updateConfigField === 'function') {
                    window.updateConfigField(primaryPath, '');
                }
                await apiFetch('/api/config/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ [primaryPath]: '' })
                });
                if (window.showToast) window.showToast(`主站 [${id.toUpperCase()}] 已停用，请重新指定主站`, 'info');
            }
        }

        // 🚀 [精准增量更新] 仅向后端提交目标字段变更，杜绝全量扁平化脏数据覆盖与副作用
        const payload = {
            [path]: checked
        };
        
        const response = await apiFetch('/api/config/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response && response.status === 'success') {
            if (typeof addAudit === 'function') {
                addAudit(`🟢 品牌配置联动：已在当前品牌下${checked ? '启用' : '停用'}了 [${id}] 能力`);
            }
            if (window.showToast) {
                window.showToast(`已在当前品牌下${checked ? '启用' : '停用'} [${id.toUpperCase()}] 能力`, 'info');
            }
            if (response.active_config) {
                window.settingsData = { ...window.settingsData, ...response.active_config };
            }
            if (typeof loadPlugins === 'function') await loadPlugins(true);
            if (typeof window.refreshGovernanceContext === 'function') {
                await window.refreshGovernanceContext();
            }
        } else {
            alert(`品牌激活失败: ${response ? response.error : '未知错误'}`);
            if (typeof loadPlugins === 'function') await loadPlugins(true);
        }
    } catch (e) {
        console.error("Brand toggle error:", e);
        if (typeof loadPlugins === 'function') await loadPlugins(true);
    }
};

// 3. 物理链路探测
window.probePlugin = async (id, category = null) => {
    addAudit(`🛰️ 正在物理探测 [${id}] 链路状态...`);
    const res = await apiFetch('/api/plugins/probe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, category })
    });

    window.probePassState = window.probePassState || {};
    if (res && res.success) {
        // 🚀 [V87.0] 优先选择精确包含 category 的状态灯 ID，兼容旧版本
        const dotId = category ? `dot-${category}-${id}` : `dot-${id}`;
        const dot = document.getElementById(dotId);
        if (res.healthy) {
            addAudit(`✅ [${id}] 物理链路畅通。`);
            window.probePassState[id] = true;
            if (dot) {
                dot.classList.remove('blocked');
                dot.classList.add('healthy');
            }
        } else {
            addAudit(`❌ [${id}] 链路阻塞：${res.message || '物理连接失败或凭据无效。'}`, "error");
            window.probePassState[id] = false;
            if (dot) {
                dot.classList.remove('healthy');
                dot.classList.add('blocked');
            }
        }
    } else {
        addAudit(`⚠️ [${id}] 探测失败: ${res.error || '组件不支持物理自检'}`, "warning");
        window.probePassState[id] = false;
    }
};

// 🏠 [V80.1] 手动切换主站：将指定托管平台设为 canonical 主站，其余自动降为镜像
window.setHostingAsPrimary = async (id, event) => {
    if (event) event.stopPropagation();
    try {
        const primaryPath = 'publish_control.primary_hosting_id';

        // 乐观更新内存 + 即时刷新卡片
        if (!window.settingsData) window.settingsData = {};
        if (!window.settingsData.publish_control) window.settingsData.publish_control = {};
        window.settingsData.publish_control.primary_hosting_id = id;
        if (typeof window.updateConfigField === 'function') {
            window.updateConfigField(primaryPath, id);
        }
        if (typeof window.renderPlugins === 'function') window.renderPlugins();

        // 写入后端
        const resp = await apiFetch('/api/config/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ [primaryPath]: id })
        });

        if (resp && resp.status === 'success') {
            if (window.showToast) window.showToast(`🏠 [${id.toUpperCase()}] 已切换为主站，其余为镜像站`, 'success');
            if (typeof addAudit === 'function') {
                addAudit(`🏠 主站切换：[${id}] 已成为 canonical 权威站，其他托管平台降级为镜像`);
            }
            if (resp.active_config) {
                window.settingsData = { ...window.settingsData, ...resp.active_config };
            }
        } else {
            if (window.showToast) window.showToast(`主站切换失败: ${resp ? resp.error : '未知错误'}`, 'error');
        }

        if (typeof loadPlugins === 'function') await loadPlugins(true);
    } catch (e) {
        console.error('setHostingAsPrimary error:', e);
    }
};
