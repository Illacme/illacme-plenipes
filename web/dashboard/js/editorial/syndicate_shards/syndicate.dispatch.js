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

        // 🛡️ [Preflight Guard] 封面图智能防呆拦截 (仅在前台抽屉交互上下文中激活)
        const hasStudio = !!document.getElementById('syndicate-cover-studio-container');
        const REQ_COVER_MAP = { 'wechat': '微信公众号', 'xiaohongshu': '小红书', 'bilibili': 'B站专栏', 'toutiao': '今日头条' };
        const reqTargets = selectedPlatforms.filter(id => REQ_COVER_MAP[id.toLowerCase()]);
        const strat = window.currentSyndicateCover?.strategy || '';
        const isAbstractOrEmpty = !window.currentSyndicateCover?.url || strat === 'og_card' || strat === 'minimal_badge';

        if (hasStudio && reqTargets.length > 0 && isAbstractOrEmpty && !window._bypassCoverPreflight) {
            window.showCoverPreflightModal(relPath, reqTargets.map(id => REQ_COVER_MAP[id.toLowerCase()]));
            return;
        }
        window._bypassCoverPreflight = false;

        // 🚀 1. 切换生命周期到 'running' 执行态
        if (typeof window.switchSyndicateDrawerStage === 'function') {
            window.switchSyndicateDrawerStage('running', { lang: selectedLang, platformCount: selectedPlatforms.length });
        }

        const progressPanel = document.getElementById('syndicate-progress-panel');
        const progressTitle = document.getElementById('syndicate-progress-title');
        const progressPercent = document.getElementById('syndicate-progress-percent');
        const progressBar = document.getElementById('syndicate-progress-bar');
        const progressDesc = document.getElementById('syndicate-progress-desc');

        if (progressPanel) {
            progressPanel.style.display = 'flex';
            if (progressTitle) progressTitle.innerText = `⚙️ 正在启动 [${selectedLang.toUpperCase()}] 分发管线...`;
            if (progressPercent) progressPercent.innerText = '15%';
            if (progressBar) progressBar.style.width = '15%';
            if (progressDesc) progressDesc.innerText = '正在调起后端智能编译与分发中心...';
        }

        const fetchFunc = window.apiFetch || (async (u, i) => { const r = await fetch(u, i); return r.json(); });

        for (let i = 0; i < selectedPlatforms.length; i++) {
            const channelId = selectedPlatforms[i];
            const currentRatio = Math.round(15 + ((i + 1) / selectedPlatforms.length) * 35);
            if (progressPercent) progressPercent.innerText = `${currentRatio}%`;
            if (progressBar) progressBar.style.width = `${currentRatio}%`;
            if (progressDesc) progressDesc.innerText = `📡 [${i + 1}/${selectedPlatforms.length}] 正在向 [${channelId.toUpperCase()}] 进行广播推流...`;

            try {
                const cCov = window.currentSyndicateCover || {};
                await fetchFunc(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        target_slot: selectedLang, target_channel: channelId, skip_syndication: false, clear_cache: false,
                        cover_mode: cCov.mode || 'global', cover_image: cCov.url || '', cover_offset: cCov.offset || 0,
                        cover_overrides: cCov.overrides || {}
                    })
                });
            } catch (e) {
                console.error(`[Syndication Network Error] ${channelId}:`, e);
            }
        }

        let cardSuccessCount = 0;
        let cardFailCount = 0;

        const renderResultsPanel = async (retryCount = 0) => {
            try {
                const timestamp = Date.now();
                const finalStatus = await fetchFunc(`/api/vault/dispatch-status/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}&_t=${timestamp}`);
                const syncMatrix = (finalStatus && Array.isArray(finalStatus.sync_matrix)) ? finalStatus.sync_matrix : [];

                try {
                    const recordsData = await fetchFunc(`/api/syndication/records/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}&_t=${timestamp}`);
                    if (recordsData && Array.isArray(recordsData.records)) {
                        window.currentSyndicationRecords = recordsData.records;
                    }
                } catch (_) { }

                const cardsHtml = [];
                const failedChannelsList = [];
                let allCompleted = true;
                cardSuccessCount = 0;
                cardFailCount = 0;

                selectedPlatforms.forEach(chanId => {
                    const chanMeta = (typeof window.getSyndicateChannelMeta === 'function')
                        ? window.getSyndicateChannelMeta(chanId)
                        : ((typeof window.getSyndicatePlatformMeta === 'function') ? window.getSyndicatePlatformMeta(chanId) : { name: chanId, icon: '📡' });
                    const statusItem = syncMatrix.find(item => {
                        const cId = (item.channel_id || item.channel || '');
                        return cId && cId.toLowerCase() === chanId.toLowerCase();
                    }) || {};
                    const recordItem = (window.currentSyndicationRecords || []).find(r => {
                        const cId = (r.channel || r.channel_id || r.target_id || '');
                        return cId && cId.toLowerCase() === chanId.toLowerCase();
                    }) || {};

                    const cleanStatus = (statusItem.status || '').toUpperCase();
                    const isSyncing = cleanStatus === 'SYNCING' || (cleanStatus === 'PENDING' && retryCount < 3);
                    const isSuccess = ['SUCCESS', 'PUBLISHED', 'SYNCED', 'DONE'].includes(cleanStatus);
                    const isFailed = ['FAILED', 'ERROR'].includes(cleanStatus);
                    const isDraft = ['DRAFT', 'DRAFT_SAVED'].includes(cleanStatus);
                    const isSkipped = ['SKIPPED', 'SKIPPED_UNMODIFIED'].includes(cleanStatus);

                    if (isSyncing) allCompleted = false;
                    if (isSuccess || isSkipped || isDraft) cardSuccessCount++;
                    if (isFailed) {
                        cardFailCount++;
                        failedChannelsList.push(chanId);
                    }

                    const liveLink = recordItem.remote_url || recordItem.url || statusItem.artifact_url || statusItem.url || '';
                    const diag = statusItem.diagnosis || statusItem.diagnostic || null;
                    const errorMsg = statusItem.reason || (diag && diag.friendly_message) || '广播异常';

                    let actionHtml = '';
                    if (isSyncing) {
                        actionHtml = `<span style="font-size:0.68rem;color:#00f2fe;background:rgba(0,242,255,0.12);padding:3px 7px;border-radius:4px;">⚙️ 推流中...</span>`;
                    } else if ((isSkipped || isSuccess) && liveLink && liveLink !== '#') {
                        actionHtml = `<a href="${liveLink}" target="_blank" style="padding:4px 10px;font-size:0.72rem;font-weight:700;background:rgba(0,242,255,0.2);color:#00f2fe;border:1px solid rgba(0,242,255,0.4);border-radius:6px;text-decoration:none;">🌐 线上 ↗</a>`;
                    } else if (isDraft && liveLink && liveLink !== '#') {
                        actionHtml = `<a href="${liveLink}" target="_blank" style="padding:4px 10px;font-size:0.72rem;font-weight:700;background:#ffc107;color:#000;border-radius:6px;text-decoration:none;">📝 草稿箱 ↗</a>`;
                    } else if (isFailed) {
                        const qId = diag && diag.quick_drawer_id ? diag.quick_drawer_id : '';
                        actionHtml = `
                            ${qId ? `<button type="button" onclick="if(window.openPluginConfig)window.openPluginConfig('${qId}','syndicate','syndicate');" style="padding:3px 7px;font-size:0.68rem;background:rgba(0,242,255,0.12);color:#00f2fe;border:1px solid rgba(0,242,255,0.3);border-radius:5px;cursor:pointer;">⚙️ 快速配置</button>` : ''}
                            <button type="button" onclick="window.retrySinglePlatform('${relPath.replace(/'/g, "\\'")}', '${chanId}')" style="padding:3px 8px;font-size:0.7rem;font-weight:600;background:rgba(0,242,255,0.15);color:#00f2fe;border:1px solid rgba(0,242,255,0.35);border-radius:5px;cursor:pointer;">🔄 重试</button>
                        `;
                    } else {
                        actionHtml = `<span style="font-size:0.68rem;color:#00ff88;background:rgba(0,255,136,0.12);padding:3px 7px;border-radius:4px;">🟢 推流完成</span>`;
                    }

                    let diagContentHtml = '';
                    if (isFailed && diag) {
                        const qId = diag.quick_drawer_id || '';
                        diagContentHtml = `
                            <div style="font-size:0.7rem;color:#ff7875;background:rgba(255,77,79,0.08);border:1px solid rgba(255,77,79,0.25);border-left:3px solid #ff4d4f;border-radius:6px;padding:6px 9px;display:flex;flex-direction:column;gap:3px;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <span style="font-weight:700;color:#ff4d4f;">${diag.badge || '❌ 分发失败'}</span>
                                    ${qId ? `<span style="font-size:0.65rem;color:#00f2fe;cursor:pointer;text-decoration:underline;" onclick="if(window.openPluginConfig)window.openPluginConfig('${qId}','syndicate','syndicate');">直达配置 ↗</span>` : ''}
                                </div>
                                <div><strong>归因：</strong>${diag.friendly_message || errorMsg}</div>
                                ${diag.suggestion ? `<div style="color:#ffd591;font-size:0.66rem;"><strong>建议：</strong>${diag.suggestion}</div>` : ''}
                            </div>
                        `;
                    } else if (isFailed && errorMsg) {
                        diagContentHtml = `
                            <div style="font-size:0.7rem;color:#ff7875;background:rgba(255,77,79,0.08);border:1px solid rgba(255,77,79,0.25);border-left:3px solid #ff4d4f;border-radius:6px;padding:6px 9px;">
                                <div><strong>失败原因：</strong>${errorMsg}</div>
                            </div>
                        `;
                    }

                    cardsHtml.push(`
                        <div style="flex-shrink:0;padding:8px 10px;border-radius:8px;background:${isFailed ? 'rgba(255,77,79,0.05)' : 'rgba(255,255,255,0.02)'};border:1px solid ${isFailed ? 'rgba(255,77,79,0.3)' : 'rgba(255,255,255,0.06)'};display:flex;flex-direction:column;gap:6px;">
                            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                                <div style="display:flex;align-items:center;gap:6px;min-width:0;">
                                    <span style="font-size:1rem;flex-shrink:0;">${chanMeta.icon}</span>
                                    <span style="font-size:0.82rem;font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${chanMeta.name}</span>
                                </div>
                                <div style="flex-shrink:0;display:flex;align-items:center;gap:6px;">${actionHtml}</div>
                            </div>
                            ${diagContentHtml}
                        </div>
                    `);
                });

                const totalChannels = selectedPlatforms.length;
                let summaryBadge = cardFailCount > 0
                    ? `<span style="color:#ff7875;font-size:0.75rem;font-weight:700;">⚠️ ${cardSuccessCount} 成功 · ${cardFailCount} 需注意</span>`
                    : `<span style="color:#00ff88;font-size:0.75rem;font-weight:700;">🎉 全部 ${totalChannels} 渠道推流完成</span>`;

                let resultsHtml = `
                    <div id="syndicate-results-panel" style="flex-shrink:0;display:flex;flex-direction:column;gap:8px;border:1px solid ${cardFailCount > 0 ? 'rgba(255,77,79,0.4)' : 'var(--accent-secondary,#00f2fe)'};background:${cardFailCount > 0 ? 'rgba(255,77,79,0.03)' : 'rgba(0,242,255,0.03)'};padding:10px 12px;border-radius:10px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                            <span style="font-size:0.82rem;font-weight:700;color:#fff;">📡 广播物理凭证终态分布</span>
                            ${summaryBadge}
                        </div>
                        <div style="display:flex;flex-direction:column;gap:6px;">
                            ${cardsHtml.join('')}
                        </div>
                    </div>
                `;

                const resultsSlot = document.getElementById('syndicate-results-panel-slot');
                if (resultsSlot) {
                    resultsSlot.innerHTML = resultsHtml;
                }

                if (!allCompleted && retryCount < 15) {
                    const pollProgress = Math.min(95, 50 + retryCount * 4);
                    if (progressPercent) progressPercent.innerText = `${pollProgress}%`;
                    if (progressBar) progressBar.style.width = `${pollProgress}%`;
                    if (progressDesc) progressDesc.innerText = `⚙️ 正在等待各渠道对端服务器确认凭证 (轮询第 ${retryCount + 1} 次)...`;
                    setTimeout(() => renderResultsPanel(retryCount + 1), 1000);
                } else {
                    if (progressPercent) progressPercent.innerText = '100%';
                    if (progressBar) progressBar.style.width = '100%';
                    if (progressDesc) {
                        progressDesc.innerText = cardFailCount > 0
                            ? '⚠️ 广播管线已处理完成（含错误告警，详见下方分布卡片）'
                            : '🎉 广播与自动翻译管线已全部闭环处理完成！';
                    }
                    if (typeof window.switchSyndicateDrawerStage === 'function') {
                        window.switchSyndicateDrawerStage('telemetry', {
                            failedCount: cardFailCount,
                            failedChannelsJson: JSON.stringify(failedChannelsList)
                        });
                    }
                }
            } catch (e) {
                console.warn("[Syndication Telemetry Error]:", e);
                if (typeof window.switchSyndicateDrawerStage === 'function') {
                    window.switchSyndicateDrawerStage('telemetry', { failedCount: 1, failedChannelsJson: '[]' });
                }
            }
        };

        await renderResultsPanel(0);
    };

    window.showCoverPreflightModal = function (relPath, channelNames) {
        let modal = document.getElementById('syndicate-cover-preflight-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'syndicate-cover-preflight-modal';
            modal.style.cssText = 'position:fixed;inset:0;z-index:10005;background:rgba(5,8,16,0.85);backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:center;padding:16px;';
            document.body.appendChild(modal);
        }
        const namesStr = (channelNames || []).join('、');
        modal.innerHTML = `
            <div class="glass-panel" style="width:460px;max-width:92vw;background:rgba(18,24,38,0.98);border:1px solid rgba(0,242,254,0.25);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:14px;box-shadow:0 20px 60px rgba(0,0,0,0.7);">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:8px;font-size:0.95rem;font-weight:700;color:var(--accent-secondary,#00f2fe);">
                        <span>🖼️ 封面视觉增强建议</span>
                    </div>
                    <button type="button" onclick="window.closeCoverPreflightModal()" style="background:transparent;border:none;color:var(--text-dim);font-size:1.3rem;cursor:pointer;line-height:1;">×</button>
                </div>
                <div style="font-size:0.78rem;color:var(--text-main,#e2e8f0);line-height:1.6;background:rgba(255,255,255,0.03);padding:10px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);">
                    检测到您勾选了 <b style="color:#00f2fe;">【${namesStr}】</b> 等强依赖视觉封面的平台，当前文章尚未配置实体封面（将使用技术抽象卡片保底）。<br><span style="color:var(--text-dim);font-size:0.72rem;">配置精美封面可显著提升读者在社交信息流与会话列表的点击率。</span>
                </div>
                <div style="display:flex;flex-direction:column;gap:8px;padding-top:4px;">
                    <button type="button" class="mini-btn glow-btn" onclick="window.triggerAiCoverAndProceed('${(relPath || '').replace(/'/g, "\\'")}')" style="width:100%;padding:9px;background:rgba(0,242,254,0.18);border:1px solid rgba(0,242,254,0.4);color:var(--accent-secondary,#00f2fe);border-radius:8px;cursor:pointer;font-weight:700;font-size:0.8rem;display:flex;align-items:center;justify-content:center;gap:6px;">
                        🤖 一键 AI 意境生图并继续分发
                    </button>
                    <div style="display:flex;gap:8px;">
                        <button type="button" class="mini-btn" onclick="window.closeCoverPreflightModal(); window.openSyndicateAssetPickerModal();" style="flex:1;padding:8px;background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.35);color:#a5b4fc;border-radius:8px;cursor:pointer;font-size:0.75rem;">
                            🗄️ 从资产库挑选...
                        </button>
                        <button type="button" class="mini-btn" onclick="window.bypassCoverPreflightAndDispatch('${(relPath || '').replace(/'/g, "\\'")}')" style="flex:1;padding:8px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.15);color:var(--text-dim);border-radius:8px;cursor:pointer;font-size:0.75rem;">
                            🚀 保持现状直接分发
                        </button>
                    </div>
                </div>
            </div>
        `;
        modal.style.display = 'flex';
    };

    window.closeCoverPreflightModal = function () {
        const modal = document.getElementById('syndicate-cover-preflight-modal');
        if (modal) modal.style.display = 'none';
    };

    window.bypassCoverPreflightAndDispatch = function (relPath) {
        window.closeCoverPreflightModal();
        window._bypassCoverPreflight = true;
        window.dispatchArticleSyndication(relPath);
    };

    window.triggerAiCoverAndProceed = async function (relPath) {
        const btn = document.querySelector('#syndicate-cover-preflight-modal .glow-btn');
        if (btn) { btn.innerHTML = '🤖 正在生成 AI 意境封面...'; btn.disabled = true; }
        if (typeof window.onSyndicateCoverModeChange === 'function') {
            await window.onSyndicateCoverModeChange('ai_generation');
        }
        window.closeCoverPreflightModal();
        window._bypassCoverPreflight = true;
        window.dispatchArticleSyndication(relPath);
    };
})();
