/**
 * 🚀 [V122.0] Illacme Plenipes - Dispatch Popover Component
 * 职责：右上角轻量下拉小窗浮层（Task Popover）渲染与交互控制。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

window._isPopoverOpen = false;

/**
 * 切换下拉浮层的显示/隐藏
 */
window.toggleDispatchPopover = function (forceState) {
    let popover = document.getElementById('dispatch-popover-tray');
    if (!popover) {
        popover = window.createDispatchPopoverDOM();
    }

    const nextState = typeof forceState === 'boolean' ? forceState : !window._isPopoverOpen;
    window._isPopoverOpen = nextState;

    if (nextState) {
        const trigger = document.getElementById('btn-dispatch-center');
        if (trigger) {
            const rect = trigger.getBoundingClientRect();
            popover.style.top = `${rect.bottom + 8}px`;
            const rightOffset = window.innerWidth - rect.right;
            popover.style.right = `${Math.max(rightOffset - 120, 20)}px`;
        }
        popover.classList.add('active');
        if (window._lastDispatchOverview) {
            window.renderPopoverContent(window._lastDispatchOverview);
        } else if (typeof window.refreshDispatchIndicator === 'function') {
            window.refreshDispatchIndicator();
        }
    } else {
        popover.classList.remove('active');
    }
};

/**
 * 创建浮层 DOM 节点挂载至 body
 */
window.createDispatchPopoverDOM = function () {
    let el = document.getElementById('dispatch-popover-tray');
    if (el) return el;

    el = document.createElement('div');
    el.id = 'dispatch-popover-tray';
    el.className = 'dispatch-popover';
    el.innerHTML = `
        <div class="popover-header">
            <span class="popover-title">
                <span>🚀 出版调度实时监视器</span>
            </span>
            <button class="popover-close" onclick="window.toggleDispatchPopover(false)">×</button>
        </div>
        <div class="popover-body" id="dispatch-popover-body">
            <div style="padding: 20px; text-align: center; color: var(--text-muted, #9ca3af); font-size: 0.82rem;">
                正在获取出版流水线心跳...
            </div>
        </div>
        <div class="popover-footer">
            <button class="btn-open-workbench" onclick="window.toggleDispatchPopover(false); if(typeof window.showView==='function') window.showView('tasks');">
                🚀 进入完整发布任务大厅与历史账本 ↗
            </button>
        </div>
    `;
    document.body.appendChild(el);

    // 全局点击遮罩关闭侦听
    document.addEventListener('click', (e) => {
        if (!window._isPopoverOpen) return;
        const trigger = document.getElementById('btn-dispatch-center');
        if (trigger && (trigger === e.target || trigger.contains(e.target))) return;
        if (el && !el.contains(e.target)) {
            window.toggleDispatchPopover(false);
        }
    });

    return el;
};

/**
 * 填充浮层内部内容
 */
window.renderPopoverContent = function (data) {
    const body = document.getElementById('dispatch-popover-body');
    if (!body) return;

    const isPublishing = Boolean(data && data.is_publishing);
    const summary = (data && data.summary) || {};
    const deadTasks = (data && data.dead_letter_tasks) || [];
    const recentRecords = (data && data.recent_records) || [];

    let html = '';

    // 1. 活跃状态专区
    if (isPublishing) {
        html += `
            <div class="popover-status-box running">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span class="status-indicator-text running">
                        <span>⏳ 全域流水线正在运行...</span>
                    </span>
                    <button class="mini-btn danger" onclick="if(typeof window.abortSync==='function') window.abortSync();" style="padding: 3px 8px; font-size: 0.72rem; border-radius: 4px; cursor: pointer;">
                        ⏹️ 中止发布
                    </button>
                </div>
                <div class="pipeline-progress-track">
                    <div class="pipeline-progress-bar"></div>
                </div>
                <div class="popover-status-sub">
                    正在执行：多语种翻译、静态排版编译与多渠道并发推送
                </div>
            </div>
        `;
    } else if (deadTasks.length > 0) {
        html += `
            <div class="popover-status-box warning">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="status-indicator-text warning">
                        ⚠️ 存在 ${deadTasks.length} 项分发异常
                    </span>
                    <a href="#/tasks" class="popover-heal-link" onclick="window.toggleDispatchPopover(false); if(typeof window.showView==='function') window.showView('tasks', 'deadletter');">
                        一键自愈 ↗
                    </a>
                </div>
                <div class="popover-status-sub" style="margin-top: 4px;">
                    最近错误：${window.escapeHtml ? window.escapeHtml(deadTasks[0].last_error || '') : deadTasks[0].last_error}
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="popover-status-box ready">
                <div>
                    <div class="status-indicator-text ready">🟢 全网分发就绪 · 待命状态</div>
                    <div class="popover-status-sub" style="margin-top: 2px;">
                        历史累计已推送 ${summary.total_syndicated || 0} 篇次成果
                    </div>
                </div>
                <button class="mini-btn glow-btn primary-btn" onclick="window.toggleDispatchPopover(false); if(typeof window.triggerPublish==='function') window.triggerPublish(false);" style="padding: 4px 10px; font-size: 0.74rem;">
                    🚀 触发发布
                </button>
            </div>
        `;
    }

    // 2. 最近完成发布小票
    html += `
        <div style="margin-top: 4px;">
            <div class="popover-section-title">
                最近发布成果
            </div>
    `;

    if (recentRecords.length === 0) {
        html += `
            <div class="popover-empty-tip">
                暂无历史发布记录
            </div>
        `;
    } else {
        const topRecords = recentRecords.slice(0, 3);
        html += '<div style="display: flex; flex-direction: column; gap: 8px;">';
        topRecords.forEach(rec => {
            const relPath = window.escapeHtml ? window.escapeHtml(rec.rel_path) : rec.rel_path;
            const targetId = window.escapeHtml ? window.escapeHtml(rec.target_id) : rec.target_id;
            const langCode = window.escapeHtml ? window.escapeHtml(rec.lang_code || 'all') : (rec.lang_code || 'all');
            html += `
                <div class="popover-record-item">
                    <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 250px;">
                        <div class="popover-record-title">${relPath}</div>
                        <div class="popover-record-sub">${targetId} · ${langCode}</div>
                    </div>
                    <div>
                        ${rec.remote_url ? `
                            <a href="${rec.remote_url}" target="_blank" class="magic-link-mini" title="直达线上物权">
                                🔗 访问
                            </a>
                        ` : `
                            <span class="tag-synced-mini">已同步</span>
                        `}
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }

    html += '</div>';
    body.innerHTML = html;
};
