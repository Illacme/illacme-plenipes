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
                window.openUpdateModal();
                if (!data.has_update && typeof window.showToast === 'function') {
                    window.showToast(`✨ 当前已是最新正式版本 (${data.current_version})`, 'success');
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
     * 运行基座渲染小部件
     */
    window.renderEngineUpdateWidget = function () {
        const info = window._latestUpdateInfo;
        const curVer = info ? info.current_version : 'v1.8.0';
        return `
            <div class="settings-card" style="background:rgba(255,255,255,0.02);border:1px solid var(--glass-border);border-radius:12px;padding:18px;margin-top:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:1.1rem;">🛰️</span>
                            <span style="font-size:0.95rem;font-weight:700;color:var(--text-main);">客户端软件版本与云端更新中枢</span>
                            <span class="version-tag tiny" style="background:rgba(0,240,255,0.12);color:var(--neon-cyan);border:1px solid rgba(0,240,255,0.3);">${curVer}</span>
                        </div>
                        <div id="engine-update-status-text" style="font-size:0.78rem;color:var(--text-muted);margin-top:6px;">已集成 GitHub Releases 自动版本同步。点击按钮可即时同步最新发版动态与原装安装包。</div>
                    </div>
                    <button type="button" id="engine-check-update-btn" class="secondary-btn" onclick="window.checkSystemUpdate(true)"
                            style="font-size:0.8rem;padding:6px 14px;border-radius:8px;cursor:pointer;background:var(--white-10);border:1px solid var(--glass-border);color:var(--text-main);display:inline-flex;align-items:center;gap:6px;transition:all 0.2s;">
                        <span>🔍 立即检查云端新版本</span>
                    </button>
                </div>
            </div>`;
    };

    // 浏览器页面完全就绪后，延迟 3 秒静默执行一次版本探测
    if (typeof window !== 'undefined' && typeof window.location !== 'undefined' && window.location.protocol) {
        const delayCheck = () => setTimeout(() => window.checkSystemUpdate(false), 3000);
        if (document.readyState === 'complete') delayCheck();
        else window.addEventListener('load', delayCheck);
    }
})();
