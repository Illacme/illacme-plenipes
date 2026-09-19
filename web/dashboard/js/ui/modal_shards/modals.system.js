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
                                <label>TITLE</label>
                                <input type="text" id="editor-meta-title" class="drawer-input">
                            </div>
                            <div class="drawer-item" style="flex-shrink: 0;">
                                <label>SLUG / IDENTIFIER</label>
                                <input type="text" id="editor-meta-slug" class="drawer-input">
                            </div>
                            <div class="drawer-item" style="flex-shrink: 0;">
                                <label>PUBLISH DATE</label>
                                <input type="datetime-local" id="editor-meta-date" class="drawer-input">
                            </div>
                            
                            <!-- 🚀 [NEW] 动态元数据容器 (V68.0) -->
                            <div id="editor-dynamic-meta-container" style="display: flex; flex-direction: column; gap: 15px; border-top: 1px dashed var(--glass-border); padding-top: 15px;">
                                <!-- 动态注入项将出现在这里 -->
                            </div>
                        </div>

                        <div class="editor-actions" style="border-top: 1px solid var(--glass-border); padding-top: 15px; margin-top: auto; display: flex; gap: 10px;">
                            <button class="primary-btn glow-btn" onclick="saveEditorManuscript()" style="flex: 1;">SAVE DISK</button>
                            <button class="secondary-btn" onclick="closeEditor()" style="flex: 1;">DISCARD</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 🏗️ Terminal Modal for Installation -->
        <div id="terminal-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content terminal-modal-content">
                <div class="modal-header">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span class="status-indicator live"></span>
                        <h2>SYSTEM TERMINAL PIPELINE</h2>
                    </div>
                    <div class="terminal-meta">
                        <span id="terminal-status" class="online">ONLINE</span>
                        <button class="close-btn" onclick="closeTerminalModal()">×</button>
                    </div>
                </div>
                <div class="modal-body terminal-modal-body">
                    <div id="terminal-output" class="terminal-view"></div>
                </div>
                
                <!-- 底部操作与直达栏 -->
                <div class="modal-footer" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <button class="secondary-btn" id="btn-terminal-clear" onclick="document.getElementById('terminal-output').innerHTML=''" style="padding: 6px 12px; font-size: 0.8rem;">清屏</button>
                        <button class="secondary-btn" id="btn-terminal-abort" onclick="window.abortActivePublishJob()" style="padding: 6px 14px; font-size: 0.8rem; color: #ff4d4d; border-color: rgba(255,77,77,0.4); display: none;">🛑 紧急终止</button>
                    </div>

                    <!-- ⚡ 强制覆盖选项条（常驻于发布按钮上方，绝不因日志滚动而丢失） -->
                    <div id="preview-force-sync-bar" style="display: none; align-items: center; gap: 6px; padding: 4px 10px; background: rgba(245, 158, 11, 0.08); border: 1px dashed rgba(245, 158, 11, 0.35); border-radius: 6px; font-size: 0.75rem; color: #f59e0b;">
                        <input type="checkbox" id="chk-preview-force-sync" style="accent-color: #f59e0b; cursor: pointer; margin: 0;">
                        <label for="chk-preview-force-sync" style="cursor: pointer; user-select: none; font-weight: 500;" title="忽略文章时间戳对比，无条件重新翻译并强制覆写所有语种目标文件与资源">强制全量重新翻译并覆盖</label>
                    </div>

                    <div style="display:flex; align-items:center; gap:10px;">
                        <!-- 重新发布全站按钮（仅在构建失败或完成时动态呼出） -->
                        <button class="primary-btn glow-btn" id="btn-terminal-republish" onclick="window.triggerRepublishFromTerminal()" style="display:none; padding:6px 16px; font-size:0.8rem; background:linear-gradient(135deg, #ff8c00, #ff0055); border-color:rgba(255,140,0,0.5);">🚀 重新发布全站</button>
                        <!-- 启动预览服务按钮 -->
                        <button class="secondary-btn" id="btn-terminal-start-preview" onclick="window.startPreviewServiceFromTerminal()" style="display:none; padding:6px 14px; font-size:0.8rem; color:#00f2fe; border-color:rgba(0,242,254,0.4);">🌐 启动预览服务</button>
                        <!-- 打开本地预览按钮 -->
                        <button class="primary-btn glow-btn" id="btn-terminal-open-preview" onclick="window.openPreviewFromTerminal()" style="display:none; padding:6px 16px; font-size:0.8rem;">🌐 打开本地预览</button>
                        <!-- 立即访问线上主站按钮 -->
                        <button class="primary-btn glow-btn" id="btn-terminal-visit-site" onclick="window.openPrimaryLiveSite()" style="display:none; padding:6px 18px; font-size:0.82rem; font-weight:700; background:linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); border-color:rgba(0,242,254,0.6); color:#000; box-shadow:0 0 16px rgba(0,242,254,0.4);">🏠 访问主站 ↗</button>
                        <button class="secondary-btn" id="btn-terminal-close" onclick="closeTerminalModal()" style="display:none; padding:6px 14px; font-size:0.8rem;">关闭</button>
                        <button class="primary-btn glow-btn" id="btn-terminal-ok" onclick="closeTerminalModal()" style="display:none; padding:6px 16px; font-size:0.8rem;">完成</button>
                    </div>
                </div>
            </div>
        </div>
        `;
    };

})();
