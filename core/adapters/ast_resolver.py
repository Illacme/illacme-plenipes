#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AST Resolver (核心逻辑解析中枢)
模块职责：AST（抽象语法树）级的跨文档嵌套逻辑处理器。
架构原则：专职处理文件与文件之间的相对关系（跨文件引用块注入、MDX 组件物理拷贝、ESM 路径重计算）。
它不关心输入长什么样，也不关心最终发给哪个框架。
"""

import os
import re
import logging
import shutil
import threading
# 注意：由于我们在 adapters 目录下，需要跨级引入 utils
from ..utils import extract_frontmatter

logger = logging.getLogger("Illacme.plenipes")

class MDXResolver:
    """
    MDX 专用解析引擎与物理隔离护盾。
    负责处理 MDX 特有的 ESM (ECMAScript Modules) 语法，解决相对路径偏移，
    并在 AI 介入前为复杂的 JSX/React 组件套上防篡改保护罩。
    🚀 [V14.6 升级] 赋予物理空间穿梭能力：不仅重写路径，更会自动抓取并拷贝伴生的 CSS/JSX 组件！
    """
    def __init__(self, vault_root, target_base):
        """
        :param vault_root: 原始笔记库根目录。
        :param target_base: 前端输出基准目录。
        """
        self.vault_root = os.path.abspath(vault_root)
        self.target_base = os.path.abspath(target_base)
        
        # 🚀 预编译 MDX 逻辑块捕获正则 (全面升级为多行防断裂模式)
        # 匹配 import { \n A, \n B \n } from '...' 的多行解构语法
        self._import_pattern = re.compile(r'^(import\s+(?:\{[^}]+\}|.*?)\s+from\s+[\'"])(.*?)(\'|")', re.MULTILINE | re.DOTALL)
        
        # 🚀 跨域安全防火墙：白名单机制 (Allowed Companion Extensions)
        # 严格限制能被引擎自动跨目录搬运的文件类型，彻底防止恶意的相对路径探针将 .env 或密钥文件暴露到公网！
        self._allowed_companion_exts = {'.jsx', '.tsx', '.js', '.ts', '.css', '.scss', '.sass', '.less', '.json'}

    def remap_imports(self, content, src_path, dest_path):
        """
        🚀 终极 ESM 映射与伴生资源物理同步引擎。
        自动计算源文件与目标文件在物理层面的位移，修复相对路径。
        同时，将被依赖的本地组件和样式表一并拉升拷贝到前端环境，打通 SSG 构建闭环。
        """
        # 1. 🚀 [HTML 注释降维护盾] 将 转化为 MDX 合法的 {/* */}
        html_comment_regex = r'<!' + r'--(.*?)--' + r'>'
        safe_comment_pattern = re.compile(r'(```.*?```|`.*?`)|' + html_comment_regex, re.DOTALL)
        
        def safe_comment_repl(m):
            try:
                if m.group(1): return m.group(1) 
                if len(m.groups()) >= 2 and m.group(2) is not None:
                    return f"{{/*{m.group(2)}*/}}" 
            except IndexError:
                pass
            return m.group(0) 
            
        content = safe_comment_pattern.sub(safe_comment_repl, content)

        # 2. 🚀 [新增防线：MDX 原生 Style 标签防爆破引擎]
        # 拦截用户在 Markdown 中手写的 <style> 标签，自动穿上 JSX 模板字符串防弹衣
        # 彻底解决前端 Acorn 引擎将 CSS 大括号误认为 JavaScript 导致的崩溃
        def style_protect_repl(m):
            inner_css = m.group(1)
            # 智能判定：如果用户自己已经写了 {` `} 包裹，就不做重复处理
            if inner_css.strip().startswith("{`") and inner_css.strip().endswith("`}"):
                return m.group(0)
            # 自动注入防弹衣。注意 Python f-string 语法中用 {{ 和 }} 代表单大括号
            return f"<style>{{`\n{inner_css}\n`}}</style>"
            
        content = re.sub(r'<style>(.*?)</style>', style_protect_repl, content, flags=re.DOTALL | re.IGNORECASE)

        # 3. 🚀 [ESM 模块导入重映射]
        def repl(m):
            prefix = m.group(1)
            raw_path = m.group(2)
            suffix = m.group(3)

            # 过滤网络路径和别名路径
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
                                logger.debug(f"📦 [组件拉升] 成功同步 MDX 伴生资源: {final_raw_path}")
                                
                            if not final_raw_path.startswith('.'):
                                final_raw_path = './' + final_raw_path
                                
                            return f"{prefix}{final_raw_path}{suffix}"
                        except Exception as e:
                            logger.error(f"🛑 [跨界拷贝失败] 无法同步 MDX 本地组件 {raw_path}: {e}")
                            return m.group(0)
                else:
                    logger.debug(f"⚠️ [伴生资源缺失] 未能在源目录找到对应前端组件: {raw_path}")
                    return m.group(0)
                    
            return m.group(0)

        return self._import_pattern.sub(repl, content)

    def extract_logic_blocks(self, content):
        """
        🚀 终极逻辑隔离护盾：提取所有的 ESM 语句与 JSX 高级组件。
        基于启发式状态机，将这些前端特有代码物理抽出，替换为掩码，彻底斩断大模型产生幻觉的可能。
        """
        blocks = []
        
        # 1. 提取多行 import 语句
        import_capture = re.compile(r'^(import\s+(?:\{[^}]+\}|[^;]+)\s+from\s+[\'"][^\'"]+[\'"];?)', re.MULTILINE | re.DOTALL)
        blocks.extend(import_capture.findall(content))
        
        # 2. 提取多行 export 语句 (兼容 export const/let/function)
        export_capture = re.compile(r'^(export\s+(?:default\s+)?(?:const|let|var|function|class|type|interface)\s+[^;]+;?)', re.MULTILINE | re.DOTALL)
        blocks.extend(export_capture.findall(content))
        
        # 3. 提取 JSX 组件级物理护盾 (匹配 <CapitalizedTag ... /> 自闭合标签)
        # 强制只匹配大写字母开头的标签，避免误杀标准的 HTML 标签 (如 <br/> 或 <img>)
        jsx_self_closing = re.compile(r'(<[A-Z][A-Za-z0-9_]*[^>]*?/>)', re.DOTALL)
        blocks.extend(jsx_self_closing.findall(content))
        
        # 4. 提取成对的 JSX 组件块 (匹配 <CapitalizedTag>...</CapitalizedTag>)
        jsx_paired = re.compile(r'(<([A-Z][A-Za-z0-9_]*)[^>]*?>.*?</\2>)', re.DOTALL)
        blocks.extend([m[0] for m in jsx_paired.findall(content)])
        
        # 去重，保证掩码表的纯净
        return list(set(blocks))


class TransclusionResolver:
    """
    处理 Obsidian / Logseq 特有的 ![[嵌套文档]] 双链展开逻辑。
    
    该类通过递归扫描 Markdown 内容中的嵌入指令，将引用的子文档内容直接注入到父文档中，
    并内置了双重检查锁定 (DCL) 缓存机制以优化高并发下的 I/O 吞吐性能。
    """
    def __init__(self, md_index, asset_index, max_depth=3):
        """
        初始化嵌套解析器。
        :param md_index: 全局 Markdown 文件寻址倒排索引。
        :param asset_index: 全局静态资产寻址索引。
        :param max_depth: 最大嵌套递归深度，防止出现循环引用导致的进程栈溢出。
        """
        self.md_index = md_index
        self.asset_index = asset_index
        self.max_depth = max_depth
        
        # 架构升级：注入线程安全的内存级防抖缓存
        self._cache = {}
        self._cache_lock = threading.Lock()
        
        # 预编译正则表达式，确保在高频文本匹配中拥有极致的性能表现
        self._pattern = re.compile(r'^[ \t]*\!\[\[([^\]]+)\]\]', re.MULTILINE)

    def _extract_sub_content(self, body, sub_target, is_block=False):
        """
        🚀 高精度游标卡尺：在完整的文档正文中，精准切割出用户指定的块或标题区域。
        """
        if not sub_target:
            return body
            
        if is_block:
            # 块级引用截断：匹配包含 ^block-id 的独立段落
            # 采用非贪婪匹配捕获以该 ID 结尾的文本块
            pattern = re.compile(r'(?:^|\n\n)(.*?\^' + re.escape(sub_target) + r')(?:$|\n\n)', re.DOTALL)
            match = pattern.search(body)
            if match:
                # 剔除末尾的 ^block-id 标识符，防止污染生成后的前端页面排版
                return re.sub(r'\s*\^' + re.escape(sub_target) + r'$', '', match.group(1)).strip()
        else:
            # 标题级引用截断：提取指定 Heading 及其下属内容，直至遇到同级或更高级 Heading
            header_pattern = re.compile(r'^(#+)\s+' + re.escape(sub_target) + r'\s*$', re.MULTILINE)
            hmatch = header_pattern.search(body)
            if hmatch:
                level = len(hmatch.group(1))
                start_idx = hmatch.end()
                
                # 寻找下一个同级或更高层级的标题作为终点护城河
                next_header_pattern = re.compile(r'^#{1,' + str(level) + r'}\s+', re.MULTILINE)
                next_match = next_header_pattern.search(body, start_idx)
                
                if next_match:
                    return body[start_idx:next_match.start()].strip()
                else:
                    return body[start_idx:].strip()
                    
        return body

    def expand(self, content, current_depth=0):
        """
        递归且物理地展开嵌套引用。
        
        采用深度优先搜索 (DFS) 算法，逐层剥离并注入嵌套的引用标记。
        若达到最大深度限制，将触发主动预判告警并停止穿透，保留原始标记以保护进程安全。
        """
        if current_depth > self.max_depth: 
            logger.warning(f"⚠️ 嵌套递归受限: 节点展开深度已达上限 ({self.max_depth})。💡 建议: 请检查是否存在 A 引用 B、B 又引用 A 的循环引用逻辑。")
            return content
            
        def repl(m):
            # 🚀 提取链接全量原始特征，准备执行块级降维拆解
            raw_target = m.group(1).split('|')[0].strip()
            
            is_block = '^' in raw_target
            is_heading = '#' in raw_target and not is_block
            
            # 分离出物理文件名与内部锚点
            if is_block:
                file_part, sub_target = raw_target.split('^', 1)
            elif is_heading:
                file_part, sub_target = raw_target.split('#', 1)
            else:
                file_part, sub_target = raw_target, None
                
            link_target = file_part.strip()
            sub_target = sub_target.strip() if sub_target else None
            
            # 容错降级：如果只写了 ![[#Heading]] (页内自引)，目前跨文件引擎无法拿到当前上下文，原样退回以防崩溃
            if not link_target:
                return m.group(0)
            
            # 如果命中的是静态资产（如图片），则不属于文档展开范畴，原样退回给后续的资产管线接管
            if link_target in self.asset_index: 
                return m.group(0)
            
            # 从全局寻址索引中获取该文档的物理绝对路径
            target_abs_path = self.md_index.get(link_target)
            
            if target_abs_path and os.path.exists(target_abs_path):
                # 探针升级：获取被引用文件的当前物理修改时间
                current_mtime = os.path.getmtime(target_abs_path)
                
                # 双重检查锁定 (DCL) 内存缓存读取：阻断多线程环境下的重复磁盘 I/O 竞争
                with self._cache_lock:
                    cached_node = self._cache.get(target_abs_path)
                    # 防毒化验证：只有当缓存存在，且写入时间大于等于当前文件的物理时间时，才允许复用
                    if cached_node and cached_node['mtime'] >= current_mtime:
                        cached_body = cached_node['content']
                    else:
                        cached_body = None
                    
                if cached_body is None:
                    try:
                        with open(target_abs_path, 'r', encoding='utf-8') as f: 
                            t_content = f.read()
                        
                        # 仅提取 Body 内容，剔除 Frontmatter 元数据，防止污染父文档的属性区
                        _, t_body = extract_frontmatter(t_content)
                        
                        with self._cache_lock:
                            self._cache[target_abs_path] = {
                                'mtime': current_mtime,
                                'content': t_body
                            }
                            cached_body = t_body
                    except Exception:
                        logger.warning(f"⚠️ 引用展开失败: 无法读取文件 '{link_target}'。💡 诊断: 文件可能正在被占用，或路径包含非法字符。")
                        return m.group(0)
                
                # 🚀 触发高精度寻址拦截器，切出目标内容块
                scoped_body = self._extract_sub_content(cached_body, sub_target, is_block)
                
                # 对提取出的内容块递归执行深度展开，步进深度计数器
                expanded = self.expand(scoped_body, current_depth + 1)
                return f"\n\n{expanded}\n\n"
                
            return m.group(0)
            
        return self._pattern.sub(repl, content)