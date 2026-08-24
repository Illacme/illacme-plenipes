/**
 * 💎 [V102.0] Illacme Plenipes License & Help Center UI Module (SPA Drag & Drop Engine)
 * 职责：治理中心“💎 授权帮助”分类及 3 大 Sub-Tab 动态拖拽与授权激活引擎。
 * 遵循 SOP-01 单文件 300 行上限规则。
 */

(function () {
    const licenseSubDescs = {
        activation: '💡 查看当前设备的硬件标识 (机器指纹)，或拖拽/粘贴许可证文件激活专业版功能。',
        comparison: '💡 查看免费社区版与高级专业版的核心功能对比说明。',
        docs: '💡 查阅快速上手教程、Obsidian 金库配置规范及常见问题排错指南。'
    };

    window.bindLicenseDragAndDrop = function () {
        const textarea = document.getElementById('license-text-input');
        if (!textarea || textarea.dataset.dragBound === 'true') return;
        textarea.dataset.dragBound = 'true';

        ['dragenter', 'dragover'].forEach(eventName => {
            textarea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                textarea.style.borderColor = 'var(--accent-primary, #00f2fe)';
                textarea.style.boxShadow = '0 0 16px rgba(0, 242, 255, 0.3)';
                textarea.style.background = 'rgba(0, 242, 255, 0.05)';
            }, false);
        });

        ['dragleave', 'dragend'].forEach(eventName => {
            textarea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                textarea.style.borderColor = 'var(--glass-border)';
                textarea.style.boxShadow = 'none';
                textarea.style.background = 'transparent';
            }, false);
        });

        textarea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            textarea.style.borderColor = 'var(--glass-border)';
            textarea.style.boxShadow = 'none';
            textarea.style.background = 'transparent';

            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length > 0) {
                const file = dt.files[0];
                const fileName = file.name || '';
                const lowerName = fileName.toLowerCase();
                const isValidLicFile = lowerName.endsWith('.lic') || lowerName.endsWith('.lic.txt') || lowerName.endsWith('.key') || lowerName.endsWith('.txt');

                if (!isValidLicFile) {
                    if (typeof showNotification === 'function') {
                        showNotification(`⚠️ 拖入的文件 [${fileName}] 格式不匹配！请拖入官方发放的 .lic 许可证文件`, 'warning');
                    } else {
                        alert(`⚠️ 拖入的文件 [${fileName}] 格式不匹配！请拖入官方发放的 .lic 许可证文件`);
                    }
                    return;
                }

                const reader = new FileReader();
                reader.onload = (evt) => {
                    textarea.value = evt.target.result;
                    if (typeof showNotification === 'function') {
                        showNotification(`📄 已成功装载许可证文件: ${fileName}`, 'info');
                    }
                };
                reader.readAsText(file);
            }
        }, false);
    };

    window.switchLicenseSubTab = function (subTab, btn) {
        window.currentActiveLicenseSubTab = subTab;
        const container = document.getElementById('license-sub-tab-bar');
        if (container) {
            const btns = container.querySelectorAll('.sub-tab-btn');
            btns.forEach(b => b.classList.remove('active'));
        }
        if (btn) {
            btn.classList.add('active');
        } else if (typeof event !== 'undefined' && event.currentTarget) {
            event.currentTarget.classList.add('active');
        }

        const panels = ['activation', 'comparison', 'docs'];
        panels.forEach(p => {
            const el = document.getElementById(`lic-panel-${p}`);
            if (el) el.style.display = (p === subTab) ? 'block' : 'none';
        });

        const descEl = document.getElementById('lic-sub-tab-desc');
        if (descEl) descEl.innerHTML = licenseSubDescs[subTab] || '';

        if (subTab === 'activation') {
            setTimeout(() => {
                if (typeof window.bindLicenseDragAndDrop === 'function') window.bindLicenseDragAndDrop();
            }, 50);
        }
    };

    window.renderLicenseCategory = function () {
        const activeSub = window.currentActiveLicenseSubTab || 'activation';
        const html = typeof window.renderLicenseCategoryHTML === 'function' 
            ? window.renderLicenseCategoryHTML(activeSub)
            : '<div class="category-header-banner">💎 授权与帮助中心</div>';

        setTimeout(() => {
            fetchLicenseDataAndUpdateDOM();
            if (activeSub === 'activation' && typeof window.bindLicenseDragAndDrop === 'function') {
                window.bindLicenseDragAndDrop();
            }
        }, 60);

        return html;
    };

    async function fetchLicenseDataAndUpdateDOM() {
        try {
            const res = await apiFetch('/api/governance/license/info');
            if (!res) return;

            const fpInput = document.getElementById('input-machine-fingerprint');
            if (fpInput) fpInput.value = res.fingerprint || 'UNKNOWN';

            const emblem = document.getElementById('lic-emblem-container');
            const badge = document.getElementById('lic-tier-badge');
            const verBadge = document.getElementById('lic-version-badge');
            const descEl = document.getElementById('lic-banner-desc');
            const pillsEl = document.getElementById('lic-feature-pills');
            const revokeBtn = document.getElementById('btn-revoke-license');
            const headerProBadge = document.getElementById('header-pro-badge');

            if (headerProBadge) {
                headerProBadge.innerText = res.is_licensed ? '💎 PRO' : '🌱 LITE';
                headerProBadge.className = res.is_licensed ? 'header-pro-badge pro-active' : 'header-pro-badge lite-active';
                headerProBadge.style.display = 'inline-flex';
            }

            if (verBadge && res.version) {
                const cleanVer = String(res.version).split('-')[0];
                verBadge.innerText = cleanVer.startsWith('v') || cleanVer.startsWith('V') ? cleanVer : `v${cleanVer}`;
            }

            if (res.is_licensed) {
                const tier = res.tier || 'PRO';
                if (tier === 'STANDARD') {
                    if (emblem) { emblem.innerText = '🚀'; emblem.style.background = 'linear-gradient(135deg, rgba(0, 242, 255, 0.18), rgba(0, 100, 255, 0.08))'; emblem.style.borderColor = 'rgba(0, 242, 255, 0.4)'; }
                    if (badge) { badge.innerText = '基础增强版'; badge.className = 'tier-tag tier-global'; badge.style.color = 'var(--neon-cyan, #00f2fe)'; }
                    if (descEl) descEl.innerHTML = `<div>🚀 已解锁基础增强版特权！支持 3 个出版品牌、3~5 个主流语种矩阵与子目录频道精准映射。</div><div style="margin-top: 6px; font-weight: 600; color: var(--accent-primary, #00f2fe); font-size: 0.78rem;">🔑 授权客户：${res.customer} <span style="opacity: 0.85; font-weight: normal;">(至 ${res.exp_date})</span></div>`;
                    if (pillsEl) pillsEl.innerHTML = `<span class="lic-pill-unlocked">✓ 工业级 AI 出版引擎</span><span class="lic-pill-unlocked">✓ Obsidian 双链全息图谱</span><span class="lic-pill-unlocked">✓ 创作中心灵感润色</span><span class="lic-pill-unlocked">✓ 3个独立品牌管理</span><span class="lic-pill-unlocked">✓ 3~5个主流语种翻译</span><span class="lic-pill-unlocked">✓ 📂 子目录频道映射</span><span class="lic-pill-unlocked">✓ ⚡ 双节点主备容灾</span><span class="lic-pill-locked">🔒 ♾️ 无限品牌 (专业版)</span><span class="lic-pill-locked">🔒 🌐 50+语种矩阵 (专业版)</span><span class="lic-pill-locked">🔒 🎭 频道方言风格 (专业版)</span>`;
                    if (revokeBtn) revokeBtn.style.display = 'inline-block';
                } else {
                    if (emblem) { emblem.innerText = '💎'; emblem.style.background = 'linear-gradient(135deg, rgba(0, 255, 170, 0.18), rgba(0, 242, 255, 0.08))'; emblem.style.borderColor = 'rgba(0, 255, 170, 0.4)'; }
                    if (badge) { badge.innerText = '高级专业版'; badge.className = 'tier-tag tier-global'; }
                    if (descEl) descEl.innerHTML = `<div>🚀 已解锁高级专业版全量特权！支持无限品牌隔离、50+ 语种多线程翻译矩阵与混合算力集群。</div><div style="margin-top: 6px; font-weight: 600; color: var(--accent-primary, #00f2fe); font-size: 0.78rem;">🔑 授权客户：${res.customer} <span style="opacity: 0.85; font-weight: normal;">(至 ${res.exp_date})</span></div>`;
                    if (pillsEl) pillsEl.innerHTML = `<span class="lic-pill-unlocked">✓ 工业级 AI 出版引擎</span><span class="lic-pill-unlocked">✓ Obsidian 双链全息图谱</span><span class="lic-pill-unlocked">✓ 创作中心灵感润色</span><span class="lic-pill-unlocked">✓ 算力节点灵活对接</span><span class="lic-pill-unlocked">✓ ♾️ 无限品牌独立隔离</span><span class="lic-pill-unlocked">✓ 🌐 50+语种矩阵分发</span><span class="lic-pill-unlocked">✓ 📂 子目录频道映射</span><span class="lic-pill-unlocked">✓ 🎭 频道专属方言风格</span><span class="lic-pill-unlocked">✓ ☁️ 算力集群自动容灾</span>`;
                    if (revokeBtn) revokeBtn.style.display = 'inline-block';
                }
            } else {
                if (emblem) { emblem.innerText = '🌱'; emblem.style.background = 'rgba(0, 242, 255, 0.08)'; emblem.style.borderColor = 'rgba(0, 242, 255, 0.25)'; }
                if (badge) { badge.innerText = '免费社区版'; badge.className = 'tier-tag tier-local'; }
                if (descEl) descEl.innerHTML = '✨ 免费社区版已包含完整 AI 创作润色、Obsidian 双链全息图谱与全自动静态出版引擎。激活增强版或专业版可进一步解封多品牌管理、多语种并行矩阵分发与子目录频道映射。';
                if (pillsEl) pillsEl.innerHTML = `<span class="lic-pill-unlocked">✓ 工业级 AI 出版引擎</span><span class="lic-pill-unlocked">✓ Obsidian 双链全息图谱</span><span class="lic-pill-unlocked">✓ 创作中心灵感润色</span><span class="lic-pill-unlocked">✓ 算力节点灵活对接</span><span class="lic-pill-unlocked">✓ 单品牌全渠道分发</span><span class="lic-pill-locked">🔒 3个独立品牌 (增强版)</span><span class="lic-pill-locked">🔒 多语种矩阵分发 (增强版)</span><span class="lic-pill-locked">🔒 子目录频道映射 (增强版)</span><span class="lic-pill-locked">🔒 频道专属方言风格 (专业版)</span><span class="lic-pill-locked">🔒 算力集群自动容灾 (专业版)</span>`;
                if (revokeBtn) revokeBtn.style.display = 'none';
            }
        } catch (err) { console.error('获取许可证信息失败:', err); }
    }
    window.fetchLicenseDataAndUpdateDOM = fetchLicenseDataAndUpdateDOM;

    window.refreshLicenseStatusWithFeedback = async function () {
        const btn = document.getElementById('btn-refresh-lic-status');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '⌛ 正在刷新...';
            btn.style.opacity = '0.75';
        }

        try {
            await fetchLicenseDataAndUpdateDOM();
            const emblem = document.getElementById('lic-emblem-container');
            if (emblem) {
                emblem.style.transform = 'scale(1.08)';
                emblem.style.boxShadow = '0 0 16px rgba(0, 242, 255, 0.4)';
                setTimeout(() => {
                    emblem.style.transform = 'scale(1)';
                    emblem.style.boxShadow = 'none';
                }, 400);
            }
            if (typeof showNotification === 'function') {
                showNotification('✨ 已完成最新授权状态探针校验与回显', 'info');
            }
        } catch (err) {
            console.error('刷新授权状态失败:', err);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '🔄 刷新授权状态';
                btn.style.opacity = '1';
            }
        }
    };

    window.checkAndUpdateHeaderProBadge = async function () {
        try {
            const res = await apiFetch('/api/governance/license/info');
            const headerProBadge = document.getElementById('header-pro-badge');
            if (headerProBadge && res) {
                if (!res.is_licensed) {
                    headerProBadge.innerText = '🌱 LITE';
                    headerProBadge.className = 'header-pro-badge lite-active';
                } else if (res.tier === 'STANDARD') {
                    headerProBadge.innerText = '🚀 PLUS';
                    headerProBadge.className = 'header-pro-badge pro-active';
                } else {
                    headerProBadge.innerText = '💎 PRO';
                    headerProBadge.className = 'header-pro-badge pro-active';
                }
                headerProBadge.style.display = 'inline-flex';
            }
        } catch (e) {}
    };

    document.addEventListener('DOMContentLoaded', () => {
        window.checkAndUpdateHeaderProBadge();
    });

    window.copyMachineFingerprint = function () {
        const input = document.getElementById('input-machine-fingerprint');
        if (!input) return;
        input.select();
        navigator.clipboard.writeText(input.value).then(() => {
            if (typeof showNotification === 'function') {
                showNotification('📋 已复制机器指纹至剪贴板', 'info');
            } else {
                alert('已复制机器指纹！');
            }
        }).catch(err => {
            console.error('复制失败:', err);
        });
    };

    window.submitLicenseActivation = async function () {
        const textInput = document.getElementById('license-text-input');
        if (!textInput || !textInput.value.trim()) {
            showNotification('请先粘贴或拖入有效的 .lic 许可证内容', 'warning');
            return;
        }

        const btn = document.getElementById('btn-activate-license');
        if (btn) { btn.disabled = true; btn.innerText = '⌛ 正在对正授权...'; }

        try {
            const res = await apiFetch('/api/governance/license/activate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ license_text: textInput.value.trim() })
            });

            if (res && (res.status === 'success' || res.success)) {
                showNotification(`🎉 ${res.message || '激活成功！已解锁高级专业版全量能力'}`, 'success');
                textInput.value = '';
                fetchLicenseDataAndUpdateDOM();
            } else {
                showNotification(`❌ ${res ? res.message : '激活失败，密钥不匹配'}`, 'error');
            }
        } catch (e) {
            showNotification(`❌ 激活开验抛出异常: ${e.message}`, 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerText = '🚀 验证并激活'; }
        }
    };

    window.revokeCurrentLicense = async function (evt) {
        if (evt) {
            evt.preventDefault();
            evt.stopPropagation();
        }

        const result = await Swal.fire({
            title: '确认解绑许可证？',
            text: '注销解绑后系统将切回【免费社区版 (LITE)】，原高级专业版功能将被锁定。是否确定操作？',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ff4d4d',
            cancelButtonColor: '#4a5568',
            confirmButtonText: '🔓 确认解绑',
            cancelButtonText: '取消',
            background: 'var(--glass-bg, #1a202c)',
            color: 'var(--text-main, #ffffff)',
            customClass: { popup: 'swal2-dark-popup' }
        });

        if (!result.isConfirmed) return;

        try {
            const res = await apiFetch('/api/governance/license/revoke', { method: 'POST' });
            if (res && (res.status === 'success' || res.success)) {
                showNotification(`🔓 ${res.message || '许可证已成功解绑，系统切回免费社区版 (LITE)'}`, 'info');
                fetchLicenseDataAndUpdateDOM();
            } else {
                const errMsg = res ? (res.message || res.error || '解绑拒绝') : '网络连接失败';
                showNotification(`❌ 解绑失败: ${errMsg}`, 'error');
            }
        } catch (e) {
            showNotification(`❌ 解绑请求异常: ${e.message}`, 'error');
        }
    };
})();
