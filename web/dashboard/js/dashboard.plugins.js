/**
 * 🧩 [V87.0] Illacme Plenipes Plugins & Capability Module (Hub Controller)
 * 职责：能力矩阵核心状态矩阵声明、全局开关管控与物理链路通道探测调度。
 */

// 1. 状态矩阵
window.activePluginCategory = 'all';
window.allPlugins = [];

// 2. 插件开关控制
window.togglePlugin = async (id, enable) => {
    try {
        const response = await fetch('/api/plugins/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, enable })
        });
        const result = await response.json();
        if (result.status === 'success') {
            addAudit(`🛡️ 能力治理：已${enable ? '激活' : '封锁'}插件 [${id}]`);
            if (typeof loadPlugins === 'function') await loadPlugins();
            
            // 🚀 [V80.2] 全域联动重绘：若当前位于系统治理的装帧主题选项卡，智能触发实时渲染以同步呼吸灯和状态条
            const activeTab = document.querySelector('.s-tab.active');
            if (activeTab && activeTab.dataset.cat === 'themes' && typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('themes');
            }
        } else {
            alert(`操作失败: ${result.error}`);
        }
    } catch (e) {
        console.error("Toggle error:", e);
    }
};

// 3. 物理链路探测
window.probePlugin = async (id) => {
    addAudit(`🛰️ 正在物理探测 [${id}] 链路状态...`);
    const res = await apiFetch('/api/plugins/probe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });

    if (res && res.success) {
        const dot = document.getElementById(`dot-${id}`);
        if (res.healthy) {
            addAudit(`✅ [${id}] 物理链路畅通。`);
            if (dot) {
                dot.classList.remove('blocked');
                dot.classList.add('healthy');
            }
        } else {
            addAudit(`❌ [${id}] 链路阻塞：${res.message || '物理连接失败或凭据无效。'}`, "error");
            if (dot) {
                dot.classList.remove('healthy');
                dot.classList.add('blocked');
            }
        }
    } else {
        addAudit(`⚠️ [${id}] 探测失败: ${res.error || '组件不支持物理自检'}`, "warning");
    }
};
