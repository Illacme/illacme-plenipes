# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Desktop Application Packager Core
模块职责：跨平台单体独立应用打包流水线核心（基于 PyInstaller 与原生 Webview）。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os, sys, shutil, platform, subprocess
from typing import List, Optional

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try: stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception: pass

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path: sys.path.insert(0, _ROOT)

from core.utils.tracing import tlog
try:
    from .packager_manifest import get_hidden_imports, get_data_mappings
except ImportError:
    from desktop.packager_manifest import get_hidden_imports, get_data_mappings


class DesktopPackager:
    """📦 跨平台桌面客户端打包工坊核心"""

    APP_NAME = "Illacme-Plenipes"
    MAIN_ENTRY = os.path.join("desktop", "app.py")

    @classmethod
    def stage_assets(cls) -> str:
        """物理清洗并暂存主题模板与静态资源 (剔除 node_modules, 构建产物与临时文件)"""
        stage_dir = os.path.join("build", "desktop", "staged_themes")
        if os.path.exists(stage_dir):
            shutil.rmtree(stage_dir, ignore_errors=True)
        os.makedirs(os.path.dirname(stage_dir), exist_ok=True)
        shutil.copytree(
            "themes", stage_dir,
            ignore=shutil.ignore_patterns("node_modules", ".next", ".astro", ".docusaurus", "dist", "build", ".temp", ".git", "__pycache__", ".DS_Store")
        )
        tlog.info(f"🧬 [资产暂存] 主题母本已物理纯净剥离并暂存至: {stage_dir}")
        return stage_dir

    @classmethod
    def assemble_build_args(
        cls,
        output_dir: str = "dist/desktop",
        icon_path: Optional[str] = None,
        target_arch: Optional[str] = None
    ) -> List[str]:
        """组装全量 PyInstaller 编译参数 (支持 macOS target_arch: universal2 / arm64 / x86_64)"""
        sep = ";" if platform.system() == "Windows" else ":"
        staged_themes = os.path.join("build", "desktop", "staged_themes")
        themes_src = staged_themes if os.path.exists(staged_themes) else "themes"
        data_mappings = get_data_mappings(themes_src)

        args = [
            sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed",
            f"--name={cls.APP_NAME}", f"--distpath={output_dir}", "--workpath=build/desktop",
        ]

        if platform.system() == "Darwin" and target_arch:
            arch_norm = target_arch.strip().lower()
            if arch_norm in ("universal2", "arm64", "x86_64"):
                args.append(f"--target-arch={arch_norm}")
            else:
                tlog.warning(f"⚠️ [打包工坊] 未知 macOS 架构 '{target_arch}'，将使用系统默认架构")

        for src, dst in data_mappings:
            if os.path.exists(src):
                args.append(f"--add-data={src}{sep}{dst}")

        hidden_imports = get_hidden_imports(platform.system())
        for h in hidden_imports:
            args.append(f"--hidden-import={h}")

        if icon_path and os.path.exists(icon_path):
            args.append(f"--icon={icon_path}")

        args.append(cls.MAIN_ENTRY)
        return args

    @classmethod
    def generate_icon(cls, base_logo_path: str = "web/dashboard/logo.png") -> Optional[str]:
        """从预置专属资产或网站 Logo 生成系统原生图标"""
        system = platform.system()
        asset_icns, asset_ico = os.path.join("desktop", "assets", "icon.icns"), os.path.join("desktop", "assets", "icon.ico")
        asset_png = os.path.join("desktop", "assets", "icon.png")
        if system == "Darwin" and os.path.exists(asset_icns): return asset_icns
        if system == "Windows" and os.path.exists(asset_ico): return asset_ico
        if system == "Linux" and os.path.exists(asset_png): return asset_png
        if not os.path.exists(base_logo_path): return None
        out_dir = os.path.join("build", "desktop", "icons")
        os.makedirs(out_dir, exist_ok=True)
        try:
            from PIL import Image
            img = Image.open(base_logo_path)
            if system == "Darwin":
                iconset_dir = os.path.join(out_dir, "AppIcon.iconset")
                os.makedirs(iconset_dir, exist_ok=True)
                for s in [16, 32, 128, 256, 512]:
                    img.resize((s, s), Image.Resampling.LANCZOS).save(os.path.join(iconset_dir, f"icon_{s}x{s}.png"))
                    img.resize((s * 2, s * 2), Image.Resampling.LANCZOS).save(os.path.join(iconset_dir, f"icon_{s}x{s}@2x.png"))
                icns_path = os.path.join(out_dir, "AppIcon.icns")
                if shutil.which("iconutil"):
                    subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
                    return icns_path
            elif system == "Windows":
                ico_path = os.path.join(out_dir, "AppIcon.ico")
                img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
                return ico_path
        except Exception as e:
            tlog.warning(f"⚠️ [图标生成] 跳过定制图标: {e}")
        return None

    @classmethod
    def execute_build(
        cls,
        dry_run: bool = False,
        output_dir: str = "dist/desktop",
        target_arch: Optional[str] = None,
        create_dmg: bool = False
    ) -> bool:
        """执行完整打包流程 (支持 macOS 双架构与 Universal 2 编译及 DMG 生成)"""
        import logging
        if tlog.getEffectiveLevel() > logging.INFO: tlog.setLevel(logging.INFO)
        tlog.info("🔨 [打包工坊] 启动 Illacme Plenipes 独立桌面客户端构建...")
        if target_arch and platform.system() == "Darwin":
            tlog.info(f"🎯 [目标架构] macOS 编译目标架构已锁定: [{target_arch}]")

        if not dry_run:
            try:
                import PyInstaller  # noqa: F401
            except ImportError:
                tlog.error("❌ 未检测到 PyInstaller，请先安装: pip install pyinstaller pillow")
                return False
            cls.stage_assets()

        icon_path = cls.generate_icon()
        if icon_path: tlog.info(f"🎨 [打包工坊] 已就绪应用图标: {icon_path}")

        cmd = cls.assemble_build_args(output_dir=output_dir, icon_path=icon_path, target_arch=target_arch)
        tlog.info(f"⚙️ [打包命令] {' '.join(cmd[:6])} ... ({len(cmd)} 个参数)")

        if dry_run:
            tlog.info("🧪 [Dry-Run] 校验完成，构建配置合法严谨。")
            return True

        os.makedirs(output_dir, exist_ok=True)
        try:
            res = subprocess.run(cmd, check=True)
            if res.returncode == 0:
                cls.write_quickstart_guide(output_dir)
                if platform.system() == "Darwin":
                    cls.write_macos_fix_script(output_dir)
                    if create_dmg: cls.build_macos_dmg(output_dir)
                elif platform.system() == "Linux":
                    cls.write_linux_desktop_entry(output_dir)
                tlog.info(f"🎉 [打包成功] 桌面应用已编译输出至: {os.path.abspath(output_dir)}")
                return True
        except subprocess.CalledProcessError as e:
            tlog.error(f"❌ [打包失败] PyInstaller 编译异常中断: {e}")
        return False

    @classmethod
    def build_macos_dmg(cls, output_dir: str, dmg_path: Optional[str] = None) -> Optional[str]:
        """使用 macOS 原生 hdiutil 将打包产物制作为便携式 .dmg 磁盘镜像"""
        if platform.system() != "Darwin" or not shutil.which("hdiutil"):
            return None
        app_path = os.path.join(output_dir, f"{cls.APP_NAME}.app")
        if not os.path.exists(app_path):
            tlog.warning(f"⚠️ [DMG 工坊] 未在 {output_dir} 找到 {cls.APP_NAME}.app，跳过 DMG 制作。")
            return None
        if not dmg_path:
            from core import __version__
            dmg_path = os.path.join(output_dir, f"{cls.APP_NAME}-v{__version__}.dmg")
        tlog.info(f"💿 [DMG 工坊] 正在生成 macOS 安装镜像: {dmg_path} ...")
        try:
            # 注入 DMG 品牌卷标图标
            asset_icns = os.path.join("desktop", "assets", "icon.icns")
            if os.path.exists(asset_icns):
                try: shutil.copy(asset_icns, os.path.join(output_dir, ".VolumeIcon.icns"))
                except Exception: pass

            app_link = os.path.join(output_dir, "Applications")
            if not os.path.exists(app_link):
                try: os.symlink("/Applications", app_link)
                except Exception: pass
            cmd = ["hdiutil", "create", "-volname", "Illacme Plenipes", "-srcfolder", output_dir, "-ov", "-format", "UDZO", dmg_path]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if os.path.islink(app_link):
                try: os.unlink(app_link)
                except Exception: pass
            tlog.info(f"✨ [DMG 工坊] 安装镜像制作成功: {dmg_path}")
            return dmg_path
        except Exception as e:
            tlog.warning(f"⚠️ [DMG 工坊] DMG 镜像生成容错跳过: {e}")
            return None

    @classmethod
    def write_macos_fix_script(cls, output_dir: str):
        """生成 macOS 一键解除隔离 Gatekeeper 修复脚本 (双击即可运行)"""
        script_content = (
            "#!/bin/bash\n# Illacme Plenipes · macOS 一键解除应用安全隔离 (消除首次打开损坏提示)\n"
            "TARGET_APP=\"/Applications/Illacme-Plenipes.app\"\nDIR=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" >/dev/null 2>&1 && pwd )\"\n"
            "LOCAL_APP=\"$DIR/Illacme-Plenipes.app\"\nclear\n"
            "echo \"============================================================\"\n"
            "echo \"  Illacme Plenipes · macOS 应用信任与隔离修复工具\"\n"
            "echo \"============================================================\"\n"
            "if [ -d \"$TARGET_APP\" ]; then\n"
            "    echo \"正在为应用程序目录中的 Illacme Plenipes 解除隔离...\"\n"
            "    xattr -cr \"$TARGET_APP\" 2>/dev/null || sudo xattr -cr \"$TARGET_APP\"\n"
            "    echo \"✅ 修复完成！您现在可以直接打开 Illacme Plenipes 了。\"\n"
            "elif [ -d \"$LOCAL_APP\" ]; then\n"
            "    echo \"正在为镜像内的 Illacme Plenipes 解除隔离...\"\n"
            "    xattr -cr \"$LOCAL_APP\" 2>/dev/null\n"
            "    echo \"✅ 修复完成！请将应用拖入右侧 Applications 目录即可。\"\n"
            "else\n    echo \"⚠️ 未在 /Applications 找到应用，请先将应用拖入 Applications 文件夹。\"\nfi\n"
            "echo \"\"\nread -n 1 -s -r -p \"按任意键退出窗口...\"\nexit 0\n"
        )
        try:
            cmd_path = os.path.join(output_dir, "双击修复无法打开.command")
            with open(cmd_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            os.chmod(cmd_path, 0o755)
        except Exception as e:
            tlog.warning(f"⚠️ [打包工坊] 生成修复脚本跳过: {e}")

    @classmethod
    def write_quickstart_guide(cls, output_dir: str):
        """生成客户端快速启动与各操作系统指引文档"""
        guide_content = (
            "============================================================\n"
            "Illacme Plenipes · 全球私人出版社桌面客户端\n"
            "============================================================\n\n"
            "【快速启动指引】\n"
            "1. Windows: 双击直接运行 Illacme-Plenipes.exe，无需安装任何 Python 运行环境。\n"
            "2. macOS: 将 Illacme-Plenipes.app 拖入 Applications；如提示未知开发者可双击运行「双击修复无法打开.command」。\n"
            "3. Linux: 赋予执行权限并启动: chmod +x Illacme-Plenipes && ./Illacme-Plenipes (或双击 Illacme-Plenipes.desktop)。\n\n"
            "【系统网络与端口规范】\n"
            "- 出版社核心网关: http://127.0.0.1:43212 | 单例守护端口: 43210\n"
            "- 若已有实例运行，新打开客户端将自动无缝激活浏览器控制台。\n\n祝您出版愉快！\n"
        )
        try:
            with open(os.path.join(output_dir, "README_使用说明.txt"), "w", encoding="utf-8") as f:
                f.write(guide_content)
        except Exception: pass

    @classmethod
    def write_linux_desktop_entry(cls, output_dir: str):
        """生成 Linux 标准 XDG 桌面项与图标"""
        entry = (
            f"[Desktop Entry]\nType=Application\nName=Illacme Plenipes\nComment=全球私人出版社桌面客户端\n"
            f"Exec=./{cls.APP_NAME}\nIcon=icon\nTerminal=false\nCategories=Office;Publishing;\n"
        )
        try:
            with open(os.path.join(output_dir, f"{cls.APP_NAME}.desktop"), "w", encoding="utf-8") as f:
                f.write(entry)
            icon_src = os.path.join("desktop", "assets", "icon.png")
            if os.path.exists(icon_src): shutil.copy(icon_src, os.path.join(output_dir, "icon.png"))
        except Exception: pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Illacme Plenipes 桌面独立客户端构建流水线")
    parser.add_argument("--dry-run", action="store_true", help="仅校验配置，不执行编译")
    parser.add_argument("--output-dir", default="dist/desktop", help="产物输出目录")
    parser.add_argument("--dmg", action="store_true", help="构建完成后制作 macOS .dmg 镜像")
    parser.add_argument("--target-arch", choices=["universal2", "arm64", "x86_64"], default=None, help="目标架构")
    args = parser.parse_args()

    success = DesktopPackager.execute_build(dry_run=args.dry_run, output_dir=args.output_dir, target_arch=args.target_arch, create_dmg=args.dmg)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
