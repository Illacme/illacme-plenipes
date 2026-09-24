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

    // 2. 加载并执行 plugins.render.badges.js, plugins.render.pod.js, plugins.render.physics.js
    eval(fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.badges.js', 'utf8'));
    eval(fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.pod.js', 'utf8'));
    eval(fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.physics.js', 'utf8'));
    if (typeof window.getPlatformBrandBadge !== 'function' || typeof window.init3DHoverPhysics !== 'function') {
        throw new Error('Plugins badges or physics shards failed to register functions on window');
    }

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

        // 4.1 加载并执行 route.slug_render.js (Rule 7: 网址路径二级面板与 URL 沙盒断言)
        const slugRenderCode = fs.readFileSync('web/dashboard/js/route/route_shards/route.slug_render.js', 'utf8');
        eval(slugRenderCode);
        const slugHtml = window.renderSlugSettingsCategory();
        if (!slugHtml || typeof slugHtml !== 'string') {
            throw new Error('renderSlugSettingsCategory must return valid html string');
        }
        if (!slugHtml.includes('slug-dir-card') || !slugHtml.includes('sandbox-file-select')) {
            throw new Error('Slug settings DOM topology broken: missing slug-dir-card or sandbox playground');
        }

        // 4.1.1 加载并执行 route.slug_actions.js 与 route.slug.sandbox.js (Rule 7: 模式切换与实时推导)
        eval(fs.readFileSync('web/dashboard/js/route/route_shards/route.slug_actions.js', 'utf8'));
        eval(fs.readFileSync('web/dashboard/js/route/route.slug.sandbox.js', 'utf8'));
        if (typeof window.selectSlugDirModeCard !== 'function' || typeof window.updateSlugSandboxPreview !== 'function') {
            throw new Error('route.slug_actions or sandbox functions not registered on window');
        }
        window.selectSlugDirModeCard('nested');
        await window.updateSlugSandboxPreview();

        // 4.2 加载并执行 core.deploy_summary.js (Rule 7: 全域部署成果卡片与 CDN 健康雷达)
        global.document.createElement = (tag) => ({
            tagName: tag.toUpperCase(),
            style: {},
            classList: { add: ()=>{}, remove: ()=>{} },
            innerHTML: '',
            appendChild: function(c) { this.children = this.children || []; this.children.push(c); },
            remove: () => {}
        });
        const mockTermOutput = {
            children: [],
            appendChild: function(child) { this.children.push(child); },
            querySelector: function(sel) { return null; },
            scrollTop: 0,
            scrollHeight: 100
        };
        const origGetElem = global.document.getElementById;
        global.document.getElementById = (id) => {
            if (id === 'terminal-output') return mockTermOutput;
            return origGetElem(id);
        };
        eval(fs.readFileSync('web/dashboard/js/core/core_shards/core.deploy_summary.js', 'utf8'));
        window.renderDeploymentSummaryCard({
            total_channels: 2,
            channels: [
                { name: 'GitHub Pages', status: 'success', url: 'https://example.github.io', is_primary: true },
                { name: 'Vercel', status: 'success', url: 'https://example.vercel.app', is_primary: false }
            ]
        });
        if (mockTermOutput.children.length === 0) {
            throw new Error('renderDeploymentSummaryCard failed to append card to terminal-output');
        }
        const summaryCardHtml = mockTermOutput.children[0].innerHTML;
        if (!summaryCardHtml.includes('全域发布圆满完成') || !summaryCardHtml.includes('官方主站') || !summaryCardHtml.includes('health-radar-badge')) {
            throw new Error('Deployment summary card topology broken: missing title, primary badge or health-radar-badge');
        }
        global.document.getElementById = origGetElem;

        // 4.3 加载并执行 modals 体系沙箱断言 (Rule 7: 全局弹窗拓扑完备性)
        eval(fs.readFileSync('web/dashboard/js/ui/modal_shards/modals.system.js', 'utf8'));
        eval(fs.readFileSync('web/dashboard/js/ui/modal_shards/modals.wizard_step3.js', 'utf8'));
        eval(fs.readFileSync('web/dashboard/js/ui/modal_shards/modals.wizard_success.js', 'utf8'));
        eval(fs.readFileSync('web/dashboard/js/ui/modals.js', 'utf8'));
        const allModalsHtml = window.getUIModalsHTML();
        if (!allModalsHtml || typeof allModalsHtml !== 'string') {
            throw new Error('getUIModalsHTML must return valid HTML string');
        }
        const requiredModalIds = ['publish-modal', 'editor-modal', 'terminal-modal', 'imprint-wizard-modal', 'wiz-step-3', 'imprint-success-modal'];
        for (const mid of requiredModalIds) {
            if (!allModalsHtml.includes(`id="${mid}"`)) {
                throw new Error(`Modals DOM topology broken: missing id="${mid}"`);
            }
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
        const statusCode = fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.status.js', 'utf8');
        eval(statusCode);
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

        // 8.5 网络穿透驱动双模凭据感知 (Cloudflare Tunnel: Quick 免配即用 vs 专属通道就绪, Pinggy SSH: 免配即用)
        const rPinggy = window.isPluginCredentialReady('pinggy', 'tunnel', {});
        if (!rPinggy.ready || rPinggy.label !== '免配即用') throw new Error('Pinggy tunnel readiness failed');

        const rCFTemp = window.isPluginCredentialReady('cloudflare', 'tunnel', {});
        if (!rCFTemp.ready || rCFTemp.label !== '免配即用' || rCFTemp.mode !== 'quick') throw new Error('Cloudflare tunnel quick readiness failed');

        const rCFTok = window.isPluginCredentialReady('cloudflare', 'tunnel', { tunnel_token: 'cf-secret-token' });
        if (!rCFTok.ready || rCFTok.label !== '专属通道就绪' || rCFTok.mode !== 'token') throw new Error('Cloudflare tunnel token readiness failed');

        // 8.6 网络穿透插件卡片徽标判定 (checkPluginConfiguredStatus)
        window.settingsData.tunnel = {};
        const cfStatusQuick = window.checkPluginConfiguredStatus({ id: 'cloudflare', category: 'tunnel', is_enabled: true, is_manageable: true, has_config: true });
        if (cfStatusQuick.label !== '⚡ 免配即用') throw new Error(`Expected '⚡ 免配即用' for unconfigured Cloudflare Tunnel, got: ${cfStatusQuick.label}`);

        window.settingsData.tunnel = { cloudflare: { tunnel_token: 'cf-token-abc' } };
        const cfStatusToken = window.checkPluginConfiguredStatus({ id: 'cloudflare', category: 'tunnel', is_enabled: true, is_manageable: true, has_config: true });
        if (cfStatusToken.label !== '🟢 专属通道就绪') throw new Error(`Expected '🟢 专属通道就绪' for configured Cloudflare Tunnel, got: ${cfStatusToken.label}`);


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
            createdPreviewModal = {
                id: '',
                style: {},
                className: '',
                classList: { add: ()=>{}, remove: ()=>{}, contains: ()=>false },
                innerHTML: '',
                onclick: null
            };
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

        // 🚀 [V122.0] 全域发布任务大厅与成果账本沙箱断言 (Rule 7)
        eval(fs.readFileSync('web/dashboard/js/dispatch/dispatch.templates.js', 'utf8'));
        if (!window.viewTemplates.tasks.includes('id="view-tasks"')) {
            throw new Error('viewTemplates.tasks missing id="view-tasks"');
        }
        if (!window.viewTemplates.tasks.includes('dispatch-metric-grid') || !window.viewTemplates.tasks.includes('channel-matrix-grid')) {
            throw new Error('viewTemplates.tasks missing metric or channel matrix grid');
        }

        eval(fs.readFileSync('web/dashboard/js/dispatch/dispatch.indicator.js', 'utf8'));
        eval(fs.readFileSync('web/dashboard/js/dispatch/dispatch.popover.js', 'utf8'));
        eval(fs.readFileSync('web/dashboard/js/dispatch/dispatch.workbench.js', 'utf8'));
        eval(fs.readFileSync('web/dashboard/js/dispatch/dispatch.ledger.render.js', 'utf8'));

        const mockBodySlot = { innerHTML: '' };
        const mockLedgerSlot = { innerHTML: '' };
        const mockDeadletterSlot = { innerHTML: '' };
        global.document.getElementById = (id) => {
            if (id === 'dispatch-popover-body') return mockBodySlot;
            if (id === 'dispatch-ledger-container') return mockLedgerSlot;
            if (id === 'dispatch-deadletter-container') return mockDeadletterSlot;
            if (id === 'dispatch-channel-matrix') return { innerHTML: '' };
            if (id === 'dispatch-active-pipeline-zone') return { innerHTML: '', style: {} };
            return { style: {}, classList: { add: ()=>{}, remove: ()=>{} }, innerText: '' };
        };

        const testOverview = {
            status: 'success',
            is_publishing: false,
            summary: { total_syndicated: 12, total_failed: 1, active_count: 0, success_rate: '92.3%' },
            channel_health: [{ id: 'devto', name: 'Dev.to', icon: '👩‍💻', status: 'healthy', status_msg: '就绪', enabled: true }],
            dead_letter_tasks: [{ rel_path: 'fail.md', target_id: 'devto', last_error: 'Token error', retry_count: 1 }],
            recent_records: [{ rel_path: 'article.md', lang_code: 'zh-CN', target_id: 'devto', remote_url: 'https://dev.to/test/123' }]
        };

        window.updateDispatchIndicator(testOverview);
        window.renderPopoverContent(testOverview);
        if (!mockBodySlot.innerHTML.includes('https://dev.to/test/123') || !mockBodySlot.innerHTML.includes('magic-link-mini')) {
            throw new Error('Popover missing magic-link-mini');
        }

        window.renderDispatchLedger(testOverview.recent_records);
        if (!mockLedgerSlot.innerHTML.includes('ledger-table') || !mockLedgerSlot.innerHTML.includes('https://dev.to/test/123')) {
            throw new Error('Ledger render missing table or remote url');
        }

        window.renderDispatchDeadLetters(testOverview.dead_letter_tasks);
        if (!mockDeadletterSlot.innerHTML.includes('deadletter-card') || !mockDeadletterSlot.innerHTML.includes('Token error')) {
            throw new Error('DeadLetter render missing card or diagnosis');
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


def test_review_drawer_render_integrity():
    """
    🛡️ 审稿抽屉 (Review Drawer) 渲染函数运行时沙箱与 DOM 拓扑完备性门禁 (Rule 7)
    断言：
    1. review.template.js 挂载包含 .review-drawer-overlay 与 .review-drawer-window 语义类
    2. review.render.body.js 渲染包含 .review-three-cols、.review-progress-track 等结构
    3. 运行全程 0 ReferenceError、0 未定义变量
    """
    runner_script = """
    const fs = require('fs');

    const elements = {};
    global.document = {
        _elements: elements,
        getElementById(id) {
            return elements[id] || null;
        },
        body: {
            insertAdjacentHTML(pos, html) {
                global.insertedHtml = html;
            }
        },
        readyState: 'complete'
    };
    global.window = {
        _reviewState: {
            docId: 'test-doc.md',
            activeLang: 'en',
            showPreview: true,
            showSource: false,
            data: {
                doc_title: 'Test Doc',
                langs: {
                    en: { is_missing: false, human_approved: true, reviewed_at: 1700000000 },
                    ja: { is_missing: true }
                },
                source_paragraphs: [
                    { index: 0, text: 'Hello world', type: 'text' },
                    { index: 1, text: 'console.log(1)', type: 'code' }
                ]
            },
            edits: {
                en: {
                    title: 'Test Doc EN',
                    desc: 'Test Description',
                    paragraphs: [
                        { index: 0, text: 'Hello world translated', type: 'text', _edited: true },
                        { index: 1, text: 'console.log(1)', type: 'code' }
                    ]
                }
            }
        },
        availableLangs: [{ code: 'en', name: 'English', icon: '🌍' }],
        marked: { parse: (t) => '<p>' + t + '</p>' }
    };

    // 1. 验证 review.template.js 骨架挂载与语义类
    const templateCode = fs.readFileSync('web/dashboard/js/localization/review_shards/review.template.js', 'utf8');
    eval(templateCode);

    if (!global.insertedHtml || !global.insertedHtml.includes('review-drawer-overlay')) {
        throw new Error('review.template.js failed: missing review-drawer-overlay class');
    }
    if (!global.insertedHtml.includes('review-drawer-window')) {
        throw new Error('review.template.js failed: missing review-drawer-window class');
    }
    if (!global.insertedHtml.includes('review-view-toggle')) {
        throw new Error('review.template.js failed: missing review-view-toggle');
    }

    // 2. 模拟真实 DOM 节点注入
    function makeEl(id) {
        elements[id] = {
            id,
            style: {},
            classList: {
                _classes: new Set(),
                add(c) { this._classes.add(c); },
                remove(c) { this._classes.delete(c); },
                toggle(c, force) {
                    if (force !== undefined) {
                        if (force) this._classes.add(c);
                        else this._classes.delete(c);
                        return force;
                    }
                    if (this._classes.has(c)) { this._classes.delete(c); return false; }
                    else { this._classes.add(c); return true; }
                },
                contains(c) { return this._classes.has(c); }
            },
            innerHTML: '',
            textContent: ''
        };
        return elements[id];
    }
    ['review-drawer', 'review-drawer-title', 'review-lang-tabs', 'review-mode-alert', 'review-body', 'btn-view-source', 'btn-view-preview'].forEach(makeEl);

    // 3. 加载前置依赖与主体渲染分片
    const progressCode = fs.readFileSync('web/dashboard/js/localization/review_shards/review.render.progress.js', 'utf8');
    eval(progressCode);

    const bodyCode = fs.readFileSync('web/dashboard/js/localization/review_shards/review.render.body.js', 'utf8');
    eval(bodyCode);

    // 4. 执行渲染断言
    _reviewRender();

    const reviewBodyEl = global.document.getElementById('review-body');
    if (!reviewBodyEl.innerHTML.includes('review-three-cols')) {
        throw new Error('_reviewRender failed: missing review-three-cols');
    }
    if (!reviewBodyEl.innerHTML.includes('col-target') || !reviewBodyEl.innerHTML.includes('col-preview')) {
        throw new Error('_reviewRender failed: missing column containers');
    }

    console.log('REVIEW_DRAWER_RENDER_DOM_VERIFIED_SUCCESS');
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Review Drawer Render Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "REVIEW_DRAWER_RENDER_DOM_VERIFIED_SUCCESS" in res.stdout


def test_vault_drawer_and_ui_drawers_integrity():
    """
    🛡️ 通用抽屉与文库抽屉 (Drawers & Vault Drawer) 渲染函数沙箱与 DOM 拓扑完备性门禁 (Rule 7)
    断言：
    1. drawers.js 骨架生成包含 .vault-drawer-backdrop, .vault-drawer-shell, .plugin-drawer-overlay 等语义类
    2. vault.drawer.cards.js 渲染卡片包含 .hosting-card, .hosting-card-header-row, .vault-preview-link
    3. 运行全程 0 ReferenceError、0 模板断裂
    """
    runner_script = """
    const fs = require('fs');

    global.window = {
        addEventListener: () => {},
        removeEventListener: () => {}
    };

    // 1. 验证 drawers.js 通用抽屉骨架与语义类
    const drawersCode = fs.readFileSync('web/dashboard/js/ui/drawers.js', 'utf8');
    eval(drawersCode);

    const drawersHtml = window.getUIDrawersHTML();
    if (!drawersHtml || typeof drawersHtml !== 'string') {
        throw new Error('getUIDrawersHTML failed to return HTML string');
    }
    if (!drawersHtml.includes('vault-drawer-backdrop')) {
        throw new Error('drawers.js missing vault-drawer-backdrop class');
    }
    if (!drawersHtml.includes('vault-drawer-shell')) {
        throw new Error('drawers.js missing vault-drawer-shell class');
    }
    if (!drawersHtml.includes('drawer-header-row')) {
        throw new Error('drawers.js missing drawer-header-row class');
    }
    if (!drawersHtml.includes('plugin-drawer-overlay')) {
        throw new Error('drawers.js missing plugin-drawer-overlay class');
    }
    if (!drawersHtml.includes('plugin-drawer-header')) {
        throw new Error('drawers.js missing plugin-drawer-header class');
    }

    // 2. 验证 vault.drawer.cards.js 卡片渲染与语义类
    const cardsCode = fs.readFileSync('web/dashboard/js/vault/drawer_shards/vault.drawer.cards.js', 'utf8');
    eval(cardsCode);

    const mockLocalDocs = [
        { status: 'published', locale: '中文原稿', lang_code: 'zh', artifact_url: '/docs/index.html', tokens: 120, last_sync: '2026-09-18' }
    ];
    const localHtml = window.renderVaultLocalArtifactsHtml(mockLocalDocs, false, '');
    if (!localHtml.includes('matrix-item') || !localHtml.includes('vault-preview-link')) {
        throw new Error('renderVaultLocalArtifactsHtml missing matrix-item or vault-preview-link');
    }

    const mockHostingList = [
        { id: 'github_pages', isReady: true, isBrandInUse: true, isChecked: true, name: 'GitHub Pages', icon: '🐙', desc: 'Git 自动化部署', record: null }
    ];
    const hostingHtml = window.renderVaultHostingCardsHtml(mockHostingList, 'Docs/index.md');
    if (!hostingHtml.includes('hosting-card') || !hostingHtml.includes('hosting-card-header-row')) {
        throw new Error('renderVaultHostingCardsHtml missing hosting-card or hosting-card-header-row');
    }
    if (!hostingHtml.includes('vault-hosting-platform-checkbox') || !hostingHtml.includes('hosting-desc-text')) {
        throw new Error('renderVaultHostingCardsHtml missing checkbox or desc-text class');
    }

    console.log('VAULT_DRAWER_UI_DRAWERS_VERIFIED_SUCCESS');
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Vault Drawer Render Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "VAULT_DRAWER_UI_DRAWERS_VERIFIED_SUCCESS" in res.stdout


def test_syndicate_drawer_render_integrity():
    """
    🛡️ [Rule 7 Gate] 验证社交媒体分发抽屉 (Syndicate Drawer) 渲染 DOM 完备性与样式类规范化契约
    """
    runner_script = """
    const fs = require('fs');

    // 1. 构建 Mock DOM 环境
    const elementsById = {};
    const elementsByClass = {};
    const createdElements = [];

    class MockClassList {
        constructor() { this.classes = new Set(); }
        add(...cls) { cls.forEach(c => this.classes.add(c)); }
        remove(...cls) { cls.forEach(c => this.classes.delete(c)); }
        contains(c) { return this.classes.has(c); }
        toggle(c, force) {
            if (force === undefined) {
                if (this.classes.has(c)) { this.classes.delete(c); return false; }
                else { this.classes.add(c); return true; }
            }
            if (force) { this.classes.add(c); return true; }
            else { this.classes.delete(c); return false; }
        }
        toString() { return Array.from(this.classes).join(' '); }
    }

    class MockElement {
        constructor(tag) {
            this.tagName = (tag || 'div').toUpperCase();
            this.id = '';
            this._className = '';
            this.classList = new MockClassList();
            this.style = {};
            this.innerHTML = '';
            this.attributes = {};
            this.children = [];
            this.parentElement = null;
        }
        set className(val) {
            this._className = val || '';
            this.classList.classes.clear();
            if (val) val.split(/\\s+/).filter(Boolean).forEach(c => this.classList.add(c));
        }
        get className() {
            return this.classList.toString();
        }
        appendChild(child) {
            child.parentElement = this;
            this.children.push(child);
            return child;
        }
        querySelectorAll(selector) {
            return [];
        }
        querySelector(selector) {
            return null;
        }
    }

    const documentMock = {
        body: new MockElement('body'),
        getElementById(id) {
            return elementsById[id] || null;
        },
        createElement(tag) {
            const el = new MockElement(tag);
            createdElements.push(el);
            Object.defineProperty(el, 'id', {
                set: function(val) { this._id = val; elementsById[val] = this; },
                get: function() { return this._id || ''; }
            });
            return el;
        },
        querySelectorAll(sel) {
            return [];
        },
        querySelector(sel) {
            return null;
        }
    };

    global.window = {
        apiFetch: async () => ({ records: [] }),
        settingsData: {
            current_brand: 'default',
            syndication: {},
            image_policy: { default_strategy: 'auto' }
        },
        allPlugins: [
            { id: 'wechat', name: '微信公众号', category: 'publisher', icon: '🟢', sla_tier: 'tier2' },
            { id: 'devto', name: 'Dev.to', category: 'publisher', icon: '📝', sla_tier: 'tier1' }
        ],
        getAvailableSyndicateLangs: () => [
            { code: 'zh', name: '中文', icon: '🇨🇳', isSource: true },
            { code: 'en', name: 'English', icon: '🇺🇸', isSource: false }
        ]
    };
    global.document = documentMock;
    global.requestAnimationFrame = (cb) => { if (cb) cb(); };
    global.setTimeout = (cb) => { if (cb) cb(); };

    // 2. 加载 Syndicate 相关分片
    const cardsCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.cards.js', 'utf8');
    eval(cardsCode);
    const coverStudioCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.cover_studio.js', 'utf8');
    eval(coverStudioCode);
    const renderCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.render.js', 'utf8');
    eval(renderCode);

    (async () => {
        // 3. 执行 openArticleSyndicationDrawer
        await window.openArticleSyndicationDrawer('docs/guide.md', '用户手册');

        const backdropEl = documentMock.getElementById('article-syndicate-drawer-backdrop');
        if (!backdropEl) throw new Error('backdrop element not found');
        if (!backdropEl.classList.contains('syndicate-drawer-backdrop')) {
            throw new Error('backdrop missing syndicate-drawer-backdrop class');
        }

        const drawerEl = documentMock.getElementById('article-syndicate-drawer');
        if (!drawerEl) throw new Error('drawer element not found');
        if (!drawerEl.classList.contains('syndicate-drawer-shell')) {
            throw new Error('drawer missing syndicate-drawer-shell class');
        }

        const html = drawerEl.innerHTML;
        const requiredClasses = [
            'syndicate-drawer-header',
            'syndicate-drawer-title',
            'drawer-doc-card',
            'syndicate-drawer-body',
            'syndicate-stage-view',
            'syndicate-step-group',
            'syndicate-step-label',
            'syndicate-lang-picker',
            'lang-radio-btn',
            'syndicate-tip-box',
            'syndicate-preview-entry',
            'syndicate-drawer-footer',
            'syndicate-start-btn'
        ];

        for (const cls of requiredClasses) {
            if (!html.includes(cls)) {
                throw new Error('Syndicate drawer DOM topology missing semantic class: ' + cls);
            }
        }

        // 4. 验证关闭生命周期与 CSS 类协调
        window.closeArticleSyndicationDrawer();
        if (drawerEl.classList.contains('is-open')) {
            throw new Error('closeArticleSyndicationDrawer failed to remove is-open from drawer');
        }
        if (backdropEl.classList.contains('is-open')) {
            throw new Error('closeArticleSyndicationDrawer failed to remove is-open from backdrop');
        }

        console.log('SYNDICATE_DRAWER_VERIFIED_SUCCESS');
    })().catch(err => {
        console.error(err);
        process.exit(1);
    });
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Syndicate Drawer Render Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "SYNDICATE_DRAWER_VERIFIED_SUCCESS" in res.stdout


def test_syndicate_live_preview_modal_render_integrity():
    """
    🛰️ [V105.0] 全渠道排版即时审查弹窗与取景器渲染完整性与 DOM 拓扑门禁测试 (Phase 4 方向 A)
    验证目标：
    1. openSyndicateLivePreviewModal 生成的 DOM 具备完整的语义化 CSS 类拓扑，杜绝内联 style。
    2. renderChannelCoverStudio 取景器工作台具有标准的 CSS 类拓扑（panel, header, viewport, grid, focal-hint）。
    3. 弹窗打开与关闭生命周期与 is-open 状态类完全联动。
    """
    runner_script = """
    const fs = require('fs');

    // 1. 模拟浏览器运行沙箱
    const elementsById = {};
    function createMockElement(tagName) {
        const classListSet = new Set();
        return {
            tagName: (tagName || 'div').toUpperCase(),
            style: {},
            children: [],
            className: '',
            classList: {
                add: (c) => classListSet.add(c),
                remove: (c) => classListSet.delete(c),
                contains: (c) => classListSet.has(c),
            },
            setAttribute: () => {},
            getAttribute: () => null,
            appendChild: function(c) { this.children.push(c); return c; },
            removeChild: function(c) {
                const idx = this.children.indexOf(c);
                if (idx !== -1) this.children.splice(idx, 1);
            },
            addEventListener: () => {},
            removeEventListener: () => {},
            querySelectorAll: () => [],
            querySelector: () => null
        };
    }

    const documentMock = {
        getElementById: (id) => elementsById[id] || null,
        createElement: (tag) => createMockElement(tag),
        body: {
            appendChild: (el) => {
                if (el.id) elementsById[el.id] = el;
                return el;
            }
        },
        querySelectorAll: () => [],
        querySelector: () => null,
        addEventListener: () => {},
        removeEventListener: () => {}
    };

    global.window = {
        allPlugins: [{ id: 'wechat', name: '微信公众号', category: 'publisher', icon: '💬' }],
        currentSyndicatingTitle: '测试排版文稿',
        currentSyndicatingRelPath: 'articles/test.md',
        currentSyndicateCover: { url: 'https://example.com/cover.png', overrides: {} },
        showToast: () => {},
        apiFetch: async () => ({ status: 'success', stats: { word_count: 1200 }, rendered_html: '<p>测试内容</p>' })
    };
    global.document = documentMock;

    // 2. 加载 Preview 相关分片
    const previewCoverCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.preview_cover.js', 'utf8');
    eval(previewCoverCode);
    const previewCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.preview.js', 'utf8');
    eval(previewCode);

    // 3. 执行 openSyndicateLivePreviewModal
    window.openSyndicateLivePreviewModal();

    const modalEl = documentMock.getElementById('syndicate-live-preview-modal-root');
    if (!modalEl) throw new Error('Preview modal root not created');
    if (!modalEl.classList.contains('is-open')) {
        throw new Error('Preview modal root missing is-open class');
    }
    if (!modalEl.className.includes('syndicate-modal-backdrop')) {
        throw new Error('Preview modal root missing syndicate-modal-backdrop class');
    }

    const html = modalEl.innerHTML;
    const requiredModalClasses = [
        'syndicate-preview-modal-card',
        'syndicate-modal-header',
        'syndicate-modal-title-group',
        'syndicate-modal-title',
        'syndicate-modal-subtitle',
        'syndicate-modal-header-actions',
        'syndicate-modal-tabs',
        'syndicate-modal-channel-select',
        'syndicate-modal-close-btn',
        'syndicate-modal-toolbar',
        'syndicate-modal-stats',
        'syndicate-modal-actions',
        'syndicate-modal-body',
        'syndicate-card-preview-renderer'
    ];
    for (const cls of requiredModalClasses) {
        if (!html.includes(cls)) {
            throw new Error('Preview modal DOM topology missing class: ' + cls);
        }
    }

    // 4. 验证取景器工作台渲染
    const dummyStudioContainer = createMockElement('div');
    window.renderChannelCoverStudio('wechat', dummyStudioContainer, 'https://example.com/cover.jpg');
    const studioHtml = dummyStudioContainer.innerHTML;
    const requiredStudioClasses = [
        'channel-cover-studio-panel',
        'channel-cover-studio-header',
        'channel-cover-studio-title-box',
        'channel-cover-studio-actions',
        'channel-crop-viewport',
        'channel-preview-cover-img',
        'channel-crop-grid-overlay',
        'channel-crop-focal-hint'
    ];
    for (const cls of requiredStudioClasses) {
        if (!studioHtml.includes(cls)) {
            throw new Error('Channel cover studio DOM topology missing class: ' + cls);
        }
    }

    // 5. 验证关闭模态窗
    window.closeSyndicateLivePreviewModal();
    if (modalEl.classList.contains('is-open')) {
        throw new Error('closeSyndicateLivePreviewModal failed to remove is-open class');
    }

    console.log('SYNDICATE_LIVE_PREVIEW_MODAL_VERIFIED_SUCCESS');
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Syndicate Preview Modal Render Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "SYNDICATE_LIVE_PREVIEW_MODAL_VERIFIED_SUCCESS" in res.stdout


def test_syndicate_asset_picker_modal_render_integrity():
    """
    🛡️ 资产拾取弹窗与大图详情弹窗运行时沙箱与 DOM 拓扑完备性门禁测试 (Rule 7)
    验证覆盖：
    1. openSyndicateAssetPickerModal 创建并打开资产选择弹窗，验证 backdrop、card、header、actions、scroll-view、grid 拓扑
    2. loadAssetsForCoverPicker 加载资产并渲染 item、thumb-box、img、engine-tag、meta-row、pagination 拓扑
    3. closeSyndicateAssetPickerModal 正确移除 is-open 状态
    4. showImageModal 创建并打开全屏大图详情弹窗，验证 card、header、viewport、footer、meta、download-btn 拓扑
    5. closeGlobalImageDetailModal 正确移除 is-open 状态
    """
    runner_script = """
    const fs = require('fs');

    const elementsById = {};
    function createMockElement(tagName) {
        const classListSet = new Set();
        const el = {
            tagName: (tagName || 'div').toUpperCase(),
            style: {},
            children: [],
            className: '',
            classList: {
                add: (c) => classListSet.add(c),
                remove: (c) => classListSet.delete(c),
                contains: (c) => classListSet.has(c),
            },
            setAttribute: () => {},
            getAttribute: () => null,
            appendChild: function(c) { this.children.push(c); return c; },
            removeChild: function(c) {
                const idx = this.children.indexOf(c);
                if (idx !== -1) this.children.splice(idx, 1);
            },
            addEventListener: () => {},
            removeEventListener: () => {},
            querySelectorAll: () => [],
            querySelector: () => null
        };
        return el;
    }

    const documentMock = {
        getElementById: (id) => {
            if (elementsById[id]) return elementsById[id];
            // 若子元素包含在某个已挂载父容器的 innerHTML 中，动态创建并记录
            for (const parent of Object.values(elementsById)) {
                if (parent.innerHTML && parent.innerHTML.includes(`id="${id}"`)) {
                    const child = createMockElement('div');
                    child.id = id;
                    elementsById[id] = child;
                    return child;
                }
            }
            return null;
        },
        createElement: (tag) => createMockElement(tag),
        body: {
            appendChild: (el) => {
                if (el.id) elementsById[el.id] = el;
                return el;
            }
        },
        querySelectorAll: () => [],
        querySelector: () => null,
        addEventListener: () => {},
        removeEventListener: () => {}
    };

    global.window = {
        settingsData: {
            image_policy: { default_strategy: 'auto' },
            current_brand: 'default'
        },
        showToast: () => {},
        apiFetch: async (url) => {
            if (url.includes('/api/design/assets')) {
                return {
                    success: true,
                    total: 2,
                    total_pages: 1,
                    assets: [
                        { url: '/assets/sample1.png', engine: 'flux_schnell', strategy: 'ai_generation', created_at: '2026-09-18 10:00:00' },
                        { url: '/assets/sample2.png', engine: 'dalle_3', strategy: 'ai_generation', created_at: '2026-09-18 10:05:00' }
                    ]
                };
            }
            return { success: true };
        }
    };
    global.document = documentMock;

    // 1. 加载 syndicate.cover_studio.js
    const coverStudioCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.cover_studio.js', 'utf8');
    eval(coverStudioCode);

    // 2. 验证 openSyndicateAssetPickerModal
    window.openSyndicateAssetPickerModal().then(async () => {
        const pickerModal = elementsById['syndicate-asset-picker-modal'];
        if (!pickerModal) throw new Error('Asset picker modal not created in document');
        if (!pickerModal.classList.contains('is-open')) {
            throw new Error('Asset picker modal missing is-open class');
        }
        if (!pickerModal.className.includes('syndicate-asset-picker-backdrop')) {
            throw new Error('Asset picker modal missing syndicate-asset-picker-backdrop class');
        }

        const pickerHtml = pickerModal.innerHTML;
        const requiredPickerClasses = [
            'syndicate-asset-picker-card',
            'syndicate-asset-picker-header',
            'syndicate-asset-picker-title-group',
            'syndicate-asset-picker-title',
            'syndicate-asset-picker-desc',
            'syndicate-asset-picker-actions',
            'syndicate-asset-picker-studio-btn',
            'syndicate-asset-picker-close-btn',
            'syndicate-asset-picker-scroll-view',
            'syndicate-asset-picker-grid',
            'syndicate-asset-picker-pagination'
        ];
        for (const cls of requiredPickerClasses) {
            if (!pickerHtml.includes(cls)) {
                throw new Error('Asset picker DOM topology missing class: ' + cls);
            }
        }

        // 3. 验证 loadAssetsForCoverPicker 渲染的子卡片与分页
        await window.loadAssetsForCoverPicker(1);
        const gridEl = elementsById['syndicate-asset-picker-grid'];
        const gridHtml = gridEl.innerHTML || '';
        const requiredGridClasses = [
            'syndicate-asset-item',
            'syndicate-asset-thumb-box',
            'syndicate-asset-img',
            'syndicate-asset-engine-tag',
            'syndicate-asset-meta-row',
            'syndicate-asset-engine-name',
            'syndicate-asset-date'
        ];
        for (const cls of requiredGridClasses) {
            if (!gridHtml.includes(cls)) {
                throw new Error('Asset grid DOM topology missing class: ' + cls);
            }
        }

        const pagEl = elementsById['syndicate-asset-picker-pagination'];
        const pagHtml = pagEl.innerHTML || '';
        const requiredPagClasses = [
            'syndicate-asset-picker-page-info',
            'syndicate-asset-picker-page-current',
            'syndicate-asset-picker-page-actions',
            'syndicate-asset-picker-page-btn'
        ];
        for (const cls of requiredPagClasses) {
            if (!pagHtml.includes(cls)) {
                throw new Error('Asset pagination DOM topology missing class: ' + cls);
            }
        }

        // 4. 验证 closeSyndicateAssetPickerModal
        window.closeSyndicateAssetPickerModal();
        if (pickerModal.classList.contains('is-open')) {
            throw new Error('closeSyndicateAssetPickerModal failed to remove is-open class');
        }

        // 5. 验证 showImageModal
        window.showImageModal('https://example.com/original.jpg', '测试封面原图', { ratio: '16:9', strategy: 'ai_generation' });
        const imgModal = elementsById['global-image-detail-modal'];
        if (!imgModal) throw new Error('Global image detail modal not created');
        if (!imgModal.classList.contains('is-open')) {
            throw new Error('Global image detail modal missing is-open class');
        }
        if (!imgModal.className.includes('syndicate-image-detail-backdrop')) {
            throw new Error('Global image detail modal missing syndicate-image-detail-backdrop class');
        }

        const imgModalHtml = imgModal.innerHTML;
        const requiredImgModalClasses = [
            'syndicate-image-detail-card',
            'syndicate-image-detail-header',
            'syndicate-image-detail-title',
            'syndicate-image-detail-close-btn',
            'syndicate-image-detail-viewport',
            'syndicate-image-detail-img',
            'syndicate-image-detail-footer',
            'syndicate-image-detail-meta',
            'syndicate-image-detail-meta-val',
            'syndicate-image-detail-meta-val--purple',
            'syndicate-image-detail-actions',
            'syndicate-image-detail-download-btn',
            'syndicate-image-detail-btn'
        ];
        for (const cls of requiredImgModalClasses) {
            if (!imgModalHtml.includes(cls)) {
                throw new Error('Image detail modal DOM topology missing class: ' + cls);
            }
        }

        // 6. 验证 closeGlobalImageDetailModal
        window.closeGlobalImageDetailModal();
        if (imgModal.classList.contains('is-open')) {
            throw new Error('closeGlobalImageDetailModal failed to remove is-open class');
        }

        console.log('SYNDICATE_ASSET_PICKER_AND_IMAGE_DETAIL_MODAL_VERIFIED_SUCCESS');
    }).catch(e => {
        console.error(e);
        process.exit(1);
    });
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Syndicate Asset Picker & Image Modal Render Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "SYNDICATE_ASSET_PICKER_AND_IMAGE_DETAIL_MODAL_VERIFIED_SUCCESS" in res.stdout



