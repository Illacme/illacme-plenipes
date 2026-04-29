import re

mask_pattern = r'\[\[SECRET_TAG\]\]|\{\{<.*?>\}\}|\$\$.*?\$\$|\$[^\$]+\$|\!\[\[[^\]]+\]\]|\[\[[^\]]+\]\]|\!\[[^\]]*\]\([^)]+\)|\[[^\]]*\]\([^)]+\)'
content = "We have a secret internal tag: [[SECRET_TAG]]. This should NOT be translated."

def mask_fn(m):
    return f"[[STB_MASK_0]]"

masked = re.sub(mask_pattern, mask_fn, content)
print(f"Content: {content}")
print(f"Masked: {masked}")
