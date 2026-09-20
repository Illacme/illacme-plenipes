#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Content Syndicator Management Mixin
职责：提供分发插件枚举、远程文章物理下架与本地账本解绑等治理接口。
"""

import importlib.util
from core.adapters.syndication.targets import TARGET_REGISTRY
from core.utils.tracing import tlog


class HubManagementMixin:
    """分发节点与文章生命周期管理 Mixin"""

    def list_all_plugins(self):
        """🚀 [V17.0] 枚举所有已发现的外部插件及其状态"""
        report = []
        for p_id, p_cls in TARGET_REGISTRY.items():
            platform_cfg = getattr(self.cfg, p_id, None)
            is_enabled = platform_cfg and getattr(platform_cfg, 'enabled', False)

            reqs = getattr(p_cls, 'REQUIRED_PACKAGES', [])
            missing_reqs = []
            for req in reqs:
                if importlib.util.find_spec(req) is None:
                    missing_reqs.append(req)

            status = "ACTIVE" if is_enabled and not missing_reqs else "INACTIVE"
            if is_enabled and missing_reqs:
                status = "DEP_MISSING"

            report.append({
                "id": p_id,
                "class": p_cls.__name__,
                "status": status,
                "missing": missing_reqs
            })
        return report

    def delete_remote_article(self, rel_path: str, lang_code: str, target_id: str) -> dict:
        """🚀 [V120.0] 远程下架：调起插件的 delete 接口并清除物理账本映射"""
        if not getattr(self, "meta", None):
            return {"ok": False, "error": "Meta ledger not initialized"}
        rec = self.meta.get_syndication_record(rel_path, lang_code, target_id)
        if not rec or not rec.get("remote_article_id"):
            return {"ok": False, "error": "未找到对应的远程文章映射记录"}

        remote_id = rec["remote_article_id"]
        plugins = getattr(self, "plugins", [])
        plugin = next((p for p in plugins if getattr(p, 'PLUGIN_ID', p.__class__.__name__).lower() == target_id.lower()), None)
        if not plugin:
            return {"ok": False, "error": f"渠道插件 {target_id} 未激活或未装载"}

        if not hasattr(plugin, "delete"):
            return {
                "ok": False,
                "error": f"{target_id} 平台官方 API 不支持远程删除，建议点击右侧「🔗 解绑」并在该平台后台手动处理。"
            }

        actual_lang = rec.get("lang_code") or lang_code
        try:
            success = plugin.delete(remote_id)
            if success:
                self.meta.delete_syndication_record(rel_path, actual_lang, target_id)
                if actual_lang != lang_code:
                    self.meta.delete_syndication_record(rel_path, lang_code, target_id)
                if hasattr(self.meta, "update_egress_status"):
                    self.meta.update_egress_status(rel_path, target_id, "pending", url="")
                    self.meta.save()
                tlog.info(f"🗑️ [物理下架与解绑成功] {rel_path} ({actual_lang}) -> {target_id} (ID: {remote_id})")
                return {"ok": True, "message": f"文章 (ID: {remote_id}) 已从 {target_id} 成功物理下架。"}
            else:
                return {"ok": False, "error": f"{target_id} 平台返回下架失败。"}
        except NotImplementedError:
            return {
                "ok": False,
                "error": f"{target_id} 平台官方 API 不支持远程删除，建议点击右侧「🔗 解绑」并在该平台后台手动处理。"
            }
        except Exception as e:
            tlog.error(f"🛑 [远程下架异常] {target_id}: {e}")
            return {"ok": False, "error": str(e)}

    def unlink_remote_article(self, rel_path: str, lang_code: str, target_id: str) -> dict:
        """🚀 [V120.0] 本地解绑：仅从 SQLite 账本删除物理映射，不影响对端已发布的文章"""
        if not getattr(self, "meta", None):
            return {"ok": False, "error": "Meta ledger not initialized"}
        rec = self.meta.get_syndication_record(rel_path, lang_code, target_id)
        actual_lang = rec.get("lang_code") if rec else lang_code
        self.meta.delete_syndication_record(rel_path, actual_lang, target_id)
        if actual_lang != lang_code:
            self.meta.delete_syndication_record(rel_path, lang_code, target_id)
        if hasattr(self.meta, "update_egress_status"):
            self.meta.update_egress_status(rel_path, target_id, "pending", url="")
            self.meta.save()
        tlog.info(f"🔗 [本地解绑成功] {rel_path} ({actual_lang}) -> {target_id}")
        return {"ok": True, "message": f"已解除 {target_id} 与该文章的本地绑定。"}
