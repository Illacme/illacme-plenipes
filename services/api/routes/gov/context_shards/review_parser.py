# -*- coding: utf-8 -*-
"""
🔒 [I5] Translation Human Review Parser Shard
职责：提供人工校对工作台的 Markdown 段落切割、杂质清洗与 Block 拓扑归一化。
"""

import re


def split_paragraphs(body: str) -> list:
    """将 Markdown 正文切割为段落块列表，用于前端段落级校对（Q1=C）。"""
    if not body:
        return []

    # 剥离系统内部追踪注释（Sovereign-Tag），不在校对 UI 中对用户展示
    body = re.sub(r'\s*<!--\s*Sovereign-Tag:.*?-->', '', body, flags=re.DOTALL).strip()

    # 🚀 [V115.0] 物理级 Markdown Block 对齐规范化：物理擦除 Çeviri ### 杂质、空 ### 标题及补齐标题前后空行断点
    body = re.sub(r'^(?:Çeviri|Translation|Translate|Çevirisi|翻译)\s*(?:###|:|：)?\s*', '', body, flags=re.IGNORECASE)
    body = re.sub(r'(?:Çeviri|Translation|Translate|Çevirisi|翻译)\s*###', '', body, flags=re.IGNORECASE)
    lines_clean = [l for l in body.split("\n") if not re.match(r'^#{1,6}\s*(?:Translation|Content|Inhalt|Übersetzung|Traduction|Contenido|Context|Tərcümə|Çeviri|原文|内容|译文|説明|概要)?\s*#{0,6}$', l.strip(), re.IGNORECASE)]
    body = "\n".join(lines_clean)
    body = re.sub(r'([^\n#])\s*(#{1,6}\s+)', r'\1\n\n\2', body)
    body = re.sub(r'^(#{1,6}\s+.*?)\n([^\n#])', r'\1\n\n\2', body, flags=re.MULTILINE)

    blocks = []
    idx = 0
    lines = body.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # 🚀 [V114.2] Alert 块自动归一化：若 > [!TAG] 标签与引文正文被 LLM 粘连在同一行，自动切割为独立的 Alert 头 Block
        if line.strip().startswith(">") and "[!" in line and "]" in line:
            match = re.match(r'^(\s*>\s*\[![^\]]+\])(.+)$', line.strip())
            if match and match.group(2).strip():
                tag_line = match.group(1).strip()
                rest_text = match.group(2).strip()
                rest_line = f"> {rest_text}" if not rest_text.startswith(">") else rest_text
                lines[i] = tag_line
                lines.insert(i + 1, rest_line)
                line = tag_line

        # 代码块：只读整体
        if line.strip().startswith("```"):
            end_j = i + 1
            while end_j < len(lines) and not lines[end_j].strip().startswith("```"):
                end_j += 1
            if end_j < len(lines):
                end_j += 1
            blocks.append({
                "index": idx,
                "type": "code",
                "text": "\n".join(lines[i:end_j])
            })
            idx += 1
            i = end_j
            continue

        # Callout 块（::: 语法）
        if line.strip().startswith(":::"):
            end_j = i + 1
            while end_j < len(lines) and not lines[end_j].strip().startswith(":::"):
                end_j += 1
            if end_j < len(lines):
                end_j += 1
            blocks.append({
                "index": idx,
                "type": "callout",
                "text": "\n".join(lines[i:end_j])
            })
            idx += 1
            i = end_j
            continue

        # 普通段落 / Callout (>)：智能拆分与连贯性识别
        if line.strip():
            para_lines = []
            is_quote_block = line.strip().startswith(">")
            while i < len(lines) and lines[i].strip():
                curr_l = lines[i].strip()
                if para_lines:
                    if curr_l.startswith('#'):
                        break
                    if not is_quote_block and curr_l.startswith('>'):
                        break
                    if is_quote_block and not curr_l.startswith('>'):
                        break
                para_lines.append(lines[i])
                i += 1
            text = "\n".join(para_lines).strip()
            # 🛡️ [SSOT] 分割线与纯 HTML 注释：设为 spacer 块（index=-1），在 UI 中展示但不计入正文段落编号
            from core.markup.base import MarkupBlock
            if MarkupBlock.is_ignorable_spacer(text):
                blocks.append({
                    "index": -1,
                    "type": "spacer",
                    "text": text
                })
                continue
            b_type = "callout" if is_quote_block else "paragraph"
            blocks.append({
                "index": idx,
                "type": b_type,
                "text": text
            })
            idx += 1
        else:
            i += 1

    return blocks
