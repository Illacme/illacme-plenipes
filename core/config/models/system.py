#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - System Models
职责：定义引擎并发、韧性、看门狗及全局路径。
🛡️ [V24.0] Pydantic 严格校验体系：实现全量配置审计与物理红线保护。
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from .base import LogFormat

class NetworkSettings(BaseModel):
    ignored_domains: List[str] = Field(default_factory=lambda: ["img.shields.io"])
    asset_prober_ua: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    prober_cooling_delay: float = Field(0.1, ge=0)

class ConcurrencySettings(BaseModel):
    global_workers: int = Field(2, ge=1, le=64)
    ai_workers: int = Field(4, ge=1, le=128)
    min_ai_workers: int = Field(2, ge=1)
    audit_workers: int = Field(10, ge=1)
    io_workers: int = Field(8, ge=1)

class ResilienceSettings(BaseModel):
    cb_failure_threshold: int = Field(5, ge=1)
    cb_recovery_timeout: int = Field(60, ge=1)
    db_timeout: float = Field(30.0, ge=1)
    ai_semaphore_timeout: int = Field(60, ge=1)
    api_retry_delay: float = Field(1.0, ge=0)
    network_timeout: int = Field(5, ge=1)
    heartbeat_timeout: float = Field(5.0, ge=1)
    asset_ping_timeout: int = Field(3, ge=1)

class ThrottleSettings(BaseModel):
    timeline_write_delay: float = Field(5.0, ge=0)
    ai_block_delay: float = Field(0.2, ge=0)
    api_response_delay: float = Field(0.5, ge=0)

class WatchdogSettings(BaseModel):
    exclude_dirs: List[str] = Field(default_factory=lambda: [".git", "node_modules"])
    exclude_patterns: List[str] = Field(default_factory=lambda: [".lock", ".tmp"])
    heavy_task_delay: float = Field(0.8, ge=0)
    gc_delay: float = Field(5.0, ge=0)
    handover_delay: float = Field(1.5, ge=0)

class JanitorSettings(BaseModel):
    global_exclude: List[str] = Field(default_factory=lambda: [".git", "node_modules", "dist"])
    theme_exclude: Dict[str, List[str]] = Field(default_factory=dict)

class PurificationSettings(BaseModel):
    strip_styles: bool = True
    strip_mdx_imports: bool = True
    strip_comments: bool = True
    strip_code_blocks: bool = True
    strip_jsx_tags: bool = True
    protect_jsx: bool = True
    protect_html: bool = True
    protect_latex: bool = True
    custom_patterns: List[str] = Field(default_factory=list)

class ResourceGuardSettings(BaseModel):
    """🛡️ [V24.6] 物理负载卫士设置集"""
    enabled: bool = True
    cpu_threshold: float = Field(85.0, ge=10.0, le=100.0)
    ram_threshold: float = Field(85.0, ge=10.0, le=100.0)
    check_interval: float = Field(5.0, ge=1.0)

class GovernanceSettings(BaseModel):
    """🚀 [V24.6] 全局治理矩阵"""
    resource_guard: ResourceGuardSettings = Field(default_factory=ResourceGuardSettings)

class SafetyPolicy(BaseModel):

    """🛡️ [V16.8] 系统安全与物理红线政策库"""
    min_ai_workers: int = Field(2, ge=1)
    singleton_port: int = Field(43210, ge=1024, le=65535)
    network_timeout: float = Field(30.0, ge=1)
    config_audit_severity: str = "WARN"

class SystemSettings(BaseModel):
    """🚀 [V24.0] 系统全域配置主权"""
    data_root: str = "."

    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.RICH
    verbose_ai_logs: bool = True
    serve_host: str = "127.0.0.1"
    serve_port: int = Field(43212, ge=1024, le=65535)
    singleton_port: int = Field(43210, ge=1024, le=65535)
    api_host: str = "0.0.0.0"
    api_port: int = Field(43211, ge=1024, le=65535)
    api_token: str = ""
    
    max_workers: int = Field(4, ge=1)
    auto_save_interval: float = Field(2.0, ge=0.5)
    max_depth: int = Field(3, ge=1)
    enable_asset_audit: bool = True
    typing_idle_threshold: float = Field(0.5, ge=0.1)
    headless: bool = False
    
    index_filenames: List[str] = Field(default_factory=lambda: ["index.md", "readme.md", "index.mdx"])
    allowed_extensions: List[str] = Field(default_factory=lambda: [".md", ".mdx", ".markdown", ".mdown", ".txt"])
    mask_pattern: str = r"<!\[CDATA\[.*?\]\]>|<!--.*?-->|<script.*?>.*?</script>|<style.*?>.*?</style>|```.*?```|`[^`\n]+`|\[\[[^\]]+\]\]|\!\[\[[^\]]+\]\]|\!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)"
    
    logs_dir: str = "logs"
    sandbox_dir: str = "sandbox"
    data_paths: Dict[str, str] = Field(default_factory=lambda: {
        "sync_stats": "sync_stats_{theme}.json",
        "link_graph": "link_graph_{theme}.json",
        "usage_ledger": "usage_ledger_{theme}.json",
        "search_index": "search_index_{theme}.json",
        "health_log": "sentinel_health.json",
        "timeline_json": "timeline_{theme}.json",
        "vectors_json": "vectors_{theme}.json",
        "pulse_json": "pulse_{theme}.json",
        "quotas_json": "quotas.json"
    })
    
    network_settings: NetworkSettings = Field(default_factory=NetworkSettings)
    safety_policy: SafetyPolicy = Field(default_factory=SafetyPolicy)
    
    concurrency: ConcurrencySettings = Field(default_factory=ConcurrencySettings)
    resilience: ResilienceSettings = Field(default_factory=ResilienceSettings)
    throttle: ThrottleSettings = Field(default_factory=ThrottleSettings)
    watchdog_settings: WatchdogSettings = Field(default_factory=WatchdogSettings)
    janitor_settings: JanitorSettings = Field(default_factory=JanitorSettings)
    ai_context_purification: PurificationSettings = Field(default_factory=PurificationSettings)
    governance: GovernanceSettings = Field(default_factory=GovernanceSettings)
    pipeline_steps: List[str] = Field(default_factory=lambda: [
        "read_normalize",
        "purify",
        "metadata_hash",
        "ai_slug_seo",
        "semantic_linker",
        "masking_routing",
        "verification"
    ])


