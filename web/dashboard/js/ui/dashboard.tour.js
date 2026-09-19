/**
 * 🧭 [V82.0] Illacme Plenipes Dashboard Tour System - UI/UX Sovereignty Controller
 * 职责：主控制器调度、工作台 6 步漫游生命周期管理、事件总线监听与自愈恢复。
 */

(function () {
    'use strict';

    var _currentStep = 0;
    var _initialSidebarState = { left: false, right: false };
    var _rafId = null;

    window._tourGetCurrentStep = function () {
        return _currentStep;
    };

    /**
     * 启动工作台漫游导览
     */
    window.startDashboardTour = function (options) {
        if (window._isTourActive) return;
        options = options || {};
        var steps = window.TOUR_STEPS || [];
        var startStep = (typeof options.startStep === 'number' && options.startStep >= 0 && options.startStep < steps.length)
            ? options.startStep : 0;
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

        // 3. 构建 DOM 容器并渲染第一步
        if (typeof window._createTourElements === 'function') {
            window._createTourElements();
        }
        _currentStep = startStep;
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
        if (typeof window.unlockTourBrand === 'function') {
            window.unlockTourBrand();
        }
        if (typeof window._stopBrandWatcher === 'function') {
            window._stopBrandWatcher();
        }

        // 移除监听
        window.removeEventListener('resize', _onResize);
        window.removeEventListener('keydown', _onKeyDown);
        if (_rafId) cancelAnimationFrame(_rafId);

        try {
            sessionStorage.removeItem('_illacme_tour_resume_step');
        } catch (_) { }

        // 恢复边栏原始折叠状态
        var appContainer = document.getElementById('app-container');
        if (appContainer) {
            if (_initialSidebarState.left) appContainer.classList.add('left-collapsed');
            if (_initialSidebarState.right) appContainer.classList.add('right-collapsed');
        }

        // 停止 3D 星系自旋
        if (typeof window._stopGalaxyOrbit === 'function') {
            window._stopGalaxyOrbit();
        }

        // 淡出并清理 DOM
        if (typeof window._destroyTourElements === 'function') {
            window._destroyTourElements();
        }

        // 标记完成状态
        try {
            localStorage.setItem('illacme_tour_completed', 'true');
        } catch (_) { }

        // 若为最终步触发发布预览
        if (options.triggerPreview) {
            if (typeof window.triggerPublishAndPreview === 'function') {
                window.triggerPublishAndPreview();
            } else if (typeof window.triggerPreview === 'function') {
                window.triggerPreview();
            }
        }
    };

    function _renderStep(stepIndex) {
        var steps = window.TOUR_STEPS || [];
        var step = steps[stepIndex];
        if (!step) return;

        // 调度步骤专属视觉光效与 3D 自旋（由 tour.steps.js 供给）
        var transitioned = false;
        if (typeof window._applyStepVisualEffects === 'function') {
            transitioned = window._applyStepVisualEffects(stepIndex, step);
        }

        var applyPosition = function () {
            var targetEl = document.querySelector(step.selector);
            if (!targetEl && step.placement !== 'stage-center') {
                console.warn('[Tour] Target element not found for selector:', step.selector);
                if (typeof window._updateSpotlightAndTooltip === 'function') {
                    window._updateSpotlightAndTooltip(null, step, stepIndex);
                }
                return;
            }
            if (typeof window._updateSpotlightAndTooltip === 'function') {
                window._updateSpotlightAndTooltip(targetEl, step, stepIndex);
            }
        };

        if (transitioned) {
            setTimeout(applyPosition, 80);
        } else {
            applyPosition();
        }
    }
    window._tourRenderStep = _renderStep;

    // 监听全域品牌热重载事件，如果在 STEP 1 进行中则自愈刷新卡片与按钮状态
    if (window.feBus && typeof window.feBus.on === 'function') {
        window.feBus.on('IMPRINT_CHANGED', function () {
            if (window._isTourActive && _currentStep === 0) {
                _renderStep(0);
            }
        });
        window.feBus.on('IMPRINT_SWITCHED', function () {
            if (window._isTourActive && _currentStep === 0) {
                _renderStep(0);
            }
        });
    }

    window._tourNextStep = function () {
        var isDefault = (typeof window._isDefaultBrandActive === 'function') ? window._isDefaultBrandActive() : true;
        if (_currentStep === 0 && !isDefault) {
            if (typeof window._tourAlertSwitchBrand === 'function') window._tourAlertSwitchBrand();
            return;
        }
        if (typeof window._stopBrandWatcher === 'function') window._stopBrandWatcher();
        var steps = window.TOUR_STEPS || [];
        if (_currentStep < steps.length - 1) {
            _currentStep++;
            _renderStep(_currentStep);
        }
    };

    window._tourPrevStep = function () {
        if (typeof window._stopBrandWatcher === 'function') window._stopBrandWatcher();
        if (_currentStep > 0) {
            _currentStep--;
            _renderStep(_currentStep);
        }
    };

    window._tourJumpToStep = function (targetIndex) {
        var steps = window.TOUR_STEPS || [];
        if (targetIndex >= 0 && targetIndex < steps.length) {
            var isDefault = (typeof window._isDefaultBrandActive === 'function') ? window._isDefaultBrandActive() : true;
            if (_currentStep === 0 && targetIndex > 0 && !isDefault) {
                if (typeof window._tourAlertSwitchBrand === 'function') window._tourAlertSwitchBrand();
                return;
            }
            if (typeof window._stopBrandWatcher === 'function') window._stopBrandWatcher();
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

    /**
     * 🎉 导览完结并触发新人启航里程碑与 Copilot 联动
     */
    window._tourCompleteTour = function () {
        var btn = document.getElementById('tour-complete-btn');
        if (btn) {
            btn.innerHTML = '🎉 正在完成...';
            btn.disabled = true;
        }
        setTimeout(function () {
            window.closeDashboardTour({ isCompletion: true });
            if (typeof window._showTourMilestoneAndActivateCopilot === 'function') {
                window._showTourMilestoneAndActivateCopilot();
            }
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
            var isDefault = (typeof window._isDefaultBrandActive === 'function') ? window._isDefaultBrandActive() : true;
            if (_currentStep === 0 && !isDefault) {
                if (typeof window._tourAlertSwitchBrand === 'function') window._tourAlertSwitchBrand();
                return;
            }
            window._tourNextStep();
        } else if (e.key === 'ArrowLeft') {
            window._tourPrevStep();
        }
    }

    // 🔄 [自动恢复导览] 页面刷新或切换品牌后若处于导览进行态，无缝自愈恢复
    if (typeof window !== 'undefined') {
        window.addEventListener('load', function () {
            try {
                var resumeStep = sessionStorage.getItem('_illacme_tour_resume_step');
                if (resumeStep !== null) {
                    sessionStorage.removeItem('_illacme_tour_resume_step');
                    var targetStep = parseInt(resumeStep, 10) || 0;
                    setTimeout(function () {
                        if (typeof window.startDashboardTour === 'function') {
                            window.startDashboardTour({ startStep: targetStep });
                        }
                    }, 450);
                }
            } catch (_) { }
        });
    }

})();
