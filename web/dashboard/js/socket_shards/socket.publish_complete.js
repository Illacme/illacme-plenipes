/**
 * ✅ [V55.9] Dashboard WebSocket - Publish Complete Shard
 * 模块职责：SYNC_COMPLETED 信号处理器 — 发布完成流水线通知、终端状态更新
 *           以及智能社媒分发引导弹窗。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 从 dashboard.socket.js 纵切分离。
 */

/**
 * 处理 SYNC_COMPLETED 信号：标记发布完成、更新终端 UI 与触发社媒分发引导。
 * @param {object} data - WebSocket 消息体
 */
window._wsHandlePublishComplete = (data) => {
    // 🪐 [混合渐进式] 同步完成 — 拉取最终全量图谱确保一致性
    console.log('✅ [WS] 同步完成，拉取最终全量图谱...');
    if (typeof window.addAudit === 'function') {
        window.addAudit('网站发布流程已全部完成！', 'success');
    }
    // 🚀 [V10.4] 记录已完成发布状态，用于防重入提示及重新发布选项
    const activeId = window.settingsData?._active_imprint || 'default';
    localStorage.setItem(`sync_completed_${activeId}`, 'true');
    localStorage.setItem('sync_completed', 'true');

    if (typeof window.refreshGalaxy === 'function') {
        window.refreshGalaxy();
    }
    // 🚀 [V78.7] 白盒化进度流：显示流水线完成并点亮确认按钮
    const modal = document.getElementById('terminal-modal');
    if (modal && modal.style.display !== 'none') {
        if ((modal.dataset.context === 'publish_preview' || modal.dataset.context === 'preview') && typeof window.handlePreviewSyncCompleted === 'function') {
            window.handlePreviewSyncCompleted();
        } else {
            if (typeof window.appendTerminalLog === 'function') {
                window.appendTerminalLog('✅ 同步流水线执行完毕，资产已全量生成！', '#00ff88');
            }
            const okBtn = document.getElementById('btn-terminal-ok');
            if (okBtn) okBtn.style.display = 'block';

            const republishBtn = document.getElementById('btn-terminal-republish');
            if (republishBtn) republishBtn.style.display = 'none';

            const openPreviewBtn = document.getElementById('btn-terminal-open-preview');
            if (openPreviewBtn) openPreviewBtn.style.display = 'none';

            // 🛡️ [Abort] 隐藏中止按钮
            const abortBtn = document.getElementById('btn-terminal-abort');
            if (abortBtn) abortBtn.style.display = 'none';

            const statusEl = document.getElementById('terminal-status');
            if (statusEl) {
                statusEl.innerText = 'COMPLETED';
                statusEl.className = 'online';
            }
        }
    }

    // 🚀 [V89.0] 部署后置智能自愈引导：智能查询待同步分发资产并提供一键同步弹窗
    // 🛡️ [发布预览与校对豁免] 本地发布预览、单篇校对工作台激活中、或未启用社媒分发时，绝不弹出社媒分发提示
    const isReviewDrawerOpen = !!(window._reviewState?.docId || 
                                  document.getElementById('translation-review-drawer')?.classList.contains('active') ||
                                  document.getElementById('translation-review-modal')?.classList.contains('active'));
    const isSyndicationEnabled = window.settingsData?.syndication?.enabled === true;
    const isPreviewFlow = data.payload?.local_only === true ||
                          window._isPublishPreviewActive ||
                          isReviewDrawerOpen ||
                          !isSyndicationEnabled ||
                          (modal && (modal.dataset.context === 'publish_preview' || modal.dataset.context === 'preview' || modal.dataset.lastContext?.startsWith('publish_preview')));
    if (isPreviewFlow) {
        return;
    }

    setTimeout(async () => {
        try {
            // 🛡️ 免打扰自愈：如果用户点击过"不再提示"，则直接屏蔽后续弹窗
            if (localStorage.getItem('ignore_syndication_sync_prompt') === 'true') {
                return;
            }

            const syncInfo = await apiFetch('/api/vault/pending-syndication');
            if (syncInfo && syncInfo.count > 0) {
                Swal.fire({
                    title: '📢 发现待分发社媒资产',
                    html: `全站网页发布已全部就绪。<br>检测到有 <b style="color: #00f2fe;">${syncInfo.count}</b> 篇新稿件尚未分发至社交媒体（如 Dev.to 等），是否需要一键并行分发？`,
                    icon: 'question',
                    showCancelButton: true,
                    showDenyButton: true, // 提供"不再提示"屏蔽开关
                    confirmButtonText: '🚀 一键分发',
                    denyButtonText: '🔕 不再提示',
                    cancelButtonText: '暂不分发',
                    background: 'rgba(20,20,30,0.95)',
                    color: '#e0e0e0',
                    confirmButtonColor: '#00f2fe',
                    denyButtonColor: '#e74c3c',
                    cancelButtonColor: '#555'
                }).then(async (result) => {
                    if (result.isDenied) {
                        localStorage.setItem('ignore_syndication_sync_prompt', 'true');
                        if (typeof window.addAudit === 'function') {
                            window.addAudit('已记录创作者偏好：后续全站发布完毕后不再主动弹出社媒分发提醒。', 'info');
                        }
                        return;
                    }

                    if (result.isConfirmed) {
                        Swal.fire({
                            title: '🛰️ 正在分发中...',
                            html: '正在向激活的社交媒体网关分发资产，并实时追踪链路状态，请稍候...',
                            allowOutsideClick: false,
                            didOpen: () => {
                                Swal.showLoading();
                            }
                        });
                        
                        const pendingDocs = syncInfo.pending_docs || [];
                        
                        // 1. 发起所有文档的重新同步请求
                        for (const doc of pendingDocs) {
                            try {
                                await apiFetch(`/api/vault/re-dispatch/${encodeURIComponent(doc.rel_path)}`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ force: true })
                                });
                            } catch (e) {
                                console.error('[Sync] 提交分发任务失败:', e);
                            }
                        }
                        
                        // 2. 轮询各渠道状态，直到全部 syncing 结束
                        const maxPollAttempts = 40; // 最多轮询 60 秒 (40 * 1500ms)
                        let attempt = 0;
                        
                        while (attempt < maxPollAttempts) {
                            await new Promise(resolve => setTimeout(resolve, 1500));
                            attempt++;
                            
                            let allDone = true;
                            for (const doc of pendingDocs) {
                                try {
                                    const statusResp = await apiFetch(`/api/vault/dispatch-status/${encodeURIComponent(doc.rel_path)}`);
                                    if (statusResp && statusResp.sync_matrix) {
                                        const targetItems = statusResp.sync_matrix.filter(item => item.lang_code === 'SYNDICATION' || item.lang_code === 'HOSTING');
                                        for (const item of targetItems) {
                                            if ((item.status || '').toLowerCase() === 'syncing') {
                                                allDone = false;
                                                break;
                                            }
                                        }
                                    }
                                } catch (e) {
                                    console.error('[Sync] 查询分发状态异常:', e);
                                }
                                if (!allDone) break;
                            }
                            
                            if (allDone) {
                                break;
                            }
                        }
                        
                        // 3. 统计最终真实的成功与失败文档数
                        let successCount = 0;
                        let failCount = 0;
                        let failedDetails = [];
                        for (const doc of pendingDocs) {
                            try {
                                const finalResp = await apiFetch(`/api/vault/dispatch-status/${encodeURIComponent(doc.rel_path)}`);
                                let docHasFailedChannel = false;
                                let docHasSuccessChannel = false;
                                let channelErrors = [];
                                
                                if (finalResp && finalResp.sync_matrix) {
                                    const targetItems = finalResp.sync_matrix.filter(item => item.lang_code === 'SYNDICATION' || item.lang_code === 'HOSTING');
                                    for (const item of targetItems) {
                                        const stat = (item.status || '').toLowerCase();
                                        if (stat === 'success' || stat === 'published' || stat === 'done' || stat === 'synced') {
                                            docHasSuccessChannel = true;
                                        } else {
                                            docHasFailedChannel = true;
                                            channelErrors.push({
                                                channel: item.locale.replace('📡 ', '').replace('🌐 ', ''),
                                                reason: item.reason || '未提供具体错误信息'
                                            });
                                        }
                                    }
                                }
                                if (docHasFailedChannel) {
                                    failCount++;
                                    failedDetails.push({
                                        title: doc.title || doc.rel_path,
                                        errors: channelErrors
                                    });
                                } else if (docHasSuccessChannel) {
                                    successCount++;
                                }
                            } catch (e) {
                                failCount++;
                                failedDetails.push({
                                    title: doc.title || doc.rel_path,
                                    errors: [{ channel: '系统', reason: e.message || '查询分发状态超时' }]
                                });
                            }
                        }
                        
                        let htmlContent = `已成功将 <b style="color: #00ff88;">${successCount}</b> 篇稿件同步至目标渠道。`;
                        if (failCount > 0) {
                            htmlContent += `<br><br><div style="text-align: left; background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(231, 76, 60, 0.25); max-height: 200px; overflow-y: auto; font-size: 0.8rem;">`;
                            htmlContent += `<b style="color: #ff6b6b; display: block; margin-bottom: 8px;">🚨 同步失败详情 (${failCount} 篇)：</b>`;
                            failedDetails.forEach(detail => {
                                htmlContent += `<div style="margin-bottom: 6px; border-bottom: 1px dashed rgba(255,255,255,0.08); padding-bottom: 6px;">`;
                                htmlContent += `📄 <b style="color: #fff;">${detail.title}</b>:`;
                                detail.errors.forEach(err => {
                                    htmlContent += `<br>&nbsp;&nbsp;• <span style="color: #a5f3fc;">[${err.channel}]</span> <span style="color: #ffb7b7;">${err.reason}</span>`;
                                });
                                htmlContent += `</div>`;
                            });
                            htmlContent += `</div>`;
                        }

                        Swal.fire({
                            title: successCount > 0 && failCount === 0 ? '✅ 一键同步完成' : '⚠️ 同步完成 (含失败)',
                            html: htmlContent,
                            icon: failCount === 0 ? 'success' : 'warning',
                            background: 'rgba(20,20,30,0.95)',
                            color: '#e0e0e0',
                            confirmButtonColor: '#00f2fe'
                        });
                    }
                });
            }
        } catch (e) {
            console.error('⚠️ [自愈引导] 检索待同步列表异常:', e);
        }
    }, 1500);
};
