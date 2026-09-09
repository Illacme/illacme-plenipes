#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Deployment Manager
职责：全渠道发布编排器，负责将出版物投递至 S3、CDN、Webhook 等外部端点。
🛡️ [V35.0]：主权隔离分发引擎。
"""

import os
from dataclasses import asdict
from typing import List, Dict, Any
from contextlib import contextmanager
from core.utils.tracing import tlog
from core.governance.license_guard import LicenseGuard
from core.adapters.egress.publishers.base import BasePublisher, PublisherRegistry
import core.adapters.egress.publishers # Trigger loading

@contextmanager
def apply_publisher_proxy(proxy: str = None):
    old_env = {
        "HTTP_PROXY": os.environ.get("HTTP_PROXY"),
        "HTTPS_PROXY": os.environ.get("HTTPS_PROXY"),
        "http_proxy": os.environ.get("http_proxy"),
        "https_proxy": os.environ.get("https_proxy")
    }
    if proxy:
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy
        os.environ["http_proxy"] = proxy
        os.environ["https_proxy"] = proxy
    else:
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)
    try:
        yield
    finally:
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

class DeploymentManager:
    """🚀 [V35.0] 发布编排器：指挥全渠道分发战役"""
    
    def __init__(self, imprint_config: Any):
        self.config = imprint_config
        self.publishers = []
        self._initialize_publishers()

    def _initialize_publishers(self):
        """🚀 [V35.1] 主权加载逻辑：按需点火分发渠道"""
        from core.utils.secret_sentinel import sentinel
        
        # 获取配置对象
        pub_model = getattr(self.config, 'publish_control', None)
        if not pub_model: return
        
        # 🛡️ [V35.2] 强类型兼容并执行凭据解密
        pub_cfg_raw = asdict(pub_model) if hasattr(pub_model, '__dataclass_fields__') else (
            pub_model.model_dump() if hasattr(pub_model, 'model_dump') else pub_model
        )
        
        # 🚀 [V35.2] 深度递归解密：支持 config.imprint.yaml 中的 ENC: 凭据
        def deep_decrypt(d):
            if isinstance(d, dict):
                return {k: deep_decrypt(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [deep_decrypt(i) for i in d]
            elif isinstance(d, str):
                return sentinel.decrypt(d)
            return d

        pub_cfg = deep_decrypt(pub_cfg_raw)

        # 检查商业授权：免费版限制分发渠道数量
        allowed_channels = 99 if LicenseGuard.is_pro_feature_allowed("multi_imprint") else 1
        
        active_count = 0
        # 🚀 [V75.0] 对正：从中心化注册表获取所有发布器类
        publisher_classes = [PublisherRegistry.get_publisher(name) for name in PublisherRegistry.list_active_targets()]
        
        for cls in publisher_classes:
            if not cls: continue
            # 获取插件标识 (如 s3, webhook)
            plugin_id = getattr(cls, "PLUGIN_ID", cls.__name__.lower().replace("publisher", "").replace("plugin", ""))
            
            # 🚀 [V55.25] 深度寻址：优先从 root 读取，否则从 direct_upload 查找
            chan_cfg = pub_cfg.get(plugin_id)
            if not chan_cfg and "direct_upload" in pub_cfg:
                chan_cfg = pub_cfg["direct_upload"].get(plugin_id)
            
            if not chan_cfg:
                chan_cfg = {}

            if chan_cfg.get("enabled"):
                if active_count >= allowed_channels:
                    tlog.warning(f"🛡️ [分发拦截] 免费版限额 ({allowed_channels} 渠道)，已忽略 '{plugin_id}'。")
                    continue
                
                try:
                    # 获取系统配置字典
                    sys_cfg_dict = self.config.system.model_dump() if hasattr(self.config.system, 'model_dump') else asdict(self.config.system)
                    
                    # 注入该品牌的私有配置 (已解密)
                    inst = cls(chan_cfg, sys_config=sys_cfg_dict)
                    self.publishers.append(inst)

                    active_count += 1
                    tlog.info(f"📡 [分发中心] 已激活发布渠道: {plugin_id}")
                except Exception as e:
                    tlog.error(f"❌ [分发中心] 实例化发布插件 {plugin_id} 失败: {e}")

        # 🚀 [主权对正] 按官方主站优先级排序：主站渠道永远排在首位率先投递，备用镜像排在其后
        self._sort_publishers_by_primary()

    def _get_primary_hosting_id(self) -> str:
        """解析当前品牌或全局配置中指定的主站发布渠道 ID"""
        pub_cfg = (self.config.publish_control.model_dump()
                   if hasattr(self.config, 'publish_control') and hasattr(self.config.publish_control, 'model_dump')
                   else getattr(self.config, 'publish_control', {}))
        if not isinstance(pub_cfg, dict):
            pub_cfg = {}
        return pub_cfg.get("primary_hosting_id") or pub_cfg.get("direct_upload", {}).get("primary_hosting_id") or ""

    def _sort_publishers_by_primary(self):
        """将官方主站发布器稳定排在列表第一位"""
        primary_id = self._get_primary_hosting_id()
        if primary_id and self.publishers:
            self.publishers.sort(
                key=lambda pub: 0 if getattr(pub, "PLUGIN_ID", pub.__class__.__name__.lower().replace("publisher", "").replace("plugin", "")) == primary_id else 1
            )

    def deploy_all(self, bundle_path: str, metadata: Dict[str, Any]):
        """执行全渠道同步投递 (事务化汇总，官方主站率先投递)"""
        if not self.publishers:
            tlog.debug("ℹ️ [分发中心] 当前主权品牌未激活任何外部发布渠道。")
            return {"status": "skipped", "reason": "no_active_channels"}

        # 保证投递前再次对齐主站优先顺序
        self._sort_publishers_by_primary()
        primary_hosting_id = self._get_primary_hosting_id()

        tlog.info(f"🚀 [分发中心] 正在向 {len(self.publishers)} 个渠道投递出版资产 (官方主站优先)...")
        results = {"status": "success", "channels": {}}
        
        fail_count = 0
        for pub in self.publishers:
            pub_name = pub.__class__.__name__
            plugin_id = getattr(pub, "PLUGIN_ID", pub_name.lower().replace("publisher", "").replace("plugin", ""))
            is_primary = (plugin_id == primary_hosting_id) or (len(self.publishers) == 1)

            # 注入渠道角色元数据
            chan_meta = dict(metadata) if isinstance(metadata, dict) else {}
            chan_meta["is_primary"] = is_primary
            chan_meta["channel_role"] = "primary" if is_primary else "mirror"

            try:
                # 执行物理发布（应用代理沙盒，保障 CLI/SDK/Requests 代理优先级全部对齐）
                with apply_publisher_proxy(pub.get_proxy()):
                    res = pub.push(bundle_path, chan_meta)
                if isinstance(res, dict) and res.get("status") == "error":
                    err_msg = res.get("message", "未知错误")
                    tlog.error(f"  └── ❌ 渠道 {pub_name} 投递失败: {err_msg}")
                    results["channels"][pub_name] = {"status": "error", "message": err_msg}
                    fail_count += 1
                else:
                    results["channels"][pub_name] = {"status": "success", "response": res}
                    tlog.success(f"  └── ✅ 渠道 {pub_name} 投递成功。")
            except Exception as e:
                tlog.error(f"  └── ❌ 渠道 {pub_name} 投递异常: {e}")
                results["channels"][pub_name] = {"status": "error", "message": str(e)}
                fail_count += 1
        
        if fail_count > 0:
            results["status"] = "partial_success" if fail_count < len(self.publishers) else "failed"

        # 📊 [V90.0] 组织全域分发汇总报告与站点直达链接
        summary = self._build_deployment_summary(results)
        results["summary"] = summary

        # 🛰️ 广播结构化汇总与高亮终端日志
        try:
            from core.utils.event_bus import bus
            bus.emit("UI_TERMINAL_DATA", type="DEPLOY_SUMMARY", data=summary)

            bus.emit("UI_TERMINAL_DATA", type="LOG", data="")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="📊 全域发布统计与站点直达：")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"• 投递渠道：共 {summary['total_channels']} 个渠道 (🟢 成功 {summary['success_count']} / 🔴 失败 {summary['fail_count']})")
            for ch in summary.get("channels", []):
                role = "🏠 [官方主站]" if ch["is_primary"] else "🔄 [备用镜像]"
                if ch["status"] == "success":
                    url_str = f" 👉 访问网址: {ch['url']}" if ch.get("url") else ""
                    bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"• {role} {ch['name']}: 🟢 部署成功{url_str}")
                else:
                    bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"• {role} {ch['name']}: ❌ 投递失败 ({ch.get('error', '未知错误')})")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        except Exception as be:
            tlog.warning(f"⚠️ [分发中心] 广播发布汇总失败: {be}")

        return results

    def _build_deployment_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """📊 [V90.0] 组织结构化的全域发布推送统计与访问网址字典"""
        primary_hosting_id = self._get_primary_hosting_id()

        name_map = {
            "vercel": "Vercel",
            "github_pages": "GitHub Pages",
            "cloudflare_pages": "Cloudflare Pages",
            "netlify": "Netlify",
            "zeabur": "Zeabur",
            "render": "Render",
            "railway": "Railway",
            "gitee_pages": "Gitee Pages",
            "gitlab_pages": "GitLab Pages",
            "firebase": "Firebase Hosting",
            "s3": "AWS S3",
            "sftp": "SFTP / SSH"
        }

        channels_data = results.get("channels", {})
        summary_channels = []
        fail_count = 0
        for pub in self.publishers:
            pub_cls_name = pub.__class__.__name__
            plugin_id = getattr(pub, "PLUGIN_ID", pub_cls_name.lower().replace("publisher", "").replace("plugin", ""))
            ch_data = channels_data.get(pub_cls_name, {})
            status = ch_data.get("status", "unknown")
            if status != "success":
                fail_count += 1
            resp = ch_data.get("response", {}) if isinstance(ch_data.get("response"), dict) else {}
            is_primary = (plugin_id == primary_hosting_id) or (len(self.publishers) == 1 and status == "success")

            # 解析访问 URL
            url = resp.get("url") or resp.get("pages_base_url") or ""
            if plugin_id == "vercel":
                proj = getattr(pub, "project_name", "") or resp.get("project") or ""
                # 若存在 project_name，且为生产模式或权威主站，优先呈现稳定的主域名
                if proj and (is_primary or getattr(pub, "prod", True) or resp.get("mode") == "production"):
                    url = f"https://{proj}.vercel.app/"
            elif not url:
                if plugin_id == "github_pages":
                    owner, repo = getattr(pub, "_parse_owner_repo", lambda: ("", ""))()
                    if owner and repo:
                        url = f"https://{owner}.github.io/{repo}/"
                elif plugin_id == "cloudflare_pages":
                    proj = getattr(pub, "project_name", "")
                    if proj:
                        url = f"https://{proj}.pages.dev/"
                elif plugin_id == "netlify":
                    site_id = getattr(pub, "site_id", "")
                    if site_id:
                        url = f"https://{site_id}.netlify.app/"

            if url and not url.startswith("http://") and not url.startswith("https://"):
                url = f"https://{url}"
            display_name = name_map.get(plugin_id, plugin_id.replace("_", " ").title())

            summary_channels.append({
                "id": plugin_id,
                "name": display_name,
                "status": status,
                "is_primary": is_primary,
                "url": url,
                "error": ch_data.get("message") if status == "error" else ""
            })

        # 主站优先排在前面，成功渠道靠前
        summary_channels.sort(key=lambda x: (not x["is_primary"], x["status"] != "success"))

        total = len(self.publishers)
        success_count = total - fail_count
        return {
            "total_channels": total,
            "success_count": success_count,
            "fail_count": fail_count,
            "channels": summary_channels
        }
