#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Runner
模块职责：单向数据流调度引擎。
"""

import logging

from core.utils.tracing import tlog

class PipelineStep:
    """流水线工序基类"""
    def process(self, context):
        raise NotImplementedError("子类必须实现 process 方法")

class Pipeline:
    """流水线调度引擎"""
    def __init__(self):
        self.steps = []

    def add_step(self, step: PipelineStep):
        self.steps.append(step)
        return self

    @classmethod
    def build(cls, step_names: list, registry) -> 'Pipeline':
        """🚀 [V33] 动态构建器：从注册中心按序提取组件"""
        p = cls()
        for name in step_names:
            step_cls = registry.get_step(name)
            if step_cls:
                p.add_step(step_cls())
            else:
                tlog.warning(f"⚠️ [管线装配] 无法找到已注册的步骤: {name}")
        return p

    def execute(self, context):
        total_steps = len(self.steps)
        for i, step in enumerate(self.steps):
            if context.is_aborted:
                # 管道已触发熔断，静默跳过后续所有动作
                break

            step_name = step.__class__.__name__
            progress = (i / total_steps) * 100
            context.push_status(f"STEP_{step_name.upper()}", msg=f"正在执行工序: {step_name}", progress=progress)

            try:
                # 在此处执行具体工序
                step.process(context)
            except Exception as e:
                tlog.error(f"❌ 流水线工序 [{step_name}] 发生致命崩溃: {e}")
                context.is_aborted = True
                context.push_status("CRASHED", msg=f"工序 {step_name} 崩溃: {e}")
                raise # 向上抛出，交由 orchestrator 的 ThreadPoolExecutor 捕获并打印堆栈
        
        if not context.is_aborted:
            context.push_status("COMPLETED", msg="文档同步流水线执行完毕", progress=100.0)
