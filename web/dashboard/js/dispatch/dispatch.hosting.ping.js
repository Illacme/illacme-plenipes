/**
 * ⚡ [V125.1] Illacme Plenipes - Hosting Channel Connectivity Ping
 * 职责：为 11 大全站托管平台提供一键凭证连通性测试、网络健康诊断与即时状态回填。
 * 🛡️ 严格遵守 SOP-02 模块拆分规范（单文件 < 300 行）与 Rule 7 / Rule 14 门禁。
 */

window.testHostingChannelPing = async function (channelId, btnEl) {
    if (!channelId) return;

    const channelMap = {
        github_pages: 'GitHub Pages',
        cloudflare_pages: 'Cloudflare Pages',
        vercel: 'Vercel',
        netlify: 'Netlify',
        render: 'Render',
        zeabur: 'Zeabur',
        railway: 'Railway',
        firebase: 'Firebase',
        gitlab_pages: 'GitLab Pages',
        gitee_pages: 'Gitee Pages',
        sftp: 'SFTP 独立主机'
    };
    const channelName = channelMap[channelId] || channelId;
    const safeEscape = (s) => (window.escapeHtml ? window.escapeHtml(s) : (s || ''));

    // 视觉反馈：按钮进入加载态
    let originalHtml = '';
    if (btnEl) {
        originalHtml = btnEl.innerHTML;
        btnEl.disabled = true;
        btnEl.innerHTML = '<span>⏳</span>';
    }

    if (typeof showToast === 'function') {
        showToast(`⚡ 正在探测【${channelName}】凭证有效性与网络延迟...`, 'info');
    }

    try {
        if (typeof apiFetch !== 'function') {
            throw new Error('API 客户端未就绪');
        }

        const res = await apiFetch('/api/dispatch/hosting/ping', {
            method: 'POST',
            body: JSON.stringify({ channel: channelId })
        });

        if (res && res.healthy) {
            const idInfo = res.identity ? `<div style="margin-top: 6px; font-size: 0.82rem; color: var(--accent);">👤 识别身份: <strong>${safeEscape(res.identity)}</strong></div>` : '';
            const latInfo = res.latency_ms ? `<span style="display: inline-block; padding: 2px 8px; border-radius: 4px; background: rgba(35, 134, 54, 0.2); color: #3fb950; font-weight: 600; font-size: 0.78rem; margin-top: 4px;">⚡ 响应延迟: ${res.latency_ms}ms</span>` : '';

            if (window.Swal && typeof window.Swal.fire === 'function') {
                await window.Swal.fire({
                    title: '🟢 连通性测试通过',
                    html: `
                        <div style="text-align: left; font-size: 0.88rem; line-height: 1.6;">
                            <div>目标平台: <strong>${channelName}</strong></div>
                            <div>诊断状态: <span style="color: #3fb950; font-weight: 600;">凭证有效 · 接口通信正常</span></div>
                            ${latInfo}
                            ${idInfo}
                            <div style="margin-top: 8px; font-size: 0.8rem; color: var(--text-muted);">${safeEscape(res.summary || '各项参数探测正常')}</div>
                        </div>
                    `,
                    icon: 'success',
                    confirmButtonText: '确定',
                    background: 'var(--bg-card, #161b22)',
                    color: 'var(--text-bright, #ffffff)',
                    customClass: { popup: 'glass-panel', confirmButton: 'primary-btn' }
                });
            } else if (typeof showToast === 'function') {
                showToast(`🟢【${channelName}】连通性测试通过 (${res.latency_ms}ms)`, 'success');
            }
        } else {
            const errSummary = (res && res.summary) || '未通过凭证或网络鉴权';
            if (window.Swal && typeof window.Swal.fire === 'function') {
                const result = await window.Swal.fire({
                    title: '❌ 连通性测试未通过',
                    html: `
                        <div style="text-align: left; font-size: 0.88rem; line-height: 1.6;">
                            <div>目标平台: <strong>${channelName}</strong></div>
                            <div style="margin-top: 6px; color: var(--danger, #f85149); font-weight: 600;">问题原因: ${safeEscape(errSummary)}</div>
                            <div style="margin-top: 8px; font-size: 0.8rem; color: var(--text-muted);">
                                建议检查 API Token 是否过期、权限配置是否完备或网络代理是否正常。
                            </div>
                        </div>
                    `,
                    icon: 'error',
                    showCancelButton: true,
                    confirmButtonText: '⚙️ 前往修改配置',
                    cancelButtonText: '关闭',
                    background: 'var(--bg-card, #161b22)',
                    color: 'var(--text-bright, #ffffff)',
                    customClass: { popup: 'glass-panel', confirmButton: 'primary-btn', cancelButton: 'secondary-btn' }
                });
                if (result.isConfirmed) {
                    window.navToHostingChannelConfig(channelId);
                }
            } else if (typeof showToast === 'function') {
                showToast(`❌【${channelName}】连通性测试未通过: ${errSummary}`, 'error');
            }
        }
    } catch (e) {
        console.error("🛑 托管渠道连通性测试失败:", e);
        if (typeof showToast === 'function') {
            showToast(`❌ 探测异常: ${e.message || e}`, 'error');
        }
    } finally {
        if (btnEl && originalHtml) {
            btnEl.disabled = false;
            btnEl.innerHTML = originalHtml;
        }
    }
};
