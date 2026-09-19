/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Social Media Session Sniffing Handlers Shard
 * 职责：本地活跃浏览器会话探测与 Cookie 凭据自动嗅探感应交互 Handlers（稀土掘金、知乎、Bilibili 等）。
 */

(function () {
    'use strict';

    const _fetch = window.apiFetch || (async (url, init) => (await fetch(url, init)).json());

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

                const fillField = (path, val) => {
                    if (!val) return;
                    const el = document.querySelector(`textarea[data-path="${path}"], input[data-path="${path}"], textarea[name="${path}"], input[name="${path}"]`);
                    if (el) {
                        el.value = val;
                        el.dispatchEvent(new Event("input", { bubbles: true }));
                        el.dispatchEvent(new Event("change", { bubbles: true }));
                    }
                    if (typeof window.updateConfigField === 'function') window.updateConfigField(path, val);
                };

                if (pluginId === 'juejin') {
                    fillField('syndication.juejin.cookie', res.cookie);
                    if (res.api_token) fillField('syndication.juejin.api_token', res.api_token);
                } else if (pluginId === 'zhihu') {
                    fillField('syndication.zhihu.cookie', res.cookie);
                    if (res.token) fillField('syndication.zhihu.token', res.token);
                } else if (pluginId === 'bilibili') {
                    fillField('syndication.bilibili.sessdata', res.sessdata);
                    fillField('syndication.bilibili.bili_jct', res.bili_jct);
                    if (res.cookie) fillField('syndication.bilibili.cookie', res.cookie);
                } else {
                    fillField(`syndication.${pluginId}.cookie`, res.cookie);
                }

                const userName = res.user_name || "创作者";
                const uid = res.user_id ? ` (UID: ${res.user_id})` : "";
                if (window.showToast) window.showToast(res.message || `🎉 会话抓取成功！已自动绑定: ${userName}${uid}`, 'success');
                setTimeout(() => { if (typeof window.loadPluginsView === 'function') window.loadPluginsView(); }, 800);
            } else {
                btn.disabled = false;
                btn.innerText = originalText;
                const errMsg = res ? res.error : "未能探测到活跃页面";
                if (window.showToast) window.showToast(`⚠️ 自动抓取失败: ${errMsg}`, 'error');
                else alert(`⚠️ 自动抓取失败: ${errMsg}`);
            }
        } catch (err) {
            btn.disabled = false;
            btn.innerText = originalText;
            if (window.showToast) window.showToast(`❌ 请求异常: ${err.message || err}`, 'error');
            else alert(`❌ 请求异常: ${err.message || err}`);
        }
    };

    window.autoSniffJuejinCookie = (btn) => window.autoSniffLocalCookie('juejin', btn);

})();
