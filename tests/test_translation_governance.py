from core.logic.ai.ai_logic_hub import AILogicHub

def test_glossary_masking_unmasking():
    """测试术语屏蔽与还原功能"""
    glossary = {
        "Illacme Plenipes": "Illacme Plenipes",
        "环境配置": "Environment Setup",
        "算力底座": "Compute Base"
    }
    
    text = "欢迎使用 Illacme Plenipes。请参考环境配置，确保我们的算力底座稳固。"
    
    # 1. 执行屏蔽
    masked, masks = AILogicHub.mask_glossary(text, glossary)
    
    assert "[[GLOS_MASK_0]]" in masked
    assert "[[GLOS_MASK_1]]" in masked
    assert "[[GLOS_MASK_2]]" in masked
    assert "Illacme Plenipes" not in masked
    assert "环境配置" not in masked
    
    # 2. 模拟翻译
    translated = "Welcome to [[GLOS_MASK_0]]. Please refer to [[GLOS_MASK_1]] to ensure our [[GLOS_MASK_2]] is stable."
    
    # 3. 执行还原
    unmasked = AILogicHub.unmask_glossary(translated, masks)
    
    assert unmasked == "Welcome to Illacme Plenipes. Please refer to Environment Setup to ensure our Compute Base is stable."

def test_mask_block_with_governance_options():
    """测试带不同治理选项的块遮罩"""
    # 测试关闭 translate_labels 时，整个 Markdown 链接是否被遮蔽
    text = "点击 [快速入门](http://example.com/start) 开启旅程。"
    
    # translate_labels=True
    masked_t, _ = AILogicHub.mask_block(text, translate_labels=True)
    assert "快速入门" in masked_t
    assert "__B_MASK_0__" in masked_t
    
    # translate_labels=False
    masked_f, masks = AILogicHub.mask_block(text, translate_labels=False)
    assert "快速入门" not in masked_f
    assert "__B_MASK_0__" in masked_f
    assert masks["__B_MASK_0__"] == "[快速入门](http://example.com/start)"

def test_external_links_mask_all():
    """测试外部链接整体遮罩模式"""
    # 测试 external_mask_mode = "all" 时，外链被整体遮罩
    text = "外部链接 [谷歌](https://google.com)"
    
    masked, masks = AILogicHub.mask_block(text, external_mask_mode="all")
    assert "谷歌" not in masked
    assert "__B_MASK_0__" in masked
    assert masks["__B_MASK_0__"] == "[谷歌](https://google.com)"

def test_pydantic_glossary_migration():
    """测试老格式术语自动迁移适配"""
    # 测试老配置格式 {"原词": "译词"} 是否被 model_validator 自动自愈升轨为 {"en": {"原词": "译词"}}
    from core.config.models.ai import ContentGovernanceConfig
    raw_data = {
        "enabled": True,
        "glossary": {
            "主权版图": "Sovereign Territory",
            "算力底座": "Compute Infrastructure"
        }
    }
    cfg = ContentGovernanceConfig.model_validate(raw_data)
    assert "en" in cfg.glossary
    assert cfg.glossary["en"]["主权版图"] == "Sovereign Territory"
    assert cfg.glossary["en"]["算力底座"] == "Compute Infrastructure"

def test_pydantic_glossary_multi_lang():
    """测试多语言格式术语正常解析"""
    # 测试新格式多语种对照表是否被正常保留加载
    from core.config.models.ai import ContentGovernanceConfig
    raw_data = {
        "enabled": True,
        "glossary": {
            "en": {
                "主权版图": "Sovereign Territory"
            },
            "ja": {
                "主权版图": "主権領域"
            }
        }
    }
    cfg = ContentGovernanceConfig.model_validate(raw_data)
    assert cfg.glossary["en"]["主权版图"] == "Sovereign Territory"
    assert cfg.glossary["ja"]["主权版图"] == "主権領域"

def test_clean_translation_response_prompt_delimiter_stripping():
    """测试彻底剥离 LLM 幻觉输出的多语种 Prompt 分隔符与 <think> 标签"""
    raw_llm_out = "### Inhalt ###\n# Unbenannter Entwurf\n### Übersetzung ###"
    cleaned = AILogicHub.clean_translation_response(raw_llm_out)
    assert cleaned == "# Unbenannter Entwurf"

def test_clean_metadata_value_wikilink_and_json_stripping():
    """测试 SEO 描述与元数据在 AI 润色时自动剥离 Wikilinks 语法与 LLM 键值包围"""
    raw_llm_out = 'Unbenannter Original 1: Hier den Inhalt des Manuskripts eingeben...\n[[index|Index]]\n### Übersetzung ###'
    cleaned = AILogicHub.clean_metadata_value(raw_llm_out)
    assert "[[index|Index]]" not in cleaned
    assert "Index" in cleaned
    assert "### Übersetzung ###" not in cleaned
