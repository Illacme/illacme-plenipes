# -*- coding: utf-8 -*-
"""
🛡️ [V74.97] Gov Plugin Dry Run Social Shard Facade
职责：分发渠道类插件（海外与国内主流社交/博客平台）的真实 API 凭证有效性探测与代理路由分发门面。
架构：已按照 SOP-02 物理降解为 social_shards/*，主文件作为轻量分发门面。
"""

from typing import Dict, Any, List
from .social_shards.social_domestic import probe_domestic_social
from .social_shards.social_global import probe_global_social

DOMESTIC_SOCIAL_PLUGINS = {
    "wechat",
    "zhihu",
    "juejin",
    "xiaohongshu",
    "red",
    "toutiao",
    "csdn",
    "cnblogs",
    "bilibili",
    "segmentfault",
    "oschina"
}


def run_social_plugin_dry_run(
    plugin_id: str,
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any
) -> bool:
    """
    🚀 物理测试分发渠道类托管通道连接性
    """
    # 提取网络代理（大部分海外分发平台必须使用代理）
    proxy_url = settings.get("proxy") or ""
    proxies = {}
    if proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        logs.append(log_func("INFO", f"🌐 [代理] 已装载本地网络通道代理: {proxy_url}"))

    if plugin_id in DOMESTIC_SOCIAL_PLUGINS:
        return probe_domestic_social(plugin_id, settings, logs, log_func, proxies)

    return probe_global_social(plugin_id, settings, logs, log_func, proxies)
