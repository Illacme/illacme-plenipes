# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Sovereign Onboarding Wizard
职责：引导用户完成第一个出版社空间的物理创建与算力绑定。
🛡️ [V50.3]：基于“主权 Imprint”共识的交互式引导。
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from core.governance.imprint_manager import im

from core.utils.tracing import tlog

console = Console()

def run_onboarding_wizard() -> bool:
    """🚀 [V50.3] 极速主权引导：开启您的第一个出版品牌 (Imprint)"""
    
    banner_content = Text.assemble(
        ("\n", "white"),
        ("🚀 欢迎，总编辑阁下。系统检测到尚未建立出版品牌 (Imprint)。\n", "bold white"),
        ("💡 提示：每一个 Imprint 都是一个独立的物理隔离单元，拥有私有配置与影子缓存。\n", "dim")
    )

    
    console.print(Panel(
        Align.center(banner_content),
        border_style="bold cyan",
        padding=(1, 2),
        title="[bold white]THE FOUNDRY VOYAGE[/bold white]",
        subtitle="[bold cyan]Sovereign Press Onboarding[/bold cyan]"
    ))
    console.print("\n")

    wizard_mode = Prompt.ask(
        "🔮 请选择主权操作 ([bold cyan]1[/]. Web 引导 | [bold white]2[/]. 终端引导 | [bold green]3[/]. 切换已有品牌)",
        choices=["1", "2", "3"],
        default="1"
    )
    
    if wizard_mode == "1":
        import webbrowser
        from services.wizard.wizard_server import start_wizard_server
        
        # 🚀 [V50.5] 端口矩阵：向导固定使用 43211
        port = 43211
        url = f"http://127.0.0.1:{port}"
        console.print(Panel(
            f"📡 [bold yellow]Web 引导服务已启动[/]\n请在浏览器访问: [bold cyan]{url}[/]\n[dim]正在尝试自动为您打开浏览器...[/]",
            border_style="yellow"
        ))
        
        # 异步拉起浏览器，防止阻塞服务器启动
        import threading
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        
        # 🚀 [V50.3] 动态守护：在终端展示实时监听状态
        with console.status("[bold yellow]📡 正在后台守护主权引导流程，请在浏览器中完成配置...[/]", spinner="earth"):
            start_wizard_server(port=port)
            
        console.print("\n[bold green]✅ [自举完成] 引导配置已同步，正在销毁临时引导服务...[/]")
        console.print("[bold cyan]🚀 正在平滑切换至主权总编室 (Port 43212)...[/]\n")
        return True

    elif wizard_mode == "3":
        # 🛡️ [V52.10] 主权修复：尝试切换到已有的品牌标识
        available_imprints = [d for d in os.listdir(im.imprint_root) if os.path.isdir(os.path.join(im.imprint_root, d)) and not d.startswith('.')]
        
        if not available_imprints:
            console.print("[bold red]❌ 领土真空：未在 imprints/ 目录下发现任何有效的出版品牌文件夹。[/]")
            return False
            
        choices_with_back = available_imprints + ["back"]
        console.print("📁 [bold cyan]当前探测到的品牌领土:[/]\n  " + "\n  ".join([f"• [bold white]{d}[/]" for d in available_imprints]) + "\n  • [bold yellow]back[/] (返回主菜单)")
        
        target_id = Prompt.ask("\n🎯 请输入您想切换到的品牌标识 (Imprint ID)", choices=choices_with_back, default="back")
        
        if target_id == "back":
            return run_onboarding_wizard() # 递归返回主菜单
        
        from core.config.config import CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR
        # 校验 config.imprint.yaml 存在性
        config_path = os.path.join(IMPRINT_DIR, target_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if not os.path.exists(config_path):
            console.print(f"[bold red]❌ 逻辑残缺：品牌 '{target_id}' 缺少核心配置文件 ({CONFIG_DIR}/{CONFIG_IMPRINT_NAME})，无法激活。[/]")
            return False
            
        # 更新本地覆盖配置（使用门面层，彻底剥离物理读写行为）
        try:
            from core.config.config import load_local_config, save_local_config
            config_obj = load_local_config()
            config_obj.active_imprint = target_id
            save_local_config(config_obj)
            
            console.print(f"\n✨ [bold green]主权对正完成！当前品牌已切换至 '{target_id}'。[/]")
            return True
        except Exception as e:
            tlog.error(f"🛑 [主权修复失败] 更新配置文件时出错: {e}")
            return False

    # 2. 收集出版社元数据 (Terminal 模式)
    press_name = Prompt.ask("🏷️ [bold cyan]1/2[/] 请为出版品牌 (Imprint) 命名", default="MySovereignImprint")
    vault_path = Prompt.ask("📂 [bold cyan]2/2[/] 请输入您的 Markdown 原稿库 (Vault) 路径", default="./manuscripts")
    
    # 物理路径预检
    if not os.path.exists(vault_path):
        if Confirm.ask(f"⚠️ 路径 [yellow]{vault_path}[/] 不存在，是否自动创建？"):
            os.makedirs(vault_path, exist_ok=True)
        else:
            tlog.error("🛑 [引导中断] 未能建立原稿库关联。")
            return False

    # 3. 物理点火
    success = im.init_sovereign_imprint(press_name, vault_path)

    if success:
        im.switch(press_name)
        console.print(f"\n✨ [bold green]祝贺！出版品牌 '{press_name}' 已成功落成。[/]")
        console.print("📖 您现在可以开始向原稿库投递 Markdown，系统将自动开始出版流水线。\n")
        return True
    
    return False

class SetupWizard:
    """保留旧类兼容性（可选）"""
    @staticmethod
    def show():
        return run_onboarding_wizard()
