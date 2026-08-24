# -*- coding: utf-8 -*-
"""
🧪 [Test] 出版级自适应多段聚合翻译与全景语境引擎 (Adaptive Batch Translation) 10 大全景测试套件
涵盖：语种密度预算、模型段位降维、4 大深层冲突消解验证、局部精准拯救、DR 容灾接力与 Dry-Run 仿真
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.markup.base import MarkupBlock
from core.logic.ai.ai_scheduler_shards.batch_chunker import BatchChunker, TranslationBatch, BatchItem
from core.logic.ai.ai_scheduler_shards.batch_payload import BatchPayloadAssembler
from core.logic.ai.ai_scheduler_shards.batch_unpacker import BatchUnpacker
from core.logic.ai.ai_scheduler_shards.dispatch_ops import AISchedulerDispatchOps

class TestAdaptiveBatchTranslation(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    # 1. 验证多语种文字密度自适应预算
    def test_batch_chunking_density_and_limits(self):
        # 中文 1500 字符上限
        paras_zh, chars_zh = BatchChunker.resolve_budget_limits("zh")
        self.assertEqual(paras_zh, 8)
        self.assertEqual(chars_zh, 1500)

        # 英文 3000 字符上限
        paras_en, chars_en = BatchChunker.resolve_budget_limits("en")
        self.assertEqual(paras_en, 8)
        self.assertEqual(chars_en, 3000)

        # 构造 10 个简短任务
        tasks = [
            (i, MarkupBlock(f"这是测试段落 {i}，内容简洁明了。", "paragraph"), None)
            for i in range(10)
        ]
        batches = BatchChunker.chunk_tasks_into_batches(tasks, source_lang="zh", target_lang="en")
        # 10 个段落，单批上限 8 段，应切分成 2 批 (第一批 8 段，第二批 2 段)
        self.assertEqual(len(batches), 2)
        self.assertEqual(len(batches[0].items), 8)
        self.assertEqual(len(batches[1].items), 2)
        self.assertEqual(batches[0].items[0].block_idx, 0)
        self.assertEqual(batches[1].items[0].block_idx, 8)

    # 2. 验证模型算力段位自适应 (Flagship vs Local/Ollama)
    def test_model_tier_adaptive_scaling(self):
        mock_flagship = MagicMock()
        mock_flagship.node_name = "DeepSeek-V3-Primary"
        mock_flagship.provider = "deepseek"
        mock_flagship.model_name = "deepseek-chat"

        p_flag, c_flag = BatchChunker.resolve_budget_limits("zh", active_translator=mock_flagship)
        self.assertEqual(p_flag, 8)
        self.assertEqual(c_flag, 1500)

        mock_local = MagicMock()
        mock_local.node_name = "Ollama-Local-7B"
        mock_local.provider = "ollama"
        mock_local.model_name = "qwen2.5:7b"

        p_local, c_local = BatchChunker.resolve_budget_limits("zh", active_translator=mock_local)
        self.assertEqual(p_local, 3)
        self.assertEqual(c_local, 600)

    # 3. 冲突消解 1 验证：分段独立掩码命名空间隔离 (__MASK_B{idx}_{id}__) 与长词优先术语匹配
    def test_mask_namespace_isolation_and_glossary(self):
        glossary = {
            "OpenAI": "OpenAI 机构",
            "OpenAI API": "OpenAI 应用程序接口",
            "Publisher": "出版社"
        }
        batch = TranslationBatch(
            batch_id=0,
            items=[
                BatchItem(
                    seg_id="seg_4",
                    block_idx=4,
                    block=MarkupBlock("欢迎使用 [OpenAI API](https://openai.com) 进行出海发布。", "paragraph"),
                    raw_text="欢迎使用 [OpenAI API](https://openai.com) 进行出海发布。"
                ),
                BatchItem(
                    seg_id="seg_5",
                    block_idx=5,
                    block=MarkupBlock("这是第二个链接 [OpenAI](https://openai.com/about)，由 [[Publisher]] 驱动。", "paragraph"),
                    raw_text="这是第二个链接 [OpenAI](https://openai.com/about)，由 [[Publisher]] 驱动。"
                )
            ]
        )

        payload, item_masks_map, dry_run = BatchPayloadAssembler.assemble_batch_payload(
            batch, glossary=glossary
        )

        # 检查段落 4 与段落 5 的掩码前缀隔离
        self.assertIn("__MASK_B4_0__", payload)
        self.assertIn("__MASK_B5_0__", payload)
        # 检查术语长词优先：OpenAI API 应被优先匹配为 __GLOS_B4_0__，而不是将 OpenAI 单独切碎
        self.assertIn("__GLOS_B4_0__", payload)
        self.assertEqual(item_masks_map["seg_4"]["glossary_masks"]["__GLOS_B4_0__"], "OpenAI 应用程序接口")

        # 模拟大模型输出带有 XML 隔离标签 (直接原样保留占位符)
        llm_response = (
            f'<i18n_seg id="seg_4">\n'
            f'Welcome to use [__GLOS_B4_0__](__MASK_B4_0__) for global publishing.\n'
            f'</i18n_seg>\n\n'
            f'<i18n_seg id="seg_5">\n'
            f'{payload.split("<i18n_seg id=\"seg_5\">")[1].split("</i18n_seg>")[0].strip()}\n'
            f'</i18n_seg>'
        )

        unpack_res = BatchUnpacker.unpack_and_rescue(
            llm_response, item_masks_map, batch,
            structure_validator=AISchedulerDispatchOps.validate_block_structure
        )

        self.assertTrue(unpack_res.is_all_success)
        # 验证解包后段落 4 与段落 5 各自的链接与术语精准还原且无交叉污染
        seg_4_trans = unpack_res.succeeded_blocks[4]
        seg_5_trans = unpack_res.succeeded_blocks[5]

        self.assertIn("https://openai.com", seg_4_trans)
        self.assertIn("OpenAI 应用程序接口", seg_4_trans)
        self.assertIn("https://openai.com/about", seg_5_trans)
        self.assertIn("OpenAI 机构", seg_5_trans)
        self.assertIn("[[Publisher|出版社]]", seg_5_trans)

    # 4. 冲突消解 2 验证：Frontmatter 优先与已译大标题单向注入全景语境
    def test_frontmatter_pipeline_and_title_injection(self):
        batch = TranslationBatch(
            batch_id=0,
            items=[
                BatchItem(
                    seg_id="seg_0",
                    block_idx=0,
                    block=MarkupBlock("开篇第一段。", "paragraph"),
                    raw_text="开篇第一段。"
                )
            ]
        )
        translated_title = "Illacme Plenipes Global Guide"
        translated_desc = "A comprehensive architecture overview."

        payload, _, _ = BatchPayloadAssembler.assemble_batch_payload(
            batch,
            article_title=translated_title,
            article_desc=translated_desc
        )

        self.assertIn("<article_context>", payload)
        self.assertIn(f"<article_title>{translated_title}</article_title>", payload)
        self.assertIn(f"<article_summary>{translated_desc}</article_summary>", payload)

    # 5. 冲突消解 3 验证：缓存跳过后的原稿物理绝对索引 (block_idx) 准确透传
    def test_absolute_block_indexing_with_cache_skips(self):
        # 假设原稿有 10 个段落，0, 1, 2 命中缓存，3 为代码块跳过，仅 4, 7 需要翻译
        tasks = [
            (4, MarkupBlock("第 4 段内容", "paragraph"), None),
            (7, MarkupBlock("第 7 段内容", "paragraph"), None)
        ]
        batches = BatchChunker.chunk_tasks_into_batches(tasks, source_lang="zh", target_lang="en")
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0].items[0].seg_id, "seg_4")
        self.assertEqual(batches[0].items[0].block_idx, 4)
        self.assertEqual(batches[0].items[1].seg_id, "seg_7")
        self.assertEqual(batches[0].items[1].block_idx, 7)

        payload, item_masks_map, _ = BatchPayloadAssembler.assemble_batch_payload(batches[0])
        self.assertIn('<i18n_seg id="seg_4">', payload)
        self.assertIn('<i18n_seg id="seg_7">', payload)

        mock_resp = (
            '<i18n_seg id="seg_4">Paragraph 4 content in English.</i18n_seg>\n'
            '<i18n_seg id="seg_7">Paragraph 7 content in English.</i18n_seg>'
        )
        res = BatchUnpacker.unpack_and_rescue(mock_resp, item_masks_map, batches[0])
        self.assertTrue(res.is_all_success)
        # 槽位必须是 4 和 7，绝不能是 0 和 1
        self.assertIn(4, res.succeeded_blocks)
        self.assertIn(7, res.succeeded_blocks)
        self.assertEqual(res.succeeded_blocks[4], "Paragraph 4 content in English.")
        self.assertEqual(res.succeeded_blocks[7], "Paragraph 7 content in English.")

    # 6. 冲突消解 4 验证：局部精准拯救 (Selective Rescue) 与漏译段落标记
    def test_slot_barrier_and_selective_rescue(self):
        batch = TranslationBatch(
            batch_id=0,
            items=[
                BatchItem(seg_id="seg_4", block_idx=4, block=MarkupBlock("段落 4", "p"), raw_text="段落 4"),
                BatchItem(seg_id="seg_5", block_idx=5, block=MarkupBlock("段落 5 漏译", "p"), raw_text="段落 5 漏译"),
                BatchItem(seg_id="seg_6", block_idx=6, block=MarkupBlock("段落 6", "p"), raw_text="段落 6")
            ]
        )
        _, item_masks_map, _ = BatchPayloadAssembler.assemble_batch_payload(batch)

        # 模拟大模型漏吐了 seg_5
        flawed_resp = (
            '<i18n_seg id="seg_4">Paragraph 4 translated.</i18n_seg>\n'
            '<i18n_seg id="seg_6">Paragraph 6 translated.</i18n_seg>'
        )
        unpack_res = BatchUnpacker.unpack_and_rescue(flawed_resp, item_masks_map, batch)

        self.assertFalse(unpack_res.is_all_success)
        # 4 和 6 成功拯救并产出
        self.assertEqual(len(unpack_res.succeeded_blocks), 2)
        self.assertEqual(unpack_res.succeeded_blocks[4], "Paragraph 4 translated.")
        self.assertEqual(unpack_res.succeeded_blocks[6], "Paragraph 6 translated.")
        # 5 被精确抓取为失败条目
        self.assertEqual(len(unpack_res.failed_items), 1)
        self.assertEqual(unpack_res.failed_items[0].seg_id, "seg_5")
        self.assertIn("seg_5", unpack_res.missing_seg_ids)

    # 7. 验证多品牌版图专属风格装配与只读代码语境注入
    def test_imprint_scoped_context_injection(self):
        batch = TranslationBatch(
            batch_id=0,
            items=[
                BatchItem(seg_id="seg_1", block_idx=1, block=MarkupBlock("请参考下方配置。", "p"), raw_text="请参考下方配置。")
            ],
            context_refs=[
                {"type": "code", "content": "```yaml\nversion: 2.0\n```"}
            ]
        )
        payload, _, _ = BatchPayloadAssembler.assemble_batch_payload(batch)
        self.assertIn("<readonly_references>", payload)
        self.assertIn('<context_ref type="code">', payload)
        self.assertIn("version: 2.0", payload)

    # 8. 验证超长单段自适应安全标点分句切分 (Sub-Sentence Splitting)
    def test_sub_sentence_splitting_for_oversized_block(self):
        long_text = (
            "这是第一句超长中文说明测试内容。"
            "这是第二句同样非常详尽的技术原理解释。"
            "这是第三句关于架构容灾与高可用的深度阐述。"
        )
        # 限制每段最大 30 字符
        sub_parts = BatchChunker.split_oversized_text(long_text, max_chars=30)
        self.assertTrue(len(sub_parts) >= 2)
        for part in sub_parts:
            self.assertTrue(len(part) <= 35)

    # 9. 验证全库出海 Token 预算前置估算
    def test_preflight_token_budget_estimation(self):
        tasks = [
            (0, MarkupBlock("中文字符测试" * 20, "p"), None), # 120 字符
            (1, MarkupBlock("更多技术内容" * 30, "p"), None), # 180 字符
        ]
        # 300 字符，目标 3 种语言
        est = BatchChunker.estimate_batch_tokens(tasks, source_lang="zh", target_langs_count=3)
        self.assertEqual(est["total_chars"], 300)
        self.assertEqual(est["tasks_count"], 2)
        self.assertTrue(est["estimated_total_tokens"] > 0)

    # 10. 验证 Dry-Run 沙盘演练高保真 XML 虚拟应答与解包
    def test_abort_sync_and_dry_run_fidelity(self):
        batch = TranslationBatch(
            batch_id=0,
            target_lang="ja",
            items=[
                BatchItem(seg_id="seg_0", block_idx=0, block=MarkupBlock("主权出版社系统。", "p"), raw_text="主权出版社系统。")
            ]
        )
        payload, item_masks_map, dry_run_resp = BatchPayloadAssembler.assemble_batch_payload(
            batch, is_dry_run=True
        )
        self.assertIn("<i18n_seg id=\"seg_0\">", dry_run_resp)
        self.assertIn("[DRY-RUN JA TRANSLATION OF seg_0]", dry_run_resp)

        # 解包 Dry-Run 产物
        unpack_res = BatchUnpacker.unpack_and_rescue(dry_run_resp, item_masks_map, batch)
        self.assertTrue(unpack_res.is_all_success)
        self.assertIn(0, unpack_res.succeeded_blocks)
        self.assertIn("DRY-RUN JA TRANSLATION", unpack_res.succeeded_blocks[0])

    # 11. 验证复合 HTML 块原子化封包（禁止跨标签生硬切分产生残缺碎块）
    def test_html_container_atomic_batching_not_fragmented(self):
        html_content = '<div class="home-hero-container" style="padding: 4rem 1rem;">' + '<p>长内容描述</p>' * 100 + '</div>'
        self.assertTrue(len(html_content) > 1000)
        tasks = [(0, MarkupBlock(html_content, "html"), None)]
        batches = BatchChunker.chunk_tasks_into_batches(tasks, source_lang="zh", target_lang="en")
        # 即使超过字符限制，HTML 块也必须作为原子整体独立成 1 个批次，不得产生 _sub 碎片
        self.assertEqual(len(batches), 1)
        self.assertEqual(len(batches[0].items), 1)
        self.assertEqual(batches[0].items[0].seg_id, "seg_0")
        self.assertFalse(batches[0].items[0].is_sub_split)

    # 12. 验证扫描器路径过滤精确匹配（防止 index.md 误匹配 Showcase/index.md 等同名子目录文件）
    def test_scanner_requested_paths_exact_match(self):
        from core.runtime.orchestration.scanner import build_task_queue
        mock_engine = MagicMock()
        mock_engine.vault_root = "/tmp/mock_vault"
        mock_engine.config.system.allowed_extensions = [".md"]
        mock_engine._is_excluded = MagicMock(return_value=False)
        mock_engine.route_matrix = []

        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                ("/tmp/mock_vault", [], ["index.md"]),
                ("/tmp/mock_vault/Showcase", [], ["index.md"]),
                ("/tmp/mock_vault/Docs", [], ["index.md"]),
            ]
            with patch("core.governance.license_guard.LicenseGuard.is_pro_feature_allowed", return_value=True):
                # 仅请求顶层 index.md
                task_queue, found_files = build_task_queue(mock_engine, requested_paths=["index.md"])
                self.assertIn("index.md", found_files)
                self.assertNotIn("Showcase/index.md", found_files)
                self.assertNotIn("Docs/index.md", found_files)
                self.assertEqual(len(found_files), 1)

    # 13. 验证 MarkupBlock SSOT 唯一段落过滤与可翻译性判定
    def test_markup_block_ssot_translatability_and_spacer_rules(self):
        # 纯注释
        b_comment = MarkupBlock("<!-- 这是一个纯注释 -->\n<!-- 第二行注释 -->", "comment")
        self.assertTrue(MarkupBlock.is_ignorable_spacer(b_comment.content))
        self.assertFalse(b_comment.is_translatable)

        # 纯分割线
        b_hr = MarkupBlock("---", "hr")
        self.assertTrue(MarkupBlock.is_ignorable_spacer(b_hr.content))
        self.assertFalse(b_hr.is_translatable)

        # 带注释开头的复合 HTML 块（包含实质可翻译文本）
        b_mixed_html = MarkupBlock("<!-- 📊 数据矩阵 -->\n<div class='stats'><span class='num'>100+</span> 语种</div>", "html")
        self.assertFalse(MarkupBlock.is_ignorable_spacer(b_mixed_html.content))
        self.assertTrue(b_mixed_html.is_translatable)

        # 常规段落
        b_para = MarkupBlock("这是普通的 Markdown 文本段落。", "paragraph")
        self.assertFalse(MarkupBlock.is_ignorable_spacer(b_para.content))
        self.assertTrue(b_para.is_translatable)

if __name__ == '__main__':
    unittest.main()
