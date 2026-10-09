/**
 * 🛰️ Illacme Plenipes UI - System Auto-Update & Cloud Release Hub
 * 职责：负责静默感知云端 GitHub Releases 最新发版、底栏/边栏微光徽章唤起、专属毛玻璃更新向导弹窗渲染。
 * 🛡️ [SOP-01 & SOP-03 视觉主权规范]：单文件严格 ≤ 300 行。
 */

(function () {
    window._latestUpdateInfo = null;
    window._isCheckingUpdate = false;

    /**
     * 🛰️ 请求后端 API 检查最新版本
     */
    window.checkSystemUpdate = async function (interactive = false) {
        if (window._isCheckingUpdate) return;
        window._isCheckingUpdate = true;

        const updateBtn = document.getElementById('engine-check-update-btn');
        if (updateBtn) {
            updateBtn.disabled = true;
            updateBtn.innerHTML = '<span>⏳ 正在查询 GitHub Releases...</span>';
        }

        try {
            const resp = await fetch(`/api/system/check_update?force=${interactive ? 'true' : 'false'}`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            window._latestUpdateInfo = data;

            // 1. 更新全局版本号显示胶囊
            const verPill = document.getElementById('footer-version-display');
            if (verPill && data.current_version) {
                verPill.textContent = data.current_version;
            }

            // 2. 有更新时点亮呼吸徽章
            const badge = document.getElementById('footer-update-badge');
            if (badge) {
                if (data.has_update) {
                    badge.style.display = 'inline-flex';
                    badge.innerHTML = `✨ 发现新版 ${data.latest_version}`;
                    badge.setAttribute('title', `发现全新版本 ${data.latest_version}，点击查看更新详情`);
                } else {
                    badge.style.display = 'none';
                }
            }

            // 3. 运行基座小部件状态更新
            const statusLabel = document.getElementById('engine-update-status-text');
            if (statusLabel) {
                if (data.has_update) {
                    statusLabel.innerHTML = `<span style="color: var(--accent-primary); font-weight: 700;">✨ 发现新版 ${data.latest_version}</span>（当前 ${data.current_version}）`;
                } else {
                    statusLabel.innerHTML = `<span style="color: var(--neon-cyan); font-weight: 700;">🟢 已是最新版本</span>（${data.current_version}）`;
                }
            }

            // 4. 交互式点击响应
            if (interactive) {
                if (data.has_update) {
                    window.openUpdateModal();
                } else if (typeof window.showToast === 'function') {
                    window.showToast(`✨ 当前已是最新正式版本 (${data.current_version})`, 'success');
                } else {
                    alert(`✨ 当前已是最新版本 (${data.current_version})`);
                }
            }

        } catch (e) {
            console.warn('[AutoUpdate] 检查云端更新失败:', e);
            if (interactive) {
                if (typeof window.showToast === 'function') {
                    window.showToast('⚠️ 检查更新异常，可能处于离线或网络受限环境', 'warning');
                } else {
                    alert('⚠️ 检查更新异常，可能处于离线或网络受限环境');
                }
            }
        } finally {
            window._isCheckingUpdate = false;
            if (updateBtn) {
                updateBtn.disabled = false;
                updateBtn.innerHTML = '<span>🔍 立即检查云端新版本</span>';
            }
        }
    };

    /**
     * 🚀 渲染并弹出高档毛玻璃更新向导弹窗
     */
    window.openUpdateModal = function () {
        const info = window._latestUpdateInfo;
        if (!info) {
            window.checkSystemUpdate(true);
            return;
        }

        let modal = document.getElementById('system-update-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'system-update-modal';
            modal.className = 'glass-modal-backdrop';
            modal.style.cssText = `
                position: fixed; inset: 0; z-index: 10000;
                background: rgba(4, 8, 14, 0.75);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                display: flex; align-items: center; justify-content: center;
                padding: 20px; transition: opacity 0.3s ease;
            `;
            document.body.appendChild(modal);
        }

        const asset = info.recommended_asset;
        const assetHtml = asset ? `
            <div style="background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 12px; padding: 14px 18px; margin: 16px 0; display: flex; align-items: center; justify-content: space-between; gap: 12px;">
                <div style="display: flex; flex-direction: column; gap: 4px; overflow: hidden;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 0.72rem; padding: 2px 8px; border-radius: 6px; background: rgba(0, 240, 255, 0.2); color: var(--neon-cyan); font-weight: 700;">当前系统专属推荐</span>
                        <span style="font-size: 0.85rem; font-weight: 700; color: var(--text-main); font-family: var(--font-mono); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${asset.name}</span>
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">格式: ${asset.format_desc} · 体积: ${asset.size_mb} MB</div>
                </div>
                <a href="${asset.download_url}" target="_blank" rel="noopener noreferrer"
                   style="background: linear-gradient(135deg, var(--neon-cyan), #00a8ff); color: #04080e; font-weight: 800; font-size: 0.82rem; padding: 8px 18px; border-radius: 8px; text-decoration: none; white-space: nowrap; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 16px rgba(0, 240, 255, 0.3); transition: transform 0.2s;"
                   onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform='translateY(0)'">
                   ⚡ 立即下载
                </a>
            </div>
        ` : `
            <div style="background: var(--white-05); border: 1px solid var(--glass-border); border-radius: 12px; padding: 14px; margin: 16px 0; text-align: center; color: var(--text-muted); font-size: 0.82rem;">
                暂未检测到当前平台的专属编译产物，请在 GitHub 发布页面下载通用版本。
            </div>
        `;

        // 处理 Markdown 提交列表展示
        const notes = info.release_notes ? info.release_notes
            .replace(/###\s*(.*)/g, '<h4 style="margin: 10px 0 6px; color: var(--neon-cyan); font-size: 0.88rem;">$1</h4>')
            .replace(/\*\s*(.*)/g, '<li style="margin-left: 16px; margin-bottom: 4px; color: var(--text-main); font-size: 0.8rem; line-height: 1.5;">$1</li>')
            .replace(/\n\n/g, '<br>') : '无详细更新说明。';

        modal.innerHTML = `
            <div style="background: var(--glass-bg, #0b1219); border: 1px solid var(--glass-border, rgba(255,255,255,0.12)); border-radius: 16px; max-width: 620px; width: 100%; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 24px 60px rgba(0,0,0,0.6); animation: modalFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);">
                <div style="padding: 18px 24px; border-bottom: 1px solid var(--glass-border); display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.3rem;">🚀</span>
                        <div>
                            <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">发现新版本 ${info.latest_version}</h3>
                            <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">当前运行版本: ${info.current_version} · 发布于: ${info.published_at ? info.published_at.slice(0, 10) : '近期'}</div>
                        </div>
                    </div>
                    <button type="button" onclick="window.closeUpdateModal()" style="background: none; border: none; color: var(--text-muted); font-size: 1.2rem; cursor: pointer; padding: 4px; border-radius: 6px; transition: color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='var(--text-muted)'">✕</button>
                </div>

                <div style="padding: 20px 24px; overflow-y: auto; flex: 1;">
                    ${assetHtml}

                    <div style="margin-top: 14px;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.8px;">✨ 本次版本更新内容</div>
                        <div style="background: rgba(0,0,0,0.25); border: 1px solid var(--glass-border); border-radius: 10px; padding: 14px 16px; max-height: 260px; overflow-y: auto; font-family: var(--font-sans);">
                            ${notes}
                        </div>
                    </div>
                </div>

                <div style="padding: 14px 24px; border-top: 1px solid var(--glass-border); background: var(--white-05); display: flex; align-items: center; justify-content: space-between;">
                    <a href="${info.html_url}" target="_blank" rel="noopener noreferrer" style="font-size: 0.78rem; color: var(--text-muted); text-decoration: underline; cursor: pointer;">
                        🔗 前往 GitHub Releases 网页查看全部资产 (${info.assets_count || 0})
                    </a>
                    <div style="display: flex; gap: 10px;">
                        <button type="button" onclick="window.closeUpdateModal()" style="background: var(--white-10); border: 1px solid var(--glass-border); color: var(--text-main); font-size: 0.82rem; padding: 6px 14px; border-radius: 8px; cursor: pointer;">
                            稍后再说
                        </button>
                    </div>
                </div>
            </div>
        `;
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
     * 运行基座渲染小部件
     */
    window.renderEngineUpdateWidget = function () {
        const info = window._latestUpdateInfo;
        const curVer = info ? info.current_version : 'v1.5.0';
        return `
            <div class="settings-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 12px; padding: 18px; margin-top: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.1rem;">🛰️</span>
                            <span style="font-size: 0.95rem; font-weight: 700; color: var(--text-main);">客户端软件版本与云端更新中枢</span>
                            <span class="version-tag tiny" style="background: rgba(0,240,255,0.12); color: var(--neon-cyan); border: 1px solid rgba(0,240,255,0.3);">${curVer}</span>
                        </div>
                        <div id="engine-update-status-text" style="font-size: 0.78rem; color: var(--text-muted); margin-top: 6px;">
                            已集成 GitHub Releases 自动版本同步。点击按钮可即时同步最新发版动态与原装安装包。
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <button type="button" id="engine-check-update-btn" class="secondary-btn" onclick="window.checkSystemUpdate(true)"
                                style="font-size: 0.8rem; padding: 6px 14px; border-radius: 8px; cursor: pointer; background: var(--white-10); border: 1px solid var(--glass-border); color: var(--text-main); display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;">
                            <span>🔍 立即检查云端新版本</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    };

    // 浏览器页面完全就绪后，延迟 3 秒静默执行一次版本探测
    if (typeof window !== 'undefined' && typeof window.location !== 'undefined' && window.location.protocol) {
        const delayCheck = () => setTimeout(() => window.checkSystemUpdate(false), 3000);
        if (document.readyState === 'complete') {
            delayCheck();
        } else {
            window.addEventListener('load', delayCheck);
        }
    }
})();
