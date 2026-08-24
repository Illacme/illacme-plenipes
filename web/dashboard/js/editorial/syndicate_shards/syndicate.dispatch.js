/**
 * 🛰️ [V107.0] Illacme Plenipes Article Syndication - Dispatch Pipeline & Results Telemetry Shard
 * 职责：社媒广播管线推流调度、多周期平滑长轮询、广播物理终态凭证回填与状态卡片渲染。
 */

(function () {
    window.dispatchArticleSyndication = async function (relPath) {
        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = langRadio ? langRadio.value : 'zh';

        const platformCheckboxes = document.querySelectorAll('.syndicate-platform-checkbox:checked');
        const selectedPlatforms = Array.from(platformCheckboxes).map(cb => cb.value);

        if (selectedPlatforms.length === 0) {
            if (typeof window.showToast === 'function') {
                window.showToast('⚠️ 请至少勾选 1 个已就绪的社媒分发渠道', 'warning');
            }
            return;
        }

        const btn = document.getElementById('btn-start-article-syndicate');
        const progressPanel = document.getElementById('syndicate-progress-panel');
        const progressTitle = document.getElementById('syndicate-progress-title');
        const progressPercent = document.getElementById('syndicate-progress-percent');
        const progressBar = document.getElementById('syndicate-progress-bar');
        const progressDesc = document.getElementById('syndicate-progress-desc');

        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-gear">⚙️</span> 分发管线运行中...';
        }

        if (progressPanel) {
            progressPanel.style.display = 'flex';
            progressTitle.innerText = `⚙️ 正在启动 [${selectedLang.toUpperCase()}] 分发管线...`;
            progressPercent.innerText = '15%';
            progressBar.style.width = '15%';
            progressDesc.innerText = '正在调起后端智能编译与分发中心...';
        }

        const fetchFunc = window.apiFetch || (async (url, init) => {
            const r = await fetch(url, init);
            return r.json();
        });

        let currentProgress = 20;

        if (window.syndicateProgressTimer) clearInterval(window.syndicateProgressTimer);
        window.syndicateProgressTimer = setInterval(async () => {
            try {
                const statusData = await fetchFunc(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}`);
                if (statusData && statusData.telemetry && statusData.telemetry.pipeline) {
                    const pipe = statusData.telemetry.pipeline;
                    if (pipe.status === 'RUNNING') {
                        currentProgress = Math.min(90, currentProgress + 10);
                        if (progressPercent) progressPercent.innerText = `${currentProgress}%`;
                        if (progressBar) progressBar.style.width = `${currentProgress}%`;
                        if (progressDesc) progressDesc.innerText = `⚙️ [底层实时日志] ${pipe.stage || '正在处理 AST 结构与外部接口...'}`;
                    }
                }
            } catch (_) {}
        }, 1200);

        const oldPanel = document.getElementById('syndicate-results-panel');
        if (oldPanel) oldPanel.remove();

        for (let i = 0; i < selectedPlatforms.length; i++) {
            const channelId = selectedPlatforms[i];
            if (progressDesc) progressDesc.innerText = `📡 [${i + 1}/${selectedPlatforms.length}] 正在向 [${channelId.toUpperCase()}] 进行广播推流调度...`;

            try {
                await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        target_slot: selectedLang,
                        target_channel: channelId,
                        skip_syndication: false,
                        clear_cache: false
                    })
                });
            } catch (e) {
                console.error(`[Syndication Network Error] ${channelId}:`, e);
            }
        }

        if (window.syndicateProgressTimer) {
            clearInterval(window.syndicateProgressTimer);
            window.syndicateProgressTimer = null;
        }

        // 🚀 [V107.0] 物理终态凭证回填：拉取后端最新传感数据并动态渲染渠道直达卡片 (带多周期平滑长轮询与物权对正)
        let cardSuccessCount = 0;
        let cardFailCount = 0;

        const renderResultsPanel = async (retryCount = 0) => {
            try {
                const timestamp = Date.now();
                const finalStatus = await fetchFunc(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}&_t=${timestamp}`);
                const syncMatrix = (finalStatus && finalStatus.sync_matrix) ? finalStatus.sync_matrix : [];

                // 🚀 实时同步拉取物权账本（精准按 selectedLang 语种物理隔离并防 HTTP 缓存）
                try {
                    const recordsData = await fetchFunc(`/api/syndication/records/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}&_t=${timestamp}`);
                    if (recordsData && recordsData.records) {
                        window.currentSyndicationRecords = recordsData.records;
                    }
                } catch (re) {
                    console.warn("[Syndicate Drawer] Refresh records failed:", re);
                }

                let allCompleted = true;
                cardSuccessCount = 0;
                cardFailCount = 0;

                const platformMetadata = window.platformMetadata || {};

                let resultsHtml = `
                    <div id="syndicate-results-panel" style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px; border: 1px solid var(--accent-secondary, #00f2fe); background: rgba(0, 242, 255, 0.04); padding: 12px; border-radius: 10px;">
                        <div style="font-size: 0.85rem; font-weight: 700; color: var(--accent-secondary, #00f2fe); display: flex; align-items: center; justify-content: space-between;">
                            <span>📡 广播物理凭证终态分布</span>
                            <span style="font-size: 0.68rem; color: var(--text-dim);">${new Date().toTimeString().split(' ')[0]}</span>
                        </div>
                `;

                selectedPlatforms.forEach(chanId => {
                    const chanMeta = platformMetadata[chanId] || { name: chanId.toUpperCase(), icon: '📡' };
                    const cleanChanId = chanId.toLowerCase().replace(/[_-\s]/g, '');
                    const statusItem = syncMatrix.find(m => (m.channel_id || '').toLowerCase().replace(/[_-\s]/g, '') === cleanChanId) || {};
                    
                    // 优先从当前选中语种的物权账本中获取真实 remote_url
                    const langRecord = (window.currentSyndicationRecords || []).find(r => 
                        (r.target_id || '').toLowerCase().replace(/[_-\s]/g, '') === cleanChanId &&
                        (r.lang_code || '').toLowerCase() === selectedLang.toLowerCase()
                    );
                    
                    const liveLink = (langRecord && langRecord.remote_url) 
                        ? langRecord.remote_url 
                        : (statusItem.artifact_url && statusItem.artifact_url !== '#' ? statusItem.artifact_url : null);
                    
                    const statusLower = (statusItem.status || '').toLowerCase();
                    const isFailed = statusLower === 'failed' || statusLower === 'error' || !!statusItem.reason;
                    const isSyncing = !isFailed && (statusLower === 'syncing' || statusLower === 'running');
                    const isDraft = !isFailed && statusLower === 'draft';
                    const isSkipped = !isFailed && !isSyncing && (statusLower === 'skipped' || statusLower === 'same_content');
                    const isSuccess = !isFailed && !isSyncing && !isDraft && (isSkipped || statusLower === 'published' || statusLower === 'success' || statusLower === 'synced' || statusLower === 'done' || (!!liveLink && !isFailed));
                    const errorMsg = statusItem.reason || '网络传输中断或未配置凭据';

                    // 🚀 智能长轮询收敛：若仍在推流中，或处于刚提交且未达终态的过渡期 (retryCount < 8)，持续轮询
                    if (isSyncing || (!isFailed && !isSuccess && !isDraft && !isSkipped && retryCount < 8)) {
                        allCompleted = false;
                    } else if (isDraft) {
                        cardSuccessCount++;
                    } else if (isSuccess) {
                        cardSuccessCount++;
                    } else if (isFailed) {
                        cardFailCount++;
                    }

                    // 🎨 五态渲染：推流中 (青蓝) / 已对正跳过 (青) / 草稿 (琥珀) / 成功 (绿) / 失败 (红)
                    const cardBg = isSyncing ? 'rgba(0, 242, 255, 0.05)' : (isSkipped ? 'rgba(0, 242, 255, 0.08)' : (isDraft ? 'rgba(255, 193, 7, 0.08)' : (isSuccess ? 'rgba(0, 255, 136, 0.08)' : (isFailed ? 'rgba(255, 77, 77, 0.08)' : 'rgba(255, 255, 255, 0.02)'))));
                    const cardBorder = isSyncing ? 'rgba(0, 242, 255, 0.25)' : (isSkipped ? 'rgba(0, 242, 255, 0.35)' : (isDraft ? 'rgba(255, 193, 7, 0.35)' : (isSuccess ? 'rgba(0, 255, 136, 0.35)' : (isFailed ? 'rgba(255, 77, 77, 0.35)' : 'rgba(255, 255, 255, 0.1)'))));
                    const statusColor = isSyncing ? '#00f2fe' : (isSkipped ? '#00f2fe' : (isDraft ? '#ffc107' : (isSuccess ? '#00ff88' : (isFailed ? '#ff4d4d' : '#888'))));
                    const statusText = isSyncing
                        ? '⚙️ 正在向平台进行广播推流与物权绑定...'
                        : (isSkipped
                            ? '✨ 内容一致自动对正 (已跳过重复网络推流)'
                            : (isDraft
                                ? '🟡 已推送，但平台强制降级为草稿（需手动发布）'
                                : (isSuccess ? '🟢 已成功广播分发' : (isFailed ? `❌ ${errorMsg}` : '⚪ 尚未分发至该渠道'))));

                    let actionHtml = '';
                    if (isSyncing) {
                        actionHtml = `<span style="font-size: 0.68rem; color: #00f2fe; background: rgba(0, 242, 255, 0.12); border: 1px solid rgba(0, 242, 255, 0.25); padding: 4px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px;">⚙️ 推流中...</span>`;
                    } else if (isSkipped && liveLink) {
                        actionHtml = `<a href="${liveLink}" target="_blank" style="padding: 6px 12px; font-size: 0.72rem; font-weight: 700; background: rgba(0, 242, 255, 0.2); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.4); border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; box-shadow: 0 0 10px rgba(0, 242, 255, 0.2);">✨ 保持对正 ↗</a>`;
                    } else if (isDraft && liveLink) {
                        actionHtml = `<a href="${liveLink}" target="_blank" style="padding: 6px 12px; font-size: 0.72rem; font-weight: 700; background: #ffc107; color: #000; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; box-shadow: 0 0 10px rgba(255, 193, 7, 0.4);">📝 前往手动发布 ↗</a>`;
                    } else if (liveLink) {
                        actionHtml = `<a href="${liveLink}" target="_blank" style="padding: 6px 12px; font-size: 0.72rem; font-weight: 700; background: var(--accent-secondary, #00f2fe); color: #000; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; box-shadow: 0 0 10px rgba(0, 242, 255, 0.4);">🌐 线上文章 ↗</a>`;
                    } else if (isSkipped) {
                        actionHtml = `<span style="font-size: 0.68rem; color: #00f2fe; background: rgba(0, 242, 255, 0.12); border: 1px solid rgba(0, 242, 255, 0.25); padding: 4px 8px; border-radius: 4px;">✨ 自动跳过</span>`;
                    } else if (isSuccess) {
                        actionHtml = `<span style="font-size: 0.68rem; color: #00ff88; background: rgba(0, 255, 136, 0.12); border: 1px solid rgba(0, 255, 136, 0.25); padding: 4px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px;">⚙️ 已发送推流</span>`;
                    } else if (isFailed) {
                        actionHtml = `<button type="button" onclick="window.retrySinglePlatform('${relPath.replace(/'/g, "\\'")}', '${chanId}')" style="padding: 4px 10px; font-size: 0.72rem; font-weight: 600; background: rgba(0, 242, 255, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">🔄 重试</button>`;
                    } else {
                        actionHtml = `<span style="font-size: 0.68rem; color: #888; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 4px 8px; border-radius: 4px; white-space: nowrap;">⚪ 待分发</span>`;
                    }

                    resultsHtml += `
                        <div style="padding: 10px 12px; border-radius: 8px; background: ${cardBg}; border: 1px solid ${cardBorder}; display: flex; flex-direction: column; gap: 6px;">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                                <div style="display: flex; align-items: center; gap: 8px; min-width: 0;">
                                    <span style="font-size: 1.1rem; flex-shrink: 0;">${chanMeta.icon}</span>
                                    <span style="font-size: 0.85rem; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${chanMeta.name}</span>
                                </div>
                                <div style="flex-shrink: 0; display: flex; align-items: center; gap: 6px;">
                                    ${actionHtml}
                                </div>
                            </div>
                            ${isFailed ? `
                                <div style="font-size: 0.72rem; color: #ff7875; background: rgba(255, 77, 79, 0.08); border: 1px solid rgba(255, 77, 79, 0.25); border-left: 3px solid #ff4d4f; border-radius: 4px; padding: 6px 10px; line-height: 1.45; word-break: break-word;">
                                    ${statusText}
                                </div>
                            ` : (statusText && statusText !== '⚪ 尚未分发至该渠道' && !isSuccess && !isSkipped ? `
                                <div style="font-size: 0.7rem; color: ${statusColor}; padding-left: 28px; line-height: 1.35;">
                                    ${statusText}
                                </div>
                            ` : '')}
                        </div>
                    `;
                });
                resultsHtml += `</div>`;

                const oldPanel = document.getElementById('syndicate-results-panel');
                if (oldPanel) oldPanel.remove();

                const progressPanel = document.getElementById('syndicate-progress-panel');
                if (progressPanel) {
                    progressPanel.insertAdjacentHTML('afterend', resultsHtml);
                    // 🚀 物理自动平滑滚动：确保结果卡片自动拉入可视视口区
                    const drawerBody = document.getElementById('article-syndicate-drawer');
                    if (drawerBody) {
                        drawerBody.scrollTo({ top: drawerBody.scrollHeight, behavior: 'smooth' });
                    }
                }

                // 🚀 物理实时刷新 Section 2 渠道选择卡片：实时对正最新 Remote ID 与徽章
                if (typeof window.updateSyndicatePlatformCards === 'function') {
                    await window.updateSyndicatePlatformCards(relPath);
                }

                // 🚀 物理长轮询对正：只要仍有渠道在推流中或尚未获取终态，继续轮询 (最高 20 次 / 25 秒)
                if (!allCompleted && retryCount < 20) {
                    setTimeout(() => renderResultsPanel(retryCount + 1), 1200);
                } else {
                    if (progressPercent) progressPercent.innerText = '100%';
                    if (progressBar) progressBar.style.width = '100%';
                    if (progressDesc) {
                        progressDesc.innerText = cardFailCount > 0 
                            ? '⚠️ 广播管线已处理完成（含错误告警，详见下方分布卡片）' 
                            : '🎉 广播与自动翻译管线已全部闭环处理完成！';
                    }
                    if (btn) {
                        btn.disabled = false;
                        btn.innerHTML = '🚀 重新启动社交广播';
                    }
                }
            } catch (e) {
                console.warn("[Syndication Telemetry Error]:", e);
            }
        };

        await renderResultsPanel(0);
    };
})();
