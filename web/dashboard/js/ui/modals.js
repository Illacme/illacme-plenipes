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

        <!-- 🏛️ Imprint Setup Wizard Modal (出版品牌创建向导) -->
        <div id="imprint-wizard-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content" style="max-width: 630px; width: 92%; height: auto; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; padding: 14px 18px;">
                <div class="modal-header" style="margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.25rem;">🏛️</span>
                        <h2 style="margin: 0; font-size: 1.1rem; letter-spacing: 0.5px; color: var(--accent-primary);">出版品牌创建向导 <span class="version-tag tiny">WIZARD</span></h2>
                    </div>
                    <button class="close-btn" onclick="closeImprintWizard()" style="position: static; margin-left: auto;">×</button>
                </div>
                
                <!-- 向导进度条标示 (1.文库 ➔ 2.品牌装帧 ➔ 3.算力分发) -->
                <div class="wizard-steps-indicator" style="display: flex; justify-content: space-between; margin-bottom: 10px; position: relative;">
                    <div class="step-line" style="position: absolute; top: 11px; left: 0; right: 0; height: 2px; background: rgba(255,255,255,0.08); z-index: 1;"></div>
                    <div class="step-line-active" id="wiz-progress-line" style="position: absolute; top: 11px; left: 0; width: 0%; height: 2px; background: var(--accent-primary); transition: width 0.3s ease; z-index: 2;"></div>
                    
                    <div class="wiz-step-node active" id="wiz-node-1" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 22px; height: 22px; border-radius: 50%; background: var(--card-bg); border: 2px solid var(--accent-primary); color: var(--text-bright); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; transition: all 0.3s;">1</div>
                        <span style="font-size: 0.68rem; color: var(--text-bright); margin-top: 3px; font-weight: bold;">关联原稿文库</span>
                    </div>
                    <div class="wiz-step-node" id="wiz-node-2" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 22px; height: 22px; border-radius: 50%; background: var(--card-bg); border: 2px solid rgba(255,255,255,0.1); color: var(--text-dim); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; transition: all 0.3s;">2</div>
                        <span style="font-size: 0.68rem; color: var(--text-dim); margin-top: 3px; font-weight: bold;">品牌名称与装帧</span>
                    </div>
                    <div class="wiz-step-node" id="wiz-node-3" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 22px; height: 22px; border-radius: 50%; background: var(--card-bg); border: 2px solid rgba(255,255,255,0.1); color: var(--text-dim); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; transition: all 0.3s;">3</div>
                        <span style="font-size: 0.68rem; color: var(--text-dim); margin-top: 3px; font-weight: bold;">算力底座与分发</span>
                    </div>
                </div>

                <div class="modal-body" style="flex: 1; overflow-y: auto; padding-right: 2px; margin-bottom: 8px;">
                    <!-- Step 1: 📂 关联原稿文库 -->
                    <div id="wiz-step-1" class="wizard-pane fade-in">
                        <div class="sovereign-memo glass-panel" style="margin-bottom: 10px; padding: 7px 12px; border-left: 3px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.04); border-radius: 6px;">
                            <p style="font-size: 0.76rem; color: var(--text-dim); margin: 0; line-height: 1.4;">
                                💡 <b>内容文库 (Vault)</b> 是存放手稿 Markdown 笔记的本地物理文件夹。支持选取已有目录或自动新建：
                            </p>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px 14px; display: flex; flex-direction: column; gap: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.84rem; color: var(--text-bright); margin: 0;">内容文库绝对物理路径</label>
                                    <span class="tier-tag tier-local" style="font-size: 0.62rem; padding: 1px 5px;">本地物理路径</span>
                                </div>
                                <p style="font-size: 0.72rem; color: var(--text-dim); margin: 0; line-height: 1.3;">选择您本地电脑的笔记文件夹路径。留空将自动生成标准演示路径。</p>
                                <div style="display: flex; gap: 8px; margin-top: 4px;">
                                    <input type="text" id="wiz-vault-path" class="setting-input" placeholder="例如: /Users/username/MyVault" style="flex: 1; font-family: var(--font-mono); font-size: 0.78rem; padding: 6px 10px; border-radius: 6px;">
                                    <button type="button" class="secondary-btn" onclick="window.pickWizardVaultDirectory()" style="padding: 6px 12px; font-size: 0.75rem; white-space: nowrap;">📁 选择文件夹</button>
                                </div>
                                <div id="wiz-error-path" class="glass-panel" style="display: none; margin-top: 6px; padding: 6px 10px; border-left: 3px solid #ff4d6a; background: rgba(255, 77, 106, 0.08); border-radius: 6px; color: #ff859b; font-size: 0.74rem; line-height: 1.3;"></div>
                            </div>
                            
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" id="wiz-bootstrap-vault" style="margin: 0; transform: scale(1.1); cursor: pointer;" checked>
                                <label for="wiz-bootstrap-vault" style="font-size: 0.74rem; color: var(--text-dim); cursor: pointer; line-height: 1.3;">
                                    自动注入中英双语演示手稿与资产目录结构 (推荐新手勾选)
                                </label>
                            </div>
                        </div>
                    </div>

                    <!-- Step 2: 🏷️ 品牌标识与装帧主题 -->
                    <div id="wiz-step-2" class="wizard-pane fade-in" style="display: none;">
                        <div class="sovereign-memo glass-panel" style="margin-bottom: 8px; padding: 6px 12px; border-left: 3px solid var(--accent-primary); background: rgba(163, 76, 255, 0.04); border-radius: 6px;">
                            <p style="font-size: 0.74rem; color: var(--text-dim); margin: 0; line-height: 1.35;">
                                💡 <b>品牌名与装帧</b>：品牌 ID 将作为物理文件夹名；装帧主题决定网站的视觉与静态渲染框架。
                            </p>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <!-- 品牌名称与品牌 ID 同排紧凑布局 (带精准错误提示) -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 8px 12px;">
                                <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 10px; align-items: start;">
                                    <div>
                                        <label style="font-weight: 600; font-size: 0.78rem; color: var(--text-bright); display: block; margin-bottom: 2px;">🏷️ 品牌出版物名称</label>
                                        <input type="text" id="wiz-imprint-name" class="setting-input" placeholder="例如: 极客漫游指南" style="width: 100%; box-sizing: border-box; font-size: 0.78rem; padding: 5px 8px; border-radius: 6px;" oninput="window.onWizardNameInput(this.value)">
                                        <div id="wiz-error-name" style="display: none; margin-top: 3px; color: #ff859b; font-size: 0.68rem; line-height: 1.2;"></div>
                                    </div>
                                    <div>
                                        <label style="font-weight: 600; font-size: 0.78rem; color: var(--text-bright); display: block; margin-bottom: 2px;">🆔 品牌 ID (英文/数字/中划线)</label>
                                        <input type="text" id="wiz-imprint-id" class="setting-input" placeholder="例如: geek-guide" style="width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 0.78rem; padding: 5px 8px; border-radius: 6px;" oninput="window.onWizardIdInput(this.value)">
                                        <div id="wiz-error-id" style="display: none; margin-top: 3px; color: #ff859b; font-size: 0.68rem; line-height: 1.2;"></div>
                                    </div>
                                </div>
                                <div id="wiz-error-step2" class="glass-panel" style="display: none; margin-top: 6px; padding: 4px 8px; border-left: 3px solid #ff4d6a; background: rgba(255, 77, 106, 0.08); border-radius: 4px; color: #ff859b; font-size: 0.72rem; line-height: 1.2;"></div>
                            </div>

                            <!-- 挑选装帧主题 (6 大官方主题) -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 8px 12px; display: flex; flex-direction: column; gap: 6px; margin-top: 2px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.8rem; color: var(--text-bright); margin: 0;">🎭 装帧主题选择 (SSG Theme)</label>
                                    <span class="tier-tag" style="background: rgba(0, 242, 255, 0.1); color: var(--accent-secondary); font-size: 0.6rem; padding: 1px 6px;">✨ 支持随时无损切换</span>
                                </div>
                                <input type="hidden" id="wiz-selected-theme" value="sovereign">
                                
                                <div class="wiz-theme-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 2px; max-height: 200px; overflow-y: auto; padding-right: 2px;">
                                    <!-- Sovereign -->
                                    <div class="wiz-theme-card active" data-theme="sovereign" onclick="window.selectWizardTheme('sovereign')">
                                        <div style="font-weight: 700; font-size: 0.78rem; color: var(--accent-secondary); display: flex; align-items: center; justify-content: space-between;">
                                            <span>👑 Sovereign</span>
                                            <span class="wiz-theme-badge flag-badge">👑 官方旗舰</span>
                                        </div>
                                        <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 2px;">数字主权出版原生装帧，开箱即用</div>
                                    </div>
                                    <!-- Universal -->
                                    <div class="wiz-theme-card" data-theme="universal" onclick="window.selectWizardTheme('universal')">
                                        <div style="font-weight: 700; font-size: 0.78rem; color: var(--text-bright); display: flex; align-items: center; justify-content: space-between;">
                                            <span>🌐 Universal</span>
                                            <span class="wiz-theme-badge">🌐 自适应响应</span>
                                        </div>
                                        <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 2px;">全球通用现代化自适应科技版式</div>
                                    </div>
                                    <!-- Docusaurus -->
                                    <div class="wiz-theme-card" data-theme="docusaurus" onclick="window.selectWizardTheme('docusaurus')">
                                        <div style="font-weight: 700; font-size: 0.78rem; color: var(--text-bright); display: flex; align-items: center; justify-content: space-between;">
                                            <span>🦖 Docusaurus</span>
                                            <span class="wiz-theme-badge">🦖 知识库工程</span>
                                        </div>
                                        <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 2px;">经典开源工程文档与体系化知识库</div>
                                    </div>
                                    <!-- Starlight -->
                                    <div class="wiz-theme-card" data-theme="starlight" onclick="window.selectWizardTheme('starlight')">
                                        <div style="font-weight: 700; font-size: 0.78rem; color: var(--text-bright); display: flex; align-items: center; justify-content: space-between;">
                                            <span>🌟 Starlight</span>
                                            <span class="wiz-theme-badge">🌟 Astro极星</span>
                                        </div>
                                        <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 2px;">Astro 驱动的高性能极速多语种文档</div>
                                    </div>
                                    <!-- Nextra -->
                                    <div class="wiz-theme-card" data-theme="nextra" onclick="window.selectWizardTheme('nextra')">
                                        <div style="font-weight: 700; font-size: 0.78rem; color: var(--text-bright); display: flex; align-items: center; justify-content: space-between;">
                                            <span>⚡ Nextra</span>
                                            <span class="wiz-theme-badge">⚡ Next.js极简</span>
                                        </div>
                                        <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 2px;">极简现代化 Next.js 极速轻快渲染</div>
                                    </div>
                                    <!-- VitePress -->
                                    <div class="wiz-theme-card" data-theme="vitepress" onclick="window.selectWizardTheme('vitepress')">
                                        <div style="font-weight: 700; font-size: 0.78rem; color: var(--text-bright); display: flex; align-items: center; justify-content: space-between;">
                                            <span>🚀 VitePress</span>
                                            <span class="wiz-theme-badge">🚀 Vue超轻量</span>
                                        </div>
                                        <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 2px;">Vue 驱动的极致轻量与超快响应</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Step 3: 🤖 算力底座与全域分发赋能 (渐进式紧凑呈现架构) -->
                    <div id="wiz-step-3" class="wizard-pane fade-in" style="display: none;">
                        <input type="hidden" id="wiz-ai-provider" value="deepseek">
                        <input type="hidden" id="wiz-dispatch-platform" value="local_preview">

                        <!-- 🌟 默认极简开箱态 (Default Streamlined State) -->
                        <div id="wiz-step3-streamlined-view" style="display: flex; flex-direction: column; gap: 10px;">
                            <div class="sovereign-memo glass-panel" style="padding: 8px 12px; border-left: 3px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.04); border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-size: 0.76rem; color: var(--text-dim); line-height: 1.4;">
                                    ⚡ <b>智能装配就绪</b>：系统已根据您的运行环境全自动预设最佳发行底座，可即刻极速建站：
                                </div>
                                <button type="button" class="secondary-btn" onclick="window.toggleWizardAdvancedConfig(true)" style="padding: 3px 8px; font-size: 0.7rem; white-space: nowrap; border-color: rgba(0, 242, 255, 0.3); color: var(--accent-secondary);">⚙️ 自定义配置</button>
                            </div>

                            <!-- 两张精美预设赋能卡片 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                <!-- 预设算力卡片 -->
                                <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; gap: 8px;">
                                    <div>
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                            <span style="font-weight: 700; font-size: 0.8rem; color: var(--text-bright);">🤖 翻译算力与语种</span>
                                            <span id="wiz-summary-compute-badge" class="tier-tag tier-imprint" style="font-size: 0.58rem; padding: 1px 5px;">智能推荐</span>
                                        </div>
                                        <div id="wiz-summary-compute-title" style="font-size: 0.82rem; font-weight: 700; color: var(--accent-secondary); margin-bottom: 2px;">
                                            🐋 DeepSeek (deepseek-chat)
                                        </div>
                                        <div id="wiz-summary-compute-desc" style="font-size: 0.68rem; color: var(--text-dim); line-height: 1.35;">
                                            官方推荐高性价比极速模型 · 默认发行 🇺🇸 English
                                        </div>
                                    </div>
                                    <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 0.64rem; color: var(--text-dim);">免密钥即刻体验</span>
                                        <a href="javascript:void(0)" onclick="window.toggleWizardAdvancedConfig(true)" style="font-size: 0.68rem; color: var(--accent-secondary); text-decoration: none;">切换模型/语种 ⚙️</a>
                                    </div>
                                </div>

                                <!-- 预设分发网络卡片 -->
                                <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; gap: 8px;">
                                    <div>
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                            <span style="font-weight: 700; font-size: 0.8rem; color: var(--text-bright);">🚀 网站托管与在线发布</span>
                                            <span class="tier-tag tier-global" style="font-size: 0.58rem; padding: 1px 5px;">0 门槛</span>
                                        </div>
                                        <div id="wiz-summary-dispatch-title" style="font-size: 0.82rem; font-weight: 700; color: var(--accent-secondary); margin-bottom: 2px;">
                                            📦 本地全功能离线预览
                                        </div>
                                        <div id="wiz-summary-dispatch-desc" style="font-size: 0.68rem; color: var(--text-dim); line-height: 1.35;">
                                            独立静态服务器 (43213 端口) · 稍后随时一键发布到全网
                                        </div>
                                    </div>
                                    <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 0.64rem; color: var(--text-dim);">全站托管随时扩展</span>
                                        <a href="javascript:void(0)" onclick="window.toggleWizardAdvancedConfig(true)" style="font-size: 0.68rem; color: var(--accent-secondary); text-decoration: none;">配置在线托管 ⚙️</a>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 🛠️ 详细定制配置区 (紧凑流式/无滚动溢出) -->
                        <div id="wiz-step3-custom-view" style="display: none; flex-direction: column; gap: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 3px 6px; background: rgba(255,255,255,0.03); border-radius: 6px;">
                                <span style="font-size: 0.72rem; font-weight: 700; color: var(--accent-secondary);">🛠️ 自定义高级配置面板</span>
                                <button type="button" class="secondary-btn" onclick="window.toggleWizardAdvancedConfig(false)" style="padding: 2px 8px; font-size: 0.66rem;">↩️ 折叠为默认预设</button>
                            </div>

                            <!-- 模块 A: 🤖 AI 翻译算力底座 -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 6px; padding: 6px 8px; display: flex; flex-direction: column; gap: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.76rem; color: var(--text-bright); margin: 0;">🤖 AI 翻译算力底座</label>
                                    <span id="wiz-probe-badge" class="tier-tag tier-imprint" style="font-size: 0.56rem; padding: 1px 5px;">🔍 探测中</span>
                                </div>
                                
                                <!-- 算力服务商单选卡片组 (4 选 1) -->
                                <div class="wiz-provider-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px;">
                                    <!-- 本地免密算力 -->
                                    <div class="wiz-provider-card" data-provider="lmstudio" onclick="window.selectWizardComputeProvider('lmstudio')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright); white-space: nowrap;">💻 本地模型</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">LM Studio/Ollama</div>
                                    </div>
                                    <!-- DeepSeek -->
                                    <div class="wiz-provider-card" data-provider="deepseek" onclick="window.selectWizardComputeProvider('deepseek')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--accent-secondary); white-space: nowrap;">🐋 DeepSeek</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">官方推荐直连</div>
                                    </div>
                                    <!-- SiliconFlow 硅基流动 -->
                                    <div class="wiz-provider-card" data-provider="siliconflow" onclick="window.selectWizardComputeProvider('siliconflow')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright); white-space: nowrap;">⚡ 硅基流动</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">全网模型/海量赠送</div>
                                    </div>
                                    <!-- 暂不接入 -->
                                    <div class="wiz-provider-card" data-provider="none" onclick="window.selectWizardComputeProvider('none')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright); white-space: nowrap;">⏸️ 稍后配置</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">纯静态建站</div>
                                    </div>
                                </div>

                                <!-- ① 🔑 API Key 输入框 (置于模型选择上方，支持在线/本地安全鉴权) -->
                                <div id="wiz-ai-key-container" style="display: flex; flex-direction: column; gap: 2px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <label id="wiz-key-label" style="font-size: 0.68rem; color: var(--text-dim); margin: 0;">🔑 API 密钥 (Key):</label>
                                        <span id="wiz-key-hint" style="font-size: 0.58rem; color: var(--text-dim);">输入后失焦或点击 🔄 真实拉取模型</span>
                                    </div>
                                    <div style="position: relative; display: flex; align-items: center;">
                                        <input type="password" id="wiz-ai-key" class="setting-input" placeholder="sk-... (选填/如启用鉴权则输入)" style="width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 0.72rem; padding: 3px 24px 3px 6px; border-radius: 4px;" onblur="window.onWizardKeyBlur()" onkeydown="if(event.key==='Enter'){event.preventDefault();window.refreshWizardModelList();}">
                                        <span onclick="window.toggleWizardKeyVisibility()" style="position: absolute; right: 6px; cursor: pointer; font-size: 0.7rem; opacity: 0.7;">👁️</span>
                                    </div>
                                </div>

                                <!-- ② 🎯 模型选择与首要语种单选并排布局 (标准 select 展开全量列表) -->
                                <div style="display: grid; grid-template-columns: 1.15fr 1fr; gap: 8px; align-items: start;">
                                    <!-- 左侧：标准全量模型下拉与真实拉取 -->
                                    <div id="wiz-ai-model-container" style="display: flex; flex-direction: column; gap: 2px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <label style="font-size: 0.68rem; color: var(--text-dim); margin: 0;">🎯 翻译引擎模型 (Model):</label>
                                            <span id="wiz-model-status" style="font-size: 0.58rem; color: var(--accent-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 130px;"></span>
                                        </div>
                                        <div style="display: flex; gap: 4px; align-items: center;">
                                            <select id="wiz-ai-model-select" class="setting-input" style="flex: 1; font-size: 0.72rem; padding: 3px 6px; border-radius: 4px;" onchange="window.onWizardModelSelected(this.value)">
                                                <option value="">-- 点击 🔄 真实拉取模型 --</option>
                                            </select>
                                            <input type="text" id="wiz-ai-model-custom" class="setting-input" placeholder="输入模型名，如 deepseek-chat" style="display: none; flex: 1; font-size: 0.72rem; padding: 3px 6px; border-radius: 4px;" oninput="window.updateWizardSummaryView()" onblur="window.onWizardCustomModelBlur()">
                                            <button type="button" class="secondary-btn" onclick="window.refreshWizardModelList()" title="向服务商/本地发起真实连通性测试并拉取完整模型列表" style="padding: 2px 6px; font-size: 0.66rem;">🔄</button>
                                        </div>
                                    </div>

                                    <!-- 右侧：首要目标语种单选 -->
                                    <div style="display: flex; flex-direction: column; gap: 2px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <label style="font-size: 0.68rem; color: var(--text-dim); margin: 0;">🌍 首要目标语种:</label>
                                            <span style="font-size: 0.58rem; color: var(--text-dim);">可随时扩展</span>
                                        </div>
                                        <select id="wiz-primary-lang-select" class="setting-input" style="width: 100%; box-sizing: border-box; font-size: 0.72rem; padding: 3px 6px; border-radius: 4px;" onchange="window.onWizardPrimaryLangSelected(this.value)">
                                            <option value="en" data-lang="en" selected>🇺🇸 English (英语 · 推荐)</option>
                                            <option value="ja" data-lang="ja">🇯🇵 日本語 (日语)</option>
                                            <option value="de" data-lang="de">🇩🇪 Deutsch (德语)</option>
                                            <option value="fr" data-lang="fr">🇫🇷 Français (法语)</option>
                                            <option value="es" data-lang="es">🇪🇸 Español (西班牙语)</option>
                                            <option value="ru" data-lang="ru">🇷🇺 Русский (俄语)</option>
                                            <option value="zh" data-lang="zh">🇨🇳 简体中文 (单语源站)</option>
                                        </select>
                                    </div>
                                </div>

                                <!-- 灵活扩展友好提示条 -->
                                <div style="font-size: 0.64rem; color: var(--text-dim); line-height: 1.35; padding: 3px 6px; background: rgba(255,255,255,0.015); border-radius: 4px; border: 1px dashed rgba(255,255,255,0.06);">
                                    💡 <b>自由扩展提示</b>：算力渠道、多语种翻译、全站托管及社媒分发平台均可在品牌创建完成后随时扩展。
                                </div>
                            </div>

                            <!-- 模块 B: 🚀 网站托管与在线发布 (全站托管平台) -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 6px; padding: 6px 8px; display: flex; flex-direction: column; gap: 4px; margin-top: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.76rem; color: var(--text-bright); margin: 0;">🚀 网站托管与在线发布</label>
                                    <span class="tier-tag tier-global" style="font-size: 0.56rem; padding: 1px 5px;">全站托管</span>
                                </div>
                                
                                <!-- 3 选 1 分发渠道卡片 -->
                                <div class="wiz-dispatch-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px;">
                                    <div class="wiz-dispatch-card active" data-dispatch="local_preview" onclick="window.selectWizardDispatchPlatform('local_preview')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright);">📦 本地预览优先</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">纯离线 0 门槛</div>
                                    </div>
                                    <div class="wiz-dispatch-card" data-dispatch="github_pages" onclick="window.selectWizardDispatchPlatform('github_pages')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--accent-secondary);">🌐 GitHub Pages</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">开源免费托管</div>
                                    </div>
                                    <div class="wiz-dispatch-card" data-dispatch="cloudflare_pages" onclick="window.selectWizardDispatchPlatform('cloudflare_pages')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright);">⚡ Cloudflare</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">超快全球 CDN</div>
                                    </div>
                                </div>

                                <!-- 🌐 GitHub Pages 面板 -->
                                <div id="wiz-dispatch-github-pane" style="display: none; flex-direction: column; gap: 4px; padding: 4px 6px; background: rgba(0, 242, 255, 0.03); border: 1px dashed rgba(0, 242, 255, 0.2); border-radius: 4px;">
                                    <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 4px;">
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🏷️ 仓库全名 (Repository):</label>
                                            <input type="text" id="wiz-gh-repo" class="setting-input" placeholder="username/repo-name" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                        </div>
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🌿 分支:</label>
                                            <select id="wiz-gh-branch" class="setting-input" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 4px; border-radius: 4px;">
                                                <option value="gh-pages" selected>gh-pages</option>
                                                <option value="main">main</option>
                                                <option value="docs">docs</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div>
                                        <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🔑 GitHub Token (选填/可稍后免密授权):</label>
                                        <input type="password" id="wiz-gh-token" class="setting-input" placeholder="ghp_xxxx 或建站后一键免密授权" style="width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                    </div>
                                </div>

                                <!-- ⚡ Cloudflare Pages 面板 -->
                                <div id="wiz-dispatch-cloudflare-pane" style="display: none; flex-direction: column; gap: 4px; padding: 4px 6px; background: rgba(255, 184, 0, 0.03); border: 1px dashed rgba(255, 184, 0, 0.2); border-radius: 4px;">
                                    <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 4px;">
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🏷️ 项目名称:</label>
                                            <input type="text" id="wiz-cf-project" class="setting-input" placeholder="project-name" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                        </div>
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🌿 生产分支:</label>
                                            <input type="text" id="wiz-cf-branch" class="setting-input" value="main" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                        </div>
                                    </div>
                                    <div>
                                        <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🔑 Cloudflare API Token (选填):</label>
                                        <input type="password" id="wiz-cf-token" class="setting-input" placeholder="API Token (选填)" style="width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                    </div>
                                </div>

                                <!-- 📦 本地离线预览面板 -->
                                <div id="wiz-dispatch-local-pane" style="padding: 6px 8px; background: rgba(0, 242, 255, 0.04); border: 1px dashed rgba(0, 242, 255, 0.25); border-radius: 6px;">
                                    <div style="font-size: 0.7rem; color: var(--accent-secondary); font-weight: 700; margin-bottom: 2px;">
                                        🎉 零密钥纯本地极速建站 (推荐)
                                    </div>
                                    <div style="font-size: 0.64rem; color: var(--text-dim); line-height: 1.35;">
                                        无需任何远程密钥，建站后系统将在本地 <code>http://127.0.0.1:43213</code> 启动独立静态服务器。您可以 100% 离线撰写、翻译与预览，稍后随时开启远程全域分发。
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="wiz-error-step3" class="glass-panel" style="display: none; margin-top: 8px; padding: 6px 10px; border-left: 3px solid #ff4d6a; background: rgba(255, 77, 106, 0.08); border-radius: 6px; color: #ff859b; font-size: 0.74rem; line-height: 1.3;"></div>
                    </div>
                </div>

                <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--glass-border); padding-top: 12px; margin-top: auto;">
                    <button class="secondary-btn" id="btn-wiz-prev" onclick="navigateWizard(-1)" style="visibility: hidden; font-size: 0.78rem; padding: 6px 14px;">上一步</button>
                    <button class="primary-btn glow-btn" id="btn-wiz-next" onclick="navigateWizard(1)" style="min-width: 110px; font-size: 0.78rem; padding: 6px 16px;">下一步 →</button>
                </div>
            </div>
        </div>

        <!-- 🏛️ [V75.2] 品牌出版物创建成功就绪确认页组件 (Success Modal & Workbench Handoff) -->
        <div id="imprint-success-modal" class="modal-overlay fade-in" style="display: none; position: fixed; inset: 0; background: rgba(0, 0, 0, 0.78); backdrop-filter: blur(12px); z-index: 10000; align-items: center; justify-content: center; padding: 16px;">
            <div class="glass-card modal-content" style="max-width: 620px; width: 92%; border: 1px solid rgba(0, 242, 255, 0.35); box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6), 0 0 32px rgba(0, 242, 255, 0.15); border-radius: 12px; padding: 18px 22px; display: flex; flex-direction: column; gap: 12px; animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);">
                
                <!-- 头部庆祝横幅 -->
                <div style="display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <div style="width: 38px; height: 38px; border-radius: 50%; background: rgba(0, 242, 255, 0.12); border: 1px solid var(--accent-secondary); display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
                        🎉
                    </div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.15rem; color: var(--text-bright); font-weight: 700; display: flex; align-items: center; gap: 8px;">
                            <span>出版品牌创建就绪！</span>
                            <span class="tier-tag tier-local" style="font-size: 0.62rem; padding: 1px 6px;">READY</span>
                        </h2>
                        <p style="margin: 2px 0 0 0; font-size: 0.72rem; color: var(--text-dim); line-height: 1.3;">
                            恭喜！您的独立数字出版品牌已全自动初始化完成，核心配置如下：
                        </p>
                    </div>
                </div>

                <!-- 品牌信息完整配置清单 -->
                <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px 14px; display: flex; flex-direction: column; gap: 8px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                        <!-- 品牌标识 -->
                        <div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🏷️ 出版品牌</div>
                            <div id="succ-imprint-brand" style="font-size: 0.8rem; font-weight: 700; color: var(--accent-secondary);">--</div>
                        </div>
                        <!-- 装帧主题 -->
                        <div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🎭 装帧主题引擎</div>
                            <div id="succ-imprint-theme" style="font-size: 0.8rem; font-weight: 700; color: var(--accent-primary);">--</div>
                        </div>
                        <!-- 原稿文库物理路径 -->
                        <div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); grid-column: 1 / -1;">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">📂 内容文库物理路径</div>
                            <div id="succ-imprint-vault" style="font-size: 0.74rem; font-family: var(--font-mono); color: var(--text-bright); word-break: break-all;">--</div>
                        </div>
                        <!-- 翻译算力底座 (独立展示) -->
                        <div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🤖 翻译算力底座</div>
                            <div id="succ-imprint-compute" style="font-size: 0.74rem; font-weight: 600; color: var(--text-bright);">--</div>
                        </div>
                        <!-- 首发翻译语种 (独立展示) -->
                        <div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 2px;">🌍 首发翻译语种</div>
                            <div id="succ-imprint-lang" style="font-size: 0.74rem; font-weight: 600; color: var(--text-bright);">--</div>
                        </div>
                        <!-- 托管与在线发布 (跨全列，支持本地与云端双行展示) -->
                        <div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); grid-column: 1 / -1; display: flex; flex-direction: column; gap: 4px;">
                            <div style="font-size: 0.64rem; color: var(--text-dim); margin-bottom: 1px;">🚀 网站托管与分发</div>
                            <div id="succ-imprint-dispatch" style="font-size: 0.72rem; color: var(--text-bright); line-height: 1.45;">--</div>
                        </div>
                    </div>
                </div>

                <!-- 工作台导向选择提示 -->
                <div class="sovereign-memo glass-panel" style="padding: 6px 12px; border-left: 3px solid var(--accent-primary); background: rgba(163, 76, 255, 0.04); border-radius: 6px;">
                    <p style="font-size: 0.7rem; color: var(--text-dim); margin: 0; line-height: 1.35;">
                        💡 <b>工作台导向</b>：您可以立即切换进入新品牌工作台开始创作，也可以返回继续当前工作台体验（稍后随时可在顶栏切换）。
                    </p>
                </div>

                <!-- 底部双向操作按钮 (左右两端对齐) -->
                <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--glass-border); padding-top: 10px; margin-top: 2px;">
                    <button class="secondary-btn" onclick="window.dismissImprintSuccessStay()" style="font-size: 0.78rem; padding: 7px 16px;">
                        ← 返回继续当前工作台
                    </button>
                    <button class="primary-btn glow-btn" onclick="window.dismissImprintSuccessSwitch()" style="font-size: 0.78rem; padding: 7px 18px;">
                        切换到新品牌工作台 →
                    </button>
                </div>
            </div>
        </div>
    `;
};
