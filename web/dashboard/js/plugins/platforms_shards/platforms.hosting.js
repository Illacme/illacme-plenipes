/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Hosting & Storage Platforms Shard
 * 职责：托管与存储平台 (S3, GitHub Pages, Gitee Pages, GitLab Pages, Firebase, Cloudflare Pages, Netlify, Vercel, OSS, COS, USS, SFTP) 的配置表单渲染。
 */

var renderSettingsItem = window.renderSettingsItem || (() => "");

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
                ${window.renderPlatformAdvancedGroup('高级扩展参数 (Region / Endpoint / ACL)', `
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
                ${window.renderPlatformAdvancedGroup('高级 Git 参数 (CNAME / 代理 / 用户身份)', `
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
                ${window.renderPlatformAdvancedGroup('高级 Gitee 参数 (代理 / 用户身份)', `
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
                ${window.renderPlatformAdvancedGroup('高级 GitLab 参数 (代理 / 用户身份)', `
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
                ${window.renderPlatformAdvancedGroup('高级站点与代理参数', `
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
                ${window.renderPlatformAdvancedGroup('高级分支与环境参数', `
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
                ${window.renderPlatformAdvancedGroup('高级部署与代理参数', `
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
                ${window.renderPlatformAdvancedGroup('高级组织与代理参数', `
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
                <div class="api-token-helper">
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
                <div class="api-token-helper">
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

    if (window.rawRenderPublisherConfig) {
        return window.rawRenderPublisherConfig(id, cfg, category);
    }
    return '';
};

window.renderPlatformConfig = (id, cfg, category = 'publisher') => {
    const portalGuide = window.renderPlatformPortalGuide ? window.renderPlatformPortalGuide(id) : '';
    const content = window.rawRenderPlatformConfig ? window.rawRenderPlatformConfig(id, cfg, category) : '';
    if (!content.includes('api-token-helper') && portalGuide) {
        return portalGuide + content;
    }
    return content;
};
