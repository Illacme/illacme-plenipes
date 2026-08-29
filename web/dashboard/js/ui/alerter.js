/**
 * 🛡️ [V75.9] Reactive Security Alerter (动态实时警报器)
 * 职责：负责拦截 WS 的安全警示信号，并在仪表盘右上角动态绘制高级玻璃拟态的红色呼吸警报条。
 */
(function() {
    let container = document.getElementById('active-security-alerter-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'active-security-alerter-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 12px;
            width: 380px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    // 注入滑入滑出动画 CSS
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        @keyframes slideInAlert {
            from { transform: translateX(120%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutAlert {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(120%); opacity: 0; }
        }
        @keyframes pulseRed {
            0% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); }
            70% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 0 6px rgba(255, 59, 48, 0); }
            100% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); }
        }
        .active-alert-card {
            pointer-events: auto;
            background: rgba(255, 59, 48, 0.12);
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid rgba(255, 59, 48, 0.3);
            border-left: 4px solid #ff3b30;
            border-radius: 12px;
            padding: 16px;
            color: var(--text-bright, #fff);
            box-shadow: 0 10px 30px rgba(255, 59, 48, 0.15), inset 0 1px 0 rgba(255,255,255,0.1);
            display: flex;
            flex-direction: column;
            gap: 8px;
            animation: slideInAlert 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            position: relative;
            transition: all 0.3s;
        }
        .active-alert-card.removing {
            animation: slideOutAlert 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .active-alert-card.success-restore {
            background: rgba(52, 199, 89, 0.12);
            border-color: rgba(52, 199, 89, 0.3);
            border-left-color: #34c759;
            box-shadow: 0 10px 30px rgba(52, 199, 89, 0.15);
        }
        .active-alert-card h5 {
            margin: 0;
            font-size: 0.9rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .active-alert-card p {
            margin: 0;
            font-size: 0.8rem;
            line-height: 1.5;
            color: rgba(255,255,255,0.85);
        }
    `;
    document.head.appendChild(styleEl);

    window.triggerDynamicAlert = (type, title, message, duration = 0) => {
        const id = `alert-card-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
        
        // 查找是否已有相同的持续性警报正在显示（防止重复堆叠）
        if (type === 'throttle') {
            const existing = document.getElementById('active-throttle-alert');
            if (existing) {
                existing.querySelector('p').innerHTML = message;
                return;
            }
        }

        const card = document.createElement('div');
        card.className = 'active-alert-card';
        if (type === 'throttle') {
            card.id = 'active-throttle-alert';
        } else {
            card.id = id;
        }

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; width: 100%;">
                <h5 style="color: ${type === 'restore' ? '#34c759' : '#ff4d4d'};">
                    ${type === 'restore' ? '🟢' : '🚨'} ${title}
                </h5>
                <button onclick="window.dismissDynamicAlert(this.closest('.active-alert-card'))" style="background: none; border: none; color: rgba(255,255,255,0.4); cursor: pointer; font-size: 1.1rem; line-height: 1; padding: 0 4px; transition: color 0.2s; outline: none;">&times;</button>
            </div>
            <p>${message}</p>
        `;

        if (type === 'restore') {
            card.classList.add('success-restore');
        }

        container.appendChild(card);

        // 如果是临时警告，则设置延时消失
        if (duration > 0) {
            setTimeout(() => {
                window.dismissDynamicAlert(card);
            }, duration);
        }
    };

    window.dismissDynamicAlert = (cardEl) => {
        if (!cardEl) return;
        cardEl.classList.add('removing');
        cardEl.addEventListener('animationend', () => {
            cardEl.remove();
        });
    };

    window.clearThrottleAlert = () => {
        const existing = document.getElementById('active-throttle-alert');
        if (existing) {
            window.dismissDynamicAlert(existing);
            return true;
        }
        return false;
    };
})();
