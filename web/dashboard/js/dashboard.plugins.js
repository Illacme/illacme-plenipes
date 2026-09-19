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
        if (typeof window.refreshGovernanceContext === 'function') {
            await window.refreshGovernanceContext();
        }
    } catch (e) {
        console.error('setHostingAsPrimary error:', e);
    }
};
