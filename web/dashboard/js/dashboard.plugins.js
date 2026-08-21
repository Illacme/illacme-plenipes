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
