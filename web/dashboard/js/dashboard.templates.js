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
                    <button class="primary-btn" id="btn-save-settings" style="display: none; padding: 5px 12px; font-size: 0.75rem; height: 28px; line-height: 14px;" disabled>💾 保存配置</button>
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
                        <div class="tab-item s-tab" data-cat="route_matrix"><span class="tab-icon">🛣️</span> 高级路由</div>
                        <div class="tab-item s-tab" data-cat="slug_settings"><span class="tab-icon">🔗</span> Slug 策略</div>
                        <div class="tab-item s-tab" data-cat="guardrails"><span class="tab-icon">🛡️</span> 治理准入</div>
                        <div class="tab-item s-tab" data-cat="security"><span class="tab-icon">🔒</span> 安全审计</div>
                    </aside>
                    <section class="tab-content-area">
                        <div id="settings-form" class="settings-grid">
                            <!-- 动态注入 -->
                        </div>
                    </section>
                </div>
            </div>
        </div>
    `,
    tower: `
        <div id="view-tower" class="view-panel">
            <div class="view-header">
                <h2>🗼 系统遥测 (System Telemetry)</h2>
            </div>
            <div class="view-content scroll-container" style="display: flex; flex-direction: column; gap: 20px; padding: 20px; overflow-y: auto; flex: 1;">
                <!-- 第一行：状态卡片 -->
                <div class="tower-stats-row" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;">
                    <div class="glass-panel tower-card">
                        <div class="card-label">系统状态</div>
                        <div class="card-val" id="tower-status">LOADING...</div>
                    </div>
                    <div class="glass-panel tower-card">
                        <div class="card-label">运行时间 (Uptime)</div>
                        <div class="card-val" id="tower-uptime">--</div>
                    </div>
                    <div class="glass-panel tower-card">
                        <div class="card-label">出版总进度</div>
                        <div class="card-val" id="tower-progress">--</div>
                    </div>
                    <div class="glass-panel tower-card">
                        <div class="card-label">累计算力花费 (Cost)</div>
                        <div class="card-val" id="tower-cost">--</div>
                    </div>
                </div>
                
                <!-- 第二行：排队负载与性能 -->
                <div class="tower-charts-row" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; min-height: 250px;">
                    <!-- 任务排队负载监控 -->
                    <div class="glass-panel chart-container" style="display: flex; flex-direction: column; padding: 15px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.8rem; color: var(--accent-secondary); margin-bottom: 15px;">📡 任务调度队列监控</div>
                        <div class="pool-grid" style="display: flex; flex-direction: column; gap: 15px; justify-content: center; flex: 1;">
                            <div class="pool-item">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.75rem;">
                                    <span>全局同步线程池 (Global Sync Pool)</span>
                                    <span id="pool-global-text">0 / 0</span>
                                </div>
                                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.05); height:10px; border-radius:5px; overflow:hidden;">
                                    <div id="pool-global-bar" style="width:0%; height:100%; background:var(--accent-primary); transition:width 0.5s;"></div>
                                </div>
                            </div>
                            <div class="pool-item">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.75rem;">
                                    <span>AI 翻译与推理池 (AI Compute Pool)</span>
                                    <span id="pool-ai-text">0 / 0</span>
                                </div>
                                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.05); height:10px; border-radius:5px; overflow:hidden;">
                                    <div id="pool-ai-bar" style="width:0%; height:100%; background:var(--accent-secondary); transition:width 0.5s;"></div>
                                </div>
                            </div>
                            <div class="pool-item">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.75rem;">
                                    <span>静态资源处理池 (Asset Processor Pool)</span>
                                    <span id="pool-asset-text">0 / 0</span>
                                </div>
                                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.05); height:10px; border-radius:5px; overflow:hidden;">
                                    <div id="pool-asset-bar" style="width:0%; height:100%; background:var(--accent-orange, #ff9d00); transition:width 0.5s;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 系统实时性能负载 -->
                    <div class="glass-panel chart-container" style="display: flex; flex-direction: column; padding: 15px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.8rem; color: var(--accent-secondary); margin-bottom: 15px;">💻 物理服务器负载监控</div>
                        <div style="display: flex; gap: 20px; flex: 1; align-items: center; justify-content: space-around;">
                            <!-- CPU 负载仪表盘 -->
                            <div class="gauge-box" style="text-align:center;">
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 8px;">CPU 负载</div>
                                <div class="gauge-wrapper" style="position:relative; width:100px; height:100px;">
                                    <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                                        <circle cx="50" cy="50" r="42" stroke="rgba(255,255,255,0.05)" stroke-width="8" fill="none"/>
                                        <circle id="gauge-cpu-ring" cx="50" cy="50" r="42" stroke="var(--accent-primary)" stroke-width="8" fill="none"
                                                stroke-dasharray="263.89" stroke-dashoffset="263.89" stroke-linecap="round" style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);"/>
                                    </svg>
                                    <div class="gauge-text" id="gauge-cpu" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:1.1rem; font-family:var(--font-mono); font-weight:bold; color:var(--text-bright);">--%</div>
                                </div>
                            </div>
                            <!-- 内存占用仪表盘 -->
                            <div class="gauge-box" style="text-align:center;">
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 8px;">内存占用</div>
                                <div class="gauge-wrapper" style="position:relative; width:100px; height:100px;">
                                    <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                                        <circle cx="50" cy="50" r="42" stroke="rgba(255,255,255,0.05)" stroke-width="8" fill="none"/>
                                        <circle id="gauge-mem-ring" cx="50" cy="50" r="42" stroke="var(--accent-secondary)" stroke-width="8" fill="none"
                                                stroke-dasharray="263.89" stroke-dashoffset="263.89" stroke-linecap="round" style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);"/>
                                    </svg>
                                    <div class="gauge-text" id="gauge-mem" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:1.1rem; font-family:var(--font-mono); font-weight:bold; color:var(--text-bright);">--%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 第三行：历史负载走势图 -->
                <div class="tower-history-row" style="display: grid; grid-template-columns: 1fr; gap: 20px; margin-top: 20px;">
                    <div class="glass-panel chart-container" style="display: flex; flex-direction: column; padding: 15px; min-height: 180px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.8rem; color: var(--accent-secondary); margin-bottom: 10px; display: flex; justify-content: space-between;">
                            <span>📈 负载历史演进趋势 (CPU & Memory Sparkline)</span>
                            <div style="display: flex; gap: 15px; font-size: 0.75rem; font-family: var(--font-mono);"><span style="color: var(--accent-primary);">● CPU</span><span style="color: var(--accent-secondary);">● MEM</span></div>
                        </div>
                        <div style="flex: 1; position: relative; width: 100%; height: 120px;">
                            <svg id="tower-trend-svg" width="100%" height="100%" viewBox="0 0 500 120" preserveAspectRatio="none" style="overflow: visible;">
                                <defs>
                                    <linearGradient id="cpu-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-primary)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent-primary)" stop-opacity="0"/></linearGradient>
                                    <linearGradient id="mem-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-secondary)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent-secondary)" stop-opacity="0"/></linearGradient>
                                </defs>
                                <path id="trend-cpu-area" fill="url(#cpu-grad)" d=""/><path id="trend-cpu-line" fill="none" stroke="var(--accent-primary)" stroke-width="2" d=""/>
                                <path id="trend-mem-area" fill="url(#mem-grad)" d=""/><path id="trend-mem-line" fill="none" stroke="var(--accent-secondary)" stroke-width="2" d=""/>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `
};
