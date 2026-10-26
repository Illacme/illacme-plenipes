/**
 * 🛰️ Illacme Plenipes UI - System Update Modal & Silent Download Shard
 * 职责：负责更新向导专属毛玻璃弹窗渲染、下载进度动态轮询与平滑接力热重启。
 * 🛡️ [SOP-01 & SOP-03 视觉主权规范]：单文件严格 ≤ 300 行。
 */

(function () {
    'use strict';

    /**
     * 🚀 渲染并弹出高档毛玻璃更新向导弹窗
     */
    window.openUpdateModal = function () {
        const info = window._latestUpdateInfo;
        if (!info) {
            if (typeof window.checkSystemUpdate === 'function') {
                window.checkSystemUpdate(true);
            }
            return;
        }

        let modal = document.getElementById('system-update-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'system-update-modal';
            modal.className = 'glass-modal-backdrop';
            modal.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(4,8,14,0.75);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);display:flex;align-items:center;justify-content:center;padding:20px;transition:opacity 0.3s ease;';
            document.body.appendChild(modal);
        }

        const asset = info.recommended_asset;
        const assetHtml = asset ? `
            <div id="updater-card-box" style="background:rgba(0,240,255,0.08);border:1px solid rgba(0,240,255,0.3);border-radius:12px;padding:14px 18px;margin:14px 0;display:flex;flex-direction:column;gap:10px;">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
                    <div style="display:flex;flex-direction:column;gap:4px;overflow:hidden;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:0.72rem;padding:2px 8px;border-radius:6px;background:rgba(0,240,255,0.2);color:var(--neon-cyan);font-weight:700;">专属推荐安装包</span>
                            <span style="font-size:0.85rem;font-weight:700;color:var(--text-main);font-family:var(--font-mono);text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">${asset.name}</span>
                        </div>
                        <div style="font-size:0.75rem;color:var(--text-muted);">格式: ${asset.format_desc} · 体积: ${asset.size_mb} MB</div>
                    </div>
                    <button type="button" id="btn-silent-update-action" onclick="window.startSilentUpdate('${asset.download_url}', '${info.latest_version}')"
                       style="background:linear-gradient(135deg, var(--neon-cyan), #00a8ff);color:#04080e;font-weight:800;font-size:0.82rem;padding:8px 18px;border-radius:8px;border:none;cursor:pointer;white-space:nowrap;box-shadow:0 4px 16px rgba(0,240,255,0.3);transition:all 0.2s;">
                       ⚡ 一键静默升级
                    </button>
                </div>
                <div id="updater-progress-wrapper" style="display:none;flex-direction:column;gap:6px;padding-top:8px;border-top:1px dashed rgba(0,240,255,0.2);">
                    <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-muted);">
                        <span id="updater-progress-status-text">正在后台建立安全下载通道...</span>
                        <span id="updater-progress-percent-text" style="color:var(--neon-cyan);font-weight:700;font-family:var(--font-mono);">0%</span>
                    </div>
                    <div style="height:6px;background:rgba(255,255,255,0.08);border-radius:4px;overflow:hidden;width:100%;">
                        <div id="updater-progress-bar-fill" style="height:100%;width:0%;background:linear-gradient(90deg, var(--neon-cyan), #00ff88);transition:width 0.3s ease;"></div>
                    </div>
                </div>
            </div>` : `<div style="background:var(--white-05);border:1px solid var(--glass-border);border-radius:12px;padding:14px;margin:16px 0;text-align:center;color:var(--text-muted);font-size:0.82rem;">暂未检测到当前平台的专属编译产物，请在 GitHub 发布页面下载通用版本。</div>`;

        const notes = info.release_notes ? info.release_notes
            .replace(/###\s*(.*)/g, '<h4 style="margin:10px 0 6px;color:var(--neon-cyan);font-size:0.88rem;">$1</h4>')
            .replace(/\*\s*(.*)/g, '<li style="margin-left:16px;margin-bottom:4px;color:var(--text-main);font-size:0.8rem;line-height:1.5;">$1</li>')
            .replace(/\n\n/g, '<br>') : '无详细更新说明。';

        modal.innerHTML = `
            <div style="background:var(--glass-bg,#0b1219);border:1px solid var(--glass-border,rgba(255,255,255,0.12));border-radius:16px;max-width:620px;width:100%;max-height:85vh;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,0.6);animation:modalFadeIn 0.25s cubic-bezier(0.16,1,0.3,1);">
                <div style="padding:18px 24px;border-bottom:1px solid var(--glass-border);display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:1.3rem;">🚀</span>
                        <div>
                            <h3 style="margin:0;font-size:1.05rem;font-weight:800;color:var(--text-main);letter-spacing:0.5px;">发现新版本 ${info.latest_version}</h3>
                            <div style="font-size:0.72rem;color:var(--text-muted);margin-top:2px;">当前运行版本: ${info.current_version} · 发布于: ${info.published_at ? info.published_at.slice(0, 10) : '近期'}</div>
                        </div>
                    </div>
                    <button type="button" onclick="window.closeUpdateModal()" style="background:none;border:none;color:var(--text-muted);font-size:1.2rem;cursor:pointer;padding:4px;border-radius:6px;transition:color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='var(--text-muted)'">✕</button>
                </div>
                <div style="padding:20px 24px;overflow-y:auto;flex:1;">
                    ${assetHtml}
                    <div style="margin-top:14px;">
                        <div style="font-size:0.8rem;font-weight:700;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.8px;">✨ 本次版本更新内容</div>
                        <div style="background:rgba(0,0,0,0.25);border:1px solid var(--glass-border);border-radius:10px;padding:14px 16px;max-height:240px;overflow-y:auto;font-family:var(--font-sans);">${notes}</div>
                    </div>
                </div>
                <div style="padding:14px 24px;border-top:1px solid var(--glass-border);background:var(--white-05);display:flex;align-items:center;justify-content:space-between;">
                    <a href="${info.html_url}" target="_blank" rel="noopener noreferrer" style="font-size:0.78rem;color:var(--text-muted);text-decoration:underline;cursor:pointer;">🔗 前往 GitHub Releases 查看全部资产 (${info.assets_count || 0})</a>
                    <button type="button" onclick="window.closeUpdateModal()" style="background:var(--white-10);border:1px solid var(--glass-border);color:var(--text-main);font-size:0.82rem;padding:6px 14px;border-radius:8px;cursor:pointer;">稍后再说</button>
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
