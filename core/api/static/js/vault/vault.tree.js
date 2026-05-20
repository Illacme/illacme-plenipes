/**
 * 📁 [V87.5] Illacme Plenipes Obsidian-style Directory Tree Module
 * 职责：文稿仓库 Obsidian 风格目录树解析、高亮交互与侧边栏遥测记忆控制。
 */

// 📁 [V87.5] Obsidian 风格目录树解析与渲染算法
window.initializeVaultTree = async () => {
    try {
        const res = await apiFetch('/api/vault/list');
        if (res && res.manuscripts) {
            window.renderVaultTree(res.manuscripts, res.directories || []);
            window.vaultTreeInitialized = true;
        }
    } catch (e) {
        console.error("Initialize vault tree error:", e);
    }
};

window.renderVaultTree = (manuscripts, directories = []) => {
    const treeEl = document.getElementById('vault-tree');
    if (!treeEl) return;

    const paths = manuscripts.map(m => m.path || m.rel_path);
    const tree = { name: "Root", path: "", children: {} };

    // 1. 预先填充物理真实子目录结构，支持空目录展示
    directories.forEach(dirPath => {
        if (!dirPath) return;
        const parts = dirPath.split('/');
        let current = tree;
        let currentPath = "";
        parts.forEach(folder => {
            currentPath = currentPath ? `${currentPath}/${folder}` : folder;
            if (!current.children[folder]) {
                current.children[folder] = {
                    name: folder,
                    path: currentPath,
                    children: {}
                };
            }
            current = current.children[folder];
        });
    });

    // 2. 根据原稿路径补充推演目录树节点
    paths.forEach(p => {
        if (!p) return;
        const parts = p.split('/');
        if (parts.length <= 1) return; // 根目录文件
        const folders = parts.slice(0, -1);
        let current = tree;
        let currentPath = "";
        folders.forEach(folder => {
            currentPath = currentPath ? `${currentPath}/${folder}` : folder;
            if (!current.children[folder]) {
                current.children[folder] = {
                    name: folder,
                    path: currentPath,
                    children: {}
                };
            }
            current = current.children[folder];
        });
    });

    const isAllActive = !window.vaultActiveFolder;

    let html = `
        <div class="tree-root-item ${isAllActive ? 'active' : ''}" onclick="window.selectVaultFolder('', event)">
            <span class="tree-icon">🏠</span>
            <span class="tree-label">全部原稿</span>
        </div>
        <div class="tree-divider" style="margin: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);"></div>
    `;

    // 递归子节点渲染器
    function renderNode(node, depth = 0) {
        const childrenKeys = Object.keys(node.children);
        let html = '';
        childrenKeys.sort();

        childrenKeys.forEach(key => {
            const child = node.children[key];
            const hasChildren = Object.keys(child.children).length > 0;
            const indent = depth * 12; // 层级缩进
            const isActive = window.vaultActiveFolder === child.path;

            html += `
                <div class="tree-folder" data-path="${child.path}">
                    <div class="tree-folder-header ${isActive ? 'active' : ''}" style="padding-left: ${indent}px;" onclick="window.selectVaultFolder('${child.path}', event)">
                        <span class="tree-arrow ${hasChildren ? 'has-children' : 'leaf'} expanded" onclick="window.toggleVaultFolder(this, event)">▶</span>
                        <span class="tree-icon">📁</span>
                        <span class="tree-label">${child.name}</span>
                    </div>
                    <div class="tree-folder-children" style="display: block;">
                        ${renderNode(child, depth + 1)}
                    </div>
                </div>
            `;
        });
        return html;
    }

    html += renderNode(tree, 0);
    treeEl.innerHTML = html;
};

window.toggleVaultFolder = (element, event) => {
    if (event) event.stopPropagation();
    const folderEl = element.closest('.tree-folder');
    const childrenEl = folderEl.querySelector('.tree-folder-children');
    const arrowEl = folderEl.querySelector('.tree-arrow');
    if (childrenEl.style.display === 'none') {
        childrenEl.style.display = 'block';
        arrowEl.classList.add('expanded');
    } else {
        childrenEl.style.display = 'none';
        arrowEl.classList.remove('expanded');
    }
};

window.selectVaultFolder = (path, event) => {
    if (event) event.stopPropagation();
    window.vaultActiveFolder = path;
    window.vaultCurrentPage = 1; // 切换目录时重置分页

    // 高亮状态同步切换，防止树重新渲染导致折叠状态丢失
    const headers = document.querySelectorAll('.tree-folder-header, .tree-root-item');
    headers.forEach(h => h.classList.remove('active'));

    if (path === "") {
        const rootItem = document.querySelector('.tree-root-item');
        if (rootItem) rootItem.classList.add('active');
    } else {
        const folderEl = document.querySelector(`.tree-folder[data-path="${path}"] > .tree-folder-header`);
        if (folderEl) {
            folderEl.classList.add('active');
            // 🚀 [V87.6] 点击整行高亮时，同时执行折叠/展开的切换，提升在大屏/Pad 上的易用性
            const arrowEl = folderEl.querySelector('.tree-arrow');
            if (arrowEl && arrowEl.classList.contains('has-children')) {
                window.toggleVaultFolder(arrowEl);
            }
        }
    }

    // 🗑️ 上下文自适应目录删除按钮控制
    const delDirBtn = document.getElementById('btn-delete-directory');
    if (delDirBtn) {
        if (path === "") {
            delDirBtn.style.display = 'none';
        } else {
            delDirBtn.style.display = 'inline-block';
        }
    }

    window.loadVault();
};

window.toggleVaultSidebar = () => {
    const sidebar = document.getElementById('vault-tree-sidebar');
    const btn = document.getElementById('toggle-vault-sidebar-btn');
    if (!sidebar) return;

    const isCollapsed = sidebar.classList.toggle('collapsed');
    if (btn) {
        btn.innerHTML = isCollapsed ? '📑 展开侧栏' : '📑 隐藏侧栏';
    }
    localStorage.setItem('vaultSidebarCollapsed', isCollapsed ? 'true' : 'false');
};

window.vaultTreeAllExpanded = true; // 默认所有目录树节点为展开状态

window.toggleAllVaultFolders = () => {
    const btn = document.getElementById('tree-toggle-all-btn');
    const childrenEls = document.querySelectorAll('.tree-folder-children');
    const arrowEls = document.querySelectorAll('.tree-arrow.has-children');

    if (window.vaultTreeAllExpanded) {
        // 瞬间折叠全部
        childrenEls.forEach(el => el.style.display = 'none');
        arrowEls.forEach(el => el.classList.remove('expanded'));
        window.vaultTreeAllExpanded = false;
        if (btn) {
            btn.innerHTML = '📂';
            btn.title = '展开全部目录';
        }
    } else {
        // 瞬间展开全部
        childrenEls.forEach(el => el.style.display = 'block');
        arrowEls.forEach(el => el.classList.add('expanded'));
        window.vaultTreeAllExpanded = true;
        if (btn) {
            btn.innerHTML = '📁';
            btn.title = '折叠全部目录';
        }
    }
};
