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
        默认品牌享有全量 PRO 权限豁免，作为无限制的产品功能展示与体验橱窗，支持任意装帧主题与全语种矩阵。
        """
        try:
            from core.governance.imprint_manager import im
            active_imp = im.get_active_imprint()
            return active_imp == "default"
        except Exception:
            return False

    @classmethod
    def get_active_tier(cls) -> str:
        """获取当前生效的许可证级别 (PRO / STANDARD / LITE)"""
        if os.environ.get("ILLACME_DEV_LICENSE", "").strip() == "1":
            return "PRO"
        
        # 默认品牌永远享有 PRO 级别全功能体验沙盒
        if cls.is_default_imprint_and_theme_active():
            return "PRO"
            
        if cls.is_licensed():
            payload = cls._cached_license_result[1] if (cls._cached_license_result and cls._cached_license_result[0]) else {}
            tier_val = str(payload.get("tier", "PRO")).upper()
            if tier_val in ("STANDARD", "PLUS", "STD"):
                return "STANDARD"
            return "PRO"
            
        return "LITE"

    @classmethod
    def get_max_imprints(cls) -> int:
        """获取当前授权允许管理的最大版图数量"""
        tier = cls.get_active_tier()
        if tier == "PRO": return 999
        if tier == "STANDARD": return 3
        return 1

    @classmethod
    def get_max_i18n_targets(cls) -> int:
        """获取当前授权允许配置的最大多语言目标语种数量"""
        tier = cls.get_active_tier()
        if tier == "PRO": return 999
        if tier == "STANDARD": return 5
        return 1

    @classmethod
    def is_pro_feature_allowed(cls, feature_name: str) -> bool:
        """🚀 [V35.1] 功能栅栏校验：拦截未授权的高级功能调用"""
        if feature_name not in cls._PRO_FEATURES:
            return True

        tier = cls.get_active_tier()
        if tier == "PRO":
            return True

        if tier == "STANDARD":
            # 基础增强版支持：多语种矩阵(上限5个)、子目录频道映射、基础版图(上限3个)
            if feature_name in ("subfolder_ingress", "multi_language", "multi_imprint"):
                return True
            return False

        # LITE 免费社区版拦截
        if feature_name not in cls._warned_features:
            feature_desc = cls._PRO_FEATURES.get(feature_name, feature_name)
            tlog.debug(f"🛡️ [功能栅栏] 未激活授权，静默拦截受限功能 '{feature_desc}' (同类提示已抑制)。")
            cls._warned_features.add(feature_name)
            from core.utils.event_bus import bus
            bus.emit("SECURITY_ALERT", category="LICENSE_LIMIT", message=f"系统已拦截对未授权专业版功能'{feature_desc}'的访问")
        return False

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
        is_default_pro = cls.is_default_imprint_and_theme_active()
        effective_licensed = is_licensed or is_default_pro
        tier = cls.get_active_tier()
        fingerprint = cls.get_machine_fingerprint()
        payload = cls._cached_license_result[1] if cls._cached_license_result and cls._cached_license_result[0] else {}

        exp = payload.get("exp", 0)
        exp_str = "永久授权" if (exp == 0 or (not is_licensed and is_default_pro)) else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))

        tier_names = {
            "PRO": "高级专业版",
            "STANDARD": "基础增强版",
            "LITE": "免费社区版"
        }
        tier_name = tier_names.get(tier, "高级专业版")

        return {
            "version": "v11.2",
            "is_licensed": effective_licensed,
            "is_default_imprint": is_default_pro,
            "fingerprint": fingerprint,
            "tier": tier,
            "tier_name": tier_name,
            "customer": payload.get("customer", f"{tier_name}用户") if is_licensed else (f"{tier_name}用户" if is_default_pro else "社区免费版用户"),
            "exp_date": exp_str if effective_licensed else "N/A",
            "features": payload.get("features", list(cls._PRO_FEATURES.keys())) if effective_licensed else [],
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
