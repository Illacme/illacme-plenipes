from core.logic.ai.ai_logic_hub import AILogicHub

def test_markdown_link_only_mask_url():
    """验证仅遮罩 Markdown 超链接中的 URL，保留文本的测试"""
    text = "请点击 [快速入门](./getting-started.html) 来了解更多。"
    masked, masks = AILogicHub.mask_block(text)
    
    # 验证 URL 被正确遮罩，但 Label 保留
    assert "快速入门" in masked
    assert "./getting-started.html" not in masked
    assert "__B_MASK_0__" in masked
    assert masks.get("__B_MASK_0__") == "./getting-started.html"
    
    # 模拟翻译修改 Label
    translated = masked.replace("快速入门", "Getting Started")
    unmasked = AILogicHub.unmask_block(translated, masks)
    
    # 验证翻译后的文本和 URL 还原
    assert unmasked == "请点击 [Getting Started](./getting-started.html) 来了解更多。"

def test_markdown_link_with_anchor_mask():
    """验证带锚点的 Markdown 超链接的遮罩测试"""
    text = "请参考 [环境配置](./getting-started.html#1-安装与准备) 来搭建基础。"
    masked, masks = AILogicHub.mask_block(text)
    
    # 验证只有 base_url 被遮罩，而锚点保留在外面并且有包裹结构
    assert "环境配置" in masked
    assert "./getting-started.html" not in masked
    assert "#|1-安装与准备|" in masked
    assert "__B_MASK_0__#|1-安装与准备|" in masked
    assert masks.get("__B_MASK_0__") == "./getting-started.html"
    
    # 模拟翻译修改 Label 和 Anchor
    translated = masked.replace("环境配置", "Environment Setup").replace("1-安装与准备", "1. Installation and Preparation")
    unmasked = AILogicHub.unmask_block(translated, masks)
    
    # 验证最终拼接结果以及合规清洗
    assert unmasked == "请参考 [Environment Setup](./getting-started.html#1.-installation-and-preparation) 来搭建基础。"

def test_markdown_link_already_packaged_mask():
    """验证针对已打包遮罩超链接的匹配与解析测试"""
    # 模拟经过 MaskingAndRoutingStep 后的带包裹状态
    text = "请参考 [环境配置]([[STB_MASK_1]]#|1-安装与准备|) 来搭建基础。"
    masked, masks = AILogicHub.mask_block(text)
    
    assert "环境配置" in masked
    assert "[[STB_MASK_1]]" not in masked
    assert "#|1-安装与准备|" in masked
    assert "__B_MASK_0__#|1-安装与准备|" in masked
    assert masks.get("__B_MASK_0__") == "[[STB_MASK_1]]"
    
    translated = masked.replace("环境配置", "Environment Setup").replace("1-安装与准备", "1. Installation and Preparation")
    unmasked = AILogicHub.unmask_block(translated, masks)
    
    assert unmasked == "请参考 [Environment Setup]([[STB_MASK_1]]#1.-installation-and-preparation) 来搭建基础。"

def test_markdown_image_only_mask_url():
    """验证针对 Markdown 图片 URL 遮罩的测试"""
    text = "看看这张图片 ![示例图片](http://example.com/logo.png) 怎么样。"
    masked, masks = AILogicHub.mask_block(text)
    
    assert "示例图片" in masked
    assert "http://example.com/logo.png" not in masked
    assert "__B_MASK_0__" in masked
    assert masks.get("__B_MASK_0__") == "http://example.com/logo.png"
    
    translated = masked.replace("示例图片", "Example Logo")
    unmasked = AILogicHub.unmask_block(translated, masks)
    assert unmasked == "看看这张图片 ![Example Logo](http://example.com/logo.png) 怎么样。"

def test_other_masks_intact():
    """验证 Obsidian 链接和 HTML 注释等其他遮罩不受干扰的测试"""
    text = "这是 Obsidian 链接 [[MyNote|My Note]] 和注释 <!-- 这里是注释 -->"
    masked, masks = AILogicHub.mask_block(text)
    
    # Wikilink display label 保留给 AI 翻译，target 被遮罩；注释被整体遮罩
    assert "My Note" in masked
    assert "MyNote" not in masked  # target 被遮罩
    assert "这里是注释" not in masked
    assert "__W_MASK_0__" in masked
    assert "__B_MASK_1__" in masked
    
    unmasked = AILogicHub.unmask_block(masked, masks)
    assert unmasked == text


def test_llm_casing_and_bracket_dropped_self_healing():
    """验证 LLM 产生大小写抖动及丢弃方括号时的自愈还原能力"""
    text = "写点笔记，[[创建链接]]，或者试一试[导入器](https://example.com/import)"
    masked, masks = AILogicHub.mask_block(text)
    
    # Wikilink [[创建链接]] 转换为 [创建链接](__W_MASK_0__)
    # Markdown link [导入器](url) 转换为 [导入器](__B_MASK_1__)
    # 模拟 LLM 产生了大小写抖动 (__w_mask_0__) 并翻译了 display text
    llm_output = "Schreiben Sie Notizen, [Links erstellen](__w_mask_0__), oder probieren Sie Importer (__B_MASK_1__)"
    unmasked = AILogicHub.unmask_block(llm_output, masks)
    
    assert "[[创建链接|Links erstellen]]" in unmasked
    assert "[Importer](https://example.com/import)" in unmasked


def test_llm_complete_placeholder_dropped_self_healing():
    """验证 LLM 彻底遗漏占位符 (__B_MASK_1__) 只保留 [Importer] 时的自愈挂载能力"""
    text = "写点笔记，或者试一试[导入器](https://example.com/import)"
    masked, masks = AILogicHub.mask_block(text)
    
    # 模拟 LLM 彻底删除了 (__B_MASK_0__) 占位符，只返回了 [Importer]
    llm_output = "Schreiben Sie Notizen, oder probieren Sie [Importer]"
    unmasked = AILogicHub.unmask_block(llm_output, masks)
    
    assert "[Importer](https://example.com/import)" in unmasked


