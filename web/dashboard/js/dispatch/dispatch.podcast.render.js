/**
 * 🎙️ [V115.0] Illacme Plenipes Publishing Hub - Podcast Syndication Shard
 * 职责：发布中心播客流媒体与全网分发矩阵、指标态势及单集货架渲染。
 * 🛡️ [SOP-01] 物理行数严格收敛于 300 行以内。
 */

(function () {
    window._lastPodcastOverview = null;

    /**
     * 更新顶部导航 Tab 中的播客徽章数字
     */
    window.updatePodcastBadge = async function () {
        try {
            if (typeof apiFetch !== 'function') return;
            const res = await apiFetch('/api/podcast/overview');
            if (res && res.status === 'success') {
                window._lastPodcastOverview = res;
                const badge = document.getElementById('badge-podcast-episodes');
                if (badge && res.metrics) {
                    badge.innerText = String(res.metrics.total_episodes || 0);
                }
            }
        } catch (e) {
            console.warn('[Podcast Badge] Error:', e);
        }
    };

    /**
     * 核心加载入口：渲染播客音频分发中心
     */
    window.loadDispatchPodcastCenter = async function () {
        const container = document.getElementById('dispatch-podcast-container');
        if (!container) return;

        try {
            if (typeof apiFetch !== 'function') return;
            const res = await apiFetch('/api/podcast/overview');
            if (!res || res.status !== 'success') {
                container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-danger);">⚠️ 播客发行中心加载失败，请核验物理链路。</div>';
                return;
            }

            window._lastPodcastOverview = res;
            const metrics = res.metrics || {};
            const platforms = res.platforms || [];
            const episodes = res.episodes || [];
            const pendingDocs = res.pending_docs || [];

            // 1. 同步顶部 Tab 徽章
            const badge = document.getElementById('badge-podcast-episodes');
            if (badge) badge.innerText = String(metrics.total_episodes || 0);

            // 2. 渲染全景 HTML
            container.innerHTML = `
                ${_buildMetricsHtml(metrics)}
                ${_buildPlatformsHtml(platforms, metrics, pendingDocs)}
                ${_buildEpisodesHtml(episodes, pendingDocs)}
            `;
        } catch (err) {
            console.error('🛑 加载播客音频分发中心失败:', err);
            container.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-danger);">🚨 加载异常: ${err.message}</div>`;
        }
    };

    /**
     * 构建四大态势感知卡片
     */
    function _buildMetricsHtml(m) {
        const rssUrl = m.rss_public_url || m.rss_api_url || '/podcast-feed.xml';
        const escapedRss = String(rssUrl).replace(/'/g, "\\'");
        return `
        <div class="metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 24px;">
            <div class="metric-card glass-panel" style="padding: 16px; border-radius: 12px; border: 1px solid var(--glass-border); background: rgba(var(--bg-modal-solid-rgb), 0.45); backdrop-filter: blur(10px);">
                <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>🎙️ 播客单集总数</span>
                    <span style="color: var(--accent-primary); font-size: 0.75rem;">双人对谈伴读</span>
                </div>
                <div style="font-size: 1.85rem; font-weight: 700; color: var(--text-bright); line-height: 1.2;">
                    ${m.total_episodes || 0} <span style="font-size: 0.9rem; font-weight: 400; color: var(--text-muted);">期</span>
                </div>
                <div style="font-size: 0.73rem; color: var(--text-muted); margin-top: 6px;">
                    已落盘并在静态站点发布
                </div>
            </div>

            <div class="metric-card glass-panel" style="padding: 16px; border-radius: 12px; border: 1px solid var(--glass-border); background: rgba(var(--bg-modal-solid-rgb), 0.45); backdrop-filter: blur(10px);">
                <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>⏱️ 总音频时长</span>
                    <span style="color: var(--neon-cyan); font-size: 0.75rem;">完整节目单</span>
                </div>
                <div style="font-size: 1.85rem; font-weight: 700; color: var(--text-bright); line-height: 1.2;">
                    ${m.total_duration_formatted || '0 秒'}
                </div>
                <div style="font-size: 0.73rem; color: var(--text-muted); margin-top: 6px;">
                    累计听力陪伴时长
                </div>
            </div>

            <div class="metric-card glass-panel" style="padding: 16px; border-radius: 12px; border: 1px solid var(--glass-border); background: rgba(var(--bg-modal-solid-rgb), 0.45); backdrop-filter: blur(10px);">
                <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>💾 音频物理容量</span>
                    <span style="color: ${m.r2_storage_active ? 'var(--neon-green)' : 'var(--text-muted)'}; font-size: 0.75rem;">${m.r2_storage_active ? '☁️ CDN 托管' : '本地存储'}</span>
                </div>
                <div style="font-size: 1.85rem; font-weight: 700; color: var(--text-bright); line-height: 1.2;">
                    ${m.total_size_formatted || '0 MB'}
                </div>
                <div style="font-size: 0.73rem; color: var(--text-muted); margin-top: 6px;">
                    ${m.r2_storage_active ? '已启用对象存储边缘加速' : '建议在插件中心配置 R2 CDN'}
                </div>
            </div>

            <div class="metric-card glass-panel" style="padding: 16px; border-radius: 12px; border: 1px solid var(--glass-border); background: rgba(var(--bg-modal-solid-rgb), 0.45); backdrop-filter: blur(10px);">
                <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>📻 工业级 RSS 源</span>
                    <span style="color: var(--neon-green); font-size: 0.75rem;">iTunes DTD 规范</span>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 8px;">
                    <button type="button" class="mini-btn glow-btn" onclick="window.copyPodcastRssFeed('${escapedRss}')" style="flex: 1; height: 28px; font-size: 0.76rem; background: rgba(0, 242, 254, 0.12); border-color: rgba(0, 242, 254, 0.35); color: var(--neon-cyan);" title="点击复制公开播客 RSS 订阅链接">📋 复制源</button>
                    <a href="${rssUrl}" target="_blank" class="mini-btn" style="height: 28px; line-height: 26px; padding: 0 10px; font-size: 0.76rem; text-decoration: none; display: inline-flex; align-items: center;" title="在浏览器打开原始 XML 订阅源">🔗 预览</a>
                </div>
                <div style="font-size: 0.71rem; color: var(--text-muted); margin-top: 8px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;" title="${rssUrl}">
                    ${rssUrl}
                </div>
            </div>
        </div>
        `;
    }

    /**
     * 构建全球与国内主流播客平台矩阵
     */
    function _buildPlatformsHtml(platforms, m, pendingDocs = []) {
        const pendingCount = pendingDocs.length || m.pending_episodes || 0;
        const batchBtn = pendingCount > 0
            ? `<button type="button" class="mini-btn glow-btn" onclick="window.openBatchPodcastModal()" style="font-size: 0.74rem; padding: 3px 10px; background: rgba(168, 85, 247, 0.2); border-color: rgba(168, 85, 247, 0.5); color: #c084fc;">🎙️ 批量合成待处理音频 (${pendingCount})</button>`
            : `<button type="button" class="mini-btn" onclick="window.openBatchPodcastModal()" style="font-size: 0.74rem; padding: 3px 8px;">🎙️ 巡检待合成音频</button>`;
        const cards = platforms.map(p => {
            const hasMagic = Boolean(p.magic_link);
            const isR2 = p.id === 'podcast_r2_storage';
            const actionBtn = hasMagic
                ? `<a href="${p.magic_link}" target="_blank" class="secondary-btn btn-sm" style="font-size: 0.73rem; padding: 3px 8px; text-decoration: none; display: inline-flex; align-items: center;" title="直达该平台创作者中心或提交入口">${p.magic_label || '平台中心 ↗'}</a>`
                : (isR2 ? `<button type="button" class="secondary-btn btn-sm" onclick="window.showView('plugins', 'podcast')" style="font-size: 0.73rem; padding: 3px 8px;">⚙️ 配置存储</button>` : '');

            return `
            <div class="podcast-platform-card glass-panel" style="padding: 14px; border-radius: 10px; border: 1px solid var(--glass-border); background: rgba(var(--bg-modal-solid-rgb), 0.35); display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.25rem;">${p.icon || '🎙️'}</span>
                            <span style="font-weight: 600; font-size: 0.88rem; color: var(--text-bright);">${p.name}</span>
                        </div>
                        <span class="vault-pill-badge" style="font-size: 0.68rem; padding: 2px 7px; background: rgba(0, 242, 254, 0.08); border: 1px solid rgba(0, 242, 254, 0.3); color: var(--accent-primary); border-radius: 10px;">${p.status_label || '就绪'}</span>
                    </div>
                    <div style="font-size: 0.74rem; color: var(--text-dim); line-height: 1.45; margin-bottom: 12px;">
                        ${p.desc || ''}
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 8px; margin-top: auto;">
                    <span style="font-size: 0.7rem; color: var(--text-muted);">${p.type || '播客目录'}</span>
                    ${actionBtn}
                </div>
            </div>
            `;
        }).join('');

        return `
        <div style="margin-bottom: 28px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 0.95rem; font-weight: 600; color: var(--text-bright); display: flex; align-items: center; gap: 6px;">
                    <span>🧭 全网主流播客平台矩阵</span>
                    <span style="font-size: 0.75rem; font-weight: 400; color: var(--text-muted);">(通过标准 RSS 源一次性认领，全网自动同步)</span>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    ${batchBtn}
                    <button type="button" class="mini-btn" onclick="window.showView('plugins', 'podcast')" style="font-size: 0.74rem; padding: 3px 8px;">⚙️ 播客插件配置 ↗</button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px;">
                ${cards}
            </div>
        </div>
        `;
    }

    /**
     * 构建已发布单集列表货架
     */
    function _buildEpisodesHtml(episodes) {
        if (!episodes || episodes.length === 0) {
            return `
            <div class="glass-panel" style="padding: 30px; text-align: center; border-radius: 12px; border: 1px dashed var(--glass-border);">
                <div style="font-size: 2rem; margin-bottom: 8px;">📭</div>
                <div style="font-weight: 600; color: var(--text-bright); margin-bottom: 6px;">暂无已合成的播客单集</div>
                <div style="font-size: 0.78rem; color: var(--text-dim); max-width: 480px; margin: 0 auto 14px;">
                    您可以在【原稿文库】中为文章开启播客开关，并通过右侧操作菜单【🎙️ 双人技术播客工坊】一键提炼剧本并生成音频。
                </div>
                <button type="button" class="primary-btn glow-btn" onclick="window.showView('vault')" style="padding: 5px 14px; font-size: 0.78rem;">📂 前往原稿文库</button>
            </div>
            `;
        }

        const rows = episodes.map((ep, idx) => {
            const audioSrc = ep.audio_url;
            const escapedRel = (ep.rel_path || '').replace(/'/g, "\\'");
            const docBadge = ep.rel_path
                ? `<span class="tag-pill" style="font-size: 0.7rem; cursor: pointer;" title="点击前往文库查看原稿" onclick="window.showView('vault');">${ep.rel_path}</span>`
                : `<span style="font-size: 0.7rem; color: var(--text-muted);">独立音频</span>`;

            return `
            <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                <td style="padding: 10px 14px; text-align: center; width: 44px; color: var(--text-muted); font-size: 0.8rem;">
                    ${idx + 1}
                </td>
                <td style="padding: 10px 14px;">
                    <div style="font-weight: 600; color: var(--text-bright); font-size: 0.88rem; margin-bottom: 3px;">
                        ${ep.title}
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        ${docBadge}
                        <span style="font-size: 0.7rem; color: var(--accent-primary); background: rgba(0, 242, 254, 0.08); padding: 1px 6px; border-radius: 4px;">${ep.style_label}</span>
                        <span style="font-size: 0.7rem; color: var(--text-muted);">${ep.lang ? ep.lang.toUpperCase() : 'ZH'}</span>
                        <span style="font-size: 0.7rem; color: var(--text-dim);">📅 ${ep.updated_at}</span>
                    </div>
                </td>
                <td style="padding: 10px 14px; text-align: center; white-space: nowrap;">
                    <span style="font-family: var(--font-mono, monospace); font-size: 0.82rem; color: var(--text-bright);">⏱️ ${ep.duration_formatted}</span>
                    <div style="font-size: 0.7rem; color: var(--text-muted);">${ep.chapters_count} 个章节</div>
                </td>
                <td style="padding: 10px 14px; text-align: center; white-space: nowrap;">
                    <span style="font-family: var(--font-mono, monospace); font-size: 0.82rem; color: var(--text-muted);">${ep.size_formatted}</span>
                </td>
                <td style="padding: 10px 14px; text-align: center; min-width: 250px;">
                    <div style="display: flex; align-items: center; gap: 6px; justify-content: center;">
                        <audio controls preload="none" src="${audioSrc}" style="height: 28px; max-width: 155px; outline: none;"></audio>
                        ${ep.rel_path ? `<button type="button" class="mini-btn" onclick="if(window.openPodcastStudioModal) window.openPodcastStudioModal('${escapedRel}');" style="height: 28px; padding: 0 7px; font-size: 0.74rem;" title="打开播客工坊微调台词或重编">🎙️</button>` : ''}
                        <a href="${audioSrc}" download="${ep.filename}" class="mini-btn" style="height: 28px; line-height: 26px; padding: 0 7px; font-size: 0.74rem; text-decoration: none;" title="下载原版 MP3">⬇️</a>
                        <button type="button" class="mini-btn danger" onclick="if(window.deletePodcastEpisode) window.deletePodcastEpisode('${ep.filename}');" style="height: 28px; padding: 0 7px; font-size: 0.74rem;" title="物理删除该期单集缓存">🗑️</button>
                    </div>
                </td>
            </tr>
            `;
        }).join('');

        return `
        <div style="margin-bottom: 30px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div style="font-size: 0.95rem; font-weight: 600; color: var(--text-bright); display: flex; align-items: center; gap: 6px;">
                    <span>🎙️ 已发行播客单集货架 (Cataloged Podcast Releases)</span>
                    <span style="font-size: 0.75rem; font-weight: 400; color: var(--text-muted);">(共 ${episodes.length} 期)</span>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button type="button" class="mini-btn" onclick="if(window.batchSyncPodcastsToCdn) window.batchSyncPodcastsToCdn(this);" style="padding: 4px 10px; font-size: 0.76rem; color: var(--accent-primary); border-color: rgba(0, 242, 254, 0.3);" title="将本地全部已合成 MP3 批量上传至 R2/S3 对象存储 CDN">☁️ 批量转储 CDN</button>
                </div>
            </div>
            <div class="table-container glass-panel" style="border-radius: 12px; overflow: hidden; border: 1px solid var(--glass-border);">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--glass-border); background: rgba(var(--bg-modal-solid-rgb), 0.6); color: var(--text-dim); text-align: left;">
                            <th style="padding: 10px 14px; text-align: center; width: 44px;">#</th>
                            <th style="padding: 10px 14px;">单集名称与原稿溯源</th>
                            <th style="padding: 10px 14px; text-align: center; width: 120px;">时长 / 章节</th>
                            <th style="padding: 10px 14px; text-align: center; width: 100px;">文件体积</th>
                            <th style="padding: 10px 14px; text-align: center; width: 220px;">在线试听与交付</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        </div>
        `;
    }

    window.copyPodcastRssFeed = function (url) {
        if (!url) return;
        const fullUrl = url.startsWith('http') ? url : (window.location.origin + (url.startsWith('/') ? '' : '/') + url);
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(fullUrl).then(() => {
                if (typeof window.showToast === 'function') window.showToast('📋 播客 RSS 订阅链接已复制到剪贴板！', 'success');
            }).catch(() => _fallbackCopy(fullUrl));
        } else _fallbackCopy(fullUrl);
    };

    function _fallbackCopy(text) {
        const ta = document.createElement('textarea');
        ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        try {
            document.execCommand('copy');
            if (typeof window.showToast === 'function') window.showToast('📋 播客 RSS 订阅链接已复制到剪贴板！', 'success');
        } catch (e) { prompt('请手动复制播客 RSS 链接：', text); }
        document.body.removeChild(ta);
    }
})();

