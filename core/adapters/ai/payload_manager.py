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
    def prepare_payload(adapter, system_prompt: str, user_content: str, is_json: bool = False, payload_max_tokens: int = None, tools: list = None, messages: list = None) -> Dict[str, Any]:
        """🚀 [AEL-Iter-v75.0] 组装中立意图对象 (新增 tools 和 messages 大一统字段)"""
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
            "messages": messages or [],
            "tools": tools or [],
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

    @staticmethod
    def align_and_clean_payload(model_name: str, payload: Dict[str, Any], adapter=None) -> Dict[str, Any]:
        """
        🏢 智能大模型参数清洗与兼容网关 (Sovereign Parameter Cleansing & Alignment Gateway)
        负责针对不同厂商的大模型 (OpenAI o1/o3-mini, DeepSeek-R1, Local/LMStudio 等)
        进行入参格式校验、智能降级、物理剔除和格式化对齐，防止服务端抛出 400 Bad Request。
        """
        import copy
        cleaned = copy.deepcopy(payload)
        model_lower = model_name.lower()
        
        # 1. 识别算力节点属性与适配器来源
        ac_name = ""
        url = ""
        if adapter:
            ac_name = adapter.__class__.__name__
            url = getattr(adapter, "safe_get_url", lambda: "")().lower()
        
        is_lmstudio = "lmstudio" in ac_name.lower() or "localhost" in url or "127.0.0.1" in url
        is_openai_official = "openai" in ac_name.lower() and not is_lmstudio
        is_o_series = "o1" in model_lower or "o3" in model_lower
        
        # 获取现有的 params
        params = cleaned.get("params", {}) if "params" in cleaned else cleaned
        
        # 2. 针对 OpenAI o1/o3 推理模型进行深度参数对正
        if is_o_series:
            # o1/o3 不支持非 1.0 (或不能显式设定 temperature != 1.0)，删除 temperature 最为稳妥
            if "temperature" in params:
                del params["temperature"]
            if "temperature" in cleaned:
                del cleaned["temperature"]
                
            # o1/o3 废弃了 max_tokens，强推 max_completion_tokens
            if "max_tokens" in params:
                params["max_completion_tokens"] = params.pop("max_tokens")
            if "max_tokens" in cleaned:
                cleaned["max_completion_tokens"] = cleaned.pop("max_tokens")
                
            # 整理 system/developer 消息角色兼容性
            messages = cleaned.get("messages", [])
            if messages:
                for idx, msg in enumerate(messages):
                    if msg.get("role") == "system":
                        # o1-mini 和 o1-preview 早期版本完全不支持 system / developer 消息，必须改写为 user
                        if "o1-mini" in model_lower or "o1-preview" in model_lower:
                            msg["role"] = "user"
                        else:
                            # 较新 o1/o3 模型官方支持 developer 角色
                            msg["role"] = "developer"
        else:
            # 3. 非 o1/o3 通用大模型（如 GPT-4o, DeepSeek, Claude, Llama, Qwen 等）
            # 不支持 max_completion_tokens，必须回退为 max_tokens
            if "max_completion_tokens" in params:
                params["max_tokens"] = params.pop("max_completion_tokens")
            if "max_completion_tokens" in cleaned:
                cleaned["max_tokens"] = cleaned.pop("max_completion_tokens")
                
            # 恢复或确保 system 消息使用常规 system 角色
            messages = cleaned.get("messages", [])
            if messages:
                for msg in messages:
                    if msg.get("role") == "developer":
                        msg["role"] = "system"

        # 4. 推理思维链参数精细适配 (整合并升级 assemble_reasoning_params 逻辑)
        # 获取现有的推理控制设置
        reasoning_enabled = params.get("enable_thinking") or params.get("think") or False
        reasoning_effort = params.get("reasoning_effort", "medium")
        
        # 彻底清洗掉非标准推理参数，防止普通模型报错
        for k in ["enable_thinking", "think", "thinking_budget", "reasoning_effort", "reasoning"]:
            if k in params: del params[k]
            if k in cleaned: del cleaned[k]

        # 根据不同平台的偏好注入受控参数
        if "openrouter" in ac_name.lower():
            params["reasoning"] = {"enabled": reasoning_enabled, "effort": reasoning_effort}
        elif "together" in ac_name.lower():
            params["reasoning"] = {"enabled": reasoning_enabled}
            if reasoning_enabled:
                params["reasoning_effort"] = reasoning_effort
        elif "siliconflow" in ac_name.lower() or "silicon" in url:
            params["thinking_budget"] = 1024 if reasoning_enabled else 0
        elif "ollama" in ac_name.lower() or "ollama" in url:
            params["think"] = reasoning_enabled
            params["thinking"] = reasoning_enabled
        elif is_lmstudio:
            # 🏢 [LM Studio 极致兼容防线]
            # 本地思维链模型（如 Qwen, Llama）与外层 LM Studio 顶级网关的 reasoning_effort 存在严重的格式与警告冲突。
            # 经深度调研与物理对准，最稳妥、百分之百无报错和警告的方案是：
            # 本地通道完全物理剥离 reasoning_effort 参数，仅保留本地模型原生支持的 enable_thinking / think / thinking_budget。
            params.update({
                "enable_thinking": reasoning_enabled,
                "think": reasoning_enabled,
                "thinking_budget": 1024 if reasoning_enabled else 0
            })
        elif is_o_series and is_openai_official:
            if reasoning_enabled:
                params["reasoning_effort"] = reasoning_effort
        else:
            if "r1" in model_lower or "reasoning" in model_lower or reasoning_enabled:
                params.update({
                    "enable_thinking": reasoning_enabled,
                    "think": reasoning_enabled,
                    "thinking_budget": 1024 if reasoning_enabled else 0
                })

        # 5. 回写 params 并进行二次深层校验
        if "params" in cleaned:
            cleaned["params"] = params
        else:
            cleaned.update(params)
            
        return cleaned

