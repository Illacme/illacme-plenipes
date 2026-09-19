/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - OrbitControls & Animation Lifecycle Module
 * 职责：OrbitControls 阻尼滑行重载、Kinetic自呼吸、Neural Pulse 节流呼吸和 WebGL 渲染生命周期管理。
 * 遵循 SOP-02 模块拆分规范，代码行数严格控制在 300 行内。
 */

// 🪐 [Orbit Engine] 3D 星系平滑轨道自转全局控制器、倾角调节与旋转阻尼
let _galaxyOrbitRaf = null, _galaxyOrbitAngle = 0, _galaxyOrbitDistance = 600;
let _galaxyOrbitPausedByDrag = false, _isRotating = false, _galaxyOrbitSpeedMultiplier = 1.0;
let _galaxyOrbitIncline = 20, _galaxyOrbitDamping = true;

try {
    if (typeof localStorage !== 'undefined') {
        const savedSpeed = localStorage.getItem('illacme_galaxy_rotate_speed');
        if (savedSpeed) _galaxyOrbitSpeedMultiplier = Math.max(0.2, Math.min(3.0, parseFloat(savedSpeed) || 1.0));
        const savedIncline = localStorage.getItem('illacme_galaxy_orbit_incline');
        if (savedIncline !== null) _galaxyOrbitIncline = Math.max(0, Math.min(60, parseFloat(savedIncline) || 20));
        const savedDamping = localStorage.getItem('illacme_galaxy_rotation_damping');
        if (savedDamping !== null) _galaxyOrbitDamping = savedDamping !== 'false';
    }
} catch (e) {}

window.getGalaxyRotateSpeed = () => _galaxyOrbitSpeedMultiplier;
window.setGalaxyRotateSpeed = function (speed) {
    _galaxyOrbitSpeedMultiplier = Math.max(0.2, Math.min(3.0, parseFloat(speed) || 1.0));
    try { if (typeof localStorage !== 'undefined') localStorage.setItem('illacme_galaxy_rotate_speed', _galaxyOrbitSpeedMultiplier.toFixed(1)); } catch (e) {}
    const slider = document.getElementById('rotate-speed-slider'), label = document.getElementById('rotate-speed-val');
    if (slider && parseFloat(slider.value) !== _galaxyOrbitSpeedMultiplier) slider.value = _galaxyOrbitSpeedMultiplier.toFixed(1);
    if (label) label.innerText = `${_galaxyOrbitSpeedMultiplier.toFixed(1)}x`;
};

window.getGalaxyOrbitIncline = () => _galaxyOrbitIncline;
window.setGalaxyOrbitIncline = function (deg) {
    _galaxyOrbitIncline = Math.max(0, Math.min(60, parseFloat(deg) || 0));
    try { if (typeof localStorage !== 'undefined') localStorage.setItem('illacme_galaxy_orbit_incline', _galaxyOrbitIncline.toFixed(0)); } catch (e) {}
    const slider = document.getElementById('rotate-incline-slider'), label = document.getElementById('rotate-incline-val');
    if (slider && parseInt(slider.value) !== _galaxyOrbitIncline) slider.value = _galaxyOrbitIncline;
    if (label) label.innerText = `${_galaxyOrbitIncline}°`;
    if (_isRotating && window.galaxyGraph) {
        const rad = (_galaxyOrbitIncline * Math.PI) / 180, rXZ = _galaxyOrbitDistance * Math.cos(rad);
        window.galaxyGraph.cameraPosition({ x: rXZ * Math.sin(_galaxyOrbitAngle), y: _galaxyOrbitDistance * Math.sin(rad), z: rXZ * Math.cos(_galaxyOrbitAngle) });
    }
};

window.getGalaxyRotationDamping = () => _galaxyOrbitDamping;
window.setGalaxyRotationDamping = function (enabled) {
    _galaxyOrbitDamping = !!enabled;
    try { if (typeof localStorage !== 'undefined') localStorage.setItem('illacme_galaxy_rotation_damping', _galaxyOrbitDamping ? 'true' : 'false'); } catch (e) {}
    const chk = document.getElementById('toggle-rotation-damping') || document.getElementById('toggle-anti-flip');
    if (chk && chk.checked !== _galaxyOrbitDamping) chk.checked = _galaxyOrbitDamping;
    if (_isRotating && window.galaxyGraph) {
        const ctrl = window.galaxyGraph.controls();
        if (ctrl) ctrl.enableDamping = _galaxyOrbitDamping;
    }
};
window.getGalaxyAntiFlip = () => !_galaxyOrbitDamping;
window.setGalaxyAntiFlip = (enabled) => window.setGalaxyRotationDamping(!enabled);

window.shouldAutoRotateGalaxy = function () {
    try { return typeof localStorage !== 'undefined' && localStorage.getItem('illacme_galaxy_auto_rotate') === 'true'; } catch (e) { return false; }
};

window.setGalaxyAutoRotatePreference = function (enabled) {
    try { if (typeof localStorage !== 'undefined') localStorage.setItem('illacme_galaxy_auto_rotate', enabled ? 'true' : 'false'); } catch (e) {}
    enabled ? window.startGalaxyAutoRotate() : window.stopGalaxyAutoRotate(true);
    window.updateGalaxyRotateUIState(enabled);
};

window.isGalaxyAutoRotating = () => _isRotating;

/**
 * 激活平滑壮观的环绕轨道自转
 */
window.startGalaxyAutoRotate = function () {
    if (!window.galaxyGraph) return;
    _isRotating = true;
    window.stopGalaxyAutoRotate(false); // 停止遗留 RAF 但保留激活标记

    // 🔒 稳态锁定：自转启动时采用温和的 d3Alpha(0)（动力归零休眠），绝不篡改全局生命周期 cooldownTicks
    if (typeof window.galaxyGraph.d3Alpha === 'function') window.galaxyGraph.d3Alpha(0);

    // 🪐 旋转阻尼动效：根据用户配置决定是否保留阻尼滑行与周期回拉翻转动效
    const controls = window.galaxyGraph.controls();
    if (controls) controls.enableDamping = !!_galaxyOrbitDamping;

    const camPos = window.galaxyGraph.cameraPosition();
    _galaxyOrbitDistance = Math.hypot(camPos.x, camPos.y, camPos.z) || 600;
    _galaxyOrbitAngle = Math.atan2(camPos.x, camPos.z) || 0;

    let lastTime = performance.now();
    const baseOrbitSpeed = 0.00045; // 壮观平滑自转基准速度

    const orbitLoop = (time) => {
        if (!_isRotating) return;
        const dt = time - lastTime;
        lastTime = time;

        if (!_galaxyOrbitPausedByDrag && window._galaxyVisible && window.galaxyGraph) {
            const validDt = (dt > 100) ? 16 : dt;
            _galaxyOrbitAngle += baseOrbitSpeed * _galaxyOrbitSpeedMultiplier * validDt;
            const inclineRad = (_galaxyOrbitIncline * Math.PI) / 180;
            const rXZ = _galaxyOrbitDistance * Math.cos(inclineRad);
            const y = _galaxyOrbitDistance * Math.sin(inclineRad);
            const x = rXZ * Math.sin(_galaxyOrbitAngle);
            const z = rXZ * Math.cos(_galaxyOrbitAngle);
            window.galaxyGraph.cameraPosition({ x, y, z });

            if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
        }
        _galaxyOrbitRaf = requestAnimationFrame(orbitLoop);
    };

    _galaxyOrbitRaf = requestAnimationFrame((time) => { lastTime = time; orbitLoop(time); });
    window.updateGalaxyRotateUIState(true);
    console.log(`🪐 [Galaxy] 轨道环绕自转已激活 (倍率: ${_galaxyOrbitSpeedMultiplier.toFixed(1)}x, 倾角: ${_galaxyOrbitIncline}°, 旋转阻尼: ${_galaxyOrbitDamping})`);
};

/**
 * 暂停平滑自转并实现力学状态闭环恢复
 * @param {boolean} clearFlag 是否清除自转偏好标志
 */
window.stopGalaxyAutoRotate = function (clearFlag = true) {
    if (clearFlag) _isRotating = false;
    if (_galaxyOrbitRaf) { cancelAnimationFrame(_galaxyOrbitRaf); _galaxyOrbitRaf = null; }
    if (window.galaxyGraph) {
        const ctrl = window.galaxyGraph.controls();
        if (ctrl) ctrl.enableDamping = true;
        if (typeof window.galaxyGraph.cooldownTicks === 'function') window.galaxyGraph.cooldownTicks(150);
        if (typeof window.galaxyGraph.d3ReheatSimulation === 'function') window.galaxyGraph.d3ReheatSimulation();
        else if (typeof window.galaxyGraph.d3Alpha === 'function') window.galaxyGraph.d3Alpha(0.2);
    }
    if (clearFlag) {
        window.updateGalaxyRotateUIState(false);
        console.log("⏸️ [Galaxy] 轨道环绕自转已暂停，力学引擎已温和就绪");
    }
};

window.toggleGalaxyAutoRotate = function () {
    const nextState = !_isRotating;
    window.setGalaxyAutoRotatePreference(nextState);
    if (typeof window.addAudit === 'function') window.addAudit('🪐 知识星谱自转已' + (nextState ? '开启' : '暂停'), 'info');
    return nextState;
};

// 🔄 全域广播更新自转状态（指标卡片、转速滑杆、倾角与防翻转）
window.updateGalaxyRotateUIState = function (enabled) {
    const rotateBtn = document.getElementById('btn-toggle-rotate'), rotateLabel = document.getElementById('rotate-btn-label');
    if (rotateBtn && rotateLabel) {
        rotateLabel.innerText = enabled ? '🪐 自转中' : '🪐 开启自转';
        rotateBtn.classList.toggle('active-rotating', !!enabled);
        const tipText = enabled ? '点击暂停星系自转' : '点击开启星系平滑轨道自转';
        rotateBtn.title = tipText;
        if (rotateBtn.hasAttribute('data-tooltip')) rotateBtn.setAttribute('data-tooltip', tipText);
        const curTip = document.querySelector('.custom-glass-tooltip');
        if (curTip) curTip.innerText = tipText;
    }

    const cfgToggle = document.getElementById('cfg-ui-galaxy_auto_rotate');
    if (cfgToggle) cfgToggle.checked = enabled;

    const speedSlider = document.getElementById('rotate-speed-slider'), speedLabel = document.getElementById('rotate-speed-val');
    if (speedSlider) speedSlider.value = _galaxyOrbitSpeedMultiplier.toFixed(1);
    if (speedLabel) speedLabel.innerText = `${_galaxyOrbitSpeedMultiplier.toFixed(1)}x`;

    const inclineSlider = document.getElementById('rotate-incline-slider'), inclineLabel = document.getElementById('rotate-incline-val');
    if (inclineSlider) inclineSlider.value = _galaxyOrbitIncline;
    if (inclineLabel) inclineLabel.innerText = `${_galaxyOrbitIncline}°`;

    const dampingChk = document.getElementById('toggle-rotation-damping') || document.getElementById('toggle-anti-flip');
    if (dampingChk) dampingChk.checked = _galaxyOrbitDamping;
};

// 🪐 配置 OrbitControls、自转、阻尼滑行与 Kinetic 呼吸
window.setupGalaxyEngineControls = (graph) => {
    if (!graph) return;

    let isDraggingGalaxy = false, dragFrameId = null;

    const activatePhysicsEngine = () => {
        if (typeof graph.cooldownTicks === 'function') graph.cooldownTicks(150);
        if (typeof graph.d3ReheatSimulation === 'function') {
            graph.d3ReheatSimulation();
        } else if (typeof graph.d3Alpha === 'function') {
            graph.d3Alpha(0.2);
        }
    };

    const startContinuousSync = () => {
        _galaxyOrbitPausedByDrag = true; // 交互拖拽时临时挂起自转
        const ctrl = graph.controls();
        if (ctrl) ctrl.enableDamping = true; // 拖拽时保证滑行手感
        activatePhysicsEngine();
        if (isDraggingGalaxy) return;
        isDraggingGalaxy = true;
        const syncLoop = () => {
            if (!isDraggingGalaxy) return;
            if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
            dragFrameId = requestAnimationFrame(syncLoop);
        };
        dragFrameId = requestAnimationFrame(syncLoop);
    };

    const stopContinuousSync = () => {
        isDraggingGalaxy = false;
        if (dragFrameId) { cancelAnimationFrame(dragFrameId); dragFrameId = null; }
        if (typeof graph.d3AlphaTarget === 'function') graph.d3AlphaTarget(0);
        if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();

        // 拖拽释放后：重新对准当前相机的距离与角度，平滑继续旋转
        if (window.galaxyGraph) {
            const newPos = window.galaxyGraph.cameraPosition();
            _galaxyOrbitDistance = Math.hypot(newPos.x, newPos.y, newPos.z) || 600;
            _galaxyOrbitAngle = Math.atan2(newPos.x, newPos.z) || 0;
            const ctrl = window.galaxyGraph.controls();
            if (_isRotating && ctrl) ctrl.enableDamping = !!_galaxyOrbitDamping;
        }
        _galaxyOrbitPausedByDrag = false;
    };

    const controls = graph.controls();
    if (controls) {
        controls.minDistance = 15;        // 极限贴脸距离
        controls.maxDistance = 2000;      // 极限拉远距离
        controls.enablePan = true;        // 允许通过右键平移相机旋转中心
        controls.enableDamping = true;    // 启用太空滑行阻尼感
        controls.dampingFactor = 0.05;    // 阻尼强度

        controls.addEventListener('start', startContinuousSync);
        controls.addEventListener('change', () => {
            if (!isDraggingGalaxy && typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
        });
        controls.addEventListener('end', stopContinuousSync);
    }

    // 🪐 绑定节点拖动生命周期：确保拖拽任意星球瞬间激活跟随力学，鲜活拉扯
    if (typeof graph.onNodeDrag === 'function') {
        graph.onNodeDrag((node) => {
            _galaxyOrbitPausedByDrag = true;
            activatePhysicsEngine();
            if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
        });
    }
    if (typeof graph.onNodeDragEnd === 'function') {
        graph.onNodeDragEnd(() => stopContinuousSync());
    }

    // 🧪 Neural Pulse: 大规模时自动降频呼吸 + 标签持续同步
    let angle = 0;
    setInterval(() => {
        if (!window._galaxyVisible || _isRotating) return;
        if (window.galaxyGraph) {
            const nodeCount = window.galaxyGraph.graphData().nodes.length;
            const perf = window.GALAXY_PERF || { SCALE_THRESHOLD_HUGE: 5000 };
            if (nodeCount > perf.SCALE_THRESHOLD_HUGE) return;
            angle += 0.05;
            window.galaxyGraph.nodeRelSize(4.5 + Math.sin(angle) * 0.8);
            if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
        }
    }, 100);

    // 📏 响应式监听 + 容器尺寸缓存
    const elem = document.getElementById('galaxy-3d');
    if (elem) {
        window._galaxyWidth = elem.clientWidth; window._galaxyHeight = elem.clientHeight;
        const resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                if (window.galaxyGraph) {
                    const { width, height } = entry.contentRect;
                    window._galaxyWidth = width; window._galaxyHeight = height;
                    window.galaxyGraph.width(width); window.galaxyGraph.height(height);
                }
            }
        });
        resizeObserver.observe(elem);
    }

    if (window.shouldAutoRotateGalaxy()) {
        setTimeout(() => { if (window._galaxyVisible) window.startGalaxyAutoRotate(); }, 300);
    }
};

// 🛡️ [V87.0] WebGL 生命周期管理 — 星系动画暂停/恢复接口
window.pauseGalaxy = () => {
    window._galaxyVisible = false;
    window.stopGalaxyAutoRotate(false);
    if (window.galaxyGraph) window.galaxyGraph.pauseAnimation();
    console.log('⏸️ [Galaxy] 渲染循环与自转已暂停（视图离开）');
};

window.resumeGalaxy = () => {
    window._galaxyVisible = true;
    if (window.galaxyGraph) window.galaxyGraph.resumeAnimation();
    if (_isRotating || window.shouldAutoRotateGalaxy()) window.startGalaxyAutoRotate();
    console.log('▶️ [Galaxy] 渲染循环已恢复（视图激活）');
};



