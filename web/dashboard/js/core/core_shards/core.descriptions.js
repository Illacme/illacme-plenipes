/**
 * 🛰️ [V55.9] Illacme Plenipes Dashboard Core - Smart Descriptions Shard
 * 职责：智能推断表单配置项的人性化白话说明，彻底替代生硬晦涩的技术黑话。
 */

window.resolveSmartDescription = (label, path) => {
    const p = (path || '').toLowerCase();
    const l = (label || '').toLowerCase();

    // 1. 密钥 / 令牌 / 密码 / 凭证
    if (p.includes('api_key') || p.includes('access_key_id') || p.includes('access_key') || l.includes('api key') || l.includes('access key') || l.includes('密钥 id') || l.includes('公钥')) {
        return '用于调用对端服务 API 的身份鉴权账号或公钥凭据。';
    }
    if (p.includes('secret_key') || p.includes('access_key_secret') || p.includes('app_secret') || l.includes('secret key') || l.includes('私钥') || l.includes('appsecret')) {
        return '用于请求安全签名计算与身份鉴权的安全私钥凭证。';
    }
    if (p.includes('token') || l.includes('token') || l.includes('令牌')) {
        return '用于连接对端服务进行自动化调用的身份访问令牌（Token）。';
    }
    if (p.includes('password') || l.includes('password') || l.includes('密码') || l.includes('授权码')) {
        return '用于登录远程主机或服务的密码或客户端专用授权凭据。';
    }
    if (p.includes('cookie') || l.includes('cookie')) {
        return '网页端登录会话 Cookie 凭据，用于维持创作者后台授权状态。';
    }

    // 2. 仓库 / 分支
    if (p.includes('repo_url') || p.includes('repo') || l.includes('repo') || l.includes('仓库')) {
        return '部署静态站点或同步代码的 Git 目标仓库地址（支持 HTTPS 或 SSH 格式）。';
    }
    if (p.includes('branch') || l.includes('branch') || l.includes('分支')) {
        return '静态网页产物发布推送的目标代码分支（通常为 main、gh-pages 或 production）。';
    }

    // 3. 项目 / 站点 / 组织
    if (p.includes('project_id') || p.includes('project_name') || p.includes('project') || l.includes('project') || l.includes('项目')) {
        return '目标托管平台中用于部署站点的项目名称或唯一识别 ID。';
    }
    if (p.includes('site_id') || p.includes('site') || l.includes('site id') || l.includes('站点 id')) {
        return '目标托管平台中用于标识当前站点的唯一 ID。';
    }
    if (p.includes('account_id') || p.includes('org_id') || l.includes('account id') || l.includes('账号 id') || l.includes('组织')) {
        return '对应云服务商的主体账号 ID 或团队组织 ID。';
    }
    if (p.includes('app_id') || l.includes('appid') || l.includes('app id')) {
        return '开放平台中注册的应用唯一识别 ID（AppID）。';
    }
    if (p.includes('column_id') || l.includes('专栏')) {
        return '目标平台中用于归集文章的专栏唯一识别 ID。';
    }

    // 4. 云存储桶 / 存储区域 / 前缀 / 权限
    if (p.includes('bucket') || l.includes('bucket') || l.includes('存储桶')) {
        return '云存储中用于托管静态网页与资源的存储桶（Bucket）名称。';
    }
    if (p.includes('region') || l.includes('region') || l.includes('存储区域') || l.includes('区域')) {
        return '云服务所在的数据中心物理区域代号（例如 us-east-1、ap-east-1）。';
    }
    if (p.includes('prefix') || l.includes('prefix') || l.includes('路径前缀') || l.includes('前缀')) {
        return '静态站点在存储桶或网址中的二级子目录前缀（无前缀请留空）。';
    }
    if (p.includes('acl') || l.includes('acl') || l.includes('访问权限')) {
        return '云存储文件上传的公开访问控制权限策略（例如 public-read）。';
    }

    // 5. 端口 / 主机 / 用户名
    if (p.includes('port') || l.includes('port') || l.includes('端口')) {
        return '目标网络服务的连接监听端口（例如 SFTP 默认端口为 22）。';
    }
    if (p.includes('host') || l.includes('host') || l.includes('主机') || l.includes('服务器地址')) {
        return '远程目标服务器的 IP 地址或完整主机域名。';
    }
    if (p.includes('username') || p.includes('user') || l.includes('username') || l.includes('用户名')) {
        return '用于远程登录对端服务器的系统账号名称。';
    }

    // 6. 域名 / URL / 端点 / 代理 / 路径
    if (p.includes('wrangler_path') || p.includes('vercel_path') || p.includes('netlify_path') || l.includes('cli 路径')) {
        return '本地安装的 CLI 命令行工具可执行路径（通常留空或使用系统默认）。';
    }
    if (p.includes('endpoint') || l.includes('endpoint') || l.includes('端点') || l.includes('接入点')) {
        return '自建服务或兼容第三方 S3/API 的自定义服务接口端点 URL。';
    }
    if (p.includes('cname') || p.includes('public_url') || p.includes('site_url') || l.includes('cname') || l.includes('域名') || l.includes('访问地址') || l.includes('url')) {
        return '站点或服务对外公开访问的自定义域名或基准 URL。';
    }
    if (p.includes('proxy') || l.includes('proxy') || l.includes('代理')) {
        return '连接对端平台时的本地网络代理（如无需代理可填 direct 或留空）。';
    }

    // 7. 通用白话兜底
    return `设置当前服务所需的 ${label} 参数。`;
};
