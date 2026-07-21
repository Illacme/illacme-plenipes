/**
 * 🗼 [V1.1] 控制塔数据调度器 - 总编室控制塔可视化面板
 * 职责：支持自适应动态调频（活跃状态 2s / 空闲状态 10s），并绘制 CPU/内存 15点历史负载走势 SVG Sparkline。
 */

(function() {
    window.towerTimeoutId = null;
    window.currentTrendRange = '80s'; // 默认 80 秒历史

    // 🚀 [V75.6] 切换时间轴趋势范围切换器，实现负载与 AI 的同步联动
    window.switchTrendRange = function(range) {
        window.currentTrendRange = range;
        
        // 立即触发一次渲染刷新，提高交互响应敏捷度
        if (typeof window.refreshTowerTelemetry === 'function') {
            window.refreshTowerTelemetry();
        }
    };

    // 🚀 [新增] 动态自适应 Sparkline 渲染函数
    function generateAdaptiveSvgPaths(history, maxVal = null) {
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
    }

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
                
                if (dataSource) {
                    const rangePoints = { '80s': 40, '180s': 90, '300s': 150, '12h': 360 };
                    const limit = rangePoints[range] || 40;
                    
                    const sliceHistory = (arr) => {
                        if (!arr) return [];
                        return arr.slice(-limit);
                    };

                    const cpuPaths = generateAdaptiveSvgPaths(sliceHistory(dataSource.cpu), 100);
                    const memPaths = generateAdaptiveSvgPaths(sliceHistory(dataSource.memory), 100);
                    const compPaths = generateAdaptiveSvgPaths(sliceHistory(dataSource.compute_memory), 100);

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
                    const tokensPaths = generateAdaptiveSvgPaths(sliceHistory(dataSource.tokens_rate));
                    const threadsPaths = generateAdaptiveSvgPaths(sliceHistory(dataSource.active_workers));

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
                    const updateTrendTicks = (svgId, currentRange) => {
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
                    updateTrendTicks('tower-trend-svg', range);
                    updateTrendTicks('tower-ai-trend-svg', range);

                    // 🛰️ [V75.6] 每次刷新时自动对 Tab 按钮的样式进行一次同步（确保重新渲染模板时自愈）
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

    // 刷新分发死信/重试队列数据
    window.refreshSyndicationQueue = async () => {
        const listEl = document.getElementById('tower-syndication-list');
        if (!listEl || typeof apiFetch !== 'function') return;
        const data = await apiFetch('/api/governance/syndication/queue');
        if (!data || !data.tasks) {
            listEl.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-dim); padding:15px;">拉取数据失败</td></tr>`;
            return;
        }
        if (data.tasks.length === 0) {
            listEl.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-dim); padding:20px;">🎉 分发队列为空，暂无死信或积压任务。</td></tr>`;
            return;
        }
        listEl.innerHTML = data.tasks.map(t => {
            const isFailed = t.status === 'FAILED';
            const color = isFailed ? '#ef4444' : '#6366f1';
            const bg = isFailed ? 'rgba(239, 68, 68, 0.1)' : 'rgba(99, 102, 241, 0.1)';
            const err = t.last_error || '无记录';
            return `<tr style="border-bottom: 1px solid var(--glass-border); text-align: left; height:40px;">
                <td style="padding: 8px; font-family:var(--font-mono); font-size:0.75rem; word-break:break-all;">${t.rel_path}</td>
                <td style="padding: 8px; font-weight:bold; color:var(--text-bright);">${t.target_id}</td>
                <td style="padding: 8px;"><span style="color:${color}; background:${bg}; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:bold;">${t.status}</span></td>
                <td style="padding: 8px; font-family:var(--font-mono);">${t.retry_count} / ${t.max_retries}</td>
                <td style="padding: 8px; color:var(--text-dim); font-size:0.75rem; max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${err}">${err}</td>
                <td style="padding: 8px; text-align: right;">
                    <button class="primary-btn" onclick="window.retrySyndicationTask('${t.rel_path}', '${t.target_id}')" style="padding:1px 5px; font-size:0.65rem; height:20px; cursor:pointer;">重试</button>
                    <button class="danger-btn" onclick="window.deleteSyndicationTask('${t.rel_path}', '${t.target_id}')" style="padding:1px 5px; font-size:0.65rem; height:20px; cursor:pointer; background:rgba(239,68,68,0.1); border:1px solid #ef4444; color:#fca5a5; border-radius:4px; margin-left:4px;">删除</button>
                </td></tr>`;
        }).join('');
    };

    window.retrySyndicationTask = async (relPath, targetId) => {
        const res = await apiFetch('/api/governance/syndication/queue/retry', {
            method: 'POST', body: JSON.stringify({ rel_path: relPath, target_id: targetId })
        });
        if (res?.success) { showToast("🔄 分发重试任务已在后台拉起...", "info"); window.refreshSyndicationQueue(); }
        else showToast(`重试失败: ${res?.error || '未知错误'}`, "error");
    };

    window.retryAllSyndicationTasks = async () => {
        if (!confirm("是否确认一键重试所有失败的分发任务？")) return;
        const res = await apiFetch('/api/governance/syndication/queue/retry', { method: 'POST', body: JSON.stringify({}) });
        if (res?.success) { showToast("🔄 所有任务已重置并在后台拉起...", "success"); window.refreshSyndicationQueue(); }
        else showToast("重置失败", "error");
    };

    window.deleteSyndicationTask = async (relPath, targetId) => {
        if (!confirm(`确定丢弃 ${targetId} 渠道的分发任务？`)) return;
        const res = await apiFetch('/api/governance/syndication/queue/delete', {
            method: 'POST', body: JSON.stringify({ rel_path: relPath, target_id: targetId })
        });
        if (res?.success) { showToast("🗑️ 任务已移出队列", "info"); window.refreshSyndicationQueue(); }
    };

    window.clearFailedSyndicationTasks = async () => {
        if (!confirm("⚠️ 确定要清空所有 FAILED 状态的分发任务吗？")) return;
        const res = await apiFetch('/api/governance/syndication/queue/delete', { method: 'POST', body: JSON.stringify({}) });
        if (res?.success) { showToast("🗑️ 已清空失败任务", "success"); window.refreshSyndicationQueue(); }
    };

    // 🚀 [V75.7] 设置 SVG 折线图鼠标悬停数值探针与 Legend 图例回填
    window.setupTrendHoverProbes = () => {
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

    // 初始化控制塔
    window.loadTowerCenter = () => {
        // 重置定时器并立即拉取
        if (window.towerTimeoutId) {
            clearTimeout(window.towerTimeoutId);
            window.towerTimeoutId = null;
        }
        window.refreshTowerTelemetry();
        window.refreshSyndicationQueue();
    };

})();
