"""🎨 Sovereign 主题案例展示视图转换器分片 (Showcase Multi-View Shard)

物理职责：
- 负责提取与重塑案例页（Showcase）的双视图切换交互（网格卡片 vs 紧凑列表）。
- 严格遵循 SOP-02 架构演进规约，物理行数保持在 300 行以内。
"""

import re
from themes.sovereign.adapters.sovereign_i18n import get_ui_i18n


def transform_showcase_multi_view(content_html: str, lang: str) -> str:
    """🎨 为案例页注入网格与紧凑列表双视图切换器"""
    # 1. 提取全页所有 card-pioneer
    cards = re.findall(
        r'<a\s+[^>]*href="([^"]+)"[^>]*class="[^"]*card-pioneer[^"]*"[^>]*>(.*?)</a>|<a\s+[^>]*class="[^"]*card-pioneer[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        content_html,
        re.DOTALL
    )
    
    compact_rows = []
    card_count = 0
    for match in cards:
        href = match[0] or match[2]
        inner = match[1] or match[3]
        if not href or not inner:
            continue
        card_count += 1
        tag_match = re.search(r'<span\s+[^>]*class="[^"]*card-tag[^"]*"[^>]*>([^<]+)</span>', inner)
        tag = tag_match.group(1).strip() if tag_match else "生态"
        title_match = re.search(r'<h3[^>]*>([^<]+)</h3>', inner)
        title = title_match.group(1).strip() if title_match else "Showcase"
        desc_match = re.search(r'<p[^>]*>([^<]+)</p>', inner)
        desc = desc_match.group(1).strip() if desc_match else ""
        
        compact_rows.append(f"""<a href="{href}" class="compact-row showcase-row">
<span class="compact-tags"><span class="tag-pill">{tag}</span></span>
<span class="compact-title">{title}</span>
<span class="compact-desc">{desc}</span>
</a>""")

    if card_count == 0:
        return content_html

    ui = get_ui_i18n(lang)
    t_grid = ui.get("view_cards", "Cards")
    t_compact = ui.get("view_list", "List")

    toolbar_html = f"""<div class="showcase-toolbar">
<div class="showcase-view-switcher" role="tablist" aria-label="Showcase layout views">
<button class="view-switch-btn active" data-view="grid" role="tab" aria-selected="true">
<span class="view-btn-icon">🎛️</span>
<span class="view-btn-text">{t_grid}</span>
<span class="view-btn-badge">{card_count}</span>
</button>
<button class="view-switch-btn" data-view="compact" role="tab" aria-selected="false">
<span class="view-btn-icon">📑</span>
<span class="view-btn-text">{t_compact}</span>
</button>
</div>
</div>"""

    # 包装：网格视图包含原页面全部 HTML 内容；紧凑视图展示平铺列表
    grid_view = f'<div class="showcase-view-container showcase-grid-view active" id="showcase-view-grid">\n{content_html}\n</div>'
    compact_view = f'<div class="showcase-view-container showcase-compact-view" id="showcase-view-compact">\n<div class="compact-table">{"".join(compact_rows)}</div>\n</div>'

    # 将切换栏插入到第一个标题/描述之后或内容最前部
    first_hr = content_html.find('<hr')
    if first_hr != -1:
        hr_end = content_html.find('>', first_hr) + 1
        head_part = content_html[:hr_end]
        rest_part = content_html[hr_end:]
        grid_view_rest = f'<div class="showcase-view-container showcase-grid-view active" id="showcase-view-grid">\n{rest_part}\n</div>'
        return f"{head_part}\n{toolbar_html}\n{grid_view_rest}\n{compact_view}"

    return f"{toolbar_html}\n{grid_view}\n{compact_view}"
