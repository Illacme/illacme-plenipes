/**
 * 🚀 [V122.0] Illacme Plenipes - Dispatch Ledger & Dead-Letter Rendering
 * 职责：分发成果账本表格渲染（含真实线上访问链接直达）与死信异常自愈卡片交互。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

/**
 * 渲染全域分发成果账本表格
 */
window.renderDispatchLedger = function (records) {
    const container = document.getElementById('dispatch-ledger-container');
    const badge = document.getElementById('tab-badge-ledger');
    if (!container) return;

    if (badge) badge.innerText = String(records ? records.length : 0);

    if (!records || records.length === 0) {
        container.innerHTML = `
            <div style="padding: 40px 20px; text-align: center; color: var(--text-muted, #9ca3af);">
                <div style="font-size: 2rem; margin-bottom: 8px;">📖</div>
                <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-bright, #ffffff);">尚无成功发布记录</div>
                <div style="font-size: 0.8rem; margin-top: 4px;">点击右上角【全域发布】或在文库中选择笔记即可发起分发。</div>
            </div>
        `;
        return;
    }

    let html = `
        <table class="ledger-table">
            <thead>
                <tr>
                    <th style="width: 35%;">原稿文档路径</th>
                    <th style="width: 12%;">发布语种</th>
                    <th style="width: 18%;">目标分发渠道</th>
                    <th style="width: 20%;">发布时间</th>
                    <th style="width: 15%; text-align: right;">线上真实产物</th>
                </tr>
            </thead>
            <tbody>
    `;

    records.forEach(rec => {
        const hasUrl = Boolean(rec.remote_url);
        const safePath = window.escapeHtml ? window.escapeHtml(rec.rel_path) : rec.rel_path;
        const targetId = window.escapeHtml ? window.escapeHtml(rec.target_id) : rec.target_id;
        const langCode = window.escapeHtml ? window.escapeHtml(rec.lang_code || 'zh-CN') : (rec.lang_code || 'zh-CN');
        const rawTime = rec.updated_at;
        const timeText = window.formatDispatchTime ? window.formatDispatchTime(rawTime) : (rawTime || '刚刚');
        const fullTime = window.formatDispatchFullTime ? window.formatDispatchFullTime(rawTime) : (rawTime || '刚刚');

        html += `
            <tr class="ledger-row" data-path="${safePath.toLowerCase()}" data-target="${targetId.toLowerCase()}">
                <td>
                    <div style="font-weight: 600; color: var(--text-bright, #ffffff); font-size: 0.86rem;">
                        ${safePath}
                    </div>
                </td>
                <td>
                    <span style="font-family: var(--font-mono, monospace); font-size: 0.78rem; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">
                        ${langCode}
                    </span>
                </td>
                <td>
                    <span class="platform-pill">
                        <span>🏷️</span>
                        <span>${targetId}</span>
                    </span>
                </td>
                <td>
                    <span style="font-size: 0.78rem; color: var(--text-muted, #9ca3af);" title="${fullTime}">
                        ${timeText || '刚刚'}
                    </span>
                </td>
                <td style="text-align: right;">
                    ${hasUrl ? `
                        <a href="${rec.remote_url}" target="_blank" rel="noopener noreferrer" class="magic-deep-link" title="在新标签页中访问线上真实文章页面">
                            <span>🌐 访问线上页面 ↗</span>
                        </a>
                    ` : `
                        <span style="font-size: 0.76rem; color: #00ff88; font-weight: 600;">✓ 已对准上线</span>
                    `}
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
};

/**
 * 渲染死信异常自愈卡片列表
 */
window.renderDispatchDeadLetters = function (tasks) {
    const container = document.getElementById('dispatch-deadletter-container');
    const badge = document.getElementById('tab-badge-deadletter');
    if (!container) return;

    if (badge) badge.innerText = String(tasks ? tasks.length : 0);

    if (!tasks || tasks.length === 0) {
        container.innerHTML = `
            <div class="glass-panel" style="padding: 40px 20px; text-align: center; border-radius: 12px;">
                <div style="font-size: 2rem; margin-bottom: 8px;">🎉</div>
                <div style="font-weight: 700; font-size: 0.95rem; color: #00ff88;">队列健康 · 0 项死信异常</div>
                <div style="font-size: 0.8rem; color: var(--text-muted, #9ca3af); margin-top: 4px;">所有渠道同步任务均已圆满完成或就绪。</div>
            </div>
        `;
        return;
    }

    container.innerHTML = tasks.map(t => {
        const safePath = window.escapeHtml ? window.escapeHtml(t.rel_path) : t.rel_path;
        const targetId = window.escapeHtml ? window.escapeHtml(t.target_id) : t.target_id;
        const safeError = window.escapeHtml ? window.escapeHtml(t.last_error || '未知网络或认证异常') : (t.last_error || '未知网络或认证异常');

        return `
            <div class="deadletter-card" data-path="${safePath.toLowerCase()}" data-target="${targetId.toLowerCase()}">
                <div class="dl-header">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.1rem;">⚠️</span>
                        <span class="dl-title">${safePath}</span>
                        <span class="platform-pill" style="border-color: rgba(255, 77, 77, 0.4); color: #ff6b6b;">
                            ${targetId}
                        </span>
                    </div>
                    <span style="font-size: 0.76rem; color: var(--text-muted, #9ca3af);">
                        已重试 ${t.retry_count || 0} 次
                    </span>
                </div>
                <div class="dl-reason">
                    <span style="color: #ff6b6b; font-weight: 700;">诊断根因:</span> ${safeError}
                </div>
                <div class="dl-actions">
                    <a href="#/plugins" onclick="if(typeof window.showView==='function') window.showView('plugins', 'hosting');" class="secondary-btn" style="padding: 5px 12px; font-size: 0.78rem; text-decoration: none;">
                        <span>🔑 检查渠道授权</span>
                    </a>
                    <button class="secondary-btn danger" onclick="window.clearSingleDeadLetterTask('${safePath}', '${targetId}')" style="padding: 5px 12px; font-size: 0.78rem;">
                        <span>🗑️ 移出队列</span>
                    </button>
                    <button class="primary-btn glow-btn" onclick="window.retrySingleDeadLetterTask('${safePath}', '${targetId}')" style="padding: 5px 14px; font-size: 0.78rem;">
                        <span>🔄 立即重试</span>
                    </button>
                </div>
            </div>
        `;
    }).join('');
};

/**
 * 重试单篇死信任务
 */
window.retrySingleDeadLetterTask = async function (relPath, targetId) {
    if (typeof apiFetch !== 'function') return;
    try {
        const res = await apiFetch('/api/dispatch/deadletter/retry', {
            method: 'POST',
            body: JSON.stringify({ rel_path: relPath, target_id: targetId })
        });
        if (typeof showToast === 'function') {
            showToast('已重置并启动自愈重试', 'success');
        }
        if (typeof window.loadDispatchCenter === 'function') {
            window.loadDispatchCenter('deadletter');
        }
    } catch (e) {
        if (typeof showToast === 'function') showToast('重试请求失败: ' + e.message, 'error');
    }
};

/**
 * 批量一键重试所有死信任务
 */
window.retryAllFailedTasks = async function () {
    if (typeof apiFetch !== 'function') return;
    try {
        const res = await apiFetch('/api/dispatch/deadletter/retry', {
            method: 'POST',
            body: JSON.stringify({})
        });
        if (typeof showToast === 'function') {
            showToast('已将所有失败任务加入重试队列', 'success');
        }
        if (typeof window.loadDispatchCenter === 'function') {
            window.loadDispatchCenter('deadletter');
        }
    } catch (e) {
        if (typeof showToast === 'function') showToast('批量重试请求失败: ' + e.message, 'error');
    }
};

/**
 * 移出死信队列
 */
window.clearSingleDeadLetterTask = async function (relPath, targetId) {
    if (typeof apiFetch !== 'function') return;
    try {
        await apiFetch('/api/dispatch/deadletter/clear', {
            method: 'DELETE',
            body: JSON.stringify({ rel_path: relPath, target_id: targetId })
        });
        if (typeof showToast === 'function') {
            showToast('已移出死信队列', 'info');
        }
        if (typeof window.loadDispatchCenter === 'function') {
            window.loadDispatchCenter('deadletter');
        }
    } catch (e) {
        if (typeof showToast === 'function') showToast('清理失败: ' + e.message, 'error');
    }
};

/**
 * 本地实时过滤账本或死信
 */
window.filterDispatchLedger = function () {
    const input = document.getElementById('dispatch-search-input');
    if (!input) return;
    const query = input.value.trim().toLowerCase();

    // 过滤表格行
    const rows = document.querySelectorAll('.ledger-row');
    rows.forEach(r => {
        const p = r.getAttribute('data-path') || '';
        const t = r.getAttribute('data-target') || '';
        r.style.display = (!query || p.includes(query) || t.includes(query)) ? '' : 'none';
    });

    // 过滤死信卡片
    const cards = document.querySelectorAll('.deadletter-card');
    cards.forEach(c => {
        const p = c.getAttribute('data-path') || '';
        const t = c.getAttribute('data-target') || '';
        c.style.display = (!query || p.includes(query) || t.includes(query)) ? 'flex' : 'none';
    });
};
