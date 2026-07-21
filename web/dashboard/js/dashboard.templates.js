/**
 * 🌌 [V57.0] Illacme Plenipes View Templates
 * 职责：定义所有顶级 HTML 模板以解除 dashboard.views.js 的文件大小限制。
 */

window.viewTemplates = {
    overview: `
        <div id="view-overview" class="view-panel active">
            <div id="galaxy-3d">
                <div id="galaxy-labels-layer"></div>
            </div>
            <!-- 左控制与指标列 -->
            <div class="hud-container top-left" id="galaxy-hud-column" style="position: absolute; top: 25px; left: 25px; z-index: 100; display: flex; flex-direction: row; gap: 0; width: auto;">
                <!-- 动态仪表盘由 galaxy.hud.js 负责统一注入与局部刷新 -->
            </div>
            <!-- 右检索与属性仪列 -->
            <div id="galaxy-right-column" style="position: absolute; top: 25px; right: 25px; z-index: 101; display: flex; flex-direction: column; gap: 12px; width: 260px;">
                <!-- 动态检索框与星球控制仪由 galaxy.hud.js 注入 -->
            </div>
            <div class="overview-overlay" id="command-hub-overlay" style="display: flex;">
                <div class="command-hub">
                    <div class="hub-header">
                        <button class="close-btn" style="position: absolute; right: 2rem; top: 2rem;">×</button>
                        <h2 id="hub-title" style="font-size: 2.2rem; margin-bottom: 0.5rem; letter-spacing: -1px; font-weight: 900;">主权指挥中心</h2>
                        <div class="hub-meta-row" style="display: flex; gap: 1.5rem; font-size: 0.8rem; opacity: 0.7; justify-content: center; font-family: 'JetBrains Mono', monospace;">
                            <div><span style="color: var(--accent-secondary);">IMPRINT:</span> <span id="display-imprint">...</span></div><div><span style="color: var(--accent-secondary);">THEME:</span> <span id="display-theme">...</span></div>
                        </div>
                    </div>
                    <div class="quick-actions">
                        <div class="action-card" onclick="triggerPublish()"><div class="action-icon">🚀</div><div class="action-text"><h4>全域发布</h4><p>启动流水线并分发内容</p></div></div>
                        <div class="action-card" onclick="showView('vault')"><div class="action-icon">📦</div><div class="action-text"><h4>文稿管理</h4><p>审计文库文稿与元数据</p></div></div>
                        <div class="action-card" onclick="showView('settings')"><div class="action-icon">⚙️</div><div class="action-text"><h4>系统设置</h4><p>管理出版社核心参数与翻译风格</p></div></div>
                    </div>
                </div>
            </div>
            <div class="viewport-hint">🖱️ 旋转 | 滚轮缩放 | 右键平移</div>
        </div>
    `,
    vault: `
        <div id="view-vault" class="view-panel">
            <div class="view-header">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h2>📂 原稿文库 (Vault)</h2>
                </div>
                <div class="header-actions">
                    <div class="search-box">
                        <input type="text" id="vault-search" placeholder="搜索标题、路径或 Slug...">
                    </div>
                </div>
            </div>
            <div class="view-content" style="display: flex; flex-direction: row; gap: 20px; overflow: hidden; flex: 1; min-height: 0;">
                <!-- 📁 左侧目录树浏览器 -->
                <aside id="vault-tree-sidebar" class="glass-panel" style="width: 260px; flex-shrink: 0; display: flex; flex-direction: column; overflow: hidden; padding: 15px; border-radius: 12px; height: 100%; box-sizing: border-box;">
                    <div class="sector-header" style="margin-bottom: 12px; font-weight: 800; font-size: 0.75rem; letter-spacing: 1px; color: var(--accent-secondary); opacity: 0.8; font-family: 'JetBrains Mono', monospace; display: flex; justify-content: space-between; align-items: center;">
                        <span>📁 ARCHIVE EXPLORER</span>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <span id="tree-toggle-all-btn" class="tree-header-action" onclick="window.toggleAllVaultFolders()" title="折叠全部目录" style="cursor: pointer; font-size: 0.8rem; filter: grayscale(1); transition: filter 0.2s;">📁</span>
                            <span class="tree-header-action" onclick="window.toggleVaultSidebar()" title="收起侧边目录树栏" style="cursor: pointer; font-size: 0.8rem; filter: grayscale(1); transition: filter 0.2s;">◀</span>
                        </div>
                    </div>
                    <div id="vault-tree" class="scroll-container" style="flex: 1; overflow-y: auto;">
                        <!-- 目录树动态加载 -->
                    </div>
                </aside>

                <!-- 📄 右侧稿件主列表 -->
                <div id="vault-main-content" style="flex: 1; display: flex; flex-direction: column; overflow: hidden; height: 100%; min-width: 0;">
                    <!-- 🛠️ 原稿操作工具栏 (Action Toolbar) -->
                    <div class="vault-toolbar" style="display: flex; gap: 12px; align-items: center; margin-bottom: 12px; flex-shrink: 0;">
                        <button id="toggle-vault-sidebar-btn" class="mini-btn" style="padding: 6px 10px; font-size: 0.8rem; border-radius: 6px; cursor: pointer; transition: all 0.3s; height: 28px; line-height: 14px;" onclick="window.toggleVaultSidebar()" title="折叠/展开目录侧边栏">📑 隐藏侧栏</button>
                        <button class="primary-btn glow-btn" id="btn-create-document" style="padding: 6px 12px; font-size: 0.8rem; height: 28px; line-height: 14px;" onclick="window.triggerCreateDocument()" title="物理创建新 Markdown 稿件 (New Document)">＋ 新建原稿</button>
                        <button class="primary-btn glow-btn" id="btn-create-directory" style="padding: 6px 12px; font-size: 0.8rem; height: 28px; line-height: 14px;" onclick="window.triggerCreateDirectory()" title="物理创建新分类文件夹 (New Folder)">＋ 新建目录</button>
                        <button class="mini-btn" id="btn-delete-directory" style="padding: 6px 12px; font-size: 0.8rem; height: 28px; line-height: 14px; background: rgba(220,53,69,0.15); color: #ff6b6b; border: 1px solid rgba(220,53,69,0.3); display: none; cursor: pointer; transition: all 0.3s;" onclick="window.triggerDeleteDirectory()" title="删除当前选中的空目录">🗑️ 删除目录</button>
                    </div>
                    <div class="table-container glass-panel" style="flex: 1; overflow: auto; min-height: 0; border-radius: 12px;">
                        <table id="vault-table" style="min-width: 600px;">
                            <thead style="position: sticky; top: 0; z-index: 10; background: rgba(var(--bg-modal-solid-rgb), 0.95); backdrop-filter: blur(10px); box-shadow: 0 1px 0 var(--glass-border);">
                                <tr>
                                    <th style="width: 35%;">标题</th>
                                    <th style="width: auto;">物理路径</th>
                                    <th style="width: 60px; text-align: center;">字数</th>
                                    <th style="width: 120px;">操作</th>
                                </tr>
                            </thead>
                            <tbody id="vault-list">
                                <!-- 动态注入 -->
                            </tbody>
                        </table>
                    </div>
                    <div class="pagination-container" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0 10px 0; flex-shrink: 0;">
                        <span id="vault-page-info" style="font-size: 0.8rem; color: var(--text-dim);">第 1 页</span>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="display: flex; gap: 6px;">
                                <button id="vault-first-btn" class="mini-btn" onclick="window.changeVaultPageDirect(1)" disabled>首页</button>
                                <button id="vault-prev-btn" class="mini-btn" onclick="window.changeVaultPage(-1)" disabled>◀ 上一页</button>
                                <button id="vault-next-btn" class="mini-btn" onclick="window.changeVaultPage(1)">下一页 ▶</button>
                                <button id="vault-last-btn" class="mini-btn" onclick="window.changeVaultPageDirect(-1)">尾页</button>
                            </div>
                            <div style="display: flex; align-items: center; gap: 6px; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 12px;">
                                <span style="font-size: 0.8rem; color: var(--text-dim);">跳转至</span>
                                <input type="number" id="vault-go-page-input" min="1" style="width: 55px; height: 28px; padding: 0 4px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.05); color: var(--text-bright); border-radius: 4px; text-align: center; font-size: 0.8rem; box-sizing: border-box; outline: none; transition: border-color 0.2s;" placeholder="页" onkeydown="if(event.keyCode===13) window.goVaultPage()">
                                <button id="vault-go-page-btn" class="mini-btn" style="height: 28px; line-height: 14px;" onclick="window.goVaultPage()">跳转</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    compute: `
        <div id="view-compute" class="view-panel">
            <div class="view-header" style="flex-direction: column; align-items: stretch; height: auto;">
                <!-- 🛰️ 上层矩阵: 品牌与全局检索 -->
                <div class="header-main-row" style="display: flex; justify-content: space-between; align-items: center; padding: 0 20px 0 0px;">
                    <div class="header-title-area">
                        <h2>🧠 算力中心 (Compute)</h2>
                    </div>
                    <div class="header-actions" id="compute-header-actions-top" style="gap: 12px;">
                        <!-- 动态注入: 搜索框 + 策略勋章 -->
                    </div>
                </div>
                
                <!-- 🛰️ 下层矩阵: 导航切换与即时操作 (固定吸顶) -->
                <div class="header-nav-row" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 20px 0 10px; margin-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                    <div id="compute-nav-tabs-slot">
                        <!-- 动态注入: Tactical Tabs -->
                    </div>
                    <div id="compute-nav-actions-slot">
                        <!-- 动态注入: 新增/脉冲/刷新 -->
                    </div>
                </div>
            </div>
            <div class="view-content" id="compute-center-root">
                <!-- 动态注入: 只有内容网格 -->
            </div>
        </div>
    `,
    plugins: `
        <div id="view-plugins" class="view-panel" style="gap: 16px;">
            <div class="view-header" style="display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 6px; margin-bottom: 8px;">
                <div class="header-title-area" style="padding-top: 2px;">
                    <h2>🧩 插件矩阵 (Capability Hub)</h2>
                </div>
                <div class="header-actions" id="plugins-header-actions-top" style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px; min-width: 320px; margin-right: 14px;">
                    <div class="search-box" style="position: relative; width: 100%;">
                        <input type="text" id="plugin-search-input" placeholder="搜索能力、平台或描述..." value="" oninput="window.filterPluginsBySearch(this.value)">
                    </div>
                    <div class="plugin-header-tools" style="display: flex; gap: 8px; justify-content: flex-end; width: 100%;">
                        <button type="button" onclick="window.senseClipboardCredentials()" title="感应剪贴板中的 Token 并自动填入表单" style="font-size: 0.7rem; background: rgba(0, 255, 136, 0.08); border: 1px solid rgba(0, 255, 136, 0.25); color: #00ff88; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.background='rgba(0,255,136,0.2)'" onmouseout="this.style.background='rgba(0, 255, 136, 0.08)'">📋 剪贴板感知</button>
                        <button type="button" onclick="window.exportConfigBackup()" title="导出全域配置为 JSON 备份" style="font-size: 0.7rem; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); color: var(--neon-cyan); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.background='rgba(0,242,255,0.2)'" onmouseout="this.style.background='rgba(0, 242, 255, 0.08)'">📥 导出配置备份</button>
                        <button type="button" onclick="document.getElementById('config-import-file-input').click()" title="从 JSON 备份恢复全站配置" style="font-size: 0.7rem; background: rgba(163, 76, 255, 0.08); border: 1px solid rgba(163, 76, 255, 0.25); color: var(--accent-primary); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.background='rgba(163,76,255,0.2)'" onmouseout="this.style.background='rgba(163, 76, 255, 0.08)'">📤 导入配置复原</button>
                        <input type="file" id="config-import-file-input" accept=".json" style="display: none;" onchange="window.importConfigBackup(event)">
                    </div>
                </div>
            </div>
            <div class="view-content">
                <div class="side-tabs-container">
                    <aside class="side-tabs">
                        <div class="tab-item cap-tab active" data-cat="all"><span class="tab-icon">🌈</span> 全部能力</div>
                        <div class="tab-item cap-tab" data-cat="theme"><span class="tab-icon">🎨</span> 视觉装帧</div>
                        <div class="tab-item cap-tab" data-cat="hosting"><span class="tab-icon">🌐</span> 全站托管</div>
                        <div class="tab-item cap-tab" data-cat="publisher"><span class="tab-icon">🚀</span> 分发渠道</div>
                        <div class="tab-item cap-tab" data-cat="editorial"><span class="tab-icon">🧬</span> 流程审计</div>
                    </aside>
                    <section class="tab-content-area scroll-container">
                        <div id="plugins-grid">
                            <!-- 动态注入 -->
                        </div>
                    </section>
                </div>
            </div>
        </div>
    `,
    settings: `
        <div id="view-settings" class="view-panel">
            <style>
                .security-sub-tab-bar {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    border-bottom: 1px solid var(--white-08, rgba(255,255,255,0.08));
                    padding-bottom: 10px;
                    flex-wrap: wrap;
                    width: 100%;
                }
                .sub-tab-btn {
                    background: var(--white-03, rgba(255,255,255,0.03));
                    border: 1px solid var(--white-08, rgba(255,255,255,0.08));
                    color: var(--text-dim, #888);
                    padding: 6px 14px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    outline: none;
                }
                .sub-tab-btn:hover {
                    background: var(--white-08, rgba(255,255,255,0.08));
                    color: var(--text-bright, #fff);
                }
                .sub-tab-btn.active {
                    background: rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.1);
                    border-color: rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.3);
                    color: var(--accent-secondary, #00f2ff);
                    box-shadow: 0 0 8px rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.2);
                }
            </style>
            <div class="view-header" style="margin-bottom: 0; padding-bottom: 10px; border-bottom: 1px solid var(--glass-border);">
                <h2>⚙️ 治理中心 (Governance)</h2>
                <div class="header-actions">
                    <button class="primary-btn" id="btn-save-settings" style="display: none; padding: 5px 12px; font-size: 0.75rem; height: 28px; line-height: 14px;" disabled>💾 保存配置</button>
                </div>
            </div>
            <div class="view-content" style="padding-top: 25px;">
                <div class="side-tabs-container">
                    <aside class="side-tabs">
                        <div class="tab-item s-tab active" data-cat="general"><span class="tab-icon">⚙️</span> 基础配置与运维</div>
                        <div class="tab-item s-tab" data-cat="layout"><span class="tab-icon">🎨</span> 版图装帧与模式</div>
                        <div class="tab-item s-tab" data-cat="i18n_routing"><span class="tab-icon">🌍</span> 多语翻译与路由</div>
                        <div class="tab-item s-tab" data-cat="security_audit"><span class="tab-icon">🛡️</span> 安全审计与治理</div>
                    </aside>
                    <section class="tab-content-area">
                        <div id="settings-form" class="settings-grid">
                            <!-- 动态注入 -->
                        </div>
                    </section>
                </div>
            </div>
        </div>
    `
};
