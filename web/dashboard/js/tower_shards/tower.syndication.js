/**
 * 🗼 [V1.1] 控制塔分发死信队列与任务治理交互 (Tower Syndication Queue)
 * 职责：
 * 1. 刷新分发死信/重试队列数据；
 * 2. 单条任务重试与一键重试全部失败任务；
 * 3. 单条任务移出队列与一键清空全部失败任务。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
 */

(function () {
    // 刷新分发死信/重试队列数据
    window.refreshSyndicationQueue = async function () {
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
                    <button type="button" class="danger-btn" onclick="event.preventDefault(); event.stopPropagation(); window.deleteSyndicationTask('${t.rel_path}', '${t.target_id}')" style="padding:1px 5px; font-size:0.65rem; height:20px; cursor:pointer; background:rgba(239,68,68,0.1); border:1px solid #ef4444; color:#fca5a5; border-radius:4px; margin-left:4px;">删除</button>
                </td></tr>`;
        }).join('');
    };

    window.retrySyndicationTask = async function (relPath, targetId) {
        const res = await apiFetch('/api/governance/syndication/queue/retry', {
            method: 'POST', body: JSON.stringify({ rel_path: relPath, target_id: targetId })
        });
        if (res?.success) { showToast("🔄 分发重试任务已在后台拉起...", "info"); window.refreshSyndicationQueue(); }
        else showToast(`重试失败: ${res?.error || '未知错误'}`, "error");
    };

    window.retryAllSyndicationTasks = async function () {
        if (!confirm("是否确认一键重试所有失败的分发任务？")) return;
        const res = await apiFetch('/api/governance/syndication/queue/retry', { method: 'POST', body: JSON.stringify({}) });
        if (res?.success) { showToast("🔄 所有任务已重置并在后台拉起...", "success"); window.refreshSyndicationQueue(); }
        else showToast("重置失败", "error");
    };

    window.deleteSyndicationTask = async function (relPath, targetId) {
        if (!confirm(`确定丢弃 ${targetId} 渠道的分发任务？`)) return;
        const res = await apiFetch('/api/governance/syndication/queue/delete', {
            method: 'POST', body: JSON.stringify({ rel_path: relPath, target_id: targetId })
        });
        if (res?.success) { showToast("🗑️ 任务已移出队列", "info"); window.refreshSyndicationQueue(); }
    };

    window.clearFailedSyndicationTasks = async function () {
        if (!confirm("⚠️ 确定要清空所有 FAILED 状态的分发任务吗？")) return;
        const res = await apiFetch('/api/governance/syndication/queue/delete', { method: 'POST', body: JSON.stringify({}) });
        if (res?.success) { showToast("🗑️ 已清空失败任务", "success"); window.refreshSyndicationQueue(); }
    };
})();
