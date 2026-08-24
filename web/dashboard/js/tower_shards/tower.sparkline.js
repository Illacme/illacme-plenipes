/**
 * 🗼 [V1.1] 控制塔时序趋势图与探针引擎 (Tower Sparkline & Probes)
 * 职责：
 * 1. 动态自适应 Sparkline 折线与面积 SVG 路径计算；
 * 2. 格式化运行时间与 X/Y 轴刻度文本动态同步；
 * 3. 鼠标悬停数值探针与 Legend 图例联动。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
 */

(function () {
    // 动态自适应 Sparkline 渲染函数
    window.generateAdaptiveSvgPaths = function (history, maxVal = null) {
        if (!history || history.length === 0) return { line: '', area: '' };
        const computedMax = maxVal || Math.max(10, Math.max(...history) * 1.2);

        const points = history.map((val, i) => {
            const x = history.length > 1 ? (i / (history.length - 1)) * 500 : 250;
            const y = 115 - (val / computedMax) * 110;
            return { x, y };
        });

        const linePath = 'M ' + points.map(p => `${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' L ');
        const areaPath = `${linePath} L ${points[points.length - 1].x.toFixed(1)} 120 L ${points[0].x.toFixed(1)} 120 Z`;
        return { line: linePath, area: areaPath };
    };

    // 格式化运行时间
    window.formatUptime = function (seconds) {
        if (typeof seconds !== 'number' || isNaN(seconds)) return '--';
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hrs}h ${mins}m ${secs}s`;
    };

    // 生成 SVG 折线与面积路径
    window.generateSvgPaths = function (history) {
        if (!history || history.length === 0) return { line: '', area: '' };
        const points = history.map((val, i) => {
            const x = history.length > 1 ? (i / (history.length - 1)) * 500 : 250;
            const y = 115 - (val / 100) * 110; // 留出上下各 5px 的安全间距，y轴反转
            return { x, y };
        });

        const linePath = 'M ' + points.map(p => `${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' L ');
        const areaPath = `${linePath} L ${points[points.length - 1].x.toFixed(1)} 120 L ${points[0].x.toFixed(1)} 120 Z`;
        return { line: linePath, area: areaPath };
    };

    // 🚀 [V75.6] 切换时间轴趋势范围切换器，实现负载与 AI 的同步联动
    window.switchTrendRange = function (range) {
        window.currentTrendRange = range;

        // 立即触发一次渲染刷新，提高交互响应敏捷度
        if (typeof window.refreshTowerTelemetry === 'function') {
            window.refreshTowerTelemetry();
        }
    };

    // 🛰️ [V75.6] 同步更新趋势图的 X 轴刻度文本
    window.updateTrendTicks = function (svgId, currentRange) {
        const svg = document.getElementById(svgId);
        if (!svg) return;
        const t0 = svg.querySelector('.trend-tick-0');
        const t1 = svg.querySelector('.trend-tick-1');
        const t2 = svg.querySelector('.trend-tick-2');
        const t3 = svg.querySelector('.trend-tick-3');
        const t4 = svg.querySelector('.trend-tick-4');

        if (currentRange === '80s') {
            if (t0) t0.textContent = '-80s';
            if (t1) t1.textContent = '-60s';
            if (t2) t2.textContent = '-40s';
            if (t3) t3.textContent = '-20s';
            if (t4) t4.textContent = '现在 (0s)';
        } else if (currentRange === '180s') {
            if (t0) t0.textContent = '-180s';
            if (t1) t1.textContent = '-135s';
            if (t2) t2.textContent = '-90s';
            if (t3) t3.textContent = '-45s';
            if (t4) t4.textContent = '现在 (0s)';
        } else if (currentRange === '300s') {
            if (t0) t0.textContent = '-300s';
            if (t1) t1.textContent = '-225s';
            if (t2) t2.textContent = '-150s';
            if (t3) t3.textContent = '-75s';
            if (t4) t4.textContent = '现在 (0s)';
        } else if (currentRange === '12h') {
            if (t0) t0.textContent = '-12h';
            if (t1) t1.textContent = '-9h';
            if (t2) t2.textContent = '-6h';
            if (t3) t3.textContent = '-3h';
            if (t4) t4.textContent = '现在 (0s)';
        }
    };

    // 🚀 [V75.7] 设置 SVG 折线图鼠标悬停数值探针与 Legend 图例回填
    window.setupTrendHoverProbes = function () {
        const bindEvents = (svgId, legendId, probeLineId, isAi = false) => {
            const svg = document.getElementById(svgId);
            if (!svg || svg._hasProbeEvent) return;
            svg._hasProbeEvent = true;

            const legend = document.getElementById(legendId);
            const probeLine = document.getElementById(probeLineId);

            const handleMove = (e) => {
                const data = svg._currentData;
                if (!data) return;

                const rect = svg.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const pctX = Math.min(1.0, Math.max(0.0, mouseX / rect.width));

                const limit = data.limit || 40;
                const range = data.range || '80s';
                const idx = Math.min(limit - 1, Math.max(0, Math.round(pctX * (limit - 1))));

                // 计算磁吸对应的 X 轴坐标 (0-500 SVG视口宽度)
                const snapX = (idx / (limit - 1)) * 500;

                if (probeLine) {
                    probeLine.setAttribute('x1', snapX);
                    probeLine.setAttribute('x2', snapX);
                    probeLine.style.display = 'block';
                }

                // 格式化时间偏差文本
                const formatTimeOffset = (idx, limit, range) => {
                    const offsetTicks = limit - 1 - idx;
                    if (range === '12h') {
                        const minutes = offsetTicks * 2;
                        if (minutes === 0) return '现在';
                        if (minutes >= 60) {
                            const h = Math.floor(minutes / 60);
                            const m = minutes % 60;
                            return `-${h}h${m > 0 ? m + 'm' : ''}`;
                        }
                        return `-${minutes}m`;
                    } else {
                        const seconds = offsetTicks * 2;
                        if (seconds === 0) return '现在';
                        return `-${seconds}s`;
                    }
                };
                const timeStr = formatTimeOffset(idx, limit, range);

                if (legend) {
                    if (isAi) {
                        const tokens = (data.tokens_rate || [])[idx] || 0.0;
                        const threads = (data.active_workers || [])[idx] || 0;
                        legend.innerHTML = `
                            <span style="color: var(--accent-secondary);">● 吞吐: ${tokens.toFixed(1)} t/s</span>
                            <span style="color: var(--accent-orange, #ff9d00);">● 线程: ${threads}</span>
                            <span style="color: var(--text-dim); margin-left: 5px;">(${timeStr})</span>
                        `;
                    } else {
                        const cpu = (data.cpu || [])[idx] || 0.0;
                        const mem = (data.memory || [])[idx] || 0.0;
                        const comp = (data.compute_memory || [])[idx] || 0.0;
                        legend.innerHTML = `
                            <span style="color: var(--accent-primary);">● CPU: ${cpu.toFixed(1)}%</span>
                            <span style="color: var(--accent-secondary);">● MEM: ${mem.toFixed(1)}%</span>
                            <span style="color: var(--accent-orange, #ff9d00);">● COMPUTE: ${comp.toFixed(1)}%</span>
                            <span style="color: var(--text-dim); margin-left: 5px;">(${timeStr})</span>
                        `;
                    }
                }
            };

            const handleLeave = () => {
                if (probeLine) probeLine.style.display = 'none';
                if (legend) {
                    if (isAi) {
                        legend.innerHTML = `
                            <span style="color: var(--accent-secondary);">● 吞吐速率 (Tokens/s)</span>
                            <span style="color: var(--accent-orange, #ff9d00);">● 活动工作线程 (Active Threads)</span>
                        `;
                    } else {
                        legend.innerHTML = `
                            <span style="color: var(--accent-primary);">● CPU</span>
                            <span style="color: var(--accent-secondary);">● MEM</span>
                            <span style="color: var(--accent-orange, #ff9d00);">● COMPUTE</span>
                        `;
                    }
                }
            };

            svg.addEventListener('mousemove', handleMove);
            svg.addEventListener('mouseleave', handleLeave);
        };

        bindEvents('tower-trend-svg', 'trend-legend-val', 'trend-probe-line', false);
        bindEvents('tower-ai-trend-svg', 'trend-ai-legend-val', 'trend-ai-probe-line', true);
    };
})();
