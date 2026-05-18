/**
 * 📂 [V55.0] Illacme Plenipes Vault & Editor Module
 * 职责：稿件仓库管理、元数据治理与物理原件编辑。
 */

// 1. 状态矩阵
window.currentDocId = null;
window.activeDocId = null;
window.vaultSearchTimeout = null;
window.vaultCurrentPage = 1;
window.vaultCurrentQuery = '';
window.vaultPageSize = 20;
window.vaultActiveFolder = '';
window.vaultTreeInitialized = false;

// 📁 [V87.5] Obsidian 风格目录树解析与渲染算法
window.initializeVaultTree = async () => {
    try {
        const res = await apiFetch('/api/vault/list');
        if (res && res.manuscripts) {
            window.renderVaultTree(res.manuscripts);
            window.vaultTreeInitialized = true;
        }
    } catch (e) {
        console.error("Initialize vault tree error:", e);
    }
};

window.renderVaultTree = (manuscripts) => {
    const treeEl = document.getElementById('vault-tree');
    if (!treeEl) return;

    const paths = manuscripts.map(m => m.path || m.rel_path);
    const tree = { name: "Root", path: "", children: {} };

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

    window.loadVault();
};

window.toggleVaultSidebar = () => {
    const sidebar = document.getElementById('vault-tree-sidebar');
    const btn = document.getElementById('toggle-vault-sidebar-btn');
    if (!sidebar) return;

    const isCollapsed = sidebar.classList.toggle('collapsed');
    if (btn) {
        btn.innerHTML = isCollapsed ? '▶ 展开侧栏' : '◀ 隐藏侧栏';
    }
    localStorage.setItem('vaultSidebarCollapsed', isCollapsed ? 'true' : 'false');
};

window.expandAllVaultFolders = () => {
    const childrenEls = document.querySelectorAll('.tree-folder-children');
    const arrowEls = document.querySelectorAll('.tree-arrow.has-children');
    childrenEls.forEach(el => el.style.display = 'block');
    arrowEls.forEach(el => el.classList.add('expanded'));
};

window.collapseAllVaultFolders = () => {
    const childrenEls = document.querySelectorAll('.tree-folder-children');
    const arrowEls = document.querySelectorAll('.tree-arrow.has-children');
    childrenEls.forEach(el => el.style.display = 'none');
    arrowEls.forEach(el => el.classList.remove('expanded'));
};

// 2. 稿件仓库加载器
window.loadVault = async (query = null, page = null) => {
    if (query !== null) {
        window.vaultCurrentQuery = query;
        if (page === null) window.vaultCurrentPage = 1; // 新搜索默认回到第一页
    }
    if (page !== null) window.vaultCurrentPage = page;

    // 🚀 [V87.6] 维持侧边栏折叠/展开状态记忆对正
    const sidebar = document.getElementById('vault-tree-sidebar');
    const toggleBtn = document.getElementById('toggle-vault-sidebar-btn');
    if (sidebar && toggleBtn) {
        const wasCollapsed = localStorage.getItem('vaultSidebarCollapsed') === 'true';
        if (wasCollapsed) {
            sidebar.classList.add('collapsed');
            toggleBtn.innerHTML = '▶ 展开侧栏';
        } else {
            sidebar.classList.remove('collapsed');
            toggleBtn.innerHTML = '◀ 隐藏侧栏';
        }
    }

    if (!window.vaultTreeInitialized) {
        window.initializeVaultTree();
    }

    const listEl = document.getElementById('vault-list');
    if (!listEl) return;

    // 预更新分页 UI
    const pageInfo = document.getElementById('vault-page-info');
    if (pageInfo) pageInfo.innerText = `第 ${window.vaultCurrentPage} 页`;
    const prevBtn = document.getElementById('vault-prev-btn');
    const nextBtn = document.getElementById('vault-next-btn');
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;

    listEl.innerHTML = Array(5).fill(0).map(() => `
        <tr>
            <td><div class="skeleton" style="width: 140px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 200px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 60px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 80px; height: 30px;"></div></td>
        </tr>
    `).join('');

    try {
        // 🚀 [V74.8] 物理检索：利用后端索引引擎进行全量过滤，带分页与文件夹过滤参数
        const res = await apiFetch(`/api/vault/search?q=${encodeURIComponent(window.vaultCurrentQuery)}&limit=${window.vaultPageSize}&page=${window.vaultCurrentPage}&folder=${encodeURIComponent(window.vaultActiveFolder || '')}`);
        
        if (!res || !res.items) {
            listEl.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:2rem; opacity:0.5;">⚠️ 仓库扫描失败，请核验物理链路。</td></tr>';
            return;
        }

        const manuscripts = res.items;

        // 更新分页按钮可用性
        if (prevBtn) prevBtn.disabled = window.vaultCurrentPage <= 1;
        if (nextBtn) nextBtn.disabled = manuscripts.length < window.vaultPageSize;

        if (manuscripts.length === 0) {
            listEl.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:2rem; opacity:0.5;">📭 仓库空空如也，未发现合规稿件。</td></tr>';
            return;
        }

        listEl.innerHTML = manuscripts.map(m => {
            const wc = (m.seo_data && m.seo_data.word_count) ? m.seo_data.word_count : 0;
            return `
            <tr>
                <td><div style="font-weight:600; color:var(--text-bright);">${m.title}</div>${m.slug && m.slug !== 'null' ? `<div style="font-size:0.7rem; opacity:0.4;">/${m.slug}</div>` : ''}</td>
                <td><code class="path-tag" title="${m.rel_path}">${m.rel_path.length > 40 ? '...' + m.rel_path.slice(-37) : m.rel_path}</code></td>
                <td style="text-align: center;"><span class="mono">${wc.toLocaleString()}</span></td>
                <td>
                    <div style="display:flex; gap:8px;">
                        <button class="mini-action-btn" title="快速编辑" onclick="openEditor('${m.rel_path}')">📝</button>
                        <button class="mini-action-btn" title="分发详情" onclick="openVaultDrawer('${m.rel_path}')">⚙️</button>
                    </div>
                </td>
            </tr>
            `;
        }).join('');
    } catch (e) {
        console.error("Vault load error:", e);
        listEl.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:2rem; color:var(--accent-primary);">🚨 物理链路异常: ${e.message}</td></tr>`;
    }
};

window.changeVaultPage = (delta) => {
    const newPage = window.vaultCurrentPage + delta;
    if (newPage < 1) return;
    window.loadVault(null, newPage);
};

window.closeVaultDrawer = () => {
    document.getElementById('vault-drawer').style.display = 'none';
};

// 3. 📡 分发枢纽 (Dispatch Hub) 监控引擎
window.openVaultDrawer = async (relPath) => {
    window.currentDocId = relPath;
    const drawer = document.getElementById('vault-drawer');
    const hubDocId = document.getElementById('hub-doc-id');
    const matrixContainer = document.getElementById('hub-sync-matrix');

    if (hubDocId) hubDocId.innerText = relPath.toUpperCase();
    drawer.style.display = 'flex';

    // 🚀 [V68.0] 请求 Mock 契约接口
    const data = await apiFetch(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
    if (!data) return;

    // 渲染分发矩阵
    if (matrixContainer) {
        matrixContainer.innerHTML = data.sync_matrix.map(item => `
            <div class="matrix-item status-${item.status}">
                <div class="m-info">
                    <span class="m-locale">${item.locale}</span>
                    <span class="m-status-text">${item.status.toUpperCase()}</span>
                </div>
                <div class="m-meta">
                    <span class="m-time">${item.last_sync}</span>
                    ${item.tokens ? `<span class="m-tokens">${item.tokens} tokens</span>` : ''}
                </div>
                ${item.status === 'syncing' ? `
                    <div class="mini-progress"><div class="fill" style="width:${item.progress}%"></div></div>
                ` : ''}
                ${item.status === 'published' ? `
                    <a href="${item.artifact_url}" target="_blank" class="preview-link">👁️ 预览产物</a>
                ` : ''}
                ${item.status === 'failed' ? `
                    <div class="error-msg">${item.reason}</div>
                ` : ''}
            </div>
        `).join('');
    }

    // 填充遥测数据
    document.getElementById('hub-cost').innerText = data.telemetry.total_cost;
    document.getElementById('hub-node').innerText = data.telemetry.node;
    
    // 🚀 [V68.0] 环境自感应：实验室模式
    const labBadge = document.getElementById('hub-lab-badge');
    const labBtn = document.getElementById('btn-toggle-lab');
    if (data.environment.is_lab_active) {
        labBadge.innerText = "ACTIVE (LIVE)";
        labBadge.className = "badge active";
        labBtn.innerText = "🛑 关闭实时预览引擎";
        labBtn.className = "engine-btn stop-mode";
        // 升级所有预览链接为 Live 模式
        document.querySelectorAll('.preview-link').forEach(link => {
            link.innerText = "⚡ 实时引擎预览 (LIVE)";
            link.classList.add('live-pulse');
        });
    } else {
        labBadge.innerText = "OFFLINE";
        labBadge.className = "badge";
        labBtn.innerText = "🔌 启动实时预览引擎 (LIVE PREVIEW)";
        labBtn.className = "engine-btn start-mode";
    }

    const auditBadge = document.getElementById('hub-audit-status');
    if (auditBadge) {
        auditBadge.innerText = `AUDIT: ${data.telemetry.last_audit}`;
        auditBadge.className = `audit-badge ${data.telemetry.last_audit.toLowerCase()}`;
    }
};

window.triggerReDispatch = async (scope) => {
    if (!window.currentDocId) return;
    addAudit(`🚀 [Dispatch] 手动触发重调度请求: ${scope}`, "info");
    
    const res = await apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(window.currentDocId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locales: scope === 'all' ? [] : [scope], force: true })
    });

    if (res && res.success) {
        console.info(`✅ [Dispatch] 重调度指令已由管线受理: ${window.currentDocId}`);
        Swal.fire({
            title: '重调度已受理',
            text: res.message,
            icon: 'success',
            toast: true,
            position: 'top-end',
            timer: 3000,
            showConfirmButton: false
        });
        // 刷新状态
        setTimeout(() => openVaultDrawer(window.currentDocId), 1000);
    }
};

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


// 4. 全量物理编辑器 (Modal)
window.openEditor = async (docId) => {
    window.activeDocId = docId;
    const modal = document.getElementById('editor-modal');
    const body = document.getElementById('editor-body');
    const title = document.getElementById('editor-title');
    const mTitle = document.getElementById('editor-meta-title');
    const mSlug = document.getElementById('editor-meta-slug');

    title.innerText = "EXTRACTING PHYSICAL ASSET...";
    if (body) body.placeholder = "等待数据载入...";
    const status = document.getElementById('save-status');
    if (status) status.innerText = ""; // 🚀 状态对齐：清除上一个文档的残留状态
    modal.style.display = 'flex';

    const doc = await apiFetch(`/ledger/document/${encodeURIComponent(docId)}`);
    if (doc) {
        title.innerText = `EDITOR: ${doc.title || docId}`;
        if (body) {
            body.placeholder = "在此处输入文稿内容（支持 Markdown 语法）...";
            body.value = doc.content || "";
        }
        if (mTitle) mTitle.value = doc.title || "";
        if (mSlug) mSlug.value = doc.slug || "";
        
        // 🚀 [V68.0] 动态元数据注入
        renderDynamicMetadata(doc.frontmatter || {});
        
        // 🌓 [V87.0] 初始化编辑器模式为源码模式，并预渲染预览内容
        setEditorMode('source');
        updateEditorPreview();
        initSyncScroll();
    }
};

window.renderDynamicMetadata = (metadata) => {
    const container = document.getElementById('dynamic-metadata-container');
    if (!container) return;
    container.innerHTML = "";

    // 过滤掉已经在上方固定显示的 title 和 slug
    const keys = Object.keys(metadata).filter(k => k !== 'title' && k !== 'slug');
    
    if (keys.length === 0) {
        container.innerHTML = `<div style="font-size:0.7rem; opacity:0.3; text-align:center; padding:10px;">(未发现扩展元数据)</div>`;
        return;
    }

    keys.forEach(key => {
        const val = metadata[key];
        const item = document.createElement('div');
        item.className = 'drawer-item';
        
        // 渲染项结构标头
        item.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <label class="tiny-label">${key.toUpperCase()}</label>
                <button class="mini-action-btn" onclick="this.parentElement.parentElement.remove()" title="删除该字段" style="font-size:0.6rem; padding:2px 5px; opacity:0.5;">×</button>
            </div>
        `;
        
        // 探测是否为日期/时间字段（包含 date, time, created, updated 或符合 ISO 日期时间正则）
        const isDateField = key.toLowerCase().includes('date') || 
                            key.toLowerCase().includes('time') || 
                            key.toLowerCase().includes('created') || 
                            key.toLowerCase().includes('updated') ||
                            (typeof val === 'string' && /^\d{4}-\d{2}-\d{2}(T|\s)\d{2}:\d{2}/.test(val));

        // 采用编程式属性注入，完美防范 JSON 字符串单双引号及特殊符号引起的 HTML 解析截断与混淆
        if (typeof val === 'boolean') {
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'metadata-input';
            input.setAttribute('data-key', key);
            input.checked = val;
            input.style.width = 'auto';
            input.style.marginLeft = '10px';
            item.firstElementChild.appendChild(input);
        } else if (isDateField) {
            // 🚀 [V87.3] 尊贵日期微端交互：采用 HTML5 本地化日期选择器
            const input = document.createElement('input');
            input.type = 'datetime-local';
            input.className = 'metadata-input setting-input';
            input.setAttribute('data-key', key);
            input.setAttribute('data-is-date', 'true');
            
            // 将输入值标准化为 YYYY-MM-DDTHH:mm 格式以加载到 datetime-local 控件中
            let displayVal = "";
            if (val) {
                const dateObj = new Date(val);
                if (!isNaN(dateObj.getTime())) {
                    const y = dateObj.getFullYear();
                    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
                    const d = String(dateObj.getDate()).padStart(2, '0');
                    const hh = String(dateObj.getHours()).padStart(2, '0');
                    const mm = String(dateObj.getMinutes()).padStart(2, '0');
                    displayVal = `${y}-${m}-${d}T${hh}:${mm}`;
                } else {
                    // 若日期不可解析，则作为普通字符串回退显示
                    displayVal = val;
                }
            }
            input.value = displayVal;
            item.appendChild(input);
        } else {
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'metadata-input setting-input';
            input.setAttribute('data-key', key);
            
            if (Array.isArray(val)) {
                // 检查数组中是否包含对象类型（复杂结构，如 HREFLANGS）
                const hasObject = val.some(item => item !== null && typeof item === 'object');
                if (hasObject) {
                    input.value = JSON.stringify(val);
                    input.placeholder = "JSON 数组格式";
                } else {
                    input.value = val.join(', ');
                    input.placeholder = "逗号分隔列表";
                }
            } else if (val !== null && typeof val === 'object') {
                // 复杂键值对结构（如 dict）
                input.value = JSON.stringify(val);
                input.placeholder = "JSON 对象格式";
            } else {
                input.value = val || '';
            }
            item.appendChild(input);
        }
        
        container.appendChild(item);
    });
};

window.setEditorMode = (mode) => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    const btnSource = document.getElementById('mode-source');
    const btnPreview = document.getElementById('mode-preview');
    const btnSplit = document.getElementById('mode-split');

    if (!body || !preview) return;

    [btnSource, btnPreview, btnSplit].forEach(b => b?.classList.remove('active'));

    if (mode === 'source') {
        body.style.display = 'block';
        preview.style.display = 'none';
        btnSource?.classList.add('active');
    } else if (mode === 'preview') {
        body.style.display = 'none';
        preview.style.display = 'block';
        btnPreview?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    } else if (mode === 'split') {
        body.style.display = 'block';
        preview.style.display = 'block';
        btnSplit?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    }
};

window.updateEditorPreview = () => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    if (!body || !preview) return;

    let mdContent = body.value;

    // 1. 物理资源解析：替换 Obsidian 双链图片 ![[image.png]] 或 ![[image.png|width]]
    mdContent = mdContent.replace(/!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, extra) => {
        const cleanPath = decodeURIComponent(path.trim());
        const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
        const alt = cleanPath;
        if (extra && !isNaN(extra.trim())) {
            return `<img src="${url}" alt="${alt}" width="${extra.trim()}" />`;
        }
        return `![${alt}](${url})`;
    });

    // 2. 物理资源解析：替换 Obsidian 双链普通附件 [[file.pdf]] 或 [[file.pdf|display]] (排除了带 ! 前缀的情况)
    mdContent = mdContent.replace(/(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, path, display) => {
        const cleanPath = decodeURIComponent(path.trim());
        const displayName = (display || cleanPath).trim();
        const extMatch = cleanPath.match(/\.([a-zA-Z0-9]+)$/);
        if (extMatch && !['md', 'mdx', 'markdown'].includes(extMatch[1].toLowerCase())) {
            const url = `/api/vault-assets/${encodeURIComponent(cleanPath)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
            return `<a href="${url}" target="_blank" class="attachment-link">📎 ${displayName}</a>`;
        } else {
            const cleanDocPath = cleanPath.replace(/\.mdx?$/, '');
            return `<a href="#" onclick="openEditorFromPreview('${cleanDocPath.replace(/'/g, "\\'")}', event)" class="wiki-doc-link">📄 ${displayName}</a>`;
        }
    });

    // 3. 物理资源解析：替换标准 Markdown 图片 ![alt](path)
    mdContent = mdContent.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('data:')) {
            return match;
        }
        const decodedUrl = decodeURIComponent(cleanUrl);
        const resolvedUrl = `/api/vault-assets/${encodeURIComponent(decodedUrl)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
        return `![${alt}](${resolvedUrl})`;
    });

    // 4. 物理资源解析：替换标准 Markdown 链接 [text](path) (排除了带 ! 前缀的图片链接，防止二次污染)
    mdContent = mdContent.replace(/(?<!\!)\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('data:') || cleanUrl.startsWith('#')) {
            return match;
        }
        const decodedUrl = decodeURIComponent(cleanUrl);
        const extMatch = decodedUrl.match(/\.([a-zA-Z0-9]+)$/);
        if (extMatch && !['md', 'mdx', 'markdown'].includes(extMatch[1].toLowerCase())) {
            const resolvedUrl = `/api/vault-assets/${encodeURIComponent(decodedUrl)}?relative_to=${encodeURIComponent(window.activeDocId)}`;
            return `<a href="${resolvedUrl}" target="_blank" class="attachment-link">📎 ${text}</a>`;
        } else {
            const cleanDocPath = decodedUrl.replace(/\.mdx?$/, '');
            return `<a href="#" onclick="openEditorFromPreview('${cleanDocPath.replace(/'/g, "\\'")}', event)" class="wiki-doc-link">📄 ${text}</a>`;
        }
    });

    // 🚀 [V87.0] 实时解析 Markdown (依赖 vendor/marked.js)
    if (typeof marked !== 'undefined') {
        preview.innerHTML = marked.parse(mdContent);
    } else {
        preview.innerText = "Markdown 引擎尚未就绪...";
    }
};

// 📄 相对路径物理对齐与降级解析器 (JavaScript 版 Path.resolve)
const resolveRelativePath = (basePath, relPath) => {
    if (!relPath.startsWith('.')) return relPath; // 非相对路径直接返回
    
    const baseParts = basePath.split('/');
    baseParts.pop(); // 移除文件名，保留目录结构
    
    const relParts = relPath.split('/');
    for (const part of relParts) {
        if (part === '.' || part === '') continue;
        if (part === '..') {
            baseParts.pop();
        } else {
            baseParts.push(part);
        }
    }
    return baseParts.join('/');
};

// 📄 [NEW] 双链编辑器联动跳转引擎
window.openEditorFromPreview = async (wikiName, event) => {
    if (event) event.preventDefault();
    try {
        // 🚀 高能对齐：先进行 URL-decode（将 %20 等符号还原为真实的物理路径空格）
        const decodedWikiName = decodeURIComponent(wikiName);
        
        // 🚀 兼容性护航：分离出 Obsidian 标题锚点（如 [[Doc#Heading]]）或块引用（如 [[Doc#^block]]）
        let docPathOnly = decodedWikiName;
        let anchor = "";
        const hashIndex = decodedWikiName.indexOf('#');
        if (hashIndex !== -1) {
            docPathOnly = decodedWikiName.substring(0, hashIndex);
            anchor = decodedWikiName.substring(hashIndex + 1);
        }
        
        // 再进行相对路径物理对正（支持 ../ 等相对路径）
        const normalizedName = resolveRelativePath(window.activeDocId, docPathOnly);
        console.log(`[Wiki Navigation] Original: ${wikiName} -> Decoded: ${decodedWikiName} -> Normalized: ${normalizedName} (Anchor: ${anchor})`);

        // 全量联邦检索定位目标相对路径
        const res = await apiFetch(`/api/vault/search?q=${encodeURIComponent(normalizedName)}&limit=1`);
        if (res && res.items && res.items.length > 0) {
            const doc = res.items[0];
            // 平滑进入下一份资产编辑，刷新编辑器面板
            openEditor(doc.rel_path);
        } else {
            Swal.fire({
                title: '未发现该资产',
                text: `系统在原稿库中未能定位匹配到 "${normalizedName}"。`,
                icon: 'warning',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
        }
    } catch (e) {
        console.error("Open editor from preview error:", e);
    }
};


// 🔄 [V87.1] 同步滚动引擎 (Synchronized Scroll Engine)
let isSyncingScroll = false;
window.initSyncScroll = () => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    if (!body || !preview || body._syncBound) return;

    body._syncBound = true;

    const sync = (source, target) => {
        if (isSyncingScroll) return;
        const btnSplit = document.getElementById('mode-split');
        if (!btnSplit?.classList.contains('active')) return;

        isSyncingScroll = true;
        const sourceMax = source.scrollHeight - source.clientHeight;
        const targetMax = target.scrollHeight - target.clientHeight;

        if (sourceMax > 0) {
            const percentage = source.scrollTop / sourceMax;
            target.scrollTop = percentage * targetMax;
        }

        // 使用 requestAnimationFrame 确保平滑度并防止死循环
        requestAnimationFrame(() => {
            isSyncingScroll = false;
        });
    };

    body.addEventListener('scroll', () => sync(body, preview), { passive: true });
    preview.addEventListener('scroll', () => sync(preview, body), { passive: true });
};

window.closeEditor = () => {
    document.getElementById('editor-modal').style.display = 'none';
    const configTabs = document.getElementById('config-tabs');
    if (configTabs) configTabs.style.display = 'none';
};

window.saveDocument = async () => {
    const content = document.getElementById('editor-body').value;
    const titleEl = document.getElementById('editor-meta-title');
    const slugEl = document.getElementById('editor-meta-slug');
    const status = document.getElementById('save-status');
    status.innerText = "💾 正在写入磁道...";

    // 🚀 [V68.0] 收集动态元数据
    const frontmatter = {};
    const metaInputs = document.querySelectorAll('.metadata-input');
    metaInputs.forEach(input => {
        const key = input.getAttribute('data-key');
        if (input.type === 'checkbox') {
            frontmatter[key] = input.checked;
        } else {
            const val = input.value.trim();
            
            // 🚀 [V87.3] 智能日期时区反向对准与重塑
            if (input.getAttribute('data-is-date') === 'true') {
                if (!val) {
                    frontmatter[key] = "";
                    return;
                }
                const dateObj = new Date(val);
                if (!isNaN(dateObj.getTime())) {
                    const pad = (n) => String(n).padStart(2, '0');
                    const offset = -dateObj.getTimezoneOffset();
                    const sign = offset >= 0 ? '+' : '-';
                    const tz = sign + pad(Math.floor(Math.abs(offset) / 60)) + ':' + pad(Math.abs(offset) % 60);
                    
                    const y = dateObj.getFullYear();
                    const m = pad(dateObj.getMonth() + 1);
                    const d = pad(dateObj.getDate());
                    const hh = pad(dateObj.getHours());
                    const mm = pad(dateObj.getMinutes());
                    const ss = pad(dateObj.getSeconds());
                    
                    frontmatter[key] = `${y}-${m}-${d}T${hh}:${mm}:${ss}${tz}`;
                    return;
                }
            }
            
            // 🚀 [V87.2] 智能解析 JSON 数组与复杂对象，防止结构混淆与二次破坏
            if ((val.startsWith('{') && val.endsWith('}')) || (val.startsWith('[') && val.endsWith(']'))) {
                try {
                    frontmatter[key] = JSON.parse(val);
                    return; // 成功解析为 JSON，跳过后续 standard 处理
                } catch (e) {
                    console.warn(`Failed to parse metadata field "${key}" as JSON, fallback to raw string:`, e);
                }
            }
            
            // 简单处理：如果包含逗号，尝试转为数组（对应用户对列表的支持要求）
            if (val.includes(',')) {
                frontmatter[key] = val.split(',').map(v => v.trim()).filter(v => v !== "");
            } else {
                frontmatter[key] = val;
            }
        }
    });

    const payload = { content, frontmatter };
    if (titleEl) payload.title = titleEl.value;
    if (slugEl) payload.slug = slugEl.value;

    const res = await apiFetch(`/ledger/document/${encodeURIComponent(window.activeDocId)}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.success) {
        status.innerText = "✅ 写入成功";
        addAudit(`📄 资产 ${window.activeDocId.substring(0, 8)} 已完成物理变更。`);
        setTimeout(closeEditor, 800);
        if (typeof currentView !== 'undefined' && window.currentView === 'overview') {
            if (typeof refreshGalaxy === 'function') refreshGalaxy();
        }
        if (typeof loadVault === 'function') {
            loadVault(window.vaultCurrentQuery, window.vaultCurrentPage);
        }
    } else {
        status.innerText = "❌ 写入失败";
        if (res && res.error) console.error(res.error);
    }
};
