# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Desktop System Tray Hub
模块职责：跨平台系统托盘（System Tray / 菜单栏图标）服务与状态快捷感知。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
🛡️ [SOP-04 容错]：在缺失 pystray 依赖或无 GUI 显示时具备 100% 防御性优雅降级。
"""

import os
import sys
import threading
import webbrowser
from typing import Callable, Optional
import urllib.request
import json

from core.utils.tracing import tlog
from core.utils.frozen_paths import FrozenPathResolver

# 防御性检测 pystray 与 PIL 依赖
try:
    import pystray
    from PIL import Image, ImageDraw
    _PYSTRAY_AVAILABLE = True
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None
    _PYSTRAY_AVAILABLE = False


class SystemTrayManager:
    """🛰️ 跨平台桌面系统托盘中枢管理器"""

    def __init__(self, api_url: str = "http://127.0.0.1:43212"):
        self.api_url = api_url.rstrip("/")
        self._icon: Optional[object] = None
        self._thread: Optional[threading.Thread] = None
        self._on_open: Optional[Callable[[], None]] = None
        self._on_quit: Optional[Callable[[], None]] = None

    @classmethod
    def is_supported(cls) -> bool:
        """检查当前运行环境是否支持系统托盘"""
        if not _PYSTRAY_AVAILABLE:
            return False
        # 无图形界面的 Linux (CI 或纯服务器终端) 优雅跳过
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            return False
        return True

    def _generate_icon_image(self) -> Optional[object]:
        """生成或加载托盘图标 (64x64 RGBA)"""
        if not _PYSTRAY_AVAILABLE:
            return None

        # 1. 尝试从打包或本地路径读取网站 Logo
        candidates = [
            FrozenPathResolver.resolve("web/dashboard/logo.png"),
            os.path.join(os.path.dirname(__file__), "..", "web", "dashboard", "logo.png"),
            "web/dashboard/logo.png",
        ]
        for path in candidates:
            if path and os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    return img.resize((64, 64), Image.Resampling.LANCZOS)
                except Exception as e:
                    tlog.debug(f"⚠️ [系统托盘] 读取 Logo 异常: {e}")

        # 2. 内存合成暗色科技风 IP 专属托盘徽标
        try:
            size = 64
            img = Image.new("RGBA", (size, size), (11, 18, 25, 255))
            draw = ImageDraw.Draw(img)
            # 绘制青色环形边界与文字
            draw.ellipse([4, 4, size - 4, size - 4], outline=(0, 242, 255, 220), width=3)
            draw.rectangle([18, 20, 22, 44], fill=(0, 242, 255, 240))
            draw.rectangle([28, 20, 32, 44], fill=(255, 255, 255, 240))
            draw.rectangle([32, 20, 44, 32], fill=(255, 255, 255, 240))
            return img
        except Exception as e:
            tlog.warning(f"⚠️ [系统托盘] 内存合成托盘微标失败: {e}")
            return None

    def _async_api_call(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> Optional[dict]:
        """安全异步执行后台 API 调用"""
        try:
            url = f"{self.api_url}{endpoint}"
            req = urllib.request.Request(url, method=method)
            req.add_header("User-Agent", "IllacmePlenipes-DesktopTray/1.0")
            body = None
            if data is not None:
                body = json.dumps(data).encode("utf-8")
                req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, data=body, timeout=5.0) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            tlog.debug(f"⚠️ [系统托盘] API 调用 [{method} {endpoint}] 异常: {e}")
        return None

    def _action_open(self, icon=None, item=None):
        """打开/聚焦控制台"""
        if self._on_open:
            try:
                self._on_open()
                return
            except Exception as e:
                tlog.warning(f"⚠️ [系统托盘] 唤起主窗口异常: {e}")
        webbrowser.open(self.api_url)

    def _action_publish(self, icon=None, item=None):
        """触发全域一键发布"""
        def _worker():
            tlog.info("🚀 [系统托盘] 创作者通过托盘触发全域一键发布...")
            res = self._async_api_call("/api/publish/trigger", method="POST")
            if icon and hasattr(icon, "notify"):
                if res and res.get("status") == "ok":
                    icon.notify("已成功启动全域发布管线", "🚀 Illacme Plenipes 发布中心")
                else:
                    icon.notify("触发发布指令失败，请在控制台查看详情", "⚠️ 发布提示")
        threading.Thread(target=_worker, daemon=True).start()

    def _action_check_update(self, icon=None, item=None):
        """检查云端新版本"""
        def _worker():
            tlog.info("🛰️ [系统托盘] 正在同步检查云端最新发版...")
            res = self._async_api_call("/api/system/check_update?force=true", method="GET")
            if icon and hasattr(icon, "notify"):
                if res and res.get("has_update"):
                    latest = res.get("latest_version", "新版本")
                    icon.notify(f"发现云端全新版本 {latest}！点击工作台查看更新详情", "✨ 新版发布提示")
                elif res:
                    cur = res.get("current_version", "")
                    icon.notify(f"当前已是最新稳定版本 ({cur})", "🟢 检查更新")
                else:
                    icon.notify("检查更新超时，可能处于离线环境", "⚠️ 检查更新")
        threading.Thread(target=_worker, daemon=True).start()

    def _action_restart(self, icon=None, item=None):
        """重启出版内核"""
        def _worker():
            tlog.info("⚡ [系统托盘] 创作者通过托盘触发内核平滑重载...")
            self._async_api_call("/api/system/restart", method="POST")
            if icon and hasattr(icon, "notify"):
                icon.notify("内核正在进行平滑热重启...", "⚡ 核心网关")
        threading.Thread(target=_worker, daemon=True).start()

    def _action_quit(self, icon=None, item=None):
        """退出桌面端"""
        tlog.info("🛑 [系统托盘] 收到退出指令，正在优雅终止桌面服务...")
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
        if self._on_quit:
            try:
                self._on_quit()
            except Exception as e:
                tlog.warning(f"⚠️ [系统托盘] 退出回调异常: {e}")
        sys.exit(0)

    def build_menu(self):
        """构建托盘上下文菜单"""
        if not _PYSTRAY_AVAILABLE:
            return None
        return pystray.Menu(
            pystray.MenuItem("🌐 打开出版工作台", self._action_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚀 全域一键发布", self._action_publish),
            pystray.MenuItem("🛰️ 检查云端新版", self._action_check_update),
            pystray.MenuItem("⚡ 重启出版内核", self._action_restart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🛑 退出 Illacme Plenipes", self._action_quit)
        )

    def start_in_thread(
        self,
        on_open: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None
    ) -> bool:
        """在独立后台线程中挂载常驻系统托盘"""
        if not self.is_supported():
            tlog.info("ℹ️ [系统托盘] 当前运行环境无需或未启用系统托盘，优雅跳过。")
            return False

        self._on_open = on_open
        self._on_quit = on_quit

        icon_image = self._generate_icon_image()
        if not icon_image:
            return False

        try:
            self._icon = pystray.Icon(
                name="IllacmePlenipes",
                icon=icon_image,
                title="Illacme Plenipes · 全球私人出版社",
                menu=self.build_menu()
            )

            def _run():
                try:
                    self._icon.run()
                except Exception as e:
                    tlog.warning(f"⚠️ [系统托盘] 托盘事件循环异常退出: {e}")

            self._thread = threading.Thread(target=_run, daemon=True, name="SystemTrayThread")
            self._thread.start()
            tlog.info("✨ [系统托盘] 原生状态栏托盘已就绪并常驻后台。")
            return True
        except Exception as e:
            tlog.warning(f"⚠️ [系统托盘] 启动托盘失败，降级为常规模式: {e}")
            return False

    def stop(self) -> None:
        """终止托盘运行"""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
