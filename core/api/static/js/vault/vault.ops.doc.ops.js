/**
 * ⚡ [V87.6] Illacme Plenipes Vault Operations - Document Operations Shard (SOP-02 DECOUPLED)
 * 职责：具体的 API 网络提报、账本审计日志记录、状态校验自愈及同步重载事务。
 */

window.VaultDocOps = window.VaultDocOps || {};

Object.assign(window.VaultDocOps, {
    /**
     * 💾 物理写入新资产至磁盘并重载视图状态
     */
    async createDocumentRecord(title, doc_id) {
        if (typeof addAudit === 'function') {
            addAudit(`📂 正在向磁盘写入新资产 [${doc_id}]...`, "info");
        }
        
        try {
            const res = await apiFetch('/ledger/document/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, doc_id })
            });
            
            if (res && res.success) {
                Swal.fire({
                    title: '原稿创建成功',
                    text: `新资产已物理写入: ${res.doc_id}`,
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });
                
                if (typeof addAudit === 'function') {
                    addAudit(`✅ 新资产 ${res.doc_id} 已成功写入磁道并注册入库。`);
                }
                
                // 重置左侧树折叠记忆以进行全量同步
                window.vaultTreeInitialized = false;
                
                // 重新加载文稿列表
                if (typeof loadVault === 'function') {
                    await loadVault(window.vaultCurrentQuery, window.vaultCurrentPage);
                }
                
                // 🌟 交互极致跃升：直接进入新创建文档的物理编辑器中！
                if (typeof openEditor === 'function') {
                    openEditor(res.doc_id);
                }
            } else {
                Swal.fire({
                    title: '创建失败',
                    text: res ? res.error : '物理写入超时，请核验系统日志',
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
            console.error("Create document error:", e);
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
    },

    /**
     * 🔄 物理搬迁/重命名磁盘原稿并实现状态对齐自愈
     */
    async moveDocumentRecord(docId, newPath) {
        if (typeof addAudit === 'function') {
            addAudit(`🔄 正在请求搬迁原稿 ${docId} 至新地址 ${newPath}...`, "info");
        }

        try {
            const res = await apiFetch('/ledger/document/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: docId, new_path: newPath })
            });

            if (res && res.success) {
                Swal.fire({
                    title: '原稿搬迁成功',
                    text: `文件已平滑重映射: ${res.new_path}`,
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });

                if (typeof addAudit === 'function') {
                    addAudit(`✅ 原稿已成功从 ${res.doc_id} 平滑搬迁至 ${res.new_path}。`);
                }

                // 🚀 心流对正：若当前正处于该文档的编辑态，自愈性更新编辑器的目标 ID 避免脑裂
                if (window.currentDocId === docId) {
                    window.currentDocId = res.new_path;
                    // 更新一下右侧编辑器标题或面包屑
                    const headerEl = document.querySelector('.editor-header h3');
                    if (headerEl) {
                        headerEl.innerText = `编辑中: ${res.new_path.split('/').pop()}`;
                    }
                }
                
                // 🚀 空间对正自愈：根据原稿搬迁后的新路径自动对齐
                const lastSlashOld = docId.lastIndexOf('/');
                const oldFolder = lastSlashOld !== -1 ? docId.substring(0, lastSlashOld) : "";
                const lastSlashNew = res.new_path.lastIndexOf('/');
                const newFolder = lastSlashNew !== -1 ? res.new_path.substring(0, lastSlashNew) : "";

                // 🛡️ 极客体验维系：如果只是在当前目录下原地重命名，绝对保持当前视图目录一动不动！
                // 仅当用户在弹窗中主动将文件搬迁 to 另一个不同的物理文件夹下时，我们才自动将视图切换至新目录追随展示
                if (oldFolder !== newFolder) {
                    window.vaultActiveFolder = newFolder;
                }
                
                // 🚀 清空模糊搜索词与重置分页，防止因搜索词残留过滤掉最新修改的原稿
                window.vaultCurrentQuery = "";
                window.vaultCurrentPage = 1;
                const searchInput = document.getElementById('vault-search-input');
                if (searchInput) {
                    searchInput.value = "";
                }

                // 重置目录树折叠状态记忆以进行全量同步
                window.vaultTreeInitialized = false;

                // 🚀 磁盘 I/O 缓冲自愈：延迟 150ms 避开物理磁盘与 SQLite 账本写入微秒级并发滞后
                await new Promise(resolve => setTimeout(resolve, 150));

                // 重新加载原稿列表
                if (typeof loadVault === 'function') {
                    await loadVault("", 1);
                }
            } else {
                Swal.fire({
                    title: '原稿搬迁失败',
                    text: res ? res.error : '原稿物理重映射超时，请核验系统日志',
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
            console.error("Move document error:", e);
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
