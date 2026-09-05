/**
 * 🛣️ [V106.3] Illacme Plenipes Route Matrix - Source Options Generator Shard
 * 职责：模板槽位感知的前端文库来源下拉数据生成器、树形目录结构递归扁平化与单篇文件过滤。
 */

(function () {
    /**
     * 🌲 [V106.3] 模板槽位感知的前端文库来源下拉选项生成器 (Template-Aware Slot Source Filter)
     * - docs / blog / showcase / show: 纯目录树形列表 (只列目录，不列单篇文件)
     * - pages / page / static / assets: 纯文件列表 (根目录文件直接呈现，子目录文件带精简路径)
     * - 其他/自定义槽位: 目录与文件归类展示
     */
    window.buildSourceDatalistOptions = function (slotVal, sourceVal) {
        const directories = window.settingsData?._directories || [];
        const vaultFiles = window.settingsData?._vault_files || [];
        const cleanVal = (sourceVal || '').trim();
        const slot = (slotVal || '').toLowerCase().trim();

        const dirSlots = ['docs', 'blog', 'showcase', 'show'];
        const fileSlots = ['pages', 'page', 'static', 'assets'];

        const isDirOnly = dirSlots.includes(slot);
        const isFileOnly = fileSlots.includes(slot);

        let optionsHtml = '';

        // 1. 构建物理目录树结构
        const rootTree = { name: '', path: '', dirs: {}, files: [] };

        if (directories.length > 0) {
            directories.forEach(d => {
                if (!d) return;
                const parts = d.replace(/\\/g, '/').split('/');
                let cur = rootTree;
                let curPath = '';
                parts.forEach(folder => {
                    curPath = curPath ? `${curPath}/${folder}` : folder;
                    if (!cur.dirs[folder]) {
                        cur.dirs[folder] = { name: folder, path: curPath, dirs: {}, files: [] };
                    }
                    cur = cur.dirs[folder];
                });
            });
        }

        if (!isDirOnly && vaultFiles.length > 0) {
            vaultFiles.forEach(f => {
                const p = (f.path || f.rel_path || f.id || f || '').replace(/\\/g, '/');
                if (!p) return;
                const parts = p.split('/');
                let cur = rootTree;
                for (let i = 0; i < parts.length - 1; i++) {
                    const folder = parts[i];
                    if (!cur.dirs[folder]) {
                        const folderPath = parts.slice(0, i + 1).join('/');
                        cur.dirs[folder] = { name: folder, path: folderPath, dirs: {}, files: [] };
                    }
                    cur = cur.dirs[folder];
                }
                cur.files.push({
                    name: parts[parts.length - 1],
                    path: p,
                    title: f.title || ''
                });
            });
        }

        // 递归生成纯目录树结构（保持层级视觉与折线）
        function flattenDirsTree(node, prefix = '', isLast = true, isRoot = false) {
            let html = '';
            if (!isRoot) {
                const marker = isLast ? '└─ ' : '├─ ';
                const label = `${prefix}${marker}📁 ${node.name} (目录)`;
                html += `<option value="${node.path}">${label}</option>`;
            }
            const childPrefix = isRoot ? '' : `${prefix}${isLast ? '    ' : '│   '}`;
            const dirKeys = Object.keys(node.dirs).sort();
            dirKeys.forEach((k, idx) => {
                const last = (idx === dirKeys.length - 1);
                html += flattenDirsTree(node.dirs[k], childPrefix, last, false);
            });
            return html;
        }

        // 生成精简的文件选项（根目录直接排前，子目录带路径前缀，附带文档标题）
        function flattenFilesList(files) {
            let html = '';
            // 排序：先根目录文件，再子目录文件
            const sorted = [...files].sort((a, b) => {
                const aPath = (a.path || a.rel_path || a.id || a || '');
                const bPath = (b.path || b.rel_path || b.id || b || '');
                const aIsRoot = !aPath.includes('/');
                const bIsRoot = !bPath.includes('/');
                if (aIsRoot && !bIsRoot) return -1;
                if (!aIsRoot && bIsRoot) return 1;
                return aPath.localeCompare(bPath);
            });

            sorted.forEach(f => {
                const p = (f.path || f.rel_path || f.id || f || '').replace(/\\/g, '/');
                if (!p) return;
                const parts = p.split('/');
                const fileName = parts.pop();
                const dirPart = parts.length > 0 ? parts.join('/') + ' / ' : '';
                const cleanBase = fileName.replace(/\.(md|markdown)$/i, '');
                const hasRealTitle = f.title && f.title !== p && f.title !== fileName && f.title !== cleanBase;
                const titlePart = hasRealTitle ? ` (${f.title})` : '';
                const label = dirPart ? `📁 ${dirPart}📄 ${fileName}${titlePart}` : `📄 ${fileName}${titlePart}`;
                html += `<option value="${p}">${label}</option>`;
            });
            return html;
        }

        // 分支 1：文档/博客/展厅等聚合槽位 -> 纯目录
        if (isDirOnly) {
            optionsHtml = flattenDirsTree(rootTree, '', true, true);
        }
        // 分支 2：独立页面/静态资源等单体槽位 -> 纯文件
        else if (isFileOnly) {
            optionsHtml = flattenFilesList(vaultFiles);
        }
        // 分支 3：自定义或其他槽位 -> 目录在前，文件在后
        else {
            optionsHtml = flattenDirsTree(rootTree, '', true, true) + flattenFilesList(vaultFiles);
        }

        // 容错兜底：若已有 cleanVal 不在选项列表中（如已被移走或当前模板不匹配），保留该选项提示
        if (cleanVal && !optionsHtml.includes(`value="${cleanVal}"`)) {
            const isMd = cleanVal.toLowerCase().endsWith('.md') || cleanVal.toLowerCase().endsWith('.markdown');
            const icon = isMd ? '📄' : '📁';
            optionsHtml = `<option value="${cleanVal}">⚠️ ${icon} ${cleanVal} (当前未找到)</option>` + optionsHtml;
        }

        return optionsHtml;
    };

    /**
     * 🌲 [V107.0] 收集当前槽位感知下的结构化文库条目列表（用于方案 B 轻量毛玻璃单行下拉浮层渲染）
     */
    window.getSourcePickerItems = function (slotVal, cleanVal) {
        const directories = window.settingsData?._directories || [];
        const vaultFiles = window.settingsData?._vault_files || [];
        const slot = (slotVal || '').toLowerCase().trim();

        const dirSlots = ['docs', 'blog', 'showcase', 'show'];
        const fileSlots = ['pages', 'page', 'static', 'assets'];

        const isDirOnly = dirSlots.includes(slot);
        const isFileOnly = fileSlots.includes(slot);

        const items = [];

        // 1. 构建目录树
        const rootTree = { name: '', path: '', dirs: {}, files: [] };
        if (directories.length > 0) {
            directories.forEach(d => {
                if (!d) return;
                const parts = d.replace(/\\/g, '/').split('/');
                let cur = rootTree;
                let curPath = '';
                parts.forEach(folder => {
                    curPath = curPath ? `${curPath}/${folder}` : folder;
                    if (!cur.dirs[folder]) {
                        cur.dirs[folder] = { name: folder, path: curPath, dirs: {}, files: [] };
                    }
                    cur = cur.dirs[folder];
                });
            });
        }

        // 收集目录树条目
        function collectDirs(node, prefix = '', isLast = true, isRoot = false) {
            if (!isRoot) {
                const marker = isLast ? '└─ ' : '├─ ';
                items.push({
                    type: 'dir',
                    path: node.path,
                    name: node.name,
                    treePrefix: `${prefix}${marker}`,
                    label: node.name,
                    tag: '目录'
                });
            }
            const childPrefix = isRoot ? '' : `${prefix}${isLast ? '    ' : '│   '}`;
            const dirKeys = Object.keys(node.dirs).sort();
            dirKeys.forEach((k, idx) => {
                const last = (idx === dirKeys.length - 1);
                collectDirs(node.dirs[k], childPrefix, last, false);
            });
        }

        // 收集文件条目
        function collectFiles(files) {
            const sorted = [...files].sort((a, b) => {
                const aPath = (a.path || a.rel_path || a.id || a || '');
                const bPath = (b.path || b.rel_path || b.id || b || '');
                const aIsRoot = !aPath.includes('/');
                const bIsRoot = !bPath.includes('/');
                if (aIsRoot && !bIsRoot) return -1;
                if (!aIsRoot && bIsRoot) return 1;
                return aPath.localeCompare(bPath);
            });

            sorted.forEach(f => {
                const p = (f.path || f.rel_path || f.id || f || '').replace(/\\/g, '/');
                if (!p) return;
                const parts = p.split('/');
                const fileName = parts.pop();
                const dirPart = parts.length > 0 ? parts.join('/') + '/' : '';
                const cleanBase = fileName.replace(/\.(md|markdown)$/i, '');
                const hasRealTitle = f.title && f.title !== p && f.title !== fileName && f.title !== cleanBase;
                items.push({
                    type: 'file',
                    path: p,
                    name: fileName,
                    dirPart: dirPart,
                    title: hasRealTitle ? f.title : '',
                    tag: hasRealTitle ? f.title : '页面'
                });
            });
        }

        if (isDirOnly) {
            collectDirs(rootTree, '', true, true);
        } else if (isFileOnly) {
            collectFiles(vaultFiles);
        } else {
            collectDirs(rootTree, '', true, true);
            collectFiles(vaultFiles);
        }

        return items;
    };
})();
