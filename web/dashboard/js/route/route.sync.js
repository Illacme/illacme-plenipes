/**
 * 🛣️ [V75.0 / V100.9] Advanced Channel Routing & Universal Navigation - Sync & Action Module
 * 职责：处理频道与全景导航矩阵的前端交互表单数据同步与事件绑定。
 */

// 常用图标库分类定义
const EMOJI_PALETTE = {
    "📚 文档与知识": ["📚", "📖", "📄", "📝", "📰", "📁", "📑", "📋", "🧠", "💡", "🔖", "✍️"],
    "🌐 网络与导航": ["🌐", "🐙", "🔗", "🚀", "🧭", "🏠", "📡", "💻", "⚡", "🎯", "🗺️", "🔌"],
    "🎨 视觉与分类": ["🎨", "🎭", "☕", "💼", "🔬", "⭐", "📦", "🏷️", "🔍", "💬", "📊", "🛡️"],
    "⚙️ 系统与工具": ["⚙️", "🛠️", "💎", "🔥", "✨", "📌", "🎉", "❤️", "🟢", "🔑", "🔔", "🚩"]
};

// 🌍 [V100.9] 全量 50 语种导航标准字典 (100% 覆盖产品所有受控语种)
const COMMON_SLOT_I18N = {
    "docs": {
        "zh": "文档中心", "zh-hans": "文档中心", "zh-hant": "文檔中心", "en": "Documentation",
        "hi": "दस्तावेज़", "es": "Documentación", "fr": "Documentation", "ar": "التوثيق",
        "bn": "নথিপত্র", "pt": "Documentação", "ru": "Документация", "ur": "دستاویزات",
        "id": "Dokumentasi", "de": "Dokumentation", "ja": "ドキュメント", "mr": "दस्तऐवजीकरण",
        "te": "డాక్యుమెంటేషన్", "tr": "Belgeler", "ta": "ஆவணங்கள்", "vi": "Tài liệu",
        "tl": "Dokumentasyon", "ko": "문서 센터", "fa": "مستندات", "ha": "Takardu",
        "sw": "Nyaraka", "jv": "Dokumentasi", "it": "Documentazione", "pa": "ਦਸਤਾਵੇਜ਼",
        "kn": "ದಾಖಲೆಗಳು", "gu": "દસ્તાવેજીકરણ", "th": "เอกสาร", "am": "ሰነዶች",
        "yo": "Àwọn àkọsílẹ̀", "my": "စာရွက်စာတမ်းများ", "om": "Sanadoota", "ps": "اسناد",
        "uk": "Документація", "su": "Dokuméntasi", "pl": "Dokumentacja", "uz": "Hujjatlar",
        "ro": "Documentație", "az": "Sənədlər", "ml": "രേഖകൾ", "sd": "دستاويز",
        "ig": "Akwụkwọ", "hu": "Dokumentáció", "el": "Τεκμηρίωση", "cs": "Dokumentace",
        "nl": "Documentatie", "sv": "Dokumentation", "fi": "Dokumentaatio", "no": "Dokumentasjon"
    },
    "blog": {
        "zh": "官方博客", "zh-hans": "官方博客", "zh-hant": "官方博客", "en": "Blog",
        "hi": "ब्लॉग", "es": "Blog", "fr": "Blog", "ar": "المدونة",
        "bn": "ব্লগ", "pt": "Blog", "ru": "Блог", "ur": "بلاگ",
        "id": "Blog", "de": "Blog", "ja": "ブログ", "mr": "ब्लॉग",
        "te": "బ్లాగ్", "tr": "Blog", "ta": "வலைப்பதிவு", "vi": "Blog",
        "tl": "Blog", "ko": "블로그", "fa": "وبلاگ", "ha": "Blog",
        "sw": "Blogu", "jv": "Blog", "it": "Blog", "pa": "ਬਲੌਗ",
        "kn": "ಬ್ಲಾಗ್", "gu": "બ્લોગ", "th": "บล็อก", "am": "ብሎግ",
        "yo": "Búlọ́ọ̀gì", "my": "ဘလော့ဂ်", "om": "Biloogii", "ps": "بلاګ",
        "uk": "Блог", "su": "Blog", "pl": "Blog", "uz": "Blog",
        "ro": "Blog", "az": "Bloq", "ml": "ബ്ലോഗ്", "sd": "بلاگ",
        "ig": "Blọọgụ", "hu": "Blog", "el": "Ιστολόγιο", "cs": "Blog",
        "nl": "Blog", "sv": "Blogg", "fi": "Blogi", "no": "Blogg"
    },
    "pages": {
        "zh": "展示页面", "zh-hans": "展示页面", "zh-hant": "展示頁面", "en": "Showcase",
        "hi": "प्रदर्शनी", "es": "Exhibición", "fr": "Vitrines", "ar": "المعرض",
        "bn": "শোকেস", "pt": "Vitrine", "ru": "Витрина", "ur": "شوکیس",
        "id": "Showcase", "de": "Seiten", "ja": "ショーケース", "mr": "प्रदर्शन",
        "te": "ప్రదర్శన", "tr": "Vitrin", "ta": "காட்சி", "vi": "Trưng bày",
        "tl": "Showcase", "ko": "쇼케이스", "fa": "ویترین", "ha": "Nunin",
        "sw": "Maonyesho", "jv": "Pameran", "it": "Vetrina", "pa": "ਸ਼ੋਕੇਸ",
        "kn": "ಪ್ರದರ್ಶನ", "gu": "ಪ್ರદર્શન", "th": "ผลงาน", "am": "ማሳያ",
        "yo": "Àfihàn", "my": "ပြခန်း", "om": "Agarsiisa", "ps": "ننداره",
        "uk": "Вітрина", "su": "Pameran", "pl": "Prezentacja", "uz": "Vitrina",
        "ro": "Vitrină", "az": "Vitrin", "ml": "ഷോകേസ്", "sd": "ڏيکاءُ",
        "ig": "Ngosipụta", "hu": "Bemutató", "el": "Βιτρίνα", "cs": "Ukázky",
        "nl": "Showcase", "sv": "Showcase", "fi": "Esittely", "no": "Showcase"
    },
    "custom": {
        "zh": "自定义频道", "zh-hans": "自定义频道", "zh-hant": "自定義頻道", "en": "Channel",
        "hi": "चैनल", "es": "Canal", "fr": "Canal", "ar": "القناة",
        "bn": "চ্যানেল", "pt": "Canal", "ru": "Канал", "ur": "چینل",
        "id": "Kanal", "de": "Kanal", "ja": "チャンネル", "mr": "चॅनेल",
        "te": "ఛానల్", "tr": "Kanal", "ta": "சேனல்", "vi": "Kênh",
        "tl": "Channel", "ko": "채널", "fa": "کانال", "ha": "Tashar",
        "sw": "Idhaa", "jv": "Saluran", "it": "Canale", "pa": "ਚੈਨਲ",
        "kn": "ಚಾನಲ್", "gu": "ચેનલ", "th": "ช่อง", "am": "ቻናል",
        "yo": "Ipa ọ̀nà", "my": "ချန်နယ်", "om": "Madaala", "ps": "چینل",
        "uk": "Канал", "su": "Saluran", "pl": "Kanał", "uz": "Kanal",
        "ro": "Canal", "az": "Kanal", "ml": "ചാനൽ", "sd": "چينل",
        "ig": "Ọwa", "hu": "Csatorna", "el": "Κανάλι", "cs": "Kanál",
        "nl": "Kanaal", "sv": "Kanal", "fi": "Kanava", "no": "Kanal"
    }
};

/**
 * 🏷️ 从产品系统全局语种智库中动态获取名称与国旗图标（零重复定义）
 */
function getProductLanguageMeta(code) {
    if (window.availableLangs && Array.isArray(window.availableLangs)) {
        const cleanCode = (code || '').toLowerCase().trim();
        const found = window.availableLangs.find(l => l.code === cleanCode || l.code === code);
        if (found) {
            return { name: found.name || code, flag: found.icon || '🌐' };
        }
    }
    return { name: code ? code.toUpperCase() : 'UNKNOWN', flag: '🌐' };
}

let activeIconPickerTarget = null;
let activeNavI18nTarget = null;

window.moveRouteMatrixRow = (btn, direction) => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) return;

    const row = btn.closest('.route-item');
    if (!row) return;

    const tbody = document.getElementById('route-matrix-body');
    if (!tbody) return;

    if (direction === 'up') {
        const prev = row.previousElementSibling;
        if (prev && prev.classList.contains('route-item')) {
            tbody.insertBefore(row, prev);
        }
    } else if (direction === 'down') {
        const next = row.nextElementSibling;
        if (next && next.classList.contains('route-item')) {
            tbody.insertBefore(next, row);
        }
    }

    window.refreshRouteMatrixOrderButtons();
    window.syncRouteMatrixToSettings();
};

window.refreshRouteMatrixOrderButtons = () => {
    const rows = document.querySelectorAll('#route-matrix-body .route-item');
    const total = rows.length;
    rows.forEach((r, idx) => {
        r.setAttribute('data-idx', idx);
        const upBtn = r.querySelector('.move-up-btn');
        const downBtn = r.querySelector('.move-down-btn');
        if (upBtn) {
            upBtn.disabled = (idx === 0);
            upBtn.style.color = (idx === 0) ? 'rgba(255,255,255,0.2)' : 'var(--text-dim)';
            upBtn.style.cursor = (idx === 0) ? 'default' : 'pointer';
        }
        if (downBtn) {
            downBtn.disabled = (idx === total - 1);
            downBtn.style.color = (idx === total - 1) ? 'rgba(255,255,255,0.2)' : 'var(--text-dim)';
            downBtn.style.cursor = (idx === total - 1) ? 'default' : 'pointer';
        }
    });
};

window.toggleIconPicker = (btn, event) => {
    if (event) event.stopPropagation();
    
    const existing = document.getElementById('global-icon-picker-popover');
    if (existing) {
        const isSame = (activeIconPickerTarget === btn);
        existing.remove();
        activeIconPickerTarget = null;
        if (isSame) return;
    }

    activeIconPickerTarget = btn;
    const rect = btn.getBoundingClientRect();

    let pickerHtml = `
        <div id="global-icon-picker-popover" class="glass-panel" style="position: fixed; top: ${rect.bottom + 6}px; left: ${Math.min(rect.left, window.innerWidth - 300)}px; width: 280px; max-height: 320px; overflow-y: auto; z-index: 99999; background: rgba(16, 18, 32, 0.96); backdrop-filter: blur(16px); border: 1px solid rgba(0, 242, 255, 0.3); border-radius: 10px; box-shadow: 0 12px 36px rgba(0,0,0,0.6); padding: 12px; font-family: inherit;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 6px;">
                <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent-secondary, #00f2fe);">✨ 选择导航图标</span>
                <button type="button" onclick="document.getElementById('global-icon-picker-popover')?.remove();" style="background: none; border: none; color: #888; cursor: pointer; font-size: 0.9rem; padding: 0 4px;">✕</button>
            </div>
    `;

    Object.entries(EMOJI_PALETTE).forEach(([cat, emojis]) => {
        pickerHtml += `
            <div style="margin-bottom: 8px;">
                <div style="font-size: 0.7rem; color: var(--text-dim); margin-bottom: 4px; font-weight: 600;">${cat}</div>
                <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px;">
                    ${emojis.map(e => `
                        <button type="button" class="emoji-opt-btn" onclick="window.selectNavIcon('${e}')" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-size: 1.1rem; padding: 4px 0; cursor: pointer; transition: all 0.15s ease; text-align: center;" onmouseover="this.style.background='rgba(0,242,255,0.15)'; this.style.borderColor='rgba(0,242,255,0.4)';" onmouseout="this.style.background='rgba(255,255,255,0.04)'; this.style.borderColor='rgba(255,255,255,0.06)';">${e}</button>
                    `).join('')}
                </div>
            </div>
        `;
    });

    pickerHtml += `
            <div style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px; display: flex; gap: 6px;">
                <input type="text" id="custom-emoji-input" placeholder="输入任意 Emoji..." maxlength="4" style="flex: 1; font-size: 0.76rem; padding: 4px 8px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #fff;" onkeydown="if(event.key==='Enter'){ window.selectNavIcon(this.value.trim()); event.preventDefault(); }">
                <button type="button" onclick="window.selectNavIcon(document.getElementById('custom-emoji-input').value.trim())" style="padding: 4px 10px; font-size: 0.74rem; background: var(--accent-primary, #00f2fe); color: #000; border: none; border-radius: 4px; font-weight: 600; cursor: pointer;">确定</button>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', pickerHtml);

    setTimeout(() => {
        const closeHandler = (e) => {
            const popover = document.getElementById('global-icon-picker-popover');
            if (popover && !popover.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
                popover.remove();
                activeIconPickerTarget = null;
                document.removeEventListener('click', closeHandler);
            }
        };
        document.addEventListener('click', closeHandler);
    }, 10);
};

window.selectNavIcon = (emoji) => {
    if (!emoji || !activeIconPickerTarget) return;
    const parentContainer = activeIconPickerTarget.parentElement;
    if (parentContainer) {
        const preview = activeIconPickerTarget.querySelector('.icon-preview');
        const hiddenInput = parentContainer.querySelector('.nav-icon-input');
        if (preview) preview.textContent = emoji;
        if (hiddenInput) hiddenInput.value = emoji;
    }
    const popover = document.getElementById('global-icon-picker-popover');
    if (popover) popover.remove();
    activeIconPickerTarget = null;
    window.syncRouteMatrixToSettings();
};

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

    // 🎯 严格仅列出当前版图已配置并启用的目标语言类型 (不罗列无关语种)
    const i18nSettings = window.settingsData?.i18n_settings || window.settingsData?.i18n || {};
    let targetLanguages = [];
    if (Array.isArray(i18nSettings.targets) && i18nSettings.targets.length > 0) {
        targetLanguages = i18nSettings.targets.filter(t => t && t.enabled !== false).map(t => typeof t === 'string' ? t : (t.lang_code || '')).filter(Boolean);
    } else if (Array.isArray(i18nSettings.target_languages) && i18nSettings.target_languages.length > 0) {
        targetLanguages = i18nSettings.target_languages.filter(Boolean);
    }

    // 探测当前版图母语
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
    targetLanguages.forEach(lang => {
        if (!currentI18n[lang] && (!COMMON_SLOT_I18N[slot] || !COMMON_SLOT_I18N[slot][lang])) {
            hasMissingDict = true;
        }
    });

    let modalHtml = `
        <div id="global-nav-i18n-modal" class="glass-panel" style="position: fixed; top: ${modalTop}px; left: ${modalLeft}px; width: 370px; max-height: 460px; overflow-y: auto; z-index: 99999; background: rgba(15, 17, 30, 0.98); backdrop-filter: blur(20px); border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 12px; box-shadow: 0 16px 48px rgba(0,0,0,0.7); padding: 14px; font-family: inherit;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 1rem;">🌐</span>
                    <span style="font-size: 0.82rem; font-weight: 700; color: var(--accent-secondary, #00f2fe);">当前版图多语种导航定制</span>
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
                    💡 当前品牌版图尚未启用任何多语言目标语种。<br>如需多语言发布，请在左侧<b>【多语种翻译】</b>中点选开启。
                </div>
            ` : `
                <div id="i18n-inputs-container" style="display: flex; flex-direction: column; gap: 8px; max-height: 250px; overflow-y: auto; padding-right: 4px;">
            `}
    `;

    targetLanguages.forEach(lang => {
        const meta = getProductLanguageMeta(lang);
        const val = currentI18n[lang] || "";
        const dictVal = COMMON_SLOT_I18N[slot] && COMMON_SLOT_I18N[slot][lang];
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
    let event = null;
    let slot = 'docs';
    let defaultLabel = '';
    let lang = 'zh';

    if (eventOrSlot && eventOrSlot.preventDefault) {
        event = eventOrSlot;
        if (event.stopPropagation) event.stopPropagation();
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
    inputs.forEach(input => {
        const targetLang = input.getAttribute('data-lang');
        if (!targetLang) return;
        const dictVal = COMMON_SLOT_I18N[slot] && COMMON_SLOT_I18N[slot][targetLang];
        if (dictVal && (!defaultLabel || defaultLabel === slot || ["文档中心", "官方博客", "展示页面", "自定义频道", "Docs", "Blog", "Showcase"].includes(defaultLabel))) {
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
            if (typeof window.apiFetch === 'function') {
                resData = await window.apiFetch('/api/governance/translate-nav-labels', {
                    method: 'POST',
                    body: JSON.stringify({
                        label: defaultLabel,
                        target_languages: pendingAILangs,
                        slot: slot,
                        source_language: lang || 'zh'
                    })
                });
            } else if (typeof apiFetch === 'function') {
                resData = await apiFetch('/api/governance/translate-nav-labels', {
                    method: 'POST',
                    body: JSON.stringify({
                        label: defaultLabel,
                        target_languages: pendingAILangs,
                        slot: slot,
                        source_language: lang || 'zh'
                    })
                });
            } else {
                const token = window.settingsData?._api_token || window.settingsData?.system?.api_token || '';
                const rawRes = await fetch('/api/governance/translate-nav-labels', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { 'X-Token': token } : {})
                    },
                    body: JSON.stringify({
                        label: defaultLabel,
                        target_languages: pendingAILangs,
                        slot: slot,
                        source_language: lang || 'zh'
                    })
                });
                if (rawRes.ok) {
                    resData = await rawRes.json();
                }
            }

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
                        const fallback = (COMMON_SLOT_I18N[slot] && COMMON_SLOT_I18N[slot][l]) || defaultLabel;
                        input.value = fallback;
                    }
                });
            }
        } catch (e) {
            console.warn('AI translation API failed, applying local fallback:', e);
            inputs.forEach(input => {
                const l = input.getAttribute('data-lang');
                if (l && !input.value) {
                    const fallback = (COMMON_SLOT_I18N[slot] && COMMON_SLOT_I18N[slot][l]) || defaultLabel;
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

    window.syncRouteMatrixToSettings();
};

window.addRouteMatrixRow = () => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '👑 专属版本权益提示',
                html: '高级频道路由与专属翻译风格矩阵为 <b>Illacme Plenipes 专属授权版 (PRO)</b> 的特权功能。<br><br>系统当前已为您自动回落至无缝的物理路径映射模式。',
                icon: 'info',
                background: 'rgba(20, 15, 25, 0.95)',
                color: '#fff',
                confirmButtonColor: 'var(--accent-primary, #a34cff)',
                confirmButtonText: '我知道了'
            });
        } else {
            alert('本功能为专属版专属功能，当前已自动降级至物理路由模式。');
        }
        return;
    }

    const themeSlots = window.settingsData._theme_slots || {};
    const hasSlots = Object.keys(themeSlots).length > 0;

    const tbody = document.getElementById('route-matrix-body');
    const emptyState = tbody.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const newIdx = tbody.querySelectorAll('.route-item').length;
    
    const rowHtml = `
        <div class="matrix-row route-item" data-idx="${newIdx}" style="display: grid; grid-template-columns: 36px 1.1fr 1fr 1fr 1.4fr 0.9fr 46px 36px; gap: 8px; padding: 8px 4px; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;">
            <!-- 0. 排序控制器 -->
            <div class="order-controls" style="display: flex; flex-direction: column; gap: 2px; align-items: center; justify-content: center;">
                <button type="button" class="mini-btn move-up-btn" onclick="window.moveRouteMatrixRow(this, 'up')" style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: var(--text-dim); border: 1px solid rgba(255,255,255,0.08); cursor: pointer;" title="上移">▲</button>
                <button type="button" class="mini-btn move-down-btn" onclick="window.moveRouteMatrixRow(this, 'down')" disabled style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.08); cursor: default;" title="下移">▼</button>
            </div>
            <!-- 1. 文库目录 -->
            <div>
                ${(() => {
                    const directories = window.settingsData._directories || [];
                    const hasDirs = directories.length > 0;
                    let html = '';
                    if (hasDirs) {
                        html += `<select class="setting-input source-select" style="width: 100%; font-size: 0.74rem; padding: 5px 6px;" onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; } syncRouteMatrixToSettings();">`;
                        html += `<option value="" selected>-- 选择目录 --</option>`;
                        directories.forEach(d => {
                            if(d) html += `<option value="${d}">📁 ${d}</option>`;
                        });
                        html += `<option value="_custom">✏️ 自定义... </option>`;
                        html += `</select>`;
                    }
                    html += `<input type="text" class="setting-input source-input" value="" placeholder="例如: docs" style="width: 100%; font-size: 0.74rem; padding: 5px 6px; display: ${!hasDirs ? 'block' : 'none'};" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">`;
                    return html;
                })()}
            </div>
            <!-- 2. 网页路径 -->
            <div>
                <input type="text" class="setting-input prefix-input" value="" placeholder="例如: /docs/" style="width: 100%; color: var(--accent-secondary); font-family: monospace; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
            </div>
            <!-- 3. 网页模板 -->
            <div>
                ${(() => {
                    let html = '';
                    if (hasSlots) {
                        html += `<select class="setting-input slot-select" style="width: 100%; font-size: 0.74rem; padding: 5px 6px;" onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; } syncRouteMatrixToSettings();">`;
                        Object.entries(themeSlots).forEach(([k, v]) => {
                            html += `<option value="${k}">${v.label || k}</option>`;
                        });
                        html += `<option value="_custom">✏️ 自定义... </option>`;
                        html += `</select>`;
                    }
                    html += `<input type="text" class="setting-input slot-input" value="docs" placeholder="例如: docs" style="width: 100%; font-size: 0.74rem; padding: 5px 6px; display: ${!hasSlots ? 'block' : 'none'};" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">`;
                    return html;
                })()}
            </div>
            <!-- 4. 顶栏导航 -->
            <div style="display: flex; gap: 4px; align-items: center; position: relative;">
                <button type="button" class="mini-btn icon-picker-btn" onclick="window.toggleIconPicker(this, event)" style="width: 30px; height: 26px; padding: 0; font-size: 0.92rem; border-radius: 6px; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; transition: all 0.2s;" title="点击弹出选择常见图标">
                    <span class="icon-preview">📚</span>
                </button>
                <input type="hidden" class="nav-icon-input" value="📚">
                <input type="text" class="setting-input nav-label-input" value="" placeholder="显示名称" style="flex: 1; min-width: 0; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
                
                <button type="button" class="mini-btn nav-i18n-btn" onclick="window.toggleNavI18nModal(this, event)" style="padding: 2px 6px; height: 26px; font-size: 0.7rem; border-radius: 6px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-dim); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; gap: 3px;" title="配置多语种导航名称">
                    <span>🌐</span>
                    <span class="i18n-count-badge" style="font-size: 0.65rem; font-weight: 700;">+</span>
                </button>
                <input type="hidden" class="nav-i18n-input" value="{}">
            </div>
            <!-- 5. 翻译风格 -->
            <div>
                <select class="setting-input style-input" style="width: 100%; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()">
                    <option value="">继承全局默认</option>
                    <option value="professional">💼 商务严谨</option>
                    <option value="casual">☕ 随性自然</option>
                    <option value="literal">⚖️ 精准直译</option>
                </select>
            </div>
            <!-- 6. 顶栏展示 -->
            <div style="text-align: center;">
                <input type="checkbox" class="nav-show-input" checked onchange="syncRouteMatrixToSettings()" style="cursor: pointer; transform: scale(1.1); accent-color: var(--accent-secondary, #00f2fe);" title="是否在网站顶栏导航显示" />
            </div>
            <!-- 7. 操作 -->
            <div style="text-align: center;">
                <button class="mini-btn" onclick="removeRouteMatrixRow(this)" style="background: rgba(255,50,50,0.1); border: 1px solid rgba(255,50,50,0.3); color: #ff5555; height: 26px; width: 26px; padding: 0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;" title="删除此规则">×</button>
            </div>
        </div>
    `;
    
    tbody.insertAdjacentHTML('beforeend', rowHtml);
    
    window.refreshRouteMatrixOrderButtons();
    
    const container = document.querySelector('#view-settings .tab-content-area');
    if (container) {
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }

    syncRouteMatrixToSettings();
};

window.addExternalNavRow = () => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '👑 专属版本权益提示',
                html: '高级频道路由与专属全景导航为 <b>Illacme Plenipes 专属授权版 (PRO)</b> 的特权功能。',
                icon: 'info',
                background: 'rgba(20, 15, 25, 0.95)',
                color: '#fff',
                confirmButtonColor: 'var(--accent-primary, #a34cff)',
                confirmButtonText: '我知道了'
            });
        }
        return;
    }

    const tbody = document.getElementById('route-matrix-body');
    const emptyState = tbody.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const newIdx = tbody.querySelectorAll('.route-item').length;
    
    const rowHtml = `
        <div class="matrix-row route-item" data-idx="${newIdx}" style="display: grid; grid-template-columns: 36px 1.1fr 1fr 1fr 1.4fr 0.9fr 46px 36px; gap: 8px; padding: 8px 4px; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;">
            <!-- 0. 排序控制器 -->
            <div class="order-controls" style="display: flex; flex-direction: column; gap: 2px; align-items: center; justify-content: center;">
                <button type="button" class="mini-btn move-up-btn" onclick="window.moveRouteMatrixRow(this, 'up')" style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: var(--text-dim); border: 1px solid rgba(255,255,255,0.08); cursor: pointer;" title="上移">▲</button>
                <button type="button" class="mini-btn move-down-btn" onclick="window.moveRouteMatrixRow(this, 'down')" disabled style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.08); cursor: default;" title="下移">▼</button>
            </div>
            <!-- 1. 文库目录 -->
            <div>
                <input type="text" class="setting-input source-input" value="🌐 外部直链" disabled style="width: 100%; font-size: 0.74rem; padding: 5px 6px; opacity: 0.7;">
            </div>
            <!-- 2. 网页路径 -->
            <div>
                <input type="text" class="setting-input ext-url-input" value="https://" placeholder="https://..." style="width: 100%; color: var(--neon-cyan, #00f2fe); font-family: monospace; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
            </div>
            <!-- 3. 网页模板 -->
            <div>
                <span style="font-size: 0.72rem; color: var(--text-dim); padding: 4px 8px; background: rgba(255,255,255,0.03); border-radius: 4px; display: inline-block;">🔗 外部直链</span>
            </div>
            <!-- 4. 顶栏导航 -->
            <div style="display: flex; gap: 4px; align-items: center; position: relative;">
                <button type="button" class="mini-btn icon-picker-btn" onclick="window.toggleIconPicker(this, event)" style="width: 30px; height: 26px; padding: 0; font-size: 0.92rem; border-radius: 6px; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; transition: all 0.2s;" title="点击弹出选择常见图标">
                    <span class="icon-preview">🌐</span>
                </button>
                <input type="hidden" class="nav-icon-input" value="🌐">
                <input type="text" class="setting-input nav-label-input" value="GitHub / 官网" placeholder="菜单显示名称" style="flex: 1; min-width: 0; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
                
                <button type="button" class="mini-btn nav-i18n-btn" onclick="window.toggleNavI18nModal(this, event)" style="padding: 2px 6px; height: 26px; font-size: 0.7rem; border-radius: 6px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-dim); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; gap: 3px;" title="配置多语种导航名称">
                    <span>🌐</span>
                    <span class="i18n-count-badge" style="font-size: 0.65rem; font-weight: 700;">+</span>
                </button>
                <input type="hidden" class="nav-i18n-input" value="{}">
            </div>
            <!-- 5. 翻译风格 -->
            <div>
                <select class="setting-input style-input" disabled style="width: 100%; font-size: 0.74rem; padding: 5px 6px; opacity: 0.5;">
                    <option value="">不适用</option>
                </select>
            </div>
            <!-- 6. 顶栏展示 -->
            <div style="text-align: center;">
                <input type="checkbox" class="nav-show-input" checked onchange="syncRouteMatrixToSettings()" style="cursor: pointer; transform: scale(1.1); accent-color: var(--accent-secondary, #00f2fe);" title="是否在网站顶栏导航显示" />
            </div>
            <!-- 7. 操作 -->
            <div style="text-align: center;">
                <button class="mini-btn" onclick="removeRouteMatrixRow(this)" style="background: rgba(255,50,50,0.1); border: 1px solid rgba(255,50,50,0.3); color: #ff5555; height: 26px; width: 26px; padding: 0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;" title="删除此规则">×</button>
            </div>
        </div>
    `;
    
    tbody.insertAdjacentHTML('beforeend', rowHtml);
    
    window.refreshRouteMatrixOrderButtons();
    
    const container = document.querySelector('#view-settings .tab-content-area');
    if (container) {
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }

    syncRouteMatrixToSettings();
};

window.applyRecommendedRouteMatrix = (detectedSubdirs) => {
    const recommended = [];
    
    const defaultMeta = {
        "Docs": { 
            prefix: "docs", slot: "docs", label: "文档中心", icon: "📚",
            i18n: { "en": "Documentation", "ja": "ドキュメント", "fr": "Documentation", "de": "Dokumentation" }
        },
        "Blog": { 
            prefix: "blog", slot: "blog", label: "官方博客", icon: "📰",
            i18n: { "en": "Blog", "ja": "ブログ", "fr": "Blog", "de": "Blog" }
        },
        "Pages": { 
            prefix: "pages", slot: "pages", label: "展示页面", icon: "📄",
            i18n: { "en": "Showcase", "ja": "ショーケース", "fr": "Vitrines", "de": "Seiten" }
        },
    };

    detectedSubdirs.forEach((d, idx) => {
        const meta = defaultMeta[d] || { prefix: d.toLowerCase(), slot: "docs", label: d, icon: "📁", i18n: {} };
        recommended.push({
            source: d,
            prefix: meta.prefix,
            target_slot: meta.slot,
            nav_label: meta.label,
            nav_label_i18n: meta.i18n || {},
            nav_icon: meta.icon,
            show_in_nav: true,
            nav_position: "left",
            nav_order: idx,
            style: null
        });
    });

    window.settingsData.route_matrix = recommended;
    if (typeof window.checkSettingsDirty === 'function') {
        window.checkSettingsDirty();
    }

    // 重新渲染当前 Tab
    if (typeof window.renderDisseminationRoutingCategory === 'function') {
        window.renderDisseminationRoutingCategory();
        setTimeout(() => {
            if (typeof window.switchDisseminationRoutingSubTab === 'function') {
                window.switchDisseminationRoutingSubTab('route_matrix');
            }
        }, 30);
    }
};

window.removeRouteMatrixRow = (btn) => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '👑 专属版本权益提示',
                html: '高级频道路由与专属翻译风格矩阵为 <b>Illacme Plenipes 专属授权版 (PRO)</b> 的特权功能。<br><br>系统当前已为您自动回落至无缝的物理路径映射模式。',
                icon: 'info',
                background: 'rgba(20, 15, 25, 0.95)',
                color: '#fff',
                confirmButtonColor: 'var(--accent-primary, #a34cff)',
                confirmButtonText: '我知道了'
            });
        } else {
            alert('本功能为专属版专属功能，当前已自动降级至物理路由模式。');
        }
        return;
    }
    
    const row = btn.closest('.route-item');
    if (row) {
        row.style.opacity = '0';
        row.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            row.remove();
            
            const tbody = document.getElementById('route-matrix-body');
            if (tbody && tbody.querySelectorAll('.route-item').length === 0) {
                tbody.innerHTML = `
                    <div class="empty-state" style="padding: 40px; text-align: center; color: var(--text-dim);">
                        暂无路由与导航策略。您的全部文件目前均按照原始物理路径进行映射发布。
                    </div>
                `;
            } else {
                window.refreshRouteMatrixOrderButtons();
            }
            syncRouteMatrixToSettings();
        }, 200);
    }
};

window.syncRouteMatrixToSettings = () => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) return;

    const routeItems = document.querySelectorAll('.route-item');
    const newRouteMatrix = [];

    routeItems.forEach((item, idx) => {
        const sourceInput = item.querySelector('.source-input');
        const prefixInput = item.querySelector('.prefix-input');
        const extUrlInput = item.querySelector('.ext-url-input');
        const slotInput = item.querySelector('.slot-input');
        const styleInput = item.querySelector('.style-input');
        const navLabelInput = item.querySelector('.nav-label-input');
        const navIconInput = item.querySelector('.nav-icon-input');
        const navShowInput = item.querySelector('.nav-show-input');
        const navI18nInput = item.querySelector('.nav-i18n-input');

        const source = sourceInput ? sourceInput.value.trim() : "";
        const prefix = prefixInput ? prefixInput.value.trim() : "";
        const extUrl = extUrlInput ? extUrlInput.value.trim() : "";
        const target_slot = slotInput ? slotInput.value.trim() : "docs";
        const style = styleInput ? styleInput.value : "";
        const nav_label = navLabelInput ? navLabelInput.value.trim() : "";
        const nav_icon = navIconInput ? navIconInput.value.trim() : "";
        const show_in_nav = navShowInput ? navShowInput.checked : true;

        let nav_label_i18n = null;
        if (navI18nInput && navI18nInput.value) {
            try {
                const parsed = JSON.parse(navI18nInput.value);
                if (parsed && typeof parsed === 'object' && Object.keys(parsed).length > 0) {
                    nav_label_i18n = parsed;
                }
            } catch (e) {}
        }

        if (extUrl) {
            newRouteMatrix.push({
                source: "",
                prefix: "",
                target_slot: "external",
                external_url: extUrl,
                nav_label: nav_label || "External Link",
                nav_label_i18n: nav_label_i18n,
                nav_icon: nav_icon || "🌐",
                show_in_nav: show_in_nav,
                nav_position: "right",
                nav_order: idx,
                style: null
            });
            return;
        }

        // Skip empty sources
        if (!source) return;

        newRouteMatrix.push({
            source: source,
            prefix: prefix || "",
            target_slot: target_slot || "docs",
            nav_label: nav_label || source,
            nav_label_i18n: nav_label_i18n,
            nav_icon: nav_icon || "📚",
            show_in_nav: show_in_nav,
            nav_position: "left",
            nav_order: idx,
            style: style || null
        });
    });

    window.settingsData.route_matrix = newRouteMatrix;

    if (typeof window.checkSettingsDirty === 'function') {
        window.checkSettingsDirty();
    }
};
