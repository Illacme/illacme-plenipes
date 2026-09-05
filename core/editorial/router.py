#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Router Engine
模块职责：全域路由分配与目录寻址机。接管中英文目录的状态机映射与 URL 安全转化，统一物理防裂探针。
架构原则：贯彻依赖注入 (DI)，彻底解耦底层账本与翻译中枢。
"""

import os
import re
import hashlib
import logging

from core.utils.tracing import tlog

class RouteManager:
    """
    🚀 独立路由寻址中心
    通过挂载状态机账本与 AI 翻译工厂，专职负责物理路径到安全前端 URL 路由的映射，
    以及全局统一的物理路径推导，彻底消灭探针与写盘器的脑裂问题。
    """
    def __init__(self, meta_manager, translator_factory, lang_mapping=None, default_lang=None, active_theme=None, ssg_adapter=None, force_source_prefix=False, config=None, engine=None):
        self.meta = meta_manager
        self.translator = translator_factory
        self.lang_mapping = lang_mapping or {}
        self.default_lang = default_lang
        self.active_theme = (active_theme or "starlight").lower()
        self.ssg_adapter = ssg_adapter
        self.force_source_prefix = force_source_prefix
        self.config = config
        self.engine = engine


    def resolve_physical_path(self, base_path, lang_code, route_prefix, mapped_sub_dir, slug, ext, source_type="docs"):
        """
        🚀 终极路径对齐探针：
        支持声明式渲染模板 (Docusaurus/Astro) 与 传统层级渲染 (Starlight)。
        """
        logical_lang = str(lang_code or "").strip("/\\").lower()
        mapped_sub_dir = str(mapped_sub_dir or "").strip("/\\")
        slug = str(slug or "")
        route_prefix = str(route_prefix or "")

        # 🚀 [V56.0] 意图感知寻址：优先使用 SSG 适配器声明的功能槽路径
        slot_formatted = False
        if self.ssg_adapter:
            slots = self.ssg_adapter.get_feature_slots()
            if source_type in slots:
                slot_cfg = slots[source_type]
                # 判定是使用单语模版还是多语模版
                from core.utils.language_hub import LanguageHub
                iso_logical = LanguageHub.resolve_to_iso(logical_lang)
                iso_default = LanguageHub.resolve_to_iso(self.default_lang)
                
                # 获取模版（如果开启了主语言前缀强制化，即使是主语言也需要走多语/带前缀模板）
                is_multi = (iso_logical != iso_default) or self.force_source_prefix
                template = slot_cfg.get("multi" if is_multi else "single")
                
                if template is not None:
                    # 解析物理语种前缀
                    physical_lang = LanguageHub.get_physical_path(
                        iso_logical,
                        theme=self.active_theme,
                        source_lang=self.default_lang,
                        force_prefix=self.force_source_prefix
                    )
                    try:
                        route_prefix = template.format(lang=physical_lang)
                    except Exception:
                        route_prefix = template.replace("{lang}", physical_lang)
                    slot_formatted = True

        # 🚀 [V105.0] 网址组织形态策略推导 (nested: 目录树复刻; flat: 极简根目录; prefix: 智能 SEO 前缀)
        cfg = getattr(self, 'config', None) or getattr(getattr(self, 'engine', None), 'config', None)
        trans_cfg = getattr(cfg, 'translation', None) if cfg else None
        dir_mode = getattr(trans_cfg, 'slug_dir_mode', 'nested') if trans_cfg else 'nested'

        # 🚀 Frontmatter 绝对路径主权: 以 / 开头直接输出至站点根目录
        if slug.startswith('/'):
            slug = slug.lstrip('/')
            route_prefix = ""
            mapped_sub_dir = ""
            dir_mode = 'flat'

        # 判定是否为全站主首页 vs 频道子首页
        is_global_home = (slug in ('', 'index', 'home') and not mapped_sub_dir and source_type not in ('docs', 'blog', 'showcase'))
        is_channel_home = (slug in ('', 'index', 'home') and not is_global_home)

        if dir_mode == 'flat':
            if is_global_home:
                # 全站主首页豁免权：必须固定输出为根目录 index.html
                route_prefix = ""
                mapped_sub_dir = ""
                slug = "index"
            elif is_channel_home:
                # 频道子首页语义收敛：避免与全站 index.html 碰撞覆盖
                channel_name = mapped_sub_dir or (source_type if source_type in ('docs', 'blog', 'showcase') else 'docs')
                slug = channel_name.strip('/\\').replace('/', '-')
                route_prefix = ""
                mapped_sub_dir = ""
            else:
                # 普通文档在 flat 模式下压平至根目录
                route_prefix = ""
                mapped_sub_dir = ""
        elif dir_mode == 'prefix':
            if is_global_home:
                route_prefix = ""
                mapped_sub_dir = ""
                slug = "index"
            elif is_channel_home:
                channel_name = mapped_sub_dir or (source_type if source_type in ('docs', 'blog', 'showcase') else 'docs')
                clean_channel = channel_name.strip('/\\').replace('/', '-')
                slug = f"{clean_channel}-index"
                route_prefix = ""
                mapped_sub_dir = ""
            else:
                channel_name = mapped_sub_dir or (route_prefix if route_prefix in ('docs', 'blog', 'showcase') else '')
                if channel_name and not slug.startswith(f"{channel_name}-"):
                    clean_channel = channel_name.strip('/\\').replace('/', '-')
                    slug = f"{clean_channel}-{slug}"
                route_prefix = ""
                mapped_sub_dir = ""
        else:
            # nested 模式：保持目录树复刻层级，但如果未指定 slot 且没有 mapped_sub_dir 时保持原有 route_prefix
            pass

        # 🚀 [V15.7] 物理主权对正：计算物理语种标识
        from core.utils.language_hub import LanguageHub
        iso_logical = LanguageHub.resolve_to_iso(logical_lang)
        iso_default = LanguageHub.resolve_to_iso(self.default_lang)
        
        # 🛡️ 智能对齐：如果为默认/原稿语言且未强制前缀，或者模板中已经包含了语种占位符，则物理语种前缀置空
        if (iso_logical == iso_default and not self.force_source_prefix) or (slot_formatted and dir_mode == 'nested'):
            physical_lang = ""
        else:
            physical_lang = LanguageHub.get_physical_path(
                iso_logical,
                theme=self.active_theme,
                source_lang=self.default_lang,
                force_prefix=self.force_source_prefix
            )

        # 🛡️ 路径去重防线与套娃拦截网：
        # 1. 避免 mapped_sub_dir 与 route_prefix 出现同名频道路由重叠 (如 /zh/docs/docs/...)
        if mapped_sub_dir:
            sub_clean = mapped_sub_dir.strip("/\\")
            prefix_parts = [p for p in route_prefix.replace('\\', '/').split('/') if p]
            if sub_clean in prefix_parts:
                mapped_sub_dir = ""

        # 2. 避免 base_path 末级与 route_prefix 首级相同引发双重目录套娃 (如 content/content/...)
        base_norm = base_path.replace('\\', '/').rstrip('/')
        base_last = os.path.basename(base_norm) if base_norm else ""
        prefix_parts = [p for p in route_prefix.replace('\\', '/').split('/') if p]
        if prefix_parts and base_last and prefix_parts[0] == base_last:
            prefix_parts.pop(0)
            route_prefix = '/'.join(prefix_parts)

        if route_prefix and "{" in route_prefix and "}" in route_prefix and dir_mode == 'nested':
            # 模式 A：声明式模板模式 (如 /docs/{lang})
            try:
                formatted_prefix = route_prefix.format(
                    lang=physical_lang or "",
                    slug=slug or "",
                    sub_dir=mapped_sub_dir or ""
                )
            except Exception:
                formatted_prefix = route_prefix
            raw_path = os.path.join(base_path, formatted_prefix.strip("/"), f"{slug}{ext}")
        else:
            # 模式 B：标准阶梯模式 (base / lang / prefix / sub / slug)
            parts = [p for p in [base_path, physical_lang, route_prefix, mapped_sub_dir, f"{slug}{ext}"] if p]
            raw_path = os.path.join(*parts) if parts else ""

        return os.path.normpath(re.sub(r'[/\\]+', os.sep, raw_path))

    def get_mapped_sub_dir(self, raw_sub_dir, is_dry_run=False, allow_ai=False):
        """
        🚀 目录结构状态机：将源目录物理路径安全映射为纯英文 URL 路径。
        """
        if not raw_sub_dir or raw_sub_dir == '.':
            return ""

        parts = raw_sub_dir.split('/')
        mapped_parts = []

        for p in parts:
            if not p: continue
            d_slug = self.meta.get_dir_slug(p)
            if not d_slug:
                if allow_ai and not is_dry_run and self.translator:
                    try:
                        d_slug, _ = self.translator.generate_slug(p, is_dry_run)
                    except Exception as e:
                        tlog.warning(f"⚠️ [路由 AI 故障] {e}，将回退至物理清洗。")
                        d_slug = None

                if not d_slug:
                    safe_p = re.sub(r'[^\w\-]', '', p.replace(' ', '-')).lower()
                    safe_p = re.sub(r'-+', '-', safe_p).strip('-')
                    if not safe_p:
                        safe_p = f"dir-{hashlib.md5(p.encode('utf-8')).hexdigest()[:6]}"
                    d_slug = safe_p

                if not is_dry_run:
                    self.meta.register_dir_slug(p, d_slug)

            mapped_parts.append(d_slug)

        return '/'.join(mapped_parts)

    def resolve_logical_url(self, lang_code: str, route_prefix: str, mapped_sub_dir: str, slug: str) -> str:
        """
        🚀 逻辑 URL 构造器：将各组件组装为最终浏览器可跳转的 URL 路径。
        """
        logical_lang = str(lang_code or "").strip("/\\").lower()
        mapped_sub_dir = str(mapped_sub_dir or "").strip("/\\")
        slug = str(slug or "")
        route_prefix = str(route_prefix or "")

        # 🚀 [V105.0] 网址组织形态策略推导
        cfg = getattr(self, 'config', None) or getattr(getattr(self, 'engine', None), 'config', None)
        trans_cfg = getattr(cfg, 'translation', None) if cfg else None
        dir_mode = getattr(trans_cfg, 'slug_dir_mode', 'nested') if trans_cfg else 'nested'

        if slug.startswith('/'):
            slug = slug.lstrip('/')
            route_prefix = ""
            mapped_sub_dir = ""
            dir_mode = 'flat'

        is_global_home = (slug in ('', 'index', 'home') and not mapped_sub_dir and route_prefix not in ('docs', 'blog', 'showcase'))
        is_channel_home = (slug in ('', 'index', 'home') and not is_global_home)

        if dir_mode == 'flat':
            if is_global_home:
                route_prefix, mapped_sub_dir, slug = "", "", "index"
            elif is_channel_home:
                channel_name = mapped_sub_dir or (route_prefix if route_prefix in ('docs', 'blog', 'showcase') else 'docs')
                slug = channel_name.strip('/\\').replace('/', '-')
                route_prefix, mapped_sub_dir = "", ""
            else:
                route_prefix, mapped_sub_dir = "", ""
        elif dir_mode == 'prefix':
            if is_global_home:
                route_prefix, mapped_sub_dir, slug = "", "", "index"
            elif is_channel_home:
                channel_name = mapped_sub_dir or (route_prefix if route_prefix in ('docs', 'blog', 'showcase') else 'docs')
                clean_name = channel_name.strip('/\\').replace('/', '-')
                slug = f"{clean_name}-index"
                route_prefix, mapped_sub_dir = "", ""
            else:
                channel_name = mapped_sub_dir or (route_prefix if route_prefix in ('docs', 'blog', 'showcase') else '')
                if channel_name and not slug.startswith(f"{channel_name}-"):
                    clean_name = channel_name.strip('/\\').replace('/', '-')
                    slug = f"{clean_name}-{slug}"
                route_prefix, mapped_sub_dir = "", ""

        # 🚀 [V7.6] 智能语种物理化与单页同名折叠
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logical_lang)
        prefix_processed = route_prefix.strip("/")
        
        # 🛡️ 同名单页坍缩折叠：当 route_prefix 与 slug 同名且无子目录时折叠为单级 /slug，消灭 /about/about
        if prefix_processed == slug and not mapped_sub_dir:
            prefix_processed = ""

        def_iso = LanguageHub.resolve_to_iso(self.default_lang) if self.default_lang else "zh"
        if not def_iso or def_iso == "auto":
            def_iso = "zh"
        url_lang = "" if (iso_code == def_iso and not self.force_source_prefix) else iso_code
        parts = [p for p in [url_lang, prefix_processed, mapped_sub_dir, slug] if p]
        raw_url = "/" + "/".join(parts)
        return re.sub(r'/+', '/', raw_url)


    def predict_logical_url(self, target_lang, route_prefix, mapped_sub_dir, title):
        """
        🚀 虚拟路径预判器：在缺少实时账本数据时，基于一致性算法预估目标语种路径。
        用于解决同步时差导致的跨语种断链问题。
        """
        # 1. 尝试将标题转化为标准安全 Slug ( fallback 模式)
        safe_slug = re.sub(r'[^\w\-]', '', title.replace(' ', '-').lower())
        safe_slug = re.sub(r'-+', '-', safe_slug).strip('-')
        if not safe_slug:
            safe_slug = f"doc-{hashlib.md5(title.encode('utf-8')).hexdigest()[:6]}"

        # 2. 调用标准解析逻辑
        return self.resolve_logical_url(target_lang, route_prefix, mapped_sub_dir, safe_slug)
