# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG SEO Injection Helper
模块职责：为 SSG 渲染插件提供高阶 SEO 数据流的增强注入功能。
"""
import json
from typing import Any

def inject_seo_helper(fm: dict, desc_or_data: Any, keywords: list = None) -> dict:
    """
    [SEO] 框架感知的高阶 SEO 字段映射协议实现。
    支持新版完整字典传参，并保留对旧版（description + keywords）的向前兼容。
    
    参数:
        fm: Frontmatter 字典
        desc_or_data: 描述字符串（旧版）或完整的 SEO 数据字典（新版）
        keywords: 关键词列表（仅在旧版协议中使用）
    """
    if isinstance(desc_or_data, dict):
        data = desc_or_data
        # 1. 基础层 & OG/Twitter 层
        fields = [
            "description", "keywords", "og_title", "og_description",
            "og_type", "og_locale", "twitter_card", "twitter_title",
            "twitter_description", "canonical_url"
        ]
        for key in fields:
            if key in data and data[key] is not None:
                # 增量合并：Frontmatter 已存在的值不覆盖
                if not fm.get(key):
                    fm[key] = data[key]
        
        # 2. 结构化数据层 (json_ld, faq_ld, breadcrumb_ld)
        # 序列化为 JSON 字符串并写入 Frontmatter 的 structured_data 对应子键中
        structured_keys = ["json_ld", "faq_ld", "breadcrumb_ld"]
        for key in structured_keys:
            if key in data and data[key] is not None:
                structured_data = fm.setdefault("structured_data", {})
                if isinstance(data[key], (dict, list)):
                    try:
                        structured_data[key] = json.dumps(data[key], ensure_ascii=False)
                    except Exception:
                        structured_data[key] = str(data[key])
                else:
                    structured_data[key] = str(data[key])
    else:
        # 旧版兼容协议
        if desc_or_data:
            fm['description'] = desc_or_data
        if keywords:
            fm['keywords'] = keywords
            
    return fm
