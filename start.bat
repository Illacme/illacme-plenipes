@echo off
:: ==============================================================================
:: 🚀 Illacme Plenipes - Windows 一键双击启动器 (One-Click Launcher)
:: 职责：自动检测 Python 3.10+ 与虚拟环境，拉起出版引擎并自动在浏览器中打开治理中心。
:: ==============================================================================
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"
title Illacme Plenipes 全球私人出版社

echo ===================================================================
echo        Illacme Plenipes 全球私人出版社 - Windows 快速启动器
echo ===================================================================
echo.

:: 1. 优先激活本地虚拟环境
set "PY_CMD="

if exist ".venv\Scripts\activate.bat" (
    echo [发现] 正在激活本地虚拟环境 (.venv)...
    call ".venv\Scripts\activate.bat"
    set "PY_CMD=python"
) else if exist "venv\Scripts\activate.bat" (
    echo [发现] 正在激活本地虚拟环境 (venv)...
    call "venv\Scripts\activate.bat"
    set "PY_CMD=python"
) else (
    where python >nul 2>nul
    if !errorlevel! equ 0 (
        set "PY_CMD=python"
    ) else (
        where py >nul 2>nul
        if !errorlevel! equ 0 (
            set "PY_CMD=py -3"
        )
    )
)

:: 2. 检查 Python 是否可用
if "%PY_CMD%"=="" (
    echo [错误] 未检测到 Python 运行环境！
    echo [提示] 请前往 https://www.python.org 下载安装 Python 3.10 或更高版本。
    echo [提示] 安装时请务必勾选 "Add python.exe to PATH"。
    echo.
    pause
    exit /b 1
)

:: 3. 校验 Python 版本 >= 3.10
for /f "tokens=*" %%i in ('%PY_CMD% -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)" 2^>nul') do set PY_VER_CHECK=%%i
if not "%PY_VER_CHECK%"=="1" (
    echo [错误] 当前 Python 版本过低，Illacme Plenipes 要求 Python 3.10+。
    echo.
    pause
    exit /b 1
)

echo [就绪] Python 环境校验通过。

:: 4. 依赖检测与自愈安装
for /f "tokens=*" %%i in ('%PY_CMD% -c "
for mod in ['yaml', 'fastapi', 'uvicorn', 'cryptography']:
    try:
        __import__(mod)
    except ImportError:
        print(mod)
        break
" 2^>nul') do set MISSING_DEP=%%i

if not "%MISSING_DEP%"=="" (
    echo [注意] 检测到缺少核心依赖库 (%MISSING_DEP%)，正在执行自动安装...
    %PY_CMD% -m pip install --disable-pip-version-check -r requirements.txt
    if !errorlevel! neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接后重试。
        echo.
        pause
        exit /b 1
    )
    echo [成功] 依赖库安装完成。
)

:: 5. 延时异步唤醒浏览器
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:43212"

echo [点火] 正在拉起 Illacme Plenipes 全球出版引擎...
echo [提示] 治理中心看板即将自动在默认浏览器中打开 (http://localhost:43212)
echo [提示] 按 Ctrl + C 可安全停止出版引擎并存档。
echo.

:: 6. 执行主程序
%PY_CMD% plenipes.py %*

if !errorlevel! neq 0 (
    echo.
    echo [提示] 程序异常退出，按任意键关闭窗口...
    pause >nul
)
