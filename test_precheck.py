import os
import json
import asyncio
from core.runtime.engine_singleton import init_global_engine
from services.api.logic import sys_ops

async def main():
    engine = init_global_engine()
    print("Engine initialized. Vault root:", engine.vault_root)
    
    # Create a test file
    test_file = os.path.join(engine.vault_root, "Blog", "test_precheck.md")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("# Hello\n\n![missing](assets/missing_image_for_test.png)\n")
        
    print("Created test file. Running precheck...")
    res = sys_ops.run_precheck_logic(engine)
    print("Precheck result:", json.dumps(res, ensure_ascii=False, indent=2))
    
    # Clean up
    os.remove(test_file)

if __name__ == "__main__":
    asyncio.run(main())
