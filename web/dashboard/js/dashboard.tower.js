/**
 * 🗼 [V1.0] 控制塔数据调度器 - 总编室控制塔可视化面板
 * 职责：异步轮询系统脉搏接口 `/api/governance/pulse`，渲染服务器负载与算力线程池动态走势。
 */

(function() {
    window.towerIntervalId = null;

    // 格式化运行时间
    function formatUptime(seconds) {
        if (typeof seconds !== 'number' || isNaN(seconds)) return '--';
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hrs}h ${mins}m ${secs}s`;
    }

    // 刷新控制塔数据
    window.refreshTowerTelemetry = async () => {
        const el = document.getElementById('view-tower');
        // 防御性生命周期检查：如果视图不存在或已被隐藏，自动清理定时器并退出
        if (!el || el.style.display === 'none' || window.location.hash !== '#/tower') {
            if (window.towerIntervalId) {
                clearInterval(window.towerIntervalId);
                window.towerIntervalId = null;
            }
            return;
        }

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

            const progressEl = document.getElementById('tower-progress');
            if (progressEl && stats.progress) {
                const current = stats.progress.current || 0;
                const total = stats.progress.total || 0;
                const pct = stats.progress.percentage || 0;
                if (total === 0) {
                    progressEl.innerHTML = `100% <span style="font-size:0.8rem; color:var(--text-dim);">(已对准)</span>`;
                } else {
                    progressEl.innerHTML = `${pct}% <span style="font-size:0.8rem; color:var(--text-dim);">(${current}/${total})</span>`;
                }
            }

            const costEl = document.getElementById('tower-cost');
            if (costEl && stats.usage) {
                const cost = stats.usage.cost || 0;
                const tokens = stats.usage.tokens || 0;
                costEl.innerHTML = `$${cost.toFixed(4)} <span style="font-size:0.8rem; color:var(--text-dim);">(${tokens.toLocaleString()} tkn)</span>`;
            }

            // 2. 刷新线程池监控
            if (stats.pools) {
                // 全局同步线程池
                const gPool = stats.pools.global || {};
                const gActive = gPool.active_workers || 0;
                const gMax = gPool.max_workers || 1;
                const gQueue = gPool.queue_size || 0;
                const gPct = Math.min(100, Math.round((gActive / gMax) * 100));
                
                const gText = document.getElementById('pool-global-text');
                const gBar = document.getElementById('pool-global-bar');
                if (gText) gText.innerText = `${gActive} / ${gMax} (队列: ${gQueue})`;
                if (gBar) gBar.style.width = `${gPct}%`;

                // AI 翻译推理池
                const aiPool = stats.pools.ai || {};
                const aiActive = aiPool.active_workers || 0;
                const aiMax = aiPool.max_workers || 1;
                const aiQueue = aiPool.queue_size || 0;
                const aiPct = Math.min(100, Math.round((aiActive / aiMax) * 100));
                
                const aiText = document.getElementById('pool-ai-text');
                const aiBar = document.getElementById('pool-ai-bar');
                if (aiText) aiText.innerText = `${aiActive} / ${aiMax} (队列: ${aiQueue})`;
                if (aiBar) aiBar.style.width = `${aiPct}%`;

                // 资源处理池
                const assetPool = stats.pools.asset || {};
                const assetActive = assetPool.active_workers || 0;
                const assetMax = assetPool.max_workers || 1;
                const assetQueue = assetPool.queue_size || 0;
                const assetPct = Math.min(100, Math.round((assetActive / assetMax) * 100));
                
                const assetText = document.getElementById('pool-asset-text');
                const assetBar = document.getElementById('pool-asset-bar');
                if (assetText) assetText.innerText = `${assetActive} / ${assetMax} (队列: ${assetQueue})`;
                if (assetBar) assetBar.style.width = `${assetPct}%`;
            }

            // 3. 刷新物理服务器负载仪表盘 (SVG 动态周长 C = 263.89)
            if (stats.load) {
                const cpuPct = stats.load.cpu_percent || 0;
                const memPct = stats.load.memory_percent || 0;

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
            }
        } catch (error) {
            console.error("🗼 [Tower] 遥测数据拉取失败:", error);
        }
    };

    // 初始化控制塔
    window.loadTowerCenter = () => {
        // 立即拉取一次
        window.refreshTowerTelemetry();

        // 重置轮询
        if (window.towerIntervalId) {
            clearInterval(window.towerIntervalId);
        }
        window.towerIntervalId = setInterval(window.refreshTowerTelemetry, 3000);
    };
})();
