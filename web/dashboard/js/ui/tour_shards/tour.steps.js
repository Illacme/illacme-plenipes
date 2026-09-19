/**
 * 🧭 [V82.0] Illacme Plenipes Tour System - Steps Configuration & Brand State Shard
 * 职责：提供工作台 6 步黄金流线定义、示范品牌对正检测、步骤视觉特效与 WebGL 3D 星系自旋控制器。
 */

(function () {
    'use strict';

    // 导览步骤配置 (6 步黄金流线)
    window.TOUR_STEPS = [
        {
            selector: '.logo-section',
            title: '🏷️ 品牌切换入口',
            desc: '这里是您的独立出版社总控入口。当前已对正官方示范品牌<strong>「创作者指南」</strong>（包含 30+ 篇示范原稿与完整装帧排版）。未来您可随心创建并管理多个独立出版品牌，实现多站矩阵隔离运营。',
            proTip: '💡 探索秘籍：点击左上角品牌徽标，可随时唤起出版领航仪与专属建站向导。',
            placement: 'bottom-start',
            padding: 6
        },
        {
            selector: '#left-sidebar',
            title: '🛠️ 出版发行流程',
            desc: '左侧流水线贯穿<strong>原稿采编、多语言翻译、装帧主题、网址路径、独立站托管及社交媒体分发</strong> 6 大关键环节，实时感知各环节就绪状态。',
            proTip: '💡 探索秘籍：点击边栏边缘的 ◀ 收缩按钮，可一键折叠进入超宽屏沉浸模式！',
            placement: 'right-center',
            padding: 4,
            requireSidebarLeft: true
        },
        {
            selector: '.nav-tabs-wrapper',
            title: '🧭 核心功能导航',
            desc: '顶部导航可快速切换至<strong>原稿文库、算力中心、插件中心、治理中心及系统遥测</strong>等工作台，涵盖内容创作与全域发行的全生命周期。',
            proTip: '💡 探索秘籍：各工作台支持独立状态记忆，随时为您保存未完成的配置与草稿。',
            placement: 'bottom-center',
            padding: 6
        },
        {
            selector: '#galaxy-3d',
            title: '🌌 知识关联图谱',
            desc: '中心舞台运行着工业级 WebGL 3D 引力图谱引擎，直观呈现<strong>海量 Markdown 原稿与全球多语种译文</strong>之间的拓扑关联、引力密度与星空互联。',
            proTip: '💡 交互探索：鼠标滚轮缩放景深、按住右键 360° 旋转视角、左键点击星球直达原稿！',
            placement: 'stage-center',
            padding: 0
        },
        {
            selector: '#right-sidebar',
            title: '🤖 智能协作助手',
            desc: '右侧内嵌主权 AI Copilot，支持智能原稿检索、执行工作台指令、调取 SOP 规范与系统监控，全程辅助您的出版与内容管理。',
            proTip: '💡 探索秘籍：随时按下 Cmd/Ctrl + K 快捷键，可唤起全站主权指令调色板（Palette）！',
            placement: 'left-center',
            padding: 4,
            requireSidebarRight: true
        },
        {
            selector: '.header-actions-group',
            title: '⚡ 预览发布总控',
            desc: '这里是全站出版的操作中枢，包含<strong>「⚡ 发布预览」</strong>与<strong>「🚀 全域发布」</strong>双重出口。<br><br>💡 <strong>本地预览指引</strong>：在正式发布前，您可以随时点击上方高亮指示的<strong>【⚡ 发布预览】</strong>按钮，即可在本地秒级预览完整的编译排版与多语言网页效果；确认无误后再执行全域发布。',
            proTip: '💡 启航指引：点击下方「完成导览」即可进入工作台，右侧 AI 助手已就绪为您服务！',
            placement: 'bottom-end',
            padding: 4,
            isFinal: true
        }
    ];

    var _brandWatcherTimer = null;
    var _galaxyOrbitRaf = null;
    var _galaxyOrbitAngle = 0;

    function _stopBrandWatcher() {
        if (_brandWatcherTimer) {
            clearInterval(_brandWatcherTimer);
            _brandWatcherTimer = null;
        }
    }
    window._stopBrandWatcher = _stopBrandWatcher;

    function _startBrandWatcher() {
        _stopBrandWatcher();
        _brandWatcherTimer = setInterval(function () {
            if (!window._isTourActive || (typeof window._tourGetCurrentStep === 'function' && window._tourGetCurrentStep() !== 0)) {
                _stopBrandWatcher();
                return;
            }
            if (_isDefaultBrandActive()) {
                _stopBrandWatcher();
                if (typeof window._tourRenderStep === 'function') {
                    window._tourRenderStep(0);
                }
            }
        }, 350);
    }
    window._startBrandWatcher = _startBrandWatcher;

    function _isDefaultBrandActive() {
        var badgeEl = document.getElementById('active-imprint-name');
        var badgeName = (badgeEl && badgeEl.innerText) ? badgeEl.innerText.trim() : '';

        if (badgeName && badgeName !== 'LOADING...' && badgeName !== 'UNKNOWN') {
            return badgeName === '创作者指南' || badgeName === 'Illacme Press 创作者指南' || badgeName === 'Illacme Plenipes 创作者指南';
        }
        if (window.settingsData && typeof window.settingsData._active_imprint !== 'undefined') {
            return window.settingsData._active_imprint === 'default';
        }
        return false;
    }
    window._isDefaultBrandActive = _isDefaultBrandActive;

    window._onTourBrandSwitched = function () {
        var curStep = (typeof window._tourGetCurrentStep === 'function') ? window._tourGetCurrentStep() : 0;
        if (!window._isTourActive || curStep !== 0) return;
        _stopBrandWatcher();
        if (typeof window._tourRenderStep === 'function') {
            window._tourRenderStep(0);
        }
    };

    window.isTourActive = function () {
        return !!(window._isTourActive && document.querySelector('.dashboard-tour-overlay'));
    };

    window.unlockTourBrand = function () {
        window._isTourActive = false;
        var triggerEl = document.getElementById('imprint-selector-trigger');
        if (triggerEl) {
            triggerEl.classList.remove('tour-target-beacon', 'tour-brand-locked', 'tour-shimmer-capsule');
            triggerEl.removeAttribute('title');
        }
        var headerEl = document.querySelector('header');
        var logoSec = document.querySelector('.logo-section');
        var imprintDrop = document.getElementById('imprint-dropdown');
        if (headerEl) headerEl.classList.remove('tour-header-interactive');
        if (logoSec) logoSec.classList.remove('tour-interactive');
        if (imprintDrop) imprintDrop.classList.remove('tour-interactive');
    };

    function _startGalaxyOrbit() {
        if (!window.galaxyGraph) return;
        if (typeof window.resumeGalaxy === 'function') window.resumeGalaxy();
        _stopGalaxyOrbit();

        var initialPos = window.galaxyGraph.cameraPosition();
        var distance = Math.hypot(initialPos.x, initialPos.z) || 600;
        var currentY = initialPos.y || 0;
        _galaxyOrbitAngle = Math.atan2(initialPos.x, initialPos.z) || 0;

        var lastTime = performance.now();
        var orbitSpeed = 0.00045; // 弧度/毫秒

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
    window._startGalaxyOrbit = _startGalaxyOrbit;

    function _stopGalaxyOrbit() {
        if (_galaxyOrbitRaf) {
            cancelAnimationFrame(_galaxyOrbitRaf);
            _galaxyOrbitRaf = null;
        }
    }
    window._stopGalaxyOrbit = _stopGalaxyOrbit;

    /**
     * 🌈 动态适配各步骤的专属视觉层叠特效、品牌指示光晕与 3D 自旋控制
     */
    window._applyStepVisualEffects = function (stepIndex, step) {
        var headerEl = document.querySelector('header');
        var logoSec = document.querySelector('.logo-section');
        var imprintDrop = document.getElementById('imprint-dropdown');
        var triggerEl = document.getElementById('imprint-selector-trigger');
        var spotlightEl = window._tourSpotlightEl;
        var isDefault = _isDefaultBrandActive();

        if (stepIndex === 0) {
            if (headerEl) headerEl.classList.add('tour-header-interactive');
            if (logoSec) logoSec.classList.add('tour-interactive');
            if (imprintDrop) imprintDrop.classList.add('tour-interactive');
            if (triggerEl) triggerEl.classList.add('tour-shimmer-capsule');

            if (!isDefault) {
                if (spotlightEl) spotlightEl.classList.add('spotlight-active-guide');
                if (triggerEl) {
                    triggerEl.classList.add('tour-target-beacon');
                    triggerEl.classList.remove('tour-brand-locked');
                    triggerEl.setAttribute('title', '👉 请点击此处，选择「创作者指南」进行切换');
                }
            } else {
                if (spotlightEl) spotlightEl.classList.remove('spotlight-active-guide');
                if (triggerEl) {
                    triggerEl.classList.remove('tour-target-beacon');
                    triggerEl.classList.add('tour-brand-locked');
                    triggerEl.setAttribute('title', '🧭 导览进行中，已锁定官方示范品牌「创作者指南」');
                }
            }
        } else {
            if (headerEl) headerEl.classList.remove('tour-header-interactive');
            if (logoSec) logoSec.classList.remove('tour-interactive');
            if (imprintDrop) imprintDrop.classList.remove('tour-interactive');
            if (spotlightEl) spotlightEl.classList.remove('spotlight-active-guide');
            if (triggerEl) {
                triggerEl.classList.remove('tour-shimmer-capsule');
                triggerEl.classList.remove('tour-target-beacon');
                triggerEl.classList.add('tour-brand-locked');
                triggerEl.setAttribute('title', '🧭 导览进行中，已锁定官方示范品牌「创作者指南」');
            }
        }

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

        // 🌊 步骤 2 聚焦时的流水线级联流光扫描
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

        return transitioned;
    };

})();
