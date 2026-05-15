
from core.config.config import load_config
try:
    class DummyArgs:
        config = "config.yaml"
        imprint = "testniu"
    config = load_config("config.yaml", imprint_id="testniu")
    from core.runtime.engine_factory import EngineFactory
    new_engine = EngineFactory.create_engine(config, args=DummyArgs(), imprint_id="testniu")
    print("Engine created successfully")
except Exception:
    import traceback
    traceback.print_exc()

