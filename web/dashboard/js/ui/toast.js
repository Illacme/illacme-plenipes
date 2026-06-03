/**
 * 🍞 Breathing Toast Notification System
 * 职责：非侵入式“呼吸胶囊”微提示，直接集成至底部状态栏的审计雷达位。
 */

window.showBreathingToast = (message) => {
    // 1. 复用原生的审计中心记录机制，确保日志可追溯
    if (typeof window.addAudit === 'function') {
        window.addAudit(message, 'success');
    }

    // 2. 截获底部的简报文本，赋予临时的“呼吸胶囊”物理特效
    const summaryText = document.getElementById('audit-summary-text');
    if (summaryText) {
        // 重置动画状态
        summaryText.classList.remove('toast-breathe-active');
        void summaryText.offsetWidth; // 触发重绘
        
        summaryText.classList.add('toast-breathe-active');

        // 3秒后消散特效，回归普通的审计文本状态
        setTimeout(() => {
            summaryText.classList.remove('toast-breathe-active');
        }, 3000);
    }
};
