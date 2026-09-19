/**
 * 🧭 [V82.0] Illacme Plenipes Tour System - Spotlight & Tooltip Rendering Shard
 * 职责：构建导览覆盖层与聚光灯 DOM、生成步骤卡片富文本拓扑、执行 Boundary Collision Guard 防溢出定位。
 */

(function () {
    'use strict';

    var _overlayEl = null;
    var _spotlightEl = null;
    var _tooltipEl = null;

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

        // 挂载到全局供控制器与外部访问
        window._tourOverlayEl = _overlayEl;
        window._tourSpotlightEl = _spotlightEl;
        window._tourTooltipEl = _tooltipEl;

        // 激活透明度过渡
        requestAnimationFrame(function () {
            if (_overlayEl) _overlayEl.classList.add('active');
        });

        return { overlay: _overlayEl, spotlight: _spotlightEl, tooltip: _tooltipEl };
    }
    window._createTourElements = _createTourElements;

    function _destroyTourElements() {
        if (_overlayEl) {
            _overlayEl.classList.remove('active');
            var elToClean = _overlayEl;
            setTimeout(function () {
                if (elToClean && elToClean.parentNode) {
                    elToClean.parentNode.removeChild(elToClean);
                }
            }, 300);
            _overlayEl = null;
            _spotlightEl = null;
            _tooltipEl = null;
            window._tourOverlayEl = null;
            window._tourSpotlightEl = null;
            window._tourTooltipEl = null;
        }
    }
    window._destroyTourElements = _destroyTourElements;

    function _updateSpotlightAndTooltip(targetEl, step, stepIndex) {
        var pad = step.padding || 0;
        var rect;

        if (step.placement === 'stage-center') {
            // 中心知识星系舞台精确取自 #main-viewport 物理边界
            var mainVp = document.getElementById('main-viewport') || document.getElementById('view-overview');
            if (mainVp) {
                var vpRect = mainVp.getBoundingClientRect();
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

        // 2. 渲染气泡卡片内容（动态适配第 1 步品牌对正检测）
        var steps = window.TOUR_STEPS || [];
        var totalSteps = steps.length;
        var stepNumStr = 'STEP ' + (stepIndex + 1) + ' / ' + totalSteps;

        var pillsHtml = '<div class="tour-pills-bar">';
        for (var i = 0; i < totalSteps; i++) {
            var cls = 'tour-pill';
            if (i === stepIndex) cls += ' active';
            else if (i < stepIndex) cls += ' passed';
            var cleanTitle = (steps[i].title || '').replace(/<[^>]+>/g, '');
            pillsHtml += '<div class="' + cls + '" onclick="window._tourJumpToStep(' + i + ')" title="第 ' + (i + 1) + ' 步：' + cleanTitle + '"></div>';
        }
        pillsHtml += '</div>';

        var prevBtnHtml = stepIndex > 0
            ? '<button class="tour-btn tour-btn-prev" onclick="window._tourPrevStep()">← 上一步</button>'
            : '';

        var isDefaultBrand = (typeof window._isDefaultBrandActive === 'function') ? window._isDefaultBrandActive() : true;
        var isStep0NonDefault = (stepIndex === 0 && !isDefaultBrand);
        var stepTitle = step.title;
        var stepDesc = step.desc;
        var stepProTip = step.proTip;
        var nextBtnHtml = '';

        if (isStep0NonDefault) {
            if (typeof window._startBrandWatcher === 'function') window._startBrandWatcher();
            var badgeEl = document.getElementById('active-imprint-name');
            var currentBrandName = (badgeEl && badgeEl.innerText && badgeEl.innerText !== 'LOADING...' && badgeEl.innerText !== 'UNKNOWN')
                ? badgeEl.innerText.trim() : '当前出版品牌';
            stepTitle = '🏷️ 品牌切换入口 · 请先切换示范品牌';
            stepDesc = '这里是您的独立出版社总控入口。当前正处于自定义品牌<strong>「' + currentBrandName + '」</strong>。<br>' +
                '<div class="tour-brand-warning-box">' +
                '💡 <strong>操作指引：</strong>工作台漫游导览围绕官方示范品牌<strong>「创作者指南」</strong>展开。<br>' +
                '<span class="guide-arrow">👉 请直接点击左上方动态高亮指示的【出版品牌 ▾】下拉菜单</span>，在列表中选中<strong>「创作者指南」</strong>完成切换。' +
                '</div>';
            stepProTip = '↖️ 视线移至左上方：请点击高亮呼吸框【出版品牌 ▾】，选中「创作者指南」切换！';

            // 保持标准单按钮结构，彻底避免任何挤压与右侧溢出
            nextBtnHtml = '<button class="tour-btn tour-btn-next disabled" onclick="window._tourAlertSwitchBrand()" title="请先在左上方点击下拉列表切换至「创作者指南」">下一步 →</button>';
        } else {
            if (typeof window._stopBrandWatcher === 'function') window._stopBrandWatcher();
            if (step.isFinal) {
                nextBtnHtml = '<button class="tour-btn tour-btn-launch tour-btn-complete" id="tour-complete-btn" onclick="window._tourCompleteTour()">🎉 完成导览</button>';
            } else {
                nextBtnHtml = '<button class="tour-btn tour-btn-next" onclick="window._tourNextStep()">下一步 →</button>';
            }
        }

        var proTipHtml = stepProTip
            ? '<div class="tour-pro-tip"><span class="tour-pro-tip-icon">✨</span><span class="tour-pro-tip-text">' + stepProTip + '</span></div>'
            : '';

        if (_tooltipEl) {
            _tooltipEl.innerHTML =
                '<div class="tour-header">' +
                '<span class="tour-step-badge">' + stepNumStr + '</span>' +
                pillsHtml +
                '<button class="tour-close-btn" onclick="window.closeDashboardTour()" title="退出导览 (Esc)">×</button>' +
                '</div>' +
                '<div class="tour-body">' +
                '<h3 class="tour-title">' + stepTitle + '</h3>' +
                '<p class="tour-desc">' + stepDesc + '</p>' +
                proTipHtml +
                '</div>' +
                '<div class="tour-footer">' +
                '<div class="tour-skip-group">' +
                '<button class="tour-btn-skip" onclick="window.closeDashboardTour()">跳过导览</button>' +
                '<span class="tour-keyboard-hint">⌨️ ← / → 翻页 · Esc 退出</span>' +
                '</div>' +
                '<div class="tour-nav-group">' + prevBtnHtml + nextBtnHtml + '</div>' +
                '</div>';
        }

        // 3. 计算气泡智能位置（带防屏幕溢出安全钳位）
        _positionTooltip(rect, step.placement, pad);
    }
    window._updateSpotlightAndTooltip = _updateSpotlightAndTooltip;

    function _positionTooltip(targetRect, placement, pad) {
        var cardW = Math.min(420, window.innerWidth - 32);
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
    window._positionTooltip = _positionTooltip;

})();
