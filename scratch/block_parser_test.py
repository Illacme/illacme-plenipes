import sys
import os

# 确保能加载到 core 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logic.block_parser import MarkdownBlockParser

def test_slicing():
    test_md = """# 标题 1

这是一段普通的文字。

> [!NOTE]
> 这是一个 Callout 容器
> 它包含多行内容
> ```python
> print("甚至包含代码")
> ```

下面是一个 Docusaurus 的 Tabs:

:::tabs
## 标签 1
内容 1

## 标签 2
内容 2
:::

最后一段。"""

    parser = MarkdownBlockParser()
    blocks = parser.parse(test_md)

    print(f"🚀 解析完成，共拆分出 {len(blocks)} 个语义块：\n")
    for i, b in enumerate(blocks):
        preview = b.content.replace('\n', ' \\n')[:50]
        print(f"[{i}] 类型: {b.type:<12} | 指纹: {b.fingerprint[:8]} | 内容: {preview}...")

    # 验证可还原性
    rebuilt = parser.rebuild(blocks)
    if rebuilt.strip() == test_md.strip():
        print("\n✅ [物理自洽性测试通过]: 解析并重组后的内容与原文 100% 一致")
    else:
        print("\n❌ [物理自洽性测试失败]: 重组内容发生偏离！")

if __name__ == "__main__":
    test_slicing()
