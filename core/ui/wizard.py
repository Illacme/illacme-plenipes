# -*- coding: utf-8 -*-
import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()

class SetupWizard:
    """🚀 [V24.6] 极速自举向导 (Magic Onboarding)"""
    
    @staticmethod
    def show():
        """执行交互式配置向导 (工业主权版)"""
        console.clear()
        
        # 🚀 [V24.6] 品牌视觉同步：引入全大写像素标识
        ascii_art = r"""
  ▀█▀ █   █   █▀▀█ █▀▀ █▀▄▀█ █▀▀   █▀▀█ █   █▀▀ █▀▀█ ▀█▀ █▀▀█ █▀▀ █▀▀
   █  █   █   █▄▄█ █   █ █ █ █▀▀   █▄▄█ █   █▀▀ █  █  █  █▄▄█ █▀▀ ▀▀█
  ▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ ▀▀▀ ▀   ▀ ▀▀▀   █    ▀▀▀ ▀▀▀ ▀  ▀ ▀▀▀ █    ▀▀▀ ▀▀▀
        """
        banner_content = Text.assemble(
            (ascii_art, "bold cyan"),
            ("\n" + "─" * 72 + "\n", "dim"),
            ("🚀 欢迎进入主权发布官初始化矩阵\n", "white"),
            ("💡 提示：系统将为您构建 [bold yellow]Dual-Config[/] 架构 (config.yaml + config.local.yaml)\n", "dim")
        )
        
        console.print(Panel(
            Align.center(banner_content),
            border_style="bold blue",
            padding=(1, 2),
            subtitle="[bold grey]Zero-G Onboarding Wizard[/bold grey]"
        ))
        console.print("\n")

        # 1. 物理基座
        vault_path = Prompt.ask(" [bold cyan]1/3[/] 请输入您的内容库 (Vault) 路径", default="./content-vault")
        if not os.path.exists(vault_path):
             os.makedirs(vault_path, exist_ok=True)

        # 2. AI 算力
        ai_choice = Prompt.ask("请选择算力来源", choices=["local-ollama", "deepseek", "openai", "skip"], default="local-ollama")
        
        # 3. 分发渠道
        pub_choice = Prompt.ask("分发渠道", choices=["local-ssg", "cloudflare-pages"], default="cloudflare-pages")

        return {"vault_root": vault_path, "active_theme": "starlight", "ai_choice": ai_choice, "pub_choice": pub_choice}
