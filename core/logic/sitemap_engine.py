#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sitemap Engine
模块职责：全域站点地图导出引擎。支持多语种 Hreflang 矩阵与 RSS 订阅源生成。
🛡️ [AEL-Iter-V10.5]：实现物理发布侧的 SEO 主权对齐。
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from core.utils.tracing import tlog

class SitemapGenerator:
    def __init__(self, engine):
        self.engine = engine
        # 🚀 [V24.6] 防御性治理：确保 site_url 存在，否则回退至 localhost 以防逻辑崩溃
        raw_url = getattr(engine.config, 'site_url', 'http://localhost') or 'http://localhost'
        self.site_url = raw_url.rstrip('/')

    def generate(self, all_docs_snapshot=None):
        """🚀 生成全量 Sitemap"""
        tlog.info("🌐 [站点地图] 正在启动全域 SEO 矩阵扫描...")

        # 🚀 [V10.5] 物理注册命名空间，确保 ElementTree 自动处理前缀映射
        ET.register_namespace('', "http://www.sitemaps.org/schemas/sitemap/0.9")
        ET.register_namespace('xhtml', "http://www.w3.org/1999/xhtml")
        
        NS_SITEMAP = "http://www.sitemaps.org/schemas/sitemap/0.9"
        NS_XHTML = "http://www.w3.org/1999/xhtml"
        
        # 创建根节点 (物理对齐 W3C 标准，由 ET 自动管理 xmlns)
        root = ET.Element(f"{{{NS_SITEMAP}}}urlset")

        # 从元数据账本获取所有已注册文档 (V16.8 性能补丁：优先使用传入的快照)
        all_docs = all_docs_snapshot if all_docs_snapshot is not None else self.engine.meta.get_documents_snapshot()

        url_count = 0
        for rel_path, info in all_docs.items():
            if not info: continue
            # 获取该文档的所有语种版本
            translations = info.get('translations') or {}
            source_lang = getattr(self.engine.i18n.source, 'lang_code', 'zh-Hans') or 'zh-Hans'

            # 构建所有可用语种列表
            available_langs = [source_lang] + [l for l in translations.keys() if l]

            for lang in available_langs:
                if not lang: continue
                url_node = ET.SubElement(root, f"{{{NS_SITEMAP}}}url")

                # 计算逻辑 URL
                logical_url = self.engine.route_manager.resolve_logical_url(
                    lang, info.get('route_prefix', ''), info.get('sub_dir', ''), info.get('slug', '')
                )
                full_url = f"{self.site_url}{logical_url}"

                loc = ET.SubElement(url_node, f"{{{NS_SITEMAP}}}loc")
                loc.text = full_url

                lastmod = ET.SubElement(url_node, f"{{{NS_SITEMAP}}}lastmod")
                p_date = info.get('persistent_date')
                if p_date and isinstance(p_date, str):
                    lastmod.text = p_date.split('T')[0]
                else:
                    lastmod.text = datetime.now().strftime("%Y-%m-%d")

                # 注入 Hreflang 矩阵
                for h_lang in available_langs:
                    if not h_lang: continue
                    h_logical = self.engine.route_manager.resolve_logical_url(
                        h_lang, info.get('route_prefix', ''), info.get('sub_dir', ''), info.get('slug', '')
                    )
                    h_full_url = f"{self.site_url}{h_logical}"
                    
                    # 1. 注入标准语种链接
                    xhtml_link = ET.SubElement(url_node, f"{{{NS_XHTML}}}link")
                    xhtml_link.set("rel", "alternate")
                    xhtml_link.set("hreflang", h_lang)
                    xhtml_link.set("href", h_full_url)
                    
                    # 2. 如果是源语言，额外注入 x-default 以符合 Google SEO 最佳实践
                    if h_lang == source_lang:
                        x_link = ET.SubElement(url_node, f"{{{NS_XHTML}}}link")
                        x_link.set("rel", "alternate")
                        x_link.set("hreflang", "x-default")
                        x_link.set("href", h_full_url)

                url_count += 1

        # 导出文件
        target_base = self.engine.paths.get('target_base')
        if target_base:
            sitemap_path = os.path.join(target_base, "sitemap.xml")
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)
            tlog.info(f"✨ [站点地图] 导出成功: {url_count} 条 URL -> {sitemap_path}")
        else:
            tlog.warning("⚠️ [站点地图] 未配置 target_base，取消导出。")
