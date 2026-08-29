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

    // 2. 🚀 动态分发平台元数据解析算子 (不再硬编码静态列表，彻底源自已注册插件矩阵)
    window.getSyndicatePlatformMeta = function (pluginId) {
        if (!pluginId) return { name: '未知渠道', icon: '📡', desc: '' };
        const cleanId = pluginId.toLowerCase().replace(/[_-\s]/g, '');
        const p = (window.allPlugins || []).find(x => x.id === pluginId || x.id.replace(/[_-\s]/g, '') === cleanId);
        if (p) {
            return {
                name: p.name || pluginId,
                icon: p.icon || '📡',
                desc: p.desc || ''
            };
        }
        return { name: pluginId.toUpperCase(), icon: '📡', desc: '' };
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
