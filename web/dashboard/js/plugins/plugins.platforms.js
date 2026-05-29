/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Platforms Shard
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");

window.renderPlatformConfig = (id, cfg, category = 'publisher') => {
    if (id === 'wordpress') {
        return `
            ${renderSettingsItem('通道激活', `syndication.wordpress.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将自动分发并同步更新至您的 WordPress。'})}
            ${renderSettingsItem('平台 REST API 地址', `syndication.wordpress.api_url`, cfg.api_url || cfg.url, 'text', {placeholder: "例如: https://yourdomain.com/wp-json/wp/v2", description: "【如何获取】输入您的 WordPress 站点 API 端点，通常为您的网站地址加上 '/wp-json/wp/v2'"})}
            ${renderSettingsItem('管理员用户名', `syndication.wordpress.username`, cfg.username, 'text', {placeholder: "例如: admin", description: "【如何获取】您在 WordPress 中登录后台所使用的用户名"})}
            ${renderSettingsItem('应用密码 (Application Password)', `syndication.wordpress.application_password`, cfg.application_password || cfg.api_key, 'password', {placeholder: "请在此输入 24 位的应用密码", description: "【如何获取】在 WordPress 后台 -> 用户 -> 个人资料 -> 应用密码中生成（注意：此处切勿输入您的 WordPress 登录密码！）"})}
            ${renderSettingsItem('文章默认发布状态', `syndication.wordpress.default_status`, cfg.default_status || 'publish', 'select', {
                items: [
                    {value: 'publish', text: '🟢 直接公开发布 (publish)'},
                    {value: 'draft', text: '🟡 存为本地草稿 (draft)'},
                    {value: 'pending', text: '🟠 等待人工审核 (pending)'}
                ],
                description: '同步到 WordPress 后的文章默认状态'
            })}
        `;
    } else if (id === 'medium') {
        return `
            ${renderSettingsItem('通道激活', `syndication.medium.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Medium。'})}
            ${renderSettingsItem('访问凭据 (Integration Token)', `syndication.medium.integration_token`, cfg.integration_token || cfg.api_key, 'password', {placeholder: "请输入您的 Medium Integration Token", description: "【如何获取】登录 Medium 网页端，点击头像 -> Settings -> Security & Apps -> Integration Tokens 中申请生成"})}
        `;
    } else if (id === 'ghost') {
        return `
            ${renderSettingsItem('通道激活', `syndication.ghost.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Ghost 博客。'})}
            ${renderSettingsItem('Ghost 平台 URL', `syndication.ghost.url`, cfg.url, 'text', {placeholder: "例如: https://myblog.ghost.io", description: "【如何获取】您 Ghost 站点的基本访问地址"})}
            ${renderSettingsItem('Admin API Key', `syndication.ghost.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Admin API Key", description: "【如何获取】登录 Ghost 后台 -> Settings -> Integrations -> 添加 Custom Integration，复制其中的 Admin API Key"})}
        `;
    } else if (id === 'hashnode') {
        return `
            ${renderSettingsItem('通道激活', `syndication.hashnode.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Hashnode。'})}
            ${renderSettingsItem('GraphQL API Token', `syndication.hashnode.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Hashnode GraphQL Token", description: "【如何获取】登录 Hashnode 网页端 -> 点击头像 -> Account Settings -> Developer Settings 中生成个人 Token"})}
        `;
    } else {
        return `
            ${renderSettingsItem('通道激活', category === 'hosting' ? `publish_control.direct_upload.${id}.enabled` : `syndication.${id}.enabled`, cfg.enabled, 'checkbox', {description: '开启后，当前激活的品牌将在执行出版发布任务时向该端点进行物理分发。'})}
            ${renderSettingsItem('凭据/密钥 (Key/Token)', category === 'hosting' ? `publish_control.direct_upload.${id}.api_key` : `syndication.${id}.api_key`, cfg.api_key || cfg.app_password, 'password', {placeholder: "请输入访问令牌/API密钥"})}
            ${renderSettingsItem('发布目标 (URL/Bucket)', category === 'hosting' ? `publish_control.direct_upload.${id}.url` : `syndication.${id}.url`, cfg.url, 'text', {placeholder: "请输入目标 URL 或存储桶名称"})}
            ${renderSettingsItem('账号/ID', category === 'hosting' ? `publish_control.direct_upload.${id}.username` : `syndication.${id}.username`, cfg.username, 'text', {placeholder: "请输入账号名"})}
        `;
    }
};
