/**
 * 📡 [V68.0] Illacme Plenipes Vault - Hosting Cards & Local Artifacts Render Shard
 * 职责：本地多语种静态产物卡片渲染、10 大全站托管平台卡片列表构建与勾选计数联动。
 */

(function () {
    // 真实 10 大全站托管平台元数据字典 (与后端 PublisherRegistry 100% 物理对齐)
    window.vaultHostingPlatformMetadata = {
        'github_pages': { name: 'GitHub Pages', icon: '🐙', desc: 'GitHub 官方静态网页托管 (Git 自动化部署)' },
        'cloudflare_pages': { name: 'Cloudflare Pages', icon: '⚡', desc: 'Cloudflare 全球边缘 CDN 静态托管加速' },
        'vercel': { name: 'Vercel', icon: '▲', desc: '全球前端云平台 (现代 SSG 极速部署)' },
        'netlify': { name: 'Netlify', icon: '🌐', desc: '专业静态站点托管平台 (全自动 CI/CD)' },
        'firebase': { name: 'FIREBASE', icon: '🌐', desc: '全站静态站点托管发布平台' },
        'sftp': { name: 'SFTP 物理主机', icon: '🖥️', desc: 'Linux / VPS 自建服务器物理部署' },
        'render': { name: 'Render', icon: '🚀', desc: '云端全栈静态站点部署平台' },
        'railway': { name: 'Railway', icon: '🚂', desc: 'Railway 云服务自动化部署 Hook' },
        'zeabur': { name: 'Zeabur', icon: '⚡', desc: '无服务器容器化托管平台' },
        'gitee_pages': { name: 'Gitee Pages', icon: '🔴', desc: '国内 Gitee 代码托管平台 Pages 静态服务' }
    };

    window.renderVaultLocalArtifactsHtml = function (localDocMatrix, isLabActive, labUrl) {
        return (localDocMatrix || []).map((item, idx) => {
            let previewClass = 'preview-link local-preview-link';
            const statusLower = (item.status || '').toLowerCase();
            const isSuccess = ['published', 'success', 'done', 'synced'].includes(statusLower);
            const hasValidUrl = item.artifact_url && item.artifact_url !== '#' && item.artifact_url !== 'javascript:void(0)';
            const showPreview = isSuccess || hasValidUrl;

            let targetHref = item.artifact_url;
            let previewLabel = '🌐 网页预览';
            if (isLabActive) {
                previewLabel = '⚡ 实时预览';
                previewClass += ' live-pulse';
                if (item.live_url && item.live_url !== '#') {
                    targetHref = item.live_url;
                } else if (hasValidUrl) {
                    targetHref = `${labUrl}${item.artifact_url.startsWith('/') ? '' : '/'}${item.artifact_url}`;
                }
            }

            let friendlyStatus = '🟢 装帧完成';
            if (item.status === 'pending') friendlyStatus = item.progress > 0 ? `⏳ 发布中 (${item.progress}%)` : '⏳ 待发布';
            else if (item.status === 'syncing') friendlyStatus = '⚡ 正在发布...';
            else if (item.status === 'failed') friendlyStatus = '🔴 装帧异常';

            return `
                <div class="matrix-item status-${item.status} ${idx === 0 ? 'source-lang' : 'target-lang'}" style="margin-bottom: 6px;">
                    <div class="m-info">
                        <span class="m-locale">
                            ${item.locale}${item.lang_code ? ` <span class="locale-code-badge">${item.lang_code}</span>` : ''}
                            ${showPreview && hasValidUrl ? `
                                <a href="${targetHref}" target="_blank" class="${previewClass}" style="margin-top: 0; margin-left: 8px; padding: 2px 8px; font-size: 0.68rem; font-weight: 600; display: inline-flex !important; align-items: center; gap: 4px; vertical-align: middle; color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.35); background: rgba(0, 255, 136, 0.1); border-radius: 4px; text-decoration: none; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 255, 136, 0.25)';" onmouseout="this.style.background='rgba(0, 255, 136, 0.1)';">${previewLabel}</a>
                            ` : ''}
                        </span>
                        <span class="m-status-text">${friendlyStatus}</span>
                    </div>
                    <div class="m-meta">
                        <span class="m-time">${item.last_sync || '本地装帧产物'}</span>
                        ${item.tokens ? `<span class="m-tokens">${item.tokens} tokens</span>` : ''}
                        ${item.cache_info ? `<span class="m-tokens" style="opacity:0.75; margin-left:8px;">${item.cache_info}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    };

    window.renderVaultHostingCardsHtml = function (hostingPlatformsList, relPath) {
        return (hostingPlatformsList || []).map(p => {
            const rec = p.record;
            const isFailed = !!(rec && rec.status === 'failed');
            const targetUrl = rec ? rec.artifact_url : null;
            const hasValidUrl = targetUrl && targetUrl !== '#' && targetUrl !== 'javascript:void(0)';

            let statusTagHtml = p.isReady
                ? (p.isBrandInUse
                    ? '<span style="font-size: 0.65rem; color: #00ff88; font-weight: 600;">🟢 已启用</span>'
                    : '<span style="font-size: 0.65rem; color: #f59e0b; font-weight: 600;">🟡 配置就绪 (待启用)</span>')
                : '<span style="font-size: 0.65rem; color: var(--text-dim);">⚪ 待填凭据</span>';
            if (isFailed) statusTagHtml = '<span style="font-size: 0.65rem; color: #ff4d4f; font-weight: 600;">🔴 部署异常</span>';

            return `
                <div class="glass-panel" style="padding: 10px 12px; border-radius: 8px; border: 1px solid ${p.isReady ? (p.isBrandInUse ? 'rgba(0, 255, 136, 0.25)' : 'rgba(0, 242, 254, 0.2)') : 'rgba(255, 255, 255, 0.06)'}; display: flex; flex-direction: column; gap: 8px; opacity: ${p.isReady ? '1' : '0.65'}; background: ${p.isReady ? (p.isBrandInUse ? 'rgba(0, 255, 136, 0.03)' : 'rgba(0, 242, 254, 0.02)') : 'rgba(255, 255, 255, 0.01)'}; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <input type="checkbox" value="${p.id}" class="vault-hosting-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'} onchange="window.updateVaultHostingSelectionCounter()" style="accent-color: var(--accent-secondary); width: 16px; height: 16px; cursor: ${p.isReady ? 'pointer' : 'not-allowed'};">
                            <div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 0.82rem; font-weight: 600; color: ${p.isReady ? '#fff' : 'var(--text-dim)'};">${p.icon} ${p.name}</span>
                                    ${statusTagHtml}
                                </div>
                                <div style="font-size: 0.68rem; color: var(--text-dim);">${p.desc}</div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            ${p.isReady ? `
                                ${hasValidUrl ? `
                                    <a href="${targetUrl}" target="_blank" style="padding: 2px 7px; font-size: 0.65rem; font-weight: 600; color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.35); background: rgba(0, 255, 136, 0.1); border-radius: 4px; text-decoration: none; display: inline-flex; align-items: center; gap: 3px;">🔗 托管站 ↗</a>
                                ` : ''}
                                <button type="button" onclick="window.triggerChannelDispatch('${relPath}', '${p.id}')" title="单独重新发布此平台" style="padding: 2px 7px; font-size: 0.65rem; font-weight: 600; color: var(--neon-cyan); border: 1px solid rgba(0, 242, 254, 0.35); background: rgba(0, 242, 254, 0.08); border-radius: 4px; cursor: pointer;">🔄 发布</button>
                                <button type="button" onclick="window.goToHostingPluginConfig('${p.id}')" title="修改此平台的 Token 密钥或仓库参数" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">⚙️</button>
                            ` : `
                                <button type="button" onclick="window.goToHostingPluginConfig('${p.id}')" title="前往配置并激活此托管平台" style="background: rgba(0, 242, 255, 0.15); border: 1px solid rgba(0, 242, 255, 0.35); color: var(--neon-cyan, #00f2fe); border-radius: 4px; padding: 3px 8px; font-size: 0.68rem; font-weight: 600; cursor: pointer; white-space: nowrap;">⚙️ 去配置/激活</button>
                            `}
                        </div>
                    </div>
                    ${rec && rec.status === 'failed' ? `
                        <div class="error-msg" style="margin-top: 4px;">${rec.reason || '部署超时或凭据无效'}</div>
                    ` : ''}
                </div>
            `;
        }).join('');
    };
})();
