#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Logic Hub
模块职责：提供工业级的 AI 业务处理计算单元，包括 Slug 清洗、JSON 修复与提示词渲染。
🛡️ [Rule 12.9/12.10]：逻辑解耦核心，确保适配器只负责协议。
"""

import re
import json
import logging
from typing import Tuple, Dict, Any, List

from core.utils.tracing import tlog

class AILogicHub:
    """🚀 [TDR-Iter-025] 工业级 AI 业务逻辑计算中心"""

    @staticmethod
    def clean_slug(raw_slug: str, max_length: int = 100) -> str:
        """
        [Industrial-Grade] 物理级 Slug 净化逻辑
        - 强制小写
        - 仅保留字母、数字、连字符与斜杠（/）
        - 压缩连续连字符与连续斜杠
        - 去除首尾连字符与斜杠
        - 长度硬截断
        """
        if not raw_slug: return ""

        # 1. 强制小写并替换空格/下划线
        clean = raw_slug.lower().strip()
        clean = clean.replace(" ", "-").replace("_", "-")

        # 2. 物理脱敏：只允许 a-z, 0-9, - 和 /
        clean = re.sub(r'[^a-z0-9\-\/]', '', clean)

        # 3. 语义脱敏：压缩连续的 '-' 和 '/'
        clean = re.sub(r'-+', '-', clean)
        clean = re.sub(r'/+', '/', clean)

        # 4. 边界处理
        clean = clean.strip('-/')

        # 5. 长度保护
        return clean[:max_length]

    @staticmethod
    def repair_json(raw_response: str) -> str:
        """
        [Resilience] 强力 JSON 修复算法
        处理 AI 返回的带 Markdown 标签、注释或前后缀的非标 JSON
        
        🚀 [V78.1] 防御推理内容污染：当原始响应中找不到有效 JSON 边界 ({...})
        时（例如模型输出了 reasoning_content 等纯文本），直接返回空 JSON 对象
        "{}"，防止推理文字被传入 json.loads 导致 'Expecting value' 崩溃。
        """
        if not raw_response: return "{}"

        content = raw_response.strip()

        # 1. 物理剥离 Markdown 围栏
        if "```json" in content:
            match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if match: content = match.group(1)
        elif "```" in content:
            match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if match: content = match.group(1)

        # 2. 寻找第一个 { 和最后一个 } 之间的内容
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]
            return content

        # 3. 🛡️ [防污染兜底] 找不到有效 JSON 边界（例如模型返回的是推理文字），
        #    返回空 JSON 对象，让上层调用方通过 fallback 机制优雅降级，
        #    而不是将原始文本传入 json.loads 导致崩溃。
        return "{}"

    @staticmethod
    def repair_json_array(raw_response: str) -> str:
        """
        [Resilience] 强力 JSON Array 修复算法
        """
        if not raw_response: return "[]"
        content = raw_response.strip()

        # 1. 物理剥离 Markdown 围栏
        if "```json" in content:
            match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if match: content = match.group(1)
        elif "```" in content:
            match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if match: content = match.group(1)

        # 2. 寻找第一个 [ 和最后一个 ] 之间的内容
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1:
            content = content[start:end+1]

        return content

    @staticmethod
    def mask_block(text: str, translate_labels: bool = True, external_mask_mode: str = "url_only") -> Tuple[str, Dict[str, str]]:
        """🚀 [V48.3] 块级防护装甲：临时屏蔽技术实体，防止 AI 误伤"""
        if not text: return "", {}
        
        masks = {}
        # 防护矩阵：Wikilinks, MD Links, Images, 占位符
        patterns = [
            r'\!\[\[.*?\]\]',                                                   # Obsidian Image
            r'\[\[.*?\]\]',                                                    # Wikilink
            r'\!\[(?P<md_img_label>.*?)\]\((?P<md_img_url>.*?)\)',               # Markdown Image
            r'\[(?P<md_link_label>.*?)\]\((?P<md_link_url>.*?)\)',               # Markdown Link
            r'<!\[CDATA\[.*?\]\]>',                                            # CDATA
            r'<!--.*?-->',                                                      # Comments
            r'\[\[STB_MASK_\d+\]\]'                                             # System Masks
        ]
        
        def repl(m):
            # 检查是否匹配到了 Markdown Link
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

    @staticmethod
    def unmask_block(text: str, masks: Dict[str, str]) -> str:
        """🚀 [V48.3] 块级护盾解除：还原被临时屏蔽的技术实体"""
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
        
        # 2. 还原被遮罩的 URL
        final_text = processed_text
        for key in sorted(masks.keys(), key=len, reverse=True):
            final_text = final_text.replace(key, masks[key])
        return final_text

    @staticmethod
    def purify_content(text: str, strip_jsx: bool = False) -> str:
        """
        [Sovereignty] 内容净化引擎
        在发送给 AI 前进行物理预处理，防止标签干扰
        """
        if not text: return ""

        purified = text
        if strip_jsx:
            # 物理剥离类 JSX 标签 (例如 <TabItem>, <CodeBlock> 等)
            # 💡 保留内部内容，只剥离标签本身
            purified = re.sub(r'<[A-Z][a-zA-Z0-9]*.*?>', '', purified)
            purified = re.sub(r'</[A-Z][a-zA-Z0-9]*>', '', purified)

        return purified.strip()

    @staticmethod
    def extract_seo_payload(raw_json_str: str) -> Tuple[Dict[str, Any], bool]:
        """
        [Industrial-Grade] SEO 载荷安全提取
        """
        try:
            repaired = AILogicHub.repair_json(raw_json_str)
            data = json.loads(repaired)

            # 结构标准化
            result = {
                "description": str(data.get("description", ""))[:160], # 限制 SEO 描述长度
                "keywords": data.get("keywords", [])
            }

            # 关键词清洗
            if isinstance(result["keywords"], str):
                result["keywords"] = [k.strip() for k in result["keywords"].split(",") if k.strip()]
            elif not isinstance(result["keywords"], list):
                result["keywords"] = []

            return result, True
        except Exception as e:
            tlog.error(f"🛑 [SEO Logic Error]: JSON 修复失败: {e}")
            return {"description": "", "keywords": []}, False

    @staticmethod
    def split_markdown(text: str, max_chunk_size: int) -> List[str]:
        """
        [Industrial-Grade] 语义分片算法 (Markdown 优先)
        - 优先尝试在二级标题处切分
        - 其次尝试在段落处切分
        - 最后尝试在换行符处切分
        - 兜底进行硬切分
        """
        if not text: return []
        if len(text) <= max_chunk_size: return [text]

        chunks = []
        # 优先级：## 标题 > 段落 > 换行
        splitters = ['\n## ', '\n\n', '\n']

        current_text = text
        while len(current_text) > max_chunk_size:
            split_pos = -1
            for s in splitters:
                # 寻找在限制范围内的最后一个分割点
                split_pos = current_text.rfind(s, 0, max_chunk_size)
                if split_pos != -1:
                    split_pos += len(s) # 包含分割符本身或保持结构
                break

            if split_pos <= 0:
                # 兜底：如果没有找到任何分割点，进行物理硬切
                split_pos = max_chunk_size

            chunks.append(current_text[:split_pos].strip())
            current_text = current_text[split_pos:].strip()

        if current_text:
            chunks.append(current_text)
        return chunks
    @staticmethod
    def format_knowledge_context(related_nodes: List[Dict[str, Any]]) -> str:
        """🚀 [V24.5] 语义主权：将知识图谱数据转化为 AI 翻译上下文指令"""
        if not related_nodes: return ""
        
        context_block = "\n\n[SEMANTIC_CONTEXT_FROM_KNOWLEDGE_GRAPH]\n"
        context_block += "The following information is from related documents in the same knowledge base. Use it to maintain terminology consistency:\n"
        
        for node in related_nodes:
            title = node.get("title", "Untitled")
            gist = node.get("gist", "")
            entities = node.get("entities", {})
            
            context_block += f"- Document: {title}\n"
            if gist: context_block += f"  Summary: {gist}\n"
            
            # 提取核心技术术语
            concepts = entities.get("concepts", []) + entities.get("technologies", [])
            if concepts:
                context_block += f"  Key Terms: {', '.join(concepts[:10])}\n"
                
        context_block += "[/SEMANTIC_CONTEXT_FROM_KNOWLEDGE_GRAPH]\n"
        return context_block

    @staticmethod
    def mask_glossary(text: str, glossary: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
        """🚀 [V24.5] 术语隔离屏蔽：在发送给 AI 前，使用占位符保护术语不被误翻译"""
        if not text or not glossary:
            return text, {}
        
        glossary_masks = {}
        processed_text = text
        
        # 按照键长度降序排序，防止子词覆盖
        for orig_word in sorted(glossary.keys(), key=len, reverse=True):
            target_val = glossary[orig_word]
            
            # 使用无副作用的正则边界进行术语匹配
            if re.search(r'[\u4e00-\u9fa5]', orig_word):
                pattern = re.compile(re.escape(orig_word))
            else:
                pattern = re.compile(rf'\b{re.escape(orig_word)}\b', re.IGNORECASE)
                
            matches = pattern.findall(processed_text)
            
            for m in set(matches):
                mask_key = f"[[GLOS_MASK_{len(glossary_masks)}]]"
                glossary_masks[mask_key] = target_val
                processed_text = processed_text.replace(m, mask_key)
                
        return processed_text, glossary_masks

    @staticmethod
    def unmask_glossary(text: str, glossary_masks: Dict[str, str]) -> str:
        """🚀 [V24.5] 术语隔离还原：将大模型翻译后的术语占位符还原为对应的翻译目标值"""
        if not text or not glossary_masks:
            return text
        
        final_text = text
        for mask_key, orig_val in sorted(glossary_masks.items(), key=lambda x: len(x[0]), reverse=True):
            final_text = final_text.replace(mask_key, orig_val)
        return final_text
