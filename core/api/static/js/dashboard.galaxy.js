/**
 * 🚀 Illacme Plenipes Dashboard 3D Galaxy Engine
 * 职责：初始化 ForceGraph3D、定时刷新物理图谱网络，Obsidian 标签洗白及相机 2D 坐标轴深度映射。
 */

// 1. 3D 宇宙引擎 (Sovereign Refinement)
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
            if (typeof window.syncGalaxyLabels === 'function') {
                window.syncGalaxyLabels();
            }
        });

    // 🌪️ [V86.0] Kinetic Upgrade: Native Auto-Rotate
    window.galaxyGraph.controls().autoRotate = true;
    window.galaxyGraph.controls().autoRotateSpeed = 0.5;

    // 🔗 [V86.8] 核心修复：将标签同步绑定至相机控制器的 change 事件
    // 确保在手动旋转、缩放或惯性移动时，HTML 标签能实时跟踪 3D 节点
    window.galaxyGraph.controls().addEventListener('change', () => {
        if (typeof window.syncGalaxyLabels === 'function') {
            window.syncGalaxyLabels();
        }
    });

    // 🧪 [V86.1] Neural Pulse: Breath Dynamics
    let angle = 0;
    setInterval(() => {
        if (window.galaxyGraph) {
            angle += 0.05;
            const pulse = 4.5 + Math.sin(angle) * 0.8;
            window.galaxyGraph.nodeRelSize(pulse);
            // 🏷️ [V86.8] 呼吸效应期间也同步标签位置，确保视觉一致性
            if (typeof window.syncGalaxyLabels === 'function') {
                window.syncGalaxyLabels();
            }
        }
    }, 100);

    if (typeof window.refreshGalaxy === 'function') {
        window.refreshGalaxy();
    }

    // 📏 [V86.9] 响应式监听：使用 ResizeObserver 实时捕获容器尺寸变化
    // 无论是窗口缩放还是侧边栏切换，都能精准重绘图谱中心并同步标签
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            if (window.galaxyGraph) {
                const { width, height } = entry.contentRect;
                window.galaxyGraph.width(width);
                window.galaxyGraph.height(height);
                if (typeof window.syncGalaxyLabels === 'function') {
                    window.syncGalaxyLabels();
                }
            }
        }
    });
    resizeObserver.observe(elem);
};

// 2. 数据动态刷新
window.refreshGalaxy = async () => {
    if (!window.galaxyGraph || typeof apiFetch !== 'function') return;
    const data = await apiFetch('/api/galaxy/graph');
    if (data) {
        window.galaxyGraph.graphData(data);
        // 初始化标签 DOM
        if (typeof window.updateGalaxyLabelElements === 'function') {
            window.updateGalaxyLabelElements(data.nodes);
        }
    }
};

// 3. 🏷️ [V86.5] Obsidian 风格标签同步引擎
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

// 4. 2D 坐标轴深度映射与后方裁剪
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
