# -*- coding: utf-8 -*-
"""
Illacme Plenipes Core - Deployment Pipeline Generator
模块职责：自动检测当前激活的 SSG 物理位置，并为其定制化输出一键发布流水线脚本。
🛡️ [V78.0]：支持本地 Bash 一键测试/构建，并自动化对位远端 GitHub Actions YAML 配置。
"""

import os
import datetime
from core.utils.tracing import tlog

class DeploymentPipelineGenerator:
    """
    🚀 自动化一键部署流水线生成器 (DeploymentPipelineGenerator)
    职责：自动检测当前激活的 SSG 物理位置，并为其定制化输出 `.github/workflows/deploy.yml` 及 `deploy.sh`。
    """
    def generate_pipeline(self, engine):
        try:
            # 1. 确定当前激活的 SSG 物理渲染适配器
            adapter = None
            if hasattr(engine, 'ssg_adapter') and hasattr(engine.ssg_adapter, 'active_renderer'):
                adapter = engine.ssg_adapter.active_renderer
            
            if not adapter:
                tlog.warning("⚠️ [流水线生成器] 未找到激活的 SSG 物理渲染适配器，跳过生成。")
                return
            
            adapter_cls = adapter.__class__
            ssg_type = getattr(adapter_cls, 'PLUGIN_ID', 'generic')
            
            # 2. 从 engine 路径解析出 source_dir，并逆向探测 theme 物理根路径
            source_dir = engine.paths.get("source_dir")
            if not source_dir or not os.path.exists(source_dir):
                tlog.warning(f"⚠️ [流水线生成器] 无法获取有效的源文档路径: {source_dir}")
                return
                
            theme_root = self.find_theme_root(source_dir, engine.active_theme)
            if not theme_root or not os.path.exists(theme_root):
                tlog.warning(f"⚠️ [流水线生成器] 无法探测到主题 '{engine.active_theme}' 的物理根路径，跳过生成。")
                return
                
            tlog.info(f"⚓ [流水线生成器] 探测到主题根路径: {theme_root} (SSG Type: {ssg_type})")
            
            # 3. 提取部署变量值
            build_cmd = adapter_cls.get_build_command()
            path_mappings = adapter_cls.get_default_path_mappings()
            site_dir = path_mappings.get("site_dir", "dist")
            
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 4. 生成本地一键发布脚本 deploy.sh
            deploy_sh_tpl = adapter_cls.get_deploy_script_template()
            deploy_sh_content = deploy_sh_tpl.format(
                ssg_type=ssg_type.upper(),
                datetime=now_str,
                build_cmd=build_cmd,
                site_dir=site_dir
            )
            
            deploy_sh_path = os.path.join(theme_root, "deploy.sh")
            with open(deploy_sh_path, "w", encoding="utf-8") as f:
                f.write(deploy_sh_content)
            
            # 赋予可执行权限
            try:
                os.chmod(deploy_sh_path, 0o755)
            except Exception:
                pass
                
            tlog.info(f"🟢 [流水线生成器] 成功生成本地部署脚本: {deploy_sh_path}")
            
            # 5. 生成 GitHub Actions 流水线 .github/workflows/deploy.yml
            github_workflow_tpl = adapter_cls.get_github_actions_template()
            github_workflow_content = github_workflow_tpl.format(
                ssg_type=ssg_type.upper(),
                datetime=now_str,
                build_cmd=build_cmd,
                site_dir=site_dir
            )
            
            workflow_dir = os.path.join(theme_root, ".github", "workflows")
            os.makedirs(workflow_dir, exist_ok=True)
            
            deploy_yml_path = os.path.join(workflow_dir, "deploy.yml")
            with open(deploy_yml_path, "w", encoding="utf-8") as f:
                f.write(github_workflow_content)
                
            tlog.info(f"🟢 [流水线生成器] 成功生成 GitHub Actions 自动化工作流: {deploy_yml_path}")
            
        except Exception as e:
            tlog.error(f"❌ [流水线生成器] 生成部署流水线时抛出异常: {e}")
            
    def find_theme_root(self, source_dir: str, theme_name: str) -> str:
        curr = os.path.abspath(source_dir)
        for _ in range(6):
            if not curr or curr == "/":
                break
            if any(os.path.exists(os.path.join(curr, f)) for f in ["package.json", "hugo.toml", "config.toml", "hugo.yaml", "hugo.json"]):
                return curr
            if os.path.basename(curr) == theme_name:
                return curr
            curr = os.path.dirname(curr)
        return os.path.dirname(os.path.dirname(os.path.abspath(source_dir)))
