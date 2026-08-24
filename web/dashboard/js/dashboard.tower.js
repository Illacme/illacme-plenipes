/**
 * 🗼 [V1.1] 控制塔数据调度器 - 总编室控制塔可视化面板 (Hub 调度中枢)
 * 职责：
 * 1. 控制塔生命周期管理与自适应动态调频（活跃 2s / 空闲 10s）；
 * 2. 刷新第一行系统状态指标与多线程池队列占比；
 * 3. 驱动圆环仪表盘 (Gauge) 与 Sparkline 走势图数据装载。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
 */

(function () {
    window.towerTimeoutId = null;
    window.currentTrendRange = '80s'; // 默认 80 秒历史

    // 刷新控制塔数据
    window.refreshTowerTelemetry = async function () {
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
            if (uptimeEl && typeof window.formatUptime === 'function') {
                uptimeEl.innerText = window.formatUptime(stats.uptime);
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

                // 绘制 SVG 趋势图（根据当前维度进行时序切片）
                const range = window.currentTrendRange || '80s';
                const isArchive = range === '12h';
                const dataSource = isArchive ? (stats.history_archive || {}) : (stats.history || {});

                if (dataSource && typeof window.generateAdaptiveSvgPaths === 'function') {
                    const rangePoints = { '80s': 40, '180s': 90, '300s': 150, '12h': 360 };
                    const limit = rangePoints[range] || 40;

                    const sliceHistory = (arr) => {
                        if (!arr) return [];
                        return arr.slice(-limit);
                    };

                    const cpuPaths = window.generateAdaptiveSvgPaths(sliceHistory(dataSource.cpu), 100);
                    const memPaths = window.generateAdaptiveSvgPaths(sliceHistory(dataSource.memory), 100);
                    const compPaths = window.generateAdaptiveSvgPaths(sliceHistory(dataSource.compute_memory), 100);

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

                    // 绘制 AI 大模型专属时序遥测 Sparkline
                    const tokensPaths = window.generateAdaptiveSvgPaths(sliceHistory(dataSource.tokens_rate));
                    const threadsPaths = window.generateAdaptiveSvgPaths(sliceHistory(dataSource.active_workers));

                    const tokensLineEl = document.getElementById('trend-tokens-line');
                    const tokensAreaEl = document.getElementById('trend-tokens-area');
                    if (tokensLineEl) tokensLineEl.setAttribute('d', tokensPaths.line);
                    if (tokensAreaEl) tokensAreaEl.setAttribute('d', tokensPaths.area);

                    const threadsLineEl = document.getElementById('trend-threads-line');
                    const threadsAreaEl = document.getElementById('trend-threads-area');
                    if (threadsLineEl) threadsLineEl.setAttribute('d', threadsPaths.line);
                    if (threadsAreaEl) threadsAreaEl.setAttribute('d', threadsPaths.area);

                    // 🚀 [V75.7] 缓存绘图切片数据至 DOM 属性中，以供给 Hover 探针免 DOM 悬停抓取
                    const svgEl = document.getElementById('tower-trend-svg');
                    if (svgEl) {
                        svgEl._currentData = {
                            cpu: sliceHistory(dataSource.cpu),
                            memory: sliceHistory(dataSource.memory),
                            compute_memory: sliceHistory(dataSource.compute_memory),
                            limit: limit,
                            range: range
                        };
                    }
                    const aiSvgEl = document.getElementById('tower-ai-trend-svg');
                    if (aiSvgEl) {
                        aiSvgEl._currentData = {
                            tokens_rate: sliceHistory(dataSource.tokens_rate),
                            active_workers: sliceHistory(dataSource.active_workers),
                            limit: limit,
                            range: range
                        };
                    }

                    // 🚀 [V75.7] 动态重绘 AI 趋势图 Y 轴量纲刻度文本
                    const maxTokens = Math.max(...sliceHistory(dataSource.tokens_rate), 10.0);
                    const aiTicksEl = document.getElementById('trend-ai-y-ticks');
                    if (aiTicksEl) {
                        aiTicksEl.innerHTML = `
                            <text x="5" y="12" text-anchor="start">${Math.ceil(maxTokens)} t/s</text>
                            <text x="5" y="64" text-anchor="start">${Math.ceil(maxTokens / 2)} t/s</text>
                            <text x="5" y="116" text-anchor="start">0 t/s</text>
                        `;
                    }

                    // 🚀 [V75.7] 触发 Hover 探针绑定
                    if (window.setupTrendHoverProbes) {
                        window.setupTrendHoverProbes();
                    }

                    // 🛰️ [V75.6] 同步更新两个趋势图的 X 轴刻度文本
                    if (typeof window.updateTrendTicks === 'function') {
                        window.updateTrendTicks('tower-trend-svg', range);
                        window.updateTrendTicks('tower-ai-trend-svg', range);
                    }

                    // 🛰️ [V75.6] 每次刷新时自动对 Tab 按钮的样式进行一次同步
                    const loadTabs = ['80s', '180s', '300s', '12h'];
                    loadTabs.forEach(r => {
                        const btnLoad = document.getElementById(`btn-trend-${r}`);
                        if (btnLoad) {
                            if (r === range) {
                                btnLoad.classList.add('active');
                                btnLoad.style.background = 'var(--accent-primary)';
                                btnLoad.style.color = 'var(--text-bright, #fff)';
                            } else {
                                btnLoad.classList.remove('active');
                                btnLoad.style.background = 'transparent';
                                btnLoad.style.color = 'var(--text-dim)';
                            }
                        }

                        const btnAI = document.getElementById(`btn-ai-trend-${r}`);
                        if (btnAI) {
                            if (r === range) {
                                btnAI.classList.add('active');
                                btnAI.style.background = 'var(--accent-primary)';
                                btnAI.style.color = 'var(--text-bright, #fff)';
                            } else {
                                btnAI.classList.remove('active');
                                btnAI.style.background = 'transparent';
                                btnAI.style.color = 'var(--text-dim)';
                            }
                        }
                    });
                }
            }

            // 4. 自适应决策轮询周期：有活动同步或线程池繁忙时提频为 2 秒，否则空闲为 10 秒
            if (hasActiveSync || hasPoolActivity) {
                nextInterval = 2000;
            }

            // 5. 顺带刷新分发死信队列
            if (typeof window.refreshSyndicationQueue === 'function') {
                await window.refreshSyndicationQueue();
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
    window.loadTowerCenter = function () {
        // 重置定时器并立即拉取
        if (window.towerTimeoutId) {
            clearTimeout(window.towerTimeoutId);
            window.towerTimeoutId = null;
        }
        window.refreshTowerTelemetry();
        if (typeof window.refreshSyndicationQueue === 'function') {
            window.refreshSyndicationQueue();
        }
    };
})();
