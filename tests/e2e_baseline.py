#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - 物理防退化基线哨兵 (E2E Baseline Sentinel)
用途：在重构期间，验证重构前后的物理产物是否保持绝对的字节级一致。
"""

import os
import hashlib
import json
import sys

def calculate_dir_hash(directory):
    """自底向上计算目录下所有文件的聚合 MD5 指纹"""
    if not os.path.exists(directory):
        return None
        
    file_hashes = {}
    for root, _, files in os.walk(directory):
        for f in files:
            # 排除可能因时间戳波动的临时文件或日志
            if f.endswith('.tmp') or f.endswith('.log'):
                continue
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'rb') as file:
                    file_hashes[filepath] = hashlib.md5(file.read()).hexdigest()
            except Exception as e:
                print(f"无法读取文件 {filepath}: {e}")
                
    # 对路径进行排序后混合计算全局哈希，确保路径和内容的双重一致性
    sorted_keys = sorted(file_hashes.keys())
    global_hash = hashlib.md5("".join([file_hashes[k] for k in sorted_keys]).encode('utf-8')).hexdigest()
    return {"global_hash": global_hash, "file_count": len(file_hashes), "details": file_hashes}

def main():
    # 替换为你 config.yaml 中的实际前端输出路径
    output_md_dir = "./themes/starlight/src/content/docs"
    output_assets_dir = "./themes/starlight/public/assets"
    baseline_file = "tests/baseline_snapshot.json"
    
    os.makedirs("tests", exist_ok=True)
    
    current_state = {
        "docs_hash": calculate_dir_hash(output_md_dir),
        "assets_hash": calculate_dir_hash(output_assets_dir)
    }
    
    if '--record' in sys.argv:
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(current_state, f, indent=2)
        print("📸 [基线固化] 黄金快照已生成！请开始你的重构表演。")
    elif '--verify' in sys.argv:
        if not os.path.exists(baseline_file):
            print("🛑 找不到黄金快照，请先运行 python tests/e2e_baseline.py --record")
            sys.exit(1)
            
        with open(baseline_file, 'r', encoding='utf-8') as f:
            baseline_state = json.load(f)
            
        is_safe = True
        for key in ["docs_hash", "assets_hash"]:
            base = baseline_state.get(key)
            curr = current_state.get(key)
            if base and curr:
                if base["global_hash"] != curr["global_hash"]:
                    print(f"🚨 [退化警告] {key} 发生偏移！文件数 (基线:{base['file_count']} -> 当前:{curr['file_count']})")
                    is_safe = False
                else:
                    print(f"✅ [校验通过] {key} 字节级一致。")
                    
        if is_safe:
            print("🎉 重构安全！引擎输出与基线 100% 吻合。")
            sys.exit(0)
        else:
            print("🛑 发现物理退化，请立即回滚代码排查问题！")
            sys.exit(1)
    else:
        print("用法:\n  python tests/e2e_baseline.py --record  (重构前记录基线)\n  python tests/e2e_baseline.py --verify  (重构后验证基线)")

if __name__ == "__main__":
    main()
