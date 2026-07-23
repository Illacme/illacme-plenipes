/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Platforms Links & Portal Guide Shard
 * 职责：托管与定义 40+ 平台的 Portal 入口魔术链接字典及向导 / 折叠组 HTML 渲染器。
 */

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
