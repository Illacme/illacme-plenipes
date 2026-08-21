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
            ${renderSettingsItem('SMTP 服务器主机 (Host)', `publish_control.webhook_endpoints.${id}.smtp_host`, cfg.smtp_host || "", 'text', { placeholder: "例如: smtp.qq.com / smtp.163.com / smtp.gmail.com", description: "邮件服务商的 SMTP 服务器地址。" })}
            ${renderSettingsItem('SMTP 端口 (Port)', `publish_control.webhook_endpoints.${id}.smtp_port`, cfg.smtp_port || 465, 'number', { placeholder: "465 (SSL) 或 587 (TLS)", description: "通常 SSL 为 465，STARTTLS 为 587，明文为 25。" })}
            ${renderSettingsItem('启用 SSL 加密', `publish_control.webhook_endpoints.${id}.use_ssl`, cfg.use_ssl !== false, 'boolean', { description: "启用后将建立安全的 SSL/TLS 传输通道。" })}
            ${renderSettingsItem('发信邮箱账号 (User)', `publish_control.webhook_endpoints.${id}.smtp_user`, cfg.smtp_user || "", 'text', { placeholder: "例如: your_name@qq.com", description: "用于登录 SMTP 服务器的邮箱账号。" })}
            ${renderSettingsItem('授权码 / 邮箱密码 (Password)', `publish_control.webhook_endpoints.${id}.smtp_pass`, cfg.smtp_pass || "", 'password', { placeholder: "邮箱授权码或应用专用密码", description: "建议在邮箱设置中生成独立的第三方客户端授权码。" })}
            ${renderSettingsItem('发件人显示地址 (Sender)', `publish_control.webhook_endpoints.${id}.sender`, cfg.sender || "", 'text', { placeholder: "例如: noreply@yourdomain.com (留空则同账号)", description: "邮件头部显示的 From 发件人地址。" })}
            ${renderSettingsItem('接收者邮箱列表 (Receivers)', `publish_control.webhook_endpoints.${id}.receivers`, cfg.receivers || "", 'text', { placeholder: "例如: admin@example.com, alerts@domain.com (逗号分隔)", description: "接收出版通知与运维告警的目标邮箱地址。" })}
        `;
    } else if (cleanId === 'sms' || cleanId.includes('sms')) {
        html += `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan, #00f2fe); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan, #00f2fe); display: flex; align-items: center; gap: 6px;">💡 云短信与紧急告警向导</h4>
                <p style="margin: 4px 0; font-size: 0.82rem; line-height: 1.5; color: var(--text-dim, rgba(255,255,255,0.7));">面向<b>关键出版任务与算力熔断告警</b>：支持阿里云短信、腾讯云短信、Twilio 或自建 HTTP 短信网关直接推送到手机短信。</p>
            </div>
            ${renderSettingsItem('短信服务商 (Provider)', `publish_control.webhook_endpoints.${id}.provider`, cfg.provider || "aliyun", 'select', { options: [{ value: "aliyun", label: "阿里云短信 (Aliyun SMS)" }, { value: "tencent", label: "腾讯云短信 (Tencent SMS)" }, { value: "twilio", label: "Twilio 短信 (Global)" }, { value: "http_gateway", label: "通用 HTTP 短信网关" }], description: "选择您所使用的云短信服务商。" })}
            ${renderSettingsItem('API 网关端点 (URL)', `publish_control.webhook_endpoints.${id}.api_url`, cfg.api_url || "", 'text', { placeholder: "例如: https://sms.yourdomain.com/send", description: "自建短信网关端点，或第三方云短信 API 代理地址。" })}
            ${renderSettingsItem('AccessKey ID / API Key', `publish_control.webhook_endpoints.${id}.access_key_id`, cfg.access_key_id || "", 'text', { placeholder: "云服务商 AccessKey ID 或 API Key", description: "用于调用短信服务 API 的鉴权公钥/账号。" })}
            ${renderSettingsItem('AccessKey Secret / Auth Token', `publish_control.webhook_endpoints.${id}.access_key_secret`, cfg.access_key_secret || "", 'password', { placeholder: "云服务商 AccessKey Secret 或 Auth Token", description: "用于签名计算的私钥凭据。" })}
            ${renderSettingsItem('短信签名 (Sign Name)', `publish_control.webhook_endpoints.${id}.sign_name`, cfg.sign_name || "【极速出版】", 'text', { placeholder: "例如: 【极速出版】", description: "在短信运营商处审核通过的短信签名。" })}
            ${renderSettingsItem('模板代码 (Template Code)', `publish_control.webhook_endpoints.${id}.template_code`, cfg.template_code || "", 'text', { placeholder: "例如: SMS_123456789", description: "在运营商后台申请的短信通知模板 ID。" })}
            ${renderSettingsItem('目标手机号列表 (Phones)', `publish_control.webhook_endpoints.${id}.phone_numbers`, cfg.phone_numbers || "", 'text', { placeholder: "例如: +8613800000000, +8613900000000", description: "用于接收紧急告警短信的手机号列表，以逗号分隔。" })}
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
            ${renderSettingsItem('自建服务器地址 (Server URL)', `publish_control.webhook_endpoints.${id}.server_url`, cfg.server_url || "", 'text', { placeholder: "留空默认官方云 (例如 Gotify: https://gotify.yourdomain.com)", description: "若使用私有化自建的 Bark / Gotify 服务，请在此填入完整根地址。" })}
            ${renderSettingsItem('提示音效 (Sound)', `publish_control.webhook_endpoints.${id}.sound`, cfg.sound || "glass", 'select', { options: [{ value: "glass", label: "清脆玻璃 (Glass - 默认)" }, { value: "minuet", label: "优雅小步舞曲 (Minuet)" }, { value: "bell", label: "风铃 (Bell)" }, { value: "alarm", label: "高优先级警报 (Alarm)" }, { value: "silence", label: "静默推送 (Silence)" }], description: "移动设备收到推送时的提示音效（仅支持 Bark / Pushover）。" })}
            ${renderSettingsItem('消息分组 (Group)', `publish_control.webhook_endpoints.${id}.group`, cfg.group || "Illacme-Plenipes", 'text', { placeholder: "例如: Illacme-Plenipes", description: "iOS 通知中心折叠归类的消息分组名称。" })}
        `;
    } else if (cleanId === 'generic_webhook' || cleanId === 'generic' || cleanId.includes('generic')) {
        html += `
            ${renderSettingsItem('物理端点 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://yourdomain.com/api/v1/webhook", description: "接收系统事件通知的物理 HTTP/HTTPS 接口地址。" })}
            ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "防伪造签名 Secret (可选)", description: "可选。填写后系统将在 HTTP 标头中注入带 HMAC-SHA256 签名的凭据。" })}
        `;
    } else if (cleanId === 'webhook_dispatch' || cleanId.includes('dispatch') || cleanId.includes('webhook')) {
        html += `
            ${renderSettingsItem('触发端点 (URL)', `publish_control.webhook_endpoints.${id}.url`, cfg.url || "", 'text', { placeholder: "例如: https://ci.yourdomain.com/hooks/publish-complete", description: "下游 CI/CD、n8n、Make 或 Jenkins 的触发 Webhook URL。" })}
            ${renderSettingsItem('签名校验密钥 (Secret Key)', `publish_control.webhook_endpoints.${id}.secret`, cfg.secret || "", 'password', { placeholder: "签名 Secret (可选)", description: "可选。用于下游校验信号合规性。" })}
        `;
    }

    // 🚀 [全渠道事件过滤] 统一追加生命周期广播事件订阅卡片
    const defaultEvents = (cleanId === 'sms') ? ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'] : ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'];
    html += window.renderLifecycleEventsSubscription(id, cfg, defaultEvents);

    return html;
};

// 🚀 [V107.0] 商业级消息通知事件订阅中枢卡片渲染器
window.renderLifecycleEventsSubscription = (id, cfg, defaultEvents = ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS']) => {
    const rawEvents = cfg && cfg.events;
    let events = Array.isArray(rawEvents) ? rawEvents : (rawEvents ? [rawEvents] : defaultEvents);
    // 兼容传统简写
    events = events.map(e => {
        if (e === 'SUCCESS') return 'SYNC_SUCCESS';
        if (e === 'FAIL') return 'SYNC_FAIL';
        if (e === 'START') return 'SYNC_START';
        if (e === 'BLOCKED') return 'COMPLIANCE_BLOCKED';
        return e;
    });
    const hasEvent = (ev) => events.includes(ev);

    const isAlertsOnly = events.length === 5 && ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'].every(k => events.includes(k));
    const isAllEvents = events.length >= 8 && ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNC_START', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'].every(k => events.includes(k));
    const isRecommended = !isAlertsOnly && !isAllEvents && events.length === 7 && ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'].every(k => events.includes(k));
    const activePreset = isAlertsOnly ? 'alerts_only' : (isAllEvents ? 'all' : (isRecommended ? 'recommended' : 'custom'));

    return `
        <div class="lifecycle-subscription-card" style="margin-top: 18px; padding: 16px 18px; border-radius: 12px; background: rgba(255, 255, 255, 0.025); border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-bright); display: flex; align-items: center; gap: 6px;">
                    🔔 消息通知事件订阅中枢 (Event Subscriptions)
                </span>
                <span style="font-size: 0.74rem; color: var(--neon-cyan, #00f2fe);">智能分流 · 静默降噪</span>
            </div>
            <p style="margin: 0 0 12px 0; font-size: 0.76rem; color: var(--text-dim); line-height: 1.45;">
                定制该渠道需要接收的业务通知场景。未订阅的事件将全自动静默拦截，避免无效打扰与短信资费消耗。
            </p>

            <!-- 快捷预设按钮组 -->
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; background: rgba(0,0,0,0.3); padding: 5px 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                <span style="font-size: 0.73rem; color: var(--text-dim); margin-right: 4px;">快捷预设:</span>
                <button type="button" class="preset-btn" data-preset="recommended" onclick="window.applyNotificationPreset('${id}', 'recommended')" style="padding: 3px 10px; font-size: 0.75rem; border-radius: 6px; border: 1px solid ${activePreset === 'recommended' ? 'var(--neon-cyan, #00f2fe)' : 'rgba(255,255,255,0.1)'}; background: ${activePreset === 'recommended' ? 'rgba(0, 242, 254, 0.15)' : 'transparent'}; color: ${activePreset === 'recommended' ? '#fff' : 'var(--text-dim)'}; cursor: pointer;">
                    🌟 智能推荐
                </button>
                <button type="button" class="preset-btn" data-preset="alerts_only" onclick="window.applyNotificationPreset('${id}', 'alerts_only')" style="padding: 3px 10px; font-size: 0.75rem; border-radius: 6px; border: 1px solid ${activePreset === 'alerts_only' ? '#ef4444' : 'rgba(255,255,255,0.1)'}; background: ${activePreset === 'alerts_only' ? 'rgba(239, 68, 68, 0.15)' : 'transparent'}; color: ${activePreset === 'alerts_only' ? '#fff' : 'var(--text-dim)'}; cursor: pointer;">
                    🚨 仅紧急告警
                </button>
                <button type="button" class="preset-btn" data-preset="all" onclick="window.applyNotificationPreset('${id}', 'all')" style="padding: 3px 10px; font-size: 0.75rem; border-radius: 6px; border: 1px solid ${activePreset === 'all' ? '#a855f7' : 'rgba(255,255,255,0.1)'}; background: ${activePreset === 'all' ? 'rgba(168, 85, 247, 0.15)' : 'transparent'}; color: ${activePreset === 'all' ? '#fff' : 'var(--text-dim)'}; cursor: pointer;">
                    📡 开发者全知
                </button>
            </div>

            <!-- 四大场景卡片 -->
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <!-- 场景 1: 文章出版与构建 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #93c5fd; margin-bottom: 8px;">
                        📚 文章出版与构建 (Publishing)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('SYNC_SUCCESS') ? 'var(--neon-cyan, #00f2fe)' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="SYNC_SUCCESS" onchange="window.updateChannelEventSubscription('${id}', 'SYNC_SUCCESS', this.checked, this)" ${hasEvent('SYNC_SUCCESS') ? 'checked' : ''}>
                            <span>✅ 全量出版完成</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('SYNC_FAIL') ? '#ef4444' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="SYNC_FAIL" onchange="window.updateChannelEventSubscription('${id}', 'SYNC_FAIL', this.checked, this)" ${hasEvent('SYNC_FAIL') ? 'checked' : ''}>
                            <span>❌ 编译出版失败</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('SYNC_START') ? 'var(--neon-cyan, #00f2fe)' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="SYNC_START" onchange="window.updateChannelEventSubscription('${id}', 'SYNC_START', this.checked, this)" ${hasEvent('SYNC_START') ? 'checked' : ''}>
                            <span>🚀 发布流水线启动</span>
                        </label>
                    </div>
                </div>

                <!-- 场景 2: 跨平台社交分发 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #a78bfa; margin-bottom: 8px;">
                        🌐 跨平台社交分发 (Syndication)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('SYNDICATION_COMPLETED') ? 'var(--neon-cyan, #00f2fe)' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="SYNDICATION_COMPLETED" onchange="window.updateChannelEventSubscription('${id}', 'SYNDICATION_COMPLETED', this.checked, this)" ${hasEvent('SYNDICATION_COMPLETED') ? 'checked' : ''}>
                            <span>📤 社交全网分发完成</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('SYNDICATION_FAILED') ? '#ef4444' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="SYNDICATION_FAILED" onchange="window.updateChannelEventSubscription('${id}', 'SYNDICATION_FAILED', this.checked, this)" ${hasEvent('SYNDICATION_FAILED') ? 'checked' : ''}>
                            <span>⚠️ 渠道分发异常</span>
                        </label>
                    </div>
                </div>

                <!-- 场景 3: 安全合规与算力告警 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #f87171; margin-bottom: 8px;">
                        🛡️ 安全合规与算力告警 (Safety & AI Sentinel)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('AI_MELT') ? '#ef4444' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="AI_MELT" onchange="window.updateChannelEventSubscription('${id}', 'AI_MELT', this.checked, this)" ${hasEvent('AI_MELT') ? 'checked' : ''}>
                            <span>⚡ AI 算力熔断 (Token耗尽)</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('COMPLIANCE_BLOCKED') ? '#f59e0b' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="COMPLIANCE_BLOCKED" onchange="window.updateChannelEventSubscription('${id}', 'COMPLIANCE_BLOCKED', this.checked, this)" ${hasEvent('COMPLIANCE_BLOCKED') ? 'checked' : ''}>
                            <span>🔒 出版合规与敏感词拦截</span>
                        </label>
                    </div>
                </div>

                <!-- 场景 4: 云端托管与上线 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #34d399; margin-bottom: 8px;">
                        🚀 云端托管与上线 (Hosting & Deployment)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('DEPLOY_SUCCESS') ? 'var(--neon-cyan, #00f2fe)' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="DEPLOY_SUCCESS" onchange="window.updateChannelEventSubscription('${id}', 'DEPLOY_SUCCESS', this.checked, this)" ${hasEvent('DEPLOY_SUCCESS') ? 'checked' : ''}>
                            <span>🌐 全站部署上线成功</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; background: rgba(255,255,255,0.02); padding: 6px 10px; border-radius: 6px; border: 1px solid ${hasEvent('DEPLOY_FAILED') ? '#ef4444' : 'rgba(255,255,255,0.05)'};">
                            <input type="checkbox" data-event-key="DEPLOY_FAILED" onchange="window.updateChannelEventSubscription('${id}', 'DEPLOY_FAILED', this.checked, this)" ${hasEvent('DEPLOY_FAILED') ? 'checked' : ''}>
                            <span>🚨 云端构建推流失败</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    `;
};

// 🚀 [V107.0] 一键应用预设方案 (纯 DOM 丝滑响应，无闪烁，无表单数据丢失)
window.applyNotificationPreset = (id, presetType) => {
    let targetEvents = [];
    if (presetType === 'recommended') {
        targetEvents = ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'];
    } else if (presetType === 'alerts_only') {
        targetEvents = ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'];
    } else if (presetType === 'all') {
        targetEvents = ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNC_START', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS', 'DEPLOY_FAILED'];
    }

    // 1. 同步全局配置数据
    window.settingsData = window.settingsData || {};
    window.settingsData.publish_control = window.settingsData.publish_control || {};
    window.settingsData.publish_control.webhook_endpoints = window.settingsData.publish_control.webhook_endpoints || {};
    window.settingsData.publish_control.webhook_endpoints[id] = window.settingsData.publish_control.webhook_endpoints[id] || {};
    window.settingsData.publish_control.webhook_endpoints[id].events = targetEvents;

    // 2. 毫秒级直接操作 DOM 元素，更新勾选与视觉边框高亮
    const cardEl = document.querySelector('.lifecycle-subscription-card');
    if (cardEl) {
        // 更新所有复选框状态与边框
        const checkboxes = cardEl.querySelectorAll('input[data-event-key]');
        checkboxes.forEach(cb => {
            const evKey = cb.getAttribute('data-event-key');
            const isChecked = targetEvents.includes(evKey);
            cb.checked = isChecked;
            if (cb.parentElement) {
                const isAlert = evKey.includes('FAIL') || evKey.includes('MELT') || evKey.includes('BLOCKED');
                cb.parentElement.style.borderColor = isChecked ? (isAlert ? '#ef4444' : 'var(--neon-cyan, #00f2fe)') : 'rgba(255,255,255,0.05)';
            }
        });

        // 更新预设按钮的高亮状态
        const presetBtns = cardEl.querySelectorAll('.preset-btn');
        presetBtns.forEach(btn => {
            const pType = btn.getAttribute('data-preset');
            if (pType === presetType) {
                if (presetType === 'recommended') {
                    btn.style.borderColor = 'var(--neon-cyan, #00f2fe)';
                    btn.style.background = 'rgba(0, 242, 254, 0.15)';
                    btn.style.color = '#fff';
                } else if (presetType === 'alerts_only') {
                    btn.style.borderColor = '#ef4444';
                    btn.style.background = 'rgba(239, 68, 68, 0.15)';
                    btn.style.color = '#fff';
                } else if (presetType === 'all') {
                    btn.style.borderColor = '#a855f7';
                    btn.style.background = 'rgba(168, 85, 247, 0.15)';
                    btn.style.color = '#fff';
                }
            } else {
                btn.style.borderColor = 'rgba(255,255,255,0.1)';
                btn.style.background = 'transparent';
                btn.style.color = 'var(--text-dim)';
            }
        });
    }

    if (typeof window.markSettingsDirty === 'function') {
        window.markSettingsDirty();
    }
};

// 🚀 [V107.0] 实时更新渠道事件订阅配置
window.updateChannelEventSubscription = (id, eventKey, isChecked, inputEl) => {
    window.settingsData = window.settingsData || {};
    window.settingsData.publish_control = window.settingsData.publish_control || {};
    window.settingsData.publish_control.webhook_endpoints = window.settingsData.publish_control.webhook_endpoints || {};
    window.settingsData.publish_control.webhook_endpoints[id] = window.settingsData.publish_control.webhook_endpoints[id] || {};

    const node = window.settingsData.publish_control.webhook_endpoints[id];
    let currentEvents = Array.isArray(node.events) ? [...node.events] : (id === 'sms' ? ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'] : ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS']);

    if (isChecked) {
        if (!currentEvents.includes(eventKey)) currentEvents.push(eventKey);
    } else {
        currentEvents = currentEvents.filter(k => k !== eventKey);
    }
    node.events = currentEvents;

    if (inputEl && inputEl.parentElement) {
        const isAlert = eventKey.includes('FAIL') || eventKey.includes('MELT') || eventKey.includes('BLOCKED');
        inputEl.parentElement.style.borderColor = isChecked ? (isAlert ? '#ef4444' : 'var(--neon-cyan, #00f2fe)') : 'rgba(255,255,255,0.05)';
    }

    // 当用户手动点选单个复选框时，重置所有预设按钮为普通透明状态（表示当前处于自定义模式）
    const cardEl = document.querySelector('.lifecycle-subscription-card');
    if (cardEl) {
        const presetBtns = cardEl.querySelectorAll('.preset-btn');
        presetBtns.forEach(btn => {
            btn.style.borderColor = 'rgba(255,255,255,0.1)';
            btn.style.background = 'transparent';
            btn.style.color = 'var(--text-dim)';
        });
    }

    if (typeof window.markSettingsDirty === 'function') {
        window.markSettingsDirty();
    }
};



