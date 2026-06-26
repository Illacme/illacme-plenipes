#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_bindery_unmasker.py
🛡️ [V88.0] Egress Unmasker 解蔽引擎测试
验证资产预扫描与并行预热调度、多语种 alt 文本注入以及内链本地化与死链修正。
"""

import threading
from unittest.mock import MagicMock, patch

from core.bindery.bindery_unmasker import BinderyUnmasker


class MockService:
    """Mock 解蔽引擎所需的服务提供者"""
    def __init__(self):
        self.paths = {"vault": "/vault"}
        self.meta = MagicMock()
        self.route_manager = MagicMock()
        self.asset_pipeline = MagicMock()
        self.asset_base_url = "assets/"
        self.config = MagicMock()


class MockLinkResolver:
    """Mock 链接解析器，支持链接本地化与内容健康修正"""
    def resolve_link(self, target_rel_path, lang_code, route_prefix, mapped_sub_dir):
        """解析本地化链接"""
        return f"/resolved/{lang_code}/{target_rel_path}"

    def heal_content(self, body, lang_code, route_prefix, mapped_sub_dir, source_rel_path=None):
        """内容自愈钩子"""
        return body + "\n#healed"


class TestBinderyUnmasker:
    """解蔽引擎测试类"""

    @patch("core.bindery.bindery_unmasker.os.path.exists")
    def test_warm_assets(self, mock_exists):
        """测试资产预热流程是否成功投递异步加工任务"""
        mock_exists.return_value = True
        service = MockService()
        unmasker = BinderyUnmasker(service)

        masks = [
            "URL_ONLY_IMG:images/pic.png",
            "![Some Alt](images/pic2.png)",
            "URL_ONLY_LNK:https://external.com",  # 外部链接不应预热
        ]

        asset_index = {
            "pic.png": ["images/pic.png"],
            "pic2.png": ["images/pic2.png"]
        }

        # 执行预热
        futures = unmasker.warm_assets("body", masks, asset_index, slug="my-post")

        # 验证两个本地资产都向 pipeline 投递了 process_async
        assert len(futures) == 2
        assert service.asset_pipeline.process_async.call_count == 2

    @patch("core.bindery.bindery_unmasker.os.path.exists")
    def test_unmask_image_with_multilingual_alt(self, mock_exists):
        """测试图片掩码还原，验证多语种替代文本 alt_texts 注入"""
        mock_exists.return_value = True
        service = MockService()
        unmasker = BinderyUnmasker(service)

        # 模拟 pipeline 的 md5 指纹与 metadata 检索
        service.asset_pipeline._generate_fingerprint.return_value = "abc123hash"
        service.meta.get_asset_metadata.return_value = {
            "alt_texts": {
                "en": "English description",
                "zh": "中文描述"
            }
        }
        service.asset_pipeline.process.return_value = "pic_abc123.png"

        body = "Here is [[STB_MASK_0]]"
        masks = ["![Original Alt](images/pic.png)"]
        asset_index = {"pic.png": ["images/pic.png"]}

        res = unmasker.unmask(
            body=body,
            lang_code="zh",
            route_prefix="blog",
            route_source="zh",
            mapped_sub_dir="tech",
            masks=masks,
            is_dry_run=False,
            is_target=True,
            asset_index=asset_index,
            node_assets=set(),
            assets_lock=threading.Lock(),
            node_outlinks=set(),
            slug="post-slug"
        )

        # 验证 unmask_fn 能从 metadata 获取正确的语种 (zh) 对应的 alt
        # 且输出路径已根据深度正确调整（route_prefix='blog', mapped_sub_dir='tech' -> 深度为 3 -> root_path 为 ../../../）
        assert "![中文描述](../../../assets/pic_abc123.png)" in res

    @patch("core.bindery.bindery_unmasker.os.path.exists")
    def test_unmask_url_only_link_localization(self, mock_exists):
        """测试超链接掩码还原，验证内部链接自愈与本地化重定向"""
        mock_exists.return_value = True
        service = MockService()
        
        # 配置开启自愈
        gov = MagicMock()
        gov.link_governance.auto_localize_internal_links = True
        service.config.translation.governance = gov

        link_resolver = MockLinkResolver()
        unmasker = BinderyUnmasker(service, link_resolver=link_resolver)

        # 模拟内部链接映射
        service.meta.resolve_link.return_value = "posts/other-article.md"

        body = "Go to [[STB_MASK_0]]"
        masks = ["URL_ONLY_LNK:posts/other-article.md"]
        asset_index = {}

        node_outlinks = set()
        res = unmasker.unmask(
            body=body,
            lang_code="en",
            route_prefix="news",
            route_source="en",
            mapped_sub_dir="",
            masks=masks,
            is_dry_run=False,
            is_target=True,
            asset_index=asset_index,
            node_assets=set(),
            assets_lock=threading.Lock(),
            node_outlinks=node_outlinks,
            slug="my-news"
        )

        # 验证 node_outlinks 记录了外链
        assert "posts/other-article.md" in node_outlinks
        # 验证 resolved link 的调用结果
        assert "Go to /resolved/en/posts/other-article.md" in res
        # 验证 content_healer 钩子生效
        assert res.endswith("#healed")
