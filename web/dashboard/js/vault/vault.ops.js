/**
 * ⚡ [V87.6] Illacme Plenipes Vault Operations & Engines Control Module
 * 职责：预览引擎控制、资产物理销毁、以及安全物理删除空目录。
 */

window.toggleThemeLab = async () => {
    console.info("🧪 [Engine] 尝试切换预览引擎状态...");
    addAudit("🧪 [Engine] 正在切换实时预览引擎状态...", "info");
    const res = await apiFetch('/api/vault/toggle-lab', { method: 'POST' });
    
    if (res && res.success) {
        console.log("✅ 引擎状态切换成功:", res.is_active);
        Swal.fire({
            title: res.is_active ? '预览引擎已启动' : '预览引擎已关闭',
            text: res.is_active ? '已进入实时渲染模式，物理变动将立即生效。' : '已切换回静态快照预览模式。',
            icon: 'success',
            toast: true,
            position: 'top-end',
            timer: 3000,
            showConfirmButton: false
        });
        // 刷新状态 (延迟 800ms 确保后端状态已持久化)
        setTimeout(() => openVaultDrawer(window.currentDocId), 800);
    }
};

window.confirmPhysicalDelete = () => {
    Swal.fire({
        title: '确认撤销该资产吗？',
        text: "这将物理抹除磁盘上的源文件及其所有出版产物，不可恢复！",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ff4d4d',
        confirmButtonText: '🔥 确认销毁',
        cancelButtonText: '取消',
        position: 'top-end',
        backdrop: false,
        customClass: {
            popup: 'swal2-sidebar-confirm'
        }
    }).then(async (result) => {
        if (result.isConfirmed) {
            addAudit(`🗑️ 正在物理销毁资产 [${window.currentDocId}]...`, "warning");
            const res = await apiFetch(`/api/vault/destroy/${encodeURIComponent(window.currentDocId)}`, { method: 'DELETE' });
            
            if (res && res.success) {
                Swal.fire({
                    title: '资产已销毁',
                    text: res.message,
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });
                closeVaultDrawer();
                window.vaultTreeInitialized = false; // 重置树以进行全量物理同步
                if (typeof window.loadVault === 'function') {
                    window.loadVault();
                } else if (typeof loadVault === 'function') {
                    loadVault();
                }
            } else {
                Swal.fire({
                    title: '销毁失败',
                    text: res ? res.message : '未知错误',
                    icon: 'error',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });
            }
        }
    });
};

// 🗑️ [NEW] 安全物理删除空目录交互处理器
window.triggerDeleteDirectory = async () => {
    const targetDir = window.vaultActiveFolder;
    if (!targetDir) {
        Swal.fire({
            title: '未选中目录',
            text: '请先在左侧目录树中选择需要删除的空目录',
            icon: 'warning',
            background: 'rgba(13, 14, 28, 0.95)',
            color: '#fff',
            customClass: {
                popup: 'glass-panel',
                confirmButton: 'primary-btn'
            }
        });
        return;
    }

    Swal.fire({
        title: '⚠️ 确认物理删除目录吗？',
        text: `您即将物理销毁选中的空文件夹 [${targetDir}]。此操作无法撤销。`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '🗑️ 确认物理删除',
        cancelButtonText: '取消',
        background: 'rgba(13, 14, 28, 0.95)',
        color: '#fff',
        backdrop: `rgba(0, 0, 0, 0.6)`,
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'primary-btn',
            cancelButton: 'mini-btn'
        }
    }).then(async (result) => {
        if (result.isConfirmed) {
            if (typeof addAudit === 'function') {
                addAudit(`🗑️ 正在尝试从物理磁盘注销空目录 [${targetDir}]...`, "warning");
            }
            
            try {
                const res = await apiFetch('/ledger/directory/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dir_id: targetDir })
                });
                
                if (res && res.success) {
                    Swal.fire({
                        title: '目录销毁成功',
                        text: `物理空目录已清理: ${res.dir_id}`,
                        icon: 'success',
                        toast: true,
                        position: 'top-end',
                        timer: 3000,
                        showConfirmButton: false
                    });
                    
                    if (typeof addAudit === 'function') {
                        addAudit(`✅ 空目录 ${res.dir_id} 已物理注销并成功移除。`);
                    }
                    
                    // 重置激活的目录至全部原稿
                    window.vaultActiveFolder = '';
                    
                    // 隐藏删除目录按钮
                    const delDirBtn = document.getElementById('btn-delete-directory');
                    if (delDirBtn) delDirBtn.style.display = 'none';

                    // 重置左侧树折叠记忆以进行全量同步
                    window.vaultTreeInitialized = false;
                    
                    // 重新加载文稿列表
                    if (typeof loadVault === 'function') {
                        await loadVault(window.vaultCurrentQuery, window.vaultCurrentPage);
                    }
                } else {
                    Swal.fire({
                        title: '物理销毁失败',
                        text: res ? res.error : '物理目录销毁超时，请核验系统日志',
                        icon: 'error',
                        background: 'rgba(13, 14, 28, 0.95)',
                        color: '#fff',
                        customClass: {
                            popup: 'glass-panel',
                            confirmButton: 'primary-btn glow-btn'
                        }
                    });
                }
            } catch (e) {
                console.error("Delete directory error:", e);
                Swal.fire({
                    title: '系统异常',
                    text: e.message,
                    icon: 'error',
                    background: 'rgba(13, 14, 28, 0.95)',
                    color: '#fff',
                    customClass: {
                        popup: 'glass-panel',
                        confirmButton: 'primary-btn'
                    }
                });
            }
        }
    });
};
