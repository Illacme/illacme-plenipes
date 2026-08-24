/**
 * 🛡️ [V103.0] Illacme Plenipes Security Audit & Governance Render Component
 * 职责：系统设置中的“系统安全与审计”选项卡 DOM 的渲染。
 * 遵循 SOP-01 单文件 300 行限额规则。
 */

(function() {
    function renderSecurityCategory() {
        const sys = window.settingsData?.system || {};
        const gov = window.settingsData?.governance || {};
        const rg = gov.resource_guard || { cpu_threshold: 85, compute_ram_threshold: 50.0 };
        
        setTimeout(() => {
            if (typeof window.loadAndRenderConfigAudit === 'function') {
                window.loadAndRenderConfigAudit();
            }
            if (typeof window.loadAndRenderOperationAuditLogs === 'function') {
                window.loadAndRenderOperationAuditLogs();
            }
            if (typeof window.loadAndRenderAiLessonsVisualizer === 'function') {
                window.loadAndRenderAiLessonsVisualizer();
            }
        }, 50);

        const secSubDescs = {
            policy: '💡 配置后端 API 令牌、全站日志、CPU 红线与 AI 内存削峰控制。',
            topology: '💡 可视化展示全局主主权配置、品牌品牌覆盖与环境变量的层级继承树结构。',
            logs: '💡 实时查阅后端守护进程与控制中心的关键操作与变更安全审计日志。',
            lessons: '💡 查阅 AI 引擎自动修正格式异常与超链接失效的历史自愈教训库。'
        };

        if (!window.switchSecuritySubTab) {
            window.switchSecuritySubTab = (subTab, btn) => {
                const container = document.getElementById('security-sub-tab-bar');
                if (container) {
                    const btns = container.querySelectorAll('.sub-tab-btn');
                    btns.forEach(b => b.classList.remove('active'));
                }
                if (btn) {
                    btn.classList.add('active');
                } else if (typeof event !== 'undefined' && event) {
                    event.currentTarget.classList.add('active');
                }

                const panels = ['policy', 'topology', 'logs', 'lessons'];
                panels.forEach(p => {
                    const el = document.getElementById(`sec-panel-${p}`);
                    if (el) el.style.display = (p === subTab) ? 'block' : 'none';
                });

                const descEl = document.getElementById('sec-sub-tab-desc');
                if (descEl) descEl.innerHTML = secSubDescs[subTab] || '';

                if (typeof window.updateSaveButtonVisibility === 'function') {
                    window.updateSaveButtonVisibility(subTab);
                }
            };
        }

        return `
            <div class="category-header-banner" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; padding: 18px 22px; background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">🛡️ 系统安全与审计</h2>
                    </div>
                </div>

                <div class="sub-tab-navigation-bar" id="security-sub-tab-bar" style="display: flex; gap: 8px; margin-top: 10px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <button type="button" class="sub-tab-btn active" onclick="window.switchSecuritySubTab('policy', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🛡️ 安全策略</button>
                    <button type="button" class="sub-tab-btn" onclick="window.switchSecuritySubTab('topology', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🗺️ 配置继承</button>
                    <button type="button" class="sub-tab-btn" onclick="window.switchSecuritySubTab('logs', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📜 操作账本</button>
                    <button type="button" class="sub-tab-btn" onclick="window.switchSecuritySubTab('lessons', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🧠 教训自愈</button>
                </div>

                <div id="sec-sub-tab-desc" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
                    ${secSubDescs['policy']}
                </div>
            </div>

            <div class="tab-sub-content-wrapper">
                <div id="sec-panel-policy">
                    <div class="settings-grid">
                        ${renderSettingsItem('API 访问令牌 (Token)', 'system.api_token', sys.api_token || '', 'password', {
                            placeholder: '保持为空则不启用认证',
                            description: '后端 Web API 网关身份校验 Token，保持留空表示无密码访问。'
                        })}
                        ${renderSettingsItem('日志输出级别', 'system.log_level', sys.log_level || 'INFO', 'select', {
                            items: [
                                {value: 'DEBUG', text: 'DEBUG (全量输出)'},
                                {value: 'INFO', text: 'INFO (常规运行)'},
                                {value: 'WARNING', text: 'WARNING (仅告警)'},
                                {value: 'ERROR', text: 'ERROR (仅异常)'}
                            ],
                            description: '控制服务器后端在终端与日志文件中输出的详细程度。'
                        })}
                        ${renderSettingsItem('启用资产安全审计', 'system.enable_asset_audit', sys.enable_asset_audit ?? true, 'checkbox', {
                            description: '开启后，系统在编译原稿时会自动审计和监控静态资产与外部链接的合法性。'
                        })}
                        ${renderSettingsItem('资源负载红线 (%)', 'governance.resource_guard.cpu_threshold', rg.cpu_threshold ?? 85, 'number', {
                            description: 'CPU 负载警戒红线（%）。当宿主机 CPU 占用率持续高于此阈值时，自动平滑降低并发算力。'
                        })}
                        ${renderSettingsItem('本地算力内存削峰警戒线 (%)', 'governance.resource_guard.compute_ram_threshold', rg.compute_ram_threshold ?? 50.0, 'number', {
                            description: '当本地大模型（如 Ollama / LM Studio 等）常驻物理内存占用宿主机总内存比例超过此阈值时，自动降低 AI 并发以防宿主崩溃。'
                        })}
                    </div>
                </div>

                <div id="sec-panel-topology" style="display: none;">
                    <div id="config-audit-topology-container"></div>
                </div>

                <div id="sec-panel-logs" style="display: none;">
                    <div id="operation-audit-logs-container"></div>
                </div>

                <div id="sec-panel-lessons" style="display: none;">
                    <div id="ai-lessons-visualizer-container"></div>
                </div>
            </div>
        `;
    }

    window.renderSecurityCategory = renderSecurityCategory;
})();
