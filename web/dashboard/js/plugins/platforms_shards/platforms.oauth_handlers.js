/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - OAuth & Sensing Handlers Shard
 * 职责：CLI 唤醒免密授权 (Cloudflare, Netlify, Vercel, Firebase) 与本地凭据感应 (Git, AWS, SFTP) 交互 Handlers。
 */

window.triggerGithubSSHCheck = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在探测 SSH...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "正在探测您的本地 SSH 与 GitHub 服务的连通情况...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/github/ssh-status');
        if (res && res.ssh_ok) {
            infoEl.style.color = '#10B981';
            infoEl.innerHTML = `✅ <b>探测成功！</b>检测到本地 SSH 已打通 GitHub (<span style="color:#fff">账户: ${res.username}</span>)。建议您优先使用 SSH 协议的 Repo URL，此令牌 (Token) 项可留空！`;
            btn.innerText = "🔑 SSH 已打通";
            btn.style.borderColor = '#10B981';
            btn.style.background = 'rgba(16, 185, 129, 0.15)';
        } else {
            infoEl.style.color = '#F59E0B';
            infoEl.innerText = `⚠️ 未能打通本地 SSH 免密: ${res ? res.message : "连接失败"}。建议您使用上方「官方一键创建」生成 Token 填入。`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 探测发生异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerFirebaseOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "已尝试在后台拉取 Firebase CLI 登录流，请在浏览器中确认授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/firebase/oauth-login', { method: 'POST' });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待本地凭证同步... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc('/api/plugins/firebase/oauth-status');
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = '#10B981';
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.username}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = '#10B981';
                        btn.style.background = 'rgba(16, 185, 129, 0.15)';

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.firebase.token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = status.token || "firebase_oauth_session";
                            tokenInput.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        infoEl.style.color = '#EF4444';
                        infoEl.innerText = "❌ 授权探测超时，请检查浏览器是否正常弹出并登录，或者选择手动粘贴 Token 填入。";
                        btn.disabled = false;
                        btn.innerText = originalText;
                    }
                } catch (probeErr) { }
            }, 2000);
        } else {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = `❌ 无法拉取授权: ${res ? res.message : "未知错误"}`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerCloudflareOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest(".api-token-helper");
    const infoEl = container.querySelector(".oauth-status-info");
    infoEl.style.display = "block";
    infoEl.style.color = "var(--neon-cyan)";
    infoEl.innerText = "已尝试在后台拉取 Cloudflare OAuth 授权页，请在弹出的系统浏览器中点击「Authorize」完成授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc("/api/plugins/cloudflare/oauth-login", { method: "POST" });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待浏览器授权确认... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc("/api/plugins/cloudflare/oauth-status");
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = "#10B981";
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.email || status.account_name}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = "#10B981";
                        btn.style.background = "rgba(16, 185, 129, 0.15)";

                        if (status.account_id) {
                            const accInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.account_id"]');
                            if (accInput) {
                                accInput.value = status.account_id;
                                accInput.dispatchEvent(new Event("input", { bubbles: true }));
                            }
                        }

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = "wrangler_oauth_session";
                            tokenInput.dispatchEvent(new Event("input", { bubbles: true }));
                        }

                        if (status.projects && status.projects.length > 0) {
                            const projInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.project_name"]');
                            const branchInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.branch"]');

                            if (status.projects.length === 1) {
                                const p = status.projects[0];
                                if (projInput) {
                                    projInput.value = p.name;
                                    projInput.dispatchEvent(new Event("input", { bubbles: true }));
                                }
                                if (branchInput && p.branch) {
                                    branchInput.value = p.branch;
                                    branchInput.dispatchEvent(new Event("input", { bubbles: true }));
                                }
                                if (window.showToast) window.showToast(`🎉 已自动填充项目名称 ${p.name} 及部署分支 ${p.branch}！`, "success");
                            } else {
                                let html = `<div class="quick-proj-selector" style="margin-top: 8px; font-size: 0.7rem; color: var(--text-dim);">`;
                                html += `💡 发现多个 Pages 项目，点击可一键自动回填：<br/>`;
                                for (let p of status.projects) {
                                    html += `<span class="helper-btn" onclick="window.applyCloudflareProjectSelection('${p.name}', '${p.branch || "production"}')" style="margin: 4px 4px 0 0; padding: 2px 6px !important; display: inline-flex !important; font-size: 0.65rem !important;">${p.name} (${p.branch || "production"})</span>`;
                                }
                                html += `</div>`;
                                infoEl.innerHTML += html;
                            }
                        }
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        infoEl.style.color = "#EF4444";
                        infoEl.innerText = "❌ 授权探测超时，请检查浏览器是否正常弹出，或者选择手动一键创建 Token 粘贴填入。";
                        btn.disabled = false;
                        btn.innerText = originalText;
                    }
                } catch (probeErr) { }
            }, 2000);
        } else {
            infoEl.style.color = "#EF4444";
            infoEl.innerText = `❌ 无法拉取授权页面: ${res ? res.message : "未知错误"}`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = "#EF4444";
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerNetlifyOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest(".api-token-helper");
    const infoEl = container.querySelector(".oauth-status-info");
    infoEl.style.display = "block";
    infoEl.style.color = "var(--neon-cyan)";
    infoEl.innerText = "已尝试在后台拉起 Netlify OAuth 授权页，请在弹出的系统浏览器中点击「Authorize」完成授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc("/api/plugins/netlify/oauth-login", { method: "POST" });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待浏览器授权确认... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc("/api/plugins/netlify/oauth-status");
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = "#10B981";
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.email || status.name}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = "#10B981";
                        btn.style.background = "rgba(16, 185, 129, 0.15)";

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.netlify.auth_token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = status.auth_token || "netlify_oauth_session";
                            tokenInput.dispatchEvent(new Event("input", { bubbles: true }));
                        }
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        infoEl.style.color = "#EF4444";
                        infoEl.innerText = "❌ 授权探测超时，请检查浏览器是否正常弹出，或者选择手动一键创建 Token 粘贴填入。";
                        btn.disabled = false;
                        btn.innerText = originalText;
                    }
                } catch (probeErr) { }
            }, 2000);
        } else {
            infoEl.style.color = "#EF4444";
            infoEl.innerText = `❌ 无法拉取授权页面: ${res ? res.message : "未知错误"}`;
            btn.disabled = false;
            btn.innerText = originalText;
        }
    } catch (err) {
        infoEl.style.color = "#EF4444";
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        btn.disabled = false;
        btn.innerText = originalText;
    }
};
