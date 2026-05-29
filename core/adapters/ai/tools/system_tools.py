import os
import psutil
import subprocess
from typing import Dict, Any

from core.adapters.ai.tool_protocol import IllacmeTool

class CheckHealthTool(IllacmeTool):
    """
    🏢 [V75.0] 系统健康诊断工具
    """
    name = "check_system_health"
    description = "Check the server's CPU, memory, and disk usage statistics."
    
    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self) -> str:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            report = (
                f"=== Illacme Plenipes System Health ===\n"
                f"CPU Usage: {cpu_percent}%\n"
                f"Memory Usage: {mem.percent}% (Used: {mem.used / (1024**3):.2f}GB / Total: {mem.total / (1024**3):.2f}GB)\n"
                f"Disk Usage: {disk.percent}% (Free: {disk.free / (1024**3):.2f}GB)\n"
            )
            return report
        except Exception as e:
            return f"Error gathering health metrics: {str(e)}"

class GitStatusTool(IllacmeTool):
    """
    🏢 [V75.0] Git 状态检查工具
    """
    name = "get_git_status"
    description = "Run 'git status' and 'git log -1' to get the current state of the repository."
    
    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self) -> str:
        try:
            status_output = subprocess.check_output(['git', 'status', '-s'], text=True, stderr=subprocess.STDOUT)
            log_output = subprocess.check_output(['git', 'log', '-1', '--oneline'], text=True, stderr=subprocess.STDOUT)
            
            return f"--- Current Commit ---\n{log_output}\n--- Changed Files ---\n{status_output if status_output.strip() else 'No changed files.'}"
        except Exception as e:
            return f"Error executing git command: {str(e)}"
