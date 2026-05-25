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

            // 📡 物理桥接：调用 Shard 分片执行 API 提交、审计及视图自愈
            if (window.VaultDocOps && typeof window.VaultDocOps.moveDocumentRecord === 'function') {
                await window.VaultDocOps.moveDocumentRecord(docId, newPath);
            }
        }
    });
};
