/**
 * 🗼 [V1.1] 控制塔数据调度器 - 总编室控制塔可视化面板
 * 职责：支持自适应动态调频（活跃状态 2s / 空闲状态 10s），并绘制 CPU/内存 15点历史负载走势 SVG Sparkline。
 */

(function() {
    window.towerTimeoutId = null;
    let cpuHistory = [];
    let memHistory = [];
    let computeHistory = [];
    const MAX_HISTORY_POINTS = 15;

    // 格式化运行时间
    function formatUptime(seconds) {
        if (typeof seconds !== 'number' || isNaN(seconds)) return '--';
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hrs}h ${mins}m ${secs}s`;
    }

    // 生成 SVG 折线与面积路径
    function generateSvgPaths(history) {
        if (history.length === 0) return { line: '', area: '' };
        const points = history.map((val, i) => {
            const x = history.length > 1 ? (i / (history.length - 1)) * 500 : 250;
            const y = 115 - (val / 100) * 110; // 留出上下各 5px 的安全间距，y轴反转
            return { x, y };
        });

        const linePath = 'M ' + points.map(p => `${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' L ');
        const areaPath = `${linePath} L ${points[points.length - 1].x.toFixed(1)} 120 L ${points[0].x.toFixed(1)} 120 Z`;
        return { line: linePath, area: areaPath };
    }

    // 刷新控制塔数据
    window.refreshTowerTelemetry = async () => {
        const el = document.getElementById('view-tower');
        // 生命节点防御性检查
        if (!el || el.style.display === 'none' || window.location.hash !== '#/tower') {
            if (window.towerTimeoutId) {
                clearTimeout(window.towerTimeoutId);
                window.towerTimeoutId = null;
            }
            return;
        }

        let nextInterval = 10000; // 默认空闲轮询频率：10 秒

        try {
            if (typeof apiFetch !== 'function') return;
            const stats = await apiFetch('/api/governance/pulse');
            if (!stats) return;

            // 1. 刷新第一行状态卡片
            const statusEl = document.getElementById('tower-status');
            if (statusEl) {
                const status = stats.status || 'UNKNOWN';
                if (status === 'RUNNING') {
                    statusEl.innerHTML = `<span style="color: var(--neon-green); text-shadow: 0 0 10px rgba(var(--neon-green-rgb), 0.5);">● RUNNING</span>`;
                } else {
                    statusEl.innerHTML = `<span style="color: var(--text-dim);">${status}</span>`;
                }
            }

            const uptimeEl = document.getElementById('tower-uptime');
            if (uptimeEl) {
                uptimeEl.innerText = formatUptime(stats.uptime);
            }

            // 出版进度指标检测
            let hasActiveSync = false;
            const progressEl = document.getElementById('tower-progress');
            if (progressEl && stats.progress) {
                const current = stats.progress.current || 0;
                const total = stats.progress.total || 0;
                const pct = stats.progress.percentage || 0;
                if (total === 0) {
                    progressEl.innerHTML = `100% <span style="font-size:0.8rem; color:var(--text-dim);">(已对准)</span>`;
                } else {
                    progressEl.innerHTML = `${pct}% <span style="font-size:0.8rem; color:var(--text-dim);">(${current}/${total})</span>`;
                    if (current < total) {
                        hasActiveSync = true; // 存在未完成的出版任务
                    }
                }
            }

            const costEl = document.getElementById('tower-cost');
            if (costEl && stats.usage) {
                const cost = stats.usage.cost || 0;
                const tokens = stats.usage.tokens || 0;
                costEl.innerHTML = `$${cost.toFixed(4)} <span style="font-size:0.8rem; color:var(--text-dim);">(${tokens.toLocaleString()} tkn)</span>`;
            }

            // 2. 刷新线程池监控，并检测是否有活动队列任务
            let hasPoolActivity = false;
            if (stats.pools) {
                const poolsConfig = [
                    { id: 'pool-global', data: stats.pools.global || {} },
                    { id: 'pool-ai', data: stats.pools.ai || {} },
                    { id: 'pool-asset', data: stats.pools.asset || {} }
                ];

                poolsConfig.forEach(pool => {
                    const active = pool.data.active_workers || 0;
                    const max = pool.data.max_workers || 1;
                    const queue = pool.data.queue_size || 0;
                    const pct = Math.min(100, Math.round((active / max) * 100));

                    const textEl = document.getElementById(`${pool.id}-text`);
                    const barEl = document.getElementById(`${pool.id}-bar`);
                    if (textEl) textEl.innerText = `${active} / ${max} (队列: ${queue})`;
                    if (barEl) barEl.style.width = `${pct}%`;

                    if (active > 0 || queue > 0) {
                        hasPoolActivity = true; // 线程池有活动任务
                    }
                });
            }

            // 3. 刷新物理服务器负载仪表盘，并记录历史走势
            if (stats.load) {
                const cpuPct = stats.load.cpu_percent || 0;
                const memPct = stats.load.memory_percent || 0;
                const compPct = stats.load.compute_memory_percent || 0;

                // 压入历史数据
                cpuHistory.push(cpuPct);
                memHistory.push(memPct);
                computeHistory.push(compPct);
                if (cpuHistory.length > MAX_HISTORY_POINTS) {
                    cpuHistory.shift();
                    memHistory.shift();
                    computeHistory.shift();
                }

                // 更新圆环仪表盘
                const cpuText = document.getElementById('gauge-cpu');
                const cpuRing = document.getElementById('gauge-cpu-ring');
                if (cpuText) cpuText.innerText = `${cpuPct.toFixed(1)}%`;
                if (cpuRing) {
                    const offset = 263.89 - (cpuPct / 100) * 263.89;
                    cpuRing.style.strokeDashoffset = offset;
                }

                const memText = document.getElementById('gauge-mem');
                const memRing = document.getElementById('gauge-mem-ring');
                if (memText) memText.innerText = `${memPct.toFixed(1)}%`;
                if (memRing) {
                    const offset = 263.89 - (memPct / 100) * 263.89;
                    memRing.style.strokeDashoffset = offset;
                }

                const compText = document.getElementById('gauge-compute');
                const compRing = document.getElementById('gauge-compute-ring');
                if (compText) compText.innerText = `${compPct.toFixed(1)}%`;
                if (compRing) {
                    const offset = 263.89 - (compPct / 100) * 263.89;
                    compRing.style.strokeDashoffset = offset;
                }

                // 绘制 SVG 趋势图
                const cpuPaths = generateSvgPaths(cpuHistory);
                const memPaths = generateSvgPaths(memHistory);
                const compPaths = generateSvgPaths(computeHistory);

                const cpuLineEl = document.getElementById('trend-cpu-line');
                const cpuAreaEl = document.getElementById('trend-cpu-area');
                if (cpuLineEl) cpuLineEl.setAttribute('d', cpuPaths.line);
                if (cpuAreaEl) cpuAreaEl.setAttribute('d', cpuPaths.area);

                const memLineEl = document.getElementById('trend-mem-line');
                const memAreaEl = document.getElementById('trend-mem-area');
                if (memLineEl) memLineEl.setAttribute('d', memPaths.line);
                if (memAreaEl) memAreaEl.setAttribute('d', memPaths.area);

                const compLineEl = document.getElementById('trend-compute-line');
                const compAreaEl = document.getElementById('trend-compute-area');
                if (compLineEl) compLineEl.setAttribute('d', compPaths.line);
                if (compAreaEl) compAreaEl.setAttribute('d', compPaths.area);
            }

            // 4. 自适应决策轮询周期：有活动同步或线程池繁忙时提频为 2 秒，否则空闲为 10 秒
            if (hasActiveSync || hasPoolActivity) {
                nextInterval = 2000;
            }

        } catch (error) {
            console.error("🗼 [Tower] 遥测数据拉取失败:", error);
        }

        // 递归调度下一次轮询，保证线程间不冲突且轮询独立
        if (window.towerTimeoutId) {
            clearTimeout(window.towerTimeoutId);
        }
        window.towerTimeoutId = setTimeout(window.refreshTowerTelemetry, nextInterval);
    };

    // 初始化控制塔
    window.loadTowerCenter = () => {
        // 重置走势数据，防止上一次的观测点被继承
        cpuHistory = [];
        memHistory = [];
        computeHistory = [];

        // 重置定时器并立即拉取
        if (window.towerTimeoutId) {
            clearTimeout(window.towerTimeoutId);
            window.towerTimeoutId = null;
        }
        window.refreshTowerTelemetry();
    };
})();
