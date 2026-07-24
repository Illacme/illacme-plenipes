/**
 * 🌌 [V57.0] Illacme Plenipes Tower and Analytics Templates
 * 职责：定义系统遥测与数据统计 HTML 模板，以满足 dashboard.templates.js 的 300 行文件大小限制。
 */

if (!window.viewTemplates) {
    window.viewTemplates = {};
}

window.viewTemplates.tower = `
        <div id="view-tower" class="view-panel">
            <div class="view-header">
                <h2>🗼 系统遥测 (System Telemetry)</h2>
            </div>
            <div class="view-content scroll-container" style="display: flex; flex-direction: column; gap: 20px; padding: 20px; overflow-y: auto; flex: 1;">
                <!-- 第一行：状态卡片 -->
                <div class="tower-stats-row" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px;">
                    <div class="glass-panel tower-card">
                        <div class="card-label">系统状态</div>
                        <div class="card-val" id="tower-status">LOADING...</div>
                    </div>
                    <div class="glass-panel tower-card">
                        <div class="card-label">运行时间 (Uptime)</div>
                        <div class="card-val" id="tower-uptime">--</div>
                    </div>
                    <div class="glass-panel tower-card">
                        <div class="card-label">出版总进度</div>
                        <div class="card-val" id="tower-progress">--</div>
                    </div>
                    <div class="glass-panel tower-card">
                        <div class="card-label">累计算力花费 (Cost)</div>
                        <div class="card-val" id="tower-cost">--</div>
                    </div>
                </div>
                
                <!-- 第二行：排队负载与性能 -->
                <div class="tower-charts-row" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; min-height: 250px;">
                    <!-- 任务排队负载监控 -->
                    <div class="glass-panel chart-container" style="display: flex; flex-direction: column; padding: 15px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.8rem; color: var(--accent-secondary); margin-bottom: 15px;">📡 任务调度队列监控</div>
                        <div class="pool-grid" style="display: flex; flex-direction: column; gap: 15px; justify-content: center; flex: 1;">
                            <div class="pool-item">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.75rem;">
                                    <span>全局同步线程池 (Global Sync Pool)</span>
                                    <span id="pool-global-text">0 / 0</span>
                                </div>
                                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.05); height:10px; border-radius:5px; overflow:hidden;">
                                    <div id="pool-global-bar" style="width:0%; height:100%; background:var(--accent-primary); transition:width 0.5s;"></div>
                                </div>
                            </div>
                            <div class="pool-item">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.75rem;">
                                    <span>AI 翻译与推理池 (AI Compute Pool)</span>
                                    <span id="pool-ai-text">0 / 0</span>
                                </div>
                                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.05); height:10px; border-radius:5px; overflow:hidden;">
                                    <div id="pool-ai-bar" style="width:0%; height:100%; background:var(--accent-secondary); transition:width 0.5s;"></div>
                                </div>
                            </div>
                            <div class="pool-item">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.75rem;">
                                    <span>静态资源处理池 (Asset Processor Pool)</span>
                                    <span id="pool-asset-text">0 / 0</span>
                                </div>
                                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.05); height:10px; border-radius:5px; overflow:hidden;">
                                    <div id="pool-asset-bar" style="width:0%; height:100%; background:var(--accent-orange, #ff9d00); transition:width 0.5s;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 系统实时性能负载 -->
                    <div class="glass-panel chart-container" style="display: flex; flex-direction: column; padding: 15px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.8rem; color: var(--accent-secondary); margin-bottom: 15px;">💻 物理服务器负载监控</div>
                        <div style="display: flex; gap: 20px; flex: 1; align-items: center; justify-content: space-around;">
                            <!-- CPU 负载仪表盘 -->
                            <div class="gauge-box" style="text-align:center;">
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 8px;">CPU 负载</div>
                                <div class="gauge-wrapper" style="position:relative; width:100px; height:100px;">
                                    <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                                        <circle cx="50" cy="50" r="42" stroke="rgba(255,255,255,0.05)" stroke-width="8" fill="none"/>
                                        <circle id="gauge-cpu-ring" cx="50" cy="50" r="42" stroke="var(--accent-primary)" stroke-width="8" fill="none"
                                                stroke-dasharray="263.89" stroke-dashoffset="263.89" stroke-linecap="round" style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);"/>
                                    </svg>
                                    <div class="gauge-text" id="gauge-cpu" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:1.1rem; font-family:var(--font-mono); font-weight:bold; color:var(--text-bright);">--%</div>
                                </div>
                            </div>
                            <!-- 内存占用仪表盘 -->
                            <div class="gauge-box" style="text-align:center;">
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 8px;">系统内存</div>
                                <div class="gauge-wrapper" style="position:relative; width:100px; height:100px;">
                                    <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                                        <circle cx="50" cy="50" r="42" stroke="rgba(255,255,255,0.05)" stroke-width="8" fill="none"/>
                                        <circle id="gauge-mem-ring" cx="50" cy="50" r="42" stroke="var(--accent-secondary)" stroke-width="8" fill="none"
                                                stroke-dasharray="263.89" stroke-dashoffset="263.89" stroke-linecap="round" style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);"/>
                                    </svg>
                                    <div class="gauge-text" id="gauge-mem" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:1.1rem; font-family:var(--font-mono); font-weight:bold; color:var(--text-bright);">--%</div>
                                </div>
                            </div>
                            <!-- 本地算力内存仪表盘 -->
                            <div class="gauge-box" style="text-align:center;">
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 8px;">算力内存</div>
                                <div class="gauge-wrapper" style="position:relative; width:100px; height:100px;">
                                    <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                                        <circle cx="50" cy="50" r="42" stroke="rgba(255,255,255,0.05)" stroke-width="8" fill="none"/>
                                        <circle id="gauge-compute-ring" cx="50" cy="50" r="42" stroke="var(--accent-orange, #ff9d00)" stroke-width="8" fill="none"
                                                stroke-dasharray="263.89" stroke-dashoffset="263.89" stroke-linecap="round" style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);"/>
                                    </svg>
                                    <div class="gauge-text" id="gauge-compute" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:1.1rem; font-family:var(--font-mono); font-weight:bold; color:var(--text-bright);">--%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 第三行：历史负载走势图 -->
                <div class="tower-history-row" style="display: grid; grid-template-columns: 1fr; gap: 20px; margin-top: 20px;">
                    <div class="glass-panel chart-container" style="display: flex; flex-direction: column; padding: 15px; min-height: 180px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.8rem; color: var(--accent-secondary); margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span>📈 负载历史演进趋势 (CPU & Memory Sparkline)</span>
                                <!-- 🛰️ [V75.6] 时间跨度调节 Tab 组 -->
                                <div class="trend-time-tabs" id="tower-trend-tabs" style="display: flex; gap: 2px; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); padding: 2px; border-radius: 6px; height: 22px; align-items: center; box-sizing: border-box;">
                                    <button type="button" class="mini-btn active" id="btn-trend-80s" onclick="window.switchTrendRange('80s')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-bright, #fff); transition: background 0.2s; background: var(--accent-primary);">80s</button>
                                    <button type="button" class="mini-btn" id="btn-trend-180s" onclick="window.switchTrendRange('180s')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-dim); transition: background 0.2s; background: transparent;">3m</button>
                                    <button type="button" class="mini-btn" id="btn-trend-300s" onclick="window.switchTrendRange('300s')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-dim); transition: background 0.2s; background: transparent;">5m</button>
                                    <button type="button" class="mini-btn" id="btn-trend-12h" onclick="window.switchTrendRange('12h')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-dim); transition: background 0.2s; background: transparent;">12h</button>
                                </div>
                            </div>
                            <div id="trend-legend-val" style="display: flex; gap: 15px; font-size: 0.75rem; font-family: var(--font-mono); transition: color 0.15s;"><span style="color: var(--accent-primary);">● CPU</span><span style="color: var(--accent-secondary);">● MEM</span><span style="color: var(--accent-orange, #ff9d00);">● COMPUTE</span></div>
                        </div>
                        <div style="flex: 1; position: relative; width: 100%; height: 138px;">
                             <svg id="tower-trend-svg" width="100%" height="100%" viewBox="0 0 500 138" preserveAspectRatio="none" style="overflow: visible;">
                                <defs>
                                    <linearGradient id="cpu-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-primary)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent-primary)" stop-opacity="0"/></linearGradient>
                                    <linearGradient id="mem-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-secondary)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent-secondary)" stop-opacity="0"/></linearGradient>
                                    <linearGradient id="comp-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-orange, #ff9d00)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent-orange, #ff9d00)" stop-opacity="0"/></linearGradient>
                                </defs>
                                <!-- 🌌 [V75.6] 负载遥测科技感背景网格虚线 -->
                                <g stroke="rgba(255,255,255,0.04)" stroke-width="1" stroke-dasharray="2,4">
                                    <line x1="0" y1="30" x2="500" y2="30" />
                                    <line x1="0" y1="60" x2="500" y2="60" />
                                    <line x1="0" y1="90" x2="500" y2="90" />
                                    <line x1="125" y1="0" x2="125" y2="120" />
                                    <line x1="250" y1="0" x2="250" y2="120" />
                                    <line x1="375" y1="0" x2="375" y2="120" />
                                </g>
                                <!-- 时间轴底实线与刻度 -->
                                <line x1="0" y1="120" x2="500" y2="120" stroke="rgba(255,255,255,0.12)" stroke-width="1" />
                                <!-- Y轴极简百分比刻度标记 -->
                                <g id="trend-y-ticks" fill="var(--text-dim)" opacity="0.35" font-size="8" font-family="var(--font-mono)" style="pointer-events: none;">
                                    <text x="5" y="12" text-anchor="start">100%</text>
                                    <text x="5" y="64" text-anchor="start">50%</text>
                                    <text x="5" y="116" text-anchor="start">0%</text>
                                </g>
                                <!-- 磁吸式垂直数值探针线 -->
                                <line id="trend-probe-line" x1="0" y1="0" x2="0" y2="120" stroke="rgba(255,255,255,0.35)" stroke-width="1" stroke-dasharray="2,3" style="display: none; pointer-events: none;" />
                                <g fill="var(--text-dim)" font-size="9" font-family="var(--font-mono)">
                                    <text class="trend-tick-0" x="0" y="133" text-anchor="start">-80s</text>
                                    <text class="trend-tick-1" x="125" y="133" text-anchor="middle">-60s</text>
                                    <text class="trend-tick-2" x="250" y="133" text-anchor="middle">-40s</text>
                                    <text class="trend-tick-3" x="375" y="133" text-anchor="middle">-20s</text>
                                    <text class="trend-tick-4" x="500" y="133" text-anchor="end">现在 (0s)</text>
                                </g>
                                <path id="trend-cpu-area" fill="url(#cpu-grad)" d=""/><path id="trend-cpu-line" fill="none" stroke="var(--accent-primary)" stroke-width="2" d=""/>
                                <path id="trend-mem-area" fill="url(#mem-grad)" d=""/><path id="trend-mem-line" fill="none" stroke="var(--accent-secondary)" stroke-width="2" d=""/>
                                <path id="trend-compute-area" fill="url(#comp-grad)" d=""/><path id="trend-compute-line" fill="none" stroke="var(--accent-orange, #ff9d00)" stroke-width="2" d=""/>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <!-- 新增：AI 大模型实时遥测趋势图 -->
                <div class="tower-ai-trend-row" style="display: grid; grid-template-columns: 1fr; gap: 20px; margin-top: 20px;">
                    <div class="glass-panel chart-container" style="display: flex; flex-direction: column; padding: 15px; min-height: 180px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.8rem; color: var(--accent-secondary); margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span>🧠 AI 算力实时遥测走势 (AI Compute Live Telemetry)</span>
                                <!-- 🛰️ [V75.6] AI 时间跨度调节 Tab 组 -->
                                <div class="trend-time-tabs" id="tower-ai-trend-tabs" style="display: flex; gap: 2px; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); padding: 2px; border-radius: 6px; height: 22px; align-items: center; box-sizing: border-box;">
                                    <button type="button" class="mini-btn active" id="btn-ai-trend-80s" onclick="window.switchTrendRange('80s')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-bright, #fff); transition: background 0.2s; background: var(--accent-primary);">80s</button>
                                    <button type="button" class="mini-btn" id="btn-ai-trend-180s" onclick="window.switchTrendRange('180s')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-dim); transition: background 0.2s; background: transparent;">3m</button>
                                    <button type="button" class="mini-btn" id="btn-ai-trend-300s" onclick="window.switchTrendRange('300s')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-dim); transition: background 0.2s; background: transparent;">5m</button>
                                    <button type="button" class="mini-btn" id="btn-ai-trend-12h" onclick="window.switchTrendRange('12h')" 
                                            style="padding: 0 8px; height: 16px; line-height: 16px; font-size: 0.65rem; border-radius: 4px; border: none; cursor: pointer; color: var(--text-dim); transition: background 0.2s; background: transparent;">12h</button>
                                </div>
                            </div>
                            <div id="trend-ai-legend-val" style="display: flex; gap: 15px; font-size: 0.75rem; font-family: var(--font-mono); transition: color 0.15s;"><span style="color: var(--accent-secondary);">● 吞吐速率 (Tokens/s)</span><span style="color: var(--accent-orange, #ff9d00);">● 活动工作线程 (Active Threads)</span></div>
                        </div>
                        <div style="flex: 1; position: relative; width: 100%; height: 138px;">
                             <svg id="tower-ai-trend-svg" width="100%" height="100%" viewBox="0 0 500 138" preserveAspectRatio="none" style="overflow: visible;">
                                <defs>
                                    <linearGradient id="tokens-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-secondary)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent-secondary)" stop-opacity="0"/></linearGradient>
                                    <linearGradient id="threads-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-orange, #ff9d00)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent-orange, #ff9d00)" stop-opacity="0"/></linearGradient>
                                </defs>
                                <!-- 🌌 [V75.6] AI 遥测科技感背景网格虚线 -->
                                <g stroke="rgba(255,255,255,0.04)" stroke-width="1" stroke-dasharray="2,4">
                                    <line x1="0" y1="30" x2="500" y2="30" />
                                    <line x1="0" y1="60" x2="500" y2="60" />
                                    <line x1="0" y1="90" x2="500" y2="90" />
                                    <line x1="125" y1="0" x2="125" y2="120" />
                                    <line x1="250" y1="0" x2="250" y2="120" />
                                    <line x1="375" y1="0" x2="375" y2="120" />
                                </g>
                                <!-- 时间轴底实线与刻度 -->
                                <line x1="0" y1="120" x2="500" y2="120" stroke="rgba(255,255,255,0.12)" stroke-width="1" />
                                <!-- Y轴极简百分比刻度标记 -->
                                <g id="trend-ai-y-ticks" fill="var(--text-dim)" opacity="0.35" font-size="8" font-family="var(--font-mono)" style="pointer-events: none;">
                                    <!-- 动态由 JS 填充 -->
                                </g>
                                <!-- 磁吸式垂直数值探针线 -->
                                <line id="trend-ai-probe-line" x1="0" y1="0" x2="0" y2="120" stroke="rgba(255,255,255,0.35)" stroke-width="1" stroke-dasharray="2,3" style="display: none; pointer-events: none;" />
                                <g fill="var(--text-dim)" font-size="9" font-family="var(--font-mono)">
                                    <text class="trend-tick-0" x="0" y="133" text-anchor="start">-80s</text>
                                    <text class="trend-tick-1" x="125" y="133" text-anchor="middle">-60s</text>
                                    <text class="trend-tick-2" x="250" y="133" text-anchor="middle">-40s</text>
                                    <text class="trend-tick-3" x="375" y="133" text-anchor="middle">-20s</text>
                                    <text class="trend-tick-4" x="500" y="133" text-anchor="end">现在 (0s)</text>
                                </g>
                                <path id="trend-tokens-area" fill="url(#tokens-grad)" d=""/><path id="trend-tokens-line" fill="none" stroke="var(--accent-secondary)" stroke-width="2" d=""/>
                                <path id="trend-threads-area" fill="url(#threads-grad)" d=""/><path id="trend-threads-line" fill="none" stroke="var(--accent-orange, #ff9d00)" stroke-width="2" d=""/>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <!-- 第四行：多渠道分发任务队列 (死信队列监控与治理) -->
                <div class="tower-syndication-row" style="display: grid; grid-template-columns: 1fr; gap: 20px; margin-top: 20px;">
                    <div class="glass-panel" style="display: flex; flex-direction: column; padding: 20px; border-radius: 12px; min-height: 200px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.85rem; color: var(--accent-secondary); margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace;">
                            <span>📡 多渠道分发死信与重试队列 (SYNDICATION DEAD-LETTER QUEUE)</span>
                            <div style="display: flex; gap: 10px;">
                                <button class="primary-btn glow-btn" id="btn-retry-all-synd" onclick="window.retryAllSyndicationTasks()" style="padding: 4px 10px; font-size: 0.7rem; height: 24px; line-height: 12px; background: rgba(99,102,241,0.2); border: 1px solid var(--accent-primary);">🔄 一键重试所有失败</button>
                                <button class="danger-btn" id="btn-clear-failed-synd" onclick="window.clearFailedSyndicationTasks()" style="padding: 4px 10px; font-size: 0.7rem; height: 24px; line-height: 12px; background: rgba(239,68,68,0.2); border: 1px solid #ef4444; color: #fca5a5; border-radius: 4px; cursor: pointer;">🗑️ 一键清空失败</button>
                            </div>
                        </div>
                        <div class="table-container" style="overflow-x: auto; width: 100%; border-radius: 8px; border: 1px solid var(--glass-border);">
                            <table style="width: 100%; min-width: 600px; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: rgba(255, 255, 255, 0.03); border-bottom: 1px solid var(--glass-border); text-align: left;">
                                        <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 25%;">文档路径</th>
                                        <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 15%;">目标渠道</th>
                                        <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 10%;">状态</th>
                                        <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 10%;">重试次数</th>
                                        <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 25%;">最后错误信息</th>
                                        <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 15%; text-align: right;">操作</th>
                                    </tr>
                                </thead>
                                <tbody id="tower-syndication-list" style="font-size: 0.8rem;">
                                    <!-- 动态注入分发任务行 -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    `;

window.viewTemplates.analytics = `
        <div id="view-analytics" class="view-panel">
            <div class="view-header" style="margin-bottom: 0; padding-bottom: 15px; border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center;">
                <h2>📊 数据统计 (Analytics Hub)</h2>
                <div class="header-actions">
                    <button class="primary-btn glow-btn" id="btn-refresh-analytics" onclick="window.refreshAnalyticsData()" style="padding: 5px 12px; font-size: 0.75rem; height: 28px; line-height: 14px;">🔄 刷新统计</button>
                </div>
            </div>
            <div class="view-content scroll-container" style="display: flex; flex-direction: column; gap: 20px; padding: 20px; overflow-y: auto; flex: 1; min-height: 0; box-sizing: border-box;">
                <!-- 第一部分：宏观业务核心指标卡片 -->
                <div class="analytics-stats-row" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; flex-shrink: 0;">
                    <div class="glass-panel tower-card" style="position: relative; overflow: hidden; border-radius: 12px; padding: 12px 14px;">
                        <div class="card-label" style="font-size: 0.75rem; color: var(--text-dim);">📂 原稿文库规模</div>
                        <div class="card-val" id="analytics-total-docs" style="font-size: 1.4rem; font-weight: 800; color: var(--text-bright); margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">0 <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-dim);">篇</span></div>
                        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 6px;" id="analytics-total-words">全库共 0 字</div>
                    </div>
                    <div class="glass-panel tower-card" style="position: relative; overflow: hidden; border-radius: 12px; padding: 12px 14px;">
                        <div class="card-label" style="font-size: 0.75rem; color: var(--text-dim);">🚀 线上发布率 (Live)</div>
                        <div class="card-val" id="analytics-live-percent" style="font-size: 1.4rem; font-weight: 800; color: var(--accent-primary); margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">0.0%</div>
                        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 6px;" id="analytics-live-ratio">已发布 0 篇 / 草稿 0 篇</div>
                    </div>
                    <div class="glass-panel tower-card" style="position: relative; overflow: hidden; border-radius: 12px; padding: 12px 14px;">
                        <div class="card-label" style="font-size: 0.75rem; color: var(--text-dim);">🔗 双链网络健康度</div>
                        <div class="card-val" id="analytics-graph-health" style="font-size: 1.4rem; font-weight: 800; color: #4caf50; margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">100分</div>
                        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 6px;" id="analytics-graph-links">0 节点 / 0 链接</div>
                    </div>
                    <div class="glass-panel tower-card" style="position: relative; overflow: hidden; border-radius: 12px; padding: 12px 14px;">
                        <div class="card-label" style="font-size: 0.75rem; color: var(--text-dim);">🧠 累计算力花费</div>
                        <div class="card-val" id="analytics-total-cost" style="font-size: 1.4rem; font-weight: 800; color: var(--accent-secondary); margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">$0.00</div>
                        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 6px;" id="analytics-session-cost">本次运行花费 $0.00</div>
                    </div>
                </div>
                
                <!-- 第二部分：语种覆盖率与关系网络分析 -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; flex-shrink: 0;">
                    <!-- 翻译语种覆盖率进度 -->
                    <div class="glass-panel" style="display: flex; flex-direction: column; padding: 20px; border-radius: 12px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.85rem; color: var(--accent-secondary); margin-bottom: 15px; letter-spacing: 0.5px; font-family: 'JetBrains Mono', monospace;">🌍 多语种译文覆盖矩阵 (I18N COVERAGE)</div>
                        <div id="analytics-translation-list" style="display: flex; flex-direction: column; gap: 16px; justify-content: center; flex: 1; min-height: 120px;">
                            <!-- 动态注入语种进度条 -->
                        </div>
                    </div>
                    
                    <!-- 双链连通状态明细 -->
                    <div class="glass-panel" style="display: flex; flex-direction: column; padding: 20px; border-radius: 12px;">
                        <div class="sector-header" style="font-weight: 800; font-size: 0.85rem; color: var(--accent-secondary); margin-bottom: 15px; letter-spacing: 0.5px; font-family: 'JetBrains Mono', monospace;">🧬 知识网路连通审计 (GRAPH INTEGRITY)</div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; flex: 1; align-items: center; min-height: 120px;">
                            <div class="metric-item-small" style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);" title="未与其他文章建立 [[双向链接]] 的独立稿件数量">
                                <span style="font-size: 0.75rem; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                                    <span>独立未关联稿件</span>
                                    <span style="opacity: 0.6; cursor: help;" title="未与文库中其他文章建立 [[双向链接]] 的孤立稿件">💡</span>
                                </span>
                                <span id="analytics-isolated-count" style="font-size: 1.25rem; font-weight: bold; color: var(--text-bright); font-family: var(--font-mono);">0</span>
                            </div>
                            <div class="metric-item-small" style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);" title="文章中引用了已被删除或改名的文件链接数">
                                <span style="font-size: 0.75rem; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                                    <span>失效断裂引用 (死链)</span>
                                    <span style="opacity: 0.6; cursor: help;" title="指向不存在或已被删除文章的无效链接">💡</span>
                                </span>
                                <span id="analytics-broken-links" style="font-size: 1.25rem; font-weight: bold; color: #ff6b6b; font-family: var(--font-mono);">0</span>
                            </div>
                            <div class="metric-item-small" style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);" title="全库文章之间双向引用的交织密集程度 (0.0~1.0)">
                                <span style="font-size: 0.75rem; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                                    <span>知识网织密度</span>
                                    <span style="opacity: 0.6; cursor: help;" title="文章与文章之间交叉引用交织的密集程度">💡</span>
                                </span>
                                <span id="analytics-graph-density" style="font-size: 1.25rem; font-weight: bold; color: var(--accent-primary); font-family: var(--font-mono);">0.00</span>
                            </div>
                            <div class="metric-item-small" style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);" title="系统物理自动扫描并自愈死链的防线守护状态">
                                <span style="font-size: 0.75rem; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                                    <span>自愈机制守护状态</span>
                                    <span style="opacity: 0.6; cursor: help;" title="系统物理自动核验双向链接，并在出版构建时兜底自愈死链">💡</span>
                                </span>
                                <span id="analytics-self-heal-status" style="font-size: 0.78rem; font-weight: bold; color: #4caf50; display: flex; align-items: center; gap: 4px; height: 26px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">🛡️ 已自动兜底 1 处死链</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 第三部分：最近的算力开销记录明细 -->
                <div class="glass-panel" style="display: flex; flex-direction: column; padding: 20px; border-radius: 12px; min-height: 200px;">
                    <div class="sector-header" style="font-weight: 800; font-size: 0.85rem; color: var(--accent-secondary); margin-bottom: 15px; letter-spacing: 0.5px; font-family: 'JetBrains Mono', monospace;">💸 最近算力账单流水 (COMPUTE BILLING LEDGER)</div>
                    <div class="table-container" style="overflow-x: auto; width: 100%; border-radius: 8px; border: 1px solid var(--glass-border);">
                        <table style="width: 100%; min-width: 600px; border-collapse: collapse;">
                            <thead>
                                <tr style="background: rgba(255, 255, 255, 0.03); border-bottom: 1px solid var(--glass-border); text-align: left;">
                                    <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 20%;">发生时间</th>
                                    <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 20%;">计费事项</th>
                                    <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 45%;">描述明细</th>
                                    <th style="padding: 10px; font-size: 0.75rem; color: var(--text-dim); width: 15%; text-align: right;">算力花费</th>
                                </tr>
                            </thead>
                            <tbody id="analytics-ledger-list" style="font-size: 0.8rem;">
                                <!-- 动态注入流水行 -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
