import ast
import os
import sys

class SovereigntyAuditor(ast.NodeVisitor):
    """🚀 [V11.8] 基于 AST 的核心架构审计员"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.violations = []
        self.core_methods = 0

    def visit_FunctionDef(self, node):
        # 检查是否带有 SovereignCore 装饰器
        is_core = any(
            isinstance(decorator, ast.Name) and decorator.id == 'SovereignCore'
            or isinstance(decorator, ast.Attribute) and decorator.attr == 'SovereignCore'
            for decorator in node.decorator_list
        )
        
        if is_core:
            self.core_methods += 1
            # 1. 契约校验：必须有 docstring
            doc = ast.get_docstring(node)
            if not doc or len(doc) < 20:
                self.violations.append(f"❌ [文档坍塌] 核心方法 '{node.name}' 的 docstring 缺失或过短，主权记忆丢失。")
            
            # 2. 签名稳定性校验 (此处仅演示：禁止参数过少)
            if len(node.args.args) < 1:
                self.violations.append(f"❌ [契约异常] 核心方法 '{node.name}' 签名异常（参数丢失）。")

def audit_project(root_dir):
    print(f"🛡️ [主权审计] 正在扫描核心架构: {root_dir}")
    total_violations = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                        auditor = SovereigntyAuditor(path)
                        auditor.visit(tree)
                        if auditor.violations:
                            print(f"  |-- 📁 {os.path.relpath(path, root_dir)}")
                            for v in auditor.violations:
                                print(f"  |   └── {v}")
                            total_violations.extend(auditor.violations)
                except Exception as e:
                    print(f"  ⚠️ [无法解析] {path}: {e}")

    if total_violations:
        print(f"\n🛑 [审计拦截] 发现 {len(total_violations)} 处主权违规！迭代已中止。")
        sys.exit(1)
    else:
        print("\n✅ [审计通过] 核心架构契约完整，主权稳固。")

if __name__ == "__main__":
    audit_project("core")
