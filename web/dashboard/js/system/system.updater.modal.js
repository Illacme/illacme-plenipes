/**
 * 🛰️ Illacme Plenipes UI - System Update Modal & Silent Download Shard
 * 职责：负责更新向导专属毛玻璃弹窗渲染、下载进度动态轮询与平滑接力热重启。
 * 🛡️ [SOP-01 & SOP-03 视觉主权规范]：单文件严格 ≤ 300 行。
 */

(function () {
    'use strict';

    /**
     * 🚀 渲染并弹出高档毛玻璃更新向导弹窗 (支持秒开骨架屏、新版本升级与当前最新版特性速览)
     */
    window.openUpdateModal = function (isSkeleton = false) {
        let modal = document.getElementById('system-update-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'system-update-modal';
            modal.className = 'updater-modal-backdrop';
            modal.onclick = (e) => { if (e.target === modal) window.closeUpdateModal(); };
            document.body.appendChild(modal);
        }

        const info = window._latestUpdateInfo;

        // 骨架屏秒开态：若无数据或显式指定骨架态，0ms 立即展现流光加载
        if (!info || isSkeleton) {
            modal.innerHTML = `
                <div class="updater-modal-card">
                    <div class="updater-modal-header">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="font-size:1.4rem;">🛰️</span>
                            <div>
                                <h3 style="margin:0;font-size:1.05rem;font-weight:800;letter-spacing:0.5px;">正在同步云端发版状态...</h3>
                                <div style="font-size:0.72rem;margin-top:2px;">正在连接 GitHub Releases 官方同步中枢 · 请稍候</div>
                            </div>
                        </div>
                        <button type="button" class="updater-modal-close-btn" onclick="window.closeUpdateModal()" title="关闭">✕</button>
                    </div>
                    <div class="updater-modal-body">
                        <div class="updater-skeleton-box" style="height:64px;margin-bottom:12px;"></div>
                        <div class="updater-skeleton-line" style="width:35%;margin-bottom:10px;"></div>
                        <div class="updater-skeleton-box" style="height:220px;border-radius:10px;"></div>
                    </div>
                    <div class="updater-modal-footer">
                        <span style="font-size:0.76rem;color:var(--text-muted);">正在极速同步中...</span>
                        <button type="button" class="updater-footer-close-btn" onclick="window.closeUpdateModal()">关闭</button>
                    </div>
                </div>`;
            modal.style.display = 'flex';
            if (!info && typeof window.checkSystemUpdate === 'function') {
                window.checkSystemUpdate(true);
            }
            return;
        }

        const isUpToDate = !info.has_update;
        const modalIcon = isUpToDate ? '🎉' : '🚀';
        const modalTitle = isUpToDate 
            ? `当前已是最新正式版本 ${info.current_version}` 
            : `发现新版本 ${info.latest_version}`;
        const modalSub = isUpToDate 
            ? `与 GitHub 官方正式发版同步 · 发布于: ${info.published_at ? info.published_at.slice(0, 10) : '近期'}`
            : `当前运行版本: ${info.current_version} · 发布于: ${info.published_at ? info.published_at.slice(0, 10) : '近期'}`;

        const asset = info.recommended_asset;
        const btnText = isUpToDate ? '📥 重新下载/备份安装包' : '⚡ 一键静默升级';
        const tagText = isUpToDate ? '当前系统专属安装包' : '专属推荐安装包';
        const assetHtml = asset ? `
            <div id="updater-card-box" class="updater-asset-card">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
                    <div style="display:flex;flex-direction:column;gap:4px;overflow:hidden;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span class="updater-asset-badge">${tagText}</span>
                            <span class="updater-asset-name">${asset.name}</span>
                        </div>
                        <div class="updater-asset-meta">格式: ${asset.format_desc} · 产物体积: ${asset.size_mb} MB</div>
                    </div>
                    <button type="button" id="btn-silent-update-action" class="updater-asset-btn" onclick="window.startSilentUpdate('${asset.download_url}', '${info.latest_version}')">
                       ${btnText}
                    </button>
                </div>
                <div id="updater-progress-wrapper" style="display:none;flex-direction:column;gap:6px;padding-top:8px;border-top:1px dashed rgba(0,240,255,0.2);">
                    <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-muted);">
                        <span id="updater-progress-status-text">正在建立安全下载通道...</span>
                        <span id="updater-progress-percent-text" style="color:var(--neon-cyan);font-weight:700;font-family:var(--font-mono);">0%</span>
                    </div>
                    <div style="height:6px;background:rgba(255,255,255,0.08);border-radius:4px;overflow:hidden;width:100%;">
                        <div id="updater-progress-bar-fill" style="height:100%;width:0%;background:linear-gradient(90deg, var(--neon-cyan), #00ff88);transition:width 0.3s ease;"></div>
                    </div>
                </div>
            </div>` : `<div style="background:var(--white-05);border:1px solid var(--glass-border);border-radius:12px;padding:12px;margin:12px 0;text-align:center;color:var(--text-muted);font-size:0.8rem;">暂未检测到当前平台的专属安装包，请在下方 GitHub 链接下载通用版本。</div>`;

        let notesHtml = '无详细更新说明。';
        if (info.release_notes) {
            if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
                try { notesHtml = marked.parse(info.release_notes); } catch (_) { notesHtml = info.release_notes.replace(/\n/g, '<br>'); }
            } else {
                notesHtml = info.release_notes
                    .replace(/###\s*(.*)/g, '<h4 style="margin:8px 0 4px;color:var(--neon-cyan);font-size:0.88rem;">$1</h4>')
                    .replace(/\*\s*(.*)/g, '<li style="margin-left:16px;margin-bottom:3px;font-size:0.8rem;">$1</li>')
                    .replace(/\n\n/g, '<br>');
            }
        }

        const sourceModeBanner = info.is_source_mode ? `
            <div class="updater-source-banner">
                <span>🌿</span>
                <span>当前以 <b>Python 源码模式</b> 运行，终端执行 <code>git pull</code> 即可同步最新代码；亦可直接下载体验右侧独立客户端。</span>
            </div>` : '';

        modal.innerHTML = `
            <div class="updater-modal-card">
                <div class="updater-modal-header">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:1.4rem;">${modalIcon}</span>
                        <div>
                            <h3 style="margin:0;font-size:1.05rem;font-weight:800;letter-spacing:0.5px;">${modalTitle}</h3>
                            <div style="font-size:0.72rem;margin-top:2px;">${modalSub}</div>
                        </div>
                    </div>
                    <button type="button" class="updater-modal-close-btn" onclick="window.closeUpdateModal()" title="关闭">✕</button>
                </div>
                <div class="updater-modal-body">
                    ${sourceModeBanner}
                    ${assetHtml}
                    <div style="margin-top:12px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                            <div style="font-size:0.8rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.8px;">✨ 官方正式发版说明 (Release Notes)</div>
                            <span style="font-size:0.72rem;color:var(--text-muted);">中英双语 · 创作者指南</span>
                        </div>
                        <div class="updater-notes-rich">
                            ${notesHtml}
                        </div>
                    </div>
                </div>
                <div class="updater-modal-footer">
                    <a href="${info.html_url || 'https://github.com/Illacme/illacme-plenipes/releases'}" target="_blank" rel="noopener noreferrer" class="updater-footer-link">🔗 前往 GitHub Releases 查看全部资产 (${info.assets_count || 10})</a>
                    <button type="button" class="updater-footer-close-btn" onclick="window.closeUpdateModal()">关闭</button>
                </div>
            </div>`;
        modal.style.display = 'flex';
    };

    /**
     * 关闭更新弹窗
     */
    window.closeUpdateModal = function () {
        const modal = document.getElementById('system-update-modal');
        if (modal) modal.style.display = 'none';
    };

    /**
     * ⚡ 一键后台静默更新：无需用户动手，自动在后台下载并在就绪后静默替换自重启
     */
    window.startSilentUpdate = async function (downloadUrl, targetVersion) {
        const actionBtn = document.getElementById('btn-silent-update-action');
        const progressBox = document.getElementById('updater-progress-wrapper');
        const statusText = document.getElementById('updater-progress-status-text');
        const percentText = document.getElementById('updater-progress-percent-text');
        const barFill = document.getElementById('updater-progress-bar-fill');

        if (actionBtn) {
            actionBtn.disabled = true;
            actionBtn.style.opacity = '0.6';
            actionBtn.innerHTML = '⏳ 正在点火后台静默更新...';
        }
        if (progressBox) progressBox.style.display = 'flex';

        try {
            const resp = await fetch('/api/system/update/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ download_url: downloadUrl, version: targetVersion })
            });
            const data = await resp.json();
            if (!data.success && data.status !== 'downloading') {
                throw new Error(data.message || '启动下载失败');
            }

            // 启动高频平滑轮询
            let pollTimer = setInterval(async () => {
                try {
                    const pResp = await fetch('/api/system/update/progress');
                    if (!pResp.ok) return;
                    const prog = await pResp.json();

                    if (barFill) barFill.style.width = `${prog.percent || 0}%`;
                    if (percentText) percentText.textContent = `${prog.percent || 0}%`;

                    if (prog.status === 'downloading') {
                        if (statusText) statusText.textContent = `正在后台流式下载 (${prog.speed_mb || 0} MB/s)...`;
                        if (actionBtn) actionBtn.innerHTML = `⏳ 下载中 ${prog.percent || 0}%`;
                    } else if (prog.status === 'ready' || prog.is_ready) {
                        clearInterval(pollTimer);
                        if (statusText) statusText.textContent = '🚀 下载完成，正在静默替换并自动重启...';
                        if (barFill) barFill.style.width = '100%';
                        if (percentText) percentText.textContent = '100%';
                        if (actionBtn) actionBtn.innerHTML = '⚡ 正在自重启...';

                        // 自动触发静默替换与自重启
                        const applyResp = await fetch('/api/system/update/apply', { method: 'POST' });
                        const applyData = await applyResp.json();
                        if (applyData.success) {
                            if (statusText) statusText.textContent = '🎉 客户端已接力重启，页面即将重新连接...';
                            setTimeout(() => {
                                let checkTimer = setInterval(async () => {
                                    try {
                                        const h = await fetch('/api/system/health');
                                        if (h.ok) {
                                            clearInterval(checkTimer);
                                            window.location.reload();
                                        }
                                    } catch (_) {}
                                }, 1500);
                            }, 2000);
                        } else {
                            throw new Error(applyData.message || '自重启应用失败');
                        }
                    } else if (prog.status === 'error') {
                        clearInterval(pollTimer);
                        throw new Error(prog.error || '下载更新包中断');
                    }
                } catch (err) {
                    clearInterval(pollTimer);
                    console.error('[AutoUpdate] 轮询异常:', err);
                    if (statusText) statusText.textContent = `❌ 更新中断: ${err.message}`;
                    if (actionBtn) {
                        actionBtn.disabled = false;
                        actionBtn.style.opacity = '1';
                        actionBtn.innerHTML = '⚡ 重试静默升级';
                    }
                }
            }, 800);

        } catch (e) {
            console.error('[AutoUpdate] 启动失败:', e);
            if (statusText) statusText.textContent = `❌ ${e.message}`;
            if (actionBtn) {
                actionBtn.disabled = false;
                actionBtn.style.opacity = '1';
                actionBtn.innerHTML = '⚡ 重试静默升级';
            }
        }
    };

})();
