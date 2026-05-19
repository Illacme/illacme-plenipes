#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Governance Routing Map
职责：定义配置项与物理存储层级的映射关系，实现自动化治理。
🚀 [V52.17] 物理主权对正矩阵。
"""

import re

# 🎯 [V52.18] 全息配置治理矩阵 (Sensing vs. Sovereignty)
GOVERNANCE_RULES = {
    # 🔴 本地感应层 (Local: config.local.yaml) - 物理机能、凭据密钥、硬件限制
    "local": [
        r"^translation\.compute_nodes\..*$", # 物理算力节点全量属性 (ID/URL/Key/Type/Model/Enabled)
        r"^publish_control\.webhook_endpoints\..*\.(?!enabled$).*$", # Webhook 物理配置（除激活状态外）
        r"^publish_control\.direct_upload\..*\.(?!enabled$).*$", # 托管平台物理配置（除激活状态外，如 URL/Token/Key/Secret 等）
        r"^syndication\..*\.(?!enabled$).*$", # 聚合平台物理配置（除激活状态外，如 URL/Key/Token/Username/Password 等）
        r"^ingress_settings\.source_options\..*$", # 物理输入源的凭据、密钥与本地绝对路径（如 Notion/Obsidian 等）
        r"^system\.api_token$",            # 系统 API 授权令牌
        r"^system\.serve_host$",           # 本地监听地址
        r"^system\.serve_port$",           # 本地预览端口
        r"^system\.api_host$",             # 本地 API 地址
        r"^system\.api_port$",             # 本地 API 端口
        r"^system\.singleton_port$",       # 本地单例冲突端口
        r"^system\.max_workers$",          # 本地算力并发限制
        r"^system\.log_level$",            # 本地日志详细度
        r"^system\.watchdog_settings\..*$", # 本地监控轮询策略
        r"^plugins\.disabled_plugins$",    # 本机禁用的插件列表
        r"^active_imprint$",               # 本机当前活跃品牌 ID
    ],
    
    # 🔵 品牌主权层 (Imprint: imprints/{id}/configs/config.imprint.yaml) - 品牌意志、策略选择
    "imprint": [
        r"^imprint_name$",                 # 品牌名称
        r"^imprint_description$",          # 品牌介绍
        r"^vault_root$",                   # 品牌原稿物理金库
        r"^metadata_dir$",                  # 品牌治理账本目录
        r"^active_theme$",                 # 品牌视觉风格
        r"^site_url$",                     # 品牌发布域名
        r"^i18n_settings\..*$",            # 品牌多语种版图
        r"^seo_settings\..*$",             # 品牌搜索优化策略
        r"^ingress_settings\..*$",         # 品牌输入感应标准
        r"^image_settings\..*$",           # 品牌资产处理标准
        r"^syndication\..*$",              # 品牌内容聚合策略
        r"^timeline\..*$",                 # 品牌时间轴审计逻辑
        r"^system\.janitor_settings\..*$", # 品牌目录清理规则
        r"^system\.ai_context_purification\..*$", # 品牌 AI 语境清洗策略
        r"^system\.pipeline_steps$",       # 品牌出版管线流程
        r"^plugins\.imprint_disabled_plugins$", # 品牌自愿禁用的插件
        r"^translation\.strategy$",        # 品牌翻译调度逻辑
        r"^translation\.primary_node$",    # 品牌主力算力节点
        r"^translation\.primary_model$",   # 品牌主力执行模型
        r"^translation\.fallback_node$",   # 品牌备用算力节点
        r"^translation\.fallback_model$",  # 品牌备用执行模型
        r"^translation\.llm_concurrency$", # 品牌算力并发控制
        r"^translation\.api_timeout$",     # 品牌算力超时控制
        r"^translation\.max_retries$",     # 品牌算力重试机制
        r"^translation\.max_chunk_size$",  # 品牌算力切片粒度
        r"^translation\.enable_ai$",       # 品牌是否开启 AI 治理
        r"^theme_options\..*$",            # 品牌视觉参数微调
        r"^framework_adapters\..*$",       # 品牌排版框架适配
        r"^frontmatter_.*$",               # 品牌文档标准
        r"^publish_control\.active_webhook_ids$", # 品牌激活的分发节点
        r"^publish_control\.direct_upload\..*$",  # 品牌激活的托管节点
        r"^publish_control\..*$",          # 品牌分发策略控制
        r"^governance\..*$",               # 品牌安全与出版模式
        r"^route_matrix$",                 # 品牌路径路由规则
    ],
    
    # 🟢 系统底座层 (Global: config.yaml) - 缺省蓝图、公共定义
    "global": [
        r"^version$",                      # 内核基准版本
        r"^output_paths\..*$",             # 系统产出路径模板
        r"^publish_control\.webhook_registry\..*$", # 全局分发类型定义
        r"^system\.auto_save_interval$",
        r"^system\.enable_asset_audit$",
        r"^system\.data_root$",            # 全局数据锚点
    ]
}

def resolve_governance_level(field_key: str) -> str:
    """🚀 根据字段路径判定其所属的治理层级，默认为 imprint"""
    for level, patterns in GOVERNANCE_RULES.items():
        for pattern in patterns:
            if re.match(pattern, field_key):
                return level
    return "imprint" # 默认归属于品牌主权

def get_local_config_path() -> str:
    """🚀 获取本地覆盖配置的物理路径"""
    import os
    # 优先使用项目根目录下的 config.local.yaml
    from core.config.config import CONFIG_LOCAL_NAME
    local_path = os.path.join(os.getcwd(), CONFIG_LOCAL_NAME)
    return local_path
