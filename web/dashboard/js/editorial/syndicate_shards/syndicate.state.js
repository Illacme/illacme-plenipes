/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - State & Credential Shard
 * 职责：语种解包、多因子凭据智能判决、平台元数据矩阵与状态模型管理。
 */

(function () {
    /**
     * 🌐 全局语种元数据统一定义与解析算子 (SSOT: /api/system/languages -> window.availableLangs)
     * 严禁随处硬编码语种字典，全域所有语种代码、本土名称与国旗图标 100% 统一溯源自系统语种智库。
     */
    window.getLanguageMeta = function (langCode) {
        if (!langCode) return { code: 'unknown', name: '未知语种', icon: '🌐' };
        const rawCode = String(langCode).trim().toLowerCase();
        const baseCode = rawCode.split(/[-_]/)[0];

        // 1. 优先从全局拉取完毕的权威语种矩阵 window.availableLangs 中精准匹配
        const langs = window.availableLangs;
        if (Array.isArray(langs) && langs.length > 0) {
            const matched = langs.find(l => {
                const c = (l.code || '').toLowerCase();
                return c === rawCode || c === baseCode;
            });
            if (matched) {
                return {
                    code: matched.code,
                    name: matched.name,
                    icon: matched.icon || '🌐'
                };
            }
        } else {
            // 2. 竞态兜底：若全域语种尚未拉取，触发异步静默预载
            const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
            fetchApi('/api/system/languages').then(res => {
                if (res && res.languages) {
                    window.availableLangs = res.languages;
                    if (typeof window.updateSyndicatePlatformCards === 'function' && window.currentSyndicatingRelPath) {
                        window.updateSyndicatePlatformCards(window.currentSyndicatingRelPath);
                    }
                }
            }).catch(() => {});
        }

        // 3. 全局基座兜底（与 core/utils/language_data.py SUPPORTED_MATRIX 100% 对齐）
        const FALLBACK_LANGS = {
            'zh': { name: '简体中文', icon: '🇨🇳' },
            'en': { name: 'English', icon: '🇬🇧' },
            'ja': { name: '日本語', icon: '🇯🇵' },
            'ko': { name: '한국어', icon: '🇰🇷' },
            'de': { name: 'Deutsch', icon: '🇩🇪' },
            'fr': { name: 'Français', icon: '🇫🇷' },
            'es': { name: 'Español', icon: '🇪🇸' },
            'ru': { name: 'Русский', icon: '🇷🇺' },
            'ar': { name: 'العربية', icon: '🇸🇦' },
            'pt': { name: 'Português', icon: '🇵🇹' },
            'it': { name: 'Italiano', icon: '🇮🇹' },
            'nl': { name: 'Nederlands', icon: '🇳🇱' },
            'tr': { name: 'Türkçe', icon: '🇹🇷' },
            'vi': { name: 'Tiếng Việt', icon: '🇻🇳' },
            'th': { name: 'ไทย', icon: '🇹🇭' },
            'id': { name: 'Bahasa Indonesia', icon: '🇮🇩' },
            'hi': { name: 'हिन्दी', icon: '🇮🇳' },
            'az': { name: 'Azərbaycanca', icon: '🇦🇿' },
            'pl': { name: 'Polski', icon: '🇵🇱' },
            'sv': { name: 'Svenska', icon: '🇸🇪' }
        };

        const fb = FALLBACK_LANGS[rawCode] || FALLBACK_LANGS[baseCode];
        if (fb) {
            return { code: rawCode, name: fb.name, icon: fb.icon };
        }

        return { code: rawCode, name: rawCode.toUpperCase(), icon: '🌐' };
    };

    // 🌐 动态代理向前兼容旧代码读取 window.syndicateLangMap[code]
    window.syndicateLangMap = new Proxy({}, {
        get: function (target, prop) {
            if (typeof prop !== 'string' || prop === 'then') return undefined;
            return window.getLanguageMeta(prop);
        },
        has: function () {
            return true;
        }
    });

    /**
     * 🛰️ 统一从插件中心 (Plugin Registry / window.allPlugins) 动态检索渠道元数据 (SSOT)
     * 严禁在业务端随处定义私有映射关系，所有 ID、显示名、图标均唯一溯源自插件矩阵。
     */
    window.getSyndicateChannelMeta = window.getSyndicatePlatformMeta = function (pluginId) {
        if (!pluginId) return { name: '未知渠道', icon: '📡', desc: '' };
        const rawId = String(pluginId).trim().toLowerCase();
        const cleanId = rawId.replace(/[_-\s]/g, '');

        // 1. 优先在当前已感应平台 currentActivePlatforms 匹配
        const active = (window.currentActivePlatforms || []).find(x => {
            const xId = (x.id || '').toLowerCase();
            return xId === rawId || xId.replace(/[_-\s]/g, '') === cleanId;
        });
        if (active) {
            return {
                name: active.name || active.id,
                icon: active.icon || (typeof window.getPlatformBrandBadge === 'function' ? window.getPlatformBrandBadge(active.id, 'publisher').icon : '📡'),
                desc: active.desc || ''
            };
        }

        // 2. 其次在全域已注册插件矩阵 allPlugins 中匹配
        const p = (window.allPlugins || []).find(x => {
            const xId = (x.id || '').toLowerCase();
            return xId === rawId || xId.replace(/[_-\s]/g, '') === cleanId;
        });
        if (p) {
            const brand = (typeof window.getPlatformBrandBadge === 'function') ? window.getPlatformBrandBadge(p.id, p.category || 'publisher') : { icon: '📡' };
            return {
                name: p.name || p.id,
                icon: p.icon || brand.icon || '📡',
                desc: p.description || p.desc || ''
            };
        }

        // 3. 若全域插件矩阵尚未拉取，触发异步静默预热，同时通过插件中心视觉算子解析图标
        if (!window.allPlugins || window.allPlugins.length === 0) {
            const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
            fetchApi('/api/plugins/list').then(res => {
                if (res && res.plugins) {
                    window.allPlugins = res.plugins;
                    if (typeof window.updateSyndicatePlatformCards === 'function' && window.currentSyndicatingRelPath) {
                        window.updateSyndicatePlatformCards(window.currentSyndicatingRelPath);
                    }
                }
            }).catch(() => {});
        }

        // 4. 从插件中心全局视觉算子规范提取图标
        const brand = (typeof window.getPlatformBrandBadge === 'function')
            ? window.getPlatformBrandBadge(rawId, 'publisher')
            : { icon: '📡' };

        const fallbackName = pluginId.replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        return { name: fallbackName, icon: brand.icon || '📡', desc: '' };
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
            const hasSecret = Boolean(itemCfg.token || itemCfg.api_token || itemCfg.api_key || itemCfg.cookie || itemCfg.sessdata || itemCfg.webhook_url || itemCfg.access_token || itemCfg.bot_token);
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
            const info = (typeof window.getLanguageMeta === 'function') 
                ? window.getLanguageMeta(code) 
                : (window.syndicateLangMap[code] || { name: code.toUpperCase(), icon: '🌍' });
            return {
                code: code,
                name: info.name,
                icon: info.icon,
                isSource: code === sourceLangCode
            };
        });
    };
})();
