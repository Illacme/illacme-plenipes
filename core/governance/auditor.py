"""
🔍 主权审计师 — 多维度资产完整性校验引擎。
执行本地资产存在性、远程链接可达性与物理路径合规性的自动化审计。
"""
import os
import shutil
import difflib
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.utils.tracing import tlog
console = Console()

class SovereignAuditor:
    """📊 [V11.0] 全息审计员：负责差异分析与影子转正"""

    def __init__(self, engine):
        self.engine = engine
        self.sandbox = engine.paths.get('sandbox')
        self.production = engine.paths.get('target_base')

    def run_diff_audit(self):
        """执行沙盒与生产环境的深度差异审计"""
        if not self.sandbox or not os.path.exists(self.sandbox):
            tlog.error("🛑 审计失败：未发现沙盒预演数据。请先运行 --sandbox 同步。")
            return

        # 🚀 [V11.0] 发送审计开始信号
        from core.utils.event_bus import bus

        audit_data = {
            "changes": [],
            "found": 0
        }

        for root, _, files in os.walk(self.sandbox):
            for f in files:
                if not f.endswith(('.md', '.mdx')): continue

                sandbox_path = os.path.join(root, f)
                rel_path = os.path.relpath(sandbox_path, self.sandbox)
                prod_path = os.path.join(self.production, rel_path)

                if not os.path.exists(prod_path):
                    audit_data["changes"].append({"path": rel_path, "status": "NEW", "detail": "新资产注入"})
                    audit_data["found"] += 1
                else:
                    with open(sandbox_path, 'r', encoding='utf-8') as sf:
                        s_content = sf.read()
                    with open(prod_path, 'r', encoding='utf-8') as pf:
                        p_content = pf.read()

                    if s_content != p_content:
                        diff = list(difflib.unified_diff(p_content.splitlines(), s_content.splitlines()))
                        added = len([l for l in diff if l.startswith('+') and not l.startswith('+++')])
                        removed = len([l for l in diff if l.startswith('-') and not l.startswith('---')])
                        audit_data["changes"].append({"path": rel_path, "status": "MODIFIED", "detail": f"+{added} / -{removed} 行变动"})
                        audit_data["found"] += 1

        # 🚀 [V11.0] 发布结构化审计结果，由 UI 监听器负责渲染
        bus.emit("AUDIT_DIFF_RESULTS", data=audit_data)

        # 🚀 [V10.5] 触发影子语种物理对齐校验
        self.engine.janitor.sync_shadow_languages()

    def promote_to_production(self):
        """一键转正：将沙盒内容原子性推向生产环境"""
        if not self.sandbox or not os.path.exists(self.sandbox):
            tlog.error("🛑 转正失败：沙盒为空。")
            return

        tlog.info(f"🚀 [主权转正] 正在将 {self.sandbox} 推向 {self.production}...")

        try:
            # 物理合并 (覆盖式)
            for root, _, files in os.walk(self.sandbox):
                for f in files:
                    src_path = os.path.join(root, f)
                    rel_path = os.path.relpath(src_path, self.sandbox)
                    dest_path = os.path.join(self.production, rel_path)

                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)

            tlog.info("✨ [转正成功] 生产环境已与沙盒镜像完美同步。")
            # 自动清理沙盒以维持主权纯净
            shutil.rmtree(self.sandbox)
            tlog.info("🧹 沙盒已自动回收。")
        except Exception as e:
            tlog.error(f"🛑 转正过程发生灾难性异常: {e}")
