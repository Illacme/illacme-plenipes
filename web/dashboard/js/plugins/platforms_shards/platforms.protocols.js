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

    // 1. 各官方协议极简申请向导 (由 platforms.protocols.helpers.js 供给)
    const helperHtml = window.getAIProtocolHelperHtml ? window.getAIProtocolHelperHtml(cleanId) : '';


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
