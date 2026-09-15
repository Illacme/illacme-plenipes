#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Syndication SLA Matrix Test Suite
测试职责：验证社媒渠道 SLA 契约分级矩阵与插件元数据透传完整性。
严格遵守用户规则 10（不修改真实配置与文库）与规则 11（严密凭证闭环）。
"""

import unittest
from core.adapters.syndication.base import BaseSyndicator
from adapters.egress.syndication.wechat import WeChatSyndicator
from adapters.egress.syndication.ghost import GhostSyndicator
from adapters.egress.syndication.medium import MediumSyndicator
from adapters.egress.syndication.devto import DevToSyndicator
from adapters.egress.syndication.hashnode import HashnodeSyndicator
from adapters.egress.syndication.telegram import TelegramSyndicator
from adapters.egress.syndication.discord import DiscordSyndicator

from adapters.egress.syndication.zhihu import ZhihuSyndicator
from adapters.egress.syndication.xiaohongshu import XiaohongshuSyndicator
from adapters.egress.syndication.juejin import JuejinSyndicator
from adapters.egress.syndication.csdn import CSDNSyndicator
from adapters.egress.syndication.bilibili import BilibiliSyndicator
from adapters.egress.syndication.toutiao import ToutiaoSyndicator
from adapters.egress.syndication.cnblogs import CNBlogsSyndicator
from adapters.egress.syndication.oschina import OSChinaSyndicator
from adapters.egress.syndication.segmentfault import SegmentFaultSyndicator

class TestSyndicationSLAMatrix(unittest.TestCase):

    def test_base_syndicator_default_sla(self):
        self.assertEqual(BaseSyndicator.SLA_TIER, "tier1")
        self.assertEqual(BaseSyndicator.SLA_LABEL, "官方直连")

    def test_tier1_official_api_adapters(self):
        tier1_list = [
            WeChatSyndicator,
            GhostSyndicator,
            MediumSyndicator,
            DevToSyndicator,
            HashnodeSyndicator,
            TelegramSyndicator,
            DiscordSyndicator
        ]
        for cls in tier1_list:
            with self.subTest(adapter=cls.__name__):
                self.assertEqual(cls.SLA_TIER, "tier1")
                self.assertEqual(cls.SLA_LABEL, "官方直连")
                self.assertTrue(len(cls.SLA_DESC) > 0)

    def test_tier2_cookie_assisted_adapters(self):
        tier2_list = [
            ZhihuSyndicator,
            XiaohongshuSyndicator,
            JuejinSyndicator,
            CSDNSyndicator,
            BilibiliSyndicator,
            ToutiaoSyndicator,
            CNBlogsSyndicator,
            OSChinaSyndicator,
            SegmentFaultSyndicator
        ]
        for cls in tier2_list:
            with self.subTest(adapter=cls.__name__):
                self.assertEqual(cls.SLA_TIER, "tier2")
                self.assertEqual(cls.SLA_LABEL, "Cookie辅助")
                self.assertTrue(len(cls.SLA_DESC) > 0)

    def test_plugin_mapper_sla_passthrough(self):
        from unittest.mock import MagicMock, patch
        from services.api.routes.gov.plugin_mapper import assemble_plugin_matrix

        engine_mock = MagicMock()
        engine_mock.config.syndication.targets = {}
        engine_mock.config.image_hosting = {}
        engine_mock.config.plugins.disabled_plugins = []
        engine_mock.config.active_theme = "default"

        with patch("services.api.routes.gov.plugin_mapper.get_global_engine", return_value=engine_mock):
            plugins = assemble_plugin_matrix()

        publisher_plugins = [p for p in plugins if p.get("category") == "publisher"]

        self.assertGreater(len(publisher_plugins), 0)
        for p in publisher_plugins:
            self.assertIn("sla_tier", p)
            self.assertIn("sla_label", p)
            self.assertIn("sla_desc", p)
            self.assertIn(p["sla_tier"], ("tier1", "tier2"))
            self.assertIn("icon", p)
            self.assertTrue(len(p["icon"]) > 0)
            self.assertIn("name", p)
            self.assertTrue(len(p["name"]) > 0)

        pub_map = {p["id"]: p for p in publisher_plugins}
        self.assertEqual(pub_map["wechat"]["name"], "微信公众号")
        self.assertEqual(pub_map["wechat"]["icon"], "💬")
        self.assertEqual(pub_map["zhihu"]["name"], "知乎")
        self.assertEqual(pub_map["zhihu"]["icon"], "💡")
        self.assertEqual(pub_map["juejin"]["name"], "稀土掘金")
        self.assertEqual(pub_map["juejin"]["icon"], "🧱")

    def test_syndication_ledger_wildcard_and_lifecycle(self):
        """测试物权账本在 auto/all/source 及多语种前缀下的查询与删除稳固性"""
        import sqlite3
        import tempfile
        import os
        from core.archives.sqlite_syndication import SQLiteSyndicationMixin

        class MockLedger(SQLiteSyndicationMixin):
            def __init__(self, db_path):
                self.db_path = db_path
            def _get_conn(self):
                c = sqlite3.connect(self.db_path)
                c.row_factory = sqlite3.Row
                return c

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_ledger.db")
            conn = sqlite3.connect(db_path)
            conn.execute("""
                CREATE TABLE syndication_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rel_path TEXT NOT NULL,
                    lang_code TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    remote_article_id TEXT,
                    remote_url TEXT,
                    content_hash TEXT,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(rel_path, lang_code, target_id)
                )
            """)
            conn.close()

            ledger = MockLedger(db_path)
            # 存入一条真实中文记录
            ledger.save_syndication_record("docs/test.md", "zh-Hans", "devto", "12345", "https://dev.to/test")

            # 1. 验证传入 auto / all / None 均能查询到该记录
            records_auto = ledger.list_syndication_records_for_doc("docs/test.md", "auto")
            self.assertEqual(len(records_auto), 1)
            self.assertEqual(records_auto[0]["remote_article_id"], "12345")

            records_none = ledger.list_syndication_records_for_doc("docs/test.md", None)
            self.assertEqual(len(records_none), 1)

            # 2. 验证传入 zh 前缀模糊匹配 zh-Hans
            records_zh = ledger.list_syndication_records_for_doc("docs/test.md", "zh")
            self.assertEqual(len(records_zh), 1)

            # 3. 验证 get_syndication_record 在 auto 下也能取到记录
            rec_auto = ledger.get_syndication_record("docs/test.md", "auto", "devto")
            self.assertIsNotNone(rec_auto)
            self.assertEqual(rec_auto["remote_article_id"], "12345")

            # 4. 验证 delete_syndication_record 在 auto 下也能安全抹除记录
            ledger.delete_syndication_record("docs/test.md", "auto", "devto")
            rec_after = ledger.get_syndication_record("docs/test.md", "auto", "devto")
            self.assertIsNone(rec_after)

if __name__ == "__main__":
    unittest.main()
