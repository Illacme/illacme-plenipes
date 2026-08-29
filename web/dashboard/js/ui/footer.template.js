/**
 * 🚀 Illacme Plenipes UI - Main Footer Template Shard
 * 职责：底部 Sovereign OS Bar 心跳、遥测指标（CPU、内存、算力费用、Token）、连接质量与明暗主题模式选择器 DOM 动态挂载。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.ensureMainFooterMounted = function () {
    const footer = document.getElementById('main-footer');
    if (!footer || footer.children.length > 0) return;

    footer.innerHTML = `
        <div class="footer-left">
            <div class="heartbeat-container">
                <div class="heartbeat-line"></div>
            </div>
            <div class="status-indicator">
                <span id="system-status-label" class="tiny-label">ENGINE ONLINE</span>
            </div>
            <div id="audit-summary-text" class="audit-summary-mini">WAITING FOR COMMAND...</div>
        </div>

        <div class="footer-center">
            <div class="telemetry-item">
                <span class="t-label">CPU LOAD:</span>
                <span class="t-value" id="footer-cpu-val">--%</span>
            </div>
            <div class="telemetry-divider"></div>
            <div class="telemetry-item">
                <span class="t-label">MEMORY:</span>
                <span class="t-value" id="footer-mem-val">--%</span>
            </div>
            <div class="telemetry-divider"></div>
            <div class="telemetry-item">
                <span class="t-label">AI CREDIT:</span>
                <span class="t-value" id="footer-ai-cost">$0.0000</span>
            </div>
            <div class="telemetry-divider"></div>
            <div class="telemetry-item">
                <span class="t-label">TOKENS:</span>
                <span class="t-value" id="footer-ai-tokens">0</span>
            </div>
        </div>

        <div class="footer-right">
            <div class="connectivity-matrix">
                <div class="active-seats">
                    <span class="t-label">SEATS:</span>
                    <span class="t-value">1/2</span>
                </div>
                <div class="link-quality">
                    <div class="signal-bar active"></div>
                    <div class="signal-bar active"></div>
                    <div class="signal-bar active"></div>
                    <div class="signal-bar"></div>
                </div>
                <div class="ws-status-box">
                    <span id="ws-status" class="status-val online">CONNECTED</span>
                </div>
            </div>
            <div class="version-tag tiny">v50.3_STABLE</div>
            <select id="theme-mode-select"
                style="margin-left: 10px; font-size: 0.65rem; padding: 2px 24px 2px 8px; border-radius: 6px; border: 1px solid var(--glass-border); background-color: var(--white-05); color: var(--text-bright); outline: none; cursor: pointer; transition: all 0.3s;"
                onchange="if(window.ThemeModeManager) ThemeModeManager.applySetting(this.value)" title="Theme Mode">
                <option value="dark">🌙 Dark Mode</option>
                <option value="light">☀️ Light Mode</option>
                <option value="auto">⏳ Auto Mode</option>
            </select>
        </div>
    `;
};

// 自动挂载主底栏
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.ensureMainFooterMounted);
} else {
    window.ensureMainFooterMounted();
}
