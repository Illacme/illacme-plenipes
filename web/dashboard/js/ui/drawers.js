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
                        <span id="hub-doc-id" class="tiny-label mono">PATH/TO/DOC.MD</span>
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
                        <div id="hub-audit-status" class="audit-badge" style="margin-top: 10px;">⏳ 正在等待状态反馈...</div>
                        <div id="hub-audit-error" style="display: none; margin-top: 10px; padding: 10px; background: rgba(255, 76, 76, 0.08); border: 1px solid rgba(255, 76, 76, 0.2); border-radius: 6px; color: #ff6b6b; font-size: 0.75rem; line-height: 1.4; white-space: pre-wrap; word-break: break-all;"></div>
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
                            <button class="hub-btn primary-hub-btn" onclick="triggerReDispatch('all', false)" title="对当前文档执行多语种重新分发（复用段落翻译缓存）">
                                <span class="btn-icon">♻️</span> 重新分发
                            </button>
                            <button class="hub-btn warning-hub-btn" onclick="triggerReDispatch('all', true)" title="无视已有的翻译缓存，强制调用大模型重新翻译此文档">
                                <span class="btn-icon">🧹</span> 强制重译
                            </button>
                            <button class="hub-btn danger-hub-btn" style="grid-column: span 2;" onclick="confirmPhysicalDelete()">
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
                <div class="drawer-header" style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center;">
                        <h3 id="p-drawer-title" style="margin: 0;">⚙️ 配置插件能力</h3>
                        <span id="drawer-dirty-indicator" style="display: none; font-size: 0.65rem; color: #ffb700; margin-left: 10px; font-weight: 700; background: rgba(255, 183, 0, 0.08); border: 1px solid rgba(255, 183, 0, 0.2); padding: 2px 6px; border-radius: 4px; white-space: nowrap;">● 💡 发现未保存更改</span>
                    </div>
                    <button class="close-btn" id="close-p-drawer" onclick="closePluginDrawer()">×</button>
                </div>
                <div class="drawer-body" id="p-drawer-body">
                    <!-- 动态注入插件特定配置 -->
                </div>
                <div class="drawer-footer" style="display: flex; gap: 10px; width: 100%;">
                    <button class="secondary-btn" id="btn-restore-plugin-defaults" style="display: none; flex: 1; border: 1px solid #ff7b00; color: #ff7b00; background: rgba(255, 123, 0, 0.05); font-weight: 600;" onclick="restorePluginDefaults()">🧹 恢复默认</button>
                    <button class="primary-btn glow-btn" id="btn-save-plugin-cfg" style="flex: 1;" onclick="savePluginSettingsAndClose()">💾 保存配置</button>
                    <button class="secondary-btn" id="btn-dry-run-plugin" style="display: none; flex: 1; border: 1px solid var(--accent-secondary); color: var(--accent-secondary); background: rgba(0, 242, 255, 0.05); font-weight: 600;" onclick="triggerPluginDryRun()">🧪 沙盘演练</button>
                </div>
            </div>
        </div>
    `;
};
