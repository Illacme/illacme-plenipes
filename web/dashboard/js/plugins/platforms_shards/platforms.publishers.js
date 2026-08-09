/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Social & Publishing Platforms Shard
 * 职责：社交媒体与分发平台 (WordPress, Medium, Ghost, Hashnode, 微信, 知乎, 掘金, Substack, Telegram, Discord) 的配置表单渲染。
 */

var renderSettingsItem = window.renderSettingsItem || (() => "");

window.rawRenderPublisherConfig = (id, cfg, category = 'publisher') => {
    if (id === 'wordpress') {
        // 动态拼装 WordPress 站点管理页跳转地址
        const initialWpUrl = cfg.api_url || cfg.url || "";
        let initialWpLink = "#";
        if (initialWpUrl) {
            initialWpLink = initialWpUrl.replace(/\/wp-json\/wp\/v2\/?$/, '').replace(/\/$/, '') + '/wp-admin/profile.php#application-passwords-section';
        }
        return `
            ${renderSettingsItem('平台 REST API 地址', `syndication.wordpress.api_url`, cfg.api_url || cfg.url, 'text', {
            placeholder: "例如: https://yourdomain.com/wp-json/wp/v2",
            description: "【如何获取】输入您的 WordPress 站点 API 端点，通常为您的网站地址加上 '/wp-json/wp/v2'",
            oninput: "const val = this.value.trim(); const container = this.closest('.drawer-body') || document; const helper = container.querySelector('.wordpress-helper'); if(helper) { helper.style.display = val ? 'flex' : 'none'; const link = helper.querySelector('a'); if(link && val) { const cleanUrl = val.replace(/\\/wp-json\\/wp\\/v2\\/?$/, '').replace(/\\/$/, ''); link.href = cleanUrl + '/wp-admin/profile.php#application-passwords-section'; } }"
        })}
            <div class="api-token-helper wordpress-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 站点应用密码直达链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="${initialWpLink}" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 直达我站点的应用密码生成页</a>
                </div>
            </div>
            ${renderSettingsItem('管理员用户名', `syndication.wordpress.username`, cfg.username, 'text', { placeholder: "例如: admin", description: "【如何获取】您在 WordPress 中登录后台所使用的用户名" })}
            ${renderSettingsItem('应用密码 (Application Password)', `syndication.wordpress.application_password`, cfg.application_password || cfg.api_key, 'password', { placeholder: "请在此输入 24 位的应用密码", description: "【如何获取】在 WordPress 后台 -> 用户 -> 个人资料 -> 应用密码中生成（注意：此处切勿输入您的 WordPress 登录密码！）" })}
            ${renderSettingsItem('文章默认发布状态', `syndication.wordpress.default_status`, cfg.default_status || 'publish', 'select', {
            items: [
                { value: 'publish', text: '🟢 直接公开发布 (publish)' },
                { value: 'draft', text: '🟡 存为本地草稿 (draft)' },
                { value: 'pending', text: '🟠 等待人工审核 (pending)' }
            ],
            description: '同步到 WordPress 后的文章默认状态'
        })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.wordpress.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'medium') {
        return `
            ${renderSettingsItem('访问凭据 (Integration Token)', `syndication.medium.integration_token`, cfg.integration_token || cfg.api_key, 'password', { placeholder: "请输入您的 Medium Integration Token", description: "【如何获取】登录 Medium 网页端，点击头像 -> Settings -> Security & Apps -> Integration Tokens 中申请生成" })}
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Token 直达魔术链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://medium.com/me/settings/security" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Medium API 密钥申请</a>
                </div>
            </div>
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.medium.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'ghost') {
        const initialGhostUrl = cfg.url || "";
        let initialGhostLink = "#";
        if (initialGhostUrl) {
            initialGhostLink = initialGhostUrl.replace(/\/$/, '') + '/ghost/#/settings/integrations';
        }
        return `
            ${renderSettingsItem('Ghost 平台 URL', `syndication.ghost.url`, cfg.url, 'text', {
            placeholder: "例如: https://myblog.ghost.io",
            description: "【如何获取】您 Ghost 站点的基本访问地址",
            oninput: "const val = this.value.trim(); const container = this.closest('.drawer-body') || document; const helper = container.querySelector('.ghost-helper'); if(helper) { helper.style.display = val ? 'flex' : 'none'; const link = helper.querySelector('a'); if(link && val) { link.href = val.replace(/\\/$/, '') + '/ghost/#/settings/integrations'; } }"
        })}
            <div class="api-token-helper ghost-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 站点 Integrations 直达链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="${initialGhostLink}" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 直达我站点的 Integrations 管理页</a>
                </div>
            </div>
            ${renderSettingsItem('Admin API Key', `syndication.ghost.api_key`, cfg.api_key, 'password', { placeholder: "请输入 Admin API Key", description: "【如何获取】登录 Ghost 后台 -> Settings -> Integrations -> 添加 Custom Integration，复制其中的 Admin API Key" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.ghost.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'hashnode') {
        return `
            ${renderSettingsItem('GraphQL API Token', `syndication.hashnode.api_key`, cfg.api_key, 'password', { placeholder: "请输入 Hashnode GraphQL Token", description: "【如何获取】登录 Hashnode 网页端 -> 点击头像 -> Account Settings -> Developer Settings 中生成个人 Token" })}
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Token 直达魔术链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://hashnode.com/settings/developer" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Hashnode API 密钥页</a>
                </div>
            </div>
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.hashnode.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'wechat') {
        return `
            ${renderSettingsItem('开发者 AppID', `syndication.wechat.app_id`, cfg.app_id, 'text', { placeholder: "请输入微信公众号开发者 ID (AppID)" })}
            ${renderSettingsItem('开发者 AppSecret', `syndication.wechat.app_secret`, cfg.app_secret, 'password', { placeholder: "请输入微信公众号开发者密码 (AppSecret)" })}
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 微信公众平台开发者页面</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://mp.weixin.qq.com/cgi-bin/settingpage?t=setting/index&action=index" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达微信公众平台设置页</a>
                </div>
            </div>
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.wechat.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'zhihu') {
        return `
            ${renderSettingsItem('用户令牌 (Token)', `syndication.zhihu.token`, cfg.token, 'password', { placeholder: "请输入知乎个人访问令牌 (Access Token)" })}
            ${renderSettingsItem('专栏 ID (Column ID)', `syndication.zhihu.column_id`, cfg.column_id, 'text', { placeholder: "请输入知乎专栏 ID (如 column-id)" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.zhihu.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'juejin') {
        return `
            ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.juejin.cookie`, cfg.cookie, 'textarea', { placeholder: "请输入掘金 Cookie 凭据 (二选一)", rows: 2 })}
            ${renderSettingsItem('接口访问 Token (API Token)', `syndication.juejin.api_token`, cfg.api_token, 'password', { placeholder: "请输入掘金 API 访问令牌 (二选一)" })}
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Juejin Token 直达链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://juejin.cn/user/settings/key" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达掘金 API Key 申请页</a>
                </div>
            </div>
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.juejin.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'substack') {
        return `
            ${renderSettingsItem('Substack 主页 URL', `syndication.substack.url`, cfg.url, 'text', { placeholder: "例如: https://myname.substack.com" })}
            ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.substack.cookie`, cfg.cookie, 'textarea', { placeholder: "请输入 Substack sid Cookie 凭证 (二选一)", rows: 2 })}
            ${renderSettingsItem('API 令牌 (API Key)', `syndication.substack.api_key`, cfg.api_key, 'password', { placeholder: "请输入 Substack API 密钥 (二选一)" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.substack.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'telegram') {
        return `
            ${renderSettingsItem('机器人 Token (Bot Token)', `syndication.telegram.bot_token`, cfg.bot_token, 'password', { placeholder: "例如: 123456789:ABCdefGhIJKlmNoPQRsT" })}
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Telegram 机器人创建向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://t.me/BotFather" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">💬 一键唤醒 BotFather 创建 Bot</a>
                </div>
            </div>
            ${renderSettingsItem('目标 Chat ID (Chat ID)', `syndication.telegram.chat_id`, cfg.chat_id, 'text', { placeholder: "例如: @my_channel 或 -100xxxxxxxxxx" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.telegram.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'discord') {
        return `
            ${renderSettingsItem('Webhook 地址 (Webhook URL)', `syndication.discord.webhook_url`, cfg.webhook_url, 'text', { placeholder: "请输入 Discord Webhook 完整 URL" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.discord.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'linkedin') {
        return `
            ${renderSettingsItem('访问令牌 (Access Token)', `syndication.linkedin.access_token`, cfg.access_token || cfg.api_key, 'password', { placeholder: "请输入 LinkedIn OAuth2 Access Token", description: "【如何获取】在 LinkedIn Developer Portal -> Auth 中生成并申请 Publish Posts 权限。" })}
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 LinkedIn Token 开发者直达向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://www.linkedin.com/developers/apps" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 LinkedIn Developer Portal</a>
                </div>
            </div>
            ${renderSettingsItem('作者 URN (Author URN)', `syndication.linkedin.author_urn`, cfg.author_urn, 'text', { placeholder: "例如: urn:li:person:xxxxxxxxxx", description: "您的 LinkedIn 个人或 Organization 唯一标识指纹 URN。" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.linkedin.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else if (id === 'devto' || id === 'dev_to') {
        return `
            ${renderSettingsItem('API 密钥 (API Key)', `syndication.devto.api_key`, cfg.api_key || cfg.token, 'password', {
            placeholder: "请输入 Dev.to API Key",
            description: "【如何获取】登录 Dev.to 网页端 -> 点击右上角头像 -> Settings -> Extensions -> 生成并复制 Personal Access Tokens"
        })}
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Dev.to API Key 申请直达魔术链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://dev.to/settings/extensions" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Dev.to Extensions 密钥申请页</a>
                </div>
            </div>
            ${renderSettingsItem('默认直接公开发布', `syndication.devto.published`, cfg.published === true, 'checkbox', {
            description: "勾选表示同步到 Dev.to 后直接公开展示 (Published)；留空表示默认存为私密草稿 (Draft)"
        })}
            ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.devto.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    } else {
        return `
            ${renderSettingsItem('访问令牌 (API Key / Token)', category === 'hosting' ? `publish_control.direct_upload.${id}.api_key` : `syndication.${id}.api_key`, cfg.api_key || cfg.token || cfg.app_password, 'password', { placeholder: "请输入访问令牌 / API Key" })}
            ${renderSettingsItem('平台服务地址 (API URL)', category === 'hosting' ? `publish_control.direct_upload.${id}.url` : `syndication.${id}.url`, cfg.url || cfg.api_url, 'text', { placeholder: "例如: https://your-domain.com/api (可选)" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', category === 'hosting' ? `publish_control.direct_upload.${id}.proxy` : `syndication.${id}.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    }
};
