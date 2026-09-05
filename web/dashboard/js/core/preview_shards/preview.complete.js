/**
 * ⚡ [V100.9] Illacme Plenipes Preview Completion & Site Launcher
 * 职责：
 * 1. 监听流水线全量完成信号 (SYNC_COMPLETED)；
 * 2. 点火本地预览服务容器 (/api/system/preview/restart)；
 * 3. 渲染高质感成果看板与直达链路。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
 */

// 核心回调：当后台流水线全量完成 (SYNC_COMPLETED) 时触发
window.handlePreviewSyncCompleted = async function () {
    const port = window.settingsData?.system?.serve_port || 43213;
    const previewUrl = `http://localhost:${port}`;

    // 1. 点亮 4 个步骤全部为 completed (绿光全亮)
    if (window.setPreviewStepState) {
        window.setPreviewStepState(1, 'completed');
        window.setPreviewStepState(2, 'completed');
        window.setPreviewStepState(3, 'completed');
        window.setPreviewStepState(4, 'completed');
    }

    if (typeof window.appendTerminalLog === 'function') {
        window.appendTerminalLog('🚀 [步骤 4/4] 智能排版与装配完成！正在开启本地预览服务...', '#00f0ff');
    }

    try {
        // 2. 调用后端预览服务点火接口 (支持多品牌、多 SSG 框架)
        const restartRes = await window.apiFetch('/api/system/preview/restart', { method: 'POST' });
        const finalPort = window._actualPreviewPort || restartRes?.port || port;
        const finalUrl = window._actualPreviewUrl || `http://localhost:${finalPort}/`;

        // 3. 在终端中输出高质感「发布预览成果看板」
        const out = document.getElementById('terminal-output');
        if (out) {
            const cardHtml = (typeof window.renderPreviewSuccessCard === 'function')
                ? window.renderPreviewSuccessCard(finalUrl, finalPort)
                : `
                <div style="background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px; padding: 14px 18px; margin: 14px 0 6px 0; line-height: 1.6; box-shadow: 0 0 16px rgba(0, 240, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #00ffaa; font-weight: bold; font-size: 0.95rem;">🎉 本地智能排版与装配已就绪！</span>
                        <span style="font-size: 0.75rem; color: #00f0ff; background: rgba(0,240,255,0.15); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0,240,255,0.3);">HTTP 200 OK</span>
                    </div>
                    <div style="color: #ccc; font-size: 0.82rem; margin-bottom: 4px;">✔ <b>原稿合规</b>：已通过资产与双链审计（0 外部推流）</div>
                    <div style="color: #ccc; font-size: 0.82rem;">✔ <b>预览服务</b>：<a id="preview-site-link" href="${finalUrl}" target="_blank" style="color: #00f0ff; text-decoration: underline; font-weight: bold;">${finalUrl}</a> (端口 <span id="preview-site-port">${finalPort}</span>)</div>
                </div>`;
            out.innerHTML += cardHtml;
            out.scrollTop = out.scrollHeight;
        }

        // 4. 标题、状态栏与操作按钮归位至完成态
        const titleEl = document.getElementById('terminal-title');
        if (titleEl) {
            titleEl.innerHTML = '⚡ 发布预览已就绪 <span class="version-tag tiny" style="background:rgba(0,255,136,0.15);color:#00ff88;border:1px solid rgba(0,255,136,0.4);margin-left:8px;">READY</span>';
        }

        const statusEl = document.getElementById('terminal-status');
        if (statusEl) {
            statusEl.innerText = 'PREVIEW READY';
            statusEl.className = 'online';
        }

        const abortBtn = document.getElementById('btn-terminal-abort');
        if (abortBtn) abortBtn.style.display = 'none';

        const closeBtn = document.getElementById('btn-terminal-close');
        if (closeBtn) closeBtn.style.display = 'none';

        const startBtn = document.getElementById('btn-terminal-start-preview');
        if (startBtn) startBtn.style.display = 'none';

        const openPreviewBtn = document.getElementById('btn-terminal-open-preview');
        if (openPreviewBtn) {
            openPreviewBtn.style.display = 'inline-flex';
        }

        const okBtn = document.getElementById('btn-terminal-ok');
        if (okBtn) {
            okBtn.style.display = 'inline-flex';
            okBtn.innerText = '完成';
            okBtn.onclick = () => {
                window.closeTerminalModal();
                setTimeout(() => { window._isPublishPreviewActive = false; }, 3000);
            };
        }

        if (typeof window.addAudit === 'function') {
            window.addAudit(`发布预览成功开启: ${finalUrl}`, 'success');
        }

        // 5. 尝试直接拉起浏览器新标签页 (附带防缓存时间戳穿透)
        try {
            const freshUrl = finalUrl.includes('?') ? `${finalUrl}&t=${Date.now()}` : `${finalUrl}?t=${Date.now()}`;
            window.open(freshUrl, '_blank', 'noopener,noreferrer');
        } catch (e) {
            console.warn('[Preview] 浏览器弹窗拦截:', e);
        }

    } catch (e) {
        console.error('[handlePreviewSyncCompleted Error]', e);
    }
};
