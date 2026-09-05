/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - Multi-language Navigation & AI Translation Shard
 * 职责：当前品牌多语种导航定制弹窗、标准字典匹配与大模型 AI 一键翻译调度。
 */

(function () {
    let activeNavI18nTarget = null;

    window.toggleNavI18nModal = (btn, event) => {
        if (event) event.stopPropagation();

        const row = btn.closest('.route-item');
        if (!row) return;

        activeNavI18nTarget = btn;

        const navLabelInput = row.querySelector('.nav-label-input');
        const sourceInput = row.querySelector('.source-input');
        const slotInput = row.querySelector('.slot-input');
        const hiddenI18nInput = row.querySelector('.nav-i18n-input');

        const defaultLabel = navLabelInput ? navLabelInput.value.trim() : (sourceInput ? sourceInput.value.trim() : '');
        const slot = slotInput ? slotInput.value.trim() : 'docs';

        let currentI18n = {};
        if (hiddenI18nInput && hiddenI18nInput.value) {
            try {
                currentI18n = JSON.parse(hiddenI18nInput.value);
            } catch (e) {
                currentI18n = {};
            }
        }

        // 🎯 严格仅列出当前品牌已配置并启用的目标语言类型 (不罗列无关语种)
        const i18nSettings = window.settingsData?.i18n_settings || window.settingsData?.i18n || {};
        let targetLanguages = [];
        if (Array.isArray(i18nSettings.targets) && i18nSettings.targets.length > 0) {
            targetLanguages = i18nSettings.targets.filter(t => t && t.enabled !== false).map(t => typeof t === 'string' ? t : (t.lang_code || '')).filter(Boolean);
        } else if (Array.isArray(i18nSettings.target_languages) && i18nSettings.target_languages.length > 0) {
            targetLanguages = i18nSettings.target_languages.filter(Boolean);
        }

        // 探测当前品牌母语
        const sourceLang = (i18nSettings.source?.lang_code || 'zh').toLowerCase();

        // 排除与母语相同的项
        targetLanguages = targetLanguages.filter(t => t.toLowerCase() !== sourceLang && t.toLowerCase() !== 'auto');

        // 移除已有弹窗
        const existing = document.getElementById('global-nav-i18n-modal');
        if (existing) existing.remove();

        const rect = btn.getBoundingClientRect();
        const modalLeft = Math.max(20, Math.min(rect.left - 180, window.innerWidth - 390));
        const modalTop = Math.min(rect.bottom + 8, window.innerHeight - 440);

        // 判断是否有标准字典未命中的项（需要推荐 AI 填充）
        let hasMissingDict = false;
        const commonDict = window.COMMON_SLOT_I18N || {};

        // 智能推导字典槽位 key (支持按 slot、中文名、英文名智能索引)
        const cleanLabelLower = (defaultLabel || '').trim().toLowerCase();
        let matchedDictKey = slot;
        if (!commonDict[matchedDictKey]) {
            for (const [k, dict] of Object.entries(commonDict)) {
                if (k.toLowerCase() === cleanLabelLower || dict.zh === defaultLabel || (dict.en && dict.en.toLowerCase() === cleanLabelLower)) {
                    matchedDictKey = k;
                    break;
                }
            }
        } else {
            for (const [k, dict] of Object.entries(commonDict)) {
                if (dict.zh === defaultLabel || (dict.en && dict.en.toLowerCase() === cleanLabelLower)) {
                    matchedDictKey = k;
                    break;
                }
            }
        }

        targetLanguages.forEach(lang => {
            if (!currentI18n[lang] && (!commonDict[matchedDictKey] || !commonDict[matchedDictKey][lang])) {
                hasMissingDict = true;
            }
        });

        let modalHtml = `
            <div id="global-nav-i18n-modal" class="glass-panel" style="position: fixed; top: ${modalTop}px; left: ${modalLeft}px; width: 370px; max-height: 460px; overflow-y: auto; z-index: 99999; background: rgba(15, 17, 30, 0.98); backdrop-filter: blur(20px); border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 12px; box-shadow: 0 16px 48px rgba(0,0,0,0.7); padding: 14px; font-family: inherit;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 1rem;">🌐</span>
                        <span style="font-size: 0.82rem; font-weight: 700; color: var(--accent-secondary, #00f2fe);">当前品牌多语种导航定制</span>
                    </div>
                    <button type="button" onclick="document.getElementById('global-nav-i18n-modal')?.remove();" style="background: none; border: none; color: #888; cursor: pointer; font-size: 0.95rem; padding: 0 4px;">✕</button>
                </div>

                <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; background: rgba(0, 242, 255, 0.05); padding: 6px 10px; border-radius: 6px; border: 1px dashed rgba(0, 242, 255, 0.25);">
                    <span style="font-size: 0.72rem; color: var(--text-dim);">默认母语: <b style="color: #fff;">${defaultLabel || '未设置'}</b></span>
                    <button type="button" id="ai-auto-translate-btn" class="mini-btn ${hasMissingDict ? 'glow-btn' : ''}" onclick="window.autoTranslateNavLabels(event, '${slot}', '${defaultLabel}', '${sourceLang}')" style="font-size: 0.7rem; padding: 4px 9px; background: rgba(0, 242, 255, 0.2); color: #00f2fe; border: 1px solid rgba(0, 242, 255, 0.4); border-radius: 5px; cursor: pointer; font-weight: 700; display: flex; align-items: center; gap: 3px;" title="调用大模型进行多语言翻译并填入各语言文本框">
                        <span class="ai-btn-icon">🤖</span> <span class="ai-btn-text">AI 一键填充</span>
                    </button>
                </div>

                ${targetLanguages.length === 0 ? `
                    <div style="padding: 24px 12px; text-align: center; color: var(--text-dim); font-size: 0.75rem; line-height: 1.5; background: rgba(255,255,255,0.02); border-radius: 8px;">
                        💡 当前品牌尚未启用任何多语言目标语种。<br>如需多语言发布，请在左侧<b>【多语种翻译】</b>中点选开启。
                    </div>
                ` : `
                    <div id="i18n-inputs-container" style="display: flex; flex-direction: column; gap: 8px; max-height: 250px; overflow-y: auto; padding-right: 4px;">
                `}
        `;

        targetLanguages.forEach(lang => {
            const meta = typeof window.getProductLanguageMeta === 'function' ? window.getProductLanguageMeta(lang) : { name: lang.toUpperCase(), flag: '🌐' };
            const val = currentI18n[lang] || "";
            const dictVal = commonDict[matchedDictKey] && commonDict[matchedDictKey][lang];
            const placeholderText = dictVal ? `标准字典: ${dictVal}` : `待翻译 (推荐点击上方 "AI 一键填充")`;

            modalHtml += `
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="width: 105px; font-size: 0.73rem; color: var(--text-dim); display: flex; align-items: center; gap: 5px; flex-shrink: 0;" title="${meta.name} (${lang})">
                        <span style="font-size: 0.9rem;">${meta.flag}</span>
                        <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${meta.name}</span>
                    </span>
                    <input type="text" class="setting-input i18n-lang-input" data-lang="${lang}" value="${val}" placeholder="${placeholderText}" style="flex: 1; font-size: 0.74rem; padding: 5px 8px; ${!dictVal && !val ? 'border-color: rgba(0, 242, 255, 0.25);' : ''}">
                </div>
            `;
        });

        if (targetLanguages.length > 0) {
            modalHtml += `
                    </div>

                    <div style="margin-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; display: flex; justify-content: flex-end; gap: 8px;">
                        <button type="button" onclick="document.querySelectorAll('.i18n-lang-input').forEach(i => i.value='');" style="padding: 4px 10px; font-size: 0.72rem; background: rgba(255,255,255,0.05); color: var(--text-dim); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; cursor: pointer;">清空</button>
                        <button type="button" onclick="window.saveNavI18nLabels();" style="padding: 4px 14px; font-size: 0.74rem; background: var(--accent-primary, #00f2fe); color: #000; border: none; border-radius: 6px; font-weight: 700; cursor: pointer;">确定并应用</button>
                    </div>
            `;
        }

        modalHtml += `
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        setTimeout(() => {
            const closeHandler = (e) => {
                const modal = document.getElementById('global-nav-i18n-modal');
                if (!modal) {
                    document.removeEventListener('click', closeHandler);
                    return;
                }
                // 🛡️ [防误触关闭] 如果目标元素已从 DOM 树分离，或在弹窗内/触发按钮上，不关闭
                if (e.target && !e.target.isConnected) return;
                if (modal.contains(e.target) || (e.target.closest && (e.target.closest('#global-nav-i18n-modal') || e.target.closest('.nav-i18n-btn')))) {
                    return;
                }
                modal.remove();
                activeNavI18nTarget = null;
                document.removeEventListener('click', closeHandler);
            };
            document.addEventListener('click', closeHandler);
        }, 10);
    };

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

        // 1. 优先查阅产品 50 语种完整标准字典，并收集需要大模型 AI 翻译的语种
        const pendingAILangs = [];
        const commonDict = window.COMMON_SLOT_I18N || {};

        // 智能推导字典槽位 key (支持按 slot、中文名、英文名智能索引)
        const cleanLabelLower = (defaultLabel || '').trim().toLowerCase();
        let matchedDictKey = slot;
        if (!commonDict[matchedDictKey]) {
            for (const [k, dict] of Object.entries(commonDict)) {
                if (k.toLowerCase() === cleanLabelLower || dict.zh === defaultLabel || (dict.en && dict.en.toLowerCase() === cleanLabelLower)) {
                    matchedDictKey = k;
                    break;
                }
            }
        }

        inputs.forEach(input => {
            const targetLang = input.getAttribute('data-lang');
            if (!targetLang) return;
            const dictVal = commonDict[matchedDictKey] && commonDict[matchedDictKey][targetLang];
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

    window.saveNavI18nLabels = () => {
        if (!activeNavI18nTarget) return;

        const row = activeNavI18nTarget.closest('.route-item');
        if (!row) return;

        const inputs = document.querySelectorAll('#i18n-inputs-container .i18n-lang-input');
        const newI18n = {};
        let customCount = 0;

        inputs.forEach(input => {
            const lang = input.getAttribute('data-lang');
            const val = input.value.trim();
            if (lang && val) {
                newI18n[lang] = val;
                customCount++;
            }
        });

        const hiddenI18nInput = row.querySelector('.nav-i18n-input');
        if (hiddenI18nInput) {
            hiddenI18nInput.value = JSON.stringify(newI18n);
        }

        // 更新按钮徽章与高亮
        const badge = activeNavI18nTarget.querySelector('.i18n-count-badge');
        if (badge) {
            badge.textContent = customCount > 0 ? customCount : '+';
        }
        if (customCount > 0) {
            activeNavI18nTarget.style.background = 'rgba(0, 255, 136, 0.15)';
            activeNavI18nTarget.style.borderColor = 'rgba(0, 255, 136, 0.4)';
            activeNavI18nTarget.style.color = 'var(--neon-green, #00ff88)';
            activeNavI18nTarget.title = `已定制 ${customCount} 种语言导航名称`;
        } else {
            activeNavI18nTarget.style.background = 'rgba(255, 255, 255, 0.05)';
            activeNavI18nTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            activeNavI18nTarget.style.color = 'var(--text-dim)';
            activeNavI18nTarget.title = '配置多语种导航名称';
        }

        const modal = document.getElementById('global-nav-i18n-modal');
        if (modal) modal.remove();
        activeNavI18nTarget = null;

        if (typeof window.syncRouteMatrixToSettings === 'function') {
            window.syncRouteMatrixToSettings();
        }
    };
})();
