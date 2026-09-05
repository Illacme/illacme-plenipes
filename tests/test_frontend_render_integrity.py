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
        querySelectorAll: () => []
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
    window.ComputeUI.renderInfrastructureTabImpl(fakeContainer).then(() => {
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
        if (lpHtml.includes('lpwiz-footer-note')) {
            throw new Error('Launchpad onboarding should not have redundant footer note');
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
