#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Imprint Manager
职责：管理多出版社品牌的物理生命周期、镜像分发与环境隔离。
🛡️ [V50.3]：主权 Imprint 治理引擎。
"""


import os
import shutil
import yaml
from typing import List, Dict, Optional
from core.utils.tracing import tlog
from core.config.constants import (
    CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR,
    PROMPTS_NAME, DIALECTS_DIR, DEFAULT_DIALECT_NAME
)
from core.governance.license_guard import LicenseGuard
from core.governance.secret_manager import secrets


class ImprintManager:
    """🚀 [V50.3] 主权 Imprint 管家：负责物理出版社品牌的“划定”与“治理”"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        
        # 🚀 [V50.3] 物理主权对正：主权 Imprint 必须存在于 imprints 目录
        self.imprint_root = os.path.join(self.root_dir, "imprints")
        self.active_imprint = "default"
        
        # 确保主权 Imprint 根目录存在
        if not os.path.exists(self.imprint_root):
            os.makedirs(self.imprint_root)

    def init_sovereign_imprint(self, name: str, manuscripts_path: str, imprint_name: Optional[str] = None, bootstrap_vault: bool = False, theme: Optional[str] = None) -> bool:
        """🚀 [V50.3] 划定一个新的主权出版社品牌 (Imprint)"""

        # 1. 准入校验：检查是否有权创建新空间，禁止覆盖已有物理空间
        imprint_path = os.path.join(self.imprint_root, name)
        if os.path.exists(imprint_path):
            tlog.error(f"🛑 [准入拦截] (物理冲突) 出版品牌目录 '{name}' 已在磁盘存在，禁止重复创建覆盖。")
            return False

        existing = self.list_imprints()
        custom_existing = [imp for imp in existing if imp.get("id") != "default"]
        max_custom = LicenseGuard.get_max_custom_imprints()
        try:
            max_total = LicenseGuard.get_max_imprints()
            if max_total > 2 and (max_total - 1) > max_custom:
                max_custom = max_total - 1
        except Exception:
            pass
        if len(custom_existing) >= max_custom:
            tier_name = LicenseGuard.get_license_info().get("tier_name", "免费社区版")
            tlog.error(f"🛑 [准入拦截] (权限受限) 当前{tier_name}支持管理 {max_custom} 个自定义独立品牌。请删除已有自定义品牌后再创建，或升级以解锁更多版图。")
            return False
 
        tlog.info(f"🏗️ [品牌划定] (创建出版社) 正在为出版品牌 '{name}' 勘测物理版图...")
        
        # 2. 建立物理目录树
        from core.config.constants import DIALECTS_DIR, LOGS_DIR, THEMES_DIR, METADATA_DIR
        dirs = [CONFIG_DIR, os.path.join(CONFIG_DIR, DIALECTS_DIR), "cache", METADATA_DIR, THEMES_DIR, LOGS_DIR]
        for d in dirs:
            os.makedirs(os.path.join(imprint_path, d), exist_ok=True)

        # 3. 镜像分发：分发母本配置与方言
        self._mirror_mother_templates(imprint_path, manuscripts_path, imprint_name, theme=theme)
        
        # 4. 🌱 [V75.6] 空内容金库自愈初始化引导
        if manuscripts_path:
            try:
                real_vault_path = os.path.abspath(os.path.expanduser(manuscripts_path))
                os.makedirs(real_vault_path, exist_ok=True)
                
                # 若启用演示注入且目标文件夹为空，自动灌入标准结构与各装帧模板演示手稿
                if bootstrap_vault and not os.listdir(real_vault_path):
                    tlog.info(f"📂 [文库自愈] 创作者已启用演示资源注入，开始为每种装帧模板生成特性演示手稿: {real_vault_path}")
                    self._inject_template_showcase_manuscripts(real_vault_path, press_name=imprint_name or name)
                    tlog.success("✅ [文库自愈完成] 全套装帧模板特性演示手稿与双链星系拓扑已物理落盘！")
            except Exception as bootstrap_err:
                tlog.error(f"❌ [文库初始化失败] 无法自愈注入文件结构: {bootstrap_err}")

        tlog.success(f"✅ [品牌落成] (出版社已就绪) 出版品牌 '{name}' 物理主权已确立。")

        return True


    def _mirror_mother_templates(self, imprint_path: str, manuscripts_path: str, imprint_name: Optional[str] = None, theme: Optional[str] = None):
        """从核心母本库镜像初始化配置"""
        # A. 系统基础配置 (🛡️ V50.3 主权定型精简版)
        # 仅固化保留该品牌特有的“物理主权”描述：
        base_config = {
            "imprint_name": imprint_name or os.path.basename(imprint_path),
            "imprint_description": "这是一个主权出版版图节点。",
            "vault_root": manuscripts_path,
            "theme": theme or "sovereign",
            
            "system": {
                "data_root": imprint_path,
                "log_level": "INFO"
            },

            "route_matrix": []
        }

        # 🧪 [V50.3] 凭据主权加固：执行物理脱敏
        secrets.mask_dict(base_config)

        # 🛡️ [V55.22] 物理主权重建：使用统一的常量定义
        from core.utils.common import promote_config_keys
        base_config = promote_config_keys(base_config)
        with open(os.path.join(imprint_path, CONFIG_DIR, CONFIG_IMPRINT_NAME), 'w', encoding='utf-8') as f:
            yaml.safe_dump(base_config, f, allow_unicode=True)


        # B. 镜像方言母本 (Prompts)
        mother_prompts = os.path.join(self.root_dir, CONFIG_DIR, PROMPTS_NAME)
        if os.path.exists(mother_prompts):
            dialect_target_dir = os.path.join(imprint_path, CONFIG_DIR, DIALECTS_DIR)
            os.makedirs(dialect_target_dir, exist_ok=True)
            shutil.copy2(mother_prompts, os.path.join(dialect_target_dir, DEFAULT_DIALECT_NAME))
            tlog.debug(f"📜 [方言分发] 已为 '{os.path.basename(imprint_path)}' 镜像默认方言。")


    def list_imprints(self) -> List[Dict[str, str]]:
        """扫描 Imprint 根目录下的所有主权出版社品牌"""
        imprints = []
        if not os.path.exists(self.imprint_root):
            return imprints
 
        active_imprint = self.get_active_imprint()
        path = os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME)

        for entry in os.scandir(self.imprint_root):
            if entry.is_dir():
                config_path = os.path.join(entry.path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(config_path):
                    p_name = entry.name
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            cfg = yaml.safe_load(f) or {}
                            p_name = cfg.get("imprint_name", cfg.get("press_name", entry.name))
                    except Exception:
                        cfg = {}
                    
                    # 🚀 [V55.10] 增加全量金库溯源：如果品牌内缺失，尝试从全局底座补全
                    v_path = cfg.get("vault_root")
                    if not v_path:
                        from core.runtime.cli_bootstrap import get_global_engine
                        engine = get_global_engine()
                        if engine: v_path = engine.config.vault_root
                    
                    if v_path and v_path.startswith(os.path.expanduser("~")):
                        v_path = v_path.replace(os.path.expanduser("~"), "~", 1)
                    
                    raw_vault = cfg.get("vault_root") or v_path
                    try:
                        vault_abs = os.path.abspath(os.path.expanduser(raw_vault)) if raw_vault and raw_vault != "Unknown Vault" else ""
                    except Exception:
                        vault_abs = ""

                    imprints.append({
                        "id": entry.name,
                        "name": p_name,
                        "vault": v_path,
                        "vault_abs": vault_abs,
                        "active": (entry.name == active_imprint)
                    })
        return imprints

    def get_most_recent_imprint(self) -> Optional[str]:
        """
        🛰️ [V52.12] 智能物理侦察：获取最新修改或使用的真实主权品牌。
        按配置文件的最后修改时间 (mtime) 倒序排列，优先选择 Vault 真实物理可达的合法品牌。
        """
        if not os.path.exists(self.imprint_root):
            return None

        candidates = []
        for entry in os.scandir(self.imprint_root):
            if entry.is_dir() and entry.name != "default" and not entry.name.startswith("test_"):
                config_path = os.path.join(entry.path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(config_path):
                    try:
                        mtime = os.path.getmtime(config_path)
                        # 🚀 [V75.8] 校验物理可达性：如果 Vault 路径不存在（如单测临时目录被物理清理），降低其权重
                        is_vault_valid = False
                        with open(config_path, 'r', encoding='utf-8') as f:
                            cfg = yaml.safe_load(f) or {}
                            v_root = cfg.get("vault_root")
                            if v_root and os.path.exists(os.path.abspath(os.path.expanduser(v_root))):
                                is_vault_valid = True
                        
                        candidates.append((is_vault_valid, mtime, entry.name))
                    except Exception:
                        pass

        if not candidates:
            return None

        # 优先按 Vault 真实物理可达性 (True > False)，其次按 mtime 倒序
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return candidates[0][2]
 
    def _probe_vault_structure(self, vault_path: str) -> List[Dict[str, str]]:
        """🚀 [V65.8] 金库主权自感知：根据物理目录结构智能生成路由矩阵"""
        matrix = []
        if not os.path.exists(vault_path):
            return [{"source": "", "prefix": ""}]
            
        try:
            # 1. 扫描一级子目录
            subdirs = [d for d in os.listdir(vault_path) if os.path.isdir(os.path.join(vault_path, d)) and not d.startswith('.')]
            
            # 2. 检查根目录下是否有合规稿件
            has_root_files = any(f.lower().endswith(('.md', '.mdx')) for f in os.listdir(vault_path) if os.path.isfile(os.path.join(vault_path, f)))
            
            # 3. 智能映射映射
            mapping_rules = {
                "Index": "",
                "Blog": "blog",
                "Docs": "docs",
                "Pages": "pages"
            }
            
            for folder, prefix in mapping_rules.items():
                if folder in subdirs:
                    matrix.append({"source": folder, "prefix": prefix})
            
            # 4. 如果有根目录文件，或者没探测到任何已知子目录，则开启根目录全局映射
            if has_root_files or not matrix:
                matrix.append({"source": "", "prefix": ""})
                
            return matrix
        except Exception as e:
            tlog.warning(f"⚠️ [感知失败] 无法探测金库结构: {e}")
            return [{"source": "", "prefix": ""}]

    def _inject_template_showcase_manuscripts(self, vault_path: str, press_name: str = "默认出版空间"):
        """
        🌱 [V75.6] 为每种装帧模板生成中英双语演示手稿与资产目录结构，构建 3D 知识星系拓扑
        涵盖模板类型：
        1. sovereign: 官方旗舰 (赛博毛玻璃、免编译直出、无刷新双语切换)
        2. universal: 通用自适应 (现代极简单栏阅读流、移动端/桌面端全端自适应)
        3. docusaurus: 知识库工程 (Meta 开源文档标准、丰富 Callouts/Admonitions 容器)
        4. starlight: Astro 极星 (0-JS 极速加载、现代卡片矩阵与 Web Vitals 极致优化)
        5. nextra: Next.js 极简 (React MDX 组件混编、手风琴折叠面板与即时检索)
        6. vitepress: VitePress 疾速轻量 (Vite & Vue 3 驱动、代码行高亮与超轻运行时)
        """
        import datetime
        today_str = datetime.date.today().isoformat()

        # 1. 建立物理标准目录树
        blog_dir = os.path.join(vault_path, "Blog")
        docs_dir = os.path.join(vault_path, "Docs")
        pages_dir = os.path.join(vault_path, "Pages")
        images_dir = os.path.join(vault_path, "assets", "images")
        
        for d in [blog_dir, docs_dir, pages_dir, images_dir]:
            os.makedirs(d, exist_ok=True)
            
        with open(os.path.join(images_dir, ".gitkeep"), "w", encoding="utf-8") as f:
            f.write("")

        # 2. 生成中心创世手稿: welcome-to-illacme.md (根目录与 Blog 频道)
        welcome_content = f"""---
title: 欢迎探索 {press_name} 数字出版宇宙
date: {today_str}
tags: [welcome, guide, showcase, universe]
summary: 欢迎来到全新划定的出版品牌！本手稿由向导自动生成，串联了 6 大装帧模板特性指南，并构成 3D 知识星系的引力中心。
---

# 欢迎探索 {press_name} 数字出版宇宙
# Welcome to the {press_name} Publishing Universe

欢迎进入全新的出版品牌工作空间！这里是你的数字出版创世原点。
Welcome to your newly established sovereign imprint workspace! This is the origin of your digital publishing journey.

---

## 🌟 3D 知识星系与装帧模板特性概览
## 3D Knowledge Galaxy & Theme Showcases

为了帮助你全面了解系统支持的 6 种现代装帧模板，文库已自动为你生成了中英双语的模板特性演示手稿。通过下方双向链接（WikiLinks），它们在 3D 知识星系中与本创世手稿形成了引力互联拓扑：

* 👑 **Sovereign 官方旗舰装帧**：原生轻奢赛博毛玻璃视觉、免构建极速直出、实时中英双语无刷新切换。
  👉 详见特性手稿：[[demo-sovereign|Sovereign 官方旗舰模板特性指南]]

* 🌐 **Universal 通用自适应装帧**：现代极简单栏阅读流、移动端/桌面端全端自适应、暗黑明亮色盘智能适配。
  👉 详见特性手稿：[[demo-universal|Universal 通用自适应模板特性指南]]

* 🦖 **Docusaurus 知识库工程装帧**：Meta Facebook 经典技术文档套件、增强 Callouts 容器语法、多版本侧边栏。
  👉 详见特性手稿：[[demo-docusaurus|Docusaurus 知识库工程模板特性指南]]

* 🌟 **Astro Starlight 极星装帧**：基于 Astro 的极致轻量、0-JS 极速首屏、现代卡片式与徽标排版。
  👉 详见特性手稿：[[demo-starlight|Astro Starlight 极星模板特性指南]]

* ⚡ **Nextra 现代极简装帧**：Next.js 与 React MDX 深度混编、交互式手风琴折叠、秒级全文检索。
  👉 详见特性手稿：[[demo-nextra|Nextra 现代文档模板特性指南]]

* 🚀 **VitePress 疾速轻量装帧**：Vite 与 Vue 3 驱动、单页应用平滑跳转、代码行高亮与差异对比。
  👉 详见特性手稿：[[demo-vitepress|VitePress 疾速轻量模板特性指南]]

---

## 🚀 开启你的出版旅程
## Starting Your Publishing Journey

1. **直接编辑或增删文稿**：在你的原稿文库目录中新建 Markdown 手稿，系统将自动感知并同步更新 3D 知识星系。
2. **在治理中心切换模板**：前往控制台的【版图装帧与模式】(Layout & Modes) 面板，可随时为当前出版版图无缝切换上述任意装帧模板。
3. **一键分发同步**：在工作台点击“一键全量分发”，即可自动完成多语种翻译、资产打包并发布上线。
"""

        root_welcome_path = os.path.join(vault_path, "welcome-to-illacme.md")
        with open(root_welcome_path, "w", encoding="utf-8") as f:
            f.write(welcome_content)

        blog_welcome_path = os.path.join(blog_dir, "welcome-to-illacme.md")
        with open(blog_welcome_path, "w", encoding="utf-8") as f:
            f.write(welcome_content)

        # 3. 模板 1: Docs/demo-sovereign.md (官方旗舰 Sovereign)
        sovereign_doc = f"""---
title: 官方旗舰装帧模板特性指南 (Sovereign Theme Showcase)
date: {today_str}
tags: [theme, sovereign, flagship, glassmorphism]
summary: 官方旗舰模板 (Sovereign) 特性演示：原生轻奢赛博毛玻璃、免编译直出架构与即时双语无刷新切换。
---

# 👑 官方旗舰装帧模板特性指南
# Sovereign Theme Showcase

Sovereign 是 Illacme Plenipes 的官方旗舰装帧主题，专为追求极致视觉品质与出版主权的创作者量身定制。
Sovereign is the official flagship theme of Illacme Plenipes, tailored for creators who seek ultimate visual sovereignty.

---

## ✨ 核心特性矩阵 (Core Features)

1. **免编译极速直出 (Zero-Build Instant Output)**:
   - 无需复杂的 Node.js 构建流水线，手稿与静态资源即改即看，出版毫秒级直达。
2. **赛博轻奢毛玻璃视觉 (Cyber Glassmorphism Aesthetics)**:
   - 深度采用高对比度暗色调、动态光晕与半透明磨砂质感，呈现专业高档的视觉工业品味。
3. **即时无刷新中英双语切换 (Instant Bilingual Locale Switcher)**:
   - 语言切换无需重新加载整页，段落级自动平滑对齐，双语阅读丝滑流畅。
4. **原生高维知识星系融合 (Native Galaxy Integration)**:
   - 与 3D 知识星系引擎底层原生互通，每一篇手稿都是宇宙中的一颗璀璨恒星。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-universal|通用自适应模板]] · [[demo-docusaurus|Docusaurus 工程模板]]
"""
        with open(os.path.join(docs_dir, "demo-sovereign.md"), "w", encoding="utf-8") as f:
            f.write(sovereign_doc)

        # 4. 模板 2: Docs/demo-universal.md (通用自适应 Universal)
        universal_doc = f"""---
title: 通用自适应装帧模板特性指南 (Universal Theme Showcase)
date: {today_str}
tags: [theme, universal, responsive, minimal]
summary: 通用自适应模板 (Universal) 特性演示：现代极简单栏阅读流、全端自适应响应与暗黑模式深度支持。
---

# 🌐 通用自适应装帧模板特性指南
# Universal Theme Showcase

Universal 是一个极简、干净且优雅的通用现代装帧主题，专注于纯粹的文字阅读与全终端适配。
Universal is a clean and elegant universal theme focused on distraction-free reading and multi-device adaptability.

---

## ✨ 核心特性矩阵 (Core Features)

1. **全端自适应响应式布局 (Fully Responsive Across All Devices)**:
   - 完美适配手机、平板、超宽屏桌面端，提供无懈可击的排版栅格与阅读视距。
2. **沉浸式单栏阅读流 (Immersive Single-Column Reading Flow)**:
   - 剔除冗余干扰元素，让读者的注意力完全聚焦于创作者的思想与文字内容。
3. **明暗色盘智能适配 (Adaptive Light & Dark Modes)**:
   - 自动跟随操作系统或读者偏好无缝切换暗黑与浅色模式，有效保护视力。
4. **社交网络 OpenGraph 深度优化**:
   - 自动生成社交网络分享卡片、Twitter Card 与微信分享摘要。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-sovereign|官方旗舰模板]] · [[demo-starlight|Astro 极星模板]]
"""
        with open(os.path.join(docs_dir, "demo-universal.md"), "w", encoding="utf-8") as f:
            f.write(universal_doc)

        # 5. 模板 3: Docs/demo-docusaurus.md (知识库工程 Docusaurus)
        docusaurus_doc = f"""---
title: Docusaurus 知识库工程模板特性指南 (Docusaurus Theme Showcase)
date: {today_str}
tags: [theme, docusaurus, engineering, callouts]
summary: Docusaurus 知识库工程模板特性演示：基于 Meta 经典开源技术文档标准，展示丰富的 Callouts/Admonitions 容器。
---

# 🦖 Docusaurus 知识库工程模板特性指南
# Docusaurus Theme Showcase

Docusaurus 基于 Meta (Facebook) 备受赞誉的开源文档框架标准，专为大型工程文档、知识库与技术规范打造。
Docusaurus is built upon Meta's acclaimed open-source documentation framework standard, designed for engineering knowledge bases.

---

## ✨ 提示块与容器语法演示 (Admonitions Showcase)

Docusaurus 具备强大的 Admonitions 提示块解析能力，能让你的技术文档结构分明、重点突出：

:::note 💡 核心说明 (Note)
这是一个标准 Note 说明块，适用于常规补充说明与背景知识展开。
This is a standard note callout for background context.
:::

:::tip 🎯 实用技巧 (Tip)
这是一个 Tip 提示块，适合分享最佳实践、快捷键或高阶操作技巧。
This is a tip callout for sharing best practices and shortcuts.
:::

:::warning ⚠️ 注意事项 (Warning)
这是一个 Warning 警示块，用于提示需要格外注意的配置陷阱或边界条件。
This is a warning callout for critical configuration caveats.
:::

:::danger 🛑 危险操作 (Danger)
这是一个 Danger 警示块，用于警告不可逆的物理删除或重大破坏性行为。
This is a danger callout warning against irreversible actions.
:::

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-nextra|Nextra 现代文档模板]] · [[demo-vitepress|VitePress 模板]]
"""
        with open(os.path.join(docs_dir, "demo-docusaurus.md"), "w", encoding="utf-8") as f:
            f.write(docusaurus_doc)

        # 6. 模板 4: Docs/demo-starlight.md (Astro 极星 Starlight)
        starlight_doc = f"""---
title: Astro Starlight 极星模板特性指南 (Starlight Theme Showcase)
date: {today_str}
tags: [theme, starlight, astro, fast]
summary: Astro Starlight 模板特性演示：基于 Astro 驱动的高性能文档引擎、0-JS 极速首屏与现代化卡片组件。
---

# 🌟 Astro Starlight 极星模板特性指南
# Astro Starlight Theme Showcase

Starlight 是由 Astro 官方打造的极致性能文档框架，以惊人的加载速度、精美现代的排版和卓越的无障碍体验著称。
Starlight is Astro's official documentation framework, celebrated for blazingly fast load times and modern aesthetic typography.

---

## ✨ 核心特性矩阵 (Core Features)

1. **极致轻量 0-JS 首屏 (Zero-JS by Default)**:
   - 极致削减客户端 JavaScript 载荷，核心文档内容毫秒级秒开，打造顶级 Web Vitals 评分。
2. **现代卡片式排版与徽标 (Card Grid & Badges)**:
   - 原生支持卡片阵列排版，适合构建模块导航、特性矩阵与产品指南。
3. **开箱即用的多语种架构 (Built-in i18n Architecture)**:
   - 与 Illacme Plenipes 的多语种主权分发管道深度契合，原生支持全站语种自动对齐。
4. **精细化的暗色调支持 (Curated Dark Mode)**:
   - 经由视觉设计师精心校准的对比度与配色，长时间阅读不刺眼、不疲劳。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-sovereign|官方旗舰模板]] · [[demo-universal|通用自适应模板]]
"""
        with open(os.path.join(docs_dir, "demo-starlight.md"), "w", encoding="utf-8") as f:
            f.write(starlight_doc)

        # 7. 模板 5: Docs/demo-nextra.md (Next.js 极简 Nextra)
        nextra_doc = f"""---
title: Nextra 现代文档模板特性指南 (Nextra Theme Showcase)
date: {today_str}
tags: [theme, nextra, nextjs, react]
summary: Nextra 现代文档模板特性演示：基于 Next.js & React MDX，灵活组件混编与毫秒级折叠侧边栏。
---

# ⚡ Nextra 现代文档模板特性指南
# Nextra Theme Showcase

Nextra 是基于 Next.js 与 React MDX 驱动的现代知识库引擎，兼具极简外观与极高扩展性。
Nextra is a modern knowledge base engine powered by Next.js and MDX, combining minimalist aesthetics with infinite flexibility.

---

## ✨ 核心特性矩阵 (Core Features)

1. **React MDX 组件无缝混编 (MDX Component Power)**:
   - 可以在 Markdown 手稿中灵活嵌入丰富的交互式 UI 组件、演示 Demo 与图表。
2. **交互式可折叠详情 (Interactive Collapsible Details)**:
   - 原生支持 HTML5 `<details>` 与 `<summary>` 手风琴折叠面板，整洁收纳复杂内容。
3. **秒级全文检索与键盘导航 (Instant Full-Text Search)**:
   - 原生集成 FlexSearch 极速离线分词引擎，按下 `Cmd + K` 即可瞬间定位内容。
4. **自适应嵌套目录树 (Recursive Nested Sidebar)**:
   - 自动解析文件目录结构，生成可自由折叠与展开的多级导航侧边栏。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-docusaurus|Docusaurus 模板]] · [[demo-vitepress|VitePress 模板]]
"""
        with open(os.path.join(docs_dir, "demo-nextra.md"), "w", encoding="utf-8") as f:
            f.write(nextra_doc)

        # 8. 模板 6: Docs/demo-vitepress.md (Vue 3 疾速轻量 VitePress)
        vitepress_doc = f"""---
title: VitePress 疾速轻量模板特性指南 (VitePress Theme Showcase)
date: {today_str}
tags: [theme, vitepress, vue, vite]
summary: VitePress 疾速轻量模板特性演示：基于 Vite & Vue 3 驱动的现代静态文档框架，展示代码高亮与行聚焦。
---

# 🚀 VitePress 疾速轻量模板特性指南
# VitePress Theme Showcase

VitePress 是由 Vue 作者尤雨溪打造的下一代静态站点生成器，基于 Vite 的极速构建体验与 Vue 3 的轻量运行时。
VitePress is the next-generation static site generator by Vue creator Evan You, powered by Vite and Vue 3.

---

## ✨ 代码高亮与行聚焦演示 (Code Highlighting & Focus)

VitePress 提供业界一流的代码块渲染能力，支持语言标识、代码行高亮与差异对比：

```javascript
// VitePress 核心启动配置演示
import {{ defineConfig }} from 'vitepress';

export default defineConfig({{
  title: "Illacme Plenipes",
  description: "主权数字出版平台", // [!code focus] 高亮重点行
  themeConfig: {{
    nav: [{{ text: "指南", link: "/docs/demo-vitepress" }}]
  }}
}});
```

---

## ✨ 核心特性矩阵 (Core Features)

1. **Vite 极速热更新与编译 (Blazing Fast HMR)**:
   - 无论是单篇修改还是整站发布，均能享受秒级冷启动与毫秒级热更新。
2. **轻量 SPA 架构 (Lightweight SPA Navigation)**:
   - 首屏加载完成后，后续页面跳转均为纯前端无感知切换，零网络往返延迟。
3. **原生 Markdown 扩展 (Markdown Extensions)**:
   - 深度支持自定义容器、代码行高亮与 GFM 任务列表。

---

## 🔗 引力回链 (Backlinks)
* 🪐 返回中心星：[[welcome-to-illacme|返回数字出版创世手稿]]
* 📚 探索其他模板：[[demo-starlight|Astro 极星模板]] · [[demo-nextra|Nextra 现代模板]]
"""
        with open(os.path.join(docs_dir, "demo-vitepress.md"), "w", encoding="utf-8") as f:
            f.write(vitepress_doc)

        # 9. 附赠关于手稿: Pages/about.md
        about_doc = f"""---
title: 关于本出版版图 (About This Imprint)
date: {today_str}
tags: [about, imprint]
summary: 本出版版图的独立主权说明与创作者介绍。
---

# 📖 关于本出版版图
# About This Imprint

本出版版图由 Illacme Plenipes 主权出版系统驱动，享有独立的版图标识、多语种翻译治理策略与专属 3D 知识星系。
This imprint is powered by the Illacme Plenipes sovereign publishing system, with independent branding and a dedicated knowledge galaxy.

* 探索装帧模板特性指南：[[welcome-to-illacme|返回数字出版宇宙中心]]
"""
        with open(os.path.join(pages_dir, "about.md"), "w", encoding="utf-8") as f:
            f.write(about_doc)

    def switch(self, imprint_id: str):
        """激活当前活跃主权 Imprint"""
        config_path = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if not os.path.exists(config_path):
            tlog.error(f"🛑 [激活失败] 未找到主权 Imprint: {imprint_id}")
            return
        
        self.active_imprint = imprint_id
        tlog.info(f"🔄 [主权激活] (切换出版社) 出版品牌已切换至: {imprint_id}")

 
    def get_active_imprint(self) -> str:
        return self.active_imprint

    def delete_imprint(self, name: str) -> bool:
        """🚀 [V50.3] 撤销主权 Imprint：物理删除一个出版品牌的所有资产"""
        # 🛡️ [安全底线拦截] 严禁物理撤销系统默认版图以及当前正处于活动执行中的活跃版图，防止雪崩卡死
        if name == "default":
            tlog.error("🛑 [安全拦截] 严禁物理撤销系统默认主权版图 'default'！")
            return False
            
        if name == self.active_imprint:
            tlog.error(f"🛑 [安全拦截] 严禁物理撤销当前正处于激活状态的版图 '{name}'！请先切换至其他版图后再行操作。")
            return False

        imprint_path = os.path.join(self.imprint_root, name)
        if not os.path.exists(imprint_path):
            tlog.error(f"🛑 [撤销失败] 未找到出版品牌: {name}")
            return False
        
        try:
            tlog.warning(f"⚠️ [物理撤销] 正在抹除出版品牌 '{name}' 的所有物理存在...")
            shutil.rmtree(imprint_path)
            tlog.success(f"✅ [撤销完成] 出版品牌 '{name}' 及其所有配置、缓存、元数据已物理清除。")
            return True
        except Exception as e:
            tlog.error(f"🛑 [物理撤销异常] {e}")
            return False
 
# 🚀 全局主权中枢
im = ImprintManager()
