#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI - Embedding Adapter
模块职责：向量化适配器。将文本转化为高维向量，为语义搜索提供数学基座。
🛡️ [AEL-Iter-v1.0]：支持 Ollama 与 OpenAI 协议。
"""

import abc
import json
import requests
from typing import List, Optional
from core.utils.tracing import tlog

class BaseEmbedding(abc.ABC):
    @abc.abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass

class OllamaEmbedding(BaseEmbedding):
    """🚀 [V1.0] 本地算力：Ollama 向量化"""
    def __init__(self, model: str = "mxbai-embed-large", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def get_embedding(self, text: str) -> List[float]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=10
            )
            return resp.json().get("embedding", [])
        except Exception as e:
            tlog.error(f"❌ [Ollama Embedding 故障]: {e}")
            return []

class OpenAIEmbedding(BaseEmbedding):
    """🚀 [V1.0] 云端算力：OpenAI 向量化"""
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def get_embedding(self, text: str) -> List[float]:
        try:
            resp = requests.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "input": text},
                timeout=10
            )
            data = resp.json()
            return data.get("data", [{}])[0].get("embedding", [])
        except Exception as e:
            tlog.error(f"❌ [OpenAI Embedding 故障]: {e}")
            return []

class EmbeddingFactory:
    """向量适配器工厂"""
    @staticmethod
    def create(engine) -> Optional[BaseEmbedding]:
        # 优先从配置加载
        cfg = engine.config.translation
        if not hasattr(cfg, 'embeddings'): return None
        
        e_cfg = cfg.embeddings
        if e_cfg.provider == "ollama":
            return OllamaEmbedding(model=e_cfg.model, base_url=e_cfg.base_url)
        elif e_cfg.provider == "openai":
            # 尝试解密 API Key
            key = getattr(e_cfg, 'api_key', '')
            if key.startswith("enc:"):
                from core.governance.secret_manager import secret_manager
                key = secret_manager.decrypt(key[4:])
            return OpenAIEmbedding(api_key=key, model=e_cfg.model, base_url=e_cfg.base_url)
        return None
