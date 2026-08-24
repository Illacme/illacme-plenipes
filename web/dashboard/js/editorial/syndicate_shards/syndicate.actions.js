/**
 * 🛰️ [V120.0] Illacme Plenipes Article Syndication - Remote Actions & Modal Hub Shard
 * 职责：物理远程下架、本地物权解绑、单独平台重试推流、全局主权确认弹窗中枢。
 */

(function () {
    // 🛡️ [V120.0] 全局主权确认弹窗中枢 (Sovereign Action Confirm Modal Hub)
    // 彻底淘汰原生 confirm()/alert() 死穴逻辑，优先调起 Swal.fire，若无则注入 z-index 999999 的毛玻璃 Modal，永不受 DOM 刷写或焦点遮挡影响
    window.confirmSovereignAction = async function ({
        title = '⚠️ 物理安全确认',
        text = '确定要执行此物理操作吗？',
        icon = 'warning',
        confirmText = '确定执行',
        confirmColor = '#ff4d4f',
        cancelText = '取消'
    } = {}) {
        if (typeof window.Swal !== 'undefined' || typeof Swal !== 'undefined') {
            const swalInst = window.Swal || Swal;
            const res = await swalInst.fire({
                title: title,
                html: `<div style="font-size: 0.9rem; color: rgba(255,255,255,0.85); margin-top: 8px; line-height: 1.6;">${text}</div>`,
                icon: icon,
                showCancelButton: true,
                confirmButtonColor: confirmColor,
                cancelButtonColor: 'rgba(255, 255, 255, 0.15)',
                confirmButtonText: confirmText,
                cancelButtonText: cancelText,
                background: '#12131e',
                color: '#ffffff'
            });
            return res.isConfirmed;
        }

        return new Promise((resolve) => {
            const modalId = 'sovereign-confirm-modal-' + Date.now();
            const backdrop = document.createElement('div');
            backdrop.id = modalId;
            backdrop.style.cssText = `
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0, 0, 0, 0.82);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                z-index: 999999;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            backdrop.innerHTML = `
                <div class="glass-panel" style="width: 440px; max-width: 90vw; padding: 24px; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.2); background: rgba(18, 19, 30, 0.96); box-shadow: 0 20px 60px rgba(0,0,0,0.9); display: flex; flex-direction: column; gap: 16px;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px;">
                        ${title}
                    </div>
                    <div style="font-size: 0.88rem; color: rgba(255, 255, 255, 0.85); line-height: 1.6;">
                        ${text}
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px;">
                        <button type="button" id="${modalId}-cancel" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); color: #ccc; padding: 8px 16px; border-radius: 8px; font-size: 0.82rem; cursor: pointer;">${cancelText}</button>
                        <button type="button" id="${modalId}-confirm" style="background: ${confirmColor}; border: none; color: #fff; padding: 8px 18px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 14px ${confirmColor}55;">${confirmText}</button>
                    </div>
                </div>
            `;

            document.body.appendChild(backdrop);

            const close = (result) => {
                if (backdrop && backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
                resolve(result);
            };

            document.getElementById(`${modalId}-cancel`).onclick = () => close(false);
            document.getElementById(`${modalId}-confirm`).onclick = () => close(true);
        });
    };

    window.deleteRemoteArticle = async function (relPath, targetId) {
        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = langRadio ? langRadio.value : 'zh';

        const isConfirmed = await window.confirmSovereignAction({
            title: '🗑️ 物理远程下架确认',
            text: `确定要调用 <b>${targetId.toUpperCase()}</b> API 彻底远程下架该文章吗？<br><span style="color: #ff4d4f; font-size: 0.8rem; display: block; margin-top: 6px;">⚠️ 此操作将在对端社交平台物理销毁该文章，操作不可逆！</span>`,
            icon: 'warning',
            confirmText: '🗑️ 确认彻底下架',
            confirmColor: '#ff4d4f',
            cancelText: '取消'
        });
        if (!isConfirmed) return;

        try {
            const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
            const res = await fetchApi('/api/syndication/remote-action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rel_path: relPath, lang_code: selectedLang, target_id: targetId, action: 'delete' })
            });
            if (res && res.ok) {
                if (typeof window.showToast === 'function') window.showToast(`🗑️ ${res.message || '文章下架成功'}`, 'success');
                if (typeof window.updateSyndicatePlatformCards === 'function') {
                    await window.updateSyndicatePlatformCards(relPath);
                }
            } else {
                if (typeof window.showToast === 'function') window.showToast(`🛑 下架失败: ${res ? (res.error || res.detail) : '对端接口异常'}`, 'error');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 网络错误: ${e}`, 'error');
        }
    };

    window.unlinkRemoteArticle = async function (relPath, targetId) {
        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = langRadio ? langRadio.value : 'zh';

        const isConfirmed = await window.confirmSovereignAction({
            title: '🔗 本地物权解绑确认',
            text: `确定要解除本地与 <b>${targetId.toUpperCase()}</b> 的文章物权绑定吗？<br><span style="color: #00f2fe; font-size: 0.8rem; display: block; margin-top: 6px;">💡 注意：这仅会清空本地物权账本，不会删除对端社交平台上的已发布文章。</span>`,
            icon: 'question',
            confirmText: '🔗 确认解除绑定',
            confirmColor: '#3085d6',
            cancelText: '取消'
        });
        if (!isConfirmed) return;

        try {
            const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
            const res = await fetchApi('/api/syndication/remote-action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rel_path: relPath, lang_code: selectedLang, target_id: targetId, action: 'unlink' })
            });
            if (res && res.ok) {
                if (typeof window.showToast === 'function') window.showToast(`🔗 ${res.message || '已成功解绑'}`, 'info');
                if (typeof window.updateSyndicatePlatformCards === 'function') {
                    await window.updateSyndicatePlatformCards(relPath);
                }
            } else {
                if (typeof window.showToast === 'function') window.showToast(`🛑 解绑失败: ${res ? (res.error || res.detail) : '接口异常'}`, 'error');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 网络错误: ${e}`, 'error');
        }
    };

    window.retrySinglePlatform = async function (relPath, channelId) {
        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = langRadio ? langRadio.value : 'zh';

        if (typeof window.showToast === 'function') {
            window.showToast(`📡 正在向 [${channelId.toUpperCase()}] 发起单独重试推流...`, 'info');
        }

        try {
            const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
            await fetchApi(`/api/vault/re-dispatch/${encodeURIComponent(relPath)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_slot: selectedLang,
                    target_channel: channelId,
                    skip_syndication: false,
                    clear_cache: false
                })
            });

            if (typeof window.updateSyndicatePlatformCards === 'function') {
                await window.updateSyndicatePlatformCards(relPath);
            }
            const resultsEl = document.getElementById('syndicate-results-panel');
            if (resultsEl) {
                resultsEl.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (e) {
            if (typeof window.showToast === 'function') {
                window.showToast(`🛑 单独重试请求失败: ${e}`, 'error');
            }
        }
    };
})();
