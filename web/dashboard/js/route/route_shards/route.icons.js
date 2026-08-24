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
            <div id="global-icon-picker-popover" class="glass-panel" style="position: fixed; top: ${rect.bottom + 6}px; left: ${Math.min(rect.left, window.innerWidth - 300)}px; width: 280px; max-height: 320px; overflow-y: auto; z-index: 99999; background: rgba(16, 18, 32, 0.96); backdrop-filter: blur(16px); border: 1px solid rgba(0, 242, 255, 0.3); border-radius: 10px; box-shadow: 0 12px 36px rgba(0,0,0,0.6); padding: 12px; font-family: inherit;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 6px;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent-secondary, #00f2fe);">✨ 选择导航图标</span>
                    <button type="button" onclick="document.getElementById('global-icon-picker-popover')?.remove();" style="background: none; border: none; color: #888; cursor: pointer; font-size: 0.9rem; padding: 0 4px;">✕</button>
                </div>
        `;

        const palette = window.EMOJI_PALETTE || {};
        Object.entries(palette).forEach(([cat, emojis]) => {
            pickerHtml += `
                <div style="margin-bottom: 8px;">
                    <div style="font-size: 0.7rem; color: var(--text-dim); margin-bottom: 4px; font-weight: 600;">${cat}</div>
                    <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px;">
                        ${emojis.map(e => `
                            <button type="button" class="emoji-opt-btn" onclick="window.selectNavIcon('${e}')" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-size: 1.1rem; padding: 4px 0; cursor: pointer; transition: all 0.15s ease; text-align: center;" onmouseover="this.style.background='rgba(0,242,255,0.15)'; this.style.borderColor='rgba(0,242,255,0.4)';" onmouseout="this.style.background='rgba(255,255,255,0.04)'; this.style.borderColor='rgba(255,255,255,0.06)';">${e}</button>
                        `).join('')}
                    </div>
                </div>
            `;
        });

        pickerHtml += `
                <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px; display: flex; gap: 6px;">
                    <input type="text" id="custom-emoji-input" placeholder="输入任意 Emoji..." maxlength="4" style="flex: 1; font-size: 0.76rem; padding: 4px 8px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #fff;" onkeydown="if(event.key==='Enter'){ window.selectNavIcon(this.value.trim()); event.preventDefault(); }">
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
