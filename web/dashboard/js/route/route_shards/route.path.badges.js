/**
 * 🛣️ [V107.6] Illacme Plenipes Route Matrix - Path Badges & Live Inference Shard
 * 职责：实时产物路径推演 Tooltip 计算、文库原稿命中统计 (单篇 vs 目录)、失效来源模糊智能推荐、一键自愈修复与行内状态徽标刷新。
 */

(function () {
    /**
     * ⚡ [V107.6] 获取实时产物推演 Tooltip 提示文本（悬停即感知，与【网址路径组织形态】精准联动匹配）
     */
    window.getLivePathTooltip = function (route, customDirMode) {
        if (route.external_url) {
            return `🌐 外部直链：点击导航直接跳转至 ${route.external_url}`;
        }

        const source = (route.source || '').trim();
        const userPrefix = (route.prefix || '').trim().replace(/^\/+|\/+$/g, '');
        const targetSlot = (route.target_slot || 'docs').trim().toLowerCase();

        // 动态获取当前系统的两种核心路径配置：
        // 1. 网址路径组织形态 (nested 目录树复刻 / prefix 智能 SEO 前缀 / flat 极简根目录)
        const slugMode = window.settingsData?.translation?.slug_dir_mode || 'nested';
        // 2. 目录型发布模态 (url_routing_dir_mode: true => path/index.html, false => path.html)
        const isDirMode = (customDirMode !== undefined) ? !!customDirMode : !!window.settingsData?.compliance?.url_routing_dir_mode;
        const slugModeLabels = {
            'nested': '目录树复刻 (nested)',
            'prefix': '智能 SEO 前缀 (prefix)',
            'flat': '极简根目录 (flat)'
        };
        const currentModeLabel = slugModeLabels[slugMode] || slugMode;

        // 统一提取去除 .md 后缀的 slug 文件名
        const baseFileName = source.replace(/\.(md|markdown)$/i, '').split('/').pop() || 'page';
        const isSingleDoc = (targetSlot === 'pages' || targetSlot === 'page' || source.endsWith('.md'));

        if (isSingleDoc) {
            let compiledPath = '';
            if (userPrefix) {
                // 如果用户显式配置了网页路径前缀，优先使用配置
                compiledPath = isDirMode ? `${userPrefix}/index.html` : `${userPrefix}.html`;
            } else {
                // 根据当前生效的网址路径组织形态自动推导
                if (slugMode === 'flat') {
                    compiledPath = isDirMode ? `${baseFileName}/index.html` : `${baseFileName}.html`;
                } else if (slugMode === 'prefix') {
                    const dirPart = source.includes('/') ? source.substring(0, source.lastIndexOf('/')) : '';
                    const safePrefix = dirPart ? dirPart.replace(/\//g, '-').toLowerCase() + '-' : '';
                    compiledPath = isDirMode ? `${safePrefix}${baseFileName}/index.html` : `${safePrefix}${baseFileName}.html`;
                } else {
                    // nested 模式
                    const dirPart = source.includes('/') ? source.substring(0, source.lastIndexOf('/')) : '';
                    const nestedDir = dirPart ? `${dirPart.toLowerCase()}/` : '';
                    compiledPath = isDirMode ? `${nestedDir}${baseFileName}/index.html` : `${nestedDir}${baseFileName}.html`;
                }
            }
            return `📄 单篇独立页面：\n文库原稿：${source || '（未选）'}\n发布产物：${compiledPath}\n路径形态：${currentModeLabel}`;
        }

        const channelPrefix = (userPrefix || source || 'docs').trim().replace(/^\/+|\/+$/g, '');
        const channelDir = channelPrefix ? `${channelPrefix}/` : '';

        if (targetSlot === 'blog') {
            return `📰 博客频道专区：\n聚合目录：${source || '（根目录）'}\n发布产物：${channelDir}index.html、${channelDir}tags/、博文详情页\n路径形态：${currentModeLabel}`;
        }
        if (targetSlot === 'showcase' || targetSlot === 'show') {
            return `🖼️ 展示中心专区：\n聚合目录：${source || '（根目录）'}\n发布产物：${channelDir}index.html 及作品条目页\n路径形态：${currentModeLabel}`;
        }
        return `📚 文档知识库：\n聚合目录：${source || '（根目录）'}\n发布产物：${channelDir}index.html 及各级侧边栏页面\n路径形态：${currentModeLabel}`;
    };

    /**
     * 📊 [V106.0] 实时统计指定 source 匹配到的文库原稿篇数
     */
    window.calculateRouteHitCount = function (source) {
        const clean = (source || '').trim().replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
        if (!clean) return { count: 0, isFile: false };

        const isFile = clean.toLowerCase().endsWith('.md') || clean.toLowerCase().endsWith('.markdown');
        const vaultFiles = window.settingsData?._vault_files || [];
        const manuscripts = window.realManuscriptCache || [];
        const filesPool = vaultFiles.length > 0 ? vaultFiles : manuscripts;

        if (isFile) {
            const matched = filesPool.some(f => {
                const p = ((f.path || f.rel_path || f.id || f || '')).replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
                return p === clean;
            });
            return { count: matched ? 1 : 0, isFile: true };
        }

        // 目录级前缀匹配
        let count = 0;
        const prefixMatch = clean + '/';
        filesPool.forEach(f => {
            const p = ((f.path || f.rel_path || f.id || f || '')).replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
            if (p === clean || p.startsWith(prefixMatch)) {
                count++;
            }
        });
        return { count, isFile: false };
    };

    /**
     * 🔍 [V106.0] 智能计算与失效来源最相似的真实文库目录或单篇文件 (完整文件名与目录匹配)
     */
    window.findBestMatchingDirectory = function (orphanSource) {
        if (!orphanSource) return null;
        const vaultFiles = window.settingsData?._vault_files || [];
        const directories = window.settingsData?._directories || [];
        const clean = orphanSource.trim().toLowerCase();
        const base = clean.split('/').pop().replace(/\.(md|markdown)$/i, '');

        // 优先匹配单篇文库文件
        for (const f of vaultFiles) {
            const p = (f.path || f.rel_path || f.id || f || '').replace(/\\/g, '/');
            const fBase = p.split('/').pop().replace(/\.(md|markdown)$/i, '').toLowerCase();
            if (fBase === base || p.toLowerCase().includes(base)) {
                return p;
            }
        }

        // 次选匹配目录
        for (const d of directories) {
            const dBase = d.split('/').pop().toLowerCase();
            if (dBase === base || d.toLowerCase().includes(base)) {
                return d;
            }
        }
        return null;
    };

    /**
     * ✨ [V106.1] 一键自愈：将失效目录替换为推荐的真实有效目录
     */
    window.autoHealOrphanSource = function (btn, newDir) {
        const row = btn.closest('.matrix-row');
        if (!row || !newDir) return;
        const sourceInput = row.querySelector('.source-input');
        if (sourceInput) {
            sourceInput.value = newDir;
            if (typeof window.handleSourceInputChange === 'function') {
                window.handleSourceInputChange(sourceInput);
            }
        }

        if (typeof showToast === 'function') {
            showToast(`✨ 已成功将来源关联修复为【${newDir}】`, 'success');
        }
    };

    /**
     * 🔄 [V107.5] 动态刷新所有输入框内部内联 Badge（原稿篇数、警告、自愈按钮及模板槽位智能感知 Tooltip）
     */
    window.updateAllLivePathBadges = function () {
        if (typeof document === 'undefined' || !document.querySelectorAll) return;
        const rows = document.querySelectorAll('#route-matrix-body .matrix-row, .matrix-row.route-item');
        const dirMode = !!window.settingsData?.compliance?.url_routing_dir_mode;
        const directories = window.settingsData?._directories || [];
        const vaultFiles = window.settingsData?._vault_files || [];

        rows.forEach(row => {
            const extInput = row.querySelector('.ext-url-input');
            const prefixInput = row.querySelector('.prefix-input');
            const sourceInput = row.querySelector('.source-input');
            const slotSelect = row.querySelector('.slot-select');
            const badgeContainer = row.querySelector('.in-input-badge-container');
            const isExternal = row.getAttribute('data-external') === 'true' || !!(extInput && extInput.value);

            if (!badgeContainer) return;

            const toggleBtn = badgeContainer.querySelector('.source-dropdown-toggle-btn');
            // 保持下拉箭头展开按钮始终存在
            if (!toggleBtn && !isExternal) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'source-dropdown-toggle-btn';
                btn.title = '展开文库路径列表 (或按键盘 ↓ 方向键)';
                btn.innerHTML = '▼';
                btn.style.cssText = 'background: transparent; border: none; color: rgba(255, 255, 255, 0.38); cursor: pointer; font-size: 0.65rem; padding: 2px 4px; display: inline-flex; align-items: center; justify-content: center; line-height: 1; border-radius: 3px; transition: color 0.15s, background 0.15s;';
                btn.onclick = function (e) {
                    if (typeof window.toggleSourceDropdown === 'function') {
                        window.toggleSourceDropdown(this, e);
                    }
                };
                btn.onmouseenter = function () { this.style.color = '#00f2fe'; this.style.background = 'rgba(0, 242, 255, 0.1)'; };
                btn.onmouseleave = function () { this.style.color = 'rgba(255, 255, 255, 0.38)'; this.style.background = 'transparent'; };
                badgeContainer.appendChild(btn);
            }

            if (isExternal) {
                if (sourceInput) sourceInput.style.paddingRight = '32px';
                badgeContainer.innerHTML = '';
                return;
            }

            const source = (sourceInput ? sourceInput.value : '').trim();
            const prefix = prefixInput ? prefixInput.value : '';
            const targetSlot = slotSelect ? (slotSelect.value || 'docs').trim().toLowerCase() : 'docs';

            const tooltip = window.getLivePathTooltip({ source, prefix, target_slot: targetSlot }, dirMode);
            if (prefixInput) prefixInput.title = tooltip;

            // 清理除 toggleBtn 外的所有旧徽标和修复按钮
            Array.from(badgeContainer.children).forEach(child => {
                if (child !== toggleBtn && !child.classList.contains('source-dropdown-toggle-btn')) {
                    badgeContainer.removeChild(child);
                }
            });

            if (!source) {
                if (sourceInput) {
                    sourceInput.style.borderColor = '';
                    sourceInput.style.boxShadow = '';
                    sourceInput.style.paddingRight = '32px';
                }
                return;
            }

            // 判定是否是未匹配到的孤儿失效来源
            const isDir = directories.includes(source);
            const isFile = vaultFiles.some(f => (f.path || f.rel_path || f.id || f) === source);
            const isOrphan = !isDir && !isFile;

            // 智能感知模板槽位与文库路径类型协同状态
            const isSingleFile = source.toLowerCase().endsWith('.md') || source.toLowerCase().endsWith('.markdown') || isFile;
            const isDirSlot = (targetSlot === 'docs' || targetSlot === 'blog' || targetSlot === 'showcase' || targetSlot === 'show');
            const isPageSlot = (targetSlot === 'pages' || targetSlot === 'page');

            let mismatchTooltip = '';
            if (isSingleFile && isDirSlot) {
                mismatchTooltip = '💡 提示：该模板主要用于聚合整个目录，当前绑定的是单篇 .md 文件';
            } else if (!isSingleFile && isPageSlot) {
                mismatchTooltip = '💡 提示：独立页面模板通常绑定单篇 .md 文件，当前绑定的是聚合目录';
            }

            if (isOrphan) {
                if (sourceInput) {
                    sourceInput.style.borderColor = 'rgba(251, 191, 36, 0.7)';
                    sourceInput.style.boxShadow = '0 0 6px rgba(251, 191, 36, 0.2)';
                }
                const healSuggestion = typeof window.findBestMatchingDirectory === 'function' ? window.findBestMatchingDirectory(source) : null;

                const warnSpan = document.createElement('span');
                warnSpan.style.cssText = 'color: #fbbf24; cursor: help; font-size: 0.72rem; display: inline-flex; align-items: center; line-height: 1;';
                warnSpan.title = `在文库目录或独立稿件中未检索到【${source}】，请确认文件名（含后缀）或文件夹名称是否准确`;
                warnSpan.textContent = '⚠️';
                if (toggleBtn) {
                    badgeContainer.insertBefore(warnSpan, toggleBtn);
                } else {
                    badgeContainer.appendChild(warnSpan);
                }

                if (healSuggestion) {
                    const healBtn = document.createElement('button');
                    healBtn.type = 'button';
                    healBtn.className = 'mini-btn glow-btn orphan-heal-btn';
                    healBtn.style.cssText = 'padding: 1px 4px; font-size: 0.62rem; background: rgba(0, 242, 255, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 3px; cursor: pointer; white-space: nowrap; line-height: 1.2; margin-right: 2px;';
                    healBtn.title = `点击关联至现存真实文库文件【${healSuggestion}】`;
                    healBtn.textContent = '✨修复';
                    healBtn.onclick = function () { window.autoHealOrphanSource(this, healSuggestion); };
                    badgeContainer.insertBefore(healBtn, warnSpan);
                    if (sourceInput) sourceInput.style.paddingRight = '78px';
                } else {
                    if (sourceInput) sourceInput.style.paddingRight = '48px';
                }
            } else {
                if (sourceInput) {
                    sourceInput.style.borderColor = '';
                    sourceInput.style.boxShadow = '';
                    sourceInput.style.paddingRight = '48px';
                }
                const { count, isFile: isFileHit } = window.calculateRouteHitCount(source);

                const dotSpan = document.createElement('span');
                dotSpan.style.cssText = 'cursor: help; font-size: 0.72rem; line-height: 1; display: inline-flex; align-items: center;';

                let dotTitle = '';
                if (count > 0) {
                    dotSpan.textContent = '🟢';
                    dotTitle = `该专区当前包含 ${count} 篇已命中原稿 (${isFileHit ? '单篇页面' : '目录聚合'})`;
                } else {
                    dotSpan.textContent = '⚪';
                    dotTitle = '当前目录或路径暂未扫描到原稿，请检查文件是否存在';
                }

                if (mismatchTooltip) {
                    dotTitle += `\n${mismatchTooltip}`;
                }

                dotSpan.title = dotTitle;
                if (toggleBtn) {
                    badgeContainer.insertBefore(dotSpan, toggleBtn);
                } else {
                    badgeContainer.appendChild(dotSpan);
                }
            }
        });
    };
})();
