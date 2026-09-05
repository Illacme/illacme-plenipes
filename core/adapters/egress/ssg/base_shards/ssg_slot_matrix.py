#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Slot I18N Matrix
模块职责：全量 50 语种导航与功能槽标准字典矩阵 (100% 对齐 SUPPORTED_MATRIX)。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
from typing import Dict

# 🌍 [V100.9] 全量 50 语种导航标准字典矩阵 (100% 对齐 SUPPORTED_MATRIX)
SLOT_I18N_FALLBACK: Dict[str, Dict[str, str]] = {
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
        "kn": "ವೈಶಿಷ್ಟ್ಯಗಳು", "gu": "વિશેષતાઓ", "th": "คุณสมบัติ", "am": "ባህሪዎች",
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
        "kn": "ಮುಖಪುಟ", "gu": "હોમ", "th": "หน้าแรก", "am": "ዋና ገጽ",
        "yo": "Ilé", "my": "ပင်မစာမျက်နှာ", "om": "Fuula Duraa", "ps": "کورپاڼه",
        "uk": "Головна", "su": "Beranda", "pl": "Strona główna", "uz": "Bosh sahifa",
        "ro": "Acasă", "az": "Ana səhifə", "ml": "ഹോം", "sd": "مک صفحو",
        "ig": "Ụlọ", "hu": "Kezdőlap", "el": "Αρχική", "cs": "Domů",
        "nl": "Home", "sv": "Hem", "fi": "Koti", "no": "Hjem"
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
}

# 🌍 [V101.0] 全球 50 语种前台视图与组件交互标准矩阵 (100% 对齐 SUPPORTED_MATRIX)
VIEW_I18N_MATRIX: Dict[str, Dict[str, str]] = {
    "timeline": {
        "zh": "时间轴", "zh-hans": "时间轴", "zh-hant": "時間軸", "en": "Timeline",
        "hi": "समयरेखा", "es": "Cronología", "fr": "Chronologie", "ar": "الجدول الزمني",
        "bn": "সময়রেখা", "pt": "Linha do Tempo", "ru": "Хронология", "ur": "ٹائم لائن",
        "id": "Linimasa", "de": "Zeitleiste", "ja": "タイムライン", "mr": "टाइमलाइन",
        "te": "కాలక్రమం", "tr": "Zaman Çizelgesi", "ta": "காலவரிசை", "vi": "Dòng thời gian",
        "tl": "Timeline", "ko": "타임라인", "fa": "خط زمانی", "ha": "Jadawalin lokaci",
        "sw": "Mfuatano", "jv": "Garise wektu", "it": "Cronologia", "pa": "ਸਮਾਂ-ਰੇਖਾ",
        "kn": "ಸಮಯರೇಖೆ", "gu": "સમયરેખા", "th": "ไทม์ไลน์", "am": "የጊዜ ሰሌዳ",
        "yo": "Àkókò", "my": "အချိန်လိုင်း", "om": "Sarara yeroo", "ps": "مهال ویش",
        "uk": "Хронологія", "su": "Garimsa waktu", "pl": "Oś czasu", "uz": "Vaqt jadvali",
        "ro": "Cronologie", "az": "Xronologiya", "ml": "ടൈംലൈൻ", "sd": "ٽائم لائن",
        "ig": "Usoro oge", "hu": "Idővonal", "el": "Χρονολόγιο", "cs": "Časová osa",
        "nl": "Tijdlijn", "sv": "Tidslinje", "fi": "Aikajana", "no": "Tidslinje"
    },
    "cards": {
        "zh": "卡片", "zh-hans": "卡片", "zh-hant": "卡片", "en": "Cards",
        "hi": "कार्ड", "es": "Tarjetas", "fr": "Cartes", "ar": "بطاقات",
        "bn": "কার্ড", "pt": "Cartões", "ru": "Карточки", "ur": "کارڈز",
        "id": "Kartu", "de": "Karten", "ja": "カード", "mr": "कार्डे",
        "te": "కార్డులు", "tr": "Kartlar", "ta": "அட்டைகள்", "vi": "Thẻ",
        "tl": "Mga Card", "ko": "카드", "fa": "کارت‌ها", "ha": "Katuna",
        "sw": "Kadi", "jv": "Kertu", "it": "Schede", "pa": "ਕਾਰਡ",
        "kn": "ಕಾರ್ಡ್‌ಗಳು", "gu": "કાર્ડ્સ", "th": "การ์ด", "am": "ካርዶች",
        "yo": "Àwọn káàdì", "my": "ကတ်များ", "om": "Kaardota", "ps": "کارتونه",
        "uk": "Картки", "su": "Kartu", "pl": "Karty", "uz": "Kartalar",
        "ro": "Carduri", "az": "Kartlar", "ml": "കാർഡുകൾ", "sd": "ڪارڊ",
        "ig": "Kaadị", "hu": "Kártyák", "el": "Κάρτες", "cs": "Karty",
        "nl": "Kaarten", "sv": "Kort", "fi": "Kortit", "no": "Kort"
    },
    "list": {
        "zh": "列表", "zh-hans": "列表", "zh-hant": "列表", "en": "List",
        "hi": "सूची", "es": "Lista", "fr": "Liste", "ar": "قائمة",
        "bn": "তালিকা", "pt": "Lista", "ru": "Список", "ur": "فہرست",
        "id": "Daftar", "de": "Liste", "ja": "リスト", "mr": "यादी",
        "te": "జాబితా", "tr": "Liste", "ta": "பட்டியல்", "vi": "Danh sách",
        "tl": "Talaan", "ko": "목록", "fa": "فهرست", "ha": "Jerin",
        "sw": "Orodha", "jv": "Pratelan", "it": "Elenco", "pa": "ਸੂਚੀ",
        "kn": "ಪಟ್ಟಿ", "gu": "યાદી", "th": "รายการ", "am": "ዝርዝር",
        "yo": "Àtòjọ", "my": "စာရင်း", "om": "Tarree", "ps": "لړلیک",
        "uk": "Список", "su": "Daptar", "pl": "Lista", "uz": "Roʻyxat",
        "ro": "Listă", "az": "Siyahı", "ml": "പട്ടിക", "sd": "فهرست",
        "ig": "Ndepụta", "hu": "Lista", "el": "Λίστα", "cs": "Seznam",
        "nl": "Lijst", "sv": "Lista", "fi": "Luettelo", "no": "Liste"
    },
    "all": {
        "zh": "全部", "zh-hans": "全部", "zh-hant": "全部", "en": "All",
        "hi": "सभी", "es": "Todo", "fr": "Tout", "ar": "الكل",
        "bn": "সব", "pt": "Tudo", "ru": "Все", "ur": "تمام",
        "id": "Semua", "de": "Alle", "ja": "すべて", "mr": "सर्व",
        "te": "అన్నీ", "tr": "Tümü", "ta": "அனைத்தும்", "vi": "Tất cả",
        "tl": "Lahat", "ko": "전체", "fa": "همه", "ha": "Duka",
        "sw": "Yote", "jv": "Kabeh", "it": "Tutto", "pa": "ਸਭ",
        "kn": "ಎಲ್ಲಾ", "gu": "બધું", "th": "ทั้งหมด", "am": "ሁሉም",
        "yo": "Gbogbo", "my": "အားလုံး", "om": "Hunda", "ps": "ټول",
        "uk": "Усі", "su": "Sadaya", "pl": "Wszystko", "uz": "Barchasi",
        "ro": "Toate", "az": "Hamısı", "ml": "എല്ലാം", "sd": "سڀ",
        "ig": "Ha niile", "hu": "Mind", "el": "Όλα", "cs": "Vše",
        "nl": "Alles", "sv": "Alla", "fi": "Kaikki", "no": "Alle"
    },
    "read_more": {
        "zh": "阅读全文 →", "zh-hans": "阅读全文 →", "zh-hant": "閱讀全文 →", "en": "Read More →",
        "hi": "आगे पढ़ें →", "es": "Leer más →", "fr": "Lire la suite →", "ar": "اقرأ المزيد ←",
        "bn": "আরও পড়ুন →", "pt": "Ler mais →", "ru": "Читать далее →", "ur": "مزید پڑھیں ←",
        "id": "Baca selengkapnya →", "de": "Weiterlesen →", "ja": "続きを読む →", "mr": "अधिक वाचा →",
        "te": "మరింత చదవండి →", "tr": "Devamını Oku →", "ta": "மேலும் வாசிக்க →", "vi": "Đọc thêm →",
        "tl": "Magbasa Pa →", "ko": "자세히 보기 →", "fa": "ادامه مطلب ←", "ha": "Kara karantawa →",
        "sw": "Soma zaidi →", "jv": "Waca liyane →", "it": "Leggi di più →", "pa": "ਹੋਰ ਪੜ੍ਹੋ →",
        "kn": "ಇನ್ನಷ್ಟು ಓದಿ →", "gu": "વધુ વાંચો →", "th": "อ่านต่อ →", "am": "ተጨማሪ ያንብቡ →",
        "yo": "Ka siwaju →", "my": "ပိုမိုဖတ်ရှုရန် →", "om": "Dabalata dubbisaa →", "ps": "نور ولولئ ←",
        "uk": "Читати далі →", "su": "Maca deui →", "pl": "Czytaj dalej →", "uz": "Batafsil oʻqish →",
        "ro": "Citește mai mult →", "az": "Daha çox oxu →", "ml": "കൂടുതൽ വായിക്കുക →", "sd": "وڌيڪ پڙهو ←",
        "ig": "Gụkwuo →", "hu": "Tovább →", "el": "Διαβάστε περισσότερα →", "cs": "Číst dál →",
        "nl": "Lees meer →", "sv": "Läs mer →", "fi": "Lue lisää →", "no": "Les mer →"
    },
    "blog_hero_title": {
        "zh": "✍️ 博文存档与前沿洞察", "zh-hans": "✍️ 博文存档与前沿洞察", "zh-hant": "✍️ 部落格存檔與前沿洞察",
        "en": "✍️ Blog Archive & Insights", "ja": "✍️ ブログアーカイブ", "ko": "✍️ 블로그 아카이브",
        "fr": "✍️ Archives du Blog & Perspectives", "de": "✍️ Blog-Archiv & Einblicke",
        "es": "✍️ Archivo del Blog y Perspectivas", "ru": "✍️ Архив блога и аналитика",
        "ar": "✍️ أرشيف المدونة والرؤى", "pt": "✍️ Arquivo do Blog e Ideias", "it": "✍️ Archivio Blog e Approfondimenti"
    },
    "blog_hero_desc": {
        "zh": "探索技术洞察、出版手记与前沿数字工程。从段落级缓存架构到 AI 原生出版哲学。",
        "zh-hans": "探索技术洞察、出版手记与前沿数字工程。从段落级缓存架构到 AI 原生出版哲学。",
        "zh-hant": "探索技術洞察、出版手記與前沿數位工程。從段落級快取架構到 AI 原生出版哲學。",
        "en": "Explore technical insights, publishing notes, and digital sovereignty engineering.",
        "ja": "技術的洞察、出版ノート、デジタル主権エンジニアリングを探求します。",
        "ko": "기술적 통찰력, 출판 노트, 디지털 주권 엔지니어링을 탐구합니다.",
        "fr": "Explorez les perspectives techniques, notes d'édition et ingénierie souveraine.",
        "de": "Erkunden Sie technische Einblicke, Verlagsnotizen und souveräne digitale Entwicklung.",
        "es": "Explora perspectivas técnicas, notas de publicación e ingeniería soberana.",
        "ru": "Исследуйте технические инсайты, издательские заметки и цифровую суверенную инженерию."
    }
}


def get_i18n_view_label(key: str, lang: str = "zh", default: str = "") -> str:
    """🌐 通用国际化组件词汇解析器：支持 50 语种精确匹配与智能降级"""
    if key not in VIEW_I18N_MATRIX:
        return default or key

    matrix = VIEW_I18N_MATRIX[key]
    clean_lang = (lang or "zh").strip().lower().replace('_', '-')
    if clean_lang in ("auto", "", "none"):
        clean_lang = "zh"

    # 1. 精确匹配 (如 zh-hans, zh-hant, pt-br)
    if clean_lang in matrix:
        return matrix[clean_lang]

    # 2. 语族前缀匹配 (如 zh-cn -> zh, en-us -> en, fr-ca -> fr)
    prefix = clean_lang.split('-')[0]
    if prefix in matrix:
        return matrix[prefix]

    # 3. 中文别名自愈
    if prefix == "zh":
        is_hant = any(x in clean_lang for x in ('hant', 'tw', 'hk', 'mo'))
        hant_key = "zh-hant" if "zh-hant" in matrix else "zh"
        hans_key = "zh-hans" if "zh-hans" in matrix else "zh"
        return matrix.get(hant_key if is_hant else hans_key, matrix.get("zh", default))

    # 4. 英文回退
    if "en" in matrix:
        return matrix["en"]

    # 5. 默认回退
    return default or (list(matrix.values())[0] if matrix else key)
