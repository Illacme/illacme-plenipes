import asyncio, json, os, psutil, subprocess, urllib.parse
from typing import Dict, Any
from core.adapters.ai.tool_protocol import IllacmeTool


class CheckHealthTool(IllacmeTool):
    """🏢 [V75.0] 系统健康诊断工具"""
    name = "check_system_health"
    description = "Check the server's CPU, memory, and disk usage statistics."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> str:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return f"=== Illacme Plenipes System Health ===\nCPU Usage: {cpu_percent}%\nMemory Usage: {mem.percent}% (Used: {mem.used / (1024**3):.2f}GB / Total: {mem.total / (1024**3):.2f}GB)\nDisk Usage: {disk.percent}% (Free: {disk.free / (1024**3):.2f}GB)\n"
        except Exception as e:
            return f"Error gathering health metrics: {str(e)}"


class GitStatusTool(IllacmeTool):
    """🏢 [V75.0] Git 状态检查工具"""
    name = "get_git_status"
    description = "Run 'git status' and 'git log -1' to get the current state of the repository."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> str:
        try:
            status_output = subprocess.check_output(['git', 'status', '-s'], text=True, stderr=subprocess.STDOUT)
            log_output = subprocess.check_output(['git', 'log', '-1', '--oneline'], text=True, stderr=subprocess.STDOUT)
            return f"--- Current Commit ---\n{log_output}\n--- Changed Files ---\n{status_output if status_output.strip() else 'No changed files.'}"
        except Exception as e:
            return f"Error executing git command: {str(e)}"


class InspectPublishingReadinessTool(IllacmeTool):
    """📡 [Feature: Editorial Chief Agent] 全站出版与播客就绪度巡检工具"""
    name = "inspect_publishing_readiness"
    description = "Inspect global publishing readiness: vault documents, pending/synthesized podcasts, bound e-books, and active AI compute status."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> str:
        try:
            from core.runtime.engine_singleton import get_global_engine
            from core.adapters.ai.tools.vault_service import get_secure_vault_path
            from core.adapters.ai.network_mixin import get_active_ai_status
            from core.utils.text import parse_frontmatter

            engine = get_global_engine()
            vault_path = get_secure_vault_path()
            imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
            cache_dir = getattr(engine, "cache_dir", os.path.join(os.getcwd(), ".plenipes", "cache")) if engine else os.path.join(os.getcwd(), ".plenipes", "cache")
            podcast_dir = os.path.join(cache_dir, "podcasts", imprint_id)
            existing_mp3s = [f for f in os.listdir(podcast_dir) if f.endswith(".mp3")] if os.path.isdir(podcast_dir) else []
            mp3_prefixes = {f.split("_")[0] for f in existing_mp3s}
            total_docs, pending_podcasts = 0, []
            for root, _, files in os.walk(vault_path):
                for file in files:
                    if not file.endswith(".md") or file.startswith("."):
                        continue
                    total_docs += 1
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, vault_path).replace("\\", "/")
                    try:
                        with open(full_p, "r", encoding="utf-8") as f:
                            fm, _, _ = parse_frontmatter(f.read(2048))
                        if isinstance(fm, dict) and str(fm.get("podcast", "")).lower() in ("true", "1", "yes", "auto") and os.path.splitext(file)[0] not in mp3_prefixes:
                            pending_podcasts.append(rel_p)
                    except Exception:
                        pass
            from core.bindery.bindery_asset_syncer import resolve_imprint_books_dir
            books_dir = resolve_imprint_books_dir(engine)
            books_count = len([f for f in os.listdir(books_dir) if not f.startswith(".")]) if os.path.isdir(books_dir) else 0
            return json.dumps({
                "status": "ready", "imprint_id": imprint_id, "vault_total_docs": total_docs,
                "podcast_episodes_synthesized": len(existing_mp3s), "podcast_pending_docs": pending_podcasts,
                "bound_ebooks_count": books_count, "ai_compute": get_active_ai_status(),
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error inspecting publishing readiness: {str(e)}"


class CurateTopicCollectionTool(IllacmeTool):
    """🧭 [Feature: Editorial Chief Agent] 知识星谱与专题成书/播客策展推荐工具"""
    name = "curate_topic_collection"
    description = "Analyze vault categories and knowledge graph clusters to recommend high-value thematic e-book collections and podcast series."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {"type": "object", "properties": {"min_articles": {"type": "integer", "description": "Minimum number of articles in a topic cluster (default 2)."}}, "required": []}

    def execute(self, min_articles: int = 2) -> str:
        try:
            from core.adapters.ai.tools.vault_service import get_secure_vault_path
            from core.utils.text import parse_frontmatter

            vault_path = get_secure_vault_path()
            categories: Dict[str, list] = {}
            for root, _, files in os.walk(vault_path):
                for file in files:
                    if not file.endswith(".md") or file.startswith("."):
                        continue
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, vault_path).replace("\\", "/")
                    parts = rel_p.split("/")
                    cat = parts[0] if len(parts) > 1 else "Root"
                    title, char_len = os.path.splitext(file)[0], 0
                    try:
                        with open(full_p, "r", encoding="utf-8") as f:
                            fm, body, _ = parse_frontmatter(f.read(4096))
                        if isinstance(fm, dict) and fm.get("title"):
                            title = str(fm.get("title"))
                        char_len = len(body)
                    except Exception:
                        pass
                    categories.setdefault(cat, []).append({"rel_path": rel_p, "title": title, "preview_chars": char_len})
            recommendations = []
            for cat, docs in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
                if len(docs) >= max(1, int(min_articles)):
                    top_doc = max(docs, key=lambda d: d["preview_chars"])
                    recommendations.append({
                        "category": cat, "article_count": len(docs),
                        "suggested_book_action": f"bind_digital_book(category='{cat}', format_type='webbook')",
                        "suggested_podcast_lead": top_doc["rel_path"], "articles": [d["rel_path"] for d in docs[:10]],
                    })
            return json.dumps({"curated_collections": recommendations}, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error curating topics: {str(e)}"


class SynthesizePodcastTool(IllacmeTool):
    """🎙️ [Feature: Editorial Chief Agent] 单篇文稿双人对谈播客一键合成工具"""
    name = "synthesize_article_podcast"
    description = "Extract a dual-host dialogue script from a Markdown document and synthesize an MP3 podcast episode (supports zh, en, ja)."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "Relative path of the Markdown document in vault."},
                "lang": {"type": "string", "description": "Target broadcast language: 'zh', 'en', or 'ja'. Default 'zh'."},
                "style": {"type": "string", "description": "Dialogue style: 'tech_deep', 'debate', or 'casual_chat'. Default 'tech_deep'."}
            },
            "required": ["relative_path"]
        }

    def execute(self, relative_path: str, lang: str = "zh", style: str = "tech_deep") -> str:
        try:
            from core.runtime.engine_singleton import get_global_engine
            from core.adapters.ai.tools.vault_service import get_secure_vault_path, fuzzy_match_document
            from core.utils.text import parse_frontmatter
            from core.podcast.podcast_script_engine import PodcastScriptEngine
            from core.podcast.podcast_tts_engine import PodcastTTSEngine

            engine = get_global_engine()
            vault_path = get_secure_vault_path()
            full_path, resolved_rel, err = fuzzy_match_document(vault_path, relative_path)
            if err or not full_path:
                return f"Error: {err or 'Document not found'}"

            with open(full_path, "r", encoding="utf-8") as f:
                fm, body, _ = parse_frontmatter(f.read())

            target_lang = (lang or "zh").lower()
            script = PodcastScriptEngine.extract_script(
                content=body, metadata=fm if isinstance(fm, dict) else {},
                lang=target_lang, style=style or "tech_deep", max_turns=8, use_ai=False, engine=engine
            )
            imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
            cache_dir = getattr(engine, "cache_dir", os.path.join(os.getcwd(), ".plenipes", "cache")) if engine else os.path.join(os.getcwd(), ".plenipes", "cache")
            p_dir = os.path.join(cache_dir, "podcasts", imprint_id)
            os.makedirs(p_dir, exist_ok=True)
            base_stem = os.path.splitext(os.path.basename(resolved_rel))[0]
            slug = os.path.splitext(resolved_rel.replace("\\", "/").strip("/"))[0].lower().replace("/", "__") if (os.path.dirname(resolved_rel) and base_stem.lower() in ("index", "readme")) else base_stem
            filename = f"{slug}_{target_lang}_{style or 'tech_deep'}.mp3"
            out_path = os.path.join(p_dir, filename)

            try:
                asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    res = pool.submit(lambda: asyncio.run(PodcastTTSEngine.synthesize_script(script=script, output_file_path=out_path))).result()
            except RuntimeError:
                res = asyncio.run(PodcastTTSEngine.synthesize_script(script=script, output_file_path=out_path))
            return json.dumps({
                "status": "success", "artifact_type": "podcast", "document": resolved_rel, "title": script.title,
                "filename": filename, "audio_url": f"/api/podcast/audio/{imprint_id}/{filename}",
                "duration_ms": res.duration_ms, "turn_count": res.turn_count, "lang": target_lang
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error synthesizing podcast: {str(e)}"


class BindDigitalBookTool(IllacmeTool):
    """📚 [Feature: Editorial Chief Agent] 数字书籍自动合订与装帧工具"""
    name = "bind_digital_book"
    description = "Assemble and bind a category or single article into a digital book (formats: 'webbook', 'epub', 'pdf', 'docx')."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Category folder in vault (e.g. 'Docs', 'Blog', or 'all')."},
                "format_type": {"type": "string", "description": "Output format: 'webbook', 'epub', 'pdf', or 'docx'. Default 'webbook'."},
                "target_lang": {"type": "string", "description": "Language edition: 'zh', 'en', or 'ja'. Default 'zh'."},
                "single_file": {"type": "string", "description": "Optional relative path for binding a single document."}
            },
            "required": ["category"]
        }

    def execute(self, category: str = "Docs", format_type: str = "webbook", target_lang: str = "zh", single_file: str = "") -> str:
        try:
            from core.runtime.engine_singleton import get_global_engine
            from core.adapters.ai.tools.vault_service import get_secure_vault_path
            from core.bindery.book_assembler import BookAssembler
            from core.bindery.bindery_asset_syncer import resolve_imprint_books_dir

            eng = get_global_engine()
            assembler = BookAssembler(engine=eng, vault_dir=get_secure_vault_path())
            out_file = assembler.assemble_and_bind(
                category=category or "Docs", format_type=(format_type or "webbook").lower(),
                target_lang=(target_lang or "zh").lower(), output_dir=resolve_imprint_books_dir(eng),
                single_file=single_file.strip() or None
            )
            if not out_file:
                return f"Error: No chapters found or failed to bind '{category}' as {format_type}."
            fname = os.path.basename(out_file)
            q_fname = urllib.parse.quote(fname)
            return json.dumps({
                "status": "success", "artifact_type": "ebook", "category": category, "format": format_type,
                "target_lang": target_lang, "output_path": out_file, "filename": fname,
                "download_url": f"/api/bindery/download?file={q_fname}", "preview_url": f"/api/bindery/view?file={q_fname}"
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error binding digital book: {str(e)}"


class DiagnoseDispatchFailuresTool(IllacmeTool):
    """🩺 [Feature: Editorial Chief Agent] 全域分发死信与渠道故障诊断工具"""
    name = "diagnose_dispatch_failures"
    description = "Scan and diagnose failed syndication and hosting dispatch tasks in the dead-letter queue, returning root causes and remediation steps."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_id": {"type": "string", "description": "Optional channel/platform ID filter (e.g. 'wechat', 'devto', 'github_pages')."},
                "rel_path": {"type": "string", "description": "Optional relative document path filter."}
            },
            "required": []
        }

    def execute(self, target_id: str = "", rel_path: str = "") -> str:
        try:
            from core.runtime.engine_singleton import get_global_engine
            from services.api.routes.dispatch_shards.dispatch_overview_aggregator import collect_unified_dead_letter_tasks

            engine = get_global_engine()
            tasks = collect_unified_dead_letter_tasks(engine, limit=25) if engine else []
            if target_id:
                tasks = [t for t in tasks if str(t.get("target_id", "")).lower() == target_id.strip().lower()]
            if rel_path:
                tasks = [t for t in tasks if rel_path.strip().lower() in str(t.get("rel_path", "")).lower()]
            return json.dumps({"status": "success", "failed_count": len(tasks), "failures": tasks}, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error diagnosing dispatch failures: {str(e)}"
