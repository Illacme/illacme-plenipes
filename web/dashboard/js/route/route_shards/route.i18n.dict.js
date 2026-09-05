/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - Constants & Dictionary Shard
 * 职责：常用导航图标 Emoji 调色盘、50 语种受控标准导航翻译字典、系统级标准模板槽位兜底定义。
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
            "zh": "独立页面", "zh-hans": "独立页面", "zh-hant": "獨立頁面", "en": "Pages",
            "hi": "पृष्ठ", "es": "Páginas", "fr": "Pages", "ar": "الصفحات",
            "bn": "পৃষ্ঠা", "pt": "Páginas", "ru": "Страницы", "ur": "صفحات",
            "id": "Halaman", "de": "Seiten", "ja": "ページ", "mr": "पृष्ठे",
            "te": "పేజీలు", "tr": "Sayfalar", "ta": "பக்கங்கள்", "vi": "Trang",
            "tl": "Mga Pahina", "ko": "페이지", "fa": "صفحه‌ها", "ha": "Shafuka",
            "sw": "Kurasa", "jv": "Kaca", "it": "Pagine", "pa": "ਪੰਨੇ",
            "kn": "ಪುಟಗಳು", "gu": "પૃષ્ઠો", "th": "หน้า", "am": "ገጾች",
            "yo": "Àwọn ojú-ewé", "my": "စာမျက်နှာများ", "om": "Fuulawwan", "ps": "پاڼې",
            "uk": "Сторінки", "su": "Kaca", "pl": "Strony", "uz": "Sahifalar",
            "ro": "Pagini", "az": "Səhifələr", "ml": "പേജുകൾ", "sd": "صفحا",
            "ig": "Ihu akwụkwọ", "hu": "Oldalak", "el": "Σελίδες", "cs": "Stránky",
            "nl": "Pagina's", "sv": "Sidor", "fi": "Sivut", "no": "Sider"
        },
        "showcase": {
            "zh": "展示中心", "zh-hans": "展示中心", "zh-hant": "展示中心", "en": "Show",
            "hi": "प्रदर्शनी", "es": "Exhibición", "fr": "Vitrines", "ar": "المعرض",
            "bn": "শোকেস", "pt": "Vitrine", "ru": "Витрина", "ur": "شوکیس",
            "id": "Showcase", "de": "Showcase", "ja": "ショーケース", "mr": "प्रदर्शन",
            "te": "ప్రదర్శన", "tr": "Vitrin", "ta": "காட்சி", "vi": "Trưng bày",
            "tl": "Showcase", "ko": "쇼케이스", "fa": "ویترین", "ha": "Nunin",
            "sw": "Maonyesho", "jv": "Pameran", "it": "Vetrina", "pa": "ਸ਼ੋਕੇਸ",
            "kn": "ಪ್ರದರ್ಶನ", "gu": "પ્રદર્શન", "th": "ผลงาน", "am": "ማሳያ",
            "yo": "Àfihàn", "my": "ပြခန်း", "om": "Agarsiisa", "ps": "ننداره",
            "uk": "Вітрина", "su": "Pameran", "pl": "Prezentacja", "uz": "Vitrina",
            "ro": "Vitrină", "az": "Vitrin", "ml": "ഷോകേസ്", "sd": "ڏيکاءُ",
            "ig": "Ngosipụta", "hu": "Bemutató", "el": "Βιτρίνα", "cs": "Ukázky",
            "nl": "Showcase", "sv": "Showcase", "fi": "Esittely", "no": "Showcase"
        },
        "about": {
            "zh": "关于", "zh-hans": "关于", "zh-hant": "關於", "en": "About",
            "hi": "परिचय", "es": "Acerca de", "fr": "À propos", "ar": "حول",
            "bn": "সম্পর্কে", "pt": "Sobre", "ru": "О нас", "ur": "کے بارے میں",
            "id": "Tentang", "de": "Über uns", "ja": "アバウト", "mr": "बद्दल",
            "te": "గురించి", "tr": "Hakkında", "ta": "பற்றி", "vi": "Giới thiệu",
            "tl": "Tungkol", "ko": "소개", "fa": "درباره ما", "ha": "Game da",
            "sw": "Kuhusu", "jv": "Babagan", "it": "Chi siamo", "pa": "ਬਾਰੇ",
            "kn": "ಬಗ್ಗೆ", "gu": "વિશે", "th": "เกี่ยวกับ", "am": "ስለ",
            "yo": "Nípa", "my": "အကြောင်း", "om": "Waa'ee", "ps": "په اړه",
            "uk": "Про нас", "su": "Ngeunaan", "pl": "O nas", "uz": "Haqida",
            "ro": "Despre", "az": "Haqqında", "ml": "കുറിച്ച്", "sd": "بابت",
            "ig": "Gbasara", "hu": "Rólunk", "el": "Σχετικά", "cs": "O nás",
            "nl": "Over ons", "sv": "Om oss", "fi": "Tietoa meistä", "no": "Om oss"
        },
        "features": {
            "zh": "特性", "zh-hans": "特性", "zh-hant": "特性", "en": "Features",
            "hi": "विशेषताएं", "es": "Características", "fr": "Fonctionnalités", "ar": "الميزات",
            "bn": "বৈশিষ্ট্য", "pt": "Recursos", "ru": "Функции", "ur": "خصوصیات",
            "id": "Fitur", "de": "Funktionen", "ja": "機能", "mr": "वैशिष्ट्ये",
            "te": "లక్షణాలు", "tr": "Özellikler", "ta": "அம்சங்கள்", "vi": "Tính năng",
            "tl": "Mga Tampok", "ko": "기능", "fa": "امکانات", "ha": "Fasali",
            "sw": "Vipengele", "jv": "Fitur", "it": "Funzionalità", "pa": "ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ",
            "kn": "ವೈಶಿಷ್ಟ್ಯಗಳು", "gu": "વિશેಷતાઓ", "th": "คุณสมบัติ", "am": "ባህሪዎች",
            "yo": "Àwọn ẹ̀yà", "my": "အင်္ဂါရပ်များ", "om": "Amaloota", "ps": "ځانګړتیاوې",
            "uk": "Можливості", "su": "Fitur", "pl": "Funkcje", "uz": "Xususiyatlar",
            "ro": "Funcționalități", "az": "Xüsusiyyətlər", "ml": "സവിശേഷതകൾ", "sd": "خاصيتون",
            "ig": "Njirimara", "hu": "Funkciók", "el": "Δυνατότητες", "cs": "Funkce",
            "nl": "Functies", "sv": "Funktioner", "fi": "Ominaisuudet", "no": "Funksjoner"
        },
        "home": {
            "zh": "首页", "zh-hans": "首页", "zh-hant": "首頁", "en": "Home",
            "hi": "होम", "es": "Inicio", "fr": "Accueil", "ar": "الرئيسية",
            "bn": "হোম", "pt": "Início", "ru": "Главная", "ur": "ہوم",
            "id": "Beranda", "de": "Startseite", "ja": "ホーム", "mr": "मुख्यपृष्ठ",
            "te": "హోమ్", "tr": "Ana Sayfa", "ta": "முகப்பு", "vi": "Trang chủ",
            "tl": "Home", "ko": "홈", "fa": "صفحه اصلی", "ha": "Gida",
            "sw": "Nyumbani", "jv": "Beranda", "it": "Home", "pa": "ਮੁੱਖ ਪੰਨਾ",
            "kn": "ಮುಖಪುಟ", "gu": "હોಮ", "th": "หน้าแรก", "am": "ዋና ገጽ",
            "yo": "Ilé", "my": "ပင်မစာမျက်နှာ", "om": "Fuula Duraa", "ps": "کورپاڼه",
            "uk": "Головна", "su": "Beranda", "pl": "Strona główna", "uz": "Bosh sahifa",
            "ro": "Acasă", "az": "Ana səhifə", "ml": "ഹോം", "sd": "مک صفحو",
            "ig": "Ụlọ", "hu": "Kezdőlap", "el": "Αρχική", "cs": "Domů",
            "nl": "Home", "sv": "Hem", "fi": "Koti", "no": "Hjem"
        },
        "static": {
            "zh": "静态资源", "zh-hans": "静态资源", "zh-hant": "靜態資源", "en": "Static Assets",
            "hi": "स्थिर संपत्ति", "es": "Recursos Estáticos", "fr": "Ressources Statiques", "ar": "الأصول الثابتة",
            "bn": "স্থির সম্পদ", "pt": "Ativos Estáticos", "ru": "Статические ресурсы", "ur": "جامد اثاثے",
            "id": "Aset Statis", "de": "Statische Ressourcen", "ja": "静的リソース", "mr": "स्थिर मालमत्ता",
            "te": "స్థిర వనరులు", "tr": "Statik Varlıklar", "ta": "நிலையான சொத்துக்கள்", "vi": "Tài nguyên tĩnh",
            "tl": "Mga Static na Asset", "ko": "정적 리소스", "fa": "دارایی‌های استاتیک", "ha": "Kadarorin Tsaye",
            "sw": "Rasilimali Tuli", "jv": "Aset Statis", "it": "Risorse Statiche", "pa": "ਸਥਿਰ ਸੰਪਤੀਆਂ",
            "kn": "ಸ್ಥಿರ ಸಂಪನ್ಮೂಲಗಳು", "gu": "સ્થિર સંસાધનો", "th": "ทรัพยากรคงที่", "am": "የማይንቀሳቀሱ ንብረቶች",
            "yo": "Àwọn ohun-ìní tí kò yípadà", "my": "အငြိမ်ပိုင်ဆိုင်မှုများ", "om": "Qabeenya Dhaabbataa", "ps": "جامد شتمنۍ",
            "uk": "Статичні ресурси", "su": "Aset Statis", "pl": "Zasoby Statyczne", "uz": "Statik resurslar",
            "ro": "Resurse Statice", "az": "Statik Resurslar", "ml": "സ്ഥിര വിഭവങ്ങൾ", "sd": "مستقل اثاثا",
            "ig": "Ngwongwo Na-adịghị Agbanwe", "hu": "Statikus Erőforrások", "el": "Στατικοί Πόροι", "cs": "Statické Zdroje",
            "nl": "Statische Bronnen", "sv": "Statiska Resurser", "fi": "Staattiset Resurssit", "no": "Statiske Ressurser"
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

    // 🎨 [V105.0] 系统级标准模板槽位兜底定义
    window.DEFAULT_THEME_SLOTS = {
        "docs": { "label": "📚 文档中心 (docs)" },
        "blog": { "label": "📰 博客文章 (blog)" },
        "showcase": { "label": "🎨 展示中心 (show)" },
        "pages": { "label": "📄 独立页面 (pages)" },
        "static": { "label": "📦 静态资源 (static)" }
    };
})();
