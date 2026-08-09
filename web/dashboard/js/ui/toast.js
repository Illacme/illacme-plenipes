/**
 * 🍞 Illacme Plenipes - Global Toast Micro-interactions Queue
 * 职责：提供高质量毛玻璃 Toast 微通知，替代突兀的 Alert 弹窗。
 */

(function() {
    window.showToast = function(message, type = 'success', duration = 3200) {
        let container = document.getElementById('global-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'global-toast-container';
            container.style.cssText = `
                position: fixed;
                top: 24px;
                right: 24px;
                z-index: 99999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
                max-width: 380px;
            `;
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `glass-toast toast-${type}`;
        
        const typeConfig = {
            success: { icon: '✨', border: 'hsla(152, 100%, 50%, 0.4)', bg: 'rgba(10, 30, 20, 0.85)', color: '#00ff88' },
            info:    { icon: '📡', border: 'hsla(183, 100%, 50%, 0.4)', bg: 'rgba(10, 25, 35, 0.85)', color: 'var(--accent-secondary, #00f2ff)' },
            warning: { icon: '⚠️', border: 'hsla(43, 100%, 50%, 0.4)',  bg: 'rgba(35, 25, 10, 0.85)', color: '#ffb300' },
            error:   { icon: '🛑', border: 'hsla(0, 100%, 60%, 0.4)',   bg: 'rgba(35, 10, 10, 0.85)', color: '#ff5555' }
        };

        const cfg = typeConfig[type] || typeConfig.info;

        // 🛡️ 智能去重：若 message 自身已包含前置 Emoji，自动清洗，防止出现双图标 (如 ⚠️ ⚠️)
        let cleanMessage = String(message || '').trim();
        const leadingEmojiRegex = /^(\u26a0\ufe0f?|\ud83d\udeab|\ud83d\udea8|\u2728|\ud83d\udce1|\u2705|\u274c|\ud83d\uddd1\ufe0f?|\ud83d\udd17|\ud83e\uddf1|\ud83d\udee0\ufe0f?|\u26a0)\s*/;
        cleanMessage = cleanMessage.replace(leadingEmojiRegex, '');

        toast.style.cssText = `
            pointer-events: auto;
            background: ${cfg.bg};
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid ${cfg.border};
            border-radius: 8px;
            padding: 10px 16px;
            color: #ffffff;
            font-size: 0.82rem;
            line-height: 1.4;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0;
            transform: translateY(-12px) scale(0.96);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        `;

        toast.innerHTML = `
            <span style="font-size: 1.1rem; flex-shrink: 0;">${cfg.icon}</span>
            <div style="flex: 1; word-break: break-word;">${cleanMessage}</div>
        `;

        container.appendChild(toast);

        // 动画触发
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0) scale(1)';
        });

        // 自动出场
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px) scale(0.96)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    };
})();
