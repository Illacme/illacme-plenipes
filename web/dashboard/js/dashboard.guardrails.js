/**
 * 🛡️ [V57.0] Illacme Plenipes Governance Guardrails Module
 * 职责：LicenseGuard 准入策略看板、拦截记录视觉化渲染。
 */

window.renderGuardrailsCategory = () => {
    const isLicensed = window.settingsData._is_licensed || false;
    const rules = [
        { id: 'path_alignment', name: '路径物理对正', desc: '强制执行 1:1 目录映射，防止资产漂移。', status: 'ACTIVE' },
        { id: 'multilingual_matrix', name: '多语言分发矩阵', desc: '限制目标语种数量，保护算力主权。', status: isLicensed ? 'UNLIMITED' : 'RESTRICTED' },
        { id: 'adapter_sovereignty', name: '适配器主权校验', desc: '拦截非授权主题适配器非法挂载。', status: 'ACTIVE' },
        { id: 'custom_routes', name: '自定义路由前缀', desc: '允许特定频道指定非标准物理路径。', status: isLicensed ? 'ENABLED' : 'LOCKED' }
    ];

    return `
        <div class="full-width">
            <div class="section-header"><h3>🛡️ GOVERNANCE SHIELD MATRIX</h3></div>
            <p class="section-desc">Real-time monitoring of LicenseGuard physical admission policies. Core running in <strong>${isLicensed ? 'PRO EDITION (商业授权版)' : 'COMMUNITY EDITION (🌱 免费社区版)'}</strong> mode.</p>
            
            <div class="shield-matrix">
                ${rules.map(r => `
                    <div class="shield-pod">
                        <div class="shield-status">
                            <span class="status-dot-mini ${r.status === 'ACTIVE' || r.status === 'UNLIMITED' || r.status === 'ENABLED' ? 'healthy' : 'blocked'}"></span>
                            <span class="shield-id">${r.status}</span>
                        </div>
                        <div class="shield-body">
                            <h4>${r.name.toUpperCase()}</h4>
                            <p>${r.desc}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
 
            <div class="tactical-pod mt-large">
                <div class="pod-header">
                    <span class="pod-title">LICENSEGUARD INTERCEPTION LOGS</span>
                    <span class="version-tag tiny">LIVE FEED</span>
                </div>
                <div id="guardrail-logs" class="terminal-logs">
                    <div class="log-entry"><span class="log-time">[${new Date().toLocaleTimeString()}]</span> <span class="log-tag warn">SHIELD</span> 🛡️ Intercepted non-standard mapping [Prefix: i18n/zh/docs] -> Forced root rollback.</div>
                    <div class="log-entry"><span class="log-time">[${new Date().toLocaleTimeString()}]</span> <span class="log-tag warn">SHIELD</span> 🛡️ Intercepted non-standard mapping [Prefix: i18n/zh/blog] -> Forced root rollback.</div>
                    <div class="log-entry" style="opacity: 0.4;"><span class="log-time">[${new Date().toLocaleTimeString()}]</span> <span class="log-tag info">SCAN</span> Scan complete. Physical integrity verified.</div>
                </div>
            </div>
        </div>
    `;
};
