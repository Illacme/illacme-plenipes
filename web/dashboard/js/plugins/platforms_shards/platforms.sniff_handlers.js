/**
 * ⚙️ [V87.1] Illacme Plenipes Plugins - Social Media Session Sniffing & Smart Header Parser Shard
 * 职责：本地活跃浏览器会话嗅探、整段 Request Headers / Cookie 智能正则提取与凭据双向回填 Handlers。
 * 🛡️ 遵循 SOP-01 规范与前端运行沙箱标准。
 */

(function () {
    'use strict';

    const _fetch = window.apiFetch || (async (url, init) => (await fetch(url, init)).json());

    // 通用字段回填与事件触发器
    function fillField(path, val) {
        if (!val || typeof document === 'undefined') return;
        const el = document.querySelector(`textarea[data-path="${path}"], input[data-path="${path}"], textarea[name="${path}"], input[name="${path}"]`);
        if (el) { el.value = val; el.dispatchEvent(new Event("input", { bubbles: true })); el.dispatchEvent(new Event("change", { bubbles: true })); }
        if (typeof window.updateConfigField === 'function') window.updateConfigField(path, val);
    }

    /**
     * 🪄 智能解析器：支持从整段 Request Headers 或杂乱 Cookie 字符串中精准提取目标渠道凭据
     */
    window.smartParsePlatformHeadersOrCookie = function (pluginId, rawInput) {
        if (!rawInput || typeof rawInput !== 'string') return null;
        let text = rawInput.trim();
        if (!text) return null;

        let cookieStr = "";
        // 1. 如果包含换行，解析多行 HTTP Request Headers
        if (text.includes('\n')) {
            const lines = text.split('\n');
            let foundCookieLine = false;
            for (let line of lines) {
                const trimmed = line.trim();
                const match = trimmed.match(/^[Cc]ookie:\s*(.+)$/i);
                if (match) {
                    cookieStr = match[1].trim();
                    foundCookieLine = true;
                    break;
                }
            }
            if (!foundCookieLine) {
                // 剔除常见的非 Cookie 请求头行 (如 Host:, User-Agent:, Accept: 等)
                const candidateLines = lines.filter(l => {
                    const clean = l.trim();
                    if (!clean) return false;
                    return !clean.match(/^(?:Accept|Accept-Encoding|Accept-Language|Cache-Control|Connection|Content-Length|Content-Type|Host|Origin|Referer|Sec-|Upgrade-Insecure-Requests|User-Agent):/i);
                });
                cookieStr = candidateLines.join('; ').trim();
            }
        } else {
            // 单行文本，若带有 Cookie: / cookie: 前缀则剔除
            const match = text.match(/^[Cc]ookie:\s*(.+)$/i);
            cookieStr = match ? match[1].trim() : text;
        }

        // 清洗首尾多余的分号与空格
        cookieStr = cookieStr.replace(/^;+|;+$/g, '').trim();

        const result = {
            pluginId: pluginId,
            cleanCookie: cookieStr,
            extracted: {}
        };

        const id = (pluginId || '').toLowerCase();
        if (id === 'bilibili') {
            const mSess = cookieStr.match(/(?:^|;\s*)SESSDATA=([^;]+)/i);
            const mJct = cookieStr.match(/(?:^|;\s*)bili_jct=([^;]+)/i);
            if (mSess) result.extracted.sessdata = decodeURIComponent(mSess[1].trim());
            if (mJct) result.extracted.bili_jct = decodeURIComponent(mJct[1].trim());
        } else if (id === 'xiaohongshu' || id === 'red') {
            const mA1 = cookieStr.match(/(?:^|;\s*)a1=([^;]+)/i);
            const mSession = cookieStr.match(/(?:^|;\s*)web_session=([^;]+)/i);
            if (mA1) result.extracted.a1 = mA1[1].trim();
            if (mSession) result.extracted.web_session = mSession[1].trim();
        } else if (id === 'zhihu') {
            const mZc0 = cookieStr.match(/(?:^|;\s*)z_c0="?([^;"]+)"?/i);
            if (mZc0) result.extracted.token = mZc0[1].trim();
            const mCol = text.match(/(?:zhihu\.com\/column\/|zhuanlan\.zhihu\.com\/)([a-zA-Z0-9_\-]+)/i);
            if (mCol) result.extracted.column_id = mCol[1].trim();
        } else if (id === 'juejin') {
            const mSession = cookieStr.match(/(?:^|;\s*)sessionid=([^;]+)/i);
            if (mSession) result.extracted.sessionid = mSession[1].trim();
        }

        return result;
    };

    /**
     * 🪄 应用智能解析结果并自动回填至对应表单
     */
    window.applySmartParsedCookie = function (pluginId, rawInput) {
        const parsed = window.smartParsePlatformHeadersOrCookie(pluginId, rawInput);
        if (!parsed || !parsed.cleanCookie) {
            if (window.showToast) window.showToast("⚠️ 未能从输入文本中识别出有效 Cookie 或凭证", "warning");
            return false;
        }

        const id = (pluginId || '').toLowerCase();
        let toastMsg = "";

        if (id === 'bilibili') {
            let filledCount = 0;
            if (parsed.extracted.sessdata) { fillField('syndication.bilibili.sessdata', parsed.extracted.sessdata); filledCount++; }
            if (parsed.extracted.bili_jct) { fillField('syndication.bilibili.bili_jct', parsed.extracted.bili_jct); filledCount++; }
            if (parsed.cleanCookie) fillField('syndication.bilibili.cookie', parsed.cleanCookie);
            if (filledCount === 2) toastMsg = "🎉 智能提取成功！已自动填入 SESSDATA 与 bili_jct。";
            else if (filledCount === 1) toastMsg = "⚠️ 提取完成：已填入部分凭据，缺少 " + (parsed.extracted.sessdata ? "bili_jct" : "SESSDATA") + "。";
            else toastMsg = "🟢 已清洗并填入 B站 Cookie 凭据。";
        } else if (id === 'xiaohongshu' || id === 'red') {
            fillField('syndication.xiaohongshu.cookie', parsed.cleanCookie);
            const hasA1 = !!parsed.extracted.a1, hasSession = !!parsed.extracted.web_session;
            if (hasA1 && hasSession) toastMsg = "🎉 小红书凭据清洗成功！已识别核心身份 (含 a1 及 web_session)。";
            else if (hasA1 || hasSession) toastMsg = "⚠️ 已填入 Cookie，但缺少关键字段 " + (hasA1 ? "web_session" : "a1") + "，易被风控拦截。";
            else toastMsg = "🟢 已清洗并填入小红书 Cookie 凭据。";
        } else if (id === 'zhihu') {
            fillField('syndication.zhihu.cookie', parsed.cleanCookie);
            if (parsed.extracted.token) fillField('syndication.zhihu.token', parsed.extracted.token);
            if (parsed.extracted.column_id) fillField('syndication.zhihu.column_id', parsed.extracted.column_id);
            if (parsed.extracted.token && parsed.extracted.column_id) {
                toastMsg = `🎉 知乎凭据清洗成功！已回填 z_c0 及专栏 ID: ${parsed.extracted.column_id}`;
            } else if (parsed.extracted.token) {
                toastMsg = "🎉 知乎 Cookie 清洗成功！已自动提取 z_c0 填入令牌项。";
            } else {
                toastMsg = "🟢 已清洗并填入知乎 Cookie 凭据。";
            }
        } else {
            fillField(`syndication.${id}.cookie`, parsed.cleanCookie);
            toastMsg = `🟢 已清洗并填入 ${id} 凭据。`;
        }

        if (window.showToast) {
            window.showToast(toastMsg, toastMsg.includes("🎉") ? "success" : (toastMsg.includes("⚠️") ? "warning" : "info"));
        }
        return true;
    };

    /**
     * ⚡ 文本框实时粘贴自愈清洗处理器
     */
    window.handleCookieInputAutoClean = function (pluginId, inputEl) {
        if (!inputEl) return;
        const val = inputEl.value || "";
        if (val.includes('\n') || /^[Cc]ookie:\s*/i.test(val.trim())) {
            window.applySmartParsedCookie(pluginId, val);
        }
    };

    /**
     * 🪄 弹出智能粘贴解析毛玻璃浮层
     */
    window.promptSmartPasteCookie = function (pluginId) {
        if (typeof document === 'undefined') return;
        let existing = document.getElementById('smart-paste-modal-overlay');
        if (existing) existing.remove();

        const nameMap = {
            'bilibili': 'Bilibili 专栏',
            'xiaohongshu': '小红书创作者平台',
            'red': '小红书创作者平台',
            'zhihu': '知乎专栏'
        };
        const titleName = nameMap[pluginId] || pluginId;

        const overlay = document.createElement('div');
        overlay.id = 'smart-paste-modal-overlay';
        overlay.style.cssText = 'position: fixed; inset: 0; z-index: 1000010; background: rgba(0, 0, 0, 0.65); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center;';
        overlay.innerHTML = `
            <div style="background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(0, 242, 254, 0.35); border-radius: 12px; width: 520px; max-width: 90vw; padding: 20px 24px; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6); color: #fff; font-family: inherit;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="font-weight: 600; font-size: 1rem; color: #00f2fe; display: flex; align-items: center; gap: 8px;">
                        <span>🪄 智能解析并回填凭据 (${titleName})</span>
                    </div>
                    <button type="button" onclick="document.getElementById('smart-paste-modal-overlay').remove()" style="background: transparent; border: none; color: #94a3b8; font-size: 1.2rem; cursor: pointer;">✕</button>
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5; margin-bottom: 12px;">
                    请在浏览器登录对应平台后，按 <b style="color: #cbd5e1;">F12</b> 打开控制台 -> <b style="color: #cbd5e1;">Network</b> -> 点击请求，复制整段 <b style="color: #38bdf8;">Cookie</b> 或完整的 <b style="color: #38bdf8;">Request Headers</b> 粘贴至下方：
                </div>
                <textarea id="smart-paste-input-raw" rows="6" placeholder="请在此处直接粘贴从浏览器复制的 Cookie 或 Request Headers..." style="width: 100%; box-sizing: border-box; background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; color: #fff; padding: 10px; font-size: 0.8rem; font-family: monospace; resize: vertical; outline: none;"></textarea>
                <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px;">
                    <button type="button" onclick="document.getElementById('smart-paste-modal-overlay').remove()" style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); color: #cbd5e1; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 0.82rem;">取消</button>
                    <button type="button" id="btn-do-smart-parse" style="background: #00f2fe; border: none; color: #0f172a; font-weight: 600; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 0.82rem;">一键识别并填入</button>
                </div>
            </div>`;
        document.body.appendChild(overlay);

        const btnDo = overlay.querySelector('#btn-do-smart-parse');
        const txtArea = overlay.querySelector('#smart-paste-input-raw');
        if (txtArea) txtArea.focus();

        if (btnDo && txtArea) {
            btnDo.onclick = function () {
                const rawVal = txtArea.value || "";
                if (!rawVal.trim()) {
                    if (window.showToast) window.showToast("⚠️ 请先粘贴内容", "warning");
                    return;
                }
                const success = window.applySmartParsedCookie(pluginId, rawVal);
                if (success) {
                    overlay.remove();
                }
            };
        }
    };

    /**
     * 🌐 原有 Chrome CDP 9222 调试端口免密嗅探 Handlers
     */
    window.autoSniffLocalCookie = async (pluginId = 'juejin', btn = null) => {
        if (!btn) return;
        const originalText = btn.innerText;
        btn.disabled = true;
        btn.innerText = "⏳ 正在探测当前浏览器会话...";
        try {
            const res = await _fetch("/api/plugins/auto-sniff-cookie", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plugin_id: pluginId })
            });
            if (res && res.success) {
                btn.innerText = "✅ 已自动抓取并绑定会话";
                btn.style.borderColor = "#10B981";
                btn.style.background = "rgba(16, 185, 129, 0.2)";

                if (pluginId === 'juejin') { fillField('syndication.juejin.cookie', res.cookie); if (res.api_token) fillField('syndication.juejin.api_token', res.api_token); }
                else if (pluginId === 'zhihu') { fillField('syndication.zhihu.cookie', res.cookie); if (res.token) fillField('syndication.zhihu.token', res.token); }
                else if (pluginId === 'bilibili') { fillField('syndication.bilibili.sessdata', res.sessdata); fillField('syndication.bilibili.bili_jct', res.bili_jct); if (res.cookie) fillField('syndication.bilibili.cookie', res.cookie); }
                else if (pluginId === 'xiaohongshu' || pluginId === 'red') { fillField('syndication.xiaohongshu.cookie', res.cookie); if (res.token) fillField('syndication.xiaohongshu.token', res.token); }
                else { fillField(`syndication.${pluginId}.cookie`, res.cookie); }

                const userName = res.user_name || "创作者";
                const uid = res.user_id ? ` (UID: ${res.user_id})` : "";
                if (window.showToast) window.showToast(res.message || `🎉 会话抓取成功！已自动绑定: ${userName}${uid}`, 'success');
                setTimeout(() => { if (typeof window.loadPluginsView === 'function') window.loadPluginsView(); }, 800);
            } else {
                btn.disabled = false;
                btn.innerText = originalText;
                const errMsg = res ? res.error : "未能探测到活跃页面";
                if (window.showToast) window.showToast(`⚠️ 自动抓取失败: ${errMsg}`, 'error');
            }
        } catch (err) {
            btn.disabled = false; btn.innerText = originalText;
            if (window.showToast) window.showToast(`❌ 请求异常: ${err.message || err}`, 'error');
        }
    };

    window.autoSniffJuejinCookie = (btn) => window.autoSniffLocalCookie('juejin', btn);

    /**
     * ⚡ 知乎专栏 URL 即时自愈处理器：用户粘贴完整链接时自动提取 Column ID
     */
    window.handleZhihuColumnInputAutoClean = function (inputEl) {
        if (!inputEl) return;
        const val = (inputEl.value || "").trim();
        const m = val.match(/(?:zhihu\.com\/column\/|zhuanlan\.zhihu\.com\/)([a-zA-Z0-9_\-]+)/i);
        if (m && m[1]) {
            inputEl.value = m[1];
            inputEl.dispatchEvent(new Event("input", { bubbles: true }));
            inputEl.dispatchEvent(new Event("change", { bubbles: true }));
            if (typeof window.updateConfigField === 'function') window.updateConfigField('syndication.zhihu.column_id', m[1]);
            if (window.showToast) window.showToast(`🎉 已智能提取知乎专栏 ID: ${m[1]}`, 'success');
        }
    };

    /**
     * 🌐 微信公众号公网出口 IP 探测与一键复制 Handler
     */
    window.fetchAndCopyOutboundIp = async function (btn) {
        if (!btn) return;
        const originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '⏳ 探测公网 IP...';
        try {
            const res = await _fetch('/api/system/outbound-ip?scope=domestic');
            if (res && res.ip) {
                btn.innerHTML = `🌐 出口 IP: <b>${res.ip}</b> (已复制)`;
                btn.style.borderColor = "#10B981"; btn.style.color = "#10B981"; btn.style.background = "rgba(16, 185, 129, 0.2)";
                btn.disabled = false;
                if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(res.ip);
                    if (window.showToast) window.showToast(`📋 已复制 IP [${res.ip}]！请在微信平台添加至白名单。`, 'success');
                } else if (window.showToast) {
                    window.showToast(`🌐 探测到公网 IP: ${res.ip}，请添加至微信白名单。`, 'info');
                }
            } else {
                btn.disabled = false; btn.innerHTML = originalHtml;
                if (window.showToast) window.showToast('⚠️ 未能检测到公网 IP，请检查网络连接', 'warning');
            }
        } catch (e) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
            if (window.showToast) window.showToast(`❌ 探测异常: ${e.message || e}`, 'error');
        }
    };

})();
