import os
import re
import shutil
from typing import Dict, Any
from core.markup.base import IContentTransformer
from core.utils.tracing import tlog

class MDXTransformer(IContentTransformer):
    """🚀 [V16.0] MDX 伴生资源与 ESM 重映射转换器"""
    
    def __init__(self):
        self._allowed_companion_exts = {'.jsx', '.tsx', '.js', '.ts', '.css', '.scss', '.sass', '.less', '.json'}
        self._import_pattern = re.compile(r'^(import\s+(?:\{[^}]+\}|.*?)\s+from\s+[\'"])(.*?)(\'|")', re.MULTILINE | re.DOTALL)

    def transform(self, content: str, context: Dict[str, Any]) -> str:
        src_path = context.get('src_path')
        dest_path = context.get('dest_path')
        
        if not src_path or not dest_path:
            return content

        # 1. HTML 注释降维护盾
        html_comment_regex = r'<!' + r'--(.*?)--' + r'>'
        safe_comment_pattern = re.compile(r'(```.*?```|`.*?`)|' + html_comment_regex, re.DOTALL)

        def safe_comment_repl(m):
            if m.group(1): return m.group(1)
            if len(m.groups()) >= 2 and m.group(2) is not None:
                return f"{{/*{m.group(2)}*/}}"
            return m.group(0)

        content = safe_comment_pattern.sub(safe_comment_repl, content)

        # 2. MDX 原生 Style 标签保护
        def style_protect_repl(m):
            inner_css = m.group(1)
            if inner_css.strip().startswith("{`") and inner_css.strip().endswith("`}"):
                return m.group(0)
            return f"<style>{{`\n{inner_css}\n`}}</style>"

        content = re.sub(r'<style>(.*?)</style>', style_protect_repl, content, flags=re.DOTALL | re.IGNORECASE)

        # 3. ESM 模块导入重映射
        def repl(m):
            prefix = m.group(1)
            raw_path = m.group(2)
            suffix = m.group(3)
            if raw_path.startswith(('.', '/')) and not raw_path.startswith('//'):
                src_dir = os.path.dirname(os.path.abspath(src_path))
                target_abs_path = os.path.abspath(os.path.join(src_dir, raw_path))
                actual_source_path = None
                detected_ext = ""
                
                if os.path.exists(target_abs_path) and os.path.isfile(target_abs_path):
                    actual_source_path = target_abs_path
                    detected_ext = os.path.splitext(actual_source_path)[1]
                else:
                    for ext in ['.jsx', '.tsx', '.js', '.ts', '.css', '.module.css']:
                        probe_path = target_abs_path + ext
                        if os.path.exists(probe_path):
                            actual_source_path = probe_path
                            detected_ext = ext
                            break
                
                if actual_source_path:
                    _, ext = os.path.splitext(actual_source_path)
                    if ext.lower() in self._allowed_companion_exts:
                        try:
                            dest_dir = os.path.dirname(os.path.abspath(dest_path))
                            final_raw_path = raw_path if raw_path.endswith(detected_ext) else raw_path + detected_ext
                            dest_companion_path = os.path.abspath(os.path.join(dest_dir, final_raw_path))
                            os.makedirs(os.path.dirname(dest_companion_path), exist_ok=True)
                            
                            if not os.path.exists(dest_companion_path) or os.path.getmtime(actual_source_path) > os.path.getmtime(dest_companion_path):
                                shutil.copy2(actual_source_path, dest_companion_path)
                                tlog.debug(f"📦 [组件拉升] 成功同步 MDX 伴生资源: {final_raw_path}")
                                
                            if not final_raw_path.startswith('.'): final_raw_path = './' + final_raw_path
                            return f"{prefix}{final_raw_path}{suffix}"
                        except Exception as e:
                            tlog.error(f"🛑 [跨界拷贝失败] 无法同步 MDX 本地组件 {raw_path}: {e}")
                            return m.group(0)
            return m.group(0)

        return self._import_pattern.sub(repl, content)
