# -*- coding: utf-8 -*-
"""
Illacme Plenipes Core - Incremental Build Manager
🛡️ [SOP-01/SOP-02 Compliant]：行数限制在 300 行以下。
"""
import os
import shutil
import hashlib
import json
import subprocess
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter, inject_frontmatter

class IncrementalBuildManager:
    def __init__(self, engine):
        self.engine = engine
        self.theme_name = getattr(engine, 'active_theme', 'default') or 'default'
        self.theme_root = self._find_theme_root()
        vault_cache = engine.config.get_vault_cache_dir()
        self.cache_dir = os.path.join(vault_cache, "build", self.theme_name)
        self.history_file = os.path.join(self.cache_dir, "build_history.json")
        self.full_output_dir = os.path.join(self.cache_dir, "full_output")
        self.adapter = engine.ssg_adapter.active_renderer
        self.site_dir = os.path.join(self.theme_root, self.adapter.get_default_path_mappings().get("site_dir", "dist"))

    def _find_theme_root(self) -> str:
        source_dir = self.engine.paths.get("source_dir")
        if source_dir and os.path.exists(source_dir):
            curr = os.path.abspath(source_dir)
            for _ in range(6):
                if curr and curr != "/" and os.path.exists(os.path.join(curr, "package.json")):
                    return curr
                curr = os.path.dirname(curr)
        return os.path.join(self.engine._resolve_path("themes"), self.theme_name)

    def scan_source_fingerprints(self) -> dict:
        fingerprints, slots = {}, self.adapter.get_feature_slots()
        langs = [""]
        if self.engine.i18n.enabled:
            langs = [self.adapter.get_language_code(self.engine.i18n.source.lang_code) or ""]
            langs.extend(self.adapter.get_language_code(t.lang_code) or t.lang_code.lower() for t in self.engine.i18n.targets)
        dirs = []
        for n, cfg in slots.items():
            if n == "static": continue
            if cfg.get("single"): dirs.append(cfg["single"])
            if cfg.get("multi"):
                dirs.extend(cfg["multi"].format(lang=l) for l in langs if l)
        for rel_dir in dirs:
            abs_dir = os.path.join(self.theme_root, rel_dir)
            if not os.path.isdir(abs_dir): continue
            for root, _, files in os.walk(abs_dir):
                for file in files:
                    if file.lower().endswith((".md", ".mdx")):
                        abs_file = os.path.join(root, file)
                        rel_file = os.path.relpath(abs_file, self.theme_root)
                        try:
                            with open(abs_file, 'rb') as f:
                                fingerprints[rel_file] = hashlib.md5(f.read()).hexdigest()
                        except: pass
        return fingerprints

    def get_html_relative_paths(self, rel_path, doc_info) -> list:
        urls, slug = [], doc_info.get("slug") or os.path.splitext(os.path.basename(rel_path))[0]
        source = doc_info.get("route_source", "") or doc_info.get("source", "")
        prefix = doc_info.get("route_prefix", "") or doc_info.get("prefix", "")
        sub_dir = doc_info.get("sub_dir")
        if sub_dir is None:
            vault_path = self.engine.paths.get('vault', '.')
            t_sub = os.path.dirname(os.path.relpath(os.path.join(vault_path, rel_path), os.path.join(vault_path, source)).replace('\\', '/')).replace('\\', '/')
            sub_dir = self.engine.route_manager.get_mapped_sub_dir("" if t_sub == "." else t_sub, is_dry_run=False, allow_ai=False)

        def get_url(logical_code):
            physical_code = self.engine.route_manager.lang_mapping.get(logical_code, logical_code)
            fmt_prefix = prefix
            if "{" in prefix and "}" in prefix:
                try: fmt_prefix = prefix.format(lang=physical_code, sub_dir=sub_dir)
                except: pass
            is_docusaurus = "docusaurus" in self.theme_name.lower()
            if is_docusaurus and ("i18n/" in fmt_prefix or "docusaurus-plugin" in fmt_prefix):
                fmt_prefix = "blog" if "blog" in fmt_prefix else ("docs" if "docs" in fmt_prefix else "")
            prefix_val = f"/{fmt_prefix}" if fmt_prefix else ""
            if is_docusaurus and logical_code == self.engine.i18n.source.lang_code:
                raw_url = f"{prefix_val}/{sub_dir}/{slug}" if sub_dir else f"{prefix_val}/{slug}"
            else:
                raw_url = f"/{physical_code}{prefix_val}/{sub_dir}/{slug}" if sub_dir else f"/{physical_code}{prefix_val}/{slug}"
            import re
            return re.sub(r'/+', '/', raw_url)

        if self.engine.i18n.source.lang_code:
            urls.append(get_url(self.engine.i18n.source.lang_code))
        if self.engine.i18n.enabled:
            urls.extend(get_url(t.lang_code) for t in self.engine.i18n.targets if t.lang_code)
        html_paths = []
        for url in urls:
            clean = url.lstrip('/') or "index"
            html_paths.extend([f"{clean}.html", f"{clean}/index.html"])
        return html_paths

    def build(self) -> bool:
        os.makedirs(self.cache_dir, exist_ok=True)
        build_cmd = self.adapter.get_build_command()
        tlog.info("🔍 [增量编译] 正在扫描源文件指纹...")
        current_fps = self.scan_source_fingerprints()
        history = {}
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f: history = json.load(f)
            except: pass
        old_fps = history.get("source_fingerprints", {})
        if not old_fps or not os.path.exists(self.full_output_dir):
            tlog.info("📦 [增量编译] 未检测到历史指纹快照，启动首次全量编译...")
            subprocess.run(build_cmd, shell=True, cwd=self.theme_root, check=True)
            if os.path.exists(self.site_dir):
                shutil.rmtree(self.full_output_dir, ignore_errors=True)
                shutil.copytree(self.site_dir, self.full_output_dir)
            history["source_fingerprints"] = current_fps
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            tlog.success("✅ [增量编译] 首次全量编译与快照建立已闭环。")
            return True

        modified = [f for f, m in current_fps.items() if f not in old_fps or old_fps[f] != m]
        deleted = [f for f in old_fps if f not in current_fps]
        unmodified = [f for f in current_fps if f in old_fps and old_fps[f] == current_fps[f]]

        if not modified and not deleted:
            tlog.info("✨ [增量编译] 侦测到内容指纹无变化，直接命中缓存，无需重新渲染！")
            self._incremental_copy_tree(self.full_output_dir, self.site_dir)
            return True

        tlog.info(f"⚡ [增量编译] 变更：修改/新增 {len(modified)}，删除 {len(deleted)}，未变 {len(unmodified)}")
        self._incremental_copy_tree(self.full_output_dir, self.site_dir)
        disguised_backup = {}
        disguised_assets = {}
        try:
            # 🚀 [懒加载编译] 掏空未修改的大媒体资产
            disguised_assets = self._disguise_assets()

            for file_rel in unmodified:
                abs_path = os.path.join(self.theme_root, file_rel)
                if os.path.exists(abs_path):
                    with open(abs_path, 'r', encoding='utf-8') as f: content = f.read()
                    metadata, _, success = parse_frontmatter(content)
                    if success:
                        disguised_backup[abs_path] = content
                        disguised = inject_frontmatter("\n\n# (Incremental Build Cache Placeholder)\n", metadata)
                        with open(abs_path, 'w', encoding='utf-8') as f: f.write(disguised)

            tlog.info(f"🏗️ [增量编译] 执行 SSG 增量编译: {build_cmd}")
            subprocess.run(build_cmd, shell=True, cwd=self.theme_root, check=True)
            tlog.info("🛸 [增量编译] 正在增量归并最终静态产物...")
            
            for file_rel in deleted:
                doc_info = self.engine.meta.get_doc_info(file_rel) or {"slug": os.path.splitext(os.path.basename(file_rel))[0]}
                for h in self.get_html_relative_paths(file_rel, doc_info):
                    p = os.path.join(self.full_output_dir, h)
                    if os.path.exists(p): os.remove(p)

            for file_rel in modified:
                doc_info = next((info for k, info in self.engine.meta.get_documents_snapshot().items() if os.path.basename(k) == os.path.basename(file_rel)), {})
                for h in self.get_html_relative_paths(file_rel, doc_info):
                    src_h = os.path.join(self.site_dir, h)
                    dst_h = os.path.join(self.full_output_dir, h)
                    if os.path.exists(src_h):
                        os.makedirs(os.path.dirname(dst_h), exist_ok=True)
                        shutil.copy2(src_h, dst_h)

            # 🚀 [懒加载编译] 先还原大文件资产并回填到 site_dir
            static_in_dir = os.path.join(self.theme_root, "static")
            if not os.path.exists(static_in_dir):
                static_in_dir = os.path.join(self.theme_root, "public")
            
            for orig_path, (bak_path, abs_out_path) in disguised_assets.items():
                if os.path.exists(bak_path):
                    shutil.move(bak_path, orig_path)
                if os.path.exists(static_in_dir):
                    rel_out = os.path.relpath(orig_path, static_in_dir)
                    dst_in_site = os.path.join(self.site_dir, rel_out)
                    if not os.path.exists(dst_in_site):
                        os.makedirs(os.path.dirname(dst_in_site), exist_ok=True)
                        shutil.copy2(orig_path, dst_in_site)

            for item in os.listdir(self.site_dir):
                if item in ("assets", "img", "static"):
                    src_i = os.path.join(self.site_dir, item)
                    dst_i = os.path.join(self.full_output_dir, item)
                    if os.path.isdir(src_i):
                        self._incremental_copy_tree(src_i, dst_i)
        finally:
            tlog.info("⏪ [增量编译] 正在物理复原原地掏空的文档内容与大媒体...")
            for abs_p, orig in disguised_backup.items():
                try:
                    with open(abs_p, 'w', encoding='utf-8') as f: f.write(orig)
                except Exception as ex:
                    tlog.error(f"🚨 [增量编译] 还原文档失败: {abs_p} - {ex}")
            # 还原可能遗留的 disguised 大文件（防止编译中途出错崩溃）
            for orig_path, (bak_path, abs_out_path) in disguised_assets.items():
                if os.path.exists(bak_path):
                    try: shutil.move(bak_path, orig_path)
                    except: pass

        history["source_fingerprints"] = current_fps
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        self._incremental_copy_tree(self.full_output_dir, self.site_dir)
        tlog.success("✅ [增量编译] 增量静态装帧已完美闭环！")
        return True

    def _disguise_assets(self) -> dict:
        """在编译前隐藏未修改的大媒体资产，避免 SSG 冗余拷贝 I/O"""
        disguised = {}
        static_in_dir = os.path.join(self.theme_root, "static")
        if not os.path.exists(static_in_dir):
            static_in_dir = os.path.join(self.theme_root, "public")
        if not os.path.exists(static_in_dir):
            return disguised

        for root, _, files in os.walk(static_in_dir):
            for file in files:
                if file.endswith(".bak_disguise"):
                    continue
                abs_in_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(abs_in_path)
                    # 设定超大文件阈值为 5MB
                    if size > 5 * 1024 * 1024:
                        rel = os.path.relpath(abs_in_path, static_in_dir)
                        abs_out_path = os.path.join(self.full_output_dir, rel)
                        if os.path.exists(abs_out_path) and os.path.getsize(abs_out_path) == size:
                            if os.path.getmtime(abs_in_path) <= os.path.getmtime(abs_out_path):
                                bak_path = abs_in_path + ".bak_disguise"
                                shutil.move(abs_in_path, bak_path)
                                disguised[abs_in_path] = (bak_path, abs_out_path)
                                tlog.info(f"🔇 [懒加载资产] 掏空未修改的大媒体: {rel} ({size // (1024 * 1024)}MB)")
                except Exception as e:
                    tlog.warning(f"⚠️ 检查大资产 {file} 失败: {e}")
        return disguised

    def _incremental_copy_tree(self, src: str, dst: str):
        """智能增量差分合并目录"""
        if not os.path.exists(dst):
            os.makedirs(dst, exist_ok=True)
        src_files = set()
        for root, _, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                rel = os.path.relpath(src_file, src)
                dst_file = os.path.join(dst, rel)
                src_files.add(rel)
                
                need_copy = True
                if os.path.exists(dst_file):
                    if os.path.getsize(src_file) == os.path.getsize(dst_file):
                        if os.path.getmtime(src_file) <= os.path.getmtime(dst_file):
                            need_copy = False
                if need_copy:
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)

        # 差分清除孤儿文件
        for root, dirs, files in os.walk(dst, topdown=False):
            for file in files:
                dst_file = os.path.join(root, file)
                rel = os.path.relpath(dst_file, dst)
                if rel not in src_files:
                    try: os.remove(dst_file)
                    except: pass
            for d in dirs:
                abs_d = os.path.join(root, d)
                if not os.listdir(abs_d):
                    try: os.rmdir(abs_d)
                    except: pass
