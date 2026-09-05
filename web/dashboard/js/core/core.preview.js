/**
 * ⚡ [V100.9] Illacme Plenipes Publish & Preview Workflow Engine (发布预览全流程交互引擎 - 调度中枢 Hub)
 * 职责：
 * 1. 两阶段交互流程编排：向导就绪 (READY) -> 点火构建 (BUILDING) -> 预览就绪 (READY)；
 * 2. 防重入保护与动态参数注入 (force, local_only)；
 * 3. 协调并桥接日志过滤、卡片渲染与完成态直达链路。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
 */

// 点击直达预览站点全局函数
window.openPreviewSite = function () {
    const port = window._actualPreviewPort || window.settingsData?.system?.serve_port || 43213;
    const baseUrl = window._actualPreviewUrl || `http://localhost:${port}/`;
    const previewUrl = baseUrl.includes('?') ? `${baseUrl}&t=${Date.now()}` : `${baseUrl}?t=${Date.now()}`;
    window.open(previewUrl, '_blank', 'noopener,noreferrer');
};

// 【阶段 1】点击右上角「⚡ 发布预览」入口：打开弹窗并展示说明向导
window.triggerPublishAndPreview = async function () {
    // 动态拉取或同步当前生效的主题名称
    let rawThemeId = 'sovereign';
    try {
        if (window.settingsData && (window.settingsData.active_theme || window.settingsData.config?.active_theme)) {
            rawThemeId = window.settingsData.active_theme || window.settingsData.config?.active_theme;
        } else {
            const cfgRes = await window.apiFetch('/api/system/config', { method: 'GET' });
            if (cfgRes) {
                rawThemeId = cfgRes.active_theme || cfgRes.config?.active_theme || 'sovereign';
                if (!window.settingsData) window.settingsData = cfgRes;
                else window.settingsData.active_theme = rawThemeId;
            }
        }
    } catch (e) {
        console.warn('获取当前装帧主题失败:', e);
    }

    const displayThemeName = window.getThemeDisplayName ? window.getThemeDisplayName(rawThemeId) : rawThemeId;

    const modal = document.getElementById('terminal-modal');
    if (!modal) return;

    modal.style.display = 'flex';
    modal.dataset.context = 'publish_preview';
    window._isPublishPreviewActive = true;

    // 1. 探测后端是否已有发布流水线正在运行
    let isPublishing = false;
    try {
        const statusRes = await window.apiFetch('/api/system/sync/status', { method: 'GET' });
        isPublishing = !!(statusRes && statusRes.is_publishing);
    } catch (e) {
        console.warn('[Publish & Preview] 探测发布状态失败:', e);
    }

    const title = document.getElementById('terminal-title');
    const toolbar = document.getElementById('terminal-toolbar');
    const out = document.getElementById('terminal-output');
    const statusEl = document.getElementById('terminal-status');
    const startBtn = document.getElementById('btn-terminal-start-preview');
    const okBtn = document.getElementById('btn-terminal-ok');
    const abortBtn = document.getElementById('btn-terminal-abort');
    const closeBtn = document.getElementById('btn-terminal-close');
    const forceBar = document.getElementById('preview-force-sync-bar');

    if (toolbar) {
        toolbar.style.display = 'flex';
        toolbar.innerHTML = window.renderPreviewStepperToolbar ? window.renderPreviewStepperToolbar() : '';
    }

    // 🛡️ 重置所有按钮状态，避免单例污染
    if (typeof window.resetTerminalModalFooter === 'function') {
        window.resetTerminalModalFooter();
    }

    if (isPublishing) {
        // ⚠️ 情况 A：已有任务正在执行，限制重复点火并接入实时流
        if (title) title.innerHTML = '⚡ 发布预览流水线执行中 <span class="version-tag tiny" style="background:rgba(0,240,255,0.15);color:var(--neon-cyan);border:1px solid rgba(0,240,255,0.4);margin-left:8px;">RUNNING</span>';
        if (statusEl) {
            statusEl.innerText = 'PREVIEW RUNNING';
            statusEl.className = 'online';
        }
        if (abortBtn) {
            abortBtn.style.display = 'inline-flex';
            abortBtn.disabled = false;
            abortBtn.innerText = '🛑 中止任务';
        }
        if (closeBtn) {
            closeBtn.style.display = 'inline-flex';
            closeBtn.innerText = '隐藏窗口 (后台继续)';
        }

        if (out && modal.dataset.lastContext !== 'publish_preview_running') {
            out.innerHTML = `<div class="term-line" style="color:#00f0ff;">[${new Date().toLocaleTimeString()}] 📡 检测到后台已有发布流水线正在运行，已自动为您接入实时进度流...</div>`;
        }
        modal.dataset.lastContext = 'publish_preview_running';

        if (window.setPreviewStepState) {
            window.setPreviewStepState(1, 'completed');
            window.setPreviewStepState(2, 'active');
        }

    } else {
        // ✨ 情况 B：空闲状态，展示 4 步说明向导，等待用户手动点火
        if (title) title.innerHTML = '⚡ 极速发布预览流水线 <span class="version-tag tiny" style="background:rgba(0,240,255,0.15);color:var(--neon-cyan);border:1px solid rgba(0,240,255,0.4);margin-left:8px;">READY</span>';
        if (statusEl) {
            statusEl.innerText = 'STANDBY';
            statusEl.className = 'online';
        }

        if (out) {
            out.innerHTML = window.renderPreviewIntroCard ? window.renderPreviewIntroCard(displayThemeName) : '';
        }
        modal.dataset.lastContext = 'publish_preview_intro';

        // 按钮状态：显示“开始发布”与“关闭”，显示常驻的强制覆盖条
        if (forceBar) forceBar.style.display = 'flex';
        if (startBtn) {
            startBtn.style.display = 'inline-flex';
            startBtn.disabled = false;
            startBtn.innerHTML = '⚡ 开始发布';
        }
        if (okBtn) {
            okBtn.style.display = 'inline-flex';
            okBtn.innerText = '关闭';
        }
    }
};

// 【阶段 2】用户点击「⚡ 开始发布」：真正启动构建流水线
window.startPublishAndPreviewExecution = async function () {
    let rawThemeId = 'sovereign';
    if (window.settingsData && (window.settingsData.active_theme || window.settingsData.config?.active_theme)) {
        rawThemeId = window.settingsData.active_theme || window.settingsData.config?.active_theme;
    }
    const displayThemeName = window.getThemeDisplayName ? window.getThemeDisplayName(rawThemeId) : rawThemeId;

    window._isPublishPreviewActive = true;

    const modal = document.getElementById('terminal-modal');
    const startBtn = document.getElementById('btn-terminal-start-preview');
    const okBtn = document.getElementById('btn-terminal-ok');
    const abortBtn = document.getElementById('btn-terminal-abort');
    const closeBtn = document.getElementById('btn-terminal-close');
    const out = document.getElementById('terminal-output');
    const title = document.getElementById('terminal-title');
    const statusEl = document.getElementById('terminal-status');

    // 1. 重置去重历史集
    if (window._previewLoggedHistory) {
        window._previewLoggedHistory.clear();
    }

    // 2. 切换按钮与状态至运行态 (仅在执行中出现中止与隐藏窗口按钮)
    if (typeof window.resetTerminalModalFooter === 'function') {
        window.resetTerminalModalFooter();
    }
    if (abortBtn) {
        abortBtn.style.display = 'inline-flex';
        abortBtn.disabled = false;
        abortBtn.innerText = '🛑 中止任务';
    }
    if (closeBtn) {
        closeBtn.style.display = 'inline-flex';
        closeBtn.innerText = '隐藏窗口 (后台继续)';
    }

    if (title) title.innerHTML = '⚡ 极速发布预览流水线 <span class="version-tag tiny" style="background:rgba(0,240,255,0.15);color:var(--neon-cyan);border:1px solid rgba(0,240,255,0.4);margin-left:8px;">PREVIEW BUILDING</span>';
    if (statusEl) {
        statusEl.innerText = 'BUILDING';
        statusEl.className = 'online';
    }

    // 3. 提取强制全量同步选项
    const forceSyncCheckbox = document.getElementById('chk-preview-force-sync');
    const isForceSync = forceSyncCheckbox ? forceSyncCheckbox.checked : false;

    // 清空向导卡片，准备输出精简清晰的流水线日志
    if (out) out.innerHTML = '';
    if (modal) modal.dataset.lastContext = 'publish_preview_executing';

    if (window.setPreviewStepState) {
        window.setPreviewStepState(1, 'active');
    }

    if (typeof window.appendTerminalLog === 'function') {
        if (isForceSync) {
            window.appendTerminalLog(`⚡ [发布预览] 正在启动强制全量重装流水线 (主题: ${displayThemeName}，全量重装)...`, '#00f0ff');
        } else {
            window.appendTerminalLog(`⚡ [发布预览] 正在启动本地极速装帧流水线 (主题: ${displayThemeName})...`, '#00f0ff');
        }
        window.appendTerminalLog('🔍 [步骤 1/4] 正在扫描原稿文库并执行资产与双链预检...', '#a29bfe');
    }

    try {
        // 4. 向后端发送 local_only 点火请求 (支持动态 force 参数)
        const res = await window.apiFetch(`/api/system/sync/trigger?local_only=true&force=${isForceSync}`, { method: 'POST' });

        if (!res || (res.status !== 'started' && res.status !== 'success')) {
            throw new Error(res ? (res.reason || res.detail || '后端拒绝点火') : '网络请求未响应');
        }

        if (typeof window.appendTerminalLog === 'function') {
            window.appendTerminalLog('✍️ [步骤 2/4] 本地 Markdown 原稿解析与智能排版中...', '#00ffaa');
        }

    } catch (err) {
        console.error('[startPublishAndPreviewExecution Error]', err);
        if (typeof window.appendTerminalLog === 'function') {
            window.appendTerminalLog(`🚨 [发布预览异常] ${err.message}`, '#ff4d4d');
        }
        if (typeof window.addAudit === 'function') {
            window.addAudit(`发布预览异常: ${err.message}`, 'error');
        }
        if (statusEl) {
            statusEl.innerText = 'ERROR';
            statusEl.className = 'offline';
        }
        if (abortBtn) abortBtn.style.display = 'none';
        if (closeBtn) closeBtn.style.display = 'none';
        if (okBtn) {
            okBtn.style.display = 'inline-flex';
            okBtn.innerText = '关闭';
        }
    }
};

// 保持历史兼容别名
window.triggerPreview = window.triggerPublishAndPreview;
