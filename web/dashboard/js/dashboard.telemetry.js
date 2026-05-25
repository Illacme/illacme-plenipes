/**
 * 🚀 Illacme Plenipes Dashboard Telemetry & Networks
 * 职责：系统脉冲动效触发、遥测雷达闪烁，以及页脚实时性能指标轮询渲染。
 */

// 1. 系统就绪物理脉冲 (反馈反馈)
window.triggerSystemPulse = () => {
    document.body.classList.remove('system-pulse');
    void document.body.offsetWidth; // Trigger reflow
    document.body.classList.add('system-pulse');
    setTimeout(() => document.body.classList.remove('system-pulse'), 500);
};

// 2. 📡 [V65.0] Telemetry Dynamics Loop (雷达与心跳指示器)
window.initTelemetryDynamics = () => {
    setInterval(() => {
        // Random Signal Flicker
        const signalBars = document.querySelectorAll('.signal-bar');
        if (signalBars.length > 0) {
            const lastBar = signalBars[signalBars.length - 1];
            if (Math.random() > 0.8) {
                lastBar.classList.toggle('active');
            }
        }
    }, 1000);
};

// 3. 🚀 [V74.10] 全局遥测脉冲：物理数据推送至底部状态栏 (footer-center)
window.initGlobalTelemetryPulse = () => {
    setInterval(async () => {
        try {
            if (typeof apiFetch !== 'function') return;
            const stats = await apiFetch('/api/system/stats');
            if (!stats) return;

            // 1. 同步底部状态栏 CPU LOAD & MEMORY
            const cpuEl = document.getElementById('footer-cpu-val');
            const memEl = document.getElementById('footer-mem-val');
            if (cpuEl && stats.load) cpuEl.innerText = stats.load.cpu + '%';
            if (memEl && stats.load) memEl.innerText = stats.load.memory + '%';

            // 2. 同步 AI CREDIT & TOKENS
            const costEl = document.getElementById('footer-ai-cost');
            const tokensEl = document.getElementById('footer-ai-tokens');
            if (stats.usage) {
                if (costEl) costEl.innerText = '$' + (stats.usage.cost || 0).toFixed(4);
                if (tokensEl) tokensEl.innerText = (stats.usage.input_tokens + stats.usage.output_tokens).toLocaleString();
            }

            // 3. 如果当前在 Overview 视图，同步总编室指标
            const globalCost = document.getElementById('global-cost-display');
            if (globalCost && stats.usage) {
                globalCost.innerText = '$' + (stats.usage.cost || 0).toFixed(4);
            }
        } catch (e) {
            console.warn("Global telemetry pulse dropped:", e);
        }
    }, 3000);
};
