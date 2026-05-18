/**
 * 🎭 [V57.0] Illacme Plenipes UI Component Hub
 * 职责：渲染全局 UI 组件（如弹窗、抽屉），维持 index.html 的极简状态。
 */

window.renderUIComponents = () => {
    const appContainer = document.getElementById('app-container');
    if (!appContainer) return;

    const componentsHTML = `
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
                <div class="drawer-footer">
                    <button class="primary-btn glow-btn" id="btn-save-plugin-cfg">💾 固化插件配置</button>
                </div>
            </div>
        </div>

        <!-- 🚀 Publishing Modal -->
        <div id="publish-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content publish-modal-content">
                <div class="modal-header">
                    <h2>🚀 正在执行同步出版任务</h2>
                    <button class="close-btn" onclick="closePublishModal()">×</button>
                </div>
                <div class="modal-body publish-modal-body">
                    <div class="publish-status-main">
                        <div class="pulsing-icon">🛰️</div>
                        <h3 id="publish-step-title">正在准备物理环境...</h3>
                        <p id="publish-step-desc" class="section-desc">正在初始化发布管道与资源对正...</p>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div id="publish-progress" class="progress-fill"></div>
                        </div>
                        <div class="progress-info">
                            <span id="publish-percentage">0%</span>
                            <span id="publish-time-elapsed">用时: 0s</span>
                        </div>
                    </div>
                    <div id="publish-logs" class="terminal-mini-box"></div>
                </div>
                <div class="modal-footer centered">
                    <button class="secondary-btn" id="btn-cancel-publish" onclick="closePublishModal()">关闭窗口</button>
                </div>
            </div>
        </div>

        <!-- 📝 Document Editor Modal: Tactical Intelligence Terminal -->
        <div id="editor-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content" style="width: 90%; height: 85%; max-width: 1200px; display: flex; flex-direction: column;">
                <div class="modal-header">
                    <div style="display:flex; align-items:center; gap:15px;">
                        <span style="font-size:1.2rem;">📝</span>
                        <h2 id="editor-title" style="margin:0;">EDITOR</h2>
                        <!-- 🌓 [V87.0] 模式切换器 (Obsidian Style) -->
                        <div class="editor-mode-toggle" style="margin-left: 30px; display: flex; gap: 5px; background: rgba(255,255,255,0.05); padding: 4px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                            <button class="mode-btn active" id="mode-source" onclick="setEditorMode('source')" title="源码模式">源码</button>
                            <button class="mode-btn" id="mode-preview" onclick="setEditorMode('preview')" title="阅读视图">阅读</button>
                            <button class="mode-btn" id="mode-split" onclick="setEditorMode('split')" title="实时预览">分栏</button>
                        </div>
                    </div>
                    <button class="close-btn" onclick="closeEditor()">×</button>
                </div>
                
                <div class="editor-matrix" style="flex: 1; min-height: 0; overflow: hidden;">
                    <div class="editor-main" id="editor-container-main">
                        <div class="sector-header">PRIMARY MANUSCRIPT CONTENT</div>
                        <div class="tactical-viewport" style="display: flex; flex: 1; min-height: 0; gap: 20px;">
                            <textarea id="editor-body" class="tactical-editor" spellcheck="false" placeholder="等待数据载入..." oninput="updateEditorPreview()"></textarea>
                            <div id="editor-preview" class="tactical-preview markdown-body" style="display: none;"></div>
                        </div>
                    </div>
                    <div class="editor-sidebar">
                        <div class="sector-header">PHYSICAL METADATA</div>
                        
                        <!-- 🚀 [NEW] 滚动元数据包装区 (V87.2) -->
                        <div id="metadata-scroll-wrapper" style="flex: 1; overflow-y: auto; padding-right: 5px; display: flex; flex-direction: column; gap: 20px; min-height: 0;">
                            <div class="drawer-item" style="flex-shrink: 0;">
                                <label class="tiny-label">ASSET TITLE</label>
                                <input type="text" id="editor-meta-title" class="setting-input">
                            </div>
                            <div class="drawer-item" style="flex-shrink: 0;">
                                <label class="tiny-label">PERMALINK SLUG</label>
                                <input type="text" id="editor-meta-slug" class="setting-input">
                            </div>

                            <!-- 🚀 [NEW] 动态元数据容器 (V68.0) -->
                            <div id="dynamic-metadata-container" style="display: flex; flex-direction: column; gap: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; margin-top: 5px;">
                                <!-- 动态注入项将出现在这里 -->
                            </div>
                        </div>
                        
                        <div style="margin-top:auto; display:flex; flex-direction:column; gap:10px; flex-shrink: 0; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;">
                            <div id="save-status" style="font-size:0.7rem; color:var(--accent-secondary); font-family:var(--font-mono); text-align:center;"></div>
                            <button class="primary-btn glow-btn" id="btn-save-doc" style="width:100%;">💾 COMMIT CHANGES</button>
                            <button class="secondary-btn" onclick="closeEditor()" style="width:100%;">CANCEL</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 🏗️ Terminal Modal for Installation -->
        <div id="terminal-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content" style="max-width: 800px; width: 90%; height: 500px; display: flex; flex-direction: column; overflow: hidden;">
                <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <h2 id="terminal-title">🏗️ 正在准备框架依赖环境</h2>
                    <button class="close-btn" onclick="closeTerminalModal()" style="position: static; margin-left: auto;">×</button>
                </div>
                <div class="modal-body" style="padding: 0.5rem 1rem 0 1rem; flex: 1; display: flex; flex-direction: column; overflow: hidden;">
                    <div class="terminal-container" style="flex: 1; background: #0c0c0c; border-radius: 8px; border: 1px solid #333; overflow: hidden; display: flex; flex-direction: column;">
                        <div class="terminal-header" style="background: #1a1a1a; padding: 0.5rem 1rem; font-size: 0.7rem; color: #888; border-bottom: 1px solid #333; display: flex; justify-content: space-between;">
                            <span>COMMAND CENTER / DIAGNOSTICS</span>
                            <span id="terminal-status">STANDBY</span>
                        </div>
                        <div id="terminal-toolbar" style="padding: 10px 1rem; background: rgba(0,0,0,0.3); border-bottom: 1px solid #333; display: flex; align-items: center; flex-wrap: nowrap !important;">
                            <button class="mini-action-btn" id="btn-modal-restart" onclick="invokeServiceAction('restart')" style="margin-right: 8px;"><span>🔄</span> 重启服务</button>
                            <button class="mini-action-btn" id="btn-modal-open" onclick="window.open('http://localhost:43213', '_blank')" style="border-color: #00ff88; color: #00ff88; margin-right: 12px;"><span>🌐</span> 打开预览</button>
                            <div style="width: 1px; height: 18px; background: #444; margin: 0 12px;"></div>
                            <button class="mini-action-btn" id="btn-modal-reinstall" onclick="invokeServiceAction('install')" style="border-color: #ffaa00; color: #ffaa00; margin-right: 8px;"><span>🏗️</span> 补全依赖</button>
                            <button class="mini-action-btn" id="btn-modal-upgrade" onclick="invokeServiceAction('upgrade')" style="border-color: var(--neon-cyan); color: var(--neon-cyan); margin-right: 8px;"><span>🆙</span> 升级版本</button>
                            <button class="mini-action-btn" id="btn-modal-rollback" onclick="invokeServiceAction('rollback')" style="border-color: #ff4d4d; color: #ff4d4d;"><span>⏪</span> 环境复原</button>
                            <div style="flex: 1;"></div>
                            <button class="mini-action-btn" onclick="document.getElementById('terminal-output').innerHTML = ''"><span>🗑️</span> 清空屏幕</button>
                        </div>
                        <div id="terminal-output" style="flex: 1; padding: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #d1d1d1; overflow-y: auto; line-height: 1.4;"></div>
                    </div>
                </div>
                <div class="modal-footer" style="display: flex; justify-content: center; width: 100%; padding: 0.4rem 0 1rem 0; gap: 1rem;">
                    <button class="primary-btn glow-btn" id="btn-terminal-ok" style="display: none;" onclick="closeTerminalModal()">完成</button>
                    <button class="secondary-btn" id="btn-terminal-close" onclick="closeTerminalModal()">隐藏窗口 (后台继续)</button>
                </div>
            </div>
        </div>
    `;

    // 注入到 app-container 末尾
    appContainer.insertAdjacentHTML('beforeend', componentsHTML);
};
