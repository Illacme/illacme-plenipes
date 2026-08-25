#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧱 [V48.3] Illacme Plenipes - AI Masker & AST Structural Healer Shard
职责：提供工业级 Markdown 块级屏蔽装甲，临时遮罩 Wikilinks、Markdown 图片链接与技术实体，并提供主权级结构自愈算法。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import re
from typing import Tuple, Dict

def mask_block(text: str, translate_labels: bool = True, external_mask_mode: str = "url_only") -> Tuple[str, Dict[str, str]]:
    """🚀 [V48.3] 块级防护装甲：临时屏蔽技术实体，防止 AI 误伤"""
    if not text: return "", {}
    
    masks = {}
    # 防护矩阵：Wikilinks, MD Links, Images, 占位符
    patterns = [
        r'\!\[\[.*?\]\]',                                                   # Obsidian Image
        r'\[\[(?P<wiki_body>.*?)\]\]',                                      # Wikilink (含 display label 提取)
        r'\!\[(?P<md_img_label>.*?)\]\((?P<md_img_url>.*?)\)',               # Markdown Image
        r'\[(?P<md_link_label>.*?)\]\((?P<md_link_url>.*?)\)',               # Markdown Link
        r'<!\[CDATA\[.*?\]\]>',                                            # CDATA
        r'<!--.*?-->',                                                      # Comments
        r'\[\[STB_MASK_\d+\]\]'                                             # System Masks
    ]
    
    def repl(m):
        # A. 检查是否匹配到了 Wikilink [[...]]
        try:
            wiki_body = m.group('wiki_body')
        except IndexError:
            wiki_body = None
        if wiki_body is not None:
            if not translate_labels:
                # 不翻译标签时，整体遮罩
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = m.group(0)
                return key
            # 翻译标签模式：保留 display text 参与 AI 翻译
            if '|' in wiki_body:
                target_part, alias_part = wiki_body.split('|', 1)
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = target_part
                return f"[[{key}|{alias_part}]]"
            else:
                # [[创建链接]] → 遮罩 target 并复制为 display text
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = wiki_body
                return f"[[{key}|{wiki_body}]]"

        # B. 检查是否匹配到了 Markdown Link
        if m.group('md_link_url') is not None:
            label = m.group('md_link_label')
            url = m.group('md_link_url')
            is_ext = url.startswith(('http://', 'https://', 'mailto:', 'tel:'))
            if not translate_labels or (is_ext and external_mask_mode == "all"):
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = m.group(0)
                return key

            if '#|' in url and url.endswith('|'):
                base, rest = url.split('#|', 1)
                anchor = rest[:-1]
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = base
                return f"[{label}]({key}#|{anchor}|)"
            elif '#' in url:
                base, anchor = url.split('#', 1)
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = base
                return f"[{label}]({key}#|{anchor}|)"
            else:
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = url
                return f"[{label}]({key})"

        # 检查是否匹配到了 Markdown Image
        if m.group('md_img_url') is not None:
            label = m.group('md_img_label')
            url = m.group('md_img_url')
            is_ext = url.startswith(('http://', 'https://', 'mailto:', 'tel:'))
            if not translate_labels or (is_ext and external_mask_mode == "all"):
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = m.group(0)
                return key

            if '#|' in url and url.endswith('|'):
                base, rest = url.split('#|', 1)
                anchor = rest[:-1]
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = base
                return f"![{label}]({key}#|{anchor}|)"
            elif '#' in url:
                base, anchor = url.split('#', 1)
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = base
                return f"![{label}]({key}#|{anchor}|)"
            else:
                key = f"__B_MASK_{len(masks)}__"
                masks[key] = url
                return f"![{label}]({key})"

        # 兜底：整体遮罩
        key = f"__B_MASK_{len(masks)}__"
        masks[key] = m.group(0)
        return key

    combined_pattern = "|".join(patterns)
    masked_text = re.sub(combined_pattern, repl, text, flags=re.DOTALL)
    return masked_text, masks

def unmask_block(text: str, masks: Dict[str, str]) -> str:
    """🚀 [V48.3] 块级护盾解除：还原被临时屏蔽的技术实体，具备 Markdown 结构自愈能力"""
    if not text: return text
    
    # 1. 还原并清洗大模型翻译后的哈希锚点
    def clean_hash(h: str) -> str:
        h = h.strip().lower()
        # 转换为合规的哈希：空格和特殊字符变连字符
        h = re.sub(r'[^a-z0-9\.\-\u4e00-\u9fa5]', '-', h)
        h = re.sub(r'-+', '-', h)
        return h.strip('-')

    def repl_anchor(match):
        anchor_val = match.group(1)
        return f"#{clean_hash(anchor_val)}"

    processed_text = re.sub(r'#\|(.*?)\|', repl_anchor, text)
    if not masks: return processed_text
    
    # 2. 还原被遮罩的 URL 与实体，并执行 Markdown 控制语法结构自愈
    final_text = processed_text
    for key in sorted(masks.keys(), key=len, reverse=True):
        val = masks[key]
        esc_key = re.escape(key)
        
        # 如果 val 是 URL 或 Anchor URL
        if not val.startswith('![') and not val.startswith('[') and not val.startswith('<!') and not val.startswith('<!--'):
            # 自愈 0：Wikilink [[__B_MASK_N__|translated_alias]] 还原
            wikilink_mask_pattern = r'\[\[\s*' + esc_key + r'\s*\|\s*(?P<alias>[^\]\n]+?)\s*\]\]'
            if re.search(wikilink_mask_pattern, final_text, re.IGNORECASE):
                def _repl_wikilink(m, _val=val):
                    alias = m.group('alias').strip()
                    if alias == _val:
                        return f"[[{_val}]]"
                    return f"[[{_val}|{alias}]]"
                final_text = re.sub(wikilink_mask_pattern, _repl_wikilink, final_text, flags=re.IGNORECASE)
                continue

            def repl_link(m):
                lbl = m.group('label')
                anc = m.group('anchor') or ''
                return f"[{lbl}]({val}{anc})"

            # 自愈 1：强力对齐 [label] __B_MASK_N__#anchor、[label]-(__B_MASK_N__)、[label] ( __B_MASK_N__ )
            # 必须使用 (?<!\[) 和 (?!\]) 排除 Wikilink [[...]]
            bracket_mask_pattern = r'(?<!\[)\[(?P<label>[^\[\]\n]+)\]\s*[-–—]?\s*\(?\s*' + esc_key + r'(?P<anchor>#[^)\s]+)?\s*\)?(?!\])'
            if re.search(bracket_mask_pattern, final_text, re.IGNORECASE):
                final_text = re.sub(bracket_mask_pattern, repl_link, final_text, flags=re.IGNORECASE)
                continue
            
            # 自愈 2：对于无 [ ] 括起来的单词 + (__B_MASK_N__)，如 `Importer (__B_MASK_0__)`
            no_bracket_pattern = r'(?<!\])\b(?P<label>[^\s\[\]\(\)\{\}]+)\s*\(\s*' + esc_key + r'\s*\)'
            if re.search(no_bracket_pattern, final_text, re.IGNORECASE):
                final_text = re.sub(no_bracket_pattern, r'[\g<label>](' + val + ')', final_text, flags=re.IGNORECASE)
                continue

        # 自愈 3：标准/通用不区分大小写遮罩替换 (用于 Wikilinks [[...]]、Images、Comments、System Masks 等)
        pattern_key = re.compile(esc_key, re.IGNORECASE)
        if pattern_key.search(final_text):
            final_text = pattern_key.sub(lambda m: val, final_text)

    # 自愈 4：防漏熔断兜底 (若大模型在翻译时彻底抹掉了掩码实体，自动挂载缺失实体，确保 AST 语法及主权标签零丢失)
    for key, val in masks.items():
        if val not in final_text:
            if val.startswith(('http://', 'https://', '/')):
                # 寻找未挂载 URL 的单方括号 [label] (排除 Wikilink [[...]])
                orphan_pattern = r'(?<!\[)\[(?P<label>[^\[\]\n]+)\](?!\]|\s*\()'
                if re.search(orphan_pattern, final_text):
                    final_text = re.sub(orphan_pattern, r'[\g<label>](' + val + ')', final_text, count=1)
                else:
                    final_text = final_text.rstrip() + f" [Link]({val})"
            else:
                # 缺失的是 Wikilink 或其他实体，安全地追加在文本末尾
                final_text = final_text.rstrip() + f" {val}"

    # 自愈 5：终极语法连字符与空格清洗（防止德语等语言大模型在 ] 和 ( 之间误加 - 或空格，如 `[Importer]-(http...)` -> `[Importer](http...)`）
    final_text = re.sub(r'(?<!\[)\]\s*[-–—]?\s*\(', '](', final_text)

    return final_text
