# -*- coding: utf-8 -*-
"""
🛡️ [V74.96] Gov Plugin Dry Run Hosting Shard Facade
职责：全站托管类插件的物理通道连接测试与 API 握手探测分发门面。
架构：已按照 SOP-02 物理降解为 hosting_shards/*，主文件作为轻量分发门面。
"""

from typing import Dict, Any, List
from .hosting_shards.hosting_git import probe_git_hosting
from .hosting_shards.hosting_cloud import probe_cloud_hosting

GIT_HOSTING_PLUGINS = {"github_pages", "gitee_pages", "gitlab_pages"}


def run_hosting_plugin_dry_run(
    plugin_id: str,
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any
) -> bool:
    """
    🚀 物理测试全站托管通道的真实网络可达性与 API 凭证有效性
    """
    # 提取网络代理（部分托管平台在国内需要代理）
    proxy_url = settings.get("proxy") or ""
    proxies = {}
    if proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        logs.append(log_func("INFO", f"🌐 [代理] 已装载本地网络通道代理: {proxy_url}"))

    # 动态感应治理中心配置的第三方 API 超时时间 (默认 15s)
    try:
        from core.config.config_models import load_config
        sys_cfg = load_config()
        net_timeout = getattr(getattr(sys_cfg, "system", None), "network_timeout", 15) or 15
    except Exception:
        net_timeout = 15

    if plugin_id in GIT_HOSTING_PLUGINS:
        return probe_git_hosting(plugin_id, settings, logs, log_func, proxies, net_timeout)
    
    return probe_cloud_hosting(plugin_id, settings, logs, log_func, proxies)
