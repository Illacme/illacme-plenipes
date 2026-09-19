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
            let previewClass = 'preview-link local-preview-link vault-preview-link';
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
                <div class="matrix-item status-${item.status} ${idx === 0 ? 'source-lang' : 'target-lang'}">
                    <div class="m-info">
                        <div class="m-locale-group">
                            <span class="m-locale-name" title="${item.locale}">${item.locale}</span>
                            ${item.lang_code ? `<span class="locale-code-badge">${item.lang_code}</span>` : ''}
                        </div>
                        <div class="m-status-group">
                            ${showPreview && hasValidUrl ? `
                                <a href="${targetHref}" target="_blank" class="${previewClass}">${previewLabel}</a>
                            ` : ''}
                            <span class="m-status-text">${friendlyStatus}</span>
                        </div>
                    </div>
                    <div class="m-meta">
                        <span class="m-time">${item.last_sync || '本地装帧产物'}</span>
                        ${item.tokens ? `<span class="m-tokens">${item.tokens} tokens</span>` : ''}
                        ${item.cache_info ? `<span class="m-tokens cache-info">${item.cache_info}</span>` : ''}
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

            // Status tag via CSS class
            let statusClass = 'hosting-status hosting-status--unconfigured';
            let statusIcon = '⚪ 待填凭据';
            if (p.isReady && p.isBrandInUse) {
                statusClass = 'hosting-status hosting-status--enabled';
                statusIcon = '🟢 已启用';
            } else if (p.isReady) {
                statusClass = 'hosting-status hosting-status--ready';
                statusIcon = '🟡 配置就绪 (待启用)';
            }
            if (isFailed) {
                statusClass = 'hosting-status hosting-status--failed';
                statusIcon = '🔴 部署异常';
            }
            const statusTagHtml = `<span class="${statusClass}">${statusIcon}</span>`;

            // Card state class
            let cardStateClass = 'hosting-card';
            if (p.isReady && p.isBrandInUse) cardStateClass = 'hosting-card hosting-card--brand';
            else if (p.isReady) cardStateClass = 'hosting-card hosting-card--active';

            // Platform name class
            const nameClass = p.isReady ? 'hosting-platform-name hosting-platform-name--active' : 'hosting-platform-name hosting-platform-name--inactive';

            return `
                <div class="glass-panel ${cardStateClass}">
                    <div class="hosting-card-header-row">
                        <div class="hosting-card-identity">
                            <input type="checkbox" value="${p.id}" class="vault-hosting-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'} onchange="window.updateVaultHostingSelectionCounter()">
                            <div class="hosting-card-text-col">
                                <div class="hosting-platform-title-row">
                                    <span class="${nameClass}">${p.icon} ${p.name}</span>
                                    ${statusTagHtml}
                                </div>
                                <div class="hosting-desc-text" title="${p.desc}">${p.desc}</div>
                            </div>
                        </div>
                        <div class="hosting-card-actions">
                            ${p.isReady ? `
                                ${hasValidUrl ? `
                                    <a href="${targetUrl}" target="_blank" class="hosting-link-btn">🔗 托管站 ↗</a>
                                ` : ''}
                                <button type="button" onclick="window.triggerChannelDispatch('${relPath}', '${p.id}')" title="单独重新发布此平台" class="hosting-dispatch-btn">🔄 发布</button>
                                <button type="button" onclick="window.goToHostingPluginConfig('${p.id}')" title="修改此平台的 Token 密钥或仓库参数" class="hosting-settings-btn">⚙️</button>
                            ` : `
                                <button type="button" onclick="window.goToHostingPluginConfig('${p.id}')" title="前往配置并激活此托管平台" class="hosting-config-btn">⚙️ 去配置/激活</button>
                            `}
                        </div>
                    </div>
                    ${rec && rec.status === 'failed' ? `
                        <div class="error-msg hosting-error-text">${rec.reason || '部署超时或凭据无效'}</div>
                    ` : ''}
                </div>
            `;
        }).join('');
    };
})();
