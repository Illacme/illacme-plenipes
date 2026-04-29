#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Payload Manager
模块职责：负责 AI 请求载荷的组装与工业级审计。
"""

from typing import Dict, Any, Optional
from core.utils.tracing import tlog

class PayloadManager:
    """🚀 [V10.3] 载荷驱动引擎：组装并审计中立意图对象"""

    @staticmethod
    def prepare_payload(adapter, system_prompt: str, user_content: str, is_json: bool = False, payload_max_tokens: int = None) -> Dict[str, Any]:
        """🚀 [AEL-Iter-v10.3] 组装中立意图对象 (Neutral Intent Object)"""
        # 1. 获取全要素智能特性
        safe_system = system_prompt or ""
        is_probe = "OracleProbe" in safe_system

        intelligent_payload = adapter._intelligence_hub.get_intelligent_payload(
            adapter.config,
            adapter.plugin_id if hasattr(adapter, 'plugin_id') else 'openai',
            ai_client=adapter if not is_probe else None,
            is_json=is_json
        )

        # 2. 构造意图对象
        intent = {
            "model": adapter.config.model,
            "system": system_prompt,
            "user": user_content,
            "is_json": is_json,
            "params": {
                **intelligent_payload,
                "temperature": getattr(adapter.config, 'temperature', 0.2),
                "max_tokens": payload_max_tokens or getattr(adapter.config, 'max_tokens', 4096),
                **getattr(adapter.config, 'params', {}),
            }
        }

        # 3. 物理审计
        PayloadManager.audit_payload_logic(adapter.node_name, adapter.config, intent)

        return intent

    @staticmethod
    def audit_payload_logic(node_name: str, config, intent: Dict[str, Any]):
        """[Sovereignty] 物理审计：在发送前分析载荷是否合理"""
        audit_path = []
        is_json = intent.get("is_json", False)
        system_prompt = intent.get("system", "") or ""
        params = intent.get("params", {})

        # 1. 验证 JSON 模式一致性
        if is_json and "JSON" not in system_prompt:
            audit_path.append("⚠️ [语义不一致] 开启了 JSON 模式但提示词中未显式要求 JSON")

        # 2. 算力预算审计
        max_tokens = params.get("max_tokens", 4096)
        safe_system = system_prompt.lower() if system_prompt else ""
        if max_tokens > 2000 and "translate" in safe_system:
            audit_path.append("💡 [算力建议] 翻译任务建议压减 max_tokens 以节省开销")

        # 3. 本地环境优化审计
        base_url = getattr(config, 'base_url', '')
        safe_url = base_url.lower() if base_url else ""
        if "localhost" in safe_url or "127.0.0.1" in safe_url:
            if max_tokens > 2000:
                audit_path.append("🔋 [负载建议] 本地模型建议适当减小 max_tokens 以降低推理时延")

        # 4. 输出审计结论
        if audit_path:
            tlog.info(f"🛡️ [算力载荷预检] Node: {node_name} | { ' | '.join(audit_path) }")

    @staticmethod
    def format_prompt(template: str, **kwargs) -> str:
        """🚀 [V10.4] 提示词格式化 engine：支持动态占位符注入"""
        if not template: return ""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            tlog.warning(f"⚠️ [提示词格式化缺失占位符]: {e} | Template: {template[:50]}...")
            return template
        except Exception as e:
            tlog.error(f"🚨 [提示词格式化崩溃]: {e}")
            return template

    @staticmethod
    def get_merged_params(adapter, **overrides) -> Dict[str, Any]:
        """🚀 [V10.0] 智能参数合并引擎：Archetype -> Global -> Node -> Explicit"""
        # 1. 厂商原型默认值 (由子类实现)
        params = adapter.get_archetype_params()

        # 2. 全局通用默认值 (如 temperature, max_tokens)
        global_map = {
            'temperature': getattr(adapter.trans_cfg, 'temperature', 0.2),
            'max_tokens': getattr(adapter.trans_cfg, 'max_tokens', 8192)
        }
        params.update({k: v for k, v in global_map.items() if v is not None})

        # 3. 节点特定配置 (来自 YAML 的 params 字段)
        if adapter.config.params:
            params.update(adapter.config.params)

        # 4. 显式覆盖参数 (方法调用时传入)
        params.update(overrides)

        # 🛡️ 参数正向拦截与纠偏
        if 'temperature' in params:
            params['temperature'] = max(0.0, min(1.0, params['temperature']))

        return params
