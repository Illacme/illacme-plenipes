# -*- coding: utf-8 -*-
"""
☁️ Podcast Storage & Diagnostics Routes
职责：提供播客音频向对象存储 CDN 转储、存储状态探测及全网播客发行规范诊断。
🛡️ [SOP-01] 物理行数严格收敛于 300 行以内。
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from core.runtime.engine_singleton import get_global_engine
from core.podcast.podcast_storage_engine import PodcastStorageEngine
from .system import verify_token

router = APIRouter()


class PodcastSyncStorageRequest(BaseModel):
    filename: Optional[str] = Field(default=None, description="要转储的本地 MP3 音频文件名")
    rel_path: Optional[str] = Field(default=None, description="文库相对路径")
    lang: str = Field(default="zh", description="语言代码")
    style: str = Field(default="tech_deep", description="对话风格")
    imprint_id: Optional[str] = Field(default="default", description="品牌标识")
    sync_all: bool = Field(default=False, description="是否一键批量转储当前品牌所有本地 MP3")


@router.get("/api/podcast/storage/status", dependencies=[Depends(verify_token)])
def get_podcast_storage_status() -> Dict[str, Any]:
    """获取当前播客音频 CDN 云存储配置与就绪状态"""
    engine = get_global_engine()
    cfg = PodcastStorageEngine.get_config(engine)
    is_conf = PodcastStorageEngine.is_configured(engine)
    endpoint = PodcastStorageEngine.get_endpoint_url(cfg)

    return {
        "status": "success",
        "configured": is_conf,
        "enabled": bool(cfg.get("enabled", False)),
        "provider": cfg.get("provider", "cloudflare_r2"),
        "bucket": cfg.get("bucket", ""),
        "endpoint_url": endpoint,
        "public_cdn_url": cfg.get("public_cdn_url", ""),
        "path_prefix": cfg.get("path_prefix", "podcasts")
    }


@router.post("/api/podcast/storage/sync", dependencies=[Depends(verify_token)])
def sync_podcast_to_storage(req: PodcastSyncStorageRequest) -> Dict[str, Any]:
    """将指定播客单轨 MP3 物理转储至对象存储桶"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="出版引擎未就绪")

    if not PodcastStorageEngine.is_configured(engine):
        raise HTTPException(
            status_code=400,
            detail="播客云存储尚未在[插件中心]激活或配置完整，请先配置 Bucket 与密钥。"
        )

    # 定位本地物理音频文件（兼容根目录与按品牌子目录隔离结构）
    imprint_id = req.imprint_id or getattr(engine, "imprint_id", "default") or "default"
    base_cache = getattr(engine, "cache_dir", None)
    if not isinstance(base_cache, str) or not base_cache:
        base_cache = os.path.join(getattr(getattr(engine, "config", None), "system", None).data_root if hasattr(getattr(engine, "config", None), "system") else os.getcwd(), ".plenipes", "cache")
    root_pod_dir = os.path.join(base_cache, "podcasts")
    imp_pod_dir = os.path.join(root_pod_dir, imprint_id)

    if req.sync_all:
        cand_dirs = [d for d in (imp_pod_dir, root_pod_dir) if os.path.isdir(d)]
        uploaded = []
        seen = set()
        for d in cand_dirs:
            for fname in sorted(os.listdir(d)):
                if fname.endswith(".mp3") and fname not in seen:
                    seen.add(fname)
                    up_res = PodcastStorageEngine.upload_audio(os.path.join(d, fname), fname, engine)
                    if up_res.get("success"):
                        uploaded.append(up_res)
        return {"status": "success", "synced_count": len(uploaded), "items": uploaded}

    target_filename = req.filename
    if not target_filename and req.rel_path:
        from core.podcast.podcast_models import get_podcast_candidate_slugs, resolve_podcast_slug
        cands = get_podcast_candidate_slugs(rel_path=req.rel_path)
        for c_slug in cands:
            cand_fn = f"{c_slug}_{req.lang}_{req.style}.mp3"
            if os.path.isfile(os.path.join(imp_pod_dir, cand_fn)) or os.path.isfile(os.path.join(root_pod_dir, cand_fn)):
                target_filename = cand_fn
                break
        if not target_filename:
            pod_slug = resolve_podcast_slug(req.rel_path, engine=engine)
            target_filename = f"{pod_slug}_{req.lang}_{req.style}.mp3"

    if not target_filename:
        raise HTTPException(status_code=400, detail="必须提供 filename 或 rel_path 以定位音频。")

    local_path = os.path.join(imp_pod_dir, target_filename)
    if not os.path.isfile(local_path):
        local_path = os.path.join(root_pod_dir, target_filename)
    if not os.path.isfile(local_path):
        raise HTTPException(status_code=404, detail=f"本地未找到音频文件: {target_filename}，请先合成。")

    res = PodcastStorageEngine.upload_audio(local_path, target_filename, engine)
    if not res.get("success"):
        raise HTTPException(status_code=502, detail=res.get("error", "上传对象存储失败"))

    return {
        "status": "success",
        "data": res
    }


@router.get("/api/podcast/diagnostics/{imprint_id}", dependencies=[Depends(verify_token)])
def get_podcast_diagnostics(imprint_id: str) -> Dict[str, Any]:
    """全网播客发行规范诊断：评估专辑元数据、平台接入度与 CDN 加速就绪度"""
    engine = get_global_engine()
    p_cfg = getattr(engine.config, "podcast", {}) if engine and hasattr(engine, "config") else {}
    hub_cfg = p_cfg.get("podcast_hub", {}) if isinstance(p_cfg, dict) else {}
    xyz_cfg = p_cfg.get("podcast_xiaoyuzhou", {}) if isinstance(p_cfg, dict) else {}
    apple_cfg = p_cfg.get("podcast_apple", {}) if isinstance(p_cfg, dict) else {}
    spotify_cfg = p_cfg.get("podcast_spotify", {}) if isinstance(p_cfg, dict) else {}

    checks: List[Dict[str, Any]] = []
    score = 100

    # 1. Show 级专辑基本信息
    has_title = bool(hub_cfg.get("title", "").strip())
    checks.append({"item": "专辑标题", "passed": has_title, "desc": "Apple/Spotify 必填字段"})
    if not has_title: score -= 15

    has_email = bool(hub_cfg.get("email", "").strip())
    checks.append({"item": "官方邮箱", "passed": has_email, "desc": "Apple Podcasts Connect 校验必填"})
    if not has_email: score -= 15

    has_cover = bool(hub_cfg.get("cover_url", "").strip())
    checks.append({"item": "3000px 专辑封面", "passed": has_cover, "desc": "正方形高清专辑封面"})
    if not has_cover: score -= 15

    # 2. 音频 CDN 加速就绪度
    is_cdn = PodcastStorageEngine.is_configured(engine)
    checks.append({"item": "音频专属 CDN 托管", "passed": is_cdn, "desc": "0 出口流量费大文件边缘加速"})
    if not is_cdn: score -= 15

    # 3. 平台绑定状态
    is_xyz = bool(xyz_cfg.get("enabled") and xyz_cfg.get("podcast_id"))
    checks.append({"item": "小宇宙通道", "passed": is_xyz, "desc": "国内中文播客主流受众通道"})

    is_apple = bool(apple_cfg.get("enabled") and apple_cfg.get("apple_id"))
    checks.append({"item": "Apple Podcasts", "passed": is_apple, "desc": "全球播客基准索引目录"})

    is_spotify = bool(spotify_cfg.get("enabled") and spotify_cfg.get("show_id"))
    checks.append({"item": "Spotify for Podcasters", "passed": is_spotify, "desc": "全球流媒体受众通道"})

    # 统计本地已就绪音频期数（优先按品牌子目录隔离）
    base_cache = getattr(engine, "cache_dir", None) or (os.path.join(engine.config.system.data_root, ".plenipes", "cache") if engine and hasattr(getattr(engine, "config", None), "system") else "")
    imp_cache_dir = os.path.join(base_cache, "podcasts", imprint_id) if base_cache else ""
    cache_dir = imp_cache_dir if os.path.isdir(imp_cache_dir) else (os.path.join(base_cache, "podcasts") if base_cache else "")
    ep_count = len([f for f in os.listdir(cache_dir) if f.endswith(".mp3")]) if os.path.isdir(cache_dir) else 0

    return {
        "status": "success",
        "imprint_id": imprint_id,
        "health_score": max(20, score),
        "episodes_ready": ep_count,
        "cdn_accelerated": is_cdn,
        "checks": checks
    }


@router.get("/api/podcast/overview", dependencies=[Depends(verify_token)])
def get_podcast_overview_route() -> Dict[str, Any]:
    """获取发布中心播客分发总览：全台指标、主流播客平台矩阵与已就绪单集货架"""
    engine = get_global_engine()
    imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
    base_dir = getattr(engine, "cache_dir", os.path.join(os.getcwd(), ".plenipes", "cache")) if engine else os.path.join(os.getcwd(), ".plenipes", "cache")
    p_dir = os.path.join(base_dir, "podcasts", imprint_id)

    episodes = []
    total_duration, total_size = 0, 0
    cached_audios = set(os.listdir(p_dir)) if os.path.isdir(p_dir) else set()
    doc_map, pending_docs = {}, []

    if engine and hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
        try:
            from core.podcast.podcast_models import get_podcast_candidate_slugs
            for rp, doc in engine.meta.get_documents_snapshot().items():
                if isinstance(doc, dict):
                    clean_rp = rp.replace("\\", "/").strip("/")
                    s = doc.get("slug")
                    base_n = os.path.splitext(os.path.basename(clean_rp))[0]
                    rel_no_ext = os.path.splitext(clean_rp)[0]
                    rel_slug = rel_no_ext.replace("/", "__") if "/" in rel_no_ext else ""
                    t_val = doc.get("title") or base_n
                    d_entry = {"rel_path": rp, "title": t_val}
                    if rel_slug:
                        doc_map[rel_slug] = d_entry
                    if s:
                        doc_map[str(s)] = d_entry
                    if base_n and (base_n.lower() not in ("index", "readme") or not rel_slug):
                        doc_map[base_n] = d_entry
                    if doc.get("podcast") is True:
                        cands = get_podcast_candidate_slugs(rel_path=rp, explicit_slug=str(s or ""))
                        has_aud = any(f.endswith(".mp3") and any(f.startswith(f"{p}_") for p in cands) for f in cached_audios)
                        if not has_aud:
                            pending_docs.append({"rel_path": rp, "title": t_val, "slug": rel_slug or s or base_n})
        except Exception:
            pass

    if os.path.isdir(p_dir):
        for fname in sorted(cached_audios):
            if not fname.endswith(".mp3"): continue
            fpath = os.path.join(p_dir, fname)
            fsize, mtime = os.path.getsize(fpath), os.path.getmtime(fpath)
            total_size += fsize
            time_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            base_name = os.path.splitext(fname)[0]
            sc_path = os.path.join(p_dir, f"{base_name}.chapters.json")
            chapters, shownotes = [], ""
            if os.path.isfile(sc_path):
                try:
                    with open(sc_path, "r", encoding="utf-8") as sc_f:
                        sc_data = json.load(sc_f)
                        chapters, shownotes = sc_data.get("chapters", []), sc_data.get("shownotes", "")
                except Exception: pass
            duration_sec = int(max((c.get("end_time", 0) for c in chapters), default=0)) if chapters else 0
            if duration_sec <= 0: duration_sec = max(10, int(fsize / (128 * 1024 / 8)))
            total_duration += duration_sec
            mins, secs = divmod(duration_sec, 60)
            matched_title, matched_rel_path = base_name, ""
            for slug, dinfo in doc_map.items():
                if base_name.startswith(f"{slug}_") or base_name == slug:
                    matched_title, matched_rel_path = dinfo["title"], dinfo["rel_path"]
                    break
            lang = next((l for l in ("zh", "en", "ja") if f"_{l}_" in base_name or base_name.endswith(f"_{l}")), "zh")
            style = next((st for st in ("tech_deep", "casual_brief", "debate", "solo_read") if f"_{st}" in base_name), "tech_deep")
            style_names = {"tech_deep": "深度剖析", "casual_brief": "通俗快讯", "debate": "观点交锋", "solo_read": "单人沉浸伴读"}
            episodes.append({
                "filename": fname, "title": matched_title, "rel_path": matched_rel_path,
                "audio_url": f"/api/podcast/audio/{imprint_id}/{fname}", "size_bytes": fsize,
                "size_formatted": f"{fsize / (1024 * 1024):.2f} MB", "duration_seconds": duration_sec,
                "duration_formatted": f"{mins:02d}:{secs:02d}", "chapters_count": len(chapters),
                "chapters": chapters, "shownotes": shownotes, "lang": lang, "style": style,
                "style_label": style_names.get(style, "技术播客"), "updated_at": time_str
            })

    episodes.sort(key=lambda x: x["updated_at"], reverse=True)

    p_cfg = getattr(engine.config, "podcast", {}) if engine and hasattr(engine, "config") else {}
    if not isinstance(p_cfg, dict): p_cfg = {}
    r2_cfg = p_cfg.get("podcast_r2_storage", {})
    r2_active = bool(r2_cfg.get("enabled") and (r2_cfg.get("bucket") or r2_cfg.get("public_cdn_url")))

    site_url = getattr(getattr(engine.config, "compliance", None), "site_url", "http://localhost:43213")
    rss_public_url = f"{site_url.rstrip('/')}/podcast-feed.xml"
    rss_api_url = f"/api/podcast/feed/{imprint_id}"

    total_mins, total_secs = divmod(total_duration, 60)
    dur_display = f"{total_mins} 分 {total_secs} 秒" if total_mins > 0 else f"{total_secs} 秒"

    from services.api.routes.gov.plugin_collector_channels import is_plugin_config_ready
    def _p_stat(pid: str, def_label: str):
        c = p_cfg.get(pid, {}) if isinstance(p_cfg.get(pid), dict) else {}
        ready = is_plugin_config_ready("podcast", pid, c)
        if c.get("enabled") and ready:
            return "active", "🟢 已启用同步"
        if ready:
            return "configured", "🔵 已绑定凭据"
        return "ready", def_label

    platforms = [
        {"id": "podcast_xiaoyuzhou", "name": "小宇宙 (Xiaoyuzhou)", "icon": "🪐", "category": "domestic", "status": _p_stat("podcast_xiaoyuzhou", "RSS 订阅同步")[0], "status_label": _p_stat("podcast_xiaoyuzhou", "RSS 订阅同步")[1], "type": "泛用型播客平台", "desc": "国内中文播客主流受众通道，在创作者后台认领 RSS 订阅源后全自动更新节目单。", "magic_link": "https://podcaster.xiaoyuzhoufm.com/", "magic_label": "小宇宙创作者中心 ↗"},
        {"id": "podcast_apple", "name": "Apple Podcasts", "icon": "🍎", "category": "global", "status": _p_stat("podcast_apple", "全球标准目录")[0], "status_label": _p_stat("podcast_apple", "全球标准目录")[1], "type": "苹果官方播客网络", "desc": "全球播客基准索引目录，提交 RSS 订阅源后覆盖 iOS、macOS 与 CarPlay 全场景听众。", "magic_link": "https://podcastsconnect.apple.com/", "magic_label": "Apple Podcasts Connect ↗"},
        {"id": "podcast_spotify", "name": "Spotify for Podcasters", "icon": "🟢", "category": "global", "status": _p_stat("podcast_spotify", "全球流媒体网络")[0], "status_label": _p_stat("podcast_spotify", "全球流媒体网络")[1], "type": "Spotify 官方平台", "desc": "全球最大音频流媒体平台，通过 Spotify for Podcasters 认领与同步 RSS 节目单。", "magic_link": "https://podcasters.spotify.com/", "magic_label": "Spotify for Podcasters ↗"},
        {"id": "podcast_youtube", "name": "YouTube Podcasts", "icon": "▶️", "category": "global", "status": _p_stat("podcast_youtube", "Google 官方主力")[0], "status_label": _p_stat("podcast_youtube", "Google 官方主力")[1], "type": "视频与音频播客", "desc": "Google 官方主力播客平台，支持在 YouTube Studio 绑定 RSS 自动生成播放列表与单集。", "magic_link": "https://studio.youtube.com/", "magic_label": "YouTube Studio ↗"},
        {"id": "podcast_netease", "name": "网易云音乐播客", "icon": "🎵", "category": "domestic", "status": _p_stat("podcast_netease", "国内主流流媒体")[0], "status_label": _p_stat("podcast_netease", "国内主流流媒体")[1], "type": "网易云音乐创作者", "desc": "年轻一代与技术人文受众核心聚集地，支持在创作者后台认领 RSS 电台自动上架。", "magic_link": "https://music.163.com/st/creator", "magic_label": "网易云创作者中心 ↗"},
        {"id": "podcast_ximalaya", "name": "喜马拉雅 (Ximalaya)", "icon": "📻", "category": "domestic", "status": _p_stat("podcast_ximalaya", "综合音频网络")[0], "status_label": _p_stat("podcast_ximalaya", "综合音频网络")[1], "type": "喜马拉雅主播平台", "desc": "国内综合体量最大的音频流媒体网络，支持主播工作台节目单接入与有声专栏同步。", "magic_link": "https://studio.ximalaya.com/", "magic_label": "喜马拉雅主播工作台 ↗"},
        {"id": "podcast_r2_storage", "name": "音频 CDN 托管 (Audio Storage)", "icon": "☁️", "category": "infrastructure", "status": "active" if r2_active else "unconfigured", "status_label": "CDN 边缘加速" if r2_active else "待配置", "type": "对象存储 CDN", "desc": "为大体积播客 MP3 提供专用对象存储与 CDN 边缘加速（支持 Cloudflare R2 / AWS S3 / 阿里云 OSS / 腾讯云 COS），免除源站带宽压力并享 0 出口流量费。", "magic_link": "", "magic_label": "配置存储桶 ↗"}
    ]

    return {
        "status": "success", "imprint_id": imprint_id,
        "metrics": {
            "total_episodes": len(episodes), "pending_episodes": len(pending_docs),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": dur_display, "total_size_bytes": total_size,
            "total_size_formatted": f"{total_size / (1024 * 1024):.2f} MB",
            "rss_public_url": rss_public_url, "rss_api_url": rss_api_url,
            "r2_storage_active": r2_active
        },
        "platforms": platforms, "episodes": episodes, "pending_docs": pending_docs
    }
