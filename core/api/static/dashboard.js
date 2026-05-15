/**
 * 🚀 Illacme Plenipes Dashboard V55.1
 * Commercial-Grade Control Orchestrator (Entry Point)
 * 职责：视图编排、全局交互逻辑、3D 引擎初始化与模块协同。
 */

// 1. 核心指挥中枢控制 (全局单例)
window.toggleHub = (forceState) => {
    const hub = document.getElementById('command-hub-overlay');
    if (!hub) return;
    
    // 强制状态或切换
    if (forceState === 'show') {
        hub.style.display = 'block';
    } else if (forceState === 'hide') {
        hub.style.display = 'none';
    } else {
        const isHidden = window.getComputedStyle(hub).display === 'none';
        hub.style.display = isHidden ? 'block' : 'none';
    }
};

window.toggleImprintDropdown = (e) => {
    if (e) e.stopPropagation();
    const dropdown = document.getElementById('imprint-dropdown');
    if (!dropdown) return;
    const isHidden = dropdown.style.display === 'none';
    dropdown.style.display = isHidden ? 'flex' : 'none';
    if (isHidden && typeof renderImprintDropdown === 'function') renderImprintDropdown();
};

// 🛰️ [V55.1] 核级事件委派：确保指挥中心关闭按钮在任何层级冲突下都能被捕获
document.addEventListener('click', (e) => {
    // 寻找最近的关闭按钮，且必须在指挥中心覆盖层内
    const closeBtn = e.target.closest('.overview-overlay .close-btn');
    if (closeBtn) {
        e.preventDefault();
        e.stopPropagation();
        window.toggleHub('hide');
    }
});

// 2. 视图编排器
window.showView = (viewId, subId) => {
    window.currentView = viewId;
    
    // 🚀 [V74.15] 物理路由对正：同步 Hash 以支持深度链接与后退逻辑
    if (window.location.hash !== `#/${viewId}`) {
        window.location.hash = `#/${viewId}`;
    }

    const panels = document.querySelectorAll('.view-panel');
    const navItems = document.querySelectorAll('.nav-item');

    panels.forEach(p => p.classList.remove('active'));
    navItems.forEach(n => n.classList.remove('active'));

    const activePanel = document.getElementById(`view-${viewId}`);
    const activeNav = document.getElementById(`nav-${viewId}`);

    if (activePanel) activePanel.classList.add('active');
    if (activeNav) activeNav.classList.add('active');

    if (typeof addAudit === 'function') addAudit(`📡 导航: ${viewId.toUpperCase()}`);

    // 模块联动加载
    if (viewId === 'vault' && typeof loadVault === 'function') loadVault();
    if (viewId === 'compute' && typeof loadComputeCenter === 'function') loadComputeCenter();
    if (viewId === 'plugins' && typeof loadPlugins === 'function') loadPlugins();
    if (viewId === 'settings' && typeof loadSettings === 'function') {
        const target = subId || 'general';
        console.log(`🛰️ [导航对正] 正在强制定位设置子页面: ${target}`);
        loadSettings(target);
        if (typeof loadPlugins === 'function') loadPlugins(); 
    }
    if (viewId === 'overview' && typeof refreshGalaxy === 'function') refreshGalaxy();
};

// 3. 3D 宇宙引擎 (Sovereign Refinement)
window.initGalaxy = () => {
    const elem = document.getElementById('galaxy-3d');
    if (!elem || typeof ForceGraph3D === 'undefined') return;
    
    if (window.galaxyGraph) return;

    window.galaxyGraph = ForceGraph3D()(elem)
        .backgroundColor('rgba(0,0,0,0)')
        .nodeLabel(node => `<div class="tactical-tooltip">${node.title || node.id}</div>`)
        .nodeColor(node => node.group === 'imprint' ? '#a34cff' : '#00f2ff')
        .nodeResolution(24)
        .nodeRelSize(5)
        .linkColor(() => 'rgba(0, 242, 255, 0.15)')
        .linkWidth(1)
        .showNavInfo(false)
        .onNodeClick(node => {
            if (node.id.startsWith('doc_') && typeof openEditor === 'function') openEditor(node.id.replace('doc_', ''));
        });

    // 🚀 [V65.0] Auto-pilot Rotation
    let angle = 0;
    setInterval(() => {
        if (window.galaxyGraph) {
            window.galaxyGraph.cameraPosition({
                x: 300 * Math.sin(angle),
                z: 300 * Math.cos(angle)
            });
            angle += Math.PI / 1000;
        }
    }, 20);

    if (typeof refreshGalaxy === 'function') refreshGalaxy();
};

window.refreshGalaxy = async () => {
    if (!window.galaxyGraph || typeof apiFetch !== 'function') return;
    const data = await apiFetch('/api/galaxy/graph');
    if (data) window.galaxyGraph.graphData(data);
};

// 4. 全局交互逻辑 (Sidebar, Keyboard)
const toggleSidebar = (side) => {
    const app = document.getElementById('app-container');
    const className = side === 'left' ? 'left-collapsed' : 'right-collapsed';
    if (!app) return;
    app.classList.toggle(className);

    const btn = document.getElementById(`toggle-${side}`);
    const isCollapsed = app.classList.contains(className);
    if (btn) {
        if (side === 'left') btn.innerText = isCollapsed ? '▶' : '◀';
        else btn.innerText = isCollapsed ? '◀' : '▶';
    }
    if (typeof addAudit === 'function') addAudit(`🛰️ 视图对正: ${side === 'left' ? '左舷' : '右舷'}面板已${isCollapsed ? '收纳' : '展开'}`);
};

// 5. 系统就绪监听
/**
 * ⚡ [V65.0] Neural Feedback: System Pulse & Tactical Dynamics
 */
window.triggerSystemPulse = () => {
    document.body.classList.remove('system-pulse');
    void document.body.offsetWidth; // Trigger reflow
    document.body.classList.add('system-pulse');
    setTimeout(() => document.body.classList.remove('system-pulse'), 500);
};

// 🛰️ [V65.0] Telemetry Dynamics Loop
const initTelemetryDynamics = () => {
    const heartbeat = document.querySelector('.heartbeat-line');
    
    setInterval(() => {
        // Random Signal Flicker
        const signalBars = document.querySelectorAll('.signal-bar');
        if (signalBars.length > 0) {
            const lastBar = signalBars[signalBars.length - 1];
            if (Math.random() > 0.8) {
                lastBar.classList.toggle('active');
            }
        }
    }, 1000);
};

// Hook into actions with Tactical Transitions
const originalShowView = window.showView;
window.showView = (id, subId) => {
    const container = document.querySelector('main');
    if (container) {
        container.classList.add('switching-view');
        window.triggerSystemPulse();
        
        setTimeout(() => {
            if (originalShowView) originalShowView(id, subId);
            container.classList.remove('switching-view');
        }, 300);
    } else {
        if (originalShowView) originalShowView(id, subId);
    }
};

window.triggerPublish = async () => {
    window.triggerSystemPulse();
    window.addAudit('正在准备物理出版链路...', 'info');

    // 🚀 [V74.8] 物理点火：连接重构后的编排中枢
    try {
        const res = await apiFetch('/api/system/sync/trigger', { method: 'POST' });
        
        if (res && res.status === 'started') {
            window.addAudit(`✅ 后台出版流水线已点火 (FutureID: ${res.future_id})`, 'success');
            
            // 使用 SweetAlert2 展示全局进度遮罩 (如果需要)
            if (window.Swal) {
                window.Swal.fire({
                    title: '出版流水线已启动',
                    text: '正在跨线程调度全球节点，请关注右侧审计雷达。',
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
            }
        } else if (res && res.status === 'rejected') {
            window.addAudit('⚠️ 拦截重入：已有出版任务正在运行中。', 'warning');
        } else {
            throw new Error(res ? res.reason : '后端拒绝点火');
        }
    } catch (err) {
        window.addAudit(`❌ 链路溃决: ${err.message}`, 'error');
        if (window.Swal) {
            window.Swal.fire('点火失败', err.message, 'error');
        }
    }
};

window.initDashboard = async () => {
    try {
        // 🚀 [V57.0] 物理注入视图与 UI 组件
        if (typeof initViewContainers === 'function') initViewContainers();
        initTelemetryDynamics();
        if (typeof renderUIComponents === 'function') renderUIComponents();

        if (typeof addAudit === 'function') addAudit("🚀 正在初始化主权治理控制台...");
        
        // 侧边栏绑定
        if (document.getElementById('toggle-left')) {
            document.getElementById('toggle-left').onclick = () => toggleSidebar('left');
        }
        if (document.getElementById('toggle-right')) {
            document.getElementById('toggle-right').onclick = () => toggleSidebar('right');
        }

        // 全局快捷键
        window.onkeydown = (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            if (e.key === '[') toggleSidebar('left');
            if (e.key === 'i') window.toggleHub('show');
            if (e.key === ']') toggleSidebar('right');
        };

        // 导航绑定
        const navs = ['overview', 'vault', 'compute', 'plugins', 'settings'];
        navs.forEach(id => {
            const el = document.getElementById(`nav-${id}`);
            if (el) {
                el.onclick = () => {
                    showView(id);
                    if (id === 'overview') {
                        window.toggleHub('show');
                    }
                };
            }
        });

        // 核心组件初始化
        if (typeof initGalaxy === 'function') initGalaxy();
        if (typeof initWebSocket === 'function') initWebSocket();
        
        // 🌍 [V55.3] 动态拉取语种智库
        if (typeof apiFetch === 'function') {
            apiFetch('/api/system/languages').then(res => {
                if (res && res.languages) window.availableLangs = res.languages;
            });
        }
        
        // 治理周期任务
        setInterval(() => { if (typeof refreshHealthMatrix === 'function') refreshHealthMatrix(); }, 10000);
        setInterval(() => { if (typeof refreshGovernanceContext === 'function') refreshGovernanceContext(); }, 30000);

        // 其他 UI 绑定
        const imprintTrigger = document.getElementById('imprint-selector-trigger');
        if (imprintTrigger) {
            imprintTrigger.onclick = window.toggleImprintDropdown;
        }

        document.addEventListener('click', () => {
            const dropdown = document.getElementById('imprint-dropdown');
            if (dropdown) dropdown.style.display = 'none';
        });

        const btnPublish = document.getElementById('btn-publish');
        if (btnPublish && typeof triggerPublish === 'function') btnPublish.onclick = triggerPublish;
        
        const btnSaveDoc = document.getElementById('btn-save-doc');
        if (btnSaveDoc && typeof saveDocument === 'function') btnSaveDoc.onclick = saveDocument;
        
        const saveSettingsBtn = document.getElementById('btn-save-settings');
        if (saveSettingsBtn && typeof saveAllSettings === 'function') saveSettingsBtn.onclick = saveAllSettings;



        const vaultSearch = document.getElementById('vault-search');
        if (vaultSearch) {
            vaultSearch.oninput = (e) => {
                clearTimeout(window.vaultSearchTimeout);
                window.vaultSearchTimeout = setTimeout(() => {
                    if (typeof loadVault === 'function') loadVault(e.target.value);
                }, 300);
            };
        }

        if (typeof addAudit === 'function') addAudit("🛰️ 治理指挥中枢已全量就绪。");
        if (typeof refreshGovernanceContext === 'function') refreshGovernanceContext();
        
        const shutdownBtn = document.getElementById("master-shutdown-btn");
        if (shutdownBtn && typeof shutdownSystem === "function") shutdownBtn.onclick = shutdownSystem;
        if (typeof refreshHealthMatrix === "function") refreshHealthMatrix();
        
    } catch (err) {
        console.error("🛑 控制台引导崩溃:", err);
    }
};

// 🚀 [V74.10] 全局遥测脉冲：物理数据推送至底部状态栏 (footer-center)
const initGlobalTelemetryPulse = () => {
    setInterval(async () => {
        try {
            const stats = await apiFetch('/api/system/stats');
            if (!stats) return;

            // 1. 同步底部状态栏 CPU LOAD & MEMORY
            const cpuEl = document.getElementById('footer-cpu-val');
            const memEl = document.getElementById('footer-mem-val');
            if (cpuEl && stats.load) cpuEl.innerText = stats.load.cpu + '%';
            if (memEl && stats.load) memEl.innerText = stats.load.memory + '%';

            // 2. 同步 AI CREDIT & TOKENS
            const costEl = document.getElementById('footer-ai-cost');
            const tokensEl = document.getElementById('footer-ai-tokens');
            if (stats.usage) {
                if (costEl) costEl.innerText = '$' + (stats.usage.cost || 0).toFixed(4);
                if (tokensEl) tokensEl.innerText = (stats.usage.input_tokens + stats.usage.output_tokens).toLocaleString();
            }

            // 3. 如果当前在 Overview 视图，同步总编室指标 (可选扩展)
            const globalCost = document.getElementById('global-cost-display');
            if (globalCost && stats.usage) {
                globalCost.innerText = '$' + (stats.usage.cost || 0).toFixed(4);
            }
        } catch (e) {
            console.warn("Global telemetry pulse dropped:", e);
        }
    }, 3000);
};

// 🚀 [V74.9] 统一启动入口：确保 initDashboard 在任何 readyState 下都被执行
// 🚀 [V74.20] 物理路由分发器：确保深链接与 URL 同步
const handleRouting = () => {
    const hash = window.location.hash.replace('#/', '');
    const validViews = ['overview', 'vault', 'compute', 'plugins', 'settings'];
    
    if (hash && validViews.includes(hash)) {
        window.showView(hash);
        if (hash === 'overview') window.toggleHub('show');
    } else {
        // 默认进入指挥中心
        window.showView('overview');
        window.toggleHub('show');
    }
};

window.addEventListener('hashchange', handleRouting);

const bootDashboard = () => {
    window.initDashboard().then(() => {
        handleRouting();
        initGlobalTelemetryPulse();
    });
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootDashboard);
} else {
    bootDashboard();
}
