/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics & Service Action Module
 * 职责：系统上下文状态诊断加载、Onboarding 未初始化友好引导、预览服务治理长效命令投递与 Onboarding 进程调控。
 */

window.triggerSystemGC = async () => {
    const btn = document.getElementById('btn-system-gc');
    if (btn) {
        btn.disabled = true;
        btn.innerText = "🧹 清洗中...";
    }

    addAudit("🧹 正在发起 [清洗路由] 指令，物理回收失效资产...", "info");

    try {
        const res = await apiFetch('/api/governance/gc', { method: 'POST' });
        if (res && res.status === 'success') {
            addAudit("✅ 清洗路由成功：失效的幽灵路由与冗余文件回收完毕！", "success");
            Swal.fire({
                title: '🧹 清洗路由成功',
                text: '系统已安全唤醒清道夫 Janitor 引擎，彻底回收了出版版图内已失效的幽灵路由、过期页面和冗余垃圾资产。',
                icon: 'success',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            const msg = (res && res.message) ? res.message : '未知异常';
            addAudit(`🛑 清洗路由失败: ${msg}`, "error");
            Swal.fire({
                title: '🚨 清洗路由失败',
                text: `清道夫引擎响应异常: ${msg}`,
                icon: 'error',
                confirmButtonColor: 'var(--accent-primary)'
            });
        }
    } catch (e) {
        addAudit(`🛑 清洗路由请求崩溃: ${e.message || e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "🧹 清洗路由";
        }
    }
};

window.copyVaultPath = async (overridePath) => {
    let rawPath = overridePath;
    if (!rawPath || typeof rawPath !== 'string') {
        const el = document.getElementById('sidebar-vault-display');
        if (el) {
            rawPath = el.dataset.fullPath || el.innerText;
        }
    }
    
    if (!rawPath || rawPath === 'LOADING...' || rawPath === '-' || rawPath === '默认全局文库') return;
    
    let success = false;
    
    // 1. 尝试现代安全上下文 Clipboard API
    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
        try {
            await navigator.clipboard.writeText(rawPath);
            success = true;
        } catch (e) {
            console.warn("Modern clipboard API failed, attempting fallback:", e);
        }
    }
    
    // 2. 降级走 execCommand
    if (!success) {
        try {
            const textArea = document.createElement("textarea");
            textArea.value = rawPath;
            textArea.style.position = "fixed";
            textArea.style.opacity = "0";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            success = document.execCommand('copy');
            document.body.removeChild(textArea);
        } catch (e) {
            console.error("Fallback execCommand failed:", e);
        }
    }
    
    if (success) {
        if (typeof showNotification === 'function') {
            showNotification(`📋 物理原稿文库路径已复制到剪贴板！`, 'success');
        } else if (typeof addAudit === 'function') {
            addAudit(`📋 已复制文库路径: ${rawPath}`, "success");
        }
        Swal.fire({
            toast: true,
            position: 'top',
            icon: 'success',
            title: '绝对路径已复制',
            showConfirmButton: false,
            timer: 1500
        });
    } else {
        addAudit("🛑 复制物理路径失败：受浏览器安全环境限制", "error");
        Swal.fire({
            title: '📋 复制未成功',
            text: `由于当前浏览器安全策略限制，请手动复制文库绝对路径：\n${rawPath}`,
            icon: 'warning',
            confirmButtonColor: 'var(--accent-primary)'
        });
    }
};
