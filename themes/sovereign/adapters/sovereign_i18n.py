# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Multi-Language Internationalization
模块职责：主权原生主题全息多语言 UI 字典与跨语种对齐引擎。
"""

from typing import Dict
from core.utils.language_data import SUPPORTED_MATRIX

SOVEREIGN_UI_I18N: Dict[str, Dict[str, str]] = {
    "zh": {
        "nav_home": "首页", "nav_docs": "文档", "nav_blog": "博客", "nav_showcase": "案例", "nav_about": "关于",
        "search_placeholder": "搜索主权资产...", "search_no_results": "未发现相关文档...",
        "toc_title": "目录导航", "footer_motto": "物理主权数字花园", "footer_slogan": "物理主权，自洽生长。",
        "reading_time": "预计阅读", "min_read": "分钟", "word_count": "字数", "published_on": "发布于",
        "author": "作者", "tags": "标签", "prev_doc": "上一篇", "next_doc": "下一篇",
        "back_to_blog": "返回博客列表", "back_to_docs": "返回文档中心", "copy_code": "复制", "code_copied": "已复制!",
        "page_not_found": "404 - 页面未找到", "page_not_found_desc": "抱歉，您访问的页面不存在或已被迁移。",
        "back_home": "返回首页", "explore_docs": "探索文档", "read_blog": "阅读博客", "get_started": "立即启程"
    },
    "zh-Hans": {
        "nav_home": "首页", "nav_docs": "文档", "nav_blog": "博客", "nav_showcase": "案例", "nav_about": "关于",
        "search_placeholder": "搜索主权资产...", "search_no_results": "未发现相关文档...",
        "toc_title": "目录导航", "footer_motto": "物理主权数字花园", "footer_slogan": "物理主权，自洽生长。",
        "reading_time": "预计阅读", "min_read": "分钟", "word_count": "字数", "published_on": "发布于",
        "author": "作者", "tags": "标签", "prev_doc": "上一篇", "next_doc": "下一篇",
        "back_to_blog": "返回博客列表", "back_to_docs": "返回文档中心", "copy_code": "复制", "code_copied": "已复制!",
        "page_not_found": "404 - 页面未找到", "page_not_found_desc": "抱歉，您访问的页面不存在或已被迁移。",
        "back_home": "返回首页", "explore_docs": "探索文档", "read_blog": "阅读博客", "get_started": "立即启程"
    },
    "zh-Hant": {
        "nav_home": "首頁", "nav_docs": "文檔", "nav_blog": "部落格", "nav_showcase": "案例", "nav_about": "關於",
        "search_placeholder": "搜尋主權資產...", "search_no_results": "未發現相關文檔...",
        "toc_title": "目錄導航", "footer_motto": "物理主權數位花園", "footer_slogan": "物理主權，自洽生長。",
        "reading_time": "預計閱讀", "min_read": "分鐘", "word_count": "字數", "published_on": "發布於",
        "author": "作者", "tags": "標籤", "prev_doc": "上一篇", "next_doc": "下一篇",
        "back_to_blog": "返回部落格列表", "back_to_docs": "返回文檔中心", "copy_code": "複製", "code_copied": "已複製!",
        "page_not_found": "404 - 頁面未找到", "page_not_found_desc": "抱歉，您訪問的頁面不存在或已被遷移。",
        "back_home": "返回首頁", "explore_docs": "探索文檔", "read_blog": "閱讀部落格", "get_started": "立即啟程"
    },
    "en": {
        "nav_home": "Home", "nav_docs": "Docs", "nav_blog": "Blog", "nav_showcase": "Showcase", "nav_about": "About",
        "search_placeholder": "Search assets...", "search_no_results": "No matching documents found...",
        "toc_title": "Table of Contents", "footer_motto": "Physical Sovereignty Digital Garden", "footer_slogan": "Physical Sovereignty, Self-Consistent Growth.",
        "reading_time": "Read Time", "min_read": "min read", "word_count": "words", "published_on": "Published on",
        "author": "Author", "tags": "Tags", "prev_doc": "Previous", "next_doc": "Next",
        "back_to_blog": "Back to Blog", "back_to_docs": "Back to Docs", "copy_code": "Copy", "code_copied": "Copied!",
        "page_not_found": "404 - Page Not Found", "page_not_found_desc": "The page you are looking for does not exist or has been moved.",
        "back_home": "Back to Home", "explore_docs": "Explore Docs", "read_blog": "Read Blog", "get_started": "Get Started"
    },
    "ja": {
        "nav_home": "ホーム", "nav_docs": "ドキュメント", "nav_blog": "ブログ", "nav_showcase": "ショーケース", "nav_about": "アバウト",
        "search_placeholder": "資産を検索...", "search_no_results": "関連ドキュメントが見つかりません...",
        "toc_title": "目次", "footer_motto": "物理的主権デジタルガーデン", "footer_slogan": "物理的主権、自己完結型の成長。",
        "reading_time": "読了時間", "min_read": "分", "word_count": "文字数", "published_on": "公開日",
        "author": "著者", "tags": "タグ", "prev_doc": "前の記事", "next_doc": "次の記事",
        "back_to_blog": "ブログ一覧へ", "back_to_docs": "ドキュメント一覧へ", "copy_code": "コピー", "code_copied": "コピー完了!",
        "page_not_found": "404 - ページが見つかりません", "page_not_found_desc": "お探しのページは存在しないか移動されました。",
        "back_home": "ホームに戻る", "explore_docs": "ドキュメントを見る", "read_blog": "ブログを読む", "get_started": "今すぐ開始"
    },
    "ko": {
        "nav_home": "홈", "nav_docs": "문서", "nav_blog": "블로그", "nav_showcase": "쇼케이스", "nav_about": "소개",
        "search_placeholder": "자산 검색...", "search_no_results": "관련 문서를 찾을 수 없습니다...",
        "toc_title": "목차", "footer_motto": "물리적 주권 디지털 가든", "footer_slogan": "물리적 주권, 자가 완결적 성장.",
        "reading_time": "소요 시간", "min_read": "분", "word_count": "단어 수", "published_on": "게시일",
        "author": "작성자", "tags": "태그", "prev_doc": "이전 글", "next_doc": "다음 글",
        "back_to_blog": "블로그 목록으로", "back_to_docs": "문서 목록으로", "copy_code": "복사", "code_copied": "복사됨!",
        "page_not_found": "404 - 페이지를 찾을 수 없습니다", "page_not_found_desc": "요청하신 페이지가 존재하지 않거나 이동되었습니다.",
        "back_home": "홈으로 돌아가기", "explore_docs": "문서 탐색", "read_blog": "블로그 읽기", "get_started": "시작하기"
    },
    "fr": {
        "nav_home": "Accueil", "nav_docs": "Documentation", "nav_blog": "Blog", "nav_showcase": "Vitrine", "nav_about": "À propos",
        "search_placeholder": "Rechercher...", "search_no_results": "Aucun document trouvé...",
        "toc_title": "Table des matières", "footer_motto": "Jardin numérique souverain", "footer_slogan": "Souveraineté physique, croissance cohérente.",
        "reading_time": "Temps de lecture", "min_read": "min de lecture", "word_count": "mots", "published_on": "Publié le",
        "author": "Auteur", "tags": "Étiquettes", "prev_doc": "Précédent", "next_doc": "Suivant",
        "back_to_blog": "Retour au Blog", "back_to_docs": "Retour aux Docs", "copy_code": "Copier", "code_copied": "Copié !",
        "page_not_found": "404 - Page non trouvée", "page_not_found_desc": "La page que vous recherchez n'existe pas ou a été déplacée.",
        "back_home": "Retour à l'accueil", "explore_docs": "Explorer la documentation", "read_blog": "Lire le Blog", "get_started": "Commencer"
    },
    "de": {
        "nav_home": "Startseite", "nav_docs": "Dokumentation", "nav_blog": "Blog", "nav_showcase": "Galerie", "nav_about": "Über uns",
        "search_placeholder": "Suchen...", "search_no_results": "Keine Dokumente gefunden...",
        "toc_title": "Inhaltsverzeichnis", "footer_motto": "Souveräner digitaler Garten", "footer_slogan": "Physische Souveränität, kohärentes Wachstum.",
        "reading_time": "Lesezeit", "min_read": "Min. Lesezeit", "word_count": "Wörter", "published_on": "Veröffentlicht am",
        "author": "Autor", "tags": "Tags", "prev_doc": "Vorheriger", "next_doc": "Nächster",
        "back_to_blog": "Zurück zum Blog", "back_to_docs": "Zurück zur Doku", "copy_code": "Kopieren", "code_copied": "Kopiert!",
        "page_not_found": "404 - Seite nicht gefunden", "page_not_found_desc": "Die gesuchte Seite existiert nicht oder wurde verschoben.",
        "back_home": "Zur Startseite", "explore_docs": "Doku erkunden", "read_blog": "Blog lesen", "get_started": "Jetzt starten"
    },
    "es": {
        "nav_home": "Inicio", "nav_docs": "Documentación", "nav_blog": "Blog", "nav_showcase": "Portafolio", "nav_about": "Acerca de",
        "search_placeholder": "Buscar...", "search_no_results": "No se encontraron documentos...",
        "toc_title": "Tabla de contenidos", "footer_motto": "Jardín digital soberano", "footer_slogan": "Soberanía física, crecimiento coherente.",
        "reading_time": "Tiempo de lectura", "min_read": "min de lectura", "word_count": "palabras", "published_on": "Publicado el",
        "author": "Autor", "tags": "Etiquetas", "prev_doc": "Anterior", "next_doc": "Siguiente",
        "back_to_blog": "Volver al Blog", "back_to_docs": "Volver a Documentación", "copy_code": "Copiar", "code_copied": "¡Copiado!",
        "page_not_found": "404 - Página no encontrada", "page_not_found_desc": "La página que buscas no existe o ha sido movida.",
        "back_home": "Volver al Inicio", "explore_docs": "Explorar Docs", "read_blog": "Leer Blog", "get_started": "Comenzar"
    },
    "ru": {
        "nav_home": "Главная", "nav_docs": "Документация", "nav_blog": "Блог", "nav_showcase": "Витрина", "nav_about": "О нас",
        "search_placeholder": "Поиск по активам...", "search_no_results": "Документы не найдены...",
        "toc_title": "Содержание", "footer_motto": "Суверенный цифровой сад", "footer_slogan": "Физический суверенитет, самосогласованный рост.",
        "reading_time": "Время чтения", "min_read": "мин чтения", "word_count": "слов", "published_on": "Опубликовано",
        "author": "Автор", "tags": "Теги", "prev_doc": "Предыдущая", "next_doc": "Следующая",
        "back_to_blog": "Назад в блог", "back_to_docs": "Назад к документам", "copy_code": "Копировать", "code_copied": "Скопировано!",
        "page_not_found": "404 - Страница не найдена", "page_not_found_desc": "Запрашиваемая страница не существует или была перемещена.",
        "back_home": "На главную", "explore_docs": "Обзор документации", "read_blog": "Читать блог", "get_started": "Начать"
    }
}


def get_ui_i18n(lang: str) -> Dict[str, str]:
    """获取指定语言的 UI 本地化字典，默认降级至英语"""
    clean_lang = lang.strip().lower() if lang else "zh"
    if clean_lang in SOVEREIGN_UI_I18N:
        return SOVEREIGN_UI_I18N[clean_lang]
    # 针对 zh-cn, zh-tw 等别名进行适配
    if clean_lang.startswith("zh"):
        return SOVEREIGN_UI_I18N["zh-Hans"] if "hant" not in clean_lang and "tw" not in clean_lang and "hk" not in clean_lang else SOVEREIGN_UI_I18N["zh-Hant"]
    return SOVEREIGN_UI_I18N.get(clean_lang, SOVEREIGN_UI_I18N["en"])


def get_language_display_names() -> Dict[str, str]:
    """获取所有支持语种的友好显示名称与国旗图标"""
    lang_names = {
        "zh": "🇨🇳 简体中文", "zh-Hans": "🇨🇳 简体中文", "zh-Hant": "🇹🇼 繁體中文",
        "en": "🇬🇧 English", "ja": "🇯🇵 日本語", "ko": "🇰🇷 한국어",
        "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch", "es": "🇪🇸 Español",
        "ru": "🇷🇺 Русский", "pt": "🇵🇹 Português", "it": "🇮🇹 Italiano",
        "ar": "🇸🇦 العربية", "auto": "🇨🇳 简体中文"
    }
    for entry in SUPPORTED_MATRIX:
        code = entry.get("code", "")
        if code and code not in lang_names:
            lang_names[code] = f'{entry.get("icon", "🌐")} {entry.get("name", code)}'
    return lang_names
