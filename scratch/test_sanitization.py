
import sys
import os

# Add parent dir to sys.path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import sanitize_ai_response

def test_sanitization():
    test_cases = [
        {
            "name": "Tags only",
            "input": "<source_text>Hello World</source_text>",
            "expected": "Hello World"
        },
        {
            "name": "Markdown fence wrapping",
            "input": "```markdown\n# Hello\nContent\n```",
            "expected": "# Hello\nContent"
        },
        {
            "name": "Preamble and tags",
            "input": "Here is the translation:\n<source_text>\n# Translation result\n</source_text>",
            "expected": "# Translation result"
        },
        {
            "name": "Mixed Case Tags",
            "input": "<SOURCE_TEXT>Mixed</SOURCE_TEXT>",
            "expected": "Mixed"
        }
    ]

    for case in test_cases:
        actual = sanitize_ai_response(case["input"])
        print(f"Testing: {case['name']}")
        if actual == case["expected"]:
            print("✅ SUCCESS")
        else:
            print(f"❌ FAIL: Expected '{repr(case['expected'])}', got '{repr(actual)}'")

if __name__ == "__main__":
    test_sanitization()
