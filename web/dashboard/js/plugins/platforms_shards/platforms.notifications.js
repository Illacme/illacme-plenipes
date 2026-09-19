/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Notification Adapters One-Click UX Shard
 * 职责：消息通知插件 (飞书, 钉钉, 企微, Telegram, Discord, Email, SMS, App Push, Generic, Dispatcher) 极简单 URL 模式与 3 秒上手向导卡片。
 * 订阅中枢与预设交互已抽离至 platforms.notifications.events.js。
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
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 Telegram 运维告警 Bot 获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">面向<b>站长与运维人员</b>：在 Telegram 中联系 <b>@BotFather</b> -> 发送 <code>/newbot</code> -> 复制生成的 Bot Token 并填入管理员频道或运维群组 ID，即可实时接收全站编译就绪与故障告警。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <a href="https://t.me/BotFather" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">💬 一键唤醒 BotFather 创建机器人</a>
                </div>
            </div>
            ${renderSettingsItem('机器人 Token (Bot Token)', `publish_control.webhook_endpoints.${id}.bot_token`, cfg.bot_token || cfg.token || "", 'password', { placeholder: "例如: 123456789:ABCdefGhIJKlmNoPQRsT", description: "@BotFather 给予的机器人 Token。" })}
            ${renderSettingsItem('运维频道/群组 ID (Chat ID)', `publish_control.webhook_endpoints.${id}.chat_id`, cfg.chat_id || "", 'text', { placeholder: "例如: @my_ops_channel 或 -100123456789", description: "面向站长/运维：接收系统运维与告警消息的频道或群组 ID。" })}
        `;
    } else if (cleanId === 'discord' || cleanId.includes('discord')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 Discord 运维告警 Webhook 获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">面向<b>站长与运维人员</b>：进入管理员 Discord 频道 (⚙️) -> Integrations (整合) -> Webhooks -> Create Webhook -> 点击 Copy Webhook URL 粘贴至下方，即可实时接收全站编译就绪与 AI 算力熔断告警。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <a href="https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 Discord 官方 Webhook 图文向导</a>
                </div>
            </div>
            ${renderSettingsItem('运维通知 Webhook (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || cfg.webhook_url || "", 'text', { placeholder: "例如: https://discord.com/api/webhooks/xxxxxxxx/xxxxxxxx", description: "面向站长/运维：复制用于接收系统运维事件与故障告警的 Discord 频道 Webhook URL。" })}
        `;
    } else if (cleanId === 'email' || cleanId.includes('smtp') || cleanId.includes('mail')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 常用邮箱 SMTP 极简配置向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">
                    • <b>QQ 邮箱</b>: 主机 <code>smtp.qq.com</code> | 端口 <code>465</code> (SSL) | 密码为 <b>POP3/SMTP 授权码</b><br>
                    • <b>163 邮箱</b>: 主机 <code>smtp.163.com</code> | 端口 <code>465</code> (SSL) | 密码为 <b>客户端授权密码</b><br>
                    • <b>Gmail</b>: 主机 <code>smtp.gmail.com</code> | 端口 <code>587</code> (TLS) | 密码为 <b>Google 账户应用专用密码</b>
                </p>
            </div>
            ${renderSettingsItem('发信邮箱账号 (User)', `publish_control.webhook_endpoints.${id}.smtp_user`, cfg.smtp_user || "", 'text', { placeholder: "例如: your_name@qq.com", description: "用于登录 SMTP 服务器的邮箱账号。" })}
            ${renderSettingsItem('授权码 / 邮箱密码 (Password)', `publish_control.webhook_endpoints.${id}.smtp_pass`, cfg.smtp_pass || "", 'password', { placeholder: "邮箱授权码或应用专用密码", description: "建议在邮箱设置中生成独立的第三方客户端授权码。" })}
            ${renderSettingsItem('SMTP 服务器主机 (Host)', `publish_control.webhook_endpoints.${id}.smtp_host`, cfg.smtp_host || "", 'text', { placeholder: "例如: smtp.qq.com / smtp.163.com / smtp.gmail.com", description: "邮件服务商的 SMTP 服务器地址。" })}
            ${renderSettingsItem('SMTP 端口 (Port)', `publish_control.webhook_endpoints.${id}.smtp_port`, cfg.smtp_port || 465, 'number', { placeholder: "465 (SSL) 或 587 (TLS)", description: "通常 SSL 为 465，STARTTLS 为 587，明文为 25。" })}
            ${renderSettingsItem('启用 SSL 加密', `publish_control.webhook_endpoints.${id}.use_ssl`, cfg.use_ssl !== false, 'boolean', { description: "启用后将建立安全的 SSL/TLS 传输通道。" })}
            ${renderSettingsItem('接收者邮箱列表 (Receivers)', `publish_control.webhook_endpoints.${id}.receivers`, cfg.receivers || "", 'text', { placeholder: "例如: admin@example.com, alerts@domain.com (逗号分隔)", description: "接收出版通知与运维告警的目标邮箱地址。" })}
            ${window.renderPlatformAdvancedGroup('高级发件人参数', `
                ${renderSettingsItem('发件人显示地址 (Sender)', `publish_control.webhook_endpoints.${id}.sender`, cfg.sender || "", 'text', { placeholder: "例如: noreply@yourdomain.com (留空则同账号)", description: "邮件头部显示的 From 发件人地址。" })}
            `)}
        `;
    } else if (cleanId === 'sms' || cleanId.includes('sms')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 云短信与紧急告警向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">面向<b>关键出版任务与算力熔断告警</b>：支持阿里云短信、腾讯云短信、Twilio 或自建 HTTP 短信网关直接推送到手机短信。</p>
            </div>
            ${renderSettingsItem('短信服务商 (Provider)', `publish_control.webhook_endpoints.${id}.provider`, cfg.provider || "aliyun", 'select', { options: [{ value: "aliyun", label: "阿里云短信 (Aliyun SMS)" }, { value: "tencent", label: "腾讯云短信 (Tencent SMS)" }, { value: "twilio", label: "Twilio 短信 (Global)" }, { value: "http_gateway", label: "通用 HTTP 短信网关" }], description: "选择您所使用的云短信服务商。" })}
            ${renderSettingsItem('AccessKey ID / API Key', `publish_control.webhook_endpoints.${id}.access_key_id`, cfg.access_key_id || "", 'text', { placeholder: "云服务商 AccessKey ID 或 API Key", description: "用于调用短信服务 API 的鉴权公钥/账号。" })}
            ${renderSettingsItem('AccessKey Secret / Auth Token', `publish_control.webhook_endpoints.${id}.access_key_secret`, cfg.access_key_secret || "", 'password', { placeholder: "云服务商 AccessKey Secret 或 Auth Token", description: "用于签名计算的私钥凭据。" })}
            ${renderSettingsItem('目标手机号列表 (Phones)', `publish_control.webhook_endpoints.${id}.phone_numbers`, cfg.phone_numbers || "", 'text', { placeholder: "例如: +8613800000000, +8613900000000", description: "用于接收紧急告警短信的手机号列表，以逗号分隔。" })}
            ${renderSettingsItem('短信签名 (Sign Name)', `publish_control.webhook_endpoints.${id}.sign_name`, cfg.sign_name || "【极速出版】", 'text', { placeholder: "例如: 【极速出版】", description: "在短信运营商处审核通过的短信签名。" })}
            ${renderSettingsItem('模板代码 (Template Code)', `publish_control.webhook_endpoints.${id}.template_code`, cfg.template_code || "", 'text', { placeholder: "例如: SMS_123456789", description: "在运营商后台申请的短信通知模板 ID。" })}
            ${window.renderPlatformAdvancedGroup('高级网关参数', `
                ${renderSettingsItem('API 网关端点 (URL)', `publish_control.webhook_endpoints.${id}.api_url`, cfg.api_url || "", 'text', { placeholder: "例如: https://sms.yourdomain.com/send", description: "自建短信网关端点，或第三方云短信 API 代理地址。" })}
            `)}
        `;
    } else if (cleanId === 'app_push' || cleanId.includes('bark') || cleanId.includes('push')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 移动端推送极速获取向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">
                    • <b>Bark (iOS)</b>: 打开 Bark App -> 复制屏幕上的 <code>Device Key</code><br>
                    • <b>Server酱 (微信)</b>: 访问 <a href="https://sct.ftqq.com/" target="_blank" style="color:var(--neon-cyan);">sct.ftqq.com</a> -> 扫码绑定 -> 获取 <code>SendKey</code><br>
                    • <b>Gotify (自建)</b>: 进入 Gotify WebUI -> Apps -> Create App -> 复制 <code>App Token</code>
                </p>
            </div>
            ${renderSettingsItem('推送平台 (Push Provider)', `publish_control.webhook_endpoints.${id}.push_provider`, cfg.push_provider || "bark", 'select', { options: [{ value: "bark", label: "Bark (iOS 极速推送)" }, { value: "serverchan", label: "Server酱 (微信通知)" }, { value: "gotify", label: "Gotify (私有化服务器)" }, { value: "pushover", label: "Pushover (全平台推送)" }, { value: "custom", label: "自定义 Push 端点" }], description: "选择您所使用的移动端或桌面推送平台。" })}
            ${renderSettingsItem('设备 Key / Token / SendKey', `publish_control.webhook_endpoints.${id}.device_key`, cfg.device_key || "", 'password', { placeholder: "粘贴您的 Bark Key / Server酱 SendKey / Gotify Token", description: "用于投递消息至特定设备或频道的授权密钥。" })}
            ${window.renderPlatformAdvancedGroup('高级自建服务器与音效参数', `
                ${renderSettingsItem('自建服务器地址 (Server URL)', `publish_control.webhook_endpoints.${id}.server_url`, cfg.server_url || "", 'text', { placeholder: "留空默认官方云 (例如 Gotify: https://gotify.yourdomain.com)", description: "若使用私有化自建的 Bark / Gotify 服务，请在此填入完整根地址。" })}
                ${renderSettingsItem('提示音效 (Sound)', `publish_control.webhook_endpoints.${id}.sound`, cfg.sound || "glass", 'select', { options: [{ value: "glass", label: "清脆玻璃 (Glass - 默认)" }, { value: "minuet", label: "优雅小步舞曲 (Minuet)" }, { value: "bell", label: "风铃 (Bell)" }, { value: "alarm", label: "高优先级警报 (Alarm)" }, { value: "silence", label: "静默推送 (Silence)" }], description: "移动设备收到推送时的提示音效（仅支持 Bark / Pushover）。" })}
                ${renderSettingsItem('消息分组 (Group)', `publish_control.webhook_endpoints.${id}.group`, cfg.group || "Illacme-Plenipes", 'text', { placeholder: "例如: Illacme-Plenipes", description: "iOS 通知中心折叠归类的消息分组名称。" })}
            `)}
        `;
    } else if (cleanId === 'generic_webhook' || cleanId === 'generic' || cleanId.includes('generic')) {
        html += `
            ${renderSettingsItem('物理端点 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://yourdomain.com/api/v1/webhook", description: "接收系统事件通知的物理 HTTP/HTTPS 接口地址。" })}
            ${window.renderPlatformAdvancedGroup('高级签名密钥', `
                ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "防伪造签名 Secret (可选)", description: "可选。填写后系统将在 HTTP 标头中注入带 HMAC-SHA256 签名的凭据。" })}
            `)}
        `;
    } else if (cleanId === 'webhook_dispatch' || cleanId.includes('dispatch') || cleanId.includes('webhook')) {
        html += `
            ${renderSettingsItem('触发端点 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://ci.yourdomain.com/hooks/publish-complete", description: "下游 CI/CD、n8n、Make 或 Jenkins 的触发 Webhook URL。" })}
            ${window.renderPlatformAdvancedGroup('高级签名密钥', `
                ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "签名 Secret (可选)", description: "可选。用于下游校验信号合规性。" })}
            `)}
        `;
    }

    // 🚀 [全渠道事件过滤] 统一追加生命周期广播事件订阅卡片 (由 platforms.notifications.events.js 供给)
    const defaultEvents = (cleanId === 'sms') ? ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'] : ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'];
    if (window.renderLifecycleEventsSubscription) {
        html += window.renderLifecycleEventsSubscription(id, cfg, defaultEvents);
    }

    return html;
};
