/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Platforms Shard
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");

window.PLATFORM_PORTAL_LINKS = {
    // 托管服务平台 (Hosting Platforms)
    'cloudflare_pages': { name: 'Cloudflare Pages', home: 'https://dash.cloudflare.com', token: 'https://dash.cloudflare.com/profile/api-tokens' },
    'github_pages': { name: 'GitHub Pages', home: 'https://github.com', token: 'https://github.com/settings/tokens/new?scopes=repo&description=Plenipes-Syndication' },
    'gitee_pages': { name: 'Gitee Pages', home: 'https://gitee.com', token: 'https://gitee.com/profile/personal_access_tokens/new' },
    'gitlab_pages': { name: 'GitLab Pages', home: 'https://gitlab.com', token: 'https://gitlab.com/-/profile/personal_access_tokens' },
    'coding_pages': { name: 'Coding Pages', home: 'https://coding.net', token: 'https://coding.net/user/account/setting/pt' },
    'netlify': { name: 'Netlify', home: 'https://app.netlify.com', token: 'https://app.netlify.com/user/applications#personal-access-tokens' },
    'vercel': { name: 'Vercel', home: 'https://vercel.com', token: 'https://vercel.com/account/tokens' },
    'zeabur': { name: 'Zeabur', home: 'https://zeabur.com', token: 'https://dash.zeabur.com/account' },
    'render': { name: 'Render', home: 'https://render.com', token: 'https://dashboard.render.com/user/settings' },
    'railway': { name: 'Railway', home: 'https://railway.app', token: 'https://railway.app/account/tokens' },
    'firebase': { name: 'Firebase', home: 'https://console.firebase.google.com', token: 'https://console.firebase.google.com' },

    // 对象存储与图床平台 (Storage & Image Hosting)
    's3': { name: 'AWS S3', home: 'https://aws.amazon.com/s3', token: 'https://console.aws.amazon.com/iam/home#/security_credentials' },
    'github': { name: 'GitHub 图床', home: 'https://github.com', token: 'https://github.com/settings/tokens/new?scopes=repo&description=Plenipes-Image-Hosting' },
    'gitee': { name: 'Gitee 图床', home: 'https://gitee.com', token: 'https://gitee.com/profile/personal_access_tokens/new' },
    'gitee_img': { name: 'Gitee 图床', home: 'https://gitee.com', token: 'https://gitee.com/profile/personal_access_tokens/new' },
    'sm_ms': { name: 'SM.MS 图床', home: 'https://sm.ms', token: 'https://sm.ms/home/apitoken' },
    'smms': { name: 'SM.MS 图床', home: 'https://sm.ms', token: 'https://sm.ms/home/apitoken' },
    'imgur': { name: 'Imgur 图床', home: 'https://imgur.com', token: 'https://api.imgur.com/oauth2/addclient' },
    'telegraph': { name: 'Telegraph 图床', home: 'https://telegra.ph', token: 'https://telegra.ph' },
    'aliyun_oss': { name: '阿里云 OSS', home: 'https://www.aliyun.com/product/oss', token: 'https://ram.console.aliyun.com/manage/ak' },
    'tencent_cos': { name: '腾讯云 COS', home: 'https://cloud.tencent.com/product/cos', token: 'https://console.cloud.tencent.com/cam/capi' },
    'upyun_uss': { name: '又拍云 USS', home: 'https://www.upyun.com', token: 'https://console.upyun.com/account/operators/' },
    'upyun': { name: '又拍云 USS', home: 'https://www.upyun.com', token: 'https://console.upyun.com/account/operators/' },
    'qiniu': { name: '七牛云 Kodo', home: 'https://www.qiniu.com', token: 'https://portal.qiniu.com/user/key' },

    // 社交媒体与分发平台 (Publishers)
    'devto': { name: 'Dev.to', home: 'https://dev.to', token: 'https://dev.to/settings/extensions' },
    'hashnode': { name: 'Hashnode', home: 'https://hashnode.com', token: 'https://hashnode.com/settings/developer' },
    'medium': { name: 'Medium', home: 'https://medium.com', token: 'https://medium.com/me/settings/security' },
    'ghost': { name: 'Ghost', home: 'https://ghost.org', token: 'https://ghost.org' },
    'wordpress': { name: 'WordPress', home: 'https://wordpress.org', token: 'https://wordpress.org/documentation/article/application-passwords/' },
    'wechat': { name: '微信公众平台', home: 'https://mp.weixin.qq.com', token: 'https://mp.weixin.qq.com/cgi-bin/settingpage?t=setting/index&action=index' },
    'zhihu': { name: '知乎专栏', home: 'https://www.zhihu.com', token: 'https://www.zhihu.com' },
    'juejin': { name: '稀土掘金', home: 'https://juejin.cn', token: 'https://juejin.cn/user/settings/key' },
    'substack': { name: 'Substack', home: 'https://substack.com', token: 'https://substack.com' },
    'telegram': { name: 'Telegram', home: 'https://telegram.org', token: 'https://t.me/BotFather' },
    'discord': { name: 'Discord', home: 'https://discord.com', token: 'https://discord.com/developers/applications' },
    'linkedin': { name: 'LinkedIn', home: 'https://www.linkedin.com', token: 'https://www.linkedin.com/developers/apps' },

    // 静态生成器引擎 (SSG Engines)
    'hugo': { name: 'Hugo 引擎', home: 'https://gohugo.io', token: 'https://gohugo.io/documentation/' },
    'hexo': { name: 'Hexo 引擎', home: 'https://hexo.io', token: 'https://hexo.io/docs/' },
    'astro': { name: 'Astro 引擎', home: 'https://astro.build', token: 'https://docs.astro.build' },
    'nextjs': { name: 'Next.js 引擎', home: 'https://nextjs.org', token: 'https://nextjs.org/docs' },
    'vuepress': { name: 'VuePress 引擎', home: 'https://vuepress.vuejs.org', token: 'https://vuepress.vuejs.org' }
};

window.renderPlatformPortalGuide = (id) => {
    const info = window.PLATFORM_PORTAL_LINKS[id];
    if (!info) return '';
    const homeBtn = info.home ? `<a href="${info.home}" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 访问 ${info.name} 官网</a>` : '';
    const tokenBtn = (info.token && info.token !== info.home) ? `<a href="${info.token}" target="_blank" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Token / 密钥申请</a>` : '';

    if (!homeBtn && !tokenBtn) return '';

    return `
        <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.04);">
            <div style="font-weight: 600; display: flex; align-items: center; gap: 6px; color: var(--neon-cyan); font-size: 0.85rem; margin-bottom: 8px;">
                <span>💡 ${info.name} 极简入口向导</span>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                ${homeBtn}
                ${tokenBtn}
            </div>
        </div>
    `;
};

window.renderPlatformAdvancedGroup = (title, content, isDefaultOpen = false) => {
    if (!content) return '';
    return `
        <details class="advanced-settings-block" ${isDefaultOpen ? 'open' : ''} style="margin-top: 15px; border: 1px dashed var(--glass-border, rgba(255,255,255,0.12)); border-radius: 8px; padding: 10px 14px; background: rgba(0,0,0,0.15);">
            <summary style="cursor: pointer; font-size: 0.8rem; font-weight: 700; color: var(--accent-secondary, #00f2fe); user-select: none; padding: 4px 0; outline: none; display: flex; align-items: center; justify-content: space-between;">
                <span>🛠️ ${title || '高级参数（可选）'}</span>
                <span class="advanced-toggle-icon" style="font-size: 0.75rem; opacity: 0.6; transition: transform 0.2s ease;">▼</span>
            </summary>
            <div class="advanced-settings-content" style="margin-top: 12px; display: flex; flex-direction: column; gap: 12px;">
                ${content}
            </div>
        </details>
    `;
};

window.rawRenderPlatformConfig = (id, cfg, category = 'publisher') => {
    const portalGuide = window.renderPlatformPortalGuide ? window.renderPlatformPortalGuide(id) : '';
    if (category === 'hosting') {
        if (id === 's3') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 本地 AWS 凭证极简向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">如果您在本地安装并配置过 AWS CLI (拥有 <code>~/.aws/credentials</code> 文件)，系统可尝试一键感应并自动回填凭证信息。</p>
                    <div style="margin-top: 8px;">
                        <button type="button" class="helper-btn" onclick="window.triggerAWSCredentialsSense(this, 'publish_control.direct_upload.s3')">🔑 本地一键免密授权</button>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.s3.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-hosting-bucket" })}
                ${renderSettingsItem('访问密钥 ID (Access Key)', `publish_control.direct_upload.s3.access_key`, cfg.access_key, 'text', { placeholder: "AWS_ACCESS_KEY_ID" })}
                ${renderSettingsItem('安全私钥 (Secret Key)', `publish_control.direct_upload.s3.secret_key`, cfg.secret_key, 'password', { placeholder: "AWS_SECRET_ACCESS_KEY" })}
                ${renderPlatformAdvancedGroup('高级扩展参数 (Region / Endpoint / ACL)', `
                    ${renderSettingsItem('存储区域 (Region)', `publish_control.direct_upload.s3.region`, cfg.region || 'us-east-1', 'text', { placeholder: "例如: us-east-1" })}
                    ${renderSettingsItem('自定义端点 (Endpoint URL)', `publish_control.direct_upload.s3.endpoint_url`, cfg.endpoint_url, 'text', { placeholder: "Cloudflare R2, MinIO, or custom endpoint", description: "如果使用 Cloudflare R2 等非标准 AWS 存储，请填写此项。" })}
                    ${renderSettingsItem('公开访问域名 (Public URL)', `publish_control.direct_upload.s3.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://myblog.com", description: "网站公开访问的基地址。" })}
                    ${renderSettingsItem('存储路径前缀 (Prefix)', `publish_control.direct_upload.s3.prefix`, cfg.prefix, 'text', { placeholder: "可选前缀，例如: html-site" })}
                    ${renderSettingsItem('对象访问控制 (ACL)', `publish_control.direct_upload.s3.acl`, cfg.acl, 'text', { placeholder: "例如: public-read" })}
                `)}
            `;
        } else if (id === 'github_pages') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 GitHub Pages 极简向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">系统支持自动感应本地 Git 账户、探测本地 SSH 免密连通性，或一键申请 Access Token。</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" style="background: rgba(163, 76, 255, 0.15); border: 1px solid rgba(163, 76, 255, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerGitCredentialsSense(this, 'publish_control.direct_upload.github_pages')">🔑 自动感应本地 Git 凭据</button>
                        <button type="button" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerGithubSSHCheck(this)">🔍 自动探测本地 SSH 免密</button>
                        <a href="https://github.com/settings/tokens/new?scopes=repo&description=Plenipes-Syndication" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Token 申请魔术链接</a>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('访问令牌 (Personal Access Token / Token)', `publish_control.direct_upload.github_pages.token`, cfg.token || cfg.git_token || '', 'password', { placeholder: "例如: ghp_xxxxxxxxxxxx (使用 HTTPS 协议建仓/推送时必填，SSH 免密可留空)", description: "GitHub 个人访问令牌，需包含 repo 权限。使用 SSH 免密部署时可留空。" })}
                ${renderSettingsItem('仓库 URL (Repo URL)', `publish_control.direct_upload.github_pages.repo_url`, cfg.repo_url, 'text', { placeholder: "例如: git@github.com:username/repo.git", description: "您的 GitHub 仓库的 SSH 或 HTTPS 地址。" })}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.github_pages.branch`, cfg.branch || 'gh-pages', 'text', { placeholder: "例如: gh-pages" })}
                ${renderPlatformAdvancedGroup('高级 Git 参数 (CNAME / 代理 / 用户身份)', `
                    ${renderSettingsItem('自定义域名 (CNAME)', `publish_control.direct_upload.github_pages.cname`, cfg.cname, 'text', { placeholder: "例如: blog.example.com", description: "可选，若绑定了自定义域名请在此填写。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.github_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('Git 用户名', `publish_control.direct_upload.github_pages.git_user_name`, cfg.git_user_name || 'Plenipes Bot', 'text')}
                    ${renderSettingsItem('Git 邮箱', `publish_control.direct_upload.github_pages.git_user_email`, cfg.git_user_email || 'bot@plenipes.press', 'text')}
                    ${renderSettingsItem('强制推送 (Force Push)', `publish_control.direct_upload.github_pages.force_push`, cfg.force_push, 'checkbox')}
                `)}
            `;
        } else if (id === 'gitee_pages') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 Gitee Pages 极简向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">系统支持自动感应本地 Git 账户凭据，或一键申请 Gitee 私人令牌 (Personal Access Token)。</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" style="background: rgba(163, 76, 255, 0.15); border: 1px solid rgba(163, 76, 255, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerGitCredentialsSense(this, 'publish_control.direct_upload.gitee_pages')">🔑 自动感应本地 Git 凭据</button>
                        <a href="https://gitee.com/profile/personal_access_tokens/new" target="_blank" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Token 申请魔术链接</a>
                        <a href="https://gitee.com" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 访问 Gitee 官网</a>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('私人令牌 (Access Token)', `publish_control.direct_upload.gitee_pages.access_token`, cfg.access_token || cfg.token || '', 'password', { placeholder: "例如: Gitee Personal Access Token" })}
                ${renderSettingsItem('仓库 URL (Repo URL)', `publish_control.direct_upload.gitee_pages.repo_url`, cfg.repo_url, 'text', { placeholder: "例如: git@gitee.com:username/repo.git", description: "您的 Gitee 仓库的 SSH 或 HTTPS 地址。" })}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.gitee_pages.branch`, cfg.branch || 'gitee-pages', 'text', { placeholder: "例如: gitee-pages" })}
                ${renderPlatformAdvancedGroup('高级 Gitee 参数 (代理 / 用户身份)', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.gitee_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: direct 或代理地址", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('Git 用户名', `publish_control.direct_upload.gitee_pages.git_user_name`, cfg.git_user_name || 'Plenipes Bot', 'text')}
                    ${renderSettingsItem('Git 邮箱', `publish_control.direct_upload.gitee_pages.git_user_email`, cfg.git_user_email || 'bot@plenipes.press', 'text')}
                `)}
            `;
        } else if (id === 'gitlab_pages') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 GitLab Pages 极简向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">一键感应本地 Git 凭据或直达申请具有 api/read_repository 权限的 Personal Access Token。</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" style="background: rgba(163, 76, 255, 0.15); border: 1px solid rgba(163, 76, 255, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerGitCredentialsSense(this, 'publish_control.direct_upload.gitlab_pages')">🔑 自动感应本地 Git 凭据</button>
                        <a href="https://gitlab.com/-/profile/personal_access_tokens" target="_blank" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Token 申请魔术链接</a>
                        <a href="https://gitlab.com" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 访问 GitLab 官网</a>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('访问令牌 (Personal Access Token)', `publish_control.direct_upload.gitlab_pages.access_token`, cfg.access_token || cfg.token || '', 'password', { placeholder: "GitLab Personal Access Token" })}
                ${renderSettingsItem('仓库 URL (Repo URL)', `publish_control.direct_upload.gitlab_pages.repo_url`, cfg.repo_url, 'text', { placeholder: "例如: git@gitlab.com:username/repo.git", description: "您的 GitLab 仓库的 SSH 或 HTTPS 地址。" })}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.gitlab_pages.branch`, cfg.branch || 'main', 'text', { placeholder: "例如: main" })}
                ${renderPlatformAdvancedGroup('高级 GitLab 参数 (代理 / 用户身份)', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.gitlab_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: direct 或代理地址" })}
                    ${renderSettingsItem('Git 用户名', `publish_control.direct_upload.gitlab_pages.git_user_name`, cfg.git_user_name || 'Plenipes Bot', 'text')}
                    ${renderSettingsItem('Git 邮箱', `publish_control.direct_upload.gitlab_pages.git_user_email`, cfg.git_user_email || 'bot@plenipes.press', 'text')}
                `)}
            `;
        } else if (id === 'firebase') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 Firebase Hosting 极简向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">一键在本地拉起 Firebase CLI 免密登录授权，自动同步配置凭据。</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerFirebaseOAuthLogin(this)">🔑 本地一键免密授权 (Firebase CLI)</button>
                        <a href="https://console.firebase.google.com" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🌐 访问 Firebase 控制台</a>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('项目 ID (Project ID)', `publish_control.direct_upload.firebase.project_id`, cfg.project_id, 'text', { placeholder: "例如: my-firebase-project" })}
                ${renderSettingsItem('部署 Token (CLI Token)', `publish_control.direct_upload.firebase.token`, cfg.token, 'password', { placeholder: "Firebase CI Token (使用一键授权或 firebase login:ci 获取)" })}
                ${renderPlatformAdvancedGroup('高级站点与代理参数', `
                    ${renderSettingsItem('站点 ID (Site ID)', `publish_control.direct_upload.firebase.site`, cfg.site, 'text', { placeholder: "可选，多站点支持" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.firebase.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'cloudflare_pages') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 Cloudflare Pages 极简授权向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">系统支持在后台一键唤醒 Wrangler CLI 免密授权，或直接申请 Cloudflare API Token。</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerCloudflareOAuthLogin(this)">🔑 本地一键免密授权 (Wrangler CLI)</button>
                        <a href="https://dash.cloudflare.com/profile/api-tokens" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 直达 API Token 申请页</a>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('项目名称 (Project Name)', `publish_control.direct_upload.cloudflare_pages.project_name`, cfg.project_name, 'text', { placeholder: "例如: my-docs-site" })}
                ${renderSettingsItem('API 访问令牌 (Token)', `publish_control.direct_upload.cloudflare_pages.token`, cfg.token, 'password', { placeholder: "请输入 Cloudflare API Token" })}
                ${renderPlatformAdvancedGroup('高级分支与环境参数', `
                    ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.cloudflare_pages.branch`, cfg.branch || 'production', 'text', { placeholder: "例如: production" })}
                    ${renderSettingsItem('账号 ID (Account ID)', `publish_control.direct_upload.cloudflare_pages.account_id`, cfg.account_id, 'text', { placeholder: "Cloudflare 账号 ID (可选)" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.cloudflare_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('Wrangler CLI 路径', `publish_control.direct_upload.cloudflare_pages.wrangler_path`, cfg.wrangler_path || 'wrangler', 'text')}
                `)}
            `;
        } else if (id === 'netlify') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 Netlify 极简授权向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">一键拉起 Netlify CLI 免密授权获取身份凭据，或者直达 Personal Access Tokens 申请。</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerNetlifyOAuthLogin(this)">🔑 本地一键免密授权 (Netlify CLI)</button>
                        <a href="https://app.netlify.com/user/applications#personal-access-tokens" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 直达 Access Tokens 申请页</a>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('站点 ID (Site ID)', `publish_control.direct_upload.netlify.site_id`, cfg.site_id, 'text', { placeholder: "例如: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" })}
                ${renderSettingsItem('身份凭证 (Auth Token)', `publish_control.direct_upload.netlify.auth_token`, cfg.auth_token, 'password', { placeholder: "Netlify Personal Access Token" })}
                ${renderPlatformAdvancedGroup('高级部署与代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.netlify.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('生产模式部署 (Prod)', `publish_control.direct_upload.netlify.prod`, cfg.prod !== false, 'checkbox')}
                    ${renderSettingsItem('Netlify CLI 路径', `publish_control.direct_upload.netlify.netlify_path`, cfg.netlify_path || 'netlify', 'text')}
                `)}
            `;
        } else if (id === 'vercel') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 Vercel 极简授权向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">一键启动 Vercel CLI 免密授权获取身份 Token，亦可直达 Vercel Account Tokens 申请。</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerVercelOAuthLogin(this)">🔑 本地一键免密授权 (Vercel CLI)</button>
                        <a href="https://vercel.com/account/tokens" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px;">🔗 直达 Tokens 申请页</a>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('访问令牌 (Token)', `publish_control.direct_upload.vercel.token`, cfg.token, 'password', { placeholder: "请输入 Vercel 访问令牌 (Token)" })}
                ${renderSettingsItem('项目名称 (Project Name)', `publish_control.direct_upload.vercel.project_name`, cfg.project_name, 'text', { placeholder: "请输入 Vercel 项目名称" })}
                ${renderPlatformAdvancedGroup('高级组织与代理参数', `
                    ${renderSettingsItem('组织 ID (Org ID)', `publish_control.direct_upload.vercel.org_id`, cfg.org_id, 'text', { placeholder: "请输入 Vercel 组织 ID (可选)" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.vercel.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('生产部署 (Prod)', `publish_control.direct_upload.vercel.prod`, cfg.prod !== false, 'checkbox')}
                    ${renderSettingsItem('Vercel CLI 路径', `publish_control.direct_upload.vercel.vercel_path`, cfg.vercel_path || 'vercel', 'text')}
                `)}
            `;
        } else if (id === 'aliyun_oss') {
            return `
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.aliyun_oss.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-oss-bucket" })}
                ${renderSettingsItem('接入点 (Endpoint)', `publish_control.direct_upload.aliyun_oss.endpoint`, cfg.endpoint, 'text', { placeholder: "例如: oss-cn-hangzhou.aliyuncs.com" })}
                ${renderSettingsItem('访问密钥 ID (Access Key ID)', `publish_control.direct_upload.aliyun_oss.access_key_id`, cfg.access_key_id, 'text', { placeholder: "Access Key ID" })}
                ${renderSettingsItem('安全密钥 (Access Key Secret)', `publish_control.direct_upload.aliyun_oss.access_key_secret`, cfg.access_key_secret, 'password', { placeholder: "Access Key Secret" })}
                <div class=\"api-token-helper\">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 阿里云 AccessKey 获取向导</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://ram.console.aliyun.com/manage/ak" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达阿里云 AccessKey 管理页</a>
                    </div>
                </div>
                ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.aliyun_oss.prefix`, cfg.prefix, 'text', { placeholder: "例如: site-root (可选)" })}
                ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.aliyun_oss.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://blog.mydomain.com", description: "如果配置了自定义 CDN 域名，请在此填写。" })}
                ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.aliyun_oss.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
            `;
        } else if (id === 'tencent_cos') {
            return `
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.tencent_cos.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-cos-1250000000" })}
                ${renderSettingsItem('存储区域 (Region)', `publish_control.direct_upload.tencent_cos.region`, cfg.region, 'text', { placeholder: "例如: ap-shanghai" })}
                ${renderSettingsItem('密钥 ID (SecretId)', `publish_control.direct_upload.tencent_cos.secret_id`, cfg.secret_id, 'text', { placeholder: "SecretId" })}
                ${renderSettingsItem('安全密钥 (SecretKey)', `publish_control.direct_upload.tencent_cos.secret_key`, cfg.secret_key, 'password', { placeholder: "SecretKey" })}
                <div class=\"api-token-helper\">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 腾讯云 API 密钥获取向导</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://console.cloud.tencent.com/cam/capi" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达腾讯云 API 密钥管理页</a>
                    </div>
                </div>
                ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.tencent_cos.prefix`, cfg.prefix, 'text', { placeholder: "例如: html-site (可选)" })}
                ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.tencent_cos.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://blog.mydomain.com", description: "如果配置了自定义 CDN 域名，请在此填写。" })}
                ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.tencent_cos.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
            `;
        } else if (id === 'upyun_uss') {
            return `
                ${renderSettingsItem('服务名称 (Bucket)', `publish_control.direct_upload.upyun_uss.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-upyun-service" })}
                ${renderSettingsItem('操作员 (Operator)', `publish_control.direct_upload.upyun_uss.operator`, cfg.operator, 'text', { placeholder: "操作员账号" })}
                ${renderSettingsItem('操作员密码 (Password)', `publish_control.direct_upload.upyun_uss.password`, cfg.password, 'password', { placeholder: "操作员密码" })}
                ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.upyun_uss.prefix`, cfg.prefix, 'text', { placeholder: "例如: site (可选)" })}
                ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.upyun_uss.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://site.upaiyun.com", description: "网站公开访问的基地址。" })}
                ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.upyun_uss.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
            `;
        } else if (id === 'sftp') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 本地 SSH 密钥极简向导</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4;">如果您的服务器配置了密钥登录，系统可尝试自动感应本地常用 SSH 私钥文件物理路径（如 <code>id_ed25519</code> 或 <code>id_rsa</code>）并自动回填。</p>
                    <div style="margin-top: 8px;">
                        <button type="button" class="helper-btn" onclick="window.triggerSFTPSensing(this)">🔑 自动感应本地 SSH 私钥</button>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('服务器主机 (Host)', `publish_control.direct_upload.sftp.host`, cfg.host, 'text', { placeholder: "例如: 123.45.67.89 或 sftp.myblog.com" })}
                ${renderSettingsItem('SSH 端口 (Port)', `publish_control.direct_upload.sftp.port`, cfg.port || 22, 'number', { placeholder: "默认 22" })}
                ${renderSettingsItem('登录用户名 (Username)', `publish_control.direct_upload.sftp.username`, cfg.username, 'text', { placeholder: "例如: root" })}
                ${renderSettingsItem('登录密码 (Password)', `publish_control.direct_upload.sftp.password`, cfg.password, 'password', { placeholder: "SSH 密码，若使用私钥可留空" })}
                ${renderSettingsItem('SSH 私钥 (Private Key)', `publish_control.direct_upload.sftp.private_key`, cfg.private_key, 'textarea', { placeholder: "私钥文件路径或私钥字符串内容", rows: 4 })}
                ${renderSettingsItem('私钥口令 (Passphrase)', `publish_control.direct_upload.sftp.passphrase`, cfg.passphrase, 'password', { placeholder: "私钥保护口令（如有）" })}
                ${renderSettingsItem('远程目标目录 (Remote Path)', `publish_control.direct_upload.sftp.remote_path`, cfg.remote_path, 'text', { placeholder: "例如: /var/www/html/blog" })}
                ${renderSettingsItem('站点访问域名 (Public URL)', `publish_control.direct_upload.sftp.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://blog.mysite.com", description: "网站公开访问的基地址。" })}
                ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.sftp.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
            `;
        }
    }

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
            <div class=\"api-token-helper wordpress-helper\">
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
            <div class=\"api-token-helper\">
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
            <div class=\"api-token-helper ghost-helper\">
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
            <div class=\"api-token-helper\">
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
            <div class=\"api-token-helper\">
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
            <div class=\"api-token-helper\">
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
            <div class=\"api-token-helper\">
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
    } else {
        return `
            ${renderSettingsItem('凭据/密钥 (Key/Token)', category === 'hosting' ? `publish_control.direct_upload.${id}.api_key` : `syndication.${id}.api_key`, cfg.api_key || cfg.app_password, 'password', { placeholder: "请输入访问令牌/API密钥" })}
            ${renderSettingsItem('发布目标 (URL/Bucket)', category === 'hosting' ? `publish_control.direct_upload.${id}.url` : `syndication.${id}.url`, cfg.url, 'text', { placeholder: "请输入目标 URL 或存储桶名称" })}
            ${renderSettingsItem('账号/ID', category === 'hosting' ? `publish_control.direct_upload.${id}.username` : `syndication.${id}.username`, cfg.username, 'text', { placeholder: "请输入账号名" })}
            ${renderSettingsItem('独立代理地址 (Proxy)', category === 'hosting' ? `publish_control.direct_upload.${id}.proxy` : `syndication.${id}.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
        `;
    }
};

window.renderPlatformConfig = (id, cfg, category = 'publisher') => {
    const portalGuide = window.renderPlatformPortalGuide ? window.renderPlatformPortalGuide(id) : '';
    const content = window.rawRenderPlatformConfig ? window.rawRenderPlatformConfig(id, cfg, category) : '';
    if (!content.includes('api-token-helper') && portalGuide) {
        return portalGuide + content;
    }
    return content;
};

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
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.s3.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-assets-bucket" })}
            ${renderSettingsItem('访问密钥 ID (Access Key)', `image_hosting.s3.access_key`, cfg.access_key, 'text', { placeholder: "AWS_ACCESS_KEY_ID" })}
            ${renderSettingsItem('安全私钥 (Secret Key)', `image_hosting.s3.secret_key`, cfg.secret_key, 'password', { placeholder: "AWS_SECRET_ACCESS_KEY" })}
            ${renderSettingsItem('存储区域 (Region)', `image_hosting.s3.region`, cfg.region || 'us-east-1', 'text', { placeholder: "例如: ap-east-1" })}
            ${renderSettingsItem('自定义端点 (Endpoint URL)', `image_hosting.s3.endpoint_url`, cfg.endpoint_url, 'text', { placeholder: "Cloudflare R2, MinIO, or custom endpoint", description: "如果使用 Cloudflare R2 等非标准 AWS 存储，请填写此项。" })}
            ${renderSettingsItem('CDN 访问域名 (Public URL)', `image_hosting.s3.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://cdn.myblog.com", description: "图片公开访问的基地址，留空则使用默认 S3 访问地址。" })}
            ${renderSettingsItem('存储路径前缀 (Prefix)', `image_hosting.s3.prefix`, cfg.prefix, 'text', { placeholder: "例如: blog-assets" })}
            ${renderSettingsItem('对象访问控制 (ACL)', `image_hosting.s3.acl`, cfg.acl, 'text', { placeholder: "例如: public-read", description: "上传对象的权限控制 (留空或填写 public-read 等)。" })}
            ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.s3.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 S3 端点的网络连通校验。" })}
        `;
    } else if (id === 'github') {
        return `
            ${renderSettingsItem('GitHub 仓库名 (Repo)', `image_hosting.github.repo`, cfg.repo, 'text', { placeholder: "例如: username/repo", description: "格式必须为 '用户名/仓库名'" })}
            ${renderSettingsItem('分支 (Branch)', `image_hosting.github.branch`, cfg.branch || 'main', 'text', { placeholder: "例如: main" })}
            ${renderSettingsItem('访问令牌 (Token)', `image_hosting.github.token`, cfg.token, 'password', { placeholder: "GitHub Personal Access Token" })}
            <div class=\"api-token-helper\">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 GitHub Token 直达链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://github.com/settings/tokens/new?scopes=repo&description=Illacme-Plenipes-Image-Hosting" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Token 申请</a>
                </div>
            </div>
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.github.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.github.cdn_url`, cfg.cdn_url, 'text', { placeholder: "例如: https://cdn.jsdelivr.net/gh/username/repo@branch", description: "可选，留空则使用 jsdelivr 默认加速链接。" })}
            ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.github.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 GitHub API 的网络校验。" })}
        `;
    } else if (id === 'sm_ms') {
        return `
            ${renderSettingsItem('SM.MS 访问密钥 (Token)', `image_hosting.sm_ms.token`, cfg.token, 'password', { placeholder: "请输入 SM.MS Secret Token", description: "登录 SM.MS 官网，在 User -> API Token 中获取。" })}
            <div class=\"api-token-helper\">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Token 直达魔术链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://sm.ms/home/apitoken" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 SM.MS 密钥申请页</a>
                </div>
            </div>
            ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.sm_ms.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 SM.MS API 的校验。" })}
        `;
    } else if (id === 'imgur') {
        return `
            ${renderSettingsItem('客户端 ID (Client ID)', `image_hosting.imgur.client_id`, cfg.client_id, 'text', { placeholder: "Imgur Client ID", description: "匿名上传所需，在 Imgur API Application 页面申请。" })}
            ${renderSettingsItem('访问令牌 (Access Token)', `image_hosting.imgur.token`, cfg.token, 'password', { placeholder: "Imgur Access Token (可选)", description: "若绑定至个人账户请填写此项。" })}
            <div class=\"api-token-helper\">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 Imgur 授权直达链接</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://api.imgur.com/oauth2/addclient" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Imgur Client ID 申请页</a>
                </div>
            </div>
            ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.imgur.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 Imgur API 的校验。" })}
        `;
    } else if (id === 'telegraph') {
        return `
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.telegraph.endpoint`, cfg.endpoint || 'https://telegra.ph', 'text', { placeholder: "例如: https://telegra.ph", description: "Telegraph API 基础端点，允许填写反代域名解决连接超时。" })}
            ${renderSettingsItem('代理地址 (HTTP Proxy)', `image_hosting.telegraph.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:7890 (可选)", description: "可选。配置本地代理以穿透 Telegraph 端点的校验。" })}
        `;
    } else if (id === 'aliyun_oss') {
        return `
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.aliyun_oss.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-oss-bucket" })}
            ${renderSettingsItem('访问域名 (Endpoint)', `image_hosting.aliyun_oss.endpoint`, cfg.endpoint, 'text', { placeholder: "例如: oss-cn-hangzhou.aliyuncs.com" })}
            ${renderSettingsItem('访问密钥 ID (AccessKey ID)', `image_hosting.aliyun_oss.access_key_id`, cfg.access_key_id, 'text', { placeholder: "AccessKey ID" })}
            ${renderSettingsItem('访问密钥 Secret (AccessKey Secret)', `image_hosting.aliyun_oss.access_key_secret`, cfg.access_key_secret, 'password', { placeholder: "AccessKey Secret" })}
            <div class=\"api-token-helper\">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 阿里云 AccessKey 获取向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://ram.console.aliyun.com/manage/ak" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达阿里云 AccessKey 管理页</a>
                </div>
            </div>
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.aliyun_oss.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.aliyun_oss.cdn_url`, cfg.cdn_url, 'text', { placeholder: "例如: https://cdn.myblog.com", description: "可选。配置后将优先使用此域名生成图片链接。" })}
        `;
    } else if (id === 'tencent_cos') {
        return `
            ${renderSettingsItem('存储桶名称 (Bucket)', `image_hosting.tencent_cos.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-cos-bucket-125000000" })}
            ${renderSettingsItem('所属区域 (Region)', `image_hosting.tencent_cos.region`, cfg.region, 'text', { placeholder: "例如: ap-guangzhou" })}
            ${renderSettingsItem('安全凭证 SecretId', `image_hosting.tencent_cos.secret_id`, cfg.secret_id, 'text', { placeholder: "SecretId" })}
            ${renderSettingsItem('安全凭证 SecretKey', `image_hosting.tencent_cos.secret_key`, cfg.secret_key, 'password', { placeholder: "SecretKey" })}
            <div class=\"api-token-helper\">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 腾讯云 API 密钥获取向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://console.cloud.tencent.com/cam/capi" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达腾讯云 API 密钥管理页</a>
                </div>
            </div>
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.tencent_cos.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            ${renderSettingsItem('自定义加速域名 (CDN URL)', `image_hosting.tencent_cos.cdn_url`, cfg.cdn_url, 'text', { placeholder: "例如: https://cdn.myblog.com", description: "可选。配置后将优先使用此域名生成图片链接。" })}
        `;
    } else if (id === 'qiniu_kodo') {
        return `
            ${renderSettingsItem('存储空间名称 (Bucket)', `image_hosting.qiniu_kodo.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-kodo-bucket" })}
            ${renderSettingsItem('访问密钥 Access Key (AK)', `image_hosting.qiniu_kodo.access_key`, cfg.access_key, 'text', { placeholder: "Access Key" })}
            ${renderSettingsItem('访问密钥 Secret Key (SK)', `image_hosting.qiniu_kodo.secret_key`, cfg.secret_key, 'password', { placeholder: "Secret Key" })}
            <div class=\"api-token-helper\">
                <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>💡 七牛云个人密钥向导</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 2px;">
                    <a href="https://portal.qiniu.com/user/key" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达七牛云个人密钥页</a>
                </div>
            </div>
            ${renderSettingsItem('空间外链域名 (Domain)', `image_hosting.qiniu_kodo.domain`, cfg.domain, 'text', { placeholder: "例如: http://xxxx.qiniudn.com" })}
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.qiniu_kodo.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
        `;
    } else if (id === 'upyun_uss') {
        return `
            ${renderSettingsItem('服务名称 (Bucket)', `image_hosting.upyun_uss.bucket`, cfg.bucket, 'text', { placeholder: "请输入又拍云服务名称" })}
            ${renderSettingsItem('操作员名称 (Operator)', `image_hosting.upyun_uss.operator`, cfg.operator, 'text', { placeholder: "请输入操作员名称" })}
            ${renderSettingsItem('操作员密码 (Password)', `image_hosting.upyun_uss.password`, cfg.password, 'password', { placeholder: "请输入操作员密码" })}
            ${renderSettingsItem('存储路径前缀 (Path)', `image_hosting.upyun_uss.path`, cfg.path || 'images', 'text', { placeholder: "例如: images" })}
            ${renderSettingsItem('加速域名 (Domain)', `image_hosting.upyun_uss.domain`, cfg.domain, 'text', { placeholder: "例如: https://xxx.upaiyun.com" })}
        `;
    } else if (id === 'loli_io') {
        return `
            ${renderSettingsItem('访问密钥 (Token)', `image_hosting.loli_io.token`, cfg.token, 'password', { placeholder: "请输入路过图床 API Token", description: "登录 img.lol 或 loli.io 官网获取。" })}
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.loli_io.endpoint`, cfg.endpoint || 'https://img.lol/api/v1/upload', 'text', { placeholder: "默认: https://img.lol/api/v1/upload" })}
        `;
    } else if (id === 'superbed') {
        return `
            ${renderSettingsItem('访问密钥 (Token)', `image_hosting.superbed.token`, cfg.token, 'password', { placeholder: "请输入聚合图床 API Token" })}
            ${renderSettingsItem('API 端点 (Endpoint)', `image_hosting.superbed.endpoint`, cfg.endpoint || 'https://api.superbed.cn/upload', 'text', { placeholder: "默认: https://api.superbed.cn/upload" })}
        `;
    } else if (id === 'lsky_pro') {
        return `
            ${renderSettingsItem('接口地址 (Endpoint)', `image_hosting.lsky_pro.endpoint`, cfg.endpoint, 'text', { placeholder: "例如: https://lsky.yourdomain.com", description: "您的兰空图床实例地址，不带 /api/v1 路径。" })}
            ${renderSettingsItem('鉴权 Token', `image_hosting.lsky_pro.token`, cfg.token, 'password', { placeholder: "格式如: Bearer 1|xxxxxx" })}
            ${renderSettingsItem('存储策略 ID (Strategy ID)', `image_hosting.lsky_pro.strategy_id`, cfg.strategy_id, 'text', { placeholder: "可选，不填为默认存储策略" })}
            ${renderSettingsItem('相册 ID (Album ID)', `image_hosting.lsky_pro.album_id`, cfg.album_id, 'text', { placeholder: "可选，不填则不归类至相册" })}
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



window.triggerGithubSSHCheck = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在探测 SSH...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "正在探测您的本地 SSH 与 GitHub 服务的连通情况...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/github/ssh-status');
        if (res && res.ssh_ok) {
            infoEl.style.color = '#10B981';
            infoEl.innerHTML = `✅ <b>探测成功！</b>检测到本地 SSH 已打通 GitHub (<span style="color:#fff">账户: ${res.username}</span>)。建议您优先使用 SSH 协议的 Repo URL，此令牌 (Token) 项可留空！`;
            btn.innerText = "🔑 SSH 已打通";
            btn.style.borderColor = '#10B981';
            btn.style.background = 'rgba(16, 185, 129, 0.15)';
        } else {
            infoEl.style.color = '#F59E0B';
            infoEl.innerText = `⚠️ 未能打通本地 SSH 免密: ${res ? res.message : "连接失败"}。建议您使用上方「官方一键创建」生成 Token 填入。`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 探测发生异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerFirebaseOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "已尝试在后台拉取 Firebase CLI 登录流，请在浏览器中确认授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/firebase/oauth-login', { method: 'POST' });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待本地凭证同步... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc('/api/plugins/firebase/oauth-status');
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = '#10B981';
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.username}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = '#10B981';
                        btn.style.background = 'rgba(16, 185, 129, 0.15)';

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.firebase.token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = status.token || "firebase_oauth_session";
                            tokenInput.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        infoEl.style.color = '#EF4444';
                        infoEl.innerText = "❌ 授权探测超时，请检查浏览器是否正常弹出并登录，或者选择手动粘贴 Token 填入。";
                        btn.disabled = false;
                        btn.innerText = originalText;
                    }
                } catch (probeErr) { }
            }, 2000);
        } else {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = `❌ 无法拉取授权: ${res ? res.message : "未知错误"}`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};




window.triggerCloudflareOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest(".api-token-helper");
    const infoEl = container.querySelector(".oauth-status-info");
    infoEl.style.display = "block";
    infoEl.style.color = "var(--neon-cyan)";
    infoEl.innerText = "已尝试在后台拉取 Cloudflare OAuth 授权页，请在弹出的系统浏览器中点击「Authorize」完成授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc("/api/plugins/cloudflare/oauth-login", { method: "POST" });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待浏览器授权确认... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc("/api/plugins/cloudflare/oauth-status");
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = "#10B981";
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.email || status.account_name}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = "#10B981";
                        btn.style.background = "rgba(16, 185, 129, 0.15)";

                        if (status.account_id) {
                            const accInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.account_id"]');
                            if (accInput) {
                                accInput.value = status.account_id;
                                accInput.dispatchEvent(new Event("input", { bubbles: true }));
                            }
                        }

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = "wrangler_oauth_session";
                            tokenInput.dispatchEvent(new Event("input", { bubbles: true }));
                        }

                        if (status.projects && status.projects.length > 0) {
                            const projInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.project_name"]');
                            const branchInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.branch"]');

                            if (status.projects.length === 1) {
                                const p = status.projects[0];
                                if (projInput) {
                                    projInput.value = p.name;
                                    projInput.dispatchEvent(new Event("input", { bubbles: true }));
                                }
                                if (branchInput && p.branch) {
                                    branchInput.value = p.branch;
                                    branchInput.dispatchEvent(new Event("input", { bubbles: true }));
                                }
                                if (window.showToast) window.showToast(`🎉 已自动填充项目名称 ${p.name} 及部署分支 ${p.branch}！`, "success");
                            } else {
                                let html = `<div class="quick-proj-selector" style="margin-top: 8px; font-size: 0.7rem; color: var(--text-dim);">`;
                                html += `💡 发现多个 Pages 项目，点击可一键自动回填：<br/>`;
                                for (let p of status.projects) {
                                    html += `<span class="helper-btn" onclick="window.applyCloudflareProjectSelection('${p.name}', '${p.branch || "production"}')" style="margin: 4px 4px 0 0; padding: 2px 6px !important; display: inline-flex !important; font-size: 0.65rem !important;">${p.name} (${p.branch || "production"})</span>`;
                                }
                                html += `</div>`;
                                infoEl.innerHTML += html;
                            }
                        }
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        infoEl.style.color = "#EF4444";
                        infoEl.innerText = "❌ 授权探测超时，请检查浏览器是否正常弹出，或者选择手动一键创建 Token 粘贴填入。";
                        btn.disabled = false;
                        btn.innerText = originalText;
                    }
                } catch (probeErr) { }
            }, 2000);
        } else {
            infoEl.style.color = "#EF4444";
            infoEl.innerText = `❌ 无法拉取授权页面: ${res ? res.message : "未知错误"}`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = "#EF4444";
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerNetlifyOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest(".api-token-helper");
    const infoEl = container.querySelector(".oauth-status-info");
    infoEl.style.display = "block";
    infoEl.style.color = "var(--neon-cyan)";
    infoEl.innerText = "已尝试在后台拉起 Netlify OAuth 授权页，请在弹出的系统浏览器中点击「Authorize」完成授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc("/api/plugins/netlify/oauth-login", { method: "POST" });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待浏览器授权确认... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc("/api/plugins/netlify/oauth-status");
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = "#10B981";
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.email || status.name}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = "#10B981";
                        btn.style.background = "rgba(16, 185, 129, 0.15)";

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.netlify.auth_token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = status.auth_token || "netlify_oauth_session";
                            tokenInput.dispatchEvent(new Event("input", { bubbles: true }));
                        }
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        infoEl.style.color = "#EF4444";
                        infoEl.innerText = "❌ 授权探测超时，请检查浏览器是否正常弹出，或者选择手动一键创建 Token 粘贴填入. ";
                        btn.disabled = false;
                        btn.innerText = originalText;
                    }
                } catch (probeErr) { }
            }, 2000);
        } else {
            infoEl.style.color = "#EF4444";
            infoEl.innerText = `❌ 无法拉取授权页面: ${res ? res.message : "未知错误"}`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = "#EF4444";
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerVercelOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest(".api-token-helper");
    const infoEl = container.querySelector(".oauth-status-info");
    infoEl.style.display = "block";
    infoEl.style.color = "var(--neon-cyan)";
    infoEl.innerText = "已尝试在后台拉起 Vercel OAuth 授权页，请在弹出的系统浏览器中点击「Authorize」完成授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc("/api/plugins/vercel/oauth-login", { method: "POST" });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待浏览器授权确认... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc("/api/plugins/vercel/oauth-status");
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = "#10B981";
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.email || status.username}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = "#10B981";
                        btn.style.background = "rgba(16, 185, 129, 0.15)";

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.vercel.token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = status.token || "vercel_oauth_session";
                            tokenInput.dispatchEvent(new Event("input", { bubbles: true }));
                        }
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        infoEl.style.color = "#EF4444";
                        infoEl.innerText = "❌ 授权探测超时，请检查浏览器是否正常弹出，或者选择手动一键创建 Token 粘贴填入。";
                        btn.disabled = false;
                        btn.innerText = originalText;
                    }
                } catch (probeErr) { }
            }, 2000);
        } else {
            infoEl.style.color = "#EF4444";
            infoEl.innerText = `❌ 无法拉取授权页面: ${res ? res.message : "未知错误"}`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = "#EF4444";
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.applyCloudflareProjectSelection = (name, branch) => {
    const projInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.project_name"]');
    const branchInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.branch"]');
    if (projInput) {
        projInput.value = name;
        projInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
    if (branchInput) {
        branchInput.value = branch;
        branchInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
    if (window.showToast) window.showToast(`已一键回填项目：${name}！`, "success");
};

window.triggerAWSCredentialsSense = async (btn, prefix) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在读取本地凭证...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "正在尝试读取本地 ~/.aws/credentials 与 config ...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/aws/credentials-status');
        if (res && res.logged_in) {
            const akInput = document.querySelector(`input[name="${prefix}.access_key"]`);
            const skInput = document.querySelector(`input[name="${prefix}.secret_key"]`);
            const regionInput = document.querySelector(`input[name="${prefix}.region"]`);

            if (akInput) {
                akInput.value = res.access_key || '';
                akInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (skInput) {
                skInput.value = res.secret_key || '';
                skInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (regionInput && res.region) {
                regionInput.value = res.region;
                regionInput.dispatchEvent(new Event('input', { bubbles: true }));
            }

            infoEl.style.color = '#10B981';
            infoEl.innerText = "🟢 本地 AWS 凭据感应回填成功！已自动填充密钥与区域。";
            if (window.showToast) window.showToast("本地 AWS 凭据一键免密授权成功！", "success");
        } else {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = "❌ 未检测到本地有效的 ~/.aws/credentials 配置文件。";
            if (window.showToast) window.showToast("未检测到本地 AWS 配置，请手动填写", "warning");
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerSFTPSensing = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在检索 SSH 密钥...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "正在扫描本地 ~/.ssh 目录下的可用私钥...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/sftp/ssh-status');
        if (res && res.success) {
            const pkInput = document.querySelector('textarea[name="publish_control.direct_upload.sftp.private_key"]');
            if (pkInput) {
                pkInput.value = res.private_key_path || '';
                pkInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            infoEl.style.color = '#10B981';
            infoEl.innerText = `🟢 成功感应到本地 SSH 私钥 (${res.key_name})！路径已自动回填。`;
            if (window.showToast) window.showToast(`SSH 密钥路径感应填充成功！`, "success");
        } else {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = `❌ 感应失败: ${res ? res.message : "未找到可用私钥"}`;
            if (window.showToast) window.showToast("未感应到本地常用 SSH 私钥", "warning");
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerGitCredentialsSense = async (btn, pathPrefix = 'publish_control.direct_upload.github_pages') => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在感应 Git 凭据...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container ? container.querySelector('.oauth-status-info') : null;
    if (infoEl) {
        infoEl.style.display = 'block';
        infoEl.style.color = 'var(--neon-cyan)';
        infoEl.innerText = "正在读取本地系统的 git config --global 身份参数...";
    }

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/system/sensing/git', { method: 'POST' });
        if (res && res.success) {
            const nameInput = document.querySelector(`input[name="${pathPrefix}.git_user_name"]`);
            const emailInput = document.querySelector(`input[name="${pathPrefix}.git_user_email"]`);

            let filledCount = 0;
            if (nameInput && res.name) {
                nameInput.value = res.name;
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                filledCount++;
            }
            if (emailInput && res.email) {
                emailInput.value = res.email;
                emailInput.dispatchEvent(new Event('input', { bubbles: true }));
                filledCount++;
            }

            if (infoEl) {
                infoEl.style.color = '#10B981';
                infoEl.innerHTML = `🟢 <b>成功感应本地 Git 凭据！</b> 已填入: <span style="color:#fff">${res.name || '默认'} &lt;${res.email || '未设置'}&gt;</span>`;
            }
            if (window.showToast) window.showToast(`已成功自动感知并填入 ${filledCount} 项 Git 凭据！`, "success");
        } else {
            if (infoEl) {
                infoEl.style.color = '#EF4444';
                infoEl.innerText = `❌ 感应失败: ${res ? res.message : "无法拉取 Git 凭据"}`;
            }
            if (window.showToast) window.showToast("未探测到有效的系统全局 Git user.name/email", "warning");
        }
    } catch (err) {
        if (infoEl) {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        }
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.applyProxyPreset = (val, btn) => {
    let proxyInput = null;
    if (btn) {
        const container = btn.closest('.setting-control') || btn.closest('.setting-row');
        if (container) proxyInput = container.querySelector('input');
    }
    if (!proxyInput) {
        const drawer = document.getElementById('plugin-drawer');
        if (drawer) {
            proxyInput = drawer.querySelector('input[data-path*="proxy"], input[name*="proxy"]');
        }
    }
    if (proxyInput) {
        proxyInput.value = val;
        proxyInput.dispatchEvent(new Event('input', { bubbles: true }));
        if (window.showToast) window.showToast(`已快捷回填代理设置: ${val}`, 'success');
    }
};

window.renderProxyPresetsHtml = () => {
    return `
        <div class="proxy-preset-chips" style="width: 100%; margin-top: 8px; padding-top: 6px; border-top: 1px dashed rgba(255, 255, 255, 0.1); display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 0.7rem; color: var(--text-dim); font-weight: 600;">⚡ 快捷代理预设:</span>
            <button type="button" onclick="window.applyProxyPreset('http://127.0.0.1:7890', this)" style="font-size: 0.68rem; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); color: var(--neon-cyan); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 242, 255, 0.2)'" onmouseout="this.style.background='rgba(0, 242, 255, 0.08)'">Clash (7890)</button>
            <button type="button" onclick="window.applyProxyPreset('http://127.0.0.1:10808', this)" style="font-size: 0.68rem; background: rgba(163, 76, 255, 0.08); border: 1px solid rgba(163, 76, 255, 0.25); color: var(--accent-primary); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(163, 76, 255, 0.2)'" onmouseout="this.style.background='rgba(163, 76, 255, 0.08)'">V2RayN (10808)</button>
            <button type="button" onclick="window.applyProxyPreset('direct', this)" style="font-size: 0.68rem; background: rgba(0, 255, 136, 0.08); border: 1px solid rgba(0, 255, 136, 0.25); color: #00ff88; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 255, 136, 0.2)'" onmouseout="this.style.background='rgba(0, 255, 136, 0.08)'">🌐 物理直连 (direct)</button>
        </div>
    `;
};

window.focusErrorField = (fieldName) => {
    const drawer = document.getElementById('plugin-drawer');
    if (!drawer) return;
    let target = drawer.querySelector(`[name*="${fieldName}"]`) || drawer.querySelector(`[id*="${fieldName}"]`);
    if (!target) {
        const allInputs = Array.from(drawer.querySelectorAll('input, select, textarea'));
        target = allInputs.find(i => (i.name || i.id || '').toLowerCase().includes(fieldName.toLowerCase()));
    }
    if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        target.focus();
        target.style.transition = 'all 0.3s';
        target.style.outline = '2px solid #ff4d4d';
        target.style.boxShadow = '0 0 15px rgba(255, 77, 77, 0.6)';
        setTimeout(() => {
            target.style.outline = '';
            target.style.boxShadow = '';
        }, 2500);
        if (window.showToast) window.showToast(`已为您高亮闪烁定位至参数: ${fieldName}`, 'info');
    }
};
