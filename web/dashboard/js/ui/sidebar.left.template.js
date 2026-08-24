/**
 * 🚀 Illacme Plenipes UI - Left Sidebar Template Shard
 * 职责：左侧 Press Identity、Publishing Pipeline 6 阶段流水线、健康矩阵与运维面板 DOM 动态挂载。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.ensureLeftSidebarMounted = function () {
    const sidebar = document.getElementById('left-sidebar');
    if (!sidebar || sidebar.children.length > 0) return;

    sidebar.innerHTML = `
        <!-- 🛰️ Press Identity & Heartbeat -->
        <div class="sidebar-pod identity-pod">
            <div class="pod-header">
                <span class="pod-title">PRESS IDENTITY</span>
                <div class="heartbeat-indicator pulsing healthy"></div>
            </div>
            <div class="identity-badge-group" style="display: flex; flex-direction: column; gap: 8px;">
                <div class="identity-item" style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 0.55rem; color: var(--text-dim); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; min-width: 45px;">THEME:</span>
                    <div id="sidebar-theme-display" class="imprint-badge-glow">LOADING...</div>
                </div>
                <div class="identity-item" style="display: flex; align-items: center; gap: 6px; overflow: hidden;">
                    <span style="font-size: 0.55rem; color: var(--text-dim); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; min-width: 45px;">VAULT:</span>
                    <div id="sidebar-vault-display"
                        style="font-family: var(--font-mono); font-size: 0.65rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;"
                        title="物理文稿库绝对路径&#10;点击可一键复制到剪贴板" onclick="window.copyVaultPath()">LOADING...</div>
                </div>
            </div>
        </div>

        <!-- 🗺️ Publishing Pipeline Pod: 6-Stage Causal Workflow -->
        <div class="sidebar-pod pipeline-pod">
            <div class="pod-header" style="display: flex; justify-content: space-between; align-items: center;">
                <span class="pod-title">PUBLISHING PIPELINE</span>
                <span class="version-tag tiny" style="color: var(--accent-secondary); font-size: 0.58rem;">FLOW</span>
            </div>
            <div id="publishing-pipeline-matrix" class="pipeline-matrix">
                <!-- 阶段 1: 原稿文库 -->
                <div class="pipeline-capsule" id="pipe-cap-vault" onclick="window.showView('vault')"
                    title="点击一键直达原稿文库列表与文稿管理">
                    <div class="pipe-icon">📂</div>
                    <div class="pipe-data">
                        <div class="pipe-label">1. 原稿文库</div>
                        <div class="pipe-value" id="pipe-val-vault"><span class="pipe-skeleton"></span></div>
                    </div>
                    <div class="pipe-dot standby" id="pipe-dot-vault"></div>
                </div>

                <!-- 阶段 2: 多语言翻译 -->
                <div class="pipeline-capsule" id="pipe-cap-i18n" onclick="window.showView('settings', 'localization')"
                    title="点击一键直达多语言翻译治理与目标语种配置">
                    <div class="pipe-icon">🌍</div>
                    <div class="pipe-data">
                        <div class="pipe-label">2. 多语言翻译</div>
                        <div class="pipe-value" id="pipe-val-i18n"><span class="pipe-skeleton"></span></div>
                    </div>
                    <div class="pipe-dot standby" id="pipe-dot-i18n"></div>
                </div>

                <!-- 阶段 3: 网站主题 -->
                <div class="pipeline-capsule" id="pipe-cap-theme" onclick="window.showView('settings', 'themes')"
                    title="点击一键直达网站视觉主题与出版模式选择">
                    <div class="pipe-icon">🎭</div>
                    <div class="pipe-data">
                        <div class="pipe-label">3. 网站主题</div>
                        <div class="pipe-value" id="pipe-val-theme"><span class="pipe-skeleton"></span></div>
                    </div>
                    <div class="pipe-dot standby" id="pipe-dot-theme"></div>
                </div>

                <!-- 阶段 4: 网址路径 -->
                <div class="pipeline-capsule" id="pipe-cap-routing" onclick="window.showView('settings', 'slug_settings')"
                    title="点击一键直达网址访问路径与 Slug 沙盒定制">
                    <div class="pipe-icon">🧭</div>
                    <div class="pipe-data">
                        <div class="pipe-label">4. 网址路径</div>
                        <div class="pipe-value" id="pipe-val-routing"><span class="pipe-skeleton"></span></div>
                    </div>
                    <div class="pipe-dot standby" id="pipe-dot-routing"></div>
                </div>

                <!-- 阶段 5: 独立站托管 (优先于社媒) -->
                <div class="pipeline-capsule" id="pipe-cap-hosting" onclick="window.showView('plugins', 'hosting')"
                    title="点击一键直达独立站全站托管与云端部署配置">
                    <div class="pipe-icon">🌐</div>
                    <div class="pipe-data">
                        <div class="pipe-label">5. 独立站托管</div>
                        <div class="pipe-value" id="pipe-val-hosting"><span class="pipe-skeleton"></span></div>
                    </div>
                    <div class="pipe-dot standby" id="pipe-dot-hosting"></div>
                </div>

                <!-- 阶段 6: 社交平台同步 (独立站上线后全网广播) -->
                <div class="pipeline-capsule" id="pipe-cap-syndication" onclick="if(typeof window.openDispatchHub==='function'){window.openDispatchHub();}else{window.showView('plugins', 'publisher');}"
                    title="点击一键唤起多平台社交媒体同步与广播中枢">
                    <div class="pipe-icon">🚀</div>
                    <div class="pipe-data">
                        <div class="pipe-label">6. 社交平台同步</div>
                        <div class="pipe-value" id="pipe-val-syndication"><span class="pipe-skeleton"></span></div>
                    </div>
                    <div class="pipe-dot standby" id="pipe-dot-syndication"></div>
                </div>
            </div>
        </div>

        <!-- 📡 Functional Matrix: Health Monitoring -->
        <div class="sidebar-pod system-pod">
            <div class="pod-header">
                <span class="pod-title">FUNCTIONALITY MATRIX</span>
            </div>
            <div class="health-matrix-grid" id="health-matrix-container">
                <!-- Dynamic Status Capsules -->
            </div>
        </div>

        <!-- ⚙️ Operational Pod: System Controls -->
        <div class="sidebar-pod operational-pod">
            <div class="pod-header">
                <span class="pod-title">OPERATIONS</span>
            </div>
            <div class="control-row" style="display: flex; gap: 8px; margin-bottom: 8px;">
                <button class="mini-btn glow-btn" onclick="location.reload()" title="重新加载当前管理面板状态"
                    style="flex: 1;">🔄 刷新面板</button>
                <button class="mini-btn glow-btn" id="btn-system-gc" onclick="window.triggerSystemGC()"
                    title="物理清洗底层已失效的幽灵路由与冗余资产"
                    style="flex: 1; background: rgba(0, 242, 255, 0.1); border-color: rgba(0, 242, 255, 0.3);">🧹
                    清洗路由</button>
            </div>
            <div class="control-row">
                <button class="mini-btn danger-btn full-width" id="master-shutdown-btn" onclick="shutdownSystem()"
                    title="安全关闭后端的 Illacme Plenipes 引擎服务">⏻ 关闭服务</button>
            </div>
        </div>
    `;

    // 🚀 [Zero-Flicker 极速恢复]
    try {
        const cached = sessionStorage.getItem('_illacme_pipe_cache');
        if (cached) {
            const map = JSON.parse(cached);
            Object.keys(map).forEach(k => {
                const valEl = document.getElementById(`pipe-val-${k}`);
                const dotEl = document.getElementById(`pipe-dot-${k}`);
                if (valEl && map[k].val) valEl.innerText = map[k].val;
                if (dotEl && map[k].dot) dotEl.className = map[k].dot;
            });
        }
    } catch(e) {}
};

// 自动挂载左侧边栏
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.ensureLeftSidebarMounted);
} else {
    window.ensureLeftSidebarMounted();
}
