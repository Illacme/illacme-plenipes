/**
 * 🏛️ [V75.2] Illacme Plenipes UI Custom Tooltip Component
 * 职责：全局自愈性高保真 Glassmorphism Tooltip 悬浮框组件 (单例安全、瞬时响应、点击自愈)。
 */

window.dismissCustomTooltip = (suppressMs = 0) => {
    if (suppressMs > 0) {
        window._suppressTooltipUntil = Date.now() + suppressMs;
    }
    document.querySelectorAll('.custom-glass-tooltip').forEach(el => el.remove());
    document.querySelectorAll('[data-title-converted]').forEach(target => {
        const text = target.getAttribute('title') || target.getAttribute('data-tooltip');
        if (text) target.setAttribute('title', text);
        target.removeAttribute('data-tooltip');
        target.removeAttribute('data-title-converted');
    });
};

window.initializeCustomTooltip = () => {
    let tooltipEl = null;

    // 动态注入奢华毛玻璃气泡样式
    if (!document.getElementById('custom-tooltip-styles')) {
        const style = document.createElement('style');
        style.id = 'custom-tooltip-styles';
        style.innerHTML = `
            .custom-glass-tooltip {
                position: absolute;
                z-index: 999999;
                padding: 6px 12px;
                font-size: 0.75rem;
                font-family: inherit;
                font-weight: 500;
                color: var(--text-bright);
                background: rgba(var(--bg-modal-solid-rgb), 0.92);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid var(--glass-border);
                border-radius: 6px;
                box-shadow: 0 4px 15px var(--black-50);
                pointer-events: none;
                opacity: 0;
                transform: translateY(2px);
                transition: opacity 0.12s cubic-bezier(0.4, 0, 0.2, 1), transform 0.12s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .custom-glass-tooltip.visible {
                opacity: 1;
                transform: translateY(0);
            }
        `;
        document.head.appendChild(style);
    }

    document.body.addEventListener('mouseover', (e) => {
        if (Date.now() < (window._suppressTooltipUntil || 0)) return;
        const target = e.target.closest('[title]');
        if (!target) return;

        // 🛡️ 强制单例自愈：创建前先清除页面上任何可能残留的孤儿气泡
        window.dismissCustomTooltip();

        // 1. 获取并备份 title，消除浏览器默认气泡
        const text = target.getAttribute('title');
        if (!text || !text.trim()) return;
        target.setAttribute('data-tooltip', text);
        target.setAttribute('data-title-converted', 'true');
        target.removeAttribute('title');

        // 2. 创建高保真 Glassmorphism 悬浮层
        tooltipEl = document.createElement('div');
        tooltipEl.className = 'custom-glass-tooltip';
        tooltipEl.innerText = text;
        document.body.appendChild(tooltipEl);

        // 3. 动态测算坐标
        const rect = target.getBoundingClientRect();
        const tooltipRect = tooltipEl.getBoundingClientRect();

        let top = rect.top - tooltipRect.height - 8;
        let left = rect.left + (rect.width - tooltipRect.width) / 2;

        // 防溢出边界
        if (top < 8) top = rect.bottom + 8;
        if (left < 8) left = 8;
        if (left + tooltipRect.width > window.innerWidth - 8) {
            left = window.innerWidth - tooltipRect.width - 8;
        }

        tooltipEl.style.top = `${top + window.scrollY}px`;
        tooltipEl.style.left = `${left + window.scrollX}px`;

        requestAnimationFrame(() => {
            if (tooltipEl) tooltipEl.classList.add('visible');
        });
    });

    document.body.addEventListener('mouseout', (e) => {
        const target = e.target.closest('[data-title-converted]');
        if (target) {
            const currentTitle = target.getAttribute('title');
            const cachedText = target.getAttribute('data-tooltip');
            const text = currentTitle || cachedText;
            if (text) target.setAttribute('title', text);
            target.removeAttribute('data-tooltip');
            target.removeAttribute('data-title-converted');
        }

        if (tooltipEl) {
            tooltipEl.remove();
            tooltipEl = null;
        }
    });

    // 🛡️ [死穴自愈 1] 点击任何元素（捕获阶段）均立即销毁悬浮气泡，杜绝 DOM 切换后孤儿悬挂
    document.addEventListener('pointerdown', () => {
        window.dismissCustomTooltip();
        tooltipEl = null;
    }, true);

    // 🛡️ [死穴自愈 2] 局部或全局容器滚动时即时销毁气泡，防止视觉错位
    window.addEventListener('scroll', () => {
        if (tooltipEl) {
            tooltipEl.remove();
            tooltipEl = null;
        }
    }, true);
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initializeCustomTooltip);
} else {
    window.initializeCustomTooltip();
}
