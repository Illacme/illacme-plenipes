#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Deployment Manager
职责：全渠道发布编排器，负责将出版物投递至 S3、CDN、Webhook 等外部端点。
🛡️ [V35.0]：主权隔离分发引擎。
"""

import os
from dataclasses import asdict
from typing import List, Dict, Any
from core.utils.tracing import tlog
from core.governance.license_guard import LicenseGuard
from core.utils.plugin_loader import PluginLoader
from plugins.publishers.base import BasePublisher

class DeploymentManager:
    """🚀 [V35.0] 发布编排器：指挥全渠道分发战役"""
    
    def __init__(self, territory_config: Any):
        self.config = territory_config
        self.publishers = []
        self._initialize_publishers()

    def _initialize_publishers(self):
        """🚀 [V35.1] 主权加载逻辑：按需点火分发渠道"""
        from core.utils.secret_sentinel import sentinel
        
        # 获取配置对象
        pub_model = getattr(self.config, 'publish_control', None)
        if not pub_model: return
        
        # 🛡️ [V35.2] 强类型兼容并执行凭据解密
        pub_cfg_raw = asdict(pub_model) if hasattr(pub_model, '__dataclass_fields__') else (
            pub_model.model_dump() if hasattr(pub_model, 'model_dump') else pub_model
        )
        
        # 🚀 [V35.2] 深度递归解密：支持 system.yaml 中的 ENC: 凭据
        def deep_decrypt(d):
            if isinstance(d, dict):
                return {k: deep_decrypt(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [deep_decrypt(i) for i in d]
            elif isinstance(d, str):
                return sentinel.decrypt(d)
            return d

        pub_cfg = deep_decrypt(pub_cfg_raw)

        # 检查商业授权：免费版限制分发渠道数量
        allowed_channels = 99 if LicenseGuard.is_pro_feature_allowed("multi_territory") else 1
        
        active_count = 0
        plugin_dir = os.path.join("plugins", "publishers")
        
        # 批量加载所有继承自 BasePublisher 的插件类
        publisher_classes = PluginLoader.load_plugins(plugin_dir, BasePublisher, package_name="plugins.publishers")
        
        for cls in publisher_classes:
            # 获取插件标识 (如 s3, webhook)
            plugin_id = getattr(cls, "PLUGIN_ID", cls.__name__.lower().replace("publisher", "").replace("plugin", ""))
            
            # 检查该插件是否在配置中启用
            chan_cfg = pub_cfg.get(plugin_id, {})
            if chan_cfg.get("enabled"):
                if active_count >= allowed_channels:
                    tlog.warning(f"🛡️ [分发拦截] 免费版限额 ({allowed_channels} 渠道)，已忽略 '{plugin_id}'。")
                    continue
                
                try:
                    # 获取系统配置字典
                    sys_cfg_dict = self.config.system.model_dump() if hasattr(self.config.system, 'model_dump') else asdict(self.config.system)
                    
                    # 注入该疆域的私有配置 (已解密)
                    inst = cls(chan_cfg, sys_config=sys_cfg_dict)
                    self.publishers.append(inst)

                    active_count += 1
                    tlog.info(f"📡 [分发中心] 已激活发布渠道: {plugin_id}")
                except Exception as e:
                    tlog.error(f"❌ [分发中心] 实例化发布插件 {plugin_id} 失败: {e}")

    def deploy_all(self, bundle_path: str, metadata: Dict[str, Any]):
        """执行全渠道同步投递 (事务化汇总)"""
        if not self.publishers:
            tlog.debug("ℹ️ [分发中心] 当前主权疆域未激活任何外部发布渠道。")
            return {"status": "skipped", "reason": "no_active_channels"}


        tlog.info(f"🚀 [分发中心] 正在向 {len(self.publishers)} 个渠道投递出版资产...")
        results = {"status": "success", "channels": {}}
        
        fail_count = 0
        for pub in self.publishers:
            pub_name = pub.__class__.__name__
            try:
                # 执行物理发布
                res = pub.push(bundle_path, metadata)
                results["channels"][pub_name] = {"status": "success", "response": res}
                tlog.success(f"  └── ✅ 渠道 {pub_name} 投递成功。")
            except Exception as e:
                tlog.error(f"  └── ❌ 渠道 {pub_name} 投递失败: {e}")
                results["channels"][pub_name] = {"status": "error", "message": str(e)}
                fail_count += 1
        
        if fail_count > 0:
            results["status"] = "partial_success" if fail_count < len(self.publishers) else "failed"
            
        return results
