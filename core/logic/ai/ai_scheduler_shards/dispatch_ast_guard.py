# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - AST Guard & Translation Auditor
职责：块级 AST 结构守恒核验防线与语义主权标签核验
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import re
from typing import Tuple, Optional, List, Set


class DispatchASTGuard:
    @staticmethod
    def validate_block_structure(source: str, translated: str) -> Tuple[bool, str]:
        """
        🛡️ [P4] 块级 AST 结构守恒核验防线
        比对原文与译文的 Markdown/HTML 控制标记的一致性与完整性。
        """
        # 1. 校验代码块数量与闭合性
        s_code = len(re.findall(r'```', source))
        t_code = len(re.findall(r'```', translated))
        if s_code % 2 == 0:
            if t_code % 2 != 0:
                return False, "译文中代码块未闭合"
            if s_code != t_code:
                return False, f"代码块数量不匹配 (原文 {s_code//2} vs 译文 {t_code//2})"
        else:
            if s_code != t_code:
                return False, f"代码块标记个数不一致 (原文 {s_code} vs 译文 {t_code})"

        # 2. 校验双链 Wikilinks 数量
        s_wiki = len(re.findall(r'\[\[.*?\]\]', source))
        t_wiki = len(re.findall(r'\[\[.*?\]\]', translated))
        if s_wiki != t_wiki:
            return False, f"双链 Wikilink 数量不匹配 (原文 {s_wiki} vs 译文 {t_wiki})"

        # 3. 校验标准 Markdown 链接数量
        s_urls = len(re.findall(r'\]\(([^)]+)\)', source))
        t_urls = len(re.findall(r'\]\(([^)]+)\)', translated))
        if s_urls != t_urls:
            return False, f"Markdown 链接数量不匹配 (原文 {s_urls} vs 译文 {t_urls})"

        # 4. 校验 HTML 标签对称性
        s_open = len(re.findall(r'<([a-zA-Z0-9]+)[^>]*>', source))
        s_close = len(re.findall(r'<\/([a-zA-Z0-9]+)>', source))
        t_open = len(re.findall(r'<([a-zA-Z0-9]+)[^>]*>', translated))
        t_close = len(re.findall(r'<\/([a-zA-Z0-9]+)>', translated))
        s_tags = s_open + s_close
        t_tags = t_open + t_close

        # 如果原文本身是开闭完全平衡的完整 HTML 结构（如 <div><span>Hello</span></div>），
        # 则译文必须保持开闭平衡且标签总数一致
        if s_open == s_close:
            if t_open != t_close or s_tags != t_tags:
                return False, f"HTML 标签数量不匹配 (原文 {s_tags} vs 译文 {t_tags})"
        else:
            # 如果原文本身就是跨段落的开放式容器（s_open != s_close），
            # 允许在边界处存在与原文不平衡差值以内的容错（但核心标签不应归零）
            imbalance = abs(s_open - s_close)
            if s_tags > 0 and t_tags == 0:
                return False, "译文中遗漏了 HTML 标签结构"
            if abs(s_tags - t_tags) > imbalance:
                return False, f"HTML 标签数量不匹配 (原文 {s_tags} vs 译文 {t_tags})"

        # 5. 校验粗体/斜体闭合性
        s_bold = len(re.findall(r'\*\*|__', source))
        t_bold = len(re.findall(r'\*\*|__', translated))
        if s_bold % 2 == 0 and t_bold % 2 != 0:
            return False, "译文中粗体/斜体控制符未闭合"

        return True, ""

    @staticmethod
    def audit_translation(body: str, source_raw: str, masks: Optional[List[str]] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        🛡️ 语义完整性与主权标签核验防线
        检查译文中 Wikilinks 与主权标签是否存在漏损。
        """
        def normalize_wikilink(link: str) -> str:
            content = link.strip('[]')
            target = content.split('|')[0].strip()
            if target.lower().endswith('.md'):
                target = target[:-3]
            elif target.lower().endswith('.markdown'):
                target = target[:-9]
            return target.lower()

        source_raw_links = [b for b in re.findall(r'\[\[.*?\]\]', source_raw) if "MASK" not in b]
        if not source_raw_links:
            return None, None

        # 🚀 [V10.9] 预先解包当前 context 中挂载的系统遮罩 (STB_MASK_N -> 原始 Wikilink)，消除误报
        if masks:
            for idx_mask, mask_val in enumerate(masks):
                mask_key = f"[[STB_MASK_{idx_mask}]]"
                if mask_key in body and isinstance(mask_val, str):
                    body = body.replace(mask_key, mask_val)

        source_targets = {normalize_wikilink(b) for b in source_raw_links}
        target_raw_links = re.findall(r'\[\[.*?\]\]', body)
        target_targets = {normalize_wikilink(b) for b in target_raw_links}

        body_lower = body.lower()
        missing_targets = set()
        for src_target in source_targets:
            clean_src = src_target[:-3] if src_target.endswith('.md') else src_target
            if src_target not in target_targets and clean_src not in target_targets and src_target not in body_lower and clean_src not in body_lower:
                missing_targets.add(src_target)

        if missing_targets:
            return "SOVEREIGNTY_SHIELD", f"主权标签 [[{list(missing_targets)[0]}]] 在译文中丢失"
        return None, None
