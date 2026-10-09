/**
 * 📡 [V68.0] Illacme Plenipes Vault - Hosting Cards & Local Artifacts Render Shard
 * 职责：本地多语种静态产物卡片渲染、10 大全站托管平台卡片列表构建与勾选计数联动。
 */

(function () {
    /**
     * 🛰️ 全站托管平台元数据解析算子 (100% 溯源自插件矩阵与品牌徽章字典)
     */
    window.getVaultHostingMeta = function (id) {
        const tid = String(id || '').trim().toLowerCase();
        const cleanId = tid.replace(/[_-\s]/g, '');

        // 1. 唯一溯源自插件中心智库 (window.allPlugins)
        let pluginObj = null;
        if (Array.isArray(window.allPlugins) && window.allPlugins.length > 0) {
            pluginObj = window.allPlugins.find(p => {
                const pid = (p.id || '').toLowerCase();
                return pid === tid || pid.replace(/[_-\s]/g, '') === cleanId;
            });
        }

        // 2. 调取平台专属品牌徽章算子 (getPlatformBrandBadge)
        const brand = (typeof window.getPlatformBrandBadge === 'function')
            ? window.getPlatformBrandBadge(tid, 'hosting')
            : null;

        const name = (pluginObj && pluginObj.name) || tid.replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const icon = (pluginObj && pluginObj.icon && pluginObj.icon !== '🌐')
            ? pluginObj.icon
            : ((brand && brand.icon) || '🌐');
        const desc = (pluginObj && (pluginObj.description || pluginObj.desc)) || `全站静态站点托管发布平台 (${name})`;

        return { name, icon, desc };
    };

    // 兼容历史调用：代理到动态解析器以防外部未更新脚本报错
    window.vaultHostingPlatformMetadata = new Proxy({}, {
        get: (target, prop) => {
            if (typeof prop === 'string') {
                return window.getVaultHostingMeta(prop);
            }
            return target[prop];
        }
    });

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
        const list = Array.isArray(hostingPlatformsList) ? hostingPlatformsList : [];
        return list.map(p => {
            const rec = p.record;
            const isFailed = !!(rec && rec.status === 'failed');
            const targetUrl = rec ? rec.artifact_url : null;
            const hasValidUrl = targetUrl && targetUrl !== '#' && targetUrl !== 'javascript:void(0)';

            // Status tag via CSS class
            let statusClass = 'hosting-status hosting-status--unconfigured';
            let statusIcon = p.credLabel ? `⚪ ${p.credLabel}` : '⚪ 待填凭据';
            if (p.isPrimary && p.isBrandInUse && p.isReady) {
                statusClass = 'hosting-status hosting-status--enabled';
                statusIcon = '🏠 官方主站';
            } else if (p.isPrimary && p.isBrandInUse) {
                statusClass = 'hosting-status hosting-status--unconfigured';
                statusIcon = `🏠 主站 (${p.credLabel || '待填凭据'})`;
            } else if (p.isReady && p.isBrandInUse) {
                statusClass = 'hosting-status hosting-status--enabled';
                statusIcon = '🟢 备用镜像';
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
