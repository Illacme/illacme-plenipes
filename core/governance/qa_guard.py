#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI QA Guard (Hallucination Detector)
模块职责：对 AI 生成的内容进行最后的“物理校验”，防止幻觉与逻辑漂移。
🚀 [V15.1] 智慧升级：链路验证、标签对齐与主权盾牌自愈。
"""

import re
import requests
from core.utils.tracing import tlog

class QAGuard:
    """🛡️ [V15.1] 幻觉护卫：在产物分发前执行终极审计"""

    def __init__(self, engine):
        self.engine = engine
        self.timeout = 3 # 链接检测超时时间

    def audit_context(self, ctx):
        """
        🚀 全量审计 SyncContext 中的 AI 产物
        """
        # 1. 物理链路审计 (防止 AI 虚构无效 URL)
        # [V34.9] 性能加固：禁用同步阻塞的网络探测，避免调度线程池枯竭
        # if ctx.body_content:
        #     self._verify_links(ctx)

        # 2. 主权标签一致性校验 (防止 AEL-Iter-ID 丢失)
        self._verify_sovereignty(ctx)

        # 3. 结构完整性校验
        self._verify_structure(ctx)

    def _verify_links(self, ctx):
        """探测 AI 生成内容中的外链连通性"""
        # 匹配所有 Markdown 链接 [text](url)
        links = re.findall(r'\[.*?\]\((https?://.*?)\)', ctx.body_content)
        if not links: return

        tlog.debug(f"🔍 [QA Guard] 正在验证 {len(links)} 个 AI 生成的外部链路...")

        for url in set(links):
            # 排除已知域
            ignored_domains = self.engine.config.system.network_settings.ignored_domains
            if any(domain in url for domain in ignored_domains):
                continue

            try:
                # 仅进行 HEAD 请求以节省带宽
                headers = {'User-Agent': self.engine.config.system.network_settings.asset_prober_ua}
                resp = requests.head(url, headers=headers, timeout=self.timeout, allow_redirects=True)
                if resp.status_code >= 400:
                    tlog.warning(f"⚠️ [幻觉告警] AI 虛构或引用了失效链路: {url} (HTTP {resp.status_code})")
                    # 标记为降级状态
                    ctx.ai_health_flag[0] = False
            except Exception:
                tlog.warning(f"⚠️ [幻觉告警] AI 引用了无法访问的链路: {url}")
                ctx.ai_health_flag[0] = False

    def _verify_sovereignty(self, ctx):
        """验证产物中是否包含 AEL 追踪标签"""
        tid = ctx.ael_iter_id
        if not tid: return

        # 如果 AI 产物中丢失了追踪标签，则强制物理补全
        if tid not in ctx.body_content and "AEL-" not in ctx.body_content:
            tlog.warning(f"🛡️ [QA Guard] 发现 {ctx.rel_path} 产物中丢失主权追踪标签，正在执行物理修复...")
            ctx.body_content += f"\n\n<!-- Sovereign-Tag: [[AEL-Iter-ID: {tid}]] -->"

    def _verify_structure(self, ctx):
        """验证 Markdown 语法完整性 (如未闭合的 Markdown 块)"""
        content = ctx.body_content

        # 检查代码块是否成对出现
        code_blocks = content.count('```')
        if code_blocks % 2 != 0:
            tlog.error(f"🚨 [结构坍塌] {ctx.rel_path} 产物中存在未闭合的代码块！")
            ctx.ai_health_flag[0] = False

        # 检查加粗/斜体基本闭合（可选，视严格程度而定）
