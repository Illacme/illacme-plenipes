# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - ComfyUI Provider
职责：开源节点式 ComfyUI 工作流生图驱动。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import uuid
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class ComfyUIProvider(BaseImageProvider):
    PROVIDER_ID = "comfyui"
    PROVIDER_NAME = "ComfyUI"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        raw_base = self.config.get("base_url", "http://127.0.0.1:8188").strip()
        self.base_url = raw_base.rstrip("/")
        self.client_id = str(uuid.uuid4())[:8]
        self.timeout = int(self.config.get("timeout", 180))

    def _build_default_workflow(self, prompt: str, width: int, height: int) -> Dict[str, Any]:
        """构建最轻量兼容的 SD 基础 Checkpoint 生成工作流"""
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": 7, "denoise": 1, "latent_image": ["5", 0],
                    "model": ["4", 0], "negative": ["7", 0],
                    "positive": ["6", 0], "sampler_name": "euler",
                    "scheduler": "normal", "seed": int(time.time() * 1000) % 1000000000,
                    "steps": 20
                }
            },
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": height, "width": width}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "low quality, bad anatomy, text, watermark"}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "Plenipes", "images": ["8", 0]}}
        }

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        ratio_dims = {"16:9": (896, 512), "1:1": (512, 512), "2.35:1": (960, 408)}
        width, height = ratio_dims.get(aspect_ratio, (896, 512))

        workflow = kwargs.get("workflow") or self._build_default_workflow(prompt, width, height)
        payload = {"prompt": workflow, "client_id": self.client_id}

        try:
            tlog.info(f"🎨 [ComfyUI] 正在提交队列任务: {prompt[:30]}...")
            resp = requests.post(f"{self.base_url}/prompt", json=payload, timeout=15)
            if resp.status_code != 200:
                return None, f"ComfyUI 提交失败 ({resp.status_code}): {resp.text[:150]}"

            prompt_id = resp.json().get("prompt_id")
            if not prompt_id:
                return None, "未获取到 prompt_id"

            # 轮询产物
            t_start = time.time()
            while time.time() - t_start < self.timeout:
                time.sleep(1.5)
                h_resp = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
                if h_resp.status_code == 200:
                    history = h_resp.json().get(prompt_id, {})
                    outputs = history.get("outputs", {})
                    for node_id, out in outputs.items():
                        images = out.get("images", [])
                        if images:
                            img_info = images[0]
                            fn = img_info.get("filename")
                            subfolder = img_info.get("subfolder", "")
                            t_type = img_info.get("type", "output")
                            view_url = f"{self.base_url}/view?filename={fn}&subfolder={subfolder}&type={t_type}"
                            img_data = requests.get(view_url, timeout=30).content
                            return img_data, None
            return None, "ComfyUI 渲染任务执行超时"
        except Exception as e:
            tlog.error(f"🛑 [ComfyUI] 调度异常: {e}")
            return None, str(e)

    def test_connection(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            resp = requests.get(f"{self.base_url}/system_stats", timeout=5)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code == 200:
                devices = resp.json().get("devices", [])
                gpu_name = devices[0].get("name", "Active") if devices else "CPU/Ready"
                return {"success": True, "message": f"连接成功 (ComfyUI 服务在线: {gpu_name}, 延迟 {latency}ms)", "latency_ms": latency}
            return {"success": False, "message": f"ComfyUI 响应异常 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"无法连接 ComfyUI 服务: {e}", "latency_ms": 0}
