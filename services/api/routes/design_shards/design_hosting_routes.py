# -*- coding: utf-8 -*-
"""
🎨 Design Studio - Image Hosting Routes Shard
职责：提供媒体资产公网图床托管、CDN 链接登记与文库文档外链同步替换服务。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.adapters.image_hosting.targets import IMAGE_HOST_REGISTRY
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter, inject_frontmatter

router = APIRouter()

def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")) -> None:
    """验证 API 访问令牌"""
    engine = get_global_engine()
    if not engine or not getattr(engine, 'config', None) or not getattr(engine.config, 'system', None) or not getattr(engine.config.system, 'api_token', None):
        return
    if x_token != engine.config.system.api_token:
        raise HTTPException(status_code=403, detail="Unauthorized")

class UploadHostingRequest(BaseModel):
    asset_id: Optional[int] = None
    source_url: Optional[str] = None
    provider_id: str = "github"
    sync_references: bool = True

HOSTING_METADATA = {
    "cloudflare_r2": {"name": "Cloudflare R2", "icon": "🟧", "category": "cloud_storage", "desc": "每月 10GB 永久免费存储且 0 出口流量费，支持绑定自有域名"},
    "telegraph": {"name": "Telegraph 自建图床", "icon": "⚡", "category": "self_hosted", "desc": "基于 Cloudflare Pages/Workers 开源部署的 Telegraph-Image 自建图床"},
    "imgbb": {"name": "ImgBB 国际图床", "icon": "🖼️", "category": "free_tier", "desc": "全球老牌免维护图床，支持 1 个 API Key 一键直链"},
    "catbox": {"name": "Catbox 极客图床", "icon": "🐱", "category": "free_tier", "desc": "极客圈老牌永久直链存储，单文件上限 200MB，支持匿名直接上传"},
    "aliyun_oss": {"name": "阿里云 OSS", "icon": "☁️", "category": "cloud_storage", "desc": "国内主流对象存储，高速 CDN 加速"},
    "tencent_cos": {"name": "腾讯云 COS", "icon": "🐧", "category": "cloud_storage", "desc": "稳定高并发云存储，微信生态亲和"},
    "qiniu_kodo": {"name": "七牛云 Kodo", "icon": "🐂", "category": "cloud_storage", "desc": "国内老牌云存储，支持专属加速域名"},
    "upyun_uss": {"name": "又拍云 USS", "icon": "📡", "category": "cloud_storage", "desc": "国内老牌 CDN 存储，支持绑定自定义加速域名"},
    "s3": {"name": "AWS S3 / 兼容 S3", "icon": "🪣", "category": "cloud_storage", "desc": "全球工业级对象存储标准接口"},
    "github": {"name": "GitHub Pages 仓储", "icon": "🐙", "category": "git_repo", "desc": "使用 GitHub 仓库作为图床与 CDN 分发"},
    "superbed": {"name": "聚合图床 (Superbed)", "icon": "🚀", "category": "free_tier", "desc": "免实名轻量图床，支持一键 Token 接入"},
    "lsky_pro": {"name": "兰空图床 (Lsky Pro)", "icon": "🪶", "category": "self_hosted", "desc": "经典开源多存储驱动图床，私有化部署支持"},
    "loli_io": {"name": "路过图床 (loli.io)", "icon": "🌸", "category": "free_tier", "desc": "无需个人云存储，国内访问友好的公共图床"},
    "imgur": {"name": "Imgur 国际图床", "icon": "🌐", "category": "cloud_token", "desc": "海外极高知名度图库，需 Client ID"}
}

def _get_plugin_config(engine: Any, provider_id: str) -> Dict[str, Any]:
    """从引擎配置中提取指定图床插件的凭据参数"""
    if not engine or not hasattr(engine, "config"):
        return {}
    # 1. 优先检查 image_hosting
    ih = getattr(engine.config, "image_hosting", {})
    if isinstance(ih, dict) and isinstance(ih.get(provider_id), dict):
        return ih.get(provider_id)
    # 2. 检查 plugins
    cfg = getattr(engine.config, "plugins", {})
    if isinstance(cfg, dict) and isinstance(cfg.get(provider_id), dict):
        return cfg.get(provider_id)
    # 3. 检查 direct_upload (例如 github_pages)
    pub_ctrl = getattr(engine.config, "publish_control", {})
    if isinstance(pub_ctrl, dict):
        d_up = pub_ctrl.get("direct_upload", {})
        if isinstance(d_up, dict):
            if isinstance(d_up.get(provider_id), dict):
                return d_up.get(provider_id)
            if provider_id == "github" and isinstance(d_up.get("github_pages"), dict):
                gh = d_up.get("github_pages", {})
                if gh.get("token"):
                    return {"token": gh.get("token"), "repo": gh.get("repo_url", "")}
    return {}

@router.get("/api/design/assets/hosting-targets", dependencies=[Depends(verify_token)])
async def get_hosting_targets():
    """获取所有支持的图床列表与当前就绪状态"""
    engine = get_global_engine()
    targets: List[Dict[str, Any]] = []
    
    for pid, host_cls in IMAGE_HOST_REGISTRY.items():
        meta = HOSTING_METADATA.get(pid, {"name": pid.upper(), "icon": "☁️", "category": "cloud", "desc": "扩展图床插件"})
        p_cfg = _get_plugin_config(engine, pid)
        
        # 判定是否就绪
        is_ready = False
        status_label = "待配置"
        if pid == "telegraph":
            ep = p_cfg.get("endpoint", "") if p_cfg else ""
            if ep and "telegra.ph" not in ep:
                is_ready = True
                status_label = "自建节点就绪"
            else:
                is_ready = False
                status_label = "需配置自建节点"
        elif pid == "catbox":
            is_ready = True
            status_label = "匿名上传就绪" if not (p_cfg and any(p_cfg.values())) else "凭证已就绪"
        elif p_cfg and any(p_cfg.values()):
            is_ready = True
            status_label = "凭证已就绪"

        targets.append({
            "id": pid,
            "name": meta["name"],
            "icon": meta["icon"],
            "category": meta["category"],
            "desc": meta["desc"],
            "is_ready": is_ready,
            "status_label": status_label
        })

    # 排序：已就绪排在前面
    targets.sort(key=lambda x: (not x["is_ready"], x["id"]))
    return {"success": True, "targets": targets}

@router.post("/api/design/assets/upload-hosting", dependencies=[Depends(verify_token)])
async def upload_asset_to_hosting(req: UploadHostingRequest):
    """物理上传媒体资产至指定公网图床，并回填 CDN URL"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta") or not getattr(engine.meta, "sqlite", None):
        raise HTTPException(status_code=500, detail="系统元数据引擎未初始化")

    conn = engine.meta.sqlite.get_connection()
    cur = conn.cursor()
    if req.asset_id:
        cur.execute("SELECT id, rel_path, source_url, cdn_url FROM visual_assets WHERE id = ?", (req.asset_id,))
    elif req.source_url:
        cur.execute("SELECT id, rel_path, source_url, cdn_url FROM visual_assets WHERE source_url = ? ORDER BY id DESC LIMIT 1", (req.source_url,))
    else:
        raise HTTPException(status_code=400, detail="缺少 asset_id 或 source_url 参数")
    row = cur.fetchone()
    if not row:
        target_hint = f"ID 为 {req.asset_id}" if req.asset_id else f"URL 为 {req.source_url}"
        raise HTTPException(status_code=404, detail=f"未找到 {target_hint} 的媒体资产")
    asset_id = row[0]

    source_url = row[2] or ""
    filename = os.path.basename(source_url.split("?")[0]) if source_url else ""
    if not filename:
        raise HTTPException(status_code=400, detail="资产文件路径无效")

    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()
    file_path = os.path.join(vault_root, ".plenipes", "cache", "covers", filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), ".plenipes", "cache", "covers", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"本地图片文件未找到: {filename}")

    host_cls = IMAGE_HOST_REGISTRY.get(req.provider_id)
    if not host_cls:
        raise HTTPException(status_code=400, detail=f"不支持的图床引擎: {req.provider_id}")

    p_cfg = _get_plugin_config(engine, req.provider_id)
    sys_tuning = getattr(engine, "config", {})
    if hasattr(sys_tuning, "to_dict"):
        sys_tuning = sys_tuning.to_dict()
    elif not isinstance(sys_tuning, dict):
        sys_tuning = {}

    try:
        host = host_cls(config=p_cfg, sys_tuning=sys_tuning)
        uploaded_url = host.upload(file_path)
    except Exception as e:
        tlog.error(f"❌ [图床托管] 上传异常: {e}")
        raise HTTPException(status_code=502, detail=f"图床上传接口异常: {str(e)}")

    if not uploaded_url:
        raise HTTPException(status_code=502, detail=f"[{req.provider_id.upper()}] 图床上传失败，请检查网络连接或凭证配置")

    # 1. 更新 SQLite 账本的 cdn_url
    cur.execute("UPDATE visual_assets SET cdn_url = ? WHERE id = ?", (uploaded_url, asset_id))
    conn.commit()

    # 2. 如果开启同步，替换原稿中的本地链接
    synced_docs = 0
    if req.sync_references and vault_root and os.path.isdir(vault_root):
        for root, _, files in os.walk(vault_root):
            if ".plenipes" in root or ".git" in root:
                continue
            for f in files:
                if f.endswith(".md"):
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as sf:
                            raw = sf.read()
                        meta, pure, _ = parse_frontmatter(raw)
                        rel_path = os.path.relpath(fp, vault_root).replace("\\", "/")
                        changed = False
                        if meta.get("cover") == source_url or (meta.get("cover") and filename in meta.get("cover")):
                            meta["cover"] = uploaded_url
                            changed = True
                        if changed:
                            new_content = inject_frontmatter(pure, meta)
                            with open(fp, "w", encoding="utf-8") as wf:
                                wf.write(new_content)
                            try:
                                cur.execute("UPDATE documents SET cover = ? WHERE rel_path = ?", (uploaded_url, rel_path))
                                conn.commit()
                            except Exception:
                                pass
                            synced_docs += 1
                    except Exception as e:
                        tlog.warning(f"⚠️ 替换文档 {f} 封面外链异常: {e}")

    tlog.info(f"✨ [图床托管] 资产 #{asset_id} 成功上传至 {req.provider_id} -> {uploaded_url}, 同步原稿: {synced_docs} 篇")
    return {
        "success": True,
        "asset_id": asset_id,
        "cdn_url": uploaded_url,
        "provider": req.provider_id,
        "synced_docs_count": synced_docs
    }
