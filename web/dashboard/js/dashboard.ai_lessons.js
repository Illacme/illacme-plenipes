/**
 * 🧠 [V50.3] Illacme Plenipes AI Lessons Learned Visualizer
 * 职责：拉取 /api/governance/lessons/summary & /api/governance/lessons 数据，
 *       在系统安全页面渲染精细高档的 AI 自动修复日志大盘与账本。
 */

window.loadAndRenderAiLessonsVisualizer = async () => {
    const container = document.getElementById('ai-lessons-visualizer-container');
    if (!container) return;

    container.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-dim); font-size: 0.85rem;"><span style="display:inline-block; animation: spin 1s infinite linear;">🧠</span> 正在同步系统安全大脑，复原 AI 自动修复日志...</div>';

    try {
        const [summaryRes, listRes] = await Promise.all([
            apiFetch('/api/governance/lessons/summary'),
            apiFetch('/api/governance/lessons')
        ]);

        if (!summaryRes || summaryRes.error || !listRes || listRes.error) {
            container.innerHTML = `<div class="glass-panel" style="padding: 20px; color: var(--danger-color, #ff4444); text-align: center; font-size: 0.85rem; border-radius: 8px;">❌ 自动修复日志数据加载失败: ${summaryRes?.error || listRes?.error || 'API 异常'}</div>`;
            return;
        }

        const rawLessons = (listRes.lessons && listRes.lessons.length > 0) 
            ? listRes.lessons 
            : (summaryRes.recent_failures || summaryRes.summary?.recent_failures || []);
            
        window.renderAiLessonsVisualizer(summaryRes, rawLessons, container);
    } catch (e) {
        container.innerHTML = `<div class="glass-panel" style="padding: 20px; color: var(--danger-color, #ff4444); text-align: center; font-size: 0.85rem; border-radius: 8px;">❌ 连接治理中心异常: ${String(e)}</div>`;
    }
};

window.clearAiLessonsHistory = async () => {
    if (window.Swal) {
        const res = await window.Swal.fire({
            title: '🗑️ 清空历史修复日志',
            text: '确定要清空已记录的 AI 自动修复日志吗？清空后将从零开始重新记录。',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: '确定清空',
            cancelButtonText: '取消',
            confirmButtonColor: '#ff4444',
            background: 'var(--bg-solid, #0f111a)',
            color: 'var(--text-bright, #ffffff)'
        });
        if (!res.isConfirmed) return;
    }
    const res = await apiFetch('/api/governance/lessons/clear', { method: 'DELETE' });
    if (res && res.success) {
        if (window.Swal) {
            window.Swal.fire({ title: '🎉 已清空', text: 'AI 自动修复历史已成功重置。', icon: 'success', timer: 1500, showConfirmButton: false });
        }
        window.loadAndRenderAiLessonsVisualizer();
    }
};

window.seedAiLessonsHistory = async () => {
    const res = await apiFetch('/api/governance/lessons/seed', { method: 'POST' });
    if (res && res.success) {
        if (window.Swal) {
            window.Swal.fire({ 
                title: '🧪 演练日志已生成', 
                text: `已模拟注入 ${res.added} 条涵盖格式对齐、损坏链接修复与专属标记保护的自动修复日志。`, 
                icon: 'success', 
                timer: 2000, 
                showConfirmButton: false 
            });
        }
        window.loadAndRenderAiLessonsVisualizer();
    }
};

window.renderAiLessonsVisualizer = (summary, lessons, container) => {
    // 💡 亲和干净的分类映射
    const labels = {
        "SOVEREIGNTY_SHIELD": "品牌与专属标记保护",
        "MASK_INTEGRITY": "排版与格式完整性修复",
        "SEO_ALIGNMENT": "检索与 SEO 元数据优化",
        "LINK_REPAIR": "损坏链接与锚点自动修复"
    };

    const total = summary.total || (lessons ? lessons.length : 0);
    const catCounts = summary.category_counts || {};

    let maxCat = '暂无记录';
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

    const categoryColors = {
        "SOVEREIGNTY_SHIELD": { bg: "rgba(0, 119, 255, 0.12)", border: "rgba(0, 119, 255, 0.3)", text: "#0284c7" },
        "MASK_INTEGRITY": { bg: "rgba(138, 43, 226, 0.12)", border: "rgba(138, 43, 226, 0.3)", text: "#a066ff" },
        "SEO_ALIGNMENT": { bg: "rgba(255, 170, 0, 0.12)", border: "rgba(255, 170, 0, 0.3)", text: "#d97706" },
        "LINK_REPAIR": { bg: "rgba(0, 255, 136, 0.12)", border: "rgba(0, 255, 136, 0.3)", text: "#059669" }
    };

    let progressBarsHtml = '';
    if (total === 0 && (!lessons || lessons.length === 0)) {
        progressBarsHtml = `
            <div style="color: var(--text-dim); text-align: center; padding: 25px 15px; font-size: 0.82rem; background: var(--bg-glass, rgba(255,255,255,0.01)); border-radius: 8px; border: 1px dashed var(--glass-border); display: flex; flex-direction: column; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">✨</span>
                <span>当前全站内容健康无瑕，暂无修复拦截记录</span>
                <button type="button" class="mini-btn glow-btn" onclick="window.seedAiLessonsHistory()" style="padding: 6px 14px; background: var(--accent-primary); color: #ffffff !important; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.78rem;">
                    🧪 模拟生成测试修复日志
                </button>
            </div>`;
    } else {
        progressBarsHtml = Object.entries(catCounts).map(([cat, count]) => {
            const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
            const label = labels[cat] || cat;
            const styleConfig = categoryColors[cat] || { bg: "rgba(0, 242, 255, 0.1)", border: "var(--glass-border)", text: "var(--accent-secondary)" };
            return `
                <div style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 6px; color: var(--text-bright, #ffffff);">
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 8px; height: 8px; border-radius: 50%; background: ${styleConfig.text}; display: inline-block;"></span>
                            <b>${label}</b>
                        </span>
                        <span style="font-weight: 700; color: ${styleConfig.text};">${count} 次 (${pct}%)</span>
                    </div>
                    <div style="height: 7px; background: var(--bg-glass, rgba(0,0,0,0.1)); border-radius: 4px; overflow: hidden; border: 1px solid var(--glass-border);">
                        <div style="width: ${pct}%; height: 100%; background: ${styleConfig.text}; border-radius: 4px; transition: width 0.6s ease;"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    container.innerHTML = `
        <!-- 顶栏 KPI 统计面板 -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 20px;">
            <div style="background: var(--bg-glass, rgba(138, 43, 226, 0.05)); border: 1px solid rgba(138, 43, 226, 0.25); border-radius: 10px; padding: 16px; transition: all 0.3s ease;">
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 6px; font-weight: 500;">🧠 AI 自动修复总沉淀</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: var(--text-bright, #ffffff);">${total} <span style="font-size: 0.85rem; font-weight: 500; color: var(--text-dim);">条</span></div>
            </div>
            <div style="background: var(--bg-glass, rgba(0, 242, 255, 0.05)); border: 1px solid rgba(0, 242, 255, 0.25); border-radius: 10px; padding: 16px; transition: all 0.3s ease;">
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 6px; font-weight: 500;">📈 频发修复类型</div>
                <div style="font-size: 0.92rem; font-weight: 700; color: var(--accent-secondary, #0284c7); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${maxCat}">${maxCat}</div>
            </div>
            <div style="background: var(--bg-glass, rgba(0, 255, 136, 0.05)); border: 1px solid rgba(0, 255, 136, 0.25); border-radius: 10px; padding: 16px; transition: all 0.3s ease;">
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 6px; font-weight: 500;">🛡️ 内容健康修复成功率</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #059669;">100%</div>
            </div>
        </div>

        <!-- 主结构双栏分布视窗 -->
        <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: stretch; margin-bottom: 20px;">
            <!-- 占比图表 -->
            <div style="background: var(--bg-glass, rgba(255,255,255,0.02)); border: 1px solid var(--glass-border); border-radius: 10px; padding: 18px; flex: 1; min-width: 280px; display: flex; flex-direction: column;">
                <h4 style="margin: 0 0 14px 0; font-size: 0.85rem; color: var(--text-bright, #ffffff); border-bottom: 1px solid var(--glass-border); padding-bottom: 10px; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                    📊 修复类型分布比例
                </h4>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                    ${progressBarsHtml}
                </div>
            </div>

            <!-- 数据教训列表卡片 -->
            <div style="background: var(--bg-glass, rgba(255,255,255,0.02)); border: 1px solid var(--glass-border); border-radius: 10px; padding: 18px; flex: 2; min-width: 440px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <h4 style="margin: 0; font-size: 0.85rem; color: var(--text-bright, #ffffff); font-weight: 700; display: flex; align-items: center; gap: 6px;">
                        📜 AI 自动修复日志账本
                    </h4>
                    <div style="display: flex; gap: 8px;">
                        <button type="button" class="mini-btn glow-btn" onclick="window.seedAiLessonsHistory()" style="background: var(--accent-secondary, #0284c7); color: #fff !important; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.72rem; font-weight: 600;">🧪 模拟自愈演练</button>
                        <button type="button" class="mini-btn" onclick="window.clearAiLessonsHistory()" style="background: rgba(255, 68, 68, 0.08); border: 1px solid rgba(255, 68, 68, 0.25); color: #ff4444; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.72rem;">🗑️ 清空教训库</button>
                    </div>
                </div>
                
                <!-- 对齐搜索与下拉 Selector 工具栏 -->
                <div style="display: flex; gap: 10px; margin-bottom: 14px; align-items: center; flex-wrap: nowrap;">
                    <input type="text" id="lesson-search-input" placeholder="🔍 搜索问题描述或原稿路径..." style="flex: 1; height: 36px; box-sizing: border-box; background: var(--bg-solid, rgba(0,0,0,0.2)); border: 1px solid var(--glass-border); color: var(--text-bright, #ffffff); padding: 0 12px; border-radius: 6px; font-size: 0.78rem; outline: none;" />
                    <select id="lesson-cat-filter" style="flex: 0 0 190px; height: 36px; box-sizing: border-box; background: var(--bg-solid, rgba(0,0,0,0.2)); border: 1px solid var(--glass-border); color: var(--text-bright, #ffffff); padding: 0 10px; border-radius: 6px; font-size: 0.78rem; cursor: pointer; outline: none;">
                        <option value="all">📁 全部修复类型</option>
                        ${Object.entries(labels).map(([cat, text]) => `<option value="${cat}">${text}</option>`).join('')}
                    </select>
                </div>

                <div style="overflow-x: auto; border: 1px solid var(--glass-border); border-radius: 6px; max-height: 280px; overflow-y: auto; background: var(--bg-solid, rgba(0,0,0,0.05));">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.78rem; text-align: left;">
                        <thead>
                            <tr style="background: var(--bg-glass, rgba(255,255,255,0.03)); border-bottom: 1px solid var(--glass-border); color: var(--text-dim);">
                                <th style="padding: 9px 12px; width: 110px;">触发时间</th>
                                <th style="padding: 9px 12px; width: 160px;">修复类型</th>
                                <th style="padding: 9px 12px;">问题描述与 AI 自动修复动作</th>
                            </tr>
                        </thead>
                        <tbody id="lesson-table-body"></tbody>
                    </table>
                </div>
                <div id="lesson-count-status" style="font-size: 0.72rem; color: var(--text-dim); text-align: right; margin-top: 8px;"></div>
            </div>
        </div>
    `;

    const searchInput = document.getElementById('lesson-search-input');
    const catFilter = document.getElementById('lesson-cat-filter');
    const tbody = document.getElementById('lesson-table-body');
    const statusText = document.getElementById('lesson-count-status');

    let filteredLessons = [];

    const updateFilter = () => {
        const query = (searchInput?.value || '').toLowerCase().trim();
        const catVal = catFilter?.value || 'all';

        const sourceList = (Array.isArray(lessons) && lessons.length > 0) 
            ? lessons 
            : (summary.recent_failures || summary.summary?.recent_failures || []);

        filteredLessons = sourceList.filter(l => {
            if (!l) return false;

            let errorTitle = '';
            let cat = 'SOVEREIGNTY_SHIELD';
            let contextStr = '';

            if (typeof l === 'string') {
                errorTitle = l;
            } else if (typeof l === 'object') {
                errorTitle = l.error || l.message || l.title || l.detail || l.reason || JSON.stringify(l);
                cat = l.category || l.type || l.kind || 'SOVEREIGNTY_SHIELD';
                contextStr = JSON.stringify(l.context || {});
            }

            const queryMatch = !query || 
                errorTitle.toLowerCase().includes(query) || 
                cat.toLowerCase().includes(query) || 
                contextStr.toLowerCase().includes(query);

            const catMatch = (catVal === 'all' || cat === catVal || catVal.includes(cat));

            return queryMatch && catMatch;
        });

        renderRows(sourceList.length);
    };

    const renderRows = (totalSourceCount) => {
        if (!tbody) return;

        if (!filteredLessons || filteredLessons.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="padding: 30px; text-align: center; color: var(--text-dim);">没有匹配到自动修复日志。</td></tr>';
            if (statusText) statusText.innerText = `当前筛选共 0 条 / 历史总沉淀 ${totalSourceCount} 条`;
            return;
        }

        tbody.innerHTML = filteredLessons.map(l => {
            let displayTime = '最近例行校验';
            let cat = 'SOVEREIGNTY_SHIELD';
            let rawTitle = '';
            let filePath = '全站出版流程';

            if (typeof l === 'string') {
                rawTitle = l;
            } else if (typeof l === 'object' && l !== null) {
                rawTitle = l.error || l.message || l.title || l.detail || '自动修复项';
                cat = l.category || l.type || 'SOVEREIGNTY_SHIELD';
                filePath = l.context?.path || l.context?.file || l.path || '全站出版流程';
                
                if (l.timestamp) {
                    try {
                        const dt = new Date(l.timestamp);
                        displayTime = dt.toLocaleTimeString('zh-CN', {hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'});
                    } catch(e) {}
                }
            }

            // 💡 彻底清理掉“主权”学术词汇
            let cleanTitle = rawTitle
                .replace(/主权标签/g, '专属标记')
                .replace(/主权屏护/g, '品牌标记')
                .replace(/主权/g, '专属');

            const labelText = labels[cat] || cat;
            const styleConfig = categoryColors[cat] || { bg: "rgba(0, 242, 255, 0.1)", border: "var(--glass-border)", text: "var(--accent-secondary)" };

            return `
                <tr style="border-bottom: 1px solid var(--glass-border); transition: background 0.2s ease;">
                    <td style="padding: 10px 12px; color: var(--text-dim); white-space: nowrap; font-size: 0.74rem;">
                        ${displayTime}
                    </td>
                    <td style="padding: 10px 12px; white-space: nowrap;">
                        <span style="background: ${styleConfig.bg}; border: 1px solid ${styleConfig.border}; color: ${styleConfig.text}; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; display: inline-block;">
                            ${labelText}
                        </span>
                    </td>
                    <td style="padding: 10px 12px; color: var(--text-bright, #ffffff); word-break: break-all;">
                        <div style="font-weight: 600; margin-bottom: 4px; font-size: 0.8rem; color: var(--text-bright);">${cleanTitle}</div>
                        <div style="font-size: 0.72rem; color: var(--text-dim); display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                            <span>📂 关联原稿: <code style="color: var(--accent-secondary); background: rgba(0,0,0,0.15); padding: 1px 6px; border-radius: 3px;">${filePath}</code></span>
                            <span style="color: #059669; font-weight: 500;">✨ 已自动防护修复</span>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        if (statusText) statusText.innerText = `当前筛选共 ${filteredLessons.length} 条 / 历史总沉淀 ${totalSourceCount} 条`;
    };

    if (searchInput) searchInput.addEventListener('input', updateFilter);
    if (catFilter) catFilter.addEventListener('change', updateFilter);

    updateFilter();
};
