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

        # 🎨 ILLACME PLENIPES 赛博阶梯终极沉浸版 (V48.2)
        # 视觉主权极致对齐：实体字母网格 + 10-char 阶梯右移 + A/C 像素级对称重构
        ascii_art = r"""
████╗ ██╗    ██╗     █████╗   ████╗ ██╗   ██╗ █████╗
╚██╔╝ ██║    ██║    ██╔══██╗ ██╔══╝ ███╗ ███║ ██╔══╝
 ██║  ██║    ██║    ███████║ ██║    ██╔██╗██║ ████╗ 
 ██║  ██║    ██║    ██╔══██║ ██║    ██║╚═╝██║ ██╔═╝ 
████╗ █████╗ █████╗ ██║  ██║ ╚████╗ ██║   ██║ █████╗
╚═══╝ ╚════╝ ╚════╝ ╚═╝  ╚═╝  ╚═══╝ ╚═╝   ╚═╝ ╚════╝
          █████╗  ██╗    █████╗ ██╗ ██╗ ████╗ █████╗  █████╗ █████╗
          ██╔═██╗ ██║    ██╔══╝ ███╗██║ ╚██╔╝ ██╔═██╗ ██╔══╝ ██╔══╝
          █████╔╝ ██║    ████╗  ██╔███║  ██║  █████╔╝ ████╗  ╚███╗ 
          ██╔══╝  ██║    ██╔═╝  ██║╚██║  ██║  ██╔══╝  ██╔═╝   ╚═██╗
          ██║     █████╗ █████╗ ██║ ██║ ████╗ ██║     █████╗ ████╔╝
          ╚═╝     ╚════╝ ╚════╝ ╚═╝ ╚═╝ ╚═══╝ ╚═╝     ╚════╝ ╚═══╝ 
        """
        banner_text = Text(ascii_art, style="bold cyan")
        banner_text.append("\n" + " " * 10 + "═════════════════════════════════════════════════════════" + "\n", style="dim cyan")
        
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
            subtitle="[bold cyan]Global Private Press | 全球私人出版社[/bold cyan]",
            subtitle_align="right"
        ))
        
        # 🚀 [V35.2] 方案 C 功能底座宣告
        console.print(Align.center(
            Text("您的主权化全球出版发行中心 | Your Sovereign Global Publishing & Distribution Center", style="dim italic cyan")
        ))
        console.print("\n")


    @staticmethod
    def handle_system_warnings(warnings):
        """核心红线审计报告看板"""
        if not warnings: return
        warning_text = Text()
        for w in warnings:
            warning_text.append(f" • {w}\n", style="yellow")
        panel = Panel(warning_text, title="⚠️ [bold yellow] 核心红线审计报告 [/]", border_style="yellow", padding=(1, 4), width=100)
        console.print(panel)
