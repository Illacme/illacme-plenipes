#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - AWS Bedrock Messages Adapter
🛡️ [V67.0]：对正 Anthropic 协议族，支持 Claude 3 系列原生 Messages API。
"""
import boto3
import json
from typing import Dict, Any, List
from .anthropic_base import AnthropicCompatibleTranslator
from core.utils.tracing import tlog

class BedrockTranslator(AnthropicCompatibleTranslator):
    """🚀 AWS Bedrock 极致适配器 (Anthropic 协议对正)"""
    PLUGIN_ID = 'bedrock'
    DISPLAY_NAME = 'AWS Bedrock (Claude)'
    PROTOCOL_FAMILY = 'anthropic'
    
    def __init__(self, node_name, trans_cfg):
        # 绕过 AnthropicCompatibleTranslator 的 __init__，因为 Bedrock 不使用 requests Session
        super(AnthropicCompatibleTranslator, self).__init__(node_name, trans_cfg)
        try:
            region = self.safe_get_config('region', 'us-east-1')
            self._client = boto3.client(
                service_name='bedrock-runtime',
                region_name=region,
                aws_access_key_id=self.trans_cfg.api_key.split(':')[0] if ':' in self.trans_cfg.api_key else None,
                aws_secret_access_key=self.trans_cfg.api_key.split(':')[1] if ':' in self.trans_cfg.api_key else None
            )
        except Exception as e:
            tlog.error(f"❌ [Bedrock] SDK 初始化失败: {e}")

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """执行 Bedrock 版 Messages API 推断"""
        model_id = payload.get('model')
        
        # 🚀 极致复用：利用 Anthropic 基类的 Payload 构造逻辑
        anthropic_payload = self.build_anthropic_payload(
            payload.get("system", ""),
            payload.get("user", ""),
            payload.get("params", {})
        )
        
        # Bedrock 需要额外的版本号
        anthropic_payload["anthropic_version"] = "bedrock-2023-05-31"
        
        try:
            res = self._client.invoke_model(body=json.dumps(anthropic_payload), modelId=model_id)
            res_body = json.loads(res.get('body').read())
            return res_body.get('content', [{}])[0].get('text', '')
        except Exception as e:
            tlog.error(f"🛑 [Bedrock API Error]: {e}")
            raise

    async def list_models(self) -> list[str]:
        return ["anthropic.claude-3-5-sonnet-20241022-v2:0", "anthropic.claude-3-opus-20240229-v1:0"]
