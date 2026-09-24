/**
 * Illacme Plenipes - Vault Bindery QR Diagnostic & Auto-Heal Hub
 * 模块职责：移动端扫码穿透诊断与链路自愈中枢（网络健康度探针、回环时延评测、多网卡切换与故障一键自愈）。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 * 🌞 [SOP-03 规范]：深色/浅色自适应高透毛玻璃卡片风格。
 */
(function() {
    'use strict';

    window._binderyQrProbeRunning = false;
    window._binderyQrLastHealth = null;

    function esc(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    /** 触发链路健康度探针 */
    window.probeBinderyQrHealth = async function(mode, currentUrl) {
        const badgeEl = document.getElementById('bindery-qr-health-badge');
        if (!badgeEl) return;
        badgeEl.innerHTML = `<span class="qr-pulse-dot warning"></span><span style="color:var(--text-dim, #94a3b8);">正在进行链路活性探针...</span>`;
        window._binderyQrProbeRunning = true;

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            if (mode === 'lan') {
                const res = await fetchFunc('/api/bindery/probe/lan');
                const data = (res && typeof res.json === 'function') ? await res.json() : res;
                window._binderyQrLastHealth = { mode: 'lan', data: data };
                renderLanHealthBadge(badgeEl, data);
            } else {
                const res = await fetchFunc('/api/bindery/tunnel/probe');
                const data = (res && typeof res.json === 'function') ? await res.json() : res;
                window._binderyQrLastHealth = { mode: 'public', data: data };
                renderPublicHealthBadge(badgeEl, data);
            }
        } catch (e) {
            badgeEl.innerHTML = `<span class="qr-pulse-dot error"></span><span style="color:#ef4444;">探针网络异常: ${esc(e.message)}</span>`;
        } finally {
            window._binderyQrProbeRunning = false;
        }
    };

    function renderLanHealthBadge(container, data) {
        const isOpen = data && data.port_open;
        const candCount = (data && data.candidates && data.candidates.length) || 1;
        const color = isOpen ? '#10b981' : '#f59e0b';
        const dotCls = isOpen ? 'online' : 'warning';
        const text = isOpen ? `局域网端口 ${data.port} 就绪 (${candCount} 个网卡接口)` : `局域网端口 ${data.port} 未响应`;

        container.innerHTML = `
            <div style="display:inline-flex; align-items:center; gap:6px; cursor:pointer;" onclick="window.toggleBinderyDiagnosticPanel()" title="点击查看局域网排查与网卡切换向导">
                <span class="qr-pulse-dot ${dotCls}"></span>
                <span style="color:${color}; font-weight:600;">${text}</span>
                <span style="font-size:0.68rem; opacity:0.75; text-decoration:underline;">[诊断/换网卡]</span>
            </div>
        `;
    }

    function renderPublicHealthBadge(container, data) {
        const isHealthy = data && data.healthy;
        const rtt = (data && data.rtt_ms != null) ? `${data.rtt_ms}ms` : '';
        const prov = (data && (data.provider_name || data.provider)) || '公网隧道';

        if (isHealthy) {
            container.innerHTML = `
                <div style="display:inline-flex; align-items:center; gap:6px; cursor:pointer;" onclick="window.toggleBinderyDiagnosticPanel()" title="点击查看穿透延时与链路详情">
                    <span class="qr-pulse-dot online"></span>
                    <span style="color:#10b981; font-weight:600;">公网回环极佳 ${rtt ? `(${rtt})` : ''} · ${esc(prov)}</span>
                    <span style="font-size:0.68rem; opacity:0.75; text-decoration:underline;">[链路详情]</span>
                </div>
            `;
        } else {
            const errMsg = (data && data.message) || '公网暂不可达';
            container.innerHTML = `
                <div style="display:inline-flex; align-items:center; gap:6px; flex-wrap:wrap; justify-content:center;">
                    <div style="display:inline-flex; align-items:center; gap:5px; cursor:pointer;" onclick="window.toggleBinderyDiagnosticPanel()" title="点击查看错误分析与自愈方案">
                        <span class="qr-pulse-dot error"></span>
                        <span style="color:#ef4444; font-weight:600;">链路受阻: ${esc(errMsg)}</span>
                    </div>
                    <button type="button" onclick="window.autoHealBinderyTunnel(this)" class="mini-heal-btn" title="自动探测并无缝切换至高可用备用隧道">
                        ⚡ 一键自愈
                    </button>
                </div>
            `;
        }
    }

    /** 展开或折叠诊断面板 */
    window.toggleBinderyDiagnosticPanel = function() {
        const panel = document.getElementById('bindery-qr-diag-panel');
        if (!panel) return;
        const isHidden = panel.style.display === 'none' || !panel.style.display;
        if (isHidden) {
            panel.style.display = 'block';
            window.renderBinderyDiagnosticContent();
        } else {
            panel.style.display = 'none';
        }
    };

    /** 渲染诊断详情内容 */
    window.renderBinderyDiagnosticContent = function() {
        const bodyEl = document.getElementById('bindery-qr-diag-body');
        if (!bodyEl) return;
        const health = window._binderyQrLastHealth;

        if (!health) {
            bodyEl.innerHTML = `<div style="text-align:center; padding:10px; font-size:0.75rem; color:var(--text-dim, #94a3b8);">正在采集链路体检数据...</div>`;
            return;
        }

        if (health.mode === 'lan') {
            const d = health.data || {};
            const candidates = d.candidates || [];
            const activeIp = d.active_ip || '';
            const tips = d.tips || [];

            bodyEl.innerHTML = `
                <div class="qr-diag-box">
                    <div class="qr-diag-title">📶 局域网物理接口选择 (若手机无法访问可切换网卡):</div>
                    <div style="display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 12px;">
                        ${candidates.map(c => {
                            const isCur = c.ip === activeIp;
                            return `
                                <button type="button" onclick="window.switchBinderyLanIp('${esc(c.ip)}')" class="qr-ip-pill ${isCur ? 'active' : ''}">
                                    <span style="font-weight:700;">${esc(c.ip)}</span>
                                    <span style="font-size:0.68rem; opacity:0.8;">(${esc(c.desc)})</span>
                                    ${isCur ? '<span>✓</span>' : ''}
                                </button>
                            `;
                        }).join('')}
                    </div>
                    <div class="qr-diag-tips">
                        <strong style="display:block; margin-bottom:4px; font-size:0.75rem;">💡 局域网扫码排障指南：</strong>
                        ${tips.map(t => `<div style="margin-bottom:3px; line-height:1.4;">• ${esc(t)}</div>`).join('')}
                    </div>
                </div>
            `;
        } else {
            const d = health.data || {};
            const isH = d.healthy;
            const rtt = d.rtt_ms != null ? `${d.rtt_ms} ms` : '超时未响应';
            const stat = d.status_code || '无响应';
            const prov = d.provider_name || d.provider || '临时公网';

            bodyEl.innerHTML = `
                <div class="qr-diag-box">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="qr-diag-title">⚡ 公网穿透回环探针体检报告:</span>
                        <button type="button" onclick="window.autoHealBinderyTunnel(this)" class="mini-heal-btn">
                            ⚡ 一键自愈切换
                        </button>
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.75rem; margin-bottom:10px;">
                        <div class="qr-metric-card"><span class="label">当前通道:</span><strong>${esc(prov)}</strong></div>
                        <div class="qr-metric-card"><span class="label">链路往返时延:</span><strong style="color:${isH ? '#10b981' : '#ef4444'};">${esc(rtt)}</strong></div>
                        <div class="qr-metric-card"><span class="label">远端 HTTP 状态:</span><strong>${esc(String(stat))}</strong></div>
                        <div class="qr-metric-card"><span class="label">健康评级:</span><strong style="color:${isH ? '#10b981' : '#ef4444'};">${isH ? '🟢 优良畅通' : '🔴 异常受阻'}</strong></div>
                    </div>
                    <div class="qr-diag-tips">
                        <div style="margin-bottom:4px;"><strong>诊断建议：</strong>${esc(d.message || '')}</div>
                        <div style="opacity:0.85;">• 若提示 "no tunnel here" 或 HTTP 超时，通常由于临时 SSH 域名映射延迟或运营商网络波动造成。点击上方【一键自愈切换】将全自动调度 Pinggy / Cloudflare / Serveo 等备用高可用通道。</div>
                    </div>
                </div>
            `;
        }
    };

    /** 切换局域网候选 IP */
    window.switchBinderyLanIp = function(ip) {
        if (!ip) return;
        const file = window._binderyQrCurrentFile;
        if (!file) return;
        if (typeof window.loadBinderyLanQr === 'function') {
            window.loadBinderyLanQr(file, ip);
            if (typeof window.showToast === 'function') window.showToast(`📶 已切换至接口: ${ip}`, 'info');
        }
    };

    /** 一键链路自愈 */
    window.autoHealBinderyTunnel = async function(btn) {
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span>⏳ 正在自愈...</span>';
        }
        if (typeof window.showToast === 'function') window.showToast('🛠️ 正在探测并自愈公网穿透链路...', 'info');

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/tunnel/auto-heal', { method: 'POST' });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;

            if (data && data.success && data.healed) {
                if (typeof window.showToast === 'function') window.showToast(`✨ 自愈成功！已无缝切换至 [${data.provider_name || data.driver}]`, 'success');
                if (typeof window.loadBinderyPublicQr === 'function') {
                    await window.loadBinderyPublicQr(window._binderyQrCurrentFile);
                }
            } else if (data && data.healed === false && data.success) {
                if (typeof window.showToast === 'function') window.showToast(data.message || '链路当前已处于健康状态', 'info');
                const badgeEl = document.getElementById('bindery-qr-health-badge');
                if (badgeEl && data.probe) renderPublicHealthBadge(badgeEl, data.probe);
            } else {
                throw new Error((data && data.message) || '所有公网备用通道均无法连通');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`⚠️ 自愈受限: ${e.message}`, 'error');
            const bodyEl = document.getElementById('bindery-qr-diag-body');
            if (bodyEl) {
                bodyEl.innerHTML = `<div style="color:#ef4444; font-size:0.75rem; padding:8px; background:rgba(239,68,68,0.1); border-radius:6px;">⚠️ 自愈受限: ${esc(e.message)}。<br/>建议点击顶部切换按钮直接使用【局域网直传】模式。</div>`;
            }
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '⚡ 一键自愈';
            }
        }
    };
})();
