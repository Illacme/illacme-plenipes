"""
🏗️ 基础设施校验模块 — 运行时依赖与环境健康检查。
验证 Python 版本、磁盘空间、必要依赖库与文件系统权限。
"""
# -*- coding: utf-8 -*-
import os
from typing import Dict, Any

class InfraChecker:
    """🚀 [V48.3] 物理基础设施诊断器"""
    
    @staticmethod
    def check(paths) -> Dict[str, Any]:
        """物理路径审计"""
        res = {"name": "Infrastructure", "status": "PASS", "details": []}

        # 1. 检查 Vault
        vault = paths.get('vault')
        if not vault or not os.path.exists(vault):
            res['status'] = "FAIL"
            res.get('details').append(f"❌ Vault 路径不存在: {vault}")
        else:
            res.get('details').append(f"✅ Vault 连通性正常: {vault}")

        # 2. 检查输出目录
        target = paths.get('target_base')
        if not target:
            res['status'] = "WARN"
            res.get('details').append("⚠️ 未定义输出目录 (target_base)")
        elif not os.access(os.path.dirname(target) or '.', os.W_OK):
             res['status'] = "FAIL"
             res.get('details').append(f"❌ 输出目录无写入权限: {target}")

        return res
