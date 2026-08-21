/**
 * 🩺 [V55.0] Illacme Plenipes Health Rendering Module
 * 职责：系统健康状态矩阵 HTML 动态渲染装配、页脚状态信息刷新与预览服务指挥终端 Modal 绑定。
 */

window.refreshHealthMatrix = async () => {
    const container = document.getElementById('health-matrix-container');
    if (!container) return;

    const matrix = await apiFetch('/api/system/health/matrix');
    
    // 🚀 [V55.0] 增强型防抖与容错：如果接口返回异常，保持上一次的状态而不是清空
    if (!matrix || Object.keys(matrix).length === 0) {
        if (container.innerHTML === "" || container.querySelector('.loading')) {
            container.innerHTML = `<div class="health-node"><div class="node-status">DISCONNECTED</div></div>`;
        }
        return;
    }

    const html = Object.entries(matrix).map(([id, info]) => {
        let actions = '';
        if (id === 'preview') {
            actions = `
                <div class="node-actions">
                    <button class="mini-action-btn" title="服务管理" onclick="showServiceManager('preview')">⚙️</button>
                    <button class="mini-action-btn" title="打开预览" onclick="window.open('http://localhost:' + (window.settingsData.system?.serve_port || 43213), '_blank')">🌐</button>
                </div>
            `;
        } else if (id === 'onboarding') {
            const isActive = info.status === 'active';
            actions = `
                <div class="node-actions">
                    ${isActive ? 
                        `<button class="mini-action-btn" title="停止向导" onclick="controlWizard('stop')">⏹️</button>
                         <button class="mini-action-btn" title="进入向导" onclick="window.open('http://localhost:43211', '_blank')">🚀</button>` : 
                        `<button class="mini-action-btn" title="版图向导" onclick="controlWizard('start')">▶️</button>`
                    }
                </div>
            `;
        }
        return `
            <div class="health-node">
                <div class="status-dot-mini status-${info.status || 'offline'} ${id === 'dashboard' ? 'pulsing' : ''}"></div>
                <div class="node-info">
                    <div class="node-label">${info.label || id}</div>
                    <div class="node-status">${info.status || 'offline'}</div>
                </div>
                ${actions}
            </div>
        `;
    }).join('');
    
    if (container.innerHTML !== html) {
        container.innerHTML = html;
    }
};

window.updateHealthUI = (health) => {
    if (!health) return;
    const statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.innerText = `健康度: ${health.status?.toUpperCase()} (${health.imprint || 'N/A'})`;
    }
};

window.renderServiceToolbar = () => {
    return `
        <button class="mini-action-btn" id="btn-modal-restart" onclick="invokeServiceAction('restart')" style="margin-right: 8px;"><span>🔄</span> 重启服务</button>
        <button class="mini-action-btn" id="btn-modal-stop" onclick="invokeServiceAction('stop')" style="border-color: #ff4d4d; color: #ff4d4d; margin-right: 8px;"><span>⏹️</span> 停止服务</button>
        <button class="mini-action-btn" id="btn-modal-open" onclick="window.open('http://localhost:43213', '_blank')" style="border-color: #00ff88; color: #00ff88; margin-right: 12px;"><span>🌐</span> 打开预览</button>
        <div style="width: 1px; height: 18px; background: var(--glass-border); margin: 0 12px;"></div>
        <button class="mini-action-btn" id="btn-modal-reinstall" onclick="invokeServiceAction('install')" style="border-color: #ffaa00; color: #ffaa00; margin-right: 8px;"><span>🏗️</span> 补全依赖</button>
        <button class="mini-action-btn" id="btn-modal-upgrade" onclick="invokeServiceAction('upgrade')" style="border-color: var(--neon-cyan); color: var(--neon-cyan); margin-right: 8px;"><span>🆙</span> 升级版本</button>
        <button class="mini-action-btn" id="btn-modal-rollback" onclick="invokeServiceAction('rollback')" style="border-color: #ff4d4d; color: #ff4d4d;"><span>⏪</span> 环境复原</button>
        <div style="flex: 1;"></div>
        <button class="mini-action-btn" onclick="document.getElementById('terminal-output').innerHTML = ''"><span>🗑️</span> 清空屏幕</button>
    `;
};

window.showServiceManager = (service) => {
    if (service === 'preview') {
        // 🚀 [V55.9] 物理对正：打开全功能 SSG 容器指挥中心
        const modal = document.getElementById('terminal-modal');
        if (modal) {
            modal.style.display = 'flex';
            modal.dataset.context = 'service_preview';
            document.getElementById('terminal-title').innerText = "🛰️ 预览服务主权指挥中心";
            
            const toolbar = document.getElementById('terminal-toolbar');
            if (toolbar) {
                toolbar.style.display = 'flex';
                toolbar.innerHTML = window.renderServiceToolbar();
            }
            
            const out = document.getElementById('terminal-output');
            if (out && (modal.dataset.lastContext !== 'service_preview' || out.innerHTML.trim() === "")) {
                out.innerHTML = `<div class="term-line" style="color:#888">[${new Date().toLocaleTimeString()}] 控制台已就绪，请选择上方治理指令。</div>`;
            }
            modal.dataset.lastContext = 'service_preview';
            
            // 🛡️ 单例彻底隔离：重置所有页脚控件，只点亮服务管理需要的「关闭」按钮
            if (typeof window.resetTerminalModalFooter === 'function') {
                window.resetTerminalModalFooter();
            }
            const okBtn = document.getElementById('btn-terminal-ok');
            if (okBtn) {
                okBtn.style.display = 'inline-flex';
                okBtn.innerText = '关闭';
            }
            
            // 实时同步当前节点状态至终端状态栏
            const labels = Array.from(document.querySelectorAll('.node-label'));
            const previewLabel = labels.find(el => el.innerText.includes("预览服务"));
            const container = previewLabel ? previewLabel.closest('.health-node') : null;
            const currentStatus = container ? container.querySelector('.node-status').innerText.toUpperCase() : 'OFFLINE';
            
            const statusEl = document.getElementById('terminal-status');
            if (statusEl) statusEl.innerText = currentStatus;
        }
    }
};
