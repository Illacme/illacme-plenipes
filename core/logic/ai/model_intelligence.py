#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Model Intelligence Hub (V10.3 Gateway Edition)
模块职责：负责 AI 算力特性的深度感知、多要素参数映射与【工业级网关级】归一化。
🛡️ [AEL-Iter-v10.3]：全自动驾驶 (Autopilot) 与 协议归一化 (Protocol Normalizer) 引擎。
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional

from core.utils.tracing import tlog

class ModelIntelligenceHub:
    # 🏺 [V10.3] 专家经验库：不同模型在不同任务下的“黄金参数”
    BEST_PRACTICES = {
        "deepseek-reasoner": {
            "enable_thinking": False, # 🛡️ [V10.3] 翻译任务默认关闭思维链，追求极速
            "thinking_budget": 1024,
            "temperature": 0.0,
            "deterministic": True
        },
        "deepseek-chat": {
            "enable_thinking": False,
            "temperature": 0.0,
            "deterministic": True
        },
        "o1-": {
            "enable_thinking": False,
            "thinking_budget": 1024,
            "deterministic": True
        },
        "o3-": {
            "enable_thinking": False,
            "thinking_budget": 1024,
            "deterministic": True
        },
        "claude-3-7": {
            "enable_thinking": False,
            "thinking_budget": 1024,
            "temperature": 0.0
        },
        "gpt-4.5": {
            "enable_json_mode": True,
            "temperature": 0.0,
            "deterministic": True
        },
        "gemini-2.0": {
            "enable_thinking": True, # Gemini 2.0 默认开启轻量思考
            "thinking_budget": 1024,
            "temperature": 0.0
        },
        "deepseek-v3": {
            "temperature": 0.0,
            "deterministic": True
        },
        "gpt-4o": {
            "enable_json_mode": True,
            "temperature": 0.2
        }
    }

    # 🏺 [V10.3] 工业级协议归一化库 (参考 OpenRouter/LiteLLM 设计)
    PROTOCOL_NORMALIZER = {
        "thinking": {
            "openai-o1": lambda v, budget: {"reasoning_effort": "medium" if v and budget > 0 else "low"},
            "deepseek-r1": lambda v, budget: {"max_thinking_tokens": budget if v else 1},
            "anthropic-claude": lambda v, budget: {"thinking": {"type": "enabled", "budget_tokens": budget}} if v else {},
            "openrouter-gateway": lambda v, budget: {"include_reasoning": v, "max_thinking_tokens": budget if v else 1},
            "lmstudio-standard": lambda v, budget: {"reasoning": "on" if v else "off", "reasoning_effort": "medium" if v else "none"},
            "google-gemini": lambda v, budget: {"thinking_config": {"include_thoughts": v}} if v else {},
            "standard-openai": lambda v, _: {}
        },
        "json_mode": {
            "openai-compatible": lambda v, _: {"response_format": {"type": "json_object"}} if v else {},
            "google-gemini": lambda v, _: {"response_mime_type": "application/json"} if v else {},
            "ollama-native": lambda v, _: {"format": "json"} if v else {},
            "lmstudio-standard": lambda v, _: {"response_format": {"type": "text"}} if v else {}
        }
    }

    # 🏺 [V34.9] 全局节点健康分矩阵 (单例核心)
    _node_health = {}

    def __init__(self, cache_path: str = None):
        # 🚀 [V16.6] 使用 ConfigManager 注入的中心化路径
        self.cache_path = cache_path or ".plenipes/model_features.json"
        self.learned_features = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                tlog.warning(f"⚠️ 无法加载模型特征缓存: {e}")
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.learned_features, f, indent=2, ensure_ascii=False)
        except Exception as e:
            tlog.error(f"🛑 无法保存模型特征缓存: {e}")

    def get_autopilot_config(self, model_name: str, user_config: Any) -> Dict[str, Any]:
        """🏎️ [V10.3] 全自动驾驶：根据模型名称自动填充最优专家参数"""
        final_cfg = {
            "enable_thinking": getattr(user_config, 'enable_thinking', None),
            "thinking_budget": getattr(user_config, 'thinking_budget', None),
            "enable_json_mode": getattr(user_config, 'enable_json_mode', None),
            "deterministic": getattr(user_config, 'deterministic', None),
            "temperature": getattr(user_config, 'temperature', None)
        }
        best_practice = {}
        m_lower = model_name.lower() if model_name else ""
        for pattern, practice in self.BEST_PRACTICES.items():
            if pattern in m_lower:
                best_practice = practice
                break
        for key, value in best_practice.items():
            if final_cfg.get(key) is None:
                final_cfg[key] = value

        if final_cfg.get('enable_thinking') is None: final_cfg['enable_thinking'] = False
        if final_cfg.get('thinking_budget') is None: final_cfg['thinking_budget'] = 1024
        if final_cfg.get('enable_json_mode') is None: final_cfg['enable_json_mode'] = False
        if final_cfg.get('deterministic') is None: final_cfg['deterministic'] = True
        return final_cfg

    @classmethod
    def record_success(cls, node_name: str, reason: str = "调用成功"):
        """记录节点调用成功，提升健康分"""
        stats = cls._node_health.get(node_name, {"score": 100, "success_count": 0, "fail_count": 0, "reasons": []})
        stats["success_count"] += 1
        stats["score"] = min(100, stats["score"] + 1)
        cls._node_health[node_name] = stats

    @classmethod
    def record_failure(cls, node_name: str, reason: str = "未知错误"):
        """记录节点调用失败，降低健康分"""
        stats = cls._node_health.get(node_name, {"score": 100, "success_count": 0, "fail_count": 0, "reasons": []})
        stats["fail_count"] += 1
        stats["score"] = max(0, stats["score"] - 20) # 失败惩罚更重
        stats.setdefault("reasons", []).append(reason)
        cls._node_health[node_name] = stats
        # 🚀 [V16.8] 性能自律：系统级（system）警告已由 UI Panel 统一展示，此处不再重复打印日志
        from core.utils.tracing import Tracer
        if node_name != "system" and "SelfCheck" not in (Tracer.get_id() or ""):
            tlog.warning(f"📉 [健康分下降] 节点 {node_name} 当前分数: {stats['score']} | 原因: {reason}")

    @classmethod
    def get_all_reasons(cls, node_id: str) -> list:
        """🚀 [V34.9] 获取指定节点的所有失败原因"""
        stats = cls._node_health.get(node_id)
        if not stats: return []
        return stats.get("reasons", [])

    def get_health_score(self, node_name: str) -> int:
        """获取节点当前健康分"""
        return self.node_health.get(node_name, {"score": 100})["score"]

    def _get_protocol_family(self, model_name: str, base_url: str) -> str:
        """🔍 自动探测模型所属的协议家族"""
        m = model_name.lower() if model_name else ""
        u = base_url.lower() if base_url else ""
        if "openrouter.ai" in u: return "openrouter-gateway"
        if "o1-" in m or "o3-" in m: return "openai-o1"
        if "r1" in m or "reasoner" in m: return "deepseek-r1"
        if "claude" in m: return "anthropic-claude"
        if "localhost" in u or "127.0.0.1" in u: return "lmstudio-standard"
        return "standard-openai"

    def get_intelligent_payload(self, config, archetype: str, ai_client=None, is_json: bool = False) -> Dict[str, Any]:
        """🚀 [AEL-Iter-v10.3] 归一化网关载荷组装器"""
        payload = {}
        model_name = getattr(config, 'model', 'unknown')
        base_url = str(getattr(config, 'base_url', '') or getattr(config, 'url', '') or '')

        # 1. 执行全自动驾驶 (Autopilot)
        autopilot = self.get_autopilot_config(model_name, config)

        # 2. 识别协议家族
        family = self._get_protocol_family(model_name, base_url)

        # 3. 动态映射：思维链压制/开启
        thinking_mapper = self.PROTOCOL_NORMALIZER.get('thinking').get(family)
        if thinking_mapper:
            payload.update(thinking_mapper(autopilot.get('enable_thinking'), autopilot.get('thinking_budget')))

        # 4. 动态映射：JSON 模式 (增强对本地环境 127.0.0.1 的兼容性)
        is_local = "localhost" in base_url or "127.0.0.1" in base_url
        if (autopilot.get('enable_json_mode') or is_json):
            json_family = family if family in self.PROTOCOL_NORMALIZER.get('json_mode') else "openai-compatible"
            if "gemini" in model_name.lower(): json_family = "google-gemini"

            json_mapper = self.PROTOCOL_NORMALIZER.get('json_mode').get(json_family)
            if json_mapper:
                payload.update(json_mapper(True, None))

        # 5. 确定性推理对齐
        if autopilot.get('deterministic'):
            payload['temperature'] = 0
            m_lower = model_name.lower() if model_name else ""
            if "claude" not in m_lower:
                payload['seed'] = 42

        # 6. 身份指纹注入 (IdentityHub)
        if family == "openrouter-gateway":
            site_url = getattr(config, 'site_url', "https://github.com/Illacme-plenipes/illacme-plenipes")
            payload['headers'] = {
                "HTTP-Referer": site_url,
                "X-Title": "Illacme-plenipes Sovereign Gateway"
            }

        # 7. 补充 Oracle 学习到的特性
        model_key = f"{archetype}:{model_name}"
        if model_key in self.learned_features:
            for feature, mapping in self.learned_features[model_key].items():
                if autopilot.get(f"enable_{feature}") or autopilot.get(feature):
                    payload[mapping.get('param')] = mapping.get('format').replace("{budget}", str(autopilot.get('thinking_budget')))

        # 8. 异步触发探测
        if ai_client and model_key not in self.learned_features and autopilot.get('enable_thinking'):
            self._probe_and_learn(model_key, model_name, ai_client)

        return payload

    def _probe_and_learn(self, model_key: str, model_name: str, ai_client):
        """🔮 Oracle Probe"""
        tlog.info(f"🔮 [Oracle Probe] 正在嗅探新模型 {model_name}...")
        probe_prompt = "Task: API Protocol Discovery. Respond ONLY with raw JSON."
        try:
            response = ai_client._ask_ai({"system": "You are a helper.", "user": probe_prompt, "model": model_name, "params": {}})
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                learned_data = json.loads(json_match.group())
                self.learned_features[model_key] = learned_data
                self._save_cache()
                tlog.info(f"✨ [学习成功] 已记录 {model_name} 特征。")
        except Exception: pass
