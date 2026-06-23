#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [Test] AuditLedger Concurrency & Lock Resilience Test
职责：在高负载并发写入场景下验证 AuditLedger 的线程安全与零锁阻碍设计。
"""
import os
import tempfile
import threading
from core.governance.audit_ledger import AuditLedger

def test_audit_ledger_concurrency_robustness():
    """🧪 模拟 20 个线程并发对 AuditLedger 进行高密写入，验证重入锁和连接优化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "audit_test.db")
        ledger = AuditLedger(db_path)
        
        errors = []
        threads = []
        num_threads = 20
        writes_per_thread = 20
        
        def worker(thread_idx):
            for i in range(writes_per_thread):
                try:
                    ledger.log(
                        event_type="AI_TRANSACTION",
                        details=f"Thread {thread_idx} log entry {i}",
                        imprint_id="test_brand",
                        metadata={"cost": 0.0015, "tokens": 120}
                    )
                except Exception as e:
                    errors.append(e)
                    
        # 启动并发写入线程
        for idx in range(num_threads):
            t = threading.Thread(target=worker, args=(idx,))
            threads.append(t)
            
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        # 验证零 OperationalError: database is locked 异常
        assert len(errors) == 0, f"并发写入期间抛出异常: {errors}"
        
        # 验证数据完整性
        logs = ledger.export_report(imprint_id="test_brand")
        assert len(logs) == num_threads * writes_per_thread, f"预期日志数 {num_threads * writes_per_thread}，实际数 {len(logs)}"
        
        # 验证财务聚合查询的线程安全与准确性
        total_cost = ledger.get_total_cost(imprint_id="test_brand")
        expected_cost = num_threads * writes_per_thread * 0.0015
        assert abs(total_cost - expected_cost) < 1e-6, f"预期开销 {expected_cost}，实际开销 {total_cost}"
        
        today_cost = ledger.get_today_cost(imprint_id="test_brand")
        assert abs(today_cost - expected_cost) < 1e-6, "今日开销聚合有误"
        
        weekly_stats = ledger.get_weekly_stats(imprint_id="test_brand")
        assert len(weekly_stats) > 0, "周开销趋势查询有误"
