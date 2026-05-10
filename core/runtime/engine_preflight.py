#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Engine Preflight Coordinator
模块职责：负责引擎启动前的环境准备、主权路径锚定、契约校验与视觉 Banner 渲染。
🛡️ [AEL-Iter-v10.3]：将启动前置逻辑从工厂类中物理隔离，确保物理主权合规。
"""

import os
import sys
from core.utils.event_bus import bus
from core.utils.tracing import tlog
from core.governance.sentinel import SentinelManager
from core.governance.contract_guard import ContractGuard

from core.config.config import IMPRINT_DIR, METADATA_DIR, THEMES_DIR

class EnginePreflight:
    # 🛡️ [V50.3] 主权物理布局协议 (唯一真理源)
    SOVEREIGN_LAYOUT = {
        "metadata": METADATA_DIR,
        "metadata_core": f"{METADATA_DIR}/core",
        "metadata_ai": f"{METADATA_DIR}/ai",
        "metadata_ai_vectors": f"{METADATA_DIR}/ai/vectors",
        "metadata_ai_brain": f"{METADATA_DIR}/ai/brain",
        "metadata_themes": f"{METADATA_DIR}/themes",
        "metadata_runtime": f"{METADATA_DIR}/runtime",
        "cache": f"{METADATA_DIR}/runtime/cache",
        "logs": f"{METADATA_DIR}/runtime/logs",
        "themes": THEMES_DIR
    }

    @staticmethod
    def perform_preflight(config, imprint_id: str = "default", args=None):
        """🚀 执行起飞前全量审计与点火准备"""
        
        # 1. 🚀 [V53.0] 统一主权对正：使用 ConfigManager 执行 3 层深度合并 (Global < Imprint < Local)
        from core.config.config import load_config
        config_path = config if isinstance(config, str) else getattr(config, 'config_path', 'config.yaml')
        config = load_config(config_path, imprint_id=imprint_id)

        # 2. 🚀 [V8.0] 激活物理安全底座
        from core.governance.secret_manager import secrets
        secrets.initialize()
        
        # 🛡️ [V50.5] 主权账本物理隔离：强制锚定在品牌领土内
        from core.governance.audit_ledger import initialize_ledger
        imprint_dir = os.path.join(IMPRINT_DIR, imprint_id)
        if not os.path.exists(imprint_dir): os.makedirs(imprint_dir, exist_ok=True)
        
        # 🚀 [V55.26] 建立全量物理布局矩阵
        for _, rel_path in EnginePreflight.SOVEREIGN_LAYOUT.items():
            os.makedirs(os.path.join(imprint_dir, rel_path), exist_ok=True)

        audit_rel_path = config.get_audit_db_path()
        audit_path = os.path.join(imprint_dir, audit_rel_path)
        initialize_ledger(audit_path)

        # 🛡️ [V53.0] 品牌主权路径与环境对正
        if imprint_id and imprint_id != "default":
            imprint_path = os.path.join(IMPRINT_DIR, imprint_id)
            
            # 🚀 [V53.0] 出版模式智能推断：根据实际配置自动推导最佳模式
            gov_cfg = config.governance
            explicit_mode = gov_cfg.publishing_mode
            
            # 检测 AI 就绪性 (基于合并后的配置)
            ai_ready = False
            local_types = ["ollama", "lmstudio", "local"]
            compute_nodes = config.translation.compute_nodes or {}
            
            for node_id, node_cfg in compute_nodes.items():
                node_type = (getattr(node_cfg, "type", "") or "").lower()
                api_key = getattr(node_cfg, "api_key", "") or ""
                # 本地模型无需 API Key
                if any(t in node_type for t in local_types):
                    ai_ready = True
                    break
                # 远程模型需有效 API Key
                if len(str(api_key)) > 10 and "your" not in str(api_key).lower():
                    ai_ready = True
                    break
            
            # 智能推断逻辑
            from core.config.models.governance import PublishingMode, SeoStrategy
            
            # 如果配置仍为默认/空，或者需要根据算力状态进行安全校验
            if not ai_ready:
                if explicit_mode in (PublishingMode.ENHANCED, PublishingMode.GLOBAL):
                    config.governance.publishing_mode = PublishingMode.BASIC
                    config.governance.seo_strategy = SeoStrategy.HEURISTIC
                    tlog.warning("⚠️ [模式降级] 未检测到可用 AI 算力，品牌模式已自动降级至 basic")
            
            # 🚀 [V53.0] 模式联动：基础模式自动禁用 AI 算力
            if config.governance.publishing_mode == PublishingMode.BASIC:
                config.translation.enable_ai = False
                tlog.info("📜 [基础模式] AI 算力已自动离线，使用物理规则引擎")

            # 强制 data_root 锚定到品牌目录
            if not config.system:
                config.system = type('SystemConfig', (), {'data_root': imprint_path})()
            else:
                config.system.data_root = imprint_path
            
            tlog.debug(f"🛰️ [主权对正] 引擎数据根部已强制锚定至: {imprint_path}")
        else:
            # default 品牌也需要基本的 data_root
            if config.system:
                if not config.system.data_root:
                    config.system.data_root = ".plenipes"

        # 5. 🚀 [审计逻辑] 契约校验
        violations = ContractGuard.verify_config(config)
        if violations and any("❌" in v for v in violations):
            sys.stderr.write("\n🚨 [CONTRACT VIOLATION] 引擎启动契约校验失败：\n")
            for v in violations:
                sys.stderr.write(f"  {v}\n")
            sys.stderr.flush()
            return None

        # 6. 🚀 [V50.3] 视觉主权：Banner 抢占式渲染
        from core.ui.delegate import DisplayDelegate
        sys_version = DisplayDelegate.get_system_version(config)
        
        # 探测最新迭代 ID
        from core import __version__
        history_dir = os.path.join(imprint_dir, EnginePreflight.SOVEREIGN_LAYOUT["metadata"], "history")
        current_iter_id = f"V{__version__}_Final"
        if os.path.exists(history_dir):
            iters = [d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))]
            if iters:
                current_iter_id = sorted(iters)[-1]

        # 探测 Sentinel 状态
        config_path = getattr(config, 'config_path', 'config.yaml')
        config_name = os.path.basename(config_path)
        base, ext = os.path.splitext(config_name)
        local_name = f"{base}.local{ext}"
        local_path = os.path.join(os.path.dirname(os.path.abspath(config_path)), local_name)
        sentinel_info = f"双向热监听 ({config_name} + {local_name})" if os.path.exists(local_path) else f"标准热监听 ({config_name})"
        
        bus.emit("UI_BANNER",
                 version=sys_version,
                 ael_iter_id=current_iter_id,
                 mode=DisplayDelegate.get_banner_mode(config, args),
                 sentinel_status=sentinel_info)

        # 8. 🚀 [V53.1] 算力意志冲突审计：核验品牌节点在本地的感应状态
        if config.translation.enable_ai:
            primary = config.translation.primary_node
            fallback = config.translation.fallback_node
            compute_nodes = config.translation.compute_nodes
            
            for node_role, node_id in [("主力", primary), ("备用", fallback)]:
                if not node_id or node_id == "default": continue
                
                node_cfg = compute_nodes.get(node_id)
                if not node_cfg:
                    tlog.warning(f"🛑 [意志冲突] 品牌指定的{node_role}节点 '{node_id}' 在本地物理层中未定义！系统将陷入算力黑洞。")
                else:
                    # 检查密钥 (本地模型不需要 key)
                    is_local = any(kw in (getattr(node_cfg, 'type', '') or '').lower() for kw in ['local', 'ollama', 'lmstudio'])
                    if not is_local and not getattr(node_cfg, 'api_key', ''):
                        tlog.warning(f"🛑 [物理缺失] 品牌{node_role}节点 '{node_id}' 缺少本地 API Key，请在算力底座中完成物理挂载。")

        # 8. 🚀 [V16.0] 插件化基座点火
        from core.markup.manager import MarkupManager
        from core.ingress.manager import IngressManager
        plugin_settings = getattr(config, 'plugins', None)
        MarkupManager.initialize(plugin_settings)
        IngressManager.initialize(plugin_settings)

        return config
