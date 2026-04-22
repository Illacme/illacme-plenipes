#!/bin/sh
# 🛡️ Illacme-plenipes 开发环境初始化脚本
# 用法：clone 项目后执行 sh scripts/setup-hooks.sh
# 作用：安装 Git pre-commit hook，让治理自审引擎在每次提交时自动运行

HOOK_FILE=".git/hooks/pre-commit"

if [ ! -d ".git" ]; then
    echo "❌ 未检测到 .git 目录，请在项目根目录下运行此脚本。"
    exit 1
fi

cat > "$HOOK_FILE" << 'EOF'
#!/bin/sh
# 🛡️ Illacme-plenipes Governance Gate (pre-commit hook)
# This hook runs the governance self-audit before every commit.
# If any check fails, the commit is blocked.

echo "🛡️  [Pre-Commit] 正在执行治理自审..."
python3 tests/governance_audit.py

if [ $? -ne 0 ]; then
    echo ""
    echo "🚨 治理自审未通过，提交已被阻止。"
    echo "   请修复上述问题后重新提交。"
    echo "   如需临时跳过：git commit --no-verify"
    exit 1
fi
EOF

chmod +x "$HOOK_FILE"
echo "✅ Pre-commit hook 已安装到 $HOOK_FILE"
echo "   每次 git commit 时将自动执行 governance_audit.py"
