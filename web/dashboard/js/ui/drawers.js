/**
 * 🧩 [V75.2] Illacme Plenipes UI Drawers Component
 * 职责：承载 vault-drawer 和 plugin-drawer 的 HTML 结构。
 */
window.getUIDrawersHTML = () => {
    return `
        <!-- 📡 Dispatch Hub Backdrop Overlay (与社交广播一致的轻量半透明毛玻璃遮罩) -->
        <div id="vault-drawer-backdrop" class="vault-drawer-backdrop" onclick="window.closeVaultDrawer()"></div>

        <!-- 📡 Web Hosting & Publish Drawer (V68.0 Evolution: 现代右侧滑入抽屉) -->
        <div id="vault-drawer" class="glass-panel dispatch-hub-panel drawer-shell vault-drawer-shell">
            <!-- 1. 顶部 Header：左侧标题，右侧关闭按钮 (与社媒分发抽屉完全对齐) -->
            <div class="drawer-header-row">
                <h3 class="drawer-header-title">
                    🌐 网页托管发布
                </h3>
                <button type="button" class="drawer-close-cross" onclick="window.closeVaultDrawer()">×</button>
            </div>

            <!-- 2. 目标原稿独立卡片：深色微发光背景 -->
            <div class="drawer-doc-card">
                <span class="drawer-doc-label">📄 目标原稿：</span><b id="hub-doc-id" class="drawer-doc-id">PATH/TO/DOC.MD</b>
            </div>
            
            <div class="drawer-body vault-drawer-body">
                <!-- 🌐 全站托管与多语种网页装帧产物 -->
                <div class="hub-section">
                    <div class="sector-header">
                        <span>🌐 网页装帧产物与全站托管平台 (HOSTING & STATIC SITES)</span>
                        <button id="btn-sync-all-channels" class="p-btn" style="display: none;" onclick="window.triggerSyncAllChannels()">🚀 发布全站托管</button>
                    </div>
                    <div id="hub-sync-matrix" class="matrix-list">
                        <!-- 矩阵通道动态列表将注入此处 -->
                    </div>
                </div>
            </div>

            <div class="drawer-footer hub-footer">
                <div id="vault-hosting-live-deploy-pod" class="vault-live-deploy-pod" style="display: none;"></div>
                <div class="sovereign-action-grid">
                    <button class="hub-btn primary-hub-btn" style="flex: 1;" onclick="if (typeof window.dispatchVaultHostingSelection === 'function') { window.dispatchVaultHostingSelection(window.currentDocId); } else { triggerReDispatch('all', false); }" title="一键向已勾选的全站托管平台发布更新">
                        <span class="btn-icon">🚀</span> 开始全站托管发布
                    </button>
                    <button class="hub-btn warning-hub-btn" style="flex: 1; display: none;" onclick="triggerReDispatch('all', true)" title="强制重新装帧编译并重新翻译多语种网页">
                        <span class="btn-icon">🧹</span> 强制重译
                    </button>
                    <button type="button" class="hub-btn danger-hub-btn" style="flex: 1;" onclick="event.preventDefault(); event.stopPropagation(); confirmPhysicalDelete()" title="物理抹除磁盘文件与出版产物">
                        <span class="btn-icon">🗑️</span> 物理销毁
                    </button>
                </div>
            </div>
        </div>

        <!-- 🧩 Plugin Config Drawer -->
        <div id="plugin-drawer" class="drawer-overlay plugin-drawer-overlay" onclick="if (event.target === this) window.closePluginDrawer()">
            <div class="drawer-content glass-panel">
                <div class="drawer-header plugin-drawer-header">
                    <div class="plugin-drawer-title-group">
                        <h3 id="p-drawer-title" class="plugin-drawer-title">⚙️ 插件能力</h3>
                        <span id="drawer-dirty-indicator" class="dirty-indicator-badge plugin-dirty-badge">● 💡 未保存</span>
                    </div>
                    <div class="plugin-drawer-actions-group">
                        <div id="header-master-switch-wrapper" class="master-switch-wrap plugin-master-switch">
                            <span id="header-toggle-status-label" class="plugin-toggle-label">全局驱动</span>
                            <label class="p-switch" style="margin: 0; transform: scale(0.82); transform-origin: center;" onclick="event.stopPropagation()">
                                <input type="checkbox" id="drawer-global-driver-toggle" onclick="event.stopPropagation()">
                                <span class="p-slider round"></span>
                            </label>
                        </div>
                        <!-- 右上角操作按钮：支持从社交广播工作流深度串联跳转时自动变身为「‹ 返回广播中枢」 -->
                        <button class="close-btn plugin-close-btn" id="close-p-drawer" onclick="window.handlePluginDrawerCloseClick()">×</button>
                    </div>
                </div>
                <div class="drawer-body" id="p-drawer-body">
                    <!-- 动态注入插件特定配置 -->
                </div>
                <div class="drawer-footer plugin-drawer-footer">
                    <button class="secondary-btn plugin-btn-reset" id="btn-reset-drawer-cfg" onclick="window.resetCurrentDrawerFields()">🗑️ 清空重置</button>
                    <button class="secondary-btn plugin-btn-restore" id="btn-restore-plugin-defaults" style="display: none;" onclick="restorePluginDefaults()">🧹 恢复默认</button>
                    <button class="secondary-btn plugin-btn-dryrun" id="btn-dry-run-plugin" style="display: none;" onclick="triggerPluginDryRun()">🔌 测试连接</button>
                    <button class="primary-btn glow-btn plugin-btn-save" id="btn-save-plugin-cfg" onclick="savePluginSettingsAndClose()">💾 保存配置</button>
                </div>
            </div>
        </div>
    `;
};

window.resetCurrentDrawerFields = async () => {
    let ok = false;
    if (typeof window.confirmSovereignAction === 'function') {
        ok = await window.confirmSovereignAction({
            title: '🧹 擦除抽屉配置',
            text: '确认擦除当前配置抽屉中填写的所有文本框？<br>已输入的草稿参数将被清空。',
            icon: 'warning',
            confirmText: '确认清空',
            confirmColor: '#ff4d4f'
        });
    } else {
        ok = confirm("确认擦除当前配置抽屉中填写的所有文本框？");
    }
    if (ok) {
        const body = document.getElementById('p-drawer-body');
        if (!body) return;
        body.querySelectorAll('input[type="text"], input[type="password"], textarea').forEach(input => {
            input.value = '';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
        if (window.showToast) window.showToast("已清空擦除草稿参数", "info");
    }
};

// ⌨️ 全局 Escape 按键栈式一键关闭抽屉面板
window.addEventListener('keyup', (e) => {
    if (e.key === 'Escape') {
        const vDrawer = document.getElementById('vault-drawer');
        const pDrawer = document.getElementById('plugin-drawer');
        if (vDrawer && vDrawer.style.display !== 'none') {
            window.closeVaultDrawer();
            e.stopPropagation();
            return;
        }
        if (pDrawer && pDrawer.style.display !== 'none') {
            if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
            e.stopPropagation();
            return;
        }
    }
});

