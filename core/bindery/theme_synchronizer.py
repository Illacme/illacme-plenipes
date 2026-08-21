# -*- coding: utf-8 -*-
"""
🎨 Illacme Bindery - Theme Synchronizer (主题母本一致性同步引擎)
职责：负责将官方自带主题母本 (Mother Theme Templates) 的核心基础设施与更新热同步至所有品牌实例。
🛡️ [V100.9]：确保多品牌矩阵与母本主题时刻保持 100% 协议一致性与自愈。
"""

import os
import shutil
from typing import List, Dict, Any
from core.utils.tracing import tlog

class ThemeSynchronizer:
    """
    主题母本同步引擎：负责全自动自愈与保持各品牌主题与母本一致。
    """
    
    EXCLUDE_DIRS = {
        "node_modules", ".git", "dist", "build", ".astro", ".temp", ".vscode", "__pycache__"
    }
    EXCLUDE_FILES = {
        ".DS_Store"
    }
    
    @classmethod
    def sync_all_imprints(cls, mother_themes_dir: str = "themes", imprints_dir: str = "imprints") -> Dict[str, List[str]]:
        """
        扫描所有品牌目录并将母本主题的核心基础设施与模版同步至各品牌主题实例。
        
        Returns:
            Dict[str, List[str]]: 每个品牌更新的文件列表。
        """
        results: Dict[str, List[str]] = {}
        if not os.path.exists(mother_themes_dir) or not os.path.exists(imprints_dir):
            return results

        # 获取所有母本主题 (过滤并自动归一化 default 别名)
        mother_themes = {}
        for entry in os.scandir(mother_themes_dir):
            if entry.is_dir() and not entry.name.startswith((".", "__")):
                if entry.name == "default":
                    continue
                mother_themes[entry.name] = entry.path

        # 遍历所有品牌
        for brand_entry in os.scandir(imprints_dir):
            if not brand_entry.is_dir() or brand_entry.name.startswith((".", "__")):
                continue
            
            brand_themes_dir = os.path.join(brand_entry.path, "themes")
            os.makedirs(brand_themes_dir, exist_ok=True)

            # 🧹 清理历史旧版默认主题残留目录 (themes/default -> themes/sovereign)
            legacy_default_dir = os.path.join(brand_themes_dir, "default")
            if os.path.exists(legacy_default_dir) and "sovereign" in mother_themes:
                try:
                    shutil.rmtree(legacy_default_dir)
                    tlog.debug(f"🧹 [主题清理] 已自动清理历史废弃的旧版默认主题目录: {legacy_default_dir}")
                except Exception:
                    pass
            
            brand_updated_files = []
            for theme_name, mother_theme_path in mother_themes.items():
                brand_theme_path = os.path.join(brand_themes_dir, theme_name)
                
                # 递归同步母本主题内的所有模板、脚本、钩子与静态资源文件 (排除构建产物与临时目录)
                for root, dirs, files in os.walk(mother_theme_path):
                    # 过滤排除目录
                    dirs[:] = [d for d in dirs if d not in cls.EXCLUDE_DIRS and not d.startswith(".")]
                    rel_dir = os.path.relpath(root, mother_theme_path)
                    
                    for fname in files:
                        if fname in cls.EXCLUDE_FILES or fname.startswith("."):
                            continue
                        
                        rel_file = os.path.normpath(os.path.join(rel_dir, fname)) if rel_dir != "." else fname
                        mother_file = os.path.join(mother_theme_path, rel_file)
                        brand_file = os.path.join(brand_theme_path, rel_file)
                        
                        should_update = False
                        if not os.path.exists(brand_file):
                            should_update = True
                        else:
                            try:
                                with open(mother_file, 'rb') as f1, open(brand_file, 'rb') as f2:
                                    if f1.read() != f2.read():
                                        should_update = True
                            except Exception:
                                should_update = True
                                
                        if should_update:
                            os.makedirs(os.path.dirname(brand_file), exist_ok=True)
                            shutil.copy2(mother_file, brand_file)
                            brand_updated_files.append(f"{theme_name}/{rel_file}")
                            tlog.debug(f"🔄 [主题同步] 已同步核心母本文件 -> {brand_file}")
            
            if brand_updated_files:
                results[brand_entry.name] = brand_updated_files
        
        if results:
            total_updates = sum(len(v) for v in results.values())
            tlog.info(f"✨ [主题同步] 已完成 {len(results)} 个品牌共 {total_updates} 个主题核心文件的热同步。")
            
        return results
