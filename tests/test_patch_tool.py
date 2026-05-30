import os
import pytest
import shutil
from core.adapters.ai.tools.vault_tools import PatchDocumentTool
from core.runtime.engine_singleton import set_global_engine

# Setup a clean mock vault directory for testing
TEST_VAULT_ROOT = os.path.abspath("./test_vault_patch")

class MockEngineConfig:
    def __init__(self):
        self.vault_root = TEST_VAULT_ROOT

class MockEngine:
    def __init__(self):
        self.config = MockEngineConfig()

@pytest.fixture(autouse=True)
def setup_teardown_vault():
    # Setup test vault directory
    if os.path.exists(TEST_VAULT_ROOT):
        shutil.rmtree(TEST_VAULT_ROOT)
    os.makedirs(TEST_VAULT_ROOT, exist_ok=True)
    
    # Mock global engine
    engine = MockEngine()
    set_global_engine(engine)
    
    # Create sample file for patching
    sample_content = """# Title
This is line 1.
This is line 2.
Some repeated line.
This is line 3.
Some repeated line.
End of document.
"""
    os.makedirs(os.path.join(TEST_VAULT_ROOT, "Docs"), exist_ok=True)
    with open(os.path.join(TEST_VAULT_ROOT, "Docs/sample.md"), "w", encoding="utf-8") as f:
        f.write(sample_content)
        
    yield
    
    # Cleanup
    if os.path.exists(TEST_VAULT_ROOT):
        shutil.rmtree(TEST_VAULT_ROOT)
    set_global_engine(None)

def test_patch_document_happy_path():
    tool = PatchDocumentTool()
    
    # Replace line 2
    res = tool.execute(
        relative_path="Docs/sample.md",
        search_content="This is line 2.",
        replace_content="This is replaced line 2!"
    )
    
    assert "Successfully patched" in res
    
    # Check physical content
    with open(os.path.join(TEST_VAULT_ROOT, "Docs/sample.md"), "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "This is replaced line 2!" in content
    assert "This is line 2." not in content
    assert "This is line 1." in content
    assert "This is line 3." in content

def test_patch_document_not_found():
    tool = PatchDocumentTool()
    
    res = tool.execute(
        relative_path="Docs/sample.md",
        search_content="Non-existent content",
        replace_content="New content"
    )
    
    assert "Error: 'search_content' not found" in res

def test_patch_document_multiple_matches():
    tool = PatchDocumentTool()
    
    res = tool.execute(
        relative_path="Docs/sample.md",
        search_content="Some repeated line.",
        replace_content="Unique replace"
    )
    
    assert "Error: 'search_content' matches multiple blocks" in res

def test_patch_document_traversal_denied():
    tool = PatchDocumentTool()
    
    # Attempt path traversal
    res = tool.execute(
        relative_path="../outside_vault.md",
        search_content="Title",
        replace_content="Hacked"
    )
    
    assert "path traversal" in res.lower() or "traversal detected" in res.lower()
