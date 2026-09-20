/**
 * 🛰️ [V1.0] Dashboard Core - Deployment Summary & Health Radar Shard
 * 职责：承载全域发布完成卡片渲染 (renderDeploymentSummaryCard)、站点连通性健康雷达 (runHealthRadar)、全网访问链接管理与主站直达。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window._latestPrimaryLiveUrl = "";

    window.openPrimaryLiveSite = () => {
        if (window._latestPrimaryLiveUrl) {
            window.open(window._latestPrimaryLiveUrl, '_blank', 'noopener,noreferrer');
        } else {
            if (typeof window.showToast === 'function') {
                window.showToast('未检测到有效的主站线上访问地址', 'warning');
            }
        }
    };

    window.copyAllLiveUrls = async (urls) => {
        try {
            const text = urls.join('\n');
            await navigator.clipboard.writeText(text);
            if (typeof window.showToast === 'function') {
                window.showToast('已复制全网访问地址至剪贴板 📋', 'success');
            }
        } catch(e) {
            prompt('请手动复制以下网站链接：', urls.join('\n'));
        }
    };

    window.runHealthRadar = async (overrideUrls) => {
        const badges = document.querySelectorAll('.deploy-summary-card .health-radar-badge');
        if (!badges || badges.length === 0) return;

        let urls = overrideUrls || [];
        if (!urls || urls.length === 0) {
            badges.forEach(b => {
                const u = b.dataset.url;
                if (u && !urls.includes(u)) urls.push(u);
            });
        }
        if (urls.length === 0) return;

        // 置为探测中动画状态
        badges.forEach(b => {
            b.innerHTML = '<span style="color:#38bdf8;">🛰️ 正在探测连通性...</span>';
            b.style.borderColor = 'rgba(56,189,248,0.3)';
            b.style.background = 'rgba(56,189,248,0.08)';
        });

        try {
            const res = await window.apiFetch('/api/governance/health-radar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ urls: urls })
            });

            if (res && res.status === 'success' && Array.isArray(res.results)) {
                res.results.forEach(item => {
                    const targetBadges = document.querySelectorAll(`.deploy-summary-card .health-radar-badge[data-url="${item.url}"]`);
                    targetBadges.forEach(b => {
                        if (item.is_healthy) {
                            const isFast = item.latency_ms < 150;
                            const latencyColor = isFast ? '#10b981' : '#38bdf8';
                            const bgLight = isFast ? 'rgba(16,185,129,0.12)' : 'rgba(56,189,248,0.12)';
                            const borderLight = isFast ? 'rgba(16,185,129,0.35)' : 'rgba(56,189,248,0.35)';
                            b.innerHTML = `<span style="color:${latencyColor};font-weight:700;">⚡ ${item.latency_ms}ms</span> <span style="color:#94a3b8;">·</span> <span style="color:${latencyColor};">HTTP ${item.status_code}</span> <span style="color:#64748b;">(${item.server || 'Edge'})</span>`;
                            b.style.borderColor = borderLight;
                            b.style.background = bgLight;
                            b.title = `边缘节点: ${item.server} | 往返时延: ${item.latency_ms}ms | 状态: 正常连通`;
                        } else if (item.status_code === 404) {
                            b.innerHTML = `<span style="color:#f59e0b;font-weight:600;">⏳ 边缘广播中 (404)</span>`;
                            b.style.borderColor = 'rgba(245,158,11,0.35)';
                            b.style.background = 'rgba(245,158,11,0.1)';
                            b.title = `最新产物已推送到云端，边缘 CDN 节点正在进行全局 DNS/缓存广播，数秒后即可正常访问`;
                        } else {
                            b.innerHTML = `<span style="color:#ef4444;font-weight:600;">⚠️ ${item.message || '网络波动'}</span>`;
                            b.style.borderColor = 'rgba(239,68,68,0.35)';
                            b.style.background = 'rgba(239,68,68,0.1)';
                            b.title = `探测信息: ${item.message}`;
                        }
                    });
                });
            }
        } catch (e) {
            console.warn('⚠️ [HealthRadar] 探测接口请求失败:', e);
            badges.forEach(b => {
                b.innerHTML = '<span style="color:#94a3b8;">雷达暂不可用</span>';
            });
        }
    };

    window.renderDeploymentSummaryCard = (summary) => {
        if (!summary || !summary.channels || summary.channels.length === 0) return;
        const out = document.getElementById('terminal-output');
        if (!out) return;

        // 防重入：若已有最新汇总卡片，先移除旧的
        const existing = out.querySelector('.deploy-summary-card');
        if (existing) existing.remove();

        const card = document.createElement('div');
        card.className = 'glass-panel deploy-summary-card';
        card.style.cssText = `
            margin: 16px 0 8px 0;
            padding: 16px 18px;
            border-radius: 12px;
            backdrop-filter: blur(12px);
            font-family: inherit;
            text-align: left;
        `;

        const total = summary.total_channels || summary.channels.length;
        const success = summary.success_count !== undefined ? summary.success_count : summary.channels.filter(c => c.status === 'success').length;
        const failed = summary.fail_count !== undefined ? summary.fail_count : summary.channels.filter(c => c.status !== 'success').length;

        // 寻找主站 URL
        const primaryCh = summary.channels.find(c => c.is_primary && c.url) || summary.channels.find(c => c.url && c.status === 'success');
        if (primaryCh && primaryCh.url) {
            window._latestPrimaryLiveUrl = primaryCh.url;
            const visitBtn = document.getElementById('btn-terminal-visit-site');
            if (visitBtn) {
                visitBtn.style.display = 'inline-flex';
                visitBtn.title = `立即在新标签页打开 ${primaryCh.name} (${primaryCh.url})`;
            }
        }

        const allSuccessUrls = summary.channels.filter(c => c.status === 'success' && c.url).map(c => `${c.name}: ${c.url}`);

        let channelsHtml = summary.channels.map(ch => {
            const isSuccess = ch.status === 'success';
            const roleBadge = ch.is_primary
                ? `<span style="background:rgba(5,150,105,0.22);color:#10b981;border:1px solid rgba(16,185,129,0.4);padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;white-space:nowrap;">🏠 官方主站</span>`
                : `<span style="background:rgba(56,189,248,0.18);color:#38bdf8;border:1px solid rgba(56,189,248,0.35);padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:600;white-space:nowrap;">🔄 备用镜像</span>`;
            
            const statusBadge = isSuccess
                ? `<span style="color:#10b981;font-size:0.75rem;font-weight:600;display:inline-flex;align-items:center;gap:4px;">🟢 部署成功</span>`
                : `<span style="color:#ef4444;font-size:0.75rem;font-weight:600;display:inline-flex;align-items:center;gap:4px;">❌ 投递失败</span>`;

            // 🛰️ [V90.0] 健康雷达动态徽章插槽
            const radarBadge = isSuccess && ch.url
                ? `<span class="health-radar-badge" data-url="${ch.url}" style="font-size:0.72rem;padding:2px 8px;border-radius:4px;background:var(--card-subtle-bg, rgba(255,255,255,0.05));border:1px solid var(--glass-border);color:var(--text-dim);display:inline-flex;align-items:center;gap:4px;transition:all 0.3s;white-space:nowrap;"><span style="display:inline-block;transform:scale(0.85);">🛰️</span> 探测中...</span>`
                : '';

            const linkAction = isSuccess && ch.url
                ? `<a href="${ch.url}" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:4px;padding:4px 12px;background:rgba(0,240,255,0.15);border:1px solid rgba(0,240,255,0.4);color:var(--accent-primary, #00f0ff);border-radius:6px;font-size:0.75rem;font-weight:700;text-decoration:none;transition:all 0.15s;white-space:nowrap;" onmouseover="this.style.background='rgba(0,240,255,0.3)'" onmouseout="this.style.background='rgba(0,240,255,0.15)'">打开浏览 ↗</a>`
                : `<span style="font-size:0.72rem;color:var(--text-dim);">${ch.error || '未生成线上地址'}</span>`;

            const urlDisplay = isSuccess && ch.url
                ? `<div style="margin-top:5px;font-size:0.75rem;color:var(--text-dim);word-break:break-all;font-family:'JetBrains Mono',monospace;"><a href="${ch.url}" target="_blank" rel="noopener noreferrer" style="color:var(--accent-secondary, #38bdf8);text-decoration:underline;">${ch.url}</a></div>`
                : '';

            return `
                <div class="deploy-channel-item" style="border-radius:8px;padding:10px 14px;margin-bottom:8px;border:1px solid var(--glass-border);background:var(--card-subtle-bg, rgba(255,255,255,0.03));">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            ${roleBadge}
                            <span style="font-weight:700;font-size:0.85rem;color:var(--text-bright);">${ch.name}</span>
                            ${statusBadge}
                            ${radarBadge}
                        </div>
                        <div>
                            ${linkAction}
                        </div>
                    </div>
                    ${urlDisplay}
                </div>
            `;
        }).join('');

        const copyBtnHtml = allSuccessUrls.length > 0
            ? `<button type="button" onclick='window.copyAllLiveUrls(${JSON.stringify(allSuccessUrls)})' style="background:none;border:1px solid rgba(255,255,255,0.15);color:#cbd5e1;border-radius:6px;padding:3px 10px;font-size:0.72rem;cursor:pointer;display:inline-flex;align-items:center;gap:4px;" onmouseover="this.style.borderColor='rgba(0,240,255,0.5)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.15)'">📋 复制全部链接</button>`
            : '';

        const refreshRadarBtnHtml = allSuccessUrls.length > 0
            ? `<button type="button" onclick="window.runHealthRadar()" style="background:none;border:1px solid rgba(0,240,255,0.3);color:#00f0ff;border-radius:6px;padding:3px 10px;font-size:0.72rem;cursor:pointer;display:inline-flex;align-items:center;gap:4px;" onmouseover="this.style.background='rgba(0,240,255,0.1)'" onmouseout="this.style.background='none'" title="重新发起全球 CDN 边缘测速与连通性探测">⚡ 刷新测速</button>`
            : '';

        card.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:10px;flex-wrap:wrap;gap:8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:1.15rem;">🎉</span>
                    <span style="font-weight:800;font-size:0.95rem;color:#00ff88;letter-spacing:0.3px;">全域发布圆满完成 · 站点已上线</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <span style="font-size:0.75rem;color:#94a3b8;">已同步 ${total} 个渠道 (🟢 成功 ${success} / 🔴 失败 ${failed})</span>
                    ${refreshRadarBtnHtml}
                    ${copyBtnHtml}
                </div>
            </div>
            <div>
                ${channelsHtml}
            </div>
        `;

        out.appendChild(card);
        out.scrollTop = out.scrollHeight;

        // 🚀 [V90.0] 自动点火健康度雷达，异步探测全球 CDN 连通性
        setTimeout(() => {
            if (typeof window.runHealthRadar === 'function') {
                window.runHealthRadar();
            }
        }, 200);
    };

})();
