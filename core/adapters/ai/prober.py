#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 Illacme Plenipes - Dynamic Capability Active Prober
全动态模型能力主动嗅探服务层。负责物理探测、并发管理、多线程兼容自愈及本地缓存生命周期管理。(V77.9)
"""
import os
import json
import logging
import asyncio
import requests

from core.adapters.ai.constants import (
    TOOLS_PROBE_PAYLOAD_TEMPLATE,
    COT_PROBE_PAYLOAD_TEMPLATE,
    VISION_PROBE_PAYLOAD_TEMPLATE
)

logger = logging.getLogger(__name__)
CACHE_PATH = ".plenipes/capabilities_cache.json"

class DynamicCapabilityProber:
    _cache = {}
    _probing_models = set()

    @classmethod
    def load_cache(cls):
        if not cls._cache and os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        cls._cache = json.loads(content)
                    else:
                        cls._cache = {}
            except Exception as e:
                logger.warning(f"⚠️ Failed to load capabilities cache: {e}")
                cls._cache = {}
        return cls._cache

    @classmethod
    def save_cache(cls):
        try:
            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
            tmp_path = f"{CACHE_PATH}.tmp"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(cls._cache, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, CACHE_PATH)
        except Exception as e:
            logger.error(f"🛑 Failed to save capabilities cache: {e}")

    @classmethod
    def get_capabilities(cls, adapter, model_name: str) -> dict:
        cls.load_cache()
        
        # 1. 基础默认值 (启发式降级)
        model_lower = model_name.lower() if model_name else ""
        cot_supported = any(kw in model_lower for kw in ["r1", "o1", "o3", "thinking", "reasoning", "qwen3.5", "qwen2.5", "qwen35"])
        tools_supported = any(c.__name__ == "OpenAICompatibleTranslator" for c in adapter.__class__.__mro__) and adapter.__class__.__name__ != "MockAIProvider"
        vision_supported = any(kw in model_lower for kw in ["vl", "vision", "gpt-4o", "claude-3-5", "qwen3.5", "qwen2.5", "qwen35"])
        
        default_caps = {
            "cot": cot_supported,
            "tools": tools_supported,
            "stream": True,
            "vision": vision_supported
        }
        
        if adapter.__class__.__name__ == "MockAIProvider":
            return {"cot": False, "tools": False, "stream": True, "vision": False}
            
        url = getattr(adapter, 'safe_get_url', lambda: "")()
        if not url:
            return default_caps
            
        cache_key = f"{url}:{model_name}"
        if cache_key in cls._cache:
            # 已经有缓存，直接返回
            return cls._cache[cache_key]
            
        # 2. 如果没有缓存，且当前没有在探测中，则启动后台异步探测任务
        if cache_key not in cls._probing_models:
            cls._probing_models.add(cache_key)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(cls._async_probe(adapter, model_name, cache_key, default_caps))
            except RuntimeError:
                # 🛡️ 容错对正：若当前没有在运行的 asyncio 事件循环（如在 sync / Trio 单元测试中），则使用新开的后台守护线程执行协程，实现 100% 物理自愈
                import threading
                def run_in_thread():
                    try:
                        asyncio.run(cls._async_probe(adapter, model_name, cache_key, default_caps))
                    except Exception:
                        pass
                threading.Thread(target=run_in_thread, daemon=True).start()
            
        # 在后台探测完成前，先安全降级返回启发式默认值，零延迟响应
        return default_caps

    @classmethod
    async def _async_probe(cls, adapter, model_name: str, cache_key: str, default_caps: dict):
        """
        🌐 后台异步探测模型真实物理能力，绝不阻塞用户 UI 线程
        """
        logger.info(f"🔮 [Dynamic Probe] Background active prober starting for: {model_name}")
        probed_caps = default_caps.copy()
        try:
            url = adapter.safe_get_url()
        except Exception:
            url = ""
        if not url:
            cls._probing_models.discard(cache_key)
            return
        if not url.endswith("/chat/completions") and not url.endswith("/completions"):
            url = f"{url.rstrip('/')}/chat/completions"
        headers = {"Content-Type": "application/json"}
        api_key = getattr(adapter, 'safe_get_config', lambda k: "")('api_key')
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            loop = asyncio.get_running_loop()
            run_async = True
        except RuntimeError:
            run_async = False

        # 1. 探测工具调用支持 (Tools Probe)
        tools_payload = {"model": model_name, **TOOLS_PROBE_PAYLOAD_TEMPLATE}
        def send_tools_probe():
            return getattr(adapter, '_session', requests).post(url, json=tools_payload, headers=headers, timeout=30)
        try:
            resp = await loop.run_in_executor(None, send_tools_probe) if run_async else send_tools_probe()
            probed_caps["tools"] = (resp.status_code == 200)
        except RuntimeError as e:
            if "cannot schedule new futures" in str(e) or "event loop is closed" in str(e):
                logger.debug(f"ℹ️ [Dynamic Probe] Active probe interrupted due to event loop shutdown: {e}")
                return
            logger.warning(f"⚠️ [Dynamic Probe] Tools active probe failed: {e}")
        except Exception as e:
            logger.warning(f"⚠️ [Dynamic Probe] Tools active probe failed: {e}")

        # 2. 探测思维链推理支持 (CoT Probe)
        cot_payload = {"model": model_name, **COT_PROBE_PAYLOAD_TEMPLATE}
        def send_cot_probe():
            return getattr(adapter, '_session', requests).post(url, json=cot_payload, headers=headers, timeout=30)
        try:
            resp = await loop.run_in_executor(None, send_cot_probe) if run_async else send_cot_probe()
            if resp.status_code == 200:
                choices = resp.json().get("choices", [])
                if choices:
                    msg = choices[0].get("message", {})
                    probed_caps["cot"] = bool(("reasoning_content" in msg and msg["reasoning_content"]) or ("<think>" in msg.get("content", "")) or ("thinking" in msg))
                else:
                    probed_caps["cot"] = False
            else:
                probed_caps["cot"] = False
        except RuntimeError as e:
            if "cannot schedule new futures" in str(e) or "event loop is closed" in str(e):
                logger.debug(f"ℹ️ [Dynamic Probe] Active probe interrupted due to event loop shutdown: {e}")
                return
            logger.warning(f"⚠️ [Dynamic Probe] CoT active probe failed: {e}")
        except Exception as e:
            logger.warning(f"⚠️ [Dynamic Probe] CoT active probe failed: {e}")

        # 3. 探测多模态视觉支持 (Vision Probe)
        vision_payload = {"model": model_name, **VISION_PROBE_PAYLOAD_TEMPLATE}
        def send_vision_probe():
            return getattr(adapter, '_session', requests).post(url, json=vision_payload, headers=headers, timeout=45)
        try:
            resp = await loop.run_in_executor(None, send_vision_probe) if run_async else send_vision_probe()
            probed_caps["vision"] = (resp.status_code == 200)
        except RuntimeError as e:
            if "cannot schedule new futures" in str(e) or "event loop is closed" in str(e):
                logger.debug(f"ℹ️ [Dynamic Probe] Active probe interrupted due to event loop shutdown: {e}")
                return
            logger.warning(f"⚠️ [Dynamic Probe] Vision active probe failed: {e}")
        except Exception as e:
            logger.warning(f"⚠️ [Dynamic Probe] Vision active probe failed: {e}")

        # 4. 写入缓存并落盘
        cls._cache[cache_key] = probed_caps
        cls.save_cache()
        cls._probing_models.discard(cache_key)
        logger.info(f"✨ [Dynamic Probe] Active probe complete for {model_name}: {probed_caps}")
