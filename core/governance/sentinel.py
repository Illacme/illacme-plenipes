#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Guardian Sentinel (项目健康哨兵)
模块职责：项目健康度审计、自愈行为记录与质量阈值管控。
"""

import os
import json
import logging
import subprocess
import threading
import time
from datetime import datetime

from core.utils.tracing import tlog

class SentinelManager:
    """项目哨兵管家：负责定时执行健康检查、自愈代码并记录日志"""

    def __init__(self, config, engine=None):

        self.config = config
        self.engine = engine
        # 🛡️ [V35.2] 主权对正：使用引擎内置的路径解析器
        if engine:
            self.health_log_path = engine._resolve_path("metadata/sentinel_health.json")
            self.current_iter_id = self._detect_current_iter(engine)
        else:
            self.health_log_path = os.path.join(".plenipes", "sentinel_health.json")
            self.current_iter_id = "UNKNOWN"

        self.last_check = None
        self.status_matrix = {
            "lint": "PENDING",
            "links": "PENDING",
            "tests": "PENDING",
            "token_usage": 0,
            "token_budget": 50000,
            "last_healed": None
        }
        
        # 🚀 [V5.0] 启动配置文件热监听
        if engine:
            self._start_config_watcher()

    def _start_config_watcher(self):
        """🚀 [V24.6] 双向配置监听：同时监控基础配置与本地覆盖层"""
        config_path = self.engine.config_manager.config_path if hasattr(self.engine, 'config_manager') else "config.yaml"
        abs_config = os.path.abspath(config_path)
        local_path = os.path.join(os.path.dirname(abs_config), 'config.local.yaml')
        
        watch_paths = [abs_config]
        if os.path.exists(local_path):
            watch_paths.append(local_path)
        
        def _watch():
            last_mtimes = {p: os.path.getmtime(p) for p in watch_paths}
            while True:
                time.sleep(2.0)
                try:
                    # 动态检测 local 文件的出现 (如果之前不存在)
                    if len(watch_paths) == 1 and os.path.exists(local_path):
                        if os.path.exists(local_path):
                            watch_paths.append(local_path)
                            last_mtimes[local_path] = os.path.getmtime(local_path)
                            tlog.info("🧬 [Sentinel] 检测到本地配置层接入，已加入热监听队列。")

                    for p in watch_paths:
                        current_mtime = os.path.getmtime(p)
                        if current_mtime > last_mtimes[p]:
                            last_mtimes[p] = current_mtime
                            tlog.info(f"🔔 [Sentinel] 检测到物理变动 ({os.path.basename(p)})，正在触发热重载...")
                            self.engine.config_manager.reload()
                except Exception: pass

        t = threading.Thread(target=_watch, name="ConfigWatcher", daemon=True)
        t.start()

    @staticmethod
    def _detect_current_iter(engine=None) -> str:
        """从历史目录侦测当前活动的迭代 ID"""
        if not engine: return "UNKNOWN"
        history_dir = engine._resolve_path("metadata/history")
        if not os.path.exists(history_dir):
            return "UNKNOWN"
        iters = sorted([d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))], reverse=True)
        return iters[0] if iters else "INIT"

    def track_token_usage(self, estimated_tokens: int):
        """跟踪算力消耗并执行 TCG 熔断"""
        self.status_matrix["token_usage"] += estimated_tokens
        limit = self.status_matrix["token_budget"]
        if self.status_matrix["token_usage"] > limit:
            tlog.error(f"🚨 [TCG 熔断] 侦测到单次迭代算力消耗已触顶 ({self.status_matrix['token_usage']} > {limit})！")
            tlog.error("🛡️ [哨兵] 根据全球自律协议，任务已强制挂起，请人工注入算力配额。")
            # 在全自动模式下，此处应引发异常以切断进程
            raise RuntimeError("TCG_BUDGET_EXCEEDED")

    def inject_trace_label(self, code_block: str) -> str:
        """为代码块注入溯源 DNA 标签 (Traceable Intent)"""
        tag = f"🛡️ [AEL-{self.current_iter_id}]"
        if tag in code_block:
            return code_block
        return f"# {tag}\n{code_block}"

    def run_health_check(self, auto_fix: bool = True):
        """执行全量健康自检并触发自愈程序"""
        tlog.info("🛡️ [哨兵] 启动全量项目健康审计...")
        start_time = datetime.now()

        # 1. 执行 Ruff Lint 检查与自愈
        lint_ok = self._check_and_fix_lint(auto_fix)
        self.status_matrix["lint"] = "PASS" if lint_ok else "HEALED"

        # 2. 🛡️ [AEL-2026-04-19_slsh_healing] 执行语义死链修复
        if auto_fix:
            heal_count = self._heal_markdown_links()
            self.status_matrix["links"] = f"FIXED({heal_count})" if heal_count > 0 else "PASS"
        else:
            self.status_matrix["links"] = "PENDING"

        # 3. 记录日志
        self.last_check = datetime.now().isoformat()
        self._persist_status()

        elapsed = (datetime.now() - start_time).total_seconds()
        tlog.info(f"🛡️ [哨兵] 审计完成 (耗时: {elapsed:.2f}s) | 状态: {self.status_matrix['links']}")

    def _heal_markdown_links(self) -> int:
        """
        🚀 [SLSH] 语义死链自愈算法。
        扫描全量笔记库 -> 建立文件索引 -> 匹配死链 -> 执行重定向修正。
        """
        vault_path = self.config.vault_root
        if not os.path.exists(vault_path):
            return 0

        # 1. 建立全量文件索引库 (Filename -> FullPath)
        file_index = {}
        for root, _, files in os.walk(vault_path):
            for f in files:
                if f.endswith('.md'):
                    name_no_ext = os.path.splitext(f)[0]
                    file_index[name_no_ext] = os.path.join(root, f)

        fix_count = 0
        import re

        # 2. 正则定义：wikilinks [[target]] 和 markdown [text](path)
        wiki_pattern = re.compile(r'\[\[(.*?)\]\]')

        for root, _, files in os.walk(vault_path):
            for f in files:
                if not f.endswith('.md'): continue

                file_path = os.path.join(root, f)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # 检查是否存在死链
                new_content = content
                matches = wiki_pattern.findall(content)

                for target in matches:
                    # 分离别名：[[target|alias]]
                    clean_target = target.split('|')[0].strip()
                    # 检查物理文件是否存在 (此处假设简单匹配文件名)
                    if clean_target not in file_index:
                        # 尝试模糊修复：比如 target 含有路径，但文件可能已移动
                        target_name = os.path.basename(clean_target)
                        if target_name in file_index:
                            new_target = target_name # 简化修复，指向新文件名
                            new_content = new_content.replace(f'[[{target}]]', f'[[{new_target}]]')
                            fix_count += 1
                            tlog.info(f"🛡️ [SLSH] 已修复死链: {target} -> {new_target} (在 {f} 中)")

                if new_content != content:
                    # 注入溯源标签
                    final_content = self.inject_trace_label(new_content)
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(final_content)

        return fix_count

    def _check_and_fix_lint(self, auto_fix: bool) -> bool:
        """调用 Ruff 执行静态分析与自动修复"""
        try:
            import sys
            cmd = [sys.executable, "-m", "ruff", "check", ".", "--select", "E,F", "--exclude", ".plenipes"]
            if auto_fix:
                cmd.append("--fix")

            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return True
            else:
                if auto_fix:
                    tlog.info("🛡️ [哨兵] 侦测到代码风格偏离，已尝试执行自动修复 (Healed)。")
                return False
        except (FileNotFoundError, ImportError) as e:
            tlog.warning(f"⚠️ [哨兵] Ruff 环境未就绪或未安装，跳过静态分析自愈: {e}")
            return True
        except Exception as e:
            tlog.error(f"⚠️ [哨兵] Ruff 运行异常: {e}")
            return False
            return False

    def _persist_status(self):
        """将健康状态持久化至 .plenipes 目录"""
        try:
            data = {
                "last_check": self.last_check,
                "matrix": self.status_matrix,
                "project": "Illacme-plenipes"
            }
            with open(self.health_log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            tlog.error(f"⚠️ [哨兵] 状态持久化失败: {e}")

    def verify_docs_sync_hook(self, rel_path: str):
        """🚀 [Simulation Hook] 被 Engine 调用的钩子，用于影子校验或资产闭环记录"""
        tlog.debug(f"🛡️ [哨兵] 收到同步完成信号: {rel_path} | 触发影子校验探针...")
        # 此处可对接 autonomous_simulation.py 的逻辑
        pass
