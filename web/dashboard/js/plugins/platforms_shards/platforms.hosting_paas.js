/**
 * ⚙️ [V1.0] Illacme Plenipes Plugins - PaaS & Object Storage Hosting Shard
 * 职责：对象存储与现代 PaaS 托管平台 (OSS, COS, USS, SFTP, Railway, Render, Zeabur) 的配置表单渲染。
 */

(function () {
    'use strict';

    var renderSettingsItem = window.renderSettingsItem || (() => "");

    window.renderPaasHostingConfig = function (id, cfg) {
        if (id === 'aliyun_oss') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 阿里云 AccessKey 获取向导</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://ram.console.aliyun.com/manage/ak" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达阿里云 AccessKey 管理页</a>
                    </div>
                </div>
                ${renderSettingsItem('访问密钥 ID (Access Key ID)', `publish_control.direct_upload.aliyun_oss.access_key_id`, cfg.access_key_id, 'text', { placeholder: "Access Key ID" })}
                ${renderSettingsItem('安全密钥 (Access Key Secret)', `publish_control.direct_upload.aliyun_oss.access_key_secret`, cfg.access_key_secret, 'password', { placeholder: "Access Key Secret" })}
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.aliyun_oss.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-oss-bucket" })}
                ${renderSettingsItem('接入点 (Endpoint)', `publish_control.direct_upload.aliyun_oss.endpoint`, cfg.endpoint, 'text', { placeholder: "例如: oss-cn-hangzhou.aliyuncs.com" })}
                ${window.renderPlatformAdvancedGroup('高级托管前缀与加速参数', `
                    ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.aliyun_oss.prefix`, cfg.prefix, 'text', { placeholder: "例如: site-root (可选)" })}
                    ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.aliyun_oss.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://blog.mydomain.com", description: "如果配置了自定义 CDN 域名，请在此填写。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.aliyun_oss.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
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
                ${renderSettingsItem('密钥 ID (SecretId)', `publish_control.direct_upload.tencent_cos.secret_id`, cfg.secret_id, 'text', { placeholder: "SecretId" })}
                ${renderSettingsItem('安全密钥 (SecretKey)', `publish_control.direct_upload.tencent_cos.secret_key`, cfg.secret_key, 'password', { placeholder: "SecretKey" })}
                ${renderSettingsItem('存储桶名称 (Bucket)', `publish_control.direct_upload.tencent_cos.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-cos-1250000000" })}
                ${renderSettingsItem('存储区域 (Region)', `publish_control.direct_upload.tencent_cos.region`, cfg.region, 'text', { placeholder: "例如: ap-shanghai" })}
                ${window.renderPlatformAdvancedGroup('高级托管前缀与加速参数', `
                    ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.tencent_cos.prefix`, cfg.prefix, 'text', { placeholder: "例如: html-site (可选)" })}
                    ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.tencent_cos.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://blog.mydomain.com", description: "如果配置了自定义 CDN 域名，请在此填写。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.tencent_cos.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'upyun_uss') {
            return `
                ${renderSettingsItem('操作员 (Operator)', `publish_control.direct_upload.upyun_uss.operator`, cfg.operator, 'text', { placeholder: "操作员账号" })}
                ${renderSettingsItem('操作员密码 (Password)', `publish_control.direct_upload.upyun_uss.password`, cfg.password, 'password', { placeholder: "操作员密码" })}
                ${renderSettingsItem('服务名称 (Bucket)', `publish_control.direct_upload.upyun_uss.bucket`, cfg.bucket, 'text', { placeholder: "例如: my-upyun-service" })}
                ${window.renderPlatformAdvancedGroup('高级托管前缀与加速参数', `
                    ${renderSettingsItem('静态托管前缀 (Prefix)', `publish_control.direct_upload.upyun_uss.prefix`, cfg.prefix, 'text', { placeholder: "例如: site (可选)" })}
                    ${renderSettingsItem('绑定加速域名 (Public URL)', `publish_control.direct_upload.upyun_uss.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://site.upaiyun.com", description: "网站公开访问的基地址。" })}
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.upyun_uss.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
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
                ${renderSettingsItem('服务器主机 (Host)', `publish_control.direct_upload.sftp.host`, cfg.host, 'text', { placeholder: "例如: 123.45.67.89 或 sftp.myblog.com", description: "远程服务器的公网 IP 地址或解析域名。" })}
                ${renderSettingsItem('SSH 端口 (Port)', `publish_control.direct_upload.sftp.port`, cfg.port || 22, 'number', { placeholder: "默认 22", description: "远程主机的 SSH/SFTP 服务监听端口（通常为 22）。" })}
                ${renderSettingsItem('登录用户名 (Username)', `publish_control.direct_upload.sftp.username`, cfg.username, 'text', { placeholder: "例如: root 或 deployer", description: "用于登录远程服务器执行静态文件写入的系统账户名。" })}
                ${renderSettingsItem('登录密码 (Password)', `publish_control.direct_upload.sftp.password`, cfg.password, 'password', { placeholder: "SSH 密码，若使用私钥可留空", description: "远程账户的登录密码（密码或下方私钥任选一种即可）。" })}
                ${renderSettingsItem('SSH 私钥 (Private Key)', `publish_control.direct_upload.sftp.private_key`, cfg.private_key, 'textarea', { placeholder: "私钥文件路径或私钥字符串内容", rows: 4, description: "本地 SSH 私钥路径（如 ~/.ssh/id_rsa）或私钥文本内容（与密码二选一）。" })}
                ${renderSettingsItem('私钥口令 (Passphrase)', `publish_control.direct_upload.sftp.passphrase`, cfg.passphrase, 'password', { placeholder: "私钥保护口令（无口令留空）", description: "【选填】若您的 SSH 私钥设置了保护口令（Passphrase），请在此填写。" })}
                ${renderSettingsItem('远程目标目录 (Remote Path)', `publish_control.direct_upload.sftp.remote_path`, cfg.remote_path, 'text', { placeholder: "例如: /var/www/html/blog", description: "静态网页文件上传部署至对端服务器的绝对目标路径（请确保该目录具备写入权限）。" })}
                ${renderSettingsItem('站点访问域名 (Public URL)', `publish_control.direct_upload.sftp.public_url`, cfg.public_url, 'text', { placeholder: "例如: https://blog.mysite.com", description: "网站公开访问的基地址。" })}
                ${window.renderPlatformAdvancedGroup('高级代理调参', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.sftp.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'railway') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 Railway Deploy Hook 与 Token 向导</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://railway.app/dashboard" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 直达 Railway 控制台</a>
                    </div>
                </div>
                ${renderSettingsItem('Git 访问令牌 (Token)', `publish_control.direct_upload.railway.token`, cfg.token, 'password', { placeholder: "Git Token (可选)" })}
                ${renderSettingsItem('触发构建 Hook (Deploy Hook URL)', `publish_control.direct_upload.railway.deploy_hook_url`, cfg.deploy_hook_url, 'text', { placeholder: "例如: https://backboard.railway.app/deploy/...", description: "在 Railway 项目服务设置 -> Deploy Triggers 中创建的 Deploy Hook URL。" })}
                ${renderSettingsItem('关联 Git 仓库 URL', `publish_control.direct_upload.railway.repo_url`, cfg.repo_url, 'text', { placeholder: "例如: git@github.com:username/repo.git (可选)" })}
                ${window.renderPlatformAdvancedGroup('高级代理调参', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.railway.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'render') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 Render API 密钥向导</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://dashboard.render.com/u/settings#api-keys" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Render API 密钥页</a>
                    </div>
                </div>
                ${renderSettingsItem('Render API Key (可选)', `publish_control.direct_upload.render.api_key`, cfg.api_key, 'password', { placeholder: "rnd_xxxxxxxx (可选，用于高级部署状态探测)" })}
                ${renderSettingsItem('触发构建 Hook (Deploy Hook URL)', `publish_control.direct_upload.render.deploy_hook_url`, cfg.deploy_hook_url, 'text', { placeholder: "例如: https://api.render.com/deploy/srv-...", description: "在 Render 静态服务 Settings -> Deploy Hook 中复制的 Hook 地址。" })}
                ${window.renderPlatformAdvancedGroup('高级代理调参', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.render.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'zeabur') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 Zeabur Access Token 向导</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://zeabur.com/account" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 Zeabur 个人账户页</a>
                    </div>
                </div>
                ${renderSettingsItem('Zeabur API Token (可选)', `publish_control.direct_upload.zeabur.token`, cfg.token, 'password', { placeholder: "Zeabur Personal Access Token (可选)" })}
                ${renderSettingsItem('触发构建 Hook (Deploy Hook URL)', `publish_control.direct_upload.zeabur.deploy_hook_url`, cfg.deploy_hook_url, 'text', { placeholder: "例如: https://gateway.zeabur.app/api/v1/deploy/...", description: "在 Zeabur 服务设置 -> Git/Deploy Webhook 中生成的 Hook 地址。" })}
                ${window.renderPlatformAdvancedGroup('高级代理调参', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `publish_control.direct_upload.zeabur.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        }
        return '';
    };

})();
