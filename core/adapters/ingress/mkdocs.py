#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - MkDocs Dialect
模块职责：处理 MkDocs/Material 专属语法（!!! 缩进语法）的标准化。
🛡️ [AEL-Iter-v5.3]：模块化归位后的纯净处理器。
"""

import re
from typing import Tuple, Dict, Any
from .base import BaseDialect

class MkDocsDialect(BaseDialect):
    """🛠️ MkDocs/Material 方言处理器：处理 !!! 缩进语法"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        def mkdocs_repl(m):
            ctype = m.group(1).lower()
            title = m.group(2) or ctype.capitalize()
            body = m.group(3)
            lines = body.split('\n')
            quoted_lines = []
            for line in lines:
                if line.startswith('    '): quoted_lines.append(f"> {line[4:]}")
                elif line.startswith('\t'): quoted_lines.append(f"> {line[1:]}")
                elif line.strip() == '': quoted_lines.append(">")
                else: quoted_lines.append(f"> {line}")
            return f"> [!{ctype}] {title}\n" + '\n'.join(quoted_lines)

        text = re.sub(r'^!!!\s+([a-zA-Z]+)(?:\s+"([^"]*)")?\n((?:^[ \t]+.*\n?)*)', mkdocs_repl, text, flags=re.MULTILINE)
        return text, fm_dict
