/**
 * 🎨 Illacme Compute Center - UI Warning Banner Shard (V74.24 GENOME RESTORED)
 * 子职责：[SOP-03] 算力雪崩熔断自愈警报 Banner 动态注入、动画、倒计时及优雅淡出管理
 * 还原声明：本文件内容 100% 提取自 83b7900 基准版本，严禁 AI 瞎创造。
 */

/**
 * 🚨 [Visual Sovereign Guard]
 * 监听实时 WebSocket 熔断事件，动态渲染硬件加速、带优雅倒计时的算力自愈警报 Banner
 */
window.handleAiBreakerTripped = function(payload) {
    const nodeName = payload.node_name || "Unknown-Node";
    const failureRate = payload.rate ? Math.round(payload.rate * 100) : 100;
    
    // 1. 检查是否已经存在该节点的熔断 Banner，避免重复拉起
    const existingBanner = document.getElementById(`breaker-banner-${nodeName}`);
    if (existingBanner) {
        // 如果存在，直接重置其冷却倒计时
        existingBanner.dataset.countdown = "30";
        const timerVal = existingBanner.querySelector(".countdown-timer-value");
        if (timerVal) timerVal.textContent = "30s";
        return;
    }

    // 2. 创建横幅容器
    const banner = document.createElement("div");
    banner.id = `breaker-banner-${nodeName}`;
    banner.className = "compute-warning-banner glass-panel";
    banner.dataset.countdown = "30";
    
    // 设置硬件加速的 CSS 样式
    Object.assign(banner.style, {
        position: "fixed",
        top: "90px",
        left: "50%",
        transform: "translateX(-50%) translateY(-30px)",
        width: "90%",
        maxWidth: "680px",
        background: "rgba(255, 69, 58, 0.12)",
        backdropFilter: "blur(20px)",
        webkitBackdropFilter: "blur(20px)",
        border: "1px solid rgba(255, 69, 58, 0.35)",
        borderRadius: "12px",
        boxShadow: "0 10px 40px rgba(255, 69, 58, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
        padding: "16px 20px",
        zIndex: "99999",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "16px",
        opacity: "0",
        transition: "opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1), transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        color: "#ffffff"
    });

    // 内部结构
    banner.innerHTML = `
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="font-size: 1.5rem; animation: pulse-warning 2s infinite ease-in-out;">⚠️</div>
            <div>
                <div style="font-weight: 700; font-size: 0.9rem; color: #ff453a; letter-spacing: 0.5px; margin-bottom: 2px;">
                    算力雪崩治理警报 (Circuit Breaker Tripped)
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.85); line-height: 1.4;">
                    节点 <span style="font-family: monospace; background: rgba(255,255,255,0.15); padding: 2px 6px; border-radius: 4px; color: #fff; font-weight: 600;">${nodeName}</span> (异常率: ${failureRate}%) 遭遇算力洪峰已被自动熔断隔离。<br>
                    系统已动态引流至健康的备用节点，正在排队自愈中...
                </div>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end; justify-content: center; min-width: 80px;">
            <div style="font-size: 0.6rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 1px;">自愈冷却</div>
            <div class="countdown-timer-value" style="font-size: 1.6rem; font-weight: 800; color: #ff9f0a; font-family: monospace;">30s</div>
        </div>
    `;

    // 插入动画关键帧（用于小警告图标呼吸）
    if (!document.getElementById("breaker-keyframes")) {
        const style = document.createElement("style");
        style.id = "breaker-keyframes";
        style.textContent = `
            @keyframes pulse-warning {
                0% { transform: scale(1); filter: drop-shadow(0 0 2px rgba(255,69,58,0)); }
                50% { transform: scale(1.1); filter: drop-shadow(0 0 8px rgba(255,69,58,0.7)); }
                100% { transform: scale(1); filter: drop-shadow(0 0 2px rgba(255,69,58,0)); }
            }
        `;
        document.head.appendChild(style);
    }

    // 3. 将横幅插入 DOM 树
    document.body.appendChild(banner);

    // 触发硬件加速的 CSS 进入过渡
    requestAnimationFrame(() => {
        banner.style.opacity = "1";
        banner.style.transform = "translateX(-50%) translateY(0)";
    });

    // 4. 定时倒计时与自愈移除机制
    const intervalId = setInterval(() => {
        let count = parseInt(banner.dataset.countdown) - 1;
        if (count <= 0) {
            clearInterval(intervalId);
            // 优雅淡出并从 DOM 中物理删除
            banner.style.opacity = "0";
            banner.style.transform = "translateX(-50%) translateY(-30px)";
            banner.addEventListener("transitionend", () => {
                banner.remove();
            }, { once: true });
        } else {
            banner.dataset.countdown = count.toString();
            const timerVal = banner.querySelector(".countdown-timer-value");
            if (timerVal) timerVal.textContent = `${count}s`;
        }
    }, 1000);
};
