# -*- coding: utf-8 -*-
"""
🎨 Sovereign 主题多语言切换器分片 (Language Switcher Shard)

物理职责：
- 负责收集系统激活有效语种，并动态生成多语言下拉切换菜单项。
- 严格遵循 SOP-02 架构演进规约与 SOP-01 核心工程标准，物理行数保持在 300 行以内。
"""

from typing import Dict, Any, Tuple
from .sovereign_i18n import get_language_display_names


def build_language_switcher(
    adapter,
    effective_lang: str,
    default_code: str,
    fm: Dict[str, Any],
    prefix: str,
    sub_dir: str,
    slug: str,
    layout_type: str,
    root_path: str,
    sv_dir_mode: str
) -> Tuple[str, str]:
    """🌐 动态语种切换器构建 (仅展示当前治理中心配置的活跃语种)"""
    lang_names = get_language_display_names()
    switcher_items = []
    hreflangs = {item.get('lang'): item.get('url', '') for item in fm.get('hreflangs', []) if isinstance(item, dict)}

    # 收集系统激活的有效语种
    active_langs = set()
    if hreflangs:
        for h_l in hreflangs.keys():
            active_langs.add(default_code if h_l == "auto" else h_l)
    if adapter.engine and hasattr(adapter.engine, 'i18n') and adapter.engine.i18n:
        if getattr(adapter.engine.i18n, 'source', None):
            src_c = adapter.engine.i18n.source.lang_code
            active_langs.add(default_code if src_c == "auto" else src_c)
        if getattr(adapter.engine.i18n, 'targets', None):
            for t_item in adapter.engine.i18n.targets:
                if getattr(t_item, 'lang_code', None):
                    active_langs.add(t_item.lang_code)
    if not active_langs:
        active_langs = {default_code, 'en', effective_lang}

    active_langs.discard("auto")
    active_langs.add(default_code)

    # 按照默认语言在前、目标语言在后的顺序排序
    sorted_active_langs = sorted(list(active_langs), key=lambda c: (0 if c == default_code else 1, c))
    current_lang_name = lang_names.get(effective_lang, effective_lang.upper())

    for l_code in sorted_active_langs:
        l_name = lang_names.get(l_code, f"🌐 {l_code}")
        is_active = (l_code == effective_lang)
        active_cls = " active" if is_active else ""
        active_check = '<span class="lang-check">✓</span>' if is_active else ""
        if l_code in hreflangs and hreflangs[l_code]:
            target_url = hreflangs[l_code].lstrip('/')
            # 🛡️ 清洗 hreflangs 中可能残留的 page/ 虚假段
            if target_url.startswith("page/"):
                target_url = target_url[len("page/"):]
            elif "/page/" in target_url:
                target_url = target_url.replace('/page/', '/')
            if l_code == default_code and not getattr(adapter, 'force_source_prefix', False):
                # 🛡️ 默认语言根目录对齐：剥离错误的 zh/ 等前缀
                if target_url.startswith(f"{default_code}/"):
                    target_url = target_url[len(f"{default_code}/"):]
            if not target_url.endswith('.html'):
                target_url += '.html'
            full_dest = f"{root_path}{target_url}".replace('//', '/')
        elif l_code == default_code and "auto" in hreflangs and hreflangs["auto"]:
            target_url = hreflangs["auto"].lstrip('/')
            if target_url.startswith("page/"):
                target_url = target_url[len("page/"):]
            elif "/page/" in target_url:
                target_url = target_url.replace('/page/', '/')
            if not getattr(adapter, 'force_source_prefix', False):
                if target_url.startswith(f"{default_code}/"):
                    target_url = target_url[len(f"{default_code}/"):]
            if not target_url.endswith('.html'):
                target_url += '.html'
            full_dest = f"{root_path}{target_url}".replace('//', '/')
        else:
            # 智能计算对等相对路径
            clean_p = (prefix or "").strip("/\\").lower()
            sub_segment = f"{sub_dir}/" if sub_dir else ""
            is_global_h = (slug in ("index", "home", "") and not clean_p and not sub_segment and layout_type not in ('docs', 'blog', 'showcase'))
            is_channel_h = (slug in ("index", "home", "") and not is_global_h)
            channel_n = clean_p or (layout_type if layout_type in ('docs', 'blog', 'showcase') else 'docs')

            lang_seg = f"{l_code}/" if l_code != default_code else ""
            if is_global_h:
                dest = f"{lang_seg}index.html"
            elif is_channel_h:
                if sv_dir_mode == 'flat':
                    dest = f"{lang_seg}{channel_n}.html"
                elif sv_dir_mode == 'prefix':
                    dest = f"{lang_seg}{channel_n}-index.html"
                else:
                    dest = f"{lang_seg}{channel_n}/index.html"
            elif slug:
                if sv_dir_mode == 'flat':
                    dest = f"{lang_seg}{slug}.html"
                elif sv_dir_mode == 'prefix':
                    _p_slug = slug if slug.startswith(f"{channel_n}-") else f"{channel_n}-{slug}"
                    dest = f"{lang_seg}{_p_slug}.html"
                else:
                    dest = f"{lang_seg}{clean_p}/{sub_segment}{slug}.html" if clean_p else f"{lang_seg}{sub_segment}{slug}.html"
            else:
                dest = f"{lang_seg}index.html"

            full_dest = f"{root_path}{dest}".replace('//', '/')

        switcher_items.append(f"""<a href="{full_dest}" class="lang-menu-item{active_cls}">
                <span class="lang-code-badge">{l_code.upper()}</span>
                <span class="lang-name-text">{l_name}</span>
                {active_check}
            </a>""")

    return current_lang_name, "\n".join(switcher_items)
