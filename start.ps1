# ==============================================================================
# 🚀 Illacme Plenipes - Windows PowerShell 启动器 (PowerShell Launcher)
# 职责：检测 Python 3.10+、自动激活环境、拉起出版引擎并打开治理中心。
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Illacme Plenipes 全球私人出版社"

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🏛️  Illacme Plenipes 全球私人出版社 - PowerShell 启动器   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Set-Location -LiteralPath $PSScriptRoot

# 1. 优先探测激活虚拟环境
$PythonCmd = ""

if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "🔍 发现本地虚拟环境 (.venv)，正在激活..." -ForegroundColor Green
    & ".venv\Scripts\Activate.ps1"
    $PythonCmd = "python"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔍 发现本地虚拟环境 (venv)，正在激活..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
    $PythonCmd = "python"
} else {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonCmd = "python"
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonCmd = "py"
    }
}

# 2. 验证 Python 是否存在
if (-not $PythonCmd) {
    Write-Host "❌ 未检测到 Python 运行环境！" -ForegroundColor Red
    Write-Host "💡 请先安装 Python 3.10 或更高版本 (https://www.python.org)" -ForegroundColor Yellow
    Read-Host "按回车键退出..."
    exit 1
}

# 3. 校验 Python 版本 >= 3.10
$VerCheck = & $PythonCmd -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)" 2>$null
if ($VerCheck -ne "1") {
    Write-Host "❌ 当前 Python 版本过低，Illacme Plenipes 工业引擎要求 Python 3.10+。" -ForegroundColor Red
    Read-Host "按回车键退出..."
    exit 1
}

Write-Host "✅ Python 环境校验通过: $(& $PythonCmd -V)" -ForegroundColor Green

# 4. 依赖缺失检查与安装
$MissingDep = & $PythonCmd -c @"
for mod in ['yaml', 'fastapi', 'uvicorn', 'cryptography']:
    try:
        __import__(mod)
    except ImportError:
        print(mod)
        break
"@ 2>$null

if ($MissingDep) {
    Write-Host "⚠️ 探测到缺少依赖模块 ($MissingDep)，正在自动安装..." -ForegroundColor Yellow
    & $PythonCmd -m pip install --disable-pip-version-check -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 依赖安装失败，请检查网络后重试。" -ForegroundColor Red
        Read-Host "按回车键退出..."
        exit 1
    }
    Write-Host "✅ 依赖安装完成！" -ForegroundColor Green
}

# 5. 异步唤醒默认浏览器
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:43212"
} | Out-Null

Write-Host "🛰️ 正在点火拉起 Illacme Plenipes 全球出版引擎..." -ForegroundColor Cyan
Write-Host "💡 治理中心即将自动在浏览器中打开 (http://localhost:43212)" -ForegroundColor Yellow
Write-Host "💡 按 Ctrl + C 可安全停止出版引擎并存档。" -ForegroundColor Yellow
Write-Host ""

# 6. 拉起主程序
& $PythonCmd plenipes.py @args
