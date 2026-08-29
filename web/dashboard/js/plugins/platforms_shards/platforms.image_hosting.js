/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Image Hosting Platforms Shard
 * 职责：图床与对象存储服务 (S3, GitHub, SM.MS, Imgur, Telegraph, OSS, COS, Kodo, USS, Loli.io, Superbed, Lsky Pro) 的配置表单渲染。
 */

var renderSettingsItem = window.renderSettingsItem || (() => "");

window.rawRenderImageHostingConfig = (id, cfg) => {
    const portalGuide = window.renderPlatformPortalGuide ? window.renderPlatformPortalGuide(id) : '';
    if (id === 's3') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 本地 AWS 凭证极简向导</h4>
                <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">如果您在本地配置过 AWS CLI，系统可尝试一键感应并自动回填凭证信息。</p>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                    <button type="button" class="helper-btn" onclick="window.triggerAWSCredentialsSense(this, 'image_hosting.s3')">🔑 本地一键免密授权</button>
                    <a href="https://console.aws.amazon.com/iam/home#/security_credentials" target="_blank" class="helper-btn">🔗 一键直达 AWS IAM 安全凭证页</a>
                </div>
                <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
            </div>
            ${renderSettingsItem('访问密钥 ID (Access Key)', `image_hosting.s3.access_key`, cfg.access_key, 'text', { placeholder: "AWS_ACCESS_KEY_ID" })}
            ${renderSettingsItem('安全私钥 (Secret Key)', `image_hosting.s3.secret_key`, cfg.secret_key, 'password', { placeholder: "AWS_SECRET_ACCESS_KEY" })}
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.s3.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-assets-bucket" })}
            ${renderSettingsItem('存储区域 (Region)', `image_hosting.s3.region`, cfg.region || 'us-east-1', 'text', { placeholder: "例如: ap-east-1" })}
            ${renderSettingsItem('CDN 访问域名 (Public URL)', `image_hosting.s3.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://cdn.myblog.com", description: "图片公开访问的基地址，留空则使用默认 S3 访问地址。" })}
            ${window.renderPlatformAdvancedGroup('高级可选调参 (Prefix / ACL / Endpoint / 代理)', `
                ${renderSettingsItem('存储路径前缀 (Prefix)', `image_hosting.s3.prefix`, cfg.prefix, 'text', { placeholder: "例如: blog-assets" })}
                ${renderSettingsItem('对象访问控制 (ACL)', `image_hosting.s3.acl`, cfg.acl, 'text', { placeholder: "例如: public-read", description: "上传对象的权限控制 (留空或填写 public-read 等)。" })}
                ${renderSettingsItem('自定义端点 (Endpoint URL)', `image_hosting.s3.endpoint_url`, cfg.endpoint_url, 'text', { placeholder: "Cloudflare R2, MinIO, or custom endpoint", description: "如果使用 Cloudflare R2 等非标准 AWS 存储，请填写此项。" })}
                ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.s3.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 S3 端点的网络连通校验。" })}
            `)}
        `;
    } else if (id === 'github') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 GitHub Token 直达链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://github.com/settings/tokens/new?scopes=repo&description=Illacme-Plenipes-Image-Hosting" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Token 申请</a>
                </div>
            </div>
            ${renderSettingsItem('访问令牌 (Token)', `image_hosting.github.token`, cfg.token, 'password', { placeholder: "GitHub Personal Access Token" })}
            ${renderSettingsItem('GitHub 仓库名 (Repo)', `image_hosting.github.repo`, cfg.repo, 'text', { placeholder: "例如: username/repo", description: "格式必须为 '用户名/仓库名'" })}
            ${renderSettingsItem('分支 (Branch)', `image_hosting.github.branch`, cfg.branch || 'main', 'text', { placeholder: "例如: main" })}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.github.cdn_url`, cfg.cdn_url, 'text', { placeholder: "例如: https://cdn.jsdelivr.net/gh/username/repo@branch", description: "可选，留空则使用 jsdelivr 默认加速链接。" })}
            ${window.renderPlatformAdvancedGroup('高级可选参数 (Path / 代理)', `
                ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.github.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
                ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.github.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 GitHub API 的网络校验。" })}
            `)}
        `;
    } else if (id === 'sm_ms') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Token 直达魔术链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://sm.ms/home/apitoken" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 SM.MS 密钥申请页</a>
                </div>
            </div>
            ${renderSettingsItem('SM.MS 访问密钥 (Token)', `image_hosting.sm_ms.token`, cfg.token, 'password', { placeholder: "请输入 SM.MS Secret Token", description: "登录 SM.MS 官网，在 User -> API Token 中获取。" })}
            ${window.renderPlatformAdvancedGroup('高级代理参数', `
                ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.sm_ms.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 SM.MS API 的校验。" })}
            `)}
        `;
    } else if (id === 'imgur') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Imgur 授权直达链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://api.imgur.com/oauth2/addclient" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Imgur Client ID 申请页</a>
                </div>
            </div>
            ${renderSettingsItem('客户端 ID (Client ID)', `image_hosting.imgur.client_id`, cfg.client_id, 'text', { placeholder: "Imgur Client ID", description: "匿名上传所需，在 Imgur API Application 页面申请。" })}
            ${renderSettingsItem('访问令牌 (Access Token)', `image_hosting.imgur.token`, cfg.token, 'password', { placeholder: "Imgur Access Token (可选)", description: "若绑定至个人账户请填写此项。" })}
            ${window.renderPlatformAdvancedGroup('高级代理参数', `
                ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.imgur.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 Imgur API 的校验。" })}
            `)}
        `;
    } else if (id === 'telegraph') {
        return `
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.telegraph.endpoint`, cfg.endpoint || 'https://telegra.ph', 'text', { placeholder: "例如: https://telegra.ph", description: "Telegraph API 基础端点，允许填写反代域名解决连接超时。" })}
            ${window.renderPlatformAdvancedGroup('高级代理参数', `
                ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.telegraph.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 Telegraph 端点的校验。" })}
            `)}
        `;
    } else if (id === 'aliyun_oss') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 阿里云 AccessKey 获取向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://ram.console.aliyun.com/manage/ak" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达阿里云 AccessKey 管理页</a>
                </div>
            </div>
            ${renderSettingsItem('访问密钥 ID (AccessKey ID)', `image_hosting.aliyun_oss.access_key_id`, cfg.access_key_id, 'text', { placeholder: "AccessKey ID" })}
            ${renderSettingsItem('访问密钥 Secret (AccessKey Secret)', `image_hosting.aliyun_oss.access_key_secret`, cfg.access_key_secret, 'password', { placeholder: "AccessKey Secret" })}
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.aliyun_oss.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-oss-bucket" })}
            ${renderSettingsItem('访问域名 (Endpoint)', `image_hosting.aliyun_oss.endpoint`, cfg.endpoint, 'text', { placeholder: "例如: oss-cn-hangzhou.aliyuncs.com" })}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.aliyun_oss.cdn_url`, cfg.cdn_url, 'text', { placeholder: "例如: https://cdn.myblog.com", description: "可选。配置后将优先使用此域名生成图片链接。" })}
            ${window.renderPlatformAdvancedGroup('高级路径参数', `
                ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.aliyun_oss.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            `)}
        `;
    } else if (id === 'tencent_cos') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 腾讯云 API 密钥获取向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://console.cloud.tencent.com/cam/capi" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达腾讯云 API 密钥管理页</a>
                </div>
            </div>
            ${renderSettingsItem('安全凭证 SecretId', `image_hosting.tencent_cos.secret_id`, cfg.secret_id, 'text', { placeholder: "SecretId" })}
            ${renderSettingsItem('安全凭证 SecretKey', `image_hosting.tencent_cos.secret_key`, cfg.secret_key, 'password', { placeholder: "SecretKey" })}
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.tencent_cos.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-cos-bucket-125000000" })}
            ${renderSettingsItem('所属区域 (Region)', `image_hosting.tencent_cos.region`, cfg.region, 'text', { placeholder: "例如: ap-guangzhou" })}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.tencent_cos.cdn_url`, cfg.cdn_url, 'text', { placeholder: "例如: https://cdn.myblog.com", description: "可选。配置后将优先使用此域名生成图片链接。" })}
            ${window.renderPlatformAdvancedGroup('高级路径参数', `
                ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.tencent_cos.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            `)}
        `;
    } else if (id === 'qiniu_kodo') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 七牛云个人密钥向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://portal.qiniu.com/user/key" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达七牛云个人密钥页</a>
                </div>
            </div>
            ${renderSettingsItem('访问密钥 Access Key (AK)', `image_hosting.qiniu_kodo.access_key`, cfg.access_key, 'text', { placeholder: "Access Key" })}
            ${renderSettingsItem('访问密钥 Secret Key (SK)', `image_hosting.qiniu_kodo.secret_key`, cfg.secret_key, 'password', { placeholder: "Secret Key" })}
            ${renderSettingsItem('存储空间名称 (Bucket)', `image_hosting.qiniu_kodo.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-kodo-bucket" })}
            ${renderSettingsItem('空间外链域名 (Domain)', `image_hosting.qiniu_kodo.domain`, cfg.domain, 'text', { placeholder: "例如: http://xxxx.qiniudn.com" })}
            ${window.renderPlatformAdvancedGroup('高级路径参数', `
                ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.qiniu_kodo.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            `)}
        `;
    } else if (id === 'upyun_uss') {
        return `
            ${renderSettingsItem('操作员名称 (Operator)', `image_hosting.upyun_uss.operator`, cfg.operator, 'text', { placeholder: "请输入操作员名称" })}
            ${renderSettingsItem('操作员密码 (Password)', `image_hosting.upyun_uss.password`, cfg.password, 'password', { placeholder: "请输入操作员密码" })}
            ${renderSettingsItem('服务名称 (Bucket)', `image_hosting.upyun_uss.bucket`, cfg.bucket, 'text', { placeholder: "请输入又拍云服务名称" })}
            ${renderSettingsItem('加速域名 (Domain)', `image_hosting.upyun_uss.domain`, cfg.domain, 'text', { placeholder: "例如: https://xxx.upaiyun.com" })}
            ${window.renderPlatformAdvancedGroup('高级路径参数', `
                ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.upyun_uss.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            `)}
        `;
    } else if (id === 'loli_io') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 路过图床 API Token 向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://img.lol/page/api.html" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达路过图床 API 密钥页</a>
                </div>
            </div>
            ${renderSettingsItem('访问密钥 (Token)', `image_hosting.loli_io.token`, cfg.token, 'password', { placeholder: "请输入路过图床 API Token", description: "登录 img.lol 或 loli.io 官网获取。" })}
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.loli_io.endpoint`, cfg.endpoint || 'https://img.lol/api/v1/upload', 'text', { placeholder: "默认: https://img.lol/api/v1/upload" })}
            ${window.renderPlatformAdvancedGroup('高级代理参数', `
                ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.loli_io.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 API 校验。" })}
            `)}
        `;
    } else if (id === 'superbed') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 聚合图床 API Token 向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://superbed.cn/api" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达聚合图床 API 页</a>
                </div>
            </div>
            ${renderSettingsItem('访问密钥 (Token)', `image_hosting.superbed.token`, cfg.token, 'password', { placeholder: "请输入聚合图床 API Token" })}
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.superbed.endpoint`, cfg.endpoint || 'https://api.superbed.cn/upload', 'text', { placeholder: "默认: https://api.superbed.cn/upload" })}
            ${window.renderPlatformAdvancedGroup('高级代理参数', `
                ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.superbed.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 API 校验。" })}
            `)}
        `;
    } else if (id === 'lsky_pro') {
        return `
            <div class="api-token-helper">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 兰空图床 (Lsky Pro) 授权向导</span>
                </div>
                <div style="font-size: 0.82rem; color: var(--text-dim); margin-top: 4px; line-height: 1.45;">
                    登录您的兰空图床 Web 控制台 -> 个人中心/接口密钥 -> 创建并复制 Token 填入下方。
                </div>
            </div>
            ${renderSettingsItem('鉴权令牌 (Auth Token)', `image_hosting.lsky_pro.token`, cfg.token, 'password', { placeholder: "格式如: Bearer 1|xxxxxx 或直接 Token", description: "在兰空图床后台生成的 API 访问 Token 凭证。" })}
            ${renderSettingsItem('接口端点 (Endpoint URL)', `image_hosting.lsky_pro.endpoint`, cfg.endpoint, 'text', { placeholder: "例如: https://lsky.yourdomain.com", description: "您的兰空图床实例根地址，不带 /api/v1 路径。" })}
            ${window.renderPlatformAdvancedGroup('高级相册与策略参数', `
                ${renderSettingsItem('存储策略 ID (Strategy ID)', `image_hosting.lsky_pro.strategy_id`, cfg.strategy_id, 'text', { placeholder: "可选，不填为默认存储策略" })}
                ${renderSettingsItem('相册 ID (Album ID)', `image_hosting.lsky_pro.album_id`, cfg.album_id, 'text', { placeholder: "可选，不填则不归类至相册" })}
            `)}
        `;
    } else {
        return `
            ${renderSettingsItem('API Token / Key', `image_hosting.${id}.api_key`, cfg.api_key, 'password')}
            ${renderSettingsItem('自定义 URL', `image_hosting.${id}.url`, cfg.url, 'text')}
        `;
    }
};

window.renderImageHostingConfig = (id, cfg) => {
    const portalGuide = window.renderPlatformPortalGuide ? window.renderPlatformPortalGuide(id) : '';
    const content = window.rawRenderImageHostingConfig ? window.rawRenderImageHostingConfig(id, cfg) : '';
    if (!content.includes('api-token-helper') && portalGuide) {
        return portalGuide + content;
    }
    return content;
};
