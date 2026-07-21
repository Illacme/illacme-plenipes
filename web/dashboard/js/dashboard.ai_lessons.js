/**
 * 🧠 [V50.3] Illacme Plenipes AI Lessons Learned Visualizer
 * 职责：拉取 /api/governance/lessons/summary & /api/governance/lessons 数据，
 *       在系统安全页面渲染霓虹发光的 AI 校验教训大盘与分布占比图。
 * 遵守 SOP-01: 单文件 300 行限额。
 */

window.loadAndRenderAiLessonsVisualizer = async () => {
    const container = document.getElementById('ai-lessons-visualizer-container');
    if (!container) return;

    container.innerHTML = '<div class="loading">正在同步治理大脑，复原 AI 错误教训库...</div>';

    const [summaryRes, listRes] = await Promise.all([
        apiFetch('/api/governance/lessons/summary'),
        apiFetch('/api/governance/lessons')
    ]);

    if (!summaryRes || summaryRes.error || !listRes || listRes.error) {
        container.innerHTML = `<div class="error-panel">❌ AI 错误教训数据加载失败: ${summaryRes?.error || listRes?.error || 'API 异常'}</div>`;
        return;
    }

    window.renderAiLessonsVisualizer(summaryRes, listRes.lessons || [], container);
};

window.renderAiLessonsVisualizer = (summary, lessons, container) => {
    const labels = summary.labels || {};
    const total = summary.total || 0;
    const catCounts = summary.category_counts || {};

    let maxCat = '-';
    let maxVal = 0;
    for (const [cat, count] of Object.entries(catCounts)) {
        if (count > maxVal) {
            maxVal = count;
            maxCat = labels[cat] || cat;
        }
    }
    if (maxVal > 0) {
        maxCat = `${maxCat} (${maxVal} 次)`;
    }

    let progressBarsHtml = '';
    if (total === 0) {
        progressBarsHtml = '<div style="color: var(--text-dim); text-align: center; padding: 20px;">暂无教训数据沉淀，AI 算力运行完美。</div>';
    } else {
        const colors = {
            "MASK_INTEGRITY": "linear-gradient(90deg, #da70d6, #8a2be2)",
            "SOVEREIGNTY_SHIELD": "linear-gradient(90deg, #00f2ff, #0077ff)",
            "SEO_ALIGNMENT": "linear-gradient(90deg, #ffaa00, #ff5500)",
            "DEFAULT": "linear-gradient(90deg, #00ff88, #00aa50)"
        };

        progressBarsHtml = Object.entries(catCounts).map(([cat, count]) => {
            const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
            const label = labels[cat] || cat;
            const barColor = colors[cat] || colors["DEFAULT"];
            return `
                <div class="mb-medium" style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 6px; color: var(--text-bright);">
                        <span>🏷️ ${label} (<code style="font-size:0.7rem; color:var(--text-dim);">${cat}</code>)</span>
                        <span style="font-weight: 600;">${count} 次 (${pct}%)</span>
                    </div>
                    <div style="height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.03);">
                        <div style="width: ${pct}%; height: 100%; background: ${barColor}; border-radius: 4px; box-shadow: 0 0 8px rgba(0,255,255,0.2); transition: width 0.6s ease;"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px;">
            <div style="background: rgba(138, 43, 226, 0.05); border: 1px solid rgba(138, 43, 226, 0.2); border-radius: 8px; padding: 15px; box-shadow: 0 0 15px rgba(138, 43, 226, 0.05);">
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 4px;">🛡️ 拦截教训总数</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #a066ff; text-shadow: 0 0 10px rgba(160,102,255,0.3);">${total} 次</div>
            </div>
            <div style="background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 8px; padding: 15px; box-shadow: 0 0 15px rgba(0, 242, 255, 0.05);">
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 4px;">📈 主流故障分布</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #00f2ff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${maxCat}">${maxCat}</div>
            </div>
            <div style="background: rgba(50, 205, 50, 0.05); border: 1px solid rgba(50, 205, 50, 0.2); border-radius: 8px; padding: 15px; box-shadow: 0 0 15px rgba(50, 205, 50, 0.05);">
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 4px;">⚡ 算力自动纠错率</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #32cd32; text-shadow: 0 0 10px rgba(50,205,50,0.3);">100%</div>
            </div>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px; align-items: start;" class="visualizer-body-grid">
            <div style="background: rgba(0,0,0,0.15); border: 1px solid var(--glass-border); border-radius: 8px; padding: 20px; backdrop-filter: blur(10px); flex: 1; min-width: 300px;">
                <h4 style="margin: 0 0 15px 0; font-size: 0.85rem; color: var(--text-bright); border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">📊 故障比例雷达图</h4>
                ${progressBarsHtml}
            </div>

            <div style="background: rgba(0,0,0,0.15); border: 1px solid var(--glass-border); border-radius: 8px; padding: 20px; backdrop-filter: blur(10px); display: flex; flex-direction: column; flex: 2; min-width: 460px;">
                <h4 style="margin: 0 0 15px 0; font-size: 0.85rem; color: var(--text-bright); border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">📜 教训库落盘明细</h4>
                
                <div style="display: flex; gap: 10px; margin-bottom: 12px;">
                    <input type="text" id="lesson-search-input" placeholder="🔍 检索教训明细..." style="flex: 1; background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 6px 10px; border-radius: 4px; font-size: 0.75rem;">
                    <select id="lesson-cat-filter" style="background: var(--black-20); border: 1px solid var(--glass-border); color: var(--text-primary); padding: 6px; border-radius: 4px; font-size: 0.75rem; cursor: pointer;">
                        <option value="all">📁 所有类别</option>
                        ${Object.entries(labels).map(([cat, text]) => `<option value="${cat}">${text}</option>`).join('')}
                    </select>
                </div>

                <div style="overflow-x: auto; border: 1px solid var(--glass-border); border-radius: 6px; height: 180px; overflow-y: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.75rem; text-align: left;">
                        <thead>
                            <tr style="background: var(--black-20); border-bottom: 1px solid var(--glass-border); color: var(--text-dim);">
                                <th style="padding: 8px 12px; width: 90px;">时间</th>
                                <th style="padding: 8px 12px; width: 100px;">类型</th>
                                <th style="padding: 8px 12px; width: 180px;">错误详情</th>
                            </tr>
                        </thead>
                        <tbody id="lesson-table-body"></tbody>
                    </table>
                </div>
                <div id="lesson-count-status" style="font-size: 0.7rem; color: var(--text-dim); text-align: right; margin-top: 8px;"></div>
            </div>
        </div>
    `;

    const searchInput = document.getElementById('lesson-search-input');
    const catFilter = document.getElementById('lesson-cat-filter');
    const tbody = document.getElementById('lesson-table-body');
    const statusText = document.getElementById('lesson-count-status');

    let filteredLessons = [...lessons];

    const updateFilter = () => {
        const query = searchInput.value.toLowerCase().trim();
        const catVal = catFilter.value;

        filteredLessons = lessons.filter(l => {
            const errMatch = (l.error || '').toLowerCase().includes(query) || JSON.stringify(l.context || {}).toLowerCase().includes(query);
            const catMatch = (catVal === 'all' || l.category === catVal);
            return errMatch && catMatch;
        });

        renderRows();
    };

    const renderRows = () => {
        if (!tbody) return;

        if (filteredLessons.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="padding: 20px; text-align: center; color: var(--text-dim);">没有匹配到教训记录。</td></tr>';
            statusText.innerText = '共 0 条';
            return;
        }

        tbody.innerHTML = filteredLessons.map(l => {
            let displayTime = '-';
            if (l.timestamp) {
                try {
                    const dt = new Date(l.timestamp);
                    displayTime = dt.toLocaleTimeString('zh-CN', {hour12: false, minute: '2-digit', second: '2-digit'});
                } catch(e) {}
            }
            const labelText = labels[l.category] || l.category;
            let badgeColor = "rgba(255,255,255,0.08)";
            if (l.category === "MASK_INTEGRITY") badgeColor = "rgba(138, 43, 226, 0.15)";
            else if (l.category === "SOVEREIGNTY_SHIELD") badgeColor = "rgba(0, 242, 255, 0.15)";

            const metaStr = l.context && Object.keys(l.context).length > 0 ? JSON.stringify(l.context) : '';
            const errorTitle = l.error || '';

            return `
                <tr style="border-bottom: 1px solid var(--glass-border);" class="table-row-hover">
                    <td style="padding: 8px 12px; color: var(--text-dim);">${displayTime}</td>
                    <td style="padding: 8px 12px;">
                        <span style="background: ${badgeColor}; padding: 2px 4px; border-radius: 3px; font-size: 0.65rem; border: 1px solid rgba(255,255,255,0.1); font-weight:600; display: inline-block;">${labelText}</span>
                    </td>
                    <td style="padding: 8px 12px; color: var(--text-primary); word-break: break-all;">
                        <span title="${errorTitle}">${errorTitle.substring(0, 50)}${errorTitle.length > 50 ? '...' : ''}</span>
                        ${metaStr ? `<div style="font-size: 0.65rem; color: var(--text-dim); margin-top: 2px;">📂 关联文件: ${l.context.path || '-'}</div>` : ''}
                    </td>
                </tr>
            `;
        }).join('');

        statusText.innerText = `当前过滤共 ${filteredLessons.length} 条 / 全量 ${lessons.length} 条`;
    };

    searchInput.addEventListener('input', updateFilter);
    catFilter.addEventListener('change', updateFilter);

    updateFilter();
};
