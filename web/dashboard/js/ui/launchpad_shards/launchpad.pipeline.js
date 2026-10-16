/**
 * 📊 [V120.0] Illacme Plenipes - Launchpad Pipeline & Diagnostics Shard
 * 职责：流水线六节点全景透视、冷启动状态智能推断与动态出版就绪诊断卡片
 * 承载功能：
 * 1. 原稿、翻译、主题、网址、托管、分发六节点流水线卡片构建与交互跳转
 * 2. 状态推断兜底 (冷启动防 6 节点全灰未知状态)
 * 3. 动态诊断建议 (算力/文库/托管/分发各优先级推荐或三核心就绪全绿看板)
 */

(function () {
    /**
     * 🌐 出版产出与发行成果多语言字典
     */
    var PIPELINE_I18N = {
        zh: {
            title: '🚀 出版产出与发行成果',
            readiness_header: '💡 智能出版就绪诊断与待办处置',
            books_val: '本出版物',
            books_size_prefix: '体积 ',
            hosting_val: '次网站发布',
            hosting_rate_prefix: '成功率 ',
            synd_val: '次社媒分发',
            synd_rate_prefix: '成功率 ',
            dot_healthy: '运行健康',
            dot_warning: '存在局部告警',
            dot_error: '存在较多异常',
            dot_standby: '就绪待命中',
            dot_books_ready: '出版物已入架',
            dot_books_empty: '书架待命中'
        },
        en: {
            title: '🚀 Publishing Output & Deliverables',
            readiness_header: '💡 Publishing Readiness & Actions',
            books_val: 'Publications',
            books_size_prefix: 'Size: ',
            hosting_val: 'Hosted Deploys',
            hosting_rate_prefix: 'Success: ',
            synd_val: 'Social Dispatches',
            synd_rate_prefix: 'Success: ',
            dot_healthy: 'Healthy',
            dot_warning: 'Warning',
            dot_error: 'Error',
            dot_standby: 'Standby',
            dot_books_ready: 'Books Ready',
            dot_books_empty: 'Bookshelf Empty'
        }
    };

    function _getPipelineLang() {
        var lang = (window.currentLocale || (window.settingsData && window.settingsData.ui_lang) || 'zh').toLowerCase();
        return lang.indexOf('en') !== -1 ? 'en' : 'zh';
    }

    function _getPipelineTitle() {
        var lang = _getPipelineLang();
        return (PIPELINE_I18N[lang] || PIPELINE_I18N.zh).title;
    }

    /**
     * 构建出版产出与发行成果卡片 (书架出版物数量与体积、网站托管发布次数与成功率、社交媒体分发次数与成功率)
     */
    function _buildPipelineRow(ctx, preferredLang) {
        var lang = preferredLang || _getPipelineLang();
        var i18n = PIPELINE_I18N[lang] || PIPELINE_I18N.zh;

        var stats = (ctx && ctx.stats) || {};
        var booksCount = (typeof stats.shelf_books_count === 'number')
            ? stats.shelf_books_count
            : ((typeof window._dispatchShelfCount === 'number') ? window._dispatchShelfCount : 0);
        var shelfSize = stats.shelf_size_display || window._dispatchShelfSize || (booksCount > 0 ? '0 KB' : '0 B');

        var hostingDeployCount = (typeof stats.hosting_deploy_count === 'number')
            ? stats.hosting_deploy_count
            : ((typeof window._hostingDeployTotal === 'number') ? window._hostingDeployTotal : 0);
        var hostingRate = stats.hosting_success_rate || window._hostingSuccessRate || '100%';

        var syndCount = (typeof stats.syndication_count === 'number')
            ? stats.syndication_count
            : (window._dispatchSummary && typeof window._dispatchSummary.total_syndicated === 'number' ? window._dispatchSummary.total_syndicated : 0);
        var syndRate = stats.syndication_success_rate || (window._dispatchSummary && window._dispatchSummary.success_rate) || window._syndSuccessRate || '100%';

        var booksDesc = i18n.books_size_prefix + shelfSize;
        var hostingDesc = i18n.hosting_rate_prefix + hostingRate;
        var syndDesc = i18n.synd_rate_prefix + syndRate;

        function _getHealthDot(count, rateStr, countZeroTitle) {
            if (count === 0) return { cls: 'lpdot-standby', title: countZeroTitle };
            var m = String(rateStr || '').match(/([0-9.]+)/);
            var val = m ? parseFloat(m[1]) : 100;
            if (val < 90) return { cls: 'lpdot-offline', title: i18n.dot_error + ' (' + rateStr + ')' };
            if (val < 98) return { cls: 'lpdot-warning', title: i18n.dot_warning + ' (' + rateStr + ')' };
            return { cls: 'lpdot-healthy', title: i18n.dot_healthy + ' (' + rateStr + ')' };
        }

        var booksDot = booksCount > 0 ? { cls: 'lpdot-healthy', title: i18n.dot_books_ready } : { cls: 'lpdot-standby', title: i18n.dot_books_empty };
        var hostingDot = _getHealthDot(hostingDeployCount, hostingRate, i18n.dot_standby);
        var syndDot = _getHealthDot(syndCount, syndRate, i18n.dot_standby);

        return '<div class="lpdash-pipeline-card lpdash-delta-card">' +
            '<div class="lpdash-delta-grid">' +
                // 1. 电子出版书架数量与文件体积
                '<div class="lpdash-delta-pill interactive" onclick="window.toggleHub(\'hide\'); window.showView(\'tasks\', \'shelf\');" title="点击进入电子出版书架">' +
                    '<span class="lpdash-delta-icon">📚</span>' +
                    '<div class="lpdash-delta-info">' +
                        '<div class="lpdash-delta-val">' + booksCount + ' ' + i18n.books_val + '<span class="lpdash-pipe-dot ' + booksDot.cls + '" title="' + booksDot.title + '"></span></div>' +
                        '<div class="lpdash-delta-lbl" title="' + booksDesc + '">' + booksDesc + '</div>' +
                    '</div>' +
                '</div>' +
                // 2. 网站托管发布次数与成功率
                '<div class="lpdash-delta-pill interactive" onclick="window.toggleHub(\'hide\'); window.showView(\'tasks\', \'hosting\');" title="点击查看网站托管发布">' +
                    '<span class="lpdash-delta-icon">🌐</span>' +
                    '<div class="lpdash-delta-info">' +
                        '<div class="lpdash-delta-val">' + hostingDeployCount + ' ' + i18n.hosting_val + '<span class="lpdash-pipe-dot ' + hostingDot.cls + '" title="' + hostingDot.title + '"></span></div>' +
                        '<div class="lpdash-delta-lbl" title="' + hostingDesc + '">' + hostingDesc + '</div>' +
                    '</div>' +
                '</div>' +
                // 3. 社交媒体分发次数与成功率
                '<div class="lpdash-delta-pill interactive" onclick="window.toggleHub(\'hide\'); window.showView(\'tasks\', \'dispatch\');" title="点击查看社交媒体分发">' +
                    '<span class="lpdash-delta-icon">📡</span>' +
                    '<div class="lpdash-delta-info">' +
                        '<div class="lpdash-delta-val">' + syndCount + ' ' + i18n.synd_val + '<span class="lpdash-pipe-dot ' + syndDot.cls + '" title="' + syndDot.title + '"></span></div>' +
                        '<div class="lpdash-delta-lbl" title="' + syndDesc + '">' + syndDesc + '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '</div>';
    }

    // 静默预取分发与托管真实统计
    (async function _prefetchOutputStats() {
        if (typeof window.apiFetch !== 'function') return;
        try {
            var bp = await window.apiFetch('/api/bindery/shelf');
            if (bp && typeof bp.count === 'number') window._dispatchShelfCount = bp.count;
            if (bp && bp.total_size_display) window._dispatchShelfSize = bp.total_size_display;
        } catch (_) {}
        try {
            var dp = await window.apiFetch('/api/dispatch/overview');
            if (dp && dp.summary) {
                window._dispatchSummary = dp.summary;
                if (dp.summary.success_rate) window._syndSuccessRate = dp.summary.success_rate;
            }
            if (dp && typeof dp.hosting_total === 'number') window._hostingDeployTotal = dp.hosting_total;
        } catch (_) {}
        try {
            var hp = await window.apiFetch('/api/dispatch/hosting/overview');
            if (hp && hp.pagination && typeof hp.pagination.total === 'number') {
                window._hostingDeployTotal = hp.pagination.total;
            }
        } catch (_) {}
    })();

    /**
     * 构建流水线就绪状态与诊断建议卡片 (真实成果感知与发布中心路由彻底对齐)
     */
    function _buildSuggestions(ctx) {
        var suggestions = [];
        var activeId = (window.settingsData && window.settingsData._active_imprint) || 'default';
        var syncDone = false;
        try {
            syncDone = localStorage.getItem('sync_completed_' + activeId) === 'true' || localStorage.getItem('sync_completed') === 'true';
        } catch (_) {}

        var cache = {};
        try {
            var raw = sessionStorage.getItem('_illacme_pipe_cache');
            if (raw) cache = JSON.parse(raw);
        } catch (_) {}

        function isOffline(key) { return (cache[key] && cache[key].dot || '').indexOf('offline') !== -1; }

        var stats = (ctx && ctx.stats) || {};
        var hostingDeployCount = (typeof stats.hosting_deploy_count === 'number')
            ? stats.hosting_deploy_count
            : ((typeof window._hostingDeployTotal === 'number') ? window._hostingDeployTotal : 0);
        var hostingRate = stats.hosting_success_rate || window._hostingSuccessRate || '100%';
        var hostingRateVal = parseFloat(String(hostingRate).replace('%', '')) || 100;

        var syndCount = (typeof stats.syndication_count === 'number')
            ? stats.syndication_count
            : (window._dispatchSummary && typeof window._dispatchSummary.total_syndicated === 'number' ? window._dispatchSummary.total_syndicated : 0);
        var syndRate = stats.syndication_success_rate || (window._dispatchSummary && window._dispatchSummary.success_rate) || window._syndSuccessRate || '100%';
        var syndRateVal = parseFloat(String(syndRate).replace('%', '')) || 100;

        // 优先级 1: AI 算力未就绪
        if ((ctx && ctx.ai_status === 'offline') || isOffline('i18n')) {
            suggestions.push({
                icon: '🤖', title: '接入 AI 翻译算力大模型',
                desc: '接入 DeepSeek / OpenAI 等模型后，即可激活多语种全自动翻译与智能排版。',
                btn: '前往配置', action: "window.toggleHub('hide'); window.showView('compute');"
            });
        }

        // 优先级 2: 文库未关联
        if (!(ctx && ctx.vault && ctx.vault.root)) {
            suggestions.push({
                icon: '📂', title: '绑定您的稿件文库',
                desc: '请指定存放 Markdown 笔记的文库文件夹路径，系统将自动建立出版资产账本。',
                btn: '前往绑定', action: "window.toggleHub('hide'); window.showView('vault');"
            });
        }

        // 优先级 3: 托管状态感知 (对齐发布中心 hosting 标签)
        if (suggestions.length < 2) {
            if (hostingDeployCount > 0 && hostingRateVal < 98) {
                suggestions.push({
                    icon: '🌐', title: '排查网站托管部署告警',
                    desc: '近期部署成功率为 ' + hostingRate + '，建议查验控制台流水与平台授权。',
                    btn: '查验部署', action: "window.toggleHub('hide'); window.showView('tasks', 'hosting');"
                });
            } else if (hostingDeployCount === 0 && isOffline('hosting')) {
                suggestions.push({
                    icon: '🌐', title: '开启独立站托管平台',
                    desc: '配置 GitHub Pages 或 Netlify 渠道，流水线可自动将站点发布上云。',
                    btn: '前往开启', action: "window.toggleHub('hide'); window.showView('tasks', 'hosting');"
                });
            }
        }

        // 优先级 3.5: 分发状态感知 (对齐发布中心 dispatch 标签)
        if (suggestions.length < 2) {
            if (syndCount > 0 && syndRateVal < 98) {
                suggestions.push({
                    icon: '📡', title: '自愈社交媒体分发通道',
                    desc: '近期社媒分发成功率为 ' + syndRate + '，存在待重试死信，点击查看分发账本。',
                    btn: '查验分发', action: "window.toggleHub('hide'); window.showView('tasks', 'dispatch');"
                });
            } else if (syndCount === 0 && isOffline('syndication')) {
                suggestions.push({
                    icon: '📡', title: '配置全网多渠道分发',
                    desc: '开启 Dev.to、Hashnode 或 Medium 渠道，文章发布时全自动同步社区。',
                    btn: '前往配置', action: "window.toggleHub('hide'); window.showView('tasks', 'dispatch');"
                });
            }
        }

        // 优先级 4: 有待发布文稿
        var docCount = (ctx && ctx.vault && ctx.vault.doc_count) || 0;
        if (!syncDone && docCount > 0 && suggestions.length < 2) {
            suggestions.push({
                icon: '🚀', title: '发布您的最新稿件',
                desc: '检测到文库中有新内容尚未完成全网发布。一键点火即可完成全量自动化分发。',
                btn: '一键发布', action: "window.toggleHub('hide'); window.triggerPublish();"
            });
        }

        function _renderSuggestItem(s) {
            return '<div class="lpdash-suggest-item">' +
                '<span class="lpdash-suggest-icon">' + s.icon + '</span>' +
                '<div class="lpdash-suggest-body"><div class="lpdash-suggest-name">' + s.title + '</div><div class="lpdash-suggest-desc">' + s.desc + '</div></div>' +
                '<button class="lpdash-suggest-btn" onclick="' + s.action.replace(/"/g, '&quot;') + '">' + s.btn + ' →</button>' +
                '</div>';
        }

        if (suggestions.length >= 2) {
            return suggestions.slice(0, 2).map(_renderSuggestItem).join('');
        } else if (suggestions.length === 1) {
            return _renderSuggestItem(suggestions[0]) +
                '<div class="lpdash-suggest-item" style="background: rgba(var(--neon-green-rgb), 0.04); border-color: rgba(var(--neon-green-rgb), 0.2);">' +
                    '<span class="lpdash-suggest-icon">⚡</span>' +
                    '<div class="lpdash-suggest-body"><div class="lpdash-suggest-name" style="color: var(--neon-green);">⚡ 智能增量缓存生效中</div>' +
                    '<div class="lpdash-suggest-desc">已开启段落级智能感知，仅对修改文段重新翻译，为您自动节省 90%+ 算力开销与等待时间。</div></div>' +
                    '<button class="lpdash-suggest-btn" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\', \'storage\');">查看缓存 →</button>' +
                '</div>';
        } else {
            // 全绿 3 大核心就绪诊断与行动看板 (跨两行占位)
            var curLang = _getPipelineLang();
            var curI18n = PIPELINE_I18N[curLang] || PIPELINE_I18N.zh;
            return '<div class="lpdash-readiness-panel span-two-rows">' +
                '<div class="lpdash-ready-header">' + (curI18n.readiness_header || '💡 智能出版就绪诊断与待办处置') + '</div>' +
                '<div class="lpdash-ready-item" style="cursor: pointer;" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\', \'storage\');">' +
                '<span class="lpdash-ready-icon">⚡</span>' +
                '<div style="flex: 1; min-width: 0;"><strong>智能增量缓存</strong>：仅翻译文稿修改段落，自动节省 90%+ 算力成本与发布耗时。</div>' +
                '<button class="lpdash-ready-btn" style="flex-shrink: 0; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--white-15); background: var(--white-05); color: var(--accent-secondary); cursor: pointer;">缓存中枢 →</button>' +
                '</div>' +
                '<div class="lpdash-ready-item" style="cursor: pointer;" onclick="window.toggleHub(\'hide\'); window.showView(\'vault\');">' +
                    '<span class="lpdash-ready-icon">🎨</span>' +
                    '<div style="flex: 1; min-width: 0;"><strong>封面与视觉装帧</strong>：已接入极速商用图库与动态 OG 卡片，支持一键配图。</div>' +
                    '<button class="lpdash-ready-btn" style="flex-shrink: 0; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--white-15); background: var(--white-05); color: var(--accent-secondary); cursor: pointer;">配图工坊 →</button>' +
                '</div>' +
                '<div class="lpdash-ready-item" style="cursor: pointer;" onclick="window.toggleHub(\'hide\'); window.showView(\'tasks\', \'dispatch\');">' +
                    '<span class="lpdash-ready-icon">🛡️</span>' +
                    '<div style="flex: 1; min-width: 0;"><strong>国际物权全网分发</strong>：多语种 Sitemap、RSS 2.0 订阅源与社媒渠道矩阵就绪。</div>' +
                    '<button class="lpdash-ready-btn" style="flex-shrink: 0; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--white-15); background: var(--white-05); color: var(--accent-secondary); cursor: pointer;">分发拓扑 →</button>' +
                '</div>' +
            '</div>';
        }
    }

    // 全局导出，供 dashboard 分片组装与调试
    window._buildPipelineRow = _buildPipelineRow;
    window._buildSuggestions = _buildSuggestions;
    window.getPipelineTitle = _getPipelineTitle;
    window.PIPELINE_I18N = PIPELINE_I18N;
})();
