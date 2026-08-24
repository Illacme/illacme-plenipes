/**
 * 🚀 Illacme Plenipes Dashboard Core - Publish Abort & Republish Shard
 * 职责：全域同步熔断中止、终端状态与控制按钮归位、以及从终端触发重新发布。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

// 🛡️ [Abort] 全局中止同步交互逻辑
window.abortSync = async () => {
    if (!window.Swal) {
        // 退回降级保护机制
        const confirmAbort = confirm("确定要中止当前的全域同步任务吗？这会取消所有排队中的任务。");
        if (!confirmAbort) return;
        return window.executeAbortAction();
    }

    const result = await window.Swal.fire({
        title: '🛑 确定要中止同步吗？',
        text: '这会立即清空调度池任务并中止所有排队中的翻译/同步管线。',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '确定中止',
        cancelButtonText: '继续同步',
        confirmButtonColor: '#ff4d4d',
        cancelButtonColor: '#3085d6'
    });

    if (result.isConfirmed) {
        return window.executeAbortAction();
    }
};

window.executeAbortAction = async function () {
    if (typeof window.appendTerminalLog === 'function') {
        window.appendTerminalLog('🛑 正在向服务器发送中止指令...', '#ff4d4d');
    }

    const btn = document.getElementById('btn-terminal-abort');
    if (btn) {
        btn.disabled = true;
        btn.innerText = '正在中止...';
    }

    const res = await apiFetch('/api/system/sync/abort', { method: 'POST' });
    if (res && res.status === 'aborted') {
        if (typeof window.appendTerminalLog === 'function') {
            window.appendTerminalLog('🛑 中止指令已成功接收。流水线已物理熔断，后续所有大模型调用与分发已全部取消。', '#ff4d4d');
        }

        // 归位 UI 按钮与状态
        window._isPublishPreviewActive = false;
        const statusEl = document.getElementById('terminal-status');
        if (statusEl) {
            statusEl.innerText = 'ABORTED';
            statusEl.className = 'error';
        }
        const title = document.getElementById('terminal-title');
        if (title) {
            title.innerHTML = '⚡ 发布流水线已中止 <span class="version-tag tiny" style="background:rgba(255,77,77,0.15);color:#ff4d4d;border:1px solid rgba(255,77,77,0.4);margin-left:8px;">ABORTED</span>';
        }
        if (btn) btn.style.display = 'none';
        const closeBtn = document.getElementById('btn-terminal-close');
        if (closeBtn) closeBtn.style.display = 'none';
        const okBtn = document.getElementById('btn-terminal-ok');
        if (okBtn) {
            okBtn.style.display = 'inline-flex';
            okBtn.innerText = '关闭';
        }

        if (window.Swal) {
            window.Swal.fire({
                title: '同步已中止',
                text: '已成功中止全量同步并清空调度池任务。',
                icon: 'info',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
        }
    } else {
        if (window.Swal) {
            window.Swal.fire('发送失败', '中止同步指令发送失败或未被接受。', 'error');
        } else {
            alert("中止同步指令发送失败或未被接受。");
        }
        const btn = document.getElementById('btn-terminal-abort');
        if (btn) {
            btn.disabled = false;
            btn.innerText = '🛑 中止同步';
        }
    }
};

// 🚀 [V10.4] 从终端触发重新发布
window.republishFromTerminal = async function () {
    const republishBtn = document.getElementById('btn-terminal-republish');
    if (republishBtn) republishBtn.style.display = 'none';

    // 清理已完成状态，避免下次触发再次拦截
    const activeId = window.settingsData?._active_imprint || 'default';
    localStorage.removeItem('sync_completed');
    localStorage.removeItem(`sync_completed_${activeId}`);

    if (typeof window.appendTerminalLog === 'function') {
        window.appendTerminalLog('🔄 正在重新初始化全域同步流程...', '#ffaa00');
    }

    // 重新调用触发同步流程，传入 force = true, bypassCompletedCheck = true
    if (typeof window.triggerPublish === 'function') {
        await window.triggerPublish(true, true);
    }
};
