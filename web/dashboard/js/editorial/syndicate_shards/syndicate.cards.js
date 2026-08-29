/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - Channel Cards & Language Picker Shard
 * 职责：广播渠道卡片列表动态渲染、语种变更事件分流与译文就绪状态侦测。
 */

(function () {
    window.updateSyndicatePlatformCards = async function (relPath) {
        relPath = relPath || window.currentSyndicatingRelPath;
        const container = document.getElementById('syndicate-platform-list-container');
        if (!container || !window.currentActivePlatforms || !relPath) return;

        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = (langRadio ? langRadio.value : 'zh').toLowerCase();

        try {
            const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
            const recordsData = await fetchApi(`/api/syndication/records/${encodeURIComponent(relPath)}?lang_code=${encodeURIComponent(selectedLang)}`);
            if (recordsData && recordsData.records) {
                window.currentSyndicationRecords = recordsData.records;
            }
        } catch (e) {
            console.warn("[Article Syndication] Refresh syndication records failed:", e);
        }

        container.innerHTML = window.currentActivePlatforms.map(p => {
            const record = (window.currentSyndicationRecords || []).find(r => 
                (r.target_id || '').toLowerCase() === p.id.toLowerCase() &&
                (r.lang_code || '').toLowerCase() === selectedLang
            );
            const hasRemoteRecord = !!(record && record.remote_article_id);
            const remoteUrl = record ? record.remote_url : null;
            const noUpdateSupport = ['medium', 'substack', 'zhihu'].includes(p.id.toLowerCase());
            const isOutdated = !!(record && record.is_outdated);

            let actionBadgeHtml = '🚀 首次发布 (Create)';
            let actionBadgeBg = 'rgba(0, 242, 255, 0.12)';
            let actionBadgeColor = '#00f2fe';

            if (hasRemoteRecord) {
                if (isOutdated) {
                    actionBadgeHtml = '⚠️ 内容已变更 (Outdated)';
                    actionBadgeBg = 'rgba(245, 158, 11, 0.18)';
                    actionBadgeColor = '#f59e0b';
                } else if (noUpdateSupport) {
                    actionBadgeHtml = '⚠️ 降级新建 (Re-create)';
                    actionBadgeBg = 'rgba(251, 191, 36, 0.12)';
                    actionBadgeColor = '#fbbf24';
                } else {
                    actionBadgeHtml = '🔄 覆写更新 (Update)';
                    actionBadgeBg = 'rgba(187, 134, 252, 0.18)';
                    actionBadgeColor = '#bb86fc';
                }
            }

            return `
            <div class="glass-panel" style="padding: 10px 12px; border-radius: 8px; border: 1px solid ${hasRemoteRecord ? (isOutdated ? 'rgba(245, 158, 11, 0.45)' : 'rgba(187, 134, 252, 0.35)') : (p.isReady ? 'rgba(0, 255, 136, 0.25)' : 'rgba(255,255,255,0.06)')}; display: flex; flex-direction: column; gap: 8px; opacity: ${p.isReady ? '1' : '0.75'}; background: ${hasRemoteRecord ? (isOutdated ? 'rgba(245, 158, 11, 0.05)' : 'rgba(187, 134, 252, 0.04)') : (p.isReady ? 'rgba(0, 255, 136, 0.03)' : 'rgba(255,255,255,0.01)')};">
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <input type="checkbox" value="${p.id}" class="syndicate-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'} style="accent-color: var(--accent-secondary); width: 16px; height: 16px; cursor: ${p.isReady ? 'pointer' : 'not-allowed'};">
                        <div>
                            <div style="font-size: 0.82rem; font-weight: 600; color: ${p.isReady ? '#fff' : 'var(--text-dim)'}; display: flex; align-items: center; gap: 6px;">
                                <span>${p.icon} ${p.name}</span>
                                <span style="font-size: 0.64rem; font-weight: normal; padding: 1px 5px; border-radius: 3px; background: ${p.isReady ? 'rgba(0, 255, 136, 0.12)' : 'rgba(245, 158, 11, 0.12)'}; color: ${p.isReady ? '#00ff88' : '#f59e0b'}; border: 1px solid ${p.isReady ? 'rgba(0, 255, 136, 0.3)' : 'rgba(245, 158, 11, 0.3)'};">
                                    ${p.isReady ? `🟢 ${p.credLabel}` : `⚠️ ${p.credLabel}`}
                                </span>
                            </div>
                            <div style="font-size: 0.68rem; color: var(--text-dim); margin-top: 2px;">${p.desc}</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        ${p.isReady ? `
                            <span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; white-space: nowrap; background: ${actionBadgeBg}; color: ${actionBadgeColor}; border: 1px solid ${actionBadgeColor}55; font-weight: 600;">${actionBadgeHtml}</span>
                            <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="修改此渠道的 Token 密钥或配置" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">⚙️</button>
                        ` : `
                            <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="前往配置并激活此渠道" style="background: rgba(0, 242, 255, 0.15); border: 1px solid rgba(0, 242, 255, 0.35); color: var(--neon-cyan, #00f2fe); border-radius: 4px; padding: 3px 8px; font-size: 0.68rem; font-weight: 600; cursor: pointer; white-space: nowrap;">⚙️ 去配置/补全凭据</button>
                        `}
                    </div>
                </div>
                ${hasRemoteRecord ? `
                    <div style="padding-top: 6px; border-top: 1px dashed rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: space-between; font-size: 0.68rem; color: var(--text-dim);">
                        <div style="display: flex; align-items: center; gap: 6px; overflow: hidden;">
                            <span>🆔 ID: <code>${record.remote_article_id}</code></span>
                            ${remoteUrl ? `<a href="${remoteUrl}" target="_blank" style="color: #00f2fe; text-decoration: none;">🔗 对端文章 ↗</a>` : ''}
                        </div>
                        <div style="display: flex; gap: 4px;">
                            <button type="button" onclick="window.deleteRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}')" style="background: rgba(255, 77, 79, 0.15); border: 1px solid rgba(255, 77, 79, 0.35); color: #ff4d4f; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;">🗑️ 远程下架</button>
                            <button type="button" onclick="window.unlinkRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}')" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #aaa; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer;" title="仅在本地解绑，不删除对端文章">🔗 解绑</button>
                        </div>
                    </div>
                ` : ''}
            </div>
            `;
        }).join('');
    };

    window.onSyndicateLangChange = function (radioInput, relPath) {
        const labels = document.querySelectorAll('#syndicate-lang-picker .lang-radio-btn');
        labels.forEach(l => {
            l.classList.remove('active');
            l.style.background = '';
            l.style.borderColor = '';
        });
        if (radioInput && radioInput.parentElement) {
            radioInput.parentElement.classList.add('active');
        }

        const selectedLang = radioInput ? radioInput.value : 'zh';
        const tipEl = document.getElementById('syndicate-translation-readiness-tip');
        if (!tipEl) return;

        const sourceLangCode = (window.settingsData?.i18n_settings?.source?.lang_code || window.settingsData?.source?.lang_code || 'zh').toLowerCase();

        if (selectedLang.toLowerCase() === sourceLangCode) {
            tipEl.style.cssText = 'font-size: 0.72rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px solid rgba(0, 255, 136, 0.2); padding: 6px 10px; border-radius: 6px; margin-top: 2px;';
            tipEl.innerHTML = '🟢 当前选中的是原稿母语，无需翻译，启动后可直达社交分发平台。';
        } else {
            const docStatus = window.currentArticleDispatchStatus;
            const matrixItem = docStatus?.sync_matrix?.find(m => (m.lang_code || '').toLowerCase() === selectedLang.toLowerCase());

            const statusLower = (matrixItem?.status || '').toLowerCase();
            const cacheInfo = matrixItem?.cache_info || '';
            const progress = matrixItem?.progress || 0;
            const isReady = statusLower === 'published' || statusLower === 'success' || statusLower === 'synced' || statusLower === 'done' || progress === 100 || (cacheInfo.includes('已缓存') && !cacheInfo.includes(' 0/'));
            
            const currentTitle = window.currentSyndicatingTitle || relPath || '';
            const jumpBtnHtml = `<button type="button" onclick="window.jumpToReviewDrawer('${(relPath || '').replace(/'/g, "\\'")}', '${currentTitle.replace(/'/g, "\\'")}')" style="padding: 2px 8px; font-size: 0.68rem; font-weight: 600; background: rgba(187, 134, 252, 0.18); color: #bb86fc; border: 1px solid rgba(187, 134, 252, 0.38); border-radius: 4px; cursor: pointer; white-space: nowrap; flex-shrink: 0; display: inline-flex; align-items: center; gap: 3px;">🔍 译文精校 ↗</button>`;

            if (isReady) {
                tipEl.style.cssText = 'font-size: 0.72rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px solid rgba(0, 255, 136, 0.2); padding: 6px 10px; border-radius: 6px; margin-top: 2px; display: flex; align-items: center; justify-content: space-between; gap: 8px;';
                const detailText = cacheInfo ? ` (${cacheInfo})` : '';
                tipEl.innerHTML = `<span>🟢 目标语种 [${selectedLang.toUpperCase()}] 译文已就绪${detailText}，启动后直接分发。</span>${jumpBtnHtml}`;
            } else {
                tipEl.style.cssText = 'font-size: 0.72rem; color: #fbbf24; background: rgba(251, 191, 36, 0.08); border: 1px solid rgba(251, 191, 36, 0.25); padding: 6px 10px; border-radius: 6px; margin-top: 2px; display: flex; align-items: center; justify-content: space-between; gap: 8px;';
                tipEl.innerHTML = `<span>⚡ 目标语种 [${selectedLang.toUpperCase()}] 译文尚未就绪，启动后将由 AI 自动翻译！</span>${jumpBtnHtml}`;
            }
        }

        // 🚀 [语种切换数据隔离] 清理上一语种的执行进度条与分发终态卡片，避免状态跨语种污染
        const oldResults = document.getElementById('syndicate-results-panel');
        if (oldResults) oldResults.remove();

        const progressPanel = document.getElementById('syndicate-progress-panel');
        if (progressPanel) progressPanel.style.display = 'none';

        if (window.syndicateProgressTimer) {
            clearInterval(window.syndicateProgressTimer);
            window.syndicateProgressTimer = null;
        }

        const btn = document.getElementById('btn-start-article-syndicate');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '🚀 启动社交广播';
        }

        if (typeof window.updateSyndicatePlatformCards === 'function') {
            window.updateSyndicatePlatformCards(relPath || window.currentSyndicatingRelPath);
        }
        if (typeof window.renderSyndicateCardPreview === 'function') {
            window.renderSyndicateCardPreview();
        }
    };
})();
