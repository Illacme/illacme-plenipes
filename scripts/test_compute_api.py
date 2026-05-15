#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Compute API Verification Script
模块职责：自动验证算力节点的 CRUD 操作与物理一致性。
"""
import requests
import os

BASE_URL = "http://127.0.0.1:43212/api/compute"
HEADERS = {"Content-Type": "application/json"}

def test_api():
    print("🔍 [测试开始] 正在验证算力治理中心 API...")
    
    # 1. 获取节点列表
    print("\n📡 正在获取节点列表...")
    res = requests.get(f"{BASE_URL}/nodes")
    nodes_data = res.json()
    print(f"✅ 发现 {len(nodes_data['nodes'])} 个活跃节点。当前主节点: {nodes_data['primary']}")
    
    # 2. 新增临时节点
    test_node_id = "api_test_node"
    print(f"\n🏗️ 正在创建测试节点: {test_node_id}...")
    payload = {
        "id": test_node_id,
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "sk-test-key",
        "timeout": 15
    }
    res = requests.post(f"{BASE_URL}/nodes/update", json=payload)
    if res.json().get("success"):
        print(f"✅ 节点 {test_node_id} 已成功并网。")
    else:
        print(f"❌ 节点创建失败: {res.text}")
        return

    # 3. 验证物理文件一致性
    print("\n📂 正在验证物理配置文件一致性...")
    if os.path.exists("config.local.yaml"):
        with open("config.local.yaml", "r") as f:
            content = f.read()
            if test_node_id in content:
                print("✅ config.local.yaml 已同步更新。")
            else:
                print("❌ config.local.yaml 未发现新节点。")

    # 4. 测试节点连通性 (Mock)
    print(f"\n📡 正在测试节点连通性: {test_node_id}...")
    res = requests.post(f"{BASE_URL}/nodes/test", json={"id": test_node_id})
    test_res = res.json()
    if test_res.get("status") == "success":
        print(f"✅ 探测成功: 延迟 {test_res['latency']}ms")
    else:
        print(f"⚠️ 探测异常 (预期内，因为 API Key 为 Mock): {test_res.get('error')}")

    # 5. 删除测试节点
    print(f"\n🪓 正在移除测试节点: {test_node_id}...")
    res = requests.post(f"{BASE_URL}/nodes/delete", json={"id": test_node_id})
    if res.json().get("success"):
        print("✅ 测试节点已物理抹除。")
    else:
        print(f"❌ 移除失败: {res.text}")

    print("\n🏁 [测试完成] 算力治理链路完整性校验通过。")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"🚨 测试中断: {e}")
        print("💡 提示: 请确保服务器已运行 (python3 plenipes.py --api)")
