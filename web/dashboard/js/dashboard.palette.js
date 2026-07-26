/**
 * ⌨️ [V80.1] Cmd+P Command Palette
 * 负责全局命令调出、检索与执行
 */

(function () {
    function notify(message, type = 'info') {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else if (window.Swal) {
            const Toast = window.Swal.mixin({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2200,
                timerProgressBar: true,
                background: 'rgba(20, 20, 20, 0.9)',
                color: '#fff',
                customClass: { popup: 'swal2-glass-toast' }
            });
            Toast.fire({ icon: type === 'error' ? 'error' : (type === 'warning' ? 'warning' : 'success'), title: message });
        } else {
            console.log(`[Palette] ${message}`);
        }
    }

    const commands = typeof window.getPaletteCommandsList === 'function' ? window.getPaletteCommandsList() : [];

    let overlay, input, list;
    let selectedIndex = 0;
    let filteredCommands = [];

    function init() {
        // Build DOM
        overlay = document.createElement('div');
        overlay.id = 'command-palette-overlay';
        
        const palette = document.createElement('div');
        palette.id = 'command-palette';
        
        input = document.createElement('input');
        input.id = 'command-palette-input';
        input.type = 'text';
        input.placeholder = 'Search commands... (e.g. publish)';
        input.autocomplete = 'off';
        
        list = document.createElement('ul');
        list.id = 'command-palette-list';
        
        palette.appendChild(input);
        palette.appendChild(list);
        overlay.appendChild(palette);
        document.body.appendChild(overlay);

        // Event Listeners
        document.addEventListener('keydown', handleGlobalKeydown);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closePalette();
        });
        input.addEventListener('input', handleInput);
        input.addEventListener('keydown', handleInputKeydown);
    }

    function handleGlobalKeydown(e) {
        // Listen for Cmd+P / Cmd+K or Ctrl+P / Ctrl+K
        if ((e.metaKey || e.ctrlKey) && (e.key === 'p' || e.key === 'k')) {
            e.preventDefault();
            togglePalette();
        }
        // Close on Esc if active
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
            e.preventDefault();
            closePalette();
        }
    }

    function togglePalette() {
        if (overlay.classList.contains('active')) {
            closePalette();
        } else {
            openPalette();
        }
    }

    function openPalette() {
        overlay.classList.add('active');
        input.value = '';
        
        // Dynamically update command titles based on global state
        const previewCmd = commands.find(c => c.id === 'toggle_preview');
        if (previewCmd) {
            previewCmd.title = window.isLivePreviewActive 
                ? '关闭预览服务 (Stop Live Preview)' 
                : '开启预览服务 (Live Preview Engine)';
            // Let's also update the icon for extra detail
            previewCmd.icon = window.isLivePreviewActive ? '🛑' : '👁️';
        }

        renderList('');
        setTimeout(() => input.focus(), 50); // slight delay for transition
    }

    function closePalette() {
        overlay.classList.remove('active');
        input.blur();
    }

    function handleInput(e) {
        renderList(e.target.value);
    }

    function handleInputKeydown(e) {
        if (filteredCommands.length === 0) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = (selectedIndex + 1) % filteredCommands.length;
            updateSelection();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = (selectedIndex - 1 + filteredCommands.length) % filteredCommands.length;
            updateSelection();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            executeSelected();
        }
    }

    function renderList(query) {
        query = query.toLowerCase().trim();
        if (!query) {
            filteredCommands = [...commands];
        } else {
            filteredCommands = commands.filter(cmd => 
                cmd.title.toLowerCase().includes(query) || 
                cmd.id.toLowerCase().includes(query)
            );
        }

        list.innerHTML = '';
        selectedIndex = 0;

        filteredCommands.forEach((cmd, index) => {
            const li = document.createElement('li');
            li.className = 'palette-item';
            if (index === 0) li.classList.add('selected');
            
            li.innerHTML = `
                <span class="palette-item-icon">${cmd.icon}</span>
                <span class="palette-item-title">${cmd.title}</span>
                <span class="palette-item-shortcut">${cmd.shortcut}</span>
            `;
            
            // Allow click to execute
            li.addEventListener('click', () => {
                selectedIndex = index;
                executeSelected();
            });
            
            list.appendChild(li);
        });
    }

    function updateSelection() {
        const items = list.querySelectorAll('.palette-item');
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    function executeSelected() {
        const cmd = filteredCommands[selectedIndex];
        if (cmd && cmd.action) {
            closePalette();
            // Slight delay to allow modal to close before executing heavy actions
            setTimeout(() => {
                cmd.action();
            }, 150);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
