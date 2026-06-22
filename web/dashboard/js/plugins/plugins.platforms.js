/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Platforms Shard
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");
window.renderPlatformConfig = (id, cfg, category = 'publisher') => {
    if (category === 'hosting') {
        if (id === 's3') {
            return `
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.s3.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-hosting-bucket"})}
                ${renderSettingsItem('访问密钥 ID (Access Key)', `publish_control.direct_upload.s3.access_key`, cfg.access_key, 'text', {placeholder: "AWS_ACCESS_KEY_ID"})}
                ${renderSettingsItem('安全私钥 (Secret Key)', `publish_control.direct_upload.s3.secret_key`, cfg.secret_key, 'password', {placeholder: "AWS_SECRET_ACCESS_KEY"})}
                ${renderSettingsItem('存储区域 (Region)', `publish_control.direct_upload.s3.region`, cfg.region || 'us-east-1', 'text', {placeholder: "例如: us-east-1"})}
                ${renderSettingsItem('自定义端点 (Endpoint URL)', `publish_control.direct_upload.s3.endpoint_url`, cfg.endpoint_url, 'text', {placeholder: "Cloudflare R2, MinIO, or custom endpoint", description: "如果使用 Cloudflare R2 等非标准 AWS 存储，请填写此项。"})}
                ${renderSettingsItem('公开访问域名 (Public URL)', `publish_control.direct_upload.s3.public_url`, cfg.public_url, 'text', {placeholder: "例如: https://myblog.com", description: "网站公开访问的基地址。"})}
                ${renderSettingsItem('存储路径前缀 (Prefix)', `publish_control.direct_upload.s3.prefix`, cfg.prefix, 'text', {placeholder: "可选前缀，例如: html-site"})}
                ${renderSettingsItem('对象访问控制 (ACL)', `publish_control.direct_upload.s3.acl`, cfg.acl, 'text', {placeholder: "例如: public-read"})}
            `;
        } else if (id === 'github_pages') {
            return `
                ${renderSettingsItem('仓库 URL (Repo URL)', `publish_control.direct_upload.github_pages.repo_url`, cfg.repo_url, 'text', {placeholder: "例如: git@github.com:username/repo.git", description: "您的 GitHub 仓库的 SSH 或 HTTPS 地址。"})}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.github_pages.branch`, cfg.branch || 'gh-pages', 'text', {placeholder: "例如: gh-pages"})}
                ${renderSettingsItem('自定义域名 (CNAME)', `publish_control.direct_upload.github_pages.cname`, cfg.cname, 'text', {placeholder: "例如: blog.example.com", description: "可选，若绑定了自定义域名请在此填写。"})}
                ${renderSettingsItem('Git 用户名', `publish_control.direct_upload.github_pages.git_user_name`, cfg.git_user_name || 'Plenipes Bot', 'text')}
                ${renderSettingsItem('Git 邮箱', `publish_control.direct_upload.github_pages.git_user_email`, cfg.git_user_email || 'bot@plenipes.press', 'text')}
                ${renderSettingsItem('强制推送 (Force Push)', `publish_control.direct_upload.github_pages.force_push`, cfg.force_push, 'checkbox')}
            `;
        } else if (id === 'cloudflare_pages') {
            return `
                ${renderSettingsItem('项目名称 (Project Name)', `publish_control.direct_upload.cloudflare_pages.project_name`, cfg.project_name, 'text', {placeholder: "例如: my-docs-site"})}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.cloudflare_pages.branch`, cfg.branch || 'production', 'text', {placeholder: "例如: production"})}
                ${renderSettingsItem('账号 ID (Account ID)', `publish_control.direct_upload.cloudflare_pages.account_id`, cfg.account_id, 'text', {placeholder: "Cloudflare 账号 ID (可选)"})}
                ${renderSettingsItem('Wrangler CLI 路径', `publish_control.direct_upload.cloudflare_pages.wrangler_path`, cfg.wrangler_path || 'wrangler', 'text')}
            `;
        } else if (id === 'netlify') {
            return `
                ${renderSettingsItem('站点 ID (Site ID)', `publish_control.direct_upload.netlify.site_id`, cfg.site_id, 'text', {placeholder: "例如: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"})}
                ${renderSettingsItem('身份凭证 (Auth Token)', `publish_control.direct_upload.netlify.auth_token`, cfg.auth_token, 'password', {placeholder: "Netlify Personal Access Token"})}
                ${renderSettingsItem('生产模式部署 (Prod)', `publish_control.direct_upload.netlify.prod`, cfg.prod !== false, 'checkbox')}
                ${renderSettingsItem('Netlify CLI 路径', `publish_control.direct_upload.netlify.netlify_path`, cfg.netlify_path || 'netlify', 'text')}
            `;
        } else if (id === 'vercel') {
            return `
                ${renderSettingsItem('访问令牌 (Token)', `publish_control.direct_upload.vercel.token`, cfg.token, 'password', {placeholder: "请输入 Vercel 访问令牌 (Token)"})}
                ${renderSettingsItem('项目名称 (Project Name)', `publish_control.direct_upload.vercel.project_name`, cfg.project_name, 'text', {placeholder: "请输入 Vercel 项目名称"})}
                ${renderSettingsItem('组织 ID (Org ID)', `publish_control.direct_upload.vercel.org_id`, cfg.org_id, 'text', {placeholder: "请输入 Vercel 组织 ID (可选)"})}
                ${renderSettingsItem('生产部署 (Prod)', `publish_control.direct_upload.vercel.prod`, cfg.prod !== false, 'checkbox')}
                ${renderSettingsItem('Vercel CLI 路径', `publish_control.direct_upload.vercel.vercel_path`, cfg.vercel_path || 'vercel', 'text')}
            `;
        } else if (id === 'aliyun_oss') {
            return `
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.aliyun_oss.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-oss-bucket"})}
                ${renderSettingsItem('接入点 (Endpoint)', `publish_control.direct_upload.aliyun_oss.endpoint`, cfg.endpoint, 'text', {placeholder: "例如: oss-cn-hangzhou.aliyuncs.com"})}
                ${renderSettingsItem('访问密钥 ID (Access Key ID)', `publish_control.direct_upload.aliyun_oss.access_key_id`, cfg.access_key_id, 'text', {placeholder: "Access Key ID"})}
                ${renderSettingsItem('安全密钥 (Access Key Secret)', `publish_control.direct_upload.aliyun_oss.access_key_secret`, cfg.access_key_secret, 'password', {placeholder: "Access Key Secret"})}
                ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.aliyun_oss.prefix`, cfg.prefix, 'text', {placeholder: "例如: site-root (可选)"})}
                ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.aliyun_oss.public_url`, cfg.public_url, 'text', {placeholder: "例如: https://blog.mydomain.com", description: "如果配置了自定义 CDN 域名，请在此填写。"})}
            `;
        } else if (id === 'tencent_cos') {
            return `
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.tencent_cos.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-cos-1250000000"})}
                ${renderSettingsItem('存储区域 (Region)', `publish_control.direct_upload.tencent_cos.region`, cfg.region, 'text', {placeholder: "例如: ap-shanghai"})}
                ${renderSettingsItem('密钥 ID (SecretId)', `publish_control.direct_upload.tencent_cos.secret_id`, cfg.secret_id, 'text', {placeholder: "SecretId"})}
                ${renderSettingsItem('安全密钥 (SecretKey)', `publish_control.direct_upload.tencent_cos.secret_key`, cfg.secret_key, 'password', {placeholder: "SecretKey"})}
                ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.tencent_cos.prefix`, cfg.prefix, 'text', {placeholder: "例如: html-site (可选)"})}
                ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.tencent_cos.public_url`, cfg.public_url, 'text', {placeholder: "例如: https://blog.mydomain.com", description: "如果配置了自定义 CDN 域名，请在此填写。"})}
            `;
        } else if (id === 'upyun_uss') {
            return `
                ${renderSettingsItem('服务名称 (Bucket)', `publish_control.direct_upload.upyun_uss.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-upyun-service"})}
                ${renderSettingsItem('操作员 (Operator)', `publish_control.direct_upload.upyun_uss.operator`, cfg.operator, 'text', {placeholder: "操作员账号"})}
                ${renderSettingsItem('操作员密码 (Password)', `publish_control.direct_upload.upyun_uss.password`, cfg.password, 'password', {placeholder: "操作员密码"})}
                ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.upyun_uss.prefix`, cfg.prefix, 'text', {placeholder: "例如: site (可选)"})}
                ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.upyun_uss.public_url`, cfg.public_url, 'text', {placeholder: "例如: https://site.upaiyun.com", description: "网站公开访问的基地址。"})}
            `;
        } else if (id === 'sftp') {
            return `
                ${renderSettingsItem('服务器主机 (Host)', `publish_control.direct_upload.sftp.host`, cfg.host, 'text', {placeholder: "例如: 123.45.67.89 或 sftp.myblog.com"})}
                ${renderSettingsItem('SSH 端口 (Port)', `publish_control.direct_upload.sftp.port`, cfg.port || 22, 'number', {placeholder: "默认 22"})}
                ${renderSettingsItem('登录用户名 (Username)', `publish_control.direct_upload.sftp.username`, cfg.username, 'text', {placeholder: "例如: root"})}
                ${renderSettingsItem('登录密码 (Password)', `publish_control.direct_upload.sftp.password`, cfg.password, 'password', {placeholder: "SSH 密码，若使用私钥可留空"})}
                ${renderSettingsItem('SSH 私钥 (Private Key)', `publish_control.direct_upload.sftp.private_key`, cfg.private_key, 'textarea', {placeholder: "私钥文件路径或私钥字符串内容", rows: 4})}
                ${renderSettingsItem('私钥口令 (Passphrase)', `publish_control.direct_upload.sftp.passphrase`, cfg.passphrase, 'password', {placeholder: "私钥保护口令（如有）"})}
                ${renderSettingsItem('远程目标目录 (Remote Path)', `publish_control.direct_upload.sftp.remote_path`, cfg.remote_path, 'text', {placeholder: "例如: /var/www/html/blog"})}
                ${renderSettingsItem('站点访问域名 (Public URL)', `publish_control.direct_upload.sftp.public_url`, cfg.public_url, 'text', {placeholder: "例如: https://blog.mysite.com", description: "网站公开访问的基地址。"})}
            `;
        }
    }

    if (id === 'wordpress') {
        return `
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
            ${renderSettingsItem('访问凭据 (Integration Token)', `syndication.medium.integration_token`, cfg.integration_token || cfg.api_key, 'password', {placeholder: "请输入您的 Medium Integration Token", description: "【如何获取】登录 Medium 网页端，点击头像 -> Settings -> Security & Apps -> Integration Tokens 中申请生成"})}
        `;
    } else if (id === 'ghost') {
        return `
            ${renderSettingsItem('Ghost 平台 URL', `syndication.ghost.url`, cfg.url, 'text', {placeholder: "例如: https://myblog.ghost.io", description: "【如何获取】您 Ghost 站点的基本访问地址"})}
            ${renderSettingsItem('Admin API Key', `syndication.ghost.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Admin API Key", description: "【如何获取】登录 Ghost 后台 -> Settings -> Integrations -> 添加 Custom Integration，复制其中的 Admin API Key"})}
        `;
    } else if (id === 'hashnode') {
        return `
            ${renderSettingsItem('GraphQL API Token', `syndication.hashnode.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Hashnode GraphQL Token", description: "【如何获取】登录 Hashnode 网页端 -> 点击头像 -> Account Settings -> Developer Settings 中生成个人 Token"})}
        `;
    } else if (id === 'wechat') {
        return `
            ${renderSettingsItem('开发者 AppID', `syndication.wechat.app_id`, cfg.app_id, 'text', {placeholder: "请输入微信公众号开发者 ID (AppID)"})}
            ${renderSettingsItem('开发者 AppSecret', `syndication.wechat.app_secret`, cfg.app_secret, 'password', {placeholder: "请输入微信公众号开发者密码 (AppSecret)"})}
        `;
    } else if (id === 'zhihu') {
        return `
            ${renderSettingsItem('用户令牌 (Token)', `syndication.zhihu.token`, cfg.token, 'password', {placeholder: "请输入知乎个人访问令牌 (Access Token)"})}
            ${renderSettingsItem('专栏 ID (Column ID)', `syndication.zhihu.column_id`, cfg.column_id, 'text', {placeholder: "请输入知乎专栏 ID (如 column-id)"})}
        `;
    } else if (id === 'juejin') {
        return `
            ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.juejin.cookie`, cfg.cookie, 'textarea', {placeholder: "请输入掘金 Cookie 凭据 (二选一)", rows: 2})}
            ${renderSettingsItem('接口访问 Token (API Token)', `syndication.juejin.api_token`, cfg.api_token, 'password', {placeholder: "请输入掘金 API 访问令牌 (二选一)"})}
        `;
    } else if (id === 'substack') {
        return `
            ${renderSettingsItem('Substack 主页 URL', `syndication.substack.url`, cfg.url, 'text', {placeholder: "例如: https://myname.substack.com"})}
            ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.substack.cookie`, cfg.cookie, 'textarea', {placeholder: "请输入 Substack sid Cookie 凭证 (二选一)", rows: 2})}
            ${renderSettingsItem('API 令牌 (API Key)', `syndication.substack.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Substack API 密钥 (二选一)"})}
        `;
    } else if (id === 'telegram') {
        return `
            ${renderSettingsItem('机器人 Token (Bot Token)', `syndication.telegram.bot_token`, cfg.bot_token, 'password', {placeholder: "例如: 123456789:ABCdefGhIJKlmNoPQRsT"})}
            ${renderSettingsItem('目标 Chat ID (Chat ID)', `syndication.telegram.chat_id`, cfg.chat_id, 'text', {placeholder: "例如: @my_channel 或 -100xxxxxxxxxx"})}
        `;
    } else if (id === 'discord') {
        return `
            ${renderSettingsItem('Webhook 地址 (Webhook URL)', `syndication.discord.webhook_url`, cfg.webhook_url, 'text', {placeholder: "请输入 Discord Webhook 完整 URL"})}
        `;
    } else {
        return `
            ${renderSettingsItem('凭据/密钥 (Key/Token)', category === 'hosting' ? `publish_control.direct_upload.${id}.api_key` : `syndication.${id}.api_key`, cfg.api_key || cfg.app_password, 'password', {placeholder: "请输入访问令牌/API密钥"})}
            ${renderSettingsItem('发布目标 (URL/Bucket)', category === 'hosting' ? `publish_control.direct_upload.${id}.url` : `syndication.${id}.url`, cfg.url, 'text', {placeholder: "请输入目标 URL 或存储桶名称"})}
            ${renderSettingsItem('账号/ID', category === 'hosting' ? `publish_control.direct_upload.${id}.username` : `syndication.${id}.username`, cfg.username, 'text', {placeholder: "请输入账号名"})}
        `;
    }
};

window.renderImageHostingConfig = (id, cfg) => {
    if (id === 's3') {
        return `
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.s3.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-assets-bucket"})}
            ${renderSettingsItem('访问密钥 ID (Access Key)', `image_hosting.s3.access_key`, cfg.access_key, 'text', {placeholder: "AWS_ACCESS_KEY_ID"})}
            ${renderSettingsItem('安全私钥 (Secret Key)', `image_hosting.s3.secret_key`, cfg.secret_key, 'password', {placeholder: "AWS_SECRET_ACCESS_KEY"})}
            ${renderSettingsItem('存储区域 (Region)', `image_hosting.s3.region`, cfg.region || 'us-east-1', 'text', {placeholder: "例如: ap-east-1"})}
            ${renderSettingsItem('自定义端点 (Endpoint URL)', `image_hosting.s3.endpoint_url`, cfg.endpoint_url, 'text', {placeholder: "Cloudflare R2, MinIO, or custom endpoint", description: "如果使用 Cloudflare R2 等非标准 AWS 存储，请填写此项。"})}
            ${renderSettingsItem('CDN 访问域名 (Public URL)', `image_hosting.s3.public_url`, cfg.public_url, 'text', {placeholder: "例如: https://cdn.myblog.com", description: "图片公开访问的基地址，留空则使用默认 S3 访问地址。"})}
            ${renderSettingsItem('存储路径前缀 (Prefix)', `image_hosting.s3.prefix`, cfg.prefix, 'text', {placeholder: "例如: blog-assets"})}
            ${renderSettingsItem('对象访问控制 (ACL)', `image_hosting.s3.acl`, cfg.acl, 'text', {placeholder: "例如: public-read", description: "上传对象的权限控制 (留空或填写 public-read 等)。"})}
        `;
    } else if (id === 'github') {
        return `
            ${renderSettingsItem('GitHub 仓库名 (Repo)', `image_hosting.github.repo`, cfg.repo, 'text', {placeholder: "例如: username/repo", description: "格式必须为 '用户名/仓库名'"})}
            ${renderSettingsItem('分支 (Branch)', `image_hosting.github.branch`, cfg.branch || 'main', 'text', {placeholder: "例如: main"})}
            ${renderSettingsItem('访问令牌 (Token)', `image_hosting.github.token`, cfg.token, 'password', {placeholder: "GitHub Personal Access Token"})}
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.github.path`, cfg.path || 'images', 'text', {placeholder: "例如: images"})}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.github.cdn_url`, cfg.cdn_url, 'text', {placeholder: "例如: https://cdn.jsdelivr.net/gh/username/repo@branch", description: "可选，留空则使用 jsdelivr 默认加速链接。"})}
        `;
    } else if (id === 'sm_ms') {
        return `
            ${renderSettingsItem('SM.MS 访问密钥 (Token)', `image_hosting.sm_ms.token`, cfg.token, 'password', {placeholder: "请输入 SM.MS Secret Token", description: "登录 SM.MS 官网，在 User -> API Token 中获取。"})}
        `;
    } else if (id === 'imgur') {
        return `
            ${renderSettingsItem('客户端 ID (Client ID)', `image_hosting.imgur.client_id`, cfg.client_id, 'text', {placeholder: "Imgur Client ID", description: "匿名上传所需，在 Imgur API Application 页面申请。"})}
            ${renderSettingsItem('访问令牌 (Access Token)', `image_hosting.imgur.token`, cfg.token, 'password', {placeholder: "Imgur Access Token (可选)", description: "若绑定至个人账户请填写此项。"})}
        `;
    } else if (id === 'telegraph') {
        return `
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.telegraph.endpoint`, cfg.endpoint || 'https://telegra.ph', 'text', {placeholder: "例如: https://telegra.ph", description: "Telegraph API 基础端点，允许填写反代域名解决连接超时。"})}
        `;
    } else if (id === 'aliyun_oss') {
        return `
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.aliyun_oss.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-oss-bucket"})}
            ${renderSettingsItem('访问域名 (Endpoint)', `image_hosting.aliyun_oss.endpoint`, cfg.endpoint, 'text', {placeholder: "例如: oss-cn-hangzhou.aliyuncs.com"})}
            ${renderSettingsItem('访问密钥 ID (AccessKey ID)', `image_hosting.aliyun_oss.access_key_id`, cfg.access_key_id, 'text', {placeholder: "AccessKey ID"})}
            ${renderSettingsItem('访问密钥 Secret (AccessKey Secret)', `image_hosting.aliyun_oss.access_key_secret`, cfg.access_key_secret, 'password', {placeholder: "AccessKey Secret"})}
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.aliyun_oss.path`, cfg.path || 'images', 'text', {placeholder: "例如: images"})}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.aliyun_oss.cdn_url`, cfg.cdn_url, 'text', {placeholder: "例如: https://cdn.myblog.com", description: "可选。配置后将优先使用此域名生成图片链接。"})}
        `;
    } else if (id === 'tencent_cos') {
        return `
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.tencent_cos.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-cos-bucket-125000000"})}
            ${renderSettingsItem('所属区域 (Region)', `image_hosting.tencent_cos.region`, cfg.region, 'text', {placeholder: "例如: ap-guangzhou"})}
            ${renderSettingsItem('安全凭证 SecretId', `image_hosting.tencent_cos.secret_id`, cfg.secret_id, 'text', {placeholder: "SecretId"})}
            ${renderSettingsItem('安全凭证 SecretKey', `image_hosting.tencent_cos.secret_key`, cfg.secret_key, 'password', {placeholder: "SecretKey"})}
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.tencent_cos.path`, cfg.path || 'images', 'text', {placeholder: "例如: images"})}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.tencent_cos.cdn_url`, cfg.cdn_url, 'text', {placeholder: "例如: https://cdn.myblog.com", description: "可选。配置后将优先使用此域名生成图片链接。"})}
        `;
    } else if (id === 'qiniu_kodo') {
        return `
            ${renderSettingsItem('存储空间名称 (Bucket)', `image_hosting.qiniu_kodo.bucket`, cfg.bucket, 'text', {placeholder: "例如: my-kodo-bucket"})}
            ${renderSettingsItem('访问密钥 Access Key (AK)', `image_hosting.qiniu_kodo.access_key`, cfg.access_key, 'text', {placeholder: "Access Key"})}
            ${renderSettingsItem('访问密钥 Secret Key (SK)', `image_hosting.qiniu_kodo.secret_key`, cfg.secret_key, 'password', {placeholder: "Secret Key"})}
            ${renderSettingsItem('空间外链域名 (Domain)', `image_hosting.qiniu_kodo.domain`, cfg.domain, 'text', {placeholder: "例如: http://xxxx.qiniudn.com"})}
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.qiniu_kodo.path`, cfg.path || 'images', 'text', {placeholder: "例如: images"})}
        `;
    } else if (id === 'upyun_uss') {
        return `
            ${renderSettingsItem('服务名称 (Bucket)', `image_hosting.upyun_uss.bucket`, cfg.bucket, 'text', {placeholder: "请输入又拍云服务名称"})}
            ${renderSettingsItem('操作员名称 (Operator)', `image_hosting.upyun_uss.operator`, cfg.operator, 'text', {placeholder: "请输入操作员名称"})}
            ${renderSettingsItem('操作员密码 (Password)', `image_hosting.upyun_uss.password`, cfg.password, 'password', {placeholder: "请输入操作员密码"})}
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.upyun_uss.path`, cfg.path || 'images', 'text', {placeholder: "例如: images"})}
            ${renderSettingsItem('加速域名 (Domain)', `image_hosting.upyun_uss.domain`, cfg.domain, 'text', {placeholder: "例如: https://xxx.upaiyun.com"})}
        `;
    } else if (id === 'loli_io') {
        return `
            ${renderSettingsItem('访问密钥 (Token)', `image_hosting.loli_io.token`, cfg.token, 'password', {placeholder: "请输入路过图床 API Token", description: "登录 img.lol 或 loli.io 官网获取。"})}
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.loli_io.endpoint`, cfg.endpoint || 'https://img.lol/api/v1/upload', 'text', {placeholder: "默认: https://img.lol/api/v1/upload"})}
        `;
    } else if (id === 'superbed') {
        return `
            ${renderSettingsItem('访问密钥 (Token)', `image_hosting.superbed.token`, cfg.token, 'password', {placeholder: "请输入聚合图床 API Token"})}
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.superbed.endpoint`, cfg.endpoint || 'https://api.superbed.cn/upload', 'text', {placeholder: "默认: https://api.superbed.cn/upload"})}
        `;
    } else if (id === 'lsky_pro') {
        return `
            ${renderSettingsItem('接口地址 (Endpoint)', `image_hosting.lsky_pro.endpoint`, cfg.endpoint, 'text', {placeholder: "例如: https://lsky.yourdomain.com", description: "您的兰空图床实例地址，不带 /api/v1 路径。"})}
            ${renderSettingsItem('鉴权 Token', `image_hosting.lsky_pro.token`, cfg.token, 'password', {placeholder: "格式如: Bearer 1|xxxxxx"})}
            ${renderSettingsItem('存储策略 ID (Strategy ID)', `image_hosting.lsky_pro.strategy_id`, cfg.strategy_id, 'text', {placeholder: "可选，不填为默认存储策略"})}
            ${renderSettingsItem('相册 ID (Album ID)', `image_hosting.lsky_pro.album_id`, cfg.album_id, 'text', {placeholder: "可选，不填则不归类至相册"})}
        `;
    } else {
        return `
            ${renderSettingsItem('API Token / Key', `image_hosting.${id}.api_key`, cfg.api_key, 'password')}
            ${renderSettingsItem('自定义 URL', `image_hosting.${id}.url`, cfg.url, 'text')}
        `;
    }
};


