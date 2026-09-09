/**
 * 🌍 [V75.6] Illacme Plenipes Localization - Cross-Theme Link Doctor Shard
 * 职责：跨主题与多语言内链健康巡检可视化中枢，支持 6 大主流 SSG 一键体检与面向创作者友好的深度诊断。
 * 规范：严格符合 SOP-01 (≤ 300 行) 与 SOP-03 (高档毛玻璃视觉主权)。
 */

(function () {
    window.linkDoctorState = {
        lastReport: null,
        isAuditing: false,
        activeFilter: 'all' // all | error | warning
    };

    const THEMES = [
        { id: "sovereign", name: "Sovereign 原生", icon: "👑", highlight: "原生极速分发，相对超链与站内锚点 100% 畅通" },
        { id: "universal", name: "Universal 通用", icon: "🌐", highlight: "多语种博客中心与静态归档零 404" },
        { id: "nextra", name: "Nextra (Next.js)", icon: "▲", highlight: "自动消除 docs/ 假前缀，平铺根路由智能自愈" },
        { id: "docusaurus", name: "Docusaurus", icon: "🦖", highlight: "文档频道与多语种 Slug 拓扑全自动对齐" },
        { id: "starlight", name: "Starlight (Astro)", icon: "🌟", highlight: "Clean URL 绝对路径防重叠，外语前缀防迷航" },
        { id: "vitepress", name: "VitePress (Vue)", icon: "⚡", highlight: "深层 Markdown 相对路径与 Vue 路由无缝衔接" }
    ];

    window.renderLinkDoctorCard = function () {
        const state = window.linkDoctorState;
        const report = state.lastReport;
        const isAuditing = state.isAuditing;

        const totalFiles = report ? report.total_files : '--';
        const totalLinks = report ? report.total_links : '--';
        const rawIssues = report ? (report.issues || []) : [];
        const criticals = rawIssues.filter(i => i.level === 'CRITICAL' || i.level === 'ERROR');
        const warnings = rawIssues.filter(i => i.level === 'WARNING');

        // 状态角标
        let statusBadge = `
            <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.76rem; font-weight: 600; background: rgba(0, 245, 255, 0.08); border: 1px solid rgba(0, 245, 255, 0.25); color: var(--accent-primary, #00f2ff);">
                <span>✨</span> 待体检 (Ready)
            </span>
        `;
        if (report) {
            if (criticals.length === 0 && warnings.length === 0) {
                statusBadge = `
                    <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.76rem; font-weight: 600; background: rgba(0, 255, 136, 0.12); border: 1px solid rgba(0, 255, 136, 0.35); color: #00ff88;">
                        <span>🛡️</span> 6 大主题全绿 (0 死链)
                    </span>
                `;
            } else if (criticals.length > 0) {
                statusBadge = `
                    <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.76rem; font-weight: 600; background: rgba(255, 77, 79, 0.15); border: 1px solid rgba(255, 77, 79, 0.4); color: #ff4d4f;">
                        <span>⚠️</span> 发现 ${criticals.length} 处失效死链
                    </span>
                `;
            } else {
                statusBadge = `
                    <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.76rem; font-weight: 600; background: rgba(255, 179, 0, 0.15); border: 1px solid rgba(255, 179, 0, 0.35); color: #ffb300;">
                        <span>💡</span> 存在 ${warnings.length} 处体验优化建议
                    </span>
                `;
            }
        }

        const displayedIssues = state.activeFilter === 'error' ? criticals : (state.activeFilter === 'warning' ? warnings : rawIssues);

        return `
            <div id="link-doctor-card-container" class="settings-group" style="margin-bottom: 2rem; position: relative;">
                <div class="glass-panel" style="padding: 22px 24px; border-radius: 12px; border: 1px solid rgba(0, 245, 255, 0.18); background: rgba(15, 23, 42, 0.65); box-shadow: 0 8px 32px rgba(0,0,0,0.35); backdrop-filter: blur(12px);">
                    
                    <!-- 顶部标题与一键体检操作 -->
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 18px; flex-wrap: wrap;">
                        <div>
                            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace; display: flex; align-items: center; gap: 8px;">
                                    <span>🛰️</span> 跨主题内链健康体检中枢 (Link Doctor)
                                </h4>
                                ${statusBadge}
                            </div>
                            <p class="section-desc" style="margin: 6px 0 0 0; font-size: 0.8rem; color: var(--text-dim, #94a3b8); line-height: 1.5;">
                                深度仿真 6 大主流装帧主题在多语种矩阵下的链接转译结果，帮助创作者在发布前消除 404 与路径失效隐患。
                            </p>
                        </div>
                        <button id="btn-trigger-link-doctor" class="control-btn" 
                                onclick="window.triggerLinkDoctorAudit()" 
                                ${isAuditing ? 'disabled' : ''}
                                style="padding: 8px 18px; font-size: 0.82rem; font-weight: 700; border-radius: 8px; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); color: #050b14; border: none; cursor: ${isAuditing ? 'not-allowed' : 'pointer'}; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3); transition: all 0.2s;">
                            <span style="${isAuditing ? 'animation: spin 1s linear infinite; display: inline-block;' : ''}">${isAuditing ? '🔄' : '🩺'}</span>
                            <span>${isAuditing ? '正在深度体检...' : '启动全库内链体检'}</span>
                        </button>
                    </div>

                    <!-- 6 大主流主题适配状态矩阵 -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; margin-bottom: 18px;">
                        ${THEMES.map(t => {
                            const isThemeOk = !rawIssues.some(i => i.theme === t.id && (i.level === 'CRITICAL' || i.level === 'ERROR'));
                            const color = report ? (isThemeOk ? '#00ff88' : '#ff4d4f') : 'var(--text-dim, #94a3b8)';
                            const bg = report ? (isThemeOk ? 'rgba(0, 255, 136, 0.08)' : 'rgba(255, 77, 79, 0.1)') : 'rgba(255,255,255,0.03)';
                            return `
                                <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; padding: 7px 12px; border-radius: 6px; background: ${bg}; border: 1px solid rgba(255,255,255,0.06); font-size: 0.74rem;">
                                    <div style="display: flex; align-items: center; gap: 6px;">
                                        <span>${t.icon}</span>
                                        <span style="color: #fff; font-weight: 600;">${t.name}</span>
                                    </div>
                                    <span style="color: ${color}; font-family: monospace; font-weight: 700;">${report ? (isThemeOk ? '✓ 畅通' : '✗ 异常') : '待检'}</span>
                                </div>
                            `;
                        }).join('')}
                    </div>

                    <!-- 核心指标统计卡片 -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 16px;">
                        <div style="padding: 10px 14px; background: rgba(0,0,0,0.25); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.72rem; color: var(--text-dim, #94a3b8);">文库扫描原稿</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #fff; margin-top: 2px;">${totalFiles} <span style="font-size: 0.75rem; font-weight: 400; color: var(--text-dim);">篇</span></div>
                        </div>
                        <div style="padding: 10px 14px; background: rgba(0,0,0,0.25); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.72rem; color: var(--text-dim, #94a3b8);">校验内链总数</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: var(--accent-primary, #00f2ff); margin-top: 2px;">${totalLinks} <span style="font-size: 0.75rem; font-weight: 400; color: var(--text-dim);">条</span></div>
                        </div>
                        <div style="padding: 10px 14px; background: rgba(0,0,0,0.25); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="font-size: 0.72rem; color: var(--text-dim, #94a3b8);">跨主题健康度</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #00ff88; margin-top: 2px;">${criticals.length === 0 ? '100%' : Math.max(0, 100 - criticals.length * 10) + '%'}</div>
                        </div>
                    </div>

                    <!-- 面向创作者的友好呈现区 -->
                    ${report ? (rawIssues.length === 0 ? `
                        <!-- 🟢 100% 畅通通过时：贴心正向保障反馈 -->
                        <div style="padding: 14px 16px; background: rgba(0, 255, 136, 0.06); border: 1px solid rgba(0, 255, 136, 0.25); border-radius: 8px; margin-top: 10px;">
                            <div style="font-size: 0.82rem; font-weight: 700; color: #00ff88; display: flex; align-items: center; gap: 8px;">
                                <span>🎉</span> 您的文库内链状态极佳，已通过全系 6 大主题多语言兼容认证！
                            </div>
                            <div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 6px; line-height: 1.6;">
                                所有相对链接、双向链接与多语言前缀已全部完成虚拟转译断言。无论您切换至 <b>Nextra、Starlight、Docusaurus、VitePress、Universal</b> 还是 <b>Sovereign 原生主题</b>，读者点击超链接均能丝滑跳转，无任何 404 风险。
                            </div>
                        </div>
                    ` : `
                        <!-- 🔴/🟡 发现问题时：亲和、结构化、带修复建议的卡片面板 -->
                        <div style="margin-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 14px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                                <div style="font-size: 0.82rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 6px;">
                                    <span>📋</span> 巡检报告详情与优化指引 (${displayedIssues.length}/${rawIssues.length})
                                </div>
                                <div style="display: flex; gap: 6px;">
                                    <button class="control-btn" onclick="window.setLinkDoctorFilter('all')" style="padding: 3px 10px; font-size: 0.72rem; border-radius: 4px; background: ${state.activeFilter === 'all' ? 'rgba(0, 242, 254, 0.2)' : 'rgba(255,255,255,0.05)'}; color: ${state.activeFilter === 'all' ? 'var(--accent-primary, #00f2ff)' : 'var(--text-dim)'}; border: 1px solid ${state.activeFilter === 'all' ? 'var(--accent-primary, #00f2ff)' : 'transparent'}; cursor: pointer;">全部 (${rawIssues.length})</button>
                                    <button class="control-btn" onclick="window.setLinkDoctorFilter('error')" style="padding: 3px 10px; font-size: 0.72rem; border-radius: 4px; background: ${state.activeFilter === 'error' ? 'rgba(255, 77, 79, 0.2)' : 'rgba(255,255,255,0.05)'}; color: ${state.activeFilter === 'error' ? '#ff4d4f' : 'var(--text-dim)'}; border: 1px solid ${state.activeFilter === 'error' ? '#ff4d4f' : 'transparent'}; cursor: pointer;">死链 (${criticals.length})</button>
                                    <button class="control-btn" onclick="window.setLinkDoctorFilter('warning')" style="padding: 3px 10px; font-size: 0.72rem; border-radius: 4px; background: ${state.activeFilter === 'warning' ? 'rgba(255, 179, 0, 0.2)' : 'rgba(255,255,255,0.05)'}; color: ${state.activeFilter === 'warning' ? '#ffb300' : 'var(--text-dim)'}; border: 1px solid ${state.activeFilter === 'warning' ? '#ffb300' : 'transparent'}; cursor: pointer;">优化建议 (${warnings.length})</button>
                                </div>
                            </div>

                            <div style="max-height: 240px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 4px;">
                                ${displayedIssues.map((iss, idx) => {
                                    const isErr = iss.level === 'CRITICAL' || iss.level === 'ERROR';
                                    const borderClr = isErr ? '#ff4d4f' : '#ffb300';
                                    const badgeBg = isErr ? 'rgba(255, 77, 79, 0.15)' : 'rgba(255, 179, 0, 0.15)';
                                    const badgeTxt = isErr ? '🔴 失效死链' : '💡 建议优化';
                                    const title = iss.friendly_title || iss.message || '链接异常';
                                    const cause = iss.friendly_cause || iss.message || '链接转译未达预期。';
                                    const suggestion = iss.friendly_suggestion || '请在文稿中核实该超链接书写是否正确。';

                                    return `
                                        <div style="padding: 12px 14px; border-radius: 8px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.06); border-left: 4px solid ${borderClr};">
                                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px;">
                                                <div style="display: flex; align-items: center; gap: 8px;">
                                                    <span style="font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: ${badgeBg}; color: ${borderClr};">${badgeTxt}</span>
                                                    <span style="font-size: 0.82rem; font-weight: 700; color: #fff;">${title}</span>
                                                </div>
                                                <div style="font-size: 0.7rem; color: #94a3b8; font-family: monospace;">
                                                    <span>主题: ${iss.theme}</span> · <span>语种: ${iss.lang}</span>
                                                </div>
                                            </div>
                                            <div style="font-size: 0.74rem; color: var(--text-dim, #94a3b8); margin-bottom: 6px;">
                                                <span>📄 原稿文件: <b style="color: #cbd5e1;">${iss.file || '未指定文稿'}</b></span> · 
                                                <span>🔗 链接目标: <code style="color: var(--accent-primary, #00f2ff); background: rgba(0,0,0,0.3); padding: 1px 4px; border-radius: 3px;">${iss.alias || iss.url}</code></span>
                                            </div>
                                            <div style="font-size: 0.73rem; color: #e2e8f0; line-height: 1.5; margin-bottom: 6px;">
                                                <span style="color: #94a3b8;">原因分析：</span>${cause}
                                            </div>
                                            <div style="font-size: 0.73rem; color: #00ff88; line-height: 1.5; padding: 6px 10px; background: rgba(0, 255, 136, 0.06); border-radius: 4px;">
                                                <span style="font-weight: 600;">💡 解决建议：</span>${suggestion}
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    `) : ''}

                </div>
            </div>
        `;
    };

    window.setLinkDoctorFilter = function (filter) {
        window.linkDoctorState.activeFilter = filter;
        const container = document.getElementById('link-doctor-card-container');
        if (container) {
            container.outerHTML = window.renderLinkDoctorCard();
        }
    };

    window.triggerLinkDoctorAudit = async function () {
        if (window.linkDoctorState.isAuditing) return;
        window.linkDoctorState.isAuditing = true;
        
        const container = document.getElementById('link-doctor-card-container');
        if (container) {
            container.outerHTML = window.renderLinkDoctorCard();
        }

        try {
            const headers = window.getAuthHeaders ? window.getAuthHeaders() : { 'Content-Type': 'application/json' };
            const resp = await fetch('/api/governance/link-doctor/audit', { headers });
            const data = await resp.json();
            
            window.linkDoctorState.lastReport = data;
            window.linkDoctorState.isAuditing = false;

            const updatedContainer = document.getElementById('link-doctor-card-container');
            if (updatedContainer) {
                updatedContainer.outerHTML = window.renderLinkDoctorCard();
            }

            if (window.showToast) {
                const total = data.total_files || 0;
                const errs = (data.issues || []).filter(i => i.level === 'CRITICAL' || i.level === 'ERROR').length;
                if (errs === 0) {
                    window.showToast(`✨ 全库 6 大主题内链体检通过！共扫描 ${total} 篇原稿，0 处死链异常。`, 'success');
                } else {
                    window.showToast(`⚠️ 发现 ${errs} 处跨主题链接异常，请在下方列表查看详细指引。`, 'warning');
                }
            }
        } catch (e) {
            console.error('Link doctor audit failed:', e);
            window.linkDoctorState.isAuditing = false;
            const updatedContainer = document.getElementById('link-doctor-card-container');
            if (updatedContainer) {
                updatedContainer.outerHTML = window.renderLinkDoctorCard();
            }
            if (window.showToast) {
                window.showToast('内链体检网络请求失败: ' + e.message, 'error');
            }
        }
    };
})();
