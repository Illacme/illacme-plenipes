#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - License Guard (出版准入卫士)
职责：负责出版社的合法经营授权校验，执行基于物理指纹的功能栅栏。
🛡️ [V100.8] 商业主权：实装机器指纹绑定、HMAC/RSA 防伪解密与许可全生命周期管理。
"""

import os
import uuid
import platform
import hashlib
import hmac
import json
import base64
import time
from core import __version__
import binascii
from typing import Dict, Tuple, Optional
from core.utils.tracing import tlog

# 系统暗号主钥 (用于签名防伪验证)
SECRET_MASTER_SALT = b"ILLACME-PLENIPES-SOVEREIGN-MASTER-KEY-V100"

class LicenseGuard:
    """🚀 [V100.8] 出版准入卫士：执行出版社的“商业宪法”"""
    
    _PRO_FEATURES = {
        "multi_imprint": "无限出版社品牌",
        "subfolder_ingress": "子目录精准收稿映射",
        "multi_language": "全语种矩阵翻译",
        "multi_dialect": "按目录定制编辑方言",
        "cloud_harvesting": "云端算力联合调度"
    }

    _cached_license_result: Optional[Tuple[bool, Dict]] = None
    _warned_features: set = set()

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

    @staticmethod
    def get_license_file_path() -> str:
        """获取物理许可证落盘路径 (.plenipes/license.lic)"""
        return os.path.abspath(os.path.join(".plenipes", "license.lic"))

    @classmethod
    def verify_license_data(cls, license_text: str) -> Tuple[bool, str, Dict]:
        """
        核验许可证字符串的合法性与防伪签名。
        
        :param license_text: 许可证 Base64 编码文本
        :return: (is_valid, reason, payload)
        """
        if not license_text or not isinstance(license_text, str):
            return False, "许可证数据为空", {}
            
        license_text = license_text.strip()
        try:
            raw_bytes = base64.b64decode(license_text.encode('utf-8'))
            raw_json = raw_bytes.decode('utf-8')
            envelope = json.loads(raw_json)
        except (ValueError, binascii.Error, UnicodeDecodeError):
            return False, "许可证格式不正确 (包含非法字符或损坏的 Base64 编码)，请确认粘贴的文本或 .lic 文件是否完整", {}
        except json.JSONDecodeError:
            return False, "许可证数据结构损坏，无法解析 JSON 证书信封", {}
        except Exception as parse_err:
            return False, f"许可证解密失败: {parse_err}", {}

        if not isinstance(envelope, dict) or "payload" not in envelope or "signature" not in envelope:
            return False, "许可证结构非法，缺少 payload 或 signature", {}

        payload = envelope["payload"]
        sig = envelope["signature"]

        # 1. 签名核验
        expected_sig = hmac.new(SECRET_MASTER_SALT, json.dumps(payload, sort_keys=True).encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return False, "签名不匹配，许可证可能已被非法篡改", {}

        # 2. 硬件指纹核验
        target_fp = payload.get("fingerprint", "")
        current_fp = cls.get_machine_fingerprint()
        if target_fp != "*" and target_fp.upper() != current_fp.upper():
            return False, f"设备标识不匹配 (授权编号: {target_fp}, 当前编号: {current_fp})", {}

        # 3. 有效期核验
        exp = payload.get("exp", 0)
        if exp > 0 and time.time() > exp:
            exp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
            return False, f"许可证已于 {exp_str} 过期", {}

        return True, "验证通过", payload

    @classmethod
    def clear_cache(cls):
        """清除内存中的授权判定缓存与日志防刷记录"""
        cls._cached_license_result = None
        cls._warned_features.clear()

    @classmethod
    def is_licensed(cls) -> bool:
        """判断当前环境是否已激活授权版"""
        # 0. 研发/调试环境变量覆盖
        if os.environ.get("ILLACME_DEV_LICENSE", "").strip() == "1":
            return True

        if cls._cached_license_result is not None:
            return cls._cached_license_result[0]

        lic_path = cls.get_license_file_path()
        if not os.path.exists(lic_path):
            cls._cached_license_result = (False, {})
            return False

        try:
            with open(lic_path, 'r', encoding='utf-8') as f:
                content = f.read()
            is_valid, reason, payload = cls.verify_license_data(content)
            if is_valid:
                cls._cached_license_result = (True, payload)
                return True
            else:
                tlog.warning(f"🛡️ [准入拦截] 许可证无效: {reason}")
                cls._cached_license_result = (False, {})
                return False
        except Exception as ex:
            tlog.error(f"⚠️ [准入读取失败] {ex}")
            cls._cached_license_result = (False, {})
            return False

    @classmethod
    def is_default_imprint_and_theme_active(cls) -> bool:
        """
        🛡️ [V100.9] 检测当前是否为系统默认品牌 (default)。
        默认品牌作为官方示范文库，不占用用户自定义品牌配额。
        """
        try:
            from core.governance.imprint_manager import im
            active_imp = im.get_active_imprint()
            return active_imp == "default"
        except Exception:
            return False

    @classmethod
    def get_active_tier(cls) -> str:
        """
        获取当前生效的许可证级别 (PRO / STANDARD / LITE)。
        授权级别属于系统环境实例本身，保持稳定恒定，不随切换品牌而跳变。
        """
        if os.environ.get("ILLACME_DEV_LICENSE", "").strip() == "1":
            return "PRO"
            
        if cls.is_licensed():
            payload = cls._cached_license_result[1] if (cls._cached_license_result and cls._cached_license_result[0]) else {}
            tier_val = str(payload.get("tier", "PRO")).upper()
            if tier_val in ("STANDARD", "PLUS", "STD"):
                return "STANDARD"
            return "PRO"
            
        return "LITE"

    @classmethod
    def get_max_custom_imprints(cls) -> int:
        """
        🚀 [V101.0] 获取当前授权允许管理的【自定义独立出版品牌】数量上限。
        （系统自带的 default 创作者指南为官方示范文库，不计入此配额）
        - 免费社区版 (LITE): 1 个自定义品牌
        - 基础增强版 (STANDARD): 5 个自定义品牌
        - 高级专业版 (PRO): 99 个自定义品牌
        """
        tier = cls.get_active_tier()
        if tier == "PRO": return 99
        if tier == "STANDARD": return 5
        return 1

    @classmethod
    def get_max_imprints(cls) -> int:
        """
        获取当前授权允许管理的最大版图总数（含系统自带 default 示范文库）。
        保持向下兼容：自定义上限 + 1
        """
        return cls.get_max_custom_imprints() + 1

    @classmethod
    def get_max_i18n_targets(cls) -> int:
        """
        获取当前授权允许配置的最大多语言目标语种数量。
        - 免费社区版 (LITE): 1 个目标语种
        - 基础增强版 (STANDARD): 5 个目标语种
        - 高级专业版 (PRO): 全量语种矩阵任选 (999)
        """
        tier = cls.get_active_tier()
        if tier == "PRO": return 999
        if tier == "STANDARD": return 5
        return 1

    @classmethod
    def is_pro_feature_allowed(cls, feature_name: str) -> bool:
        """
        🚀 [V101.0] 功能栅栏校验：轻量化全量开放技术特性，纯只读无副作用查询。
        为了产品的快速推广，除【自定义品牌数】与【目标语种数】保留商业阶梯外，
        子目录收稿、多渠道分发、方言编辑、算力调度等基础技术特性全部全面放开，
        且严禁在例行查询时发射全局安全警报。
        """
        # 全量放行除核心配额外的所有特性，绝不打扰用户
        return True

    @classmethod
    def activate_license(cls, license_text: str) -> Tuple[bool, str]:
        """
        激活并物理落盘许可证。
        """
        is_valid, reason, payload = cls.verify_license_data(license_text)
        if not is_valid:
            return False, reason

        lic_path = cls.get_license_file_path()
        try:
            os.makedirs(os.path.dirname(lic_path), exist_ok=True)
            with open(lic_path, 'w', encoding='utf-8') as f:
                f.write(license_text.strip())
            cls.clear_cache()
            
            from core.utils.event_bus import bus
            fresh_cfg = None
            try:
                from core.config.config import load_config
                fresh_cfg = load_config()
            except Exception:
                pass
            bus.emit("CONFIG_RELOADED", config=fresh_cfg)
            tlog.success(f"✅ [准入激活] 许可证落盘成功: {lic_path}")
            tier_name = "基础增强版" if str(payload.get("tier", "")).upper() in ("STANDARD", "PLUS", "STD") else "高级专业版"
            return True, f"激活成功！已解锁【{payload.get('customer', tier_name)}】{tier_name}全量特权。"
        except Exception as e:
            return False, f"物理写入失败: {e}"

    @classmethod
    def revoke_license(cls) -> Tuple[bool, str]:
        """
        注销并物理删除当前许可证。
        """
        lic_path = cls.get_license_file_path()
        if os.path.exists(lic_path):
            try:
                os.remove(lic_path)
                cls.clear_cache()
                from core.utils.event_bus import bus
                fresh_cfg = None
                try:
                    from core.config.config import load_config
                    fresh_cfg = load_config()
                except Exception:
                    pass
                bus.emit("CONFIG_RELOADED", config=fresh_cfg)
                return True, "许可证解绑成功，已切回社区免费版 (LITE)。"
            except Exception as e:
                return False, f"文件删除失败: {e}"
        cls.clear_cache()
        return True, "当前未导入任何许可证。"

    @classmethod
    def get_license_info(cls) -> Dict:
        """获取全量系统准入信息概览"""
        is_licensed = cls.is_licensed()
        tier = cls.get_active_tier()
        fingerprint = cls.get_machine_fingerprint()
        payload = cls._cached_license_result[1] if cls._cached_license_result and cls._cached_license_result[0] else {}

        exp = payload.get("exp", 0)
        exp_str = "永久授权" if (exp == 0 and is_licensed) else (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp)) if exp > 0 else "N/A")

        tier_names = {
            "PRO": "高级专业版",
            "STANDARD": "基础增强版",
            "LITE": "免费社区版"
        }
        tier_name = tier_names.get(tier, "免费社区版")

        return {
            "version": f"v{__version__}",
            "is_licensed": is_licensed,
            "fingerprint": fingerprint,
            "tier": tier,
            "tier_name": tier_name,
            "customer": payload.get("customer", f"{tier_name}用户") if is_licensed else "社区免费版用户",
            "exp_date": exp_str if is_licensed else "N/A",
            "features": payload.get("features", list(cls._PRO_FEATURES.keys())),
            "max_custom_imprints": cls.get_max_custom_imprints(),
            "max_imprints": cls.get_max_imprints(),
            "max_i18n_targets": cls.get_max_i18n_targets()
        }

    @staticmethod
    def verify_authority():
        """执行全系统准入审计"""
        fingerprint = LicenseGuard.get_machine_fingerprint()
        tlog.info(f"🛡️ [准入校验] 正在核验设备指纹: {fingerprint}...")
        
        if LicenseGuard.is_licensed():
            tlog.success("✅ [准入校验] 出版许可证核验通过：高级专业版 (Professional Edition)。")
            return True
        
        tlog.info("ℹ️ [准入校验] 当前运行于免费社区版 (Community Edition)。")
        return False

    @staticmethod
    def get_publisher_seal():
        """获取出版社官方电子印章"""
        return f"ILLACME-PLENIPES-PRO-SEAL-{LicenseGuard.get_machine_fingerprint()}"
