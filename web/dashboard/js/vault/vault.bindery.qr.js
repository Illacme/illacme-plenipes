/**
 * Illacme Plenipes - Vault Bindery QR Mobile Sync
 * 模块职责：移动端/平板设备局域网扫码直传 (LAN Mobile Sync) 弹窗渲染与交互。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */
(function() {
    'use strict';

    function esc(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function onKeydown(e) {
        if (e.key === 'Escape') {
            window.closeBinderyQrModal();
        }
    }

    window.closeBinderyQrModal = function() {
        const root = document.getElementById('bindery-qr-modal-root');
        if (root) {
            root.style.opacity = '0';
            setTimeout(() => {
                if (root && root.parentNode) root.parentNode.removeChild(root);
            }, 200);
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
                setTimeout(() => {
                    btn.innerHTML = orig;
                    btn.style.borderColor = '';
                    btn.style.color = '';
                }, 1500);
            }
            if (typeof window.showToast === 'function') {
                window.showToast('📋 直链已复制到剪贴板', 'success');
            }
        }).catch(err => {
            console.error('复制失败:', err);
            if (typeof window.showToast === 'function') {
                window.showToast('❌ 复制失败，请手动选择复制', 'error');
            }
        });
    };

    window.openBinderyQrModal = async function(filename) {
        if (!filename) return;
        window.closeBinderyQrModal();

        const root = document.createElement('div');
        root.id = 'bindery-qr-modal-root';
        root.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.65); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); z-index:99999; display:flex; align-items:center; justify-content:center; opacity:0; transition:opacity 0.2s ease;';
        root.onclick = function(e) {
            if (e.target === root) window.closeBinderyQrModal();
        };

        const card = document.createElement('div');
        card.style.cssText = 'background:var(--panel-bg, #1e293b); border:1px solid var(--glass-border, rgba(255,255,255,0.12)); box-shadow:0 20px 45px rgba(0,0,0,0.5); border-radius:14px; width:92%; max-width:440px; padding:24px; color:var(--text-bright, #fff); position:relative;';

        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.3rem;">📱</span>
                    <strong style="font-size:1.05rem; color:var(--text-bright, #fff);">局域网扫码直传 (LAN Mobile Sync)</strong>
                </div>
                <button type="button" onclick="window.closeBinderyQrModal()" style="background:none; border:none; color:var(--text-dim, rgba(255,255,255,0.5)); font-size:1.3rem; cursor:pointer; padding:2px 6px; line-height:1; border-radius:4px;">×</button>
            </div>
            <div id="bindery-qr-content" style="text-align:center; padding:20px 10px;">
                <div style="font-size:1.5rem; margin-bottom:10px;"><span class="pulse-spin" style="display:inline-block;">⏳</span></div>
                <div style="font-size:0.85rem; color:var(--text-dim, rgba(255,255,255,0.7));">正在生成移动端传输二维码与局域网节点...</div>
            </div>
        `;

        root.appendChild(card);
        document.body.appendChild(root);
        document.addEventListener('keydown', onKeydown);

        requestAnimationFrame(() => {
            root.style.opacity = '1';
        });

        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const res = await fetchFunc(`/api/bindery/qr?file=${encodeURIComponent(filename)}`);
            const data = (res && typeof res.json === 'function') ? await res.json() : res;

            const contentEl = document.getElementById('bindery-qr-content');
            if (!contentEl) return;

            if (!data || !data.success) {
                contentEl.innerHTML = `
                    <div style="color:#ef4444; font-size:1.5rem; margin-bottom:8px;">⚠️</div>
                    <div style="color:#ef4444; font-size:0.9rem; font-weight:600;">生成二维码失败</div>
                    <div style="color:var(--text-dim, rgba(255,255,255,0.6)); font-size:0.75rem; margin-top:6px;">${esc((data && data.detail) || '无法探测局域网节点')}</div>
                `;
                return;
            }

            const isWb = filename.endsWith('.html');
            const targetTip = isWb ? '手机 / 平板扫码可直接在线全屏翻阅' : 'iPhone / iPad (Books)、Android、Kindle 扫码即刻下载导入';
            const qrBlockHtml = data.qr_data_uri
                ? `<div style="background:#ffffff; border-radius:12px; padding:12px; display:inline-block; box-shadow:0 6px 20px rgba(0,0,0,0.3); margin-bottom:14px;"><img src="${data.qr_data_uri}" alt="扫码下载" style="width:200px; height:200px; display:block;" /></div>`
                : `<div style="background:rgba(255,255,255,0.04); border:1px dashed var(--glass-border, rgba(255,255,255,0.18)); border-radius:12px; padding:22px 14px; margin-bottom:14px;"><div style="font-size:2rem; margin-bottom:6px;">📡</div><div style="font-size:0.85rem; font-weight:600; color:var(--text-bright, #fff); margin-bottom:4px;">局域网直连链路就绪</div><div style="font-size:0.72rem; color:var(--text-dim, rgba(255,255,255,0.6));">移动设备连接同一 Wi-Fi 后，直接在浏览器中打开下方直链即可</div><div style="margin-top:10px; font-size:0.68rem; color:#38bdf8; background:rgba(56,189,248,0.1); padding:4px 8px; border-radius:4px; display:inline-block;">💡 提示：终端运行 pip install qrcode 即可启用图形二维码扫码</div></div>`;

            contentEl.innerHTML = `
                ${qrBlockHtml}
                <div style="font-size:0.85rem; font-weight:600; color:var(--text-bright, #fff); margin-bottom:4px; word-break:break-all;">
                    ${esc(filename)}
                </div>
                <div style="font-size:0.75rem; color:var(--accent, #10b981); margin-bottom:14px;">
                    ✨ ${targetTip}
                </div>
                <div style="background:rgba(0,0,0,0.25); border:1px solid var(--glass-border, rgba(255,255,255,0.08)); border-radius:8px; padding:8px 10px; display:flex; align-items:center; gap:8px; margin-bottom:14px; text-align:left;">
                    <div style="font-size:0.72rem; color:var(--text-dim, rgba(255,255,255,0.6)); min-width:0; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-family:var(--font-mono, monospace);">
                        ${esc(data.url)}
                    </div>
                    <button type="button" onclick="window.copyBinderyQrUrl('${esc(data.url)}', this)" class="mini-btn" style="padding:4px 8px; font-size:0.72rem; border-radius:5px; border:1px solid var(--glass-border, rgba(255,255,255,0.15)); background:rgba(255,255,255,0.08); color:var(--text-bright, #fff); cursor:pointer; white-space:nowrap; flex-shrink:0;">
                        📋 复制
                    </button>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.72rem; color:var(--text-dim, rgba(255,255,255,0.5)); border-top:1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-top:12px;">
                    <span>局域网节点: <strong style="color:var(--text-bright, #fff);">${esc(data.lan_ip)}:${esc(data.port)}</strong></span>
                    <a href="${esc(data.url)}" target="_blank" rel="noopener noreferrer" style="color:var(--accent, #38bdf8); text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                        在新标签打开 ↗
                    </a>
                </div>
            `;
        } catch (e) {
            console.error('[BinderyQR] 弹窗加载异常:', e);
            const contentEl = document.getElementById('bindery-qr-content');
            if (contentEl) {
                contentEl.innerHTML = `<div style="color:#ef4444; font-size:0.85rem;">⚠️ 获取移动端同步信息失败，请检查网络连接</div>`;
            }
        }
    };
})();
