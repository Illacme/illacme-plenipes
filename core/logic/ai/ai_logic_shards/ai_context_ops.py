#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 [V24.5] Illacme Plenipes - AI Context & Glossary Masker Shard
职责：提供 Markdown 智能语义分片、知识图谱上下文注入与术语词库隔离保护。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import re
from typing import Tuple, Dict, Any, List

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
        if gist:
            clean_gist = re.sub(r'(?:\d+\.\s*Analyze the Request|Draft\s*\d+:|Final Decision:).*', '', gist, flags=re.DOTALL | re.IGNORECASE)
            clean_gist = re.sub(r'<think>.*?</think>', '', clean_gist, flags=re.DOTALL)
            clean_gist = clean_gist.strip()
            if clean_gist:
                clean_gist = clean_gist.split('\n')[-1][:150]
                context_block += f"  Summary: {clean_gist}\n"
        
        # 提取核心技术术语
        concepts = entities.get("concepts", []) + entities.get("technologies", [])
        if concepts:
            context_block += f"  Key Terms: {', '.join(concepts[:10])}\n"
            
    context_block += "[/SEMANTIC_CONTEXT_FROM_KNOWLEDGE_GRAPH]\n"
    return context_block

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

def unmask_glossary(text: str, glossary_masks: Dict[str, str]) -> str:
    """🚀 [V24.5] 术语隔离还原：将大模型翻译后的术语占位符还原为对应的翻译目标值"""
    if not text or not glossary_masks:
        return text
    
    final_text = text
    for mask_key, orig_val in sorted(glossary_masks.items(), key=lambda x: len(x[0]), reverse=True):
        final_text = final_text.replace(mask_key, orig_val)
    return final_text
