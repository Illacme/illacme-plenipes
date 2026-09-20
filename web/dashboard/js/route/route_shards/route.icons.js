/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - Icon Picker Popover Shard
 * 职责：导航图标选择器浮窗触发、自定义 Emoji 注入与图标绑定。
 */

(function () {
    let activeIconPickerTarget = null;

    window.toggleIconPicker = (btn, event) => {
        if (event) event.stopPropagation();
        
        const existing = document.getElementById('global-icon-picker-popover');
        if (existing) {
            const isSame = (activeIconPickerTarget === btn);
            existing.remove();
            activeIconPickerTarget = null;
            if (isSame) return;
        }

        activeIconPickerTarget = btn;
        const rect = btn.getBoundingClientRect();

        let pickerHtml = `
            <div id="global-icon-picker-popover" class="glass-panel global-icon-picker-popover" style="position: fixed; top: ${rect.bottom + 6}px; left: ${Math.min(rect.left, window.innerWidth - 300)}px; width: 280px; max-height: 320px; overflow-y: auto; z-index: 99999; backdrop-filter: blur(16px); border-radius: 10px; padding: 12px; font-family: inherit;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid var(--glass-border); padding-bottom: 6px;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent-secondary, #00f2fe);">✨ 选择导航图标</span>
                    <button type="button" onclick="document.getElementById('global-icon-picker-popover')?.remove();" style="background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 0.9rem; padding: 0 4px;">✕</button>
                </div>
        `;

        const palette = window.EMOJI_PALETTE || {};
        Object.entries(palette).forEach(([cat, emojis]) => {
            pickerHtml += `
                <div style="margin-bottom: 8px;">
                    <div style="font-size: 0.7rem; color: var(--text-dim); margin-bottom: 4px; font-weight: 600;">${cat}</div>
                    <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px;">
                        ${emojis.map(e => `
                            <button type="button" class="emoji-opt-btn" onclick="window.selectNavIcon('${e}')" style="background: var(--card-subtle-bg, rgba(255,255,255,0.04)); border: 1px solid var(--glass-border); border-radius: 6px; font-size: 1.1rem; padding: 4px 0; cursor: pointer; transition: all 0.15s ease; text-align: center;">${e}</button>
                        `).join('')}
                    </div>
                </div>
            `;
        });

        pickerHtml += `
                <div style="margin-top: 8px; border-top: 1px solid var(--glass-border); padding-top: 8px; display: flex; gap: 6px;">
                    <input type="text" id="custom-emoji-input" class="setting-input" placeholder="输入任意 Emoji..." maxlength="4" style="flex: 1; font-size: 0.76rem; padding: 4px 8px; border-radius: 4px;" onkeydown="if(event.key==='Enter'){ window.selectNavIcon(this.value.trim()); event.preventDefault(); }">
                    <button type="button" onclick="window.selectNavIcon(document.getElementById('custom-emoji-input').value.trim())" style="padding: 4px 10px; font-size: 0.74rem; background: var(--accent-primary, #00f2fe); color: #000; border: none; border-radius: 4px; font-weight: 600; cursor: pointer;">确定</button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', pickerHtml);

        setTimeout(() => {
            const closeHandler = (e) => {
                const popover = document.getElementById('global-icon-picker-popover');
                if (popover && !popover.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
                    popover.remove();
                    activeIconPickerTarget = null;
                    document.removeEventListener('click', closeHandler);
                }
            };
            document.addEventListener('click', closeHandler);
        }, 10);
    };

    window.selectNavIcon = (emoji) => {
        if (!emoji || !activeIconPickerTarget) return;
        const parentContainer = activeIconPickerTarget.parentElement;
        if (parentContainer) {
            const preview = activeIconPickerTarget.querySelector('.icon-preview');
            const hiddenInput = parentContainer.querySelector('.nav-icon-input');
            if (preview) preview.textContent = emoji;
            if (hiddenInput) hiddenInput.value = emoji;
        }
        const popover = document.getElementById('global-icon-picker-popover');
        if (popover) popover.remove();
        activeIconPickerTarget = null;
        if (typeof window.syncRouteMatrixToSettings === 'function') {
            window.syncRouteMatrixToSettings();
        }
    };
})();
