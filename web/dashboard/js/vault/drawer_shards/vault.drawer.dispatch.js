/**
 * 📡 [V68.0] Illacme Plenipes Vault - Re-dispatch & Channel Triggers Shard
 * 职责：全局出版模式自动升级、单篇/全量重调度触发、单渠道独立部署推送、全渠道一键并行同步。
 */

(function () {
    // 🛡️ [V89.8] 防呆辅助：自愈式 Toast 弹窗渲染器，防止在某些子视图下打断异步链路
    const showToast = (message, icon = 'success') => {
        if (window.Swal) {
            window.Swal.fire({
                title: message,
                icon: icon,
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
        } else if (window._showToast) {
            window._showToast(message, icon);
        } else {
            console.log(`[Toast] ${icon}: ${message}`);
        }
    };

    window.triggerReDispatch = async (scope, clearCache = false) => {
        if (!window.currentDocId) return;

        const pubMode = window.settingsData?.governance?.publishing_mode || 'basic';
        if (clearCache && pubMode !== 'global') {
            let isConfirmed = false;
            if (window.Swal) {
                const confirmSwitch = await window.Swal.fire({
                    title: '🌐 需要开启全球出版模式',
                    html: `强制重新 AI 翻译正文需要将出版模式设置为 <b style="color:var(--accent-secondary);">全球多语言分发模式 (global)</b>。<br/><span style="font-size:0.75rem;color:var(--text-dim);">是否自动将当前出版模式升级为全球模式并立即执行全量重译？</span>`,
                    icon: 'info',
                    showCancelButton: true,
                    confirmButtonText: '一键升级模式并重译',
                    cancelButtonText: '取消',
                    background: 'hsla(220, 43%, 7%, 0.98)',
                    color: 'var(--text-bright)',
                    confirmButtonColor: 'var(--accent-secondary)',
                    cancelButtonColor: 'hsla(0, 0%, 27%, 1)'
                });
                isConfirmed = confirmSwitch.isConfirmed;
            } else {
                isConfirmed = confirm("🌐 强制重新 AI 翻译正文需要将出版模式设置为全球多语言分发模式 (global)。是否自动升级？");
            }

            if (!isConfirmed) return;

            // 自动升级模式
            if (window.settingsData && window.settingsData.governance) {
                window.settingsData.governance.publishing_mode = 'global';
            }
            const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url, init) => (await fetch(url, init)).json());
            await fetchFunc('/api/gov/save-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: 'modes', config: { publishing_mode: 'global' } })
            });
            window._showToast?.('✨ 已成功自动升级为全球多语言出版模式！', 'success');
        }

        if (typeof addAudit === 'function') {
            addAudit(`🚀 [Dispatch] 手动触发重调度请求: ${scope} (清除缓存: ${clearCache})`, "info");
        }

        const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url, init) => (await fetch(url, init)).json());
        const res = await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(window.currentDocId)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ locales: scope === 'all' ? [] : [scope], force: true, clear_cache: clearCache, skip_syndication: clearCache })
        });

        if (res && res.success) {
            // 🚀 [V75.6] 即刻将所有目标语种卡片（排除主权透传的"无需翻译"）设为 redispatching 状态
            document.querySelectorAll('.matrix-item.target-lang').forEach(item => {
                const cacheMeta = item.innerHTML;
                if (!cacheMeta.includes('无需翻译')) {
                    item.classList.add('redispatching');
                }
            });

            console.info(`✅ [Dispatch] 重调度指令已由管线受理: ${window.currentDocId}`);
            if (window.Swal) {
                Swal.fire({
                    title: '重调度已受理',
                    text: res.message,
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });
            }

            if (typeof window.safeStartDrawerTimer === 'function') window.safeStartDrawerTimer(window.currentDocId);

            setTimeout(() => {
                if (typeof window.refreshVaultDrawerStatus === 'function') window.refreshVaultDrawerStatus(window.currentDocId);
            }, 1000);
        } else {
            const errorMsg = res ? (res.message || res.reason || "未知异常") : "网络连接或系统异常";
            if (typeof addAudit === 'function') addAudit(`❌ 重调度失败: ${errorMsg}`, "error");
            if (window.Swal) {
                Swal.fire({
                    title: '重调度失败',
                    text: errorMsg,
                    icon: 'error'
                });
            }
        }
    };

    window.triggerChannelDispatch = async (relPath, channelId) => {
        if (!relPath || !channelId) return;

        // 给触发的按钮临时加上加载中样式
        const btn = typeof event !== 'undefined' ? event?.target : null;
        if (btn) {
            btn.style.opacity = '0.5';
            btn.innerText = "🔄 同步中...";
        }

        showToast(`🔄 正在向渠道 ${channelId} 进行单篇物理同步部署...`, "info");

        const fetchFunc = typeof apiFetch === 'function' ? apiFetch : (async (url, init) => (await fetch(url, init)).json());
        const res = await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_channel: channelId })
        });

        if (res && res.success) {
            showToast(`✅ 已向渠道 ${channelId} 完成物理同步部署！`, "success");

            // 自动拉起重调度追踪定时器，监控状态变更
            if (typeof window.safeStartDrawerTimer === 'function') window.safeStartDrawerTimer(relPath);

            setTimeout(() => {
                if (typeof window.refreshVaultDrawerStatus === 'function') window.refreshVaultDrawerStatus(relPath);
            }, 1000);
        } else {
            const errorMsg = res ? (res.message || res.reason || "未知异常") : "网络连接或系统异常";
            showToast(`❌ 渠道同步失败: ${errorMsg}`, "error");
            if (btn) {
                btn.style.opacity = '1';
                btn.innerText = "🔄 发布";
            }
        }
    };

    // 🚀 [V89.9] 全渠道一键并行同步事件处理器
    window.triggerSyncAllChannels = async () => {
        if (!window.currentDocId) return;

        // 找出所有同步按钮并并行触发
        const syncBtns = document.querySelectorAll('.sync-channel-btn');
        if (syncBtns.length === 0) {
            showToast("⚠️ 当前未配置或未启用任何全站托管平台。", "warning");
            return;
        }

        showToast(`🚀 正在发起全渠道 (${syncBtns.length} 个) 并行同步中...`, "info");

        const promises = Array.from(syncBtns).map(btn => {
            const onclickAttr = btn.getAttribute('onclick') || "";
            const match = onclickAttr.match(/window\.triggerChannelDispatch\('(.*?)',\s*'(.*?)'\)/);
            if (match && match[2]) {
                const channelId = match[2];
                return window.triggerChannelDispatch(window.currentDocId, channelId);
            }
            return Promise.resolve();
        });

        await Promise.all(promises);
        showToast("✅ 全渠道同步请求全部触发成功！正在后台并行推送...", "success");
    };
})();
