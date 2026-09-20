/**
 * 🧩 [V1.0] UI Modals - System Modals Shard
 * 职责：承载系统级核心弹窗 HTML 结构 (publish-modal, editor-modal, terminal-modal)。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.getSystemModalsHTML = () => {
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
                                <div id="editor-url-preview-box" style="margin-top: 6px; font-size: 0.72rem; color: var(--accent-secondary, #00f2fe); font-family: var(--font-mono, monospace); word-break: break-all; opacity: 0.85; display: flex; align-items: center; gap: 4px;">
                                    <span style="opacity: 0.6;">🌐</span>
                                    <span id="editor-url-preview-text">预估: /index.html</span>
                                </div>
                            </div>

                            <!-- 🚀 [NEW] 动态元数据容器 (V68.0) -->
                            <div id="dynamic-metadata-container" style="display: flex; flex-direction: column; gap: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; margin-top: 5px;">
                                <!-- 动态注入项将出现在这里 -->
                            </div>
                        </div>
                        
                        <div style="margin-top:auto; display:flex; flex-direction:column; gap:10px; flex-shrink: 0; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;">
                            <div id="save-status" style="font-size:0.7rem; color:var(--accent-secondary); font-family:var(--font-mono); text-align:center;"></div>
                            <button class="primary-btn glow-btn" id="btn-save-doc" onclick="window.saveDocument()" style="width:100%;">💾 COMMIT CHANGES</button>
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
                        <button class="primary-btn glow-btn" id="btn-terminal-republish" style="display: none; background: var(--neon-cyan); color: #000;" onclick="window.republishFromTerminal()">🔄 重新发布</button>
                        <button class="secondary-btn" id="btn-terminal-abort" style="display: none; border-color: #ff4d4d; color: #ff4d4d;" onclick="window.abortSync()">🛑 中止同步</button>
                        <button class="primary-btn glow-btn" id="btn-terminal-visit-site" style="display: none; background: linear-gradient(135deg, #00ff88 0%, #00f0ff 100%); color: #000; font-weight: 700; border: none; box-shadow: 0 0 16px rgba(0, 255, 136, 0.4);" onclick="window.openPrimaryLiveSite()">🌐 立即访问线上主站 ↗</button>
                        <button class="primary-btn glow-btn" id="btn-terminal-ok" style="display: none;" onclick="closeTerminalModal()">关闭</button>
                        <button class="secondary-btn" id="btn-terminal-close" onclick="closeTerminalModal()">隐藏窗口 (后台继续)</button>
                    </div>
                </div>
            </div>
        </div>
        `;
    };

})();
