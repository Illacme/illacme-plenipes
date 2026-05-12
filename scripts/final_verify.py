import requests
import os
import yaml
import json

TOKEN = "YOUR_TOKEN"
API_URL = "http://127.0.0.1:43212/api/config/update"
NODES_URL = "http://127.0.0.1:43212/api/compute/nodes"
IMPRINT_CFG = "imprints/stellar_harbor/configs/config.imprint.yaml"
LOCAL_CFG = "config.local.yaml"

def final_audit():
    print("🎯 [终极全链路验证]")
    
    # 1. 识别目标
    p_node = "lmstudio_local"
    new_model = f"final-verify-{int(os.times()[4])}"
    
    # 2. 执行原子更新
    payload = {
        f"translation.compute_nodes.{p_node}.model": new_model,
        "translation.primary_model": new_model
    }
    requests.post(API_URL, headers={"X-Token": TOKEN}, json=payload)
    
    # 3. 物理层校验 (磁盘)
    with open(IMPRINT_CFG, 'r') as f:
        imp = yaml.safe_load(f)
    with open(LOCAL_CFG, 'r') as f:
        loc = yaml.safe_load(f)
        
    p_strat = imp.get('translation', {}).get('primary_model')
    p_phys = loc.get('translation', {}).get('compute_nodes', {}).get(p_node, {}).get('model')
    
    print(f"  └── 💾 策略层固化: {p_strat}")
    print(f"  └── 💾 物理层固化: {p_phys}")
    
    # 4. 渲染层校验 (API)
    res = requests.get(NODES_URL, headers={"X-Token": TOKEN}).json()
    card = next((n for n in res['nodes'] if n['id'] == p_node), None)
    api_val = card.get('model') if card else 'N/A'
    print(f"  └── 🃏 API 渲染输出: {api_val}")
    
    if p_strat == new_model and p_phys == new_model and api_val == new_model:
        print("\n✅ [验证成功] 物理、策略与渲染层已达成三位一体同步！")
    else:
        print("\n❌ [验证失败] 仍存在物理层级脱节。")

if __name__ == "__main__":
    final_audit()
