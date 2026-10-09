/**
 * 🚀 [V125.0] Illacme Plenipes - Hosting Deploy Workbench Renderer
 * 职责：负责全站托管大盘三大战区（静态产物总控、11 大托管舰队网格、整站部署批次流水）渲染与动作交互。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

window._lastHostingOverview = null;

/**
 * 加载并渲染全站托管大盘数据
 */
window.loadHostingDeployCenter = async function () {
    const consoleBox = document.getElementById('hosting-control-console');
    const fleetBox = document.getElementById('hosting-fleet-container');
    const batchBox = document.getElementById('hosting-batch-container');

    try {
        if (typeof apiFetch !== 'function') return;
        const res = await apiFetch('/api/dispatch/hosting/overview');
        if (!res || res.status !== 'success') return;

        window._lastHostingOverview = res;

        // 更新顶部胶囊徽章与三大战区
        const badgeReady = document.getElementById('badge-hosting-ready');
        if (badgeReady) badgeReady.innerText = `${res.ready_channels || 0}/${res.total_channels || 11}`;
        if (consoleBox) window.renderHostingControlCenter(res.bundle || {}, res.ready_channels || 0, res.total_channels || 11);
        if (fleetBox) window.renderHostingFleetGrid(res.fleet || []);
        if (batchBox && typeof window.renderHostingBatchLedger === 'function') {
            window.renderHostingBatchLedger(res.batches || [], res.pagination || null);
        }
        if (typeof window.startHostingDeployPolling === 'function' && (res.batches || []).some(b => b && (b.overall_status === 'RUNNING' || b.overall_status === 'PENDING'))) {
            window.startHostingDeployPolling();
        }
    } catch (e) {
        console.error("🛑 加载全站托管大盘异常:", e);
        if (consoleBox) consoleBox.innerHTML = `<div style="padding: 20px; color: var(--text-danger); font-size: 0.85rem;">调取托管大盘失败: ${e.message || e}</div>`;
    }
};

/**
 * 战区一：整站编译态势与并发调度总控台
 */
window.renderHostingControlCenter = function (bundle, readyChannels, totalChannels) {
    const box = document.getElementById('hosting-control-console');
    if (!box) return;

    const exists = Boolean(bundle.bundle_exists);
    const themeName = (window.getThemeDisplayName ? window.getThemeDisplayName(bundle.theme) : bundle.theme) || 'Sovereign';
    const statusTag = exists
        ? `<span class="tag-status success">● 网站已就绪，可随时发布</span>`
        : `<span class="tag-status failed">● 尚未生成网站内容</span>`;

    box.innerHTML = `
        <div class="hosting-console-card">
            <div class="console-left">
                <div class="console-title-row">
                    <span class="console-title">📦 待发布网站内容 (Website Content)</span>
                    ${statusTag}
                </div>
                <div class="console-meta-grid">
                    <div class="meta-item"><span class="meta-k">网站主题:</span><span class="meta-v highlight">${window.escapeHtml ? window.escapeHtml(themeName) : themeName}</span></div>
                    <div class="meta-item"><span class="meta-k">包含页面:</span><span class="meta-v" title="编译生成 ${bundle.pages_count ?? 0} 个静态网页产物">${bundle.pages_count ?? 0} 个网页 <span style="font-size: 0.68rem; color: var(--text-muted); font-weight: normal;">(共 ${bundle.total_files || bundle.pages_count || 0} 个资源)</span></span></div>
                    <div class="meta-item"><span class="meta-k">内容大小:</span><span class="meta-v">${bundle.bundle_size_formatted || '0 KB'}</span></div>
                    <div class="meta-item"><span class="meta-k">生成时间:</span><span class="meta-v">${bundle.last_built_at || '--'}</span></div>
                    <div class="meta-item full-width"><span class="meta-k">存储状态:</span><span class="meta-v code-path" title="${bundle.bundle_path || ''}">本地已就绪 (可随时发布)</span></div>
                </div>
            </div>
            <div class="console-right-actions">
                <button class="primary-btn glow-btn" onclick="window.triggerFullHostingDeploy();" ${exists ? '' : 'disabled'} title="${exists ? `一键向全部 ${readyChannels} 个已就绪平台发布网站内容` : '网站内容未就绪，请先生成网站'}">
                    <span class="btn-icon">🚀</span> 一键发布到所有平台 (${readyChannels} 个平台已就绪)
                </button>
                <div class="console-action-subrow">
                    <button class="secondary-btn" onclick="if(typeof window.showView==='function') window.showView('settings', 'themes');"><span>🎨 装帧主题 ↗</span></button>
                    <button class="secondary-btn" onclick="if(typeof window.triggerPublish==='function') window.triggerPublish(false);"><span>⚡ 重新生成网站</span></button>
                </div>
                <div style="font-size: 0.72rem; color: var(--text-dim); text-align: center; margin-top: 4px;">
                    💡 直接发布当前网站内容，极速上线无需重新排版与翻译
                </div>
            </div>
        </div>
    `;
};

/**
 * 战区二：11 大全站托管平台渠道舰队网格卡片
 */
window.renderHostingFleetGrid = function (fleet) {
    const box = document.getElementById('hosting-fleet-container');
    const subtag = document.getElementById('hosting-fleet-subtag');
    if (!box) return;

    // 仅列出配置就绪并在当前品牌启用的平台
    const activeFleet = (Array.isArray(fleet) ? fleet : []).filter(ch => ch && ch.enabled);

    if (subtag) {
        subtag.innerText = activeFleet.length > 0 
            ? `已连接 ${activeFleet.length} 个可用发布平台` 
            : `未配置就绪平台 · 点击右侧平台配置`;
    }

    if (activeFleet.length === 0) {
        box.innerHTML = `
            <div class="hosting-empty-fleet-card">
                <span class="empty-icon">🌐</span>
                <span class="empty-title">尚未启用网站托管平台</span>
                <span class="empty-desc">
                    原生集成 GitHub Pages、Cloudflare Pages、Vercel、Netlify 等主流平台。<br>
                    前往配置并启用平台账号后，即可在此一键发布整站。
                </span>
                <button class="primary-btn btn-sm" onclick="if(typeof window.showView==='function') window.showView('plugins', 'hosting');" style="margin-top: 6px;">
                    <span>⚙️ 前往配置托管平台 ↗</span>
                </button>
            </div>
        `;
        return;
    }

    box.innerHTML = activeFleet.map(ch => {
        const urlDisplay = ch.site_url 
            ? `<a href="${ch.site_url}" target="_blank" class="fleet-domain-link" title="点击访问发布网址">${ch.site_url} ↗</a>`
            : `<span class="fleet-domain-none">未绑定域名</span>`;

        const isFailed = ch.last_status === 'FAILED' || ch.last_status === 'ERROR';
        const hasHistory = ch.last_deployed_at && ch.last_deployed_at !== '--';
        const deployBtnIcon = isFailed ? '🔄' : '🚀', deployBtnText = isFailed ? '重新发布' : '立即发布';
        const deployBtnTitle = isFailed ? '上次发布未完成，点击重试' : (hasHistory ? `上次发布：${ch.last_deployed_at}，点击重新发布` : `发布到 ${ch.name}`);

        return `
            <div class="hosting-fleet-card is-ready">
                <div class="fleet-card-header">
                    <div class="fleet-title-wrapper">
                        <span class="fleet-icon">${ch.icon || '🌐'}</span>
                        <div class="fleet-titles">
                            <span class="fleet-name">${window.escapeHtml ? window.escapeHtml(ch.name) : ch.name}</span>
                            <span class="fleet-status-tag">
                                <span class="fleet-dot dot-ready"></span>
                                <span class="fleet-status-label">已连接</span>
                            </span>
                        </div>
                    </div>
                </div>
                <div class="fleet-card-body">
                    <div class="fleet-meta-row">
                        <span class="meta-label">访问网址:</span>
                        <span class="meta-value">${urlDisplay}</span>
                    </div>
                    <div class="fleet-meta-row">
                        <span class="meta-label">上次发布:</span>
                        <span class="meta-value">${ch.last_deployed_at || '--'}</span>
                    </div>
                </div>
                <div class="fleet-card-footer">
                    <button class="secondary-btn btn-sm ${isFailed ? 'danger' : ''}" onclick="window.triggerFullHostingDeploy('${ch.id}');" title="${deployBtnTitle}">
                        <span>${deployBtnIcon} ${deployBtnText}</span>
                    </button>
                    <button class="secondary-btn btn-sm icon-only" onclick="window.testHostingChannelPing('${ch.id}', this);" title="连通性测试 (API 凭证与网络健康度)">
                        <span>⚡</span>
                    </button>
                    <button class="secondary-btn btn-sm icon-only" onclick="window.navToHostingChannelConfig('${ch.id}');" title="平台账号配置">
                        <span>⚙️</span>
                    </button>
                </div>
            </div>
        `;
    }).join('');
};



/**
 * 触发全站托管部署（支持全部或定向单渠道）
 */
window.triggerFullHostingDeploy = async function (targetChannel = null, options = {}) {
    const channelMap = {
        github_pages: 'GitHub Pages', vercel: 'Vercel', cloudflare_pages: 'Cloudflare Pages',
        cloudflare: 'Cloudflare Pages', netlify: 'Netlify', firebase_hosting: 'Firebase Hosting',
        supabase_storage: 'Supabase Storage', render: 'Render', railway: 'Railway',
        gitlab_pages: 'GitLab Pages', gitee_pages: 'Gitee Pages', s3_compatible: 'S3 存储'
    };
    const flt = (window._lastHostingOverview?.fleet || []).find(f => f && f.id === targetChannel);
    const channelName = flt?.name || (targetChannel && channelMap[targetChannel]) || targetChannel || '全部已就绪平台';
    const isRedeploy = Boolean(options && options.isRedeploy);
    const actionVerb = isRedeploy ? '再次发布' : '发布';
    const iconEmoji = isRedeploy ? '🔄' : '🚀';

    if (window.Swal && typeof window.Swal.fire === 'function') {
        const confirmRes = await window.Swal.fire({
            title: `${iconEmoji} 确认${actionVerb}网站`,
            text: `确认将全站内容${actionVerb}到【${channelName}】吗？`,
            icon: 'question', showCancelButton: true,
            confirmButtonText: `${iconEmoji} 立即${actionVerb}`,
            cancelButtonText: '取消',
            background: 'var(--bg-card, #161b22)', color: 'var(--text-bright, #ffffff)',
            customClass: { popup: 'glass-panel', confirmButton: 'primary-btn glow-btn', cancelButton: 'secondary-btn' }
        });
        if (!confirmRes.isConfirmed) return;
    } else if (!confirm(`${iconEmoji} 确认将网站${actionVerb}到【${channelName}】吗？`)) {
        return;
    }

    try {
        if (typeof showToast === 'function') showToast(`${iconEmoji} 正在${actionVerb}网站内容...`, 'info');
        if (typeof apiFetch !== 'function') return;

        const res = await apiFetch('/api/dispatch/hosting/deploy', {
            method: 'POST',
            body: JSON.stringify({ target_channel: targetChannel, trigger_source: isRedeploy ? 'redeploy' : 'workbench' })
        });

        if (res && res.status === 'success') {
            if (typeof showToast === 'function') showToast(`✅ 网站发布任务已启动 (${res.batch_id})`, 'success');
            window.loadHostingDeployCenter();
            if (typeof window.startHostingDeployPolling === 'function') window.startHostingDeployPolling();
            if (window._currentHostingLogBatchId && typeof window.openHostingDeployLogDrawer === 'function') {
                window.openHostingDeployLogDrawer(res.batch_id);
            }
        } else {
            throw new Error((res && res.detail) || '部署启动失败');
        }
    } catch (e) {
        console.error("🛑 触发全站托管部署失败:", e);
        if (typeof showToast === 'function') showToast(`❌ 部署失败: ${e.message || e}`, 'error');
        else alert(`部署失败: ${e.message || e}`);
    }
};

/**
 * 智能直达对应托管平台配置抽屉
 */
window.navToHostingChannelConfig = function (channelId) {
    if (typeof window.openPluginConfig === 'function') window.openPluginConfig(channelId, 'hosting');
    else if (typeof window.showView === 'function') window.showView('plugins', 'hosting');
};
