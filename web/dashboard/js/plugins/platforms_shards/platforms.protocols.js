/**
 * ⚙️ [V109.0] Illacme Plenipes Plugins - AI Protocols Shard
 * 职责：AI 算力通讯协议 (DeepSeek, OpenAI, Gemini, Anthropic, SiliconFlow, Qwen, Zhipu, Kimi, Ollama, LM Studio, LocalAI, OpenRouter, Groq 等) 的配置表单与向导渲染。
 */

var renderSettingsItem = window.renderSettingsItem || (() => "");

// 📡 一键模型资产动态感应与回填算子
window.discoverAIProtocolModels = async (btn, targetNodeId, protocolId) => {
    if (!btn) return;
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '⏳';
    btn.style.opacity = '0.7';

    const drawerBody = document.getElementById('p-drawer-body');
    const urlInput = drawerBody ? drawerBody.querySelector(`[data-path="translation.compute_nodes.${targetNodeId}.base_url"]`) : null;
    const keyInput = drawerBody ? drawerBody.querySelector(`[data-path="translation.compute_nodes.${targetNodeId}.api_key"]`) : null;
    const proxyInput = drawerBody ? drawerBody.querySelector(`[data-path="translation.compute_nodes.${targetNodeId}.proxy"]`) : null;
    const resultBox = document.getElementById(`discovered-models-box-${targetNodeId}`);

    const targetUrl = urlInput ? urlInput.value.trim() : '';
    const targetKey = keyInput ? keyInput.value.trim() : '';
    const targetProxy = proxyInput ? proxyInput.value.trim() : '';

    try {
        const query = new URLSearchParams({
            node_id: targetNodeId,
            provider: protocolId,
            api_key: targetKey,
            base_url: targetUrl,
            proxy: targetProxy
        });

        const fetchFunc = window.apiFetch || (async (u) => (await fetch(u)).json());
        const res = await fetchFunc(`/api/compute/models?${query.toString()}`);

        btn.disabled = false;
        btn.innerHTML = originalHtml;
        btn.style.opacity = '1';

        if (res && res.models && res.models.length > 0) {
            if (resultBox) {
                resultBox.style.display = 'block';
                resultBox.innerHTML = `
                    <div style="font-size: 0.72rem; color: var(--neon-cyan); margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
                        <span>✨ 已动态探测到 <b>${res.models.length}</b> 个模型资产 (点击一键填入):</span>
                        <button type="button" title="收起模型列表" style="background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 0.85rem; padding: 0 4px; line-height: 1; transition: color 0.2s;" onmouseenter="this.style.color='#fff';" onmouseleave="this.style.color='var(--text-dim)';" onclick="document.getElementById('discovered-models-box-${targetNodeId}').style.display='none'">✕</button>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px; max-height: 140px; overflow-y: auto; padding: 2px;">
                        ${res.models.map(m => `
                            <button type="button" class="model-pill-item" onclick="window.selectDiscoveredAIModel('${targetNodeId}', '${m}')" style="background: rgba(0, 242, 254, 0.08); border: 1px solid rgba(0, 242, 254, 0.25); color: #e2e8f0; border-radius: 4px; padding: 3px 8px; font-size: 0.72rem; cursor: pointer; transition: all 0.2s ease; text-align: left; font-family: monospace;">
                                💎 ${m}
                            </button>
                        `).join('')}
                    </div>
                `;
            }
            if (window.showToast) {
                window.showToast(`🟢 成功感应到 ${res.models.length} 个可用模型！`, 'success');
            }
        } else {
            const errMsg = res?.error || res?.message || '未探测到活跃模型，请确认服务已启动且端点可达';
            if (resultBox) {
                resultBox.style.display = 'block';
                resultBox.innerHTML = `
                    <div style="font-size: 0.72rem; color: #ff4d4f; padding: 4px 0; display: flex; justify-content: space-between; align-items: center;">
                        <span>❌ 感应失败: ${errMsg}</span>
                        <button type="button" title="关闭提示" style="background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 0.85rem; padding: 0 4px; line-height: 1; transition: color 0.2s;" onmouseenter="this.style.color='#fff';" onmouseleave="this.style.color='var(--text-dim)';" onclick="document.getElementById('discovered-models-box-${targetNodeId}').style.display='none'">✕</button>
                    </div>
                `;
            }
            if (window.showToast) {
                window.showToast(`⚠️ 模型感应失败: ${errMsg}`, 'warning');
            }
        }
    } catch (e) {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
        btn.style.opacity = '1';
        if (resultBox) {
            resultBox.style.display = 'block';
            resultBox.innerHTML = `
                <div style="font-size: 0.72rem; color: #ff4d4f; padding: 4px 0; display: flex; justify-content: space-between; align-items: center;">
                    <span>❌ 探测异常: ${e.message}</span>
                    <button type="button" title="关闭提示" style="background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 0.85rem; padding: 0 4px; line-height: 1; transition: color 0.2s;" onmouseenter="this.style.color='#fff';" onmouseleave="this.style.color='var(--text-dim)';" onclick="document.getElementById('discovered-models-box-${targetNodeId}').style.display='none'">✕</button>
                </div>
            `;
        }
    }
};

window.selectDiscoveredAIModel = (targetNodeId, modelName) => {
    const drawerBody = document.getElementById('p-drawer-body');
    const modelInput = drawerBody ? drawerBody.querySelector(`[data-path="translation.compute_nodes.${targetNodeId}.model"]`) : null;
    if (modelInput) {
        modelInput.value = modelName;
        modelInput.dispatchEvent(new Event('input', { bubbles: true }));
        modelInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        // 发光微交互
        modelInput.style.borderColor = 'var(--neon-cyan)';
        modelInput.style.boxShadow = '0 0 12px rgba(0, 242, 254, 0.4)';
        setTimeout(() => {
            modelInput.style.borderColor = '';
            modelInput.style.boxShadow = '';
        }, 1200);

        if (window.showToast) {
            window.showToast(`✅ 已填入模型: ${modelName}`, 'success');
        }
    }
};

window.rawRenderAIProtocolConfig = (id, protoMeta = {}) => {
    const cleanId = (id || '').toLowerCase();
    const computeNodes = window.settingsData?.translation?.compute_nodes || {};

    // 寻找当前系统中是否已存在绑定此协议的算力节点
    let targetNodeId = cleanId;
    let matchedNode = null;

    if (computeNodes[cleanId]) {
        targetNodeId = cleanId;
        matchedNode = computeNodes[cleanId];
    } else {
        for (const [nId, nData] of Object.entries(computeNodes)) {
            if (nData && (nData.type === cleanId || nData.provider === cleanId)) {
                targetNodeId = nId;
                matchedNode = nData;
                break;
            }
        }
    }

    const nodeCfg = matchedNode || {};
    
    // 优先读取用户已保存并修改的端点，若无则使用默认预设端点
    let fallbackDefaultUrl = protoMeta.default_url || "";
    if (!fallbackDefaultUrl) {
        if (cleanId === 'lmstudio') fallbackDefaultUrl = 'http://localhost:1234/v1';
        else if (cleanId === 'ollama') fallbackDefaultUrl = 'http://localhost:11434';
        else if (cleanId === 'localai') fallbackDefaultUrl = 'http://localhost:8080/v1';
    }
    const currentBaseUrl = nodeCfg.base_url || fallbackDefaultUrl || "";
    let currentApiKey = nodeCfg.api_key || "";
    if (currentApiKey.includes('PUT_YOUR_KEY_HERE') || currentApiKey.includes('your_key') || currentApiKey.includes('placeholder')) {
        currentApiKey = "";
    }
    const currentModel = nodeCfg.model || "";
    const currentProxy = nodeCfg.proxy || "";
    const currentTemp = nodeCfg.temperature !== undefined ? nodeCfg.temperature : 0.7;
    const currentMaxTokens = nodeCfg.max_tokens || 4096;

    // 智能判定本地私有化协议或内网节点
    const isLocalProto = cleanId === 'ollama' || cleanId === 'lmstudio' || cleanId === 'localai' ||
        currentBaseUrl.includes('localhost') || currentBaseUrl.includes('127.0.0.1') || currentBaseUrl.includes('0.0.0.0');

    // 1. 各官方协议极简申请向导字典
    let helperHtml = '';
    if (cleanId === 'lmstudio') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 本地 LM Studio 私有化大模型向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">LM Studio 提供零代码本地大模型推断服务。默认端口为 <code>http://localhost:1234/v1</code>。局域网其他机器部署时填写对应 IP 端点（如 <code>http://192.168.1.x:1234/v1</code>）。<strong>本地私有化部署无需填写 API Key</strong>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://lmstudio.ai/" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 LM Studio 官网下载与指引</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'ollama') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 本地 Ollama 私有化向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">本地轻量运行 Llama 3、DeepSeek-R1、Qwen2.5 等开源模型。默认端点为 <code>http://localhost:11434</code>，<strong>无需填写 API 密钥</strong>。支持自定义局域网端点。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://ollama.com/" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 Ollama 官网与模型库</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'localai') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 LocalAI 自建私有化算力向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">开源免费、Drop-in 替代 OpenAI 的本地推理框架。默认端点为 <code>http://localhost:8080/v1</code>，内网部署无需 API Key。</p>
            </div>
        `;
    } else if (cleanId === 'deepseek') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 DeepSeek (深度求索) 开放平台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">DeepSeek 提供极高性价比的深度推理与通用代码能力。推荐默认模型: <code>deepseek-chat</code> 或 <code>deepseek-reasoner</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://platform.deepseek.com/api_keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 DeepSeek API Keys 管理页</a>
                    <a href="https://api-docs.deepseek.com/" target="_blank" class="helper-btn" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.15); color: var(--text-dim); padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem;">📚 官方接口文档</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'openai') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 OpenAI 官方平台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">全球标准 OpenAI 协议基座。推荐模型: <code>gpt-4o</code>, <code>gpt-4o-mini</code> 或 <code>o1-preview</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://platform.openai.com/api-keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 OpenAI API Keys 申请页</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'gemini' || cleanId.includes('google')) {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 Google AI Studio 向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">超长上下文与多模态原生大模型。推荐模型: <code>gemini-1.5-pro</code>, <code>gemini-1.5-flash</code> 或 <code>gemini-2.0-flash</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://aistudio.google.com/app/apikey" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Google AI Studio API 密钥页</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'anthropic' || cleanId.includes('claude')) {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 Anthropic Claude 控制台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">顶级文学装帧与翻译推理引擎。推荐模型: <code>claude-3-5-sonnet-latest</code> 或 <code>claude-3-5-haiku-latest</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://console.anthropic.com/settings/keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Anthropic API Keys 管理页</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'siliconflow') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 硅基流动 (SiliconFlow) 开发者向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">提供高并发低延迟的开源主流大模型托管（Qwen, DeepSeek, GLM 等全品类一键直通）。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://cloud.siliconflow.cn/account/ak" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达硅基流动 API 密钥申请</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'dashscope' || cleanId.includes('qwen')) {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 阿里云百炼 (DashScope / 通义千问) 向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">阿里云原生千问算力矩阵。推荐模型: <code>qwen-plus</code>, <code>qwen-max</code> 或 <code>qwen-turbo</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://bailian.console.aliyun.com/" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达阿里云百炼控制台</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'zhipu') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 智谱 BigModel 开放平台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">国产基座大模型 GLM 协议。推荐模型: <code>glm-4-plus</code>, <code>glm-4-flash</code> 或 <code>glm-4-air</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://open.bigmodel.cn/usercenter/apikeys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达智谱 API Key 申请页</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'moonshot') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 月之暗面 (Moonshot / Kimi) 向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">长文本与推理专用。推荐模型: <code>moonshot-v1-8k</code>, <code>moonshot-v1-32k</code> 或 <code>moonshot-v1-128k</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://platform.moonshot.cn/console/api-keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Moonshot API 密钥页</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'openrouter') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 OpenRouter 聚合算力向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">一把密钥聚合全球 200+ 顶级大模型。推荐模型: <code>anthropic/claude-3.5-sonnet</code>, <code>deepseek/deepseek-r1</code> 等。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://openrouter.ai/keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 OpenRouter API Keys 页</a>
                </div>
            </div>
        `;
    } else if (cleanId === 'groq') {
        helperHtml = `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 Groq LPU 极速推理向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">提供每秒数百 Token 的超高速 LPU 硬件推理。推荐模型: <code>llama-3.3-70b-versatile</code>, <code>mixtral-8x7b-32768</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://console.groq.com/keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 GroqCloud Keys 申请页</a>
                </div>
            </div>
        `;
    }

    // 注入隐藏的固定类型与启用状态，确保表单提交时数据结构完整
    const hiddenFields = `
        <input type="hidden" data-path="translation.compute_nodes.${targetNodeId}.type" value="${cleanId}">
        <input type="hidden" data-path="translation.compute_nodes.${targetNodeId}.enabled" value="true">
    `;

    const apiKeyLabel = isLocalProto ? '物理密钥 (API Key) (可选)' : '物理密钥 (API Key)';
    const apiKeyPlaceholder = isLocalProto ? "本地/私有化部署无需填写 (留空)" : "请输入 API Key 或 Token";

    // 🚀 [V109.2] 严格遵循标准 setting-row 双栏网格架构（左侧 info / 右侧 control），杜绝布局挤压错乱
    const modelRowHtml = `
        <div class="setting-row level-live">
            <div class="setting-info" style="flex: 2; min-width: 260px;">
                <div class="setting-label">
                    <span>默认推理模型 (Model ID)</span>
                    <span class="badge-group"><span class="effect-icon effect-live" title="🟢 即刻生效">🟢</span></span>
                </div>
                <div class="setting-desc">主权出版与翻译治理时调用的默认模型。支持直接输入或点击右侧 📡 图标感应。</div>
            </div>
            <div class="setting-control" style="flex: 1.8; min-width: 220px; display: flex; flex-direction: column; gap: 6px; width: 100%;">
                <div style="display: flex; gap: 8px; width: 100%; align-items: center;">
                    <input type="text" class="setting-input" data-path="translation.compute_nodes.${targetNodeId}.model" value="${currentModel}" placeholder="例如: ${cleanId === 'lmstudio' ? 'qwen/qwen3.5-9b' : (cleanId === 'ollama' ? 'llama3:latest' : 'deepseek-chat')}" style="flex: 1; min-width: 0;">
                    <button type="button" class="btn-discover-models" onclick="window.discoverAIProtocolModels(this, '${targetNodeId}', '${cleanId}')" title="📡 动态感应并拉取端点已加载的模型资产 (Model Discovery)" style="background: rgba(0, 242, 254, 0.1); border: 1px solid rgba(0, 242, 254, 0.35); color: var(--neon-cyan); border-radius: 6px; width: 36px; height: 36px; min-width: 36px; display: inline-flex; align-items: center; justify-content: center; font-size: 1rem; cursor: pointer; flex-shrink: 0; transition: all 0.2s ease;" onmouseenter="this.style.background='rgba(0, 242, 254, 0.22)'; this.style.borderColor='var(--neon-cyan)'; this.style.boxShadow='0 0 10px rgba(0, 242, 254, 0.3)';" onmouseleave="this.style.background='rgba(0, 242, 254, 0.1)'; this.style.borderColor='rgba(0, 242, 254, 0.35)'; this.style.boxShadow='none';">
                        📡
                    </button>
                </div>
                <div id="discovered-models-box-${targetNodeId}" style="display: none; width: 100%; margin-top: 4px; padding: 10px; border-radius: 6px; background: rgba(0, 0, 0, 0.45); border: 1px solid var(--glass-border); box-shadow: inset 0 0 10px rgba(0,0,0,0.5);"></div>
            </div>
        </div>
    `;

    return `
        ${helperHtml}
        ${hiddenFields}
        ${renderSettingsItem(apiKeyLabel, `translation.compute_nodes.${targetNodeId}.api_key`, currentApiKey, 'password', {
            placeholder: apiKeyPlaceholder,
            description: isLocalProto ? "可选。本地或私有化部署节点默认无需鉴权密钥。" : "用于调用该协议服务商 API 的鉴权物理凭证。"
        })}
        ${renderSettingsItem('端点地址 (Endpoint / Base URL)', `translation.compute_nodes.${targetNodeId}.base_url`, currentBaseUrl, 'text', {
            placeholder: "例如: " + (fallbackDefaultUrl || "https://api.example.com/v1"),
            description: "服务商 API 请求的基础接入点地址。支持自定义本地、局域网或云端网关端点。"
        })}
        ${modelRowHtml}
        ${window.renderPlatformAdvancedGroup('高级采样与独立代理参数 (可选)', `
            ${renderSettingsItem('独立代理地址 (Proxy)', `translation.compute_nodes.${targetNodeId}.proxy`, currentProxy, 'text', {
                placeholder: "例如: http://127.0.0.1:10809 或 direct",
                description: "可选。针对当前算力渠道配置独立网络代理通道，填写 direct 表示强制直连。"
            })}
            ${renderSettingsItem('采样温度 (Temperature)', `translation.compute_nodes.${targetNodeId}.temperature`, currentTemp, 'number', {
                placeholder: "0.7",
                description: "控制生成随机性。翻译与合规推荐 0.3~0.7，创意写作推荐 0.7~1.0。"
            })}
            ${renderSettingsItem('单次最大输出 (Max Tokens)', `translation.compute_nodes.${targetNodeId}.max_tokens`, currentMaxTokens, 'number', {
                placeholder: "4096",
                description: "单次推理生成允许的最大 Token 数量。"
            })}
        `)}
    `;
};

window.renderAIProtocolConfig = (id, protoMeta = {}) => {
    return window.rawRenderAIProtocolConfig ? window.rawRenderAIProtocolConfig(id, protoMeta) : '';
};
