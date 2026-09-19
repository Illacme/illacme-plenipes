/**
 * 💡 [V109.0] Illacme Plenipes Plugins - AI Protocol Token Helper Shard
 * 职责：提供各主流大模型算力协议厂商 (LM Studio, Ollama, LocalAI, DeepSeek, OpenAI, Gemini, Anthropic, SiliconFlow, DashScope, Zhipu, Moonshot, OpenRouter, Groq 等) 的极简申请向导卡片与直达魔术链接。
 */

window.getAIProtocolHelperHtml = (cleanId) => {
    cleanId = (cleanId || '').toLowerCase();
    
    if (cleanId === 'lmstudio') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 本地 LM Studio 私有化大模型向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">LM Studio 提供零代码本地大模型推断服务。默认端口为 <code>http://localhost:1234/v1</code>。局域网其他机器部署时填写对应 IP 端点（如 <code>http://192.168.1.x:1234/v1</code>）。<strong>本地私有化部署无需填写 API Key</strong>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://lmstudio.ai/" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 LM Studio 官网下载与指引</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'ollama') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 本地 Ollama 私有化向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">本地轻量运行 Llama 3、DeepSeek-R1、Qwen2.5 等开源模型。默认端点为 <code>http://localhost:11434</code>，<strong>无需填写 API 密钥</strong>。支持自定义局域网端点。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://ollama.com/" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 Ollama 官网与模型库</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'localai') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 LocalAI 自建私有化算力向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">开源免费、Drop-in 替代 OpenAI 的本地推理框架。默认端点为 <code>http://localhost:8080/v1</code>，内网部署无需 API Key。</p>
            </div>
        `;
    }
    if (cleanId === 'deepseek') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 DeepSeek (深度求索) 开放平台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">DeepSeek 提供极高性价比的深度推理与通用代码能力。推荐默认模型: <code>deepseek-chat</code> 或 <code>deepseek-reasoner</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://platform.deepseek.com/api_keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 DeepSeek API Keys 管理页</a>
                    <a href="https://api-docs.deepseek.com/" target="_blank" class="helper-btn" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.15); color: var(--text-dim); padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem;">📚 官方接口文档</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'openai') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 OpenAI 官方平台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">全球标准 OpenAI 协议基座。推荐模型: <code>gpt-4o</code>, <code>gpt-4o-mini</code> 或 <code>o1-preview</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://platform.openai.com/api-keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 OpenAI API Keys 申请页</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'gemini' || cleanId.includes('google')) {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 Google AI Studio 向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">超长上下文与多模态原生大模型。推荐模型: <code>gemini-1.5-pro</code>, <code>gemini-1.5-flash</code> 或 <code>gemini-2.0-flash</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://aistudio.google.com/app/apikey" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Google AI Studio API 密钥页</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'anthropic' || cleanId.includes('claude')) {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 Anthropic Claude 控制台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">顶级文学装帧与翻译推理引擎。推荐模型: <code>claude-3-5-sonnet-latest</code> 或 <code>claude-3-5-haiku-latest</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://console.anthropic.com/settings/keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Anthropic API Keys 管理页</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'siliconflow') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 硅基流动 (SiliconFlow) 开发者向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">提供高并发低延迟的开源主流大模型托管（Qwen, DeepSeek, GLM 等全品类一键直通）。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://cloud.siliconflow.cn/account/ak" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达硅基流动 API 密钥申请</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'dashscope' || cleanId.includes('qwen')) {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 阿里云百炼 (DashScope / 通义千问) 向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">阿里云原生千问算力矩阵。推荐模型: <code>qwen-plus</code>, <code>qwen-max</code> 或 <code>qwen-turbo</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://bailian.console.aliyun.com/" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达阿里云百炼控制台</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'zhipu') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 智谱 BigModel 开放平台向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">国产基座大模型 GLM 协议。推荐模型: <code>glm-4-plus</code>, <code>glm-4-flash</code> 或 <code>glm-4-air</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://open.bigmodel.cn/usercenter/apikeys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达智谱 API Key 申请页</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'moonshot') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 月之暗面 (Moonshot / Kimi) 向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">长文本与推理专用。推荐模型: <code>moonshot-v1-8k</code>, <code>moonshot-v1-32k</code> 或 <code>moonshot-v1-128k</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://platform.moonshot.cn/console/api-keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Moonshot API 密钥页</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'openrouter') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 OpenRouter 聚合算力向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">一把密钥聚合全球 200+ 顶级大模型。推荐模型: <code>anthropic/claude-3.5-sonnet</code>, <code>deepseek/deepseek-r1</code> 等。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://openrouter.ai/keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 OpenRouter API Keys 页</a>
                </div>
            </div>
        `;
    }
    if (cleanId === 'groq') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan); display: flex; align-items: center; gap: 6px;">💡 Groq LPU 极速推理向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim);">提供每秒数百 Token 的超高速 LPU 硬件推理。推荐模型: <code>llama-3.3-70b-versatile</code>, <code>mixtral-8x7b-32768</code>。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://console.groq.com/keys" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 GroqCloud Keys 申请页</a>
                </div>
            </div>
        `;
    }

    return '';
};
