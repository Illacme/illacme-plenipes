/**
 * ⚡ [V87.6] Illacme Plenipes Vault Operations - Directory Control Module
 * 职责：新建物理分配空目录。
 */

// 📁 [NEW] 新建物理目录交互处理器
window.triggerCreateDirectory = async () => {
    // 智能感知当前选中的文件夹路径作为前缀
    let defaultDir = "";
    if (window.vaultActiveFolder) {
        defaultDir = window.vaultActiveFolder + "/新目录";
    } else {
        defaultDir = "新目录";
    }

    Swal.fire({
        title: '📁 新建物理目录',
        html: `
            <div style="text-align: left; padding: 0 10px;">
                <div class="drawer-item">
                    <label class="tiny-label" style="display: block; margin-bottom: 5px; color: var(--accent-secondary); font-weight: bold;">物理保存路径 (相对于文库根目录)</label>
                    <input id="swal-dir-path" class="setting-input" type="text" value="${defaultDir}" style="width: 100%; box-sizing: border-box; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace;">
                </div>
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: '⚡ 确认创建',
        cancelButtonText: '取消',
        background: 'rgba(13, 14, 28, 0.95)',
        color: '#fff',
        backdrop: `rgba(0, 0, 0, 0.6)`,
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'primary-btn glow-btn',
            cancelButton: 'mini-btn'
        },
        preConfirm: () => {
            const path = document.getElementById('swal-dir-path').value.trim();
            if (!path) {
                Swal.showValidationMessage('物理保存路径不能为空！');
                return false;
            }
            return { dir_id: path };
        }
    }).then(async (result) => {
        if (result.isConfirmed && result.value) {
            const { dir_id } = result.value;
            
            if (typeof addAudit === 'function') {
                addAudit(`📁 正在向磁盘分配新物理目录 [${dir_id}]...`, "info");
            }
            
            try {
                const res = await apiFetch('/ledger/directory/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dir_id })
                });
                
                if (res && res.success) {
                    Swal.fire({
                        title: '目录创建成功',
                        text: `新物理目录已分配: ${res.dir_id}`,
                        icon: 'success',
                        toast: true,
                        position: 'top-end',
                        timer: 3000,
                        showConfirmButton: false
                    });
                    
                    if (typeof addAudit === 'function') {
                        addAudit(`✅ 新目录 ${res.dir_id} 已物理分配并同步目录树。`);
                    }
                    
                    // 重置左侧树折叠记忆以进行全量同步
                    window.vaultTreeInitialized = false;
                    
                    // 重新加载文稿列表
                    if (typeof loadVault === 'function') {
                        await loadVault(window.vaultCurrentQuery, window.vaultCurrentPage);
                    }
                } else {
                    Swal.fire({
                        title: '创建失败',
                        text: res ? res.error : '物理目录分配超时，请核验系统日志',
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
                console.error("Create directory error:", e);
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
