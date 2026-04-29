# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Sovereign Onboarding Wizard
职责：引导用户完成第一个出版社空间的物理创建与算力绑定。
🛡️ [V35.0]：基于“主权出版社”共识的交互式引导。
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from core.governance.territory_manager import wm

from core.utils.tracing import tlog

console = Console()

def run_onboarding_wizard() -> bool:
    """🚀 [V35.0] 极速主权引导：开启您的第一个私人出版社"""
    console.clear()
    
    # 🎨 品牌视觉：主权发布官标识
    ascii_art = r"""
  ___  _               _                 ___  _                 _
 | _ \| | ___ _ _  _ _ (_) _ __  ___  ___ | _ \| | ___ _ _  _ _ (_) _ __  ___  ___
 |  _/| |/ -_) ' \| ' \| || '_ \/ -_)(_-< |  _/| |/ -_) ' \| ' \| || '_ \/ -_)(_-<
 |_|  |_|\___|_||_|_||_|_|| .__/\___|/__/ |_|  |_|\___|_||_|_||_|_|| .__/\___|/__/
                          |_|                                     |_|
    """
    banner_content = Text.assemble(
        (ascii_art, "bold cyan"),
        ("\n" + "═" * 72 + "\n", "dim cyan"),
        ("🚀 欢迎，总编辑阁下。系统检测到尚未建立主权疆域。\n", "white"),
        ("💡 提示：每一个主权疆域都是一个独立的物理隔离单元，拥有私有配置与影子缓存。\n", "dim")
    )

    
    console.print(Panel(
        Align.center(banner_content),
        border_style="bold cyan",
        padding=(1, 2),
        title="[bold white]THE FOUNDRY VOYAGE[/bold white]",
        subtitle="[bold cyan]Sovereign Press Onboarding[/bold cyan]"
    ))
    console.print("\n")

    # 1. 选择引导方式
    wizard_mode = Prompt.ask(
        "🔮 请选择安装引导方式",
        choices=["terminal", "web"],
        default="terminal"
    )
    
    if wizard_mode == "web":
        import webbrowser
        from core.ui.web.wizard_server import start_wizard_server
        
        url = "http://127.0.0.1:43210"
        console.print(Panel(
            f"📡 [bold yellow]Web 引导服务已启动[/]\n请在浏览器访问: [bold cyan]{url}[/]\n[dim]正在尝试自动为您打开浏览器...[/]",
            border_style="yellow"
        ))
        
        # 异步拉起浏览器，防止阻塞服务器启动
        import threading
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        
        # 启动阻塞式服务器
        start_wizard_server(port=43210)
        return True # 假设服务器结束意味着初始化完成


    # 2. 收集出版社元数据
    press_name = Prompt.ask("🏷️ [bold cyan]1/2[/] 请为您的出版社命名", default="MySovereignPress")
    vault_path = Prompt.ask("📂 [bold cyan]2/2[/] 请输入您的 Markdown 原稿库 (Vault) 路径", default="./manuscripts")
    
    # 物理路径预检
    if not os.path.exists(vault_path):
        if Confirm.ask(f"⚠️ 路径 [yellow]{vault_path}[/] 不存在，是否自动创建？"):
            os.makedirs(vault_path, exist_ok=True)
        else:
            tlog.error("🛑 [引导中断] 未能建立原稿库关联。")
            return False

    # 3. 物理点火
    success = wm.init_sovereign_territory(press_name, vault_path)

    if success:
        wm.switch(press_name)
        console.print(f"\n✨ [bold green]祝贺！出版社 '{press_name}' 已成功在主权版图上落成。[/]")
        console.print("📖 您现在可以开始向原稿库投递 Markdown，系统将自动开始出版流水线。\n")
        return True
    
    return False

class SetupWizard:
    """保留旧类兼容性（可选）"""
    @staticmethod
    def show():
        return run_onboarding_wizard()
