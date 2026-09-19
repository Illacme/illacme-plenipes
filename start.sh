#!/bin/bash
# ==============================================================================
# 🚀 Illacme Plenipes - Linux / 通用一键启动器 (One-Click Launcher)
# 职责：自动检测 Python 3.10+ 与虚拟环境，拉起出版引擎并按需唤醒浏览器。
# ==============================================================================

# 1. 物理定位至项目根目录
cd "$(dirname "$0")" || exit 1

# 颜色与样式
BOLD="\033[1m"
CYAN="\033[36m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║      🏛️  Illacme Plenipes 全球私人出版社 - 快速启动器         ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# 2. 虚拟环境优先对齐
PY_CMD=""

if [ -f ".venv/bin/activate" ]; then
    echo -e "${GREEN}🔍 发现本地虚拟环境 (.venv)，正在激活...${RESET}"
    source .venv/bin/activate
    PY_CMD="python3"
elif [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}🔍 发现本地虚拟环境 (venv)，正在激活...${RESET}"
    source venv/bin/activate
    PY_CMD="python3"
else
    if command -v python3 &>/dev/null; then
        PY_CMD="python3"
    elif command -v python &>/dev/null; then
        PY_CMD="python"
    fi
fi

# 3. 校验 Python 版本 >= 3.10
if [ -z "$PY_CMD" ]; then
    echo -e "${RED}❌ 未检测到 Python 运行环境！${RESET}"
    echo -e "${YELLOW}💡 请先安装 Python 3.10 或更高版本。${RESET}"
    exit 1
fi

PY_VER_CHECK=$($PY_CMD -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)" 2>/dev/null)
if [ "$PY_VER_CHECK" != "1" ]; then
    CURRENT_VER=$($PY_CMD -V 2>&1)
    echo -e "${RED}❌ 当前 Python 版本过低: ${CURRENT_VER}${RESET}"
    echo -e "${YELLOW}💡 Illacme Plenipes 工业引擎要求 Python 3.10+，请升级您的 Python 环境。${RESET}"
    exit 1
fi

echo -e "${GREEN}✅ Python 环境校验通过: $($PY_CMD -V)${RESET}"

# 4. 依赖完整性快速探测
MISSING_DEP=$($PY_CMD -c "
for mod in ['yaml', 'fastapi', 'uvicorn', 'cryptography']:
    try:
        __import__(mod)
    except ImportError:
        print(mod)
        break
" 2>/dev/null)

if [ -n "$MISSING_DEP" ]; then
    echo -e "${YELLOW}⚠️ 探测到缺少运行依赖模块: ${MISSING_DEP}${RESET}"
    echo -e "${CYAN}📦 正在尝试自动安装依赖 (pip install -r requirements.txt)...${RESET}"
    $PY_CMD -m pip install --disable-pip-version-check -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 依赖安装失败，请手动执行: pip install -r requirements.txt${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✅ 依赖自动安装完成！${RESET}"
fi

# 5. 异步尝试唤醒默认浏览器 (如果有桌面 GUI 环境)
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ] || [ "$(uname)" = "Darwin" ]; then
    (
        sleep 2.5
        if command -v open &>/dev/null; then
            open "http://localhost:43212" &>/dev/null
        elif command -v xdg-open &>/dev/null; then
            xdg-open "http://localhost:43212" &>/dev/null
        fi
    ) &
fi

echo -e "${CYAN}🛰️ 正在点火拉起 Illacme Plenipes 全球出版引擎...${RESET}"
echo -e "${YELLOW}💡 治理中心访问地址: http://localhost:43212${RESET}"
echo -e "${YELLOW}💡 按 Ctrl + C 可安全停止出版引擎并存档。${RESET}"
echo ""

# 6. 正式拉起主进程 (传递所有参数)
exec $PY_CMD ./plenipes.py "$@"
