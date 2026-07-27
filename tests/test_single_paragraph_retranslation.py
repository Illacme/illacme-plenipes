import pytest
from unittest.mock import MagicMock
from services.api.routes.gov.context_shards.review_ops import retranslate_paragraph_impl

def test_retranslate_paragraph_empty_input():
    mock_engine = MagicMock()
    res = retranslate_paragraph_impl(mock_engine, "Docs/no_frontmatter.md", "de", 0, "")
    assert res["ok"] is True
    assert res["translated_text"] == ""

def test_retranslate_paragraph_success():
    mock_engine = MagicMock()
    mock_node = MagicMock()
    mock_node.translate_segment.return_value = "Dies ist ein Test."
    
    from core.logic.ai.ai_factory import TranslatorFactory
    with pytest.MonkeyPatch.context() as m:
        m.setattr(TranslatorFactory, "create", lambda cfg: mock_node)
        res = retranslate_paragraph_impl(mock_engine, "Docs/no_frontmatter.md", "de", 0, "This is a test.")
        assert res["ok"] is True
        assert res["translated_text"] == "Dies ist ein Test."
