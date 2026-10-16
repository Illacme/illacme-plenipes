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
                <span>📋 任务进度与状态</span>
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
                🚀 前往发布中心大盘 ↗
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
 * 格式化成果发布相对时间与完整绝对时间
 */
window.parseDispatchDate = function (raw) {
    if (!raw) return null;
    try {
        let s = String(raw).trim();
        if (/^\d{10,13}$/.test(s)) return new Date(Number(s) > 1e11 ? Number(s) : Number(s) * 1000);
        if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(s)) s = s.replace(' ', 'T') + 'Z';
        const d = new Date(s);
        return isNaN(d.getTime()) ? null : d;
    } catch (e) { return null; }
};

window.formatDispatchTime = function (raw) {
    const d = window.parseDispatchDate ? window.parseDispatchDate(raw) : null;
    if (!d) return String(raw || '');
    const diffSec = Math.floor((Date.now() - d.getTime()) / 1000);
    if (diffSec < 45) return '刚刚';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}分钟前`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}小时前`;
    const pad = (n) => String(n).padStart(2, '0');
    if (diffSec < 86400 * 2) return `昨天 ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    if (diffSec < 86400 * 7) return `${Math.floor(diffSec / 86400)}天前`;
    return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

window.formatDispatchFullTime = function (raw) {
    const d = window.parseDispatchDate ? window.parseDispatchDate(raw) : null;
    if (!d) return String(raw || '');
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
};

/**
 * 填充浮层内部内容
 */
window.renderPopoverContent = function (data) {
    const body = document.getElementById('dispatch-popover-body');
    if (!body) return;

    const fullState = window._fullSitePublishState || {};
    const isPublishing = Boolean(data && data.is_publishing) || Boolean(fullState.isPublishing) || Boolean(window._isPublishPreviewActive);
    const stage = fullState.stage || (isPublishing ? 2 : 0);
    const stageName = fullState.stageName || (isPublishing ? '编译中' : '待命');
    const summary = (data && data.summary) || {};
    const deadTasks = (data && data.dead_letter_tasks) || [];
    const recentRecords = (data && data.recent_records) || [];

    let html = '';

    // 1. 活跃状态专区 (支持全站发布 4 步 Stepper 进度与终端直达)
    if (isPublishing) {
        html += `
            <div class="popover-status-box running" style="padding: 10px 12px; background: rgba(0, 240, 255, 0.06); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span class="status-indicator-text running" style="font-weight: 700; color: #00f0ff; font-size: 0.84rem; display: flex; align-items: center; gap: 6px;">
                        <span>⏳ 全站发布执行中</span>
                    </span>
                    <span style="font-size: 0.7rem; color: #00ff88; background: rgba(0,255,136,0.12); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(0,255,136,0.25);">
                        ${stageName}
                    </span>
                </div>
                <div class="preview-stepper-bar" style="margin: 6px 0; padding: 4px 6px; font-size: 0.68rem; background: rgba(0,0,0,0.3);">
                    <div class="step-item ${stage >= 1 ? (stage === 1 ? 'active' : 'completed') : ''}"><span class="step-icon">🔍</span> 预检</div>
                    <div class="step-arrow">→</div>
                    <div class="step-item ${stage >= 2 ? (stage === 2 ? 'active' : 'completed') : ''}"><span class="step-icon">🌐</span> 排版</div>
                    <div class="step-arrow">→</div>
                    <div class="step-item ${stage >= 3 ? (stage === 3 ? 'active' : 'completed') : ''}"><span class="step-icon">🎨</span> 装配</div>
                    <div class="step-arrow">→</div>
                    <div class="step-item ${stage >= 4 ? (stage === 4 ? 'active' : 'completed') : ''}"><span class="step-icon">🚀</span> 部署</div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; gap: 6px;">
                    <button class="primary-btn glow-btn" onclick="window.toggleDispatchPopover(false); if(typeof window.triggerPublish==='function') window.triggerPublish();" style="flex: 1; padding: 4px 8px; font-size: 0.75rem; background: var(--neon-cyan); color: #000; font-weight: 700; border: none; border-radius: 4px; cursor: pointer;">
                        🖥️ 恢复日志视窗
                    </button>
                    <button class="mini-btn danger" onclick="if(typeof window.abortSync==='function') window.abortSync();" style="padding: 4px 8px; font-size: 0.72rem; border-radius: 4px; cursor: pointer;">
                        🛑 中止
                    </button>
                </div>
            </div>
        `;
    } else if (deadTasks.length > 0) {
        const lastErr = (deadTasks[0] && deadTasks[0].last_error) || '';
        const safeErr = window.escapeHtml ? window.escapeHtml(lastErr) : lastErr;
        html += `
            <div class="popover-status-box warning">
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                    <span class="status-indicator-text warning">
                        ⚠️ 存在 ${deadTasks.length} 项分发异常
                    </span>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <button class="popover-retry-btn" id="btn-popover-retry-all" onclick="window.triggerPopoverRetryAll(this)" title="立即将异常任务重新排入分发管线">
                            <span>🔄</span><span>一键重试</span>
                        </button>
                        <a href="#/tasks" class="popover-heal-link" onclick="window.toggleDispatchPopover(false); if(typeof window.showView==='function') window.showView('tasks', 'deadletter');" title="进入发布中心死信队列">
                            详情 ↗
                        </a>
                    </div>
                </div>
                <div class="popover-status-sub" style="margin-top: 4px;">
                    最近错误：${safeErr}
                </div>
            </div>
        `;
    } else {
        const total = summary.total_syndicated || 0;
        const channelList = (data && data.channel_health) || [];
        const enabledChannels = channelList.filter(c => c && c.enabled);
        const enabledCount = enabledChannels.length;
        const hostingCount = enabledChannels.filter(c => c.type === 'hosting').length;
        const socialCount = enabledChannels.filter(c => c.type !== 'hosting').length;
        const channelTip = enabledCount > 0
            ? `已连接 ${enabledCount} 个发布渠道（包含 ${hostingCount} 个全站托管与 ${socialCount} 个社交分发）`
            : '暂未连接发布渠道';
        const channelText = enabledCount > 0 ? ` · ${enabledCount} 个渠道就绪` : '';
        const successRate = summary.success_rate || '100%';
        html += `
            <div class="popover-status-box ready">
                <div style="min-width: 0; flex: 1; margin-right: 8px;">
                    <div class="status-indicator-text ready">🟢 发布流水线就绪</div>
                    <div class="popover-status-sub" style="margin-top: 3px; font-size: 0.73rem; line-height: 1.3;" title="${channelTip}">
                        累计全站发布 ${total} 次${channelText}
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; flex-shrink: 0;">
                    <button class="popover-heal-link" onclick="window.toggleDispatchPopover(false); if(typeof window.triggerPublish==='function') window.triggerPublish();" style="border: none; background: transparent; cursor: pointer; color: var(--neon-cyan); font-size: 0.74rem;" title="打开白盒发布终端视窗">
                        🖥️ 日志
                    </button>
                    <span class="popover-kpi-badge" title="全站发布历史成功率: ${successRate}">
                        ${successRate}
                    </span>
                    <button class="popover-refresh-btn" onclick="window.triggerPopoverManualRefresh(this)" title="立即刷新发布状态与成果">
                        <span>🔄</span>
                    </button>
                </div>
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
            const timeText = window.formatDispatchTime ? window.formatDispatchTime(rec.updated_at) : (rec.updated_at || '');
            const fullTime = window.formatDispatchFullTime ? window.formatDispatchFullTime(rec.updated_at) : (rec.updated_at || '');
            const linkTitle = rec.target_type === 'hosting' ? '在新窗口访问在线网页 ↗' : '在新窗口查看平台文章 ↗';
            html += `
                <div class="popover-record-item">
                    <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:270px;flex:1;min-width:0;">
                        <div class="popover-record-title" title="${relPath}">${relPath}</div>
                        <div class="popover-record-sub">
                            <span>${targetId} · ${langCode}</span>
                            ${timeText ? `<span class="popover-record-time" title="${fullTime}"> · 🕒 ${timeText}</span>` : ''}
                        </div>
                    </div>
                    <div>
                        ${rec.remote_url ? `<a href="${rec.remote_url}" target="_blank" class="magic-link-mini" title="${linkTitle}">🔗 访问</a>` : `<span class="tag-synced-mini">已同步</span>`}
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }

    html += '</div>';
    body.innerHTML = html;
};

/**
 * 浮层内直接就地一键重试全部失败/异常任务
 */
window.triggerPopoverRetryAll = async function (btn) {
    if (typeof apiFetch !== 'function') return;
    const origHtml = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.innerHTML = '<span>⏳</span><span>正在重试...</span>'; }
    try {
        const res = await apiFetch('/api/dispatch/deadletter/retry', { method: 'POST', body: JSON.stringify({}) });
        if (typeof showToast === 'function') showToast((res && res.message) || '已触发后台自愈重试管线', 'success');
        if (typeof window.startHostingDeployPolling === 'function') window.startHostingDeployPolling();
        if (typeof window.loadHostingDeployCenter === 'function') window.loadHostingDeployCenter();
        if (typeof window.refreshDispatchIndicator === 'function') await window.refreshDispatchIndicator();
        if (typeof window.loadDispatchCenter === 'function' && window._currentView === 'tasks') window.loadDispatchCenter('deadletter');
    } catch (e) {
        if (typeof showToast === 'function') showToast('重试请求失败: ' + (e ? e.message : e), 'error');
        if (btn) { btn.disabled = false; btn.innerHTML = origHtml; }
    }
};

/**
 * 浮层内态势看板手动触发即时刷新
 */
window.triggerPopoverManualRefresh = async function (btn) {
    if (btn) btn.classList.add('is-spinning');
    try {
        if (typeof window.refreshDispatchIndicator === 'function') await window.refreshDispatchIndicator();
    } finally {
        if (btn) setTimeout(() => btn.classList.remove('is-spinning'), 400);
    }
};
