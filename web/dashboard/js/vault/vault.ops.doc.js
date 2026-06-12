/**
 * ⚡ [V87.6] Illacme Plenipes Vault Operations - Document Control Module (SOP-02 DECOUPLED HUB)
 * 职责：文稿新建与移动重命名模态框 UI 装配、文件夹智能感知与客户端输入门禁校验。
 */

// 📄 新建原稿物理交互处理器 (UI Hub)
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
            <div class="swal-drawer-form">
                <div class="drawer-item">
                    <label class="tiny-label">原稿标题</label>
                    <input id="swal-doc-title" class="setting-input" type="text" value="未命名原稿">
                </div>
                <div class="drawer-item">
                    <label class="tiny-label">物理保存路径 (相对于文库根目录)</label>
                    <input id="swal-doc-path" class="setting-input" type="text" value="${defaultPath}">
                </div>
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: '⚡ 确认创建',
        cancelButtonText: '取消',
        background: 'hsla(236, 37%, 8%, 0.95)',
        color: 'var(--text-bright, #ffffff)',
        backdrop: `var(--black-60)`,
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'primary-btn glow-btn',
            cancelButton: 'mini-btn'
        },
        didOpen: () => {
            const titleEl = document.getElementById('swal-doc-title');
            const pathEl = document.getElementById('swal-doc-path');
            if (!titleEl || !pathEl) return;
            
            let pathUserEdited = false;
            let debounceTimer = null;
            
            pathEl.addEventListener('input', () => {
                pathUserEdited = true;
            });
            
            titleEl.addEventListener('input', () => {
                const titleVal = titleEl.value;
                if (pathUserEdited) return;
                
                if (debounceTimer) clearTimeout(debounceTimer);
                debounceTimer = setTimeout(async () => {
                    if (pathUserEdited || !titleVal.trim()) return;
                    
                    try {
                        const res = await window.apiFetch('/api/vault/generate-slug', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ title: titleVal })
                        });
                        
                        if (res && res.success && res.slug && !pathUserEdited) {
                            const folder = window.vaultActiveFolder ? window.vaultActiveFolder + "/" : "";
                            pathEl.value = `${folder}${res.slug}.md`;
                        }
                    } catch (err) {
                        console.error("Failed to sync path from title:", err);
                    }
                }, 500);
            });
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
            // 📡 物理桥接：调用 Shard 分片执行 I/O 持久化
            if (window.VaultDocOps && typeof window.VaultDocOps.createDocumentRecord === 'function') {
                await window.VaultDocOps.createDocumentRecord(title, doc_id);
            }
        }
    });
};

// 🔄 原稿平滑重命名与移动交互控制器 (UI Hub)
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
        return `<option value="${folder}" ${isSelected} style="background: hsla(240, 10%, 7%, 1); color: var(--text-bright, #ffffff);">${label}</option>`;
    }).join('');

    Swal.fire({
        title: '🔄 重命名 / 移动原稿',
        html: `
            <div class="swal-move-container">
                <div class="swal-field-group">
                    <label>📁 目标文件夹</label>
                    <select id="swal-target-folder">
                        ${optionsHtml}
                    </select>
                </div>
                <div class="swal-field-group">
                    <label>📝 原稿文件名</label>
                    <input id="swal-target-filename" type="text" value="${currentFileName}">
                </div>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: '保存搬迁',
        cancelButtonText: '取消',
        background: 'hsla(236, 37%, 8%, 0.96)',
        color: 'var(--text-bright, #ffffff)',
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

            // 📡 物理桥接：调用 Shard 分片执行 API 提交、审计及视图自愈
            if (window.VaultDocOps && typeof window.VaultDocOps.moveDocumentRecord === 'function') {
                await window.VaultDocOps.moveDocumentRecord(docId, newPath);
            }
        }
    });
};
