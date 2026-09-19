/**
 * 🌌 [V130.0] Illacme Plenipes - 3D Brand Title Flap Controller
 * 职责：左上角品牌三位一体（品牌代号 -> 主产品定位 -> 出版发行工作台）3D 机械翻牌轮播控制器
 * 遵循微交互准则：4.5s 优雅步频，鼠标悬停暂停，点击快速切牌，页面隐藏自动挂起，双主题自适应
 */

(function () {
    'use strict';

    var FLIP_INTERVAL_MS = 4500; // 4.5秒从容驻留周期
    var timerId = null;
    var currentIndex = 0;
    var isPaused = false;

    function getItems() {
        var container = document.getElementById('brand-title-flip');
        if (!container) return [];
        return Array.prototype.slice.call(container.querySelectorAll('.flip-text-item'));
    }

    function updateContainerWidth(targetItem) {
        var container = document.getElementById('brand-title-flip');
        if (!container) return;
        var item = targetItem || container.querySelector('.flip-text-item.active') || getItems()[0];
        if (item) {
            var w = item.scrollWidth || item.offsetWidth;
            if (w > 0) {
                container.style.width = w + 'px';
            }
        }
    }

    /**
     * 执行单次翻牌过渡
     * @param {boolean} isManual 是否为用户手动触发
     */
    window.rotateBrandTitle = function (isManual) {
        var items = getItems();
        if (items.length <= 1) return;

        var prevItem = items[currentIndex];
        currentIndex = (currentIndex + 1) % items.length;
        var nextItem = items[currentIndex];

        // 1. 当前卡片：启动向上翻转退场
        prevItem.classList.remove('active');
        prevItem.classList.add('exit');

        // 2. 下一张卡片：从下方翻转入场并激活，同时平滑同步容器宽度
        nextItem.classList.remove('exit');
        nextItem.classList.add('active');
        updateContainerWidth(nextItem);

        // 3. 650ms 动画结束后清理旧卡片的 exit 类，回归隐藏待命态
        setTimeout(function () {
            if (prevItem && !prevItem.classList.contains('active')) {
                prevItem.classList.remove('exit');
            }
        }, 700);

        // 若为手动点击，重置轮播计时器
        if (isManual && !isPaused) {
            resetTimer();
        }
    };

    function startTimer() {
        if (timerId) clearInterval(timerId);
        timerId = setInterval(function () {
            if (!isPaused && !document.hidden) {
                window.rotateBrandTitle(false);
            }
        }, FLIP_INTERVAL_MS);
    }

    function stopTimer() {
        if (timerId) {
            clearInterval(timerId);
            timerId = null;
        }
    }

    function resetTimer() {
        stopTimer();
        startTimer();
    }

    function initBrandFlip() {
        var flipContainer = document.getElementById('brand-title-flip');
        var logoSection = document.querySelector('.logo-section');
        if (!flipContainer) return;

        // 1. 确保第 0 项激活
        var items = getItems();
        items.forEach(function (el, idx) {
            if (idx === 0) {
                el.classList.add('active');
                el.classList.remove('exit');
            } else {
                el.classList.remove('active', 'exit');
            }
        });
        updateContainerWidth(items[0]);

        // 2. 悬停与离开事件：悬停暂停，离开继续
        var targetHoverArea = logoSection || flipContainer;
        targetHoverArea.addEventListener('mouseenter', function () {
            isPaused = true;
        });

        targetHoverArea.addEventListener('mouseleave', function () {
            isPaused = false;
        });

        // 3. 页面可见性挂起（节约后台资源）
        document.addEventListener('visibilitychange', function () {
            if (document.hidden) {
                stopTimer();
            } else {
                startTimer();
            }
        });

        // 4. 启动自动轮播
        startTimer();
    }

    // 页面就绪时自动装载
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBrandFlip);
    } else {
        initBrandFlip();
    }
})();
