# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Shared HTML Template
模块职责：提供双模（Python 服务端预渲染 / Client 客户端离线解析）共用的完整 HTML/CSS/DOM 骨架。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import html
from typing import Optional

from .epub_reader_css import get_epub_reader_css
from .epub_reader_polyglot_css import get_epub_polyglot_css
from .epub_reader_annotator import get_epub_annotator_css, get_epub_annotator_js
from .epub_reader_search import get_epub_search_css, get_epub_search_js
from .epub_reader_prefs_css import get_epub_prefs_css
from .epub_reader_prefs_js import get_epub_prefs_js
from .epub_reader_js import get_epub_reader_js
from .epub_reader_polyglot_js import get_epub_reader_polyglot_js
from .epub_reader_polyglot_sync_js import get_epub_reader_polyglot_sync_js
from .epub_reader_poster_js import get_epub_poster_js
from .epub_reader_pager_css import get_epub_pager_css
from .epub_reader_pager_js import get_epub_pager_js


def build_epub_reader_shell(
    book_title: str,
    toc_html: str,
    content_html: str,
    qr_data_uri: str = "",
    qr_url: str = "",
    qr_tier: str = "lan",
    qr_tip: str = "📱 手机扫码直达翻阅",
    source_url: str = "",
    client_scripts_html: str = "",
    extra_css: str = ""
) -> str:
    """构建自包含的完整 EPUB 在线翻阅 HTML 视界"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark" data-read-mode="paginated" data-spread="auto" data-font="sans">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0"/>
  <title>{html.escape(book_title)} - EPUB 在线翻阅</title>
  <style>{get_epub_reader_css()}
{get_epub_polyglot_css()}
{get_epub_annotator_css()}
{get_epub_search_css()}
{get_epub_prefs_css()}
{get_epub_pager_css()}
{extra_css}</style>
</head>
<body>
  <div class="er-progress-bar" id="er-progress-bar"></div>
  <header class="er-topbar">
    <div class="er-topbar-left">
      <button type="button" class="er-btn" id="er-toggle-sidebar" title="展开/收起目录导航树 (快捷键 M)">☰<span class="er-btn-text"> 目录/检索</span></button>
      <div class="er-book-title" title="{html.escape(book_title)}">{html.escape(book_title)}</div>
    </div>
    <div class="er-topbar-polyglot" id="er-topbar-polyglot"></div>
    <div class="er-controls">
      <button type="button" class="er-btn" id="er-btn-prefs" title="排版与主题定制 (P)">🎨<span class="er-btn-text"> 排版</span></button>
      <button type="button" class="er-btn" id="er-spread-toggle" title="切换排版：单页 / 双页对开">📑<span class="er-btn-text"> 双页</span></button>
      <button type="button" class="er-btn" id="er-font-family" title="切换字体：黑体 / 宋体 / 楷体">🔤<span class="er-btn-text"> 黑体</span></button>
      <button type="button" class="er-btn er-mode-btn" id="er-mode-toggle" title="切换阅读模式：左右翻页 / 连续卷轴">📖<span class="er-btn-text"> 翻页</span></button>
      <button type="button" class="er-btn" id="er-font-dec" title="缩小字号">A-</button>
      <button type="button" class="er-btn" id="er-font-inc" title="放大字号">A+</button>
      <button type="button" class="er-theme-btn active" data-theme="dark" title="暗黑翠玉">🌙</button>
      <button type="button" class="er-theme-btn" data-theme="light" title="高亮纯净">☀️</button>
      <button type="button" class="er-theme-btn" data-theme="sepia" title="复古羊皮纸">📜</button>
      <button type="button" class="er-btn" id="er-fullscreen" title="全屏沉浸阅读 (快捷键 F)">⛶</button>
    </div>
  </header>

  <div class="er-layout" id="er-app" data-source-url="{html.escape(source_url)}">
    <aside class="er-sidebar" id="er-sidebar">
      <div class="er-sidebar-tabs">
        <button type="button" class="er-stab-btn active" id="er-stab-toc" data-tab="er-pane-toc">📑 目录</button>
        <button type="button" class="er-stab-btn" id="er-stab-notes" data-tab="er-pane-notes">🔖 划线 <span class="er-badge" id="er-notes-count">0</span></button>
        <button type="button" class="er-stab-btn" id="er-stab-search" data-tab="er-pane-search">🔍 检索 <span class="er-badge" id="er-search-count">0</span></button>
      </div>
      <div class="er-sidebar-pane active" id="er-pane-toc">
        <div id="er-toc-tree">{toc_html}</div>
      </div>
      <div class="er-sidebar-pane" id="er-pane-notes">
        <div class="er-notes-toolbar">
          <button type="button" class="er-btn er-btn-sm er-btn-primary" id="er-export-notes-btn">📥 导出笔记</button>
          <button type="button" class="er-btn er-btn-sm" id="er-clear-notes-btn">🗑️ 清空</button>
        </div>
        <div class="er-notes-list" id="er-notes-list"></div>
      </div>
      <div class="er-sidebar-pane" id="er-pane-search">
        <div class="er-search-box">
          <span class="er-search-icon">🔍</span>
          <input type="text" class="er-search-input" id="er-search-input" placeholder="输入关键词检索全书..." autocomplete="off"/>
          <span class="er-search-kbd">⌘K</span>
        </div>
        <div class="er-search-meta" id="er-search-meta">输入关键词检索全书典籍</div>
        <div class="er-search-results" id="er-search-results">
          <div class="er-search-empty">输入关键词，即可秒级全文检索所有章节与段落。</div>
        </div>
      </div>
    </aside>
    <div class="er-backdrop" id="er-backdrop"></div>
    <main class="er-main" id="er-main">
      <button type="button" class="er-page-arrow er-page-prev" id="er-page-prev" title="上一页 (←)">‹</button>
      <button type="button" class="er-page-arrow er-page-next" id="er-page-next" title="下一页 (→)">›</button>
      
      <div class="er-viewport" id="er-viewport">
        <div class="er-book-content" id="er-book-content">
          {content_html}
        </div>
      </div>

      <footer class="er-paginated-footer" id="er-paginated-footer">
        <div class="er-footer-chapter" id="er-footer-chapter"></div>
        <div class="er-footer-nav" id="er-footer-nav">
          <button type="button" class="er-footer-btn er-nav-first" id="er-nav-first" title="跳转至首页 (Home 或 1)">⇤ 首页</button>
          <button type="button" class="er-footer-btn er-nav-prev-footer" id="er-nav-prev-footer" title="上一页 (←)">‹</button>
          <div class="er-footer-page-box" id="er-footer-page-box" title="点击可直接输入目标页码跳转 (快捷键 G)">
            <span class="er-footer-page er-footer-page-text" id="er-footer-page">1 / 1</span>
            <div class="er-footer-page-jump" id="er-footer-page-jump" style="display:none;">
              <input type="number" class="er-page-jump-input" id="er-page-jump-input" min="1" placeholder="页码" />
              <span class="er-page-jump-total" id="er-page-jump-total" style="font-size:0.75rem; color:var(--text-dim, #94a3b8); font-family:monospace;">/ 1</span>
            </div>
          </div>
          <button type="button" class="er-footer-btn er-nav-next-footer" id="er-nav-next-footer" title="下一页 (→)">›</button>
          <button type="button" class="er-footer-btn er-nav-last" id="er-nav-last" title="跳转至尾页 (End)">尾页 ⇥</button>
        </div>
      </footer>
    </main>
  </div>

  <!-- 🎈 划选浮动工具栏 -->
  <div class="er-floating-bar" id="er-floating-bar">
    <button type="button" class="er-fbtn" data-color="yellow" title="黄荧光划线"><span class="er-fdot dot-yellow"></span> 划线</button>
    <button type="button" class="er-fbtn" data-color="emerald" title="翠绿高亮"><span class="er-fdot dot-emerald"></span></button>
    <button type="button" class="er-fbtn" data-color="pink" title="胭脂粉高亮"><span class="er-fdot dot-pink"></span></button>
    <div class="er-fsep"></div>
    <button type="button" class="er-fbtn" id="er-fbtn-note" title="随手批注">💭 批注</button>
    <button type="button" class="er-fbtn" id="er-fbtn-card" title="生成金句卡片">🖼️ 金句卡片</button>
    <button type="button" class="er-fbtn" id="er-fbtn-copy" title="复制纯文本">📋 复制</button>
  </div>

  <!-- 💬 正文划线就地悬浮气泡 -->
  <div class="er-mark-popover" id="er-mark-popover">
    <div class="er-pop-row">
      <div class="er-pop-colors">
        <span class="er-pop-color dot-yellow" data-color="yellow" title="黄荧光"></span>
        <span class="er-pop-color dot-emerald" data-color="emerald" title="翠绿"></span>
        <span class="er-pop-color dot-pink" data-color="pink" title="胭脂粉"></span>
      </div>
      <div class="er-pop-actions">
        <button type="button" class="er-pop-btn er-pop-copy" title="复制">📋 复制</button>
        <button type="button" class="er-pop-btn er-pop-card" title="金句卡片">🖼️ 卡片</button>
        <button type="button" class="er-pop-btn er-pop-del" title="删除划线">🗑️ 删除</button>
      </div>
    </div>
    <div class="er-pop-comment" style="display:none;"></div>
    <div class="er-pop-input-box">
      <input type="text" class="er-pop-input" placeholder="输入或修改随手批注..." maxlength="200" />
      <button type="button" class="er-pop-save-note">保存</button>
    </div>
  </div>

  <!-- 🖼️ 金句卡片模态窗 -->
  <div class="er-modal-backdrop" id="er-card-modal">
    <div class="er-card-box">
      <div class="er-quote-card" id="er-quote-card">
        <div class="er-card-quote-mark">“</div>
        <div class="er-card-quote-text" id="er-card-text"></div>
        <div class="er-card-quote-mark-end">”</div>
        <div class="er-card-meta">
          <div>
            <div class="er-card-book-title" id="er-card-book"></div>
            <div class="er-card-chapter" id="er-card-chap"></div>
          </div>
          <div class="er-card-brand">Illacme Plenipes</div>
        </div>
      </div>
      <div class="er-card-actions">
        <button type="button" class="er-btn" id="er-card-close-btn">关闭</button>
        <button type="button" class="er-btn" id="er-card-copy-btn">📋 复制金句文本</button>
        <button type="button" class="er-btn er-btn-primary" id="er-card-save-btn">🖼️ 保存卡片海报</button>
      </div>
    </div>
  </div>

  <!-- ✍️ 随手批注模态窗 -->
  <div class="er-modal-backdrop" id="er-note-modal">
    <div class="er-note-box">
      <div class="er-note-box-title">✍️ 记录随笔思考</div>
      <div class="er-note-target-text" id="er-note-target-text"></div>
      <textarea class="er-note-input" id="er-note-input" rows="3" placeholder="在此写下对本段文字的灵感、考据或思考..."></textarea>
      <div class="er-note-actions">
        <button type="button" class="er-btn" id="er-note-cancel-btn">取消</button>
        <button type="button" class="er-btn er-btn-primary" id="er-note-save-btn">保存批注</button>
      </div>
    </div>
  </div>
  <img id="er-qr-source" src="{qr_data_uri}" data-url="{qr_url}" data-tier="{qr_tier}" data-tip-text="{qr_tip}" style="display:none;" alt="📱 手机扫码直达翻阅"/>

  <!-- 🎨 Aa 排版与主题定制抽屉 -->
  <div class="er-prefs-drawer" id="er-prefs-drawer">
    <div class="er-prefs-header">
      <div class="er-prefs-title">🎨 排版与沉浸偏好</div>
      <button type="button" class="er-prefs-close" id="er-prefs-close" title="收起抽屉">✕</button>
    </div>
    <div class="er-prefs-row">
      <span class="er-prefs-label">字号大小</span>
      <div class="er-prefs-group">
        <button type="button" class="er-pbtn" id="er-pfs-dec">A- 缩小</button>
        <span id="er-pfs-val" style="font-weight:700; min-width:42px; text-align:center; font-size:0.78rem;">16px</span>
        <button type="button" class="er-pbtn" id="er-pfs-inc">A+ 放大</button>
      </div>
    </div>
    <div class="er-prefs-row">
      <span class="er-prefs-label">阅读行距</span>
      <div class="er-prefs-group">
        <button type="button" class="er-pbtn er-lh-btn" data-lh="compact">紧凑</button>
        <button type="button" class="er-pbtn er-lh-btn active" data-lh="normal">标准</button>
        <button type="button" class="er-pbtn er-lh-btn" data-lh="relaxed">宽松</button>
      </div>
    </div>
    <div class="er-prefs-row">
      <span class="er-prefs-label">五色纸质</span>
      <div class="er-theme-swatches">
        <button type="button" class="er-swatch-btn swatch-dark active" data-th="dark" title="暗黑翠玉">🌙</button>
        <button type="button" class="er-swatch-btn swatch-light" data-th="light" title="纯净日光">☀️</button>
        <button type="button" class="er-swatch-btn swatch-sepia" data-th="sepia" title="暖阳麦香">📜</button>
        <button type="button" class="er-swatch-btn swatch-mint" data-th="mint" title="水墨薄荷护眼绿">🌿</button>
        <button type="button" class="er-swatch-btn swatch-oled" data-th="oled" title="深空极黑纯黑 OLED">🌑</button>
      </div>
    </div>
    <div class="er-prefs-row" style="margin-bottom:4px; padding-top:6px; border-top:1px dashed var(--border);">
      <span class="er-prefs-label">沉浸手势</span>
      <span style="font-size:0.72rem; color:var(--text-dim);">轻触屏幕正中央，可随时全屏沉浸阅读</span>
    </div>
  </div>

  {client_scripts_html}
  <script>{get_epub_reader_js()}</script>
  <script>{get_epub_reader_polyglot_js()}</script>
  <script>{get_epub_reader_polyglot_sync_js()}</script>
  <script>{get_epub_annotator_js()}</script>
  <script>{get_epub_search_js()}</script>
  <script>{get_epub_prefs_js()}</script>
  <script>{get_epub_poster_js()}</script>
  <script>{get_epub_pager_js()}</script>
</body>
</html>"""
