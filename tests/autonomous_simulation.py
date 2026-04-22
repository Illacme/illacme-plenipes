#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Illacme-plenipes - Autonomous Simulation Sandbox (仿真沙盒)
职责：在 Shadow 目录重演全量同步逻辑，执行 [Simulation Gating] 门禁校验。
"""

import os
import shutil
import tempfile
import sys
import logging
import hashlib
from unittest.mock import MagicMock

# 🚀 动态挂载项目根目录，确保影子环境导入不失联
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engine import IllacmeEngine

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("Illacme.Simulation")

def verify_docs_sync_hook():
    """TDR & AEL Protocol: 验证核心文档与历史归档的同步约束"""
    if os.environ.get("ILLACME_SKIP_DOC_CHECK") == "TRUE":
        logger.warning("   └── ⚠️ [TDR] 检测到 ILLACME_SKIP_DOC_CHECK=TRUE，已跳过全量文档同步强校验。")
        return

    import subprocess
    logger.info("🧪 [仿真] 挂载 AEL & TDR 全矩阵文档约束钩子...")
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        changes = result.stdout
        
        core_modified = False
        docs_modified = False
        history_added = False
        any_modified = False
        
        for line in changes.split('\n'):
            if len(line) < 4:
                continue
            any_modified = True
            path = line[3:] # git porcelain format " M path/to/file"
            
            # Rule 1: Core modification detect
            if path.startswith("core/") or path.startswith("plenipes.py"):
                core_modified = True
                
            # Rule 2: Architecture docs detect
            if path.startswith("docs/") or path.startswith("CHANGELOG.md") or path.startswith(".plenipes/ROADMAP.md"):
                docs_modified = True
                
            # Rule 3: AEL History detect
            if path.startswith(".plenipes/history/"):
                history_added = True
                
        # Assertion 1: Living Documentation Mandate
        if core_modified and not docs_modified:
            raise AssertionError("[Living Documentation Mandate] 核心管线(core/)已被修改，但未同步更新 docs/、CHANGELOG.md 或 ROADMAP.md！\n"
                                 "由于违反底层活化文档规范，测试已强行熔断。")
            
        # Assertion 2: Genetic Archiving (AEL) Mandate
        if any_modified and not history_added:
            raise AssertionError("[AEL Protocol Mandate] 检测到代码库发生物理变更，但未在 .plenipes/history/ 下沉淀本次迭代的实施方案与任务清单！\n"
                                 "由于违反全自动演化矩阵基因沉淀规范，测试已强行熔断。")
            
        if any_modified:
            logger.info("   └── ✅ [AEL & TDR] 探测到历史归档与业务文档均已触发更新信号，约束已通过。")
            
    except subprocess.CalledProcessError:
        logger.warning("   └── ⚠️ [TDR] 非 Git 仓库或 Git 执行失败，跳过文档关联校验。")

def run_shadow_simulation():
    """执行影子执行仿真"""
    logger.info("🧪 [仿真] 启动影子沙盒校验 (Simulation Gating)...")
    verify_docs_sync_hook()
    
    # 1. 创建临时工作区
    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"🧪 [仿真] 创建沙盒镜像: {tmpdir}")
        
        # 2. 导出运行环境
        os.makedirs(os.path.join(tmpdir, "core"), exist_ok=True)
        shutil.copytree("core", os.path.join(tmpdir, "core"), dirs_exist_ok=True)
        shutil.copy("plenipes.py", os.path.join(tmpdir, "plenipes.py"))
        shutil.copy("config.yaml", os.path.join(tmpdir, "config.yaml"))
        
        os.makedirs(os.path.join(tmpdir, "content-vault"), exist_ok=True)
        
        # 3. 挂载仿真引擎
        try:
            origin_cwd = os.getcwd()
            os.chdir(tmpdir)
            os.environ["ILLACME_SIMULATION_MODE"] = "TRUE"
            
            engine = IllacmeEngine("config.yaml")
            
            # 4. 执行试运行 (Dry Run) 与 SLSH 自愈校验
            logger.info("🧪 [仿真] 正在试探 Pipeline 完整性与 SLSH 自愈...")
            
            test_file = os.path.join(tmpdir, "content-vault", "break_link_test.md")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("# SLSH Test\n- [[Target]]\n")
            
            os.makedirs(os.path.join(tmpdir, "content-vault", "subfolder"), exist_ok=True)
            with open(os.path.join(tmpdir, "content-vault", "subfolder", "Target.md"), 'w') as f:
                 f.write("Target Content")
            
            # ==========================================
            # 🚀 [仿真增强] 4. 初始化引擎副本
            # ==========================================
            engine = IllacmeEngine(os.path.join(tmpdir, "config.yaml"))
            
            # 🚀 [V16.6 补丁]：强行对齐引擎物理根，防止相对路径爬升导致的任务偏差
            engine.vault_root = os.path.abspath(os.path.join(tmpdir, "content-vault"))
            engine.paths['vault'] = engine.vault_root
            engine.paths['shadow'] = os.path.join(engine.vault_root, '.illacme-shadow')
            
            # 🚀 [Resonance 补丁]：显式激活多语言 Alt 描述生成
            if hasattr(engine.config, 'image_settings'):
                engine.config.image_settings.multilingual_alt = True
                logger.info("🧪 [仿真] 已显式激活 multilingual_alt (Resonance Sovereignty Force-On)")
            
            # 手动执行健康检查自愈
            engine.sentinel.run_health_check(auto_fix=True)
            
            # ==========================================
            # 🚀 [仿真增强] 5. ADMI v2.0 视觉感知与多语言校验
            # ==========================================
            logger.info("🧪 [仿真] 进入 ADMI v2.0 阶段 (视觉感知与多语言同步)...")
            
            # 创建物理图片模拟
            img_path = os.path.join(tmpdir, "content-vault", "vision_test.jpg")
            with open(img_path, 'wb') as f:
                f.write(b"MOCK_IMAGE_DATA_001") # MD5: 6cd0f9a2fb64b2d58cb5303d7e793910
                
            doc_with_img = os.path.join(tmpdir, "content-vault", "vision_doc.md")
            with open(doc_with_img, 'w', encoding='utf-8') as f:
                f.write("# Vision Test\n![](./vision_test.jpg)\n")
                
            # 🚀 [V16.6 核心对齐]：文件创建后，必须强制引擎重载物理索引，否则解蔽器将无法定位资产指纹
            from core.vault_indexer import VaultIndexer
            engine.md_index, engine.asset_index = VaultIndexer.build_indexes(engine.paths['vault'])
            engine.asset_pipeline.asset_index = engine.asset_index
            
            # 模拟 AI 视觉与翻译返回
            from unittest.mock import MagicMock, patch
            
            # 建立坚不可摧的 Mock 阵地
            def mock_translate_side_effect(text, src, tgt, context_type="body"):
                import re
                # 🚀 [Resonance 补丁]：对齐 [[STB_MASK_n]] 标准格式
                masks = re.findall(r'\[\[STB_MASK_(\d+)\]\]', text)
                mask_str = " ".join([f"[[STB_MASK_{m}]]" for m in masks])
                if "机械章鱼" in text:
                    return f"A mechanical octopus wearing sunglasses. {mask_str}"
                if "Translate this title" in text:
                    return "Vision Test Translated"
                if "JSON SEO" in text or "Analyze this article" in text:
                    return '{"description": "SEO Description", "keywords": "test"}'
                return f"Mocked {tgt}: {mask_str}"

            engine.translator.describe_image = MagicMock(return_value="一只戴着墨镜的机械章鱼")
            engine.translator.translate = MagicMock(side_effect=mock_translate_side_effect)
            engine.translator.generate_slug = MagicMock(return_value=("vision-test-slug", True))
            engine.translator.generate_seo_metadata = MagicMock(return_value=({"description": "SEO", "keywords": "k1"}, True))
            
            # 执行同步
            engine.sync_document(doc_with_img, "docs", "content-vault", is_dry_run=False)
            
            # 校验 1：账本多语言矩阵
            img_hash = hashlib.md5(b"MOCK_IMAGE_DATA_001").hexdigest()
            cached_meta = engine.meta.get_asset_metadata(img_hash)
            alt_map = cached_meta.get("alt_texts", {})
            
            if "机械章鱼" in alt_map.get("zh", "") and "octopus" in alt_map.get("en", "").lower():
                logger.info("   └── ✅ [账本校验] 多语言 Alt 描述矩阵已成功建立。")
            else:
                logger.error(f"账本内容异常: {alt_map}")
                raise Exception("多语言 Alt 矩阵建立失败")
                
            # ==========================================
            # 🚀 [仿真增强] 6. Syndication & Unmasking 校验
            # ==========================================
            logger.info("🧪 [仿真] 进入解蔽与分发校验阶段...")
            
            # 检查 en 目录下的产物
            en_prefix = engine.i18n.targets[0].lang_code # en
            # 🚀 [V16.6 核心对齐]：影子资产检索路径必须与引擎执行路径绝对一致
            actual_shadow_root = engine.paths['shadow']
            en_shadow_dir = os.path.join(actual_shadow_root, en_prefix, "docs")
            
            # 找到生成的 en 文件 (由于使用了 Mock Slug，文件名为 vision-test-slug.md)
            en_file_path = os.path.join(en_shadow_dir, "vision-test-slug.md")
            
            if not os.path.exists(en_file_path):
                # 尝试递归查找以应对不同的 Route Prefix 逻辑
                logger.debug(f"🔍 [补救尝试] 正在搜索翻译后的影子资产: {actual_shadow_root}")
                found = False
                for root, dirs, files in os.walk(actual_shadow_root):
                    for f in files:
                        if "vision-test-slug" in f:
                            en_file_path = os.path.join(root, f)
                            found = True
                            break
                    if found: break
                
                if not found:
                    raise Exception(f"未发现翻译后的目标语言影子资产。搜索起点: {actual_shadow_root}")
                
            with open(en_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "mechanical octopus" in content:
                    logger.info("   └── ✅ [解蔽校验] 目标语言影子产物已成功回填本地化 Alt 描述。")
                else:
                    logger.error(f"产物内容异常: {content}")
                    raise Exception("目标语言 Alt 回填失败")

            os.chdir(origin_cwd)
            logger.info("✅ [仿真] 全量影子门禁校验通过！Project Resonance 准备全量交付。")
            return True
            
        except Exception as e:
            logger.error(f"❌ [仿真] 影子执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = run_shadow_simulation()
    sys.exit(0 if success else 1)
