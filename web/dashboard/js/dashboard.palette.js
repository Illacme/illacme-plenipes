/**
 * ⌨️ [V80.1] Cmd+P Command Palette
 * 负责全局命令调出、检索与执行
 */

(function () {
    function showToast(message, icon = 'success') {
        if (window.Swal) {
            const Toast = window.Swal.mixin({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                background: 'rgba(20, 20, 20, 0.9)',
                color: '#fff',
                customClass: { popup: 'swal2-glass-toast' }
            });
            Toast.fire({ icon: icon, title: message });
        } else {
            console.log(`[Palette] ${message}`);
        }
    }

    const commands = [
        {
            id: 'publish',
            title: '全域发布 (Trigger Publish)',
            icon: '🚀',
            shortcut: 'Enter',
            action: () => {
                if (typeof window.triggerPublish === 'function') {
                    window.triggerPublish();
                } else {
                    showToast('发布接口未就绪', 'error');
                }
            }
        },
        {
            id: 'toggle_preview',
            title: '开启预览服务 (Live Preview Engine)',
            icon: '👁️',
            shortcut: 'Enter',
            action: () => {
                if (typeof window.toggleThemeLab === 'function') {
                    window.toggleThemeLab();
                    showToast('预览服务调起指令已发送');
                } else {
                    showToast('预览服务组件未加载', 'warning');
                }
            }
        },
        {
            id: 'toggle_galaxy',
            title: '知识星图视界 (Toggle Galaxy Graph)',
            icon: '🌌',
            shortcut: 'Enter',
            action: () => {
                // Global view switch to overview first
                if (typeof window.showView === 'function') {
                    // Force close all possible overlay panels to ensure clear view
                    if (typeof window.closeTerminalModal === 'function') window.closeTerminalModal();
                    if (typeof window.closeVaultDrawer === 'function') window.closeVaultDrawer();
                    if (typeof window.closePluginDrawer === 'function') window.closePluginDrawer();
                    if (typeof window.closeEditor === 'function') window.closeEditor();

                    window.showView('overview');
                    setTimeout(() => {
                        // Ensure the command hub overlay is hidden so we can see the 3D galaxy
                        if (typeof window.toggleHub === 'function') window.toggleHub('hide');
                        
                        if (typeof window.initGalaxy === 'function') {
                            window.initGalaxy();
                            showToast('正在进入星图视界...');
                        }
                    }, 100);
                } else {
                    if (typeof window.initGalaxy === 'function') {
                        window.initGalaxy();
                        showToast('正在进入星图视界...');
                    } else {
                        showToast('星图引擎未加载', 'error');
                    }
                }
            }
        },
        {
            id: 'clean_orphans',
            title: '清理悬空资产 (Clean Orphans)',
            icon: '🧹',
            shortcut: 'Enter',
            action: () => {
                if (typeof window.apiFetch === 'function') {
                    window.apiFetch('/api/governance/gc', { method: 'POST' })
                        .then(res => {
                            showToast('清理指令已发送至后台引擎');
                            if (typeof window.addAudit === 'function') {
                                window.addAudit("已触发悬空资产清理指令", "INFO");
                            }
                        })
                        .catch(err => {
                            console.error(err);
                            showToast('清理指令发送失败', 'error');
                        });
                } else {
                    showToast('API 模块未就绪', 'error');
                }
            }
        }
    ];

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
        // Listen for Cmd+P or Ctrl+P
        if ((e.metaKey || e.ctrlKey) && e.key === 'p') {
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
