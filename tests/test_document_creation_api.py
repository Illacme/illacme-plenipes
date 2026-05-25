#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [Test] 物理原稿安全新建 RESTful API 单元测试
职责：全面覆盖 /ledger/document/create 端点的创建、重名校验、与路径穿越拦截逻辑。
"""
import sys
import os
import tempfile
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app

# 构造 Mock 引擎和元数据管理器
class MockSystemConfig:
    def __init__(self):
        self.api_token = None # 绕过 token 校验以便测试

class MockConfig:
    def __init__(self):
        self.system = MockSystemConfig()

class MockSQLiteBackend:
    def __init__(self):
        self.registry = {}

    def get_document(self, rel_path):
        return self.registry.get(rel_path)

    def upsert_document(self, rel_path, data):
        self.registry[rel_path] = data

class MockMetadataManager:
    def __init__(self):
        self.sqlite = MockSQLiteBackend()
        self.registry = {}

    def register_document(self, rel_path, title, **kwargs):
        self.registry[rel_path] = {
            "title": title,
            "slug": kwargs.get("slug"),
            **kwargs
        }

    def remove_document(self, rel_path):
        if rel_path in self.registry:
            del self.registry[rel_path]

    def get_doc_info(self, rel_path):
        return self.registry.get(rel_path) or {}

class MockEngine:
    def __init__(self, vault_root):
        self.vault_root = vault_root
        self.meta = MockMetadataManager()
        self.config = MockConfig()

def test_document_creation_flow():
    print("🧪 [Test] 启动原稿物理新建及安全防御单元测试...")
    
    with tempfile.TemporaryDirectory() as temp_vault:
        # 1. 实例化 Mock 引擎并注入单例
        mock_engine = MockEngine(temp_vault)
        
        # 物理注入到全局单例（用于 api server 的 get_global_engine）
        import core.runtime.engine_singleton as singleton
        original_engine = singleton.get_global_engine()
        singleton.set_global_engine(mock_engine)
        
        client = TestClient(app)
        
        try:
            # 2. 正常场景：在子目录下创建原稿
            payload = {
                "doc_id": "blog/fresh-post",
                "title": "我的新鲜创作"
            }
            res = client.post("/ledger/document/create", json=payload)
            assert res.status_code == 200, "API 状态响应非 200"
            data = res.json()
            assert data.get("success") is True, f"创建失败: {data.get('error')}"
            assert data.get("doc_id") == "blog/fresh-post.md", "物理文件名后缀未正确补足为 .md"
            
            # 验证物理文件真的在临时文库中生成
            physical_file = os.path.join(temp_vault, "blog/fresh-post.md")
            assert os.path.exists(physical_file), "物理原稿文件未在磁盘中创建"
            
            with open(physical_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "我的新鲜创作" in content, "初始标题未被缝合写入文件"
                assert "slug: fresh-post" in content, "默认 slug 未被正确注入 YAML"
                
            # 验证 SQLite 索引是否完成入库注册
            registered_data = mock_engine.meta.registry.get("blog/fresh-post.md")
            assert registered_data is not None, "元数据索引未同步入库"
            assert registered_data["title"] == "我的新鲜创作", "注册的标题不符"
            
            print("  ✅ [测试] 正常新建物理流程与 Frontmatter 自动缝合完美通过！")
            
            # 3. 冲突场景：重名拦截
            res_conflict = client.post("/ledger/document/create", json=payload)
            assert res_conflict.status_code == 200
            data_conflict = res_conflict.json()
            assert data_conflict.get("success") is not True, "未能阻止重复同名文件的创建"
            assert "已存在" in data_conflict.get("error"), f"非预期的重名拦截提示: {data_conflict.get('error')}"
            print("  ✅ [测试] 物理重名防覆盖校验顺利通过！")
            
            # 4. 安全场景：路径穿越恶意阻断 (L3 级防御)
            payload_bypass = {
                "doc_id": "../../../etc/passwd",
                "title": "穿越测试"
            }
            res_bypass = client.post("/ledger/document/create", json=payload_bypass)
            assert res_bypass.status_code == 200
            data_bypass = res_bypass.json()
            assert data_bypass.get("success") is not True, "未能有效防御路径穿越穿越漏洞"
            assert "非法的物理路径穿越" in data_bypass.get("error"), f"非预期的安全拦截报错: {data_bypass.get('error')}"
            
            passwd_file_in_vault = os.path.join(temp_vault, "../../../etc/passwd.md")
            assert not os.path.exists(passwd_file_in_vault), "穿越文件违规被物理写入"
            print("  ✅ [测试] L3 级防路径穿越（Directory Traversal）安全拦截高分通过！")
            
            # ===== 新建目录（Directory Creation）单元测试 =====
            print("🧪 [Test] 启动目录新建物理流程及防御单元测试...")
            
            # 1. 正常场景：在子目录下新建文件夹
            res_dir = client.post("/ledger/directory/create", json={"dir_id": "posts/life/cooking"})
            assert res_dir.status_code == 200
            data_dir = res_dir.json()
            assert data_dir.get("success") is True, f"物理目录创建失败: {data_dir.get('error')}"
            assert data_dir.get("dir_id") == "posts/life/cooking"
            
            # 验证物理目录是否在磁盘生成
            physical_dir = os.path.join(temp_vault, "posts/life/cooking")
            assert os.path.isdir(physical_dir), "物理文件夹未在磁盘中创建"
            print("  ✅ [测试] 正常物理目录创建完美通过！")
            
            # 2. 冲突场景：重名拦截
            res_dir_conflict = client.post("/ledger/directory/create", json={"dir_id": "posts/life/cooking"})
            assert res_dir_conflict.status_code == 200
            data_dir_conflict = res_dir_conflict.json()
            assert data_dir_conflict.get("success") is not True, "未能阻止重复同名物理目录的创建"
            assert "已存在" in data_dir_conflict.get("error"), f"非预期的重名目录拦截提示: {data_dir_conflict.get('error')}"
            print("  ✅ [测试] 物理目录重复创建冲突校验通过！")
            
            # 3. 安全场景：路径穿越恶意阻断 (L3 级防御)
            res_dir_bypass = client.post("/ledger/directory/create", json={"dir_id": "../../../var/log/baddir"})
            assert res_dir_bypass.status_code == 200
            data_dir_bypass = res_dir_bypass.json()
            assert data_dir_bypass.get("success") is not True, "目录新建接口未能防御路径穿越漏洞"
            assert "非法的物理路径穿越" in data_dir_bypass.get("error"), f"非预期的安全拦截报错: {data_dir_bypass.get('error')}"
            
            bad_dir_in_system = os.path.join(temp_vault, "../../../var/log/baddir")
            assert not os.path.exists(bad_dir_in_system), "穿越文件夹违规被物理写入"
            print("  ✅ [测试] L3 级防路径穿越创建目录安全拦截顺利通过！")
            
            # ===== 安全删除目录（Safe Directory Deletion）单元测试 =====
            print("🧪 [Test] 启动安全删除空目录及非空防线拦截单元测试...")
            
            # 1. 正常场景：删除已建好的空目录 posts/life/cooking
            res_del_ok = client.post("/ledger/directory/delete", json={"dir_id": "posts/life/cooking"})
            assert res_del_ok.status_code == 200
            data_del_ok = res_del_ok.json()
            assert data_del_ok.get("success") is True, f"正常空目录删除失败: {data_del_ok.get('error')}"
            assert not os.path.exists(physical_dir), "空文件夹未从物理磁盘清除"
            print("  ✅ [测试] 正常物理空目录安全删除流程顺利通过！")
            
            # 2. 拦截场景：目录下存有原稿资产时拒绝删除
            # 先重新建立 posts/life/cooking 并往里塞一个临时原稿
            os.makedirs(physical_dir, exist_ok=True)
            dummy_file = os.path.join(physical_dir, "recipe.md")
            with open(dummy_file, 'w', encoding='utf-8') as f:
                f.write("# 食谱\n\n测试非空保护拦截。")
                
            res_del_fail = client.post("/ledger/directory/delete", json={"dir_id": "posts/life/cooking"})
            assert res_del_fail.status_code == 200
            data_del_fail = res_del_fail.json()
            assert data_del_fail.get("success") is not True, "未能成功拦截非空文件夹的物理删除！数据面临丢失风险！"
            assert "包含原稿" in data_del_fail.get("error"), f"非预期的非空保护报错提示: {data_del_fail.get('error')}"
            assert os.path.exists(dummy_file), "非空保护失效：物理子资产被强行移除！"
            print("  ✅ [测试] 钢铁级非空防护拦截高分通过！物理原稿资产绝对安全！")
            
            # 3. 拦截场景：防止跨盘穿越删除越权攻击
            res_del_bypass = client.post("/ledger/directory/delete", json={"dir_id": "../../../var/log/baddir"})
            assert res_del_bypass.status_code == 200
            data_del_bypass = res_del_bypass.json()
            assert data_del_bypass.get("success") is not True, "删除接口未能在路径穿越越权指令下进行防御拦截"
            assert "非法的物理路径穿越" in data_del_bypass.get("error"), f"非预期的安全删除拦截报错: {data_del_bypass.get('error')}"
            print("  ✅ [测试] L3 级防路径穿越恶意删除安全拦截顺利通过！")
            
            # 4. 拦截场景：防止删除文库根目录本身
            res_del_root = client.post("/ledger/directory/delete", json={"dir_id": "."})
            assert res_del_root.status_code == 200
            data_del_root = res_del_root.json()
            assert data_del_root.get("success") is not True, "未能在删除文库根目录指令下实施安全拦截"
            assert "不允许删除文库根目录" in data_del_root.get("error"), f"非预期的根目录删除拦截报错: {data_del_root.get('error')}"
            print("  ✅ [测试] 文库物理根目录误删安全防护拦截顺利通过！")
            
            # ===== 原稿平滑重命名与搬迁（Safe Rename & Move）单元测试 =====
            print("🧪 [Test] 启动原稿平滑重命名与物理搬迁安全拦截单元测试...")
            
            # 准备一个物理原稿
            old_doc_rel = "posts/life/cooking/old-recipe.md"
            old_doc_abs = os.path.join(temp_vault, old_doc_rel)
            with open(old_doc_abs, 'w', encoding='utf-8') as f:
                f.write("---\ntitle: 旧食谱\nslug: old-slug\n---\n# 旧正文")
                
            # 在 ledger 中注册该文档
            engine = singleton.get_global_engine()
            engine.meta.register_document(old_doc_rel, "旧食谱", slug="old-slug")
            
            # 1. 正常场景：同目录下文件名纯重命名
            res_rename = client.post("/ledger/document/move", json={
                "doc_id": old_doc_rel,
                "new_path": "new-recipe.md"
            })
            assert res_rename.status_code == 200
            data_rename = res_rename.json()
            assert data_rename.get("success") is True, f"同目录重命名失败: {data_rename.get('error')}"
            
            expected_new_rel = "posts/life/cooking/new-recipe.md"
            assert not os.path.exists(old_doc_abs), "旧物理文件依旧残留"
            assert os.path.exists(os.path.join(temp_vault, expected_new_rel)), "新物理文件未写入"
            
            # 验证 SQLite 元数据自动平滑迁移
            old_doc_info = engine.meta.get_doc_info(old_doc_rel)
            assert not old_doc_info, "旧 SQLite 账本索引没有注销"
            new_doc_info = engine.meta.get_doc_info(expected_new_rel)
            assert new_doc_info, "新 SQLite 账本索引未能平滑注册"
            assert new_doc_info.get("slug") == "old-slug", "元数据属性（如 slug）未能完美继承"
            print("  ✅ [测试] 正常同目录原稿重命名与账本平滑更新通过！")
            
            # 2. 正常场景：跨文件夹平滑移动
            dest_new_rel = "posts/tech/new-recipe-tech.md"
            res_move = client.post("/ledger/document/move", json={
                "doc_id": expected_new_rel,
                "new_path": dest_new_rel
            })
            assert res_move.status_code == 200
            data_move = res_move.json()
            assert data_move.get("success") is True, f"跨文件夹平滑移动失败: {data_move.get('error')}"
            assert not os.path.exists(os.path.join(temp_vault, expected_new_rel)), "移动后旧路径依旧留存"
            assert os.path.exists(os.path.join(temp_vault, dest_new_rel)), "跨文件夹移动后新路径物理文件不存在"
            
            # 验证新位置的元数据继承
            tech_doc_info = engine.meta.get_doc_info(dest_new_rel)
            assert tech_doc_info.get("slug") == "old-slug", "跨文件夹移动后元数据属性丢失"
            print("  ✅ [测试] 正常跨文件夹平滑移动与元数据继承通过！")
            
            # 2b. 场景：智能相对路径上一级（..）平滑搬迁与已有目录锚定验证
            parent_rel_dir = "posts"
            res_parent_move = client.post("/ledger/document/move", json={
                "doc_id": dest_new_rel,
                "new_path": "../"
            })
            assert res_parent_move.status_code == 200
            data_parent_move = res_parent_move.json()
            assert data_parent_move.get("success") is True, f"移到上一级目录失败: {data_parent_move.get('error')}"
            
            parent_expected_rel = "posts/new-recipe-tech.md"
            assert not os.path.exists(os.path.join(temp_vault, dest_new_rel)), "移到上一级后旧文件依然残留"
            assert os.path.exists(os.path.join(temp_vault, parent_expected_rel)), "移到上一级后物理文件不存在"
            
            # 更新为当前最新位置以便后续冲突测试使用
            dest_new_rel = parent_expected_rel
            print("  ✅ [测试] 智能相对路径上一级移动及目录自锚定通过！")
            
            # 3. 拦截场景：防同名文件覆盖冲突保护
            collision_file_rel = "posts/tech/collision.md"
            collision_file_abs = os.path.join(temp_vault, collision_file_rel)
            with open(collision_file_abs, 'w', encoding='utf-8') as f:
                f.write("# 冲突文件")
                
            res_collision = client.post("/ledger/document/move", json={
                "doc_id": dest_new_rel,
                "new_path": collision_file_rel
            })
            assert res_collision.status_code == 200
            data_collision = res_collision.json()
            assert data_collision.get("success") is not True, "未能成功拦截重名冲突覆盖，数据面临丢失危险！"
            assert "已有同名物理原稿" in data_collision.get("error"), f"非预期的重名冲突报错: {data_collision.get('error')}"
            print("  ✅ [测试] 原稿重名覆盖安全冲突拦截顺利通过！")
            
            # 4. 拦截场景：安全 L3 路径穿越攻击恶意搬迁拦截
            res_bypass_move = client.post("/ledger/document/move", json={
                "doc_id": dest_new_rel,
                "new_path": "../../../var/log/badfile.md"
            })
            assert res_bypass_move.status_code == 200
            data_bypass_move = res_bypass_move.json()
            assert data_bypass_move.get("success") is not True, "移动接口未能在路径穿越指令下安全拦截"
            assert "非法的物理路径穿越" in data_bypass_move.get("error"), f"非预期的路径穿越拦截报错: {data_bypass_move.get('error')}"
            print("  ✅ [测试] L3 级防路径穿越恶意原稿搬迁拦截完美通过！")
            
        finally:
            # 恢复单例原状，防止干扰其他用例
            singleton.set_global_engine(original_engine)

def test_safe_static_files_security():
    """🧪 测试 SafeStaticFiles 的物理防护拦截，防止敏感的本地配置文件和原稿文库泄露"""
    client = TestClient(app)
    
    # 1. 尝试越权访问 imprints/ 下的 config.local.yaml 敏感文件
    res_sensitive = client.get("/imprints/luminous_citadel/config.local.yaml")
    assert res_sensitive.status_code == 403, "敏感配置文件越权读取拦截失败！"
    assert "Sovereign Protection Activated" in res_sensitive.text
    
    # 2. 尝试越权访问 manuscripts 原稿文库目录
    res_manuscripts = client.get("/imprints/luminous_citadel/manuscripts/some_post.md")
    assert res_manuscripts.status_code == 403, "隐私原稿文库越权读取拦截失败！"
    
    # 3. 尝试越权访问 metadata 元数据 sqlite/json 目录
    res_metadata = client.get("/imprints/luminous_citadel/metadata/themes/starlight/knowledge_graph.json")
    assert res_metadata.status_code == 403, "元数据物理账本与图谱越权读取拦截失败！"
    
    print("  ✅ [测试] SafeStaticFiles 物理防泄露拦截防御测试 100% 完美通过！")

if __name__ == "__main__":
    test_document_creation_flow()
    test_safe_static_files_security()
