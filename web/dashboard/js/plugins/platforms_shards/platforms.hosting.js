/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Hosting & Storage Platforms Shard
 * 职责：托管与存储平台 (S3, GitHub Pages, Gitee Pages, GitLab Pages, Firebase, Cloudflare Pages, Netlify, Vercel, OSS, COS, USS, SFTP) 的配置表单渲染。
 */

var renderSettingsItem = window.renderSettingsItem || (() => "");

/**
 * 🏠 [V80.1] 主站/镜像角色横幅
 * 在每个托管平台配置表单顶部渲染"当前角色"提示条。
 */
function _hostingRoleBanner(platformId) {
    const primaryId = window.settingsData?.publish_control?.primary_hosting_id || '';
    const isPrimary = primaryId === platformId;
    const hasAnyEnabled = (function () {
        const du = window.settingsData?.publish_control?.direct_upload || {};
        return Object.keys(du).length > 0;
    })();

    const roleHtml = isPrimary
        ? `<div class="hosting-role-banner" style="display:flex; align-items:center; gap:8px; padding:10px 14px; border-radius:10px; background:rgba(var(--neon-green-rgb),0.07); border:1px solid rgba(var(--neon-green-rgb),0.25); margin-bottom:4px; width:100%; box-sizing:border-box;">
            <span style="font-size:1.2rem;">🏠</span>
            <div style="flex:1;">
                <div style="font-size:0.82rem; font-weight:800; color:var(--neon-green);">当前主站 (Primary)</div>
                <div style="font-size:0.72rem; color:var(--text-dim); line-height:1.4; margin-top:2px;">
                    所有页面的 <code style="color:var(--accent-secondary);">canonical</code> URL 将指向此平台，搜索引擎只索引此站。其他托管平台将以"镜像"角色运行。
                </div>
            </div>
        </div>`
        : `<div class="hosting-role-banner" style="display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:10px; background:rgba(255,255,255,0.03); border:1px dashed rgba(255,255,255,0.12); margin-bottom:4px; width:100%; box-sizing:border-box;">
            <span style="font-size:1.2rem;">🔄</span>
            <div style="flex:1;">
                <div style="font-size:0.82rem; font-weight:700; color:var(--text-dim);">镜像备用站 (Mirror)</div>
                <div style="font-size:0.72rem; color:var(--text-dim); line-height:1.4; margin-top:2px; opacity:0.75;">
                    此平台作为备用容灾或加速节点使用，canonical 指向主站，不参与 SEO 权重竞争。
                </div>
            </div>
            <button type="button"
                style="flex-shrink:0; background:rgba(0,242,254,0.1); border:1px solid rgba(0,242,254,0.3); color:var(--accent-secondary); font-size:0.75rem; font-weight:700; padding:5px 12px; border-radius:7px; cursor:pointer; white-space:nowrap; transition:all 0.2s;"
                onmouseover="this.style.background='rgba(0,242,254,0.22)'"
                onmouseout="this.style.background='rgba(0,242,254,0.1)'"
                onclick="(async function(){
                    try {
                        await apiFetch('/api/config/update', { method:'POST', body: JSON.stringify({ path: 'publish_control.primary_hosting_id', value: '${platformId}' }) });
                        if (window.settingsData && window.settingsData.publish_control) {
                            window.settingsData.publish_control.primary_hosting_id = '${platformId}';
                        }
                        if (typeof window.renderPlugins === 'function') window.renderPlugins();
                        if (typeof window.openPluginConfig === 'function') window.openPluginConfig('${platformId}', 'hosting');
                        if (typeof addAudit === 'function') addAudit('🏠 已将 ${platformId} 设为主站', 'success');
                    } catch(e) { alert('设置主站失败: ' + e.message); }
                })()">
                🏠 设为主站
            </button>
        </div>`;
    return roleHtml;
}

window.rawRenderPlatformConfig = (id, cfg, category = 'publisher') => {
    const portalGuide = window.renderPlatformPortalGuide ? window.renderPlatformPortalGuide(id) : '';
    if (category === 'hosting') {
        // 每个托管平台配置顶部注入主站/镜像角色横幅
        const roleBanner = _hostingRoleBanner(id);

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
                ${renderSettingsItem('访问密钥 ID (Access Key)', `publish_control.direct_upload.s3.access_key`, cfg.access_key, 'text', { placeholder: "AWS_ACCESS_KEY_ID", description: "AWS IAM 用户的访问密钥公钥（Access Key ID）。" })}
                ${renderSettingsItem('安全私钥 (Secret Key)', `publish_control.direct_upload.s3.secret_key`, cfg.secret_key, 'password', { placeholder: "AWS_SECRET_ACCESS_KEY", description: "AWS IAM 用户的安全私钥（Secret Access Key），用于签名请求。" })}
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.s3.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-hosting-bucket", description: "用于托管静态网页与资源的 S3 存储桶名称。" })}
                ${renderSettingsItem('存储区域 (Region)', `publish_control.direct_upload.s3.region`, cfg.region || 'us-east-1', 'text', { placeholder: "例如: us-east-1", description: "S3 存储桶所在的数据中心物理区域（如 us-east-1、ap-northeast-1）。" })}
                ${window.renderPlatformAdvancedGroup('高级可选调参 (Endpoint / Public URL / Prefix / ACL / 代理)', `
                    ${renderSettingsItem('自定义端点 (Endpoint URL)', `publish_control.direct_upload.s3.endpoint_url`, cfg.endpoint_url, 'text', { placeholder: "Cloudflare R2, MinIO, or custom endpoint", description: "如果使用 Cloudflare R2 等非标准 AWS 存储，请填写此项。" })}
                    ${renderSettingsItem('公开访问域名 (Public URL)', `publish_control.direct_upload.s3.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://myblog.com", description: "网站公开访问的基地址。" })}
                    ${renderSettingsItem('存储路径前缀 (Prefix)', `publish_control.direct_upload.s3.prefix`, cfg.prefix, 'text', { placeholder: "可选前缀，例如: html-site", description: "文件上传至存储桶时的可选相对子目录路径（留空则部署于根目录）。" })}
                    ${renderSettingsItem('对象访问控制 (ACL)', `publish_control.direct_upload.s3.acl`, cfg.acl, 'text', { placeholder: "例如: public-read", description: "上传对象的云端访问权限（通常设为 public-read）。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.s3.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'github_pages') {
            return `
                <div class="api-token-helper" style="margin-bottom: 16px; padding: 12px; border-radius: 8px; border: 1px dashed var(--neon-cyan); background: rgba(0, 242, 254, 0.05);">
                    <h4 style="margin-top: 0; color: var(--neon-cyan);">💡 GitHub Pages 零配置一键向导 (Zero-Config)</h4>
                    <p style="margin: 4px 0; font-size: 0.85rem; line-height: 1.4; color: var(--text-bright);">
                        <b style="color: var(--neon-green);">✨ 小白极简模式：</b>只需点击下方「🔑 直达 Token 申请魔术链接」（已预先勾选 repo 权限），复制 Token 粘贴到第一项，其他所有配置（仓库名、分支等）全部留空即可！系统将自动识别您的 GitHub 账号并在云端自动建仓部署。
                    </p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <a href="https://github.com/settings/tokens/new?scopes=repo&description=Illacme-Plenipes-Syndication" target="_blank" class="helper-btn" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: #fff; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: bold; display: inline-flex; align-items: center; gap: 4px;">🔑 直达 Token 申请魔术链接 (免选权限)</a>
                        <button type="button" class="helper-btn" style="background: rgba(163, 76, 255, 0.15); border: 1px solid rgba(163, 76, 255, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerGitCredentialsSense(this, 'publish_control.direct_upload.github_pages')">🔑 自动感应本地 Git 凭据</button>
                        <button type="button" class="helper-btn" style="background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.4); color: #fff; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;" onclick="window.triggerGithubSSHCheck(this)">🔍 自动探测本地 SSH 免密</button>
                    </div>
                    <div class="oauth-status-info" style="display: none; margin-top: 8px; font-size: 0.85rem;"></div>
                </div>
                ${renderSettingsItem('访问令牌 (Personal Access Token / Token)', `publish_control.direct_upload.github_pages.token`, cfg.token || cfg.git_token || '', 'password', { placeholder: "例如: ghp_xxxxxxxxxxxx (只需填此项！其他项全可留空)", description: "GitHub 个人访问令牌，点击上方魔术链接可一键生成。使用 SSH 免密部署时可留空。" })}
                ${renderSettingsItem('仓库 URL (Repo URL)', `publish_control.direct_upload.github_pages.repo_url`, cfg.repo_url, 'text', { placeholder: "选填！留空将使用 Token 自动在您的 GitHub 创建公开仓库 (illacme-press)", description: "【选填】留空即可。系统将自动通过 Token 解析您的账户并自动在云端创建公开仓库。" })}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.github_pages.branch`, cfg.branch || 'gh-pages', 'text', { placeholder: "gh-pages (默认)", description: "【选填】默认自动绑定至 gh-pages 孤儿分支。" })}
                ${renderSettingsItem('Git 用户名', `publish_control.direct_upload.github_pages.git_user_name`, cfg.git_user_name || 'Plenipes Bot', 'text', { description: "【选填】Git 提交身份中的用户名，默认自动回填。" })}
                ${renderSettingsItem('Git 邮箱', `publish_control.direct_upload.github_pages.git_user_email`, cfg.git_user_email || 'bot@plenipes.press', 'text', { description: "【选填】Git 提交身份中的邮箱，默认自动回填。" })}
                ${window.renderPlatformAdvancedGroup('高级可选参数 (CNAME / 代理 / 强制推送)', `
                    ${renderSettingsItem('自定义域名 (CNAME)', `publish_control.direct_upload.github_pages.cname`, cfg.cname, 'text', { placeholder: "例如: blog.example.com", description: "可选，若绑定了自定义域名请在此填写。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.github_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
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
                ${renderSettingsItem('Git 用户名', `publish_control.direct_upload.gitee_pages.git_user_name`, cfg.git_user_name || 'Plenipes Bot', 'text', { description: "Git 提交身份中的用户名，可点击「自动感应本地 Git 凭据」自动回填。" })}
                ${renderSettingsItem('Git 邮箱', `publish_control.direct_upload.gitee_pages.git_user_email`, cfg.git_user_email || 'bot@plenipes.press', 'text', { description: "Git 提交身份中的邮箱，可点击「自动感应本地 Git 凭据」自动回填。" })}
                ${renderSettingsItem('仓库 URL (Repo URL)', `publish_control.direct_upload.gitee_pages.repo_url`, cfg.repo_url, 'text', { placeholder: "例如: git@gitee.com:username/repo.git", description: "您的 Gitee 仓库的 SSH 或 HTTPS 地址。" })}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.gitee_pages.branch`, cfg.branch || 'gitee-pages', 'text', { placeholder: "例如: gitee-pages" })}
                ${window.renderPlatformAdvancedGroup('高级可选参数 (代理)', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.gitee_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: direct 或代理地址", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
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
                ${renderSettingsItem('Git 用户名', `publish_control.direct_upload.gitlab_pages.git_user_name`, cfg.git_user_name || 'Plenipes Bot', 'text', { description: "Git 提交身份中的用户名，可点击「自动感应本地 Git 凭据」自动回填。" })}
                ${renderSettingsItem('Git 邮箱', `publish_control.direct_upload.gitlab_pages.git_user_email`, cfg.git_user_email || 'bot@plenipes.press', 'text', { description: "Git 提交身份中的邮箱，可点击「自动感应本地 Git 凭据」自动回填。" })}
                ${renderSettingsItem('仓库 URL (Repo URL)', `publish_control.direct_upload.gitlab_pages.repo_url`, cfg.repo_url, 'text', { placeholder: "例如: git@gitlab.com:username/repo.git", description: "您的 GitLab 仓库的 SSH 或 HTTPS 地址。" })}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.gitlab_pages.branch`, cfg.branch || 'main', 'text', { placeholder: "例如: main" })}
                ${window.renderPlatformAdvancedGroup('高级可选参数 (代理)', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.gitlab_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: direct 或代理地址" })}
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
                ${renderSettingsItem('部署 Token (CLI Token)', `publish_control.direct_upload.firebase.token`, cfg.token, 'password', { placeholder: "Firebase CI Token (使用一键授权或 firebase login:ci 获取)" })}
                ${renderSettingsItem('项目 ID (Project ID)', `publish_control.direct_upload.firebase.project_id`, cfg.project_id, 'text', { placeholder: "例如: my-firebase-project" })}
                ${renderSettingsItem('站点 ID (Site ID)', `publish_control.direct_upload.firebase.site`, cfg.site, 'text', { placeholder: "可选，多站点支持" })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
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
                ${renderSettingsItem('API 访问令牌 (Token)', `publish_control.direct_upload.cloudflare_pages.token`, cfg.token, 'password', { placeholder: "请输入 Cloudflare API Token", description: "具备 Cloudflare Pages 编辑权限的 API Token，点击上方魔术链接可快速创建。" })}
                ${renderSettingsItem('账号 ID (Account ID)', `publish_control.direct_upload.cloudflare_pages.account_id`, cfg.account_id, 'text', { placeholder: "32 位 Cloudflare 账号 ID", description: "登录 Cloudflare 控制台，在任意域名或 Pages 概览右下角复制 32 位 Account ID。" })}
                ${renderSettingsItem('项目名称 (Project Name)', `publish_control.direct_upload.cloudflare_pages.project_name`, cfg.project_name, 'text', { placeholder: "例如: my-docs-site", description: "Cloudflare Pages 中创建的静态项目名称，系统将直接发布至此项目。" })}
                ${renderSettingsItem('部署分支 (Branch)', `publish_control.direct_upload.cloudflare_pages.branch`, cfg.branch || 'production', 'text', { placeholder: "例如: production", description: "绑定自动构建部署的目标分支（默认常用 production 或 main）。" })}
                ${window.renderPlatformAdvancedGroup('高级代理与 CLI 路径参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.cloudflare_pages.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('Wrangler CLI 路径', `publish_control.direct_upload.cloudflare_pages.wrangler_path`, cfg.wrangler_path || 'wrangler', 'text', { description: "本地安装的 Wrangler CLI 命令行工具路径（默认 wrangler）。" })}
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
                ${renderSettingsItem('身份凭证 (Auth Token)', `publish_control.direct_upload.netlify.auth_token`, cfg.auth_token, 'password', { placeholder: "Netlify Personal Access Token", description: "Netlify 个人访问令牌，点击上方向导可一键免密授权或直达创建。" })}
                ${renderSettingsItem('站点 ID (Site ID)', `publish_control.direct_upload.netlify.site_id`, cfg.site_id, 'text', { placeholder: "例如: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", description: "在 Netlify 站点后台 -> Site configuration -> General -> Site details 中复制 API ID。" })}
                ${window.renderPlatformAdvancedGroup('高级部署与代理参数', `
                    ${renderSettingsItem('生产模式部署 (Prod)', `publish_control.direct_upload.netlify.prod`, cfg.prod !== false, 'checkbox', { description: "勾选直接发布至正式生产环境；取消勾选将发布至预览测试草稿环境。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.netlify.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('Netlify CLI 路径', `publish_control.direct_upload.netlify.netlify_path`, cfg.netlify_path || 'netlify', 'text', { description: "本地安装的 Netlify CLI 执行路径（默认 netlify）。" })}
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
                ${renderSettingsItem('访问令牌 (Token)', `publish_control.direct_upload.vercel.token`, cfg.token, 'password', { placeholder: "请输入 Vercel 访问令牌 (Token)", description: "Vercel 访问凭证，点击上方向导可免密授权或直达 Token 申请页创建。" })}
                ${renderSettingsItem('项目名称 (Project Name)', `publish_control.direct_upload.vercel.project_name`, cfg.project_name, 'text', { placeholder: "例如: illacme-press", description: "Vercel 中对应的项目名称（首次发布若不存在将自动在云端初始化）。" })}
                ${renderSettingsItem('组织 ID (Org ID)', `publish_control.direct_upload.vercel.org_id`, cfg.org_id, 'text', { placeholder: "个人项目留空即可 (可选)", description: "【选填】仅在发布至企业或 Team 空间时填写 Team ID，个人账号请留空。" })}
                ${window.renderPlatformAdvancedGroup('高级生产部署与代理参数', `
                    ${renderSettingsItem('生产部署 (Prod)', `publish_control.direct_upload.vercel.prod`, cfg.prod !== false, 'checkbox', { description: "勾选直接发布至正式生产环境；取消勾选将发布至预览测试环境。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.vercel.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                    ${renderSettingsItem('Vercel CLI 路径', `publish_control.direct_upload.vercel.vercel_path`, cfg.vercel_path || 'vercel', 'text', { description: "本地安装的 Vercel CLI 命令行工具路径（默认 vercel）。" })}
                `)}
            `;
        }
        if (typeof window.renderPaasHostingConfig === 'function') {
            const paasHtml = window.renderPaasHostingConfig(id, cfg);
            if (paasHtml) return paasHtml;
        }
    }

    if (category === 'notification') {
        if (window.rawRenderNotificationConfig) {
            return window.rawRenderNotificationConfig(id, cfg);
        }
        return '';
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
