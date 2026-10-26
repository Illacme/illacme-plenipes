#!/bin/bash
# ==============================================================================
# 🚀 Illacme Plenipes - 命令行一键同步与出版发布脚本 (One-Click Publish Script)
# 职责：检测 Python 环境并自动执行 plenipes.py --sync 内容同步与静态出版管线。
# ==============================================================================

cd "$(dirname "$0")" || exit 1

PY_CMD=""
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    PY_CMD="python3"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    PY_CMD="python3"
else
    if command -v python3 &>/dev/null; then
        PY_CMD="python3"
    elif command -v python &>/dev/null; then
        PY_CMD="python"
    fi
fi

if [ -z "$PY_CMD" ]; then
    echo "❌ 未检测到 Python 运行环境！请先安装 Python 3.10+"
    exit 1
fi

echo "🌉 正在运行 Illacme Plenipes 全球出版引擎执行全量同步 (--sync)..."
$PY_CMD ./plenipes.py --sync "$@"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 同步出版流程执行完毕！"
else
    echo "⚠️ 同步出版流程退出，退出码: $EXIT_CODE"
fi
exit $EXIT_CODE