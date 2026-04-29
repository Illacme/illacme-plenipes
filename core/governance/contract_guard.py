#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Contract Guard
模块职责：全自治架构的物理契约警察。
负责在运行时强制审计所有动态加载的插件是否严格遵守其所属类别的【物理协议】。
🛡️ [AEL-Iter-v5.3]：防止“AI 瞎拆改”的最后一道防线。
"""
import re
import inspect
import logging
from typing import Type, List, Dict

from core.utils.tracing import tlog

class ContractGuard:
    @staticmethod
    def verify_plugin(plugin_cls: Type, base_cls: Type) -> List[str]:
        """
        物理审计：核查子类是否完整且正确地实现了基类的所有抽象协议。
        """
        violations = []

        # 1. 检查插件基类逻辑 (跳过抽象基类本身)
        if plugin_cls == base_cls or inspect.isabstract(plugin_cls) or plugin_cls.__name__.startswith('_') or 'abc' in plugin_cls.__module__:
            return []

        # 2. 检查 PLUGIN_ID 强制约束
        if not hasattr(plugin_cls, 'PLUGIN_ID') or not plugin_cls.PLUGIN_ID:
            violations.append(f"❌ [契约缺失] 插件 '{plugin_cls.__name__}' 未定义强制性属性: PLUGIN_ID")

        # 2. 检查抽象方法签名一致性
        base_methods = {name: func for name, func in inspect.getmembers(base_cls, predicate=inspect.isfunction)
                        if getattr(func, "__isabstractmethod__", False)}

        for name, base_func in base_methods.items():
            if not hasattr(plugin_cls, name):
                violations.append(f"❌ [实现缺失] 插件 '{plugin_cls.__name__}' 未实现基类协议: {name}")
                continue

            plugin_func = getattr(plugin_cls, name)

            # 核查参数签名 (Arity & Names)
            base_sig = inspect.signature(base_func)
            try:
                plugin_sig = inspect.signature(plugin_func)

                # 忽略 self
                base_params = list(base_sig.parameters.values())[1:]
                plugin_params = list(plugin_sig.parameters.values())[1:]

                if len(base_params) != len(plugin_params):
                    violations.append(f"⚠️ [签名偏移] 插件 '{plugin_cls.__name__}.{name}' 参数数量不匹配 (基类: {len(base_params)}, 实际: {len(plugin_params)})")
                else:
                    for bp, pp in zip(base_params, plugin_params):
                        if bp.name != pp.name and pp.name != 'kwargs':
                            violations.append(f"⚠️ [命名漂移] 插件 '{plugin_cls.__name__}.{name}' 参数名不匹配 (基类: {bp.name}, 实际: {pp.name})")
            except ValueError:
                # 某些内置函数可能无法获取签名，跳过
                pass

        return violations

    @staticmethod
    def audit_registry(registry: Dict[str, Type], base_cls: Type, category_name: str) -> List[str]:
        """对整个注册中心执行集群审计"""
        all_violations = []
        tlog.debug(f"🛡️ [契约哨兵] 正在启动 {category_name} 矩阵全量审计...")

        for plugin_id, cls in registry.items():
            violations = ContractGuard.verify_plugin(cls, base_cls)
            if violations:
                all_violations.extend(violations)

        return all_violations

    @staticmethod
    def verify_config(engine_config) -> List[str]:
        """🚀 [V24.6] 工业级配置基因审计：全链路契约验证"""
        import os
        violations = []

        # 1. 验证主权基座 (Vault & Ledger)
        vault_root = os.path.abspath(os.path.expanduser(engine_config.vault_root))
        if not os.path.exists(vault_root):
            violations.append(f"❌ [配置坍塌] 笔记库根目录不存在: {vault_root}")
        
        # 2. 验证 Dual-Config 隔离契约
        config_path = getattr(engine_config, 'config_path', 'config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 工业规则：严禁在主配置文件中存放未加密的敏感 Key
                if re.search(r'key:\s*["\'](sk-|AIza|ghp)[^"\']+["\']', content):
                    violations.append(f"❌ [安全红线] 检测到主配置文件 {config_path} 中包含明文敏感密钥，请迁移至 *.local.yaml 或使用 enc: 加密。")

        # 3. 验证算力网关一致性
        translation = engine_config.translation
        if translation.enable_ai:
            primary = translation.primary_node
            if not primary or primary not in translation.providers:
                violations.append(f"❌ [算力治理] 未定义的默认算力节点: {primary}")
            else:
                p_node = translation.providers[primary]
                if not p_node.api_key or "HERE" in p_node.api_key:
                    tlog.warning(f"⚠️ [算力警告] 节点 '{primary}' 尚未配置 API_KEY，推理网关处于熔断状态。")

        return violations

    @staticmethod
    def verify_structure_integrity() -> List[str]:
        """🚀 [V24.6] 架构指纹审计：锁定物理目录版图"""
        import os
        violations = []
        baseline_path = ".plenipes/governance/structure.baseline"
        
        if not os.path.exists(baseline_path):
            return ["⚠️ [指纹缺失] 未发现架构基准文件，无法执行结构完整性审计。"]

        try:
            with open(baseline_path, 'r', encoding='utf-8') as f:
                baseline = {line.strip() for line in f if line.strip()}
            
            # 实时采样当前核心目录结构
            current_structure = set()
            for root, dirs, files in os.walk('core'):
                for file in files:
                    if not file.startswith('.'):
                        path = os.path.join(root, file).replace('\\', '/')
                        current_structure.add(path)
            
            # 1. 检查缺失
            missing = baseline - current_structure
            if missing:
                violations.append(f"❌ [结构坍塌] 检测到核心文件丢失: {', '.join(list(missing)[:3])}...")
            
            # 2. 检查非法新增
            unregistered = current_structure - baseline
            if unregistered:
                violations.append(f"❌ [架构越权] 检测到未经审计的新增文件: {', '.join(list(unregistered)[:3])}...")
                
        except Exception as e:
            violations.append(f"⚠️ [审计异常] 架构指纹对比失败: {e}")

        return violations

    @staticmethod
    def verify_repository_compliance() -> List[str]:
        """🚀 [V24.6] 全域合规性哨兵：模拟 GitHub 安全审计行为"""
        import os
        import re
        violations = []
        
        # 0. 首先执行结构完整性审计
        violations.extend(ContractGuard.verify_structure_integrity())
        
        # 1. API Key 物理扫描
        KEY_PATTERN = re.compile(r'(?:sk-|AIza|ghp_)[a-zA-Z0-9]{16,}')
        # 规则 2: 不安全函数与调试残留扫描
        UNSAFE_PATTERN = re.compile(r'(?:os\.system|eval|print)\(')
        
        exclude_dirs = {".git", "node_modules", ".plenipes", ".venv", "themes"}
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if not file.endswith((".py", ".yaml", ".md")): continue
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if KEY_PATTERN.search(content) and "enc:" not in content:
                            violations.append(f"❌ [泄露风险] 文件 '{path}' 中疑似包含明文密钥。")
                        if UNSAFE_PATTERN.search(content):
                            # 仅对核心逻辑目录和 scripts 进行严格限制
                            if "core" in root or "scripts" in root:
                                violations.append(f"⚠️ [代码注入风险] 文件 '{path}' 中使用了不安全的系统调用 (os.system/eval)。")
                except: pass
        
        # 规则 3: .gitignore 完整性审计
        gitignore_path = ".gitignore"
        if not os.path.exists(gitignore_path):
            violations.append("❌ [治理缺失] 仓库根目录缺少 .gitignore 文件。")
        else:
            with open(gitignore_path, 'r') as f:
                gi = f.read()
                if "*.local.yaml" not in gi and "config.local.yaml" not in gi:
                    violations.append("❌ [隔离失效] .gitignore 未屏蔽本地配置文件 (*.local.yaml)。")

        return violations
