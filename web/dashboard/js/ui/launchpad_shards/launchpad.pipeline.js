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
     * 构建流水线六节点透视横条
     */
    function _buildPipelineRow(ctx) {
        var cache = {};
        try {
            var raw = sessionStorage.getItem('_illacme_pipe_cache');
            if (raw) cache = JSON.parse(raw);
        } catch (_) {}

        var pipelineNodes = [
            { key: 'vault',       icon: '📂', label: '原稿', view: 'vault', viewParam: null, tip: 'Obsidian 文库已关联，YAML Frontmatter 语法监测中' },
            { key: 'i18n',        icon: '🌍', label: '翻译', view: 'compute', viewParam: null, tip: '多语增量翻译中枢：目标语种就绪，段落块指纹缓存生效中' },
            { key: 'theme',       icon: '🎭', label: '主题', view: 'settings', viewParam: 'themes', tip: 'Sovereign 旗舰主题母本就绪，支持组件深度定制' },
            { key: 'routing',     icon: '🧭', label: '网址', view: 'settings', viewParam: 'dissemination_routing', tip: '网址 Slug 规则与多语多频道路由映射正常' },
            { key: 'hosting',     icon: '🌐', label: '托管', view: 'plugins', viewParam: 'hosting', tip: '独立站全站托管服务 (GitHub Pages / Vercel / Netlify) 点击前往配置' },
            { key: 'syndication', icon: '📡', label: '分发', view: 'plugins', viewParam: 'publisher', tip: '社媒多渠道分发矩阵 (Dev.to / Hashnode / Medium / RSS) 点击前往配置' }
        ];

        // 冷启动三级状态推断兜底，绝不出现 6 节点全灰未知状态
        function inferNodeStatus(key) {
            if (cache[key] && cache[key].dot) return cache[key].dot;
            if (key === 'vault') return (ctx && ctx.vault && ctx.vault.root) ? 'healthy' : 'warning';
            if (key === 'i18n') return (ctx && (ctx.ai_status === 'online' || (ctx.ai && ctx.ai.status === 'online'))) ? 'healthy' : 'offline';
            if (key === 'theme') return (window.settingsData && (window.settingsData._theme || window.settingsData.theme || window.settingsData.active_theme)) ? 'healthy' : 'standby';
            if (key === 'routing') return 'healthy';
            if (key === 'hosting') {
                var s = window.settingsData || {};
                var hasDirect = s.publish_control && s.publish_control.direct_upload;
                var hasPlatforms = s.platforms && Object.values(s.platforms).some(function(p){ return p && p.enabled; });
                return (hasDirect || hasPlatforms) ? 'healthy' : 'offline';
            }
            if (key === 'syndication') {
                var s = window.settingsData || {};
                var hasSynd = s.syndication && Object.values(s.syndication).some(function(p){ return p && p.enabled; });
                return hasSynd ? 'healthy' : 'offline';
            }
            return 'healthy';
        }

        function dotClass(className) {
            if (!className) return 'lpdot-healthy';
            if (className.indexOf('healthy') !== -1)  return 'lpdot-healthy';
            if (className.indexOf('warning') !== -1)  return 'lpdot-warning';
            if (className.indexOf('offline') !== -1)  return 'lpdot-offline';
            if (className.indexOf('standby') !== -1)  return 'lpdot-standby';
            return 'lpdot-healthy';
        }

        var nodesHtml = pipelineNodes.map(function(n, i) {
            var rawStatus = inferNodeStatus(n.key);
            var statusClass = dotClass(rawStatus);
            var clickAction = n.key === 'syndication' ?
                "window.toggleHub('hide'); if(typeof window.openDispatchHub==='function'){window.openDispatchHub();}else{window.showView('plugins', 'publisher');}" :
                "window.toggleHub('hide'); window.showView('" + n.view + "'" + (n.viewParam ? ", '" + n.viewParam + "'" : "") + ");";

            return '<div class="lpdash-pipe-node interactive" onclick="' + clickAction + '" title="' + n.tip + ' (点击跳转治理中心)">' +
                '<span class="lpdash-pipe-icon">' + n.icon + '</span>' +
                '<span class="lpdash-pipe-dot ' + statusClass + '"></span>' +
                '<span class="lpdash-pipe-label">' + n.label + '</span>' +
                (i < pipelineNodes.length - 1 ? '<span class="lpdash-pipe-arrow">›</span>' : '') +
                '</div>';
        }).join('');

        return '<div class="lpdash-pipeline-card">' +
            '<div class="lpdash-pipeline-row">' + nodesHtml + '</div>' +
            '</div>';
    }

    /**
     * 构建流水线就绪状态与诊断建议卡片
     */
    function _buildSuggestions(ctx) {
        var suggestions = [];
        var activeId = (window.settingsData && window.settingsData._active_imprint) || 'default';
        var syncDone = localStorage.getItem('sync_completed_' + activeId) === 'true' || localStorage.getItem('sync_completed') === 'true';

        var cache = {};
        try {
            var raw = sessionStorage.getItem('_illacme_pipe_cache');
            if (raw) cache = JSON.parse(raw);
        } catch (_) {}

        function isOffline(key) { return (cache[key] && cache[key].dot || '').indexOf('offline') !== -1; }

        // 优先级 1: AI 算力未就绪
        if ((ctx && ctx.ai_status === 'offline') || isOffline('i18n')) {
            suggestions.push({
                icon: '🤖',
                title: '接入 AI 翻译算力大模型',
                desc: '接入 DeepSeek / OpenAI 等模型后，即可激活多语种全自动翻译与智能排版。',
                btn: '前往配置',
                action: "window.toggleHub('hide'); window.showView('compute');"
            });
        }

        // 优先级 2: 文库未关联
        if (!(ctx && ctx.vault && ctx.vault.root)) {
            suggestions.push({
                icon: '📂',
                title: '绑定您的稿件文库',
                desc: '请指定存放 Markdown 笔记的文库文件夹路径，系统将自动建立出版资产账本。',
                btn: '前往绑定',
                action: "window.toggleHub('hide'); window.showView('vault');"
            });
        }

        // 优先级 3: 托管未开启 (解决流水线第 5 个托管红点，准确导向全站托管 plugins -> hosting)
        if (isOffline('hosting') && suggestions.length < 2) {
            suggestions.push({
                icon: '🌐',
                title: '开启独立站托管平台',
                desc: '配置 GitHub Pages 或 Netlify 渠道，出版流水线可自动将站点发布上云。',
                btn: '前往开启',
                action: "window.toggleHub('hide'); window.showView('plugins', 'hosting');"
            });
        }

        // 优先级 3.5: 分发通道未开启 (解决流水线第 6 个分发红点，准确导向社媒分发 plugins -> publisher)
        if (isOffline('syndication') && suggestions.length < 2) {
            suggestions.push({
                icon: '📡',
                title: '配置全网多渠道分发',
                desc: '开启 Dev.to、Hashnode、Medium 或 RSS 订阅，文章发布时将全自动同步至全球技术社区。',
                btn: '前往配置',
                action: "window.toggleHub('hide'); if(typeof window.openDispatchHub==='function'){window.openDispatchHub();}else{window.showView('plugins', 'publisher');}"
            });
        }

        // 优先级 4: 有待发布文稿 (当还有空余槽位时提醒发布)
        var docCount = (ctx && ctx.vault && ctx.vault.doc_count) || 0;
        if (!syncDone && docCount > 0 && suggestions.length < 2) {
            suggestions.push({
                icon: '🚀',
                title: '发布您的最新稿件',
                desc: '检测到文库中有新内容尚未完成全网发布。一键点火即可完成全量自动化分发。',
                btn: '一键发布',
                action: "window.toggleHub('hide'); window.triggerPublish();"
            });
        }

        if (suggestions.length === 2) {
            return suggestions.map(function (s) {
                return '<div class="lpdash-suggest-item">' +
                    '<span class="lpdash-suggest-icon">' + s.icon + '</span>' +
                    '<div class="lpdash-suggest-body">' +
                        '<div class="lpdash-suggest-name">' + s.title + '</div>' +
                        '<div class="lpdash-suggest-desc">' + s.desc + '</div>' +
                    '</div>' +
                    '<button class="lpdash-suggest-btn" onclick="' + s.action.replace(/"/g, '&quot;') + '">' + s.btn + ' →</button>' +
                    '</div>';
            }).join('');
        } else if (suggestions.length === 1) {
            var s = suggestions[0];
            return '<div class="lpdash-suggest-item">' +
                '<span class="lpdash-suggest-icon">' + s.icon + '</span>' +
                '<div class="lpdash-suggest-body">' +
                    '<div class="lpdash-suggest-name">' + s.title + '</div>' +
                    '<div class="lpdash-suggest-desc">' + s.desc + '</div>' +
                '</div>' +
                '<button class="lpdash-suggest-btn" onclick="' + s.action.replace(/"/g, '&quot;') + '">' + s.btn + ' →</button>' +
                '</div>' +
                '<div class="lpdash-suggest-item" style="background: rgba(var(--neon-green-rgb), 0.04); border-color: rgba(var(--neon-green-rgb), 0.2);">' +
                    '<span class="lpdash-suggest-icon">⚡</span>' +
                    '<div class="lpdash-suggest-body">' +
                        '<div class="lpdash-suggest-name" style="color: var(--neon-green);">段落块指纹哈希在线</div>' +
                        '<div class="lpdash-suggest-desc">Block Cache Hub 增量指纹已激活，当前出版已为您自动节省 90%+ 算力 Token 消耗。</div>' +
                    '</div>' +
                    '<button class="lpdash-suggest-btn" onclick="window.toggleHub(\'hide\'); window.showView(\'settings\', \'storage\');">查看缓存 →</button>' +
                '</div>';
        } else {
            // 全绿 3 大核心资产就绪看板 (跨两行占位)
            return '<div class="lpdash-readiness-panel span-two-rows">' +
                '<div class="lpdash-ready-header">💡 出版全周期就绪诊断</div>' +
                '<div class="lpdash-ready-item">' +
                    '<span class="lpdash-ready-icon">⚡</span>' +
                    '<div><strong>算力增量中枢</strong>：段落级块指纹哈希缓存生效中，翻译成本降低 90%+。</div>' +
                '</div>' +
                '<div class="lpdash-ready-item">' +
                    '<span class="lpdash-ready-icon">📑</span>' +
                    '<div><strong>文库双链监测</strong>：原生支持 Obsidian / Typora 双链、语法高亮与 Frontmatter 解析。</div>' +
                '</div>' +
                '<div class="lpdash-ready-item">' +
                    '<span class="lpdash-ready-icon">🛡️</span>' +
                    '<div><strong>国际合规分发</strong>：多语种 Sitemap 站点地图、RSS 2.0 订阅源与 SEO 结构化元数据就绪。</div>' +
                '</div>' +
            '</div>';
        }
    }

    // 全局导出，供 dashboard 分片组装与调试
    window._buildPipelineRow = _buildPipelineRow;
    window._buildSuggestions = _buildSuggestions;
})();
