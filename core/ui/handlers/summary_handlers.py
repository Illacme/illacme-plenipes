"""
📊 汇总处理器 — 任务执行汇总与算力看板的终端渲染。
负责将出版引擎的处理统计（更新/跳过/耗时/Token 支出）以 Rich 面板呈现。
"""
# -*- coding: utf-8 -*-
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text

console = Console()

class SummaryHandlers:
    """🚀 [V24.6] 任务结束汇总与性能看板处理器"""
    
    @staticmethod
    def handle_summary(stats, elapsed_time, usage_stats=None):
        """展示任务执行汇总与算力看板"""
        if usage_stats:
            cost = usage_stats.get("cost", 0.0)
            saved = usage_stats.get("saved_value", 0.0)
            if stats.get('UPDATED', 0) == 0 and stats.get('SKIP', 0) > 0:
                usage_panel = Panel(Align.center("[bold green]✨ 极速模式：100% 命中缓存。[/bold green]"), title="⚡ Token Guard 看板", border_style="green")
            else:
                roi = (saved / cost * 100) if cost > 0 else 0.0
                usage_panel = Panel(Align.center(f"[bold]支出:[/] [red]{cost:.4f}[/] | [bold]节省:[/] [green]{saved:.4f}[/] | [bold]ROI:[/] [cyan]{roi:.1f}%[/]"), title="⚡ Token Guard 看板", border_style="cyan")
            console.print(usage_panel)

        summary_table = Table(box=None, show_header=False, padding=(0, 2))
        summary_table.add_row("✅ 更新/翻译:", f"[green]{stats.get('UPDATED', 0)} 篇[/]")
        summary_table.add_row("🔄 缓存跳过:", f"[yellow]{stats.get('SKIP', 0)} 篇[/]")
        console.print(Panel(summary_table, title=f"🎉 汇总 | 耗时: [cyan]{elapsed_time}[/]", border_style="green"))
