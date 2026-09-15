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
            let actionBadgeBg = 'rgba(0, 242, 255, 0.1)';
            let actionBadgeColor = '#00f2fe';

            if (hasRemoteRecord) {
                if (isOutdated) {
                    actionBadgeHtml = '⚠️ 变更';
                    actionBadgeBg = 'rgba(245, 158, 11, 0.12)';
                    actionBadgeColor = '#f59e0b';
                } else if (noUpdateSupport) {
                    actionBadgeHtml = '⚠️ 新建';
                    actionBadgeBg = 'rgba(251, 191, 36, 0.1)';
                    actionBadgeColor = '#fbbf24';
                } else {
                    actionBadgeHtml = '🔄 更新';
                    actionBadgeBg = 'rgba(187, 134, 252, 0.12)';
                    actionBadgeColor = '#bb86fc';
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
                    coverBadgeHtml = `<span title="${cov.tip}" style="cursor:help;font-size:0.62rem;padding:1px 5px;border-radius:4px;background:rgba(239,68,68,0.12);color:#f87171;border:1px solid rgba(239,68,68,0.28);font-weight:600;display:inline-flex;align-items:center;gap:2px;white-space:nowrap;flex-shrink:0;">🖼️ ${cov.label}</span>`;
                } else if (cov.tier === 'recommended') {
                    coverBadgeHtml = `<span title="${cov.tip}" style="cursor:help;font-size:0.62rem;padding:1px 5px;border-radius:4px;background:rgba(56,189,248,0.1);color:#38bdf8;border:1px solid rgba(56,189,248,0.22);font-weight:500;display:inline-flex;align-items:center;gap:2px;white-space:nowrap;flex-shrink:0;">🖼️ ${cov.label}</span>`;
                }
            }

            const rawRemoteId = String(record?.remote_article_id || '');
            const displayRemoteId = rawRemoteId.length > 16
                ? `${rawRemoteId.slice(0, 8)}...${rawRemoteId.slice(-6)}`
                : rawRemoteId;

            return `
            <div class="glass-panel" style="padding: 8px 12px; border-radius: 8px; border: 1px solid ${hasRemoteRecord ? (isOutdated ? 'rgba(245, 158, 11, 0.45)' : 'rgba(187, 134, 252, 0.35)') : (p.isReady ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255,255,255,0.06)')}; display: flex; flex-direction: column; gap: 6px; opacity: ${p.isReady ? '1' : '0.78'}; background: ${hasRemoteRecord ? (isOutdated ? 'rgba(245, 158, 11, 0.05)' : 'rgba(187, 134, 252, 0.04)') : (p.isReady ? 'rgba(0, 255, 136, 0.02)' : 'rgba(255,255,255,0.01)')};">
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 9px; min-width: 0;">
                        <input type="checkbox" value="${p.id}" class="syndicate-platform-checkbox" ${p.isReady ? (p.isChecked ? 'checked' : '') : 'disabled'} style="accent-color: var(--accent-secondary); width: 15px; height: 15px; cursor: ${p.isReady ? 'pointer' : 'not-allowed'}; flex-shrink: 0;">
                        <div style="display: flex; align-items: center; gap: 6px; min-width: 0; flex-wrap: nowrap;">
                            <span style="font-size: 0.84rem; font-weight: 600; color: ${p.isReady ? '#fff' : 'var(--text-dim)'}; display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                <span>${channelIcon}</span>
                                <span>${p.name}</span>
                            </span>
                            <span title="${slaTip}" style="cursor: help; font-size: 0.72rem; line-height: 1; opacity: ${p.isReady ? '0.9' : '0.6'};" flex-shrink: 0;">${slaIcon}</span>
                            <span title="${credTip}" style="cursor: help; font-size: 0.7rem; line-height: 1; flex-shrink: 0;">${credIcon}</span>
                            ${coverBadgeHtml}
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; flex-shrink: 0;">
                        ${p.isReady ? `
                            <span title="${actionBadgeHtml}" style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; white-space: nowrap; background: ${actionBadgeBg}; color: ${actionBadgeColor}; border: 1px solid ${actionBadgeColor}44; font-weight: 600;">${actionBadgeHtml}</span>
                            <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="修改渠道凭据或配置" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.14); color: #fff; border-radius: 5px; padding: 2px 6px; font-size: 0.68rem; cursor: pointer; line-height: 1.2;">⚙️</button>
                        ` : `
                            <button type="button" onclick="window.goToPluginConfig('${p.id}', 'publisher')" title="${credTip} - 前往配置" style="background: rgba(0, 242, 255, 0.12); border: 1px solid rgba(0, 242, 255, 0.3); color: var(--neon-cyan, #00f2fe); border-radius: 5px; padding: 2px 6px; font-size: 0.68rem; cursor: pointer; line-height: 1.2;">⚙️</button>
                        `}
                    </div>
                </div>
                ${hasRemoteRecord ? `
                    <div style="padding-top: 6px; border-top: 1px dashed rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 0.68rem; color: var(--text-dim); min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 6px; min-width: 0; flex: 1; overflow: hidden; white-space: nowrap;">
                            <span style="display: inline-flex; align-items: center; gap: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                <span style="opacity: 0.85;">🆔 ID:</span>
                                <code title="完整对端 ID: ${rawRemoteId} (点击可复制)" onclick="if(navigator.clipboard){navigator.clipboard.writeText('${rawRemoteId}');if(window.showToast)window.showToast('已复制对端 ID','success');}" style="cursor: pointer; background: rgba(255,255,255,0.06); padding: 1px 4px; border-radius: 3px; font-family: monospace; user-select: all; border: 1px solid rgba(255,255,255,0.1);">${displayRemoteId}</code>
                            </span>
                            ${remoteUrl ? `<a href="${remoteUrl}" target="_blank" style="color: #00f2fe; text-decoration: none; flex-shrink: 0; display: inline-flex; align-items: center; gap: 2px;" title="在新标签页中打开对端文章">🔗 对端文章 ↗</a>` : ''}
                        </div>
                        <div style="display: flex; align-items: center; gap: 4px; flex-shrink: 0;">
                            <button type="button" onclick="window.deleteRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}', '${(record?.lang_code || '').replace(/'/g, "\\'")}')" style="background: rgba(255, 77, 79, 0.15); border: 1px solid rgba(255, 77, 79, 0.35); color: #ff4d4f; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer; white-space: nowrap; height: 20px; display: inline-flex; align-items: center; line-height: 1;" title="从对端平台下架删除此文章">🗑️ 下架</button>
                            <button type="button" onclick="window.unlinkRemoteArticle('${relPath.replace(/'/g, "\\'")}', '${p.id}', '${(record?.lang_code || '').replace(/'/g, "\\'")}')" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #aaa; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; cursor: pointer; white-space: nowrap; height: 20px; display: inline-flex; align-items: center; line-height: 1;" title="仅在本地解绑指纹映射，不删除对端文章">🔗 解绑</button>
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
        if (typeof window.onSyndicateCoverLangChange === 'function') {
            window.onSyndicateCoverLangChange(selectedLang);
        }
    };
})();
