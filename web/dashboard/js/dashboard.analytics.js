/**
 * 📊 [V1.0] Illacme Plenipes Analytics Hub
 * 职责：文稿与双链网络全业务流程数据统计加载、数值渐入交互、多语种翻译覆盖率及计费流水账本渲染。
 */

window.loadAnalyticsCenter = async () => {
    await window.refreshAnalyticsData();
};

window.refreshAnalyticsData = async () => {
    const refreshBtn = document.getElementById('btn-refresh-analytics');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerText = "⏳ 统计中...";
    }

    try {
        const res = await apiFetch('/api/governance/sync-stats');
        if (!res || res.error) {
            console.error("加载统计数据失败:", res ? res.error : "未知异常");
            return;
        }

        // 1. 填充宏观指标
        const docs = res.documents || { total_count: 0, total_word_count: 0, live_count: 0, draft_count: 0, live_percent: 0.0 };
        document.getElementById('analytics-total-docs').innerHTML = `${docs.total_count} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-dim);">篇</span>`;
        document.getElementById('analytics-total-words').innerText = `全库共 ${docs.total_word_count.toLocaleString()} 字`;

        document.getElementById('analytics-live-percent').innerText = `${docs.live_percent}%`;
        document.getElementById('analytics-live-ratio').innerText = `已发布 ${docs.live_count} 篇 / 草稿 ${docs.draft_count} 篇`;

        const graph = res.knowledge_graph || { total_nodes: 0, total_links: 0, isolated_count: 0, broken_link_count: 0, health_score: 100 };
        const healthValEl = document.getElementById('analytics-graph-health');
        if (healthValEl) {
            healthValEl.innerText = `${graph.health_score}分`;
            if (graph.health_score >= 90) {
                healthValEl.style.color = '#4caf50'; // 绿色健康
            } else if (graph.health_score >= 70) {
                healthValEl.style.color = 'var(--accent-orange, #ff9d00)'; // 橙色警告
            } else {
                healthValEl.style.color = '#ff6b6b'; // 红色危险
            }
        }
        document.getElementById('analytics-graph-links').innerText = `${graph.total_nodes} 节点 / ${graph.total_links} 链接`;

        const usage = res.usage || { session_cost: 0.0, total_historical_cost: 0.0, recent_ledger: [] };
        document.getElementById('analytics-total-cost').innerText = `$${usage.total_historical_cost.toFixed(2)}`;
        document.getElementById('analytics-session-cost').innerText = `本次运行花费 $${usage.session_cost.toFixed(4)}`;

        // 2. 填充知识图谱审计指标
        document.getElementById('analytics-isolated-count').innerText = graph.isolated_count;
        document.getElementById('analytics-broken-links').innerText = graph.broken_link_count;
        
        let density = 0.0;
        if (graph.total_nodes > 1) {
            density = graph.total_links / (graph.total_nodes * (graph.total_nodes - 1));
        }
        document.getElementById('analytics-graph-density').innerText = density.toFixed(4);

        const healStatusEl = document.getElementById('analytics-self-heal-status');
        if (healStatusEl) {
            if (graph.broken_link_count === 0) {
                healStatusEl.innerHTML = '🟢 严丝合缝';
                healStatusEl.style.color = '#4caf50';
            } else {
                healStatusEl.innerHTML = `⚠️ 发现 ${graph.broken_link_count} 处断链`;
                healStatusEl.style.color = 'var(--accent-orange, #ff9d00)';
            }
        }

        // 3. 渲染翻译语种矩阵进度条
        const transContainer = document.getElementById('analytics-translation-list');
        if (transContainer) {
            const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';
            if (pubMode === 'basic') {
                transContainer.innerHTML = `
                    <div style="text-align:center; opacity:0.8; padding:20px; font-size:0.8rem; border: 1px dashed rgba(230, 126, 34, 0.2); border-radius: 8px; background: rgba(230, 126, 34, 0.02); color: #e67e22; line-height: 1.6;">
                        📜 <b>当前印记模式：基础物理出版 (Basic)</b><br>
                        此模式下不执行多语言 AI 翻译，翻译进度条与物理分发阵列已被挂起。
                    </div>`;
            } else if (pubMode === 'enhanced') {
                transContainer.innerHTML = `
                    <div style="text-align:center; opacity:0.8; padding:20px; font-size:0.8rem; border: 1px dashed rgba(52, 152, 219, 0.2); border-radius: 8px; background: rgba(52, 152, 219, 0.02); color: #3498db; line-height: 1.6;">
                        🛰️ <b>当前印记模式：智能母语增强 (Enhanced)</b><br>
                        此模式下仅针对 SEO 标题与网页描述进行 AI 翻译与点击率调优，正文不执行跨语言翻译，分发矩阵已被挂起。
                    </div>`;
            } else {
                const coverageMap = res.translation.coverage || {};
                const keys = Object.keys(coverageMap);
                if (keys.length === 0) {
                    transContainer.innerHTML = `<div style="text-align:center; opacity:0.5; padding:10px; font-size:0.8rem;">ℹ️ 未配置任何目标语言，暂无译文覆盖。</div>`;
                } else {
                    transContainer.innerHTML = keys.map(lang => {
                        const data = coverageMap[lang];
                        const percent = data.coverage_percent;
                        const nativeName = window.LanguageHub && typeof window.LanguageHub.resolveToNativeName === 'function'
                            ? window.LanguageHub.resolveToNativeName(lang)
                            : lang.toUpperCase();
                        return `
                            <div class="lang-progress-item">
                                <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:0.75rem;">
                                    <span style="font-weight:600; color:var(--text-bright);">${nativeName} <span class="locale-code-badge" style="background:rgba(255,255,255,0.08); padding:1px 4px; border-radius:3px; font-size:0.65rem; margin-left:4px;">${lang}</span></span>
                                    <span style="color:var(--text-bright);">${percent}% (${data.translated_count}/${docs.total_count} 篇)</span>
                                </div>
                                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.05); height:8px; border-radius:4px; overflow:hidden;">
                                    <div class="fill" style="width: 0%; height:100%; background:linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)); border-radius:4px; transition:width 1s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                                </div>
                            </div>
                        `;
                    }).join('');

                    requestAnimationFrame(() => {
                        setTimeout(() => {
                            const items = transContainer.querySelectorAll('.lang-progress-item');
                            keys.forEach((lang, idx) => {
                                const percent = coverageMap[lang].coverage_percent;
                                const fill = items[idx].querySelector('.fill');
                                if (fill) fill.style.width = `${percent}%`;
                            });
                        }, 50);
                    });
                }
            }
        }

        // 4. 渲染算力流水
        const ledgerContainer = document.getElementById('analytics-ledger-list');
        if (ledgerContainer) {
            const ledger = usage.recent_ledger || [];
            if (ledger.length === 0) {
                ledgerContainer.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:2rem; opacity:0.4;">📭 暂无算力消耗账单流水</td></tr>`;
            } else {
                ledgerContainer.innerHTML = ledger.map(item => {
                    const costVal = item.cost ? `$${item.cost.toFixed(4)}` : '$0.0000';
                    return `
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.03); transition: background 0.2s;">
                            <td style="padding:10px; font-family:var(--font-mono); color:var(--text-dim);">${item.time_str || '-'}</td>
                            <td style="padding:10px;"><span style="background:rgba(var(--accent-secondary-rgb, 0, 242, 254), 0.1); border:1px solid rgba(var(--accent-secondary-rgb, 0, 242, 254), 0.25); padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:600; color:var(--accent-secondary);">${item.event_type}</span></td>
                            <td style="padding:10px; max-width: 350px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color:var(--text-bright);" title="${item.description}">${item.description || '-'}</td>
                            <td style="padding:10px; text-align:right; font-family:var(--font-mono); font-weight:600; color:var(--text-bright);">${costVal}</td>
                        </tr>
                    `;
                }).join('');
            }
        }

    } catch (e) {
        console.error("加载统计数据异常:", e);
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerText = "🔄 刷新统计";
        }
    }
};
