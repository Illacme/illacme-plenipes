from core.runtime.engine_singleton import get_global_engine
import socket

class SystemFragment:
    @staticmethod
    def check_port(port: int) -> bool:
        """主权探针：探测指定端口是否已物理激活"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(('127.0.0.1', port)) == 0
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
            f_onboard = executor.submit(cls.check_port, 43210)
            f_preview = executor.submit(cls.check_port, preview_port)
            
            onboarding_active = f_onboard.result()
            preview_active = f_preview.result()

        return {
            "engine": {"status": engine_status, "label": "核心引擎", "health": 100 if engine else 0},
            "onboarding": {"status": "active" if onboarding_active else "standby", "label": "引导配置服务", "health": 100 if onboarding_active else 50},
            "preview": {"status": "running" if preview_active else "offline", "label": "预览服务", "health": 100 if preview_active else 0},
            "dashboard": {"status": "healthy", "label": "指挥中心 (Dashboard)", "health": 100}
        }
