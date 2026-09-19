# -*- coding: utf-8 -*-
"""
🌐 全球全语种通用字数度量模型单元测试 (Universal Multilingual Word Count Tests)
涵盖：中文、英文、日文、韩文、法文、德文、西班牙文、俄文，以及 Frontmatter、代码块噪声剥离与混合长文。
"""
import unittest
from core.utils.text import calculate_universal_word_count


class TestUniversalWordCount(unittest.TestCase):
    def test_empty_and_whitespace(self):
        """测试空文本与纯空白"""
        self.assertEqual(calculate_universal_word_count(""), 0)
        self.assertEqual(calculate_universal_word_count("   \n\t  \r\n"), 0)
        self.assertEqual(calculate_universal_word_count(None), 0)

    def test_chinese_cjk(self):
        """测试中文（简体、繁体与扩展汉字）"""
        self.assertEqual(calculate_universal_word_count("你好世界"), 4)
        self.assertEqual(calculate_universal_word_count("全站出版與知識治理"), 9)
        # 标点符号不计入字数
        self.assertEqual(calculate_universal_word_count("「你好，世界！」"), 4)

    def test_english_words(self):
        """测试英文单词、缩写与连字符词"""
        self.assertEqual(calculate_universal_word_count("Hello world!"), 2)
        self.assertEqual(calculate_universal_word_count("State-of-the-art architecture"), 2)
        self.assertEqual(calculate_universal_word_count("Don't repeat yourself"), 3)
        self.assertEqual(calculate_universal_word_count("Year 2026 and 42 apples"), 5)

    def test_japanese_kana_and_kanji(self):
        """测试日文平假名、片假名与汉字混排"""
        # 平假名 + 汉字
        self.assertEqual(calculate_universal_word_count("こんにちは世界"), 7)
        # 片假名
        self.assertEqual(calculate_universal_word_count("オープンソース"), 7)

    def test_korean_hangul(self):
        """测试韩文音节"""
        self.assertEqual(calculate_universal_word_count("안녕하세요 세계"), 7)
        self.assertEqual(calculate_universal_word_count("지식 그래프"), 5)

    def test_european_latin_languages(self):
        """测试欧洲分词语言（法文、德文、西班牙文等重音变音符号）"""
        # 法文 (带撇号和重音)
        self.assertEqual(calculate_universal_word_count("C'est l'été à Paris"), 4)
        # 德文 (带变音 ä, ö, ü, ß)
        self.assertEqual(calculate_universal_word_count("Die Veränderung ist schön"), 4)
        # 西班牙文 (带 ñ, á, é)
        self.assertEqual(calculate_universal_word_count("¡Hola! ¿Cómo estás?"), 3)

    def test_cyrillic_russian(self):
        """测试俄文/西里尔字母"""
        self.assertEqual(calculate_universal_word_count("Привет, мир!"), 2)
        self.assertEqual(calculate_universal_word_count("Искусственный интеллект"), 2)

    def test_noise_stripping(self):
        """测试 Frontmatter、代码块与 HTML 标签过滤"""
        doc = """---
title: 测试标题
tags: [ai, galaxy, 3d]
date: 2026-09-17
---

# 主标题

这是正文内容。

```python
def calculate_something():
    print("Hello from python code")
    return 42
```

这是包含 `inline_variable` 的段落。<span class="badge">标签文字</span>
"""
        # 排除 frontmatter、```代码块```、`inline`、<标签>
        # "主标题" (3) + "这是正文内容" (6) + "这是包含" (4) + "的段落" (3) + "标签文字" (4)
        # 3 + 6 + 4 + 3 + 4 = 20
        count = calculate_universal_word_count(doc)
        self.assertEqual(count, 20)

    def test_multilingual_mixed(self):
        """测试中英日韩混合排版实战"""
        mixed = "Illacme Plenipes 发布了 3D 知识星谱，サポートする、환영합니다!"
        # Illacme(1) Plenipes(1) 发布了(3) 3D(1) 知识星谱(4) サポートする(6) 환영합니다(5)
        # 1 + 1 + 3 + 1 + 4 + 6 + 5 = 21
        self.assertEqual(calculate_universal_word_count(mixed), 21)


if __name__ == "__main__":
    unittest.main()
