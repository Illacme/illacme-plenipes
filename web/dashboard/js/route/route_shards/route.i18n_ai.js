/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - AI Navigation Translation Shard
 * 职责：频道路由矩阵多语言导航名称 AI 大模型翻译调度、标准字典秒级回填与容错降级。
 */

(function () {
    'use strict';

    window.autoTranslateNavLabels = async (eventOrSlot, slotOrDefaultLabel, defaultLabelOrSourceLang, sourceLang) => {
        let slot = 'docs';
        let defaultLabel = '';
        let lang = 'zh';

        if (eventOrSlot && eventOrSlot.preventDefault) {
            if (eventOrSlot.stopPropagation) eventOrSlot.stopPropagation();
            slot = slotOrDefaultLabel;
            defaultLabel = defaultLabelOrSourceLang;
            lang = sourceLang || 'zh';
        } else {
            slot = eventOrSlot;
            defaultLabel = slotOrDefaultLabel;
            lang = defaultLabelOrSourceLang || 'zh';
        }

        const btn = document.getElementById('ai-auto-translate-btn');
        const inputs = document.querySelectorAll('#i18n-inputs-container .i18n-lang-input');
        if (!inputs || inputs.length === 0) return;

        const targetLangs = Array.from(inputs).map(i => i.getAttribute('data-lang')).filter(Boolean);

        // 1. 智能推导标准字典槽位 key (仅当 defaultLabel 确实精准命中官方标准词汇时才秒级预填)
        const pendingAILangs = [];
        const commonDict = window.COMMON_SLOT_I18N || {};

        const cleanLabelLower = (defaultLabel || '').trim().toLowerCase();
        let matchedDictKey = null;
        for (const [k, dict] of Object.entries(commonDict)) {
            if (dict.zh === defaultLabel || (dict.en && dict.en.toLowerCase() === cleanLabelLower) || k.toLowerCase() === cleanLabelLower) {
                matchedDictKey = k;
                break;
            }
        }

        inputs.forEach(input => {
            const targetLang = input.getAttribute('data-lang');
            if (!targetLang) return;
            const dictVal = matchedDictKey && commonDict[matchedDictKey] && commonDict[matchedDictKey][targetLang];
            if (dictVal) {
                input.value = dictVal;
            } else {
                pendingAILangs.push(targetLang);
            }
        });

        // 2. 如果存在非标准词汇或需要 AI 精准翻译的语种，调用大模型接口
        if (pendingAILangs.length > 0 && defaultLabel) {
            if (btn) {
                btn.disabled = true;
                const iconSpan = btn.querySelector('.ai-btn-icon');
                const textSpan = btn.querySelector('.ai-btn-text');
                if (iconSpan) iconSpan.textContent = '⏳';
                if (textSpan) textSpan.textContent = 'AI 翻译中...';
            }

            try {
                let resData = null;
                const fetchFunc = window.apiFetch || (async (url, init) => {
                    const r = await fetch(url, init);
                    return r.json();
                });

                resData = await fetchFunc('/api/governance/translate-nav-labels', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        label: defaultLabel,
                        target_languages: pendingAILangs,
                        slot: slot,
                        source_language: lang || 'zh'
                    })
                });

                if (resData && resData.translations) {
                    const translations = resData.translations;
                    inputs.forEach(input => {
                        const l = input.getAttribute('data-lang');
                        if (l && translations[l]) {
                            input.value = translations[l];
                        }
                    });
                } else {
                    // 降级回退到标准字典
                    inputs.forEach(input => {
                        const l = input.getAttribute('data-lang');
                        if (l && !input.value) {
                            const fallback = (commonDict[matchedDictKey] && commonDict[matchedDictKey][l]) || defaultLabel;
                            input.value = fallback;
                        }
                    });
                }
            } catch (e) {
                console.warn('AI translation API failed, applying local fallback:', e);
                inputs.forEach(input => {
                    const l = input.getAttribute('data-lang');
                    if (l && !input.value) {
                        const fallback = (commonDict[matchedDictKey] && commonDict[matchedDictKey][l]) || defaultLabel;
                        input.value = fallback;
                    }
                });
            } finally {
                if (btn) {
                    btn.disabled = false;
                    const iconSpan = btn.querySelector('.ai-btn-icon');
                    const textSpan = btn.querySelector('.ai-btn-text');
                    if (iconSpan) iconSpan.textContent = '🤖';
                    if (textSpan) textSpan.textContent = 'AI 一键填充';
                }
            }
        }
    };

})();
