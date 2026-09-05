/**
 * 🛣️ [V107.5] Illacme Plenipes Route Matrix - Source Events & Intent Controller Shard
 * 职责：无障碍键盘导航控制器（方向键移动、回车直达）、三级意图自动联动、即时键入响应与全局外部点击收起监听。
 */

(function () {
    /**
     * ⌨️ [V107.5] 键盘导航与无障碍选择控制器（方向键上下移动高亮，回车直接选中）
     */
    window.handleSourceInputKeydown = function (input, e) {
        if (!input || !e) return;
        const key = e.key;
        const wrap = input.closest('.source-picker-wrap');
        if (!wrap) return;
        const menu = wrap.querySelector('.source-dropdown-menu');
        if (!menu) return;

        // 如果按下 Escape 键，直接收起浮层
        if (key === 'Escape') {
            menu.style.display = 'none';
            return;
        }

        // 如果浮层未展开且用户按下了向下箭头或回车，自动唤起浮层
        if (menu.style.display === 'none' || !menu.style.display) {
            if (key === 'ArrowDown' || key === 'Down') {
                e.preventDefault();
                if (typeof window.openSourceDropdown === 'function') {
                    window.openSourceDropdown(input);
                }
            }
            return;
        }

        const items = Array.from(menu.querySelectorAll('.source-dropdown-item'));
        if (items.length === 0) return;

        let activeIndex = items.findIndex(it => it.classList.contains('selected-highlight'));

        if (key === 'ArrowDown' || key === 'Down') {
            e.preventDefault();
            activeIndex = (activeIndex + 1 >= items.length) ? 0 : activeIndex + 1;
            items.forEach((it, idx) => {
                if (idx === activeIndex) {
                    it.classList.add('selected-highlight');
                    it.style.background = 'rgba(0, 242, 255, 0.2)';
                    it.style.boxShadow = 'inset 2px 0 0 #00f2fe';
                    if (typeof it.scrollIntoView === 'function') {
                        it.scrollIntoView({ block: 'nearest' });
                    }
                } else {
                    it.classList.remove('selected-highlight');
                    it.style.background = 'transparent';
                    it.style.boxShadow = 'none';
                }
            });
        } else if (key === 'ArrowUp' || key === 'Up') {
            e.preventDefault();
            activeIndex = (activeIndex - 1 < 0) ? items.length - 1 : activeIndex - 1;
            items.forEach((it, idx) => {
                if (idx === activeIndex) {
                    it.classList.add('selected-highlight');
                    it.style.background = 'rgba(0, 242, 255, 0.2)';
                    it.style.boxShadow = 'inset 2px 0 0 #00f2fe';
                    if (typeof it.scrollIntoView === 'function') {
                        it.scrollIntoView({ block: 'nearest' });
                    }
                } else {
                    it.classList.remove('selected-highlight');
                    it.style.background = 'transparent';
                    it.style.boxShadow = 'none';
                }
            });
        } else if (key === 'Enter') {
            if (activeIndex >= 0 && items[activeIndex]) {
                e.preventDefault();
                if (typeof window.selectSourceDropdownItem === 'function') {
                    window.selectSourceDropdownItem(items[activeIndex]);
                }
            } else if (items.length > 0) {
                // 若没有明确高亮，回车直接选中首个最匹配项
                e.preventDefault();
                if (typeof window.selectSourceDropdownItem === 'function') {
                    window.selectSourceDropdownItem(items[0]);
                }
            }
        }
    };

    /**
     * 🪄 [V106.1] 输入或选择来源时触发 3 级意图自动联动
     */
    window.handleSourceInputChange = function (input) {
        const row = input.closest('.matrix-row');
        const val = (input.value || '').trim();
        const isMdFile = val.toLowerCase().endsWith('.md') || val.toLowerCase().endsWith('.markdown');

        if (row && isMdFile) {
            // 1. 自动提取前缀
            const prefixInput = row.querySelector('.prefix-input');
            const cleanSlug = val.replace(/\.(md|markdown)$/i, '').split('/').pop().toLowerCase();
            if (prefixInput && (!prefixInput.value || prefixInput.value === 'docs' || prefixInput.value === 'blog')) {
                prefixInput.value = cleanSlug;
            }

            // 2. 自动联动模板为 📄 独立页面 (pages)
            const slotSelect = row.querySelector('.slot-select');
            const slotInput = row.querySelector('.slot-input');
            if (slotSelect) {
                slotSelect.value = 'pages';
                slotSelect.style.display = 'block';
                if (slotInput) {
                    slotInput.value = 'pages';
                    slotInput.style.display = 'none';
                }
                const listId = input.getAttribute('list');
                const datalist = listId ? document.getElementById(listId) : null;
                if (datalist && typeof window.buildSourceDatalistOptions === 'function') {
                    datalist.innerHTML = window.buildSourceDatalistOptions('pages', val);
                }
            }

            // 3. 自动填入导航名称
            const navInput = row.querySelector('.nav-label-input');
            if (navInput && !navInput.value) {
                const vaultFiles = window.settingsData?._vault_files || [];
                const found = vaultFiles.find(f => (f.path || f.rel_path || f.id || f) === val);
                if (found && found.title && found.title !== val) {
                    navInput.value = found.title;
                } else {
                    navInput.value = cleanSlug.charAt(0).toUpperCase() + cleanSlug.slice(1);
                }
            }
        }

        if (typeof window.syncRouteMatrixToSettings === 'function') window.syncRouteMatrixToSettings();
        if (typeof window.updateAllLivePathBadges === 'function') window.updateAllLivePathBadges();
    };

    /**
     * ⚡ [V106.1] 键盘实时输入响应（即时联动与过滤毛玻璃弹层）
     */
    window.handleSourceInputTyping = function (input) {
        const wrap = input.closest('.source-picker-wrap');
        if (wrap) {
            const menu = wrap.querySelector('.source-dropdown-menu');
            if (menu && menu.style.display === 'block') {
                const row = input.closest('.matrix-row');
                const slotSelect = row ? row.querySelector('.slot-select') : null;
                const slotVal = slotSelect ? slotSelect.value : 'docs';
                if (typeof window.renderSourceDropdownContent === 'function') {
                    window.renderSourceDropdownContent(menu, input, slotVal, (input.value || '').trim().toLowerCase());
                }
            }
        }
        if (typeof window.syncRouteMatrixToSettings === 'function') window.syncRouteMatrixToSettings();
        if (typeof window.updateAllLivePathBadges === 'function') window.updateAllLivePathBadges();
    };

    /**
     * 兼容历史函数
     */
    window.handleSourceSelectChange = window.handleSourceInputChange;
    window.revertSourceToSelect = function () { };

    // 🌐 [V107.0] 全局监听点击外部与 ESC 键，自动收起所有打开的毛玻璃下拉浮层
    if (typeof document !== 'undefined' && typeof document.addEventListener === 'function') {
        document.addEventListener('click', function (e) {
            if (!e.target || !e.target.closest || !e.target.closest('.source-picker-wrap')) {
                if (typeof document.querySelectorAll === 'function') {
                    document.querySelectorAll('.source-dropdown-menu').forEach(menu => {
                        menu.style.display = 'none';
                    });
                }
            }
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                if (typeof document.querySelectorAll === 'function') {
                    document.querySelectorAll('.source-dropdown-menu').forEach(menu => {
                        menu.style.display = 'none';
                    });
                }
            }
        });
    }
})();
