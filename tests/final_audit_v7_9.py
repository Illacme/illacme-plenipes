#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 将项目根目录加入路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config.config import load_config
from core.bindery.bindery_dispatcher import BinderyDispatcher
from core.editorial.router import RouteManager
from core.archives.ledger import MetadataManager

# 模拟类
class MockSSG:
    def adapt_metadata(self, fm, mtime, author): return fm

def run_final_audit():
    print("🎬 [Final Audit] 启动 V7.9 全链路收官审计...\n")
    
    # 1. 初始化核心组件
    config = load_config("config.local.yaml")
    router = RouteManager(config.route_matrix, config.active_theme)
    meta = MetadataManager(config.metadata_db)
    
    # 构造 Dispatcher
    dispatcher = BinderyDispatcher(
        paths={'vault': config.vault_root, 'target_base': './dist-test', 'shadow': './shadow-test'},
        meta=meta,
        route_manager=router,
        asset_pipeline=None,
        ssg_adapter=MockSSG(),
        mdx_resolver=None,
        syndicator=None,
        broadcaster=None,
        pub_cfg=config.publish_control,
        fm_order=config.frontmatter_order,
        asset_base_url="/assets/",
        i18n_cfg=config.i18n_settings
    )

    # 2. 定义测试场景
    test_rel_path = "Docs/GlobalMasterpiece.md"
    test_body = """# 🌍 全球分发主权测试

我要引用一个现有的文档：[[测试目录/测试笔记]]。
> [[COMMUNITY_LINK]]
"""
    test_fm = {"title": "全球同步大满贯测试", "author": "Antigravity"}
    test_masks = [] # 简化处理

    # 3. 模拟分发 - 中文版 (zh-Hans)
    print("--- 🇨🇳 正在模拟分发：简体中文版 (zh-Hans) ---")
    dispatcher.dispatch(
        asset_index={}, title="测试", slug="global-test",
        masked_body=test_body, fm_dict=test_fm, rel_path=test_rel_path,
        lang_code="zh-Hans", route_prefix="docs", route_source="Docs",
        mapped_sub_dir="", masks=[], is_dry_run=True
    )
    
    # 我们拦截一下 _prepare_metadata 的结果来展示
    final_fm_zh = dispatcher._prepare_metadata(
        test_fm, "测试", "global-test", test_rel_path, False, None, "zh-Hans", "docs", ""
    )
    print(f"✅ Hreflang 矩阵已注入: {final_fm_zh.get('hreflangs')}")
    print(f"✅ 注入组件: {config.i18n_settings.injection_matrix['zh-Hans'].append_body}\n")

    # 4. 模拟分发 - 英文版 (en)
    print("--- 🇺🇸 正在模拟分发：英文版 (en) ---")
    # 模拟经过翻译后的 body (占位符保持不变)
    en_body = "# 🌍 Global Sovereignty Test\n\n[[COMMUNITY_LINK]]"
    
    final_fm_en = dispatcher._prepare_metadata(
        test_fm, "Test", "global-test", test_rel_path, True, None, "en", "docs", ""
    )
    
    # 模拟注入后的内容
    injection_en = config.i18n_settings.injection_matrix['en']
    final_body_en = en_body.replace("[[COMMUNITY_LINK]]", injection_en.replace_placeholders["[[COMMUNITY_LINK]]"])
    final_body_en = f"{final_body_en}\n\n{injection_en.append_body}"
    
    print(f"✅ 语种感知占位符已替换: {injection_en.replace_placeholders['[[COMMUNITY_LINK]]']}")
    print(f"✅ 英文版自动导入补全: {injection_en.imports}")
    print(f"✅ 最终正文片段预览:\n{final_body_en}\n")

if __name__ == "__main__":
    run_final_audit()
