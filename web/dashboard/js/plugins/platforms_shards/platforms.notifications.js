/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Notification Adapters One-Click UX Shard
 * 职责：消息通知插件 (飞书, 钉钉, 企微, Telegram, Discord, Generic, Dispatcher) 极简单 URL 模式与 3 秒上手向导卡片。
 */

var renderSettingsItem = window.renderSettingsItem || (() => "");

window.rawRenderNotificationConfig = (id, cfg) => {
    let html = '';
    const cleanId = (id || '').toLowerCase();

    if (cleanId === 'feishu' || cleanId.includes('feishu')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 飞书机器人 3 秒获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">打开飞书电脑端 -> 任意群聊右上角 [...] -> 群机器人 -> 添加机器人 -> 选择“自定义机器人” -> 复制 Webhook 地址粘贴至下方即可。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <a href="https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 飞书官方机器人向导文档</a>
                </div>
            </div>
            ${renderSettingsItem('Webhook 地址 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx", description: "粘贴飞书群机器人生成的 Webhook 完整链接即可直接工作。" })}
            ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "无签名校验可留空 (可选)", description: "若在飞书机器人安全设置中开启了“签名校验”，请将密钥粘贴在此处。" })}
        `;
    } else if (cleanId === 'dingtalk' || cleanId.includes('dingtalk')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 钉钉机器人 3 秒获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">打开钉钉电脑端 -> 目标群聊右上角 -> 智能群助手 -> 添加机器人 -> 选择“自定义机器人” -> 复制 Webhook 地址粘贴至下方即可。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <a href="https://open.dingtalk.com/document/robots/custom-robot-access" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 钉钉官方机器人向导文档</a>
                </div>
            </div>
            ${renderSettingsItem('Webhook 地址 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://oapi.dingtalk.com/robot/send?access_token=xxxxxx", description: "粘贴钉钉群机器人生成的 Webhook 完整链接即可直接工作。" })}
            ${renderSettingsItem('加签密钥 (Sign Secret)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "例如: SECxxxxxxxxxxxx (无加签校验可留空)", description: "若在钉钉机器人安全设置中勾选了“加签”，请填入以 SEC 开头的密钥。" })}
        `;
    } else if (cleanId === 'wecom' || cleanId.includes('wecom')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 企业微信机器人 3 秒获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">打开企业微信 -> 进入目标群聊 -> 点击右上角 [...] -> 添加群机器人 -> 新建机器人 -> 复制 Webhook 地址粘贴至下方即可。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <a href="https://developer.work.weixin.qq.com/document/path/91770" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 企业微信官方机器人向导文档</a>
                </div>
            </div>
            ${renderSettingsItem('Webhook 地址 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxx", description: "粘贴企业微信机器人生成的 Webhook 完整链接即可直接工作。" })}
        `;
    } else if (cleanId === 'telegram' || cleanId.includes('telegram')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 Telegram Bot 3 秒获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">在 Telegram 中搜索并联系 <b>@BotFather</b> -> 发送 <code>/newbot</code> -> 复制生成的 Bot Token 并填入目标频道或群组 Username (@your_channel) 即可。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <a href="https://t.me/BotFather" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">💬 一键唤醒 BotFather 创建机器人</a>
                </div>
            </div>
            ${renderSettingsItem('机器人 Token (Bot Token)', `publish_control.webhook_endpoints.${id}.bot_token`, cfg.bot_token || cfg.token || "", 'password', { placeholder: "例如: 123456789:ABCdefGhIJKlmNoPQRsT", description: "@BotFather 给予的机器人Token。" })}
            ${renderSettingsItem('目标频道/群组 ID (Chat ID)', `publish_control.webhook_endpoints.${id}.chat_id`, cfg.chat_id || "", 'text', { placeholder: "例如: @my_channel 或 -100123456789", description: "接收消息的频道 Username (@开头) 或群组数字 ID。" })}
        `;
    } else if (cleanId === 'discord' || cleanId.includes('discord')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 Discord Webhook 3 秒获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">进入 Discord 服务器 -> 目标频道设置 (⚙️) -> Integrations (整合) -> Webhooks -> Create Webhook (新建 Webhook) -> 点击 Copy Webhook URL 并粘贴至下方即可。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <a href="https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 Discord 官方 Webhook 图文向导</a>
                </div>
            </div>
            ${renderSettingsItem('Webhook 地址 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || cfg.webhook_url || "", 'text', { placeholder: "例如: https://discord.com/api/webhooks/xxxxxxxx/xxxxxxxx", description: "复制 Discord 频道中的 Webhook 完整 URL 粘贴至此处。" })}
        `;
    } else if (cleanId === 'generic' || cleanId.includes('generic')) {
        html += `
            ${renderSettingsItem('物理端点 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://yourdomain.com/api/v1/webhook", description: "接收系统事件通知的物理 HTTP/HTTPS 接口地址。" })}
            ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "防伪造签名 Secret (可选)", description: "可选。填写后系统将在 HTTP 标头中注入带 HMAC-SHA256 签名的凭据。" })}
        `;
    } else if (cleanId === 'webhook_dispatch' || cleanId.includes('dispatch') || cleanId.includes('webhook')) {
        html += `
            ${renderSettingsItem('触发端点 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://ci.yourdomain.com/hooks/publish-complete", description: "下游 CI/CD、n8n、Make 或 Jenkins 的触发 Webhook URL。" })}
            ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "签名 Secret (可选)", description: "可选。用于下游校验信号合规性。" })}
        `;
    } else {
        // 🚀 [严格防穿透] 消息通知分类专属全防降级表单
        html += `
            ${renderSettingsItem('Webhook 地址 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://yourdomain.com/webhook", description: "粘贴消息通知端点的完整 Webhook 地址。" })}
            ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "签名 Secret (可选)", description: "可选。用于安全校验。" })}
        `;
    }

    return html;
};
