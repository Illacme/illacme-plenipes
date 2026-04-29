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
    def __init__(self, meta_manager, translator_factory, lang_mapping=None, default_lang=None, active_theme=None, ssg_adapter=None):
        self.meta = meta_manager
        self.translator = translator_factory
        self.lang_mapping = lang_mapping or {}
        self.default_lang = default_lang
        self.active_theme = (active_theme or "starlight").lower()
        self.ssg_adapter = ssg_adapter

    def resolve_physical_path(self, base_path, lang_code, route_prefix, mapped_sub_dir, slug, ext, source_type="docs"):
        """
        🚀 终极路径对齐探针：
        支持声明式渲染模板 (Docusaurus/Astro) 与 传统层级渲染 (Starlight)。
        """
        logical_lang = str(lang_code or "").strip("/\\").lower()
        mapped_sub_dir = str(mapped_sub_dir or "").strip("/\\")
        slug = str(slug or "")
        route_prefix = str(route_prefix or "")

        # 🚀 [V7.12] 零配置路径对齐：如果未指定 prefix，则从适配器获取当前框架的标准模版
        if not route_prefix and self.ssg_adapter:
            route_prefix = self.ssg_adapter.get_i18n_path_template(source_type) or ""

        # 🚀 [V15.7] 物理主权对齐：默认语种直接霸占根目录 (Docusaurus/Industrial Style)
        from core.utils.language_hub import LanguageHub
        iso_logical = LanguageHub.resolve_to_iso(logical_lang)
        iso_default = LanguageHub.resolve_to_iso(self.default_lang)

        # 🚀 [V11.1] 路径隔离加固：只有非默认语种才需要物理语言前缀
        if iso_logical == iso_default:
            physical_lang = ""
        else:
            physical_lang = LanguageHub.get_physical_path(iso_logical, self.active_theme)

        if route_prefix and "{" in route_prefix and "}" in route_prefix:
            # 模式 A：声明式模板模式 (Docusaurus i18n 规范)
            try:
                # 🚀 [V11.1] 模板变量保护：确保 lang, slug, sub_dir 均非 None
                formatted_prefix = route_prefix.format(
                    lang=physical_lang or "",
                    slug=slug or "",
                    sub_dir=mapped_sub_dir or ""
                )
            except Exception:
                formatted_prefix = route_prefix
            # 物理路径组装：base_path / formatted_prefix / slug.ext
            raw_path = os.path.join(base_path, formatted_prefix.strip("/"), f"{slug}{ext}")
        else:
            # 模式 B：标准阶梯模式 (向下兼容 Starlight/Nextra)
            # 结构：base_path / physical_lang / route_prefix / mapped_sub_dir / slug.ext
            parts = [p for p in [base_path, physical_lang, route_prefix, mapped_sub_dir, f"{slug}{ext}"] if p]
            raw_path = os.path.join(*parts) if parts else ""

        return os.path.normpath(re.sub(r'[/\\]+', os.sep, raw_path))

    def get_mapped_sub_dir(self, raw_sub_dir, is_dry_run=False, allow_ai=False):
        """
        🚀 目录结构状态机：将包含中文的源目录物理路径，极度安全地翻译并固化为纯英文 URL 路径。
        一旦确立，终身不变，彻底解决跨平台部署时的中文 URL 编码雪崩灾难。
        """
        if not raw_sub_dir or raw_sub_dir == '.':
            return ""

        parts = raw_sub_dir.split('/')
        mapped_parts = []

        for p in parts:
            if not p: continue

            # 1. 尝试从内存账本读取极速映射
            d_slug = self.meta.get_dir_slug(p)

            # 2. 缓存击穿，触发全新目录创建流程
            if not d_slug:
                if allow_ai and not is_dry_run:
                    tlog.info(f"   └── ⏳ 探测到全新中文目录 '{p}'，正调度 AI 为其生成永久英文 URL 路由...")
                    # 🚀 [V11.1] 提示词去噪：不再发送 "Directory Name: " 前缀，防止 AI 误解意图产生冗余 Slug
                    d_slug, _ = self.translator.generate_slug(p, is_dry_run)

                # 3. 终极无缝兜底：彻底脱离 AI 和网络环境的防撞设计
                if not d_slug:
                    safe_p = re.sub(r'[^\w\-]', '', p.replace(' ', '-')).lower()
                    safe_p = re.sub(r'-+', '-', safe_p).strip('-')
                    if not safe_p:
                        safe_p = f"dir-{hashlib.md5(p.encode('utf-8')).hexdigest()[:6]}"
                    d_slug = safe_p

                # 4. 固化账本
                if not is_dry_run:
                    self.meta.register_dir_slug(p, d_slug)

            mapped_parts.append(d_slug)

        return '/'.join(mapped_parts)

    def resolve_logical_url(self, lang_code, route_prefix, mapped_sub_dir, slug):
        """
        🚀 逻辑 URL 构造器：将各组件组装为最终浏览器可跳转的 URL 路径。
        逻辑流程：语种标识 -> 路由前缀（带模板解析） -> 映射文件夹 -> Slug
        """
        logical_lang = str(lang_code or "").strip("/\\").lower()
        mapped_sub_dir = str(mapped_sub_dir or "").strip("/\\")
        slug = str(slug or "")
        route_prefix = str(route_prefix or "")

        # 🚀 [V7.6] 智能语种物理化
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logical_lang)
        physical_lang = LanguageHub.get_physical_path(iso_code, self.active_theme)

        # 阶段 1：解析路由前缀
        if "{" in route_prefix and "}" in route_prefix:
            # 模式 A：模板解析 (如 /docs/{lang})
            try:
                prefix_processed = route_prefix.format(
                    lang=physical_lang,
                    slug=slug,
                    sub_dir=mapped_sub_dir
                ).strip("/")
            except Exception:
                prefix_processed = route_prefix.strip("/")
        else:
            # 模式 B：透传
            prefix_processed = route_prefix.strip("/")

        # 阶段 2：安全组装
        # 🚀 [V15.7] 物理主权对齐：默认语种 URL 不带前缀
        url_lang = "" if logical_lang == self.default_lang else logical_lang
        parts = [p for p in [url_lang, prefix_processed, mapped_sub_dir, slug] if p]
        raw_url = "/" + "/".join(parts)

        # 阶段 3：物理脱敏
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
