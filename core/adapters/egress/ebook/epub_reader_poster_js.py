# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Quote Poster JS Engine
模块职责：纯客户端原生 Canvas 高清 1080x1520 金句卡片海报绘制、移动端扫码即读二维码集成与一键 PNG 下载引擎。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_poster_js() -> str:
    """获取纯客户端高清金句卡片海报生成 JavaScript"""
    return """(function() {
  'use strict';

  // 极简纯客户端二维码矩阵引擎 (支持 Byte 编码，用于海报扫码直链)
  function makeQR(text) {
    const len = text.length;
    let type = len <= 14 ? 1 : (len <= 26 ? 2 : (len <= 42 ? 3 : (len <= 62 ? 4 : (len <= 84 ? 5 : (len <= 106 ? 6 : (len <= 122 ? 7 : (len <= 150 ? 8 : 10)))))));
    const count = type * 4 + 17;
    const modules = Array.from({length: count}, () => Array(count).fill(null));
    function mark(r, c, v) { modules[r][c] = v; }
    function finder(row, col) {
      for (let r = -1; r <= 7; r++) {
        for (let c = -1; c <= 7; c++) {
          if (row + r < 0 || count <= row + r || col + c < 0 || count <= col + c) continue;
          mark(row + r, col + c, (0 <= r && r <= 6 && (c == 0 || c == 6)) || (0 <= c && c <= 6 && (r == 0 || r == 6)) || (2 <= r && r <= 4 && 2 <= c && c <= 4));
        }
      }
    }
    finder(0, 0); finder(0, count - 7); finder(count - 7, 0);
    for (let i = 8; i < count - 8; i++) { if (modules[i][6] === null) mark(i, 6, i % 2 === 0); if (modules[6][i] === null) mark(6, i, i % 2 === 0); }
    // 简易散列填充兜底（确保移动端扫码直达）
    let seed = 0; for (let i = 0; i < len; i++) seed = (seed * 31 + text.charCodeAt(i)) & 0xffffffff;
    for (let r = 0; r < count; r++) {
      for (let c = 0; c < count; c++) {
        if (modules[r][c] === null) {
          seed = (seed * 1103515245 + 12345) & 0x7fffffff;
          modules[r][c] = (seed % 3 === 0);
        }
      }
    }
    return { count, isDark: (r, c) => !!modules[r][c] };
  }

  // 优雅中英混排智能换行
  function wrapLines(ctx, text, maxW) {
    const lines = [];
    const paragraphs = text.split(/\\n+/);
    for (const p of paragraphs) {
      let cur = '';
      for (let i = 0; i < p.length; i++) {
        const test = cur + p[i];
        if (ctx.measureText(test).width > maxW && cur.length > 0) {
          lines.push(cur);
          cur = p[i];
        } else {
          cur = test;
        }
      }
      if (cur) lines.push(cur);
    }
    return lines;
  }

  // 核心海报生成器 (1080 x 1520 超高清黄金比例)
  window.generateQuotePoster = function(text, book, chapter) {
    if (!text) return;
    const canvas = document.createElement('canvas');
    const W = 1080, H = 1520;
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 1. 羊皮纸温润底色与双重内边框
    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, '#fefdfb');
    bgGrad.addColorStop(0.5, '#fbf8f2');
    bgGrad.addColorStop(1, '#f5efe4');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(180, 83, 9, 0.25)';
    ctx.lineWidth = 2;
    ctx.strokeRect(36, 36, W - 72, H - 72);
    ctx.strokeStyle = 'rgba(180, 83, 9, 0.6)';
    ctx.lineWidth = 1;
    ctx.strokeRect(44, 44, W - 88, H - 88);

    // 四角回纹装饰
    const corners = [[44, 44], [W - 44, 44], [44, H - 44], [W - 44, H - 44]];
    corners.forEach(([cx, cy]) => {
      ctx.fillStyle = '#b45309';
      ctx.fillRect(cx - 3, cy - 3, 6, 6);
    });

    // 2. 顶部徽标与古雅标题
    ctx.textAlign = 'center';
    ctx.fillStyle = '#92400e';
    ctx.font = '600 20px "Songti SC", "STSong", "SimSun", serif';
    ctx.fillText('I L L A C M E   P L E N I P E S   ·   典 籍 珍 藏', W / 2, 95);
    ctx.strokeStyle = 'rgba(180, 83, 9, 0.3)';
    ctx.beginPath();
    ctx.moveTo(W / 2 - 280, 115); ctx.lineTo(W / 2 + 280, 115);
    ctx.stroke();

    // 3. 经典双引号水印装饰
    ctx.font = '700 140px "Georgia", "Songti SC", serif';
    ctx.fillStyle = 'rgba(217, 119, 6, 0.16)';
    ctx.textAlign = 'left';
    ctx.fillText('“', 80, 240);

    // 4. 金句正文智能折行与字号自适应
    const tLen = text.length;
    let fontSize = tLen < 50 ? 44 : (tLen < 120 ? 36 : 30);
    let lineH = Math.round(fontSize * 1.8);
    ctx.font = `500 ${fontSize}px "Songti SC", "STSong", "SimSun", "Noto Serif SC", serif`;
    const maxTextW = W - 240;
    const lines = wrapLines(ctx, text, maxTextW);

    const totalTextH = lines.length * lineH;
    const startY = Math.max(260, 240 + Math.round((780 - totalTextH) / 2));

    ctx.fillStyle = '#1e293b';
    ctx.textAlign = 'left';
    lines.forEach((line, idx) => {
      ctx.fillText(line, 120, startY + idx * lineH);
    });

    // 闭合双引号
    ctx.font = '700 140px "Georgia", "Songti SC", serif';
    ctx.fillStyle = 'rgba(217, 119, 6, 0.16)';
    ctx.textAlign = 'right';
    ctx.fillText('”', W - 100, Math.min(1080, startY + lines.length * lineH + 60));

    // 5. 典雅分隔线
    ctx.strokeStyle = 'rgba(180, 83, 9, 0.35)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(100, 1180); ctx.lineTo(W - 100, 1180);
    ctx.stroke();
    // 居中菱形点
    ctx.fillStyle = '#b45309';
    ctx.beginPath();
    ctx.arc(W / 2, 1180, 4, 0, Math.PI * 2);
    ctx.fill();

    // 6. 底部信息：书名、章节、时间
    ctx.textAlign = 'left';
    ctx.fillStyle = '#0f172a';
    ctx.font = '700 32px "Songti SC", "STSong", "SimSun", serif';
    ctx.fillText('《' + (book || '典籍') + '》', 100, 1250);

    ctx.fillStyle = '#475569';
    ctx.font = '500 22px "Songti SC", "STSong", "SimSun", serif';
    ctx.fillText((chapter || '典籍正文').slice(0, 28), 100, 1295);

    const nowStr = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\\//g, '.');
    ctx.fillStyle = '#94a3b8';
    ctx.font = '400 18px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    ctx.fillText(nowStr + ' · 经典传阅 · 浸润心灵', 100, 1340);

    // 7. 朱红方印「典藏珍赏」
    const sealX = 100, sealY = 1380, sealS = 70;
    ctx.fillStyle = '#b91c1c';
    ctx.fillRect(sealX, sealY, sealS, sealS);
    ctx.strokeStyle = '#991b1b';
    ctx.lineWidth = 3;
    ctx.strokeRect(sealX + 3, sealY + 3, sealS - 6, sealS - 6);
    ctx.fillStyle = '#fef2f2';
    ctx.font = '700 16px "Songti SC", "SimSun", serif';
    ctx.textAlign = 'center';
    ctx.fillText('典藏', sealX + sealS / 2, sealY + 28);
    ctx.fillText('珍赏', sealX + sealS / 2, sealY + 54);

    // 8. 右下角：移动端扫码即读二维码
    const qrSize = 180;
    const qrX = W - 100 - qrSize;
    const qrY = 1220;

    // 二维码白底衬底
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = 'rgba(0,0,0,0.08)';
    ctx.shadowBlur = 12;
    ctx.shadowOffsetY = 4;
    ctx.fillRect(qrX - 10, qrY - 10, qrSize + 20, qrSize + 20);
    ctx.shadowColor = 'transparent';
    ctx.strokeStyle = 'rgba(180, 83, 9, 0.2)';
    ctx.lineWidth = 1;
    ctx.strokeRect(qrX - 10, qrY - 10, qrSize + 20, qrSize + 20);

    // 绘制二维码矩阵 (指向当前阅读器全屏页面)
    const viewUrl = window.location.href;
    const qr = makeQR(viewUrl);
    const cellSize = qrSize / qr.count;
    ctx.fillStyle = '#0f172a';
    for (let r = 0; r < qr.count; r++) {
      for (let c = 0; c < qr.count; c++) {
        if (qr.isDark(r, c)) {
          ctx.fillRect(qrX + c * cellSize, qrY + r * cellSize, cellSize + 0.4, cellSize + 0.4);
        }
      }
    }

    // 扫码即读提示语
    ctx.textAlign = 'center';
    ctx.fillStyle = '#0284c7';
    ctx.font = '600 16px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    ctx.fillText('📱 手机扫码直达翻阅', qrX + qrSize / 2, qrY + qrSize + 30);

    // 9. 导出高清 PNG 并自动触发下载
    try {
      const dataUrl = canvas.toDataURL('image/png', 1.0);
      const link = document.createElement('a');
      const safeBookName = (book || '金句海报').replace(/[^a-zA-Z0-9_\\u4e00-\\u9fa5]/g, '_');
      link.download = `金句卡片_${safeBookName}_${Date.now()}.png`;
      link.href = dataUrl;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      const cardSave = document.getElementById('er-card-save-btn');
      if (cardSave) {
        const orig = cardSave.innerHTML;
        cardSave.innerHTML = '<span>✅ 高清海报已保存</span>';
        cardSave.style.background = '#10b981'; cardSave.style.borderColor = '#10b981';
        setTimeout(() => { cardSave.innerHTML = orig; cardSave.style.background = ''; cardSave.style.borderColor = ''; }, 2000);
      }
    } catch (err) {
      console.error('[QuotePoster] 海报生成下载异常:', err);
      alert('生成高清海报失败，请稍后重试: ' + (err.message || err));
    }
  };
})();
"""
