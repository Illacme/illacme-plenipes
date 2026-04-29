import os
import sys

# 注入核心路径
sys.path.append(os.path.abspath('.'))

from core.runtime.engine import IllacmeEngine
from core.runtime.engine_factory import EngineFactory

def debug_masking():
    # 使用主权配置加载引擎
    config_path = "config.sovereign.yaml"
    engine = IllacmeEngine(config_path)
    EngineFactory.assemble_components(engine, config_path)
    
    # 模拟处理流程
    rel_path = "Docs/Sovereignty_Test.md"
    src_abs = os.path.join(engine.paths.get('vault', '.'), rel_path)
    
    with open(src_abs, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 构造全量匿名 Context
    ctx = type('Context', (), {
        'engine': engine,
        'services': engine,
        'rel_path': rel_path,
        'src_path': src_abs,
        'raw_content': content,
        'body_content': content,
        'masked_source': content,
        'masks': [],
        'node_outlinks': set(),
        'node_assets': set(),
        'node_ext_assets': set(),
        'assets_lock': None,
        'is_aborted': False,
        'is_silent_edit': False,
        'force_sync': True, # 🚀 [调试需求] 强制同步
        'title': "Sovereignty Test",
        'slug': "sovereignty-test",
        'route_prefix': "docs",
        'route_source': "Docs",
        'mapped_sub_dir': "",
        'base_fm': {},
        'ai_health_flag': [True]
    })
    
    # 物理执行管线
    print(f"--- STARTING PIPELINE EXECUTION ---")
    engine.pipeline.execute(ctx)
    print(f"--- PIPELINE EXECUTION COMPLETE ---")
    
    print("\n[DEBUG] Mask Pattern in Config:", engine.config.system.mask_pattern)
    
    print("\n[DEBUG] Masked Source sent to AI (Snippet):")
    if "[[STB_MASK_" in ctx.masked_source:
        print("✅ SUCCESS: Found mask placeholders in source.")
    else:
        print("❌ FAILURE: No mask placeholders found!")
        
    print("\nFull Masked Body:")
    print(ctx.masked_source)
    
    print("\n[DEBUG] Collected Masks Count:", len(ctx.masks))
    for i, m in enumerate(ctx.masks):
        print(f"  Mask {i}: {m}")

if __name__ == "__main__":
    debug_masking()
