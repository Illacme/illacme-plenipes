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
    'xiaohongshu': { name: '小红书', home: 'https://creator.xiaohongshu.com', token: 'https://creator.xiaohongshu.com' },
    'red': { name: '小红书', home: 'https://creator.xiaohongshu.com', token: 'https://creator.xiaohongshu.com' },
    'toutiao': { name: '今日头条', home: 'https://mp.toutiao.com', token: 'https://mp.toutiao.com/profile_v4/graphic/publish' },
    'csdn': { name: 'CSDN 博客', home: 'https://blog.csdn.net', token: 'https://mp.csdn.net' },
    'cnblogs': { name: '博客园', home: 'https://www.cnblogs.com', token: 'https://i.cnblogs.com/settings' },
    'bilibili': { name: 'Bilibili 专栏', home: 'https://member.bilibili.com/platform/article-up', token: 'https://member.bilibili.com/platform/article-up' },
    'segmentfault': { name: 'SegmentFault 思否', home: 'https://segmentfault.com', token: 'https://segmentfault.com/user/settings' },
    'oschina': { name: '开源中国', home: 'https://www.oschina.net', token: 'https://www.oschina.net/openapi' },
    'devto': { name: 'Dev.to', home: 'https://dev.to', token: 'https://dev.to/settings/extensions' },
    'dev_to': { name: 'Dev.to', home: 'https://dev.to', token: 'https://dev.to/settings/extensions' },
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

    // 消息通知与告警 (Notifications & Webhooks)
    'feishu': { name: '飞书开放平台', home: 'https://open.feishu.cn', token: 'https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot' },
    'dingtalk': { name: '钉钉开放平台', home: 'https://open.dingtalk.com', token: 'https://open.dingtalk.com/document/robots/custom-robot-access' },
    'wecom': { name: '企业微信', home: 'https://work.weixin.qq.com', token: 'https://work.weixin.qq.com/api/doc/90000/90136/91770' },
    'email': { name: 'SMTP 邮件服务', home: 'https://support.google.com/mail/answer/7126229', token: 'https://myaccount.google.com/apppasswords' },
    'sms': { name: '短信服务网关', home: 'https://www.aliyun.com/product/sms', token: 'https://dysms.console.aliyun.com' },
    'app_push': { name: 'APP Push 通知', home: 'https://pusher.com', token: 'https://dashboard.pusher.com' },
    'generic_webhook': { name: '通用 Webhook', home: 'https://webhook.site', token: 'https://webhook.site' },
    'webhook_dispatch': { name: 'Webhook 调度中心', home: 'https://webhook.site', token: 'https://webhook.site' },

    // 图床与存储补充 (Storage Addons)
    'lsky_pro': { name: 'Lsky Pro 兰空图床', home: 'https://www.lsky.pro', token: 'https://docs.lsky.pro' },
    'superbed': { name: '聚合图床 Superbed', home: 'https://www.superbed.cn', token: 'https://www.superbed.cn' },
    'sftp': { name: 'SFTP 存储服务器', home: 'https://www.openssh.com', token: 'https://www.openssh.com' },

    // 大语言模型 AI 协议 (AI Providers & Protocols)
    'openai': { name: 'OpenAI', home: 'https://openai.com', token: 'https://platform.openai.com/api-keys' },
    'anthropic': { name: 'Anthropic Claude', home: 'https://www.anthropic.com', token: 'https://console.anthropic.com/settings/keys' },
    'claude': { name: 'Anthropic Claude', home: 'https://www.anthropic.com', token: 'https://console.anthropic.com/settings/keys' },
    'gemini': { name: 'Google Gemini', home: 'https://ai.google.dev', token: 'https://aistudio.google.com/app/apikey' },
    'deepseek': { name: 'DeepSeek', home: 'https://www.deepseek.com', token: 'https://platform.deepseek.com/api_keys' },
    'ollama': { name: 'Ollama 本地大模型', home: 'https://ollama.com', token: 'https://ollama.com' },
    'lmstudio': { name: 'LM Studio 官网', home: 'https://lmstudio.ai', token: 'https://lmstudio.ai' },
    'lmstudio_v1': { name: 'LM Studio 官网', home: 'https://lmstudio.ai', token: 'https://lmstudio.ai' },
    'localai': { name: 'LocalAI 官网', home: 'https://localai.io', token: 'https://localai.io' },
    'volcengine': { name: '火山引擎 (豆包)', home: 'https://www.volcengine.com/product/doubao', token: 'https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey' },
    'minimax': { name: 'MiniMax 开放平台', home: 'https://www.minimaxi.com', token: 'https://platform.minimaxi.com/user-center/basic-information/interface-key' },
    'qwen': { name: '通义千问 (Qwen)', home: 'https://tongyi.aliyun.com', token: 'https://dashscope.console.aliyun.com/apiKey' },
    'dashscope': { name: '阿里云百炼 (通义千问)', home: 'https://bailian.console.aliyun.com', token: 'https://dashscope.console.aliyun.com/apiKey' },
    'zhipu': { name: '智谱 GLM', home: 'https://open.bigmodel.cn', token: 'https://open.bigmodel.cn/usercenter/apikeys' },
    'moonshot': { name: 'Moonshot AI (Kimi)', home: 'https://www.moonshot.cn', token: 'https://platform.moonshot.cn/console/api-keys' },
    'kimi': { name: 'Moonshot AI (Kimi)', home: 'https://www.moonshot.cn', token: 'https://platform.moonshot.cn/console/api-keys' },
    'mistral': { name: 'Mistral AI', home: 'https://mistral.ai', token: 'https://console.mistral.ai/api-keys/' },
    'groq': { name: 'Groq Cloud', home: 'https://groq.com', token: 'https://console.groq.com/keys' },
    'together': { name: 'Together AI', home: 'https://www.together.ai', token: 'https://api.together.ai/settings/api-keys' },
    'siliconflow': { name: '硅基流动 (SiliconFlow)', home: 'https://www.siliconflow.cn', token: 'https://cloud.siliconflow.cn/account/ak' },
    'openrouter': { name: 'OpenRouter', home: 'https://openrouter.ai', token: 'https://openrouter.ai/keys' },
    'baichuan': { name: '百川智能', home: 'https://www.baichuan-ai.com', token: 'https://platform.baichuan-ai.com/console/apikey' },
    'spark': { name: '讯飞星火', home: 'https://xinghuo.xfyun.cn', token: 'https://console.xfyun.cn/services/cbm' },
    'hunyuan': { name: '腾讯混元', home: 'https://hunyuan.tencent.com', token: 'https://console.cloud.tencent.com/hunyuan/api-key' },
    'qianfan': { name: '百度千帆 (Ernie)', home: 'https://cloud.baidu.com/product/wenxinworkspace', token: 'https://console.bce.baidu.com/qianfan/ais/console/onlineTest' },
    'cohere': { name: 'Cohere', home: 'https://cohere.com', token: 'https://dashboard.cohere.com/api-keys' },

    // 静态生成器引擎与装帧主题 (SSG Engines & Themes)
    'default': { name: 'Default 默认母本', home: 'https://github.com/eason-space/illacme-plenipes', token: '' },
    'docusaurus': { name: 'Docusaurus', home: 'https://docusaurus.io', token: 'https://docusaurus.io/docs' },
    'starlight': { name: 'Starlight', home: 'https://starlight.astro.build', token: 'https://starlight.astro.build/getting-started/' },
    'vitepress': { name: 'VitePress', home: 'https://vitepress.dev', token: 'https://vitepress.dev/guide/what-is-vitepress' },
    'nextra': { name: 'Nextra', home: 'https://nextra.site', token: 'https://nextra.site/docs' },
    'universal': { name: 'Universal Markdown', home: 'https://www.markdownguide.org', token: 'https://www.markdownguide.org' },
    'sovereign': { name: 'Sovereign', home: 'https://github.com/eason-space/illacme-plenipes', token: '' },
    'hugo': { name: 'Hugo 引擎', home: 'https://gohugo.io', token: 'https://gohugo.io/documentation/' },
    'hexo': { name: 'Hexo 引擎', home: 'https://hexo.io', token: 'https://hexo.io/docs/' },
    'astro': { name: 'Astro 引擎', home: 'https://astro.build', token: 'https://docs.astro.build' },
    'nextjs': { name: 'Next.js 引擎', home: 'https://nextjs.org', token: 'https://nextjs.org/docs' },
    'vuepress': { name: 'VuePress 引擎', home: 'https://vuepress.vuejs.org', token: 'https://vuepress.vuejs.org' },

    // 安全与文稿加工 (Security & Processing)
    'exif_scrubber': { name: 'EXIF 地理脱敏', home: 'https://exiftool.org', token: '' },
    'sensitive_filter': { name: '敏感词屏障', home: 'https://github.com/eason-space/illacme-plenipes', token: '' },
    'ast_processor': { name: 'AST 语法加工', home: 'https://github.com/Python-Markdown/markdown', token: '' },
    'markdown_normalizer': { name: 'Markdown 归一化', home: 'https://commonmark.org', token: '' }
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
    if (!content || !content.trim()) return '';
    // 🚀 [V105.1] 如果高级参数内容区不包含任何 input/select/textarea 输入配置项，直接删除/不渲染该区，节省上下空间
    if (!/<(input|select|textarea)\b/i.test(content)) return '';
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
