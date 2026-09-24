/**
 * Illacme Plenipes - Vault Bindery QR Mobile Sync
 * 模块职责：移动端/平板设备扫码传输（双模支持：局域网直传 + 零配置临时公网穿透），集成链路诊断探针与自愈接入。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 * 🌞 [SOP-03 规范]：完整支持深色/亮色自适应主题与无缝切换。
 */
(function() {
    'use strict';

    window._binderyQrCurrentFile = '';
    window._binderyQrNetworkMode = 'lan'; // 'lan' | 'public'
    window._binderyQrSelectedDriver = '';
    window._binderyQrDrivers = [];

    function esc(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function onKeydown(e) {
        if (e.key === 'Escape') window.closeBinderyQrModal();
    }

    window.closeBinderyQrModal = function() {
        const root = document.getElementById('bindery-qr-modal-root');
        if (root) {
            root.style.opacity = '0';
            setTimeout(() => { if (root && root.parentNode) root.parentNode.removeChild(root); }, 200);
        }
        document.removeEventListener('keydown', onKeydown);
    };

    window.navigateToTunnelPlugins = function() {
        window.closeBinderyQrModal();
        if (typeof window.closeBinderyModal === 'function') window.closeBinderyModal();
        const bDrop = document.querySelector('.bindery-modal-backdrop');
        if (bDrop) { bDrop.style.opacity = '0'; bDrop.style.pointerEvents = 'none'; }
        if (typeof window.showView === 'function') window.showView('plugins');
        setTimeout(() => {
            if (typeof window.filterPluginCategory === 'function') window.filterPluginCategory('tunnel');
        }, 150);
    };

    window.copyBinderyQrUrl = function(url, btn) {
        if (!url) return;
        navigator.clipboard.writeText(url).then(() => {
            if (btn) {
                const orig = btn.innerHTML;
                btn.innerHTML = '<span>✅ 已复制</span>';
                btn.style.borderColor = '#10b981'; btn.style.color = '#10b981';
                setTimeout(() => { btn.innerHTML = orig; btn.style.borderColor = ''; btn.style.color = ''; }, 1500);
            }
            if (typeof window.showToast === 'function') window.showToast('📋 直链已复制到剪贴板', 'success');
        }).catch(() => {
            if (typeof window.showToast === 'function') window.showToast('❌ 复制失败，请手动选择复制', 'error');
        });
    };

    window.switchBinderyQrNetworkMode = function(mode) {
        window._binderyQrNetworkMode = mode;
        const file = window._binderyQrCurrentFile;
        if (!file) return;
        const tabLan = document.getElementById('tab-qr-lan');
        const tabPub = document.getElementById('tab-qr-public');
        if (tabLan && tabPub) {
            tabLan.className = mode === 'lan' ? 'bindery-qr-tab-btn active-lan' : 'bindery-qr-tab-btn';
            tabPub.className = mode === 'public' ? 'bindery-qr-tab-btn active-public' : 'bindery-qr-tab-btn';
        }
        if (mode === 'lan') window.loadBinderyLanQr(file);
        else window.loadBinderyPublicQr(file);
    };

    window.loadBinderyLanQr = async function(filename, ipOverride) {
        const contentEl = document.getElementById('bindery-qr-content');
        if (!contentEl) return;
        contentEl.innerHTML = `<div style="text-align:center; padding:20px 10px;"><div style="font-size:1.5rem; margin-bottom:10px;"><span class="pulse-spin" style="display:inline-block;">⏳</span></div><div class="bindery-qr-lead-desc">正在探测局域网节点...</div></div>`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const ipParam = ipOverride ? `&ip=${encodeURIComponent(ipOverride)}` : '';
            const actionParam = filename.endsWith('.html') ? '&action=view' : '';
            const res = await fetchFunc(`/api/bindery/qr?file=${encodeURIComponent(filename)}${actionParam}${ipParam}`);
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (!data || !data.success) throw new Error((data && data.detail) || '无法探测局域网');
            renderQrView(data, 'lan');
        } catch (e) {
            contentEl.innerHTML = `<div style="color:#ef4444; font-size:0.85rem; text-align:center; padding:20px;">⚠️ 加载局域网二维码失败: ${esc(e.message)}</div>`;
        }
    };

    window.selectBinderyTunnelDriver = function(driverId) {
        window._binderyQrSelectedDriver = driverId;
        const btn = document.getElementById('bindery-tunnel-start-btn');
        const driverObj = (window._binderyQrDrivers || []).find(d => d.id === driverId);
        const dName = driverObj ? driverObj.name : '临时公网';
        if (btn) btn.innerHTML = `🚀 开启 ${esc(dName)} 直链`;
        document.querySelectorAll('.bindery-tunnel-card').forEach(el => {
            el.classList.toggle('active', el.getAttribute('data-driver') === driverId);
        });
    };

    window.loadBinderyPublicQr = async function(filename) {
        const contentEl = document.getElementById('bindery-qr-content');
        if (!contentEl) return;
        contentEl.innerHTML = `<div style="text-align:center; padding:20px 10px;"><div style="font-size:1.5rem; margin-bottom:10px;"><span class="pulse-spin" style="display:inline-block;">⏳</span></div><div class="bindery-qr-lead-desc">正在检查临时公网隧道...</div></div>`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const statusRes = await fetchFunc('/api/bindery/tunnel/status');
            const status = (statusRes && typeof statusRes.json === 'function') ? await statusRes.json() : statusRes;
            if (status && status.is_running && status.public_url) {
                const actionParam = filename.endsWith('.html') ? '&action=view' : '';
                const qrRes = await fetchFunc(`/api/bindery/qr/public?file=${encodeURIComponent(filename)}${actionParam}`);
                const qrData = (qrRes && typeof qrRes.json === 'function') ? await qrRes.json() : qrRes;
                if (!qrData || !qrData.success) throw new Error((qrData && qrData.detail) || '公网令牌签发失败');
                renderQrView(qrData, 'public', status);
            } else {
                let drivers = [];
                try {
                    const dRes = await fetchFunc('/api/bindery/tunnel/drivers');
                    const dData = (dRes && typeof dRes.json === 'function') ? await dRes.json() : dRes;
                    const rawDrivers = (dData && dData.drivers) || [];
                    drivers = rawDrivers.filter(d => d.is_enabled !== false);
                    if (!drivers.length && rawDrivers.length) drivers = [rawDrivers[0]];
                    const order = { 'localhost_run': 0, 'cloudflare': 1, 'pinggy': 2, 'serveo': 3, 'cpolar': 4, 'ngrok': 5, 'frp': 6, 'tailscale': 7 };
                    drivers.sort((a, b) => (order[a.id] ?? 99) - (order[b.id] ?? 99));
                    if (!window._binderyQrSelectedDriver || !drivers.some(d => d.id === window._binderyQrSelectedDriver)) {
                        window._binderyQrSelectedDriver = (drivers.some(d => d.id === dData.active_driver) ? dData.active_driver : null) || drivers[0]?.id;
                    }
                } catch (_) {}
                window._binderyQrDrivers = drivers;
                const curDriver = drivers.find(d => d.id === window._binderyQrSelectedDriver) || drivers[0];
                const curDriverName = curDriver ? curDriver.name : '临时公网';

                contentEl.innerHTML = `
                    <div style="text-align:center; padding:12px 10px;">
                        <div style="font-size:2rem; margin-bottom:6px;">⚡</div>
                        <div class="bindery-qr-lead-title">零配置临时公网穿透</div>
                        <div class="bindery-qr-lead-desc">建立即时安全通道，即便处于 5G/4G 蜂窝网络或异地，手机也能随时扫码翻阅。</div>
                        ${drivers.length > 1 ? `
                            <div style="margin-bottom:16px;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; padding:0 2px;">
                                    <div class="bindery-qr-tunnel-selector-label" style="margin-bottom:0;">📡 选择公网穿透通道:</div>
                                    <a href="javascript:void(0)" onclick="window.navigateToTunnelPlugins()" style="font-size:0.72rem; color:var(--accent-secondary, #0284c7); text-decoration:none; font-weight:600; cursor:pointer;" title="配置穿透驱动">
                                        <span>⚙️ 穿透插件</span><span>↗</span>
                                    </a>
                                </div>
                                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:8px; max-width:440px; margin:0 auto; max-height:190px; overflow-y:auto; padding:2px;">
                                    ${drivers.map(d => `
                                        <div class="bindery-tunnel-card ${d.id === window._binderyQrSelectedDriver ? 'active' : ''}" data-driver="${d.id}" onclick="window.selectBinderyTunnelDriver('${d.id}')">
                                            <div class="driver-title">${d.icon} ${esc(d.name)}</div>
                                            <div class="driver-desc">${esc(d.desc)}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        <button type="button" id="bindery-tunnel-start-btn" onclick="window.startBinderyTunnel()" class="primary-btn glow-btn" style="background:linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); color:#fff; border:none; padding:8px 22px; font-size:0.85rem; border-radius:8px; cursor:pointer; font-weight:600;">
                            🚀 开启 ${esc(curDriverName)} 直链
                        </button>
                    </div>
                `;
            }
        } catch (e) {
            contentEl.innerHTML = `<div style="color:#ef4444; font-size:0.85rem; text-align:center; padding:20px;">⚠️ 检查公网隧道异常: ${esc(e.message)}</div>`;
        }
    };

    window.startBinderyTunnel = async function(driverId) {
        const targetDriver = driverId || window._binderyQrSelectedDriver || undefined;
        const contentEl = document.getElementById('bindery-qr-content');
        const driverObj = (window._binderyQrDrivers || []).find(d => d.id === targetDriver);
        const dName = driverObj ? driverObj.name : '临时公网';
        if (contentEl) contentEl.innerHTML = `<div style="text-align:center; padding:30px 10px;"><div style="font-size:1.8rem; margin-bottom:10px;"><span class="pulse-spin" style="display:inline-block;">⚡</span></div><div class="bindery-qr-lead-title">正在建立 [${esc(dName)}] 穿透通道...</div><div class="bindery-qr-lead-desc" style="margin-top:4px;">无需繁琐配置，请稍候 3~5 秒</div></div>`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/tunnel/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ driver: targetDriver })
            });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (!data || !data.success) throw new Error((data && data.detail) || '隧道唤醒失败');
            if (typeof window.showToast === 'function') window.showToast(`🌐 [${data.provider_name || dName}] 隧道已就绪！`, 'success');
            if (data && data.is_running && data.public_url) {
                const act = window._binderyQrCurrentFile.endsWith('.html') ? '&action=view' : '';
                const qrRes = await fetchFunc(`/api/bindery/qr/public?file=${encodeURIComponent(window._binderyQrCurrentFile)}${act}`);
                const qrData = (qrRes && typeof qrRes.json === 'function') ? await qrRes.json() : qrRes;
                if (qrData && qrData.success) { renderQrView(qrData, 'public', data); return; }
            }
            window.loadBinderyPublicQr(window._binderyQrCurrentFile);
        } catch (e) {
            if (contentEl) contentEl.innerHTML = `<div style="color:#ef4444; font-size:0.85rem; text-align:center; padding:20px;">⚠️ 启动 [${esc(dName)}] 失败: ${esc(e.message)}<div style="margin-top:12px; display:flex; gap:8px; justify-content:center;"><button onclick="window.loadBinderyPublicQr(window._binderyQrCurrentFile)" class="mini-btn">🔄 更换通道重试</button><button onclick="window.switchBinderyQrNetworkMode('lan')" class="mini-btn">返回局域网模式</button></div></div>`;
        }
    };

    window.stopBinderyTunnel = async function(silent = false) {
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            await fetchFunc('/api/bindery/tunnel/stop', { method: 'POST' });
            if (!silent && typeof window.showToast === 'function') window.showToast('🔒 公网通道已切断，已收缩至局域网', 'info');
            if (!silent) window.switchBinderyQrNetworkMode('lan');
        } catch (e) {
            console.error('关闭隧道异常:', e);
        }
    };

    window.switchBinderyTunnelDriver = async function() {
        await window.stopBinderyTunnel(true);
        window.loadBinderyPublicQr(window._binderyQrCurrentFile);
    };

    function renderQrView(data, mode, status = null) {
        const contentEl = document.getElementById('bindery-qr-content');
        if (!contentEl) return;
        const isWb = data.filename.endsWith('.html');
        const tip = isWb ? '手机 / 平板扫码直接在线翻阅 WebBook' : 'iPhone / iPad (Books)、Android、Kindle 扫码即刻下载导入';
        let qrHtml = '';
        if (data.qr_data_uri) {
            qrHtml = `<div style="background:#ffffff; border-radius:12px; padding:14px; display:inline-block; box-shadow:0 8px 24px rgba(0,0,0,0.18); margin-bottom:12px;"><img src="${data.qr_data_uri}" alt="扫码直传" style="width:200px; height:200px; display:block; image-rendering:pixelated;" /></div>`;
        } else if (typeof window.generateBinderyQrSvg === 'function') {
            qrHtml = `<div style="background:#ffffff; border-radius:12px; padding:14px; display:inline-block; box-shadow:0 8px 24px rgba(0,0,0,0.18); margin-bottom:12px;">${window.generateBinderyQrSvg(data.url, 200)}</div>`;
        }
        const providerName = (status && status.provider_name) || (status && status.provider === 'cloudflare' ? 'Cloudflare Anycast' : (status && status.provider === 'pinggy' ? 'Pinggy OpenSSH' : '全球公网访问'));
        const badge = mode === 'public'
            ? `<div style="display:inline-flex; align-items:center; gap:6px; background:rgba(139,92,246,0.15); border:1px solid rgba(139,92,246,0.35); border-radius:12px; padding:3px 12px; font-size:0.7rem; color:#8b5cf6; margin-bottom:6px; font-weight:600;"><span>⚡ ${esc(providerName)}</span><span>·</span><span>⏳ 凭证30分钟内有效</span></div>`
            : `<div style="display:inline-flex; align-items:center; gap:6px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:3px 12px; font-size:0.7rem; color:#10b981; margin-bottom:6px; font-weight:600;"><span>📶 局域网极速直连 (${esc(data.lan_ip)})</span></div>`;

        const actionBtns = mode === 'public'
            ? `<div style="display:inline-flex; gap:6px;"><button type="button" onclick="window.autoHealBinderyTunnel(this)" class="mini-btn" style="background:rgba(139,92,246,0.15); border:1px solid rgba(139,92,246,0.35); color:#8b5cf6; padding:3px 8px; font-size:0.7rem; border-radius:5px; cursor:pointer;" title="自动探测并切换到最快可用备用隧道">⚡ 一键自愈</button><button type="button" onclick="window.loadBinderyPublicQr(window._binderyQrCurrentFile)" class="mini-btn" style="background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); color:#10b981; padding:3px 8px; font-size:0.7rem; border-radius:5px; cursor:pointer;" title="重新校验活性并刷新二维码">🔄 刷新</button><button type="button" onclick="window.switchBinderyTunnelDriver()" class="mini-btn" style="background:rgba(2,132,199,0.12); border:1px solid rgba(2,132,199,0.3); color:var(--accent-secondary, #0284c7); padding:3px 8px; font-size:0.7rem; border-radius:5px; cursor:pointer;" title="切换穿透通道">🔀 换通道</button><button type="button" onclick="window.stopBinderyTunnel()" class="mini-btn" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); color:#ef4444; padding:3px 8px; font-size:0.7rem; border-radius:5px; cursor:pointer;" title="切断公网">🔌 断开</button></div>`
            : '';

        const isServeo = (status && (status.provider === 'serveo' || (status.public_url && status.public_url.indexOf('serveousercontent') !== -1))) || (data && data.url && data.url.indexOf('serveousercontent') !== -1);
        const serveoNotice = isServeo ? `<div style="font-size:0.7rem; color:#f59e0b; background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.25); border-radius:6px; padding:4px 8px; margin:0 auto 10px; max-width:320px; line-height:1.4;">💡 Serveo 官方防钓鱼拦截：手机打开后请轻触【Continue to Site】按钮即可直达。</div>` : '';

        contentEl.innerHTML = `
            <div style="text-align:center;">
                ${badge}
                <div id="bindery-qr-health-badge" class="bindery-qr-health-badge" style="margin-bottom:8px; min-height:22px; font-size:0.74rem; display:flex; justify-content:center; align-items:center;"></div>
                <div id="bindery-qr-diag-panel" class="bindery-qr-diag-panel" style="display:none; margin:8px 0 12px; text-align:left;"><div id="bindery-qr-diag-body"></div></div>
                <div>${qrHtml}</div>
                <div class="bindery-qr-lead-title" style="word-break:break-all; text-align:center; padding:0 8px;">${esc(data.filename)}</div>
                <div style="font-size:0.74rem; color:var(--accent, #10b981); margin-bottom:8px; text-align:center; font-weight:500;">✨ ${tip}</div>
                ${serveoNotice}
                <div style="display:flex; justify-content:center; margin-bottom:14px;">
                    <div class="bindery-qr-url-box">
                        <div class="bindery-qr-url-text">${esc(data.url)}</div>
                        <button type="button" onclick="window.copyBinderyQrUrl('${esc(data.url)}', this)" class="bindery-qr-copy-btn">📋 复制</button>
                    </div>
                </div>
                <div class="bindery-qr-footer">
                    ${actionBtns ? `<span>${actionBtns}</span>` : `<span>节点: <strong>${esc(data.lan_ip)}:${esc(data.port)}</strong></span>`}
                    <span style="opacity:0.3;">|</span>
                    <a href="${esc(data.url)}" target="_blank" rel="noopener noreferrer" style="color:var(--accent-secondary, #0284c7); text-decoration:none; display:inline-flex; align-items:center; gap:3px; font-weight:500;">在新标签${isWb ? '翻阅' : '打开'} ↗</a>
                </div>
            </div>
        `;

        if (typeof window.probeBinderyQrHealth === 'function') {
            window.probeBinderyQrHealth(mode, data.url);
        }
    }

    window.openBinderyQrModal = async function(filename) {
        if (!filename) return;
        window.closeBinderyQrModal();
        window._binderyQrCurrentFile = filename;

        const root = document.createElement('div');
        root.id = 'bindery-qr-modal-root';
        root.className = 'bindery-qr-backdrop';
        root.onclick = function(e) { if (e.target === root) window.closeBinderyQrModal(); };
        const card = document.createElement('div');
        card.className = 'bindery-qr-card';
        const isLan = window._binderyQrNetworkMode === 'lan';
        card.innerHTML = `
            <div class="bindery-qr-header">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.25rem;">📱</span>
                    <strong class="bindery-qr-title">移动端扫码同步 (Mobile Sync)</strong>
                </div>
                <button type="button" onclick="window.closeBinderyQrModal()" class="bindery-qr-close-btn" title="关闭">×</button>
            </div>
            <div class="bindery-qr-nav">
                <button id="tab-qr-lan" type="button" onclick="window.switchBinderyQrNetworkMode('lan')" class="bindery-qr-tab-btn ${isLan ? 'active-lan' : ''}">
                    📶 局域网直传 (同 Wi-Fi)
                </button>
                <button id="tab-qr-public" type="button" onclick="window.switchBinderyQrNetworkMode('public')" class="bindery-qr-tab-btn ${!isLan ? 'active-public' : ''}">
                    ⚡ 临时公网穿透 (5G/异地)
                </button>
            </div>
            <div id="bindery-qr-content"></div>
        `;

        root.appendChild(card);
        document.body.appendChild(root);
        document.addEventListener('keydown', onKeydown);
        requestAnimationFrame(() => { root.style.opacity = '1'; });
        if (isLan) window.loadBinderyLanQr(filename); else window.loadBinderyPublicQr(filename);
    };
})();
