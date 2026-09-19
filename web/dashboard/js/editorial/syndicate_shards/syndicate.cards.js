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

        const configuredTargets = (window.settingsData?.i18n_settings?.targets || window.settingsData?.translation?.targets || []).map(t => (typeof t === 'string' ? t : (t.lang_code || t.code || '')).toLowerCase()).filter(Boolean);
        const sourceLangCode = (window.settingsData?.i18n_settings?.source?.lang_code || window.settingsData?.source?.lang_code || 'zh').toLowerCase();

        const isRecordMatch = (rLang, selLang) => {
            const r = (rLang || '').toLowerCase();
            const s = (selLang || '').toLowerCase();
            if (s === 'auto' || s === sourceLangCode || s === 'source') {
                if (r === 'auto' || r === 'source') return true;
                if (sourceLangCode !== 'auto' && (r === sourceLangCode || r.startsWith(sourceLangCode + '-'))) return true;
                if (!configuredTargets.includes(r) && !configuredTargets.some(t => r.startsWith(t + '-'))) return true;
                return false;
            }
            if (r === s) return true;
            return r.split(/[-_]/)[0] === s.split(/[-_]/)[0];
        };

        container.innerHTML = window.currentActivePlatforms.map(p => {
            const record = (window.currentSyndicationRecords || []).find(r =>
                (r.target_id || '').toLowerCase() === p.id.toLowerCase() &&
                isRecordMatch(r.lang_code, selectedLang)
            );
            const hasRemoteRecord = !!(record && record.remote_article_id);
            const remoteUrl = record ? record.remote_url : null;
            const noUpdateSupport = ['medium', 'substack', 'zhihu'].includes(p.id.toLowerCase());
            const isOutdated = !!(record && record.is_outdated);

            let actionBadgeHtml = '🚀 首次';
            let actionBadgeClass = 'syndicate-action-badge--first';

            if (hasRemoteRecord) {
                if (isOutdated) {
                    actionBadgeHtml = '⚠️ 变更';
                    actionBadgeClass = 'syndicate-action-badge--outdated';
                } else if (noUpdateSupport) {
                    actionBadgeHtml = '⚠️ 新建';
                    actionBadgeClass = 'syndicate-action-badge--create';
                } else {
                    actionBadgeHtml = '🔄 更新';
                    actionBadgeClass = 'syndicate-action-badge--update';
                }
            }

            const slaIcon = p.sla_tier === 'tier2' ? '🍪' : '⚡';
            const slaTip = p.sla_desc || (p.sla_tier === 'tier2' ? 'Cookie 辅助：依赖平台 Web 登录凭据，建议定期校验' : '官方直连：官方开放 API 直连，企业级高可用');
            const credIcon = p.isReady ? '🟢' : '⚠️';
            const credTip = p.credLabel || (p.isReady ? '凭据已就绪' : '待填凭据');

            const channelIcon = (p.icon && p.icon !== '📡')
                ? p.icon
                : ((typeof window.getPlatformBrandBadge === 'function') ? window.getPlatformBrandBadge(p.id, 'publisher').icon : (p.icon || '📡'));

            const COVER_POLICY_MAP = {
                'wechat': { tier: 'required', label: '必配封面', tip: '微信公众号草稿箱接口强制要求永久封面素材 (thumb_media_id)，强烈建议在上方配置专属封面' },
                'xiaohongshu': { tier: 'required', label: '必配首图', tip: '小红书图文笔记机制首图即封面，必须至少包含 1 张图片方可发布' },
                'bilibili': { tier: 'required', label: '必配头图', tip: 'B站专栏文章投稿要求必须提供封面头图 (banner_url)' },
                'toutiao': { tier: 'required', label: '必配封面', tip: '今日头条文章/微头条推荐流强依赖封面卡片 (cover_url)' },
                'devto': { tier: 'recommended', label: '推荐题图', tip: 'Dev.to 支持文章主图 (main_image)，在主页与顶部以长幅横幅展示' },
                'hashnode': { tier: 'recommended', label: '推荐题图', tip: 'Hashnode 支持封面头图 (coverImageURL)，作为主视觉呈现' },
                'medium': { tier: 'recommended', label: '推荐题图', tip: 'Medium 会提取题图作为文章卡片、分享预览与首页大图推荐' },
                'ghost': { tier: 'recommended', label: '推荐特色图', tip: 'Ghost 官方支持 feature_image 特色图像，在主题首屏大图呈现' },
                'wordpress': { tier: 'recommended', label: '推荐特色图', tip: 'WordPress 支持 featured_media 特色图像，作为文章主题封面' },
                'zhihu': { tier: 'recommended', label: '推荐题图', tip: '知乎专栏支持文章题图 (title_image)，在专栏页与信息流呈现' },
                'substack': { tier: 'recommended', label: '推荐题图', tip: 'Substack 邮件订阅与文章页支持封面大图' }
            };
            const cov = COVER_POLICY_MAP[p.id.toLowerCase()];
            let coverBadgeHtml = '';
            if (cov) {
                if (cov.tier === 'required') {
                    coverBadgeHtml = `<span title="${cov.tip}" class="syndicate-cover-badge syndicate-cover-badge--required">🖼️ ${cov.label}</span>`;
                } else if (cov.tier === 'recommended') {
                    coverBadgeHtml = `<span title="${cov.tip}" class="syndicate-cover-badge syndicate-cover-badge--recommended">🖼️ ${cov.label}</span>`;
                }
            }

            const rawRemoteId = String(record?.remote_article_id || '');
            const displayRemoteId = rawRemoteId.length > 16
                ? `${rawRemoteId.slice(0, 8)}...${rawRemoteId.slice(-6)}`
                : rawRemoteId;

            const cardStateClass = hasRemoteRecord ? (isOutdated ? 'syndicate-card syndicate-card--outdated' : 'syndicate-card syndicate-card--published') : (p.isReady ? 'syndicate-card syndicate-card--ready' : 'syndicate-card');

            return `
            <div class="glass-panel ${cardStateClass}">
                <div class="syndicate-card-main-row">
                    <div class="syndicate-card-left">
                        <input type="checkbox" value="${p.id}" class="syndicate-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'}>
                        <div class="syndicate-platform-label">
                            <span class="${p.isReady ? 'syndicate-platform-name' : 'syndicate-platform-name syndicate-platform-name--inactive'}">
                                <span>${channelIcon}</span>
                                <span>${p.name}</span>
                            </span>
                            <span title="${slaTip}" class="syndicate-icon-tip" style="opacity: ${p.isReady ? '0.9' : '0.6'};">${slaIcon}</span>
                            <span title="${credTip}" class="syndicate-icon-tip">${credIcon}</span>
                            ${coverBadgeHtml}
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; flex-shrink: 0;">
                        ${p.isReady ? `
                            <span title="${actionBadgeHtml}" class="syndicate-action-badge ${actionBadgeClass}">${actionBadgeHtml}</span>
                            <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="修改渠道凭据或配置" class="syndicate-settings-btn">⚙️</button>
                        ` : `
                            <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="${credTip} - 前往配置" class="syndicate-config-btn">⚙️</button>
                        `}
                    </div>
                </div>
                ${hasRemoteRecord ? `
                    <div class="syndicate-record-row">
                        <div class="syndicate-record-left">
                            <span style="display: inline-flex; align-items: center; gap: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                <span style="opacity: 0.85;">🆔 ID:</span>
                                <code title="完整对端 ID: ${rawRemoteId} (点击可复制)" onclick="if(navigator.clipboard){navigator.clipboard.writeText('${rawRemoteId}');if(window.showToast)window.showToast('已复制对端 ID','success');}" class="syndicate-remote-id">${displayRemoteId}</code>
                            </span>
                            ${remoteUrl ? `<a href="${remoteUrl}" target="_blank" class="syndicate-remote-link" title="在新标签页中打开对端文章">🔗 对端文章 ↗</a>` : ''}
                        </div>
                        <div style="display: flex; align-items: center; gap: 4px; flex-shrink: 0;">
                            <button type="button" onclick="window.deleteRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}', '${(record?.lang_code || '').replace(/'/g, "\\'")}')" class="syndicate-delete-btn" title="从对端平台下架删除此文章">🗑️ 下架</button>
                            <button type="button" onclick="window.unlinkRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}', '${(record?.lang_code || '').replace(/'/g, "\\'")}')" class="syndicate-unlink-btn" title="仅在本地解绑指纹映射，不删除对端文章">🔗 解绑</button>
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
            tipEl.className = 'syndicate-tip-box syndicate-tip-box--source';
            tipEl.style.cssText = '';
            tipEl.innerHTML = '🟢 当前选中的是原稿母语，无需翻译，启动后可直达社交分发平台。';
        } else {
            const docStatus = window.currentArticleDispatchStatus;
            const matrixItem = docStatus?.sync_matrix?.find(m => (m.lang_code || '').toLowerCase() === selectedLang.toLowerCase());

            const statusLower = (matrixItem?.status || '').toLowerCase();
            const cacheInfo = matrixItem?.cache_info || '';
            const progress = matrixItem?.progress || 0;
            const isReady = statusLower === 'published' || statusLower === 'success' || statusLower === 'synced' || statusLower === 'done' || progress === 100 || (cacheInfo.includes('已缓存') && !cacheInfo.includes(' 0/'));

            const jumpBtnHtml = `<button type="button" class="syndicate-review-jump-btn" onclick="window.jumpToReviewDrawer(window.currentSyndicatingRelPath, window.currentSyndicatingTitle)">🔍 译文精校 ↗</button>`;

            if (isReady) {
                tipEl.className = 'syndicate-tip-box syndicate-tip-box--ready';
                tipEl.style.cssText = '';
                const detailText = cacheInfo ? ` (${cacheInfo})` : '';
                tipEl.innerHTML = `<span>🟢 目标语种 [${selectedLang.toUpperCase()}] 译文已就绪${detailText}，启动后直接分发。</span>${jumpBtnHtml}`;
            } else {
                tipEl.className = 'syndicate-tip-box syndicate-tip-box--pending';
                tipEl.style.cssText = '';
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
        if (typeof window.onSyndicateCoverLangChange === 'function') {
            window.onSyndicateCoverLangChange(selectedLang);
        }
    };
})();
