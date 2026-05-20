/**
 * ⚡ [V87.6] Illacme Plenipes Vault Operations - Document Control Module
 * 职责：文稿新建、资产重命名与搬迁。
 */

// 📄 [NEW] 新建原稿物理交互处理器
window.triggerCreateDocument = async () => {
    // 智能感知当前选中的文件夹路径
    let defaultPath = "";
    if (window.vaultActiveFolder) {
        defaultPath = window.vaultActiveFolder + "/未命名原稿.md";
    } else {
        defaultPath = "未命名原稿.md";
    }

    Swal.fire({
        title: '📂 新建物理原稿',
        html: `
            <div style="text-align: left; padding: 0 10px;">
                <div class="drawer-item" style="margin-bottom: 15px;">
                    <label class="tiny-label" style="display: block; margin-bottom: 5px; color: var(--accent-secondary); font-weight: bold;">原稿标题</label>
                    <input id="swal-doc-title" class="setting-input" type="text" value="未命名原稿" style="width: 100%; box-sizing: border-box; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px;">
                </div>
                <div class="drawer-item">
                    <label class="tiny-label" style="display: block; margin-bottom: 5px; color: var(--accent-secondary); font-weight: bold;">物理保存路径 (相对于文库根目录)</label>
                    <input id="swal-doc-path" class="setting-input" type="text" value="${defaultPath}" style="width: 100%; box-sizing: border-box; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace;">
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
            const title = document.getElementById('swal-doc-title').value.trim();
            const path = document.getElementById('swal-doc-path').value.trim();
            if (!path) {
                Swal.showValidationMessage('物理保存路径不能为空！');
                return false;
            }
            return { title, doc_id: path };
        }
    }).then(async (result) => {
        if (result.isConfirmed && result.value) {
            const { title, doc_id } = result.value;
            
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
        }
    });
};

// 🔄 [NEW] 原稿平滑重命名与移动交互控制器
window.triggerMoveDocument = async (docId) => {
    if (!docId) return;

    // 1. 获取当前笔记库内的物理文件夹列表以支持一键选择
    let directories = [];
    try {
        const listRes = await apiFetch('/api/vault/list');
        if (listRes && listRes.directories) {
            directories = listRes.directories;
        }
    } catch (e) {
        console.error("Fetch directories failed:", e);
    }

    // 2. 深度拆分当前的“父文件夹路径”与“纯文件名”
    const lastSlashIndex = docId.lastIndexOf('/');
    const currentFolder = lastSlashIndex !== -1 ? docId.substring(0, lastSlashIndex) : "";
    const currentFileName = lastSlashIndex !== -1 ? docId.substring(lastSlashIndex + 1) : docId;

    // 3. 构建高保真下拉菜单，无缝包含 Root (根目录) 
    const folderList = ["", ...directories.filter(d => d)];
    const uniqueFolders = Array.from(new Set(folderList));
    uniqueFolders.sort((a, b) => a.localeCompare(b));

    const optionsHtml = uniqueFolders.map(folder => {
        const isSelected = folder === currentFolder ? 'selected' : '';
        const label = folder ? `📁 ${folder}` : '🏠 Root (根目录)';
        return `<option value="${folder}" ${isSelected} style="background: #111; color: #fff;">${label}</option>`;
    }).join('');

    Swal.fire({
        title: '🔄 重命名 / 移动原稿',
        html: `
            <div class="swal-move-container" style="display: flex; gap: 12px; margin-top: 15px; text-align: left; flex-direction: column; font-family: inherit;">
                <div class="swal-field-group">
                    <label style="display: block; font-size: 0.85rem; opacity: 0.7; margin-bottom: 5px; color: #fff;">📁 目标文件夹</label>
                    <select id="swal-target-folder" style="width: 100%; box-sizing: border-box; padding: 10px; border-radius: 6px; background: rgba(255,255,255,0.06); color: #fff; border: 1px solid rgba(255,255,255,0.15); outline: none; font-size: 0.9rem; cursor: pointer;">
                        ${optionsHtml}
                    </select>
                </div>
                <div class="swal-field-group" style="margin-top: 5px;">
                    <label style="display: block; font-size: 0.85rem; opacity: 0.7; margin-bottom: 5px; color: #fff;">📝 原稿文件名</label>
                    <input id="swal-target-filename" type="text" value="${currentFileName}" style="width: 100%; box-sizing: border-box; padding: 10px; border-radius: 6px; background: rgba(255,255,255,0.06); color: #fff; border: 1px solid rgba(255,255,255,0.15); outline: none; font-size: 0.9rem;">
                </div>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: '保存搬迁',
        cancelButtonText: '取消',
        background: 'rgba(13, 14, 28, 0.96)',
        color: '#fff',
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'primary-btn glow-btn',
            cancelButton: 'mini-btn'
        },
        preConfirm: () => {
            const folder = document.getElementById('swal-target-folder').value;
            const filename = document.getElementById('swal-target-filename').value.trim();
            if (!filename) {
                Swal.showValidationMessage('原稿文件名不能为空');
                return false;
            }
            // 平滑拼接成最终相对路径
            return folder ? `${folder}/${filename}` : filename;
        }
    }).then(async (result) => {
        if (result.isConfirmed) {
            const newPath = result.value.trim();
            if (newPath === docId) return; // 路径没有变动，直接返回

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
};
