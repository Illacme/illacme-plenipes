/**
 * 🌌 [V57.0] Illacme Plenipes View Orchestrator
 * 职责：动态渲染顶级视图面板，实现 index.html 的物理瘦身。
 */

window.viewTemplates = {
    overview: `
        <div id="view-overview" class="view-panel active">
            <div id="galaxy-3d"></div>
            <div id="galaxy-labels-layer"></div>
            <div class="hud-container top-left">
                <div class="hud-item glass-panel tiny">
                    <div class="hud-label">知识关联密度</div>
                    <div class="hud-value" id="density-val">0.00</div>
                </div>
                <div class="hud-item glass-panel tiny">
                    <div class="hud-label">活跃神经元</div>
                    <div class="hud-value" id="conn-count">0</div>
                </div>
            </div>
            <div class="overview-overlay" id="command-hub-overlay" style="display: flex;">
                <div class="command-hub">
                    <div class="hub-header">
                        <button class="close-btn" style="position: absolute; right: 2rem; top: 2rem;">×</button>
                        <h2 id="hub-title" style="font-size: 2.2rem; margin-bottom: 0.5rem; letter-spacing: -1px; font-weight: 900;">主权指挥中心</h2>
                        <div class="hub-meta-row" style="display: flex; gap: 1.5rem; font-size: 0.8rem; opacity: 0.7; justify-content: center; font-family: 'JetBrains Mono', monospace;">
                            <div><span style="color: var(--accent-secondary);">IMPRINT:</span> <span id="display-imprint">...</span></div>
                            <div><span style="color: var(--accent-secondary);">THEME:</span> <span id="display-theme">...</span></div>
                        </div>
                    </div>
                    <div class="quick-actions">
                        <div class="action-card" onclick="triggerPublish()">
                            <div class="action-icon">🚀</div>
                            <div class="action-text">
                                <h4>一键出版</h4>
                                <p>启动流水线并分发内容</p>
                            </div>
                        </div>
                        <div class="action-card" onclick="showView('vault')">
                            <div class="action-icon">📦</div>
                            <div class="action-text">
                                <h4>文稿管理</h4>
                                <p>审计文库文稿与元数据</p>
                            </div>
                        </div>
                        <div class="action-card" onclick="showView('settings')">
                            <div class="action-icon">⚙️</div>
                            <div class="action-text">
                                <h4>系统设置</h4>
                                <p>管理出版社核心参数与翻译风格</p>
                            </div>
                        </div>
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
                    <button id="toggle-vault-sidebar-btn" class="mini-btn" style="padding: 4px 8px; font-size: 0.75rem; border-radius: 6px; cursor: pointer; transition: all 0.3s;" onclick="window.toggleVaultSidebar()" title="折叠/展开目录侧边栏">📑 隐藏侧栏</button>
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
                    <div class="table-container glass-panel" style="flex: 1; overflow: auto; min-height: 0; border-radius: 12px;">
                        <table id="vault-table" style="min-width: 600px;">
                            <thead style="position: sticky; top: 0; z-index: 10; background: rgba(13, 14, 28, 0.95); backdrop-filter: blur(10px); box-shadow: 0 1px 0 rgba(255,255,255,0.1);">
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
                        <div style="display: flex; gap: 10px;">
                            <button id="vault-prev-btn" class="mini-btn" onclick="window.changeVaultPage(-1)" disabled>◀ 上一页</button>
                            <button id="vault-next-btn" class="mini-btn" onclick="window.changeVaultPage(1)">下一页 ▶</button>
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
        <div id="view-plugins" class="view-panel">
            <div class="view-header">
                <h2>🧩 插件矩阵 (Capability Hub)</h2>
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
            <div class="view-header" style="margin-bottom: 0; padding-bottom: 10px; border-bottom: 1px solid var(--glass-border);">
                <h2>⚙️ 治理中心 (Governance)</h2>
                <div class="header-actions">
                    <button class="primary-btn" id="btn-save-settings" style="display: none;" disabled>💾 保存配置</button>
                </div>
            </div>
            <div class="view-content" style="padding-top: 25px;">
                <div class="side-tabs-container">
                    <aside class="side-tabs">
                        <div class="tab-item s-tab active" data-cat="general"><span class="tab-icon">ℹ️</span> 基础信息</div>
                        <div class="tab-item s-tab" data-cat="imprints"><span class="tab-icon">🏗️</span> 出版版图</div>
                        <div class="tab-item s-tab" data-cat="themes"><span class="tab-icon">🎨</span> 装帧主题</div>
                        <div class="tab-item s-tab" data-cat="modes"><span class="tab-icon">📋</span> 出版模式</div>
                        <div class="tab-item s-tab" data-cat="localization"><span class="tab-icon">🌍</span> 翻译阵列</div>
                        <div class="tab-item s-tab" data-cat="translation_style"><span class="tab-icon">🎭</span> 翻译风格</div>
                        <div class="tab-item s-tab" data-cat="guardrails"><span class="tab-icon">🛡️</span> 治理准入</div>
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

/**
 * 初始化所有视图容器
 */
window.initViewContainers = () => {
    const viewport = document.getElementById('main-viewport');
    if (!viewport) return;
    viewport.innerHTML = Object.values(window.viewTemplates).join('');
};
