/**
 * 🧩 [V75.2] Illacme Plenipes UI Drawers Component
 * 职责：承载 vault-drawer 和 plugin-drawer 的 HTML 结构。
 */
window.getUIDrawersHTML = () => {
    return `
        <!-- 📡 Dispatch Hub Backdrop Overlay (与社交广播一致的轻量半透明毛玻璃遮罩) -->
        <div id="vault-drawer-backdrop" style="position: fixed; inset: 0; background: rgba(0, 0, 0, 0.45); backdrop-filter: blur(2px); z-index: 9998; opacity: 0; pointer-events: none; transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);" onclick="window.closeVaultDrawer()"></div>

        <!-- 📡 Web Hosting & Publish Drawer (V68.0 Evolution: 现代右侧滑入抽屉) -->
        <div id="vault-drawer" class="glass-panel dispatch-hub-panel" style="position: fixed; top: 0; right: -480px; width: 440px; height: 100vh; background: rgba(15, 17, 26, 0.96); backdrop-filter: blur(16px); border-left: 1px solid var(--glass-border, rgba(255, 255, 255, 0.12)); box-shadow: -10px 0 35px rgba(0, 0, 0, 0.6); z-index: 9999; transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1); padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px; color: var(--text-bright, #fff); font-family: system-ui, -apple-system, sans-serif;">
            <!-- 1. 顶部 Header：左侧标题，右侧关闭按钮 (与社媒分发抽屉完全对齐) -->
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px;">
                <h3 style="margin: 0; font-size: 1.08rem; color: var(--accent-secondary, #00f2fe); display: flex; align-items: center; gap: 8px;">
                    🌐 网页托管发布
                </h3>
                <button type="button" onclick="window.closeVaultDrawer()" style="background: transparent; border: none; color: var(--text-dim); font-size: 1.4rem; cursor: pointer; line-height: 1;">×</button>
            </div>

            <!-- 2. 目标原稿独立卡片：深色微发光背景 -->
            <div style="font-size: 0.8rem; color: var(--text-dim); line-height: 1.4; background: rgba(255, 255, 255, 0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.06);">
                目标原稿：<b id="hub-doc-id" style="color: #fff; word-break: break-all;">PATH/TO/DOC.MD</b>
            </div>
            
            <div class="drawer-body" style="padding: 0; display: flex; flex-direction: column; gap: 14px; flex: 1; overflow-y: auto;">
                <!-- 🌐 Section 1: 全站托管与多语种网页装帧产物 (已剥离社媒，纯净全站托管) -->
                <div class="hub-section">
                    <div class="sector-header" style="display: flex; justify-content: space-between; align-items: center; width: 100%; font-size: 0.8rem; font-weight: 600; color: var(--accent-primary, #00f2fe); margin-bottom: 8px;">
                        <span>HOSTING & STATIC SITES</span>
                        <button id="btn-sync-all-channels" class="p-btn" style="display: none; padding: 3px 8px; font-size: 0.65rem; background: var(--accent-secondary); color: #000; border-radius: 4px; border: none; font-weight: 600; cursor: pointer; transition: all 0.2s;" onclick="window.triggerSyncAllChannels()" onmouseover="this.style.background='rgba(0, 242, 255, 0.8)'" onmouseout="this.style.background='var(--accent-secondary)'">🚀 发布全站托管</button>
                    </div>
                    <div id="hub-sync-matrix" class="matrix-list">
                        <!-- 矩阵通道动态列表将注入此处 -->
                    </div>
                </div>

                <!-- 📊 Section 2: 资产遥测与算力审计 -->
                <div class="hub-section">
                    <div class="sector-header" style="font-size: 0.8rem; font-weight: 600; color: var(--accent-primary, #00f2fe); margin-bottom: 8px;">ASSET TELEMETRY & AUDIT</div>
                    <div class="telemetry-grid">
                        <div class="t-pod">
                            <span class="t-label">ACCUMULATED COST</span>
                            <span id="hub-cost" class="t-value mono">--</span>
                        </div>
                        <div class="t-pod">
                            <span class="t-label">COMPUTE CORE</span>
                            <span id="hub-node" class="t-value">--</span>
                        </div>
                    </div>
                    <div id="hub-audit-status" class="audit-badge" style="margin-top: 10px;">⏳ 正在等待状态反馈...</div>
                    <div id="hub-audit-error" style="display: none; margin-top: 10px; padding: 10px; background: rgba(255, 76, 76, 0.08); border: 1px solid rgba(255, 76, 76, 0.2); border-radius: 6px; color: #ff6b6b; font-size: 0.75rem; line-height: 1.4; white-space: pre-wrap; word-break: break-all;"></div>
                </div>

                <!-- ⚡ Section 3: 本地实时预览服务 -->
                <div class="hub-section">
                    <div class="sector-header" style="font-size: 0.8rem; font-weight: 600; color: var(--accent-primary, #00f2fe); margin-bottom: 8px;">LIVE PREVIEW ENGINE</div>
                    
                    <div id="lab-control-panel" class="lab-box">
                        <div class="lab-status-row">
                            <span class="t-label">LOCAL PREVIEW ENGINE</span>
                            <span id="hub-lab-badge" class="badge">OFFLINE</span>
                        </div>
                        <button id="btn-toggle-lab" class="engine-btn start-mode" onclick="toggleThemeLab()">🔌 启动实时预览引擎 (LIVE PREVIEW)</button>
                    </div>
                </div>
            </div>

            <div class="drawer-footer hub-footer" style="display: flex; gap: 10px; width: 100%; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1); box-sizing: border-box;">
                <div class="sovereign-action-grid" style="display: flex; gap: 8px; width: 100%; align-items: center;">
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
        <div id="plugin-drawer" class="drawer-overlay" style="display: none; transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);" onclick="if (event.target === this) window.closePluginDrawer()">
            <div class="drawer-content glass-panel">
                <div class="drawer-header" style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h3 id="p-drawer-title" style="margin: 0;">⚙️ 插件能力</h3>
                        <span id="drawer-dirty-indicator" style="display: none; font-size: 0.65rem; color: #ffb700; font-weight: 700; background: rgba(255, 183, 0, 0.08); border: 1px solid rgba(255, 183, 0, 0.2); padding: 2px 6px; border-radius: 4px; white-space: nowrap;">● 💡 未保存</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div id="header-master-switch-wrapper" style="display: inline-flex; align-items: center; gap: 8px; padding: 3px 10px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 20px; backdrop-filter: blur(8px);">
                            <span id="header-toggle-status-label" style="font-size: 0.72rem; font-weight: 600; color: var(--text-dim);">全局驱动</span>
                            <label class="p-switch" style="margin: 0; transform: scale(0.82); transform-origin: center;" onclick="event.stopPropagation()">
                                <input type="checkbox" id="drawer-global-driver-toggle" onclick="event.stopPropagation()">
                                <span class="p-slider round"></span>
                            </label>
                        </div>
                        <!-- 右上角操作按钮：支持从社交广播工作流深度串联跳转时自动变身为「‹ 返回广播中枢」 -->
                        <button class="close-btn" id="close-p-drawer" onclick="window.handlePluginDrawerCloseClick()" style="background: transparent; border: none; color: var(--text-dim); font-size: 1.3rem; cursor: pointer; line-height: 1; padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;">×</button>
                    </div>
                </div>
                <div class="drawer-body" id="p-drawer-body">
                    <!-- 动态注入插件特定配置 -->
                </div>
                <div class="drawer-footer" style="display: flex; gap: 10px; width: 100%;">
                    <button class="secondary-btn" id="btn-reset-drawer-cfg" style="flex: 1; border: 1px dashed rgba(255, 77, 77, 0.4); color: #ff4d4d; background: rgba(255, 77, 77, 0.05); font-weight: 600;" onclick="window.resetCurrentDrawerFields()">🗑️ 清空重置</button>
                    <button class="secondary-btn" id="btn-restore-plugin-defaults" style="display: none; flex: 1; border: 1px solid #ff7b00; color: #ff7b00; background: rgba(255, 123, 0, 0.05); font-weight: 600;" onclick="restorePluginDefaults()">🧹 恢复默认</button>
                    <button class="secondary-btn" id="btn-dry-run-plugin" style="display: none; flex: 1; border: 1px solid var(--accent-secondary); color: var(--accent-secondary); background: rgba(0, 242, 255, 0.05); font-weight: 600;" onclick="triggerPluginDryRun()">🔌 测试连接</button>
                    <button class="primary-btn glow-btn" id="btn-save-plugin-cfg" style="flex: 1; font-weight: 600;" onclick="savePluginSettingsAndClose()">💾 保存配置</button>
                </div>
            </div>
        </div>
    `;
};

window.resetCurrentDrawerFields = () => {
    if (confirm("确认擦除当前配置抽屉中填写的所有文本框？")) {
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

