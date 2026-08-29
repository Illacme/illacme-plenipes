import subprocess
import json
import pytest
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
        console.log('ALL_FRONTEND_RENDER_DOM_VERIFIED_SUCCESS');
    }).catch(err => {
        console.error(err);
        process.exit(1);
    });
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Frontend Render Runtime Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "ALL_FRONTEND_RENDER_DOM_VERIFIED_SUCCESS" in res.stdout
