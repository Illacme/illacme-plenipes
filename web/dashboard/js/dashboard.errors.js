/**
 * 🛡️ [V1.0] Illacme Plenipes Global Error Boundary
 * Catch all unhandled exceptions and render an elegant diagnostic overlay.
 */

(function () {
    const ErrorBoundary = {
        init() {
            window.addEventListener('error', (event) => {
                this.handleError(event.error || new Error(event.message || 'Unknown Execution Error'));
            });

            window.addEventListener('unhandledrejection', (event) => {
                let error = event.reason;
                if (!(error instanceof Error)) {
                    error = new Error(typeof error === 'string' ? error : JSON.stringify(error));
                }
                // 对于非致命异步网络或数据流异常，降级显示为 Toast，防止强制降级系统红屏
                this.handleAsyncError(error);
            });
            
            // Expose manual trigger for subsystems like WebGL context lost
            window.showSystemError = (title, message, stack) => {
                const err = new Error(message);
                err.name = title;
                err.stack = stack || '';
                this.handleError(err, title);
            };
        },

        handleAsyncError(error) {
            console.warn('[Plenipes Sovereign Guard] Intercepted Async Rejection:', error);
            const message = error.message || '网络或数据流通道发生异常';
            
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    toast: true,
                    position: 'bottom-end',
                    icon: 'warning',
                    title: '异步链路中断',
                    text: message,
                    showConfirmButton: false,
                    timer: 5000,
                    background: 'rgba(20, 15, 10, 0.95)',
                    color: '#ffb34c'
                });
            }
            if (typeof window.addAudit === 'function') {
                window.addAudit(`⚠️ [NET FAULT] 异步链路受阻: ${message}`);
            }
        },

        handleError(error, customTitle) {
            console.error('[Plenipes Sovereign Guard] Intercepted Error:', error);
            const title = customTitle || error.name || 'Fatal Error';
            const message = error.message || 'A critical subsystem encountered an unexpected fault.';
            const stack = error.stack || 'No stack trace available.';

            this.renderOverlay(title, message, stack);
        },

        renderOverlay(title, message, stack) {
            let overlay = document.getElementById('global-error-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'global-error-overlay';
                overlay.className = 'global-error-overlay';
                document.body.appendChild(overlay);
            }

            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            const reloadHint = isMac ? 'Cmd + R' : 'Ctrl + R';

            overlay.innerHTML = `
                <div class="error-modal-glass">
                    <div class="error-modal-header">
                        <span class="error-icon">⚠️</span>
                        <h2>SYSTEM DEGRADED / 核心子系统异常</h2>
                    </div>
                    <div class="error-modal-body">
                        <div class="error-summary">
                            <span class="error-badge">${title}</span>
                            <span class="error-message">${message}</span>
                        </div>
                        <div class="error-terminal">
                            <div class="terminal-header">
                                <span>DIAGNOSTICS_TRACE.LOG</span>
                                <button class="mini-btn copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('err-stack').innerText).then(()=>this.innerText='Copied!')">Copy</button>
                            </div>
                            <pre id="err-stack"><code>${stack}</code></pre>
                        </div>
                    </div>
                    <div class="error-modal-footer">
                        <p class="hint">The system has halted faulty operations to prevent data corruption.</p>
                        <div class="error-actions" style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <button class="btn secondary-btn" onclick="document.getElementById('global-error-overlay').style.display='none'">Dismiss Warning</button>
                            <button class="btn secondary-btn" style="border-color: var(--accent-secondary); color: var(--accent-secondary);" onclick="localStorage.clear(); sessionStorage.clear(); window.location.reload();">🏥 一键自愈重载</button>
                            <button class="btn primary-btn error-btn" onclick="window.location.reload()">Reload Subsystem (${reloadHint})</button>
                        </div>
                    </div>
                </div>
            `;
            
            overlay.style.display = 'flex';
        }
    };

    // Auto-initialize as early as possible
    ErrorBoundary.init();
})();
