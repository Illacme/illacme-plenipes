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
        hub.style.display = 'flex';
    } else if (forceState === 'hide') {
        hub.style.display = 'none';
    } else {
        const isHidden = window.getComputedStyle(hub).display === 'none';
        hub.style.display = isHidden ? 'flex' : 'none';
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
        .width(elem.clientWidth)
        .height(elem.clientHeight)
        .backgroundColor('rgba(0,0,0,0)')
        .nodeColor(node => node.group === 'imprint' ? '#a34cff' : '#00f2ff')
        .nodeResolution(24)
        .nodeRelSize(5)
        .linkColor(() => 'rgba(0, 242, 255, 0.15)')
        .linkWidth(0.8)
        .showNavInfo(false)
        .linkDirectionalParticles(2)
        .linkDirectionalParticleWidth(1.2)
        .linkDirectionalParticleSpeed(0.006)
        .onNodeClick(node => {
            // 📝 [V86.8] 支持全量路径 ID，移除过时的 doc_ 前缀限制
            if (node.id && typeof openEditor === 'function') {
                const cleanId = node.id.replace('doc_', '');
                openEditor(cleanId);
            }
        })
        .onEngineTick(() => {
            // 🏷️ [V86.5] 同步 HTML 标签位置 (Obsidian 风格)
            if (typeof syncGalaxyLabels === 'function') syncGalaxyLabels();
        });

    // 🌪️ [V86.0] Kinetic Upgrade: Native Auto-Rotate
    window.galaxyGraph.controls().autoRotate = true;
    window.galaxyGraph.controls().autoRotateSpeed = 0.5;

    // 🔗 [V86.8] 核心修复：将标签同步绑定至相机控制器的 change 事件
    // 确保在手动旋转、缩放或惯性移动时，HTML 标签能实时跟踪 3D 节点
    window.galaxyGraph.controls().addEventListener('change', () => {
        if (typeof syncGalaxyLabels === 'function') syncGalaxyLabels();
    });

    // 🧪 [V86.1] Neural Pulse: Breath Dynamics
    let angle = 0;
    setInterval(() => {
        if (window.galaxyGraph) {
            angle += 0.05;
            const pulse = 4.5 + Math.sin(angle) * 0.8;
            window.galaxyGraph.nodeRelSize(pulse);
            // 🏷️ [V86.8] 呼吸效应期间也同步标签位置，确保视觉一致性
            if (typeof syncGalaxyLabels === 'function') syncGalaxyLabels();
        }
    }, 100);


    if (typeof refreshGalaxy === 'function') refreshGalaxy();

    // 📏 [V86.9] 响应式监听：使用 ResizeObserver 实时捕获容器尺寸变化
    // 无论是窗口缩放还是侧边栏切换，都能精准重绘图谱中心并同步标签
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            if (window.galaxyGraph) {
                const { width, height } = entry.contentRect;
                window.galaxyGraph.width(width);
                window.galaxyGraph.height(height);
                if (typeof syncGalaxyLabels === 'function') syncGalaxyLabels();
            }
        }
    });
    resizeObserver.observe(elem);
};

window.refreshGalaxy = async () => {
    if (!window.galaxyGraph || typeof apiFetch !== 'function') return;
    const data = await apiFetch('/api/galaxy/graph');
    if (data) {
        window.galaxyGraph.graphData(data);
        // 初始化标签 DOM
        if (typeof updateGalaxyLabelElements === 'function') updateGalaxyLabelElements(data.nodes);
    }
};

/**
 * 🏷️ [V86.5] Obsidian 风格标签同步引擎
 */
window.updateGalaxyLabelElements = (nodes) => {
    const container = document.getElementById('galaxy-labels-layer');
    if (!container) return;
    container.innerHTML = ''; // 清空旧标签
    
    nodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'tactical-node-label';
        div.id = `label-${node.id}`;
        
        // 🧼 [V86.6] 清理标题：去掉路径和扩展名
        const rawTitle = node.title || node.id;
        const cleanTitle = rawTitle.split('/').pop().replace(/\.[^/.]+$/, "");
        
        div.innerText = cleanTitle;
        div.style.position = 'absolute';
        div.style.transform = 'translate(-50%, 15px)'; // 居中并向下偏移
        container.appendChild(div);
    });
};

window.syncGalaxyLabels = () => {
    const container = document.getElementById('galaxy-labels-layer');
    const graph = window.galaxyGraph;
    if (!container || !graph) return;

    const nodes = graph.graphData().nodes;
    const camera = graph.camera();
    const camPos = camera.position;

    // 🛡️ [V86.8] 提取相机前向向量 (Forward Vector) 用于后方裁剪
    const matrix = camera.matrixWorld.elements;
    const camDir = { x: -matrix[8], y: -matrix[9], z: -matrix[10] };

    nodes.forEach(node => {
        const el = document.getElementById(`label-${node.id}`);
        if (!el) return;

        // 1. 深度校验：防止节点在相机后方时投影“回跳”到屏幕
        const toNode = { x: node.x - camPos.x, y: node.y - camPos.y, z: node.z - camPos.z };
        const dot = toNode.x * camDir.x + toNode.y * camDir.y + toNode.z * camDir.z;

        if (dot <= 0) {
            el.style.display = 'none';
            return;
        }

        // 2. 核心：3D 坐标转 2D 屏幕坐标
        const pos = graph.graph2ScreenCoords(node.x, node.y, node.z);
        
        if (pos) {
            // 📏 [V86.6] 计算相机距离以实现动态缩放
            const dist = Math.sqrt(
                Math.pow(node.x - camPos.x, 2) +
                Math.pow(node.y - camPos.y, 2) +
                Math.pow(node.z - camPos.z, 2)
            );

            // 动态字号计算 (更平缓的衰减，增加远端可见度)
            const fontSize = Math.max(0, 18 - dist / 85);
            
            // Obsidian 风格：过小时消失，只保留星球亮点
            if (fontSize < 4) {
                el.style.opacity = 0;
            } else {
                el.style.display = 'block';
                el.style.opacity = Math.min(1, (fontSize - 4) / 4); // 平滑渐入
                el.style.left = `${pos.x}px`;
                el.style.top = `${pos.y}px`;
                el.style.fontSize = `${fontSize}px`;
            }
            // 🔒 [V86.7] 必须禁用指针事件，否则会阻挡 3D 节点的点击交互
            el.style.pointerEvents = 'none';
        } else {
            el.style.display = 'none';
        }
    });
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
