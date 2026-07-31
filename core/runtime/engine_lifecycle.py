# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Illacme-plenipes Engine Lifecycle & Reload Protocols
职责：负责引擎的深度重载 (Deep Reload)、主权迁移及资源消杀。
架构：已按 SOP-04 执行物理降解，实现生命周期逻辑的原子化隔离。
"""

import os
import yaml
from core.utils.tracing import tlog
from core.config.config import CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME
from .engine_singleton import (
    get_global_engine, set_global_engine,
    get_global_args, set_global_args,
    get_global_observer, set_global_observer
)

def deep_reload_imprint(imprint_id: str):
    """🚀 [V52.6] 深度主权迁移：全量重载引擎、配置与监控管线"""
    _GLOBAL_ENGINE = get_global_engine()
    _GLOBAL_ARGS = get_global_args()
    _GLOBAL_OBSERVER = get_global_observer()
    
    if not _GLOBAL_ARGS:
        tlog.error("🛑 [重载失败] 无法定位原始启动参数，主权迁移中止。")
        return False
        
    tlog.info(f"🛰️ [主权迁移] 正在启动深度重载流水线 (Target Imprint: {imprint_id})...")
    
    # 🚀 [V65.6] 物理闭环：在重载前，必须先强制注销旧引擎的所有治理守卫 (特别是哨兵)
    if _GLOBAL_ENGINE and hasattr(_GLOBAL_ENGINE, 'governance'):
        try:
            _GLOBAL_ENGINE.governance.shutdown()
        except: pass
        
    # 🚀 [V65.8] 同步注销：销毁全局文件监控器，防止幽灵同步
    if _GLOBAL_OBSERVER:
        try:
            tlog.info("🐕 [主权迁移] 正在注销旧有的同步守护进程...")
            _GLOBAL_OBSERVER.stop()
            _GLOBAL_OBSERVER.join(timeout=1.0)
            set_global_observer(None)
        except: pass

    try:
        # 1. 优先校验并实例化新版图配置与引擎（物理原子性：预检失败则绝不更新 config.local.yaml）
        from core.config.config import ConfigManager
        config_path = _GLOBAL_ARGS.config
        manager = ConfigManager(config_path, imprint_id=imprint_id)
        config = manager.config
        
        # 2. 调用工厂组装新引擎
        from core.runtime.engine_factory import EngineFactory
        new_engine = EngineFactory.create_engine(config, args=_GLOBAL_ARGS, imprint_id=imprint_id)
        new_engine.config_manager = manager

        if not new_engine:
            tlog.error("🛑 [重载失败] 引擎工厂组装失败。")
            return False

        # 3. 预检与组装全成功后，安全更新 Local 缓存中的激活版图
        try:
            local_path = CONFIG_LOCAL_NAME
            existing_local = {}
            if os.path.exists(local_path):
                with open(local_path, "r", encoding="utf-8") as f:
                    existing_local = yaml.safe_load(f) or {}
            
            # 🚀 [V55.10] 主权迁移保障：确保在消杀前将关键路径固化到版图层
            if imprint_id != "default":
                target_imprint_yaml = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(target_imprint_yaml):
                    with open(target_imprint_yaml, "r", encoding="utf-8") as f:
                        target_cfg = yaml.safe_load(f) or {}
                    
                    # 如果版图内缺失 vault_root，则从当前 local 补全
                    if not target_cfg.get("vault_root") and existing_local.get("vault_root"):
                        target_cfg["vault_root"] = existing_local["vault_root"]
                        from core.utils.common import promote_config_keys
                        target_cfg = promote_config_keys(target_cfg)
                        with open(target_imprint_yaml, "w", encoding="utf-8") as f:
                            yaml.safe_dump(target_cfg, f, allow_unicode=True)
                        tlog.debug(f"🏗️ [主权固化] 已将金库路径迁移至版图配置: {imprint_id}")

            # 🚀 [V65.1] 物理主权对正：仅安全更新活跃品牌标识 active_imprint。
            existing_local["active_imprint"] = imprint_id
            if "system" in existing_local and isinstance(existing_local["system"], dict):
                if "data_root" in existing_local["system"]:
                    del existing_local["system"]["data_root"]
                if not existing_local["system"]:
                    del existing_local["system"]

            from core.utils.common import promote_config_keys
            existing_local = promote_config_keys(existing_local)
            with open(local_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(existing_local, f, allow_unicode=True)
            tlog.success(f"🛡️ [物理对齐] 已安全更新 Local 缓存中的激活版图为 '{imprint_id}'。")
        except Exception as ex:
            tlog.warning(f"⚠️ [物理消杀失败] {ex}")
            
        # 3. 注册新引擎 (自动清理旧哨兵)
        set_global_engine(new_engine)
        
        # 4. 🚀 [V52.6] 日志管线对正
        from core.utils import setup_logger
        setup_logger(new_engine.paths["logs"])
        
        # 5. 如果开启了 Watch 模式，重新激活看门狗
        if _GLOBAL_ARGS.watch:
            from core.runtime.daemon import start_watchdog
            from core.runtime.orchestrator import prepare_sync_tasks
            
            _, current_files = prepare_sync_tasks(new_engine, requested_paths=_GLOBAL_ARGS.path)
            
            # 启动新监听器
            new_observer, _ = start_watchdog(new_engine, _GLOBAL_ARGS, current_files)
            set_global_observer(new_observer)
            
        tlog.success(f"✅ [迁移完成] 出版版图已成功切换至 '{imprint_id}'，物理主权已全面对正。")
        return True
        
    except Exception as e:
        tlog.error(f"🛑 [迁移异常] 致命错误: {e}")
        raise e
