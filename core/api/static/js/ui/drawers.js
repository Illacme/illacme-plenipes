/**
 * 🧩 [V75.2] Illacme Plenipes UI Drawers Component
 * 职责：承载 vault-drawer 和 plugin-drawer 的 HTML 结构。
 */
window.getUIDrawersHTML = () => {
    return `
        <!-- 📡 Dispatch Hub Drawer (V68.0 Evolution) -->
        <div id="vault-drawer" class="drawer-overlay" style="display: none;">
            <div class="drawer-content glass-panel dispatch-hub-panel">
                <div class="drawer-header">
                    <div style="display:flex; flex-direction:column;">
                        <h3 style="margin:0;">📡 分发枢纽 / DISPATCH HUB</h3>
                        <span id="hub-doc-id" class="tiny-label mono" style="opacity:0.5;">PATH/TO/DOC.MD</span>
                    </div>
                    <button class="close-btn" id="close-drawer" onclick="closeVaultDrawer()">×</button>
                </div>
                
                <div class="drawer-body" style="padding-top:10px;">
                    <!-- 🛰️ Section 1: Global Sync Matrix -->
                    <div class="hub-section">
                        <div class="sector-header">GLOBAL SYNC MATRIX</div>
                        <div id="hub-sync-matrix" class="matrix-list">
                            <!-- Mock 列表将注入此处 -->
                        </div>
                    </div>

                    <!-- 📊 Section 2: Asset Telemetry -->
                    <div class="hub-section">
                        <div class="sector-header">ASSET TELEMETRY & AUDIT</div>
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
                        <div id="hub-audit-status" class="audit-badge">WAITING FOR SENSOR...</div>
                    </div>

                    <!-- 🛡️ Section 3: Sovereign Actions -->
                    <div class="hub-section" style="margin-top:auto;">
                        <div class="sector-header">SOVEREIGN ACTIONS</div>
                        
                        <div id="lab-control-panel" class="lab-box">
                            <div class="lab-status-row">
                                <span class="t-label">LIVE PREVIEW ENGINE</span>
                                <span id="hub-lab-badge" class="badge">OFFLINE</span>
                            </div>
                            <button id="btn-toggle-lab" class="engine-btn start-mode" onclick="toggleThemeLab()">🔌 启动实时预览引擎 (LIVE PREVIEW)</button>
                        </div>

                        <div class="sovereign-action-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                            <button class="hub-btn primary-hub-btn" onclick="triggerReDispatch('all')">
                                <span class="btn-icon">♻️</span> 强制重新发布
                            </button>
                            <button class="hub-btn danger-hub-btn" onclick="confirmPhysicalDelete()">
                                <span class="btn-icon">🗑️</span> 物理销毁
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 🧩 Plugin Config Drawer -->
        <div id="plugin-drawer" class="drawer-overlay" style="display: none;">
            <div class="drawer-content glass-panel">
                <div class="drawer-header">
                    <h3 id="p-drawer-title">⚙️ 配置插件能力</h3>
                    <button class="close-btn" id="close-p-drawer" onclick="closePluginDrawer()">×</button>
                </div>
                <div class="drawer-body" id="p-drawer-body">
                    <!-- 动态注入插件特定配置 -->
                </div>
                <div class="drawer-footer" style="display: flex; gap: 10px; width: 100%;">
                    <button class="primary-btn glow-btn" id="btn-save-plugin-cfg" style="flex: 1;" onclick="savePluginSettingsAndClose()">💾 保存配置</button>
                    <button class="secondary-btn" id="btn-dry-run-plugin" style="display: none; flex: 1; border: 1px solid var(--accent-secondary); color: var(--accent-secondary); background: rgba(0, 242, 255, 0.05); font-weight: 600;" onclick="triggerPluginDryRun()">🧪 沙盘演练</button>
                </div>
            </div>
        </div>
    `;
};
