"""
📋 报告处理器 — 详细运行报告与日志归档的终端渲染。
负责将引擎运行日志以结构化报表形式输出并归档至历史目录。
"""
# -*- coding: utf-8 -*-
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

class ReportHandlers:
    """🚀 [V48.3] 终端系统级报告处理器"""
    
    @staticmethod
    def handle_plugin_report(report):
        """分发插件中心看板"""
        console.print("\n[bold cyan]📡 Illacme-plenipes 分发插件中心[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta", border_style="dim")
        table.add_column("插件 ID", style="bold")
        table.add_column("状态", width=15)
        table.add_column("运行环境备注")

        for p in report:
            status_style = {"ACTIVE": "[green]● ACTIVE[/green]", "INACTIVE": "[grey]○ INACTIVE[/grey]"}.get(p.get('status'), p.get('status'))
            table.add_row(p.get('id'), status_style, "✅ 就绪")
        console.print(table)

    @staticmethod
    def handle_brain_report(summary):
        """知识沉淀简报"""
        console.print("\n" + "="*50)
        console.print(f"🧠 [bold cyan]Illacme-plenipes 知识沉淀简报[/bold cyan] ({summary.get('total_lessons')} 条教训)")
        console.print("="*50)
        if summary.get('total_lessons') > 0:
            console.print(f"\n📂 覆盖领域: {', '.join(summary.get('categories'))}")
        console.print("\n" + "="*50)
