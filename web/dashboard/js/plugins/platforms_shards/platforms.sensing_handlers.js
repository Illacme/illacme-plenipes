/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Sensing & Proxy Handlers Shard
 * 职责：Vercel OAuth 授权、 Cloudflare 项目回填、AWS/SFTP/Git 凭据自动感知及代理芯片绑定。
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

                        const tokenInput = document.querySelector('input[name="publish_control.direct_upload.vercel.token"]');
                        if (tokenInput && !tokenInput.value) {
                            tokenInput.value = status.token || "vercel_oauth_session";
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

window.applyCloudflareProjectSelection = (name, branch) => {
    const projInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.project_name"]');
    const branchInput = document.querySelector('input[name="publish_control.direct_upload.cloudflare_pages.branch"]');
    if (projInput) {
        projInput.value = name;
        projInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
    if (branchInput) {
        branchInput.value = branch;
        branchInput.dispatchEvent(new Event("input", { bubbles: true }));
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
            const akInput = document.querySelector(`input[name="${prefix}.access_key"]`);
            const skInput = document.querySelector(`input[name="${prefix}.secret_key"]`);
            const regionInput = document.querySelector(`input[name="${prefix}.region"]`);

            if (akInput) {
                akInput.value = res.access_key || '';
                akInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (skInput) {
                skInput.value = res.secret_key || '';
                skInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (regionInput && res.region) {
                regionInput.value = res.region;
                regionInput.dispatchEvent(new Event('input', { bubbles: true }));
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
            const pkInput = document.querySelector('textarea[name="publish_control.direct_upload.sftp.private_key"]');
            if (pkInput) {
                pkInput.value = res.private_key_path || '';
                pkInput.dispatchEvent(new Event('input', { bubbles: true }));
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
            const nameInput = document.querySelector(`input[name="${pathPrefix}.git_user_name"]`);
            const emailInput = document.querySelector(`input[name="${pathPrefix}.git_user_email"]`);

            let filledCount = 0;
            if (nameInput && res.name) {
                nameInput.value = res.name;
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                filledCount++;
            }
            if (emailInput && res.email) {
                emailInput.value = res.email;
                emailInput.dispatchEvent(new Event('input', { bubbles: true }));
                filledCount++;
            }

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

window.applyProxyPreset = (val, btn) => {
    let proxyInput = null;
    if (btn) {
        const container = btn.closest('.setting-control') || btn.closest('.setting-row');
        if (container) proxyInput = container.querySelector('input');
    }
    if (!proxyInput) {
        const drawer = document.getElementById('plugin-drawer');
        if (drawer) {
            proxyInput = drawer.querySelector('input[data-path*="proxy"], input[name*="proxy"]');
        }
    }
    if (proxyInput) {
        proxyInput.value = val;
        proxyInput.dispatchEvent(new Event('input', { bubbles: true }));
        if (window.showToast) window.showToast(`已快捷回填代理设置: ${val}`, 'success');
    }
};

window.renderProxyPresetsHtml = () => {
    return `
        <div class="proxy-preset-chips" style="width: 100%; margin-top: 8px; padding-top: 6px; border-top: 1px dashed rgba(255, 255, 255, 0.1); display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 0.7rem; color: var(--text-dim); font-weight: 600;">⚡ 快捷代理预设:</span>
            <button type="button" onclick="window.applyProxyPreset('http://127.0.0.1:7890', this)" style="font-size: 0.68rem; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); color: var(--neon-cyan); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 242, 255, 0.2)'" onmouseout="this.style.background='rgba(0, 242, 255, 0.08)'">Clash (7890)</button>
            <button type="button" onclick="window.applyProxyPreset('http://127.0.0.1:10808', this)" style="font-size: 0.68rem; background: rgba(163, 76, 255, 0.08); border: 1px solid rgba(163, 76, 255, 0.25); color: var(--accent-primary); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(163, 76, 255, 0.2)'" onmouseout="this.style.background='rgba(163, 76, 255, 0.08)'">V2RayN (10808)</button>
            <button type="button" onclick="window.applyProxyPreset('direct', this)" style="font-size: 0.68rem; background: rgba(0, 255, 136, 0.08); border: 1px solid rgba(0, 255, 136, 0.25); color: #00ff88; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 255, 136, 0.2)'" onmouseout="this.style.background='rgba(0, 255, 136, 0.08)'">🌐 物理直连 (direct)</button>
        </div>
    `;
};

window.focusErrorField = (fieldName) => {
    const drawer = document.getElementById('plugin-drawer');
    if (!drawer) return;
    let target = drawer.querySelector(`[name*="${fieldName}"]`) || drawer.querySelector(`[id*="${fieldName}"]`);
    if (!target) {
        const allInputs = Array.from(drawer.querySelectorAll('input, select, textarea'));
        target = allInputs.find(i => (i.name || i.id || '').toLowerCase().includes(fieldName.toLowerCase()));
    }
    if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        target.focus();
        target.style.transition = 'all 0.3s';
        target.style.outline = '2px solid #ff4d4d';
        target.style.boxShadow = '0 0 15px rgba(255, 77, 77, 0.6)';
        setTimeout(() => {
            target.style.outline = '';
            target.style.boxShadow = '';
        }, 2500);
        if (window.showToast) window.showToast(`已为您高亮闪烁定位至参数: ${fieldName}`, 'info');
    }
};
