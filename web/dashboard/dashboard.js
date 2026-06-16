/**
 * 🚀 Illacme Plenipes Dashboard V55.1
 * Commercial-Grade Control Orchestrator (Entry Point)
 * 职责：顶级就绪主引导、快捷键捕捉及模块协同。
 */

// 0. 全局异常感知与防御体系 (Global Error Boundaries)
window.addEventListener('error', (event) => {
    console.error("🔥 [Global Boundary] 捕获到未处理异常:", event.error || event.message);
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            toast: true,
            position: 'bottom-end',
            icon: 'error',
            title: '系统运行异常',
            text: event.message || '发生了未知的渲染或逻辑报错',
            showConfirmButton: false,
            timer: 5000,
            background: 'rgba(20, 10, 20, 0.95)',
            color: '#ff4c4c'
        });
    }
    if (typeof window.addAudit === 'function') {
        window.addAudit(`❌ [SYS FAULT] 运行时抛错: ${event.message}`);
    }
});

window.addEventListener('unhandledrejection', (event) => {
    console.error("🔥 [Global Boundary] 捕获到未处理的 Promise 拒绝:", event.reason);
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            toast: true,
            position: 'bottom-end',
            icon: 'warning',
            title: '异步链路中断',
            text: event.reason?.message || '网络或数据流通道发生异常',
            showConfirmButton: false,
            timer: 5000,
            background: 'rgba(20, 15, 10, 0.95)',
            color: '#ffb34c'
        });
    }
    if (typeof window.addAudit === 'function') {
        window.addAudit(`⚠️ [NET FAULT] 异步链路受阻: ${event.reason?.message || 'Unknown Reason'}`);
    }
});

// 1. 全局交互逻辑 (Sidebar)
window.toggleSidebar = (side) => {
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

// 2. 系统核心初始化引导主入口
window.initDashboard = async () => {
    try {
        // 🚀 [V57.0] 物理注入视图与 UI 组件
        if (typeof initViewContainers === 'function') initViewContainers();
        if (typeof window.initTelemetryDynamics === 'function') {
            window.initTelemetryDynamics();
        }
        if (typeof renderUIComponents === 'function') renderUIComponents();
        
        // 🌓 初始化昼夜主题引擎
        if (typeof window.ThemeModeManager !== 'undefined') {
            window.ThemeModeManager.init();
        }

        if (typeof addAudit === 'function') addAudit("🚀 正在初始化主权治理控制台...");

        // 侧边栏绑定
        if (document.getElementById('toggle-left')) {
            document.getElementById('toggle-left').onclick = () => window.toggleSidebar('left');
        }
        if (document.getElementById('toggle-right')) {
            document.getElementById('toggle-right').onclick = () => window.toggleSidebar('right');
        }

        // 全局快捷键
        window.onkeydown = (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            if (e.key === '[') window.toggleSidebar('left');
            if (e.key === 'i' && typeof window.toggleHub === 'function') {
                window.toggleHub('show');
            }
            if (e.key === ']') window.toggleSidebar('right');
        };

        // 导航绑定
        const navs = ['overview', 'vault', 'compute', 'plugins', 'settings', 'tower'];
        navs.forEach(id => {
            const el = document.getElementById(`nav-${id}`);
            if (el) {
                el.onclick = () => {
                    if (typeof window.showView === 'function') {
                        window.showView(id);
                    }
                    if (id === 'overview' && typeof window.toggleHub === 'function') {
                        window.toggleHub('show');
                    }
                };
            }
        });

        // 核心组件初始化
        if (typeof window.initGalaxy === 'function') window.initGalaxy();
        if (typeof initWebSocket === 'function') initWebSocket();

        // 🌍 [V55.3] 动态拉取语种智库与系统配置
        if (typeof apiFetch === 'function') {
            apiFetch('/api/system/languages').then(res => {
                if (res && res.languages) window.availableLangs = res.languages;
            });
            apiFetch('/api/system/config').then(res => {
                if (res) {
                    window.settingsData = { ...window.settingsData, ...(res.config || res) };
                }
            });
        }

        // 治理周期任务
        setInterval(() => { if (typeof refreshHealthMatrix === 'function') refreshHealthMatrix(); }, 10000);
        setInterval(() => { if (typeof refreshGovernanceContext === 'function') refreshGovernanceContext(); }, 30000);

        // 其他 UI 绑定
        const imprintTrigger = document.getElementById('imprint-selector-trigger');
        if (imprintTrigger && typeof window.toggleImprintDropdown === 'function') {
            imprintTrigger.onclick = window.toggleImprintDropdown;
        }

        document.addEventListener('click', () => {
            const dropdown = document.getElementById('imprint-dropdown');
            if (dropdown) dropdown.style.display = 'none';
        });

        const btnPublish = document.getElementById('btn-publish');
        if (btnPublish && typeof window.triggerPublish === 'function') {
            btnPublish.onclick = () => window.triggerPublish(false);
        }

        const btnSaveDoc = document.getElementById('btn-save-doc');
        if (btnSaveDoc && typeof saveDocument === 'function') {
            btnSaveDoc.onclick = saveDocument;
        }

        const saveSettingsBtn = document.getElementById('btn-save-settings');
        if (saveSettingsBtn && typeof saveAllSettings === 'function') {
            saveSettingsBtn.onclick = saveAllSettings;
        }

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

// 3. 统一启动入口
const bootDashboard = () => {
    window.initDashboard().then(() => {
        if (typeof window.handleRouting === 'function') {
            window.handleRouting();
        }
        if (typeof window.initGlobalTelemetryPulse === 'function') {
            window.initGlobalTelemetryPulse();
        }
    });
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootDashboard);
} else {
    bootDashboard();
}
