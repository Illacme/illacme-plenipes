/**
 * Illacme Plenipes - Vault Bindery QR Mobile Sync
 * 模块职责：移动端/平板设备扫码传输（双模支持：局域网直传 + 零配置临时公网穿透）。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */
(function() {
    'use strict';

    window._binderyQrCurrentFile = '';
    window._binderyQrNetworkMode = 'lan'; // 'lan' | 'public'

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

    window.copyBinderyQrUrl = function(url, btn) {
        if (!url) return;
        navigator.clipboard.writeText(url).then(() => {
            if (btn) {
                const orig = btn.innerHTML;
                btn.innerHTML = '<span>✅ 已复制</span>';
                btn.style.borderColor = '#10b981';
                btn.style.color = '#10b981';
                setTimeout(() => { btn.innerHTML = orig; btn.style.borderColor = ''; btn.style.color = ''; }, 1500);
            }
            if (typeof window.showToast === 'function') window.showToast('📋 直链已复制到剪贴板', 'success');
        }).catch(err => {
            console.error('复制失败:', err);
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
            if (mode === 'lan') {
                tabLan.style.background = 'var(--accent, #10b981)'; tabLan.style.color = '#fff';
                tabPub.style.background = 'transparent'; tabPub.style.color = 'var(--text-dim, rgba(255,255,255,0.6))';
            } else {
                tabPub.style.background = '#8b5cf6'; tabPub.style.color = '#fff';
                tabLan.style.background = 'transparent'; tabLan.style.color = 'var(--text-dim, rgba(255,255,255,0.6))';
            }
        }
        if (mode === 'lan') window.loadBinderyLanQr(file);
        else window.loadBinderyPublicQr(file);
    };

    window.loadBinderyLanQr = async function(filename) {
        const contentEl = document.getElementById('bindery-qr-content');
        if (!contentEl) return;
        contentEl.innerHTML = `<div style="text-align:center; padding:20px 10px;"><div style="font-size:1.5rem; margin-bottom:10px;"><span class="pulse-spin" style="display:inline-block;">⏳</span></div><div style="font-size:0.85rem; color:var(--text-dim, rgba(255,255,255,0.7));">正在探测局域网节点...</div></div>`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc(`/api/bindery/qr?file=${encodeURIComponent(filename)}`);
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (!data || !data.success) throw new Error((data && data.detail) || '无法探测局域网');
            renderQrView(data, 'lan');
        } catch (e) {
            contentEl.innerHTML = `<div style="color:#ef4444; font-size:0.85rem; text-align:center; padding:20px;">⚠️ 加载局域网二维码失败: ${esc(e.message)}</div>`;
        }
    };

    window.loadBinderyPublicQr = async function(filename) {
        const contentEl = document.getElementById('bindery-qr-content');
        if (!contentEl) return;
        contentEl.innerHTML = `<div style="text-align:center; padding:20px 10px;"><div style="font-size:1.5rem; margin-bottom:10px;"><span class="pulse-spin" style="display:inline-block;">⏳</span></div><div style="font-size:0.85rem; color:var(--text-dim, rgba(255,255,255,0.7));">正在检查临时公网隧道...</div></div>`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const statusRes = await fetchFunc('/api/bindery/tunnel/status');
            const status = (statusRes && typeof statusRes.json === 'function') ? await statusRes.json() : statusRes;
            if (status && status.is_running && status.public_url) {
                const qrRes = await fetchFunc(`/api/bindery/qr/public?file=${encodeURIComponent(filename)}`);
                const qrData = (qrRes && typeof qrRes.json === 'function') ? await qrRes.json() : qrRes;
                if (!qrData || !qrData.success) throw new Error((qrData && qrData.detail) || '公网令牌签发失败');
                renderQrView(qrData, 'public');
            } else {
                contentEl.innerHTML = `
                    <div style="text-align:center; padding:16px 10px;">
                        <div style="font-size:2.2rem; margin-bottom:8px;">⚡</div>
                        <div style="font-size:0.95rem; font-weight:700; color:var(--text-bright, #fff); margin-bottom:6px;">零配置临时公网穿透</div>
                        <div style="font-size:0.75rem; color:var(--text-dim, rgba(255,255,255,0.65)); margin-bottom:18px; line-height:1.5;">
                            通过 Cloudflare Quick Tunnel 或原生 SSH 建立即时安全通道。<br/>即便处于 5G/4G 蜂窝网络或异地，手机也能随时扫码下载。
                        </div>
                        <button type="button" onclick="window.startBinderyTunnel()" class="primary-btn glow-btn" style="background:linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); color:#fff; border:none; padding:8px 20px; font-size:0.85rem; border-radius:8px; cursor:pointer; font-weight:600;">
                            🚀 开启临时公网直链
                        </button>
                    </div>
                `;
            }
        } catch (e) {
            contentEl.innerHTML = `<div style="color:#ef4444; font-size:0.85rem; text-align:center; padding:20px;">⚠️ 检查公网隧道异常: ${esc(e.message)}</div>`;
        }
    };

    window.startBinderyTunnel = async function() {
        const contentEl = document.getElementById('bindery-qr-content');
        if (contentEl) contentEl.innerHTML = `<div style="text-align:center; padding:30px 10px;"><div style="font-size:1.8rem; margin-bottom:10px;"><span class="pulse-spin" style="display:inline-block;">⚡</span></div><div style="font-size:0.85rem; color:var(--text-bright, #fff); font-weight:600;">正在建立全球 Anycast 临时穿透通道...</div><div style="font-size:0.72rem; color:var(--text-dim, rgba(255,255,255,0.6)); margin-top:4px;">无需注册账号，请稍候 3~5 秒</div></div>`;
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc('/api/bindery/tunnel/start', { method: 'POST' });
            const data = (res && typeof res.json === 'function') ? await res.json() : res;
            if (!data || !data.success) throw new Error((data && data.detail) || '隧道唤醒失败');
            if (typeof window.showToast === 'function') window.showToast('🌐 公网临时隧道已就绪！', 'success');
            window.loadBinderyPublicQr(window._binderyQrCurrentFile);
        } catch (e) {
            if (contentEl) contentEl.innerHTML = `<div style="color:#ef4444; font-size:0.85rem; text-align:center; padding:20px;">⚠️ 启动公网隧道失败: ${esc(e.message)}<div style="margin-top:10px;"><button onclick="window.switchBinderyQrNetworkMode('lan')" class="mini-btn">返回局域网模式</button></div></div>`;
        }
    };

    window.stopBinderyTunnel = async function() {
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            await fetchFunc('/api/bindery/tunnel/stop', { method: 'POST' });
            if (typeof window.showToast === 'function') window.showToast('🔒 公网通道已切断，已收缩至局域网', 'info');
            window.switchBinderyQrNetworkMode('lan');
        } catch (e) {
            console.error('关闭隧道异常:', e);
        }
    };

    function renderQrView(data, mode) {
        const contentEl = document.getElementById('bindery-qr-content');
        if (!contentEl) return;
        const isWb = data.filename.endsWith('.html');
        const tip = isWb ? '手机 / 平板扫码直接在线翻阅 WebBook' : 'iPhone / iPad (Books)、Android、Kindle 扫码即刻下载导入';
        let qrHtml = '';
        if (data.qr_data_uri) {
            qrHtml = `<div style="background:#ffffff; border-radius:12px; padding:12px; display:inline-block; box-shadow:0 6px 20px rgba(0,0,0,0.3); margin-bottom:12px;"><img src="${data.qr_data_uri}" alt="扫码直传" style="width:190px; height:190px; display:block;" /></div>`;
        } else if (typeof window.generateBinderyQrSvg === 'function') {
            const svg = window.generateBinderyQrSvg(data.url, 190);
            qrHtml = `<div style="background:#ffffff; border-radius:12px; padding:12px; display:inline-block; box-shadow:0 6px 20px rgba(0,0,0,0.3); margin-bottom:12px;">${svg}</div>`;
        }
        const badge = mode === 'public'
            ? `<div style="display:inline-flex; align-items:center; gap:6px; background:rgba(139,92,246,0.15); border:1px solid rgba(139,92,246,0.35); border-radius:12px; padding:2px 10px; font-size:0.7rem; color:#a78bfa; margin-bottom:8px;"><span>⚡ 全球公网访问</span><span>·</span><span>⏳ 凭证30分钟内有效</span></div>`
            : `<div style="display:inline-flex; align-items:center; gap:6px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:2px 10px; font-size:0.7rem; color:#10b981; margin-bottom:8px;"><span>📶 局域网极速直连 (${esc(data.lan_ip)})</span></div>`;

        const stopBtn = mode === 'public'
            ? `<button type="button" onclick="window.stopBinderyTunnel()" class="mini-btn" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); color:#ef4444; padding:3px 8px; font-size:0.7rem; border-radius:5px; cursor:pointer;" title="立即断开公网暴露">🔌 断开公网隧道</button>`
            : '';

        contentEl.innerHTML = `
            ${badge}
            <div>${qrHtml}</div>
            <div style="font-size:0.85rem; font-weight:600; color:var(--text-bright, #fff); margin-bottom:3px; word-break:break-all;">${esc(data.filename)}</div>
            <div style="font-size:0.72rem; color:var(--accent, #10b981); margin-bottom:10px;">✨ ${tip}</div>
            <div style="background:rgba(0,0,0,0.25); border:1px solid var(--glass-border, rgba(255,255,255,0.08)); border-radius:8px; padding:6px 10px; display:flex; align-items:center; gap:8px; margin-bottom:12px; text-align:left;">
                <div style="font-size:0.7rem; color:var(--text-dim, rgba(255,255,255,0.6)); min-width:0; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-family:var(--font-mono, monospace);">${esc(data.url)}</div>
                <button type="button" onclick="window.copyBinderyQrUrl('${esc(data.url)}', this)" class="mini-btn" style="padding:3px 7px; font-size:0.7rem; border-radius:4px; border:1px solid var(--glass-border, rgba(255,255,255,0.15)); background:rgba(255,255,255,0.08); color:var(--text-bright, #fff); cursor:pointer; flex-shrink:0;">📋 复制</button>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.72rem; color:var(--text-dim, rgba(255,255,255,0.5)); border-top:1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-top:10px;">
                ${stopBtn || `<span>节点: <strong style="color:var(--text-bright, #fff);">${esc(data.lan_ip)}:${esc(data.port)}</strong></span>`}
                <a href="${esc(data.url)}" target="_blank" rel="noopener noreferrer" style="color:var(--accent, #38bdf8); text-decoration:none; display:inline-flex; align-items:center; gap:3px;">在新标签打开 ↗</a>
            </div>
        `;
    }

    window.openBinderyQrModal = async function(filename) {
        if (!filename) return;
        window.closeBinderyQrModal();
        window._binderyQrCurrentFile = filename;

        const root = document.createElement('div');
        root.id = 'bindery-qr-modal-root';
        root.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.65); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); z-index:99999; display:flex; align-items:center; justify-content:center; opacity:0; transition:opacity 0.2s ease;';
        root.onclick = function(e) { if (e.target === root) window.closeBinderyQrModal(); };

        const card = document.createElement('div');
        card.style.cssText = 'background:var(--panel-bg, #1e293b); border:1px solid var(--glass-border, rgba(255,255,255,0.12)); box-shadow:0 20px 45px rgba(0,0,0,0.5); border-radius:14px; width:92%; max-width:440px; padding:22px; color:var(--text-bright, #fff); position:relative;';

        const isLan = window._binderyQrNetworkMode === 'lan';
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.25rem;">📱</span>
                    <strong style="font-size:1rem; color:var(--text-bright, #fff);">移动端扫码同步 (Mobile Sync)</strong>
                </div>
                <button type="button" onclick="window.closeBinderyQrModal()" style="background:none; border:none; color:var(--text-dim, rgba(255,255,255,0.5)); font-size:1.3rem; cursor:pointer; padding:2px 6px; line-height:1; border-radius:4px;">×</button>
            </div>
            <div style="display:flex; background:rgba(0,0,0,0.3); border-radius:8px; padding:3px; margin-bottom:14px; border:1px solid var(--glass-border, rgba(255,255,255,0.06));">
                <button id="tab-qr-lan" type="button" onclick="window.switchBinderyQrNetworkMode('lan')" style="flex:1; padding:5px 0; font-size:0.75rem; border-radius:6px; border:none; cursor:pointer; font-weight:600; background:${isLan ? 'var(--accent, #10b981)' : 'transparent'}; color:${isLan ? '#fff' : 'var(--text-dim, rgba(255,255,255,0.6))'}; transition:all 0.2s;">
                    📶 局域网直传 (同 Wi-Fi)
                </button>
                <button id="tab-qr-public" type="button" onclick="window.switchBinderyQrNetworkMode('public')" style="flex:1; padding:5px 0; font-size:0.75rem; border-radius:6px; border:none; cursor:pointer; font-weight:600; background:${!isLan ? '#8b5cf6' : 'transparent'}; color:${!isLan ? '#fff' : 'var(--text-dim, rgba(255,255,255,0.6))'}; transition:all 0.2s;">
                    ⚡ 临时公网穿透 (5G/异地)
                </button>
            </div>
            <div id="bindery-qr-content"></div>
        `;

        root.appendChild(card);
        document.body.appendChild(root);
        document.addEventListener('keydown', onKeydown);
        requestAnimationFrame(() => { root.style.opacity = '1'; });

        if (isLan) window.loadBinderyLanQr(filename);
        else window.loadBinderyPublicQr(filename);
    };
})();
