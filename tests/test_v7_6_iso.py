#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 将项目根目录加入路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils.language_hub import LanguageHub

def test_language_hub():
    print("🧪 [Test] LanguageHub 识别测试...")
    
    test_cases = [
        ("简体中文", "zh-Hans"),
        ("Traditional Chinese", "zh-Hant"),
        ("English", "en"),
        ("Japanese", "ja"),
        ("日语", "ja"),
        ("法语", "fr"),
        ("zh-cn", "zh-Hans"),
    ]
    
    for name, expected in test_cases:
        actual = LanguageHub.resolve_to_iso(name)
        status = "✅" if actual == expected else "❌"
        print(f"  {status} {name:20} -> {actual} (Expected: {expected})")

def test_theme_awareness():
    print("\n🧪 [Test] 主题感知路径对齐测试...")
    
    iso_code = "zh-Hans"
    
    # Docusaurus 偏好
    path_doc = LanguageHub.get_physical_path(iso_code, "docusaurus")
    print(f"  Docusaurus: {iso_code} -> {path_doc} (Expected: zh-Hans)")
    
    # Starlight 偏好
    path_star = LanguageHub.get_physical_path(iso_code, "starlight")
    print(f"  Starlight:  {iso_code} -> {path_star} (Expected: zh-cn)")

def test_imprint_vault_bootstrapping():
    print("\n🧪 [Test] 版图空文库空间自愈引导（战役二）测试...")
    import tempfile
    from core.governance.imprint_manager import im
    
    # 建立独立的临时测试文库
    with tempfile.TemporaryDirectory() as temp_vault:
        imprint_name = "test-wiz-imprint"
        
        # 清除干扰
        im.delete_imprint(imprint_name)
        
        try:
            from unittest.mock import patch
            from core.governance.license_guard import LicenseGuard
            im.active_imprint = "default"
            # 启动初始化与自愈空间灌入 (使用 LicenseGuard 隔离打桩)
            with patch.object(LicenseGuard, "is_pro_feature_allowed", return_value=True), \
                 patch.object(LicenseGuard, "get_max_imprints", return_value=999):
                success = im.init_sovereign_imprint(
                    name=imprint_name,
                    manuscripts_path=temp_vault,
                    imprint_name="测试虚拟向导出版社",
                    bootstrap_vault=True
                )
            
            assert success is True, "❌ 独立版图空间划定失败"
            
            # 验证三级子目录与欢迎文稿自愈落地
            for sub in ["Blog", "Docs", "Pages"]:
                sub_path = os.path.join(temp_vault, sub)
                assert os.path.exists(sub_path), f"❌ 缺失标准物理子目录: {sub}"
                assert os.path.isdir(sub_path), f"❌ 标准物理子目录应为文件夹: {sub}"
                
            welcome_file = os.path.join(temp_vault, "Blog", "welcome-to-illacme.md")
            assert os.path.exists(welcome_file), "❌ 缺失新手欢迎文稿: welcome-to-illacme.md"
            
            with open(welcome_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "welcome-to-illacme" in content or "欢迎" in content, "❌ 欢迎指南内容校验未通过"
                
            print("  ✅ [自愈测试] 文件夹建立与欢迎文档注入 100% 严丝合缝！")
            
        finally:
            # 清理 imprint 配置与缓存
            im.delete_imprint(imprint_name)

def test_force_source_prefix_route_resolution():
    print("\n🧪 [Test] 主语言路径前缀强制化 (force_source_prefix) 路由解析测试...")
    from core.editorial.router import RouteManager
    
    class MockSSG:
        def get_feature_slots(self):
            return {
                "docs": {
                    "single": "docs/{sub_dir}",
                    "multi": "{lang}/docs/{sub_dir}"
                }
            }
        def get_language_code(self, code):
            return code

    ssg = MockSSG()
    
    # 场景 A: 启用强制主语言路径前缀
    router_forced = RouteManager(
        meta_manager=None,
        translator_factory=None,
        lang_mapping={},
        default_lang="zh",
        active_theme="starlight",
        ssg_adapter=ssg,
        force_source_prefix=True
    )
    
    phys_path_forced = router_forced.resolve_physical_path(
        base_path="/dist",
        lang_code="zh",
        route_prefix="",
        mapped_sub_dir="",
        slug="hello",
        ext=".md",
        source_type="docs"
    )
    logical_url_forced = router_forced.resolve_logical_url(
        lang_code="zh",
        route_prefix="docs",
        mapped_sub_dir="",
        slug="hello"
    )
    
    # 场景 B: 禁用强制主语言路径前缀（默认行为）
    router_default = RouteManager(
        meta_manager=None,
        translator_factory=None,
        lang_mapping={},
        default_lang="zh",
        active_theme="starlight",
        ssg_adapter=ssg,
        force_source_prefix=False
    )
    
    phys_path_default = router_default.resolve_physical_path(
        base_path="/dist",
        lang_code="zh",
        route_prefix="",
        mapped_sub_dir="",
        slug="hello",
        ext=".md",
        source_type="docs"
    )
    logical_url_default = router_default.resolve_logical_url(
        lang_code="zh",
        route_prefix="docs",
        mapped_sub_dir="",
        slug="hello"
    )
    
    # 验证强制前缀场景下的物理与逻辑路径对正 (带前缀)
    assert "zh/docs/hello" in phys_path_forced.replace("\\", "/")
    assert logical_url_forced == "/zh/docs/hello"
    
    # 验证默认场景下的物理与逻辑路径对正 (不带前缀)
    assert "zh" not in phys_path_default.replace("\\", "/")
    assert logical_url_default == "/docs/hello"
    
    print("  ✅ [前缀对齐测试] 强制主语言路径前缀功能物理与逻辑路径 100% 对齐一致！")

if __name__ == "__main__":
    test_language_hub()
    test_theme_awareness()
    test_imprint_vault_bootstrapping()
    test_force_source_prefix_route_resolution()
