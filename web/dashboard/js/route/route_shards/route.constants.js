/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - Constants & Dictionary Shard
 * 职责：常用导航图标 Emoji 调色盘、50 语种导航标准字典、语种元数据动态解析。
 */

(function () {
    // 常用图标库分类定义
    window.EMOJI_PALETTE = {
        "📚 文档与知识": ["📚", "📖", "📄", "📝", "📰", "📁", "📑", "📋", "🧠", "💡", "🔖", "✍️"],
        "🌐 网络与导航": ["🌐", "🐙", "🔗", "🚀", "🧭", "🏠", "📡", "💻", "⚡", "🎯", "🗺️", "🔌"],
        "🎨 视觉与分类": ["🎨", "🎭", "☕", "💼", "🔬", "⭐", "📦", "🏷️", "🔍", "💬", "📊", "🛡️"],
        "⚙️ 系统与工具": ["⚙️", "🛠️", "💎", "🔥", "✨", "📌", "🎉", "❤️", "🟢", "🔑", "🔔", "🚩"]
    };

    // 🌍 [V100.9] 全量 50 语种导航标准字典 (100% 覆盖产品所有受控语种)
    window.COMMON_SLOT_I18N = {
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
    window.getProductLanguageMeta = function (code) {
        if (window.availableLangs && Array.isArray(window.availableLangs)) {
            const cleanCode = (code || '').toLowerCase().trim();
            const found = window.availableLangs.find(l => l.code === cleanCode || l.code === code);
            if (found) {
                return { name: found.name || code, flag: found.icon || '🌐' };
            }
        }
        return { name: code ? code.toUpperCase() : 'UNKNOWN', flag: '🌐' };
    };
})();
