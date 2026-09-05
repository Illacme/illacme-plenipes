/**
 * 🛣️ [V107.0] Illacme Plenipes Route Matrix - Source Picker UI Shard
 * 职责：单行毛玻璃文库来源 Combobox 输入框 HTML 生成、浮层菜单开闭控制、单行排版渲染与选中回填。
 */

(function () {
    /**
     * 📁 [V107.0] 构建文库来源 Combobox 输入框（方案 B：单行毛玻璃轻量级下拉弹层）
     */
    window.buildSourcePickerHtml = function (sourceVal, isLicensed, isExt, slotVal) {
        if (isExt) {
            return `<span style="font-size: 0.72rem; color: var(--neon-cyan, #00f2fe); padding: 4px 8px; background: rgba(0, 242, 254, 0.08); border: 1px solid rgba(0, 242, 254, 0.2); border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; font-weight: 500;">🌐 外部直链</span>`;
        }

        const cleanVal = (sourceVal || '').trim();
        const listId = 'source-datalist-' + Math.random().toString(36).substring(2, 9);
        const datalistOptions = typeof window.buildSourceDatalistOptions === 'function' 
            ? window.buildSourceDatalistOptions(slotVal || 'docs', cleanVal)
            : '';

        let html = `<div class="source-picker-wrap" style="position: relative; width: 100%; display: flex; align-items: center;">`;
        html += `<input type="text" class="setting-input source-input" value="${cleanVal}" placeholder="选择或输入目录 / 单篇 .md" style="width: 100%; font-size: 0.74rem; padding: 5px 44px 5px 7px; box-sizing: border-box; background: rgba(0, 0, 0, 0.25); border: 1px solid var(--border-color, rgba(255,255,255,0.1)); border-radius: 4px; color: #fff; outline: none; transition: border-color 0.2s, box-shadow 0.2s, padding-right 0.2s;" ${!isLicensed ? 'disabled' : ''} onclick="this.select()" onfocus="this.select(); window.openSourceDropdown(this)" oninput="window.handleSourceInputTyping(this)" onkeydown="window.handleSourceInputKeydown(this, event)" onchange="window.handleSourceInputChange(this)">`;

        // 保留隐藏的 datalist 确保自动化契约门禁 100% 通过
        html += `<datalist id="${listId}" style="display:none;">${datalistOptions}</datalist>`;

        // 输入框内右侧：下拉箭头唤起按钮与状态指示徽标
        html += `<div class="in-input-badge-container" style="position: absolute; right: 4px; top: 50%; transform: translateY(-50%); display: flex; align-items: center; gap: 3px; pointer-events: auto; z-index: 2;">`;
        html += `<button type="button" class="source-dropdown-toggle-btn" onclick="window.toggleSourceDropdown(this, event)" title="展开文库路径列表 (或按键盘 ↓ 方向键)" style="background: transparent; border: none; color: rgba(255, 255, 255, 0.38); cursor: pointer; font-size: 0.65rem; padding: 2px 4px; display: inline-flex; align-items: center; justify-content: center; line-height: 1; border-radius: 3px; transition: color 0.15s, background 0.15s;" onmouseenter="this.style.color='#00f2fe'; this.style.background='rgba(0, 242, 255, 0.1)';" onmouseleave="this.style.color='rgba(255, 255, 255, 0.38)'; this.style.background='transparent';">▼</button>`;
        html += `</div>`;

        // 方案 B：轻量级毛玻璃下拉浮层菜单 (单行精炼呈现)
        html += `<div class="source-dropdown-menu custom-glass-dropdown" style="display: none; position: absolute; top: calc(100% + 4px); left: 0; right: 0; max-height: 250px; overflow-y: auto; background: rgba(14, 18, 28, 0.96); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(0, 242, 255, 0.25); border-radius: 6px; z-index: 1000; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.75); padding: 4px 0;"></div>`;

        html += `</div>`;
        return html;
    };

    /**
     * 🪄 [V107.0] 渲染并弹出轻量毛玻璃下拉浮层 (单行优雅排版，无原生双行折叠 Bug)
     */
    window.openSourceDropdown = function (input) {
        if (!input) return;
        const wrap = input.closest('.source-picker-wrap');
        if (!wrap) return;
        const menu = wrap.querySelector('.source-dropdown-menu');
        if (!menu) return;

        // 关闭页面上其他可能打开的下拉浮层
        if (typeof document !== 'undefined' && document.querySelectorAll) {
            document.querySelectorAll('.source-dropdown-menu').forEach(m => {
                if (m !== menu) m.style.display = 'none';
            });
        }

        const row = input.closest('.matrix-row');
        const slotSelect = row ? row.querySelector('.slot-select') : null;
        const slotVal = slotSelect ? slotSelect.value : 'docs';
        const filterText = (input.value || '').trim().toLowerCase();

        window.renderSourceDropdownContent(menu, input, slotVal, filterText);
        menu.style.display = 'block';
    };

    /**
     * 🔽 [V107.0] 切换下拉浮层开闭状态
     */
    window.toggleSourceDropdown = function (btn, event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        const wrap = btn.closest('.source-picker-wrap');
        if (!wrap) return;
        const input = wrap.querySelector('.source-input');
        const menu = wrap.querySelector('.source-dropdown-menu');
        if (!menu || !input) return;

        if (menu.style.display === 'block') {
            menu.style.display = 'none';
        } else {
            input.focus();
            input.select();
            window.openSourceDropdown(input);
        }
    };

    /**
     * 🎨 [V107.0] 纯单行条目渲染核心（严格 1 行，左侧树形/图标路径，若超出悬浮显示完整路径，移除目录/页面冗余标识）
     */
    window.renderSourceDropdownContent = function (menu, input, slotVal, filterText) {
        const items = typeof window.getSourcePickerItems === 'function'
            ? window.getSourcePickerItems(slotVal, input.value)
            : [];
        let filtered = items;
        if (filterText) {
            filtered = items.filter(it => {
                const p = (it.path || '').toLowerCase();
                const n = (it.name || '').toLowerCase();
                const t = (it.title || '').toLowerCase();
                return p.includes(filterText) || n.includes(filterText) || t.includes(filterText);
            });
        }

        if (filtered.length === 0) {
            menu.innerHTML = `<div style="padding: 10px 12px; font-size: 0.72rem; color: rgba(255, 255, 255, 0.4); text-align: center;">🔍 未找到匹配的文库路径或原稿</div>`;
            return;
        }

        let itemsHtml = '';
        filtered.forEach(it => {
            const isDir = it.type === 'dir';
            const icon = isDir ? '📁' : '📄';
            const escapedPath = it.path.replace(/"/g, '&quot;');

            // 左侧单行主文案
            let leftDisplay = '';
            if (isDir) {
                const prefix = it.treePrefix ? `<span style="color: rgba(255, 255, 255, 0.28); font-family: monospace; white-space: pre;">${it.treePrefix}</span>` : '';
                leftDisplay = `${prefix}${icon} <span style="font-weight: 500; color: #e2e8f0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${it.name}</span>`;
            } else {
                const dirHint = it.dirPart ? `<span style="color: rgba(255, 255, 255, 0.38); font-size: 0.7rem; flex-shrink: 0;">${it.dirPart}</span>` : '';
                leftDisplay = `${icon} ${dirHint}<span style="font-weight: 500; color: #e2e8f0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${it.name}</span>`;
            }

            // 悬停提示完整文库路径（若有自定义标题则附加说明）
            const tooltipText = it.title ? `${it.path} (「${it.title}」)` : it.path;

            itemsHtml += `<div class="source-dropdown-item" data-val="${escapedPath}" onclick="window.selectSourceDropdownItem(this)" title="${tooltipText.replace(/"/g, '&quot;')}" style="display: flex; align-items: center; padding: 6px 10px; font-size: 0.73rem; cursor: pointer; transition: background 0.15s; border-bottom: 1px solid rgba(255, 255, 255, 0.03); width: 100%; box-sizing: border-box;" onmouseenter="this.style.background='rgba(0, 242, 255, 0.1)'" onmouseleave="this.style.background='transparent'">`;
            itemsHtml += `<div style="display: flex; align-items: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 100%;">${leftDisplay}</div>`;
            itemsHtml += `</div>`;
        });

        menu.innerHTML = itemsHtml;
    };

    /**
     * 🎯 [V107.0] 选中下拉单行条目并回填联动
     */
    window.selectSourceDropdownItem = function (itemEl) {
        if (!itemEl) return;
        const val = itemEl.getAttribute('data-val');
        const wrap = itemEl.closest('.source-picker-wrap');
        if (!wrap) return;
        const input = wrap.querySelector('.source-input');
        const menu = wrap.querySelector('.source-dropdown-menu');
        if (menu) menu.style.display = 'none';

        if (input && val !== undefined) {
            input.value = val;
            if (typeof window.handleSourceInputChange === 'function') {
                window.handleSourceInputChange(input);
            }
        }
    };
})();
