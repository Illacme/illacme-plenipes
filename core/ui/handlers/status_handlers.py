# -*- coding: utf-8 -*-
import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from core.utils.tracing import tlog

console = Console()

class StatusHandlers:
    """🚀 [V24.6] 终端基础状态渲染器"""
    
    @staticmethod
    def handle_banner(version, ael_iter_id, mode, sentinel_status=None):
        """🚀 [V35.0] 品牌化 ASCII Banner：全球私人出版社专属视觉"""
        from rich.table import Table

        # 🎨 ILLACME PLENIPES 尊贵艺术字
        ascii_art = r"""
  ___  _  _                 ___  _                 _
 |_ _|| || | __ _  __ _ _ _ | _ \| | ___ _ _  _ _ (_) _ __  ___  ___
  | | | || |/ _` |/ _` | ' \|  _/| |/ -_) ' \| ' \| || '_ \/ -_)(_-<
 |___||_||_|\__,_|\__,_|_||_|_|  |_|\___|_||_|_||_|_|| .__/\___|/__/
                                                     |_|
        """
        banner_text = Text(ascii_art, style="bold cyan")
        banner_text.append("\n" + "═" * 72 + "\n", style="dim cyan")
        
        table = Table(box=None, show_header=False, padding=(0, 1))
        table.add_column("label", justify="left", style="dim cyan", width=18)
        table.add_column("sep", justify="center", width=2)
        table.add_column("value", justify="left")

        table.add_row(" 🛰️  Release", ":", f"[bold cyan]{version}[/]")
        table.add_row(" 📜  Edition", ":", f"[italic grey]{ael_iter_id}[/]")
        table.add_row(" ⚙️  Press Power", ":", f"[bold green]{mode}[/]")
        
        if sentinel_status:
            table.add_row(" 🛡️  Proofreader", ":", f"[bold yellow]{sentinel_status}[/]")
            
        from rich.console import Group
        info_group = Group(
            Align.center(banner_text),
            Align.center(table)
        )
        
        console.print(Panel(
            info_group,
            border_style="bold cyan",
            padding=(1, 4),
            title="[bold white]ILLACME PLENIPES[/bold white]",
            subtitle="[bold cyan]Your Global Private Press | 您的全球私人出版社[/bold cyan]"
        ))


    @staticmethod
    def handle_system_warnings(warnings):
        """核心红线审计报告看板"""
        if not warnings: return
        warning_text = Text()
        for w in warnings:
            warning_text.append(f" • {w}\n", style="yellow")
        panel = Panel(warning_text, title="⚠️ [bold yellow] 核心红线审计报告 [/]", border_style="yellow", padding=(1, 4), width=100)
        console.print(panel)
