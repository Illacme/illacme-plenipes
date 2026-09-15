# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Provider Configuration Manager
职责：生图引擎凭证持久化、敏感词脱敏、与算力基座同源凭据智能探测。
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import os
import yaml
from typing import Dict, Any, Optional
from core.utils.tracing import tlog
from core.runtime.engine_singleton import get_global_engine

CONFIG_LOCAL_PATH = "config.local.yaml"

class ProviderConfigManager:
    """生图模型凭证管理中枢"""

    @classmethod
    def _load_local_yaml(cls) -> Dict[str, Any]:
        if not os.path.exists(CONFIG_LOCAL_PATH):
            return {}
        try:
            with open(CONFIG_LOCAL_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            tlog.warning(f"⚠️ [ProviderConfig] 读取本地配置异常: {e}")
            return {}

    @classmethod
    def _save_local_yaml(cls, data: Dict[str, Any]) -> bool:
        try:
            with open(CONFIG_LOCAL_PATH, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            tlog.error(f"🛑 [ProviderConfig] 写入本地配置失败: {e}")
            return False

    @classmethod
    def get_all_configs(cls, mask_secrets: bool = True) -> Dict[str, Any]:
        """获取所有已持久化的生图提供商配置"""
        data = cls._load_local_yaml()
        providers_cfg = data.get("image_providers", {}) or {}
        if not mask_secrets:
            return providers_cfg

        masked = {}
        for pid, cfg in providers_cfg.items():
            if not isinstance(cfg, dict):
                continue
            item = dict(cfg)
            for k in ["api_key", "password", "secret", "access_key"]:
                if k in item and item[k] and len(str(item[k])) > 6:
                    raw = str(item[k])
                    item[k] = f"{raw[:3]}****{raw[-3:]}"
            masked[pid] = item
        return masked

    @classmethod
    def get_provider_config(cls, provider_id: str, mask_secrets: bool = False) -> Dict[str, Any]:
        """获取指定提供商的真实或脱敏配置"""
        all_cfgs = cls.get_all_configs(mask_secrets=mask_secrets)
        return all_cfgs.get(provider_id, {})

    @classmethod
    def save_provider_config(cls, provider_id: str, new_cfg: Dict[str, Any]) -> bool:
        """保存并合并提供商配置，防止脱敏字符串覆盖真实密钥"""
        data = cls._load_local_yaml()
        if "image_providers" not in data:
            data["image_providers"] = {}

        current_cfg = data["image_providers"].get(provider_id, {}) or {}
        merged = dict(current_cfg)

        for k, v in new_cfg.items():
            # 🛡️ 敏感词防覆盖：如果是掩码占位符则保留真实旧值
            if isinstance(v, str) and "****" in v:
                continue
            merged[k] = v

        data["image_providers"][provider_id] = merged
        success = cls._save_local_yaml(data)
        if success:
            tlog.info(f"✨ [ProviderConfig] 生图提供商 [{provider_id}] 配置已持久化")
        return success

    @classmethod
    def detect_suggested_credentials(cls, provider_id: str = "openai") -> Dict[str, Any]:
        """从算力中心自动探测同源已配置的凭据 (支持 openai/flux/zhipu/imagen)"""
        engine = get_global_engine()
        suggested = {"available": False, "node_name": "", "base_url": "", "api_key_masked": "", "raw_node_id": ""}
        if not engine or not getattr(engine, "config", None):
            return suggested

        ai_cfg = getattr(engine.config, "ai", None)
        if not ai_cfg or not getattr(ai_cfg, "nodes", None):
            return suggested

        p_lower = (provider_id or "openai").lower()
        target_keys = ["openai"]
        if p_lower == "flux":
            target_keys = ["siliconflow", "silicon", "flux", "openai"]
        elif p_lower == "zhipu":
            target_keys = ["zhipu", "glm", "bigmodel"]
        elif p_lower == "imagen":
            target_keys = ["gemini", "google", "imagen"]

        matched_node = None
        matched_id = ""
        for node_id, node in ai_cfg.nodes.items():
            ntype = str(getattr(node, "type", "")).lower()
            nid = str(node_id).lower()
            for tk in target_keys:
                if tk in ntype or tk in nid:
                    matched_node = node
                    matched_id = node_id
                    break
            if matched_node:
                break

        if matched_node:
            api_key = getattr(matched_node, "api_key", "")
            base_url = getattr(matched_node, "base_url", "")
            masked = f"{api_key[:3]}****{api_key[-3:]}" if len(api_key) > 6 else ("******" if api_key else "")
            suggested["available"] = bool(api_key)
            suggested["has_openai"] = bool(api_key)  # 保持旧字段兼容
            suggested["node_name"] = matched_id
            suggested["base_url"] = base_url
            suggested["api_key_masked"] = masked
            suggested["raw_node_id"] = matched_id
        return suggested

    @classmethod
    def import_credentials_from_compute_node(cls, provider_id: str, node_id: str) -> bool:
        """一键从指定算力节点导入凭据至生图提供商"""
        engine = get_global_engine()
        if not engine or not getattr(engine, "config", None):
            return False
        ai_cfg = getattr(engine.config, "ai", None)
        if not ai_cfg or not getattr(ai_cfg, "nodes", None):
            return False

        node = ai_cfg.nodes.get(node_id)
        if not node:
            return False

        p_lower = provider_id.lower()
        default_model = "dall-e-3"
        default_base = getattr(node, "base_url", "")
        if p_lower == "flux":
            default_model = "black-forest-labs/FLUX.1-schnell"
            default_base = default_base or "https://api.siliconflow.cn/v1"
        elif p_lower == "zhipu":
            default_model = "cogview-3-plus"
            default_base = default_base or "https://open.bigmodel.cn/api/paas/v4"
        elif p_lower == "imagen":
            default_model = "gemini-2.5-flash-image"
            default_base = default_base or "https://generativelanguage.googleapis.com/v1beta"
        else:
            default_base = default_base or "https://api.openai.com/v1"

        cfg = {
            "api_key": getattr(node, "api_key", ""),
            "base_url": default_base,
            "model": default_model
        }
        return cls.save_provider_config(provider_id, cfg)
