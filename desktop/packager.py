# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Desktop Application Packager Core
模块职责：跨平台单体独立应用打包流水线核心（基于 PyInstaller 与原生 Webview）。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os
import sys
import shutil
import platform
import subprocess
from typing import List, Optional

from core.utils.tracing import tlog


class DesktopPackager:
    """📦 跨平台桌面客户端打包工坊核心"""

    APP_NAME = "Illacme-Plenipes"
    MAIN_ENTRY = os.path.join("desktop", "app.py")

    @classmethod
    def assemble_build_args(cls, output_dir: str = "dist/desktop", icon_path: Optional[str] = None) -> List[str]:
        """组装全量 PyInstaller 编译参数"""
        sep = ";" if platform.system() == "Windows" else ":"
        data_mappings = [
            ("web/dashboard", "web/dashboard"),
            ("themes", "themes"),
            ("configs", "configs"),
        ]

        args = [
            "pyinstaller",
            "--noconfirm",
            "--clean",
            "--windowed",
            f"--name={cls.APP_NAME}",
            f"--distpath={output_dir}",
            f"--workpath=build/desktop",
        ]

        # 1. 注入静态资源数据
        for src, dst in data_mappings:
            if os.path.exists(src):
                args.append(f"--add-data={src}{sep}{dst}")

        # 2. 注入隐式动态导入依赖
        hidden_imports = [
            "uvicorn.logging",
            "uvicorn.loops",
            "uvicorn.loops.auto",
            "uvicorn.protocols",
            "uvicorn.protocols.http",
            "uvicorn.protocols.http.auto",
            "uvicorn.protocols.websockets",
            "uvicorn.protocols.websockets.auto",
            "uvicorn.lifespans",
            "uvicorn.lifespans.on",
            "fastapi",
            "cryptography",
            "yaml",
            "markdown",
            "latex2mathml",
            "reportlab",
            "engineio.async_drivers.asgi",
        ]
        for h in hidden_imports:
            args.append(f"--hidden-import={h}")

        # 3. 平台专属图标
        if icon_path and os.path.exists(icon_path):
            args.append(f"--icon={icon_path}")

        # 4. 入口文件
        args.append(cls.MAIN_ENTRY)
        return args

    @classmethod
    def generate_icon(cls, base_logo_path: str = "web/dashboard/logo.png") -> Optional[str]:
        """从网站 Logo 生成系统原生图标"""
        if not os.path.exists(base_logo_path):
            return None
        out_dir = os.path.join("build", "desktop", "icons")
        os.makedirs(out_dir, exist_ok=True)

        system = platform.system()
        try:
            from PIL import Image
            img = Image.open(base_logo_path)

            if system == "Darwin":
                iconset_dir = os.path.join(out_dir, "AppIcon.iconset")
                os.makedirs(iconset_dir, exist_ok=True)
                sizes = [16, 32, 64, 128, 256, 512]
                for s in sizes:
                    resized = img.resize((s, s), Image.Resampling.LANCZOS)
                    resized.save(os.path.join(iconset_dir, f"icon_{s}x{s}.png"))
                    if s <= 256:
                        resized_2x = img.resize((s * 2, s * 2), Image.Resampling.LANCZOS)
                        resized_2x.save(os.path.join(iconset_dir, f"icon_{s}x{s}@2x.png"))
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
    def execute_build(cls, dry_run: bool = False, output_dir: str = "dist/desktop") -> bool:
        """执行完整打包流程"""
        tlog.info("🔨 [打包工坊] 启动 Illacme Plenipes 独立桌面客户端构建...")
        
        pyinstaller_bin = shutil.which("pyinstaller")
        if not pyinstaller_bin and not dry_run:
            tlog.error("❌ 未检测到 pyinstaller，请先安装: pip install pyinstaller pywebview pillow")
            return False

        icon_path = cls.generate_icon()
        if icon_path:
            tlog.info(f"🎨 [打包工坊] 已就绪应用图标: {icon_path}")

        cmd = cls.assemble_build_args(output_dir=output_dir, icon_path=icon_path)
        tlog.info(f"⚙️ [打包命令] {' '.join(cmd[:6])} ... ({len(cmd)} 个参数)")

        if dry_run:
            tlog.info("🧪 [Dry-Run] 校验完成，构建配置合法严谨。")
            return True

        try:
            res = subprocess.run(cmd, check=True)
            if res.returncode == 0:
                tlog.info(f"🎉 [打包成功] 桌面应用已编译输出至: {os.path.abspath(output_dir)}")
                return True
        except subprocess.CalledProcessError as e:
            tlog.error(f"❌ [打包失败] PyInstaller 编译异常中断: {e}")
        return False
