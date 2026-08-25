#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 [V108.0] Illacme Plenipes - AI Cleaner Ops Shard
职责：提供工业级 Slug 净化、AI 译文提纯剥离、SEO 键值对提取与 JSX 标签物理预处理。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import re
import json

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

def clean_translation_response(raw_response: str) -> str:
    """
    🚀 [V108.0] 物理级 AI 译文提纯与 prompt 围栏防护
    彻底剥离 <think>...</think>、markdown 代码块包裹、### Content ### / ### Translation ### / ### Tərcümə ### 及其多语种变体，
    以及废话引言 (Let's translate..., Here is the translation...)。
    """
    if not raw_response: return ""
    # 1. 彻底剥离 <think>...</think> 及其变体
    text = re.sub(r'<(?:think|thinking)>.*?</(?:think|thinking)>', '', str(raw_response), flags=re.DOTALL).strip()

    # 2. 如果整段输出被 ```markdown 或 ``` 代码块包裹（而原文并非代码块），提取内部纯文本
    if text.startswith("```") and text.endswith("```"):
        m = re.match(r'^```[a-zA-Z0-9_-]*\n?(.*?)\n?```$', text, flags=re.DOTALL)
        if m:
            text = m.group(1).strip()

    # 3. 物理擦除 LLM 废话前缀 (如 "Here is the translation:", "Translation:", "翻訳:", "【翻訳】", "翻訳結果:")
    text = re.sub(r'^(?:Here is the translation|Here\'s the translation|Translation|Tərcümə|Çeviri|Traduction|Übersetzung|Traducción|翻译结果|译文|翻訳結果|翻訳文|日本語訳|対訳|訳文|翻訳)[:：]?\s*\n?', '', text, flags=re.IGNORECASE).strip()

    # 4. 按行过滤围栏标签 (如 ### Content ###, ### Translation ###, ### 翻訳 ###, 【翻訳】, 翻訳:, 以及孤立的空 ### 标题)
    lines = text.split("\n")
    cleaned_lines = []
    skip_line_re = re.compile(
        r'^\s*#{0,6}\s*[*_【\[`]*(?:Translation|Content|Inhalt|Übersetzung|Traduction|Contenido|Context|Tərcümə|Çeviri|原文|内容|译文|説明|概要|翻訳|日本語訳|対訳|翻訳結果|翻訳文|訳文)[*_】\]`]*\s*[:：]?\s*#{0,6}\s*$',
        re.IGNORECASE
    )
    
    for line in lines:
        stripped_line = line.strip()
        if skip_line_re.match(stripped_line):
            continue
        # 滤除单个 Line X: Translation: 前缀与行首 【翻訳】/ 翻訳: 标记
        line = re.sub(r'^Line\s*\d+[:：]\s*(?:Translation[:：]?)?\s*', '', line, flags=re.IGNORECASE)
        line = re.sub(r'^\s*[*_【\[]*(?:翻訳|日本語訳|対訳|翻訳結果|翻訳文|訳文|Translation)[:：]\s*[*_】\]]*\s*', '', line, flags=re.IGNORECASE)
        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines).strip()
    result = re.sub(r'^#{1,6}\s*(?:Translation|Content|Inhalt|Übersetzung|Traduction|Contenido|Context|Tərcümə|Çeviri|原文|内容|译文|説明|概要|翻訳|日本語訳|対訳|翻訳結果|翻訳文|訳文)\s*#{0,6}\n?', '', result, flags=re.IGNORECASE)
    result = re.sub(r'\n?#{1,6}\s*(?:Translation|Content|Inhalt|Übersetzung|Traduction|Contenido|Context|Tərcümə|Çeviri|原文|内容|译文|説明|概要|翻訳|日本語訳|対訳|翻訳结果|翻訳文|訳文)\s*#{0,6}$', '', result, flags=re.IGNORECASE)
    # 5. 彻底剥离行首/行尾孤立的 ### 标签残余 (例如 LLM 回吐的空标题头)
    result = re.sub(r'^\s*#{1,6}\s*\n', '', result).strip()
    result = re.sub(r'\n\s*#{1,6}\s*$', '', result).strip()
    return result.strip()

def clean_metadata_value(raw_response: str) -> str:
    """
    🚀 [V106.0] 物理级 SEO 与元数据提取算法
    物理剥离 LLM 返回结果中的 Typ: / Wert: / Value: / Description: / Tags: / Category: 等提示词键值对围栏、Prompt 分隔符或 Wikilinks 结构
    """
    if not raw_response: return ""
    text = re.sub(r'<think>.*?</think>', '', str(raw_response), flags=re.DOTALL).strip()
    text = re.sub(r'#{1,6}\s*(?:Translation|Content|Inhalt|Übersetzung|Traduction|Contenido|Context|原文|内容|译文|説明|概要)\s*#{0,6}', '', text, flags=re.IGNORECASE).strip()

    # 0. 尝试解析 JSON 格式 (例如 {"type": "Beschreibung", "value": "..."})
    if (text.startswith('{') and text.endswith('}')) or ('"value":' in text or '"description":' in text):
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                data = json.loads(json_str)
                if isinstance(data, dict):
                    val = data.get('value') or data.get('description') or data.get('text') or data.get('desc')
                    if val:
                        text = str(val).strip()
        except Exception:
            pass

    val_match = re.search(r'(?:Wert|Value|Description|描述|值|説明|概要|詳細)[:：]\s*(?P<val>.*?)(?:\n(?:Tags|Category|Kategorie|Typ|Type|カテゴリ|タグ|タイトル)[:：]|$)', text, re.IGNORECASE | re.DOTALL)
    if val_match:
        text = val_match.group('val').strip()
    else:
        text = re.sub(r'^(?:Typ|Type|Category|Kategorie|カテゴリ|タグ|タイトル)[:：].*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(?:Wert|Value|Description|描述|值|説明|概要|詳細)[:：]\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n(?:Tags|Category|Kategorie|カテゴリ|タグ|タイトル)[:：].*$', '', text, flags=re.IGNORECASE | re.DOTALL)

    # 剥离 Wikilinks 语法，例如 [[index|Index]] -> Index, [[index]] -> index
    text = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]+)\]\]', r'\1', text)
    return text.strip()

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
