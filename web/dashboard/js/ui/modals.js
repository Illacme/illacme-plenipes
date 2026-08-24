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
                    </div>
                    <button class="close-btn" onclick="closeEditor()">×</button>
                </div>
                
                <!-- 💾 物理自动草稿自愈与保活挂载条 -->
                <div id="editor-draft-recovery-bar" class="glass-panel" style="display: none; align-items: center; justify-content: space-between; padding: 8px 15px; margin: 10px 20px 0 20px; border: 1px dashed var(--accent-secondary); background: rgba(0, 242, 255, 0.05); border-radius: 8px; flex-shrink: 0;">
                    <div style="display: flex; align-items: center; gap: 10px; font-size: 0.8rem;">
                        <span>💡</span>
                        <span style="color: var(--text-bright);">检测到您上次有未保存的本地草稿（备份于：<span id="editor-draft-time" style="color: var(--accent-secondary); font-family: var(--font-mono); font-weight: bold;">-</span>）。</span>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button class="mini-action-btn glow-btn" onclick="restoreScratchpadDraft()" style="border-color: var(--accent-secondary); color: var(--accent-secondary); font-size: 0.75rem; padding: 3px 10px; cursor: pointer;">💾 立即复苏草稿</button>
                        <button class="mini-action-btn" onclick="discardScratchpadDraft()" style="border-color: rgba(255,255,255,0.2); color: var(--text-dim); font-size: 0.75rem; padding: 3px 8px; cursor: pointer;">忽略</button>
                    </div>
                </div>
                
                <div class="editor-matrix" style="flex: 1; min-height: 0; overflow: hidden;">
                    <div class="editor-main" id="editor-container-main">
                        <div class="sector-header" style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px;">
                            <span>PRIMARY MANUSCRIPT CONTENT</span>
                            <!-- 🌓 [V87.0] 模式切换器 (Obsidian Style) -->
                            <div class="editor-mode-toggle" style="display: flex; gap: 5px; background: rgba(255,255,255,0.05); padding: 4px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); text-transform: none;">
                                <button class="mode-btn active" id="mode-source" onclick="setEditorMode('source')" title="源码模式">源码</button>
                                <button class="mode-btn" id="mode-wysiwyg" onclick="setEditorMode('wysiwyg')" title="可视化富文本编辑">视觉</button>
                                <button class="mode-btn" id="mode-preview" onclick="setEditorMode('preview')" title="阅读视图">阅读</button>
                                <button class="mode-btn" id="mode-split" onclick="setEditorMode('split')" title="实时预览">分栏</button>
                            </div>
                        </div>
                        <!-- 🚀 [V75.7] 紧贴上面横线与下面文章内容区的富文本工具栏 (WYSIWYG Toolbar) -->
                        <div id="editor-wysiwyg-toolbar" class="wysiwyg-toolbar" style="display: none; flex-wrap: wrap; gap: 4px; padding: 6px; background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; align-items: center; justify-content: flex-start; width: 100%; height: 36px; margin-top: -35px; margin-bottom: -20px; flex-shrink: 0; position: relative; z-index: 10;">
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('bold')" title="加粗" style="font-weight: bold;">B</button>
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('italic')" title="斜体" style="font-style: italic;">I</button>
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('formatBlock', 'h1')" style="font-weight: bold;">H1</button>
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('formatBlock', 'h2')" style="font-weight: bold;">H2</button>
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('formatBlock', 'h3')" style="font-weight: bold;">H3</button>
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('formatBlock', 'blockquote')" title="引用">“</button>
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('insertUnorderedList')" title="无序列表">• List</button>
                            <button type="button" class="toolbar-btn" onclick="window.execWysiwygCmd('insertOrderedList')" title="有序列表">1. List</button>
                            <button type="button" class="toolbar-btn" onclick="window.insertWysiwygLink()" title="插入超链接">🔗</button>
                            <button type="button" class="toolbar-btn" onclick="window.insertWysiwygWikiLink()" title="插入Wiki双链" style="font-family: monospace;">[[ ]]</button>
                        </div>

                        <div class="tactical-viewport" style="display: flex; flex: 1; min-height: 0; gap: 20px; position: relative;">
                            <textarea id="editor-body" class="tactical-editor" spellcheck="false" placeholder="等待数据载入..." oninput="updateEditorPreview()"></textarea>
                            
                            <!-- 🚀 [V75.7] 视觉模式下的富文本可编辑区 (高度、圆角和外边框与其它模式 100% 保持绝对一致) -->
                            <div id="editor-wysiwyg" class="tactical-preview markdown-body scroll-container" contenteditable="true" spellcheck="false" style="display: none; outline: none; line-height: 1.7; color: var(--text-bright); height: 100%;"></div>

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
                    <div class="terminal-container" style="flex: 1; background: var(--black-10); border-radius: 8px; border: 1px solid var(--glass-border); overflow: hidden; display: flex; flex-direction: column;">
                        <div class="terminal-header" style="background: var(--black-20); padding: 0.5rem 1rem; font-size: 0.7rem; color: var(--text-dim); border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between;">
                            <span>COMMAND CENTER / DIAGNOSTICS</span>
                            <span id="terminal-status">STANDBY</span>
                        </div>
                        <div id="terminal-toolbar" style="padding: 10px 1rem; background: var(--white-05); border-bottom: 1px solid var(--glass-border); display: flex; align-items: center; flex-wrap: nowrap !important;">
                            <button class="mini-action-btn" id="btn-modal-restart" onclick="invokeServiceAction('restart')" style="margin-right: 8px;"><span>🔄</span> 重启服务</button>
                            <button class="mini-action-btn" id="btn-modal-stop" onclick="invokeServiceAction('stop')" style="border-color: #ff4d4d; color: #ff4d4d; margin-right: 8px;"><span>⏹️</span> 停止服务</button>
                            <button class="mini-action-btn" id="btn-modal-open" onclick="window.open('http://localhost:43213', '_blank')" style="border-color: #00ff88; color: #00ff88; margin-right: 12px;"><span>🌐</span> 打开预览</button>
                            <div style="width: 1px; height: 18px; background: var(--glass-border); margin: 0 12px;"></div>
                            <button class="mini-action-btn" id="btn-modal-reinstall" onclick="invokeServiceAction('install')" style="border-color: #ffaa00; color: #ffaa00; margin-right: 8px;"><span>🏗️</span> 补全依赖</button>
                            <button class="mini-action-btn" id="btn-modal-upgrade" onclick="invokeServiceAction('upgrade')" style="border-color: var(--neon-cyan); color: var(--neon-cyan); margin-right: 8px;"><span>🆙</span> 升级版本</button>
                            <button class="mini-action-btn" id="btn-modal-rollback" onclick="invokeServiceAction('rollback')" style="border-color: #ff4d4d; color: #ff4d4d;"><span>⏪</span> 环境复原</button>
                            <div style="flex: 1;"></div>
                            <button class="mini-action-btn" onclick="document.getElementById('terminal-output').innerHTML = ''"><span>🗑️</span> 清空屏幕</button>
                        </div>
                        <div id="terminal-output" style="flex: 1; padding: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--text-bright); overflow-y: auto; line-height: 1.4; background: var(--black-10);"></div>
                    </div>
                </div>
                <div class="modal-footer" style="display: flex; flex-direction: column; align-items: center; width: 100%; padding: 0.4rem 1.5rem 1rem 1.5rem; gap: 0.8rem;">
                    <!-- ⚡ 强制覆盖选项条（常驻于发布按钮上方，绝不因日志滚动而丢失） -->
                    <div id="preview-force-sync-bar" style="display: none; width: 100%; max-width: 680px; background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 8px; padding: 8px 14px; align-items: center; justify-content: space-between; box-sizing: border-box;">
                        <label for="chk-preview-force-sync" style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.82rem; color: var(--text-bright); font-weight: 600; margin: 0; user-select: none;">
                            <input type="checkbox" id="chk-preview-force-sync" style="accent-color: var(--neon-cyan); width: 16px; height: 16px; cursor: pointer; margin: 0;">
                            <span>⚡ 强制全量覆盖同步 (Force Sync)</span>
                        </label>
                        <span style="font-size: 0.74rem; color: var(--text-muted);">
                            切换装帧主题或重构站点时推荐勾选 (复用已有 AI 译文缓存，0 算力开销)
                        </span>
                    </div>

                    <div style="display: flex; justify-content: center; width: 100%; gap: 1rem;">
                        <button class="primary-btn glow-btn" id="btn-terminal-start-preview" style="display: none; background: linear-gradient(135deg, #00f0ff 0%, #00ff88 100%); color: #000; font-weight: 700; border: none; box-shadow: 0 0 16px rgba(0, 240, 255, 0.4);" onclick="window.startPublishAndPreviewExecution()">⚡ 开始发布</button>
                        <button class="primary-btn glow-btn" id="btn-terminal-open-preview" style="display: none; background: linear-gradient(135deg, #00f0ff 0%, #00ff88 100%); color: #000; font-weight: 700; border: none; box-shadow: 0 0 16px rgba(0, 240, 255, 0.4);" onclick="window.openPreviewSite()">🌐 立即前往预览站点</button>
                        <button class="primary-btn glow-btn" id="btn-terminal-ok" style="display: none;" onclick="closeTerminalModal()">完成</button>
                        <button class="primary-btn glow-btn" id="btn-terminal-republish" style="display: none; background: var(--neon-cyan); color: #000;" onclick="window.republishFromTerminal()">🔄 重新发布</button>
                        <button class="secondary-btn" id="btn-terminal-abort" style="display: none; border-color: #ff4d4d; color: #ff4d4d;" onclick="window.abortSync()">🛑 中止同步</button>
                        <button class="secondary-btn" id="btn-terminal-close" onclick="closeTerminalModal()">隐藏窗口 (后台继续)</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 🏛️ Imprint Setup Wizard Modal (品牌配置向导) -->
        <div id="imprint-wizard-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content" style="max-width: 650px; width: 90%; height: auto; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; padding: 25px;">
                <div class="modal-header" style="margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.5rem;">🏛️</span>
                        <h2 style="margin: 0; font-size: 1.3rem; letter-spacing: 1px; color: var(--accent-primary);">新品牌配置向导 <span class="version-tag tiny">WIZARD</span></h2>
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
                                <b>品牌 (Imprint)</b> 是您在数字帝国中的物理发行单元。我们将为该品牌划定独立的内容文库、算力策略和分发链条。首先请确立其 Imprint 标识：
                            </p>
                        </div>
                        <div class="settings-grid" style="display: flex; flex-direction: column; gap: 15px;">
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-label">物理唯一标识符 (ID) <span class="tier-tag tier-global">全局</span></div>
                                    <div class="setting-desc">必须为英文/数字组合，用作物理文件夹及配置文件夹路径名称。</div>
                                </div>
                                <div class="setting-control">
                                    <input type="text" id="wiz-imprint-id" class="setting-input" placeholder="例如: tech-studio" style="width: 100%;">
                                    <div id="wiz-error-id" style="color: #ff4d4d; font-size: 0.75rem; margin-top: 5px; display: none; text-align: left;"></div>
                                </div>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-label">品牌展示名称 (Name) <span class="tier-tag tier-imprint">品牌</span></div>
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
                                品牌的底层资产存储在<b>文库 (Vault)</b> 目录中。您可以使用原有的文库，亦或是让系统为您一键自愈初始化全新的 Obsidian 资产金库。
                            </p>
                        </div>
                        <div class="settings-grid" style="display: flex; flex-direction: column; gap: 15px;">
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-label">内容文库 (Vault) 绝对物理路径 <span class="tier-tag tier-local">本地</span></div>
                                    <div class="setting-desc">输入您本地电脑的物理目录绝对路径。</div>
                                </div>
                                <div class="setting-control">
                                    <input type="text" id="wiz-vault-path" class="setting-input" placeholder="例如: /Users/username/my-obsidian-vault" style="width: 100%;">
                                    <div id="wiz-error-path" style="color: #ff4d4d; font-size: 0.75rem; margin-top: 5px; display: none; text-align: left;"></div>
                                </div>
                            </div>
                            <div class="setting-row" style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="setting-info" style="flex: 1; padding-right: 20px;">
                                    <div class="setting-label">🌱 自动灌入 Obsidian 标准自愈空间 <span class="tier-tag tier-local">本地</span></div>
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
                            <h4 style="margin-top: 0; color: var(--accent-primary); font-size: 0.9rem;">🏛️ 准备发射的出版品牌概要</h4>
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
