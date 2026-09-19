/**
 * 📊 [V57.0] Illacme Plenipes Analytics Templates Shard
 * 职责：定义数据统计 Hub (Analytics Hub) 的全量视图 HTML 模板。
 */

if (!window.viewTemplates) {
    window.viewTemplates = {};
}

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
