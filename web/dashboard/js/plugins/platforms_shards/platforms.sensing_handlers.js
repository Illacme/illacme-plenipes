/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Sensing & Proxy Handlers Shard
 * 职责：Vercel OAuth 授权、 Cloudflare 项目回填、AWS/SFTP/Git 凭据自动感知与表单错误定位。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.triggerVercelOAuthLogin = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在唤醒浏览器...";

    const container = btn.closest(".api-token-helper");
    const infoEl = container.querySelector(".oauth-status-info");
    infoEl.style.display = "block";
    infoEl.style.color = "var(--neon-cyan)";
    infoEl.innerText = "已尝试在后台拉起 Vercel OAuth 授权页，请在弹出的系统浏览器中点击「Authorize」完成授权...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc("/api/plugins/vercel/oauth-login", { method: "POST" });
        if (res && res.success) {
            let attempts = 0;
            const maxAttempts = 30;
            const interval = setInterval(async () => {
                attempts++;
                infoEl.innerText = `⏳ 正在等待浏览器授权确认... (已等待 ${attempts * 2}s)`;

                try {
                    const status = await fetchFunc("/api/plugins/vercel/oauth-status");
                    if (status && status.logged_in) {
                        clearInterval(interval);
                        infoEl.style.color = "#10B981";
                        infoEl.innerHTML = `✅ <b>授权成功！</b>已连接账户: <span style="color:#fff">${status.email || status.username}</span>`;
                        btn.innerText = "🔑 授权成功";
                        btn.style.borderColor = "#10B981";
                        btn.style.background = "rgba(16, 185, 129, 0.15)";

                        const tokenInput = document.querySelector('input[data-path="publish_control.direct_upload.vercel.token"], input[name="publish_control.direct_upload.vercel.token"], #cfg-publish_control-direct_upload-vercel-token');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = status.token || "vercel_oauth_session";
                            tokenInput.dispatchEvent(new Event("input", { bubbles: true }));
                            tokenInput.dispatchEvent(new Event("change", { bubbles: true }));
                        }
                        if (typeof window.updateConfigField === 'function') {
                            window.updateConfigField('publish_control.direct_upload.vercel.token', status.token || "vercel_oauth_session");
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

window.applyCloudflareProjectSelection = (name, branch) => {
    const projInput = document.querySelector('input[data-path="publish_control.direct_upload.cloudflare_pages.project_name"], input[name="publish_control.direct_upload.cloudflare_pages.project_name"], #cfg-publish_control-direct_upload-cloudflare_pages-project_name');
    const branchInput = document.querySelector('input[data-path="publish_control.direct_upload.cloudflare_pages.branch"], input[name="publish_control.direct_upload.cloudflare_pages.branch"], #cfg-publish_control-direct_upload-cloudflare_pages-branch');
    if (projInput) {
        projInput.value = name;
        projInput.dispatchEvent(new Event("input", { bubbles: true }));
        projInput.dispatchEvent(new Event("change", { bubbles: true }));
    }
    if (branchInput) {
        branchInput.value = branch;
        branchInput.dispatchEvent(new Event("input", { bubbles: true }));
        branchInput.dispatchEvent(new Event("change", { bubbles: true }));
    }
    if (typeof window.updateConfigField === 'function') {
        window.updateConfigField('publish_control.direct_upload.cloudflare_pages.project_name', name);
        window.updateConfigField('publish_control.direct_upload.cloudflare_pages.branch', branch);
    }
    if (window.showToast) window.showToast(`已一键回填项目：${name}！`, "success");
};

window.triggerAWSCredentialsSense = async (btn, prefix) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在读取本地凭证...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "正在尝试读取本地 ~/.aws/credentials 与 config ...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/aws/credentials-status');
        if (res && res.logged_in) {
            const prefixDash = prefix.replace(/\./g, '-');
            const akInput = document.querySelector(`input[data-path="${prefix}.access_key"], input[name="${prefix}.access_key"], #cfg-${prefixDash}-access_key`);
            const skInput = document.querySelector(`input[data-path="${prefix}.secret_key"], input[name="${prefix}.secret_key"], #cfg-${prefixDash}-secret_key`);
            const regionInput = document.querySelector(`input[data-path="${prefix}.region"], input[name="${prefix}.region"], #cfg-${prefixDash}-region`);

            if (akInput) {
                akInput.value = res.access_key || '';
                akInput.dispatchEvent(new Event('input', { bubbles: true }));
                akInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (skInput) {
                skInput.value = res.secret_key || '';
                skInput.dispatchEvent(new Event('input', { bubbles: true }));
                skInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (regionInput && res.region) {
                regionInput.value = res.region;
                regionInput.dispatchEvent(new Event('input', { bubbles: true }));
                regionInput.dispatchEvent(new Event('change', { bubbles: true }));
            }

            if (typeof window.updateConfigField === 'function') {
                if (res.access_key) window.updateConfigField(`${prefix}.access_key`, res.access_key);
                if (res.secret_key) window.updateConfigField(`${prefix}.secret_key`, res.secret_key);
                if (res.region) window.updateConfigField(`${prefix}.region`, res.region);
            }

            infoEl.style.color = '#10B981';
            infoEl.innerText = "🟢 本地 AWS 凭据感应回填成功！已自动填充密钥与区域。";
            if (window.showToast) window.showToast("本地 AWS 凭据一键免密授权成功！", "success");
        } else {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = "❌ 未检测到本地有效的 ~/.aws/credentials 配置文件。";
            if (window.showToast) window.showToast("未检测到本地 AWS 配置，请手动填写", "warning");
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerSFTPSensing = async (btn) => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在检索 SSH 密钥...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container.querySelector('.oauth-status-info');
    infoEl.style.display = 'block';
    infoEl.style.color = 'var(--neon-cyan)';
    infoEl.innerText = "正在扫描本地 ~/.ssh 目录下的可用私钥...";

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/plugins/sftp/ssh-status');
        if (res && res.success) {
            const pkInput = document.querySelector('textarea[data-path="publish_control.direct_upload.sftp.private_key"], textarea[name="publish_control.direct_upload.sftp.private_key"], #cfg-publish_control-direct_upload-sftp-private_key');
            if (pkInput) {
                pkInput.value = res.private_key_path || '';
                pkInput.dispatchEvent(new Event('input', { bubbles: true }));
                pkInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (typeof window.updateConfigField === 'function' && res.private_key_path) {
                window.updateConfigField('publish_control.direct_upload.sftp.private_key', res.private_key_path);
            }
            infoEl.style.color = '#10B981';
            infoEl.innerText = `🟢 成功感应到本地 SSH 私钥 (${res.key_name})！路径已自动回填。`;
            if (window.showToast) window.showToast(`SSH 密钥路径感应填充成功！`, "success");
        } else {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = `❌ 感应失败: ${res ? res.message : "未找到可用私钥"}`;
            if (window.showToast) window.showToast("未感应到本地常用 SSH 私钥", "warning");
        }
    } catch (err) {
        infoEl.style.color = '#EF4444';
        infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
};

window.triggerGitCredentialsSense = async (btn, pathPrefix = 'publish_control.direct_upload.github_pages') => {
    if (!btn) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 正在感应 Git 凭据...";

    const container = btn.closest('.api-token-helper');
    const infoEl = container ? container.querySelector('.oauth-status-info') : null;
    if (infoEl) {
        infoEl.style.display = 'block';
        infoEl.style.color = 'var(--neon-cyan)';
        infoEl.innerText = "正在读取本地系统的 git config --global 身份参数...";
    }

    const fetchFunc = window.apiFetch || (async (url, init) => {
        const r = await fetch(url, init);
        return r.json();
    });

    try {
        const res = await fetchFunc('/api/system/sensing/git', { method: 'POST' });
        if (res && res.success) {
            // [Fix] 多选择器即时覆盖：data-path, id (cfg-xxx), name
            const prefixDash = pathPrefix.replace(/\./g, '-');
            const allNameInputs = document.querySelectorAll(`input[data-path="${pathPrefix}.git_user_name"], input[name="${pathPrefix}.git_user_name"], #cfg-${prefixDash}-git_user_name, input[id*="${prefixDash}-git_user_name"]`);
            const allEmailInputs = document.querySelectorAll(`input[data-path="${pathPrefix}.git_user_email"], input[name="${pathPrefix}.git_user_email"], #cfg-${prefixDash}-git_user_email, input[id*="${prefixDash}-git_user_email"]`);

            let filledCount = 0;
            allNameInputs.forEach(nameInput => {
                if (res.name) {
                    nameInput.value = res.name;
                    nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                    nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                    filledCount++;
                }
            });
            allEmailInputs.forEach(emailInput => {
                if (res.email) {
                    emailInput.value = res.email;
                    emailInput.dispatchEvent(new Event('input', { bubbles: true }));
                    emailInput.dispatchEvent(new Event('change', { bubbles: true }));
                    filledCount++;
                }
            });

            // 2. 深度同步写入 settingsData 与 dirty tracking
            try {
                if (typeof window.updateConfigField === 'function') {
                    if (res.name) window.updateConfigField(`${pathPrefix}.git_user_name`, res.name);
                    if (res.email) window.updateConfigField(`${pathPrefix}.git_user_email`, res.email);
                }
                const parts = pathPrefix.split('.');
                let cur = window.settingsData = window.settingsData || {};
                for (let i = 0; i < parts.length; i++) {
                    if (!cur[parts[i]]) cur[parts[i]] = {};
                    if (i < parts.length - 1) {
                        cur = cur[parts[i]];
                    } else {
                        if (res.name)  cur[parts[i]].git_user_name  = res.name;
                        if (res.email) cur[parts[i]].git_user_email = res.email;
                    }
                }
            } catch(e) { /* settingsData 写入失败不阻断流程 */ }

            if (infoEl) {
                infoEl.style.color = '#10B981';
                infoEl.innerHTML = `🟢 <b>成功感应本地 Git 凭据！</b> 已填入: <span style="color:#fff">${res.name || '默认'} &lt;${res.email || '未设置'}&gt;</span>`;
            }
            if (window.showToast) window.showToast(`已成功自动感知并填入 ${filledCount} 项 Git 凭据！`, "success");

        } else {
            if (infoEl) {
                infoEl.style.color = '#EF4444';
                infoEl.innerText = `❌ 感应失败: ${res ? res.message : "无法拉取 Git 凭据"}`;
            }
            if (window.showToast) window.showToast("未探测到有效的系统全局 Git user.name/email", "warning");
        }
    } catch (err) {
        if (infoEl) {
            infoEl.style.color = '#EF4444';
            infoEl.innerText = `❌ 请求异常: ${err.message || err}`;
        }
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
};
