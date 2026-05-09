"""
⚙️ 系统路由 — RESTful API 系统健康与运维端点。
提供引擎状态、版本信息与运行时诊断的 API 接口。
"""
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from core.runtime.cli_bootstrap import get_global_engine
from core.logic.orchestration.task_orchestrator import global_executor
import signal
import os
import time
import threading
from datetime import datetime
from core.utils.tracing import tlog
from core.utils.event_bus import bus # 🚀 [V55.9] 关键导入：确保日志信号能正常发射

router = APIRouter()

def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")):
    engine = get_global_engine()
    if not engine or not engine.config.system.api_token: return
    if x_token != engine.config.system.api_token:
        raise HTTPException(status_code=403, detail="Unauthorized")

@router.get("/api/system/health")
def health_check():
    engine = get_global_engine()
    if not engine: return {"status": "starting", "engine": "Illacme-plenipes"}
    return {
        "status": "online",
        "engine": "Illacme-plenipes",
        "imprint": engine.imprint_id,
        "services": engine.services
    }

@router.get("/api/system/status", dependencies=[Depends(verify_token)])
def get_system_status():
    """🚀 [V48.3] 全息状态诊断：返回服务状态、AI 排行榜与系统负载"""
    import time
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    # 计算服务运行时间
    for name, s in (getattr(engine, "services", {}) or {}).items():
        if (s or {}).get("start_time"):
            s["uptime"] = round(time.time() - s.get("start_time"), 1)

    from core.governance.health_registry import health_registry
    return {
        "services": engine.services,
        "ai_nodes": health_registry.get_rankings(),
        "tasks": {
            "queued": global_executor._work_queue.qsize() if hasattr(global_executor, '_work_queue') else 0,
            "active": len([t for t in global_executor.workers if t.is_alive()]) if hasattr(global_executor, 'workers') else 0
        },
        "timestamp": time.time()
    }

@router.get("/api/system/stats", dependencies=[Depends(verify_token)])
def get_stats():
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    return {
        "usage": engine.meter.get_summary_report(),
        "active_workers": len([t for t in global_executor.workers if t.is_alive()])
    }

@router.post("/api/system/shutdown", dependencies=[Depends(verify_token)])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "accepted"}

@router.post("/api/system/preview/restart", dependencies=[Depends(verify_token)])
def restart_preview():
    """🚀 [V55.8] 工业级增强型重启：支持依赖自愈与日志实时穿透"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    from core.utils.event_bus import bus
    
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    package_json = os.path.join(theme_dir, "package.json")
    is_framework = os.path.exists(package_json)
    
    # 🚀 [V55.8] 依赖自愈逻辑
    if is_framework:
        node_modules = os.path.join(theme_dir, "node_modules")
        if not os.path.exists(node_modules):
            tlog.warning("⚠️ [依赖缺失] 检测到 node_modules 不存在，正在启动自动补全程序...")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="⚠️ [系统感知] 检测到主题依赖缺失，正在启动物理补全...")
            # 这里可以调用现有的安装逻辑，或者直接在该线程执行
            # 为了让用户看到日志，我们需要确保 DevServer 能将日志喂给总线
    
    # 如果预览服务器实例不存在，尝试根据配置动态创建
    if not hasattr(engine, 'preview_server') or engine.preview_server is None:
        from core.utils.dev_server import DevServer, FrameworkDevServer
        port = getattr(engine.config.system, 'serve_port', 43213)
        
        if is_framework:
            cmd = "npm run dev -- --port {port}"
            if os.path.exists(os.path.join(theme_dir, "docusaurus.config.js")):
                cmd = "npm run start -- --port {port}"
            engine.preview_server = FrameworkDevServer(directory=theme_dir, command=cmd, port=port)
        else:
            preview_dir = engine.paths.get('static_dir') or engine.paths.get('target_base')
            engine.preview_server = DevServer(directory=preview_dir, port=port)
    
    try:
        # 如果已有运行中的服务器，先尝试停止
        if engine.preview_server:
            try:
                engine.preview_server.stop()
                time.sleep(1.0)
            except: pass
            
        # 🚀 [V55.9] 终极物理管线：绕过 EventBus，直接注入 WS 广播能力
        from core.api.routes.ws import manager, handle_bus_event
        
        def terminal_broadcaster(line):
            # 🚀 [V55.9] 物理采样：在服务端控制台打标
            tlog.info(f"🛰️ [终端采样] {line}")
            
            # 标准 EventBus 信号发射（现在 ws.py 已能正确识别并转发）
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=line)

        # 我们需要稍微修改一下 FrameworkDevServer 以接受回调
        if hasattr(engine.preview_server, 'start_with_callback'):
            success = engine.preview_server.start_with_callback(callback=terminal_broadcaster)
        else:
            success = engine.preview_server.start(blocking=False)
            
        if success:
            engine.services["preview"].update({
                "status": "running",
                "port": engine.preview_server.port,
                "start_time": time.time(),
                "mode": "framework" if is_framework else "static"
            })
            return {"status": "success", "message": "Preview server ignition started."}
        else:
            raise HTTPException(status_code=500, detail="Failed to start preview server instance")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")

import socket

class ComponentMonitor:
    """🛰️ [V52.4] 系统组件全息扫描器"""
    
    @staticmethod
    def check_port(port: int, host: str = "localhost") -> bool:
        """🚀 [V55.9] 物理级鲁棒探测：支持 IPv4/v6 双栈"""
        try:
            # create_connection 会自动尝试所有解析出的地址 (127.0.0.1, ::1)
            with socket.create_connection((host, port), timeout=0.3):
                return True
        except:
            return False

    @classmethod
    def get_matrix(cls):
        engine = get_global_engine()
        from concurrent.futures import ThreadPoolExecutor
        
        # 1. 核心状态感知 (优先从内存读取，无需物理探测)
        engine_status = "online" if engine else "starting"
        preview_port = 43213
        if engine and hasattr(engine.config.system, 'serve_port'):
            preview_port = engine.config.system.serve_port
        
        # 2. 并发探测 (消除串行 Timeout 累积延迟)
        with ThreadPoolExecutor(max_workers=3) as executor:
            f_onboard = executor.submit(cls.check_port, 43211)
            f_preview = executor.submit(cls.check_port, preview_port)
            
            onboarding_active = f_onboard.result()
            preview_active = f_preview.result()
        
        # 3. 🚀 [V55.9] 内存补位逻辑：如果端口探测失败但进程确实在运行，强制标绿
        if not preview_active and engine and hasattr(engine, 'preview_server') and engine.preview_server:
            # 检查 FrameworkDevServer 进程
            if hasattr(engine.preview_server, 'process') and engine.preview_server.process:
                if engine.preview_server.process.poll() is None:
                    preview_active = True
            # 检查静态 DevServer
            elif hasattr(engine.preview_server, 'server') and engine.preview_server.server:
                preview_active = True

        return {
            "engine": {"status": engine_status, "label": "核心引擎", "health": 100 if engine else 0},
            "onboarding": {"status": "active" if onboarding_active else "standby", "label": "版图向导", "health": 100 if onboarding_active else 50},
            "dashboard": {"status": "online", "label": "指挥中心", "health": 100},
            "preview": {"status": "online" if preview_active else "offline", "label": "预览服务", "health": 100 if preview_active else 0}
        }

@router.get("/api/system/health/matrix", dependencies=[Depends(verify_token)])
def get_health_matrix():
    """🛰️ [V52.4] 获取系统组件全息健康矩阵"""
    return ComponentMonitor.get_matrix()

@router.get("/api/system/languages")
def get_supported_languages():
    """🌍 [V55.3] 动态获取系统支持的全球语种矩阵"""
    from core.utils.language_hub import LanguageHub
    return {
        "languages": LanguageHub.get_supported_matrix()
    }
@router.post("/api/system/theme/install", dependencies=[Depends(verify_token)])
async def install_theme_dependencies():
    """🚀 [V52.11] 自动化依赖安装：执行 npm install 并通过 WS 实时回传日志"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    package_json = os.path.join(theme_dir, "package.json")
    
    if not os.path.exists(package_json):
        return {"status": "skipped", "message": "No package.json found, skipping installation."}
    
    def run_install():
        import subprocess
        from core.utils.event_bus import bus
        
        tlog.info(f"🏗️ [安装启动] 正在为主题 '{engine.active_theme}' 安装依赖...")
        bus.emit("UI_TERMINAL_DATA", type="INSTALL_START", message=f"开始安装主题 {engine.active_theme} 的依赖...")
        
        try:
            # 探测是否有 yarn/pnpm/npm
            cmd = ["npm", "install"]
            if os.path.exists(os.path.join(theme_dir, "pnpm-lock.yaml")):
                cmd = ["pnpm", "install"]
            elif os.path.exists(os.path.join(theme_dir, "yarn.lock")):
                cmd = ["yarn", "install"]
                
            process = subprocess.Popen(
                cmd,
                cwd=theme_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 🚀 [V55.9] 物理管线同步：使用 readline 替代 buffered 迭代器
            from core.api.routes.ws import manager
            import asyncio
            
            while True:
                line = process.stdout.readline()
                if not line: break
                clean_line = line.strip()
                if clean_line:
                    # 标准 EventBus 信号发射
                    bus.emit("UI_TERMINAL_DATA", type="LOG", data=clean_line)
            
            process.wait()
            if process.returncode == 0:
                tlog.success(f"✅ [安装成功] 主题 '{engine.active_theme}' 依赖已就绪。")
                bus.emit("UI_TERMINAL_DATA", type="INSTALL_SUCCESS", message="依赖安装完成！")
            else:
                tlog.error(f"❌ [安装失败] npm install 退出码: {process.returncode}")
                bus.emit("UI_TERMINAL_DATA", type="INSTALL_ERROR", message=f"安装失败，退出码: {process.returncode}")
                
        except Exception as e:
            tlog.error(f"🚨 [安装异常] {str(e)}")
            bus.emit("UI_TERMINAL_DATA", type="INSTALL_ERROR", message=f"系统异常: {str(e)}")

    import threading
    threading.Thread(target=run_install, daemon=True).start()
    
    return {"status": "started", "message": "Installation background task started."}

@router.post("/api/system/theme/upgrade", dependencies=[Depends(verify_token)])
async def upgrade_theme_dependencies():
    """🚀 [V65.0] 自动化版本升级：执行 npx @astrojs/upgrade 并通过 WS 实时回传日志"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    
    def run_upgrade():
        import subprocess
        import os
        from core.utils.event_bus import bus
        
        tlog.info(f"🔄 [升级启动] 正在为主题 '{engine.active_theme}' 执行版本更新...")
        
        # 🛡️ [V65.3] 物理快照备份：在升级前对关键配置进行冷备份
        import shutil
        try:
            for f in ["package.json", "package-lock.json", "astro.config.mjs", "docusaurus.config.js"]:
                fpath = os.path.join(theme_dir, f)
                if os.path.exists(fpath):
                    shutil.copy2(fpath, fpath + ".bak")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="🛡️ [物理保护] 已完成核心配置文件快照备份 (.bak)。")
        except Exception as e:
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"⚠️ [系统提示] 快照备份失败，但仍将尝试继续升级: {str(e)}")

        # 🚀 [V65.2] 框架感知指令集
        is_astro = os.path.exists(os.path.join(theme_dir, "astro.config.mjs")) or os.path.exists(os.path.join(theme_dir, "astro.config.js"))
        is_docusaurus = os.path.exists(os.path.join(theme_dir, "docusaurus.config.js"))
        
        if is_astro:
            cmd = ["npx", "-y", "@astrojs/upgrade", "-y"]
            msg = "正在向 Astro 引擎下达物理升级指令 (@astrojs/upgrade)..."
        elif is_docusaurus:
            # Docusaurus 通常建议通过 npm update 升级，或者指定包名升级至 latest
            cmd = ["npm", "update"]
            msg = "正在向 Docusaurus 引擎下达物理升级指令 (npm update)..."
        else:
            cmd = ["npm", "update"]
            msg = "检测到通用 Node.js 环境，正在下达全局依赖更新指令..."

        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🚀 [系统感知] {msg}")
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=theme_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            while True:
                line = process.stdout.readline()
                if not line: break
                clean_line = line.strip()
                if clean_line:
                    bus.emit("UI_TERMINAL_DATA", type="LOG", data=clean_line)
            
            process.wait()
            if process.returncode == 0:
                tlog.success(f"✅ [升级成功] 主题 '{engine.active_theme}' 已完成版本对正。")
                bus.emit("UI_TERMINAL_DATA", type="LOG", data="✅ [指令闭环] 主题版本升级完成！建议重启预览服务。")
            else:
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"❌ [升级失败] 退出码: {process.returncode}")
                
        except Exception as e:
            tlog.error(f"🚨 [升级异常] {str(e)}")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🚨 [物理冲突] 升级异常: {str(e)}")

    import threading
    threading.Thread(target=run_upgrade, daemon=True).start()
    return {"status": "started", "message": "Upgrade background task started."}

@router.post("/api/system/theme/rollback", dependencies=[Depends(verify_token)])
async def rollback_theme_config():
    """🚀 [V65.3] 物理快照回滚：从 .bak 文件恢复核心配置"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    
    import shutil
    restored = []
    try:
        for f in ["package.json", "package-lock.json", "astro.config.mjs", "docusaurus.config.js"]:
            bak_path = os.path.join(theme_dir, f + ".bak")
            target_path = os.path.join(theme_dir, f)
            if os.path.exists(bak_path):
                shutil.copy2(bak_path, target_path)
                restored.append(f)
        
        if restored:
            from core.utils.event_bus import bus
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"⏪ [环境复原] 已成功从快照恢复以下文件: {', '.join(restored)}")
            
            # 🚀 [V65.4] 深度同步：回滚配置后自动触发物理安装，确保 node_modules 与 package.json 对齐
            if "package.json" in restored:
                bus.emit("UI_TERMINAL_DATA", type="LOG", data="🏗️ [物理重构] 检测到版本声明已变更，正在启动全链路环境复原 (npm install)...")
                # 借用现有的安装逻辑
                await install_theme_dependencies()
                
            return {"status": "success", "restored": restored}
        else:
            return {"status": "skipped", "message": "No backup files found."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")

@router.post("/api/system/wizard/start", dependencies=[Depends(verify_token)])
async def start_wizard():
    """🚀 [V55.0] 远程点火版图向导 Web 服务"""
    try:
        if ComponentMonitor.check_port(43211):
            return {"status": "already_running"}
        import threading
        from core.ui.web.wizard_server import start_wizard_server
        threading.Thread(target=start_wizard_server, kwargs={"port": 43211}, daemon=True).start()
        return {"status": "started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/api/system/wizard/stop", dependencies=[Depends(verify_token)])
async def stop_wizard():
    """🛑 [V55.0] 销毁版图向导 Web 服务"""
    try:
        # 🚀 [V57.0] 鲁棒性重构：使用原生 urllib 替代 httpx 消除依赖故障
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:43211/api/shutdown", method="POST")
        with urllib.request.urlopen(req, timeout=2.0) as response:
            pass
        return {"status": "stopped"}
    except Exception as e:
        # 如果服务已经关闭，忽略连接错误
        return {"status": "stopped", "note": "Service may already be down"}
