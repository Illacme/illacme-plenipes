/**
 * 🧩 [V75.2] Illacme Plenipes UI Modals Component
 * 职责：承载 publish-modal、editor-modal、terminal-modal 和 wizard-modal 的 HTML 结构。
 */
window.getUIModalsHTML = () => {
    return `
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
                        <p id="publish-step-desc" class="section-desc">正在初始化发布管道与 resource 对正...</p>
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

        <!-- 🏛️ Imprint Setup Wizard Modal (版图配置向导) -->
        <div id="imprint-wizard-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content" style="max-width: 650px; width: 90%; height: auto; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; padding: 25px;">
                <div class="modal-header" style="margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.5rem;">🏛️</span>
                        <h2 style="margin: 0; font-size: 1.3rem; letter-spacing: 1px; color: var(--accent-primary);">新版图配置向导 <span class="version-tag tiny">WIZARD</span></h2>
                    </div>
                    <button class="close-btn" onclick="closeImprintWizard()" style="position: static; margin-left: auto;">×</button>
                </div>
                
                <!-- 向导进度条标示 -->
                <div class="wizard-steps-indicator" style="display: flex; justify-content: space-between; margin-bottom: 30px; position: relative;">
                    <div class="step-line" style="position: absolute; top: 12px; left: 0; right: 0; height: 2px; background: rgba(255,255,255,0.08); z-index: 1;"></div>
                    <div class="step-line-active" id="wiz-progress-line" style="position: absolute; top: 12px; left: 0; width: 0%; height: 2px; background: var(--accent-primary); transition: width 0.3s ease; z-index: 2;"></div>
                    
                    <div class="wiz-step-node active" id="wiz-node-1" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 26px; height: 26px; border-radius: 50%; background: var(--card-bg); border: 2px solid var(--accent-primary); color: var(--text-bright); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: bold; transition: all 0.3s;">1</div>
                        <span style="font-size: 0.7rem; color: var(--text-bright); margin-top: 6px; font-weight: bold;">标识与意志</span>
                    </div>
                    <div class="wiz-step-node" id="wiz-node-2" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 26px; height: 26px; border-radius: 50%; background: var(--card-bg); border: 2px solid rgba(255,255,255,0.1); color: var(--text-dim); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: bold; transition: all 0.3s;">2</div>
                        <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 6px; font-weight: bold;">文库与自愈</span>
                    </div>
                    <div class="wiz-step-node" id="wiz-node-3" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 26px; height: 26px; border-radius: 50%; background: var(--card-bg); border: 2px solid rgba(255,255,255,0.1); color: var(--text-dim); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: bold; transition: all 0.3s;">3</div>
                        <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 6px; font-weight: bold;">意志对齐</span>
                    </div>
                </div>

                <div class="modal-body" style="flex: 1; overflow-y: auto; padding-right: 5px; margin-bottom: 20px; min-height: 250px;">
                    <!-- Step 1 Content -->
                    <div id="wiz-step-1" class="wizard-pane fade-in">
                        <div class="sovereign-memo glass-panel" style="margin-bottom: 20px; padding: 15px; border-left: 3px solid var(--accent-primary); background: rgba(163, 76, 255, 0.03);">
                            <p style="font-size: 0.8rem; color: var(--text-dim); margin: 0; line-height: 1.5;">
                                <b>版图 (Imprint)</b> 是您在数字帝国中的物理发行单元。我们将为该版图划定独立的内容文库、算力策略和分发链条。首先请确立其 brand 标识：
                            </p>
                        </div>
                        <div class="settings-grid" style="display: flex; flex-direction: column; gap: 15px;">
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-label">物理唯一标识符 (ID) <span class="tier-tag tier-global">系统宪法</span></div>
                                    <div class="setting-desc">必须为英文/数字组合，用作物理文件夹及配置文件夹路径名称。</div>
                                </div>
                                <div class="setting-control">
                                    <input type="text" id="wiz-imprint-id" class="setting-input" placeholder="例如: tech-studio" style="width: 100%;">
                                    <div id="wiz-error-id" style="color: #ff4d4d; font-size: 0.75rem; margin-top: 5px; display: none; text-align: left;"></div>
                                </div>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-label">版图展示名称 (Name) <span class="tier-tag tier-imprint">品牌主权</span></div>
                                    <div class="setting-desc">对外展示的文学出版社名号，随时可以更改。</div>
                                </div>
                                <div class="setting-control">
                                    <input type="text" id="wiz-imprint-name" class="setting-input" placeholder="例如: 科技未来前沿出版所" style="width: 100%;">
                                    <div id="wiz-error-name" style="color: #ff4d4d; font-size: 0.75rem; margin-top: 5px; display: none; text-align: left;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Step 2 Content -->
                    <div id="wiz-step-2" class="wizard-pane fade-in" style="display: none;">
                        <div class="sovereign-memo glass-panel" style="margin-bottom: 20px; padding: 15px; border-left: 3px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.03);">
                            <p style="font-size: 0.8rem; color: var(--text-dim); margin: 0; line-height: 1.5;">
                                版图的底层资产存储在<b>文库 (Vault)</b> 目录中。您可以使用原有的文库，亦或是让系统为您一键自愈初始化全新的 Obsidian 资产金库。
                            </p>
                        </div>
                        <div class="settings-grid" style="display: flex; flex-direction: column; gap: 15px;">
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-label">内容文库 (Vault) 绝对物理路径 <span class="tier-tag tier-local">物理本地</span></div>
                                    <div class="setting-desc">输入您本地电脑的物理目录绝对路径。</div>
                                </div>
                                <div class="setting-control">
                                    <input type="text" id="wiz-vault-path" class="setting-input" placeholder="例如: /Users/username/my-obsidian-vault" style="width: 100%;">
                                    <div id="wiz-error-path" style="color: #ff4d4d; font-size: 0.75rem; margin-top: 5px; display: none; text-align: left;"></div>
                                </div>
                            </div>
                            <div class="setting-row" style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="setting-info" style="flex: 1; padding-right: 20px;">
                                    <div class="setting-label">🌱 自动灌入 Obsidian 标准自愈空间 <span class="tier-tag tier-local">物理本地</span></div>
                                    <div class="setting-desc">若路径为空，我们将自动为您建立 Blog/Docs/Pages 三层资产文件夹，并生成首篇演示文章。</div>
                                </div>
                                <div class="setting-control">
                                    <label class="p-switch"><input type="checkbox" id="wiz-bootstrap-vault" checked><span class="p-slider"></span></label>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Step 3 Content -->
                    <div id="wiz-step-3" class="wizard-pane fade-in" style="display: none;">
                        <div class="sovereign-memo glass-panel" style="margin-bottom: 20px; padding: 15px; border-left: 3px solid var(--accent-primary); background: rgba(163, 76, 255, 0.03);">
                            <p style="font-size: 0.8rem; color: var(--text-dim); margin: 0; line-height: 1.5;">
                                <b>激活与对齐</b>：确认您的配置。系统将自动生成物理隔离的配置文件、复制提示词方言，并为您的内容库做好出版总线接入。
                            </p>
                        </div>
                        <div class="glass-panel" style="padding: 15px; background: rgba(0,0,0,0.25); border-radius: 8px; border: 1px solid var(--glass-border);">
                            <h4 style="margin-top: 0; color: var(--accent-primary); font-size: 0.9rem;">🏛️ 准备发射的出版版图概要</h4>
                            <div style="font-size: 0.8rem; line-height: 1.8; color: var(--text-dim);">
                                • <b>物理标识</b>: <span id="summary-id" style="color: var(--text-bright); font-weight: bold; font-family: monospace;">-</span><br>
                                • <b>出版品牌</b>: <span id="summary-name" style="color: var(--text-bright); font-weight: bold;">-</span><br>
                                • <b>物理文库路径</b>: <span id="summary-path" style="color: var(--text-bright); font-family: monospace; word-break: break-all;">-</span><br>
                                • <b>资产空间初始化</b>: <span id="summary-bootstrap" style="color: var(--accent-secondary); font-weight: bold;">-</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--glass-border); padding-top: 15px; margin-top: auto;">
                    <button class="secondary-btn" id="btn-wiz-prev" onclick="navigateWizard(-1)" style="visibility: hidden;">上一步</button>
                    <button class="primary-btn glow-btn" id="btn-wiz-next" onclick="navigateWizard(1)" style="min-width: 120px;">下一步</button>
                </div>
            </div>
        </div>
    `;
};
