"""
🧹 审计处理器 — 资产审计基线报告与诊断简报的终端渲染。
负责将主权审计引擎的校验结果以 Rich 表格与面板形式呈现给出版社管理员。
"""
# -*- coding: utf-8 -*-
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

class AuditHandlers:
    """🚀 [V48.3] 终端审计与诊断结果处理器"""
    
    @staticmethod
    def handle_audit_results(missing_local, dead_remote, total_files):
        """资产审计基线报告"""
        console.print("\n[bold magenta]🧹 资产审计基线报告[/bold magenta]")
        table = Table(show_header=True, header_style="bold cyan", border_style="dim")
        table.add_column("维度", style="dim", width=12)
        table.add_column("状态", width=12)
        table.add_column("详情")

        if not missing_local:
            table.add_row("本地资产", "[green]PASS[/green]", f"✨ {total_files} 篇资产引用 100% 严丝合缝")
        else:
            table.add_row("本地资产", "[bold red]FAIL[/bold red]", f"⚠️ 发现 {len(missing_local)} 处物理资产丢失！")

        if not dead_remote:
            table.add_row("外链雷达", "[green]PASS[/green]", "🟢 所有远程图床链接均健康 (HTTP 200)")
        else:
            table.add_row("外链雷达", "[bold yellow]WARN[/bold yellow]", f"🔴 探测到 {len(dead_remote)} 个远程链接失效")
        console.print(table)

    @staticmethod
    def handle_diagnostic_results(degraded_files, is_watch_mode):
        """最终健康检查与运行状态"""
        if degraded_files:
            content = Text.assemble(
                ("⚠️ 发现 ", "yellow"), (f"{len(degraded_files)}", "bold yellow"), (" 篇文章触发了安全降级运行。\n", "yellow"),
                ("💡 建议抽查以上文件，系统将在下次启动时尝试自动修复。\n\n", "dim"),
                ("\n".join([f"  {i+1}. {f}" for i, f in enumerate(degraded_files[:5])]), "italic")
            )
            console.print(Panel(content, title="[bold yellow]诊断简报[/bold yellow]", border_style="yellow"))

        status_msg = "👀 [bold cyan]同步结束，正在转入后台实时守护...[/bold cyan]" if is_watch_mode else "🛑 [bold green]任务完成，引擎即将安全下线。[/bold green]"
        console.print(f"\n{status_msg}\n")
