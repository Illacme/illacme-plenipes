/**
 * 🧩 [V1.0] Illacme Plenipes Plugins Brand Activation Shard
 * 职责：品牌激活快捷开关控制（卡片外层一键切换、探针守卫、乐观响应、主站自动选举与增量同步）。
 */

(function () {
    'use strict';

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
            } else if (category === 'tunnel') {
                path = `tunnel.${id}.enabled`;
            } else {
                return;
            }

            // 🛡️ [V127.0] 凭据就绪首道物理门禁：未填必要参数严禁在品牌中启用
            const p = window.allPlugins ? window.allPlugins.find(x => x.id === id) : null;
            const pluginName = p?.name || id;

            let credState = { ready: true };
            if (typeof window.isPluginCredentialReady === 'function') {
                credState = window.isPluginCredentialReady(id, category, p?.cfg) || { ready: true };
            }

            if (checked && !credState.ready) {
                const el = document.querySelector(`input[id="chk-use-${category}-${id}"]`) || document.querySelector(`input[onchange*="toggleBrandActivation('${id}'"]`);
                if (el) el.checked = false;
                setTimeout(() => {
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            title: '请先完成参数配置 ⚙️',
                            html: `
                                <div style="text-align:left; line-height:1.75; font-size:0.92rem; color:var(--text-bright);">
                                    <p style="margin:0 0 12px 0;"><b>${pluginName}</b> 尚未配置必要密钥或连接参数（<span style="color:#ffb86c; font-weight:600;">${credState.label || '待配置'}</span>），无法在当前品牌中启用。</p>
                                    <div style="background:rgba(255,184,108,0.08); border:1px solid rgba(255,184,108,0.25); border-radius:8px; padding:10px 14px;">
                                        <b style="color:#ffb86c;">💡 规范流程：</b>
                                        <span style="color:var(--text-dim);">请先点击该插件卡片下方的 <b>[⚙️ CONFIG]</b> 填入必要凭据，保存并验证通过后即可一键启用。</span>
                                    </div>
                                </div>`,
                            icon: 'warning',
                            confirmButtonText: '⚙️ 立即前往配置',
                            showCancelButton: true,
                            cancelButtonText: '稍后再说',
                            background: 'var(--card-bg)',
                            color: 'var(--text-bright)',
                        }).then((res) => {
                            if (res.isConfirmed) {
                                if (typeof window.openPluginConfig === 'function') {
                                    window.openPluginConfig(id, category);
                                }
                            }
                        });
                    } else if (window.showToast) {
                        window.showToast(`请先点击 [CONFIG] 配置 ${pluginName} 后再启用`, 'warning');
                    }
                }, 50);
                return;
            }

            // 🔒 [V80.2] 品牌激活探针守卫：与全局驱动启用门槛一致
            // 免密零依赖驱动（如 localhost_run / serveo / pinggy / catbox / tailscale 或 zero_config 模式）直接激活；其余需通过探针测试
            const isZeroConfig = ['localhost_run', 'serveo', 'pinggy', 'catbox', 'tailscale'].includes(id) || credState?.mode === 'zero_config';
            if (checked && !isZeroConfig) {
                const needsProbe = ['hosting', 'publisher', 'image_hosting', 'notification', 'tunnel'].includes(category);
                const isPassed = !!(window.probePassState && window.probePassState[id] === true);
                if (needsProbe && !isPassed) {
                    // 回滚 checkbox 状态
                    const el = document.querySelector(`input[id="chk-use-${category}-${id}"]`) || document.querySelector(`input[onchange*="toggleBrandActivation('${id}'"]`);
                    if (el) el.checked = false;
                    setTimeout(() => {
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
            if (category === 'tunnel') {
                if (checked) {
                    payload['tunnel.active_driver'] = id;
                    if (typeof window.updateConfigField === 'function') window.updateConfigField('tunnel.active_driver', id);
                } else if (window.settingsData?.tunnel?.active_driver === id) {
                    payload['tunnel.active_driver'] = '';
                    if (typeof window.updateConfigField === 'function') window.updateConfigField('tunnel.active_driver', '');
                }
            }
            
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

    window.openPluginDrawer = (id, category = null) => {
        if (typeof window.openPluginConfig === 'function') {
            window.openPluginConfig(id, category);
        }
    };

})();
