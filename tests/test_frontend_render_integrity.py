import subprocess
from pathlib import Path

def test_frontend_render_runtime_and_dom_integrity():
    """
    🛡️ 前端渲染函数运行时沙箱与 DOM 拓扑完备性门禁测试 (Rule 7)
    拦截场景：
    1. 函数内部使用未声明变量抛出 ReferenceError (如 matchingNodeIds is not defined)
    2. 模板字符串替换时误删外层关键容器 (如 div.node-unit, div.node-grid)
    3. 全局命名空间与事件绑定异常
    """
    runner_script = """
    const fs = require('fs');
    
    // 1. 构造浏览器虚拟上下文
    global.document = {
        getElementById: () => ({ style: {}, classList: { add: ()=>{}, remove: ()=>{} } }),
        querySelectorAll: () => [],
        querySelector: () => null,
        addEventListener: () => {},
        removeEventListener: () => {}
    };
    global.window = {
        settingsData: {
            translation: {
                strategy: 'concurrent',
                primary_node: 'lmstudio_local',
                fallback_node: 'deepseek_v3',
                concurrent_nodes: ['lmstudio_local', 'deepseek_v3'],
                compute_nodes: {
                    'lmstudio_local': { type: 'lmstudio', provider_name: 'LM Studio', enabled: true, protocol_family: 'standard', model: 'qwen2.5' },
                    'deepseek_v3': { type: 'deepseek', provider_name: 'DeepSeek', enabled: true, protocol_family: 'standard', model: 'deepseek-chat' }
                }
            }
        },
        isPluginConfigurable: () => false,
        checkPluginConfiguredStatus: () => ({ class: 'info', style: '', label: 'OK' }),
        ComputeHandlers: {
            syncStrategyBadge: () => {}
        }
    };
    global.apiFetch = async () => ({ config: global.window.settingsData });

    // 2. 加载并执行 plugins.render.pod.js
    const podCode = fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.pod.js', 'utf8');
    eval(podCode);

    const testProtoPlugin = {
        id: 'lmstudio',
        name: 'LM Studio',
        category: 'protocol',
        protocol_family: 'local',
        default_url: 'http://localhost:1234',
        aliases: ['v1'],
        description: 'test'
    };

    // 执行插件卡片渲染
    const podHtml = window.buildPluginPodHtml(testProtoPlugin, 'protocol');
    if (!podHtml || typeof podHtml !== 'string') {
        throw new Error('buildPluginPodHtml failed to return HTML string');
    }
    if (!podHtml.includes('shield-pod') || !podHtml.includes('lmstudio_local')) {
        throw new Error('buildPluginPodHtml DOM topology broken: missing shield-pod or matchingNodeIds');
    }

    // 3. 加载并执行 compute.ui.render.js
    const computeRenderCode = fs.readFileSync('web/dashboard/js/compute/compute.ui.render.js', 'utf8');
    eval(computeRenderCode);

    const fakeContainer = {};
    window.ComputeUI.renderInfrastructureTabImpl(fakeContainer).then(async () => {
        const html = fakeContainer.innerHTML || '';
        if (!html.includes('class="node-grid"')) {
            throw new Error('Compute infrastructure DOM topology broken: missing div.node-grid');
        }
        if (!html.includes('class="node-unit active"')) {
            throw new Error('Compute infrastructure DOM topology broken: missing div.node-unit container');
        }
        if (!html.includes('RACE 竞速') && !html.includes('PRIMARY')) {
            throw new Error('Compute infrastructure DOM topology broken: missing role badge');
        }

        // 4. 加载并执行 route.constants.js 与 route.render.js (Rule 7: Combobox + 内联状态徽标)
        global.window.settingsData._directories = ['Docs', 'Blog'];
        global.window.settingsData._vault_files = [
            { path: 'Docs/1.md' }, { path: 'about.md', title: '关于我们' }
        ];
        global.window.settingsData.route_matrix = [
            { source: 'Docs', prefix: 'docs', target_slot: 'docs' },
            { source: 'about.md', prefix: 'about', target_slot: 'pages' },
            { source: 'MissingSource', prefix: 'missing', target_slot: 'docs' }
        ];

        const routeShardFiles = [
            'web/dashboard/js/route/route_shards/route.i18n.dict.js',
            'web/dashboard/js/route/route_shards/route.style.selector.js',
            'web/dashboard/js/route/route_shards/route.source.options.js',
            'web/dashboard/js/route/route_shards/route.source.picker.js',
            'web/dashboard/js/route/route_shards/route.source.events.js',
            'web/dashboard/js/route/route_shards/route.path.badges.js',
            'web/dashboard/js/route/route_shards/route.constants.js'
        ];
        routeShardFiles.forEach(f => eval(fs.readFileSync(f, 'utf8')));
        const routeRenderCode = fs.readFileSync('web/dashboard/js/route/route.render.js', 'utf8');
        eval(routeRenderCode);

        const routeHtml = window.renderRouteMatrixCategory();
        if (!routeHtml.includes('source-picker-wrap')) {
            throw new Error('Route matrix DOM topology broken: missing source-picker-wrap');
        }
        if (!routeHtml.includes('in-input-badge-container')) {
            throw new Error('Route matrix DOM topology broken: missing in-input-badge-container');
        }
        if (!routeHtml.includes('<datalist id="source-datalist-')) {
            throw new Error('Route matrix DOM topology broken: missing datalist for combobox');
        }
        // 🌲 验证树形制导结构已生效
        if (!routeHtml.includes('📁 Docs (目录)') || !routeHtml.includes('├─') && !routeHtml.includes('└─')) {
            throw new Error('Route matrix tree structure topology missing in datalist options');
        }
        if (routeHtml.includes('source-status-bar')) {
            throw new Error('Legacy source-status-bar should be eliminated');
        }

        // 5. 加载并执行 launchpad.js 引导向导沙箱断言与仪表盘拓扑断言
        global.localStorage = { getItem: () => null, setItem: () => {} };
        global.sessionStorage = { getItem: () => null, setItem: () => {} };
        global.window.settingsData = {
            _imprints: [{ id: 'default', name: '默认出版品牌' }],
            _active_imprint: 'default',
            compliance: { site_url: 'https://example.com' }
        };
        const lpShardFiles = [
            'web/dashboard/js/ui/launchpad_shards/launchpad.onboarding.js',
            'web/dashboard/js/ui/launchpad_shards/launchpad.skeleton.js',
            'web/dashboard/js/ui/launchpad_shards/launchpad.pipeline.js',
            'web/dashboard/js/ui/launchpad_shards/launchpad.dashboard.js',
            'web/dashboard/js/ui/launchpad.js'
        ];
        const launchpadCode = lpShardFiles.map(f => fs.readFileSync(f, 'utf8')).join('\\n');
        const dummyLpArea = {};
        const runLpFn = new Function('window', 'area', 'ctx', launchpadCode + '; _renderOnboarding(area, ctx); return area.innerHTML;');
        const lpHtml = runLpFn(global.window, dummyLpArea, {});
        if (!lpHtml.includes('lpwiz-container') || !lpHtml.includes('lpwiz-step-item') || !lpHtml.includes('lpwiz-step-num sample') || !lpHtml.includes('lpwiz-step-num custom')) {
            throw new Error('Launchpad onboarding DOM topology broken: missing lpwiz-container, lpwiz-step-item, sample or custom step-num');
        }
        if (!lpHtml.includes('官方示范原稿文库') || !lpHtml.includes('增量翻译与极速分发')) {
            throw new Error('Launchpad onboarding core feature descriptions missing in DOM');
        }

        // 6. 验证 Launchpad 仪表盘与三栏合一顶栏 DOM 沙箱
        const dummySkelArea = {};
        const runSkelFn = new Function('window', 'area', launchpadCode + '; _mountLaunchpadSkeleton(area, "dashboard"); return area.innerHTML;');
        const skelHtml = runSkelFn(global.window, dummySkelArea);
        if (!skelHtml.includes('hub-top-trio-bar') || !skelHtml.includes('hub-brand-badge') || !skelHtml.includes('hub-mode-capsule')) {
            throw new Error('Launchpad skeleton DOM missing hub-top-trio-bar, hub-brand-badge, or capsule');
        }

        const dummyDashArea = {};
        const runDashFn = new Function('window', 'area', 'ctx', launchpadCode + '; _renderDashboard(area, ctx); return area.innerHTML;');
        const dashHtml = runDashFn(global.window, dummyDashArea, { vault: { doc_count: 33, root: '/test/vault' }, i18n: { targets: ['en'] } });
        if (!dashHtml.includes('lpdash-container') || !dashHtml.includes('lpdash-stats-strip') || !dashHtml.includes('primary-cta') || !dashHtml.includes('lpdash-quick-actions')) {
            throw new Error('Launchpad dashboard DOM missing lpdash-container, stats, primary-cta, or quick-actions');
        }
        if (!dashHtml.includes('点击刷新检测') || !dashHtml.includes('按 Esc 关闭工作台')) {
            throw new Error('Launchpad dashboard missing streamlined footer actions');
        }
        // 7. 验证 loc.link_doctor.render.js 与 loc.blocks.render.js (Link Doctor 跨主题体检沙箱)
        const linkDoctorCode = fs.readFileSync('web/dashboard/js/localization/render_shards/loc.link_doctor.render.js', 'utf8');
        eval(linkDoctorCode);
        const blocksRenderCode = fs.readFileSync('web/dashboard/js/localization/render_shards/loc.blocks.render.js', 'utf8');
        eval(blocksRenderCode);

        const cardHtml = window.renderLinkDoctorCard();
        if (!cardHtml.includes('link-doctor-card-container') || !cardHtml.includes('btn-trigger-link-doctor')) {
            throw new Error('Link Doctor card DOM missing container or trigger button');
        }
        if (!cardHtml.includes('Universal 通用') || !cardHtml.includes('Nextra (Next.js)') || !cardHtml.includes('Starlight (Astro)')) {
            throw new Error('Link Doctor card missing SSG theme badges');
        }

        // 8. 验证 platforms.sensing_judger.js 与 plugins.render.cards.js 凭据判定与算力寻路沙箱
        const judgerCode = fs.readFileSync('web/dashboard/js/plugins/platforms_shards/platforms.sensing_judger.js', 'utf8');
        eval(judgerCode);
        const cardsCode = fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.cards.js', 'utf8');
        eval(cardsCode);

        // 8.1 匿名免配图床 (Catbox)
        const rCat = window.isPluginCredentialReady('catbox', 'image_hosting', {});
        if (!rCat.ready || rCat.label !== '免配即用') throw new Error('Catbox anonymous readiness failed');

        // 8.2 阿里云 OSS access_key_id / access_key_secret
        const rOSS = window.isPluginCredentialReady('aliyun_oss', 'image_hosting', { access_key_id: 'LTAI5t', access_key_secret: 'sec' });
        if (!rOSS.ready || !rOSS.label.includes('就绪')) throw new Error('Aliyun OSS credential readiness failed');

        // 8.3 微信公众号 app_id / app_secret
        const rWX = window.isPluginCredentialReady('wechat', 'publisher', { app_id: 'wx123', app_secret: 'sec' });
        if (!rWX.ready || !rWX.label.includes('就绪')) throw new Error('WeChat credential readiness failed');

        // 8.4 算力驱动路由感知
        window.settingsData.translation = {
            compute_nodes: {
                'deepseek_node': { type: 'deepseek', api_key: 'sk-123', enabled: true }
            }
        };
        const rProto = window.checkPluginConfiguredStatus({ id: 'deepseek', category: 'protocol', is_enabled: true });
        if (!rProto.label.includes('就绪')) throw new Error('Protocol compute node status routing failed');

        // 9. 验证 design.studio.js 提供商渲染与分类过滤器真实调用 (Rule 7)
        const designStudioCode = fs.readFileSync('web/dashboard/js/design/design.studio.js', 'utf8');
        eval(designStudioCode);
        if (typeof window.buildDesignProvidersHtml !== 'function') throw new Error('buildDesignProvidersHtml is not defined');
        if (typeof window.filterDesignProviders !== 'function') throw new Error('filterDesignProviders is not defined on window');
        
        const designHtml = window.buildDesignProvidersHtml();
        if (!designHtml.includes('id="provider-category-filter"') || !designHtml.includes('id="provider-cards-grid"')) {
            throw new Error('Design providers DOM topology missing filter or cards grid');
        }
        // 真实调用测试分类过滤，拦截 TypeError: window.filterDesignProviders is not a function
        window.filterDesignProviders('cloud_api', { classList: { add: ()=>{}, remove: ()=>{} } });
        // 10. 验证 syndicate.preview.js 全渠道高保真排版沉浸式 Modal 运行时与 DOM 拓扑 (Rule 7)
        const syndicatePreviewCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.preview.js', 'utf8');
        eval(syndicatePreviewCode);
        const syndicateCoverCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.preview_cover.js', 'utf8');
        eval(syndicateCoverCode);
        if (typeof window.renderChannelCoverStudio !== 'function') throw new Error('renderChannelCoverStudio is not defined');
        if (typeof window.bindViewportDragAndWheel !== 'function') throw new Error('bindViewportDragAndWheel is not defined');

        // 测试真机封面取景器渲染 (Rule 7)
        const mockCoverContainer = { innerHTML: '' };
        window.renderChannelCoverStudio('wechat', mockCoverContainer, 'https://example.com/cover.jpg');
        if (!mockCoverContainer.innerHTML.includes('channel-crop-viewport-wechat')) {
            throw new Error('renderChannelCoverStudio missing viewport topology');
        }
        if (mockCoverContainer.innerHTML.includes('type="range"')) {
            throw new Error('renderChannelCoverStudio should not contain redundant range sliders');
        }
        if (!mockCoverContainer.innerHTML.includes('channel-preview-focal-hint-wechat')) {
            throw new Error('renderChannelCoverStudio missing focal hint capsule');
        }
        if (typeof window.openSyndicateLivePreviewModal !== 'function') throw new Error('openSyndicateLivePreviewModal is not defined');
        if (typeof window.closeSyndicateLivePreviewModal !== 'function') throw new Error('closeSyndicateLivePreviewModal is not defined');
        if (typeof window.switchSyndicatePreviewTarget !== 'function') throw new Error('switchSyndicatePreviewTarget is not defined');

        let createdPreviewModal = null;
        global.document.getElementById = (id) => null;
        global.document.createElement = (tag) => {
            createdPreviewModal = { id: '', style: {}, innerHTML: '', onclick: null };
            return createdPreviewModal;
        };
        global.document.body = { appendChild: () => {} };
        global.document.addEventListener = () => {};
        global.document.removeEventListener = () => {};

        window.currentSyndicatingTitle = '测试文稿';
        window.openSyndicateLivePreviewModal();
        if (!createdPreviewModal || !createdPreviewModal.innerHTML.includes('syndicate-preview-modal-card')) {
            throw new Error('syndicate-preview-modal-card topology missing from modal');
        }
        if (!createdPreviewModal.innerHTML.includes('syndicate-modal-preview-tabs')) {
            throw new Error('syndicate-modal-preview-tabs missing from modal');
        }

        // 真实调用 renderSyndicateCardPreview 拦截未声明变量 (Rule 7 ReferenceError 拦截)
        const mockPreviewCardContainer = { innerHTML: '' };
        const mockStatsSlot = { innerHTML: '' };
        const mockActionsSlot = { innerHTML: '' };
        global.document.getElementById = (id) => {
            if (id === 'syndicate-card-preview-renderer') return mockPreviewCardContainer;
            if (id === 'syndicate-modal-stats-capsule') return mockStatsSlot;
            if (id === 'syndicate-modal-actions-slot') return mockActionsSlot;
            return null;
        };
        window.fetchSyndicatePreviewData = async () => ({
            status: 'success',
            title: '测试',
            rendered_html: '<h1>标题</h1><p>正文</p>',
            rendered_markdown: '正文',
            stats: { word_count: 100, reading_time_min: 1, footnotes_count: 0, title_length: 2 },
            compliance: { platform_rules: '微信规则' }
        });
        await window.renderSyndicateCardPreview('wechat');
        if (!mockPreviewCardContainer.innerHTML.includes('preview-viewport-chassis')) {
            throw new Error('renderSyndicateCardPreview chassis topology missing');
        }
        await window.renderSyndicateCardPreview('xiaohongshu');
        await window.renderSyndicateCardPreview('devto');

        // 11. 验证 syndicate.render.js 抽屉三大骨架与分步状态机 (Rule 7)
        const syndicateRenderCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.render.js', 'utf8');
        eval(syndicateRenderCode);
        if (typeof window.switchSyndicateDrawerStage !== 'function') throw new Error('switchSyndicateDrawerStage is not defined');

        const mockConfigView = { style: {} };
        const mockTelemetryView = { style: {} };
        const mockFooter = { innerHTML: '' };
        const mockCapsule = { innerHTML: '' };
        global.document.getElementById = (id) => {
            if (id === 'syndicate-config-stage-view') return mockConfigView;
            if (id === 'syndicate-telemetry-stage-view') return mockTelemetryView;
            if (id === 'article-syndicate-drawer-footer') return mockFooter;
            if (id === 'syndicate-telemetry-summary-capsule') return mockCapsule;
            return null;
        };

        window.switchSyndicateDrawerStage('running', { lang: 'zh', platformCount: 2 });
        if (mockConfigView.style.display !== 'none' || mockTelemetryView.style.display !== 'flex') {
            throw new Error('switchSyndicateDrawerStage running stage topology mismatch');
        }
        window.switchSyndicateDrawerStage('telemetry', { failedCount: 1, failedChannelsJson: '["wechat"]' });
        if (!mockFooter.innerHTML.includes('修改配置') || !mockFooter.innerHTML.includes('一键重试失败')) {
            throw new Error('switchSyndicateDrawerStage telemetry footer action mismatch');
        }
        // 12. 验证 syndicate.dispatch.js 真实推流与结果回填闭环 (Rule 7 TypeError / ReferenceError 拦截)
        const syndicateDispatchCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.dispatch.js', 'utf8');
        eval(syndicateDispatchCode);
        if (typeof window.dispatchArticleSyndication !== 'function') throw new Error('dispatchArticleSyndication is not defined');

        const mockProgressPanel = { style: {} };
        const mockProgressTitle = { innerText: '' };
        const mockProgressPercent = { innerText: '' };
        const mockProgressBar = { style: {} };
        const mockProgressDesc = { innerText: '' };
        const mockResultsSlot = { innerHTML: '' };

        global.document.getElementById = (id) => {
            if (id === 'syndicate-config-stage-view') return mockConfigView;
            if (id === 'syndicate-telemetry-stage-view') return mockTelemetryView;
            if (id === 'article-syndicate-drawer-footer') return mockFooter;
            if (id === 'syndicate-telemetry-summary-capsule') return mockCapsule;
            if (id === 'syndicate-progress-panel') return mockProgressPanel;
            if (id === 'syndicate-progress-title') return mockProgressTitle;
            if (id === 'syndicate-progress-percent') return mockProgressPercent;
            if (id === 'syndicate-progress-bar') return mockProgressBar;
            if (id === 'syndicate-progress-desc') return mockProgressDesc;
            if (id === 'syndicate-results-panel-slot') return mockResultsSlot;
            return null;
        };

        global.document.querySelector = (sel) => {
            if (sel === 'input[name="syndicate_lang"]:checked') return { value: 'auto' };
            return null;
        };
        global.document.querySelectorAll = (sel) => {
            if (sel === '.syndicate-platform-checkbox:checked') return [{ value: 'wechat' }, { value: 'juejin' }, { value: 'devto' }];
            return [];
        };

        global.window.apiFetch = async (url) => {
            if (url.includes('/api/vault/dispatch-status/')) {
                return {
                    doc_id: 'test.md',
                    sync_matrix: [
                        { locale: 'Auto', lang_code: 'ZH', status: 'published' },
                        { channel_id: 'wechat', status: 'draft', artifact_url: 'https://mp.weixin.qq.com' },
                        { channel_id: 'juejin', status: 'draft', artifact_url: 'https://juejin.cn/editor/drafts/123' },
                        { channel_id: 'devto', status: 'failed', reason: '401 Unauthorized', diagnosis: { badge: '⚠️ 凭据失效', friendly_message: 'Token失效' } }
                    ]
                };
            }
            if (url.includes('/api/syndication/records/')) {
                return { records: [] };
            }
            return { ok: true };
        };
        global.apiFetch = global.window.apiFetch;

        await window.dispatchArticleSyndication('test.md');
        if (!mockResultsSlot.innerHTML.includes('syndicate-results-panel')) {
            throw new Error('dispatchArticleSyndication failed to render syndicate-results-panel');
        }
        if (!mockResultsSlot.innerHTML.includes('广播物理凭证终态分布')) {
            throw new Error('dispatchArticleSyndication missing results distribution card');
        }
        if (!mockFooter.innerHTML.includes('修改配置')) {
            throw new Error('dispatchArticleSyndication failed to switch footer to telemetry stage');
        }

        console.log('ALL_FRONTEND_RENDER_DOM_VERIFIED_SUCCESS');
    }).catch(err => {
        console.error(err);
        process.exit(1);
    });
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Frontend Render Runtime Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "ALL_FRONTEND_RENDER_DOM_VERIFIED_SUCCESS" in res.stdout
