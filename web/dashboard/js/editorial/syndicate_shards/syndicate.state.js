/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - State & Credential Shard
 * 职责：语种解包、多因子凭据智能判决、平台元数据矩阵与状态模型管理。
 */

(function () {
    // 1. 🌐 语种元数据映射表
    window.syndicateLangMap = {
        'zh': { name: '中文 (ZH)', icon: '🇨🇳' },
        'en': { name: 'English (EN)', icon: '🇬🇧' },
        'ja': { name: '日本語 (JA)', icon: '🇯🇵' },
        'ko': { name: '한국어 (KO)', icon: '🇰🇷' },
        'de': { name: 'Deutsch (DE)', icon: '🇩🇪' },
        'fr': { name: 'Français (FR)', icon: '🇫🇷' },
        'es': { name: 'Español (ES)', icon: '🇪🇸' },
        'ru': { name: 'Русский (RU)', icon: '🇷🇺' },
        'ar': { name: 'العربية (AR)', icon: '🇸🇦' }
    };

    // 2. 🚀 物理分发平台元数据矩阵
    window.platformMetadata = window.platformMetadata || {
        'xiaohongshu': { name: '小红书', icon: '📕', desc: '小红书图文笔记与热门话题' },
        'red': { name: '小红书', icon: '📕', desc: '小红书图文笔记与热门话题' },
        'toutiao': { name: '今日头条', icon: '⚡', desc: '今日头条（头条号）全网算法推荐' },
        'csdn': { name: 'CSDN 博客', icon: '📑', desc: 'CSDN 开发者社区与搜索引擎收录' },
        'cnblogs': { name: '博客园', icon: '🌿', desc: '博客园极客技术社区' },
        'bilibili': { name: 'Bilibili 专栏', icon: '📺', desc: 'B 站专栏长文与硬核科技' },
        'segmentfault': { name: 'SegmentFault 思否', icon: '💡', desc: '思否开发者技术专栏' },
        'oschina': { name: '开源中国', icon: '🇨🇳', desc: '开源中国技术与软件资讯' },
        'devto': { name: 'Dev.to', icon: '👩‍💻', desc: '开发者社区 (支持 Markdown / Canonical URL 注入)' },
        'medium': { name: 'Medium', icon: '📝', desc: '高权重长文平台' },
        'hashnode': { name: 'Hashnode', icon: '🔷', desc: '技术博客平台' },
        'substack': { name: 'Substack', icon: '📮', desc: 'Newsletter 通讯平台' },
        'zhihu': { name: '知乎', icon: '💡', desc: '中文知识社区' },
        'wechat': { name: '微信公众号', icon: '💬', desc: '微信图文矩阵' },
        'ghost': { name: 'Ghost CLI', icon: '👻', desc: '独立 Ghost 站点 API' },
        'wordpress': { name: 'WordPress', icon: '📰', desc: 'WordPress 自动打标发布' },
        'juejin': { name: '掘金', icon: '🧱', desc: '掘金技术社区' },
        'linkedin': { name: 'LinkedIn', icon: '💼', desc: '职场社交平台' },
        'telegram': { name: 'Telegram 频道广播', icon: '✈️', desc: '读者频道与社区群组新文章推送' },
        'discord': { name: 'Discord 社区广播', icon: '💬', desc: '读者社区公告与新文章 Embed 广播' }
    };

    /**
     * 全量多因子凭据智能判决算子
     */
    window.evaluateSyndicateChannelStatus = function (key, itemCfg) {
        const cleanKey = key.toLowerCase().replace('_', '');
        let targetPlugin = null;
        if (window.allPlugins && Array.isArray(window.allPlugins)) {
            targetPlugin = window.allPlugins.find(p => p.id === key || p.id.replace('_', '') === cleanKey);
        }

        // 结合能力矩阵中的全局总开关 is_enabled 与品牌激活状态 is_in_use
        const isPluginEnabled = targetPlugin ? !!targetPlugin.is_enabled : (itemCfg && itemCfg.enabled === true);
        const isBrandActive = targetPlugin ? !!targetPlugin.is_in_use : (itemCfg && (itemCfg.enabled === true || itemCfg.is_in_use === true));

        // 调取多因子凭据智能判决算子
        let credCheck = { ready: false, mode: 'missing', label: '待填凭据' };
        if (typeof window.isPluginCredentialReady === 'function') {
            credCheck = window.isPluginCredentialReady(key, 'publisher', itemCfg);
        } else {
            const hasSecret = Boolean(itemCfg.token || itemCfg.api_key || itemCfg.webhook_url || itemCfg.access_token || itemCfg.bot_token);
            credCheck = { ready: hasSecret, mode: hasSecret ? 'secret' : 'missing', label: hasSecret ? '凭据就绪' : '待填凭据' };
        }

        // 只有【插件启用 + 物理凭据就绪】，渠道才被视为完全就绪可广播
        const isReady = isPluginEnabled && credCheck.ready;

        return {
            isReady,
            isPluginEnabled,
            isBrandActive,
            credReady: credCheck.ready,
            credMode: credCheck.mode,
            credLabel: credCheck.label
        };
    };

    /**
     * 解包受控语种列表
     */
    window.getAvailableSyndicateLangs = function (cfgData) {
        const i18n = cfgData.i18n_settings || {};
        const sourceLangCode = (i18n.source?.lang_code || cfgData.source?.lang_code || 'zh').toLowerCase();
        const rawTargets = i18n.targets || cfgData.translation?.targets || cfgData.i18n_routing?.targets || ['en'];
        const targetLangCodes = Array.isArray(rawTargets)
            ? rawTargets.map(t => (typeof t === 'string' ? t : t.lang_code || t.code || '').toLowerCase()).filter(Boolean)
            : [];

        const allConfiguredCodes = Array.from(new Set([sourceLangCode, ...targetLangCodes]));
        return allConfiguredCodes.map(code => {
            const info = window.syndicateLangMap[code] || { name: code.toUpperCase(), icon: '🌍' };
            return {
                code: code,
                name: info.name,
                icon: info.icon,
                isSource: code === sourceLangCode
            };
        });
    };
})();
