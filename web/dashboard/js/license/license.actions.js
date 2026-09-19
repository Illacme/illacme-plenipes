/**
 * 💎 [V102.0] Illacme Plenipes License & Help Center - Actions Shard
 * 职责：机器硬件指纹复制、许可证激活与许可证注销解绑交互 Actions。
 */

(function () {
    'use strict';

    window.copyMachineFingerprint = function () {
        const input = document.getElementById('input-machine-fingerprint');
        if (!input) return;
        input.select();
        navigator.clipboard.writeText(input.value).then(() => {
            if (typeof window.showToast === 'function') {
                window.showToast('📋 已复制机器指纹至剪贴板', 'info');
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
            if (typeof window.showToast === 'function') window.showToast('请先粘贴或拖入有效的 .lic 许可证内容', 'warning');
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
                if (typeof window.showToast === 'function') window.showToast(`🎉 ${res.message || '激活成功！已解锁高级专业版全量能力'}`, 'success');
                textInput.value = '';
                if (typeof window.fetchLicenseDataAndUpdateDOM === 'function') {
                    window.fetchLicenseDataAndUpdateDOM();
                }
            } else {
                if (typeof window.showToast === 'function') window.showToast(`❌ ${res ? res.message : '激活失败，密钥不匹配'}`, 'error');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`❌ 激活开验抛出异常: ${e.message}`, 'error');
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
                if (typeof window.showToast === 'function') window.showToast(`🔓 ${res.message || '许可证已成功解绑，系统切回免费社区版 (LITE)'}`, 'info');
                if (typeof window.fetchLicenseDataAndUpdateDOM === 'function') {
                    window.fetchLicenseDataAndUpdateDOM();
                }
            } else {
                const errMsg = res ? (res.message || res.error || '解绑拒绝') : '网络连接失败';
                if (typeof window.showToast === 'function') window.showToast(`❌ 解绑失败: ${errMsg}`, 'error');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`❌ 解绑请求异常: ${e.message}`, 'error');
        }
    };

})();
