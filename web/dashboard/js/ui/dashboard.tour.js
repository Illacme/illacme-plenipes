/**
 * 🧭 [V82.0] Illacme Plenipes Dashboard Tour System - UI/UX Sovereignty Controller
 * 职责：提供工作台 6 步沉浸式漫游导览，包含知识星系说明、探索秘籍胶囊、动态空间避让定位与发布预览闭环。
 */

(function () {
    'use strict';

    // 导览步骤配置 (6 步黄金流线)
    var TOUR_STEPS = [
        {
            selector: '.logo-section',
            title: '🏷️ 品牌出版疆域',
            desc: '这里是您的独立出版社总控入口。系统已为您预置官方示范品牌<strong>「Illacme Press 创作者指南」</strong>。未来您可随心创建并管理多个独立出版品牌，实现多站矩阵隔离运营。',
            proTip: '💡 探索秘籍：点击左上角品牌徽标，可随时呼出出版工作台与专属建站向导。',
            placement: 'bottom-start',
            padding: 6
        },
        {
            selector: '#left-sidebar',
            title: '🛠️ 出版与分发全流水线',
            desc: '左侧流水线贯穿<strong>原稿采编、多语言翻译、装帧主题、网址路径、独立站托管及社交媒体分发</strong> 6 大关键环节，实时感知各环节就绪状态。',
            proTip: '💡 探索秘籍：点击边栏边缘的 ◀ 收缩按钮，可一键折叠进入超宽屏沉浸模式！',
            placement: 'right-center',
            padding: 4,
            requireSidebarLeft: true
        },
        {
            selector: '.nav-tabs-wrapper',
            title: '🧭 七大多维工作台',
            desc: '顶部导航可快速切换至<strong>原稿文库、算力中心、插件中心、治理中心及系统遥测</strong>等工作台，涵盖内容创作与全域发行的全生命周期。',
            proTip: '💡 探索秘籍：各工作台支持独立状态记忆，随时为您保存未完成的配置与草稿。',
            placement: 'bottom-center',
            padding: 6
        },
        {
            selector: '#galaxy-3d',
            title: '🌌 3D 知识引力星系',
            desc: '中心舞台运行着工业级 WebGL 3D 引力图谱引擎，直观呈现<strong>海量 Markdown 原稿与全球多语种译文</strong>之间的拓扑关联、引力密度与星空互联。',
            proTip: '💡 交互探索：鼠标滚轮缩放景深、按住右键 360° 旋转视角、左键点击星球直达原稿！',
            placement: 'stage-center',
            padding: 0
        },
        {
            selector: '#right-sidebar',
            title: '🤖 主权 AI 协作助手',
            desc: '右侧内嵌主权 AI Copilot，支持智能原稿检索、执行工作台指令、调取 SOP 规范与系统监控，全程辅助您的出版与内容管理。',
            proTip: '💡 探索秘籍：随时按下 Cmd/Ctrl + K 快捷键，可唤起全站主权指令调色板（Palette）！',
            placement: 'left-center',
            padding: 4,
            requireSidebarRight: true
        },
        {
            selector: '.header-actions-group',
            title: '⚡ 开启首次发布预览',
            desc: '这里是全站出版的操作中枢，包含<strong>「⚡ 发布预览」</strong>与<strong>「🚀 全域发布」</strong>双重出口。在当前导览阶段，建议您点击<strong>「发布预览」</strong>在本地查看完整的编译与渲染效果（「全域发布」将在配置好云端凭证后开启全球一键同步）。',
            proTip: '💡 视觉彩蛋：在底栏右下角可随心切换「🌙 暗夜黑客」与「☀️ 白昼高奢」双主题！',
            placement: 'bottom-end',
            padding: 4,
            isFinal: true
        }
    ];

    var _currentStep = 0;
    var _overlayEl = null;
    var _spotlightEl = null;
    var _tooltipEl = null;
    var _initialSidebarState = { left: false, right: false };
    var _rafId = null;
    var _galaxyOrbitRaf = null;
    var _galaxyOrbitAngle = 0;

    function _startGalaxyOrbit() {
        if (!window.galaxyGraph) return;
        if (typeof window.resumeGalaxy === 'function') window.resumeGalaxy();
        _stopGalaxyOrbit();

        var initialPos = window.galaxyGraph.cameraPosition();
        var distance = Math.hypot(initialPos.x, initialPos.z) || 600;
        var currentY = initialPos.y || 0;
        _galaxyOrbitAngle = Math.atan2(initialPos.x, initialPos.z) || 0;

        var lastTime = performance.now();
        var orbitSpeed = 0.00045; // 弧度/毫秒，平滑优雅的环绕自旋

        var orbitLoop = function (time) {
            if (!_galaxyOrbitRaf) return;
            var dt = time - lastTime;
            lastTime = time;
            if (dt > 100) dt = 16;

            _galaxyOrbitAngle += orbitSpeed * dt;
            var x = distance * Math.sin(_galaxyOrbitAngle);
            var z = distance * Math.cos(_galaxyOrbitAngle);
            if (window.galaxyGraph) {
                window.galaxyGraph.cameraPosition({ x: x, y: currentY, z: z });
            }
            _galaxyOrbitRaf = requestAnimationFrame(orbitLoop);
        };

        _galaxyOrbitRaf = requestAnimationFrame(function (time) {
            lastTime = time;
            orbitLoop(time);
        });
    }

    function _stopGalaxyOrbit() {
        if (_galaxyOrbitRaf) {
            cancelAnimationFrame(_galaxyOrbitRaf);
            _galaxyOrbitRaf = null;
        }
    }

    /**
     * 启动工作台漫游导览
     */
    window.startDashboardTour = function () {
        if (window._isTourActive) return;
        window._isTourActive = true;

        // 0. 隐藏 Launchpad 弹窗，露出中心舞台 3D 知识星系
        if (typeof window.toggleHub === 'function') {
            window.toggleHub('hide');
        } else {
            var hub = document.getElementById('command-hub-overlay');
            if (hub) hub.style.display = 'none';
        }

        // 1. 视图自愈复位：确保处于 overview 视图
        if (window.currentView !== 'overview' && typeof window.showView === 'function') {
            window.showView('overview');
        }

        // 2. 记录初始边栏折叠状态
        var appContainer = document.getElementById('app-container');
        if (appContainer) {
            _initialSidebarState.left = appContainer.classList.contains('left-collapsed');
            _initialSidebarState.right = appContainer.classList.contains('right-collapsed');
        }

        // 3. 构建 DOM 容器
        _createTourElements();
        _currentStep = 0;
        _renderStep(_currentStep);

        // 4. 绑定全局事件
        window.addEventListener('resize', _onResize);
        window.addEventListener('keydown', _onKeyDown);
    };

    /**
     * 退出/销毁导览
     */
    window.closeDashboardTour = function (options) {
        options = options || {};
        window._isTourActive = false;

        // 移除监听
        window.removeEventListener('resize', _onResize);
        window.removeEventListener('keydown', _onKeyDown);
        if (_rafId) cancelAnimationFrame(_rafId);

        // 恢复边栏原始折叠状态
        var appContainer = document.getElementById('app-container');
        if (appContainer) {
            if (_initialSidebarState.left) appContainer.classList.add('left-collapsed');
            if (_initialSidebarState.right) appContainer.classList.add('right-collapsed');
        }

        // 停止 3D 星系自旋
        _stopGalaxyOrbit();

        // 淡出并清理 DOM
        if (_overlayEl) {
            _overlayEl.classList.remove('active');
            setTimeout(function () {
                if (_overlayEl && _overlayEl.parentNode) {
                    _overlayEl.parentNode.removeChild(_overlayEl);
                }
                _overlayEl = null;
                _spotlightEl = null;
                _tooltipEl = null;
            }, 300);
        }

        // 标记完成状态
        try {
            localStorage.setItem('illacme_tour_completed', 'true');
        } catch (_) {}

        // 若为最终步触发发布预览
        if (options.triggerPreview) {
            if (typeof window.triggerPublishAndPreview === 'function') {
                window.triggerPublishAndPreview();
            } else if (typeof window.triggerPreview === 'function') {
                window.triggerPreview();
            }
        }
    };

    function _createTourElements() {
        if (_overlayEl && _overlayEl.parentNode) {
            _overlayEl.parentNode.removeChild(_overlayEl);
        }

        _overlayEl = document.createElement('div');
        _overlayEl.className = 'dashboard-tour-overlay';

        _spotlightEl = document.createElement('div');
        _spotlightEl.className = 'tour-spotlight-box pulse';

        _tooltipEl = document.createElement('div');
        _tooltipEl.className = 'tour-tooltip-card';

        _overlayEl.appendChild(_spotlightEl);
        _overlayEl.appendChild(_tooltipEl);
        document.body.appendChild(_overlayEl);

        // 激活透明度过渡
        requestAnimationFrame(function () {
            if (_overlayEl) _overlayEl.classList.add('active');
        });
    }

    function _renderStep(stepIndex) {
        var step = TOUR_STEPS[stepIndex];
        if (!step) return;

        // 边栏智能展开支持
        var appContainer = document.getElementById('app-container');
        var transitioned = false;
        if (appContainer) {
            if (step.requireSidebarLeft && appContainer.classList.contains('left-collapsed')) {
                appContainer.classList.remove('left-collapsed');
                transitioned = true;
            }
            if (step.requireSidebarRight && appContainer.classList.contains('right-collapsed')) {
                appContainer.classList.remove('right-collapsed');
                transitioned = true;
            }
        }

        // 🌊 步骤 2 聚焦时的流水线级联流光扫描 (Pipeline Cascade Shimmer)
        if (stepIndex === 1) {
            var capsules = document.querySelectorAll('#left-sidebar .pipeline-capsule');
            capsules.forEach(function (cap, idx) {
                cap.classList.remove('tour-cascade-shimmer');
                void cap.offsetWidth;
                cap.style.animationDelay = (idx * 0.08) + 's';
                cap.classList.add('tour-cascade-shimmer');
            });
        }

        // 🌌 3D 星系物理缓动自旋光效支持
        if (stepIndex === 3) {
            _startGalaxyOrbit();
        } else {
            _stopGalaxyOrbit();
        }

        var applyPosition = function () {
            var targetEl = document.querySelector(step.selector);
            if (!targetEl && step.placement !== 'stage-center') {
                console.warn('[Tour] Target element not found for selector:', step.selector);
                _updateSpotlightAndTooltip(null, step, stepIndex);
                return;
            }
            _updateSpotlightAndTooltip(targetEl, step, stepIndex);
        };

        if (transitioned) {
            setTimeout(applyPosition, 80);
        } else {
            applyPosition();
        }
    }

    function _updateSpotlightAndTooltip(targetEl, step, stepIndex) {
        var pad = step.padding || 0;
        var rect;

        if (step.placement === 'stage-center') {
            // 中心知识星系舞台精确取自 #main-viewport 物理边界
            var mainVp = document.getElementById('main-viewport') || document.getElementById('view-overview');
            if (mainVp) {
                var vpRect = mainVp.getBoundingClientRect();
                // 留出内边距 8px，使聚光灯外框完全位于主视口内，不压到顶栏、底栏及左右边栏
                rect = {
                    top: vpRect.top + 8,
                    left: vpRect.left + 8,
                    right: vpRect.right - 8,
                    bottom: vpRect.bottom - 8,
                    width: Math.max(200, vpRect.width - 16),
                    height: Math.max(200, vpRect.height - 16)
                };
                pad = 0;
            } else {
                rect = {
                    top: 80,
                    left: 270,
                    width: window.innerWidth - 600,
                    height: window.innerHeight - 130
                };
                pad = 0;
            }
        } else {
            rect = targetEl ? targetEl.getBoundingClientRect() : {
                top: window.innerHeight / 2 - 50,
                left: window.innerWidth / 2 - 100,
                width: 200,
                height: 100
            };
        }

        // 1. 设置高亮框位置
        if (_spotlightEl) {
            _spotlightEl.style.top = Math.max(0, rect.top - pad) + 'px';
            _spotlightEl.style.left = Math.max(0, rect.left - pad) + 'px';
            _spotlightEl.style.width = (rect.width + pad * 2) + 'px';
            _spotlightEl.style.height = (rect.height + pad * 2) + 'px';
        }

        // 2. 渲染气泡卡片内容
        var totalSteps = TOUR_STEPS.length;
        var stepNumStr = 'STEP ' + (stepIndex + 1) + ' / ' + totalSteps;

        var pillsHtml = '<div class="tour-pills-bar">';
        for (var i = 0; i < totalSteps; i++) {
            var cls = 'tour-pill';
            if (i === stepIndex) cls += ' active';
            else if (i < stepIndex) cls += ' passed';
            var cleanTitle = (TOUR_STEPS[i].title || '').replace(/<[^>]+>/g, '');
            pillsHtml += '<div class="' + cls + '" onclick="window._tourJumpToStep(' + i + ')" title="第 ' + (i + 1) + ' 步：' + cleanTitle + '"></div>';
        }
        pillsHtml += '</div>';

        var prevBtnHtml = stepIndex > 0
            ? '<button class="tour-btn tour-btn-prev" onclick="window._tourPrevStep()">← 上一步</button>'
            : '';

        var nextBtnHtml = step.isFinal
            ? '<button class="tour-btn tour-btn-launch" id="tour-launch-btn" onclick="window._tourLaunchPreview()">⚡ 立即启动发布预览</button>'
            : '<button class="tour-btn tour-btn-next" onclick="window._tourNextStep()">下一步 →</button>';

        var proTipHtml = step.proTip
            ? '<div class="tour-pro-tip"><span class="tour-pro-tip-icon">✨</span><span class="tour-pro-tip-text">' + step.proTip + '</span></div>'
            : '';

        _tooltipEl.innerHTML =
            '<div class="tour-header">' +
                '<span class="tour-step-badge">' + stepNumStr + '</span>' +
                pillsHtml +
                '<button class="tour-close-btn" onclick="window.closeDashboardTour()" title="退出导览 (Esc)">×</button>' +
            '</div>' +
            '<div class="tour-body">' +
                '<h3 class="tour-title">' + step.title + '</h3>' +
                '<p class="tour-desc">' + step.desc + '</p>' +
                proTipHtml +
            '</div>' +
            '<div class="tour-footer">' +
                '<div class="tour-skip-group">' +
                    '<button class="tour-btn-skip" onclick="window.closeDashboardTour()">跳过导览</button>' +
                    '<span class="tour-keyboard-hint">⌨️ ← / → 翻页 · Esc 退出</span>' +
                '</div>' +
                '<div class="tour-nav-group">' + prevBtnHtml + nextBtnHtml + '</div>' +
            '</div>';

        // 3. 计算气泡智能位置（带防屏幕溢出安全钳位）
        _positionTooltip(rect, step.placement, pad);
    }

    function _positionTooltip(targetRect, placement, pad) {
        var cardW = Math.min(400, window.innerWidth - 32);
        var cardH = 260; // 预估高度
        var top = 0;
        var left = 0;
        var gap = 14;
        var isNarrow = window.innerWidth < 1000;

        if (placement === 'bottom-start') {
            top = targetRect.bottom + pad + gap;
            left = targetRect.left;
        } else if (placement === 'bottom-center') {
            top = targetRect.bottom + pad + gap;
            left = targetRect.left + (targetRect.width / 2) - (cardW / 2);
        } else if (placement === 'bottom-end') {
            top = targetRect.bottom + pad + gap;
            left = targetRect.right - cardW;
        } else if (placement === 'right-center') {
            if (isNarrow) {
                top = Math.min(window.innerHeight - cardH - 20, targetRect.top + 40);
                left = window.innerWidth / 2 - cardW / 2;
            } else {
                top = Math.max(80, targetRect.top + 60);
                left = targetRect.right + pad + gap;
            }
        } else if (placement === 'left-center') {
            if (isNarrow) {
                top = Math.min(window.innerHeight - cardH - 20, targetRect.top + 40);
                left = window.innerWidth / 2 - cardW / 2;
            } else {
                top = Math.max(80, targetRect.top + 60);
                left = targetRect.left - pad - gap - cardW;
            }
        } else if (placement === 'stage-center') {
            // 中心舞台底部停泊
            top = Math.max(100, targetRect.bottom - cardH - 24);
            left = targetRect.left + (targetRect.width / 2) - (cardW / 2);
        } else {
            top = targetRect.bottom + pad + gap;
            left = targetRect.left;
        }

        // 边界安全钳位 (Boundary Collision Guard)
        var maxLeft = window.innerWidth - cardW - 16;
        var maxTop = window.innerHeight - cardH - 16;
        left = Math.max(16, Math.min(left, maxLeft));
        top = Math.max(16, Math.min(top, maxTop));

        if (_tooltipEl) {
            _tooltipEl.style.top = top + 'px';
            _tooltipEl.style.left = left + 'px';
        }
    }

    // 步进控制与快速跳步挂载
    window._tourNextStep = function () {
        if (_currentStep < TOUR_STEPS.length - 1) {
            _currentStep++;
            _renderStep(_currentStep);
        }
    };

    window._tourPrevStep = function () {
        if (_currentStep > 0) {
            _currentStep--;
            _renderStep(_currentStep);
        }
    };

    window._tourJumpToStep = function (targetIndex) {
        if (targetIndex >= 0 && targetIndex < TOUR_STEPS.length) {
            _currentStep = targetIndex;
            _renderStep(_currentStep);
        }
    };

    window._tourLaunchPreview = function () {
        var btn = document.getElementById('tour-launch-btn');
        if (btn) {
            btn.innerHTML = '⚡ 正在启动预览...';
            btn.disabled = true;
        }
        setTimeout(function () {
            window.closeDashboardTour({ triggerPreview: true });
        }, 180);
    };

    function _onResize() {
        if (!window._isTourActive) return;
        if (_rafId) cancelAnimationFrame(_rafId);
        _rafId = requestAnimationFrame(function () {
            _renderStep(_currentStep);
        });
    }

    function _onKeyDown(e) {
        if (!window._isTourActive) return;
        if (e.key === 'Escape') {
            window.closeDashboardTour();
        } else if (e.key === 'ArrowRight') {
            window._tourNextStep();
        } else if (e.key === 'ArrowLeft') {
            window._tourPrevStep();
        }
    }

})();
