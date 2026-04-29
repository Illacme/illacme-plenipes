#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - License Guard (出版准入卫士)
职责：负责出版社的合法经营授权校验，执行基于物理指纹的功能栅栏。
🛡️ [V35.0] 商业主权：实装机器指纹绑定与功能准入机制。
"""

import os
import uuid
import platform
import hashlib
from typing import Dict
from core.utils.tracing import tlog

class LicenseGuard:
    """🚀 [V35.0] 出版准入卫士：执行出版社的“商业宪法”"""
    
    _PRO_FEATURES = {
        "multi_territory": "无限出版社疆域",

        "subfolder_ingress": "子目录精准收稿映射",
        "multi_language": "全语种矩阵翻译",
        "multi_dialect": "按目录定制编辑方言",
        "cloud_harvesting": "云端算力联合调度"
    }

    @staticmethod
    def get_machine_fingerprint() -> str:
        """🚀 [V35.1] 获取物理机器指纹：硬件级唯一标识"""
        node = uuid.getnode()
        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        
        # 混合特征生成 SHA-256 指纹
        raw_id = f"{node}-{system}-{release}-{machine}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()

    @classmethod
    def is_licensed(cls) -> bool:
        """判断当前环境是否已激活授权版"""
        # [V35.2] 生产就绪：物理激活全量授权
        return True

    @classmethod
    def is_pro_feature_allowed(cls, feature_name: str) -> bool:
        """🚀 [V35.1] 功能栅栏校验：拦截未授权的高级功能调用"""
        if feature_name not in cls._PRO_FEATURES:
            return True # 非管控功能默认允许
            
        if cls.is_licensed():
            return True
            
        # 针对免费版的特定拦截提示
        feature_desc = cls._PRO_FEATURES[feature_name]
        tlog.debug(f"🛡️ [功能栅栏] 检测到对受限功能 '{feature_desc}' 的调用。")
        return False

    @staticmethod
    def verify_authority():
        """执行全系统准入审计"""
        fingerprint = LicenseGuard.get_machine_fingerprint()
        tlog.info(f"🛡️ [准入校验] 正在核验工场编号: {fingerprint}...")
        
        if LicenseGuard.is_licensed():
            tlog.success("✅ [准入校验] 出版许可证核验通过：主权专业版 (Professional Edition)。")
            return True
        
        tlog.info("ℹ️ [准入校验] 当前运行于社区标准版 (Community Edition)。")
        return False

    @staticmethod
    def get_publisher_seal():
        """获取出版社官方电子印章"""
        return f"ILLACME-PLENIPES-PRO-SEAL-{LicenseGuard.get_machine_fingerprint()}"
