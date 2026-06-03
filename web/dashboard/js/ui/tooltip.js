/**
 * 🏛️ [V75.2] Illacme Plenipes UI Custom Tooltip Component
 * 职责：全局自愈性高保真 Glassmorphism Tooltip 悬浮框组件 (瞬时响应)。
 */
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
                color: #ffffff;
                background: rgba(var(--bg-modal-solid-rgb), 0.92);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
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
        const target = e.target.closest('[title]');
        if (!target) return;

        // 1. 获取并备份 title，消除浏览器默认气泡
        const text = target.getAttribute('title');
        if (!text || !text.trim()) return;
        target.setAttribute('data-tooltip', text);
        target.removeAttribute('title');

        // 2. 创建高保真 Glassmorphism 悬浮层
        tooltipEl = document.createElement('div');
        tooltipEl.className = 'custom-glass-tooltip';
        tooltipEl.innerText = text;
        document.body.appendChild(tooltipEl);

        // 3. 动态测算坐标
        const rect = target.getBoundingClientRect();
        const tooltipRect = tooltipEl.getBoundingClientRect();
        
        // 计算居中 Top 定位
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
        
        // 瞬间淡入
        requestAnimationFrame(() => {
            if (tooltipEl) tooltipEl.classList.add('visible');
        });
    });

    document.body.addEventListener('mouseout', (e) => {
        const target = e.target.closest('[data-tooltip]');
        if (!target) return;

        // 归还 title
        const text = target.getAttribute('data-tooltip');
        if (text) {
            target.setAttribute('title', text);
            target.removeAttribute('data-tooltip');
        }

        // 销毁悬浮层
        if (tooltipEl) {
            tooltipEl.remove();
            tooltipEl = null;
        }
    });
};

// 自动在 DOMContentLoaded 或立即注册
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initializeCustomTooltip);
} else {
    window.initializeCustomTooltip();
}
