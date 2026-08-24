/**
 * 🛰️ [V105.0] Illacme Plenipes Plugin Editor - Global Driver & Brand State Shard
 * 职责：全局驱动启停开关、物理链路校验拦截与品牌激活互斥防护逻辑。
 */

(function () {
    window.isPluginActiveInCurrentBrand = (id, category) => {
        const cfg = window.settingsData || {};
        if (category === 'notification') {
            const isSelfEnabled = !!(cfg.publish_control?.webhook_endpoints?.[id]?.enabled);
            if (!isSelfEnabled && id === 'generic_webhook') {
                return !!(cfg.publish_control?.webhook_endpoints?.['generic']?.enabled);
            }
            return isSelfEnabled;
        }
        if (category === 'hosting') {
            return !!(cfg.publish_control?.direct_upload?.[id]?.enabled);
        }
        if (category === 'publisher') {
            return !!(cfg.syndication?.[id]?.enabled);
        }
        if (category === 'image_hosting') {
            return !!(cfg.image_hosting?.[id]?.enabled || (cfg.image_hosting?.provider === id));
        }
        const p = window.allPlugins ? window.allPlugins.find(x => x.id === id && (!category || x.category === category)) : null;
        return !!(p && p.is_in_use);
    };

    window.handleGlobalDriverToggle = async (id, el, category) => {
        const checked = el ? el.checked : false;
        const p = window.allPlugins ? window.allPlugins.find(x => x.id === id && (!category || x.category === category)) : null;
        const headerStatusLabel = document.getElementById('header-toggle-status-label');

        if (checked) {
            const needsProbe = ['protocol', 'publisher', 'hosting', 'image_hosting', 'notification'].includes(category);
            const isPassed = !!(window.probePassState && window.probePassState[id] === true);

            if (needsProbe && !isPassed) {
                if (el) el.checked = false;
                if (headerStatusLabel) {
                    headerStatusLabel.textContent = '⚪ 全局已暂停';
                    headerStatusLabel.style.color = 'var(--text-dim)';
                }

                setTimeout(() => {
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            title: '🚨 无法开启全局驱动',
                            html: `插件 [<b>${p?.name || id}</b>] 尚未通过物理连通性校验。<br><br><span style="color:#00f2ff; font-size:0.85rem;">💡 请先点击抽屉底部的 <b>「🔌 测试连接」</b> 完成链路验证！</span>`,
                            icon: 'warning',
                            allowOutsideClick: false,
                            allowEscapeKey: true,
                            confirmButtonText: '⚡ 立即测试连通性',
                            showCancelButton: true,
                            cancelButtonText: '取消',
                            background: 'var(--card-bg)',
                            color: 'var(--text-bright)',
                            confirmButtonColor: 'var(--accent-secondary)'
                        }).then((r) => {
                            if (r.isConfirmed && typeof window.triggerPluginDryRun === 'function') {
                                window.triggerPluginDryRun(id);
                            }
                        });
                    } else if (window.showToast) {
                        window.showToast("🚨 请先点击「🔌 测试连接」完成链路验证", "error");
                    } else {
                        alert(`🔒 连通性未校验: 插件 [${p?.name || id}] 尚未通过物理连通性校验，请先完成测试连接。`);
                    }
                }, 30);
                return;
            }

            if (headerStatusLabel) {
                headerStatusLabel.textContent = '🟢 全局已启用';
                headerStatusLabel.style.color = 'var(--neon-cyan)';
            }
        } else {
            const isActiveInBrand = window.isPluginActiveInCurrentBrand(id, category);
            if (isActiveInBrand) {
                if (el) el.checked = true;
                if (headerStatusLabel) {
                    headerStatusLabel.textContent = '🟢 全局已启用';
                    headerStatusLabel.style.color = 'var(--neon-cyan)';
                }

                setTimeout(() => {
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            title: '⚠️ 物理锁定',
                            text: '当前品牌已激活并正在使用此功能，禁止关闭全局物理驱动！如需停用，请先关闭当前品牌的“品牌激活使用”开关。',
                            icon: 'warning',
                            allowOutsideClick: false,
                            allowEscapeKey: true,
                            background: 'var(--card-bg)',
                            color: 'var(--text-bright)',
                            confirmButtonText: '确定'
                        });
                    } else {
                        alert('⚠️ 物理锁定: 当前品牌已激活并正在使用此功能，禁止关闭全局物理驱动！如需停用，请先关闭当前品牌的“品牌激活使用”开关。');
                    }
                }, 30);
                return;
            }

            if (headerStatusLabel) {
                headerStatusLabel.textContent = '⚪ 全局已暂停';
                headerStatusLabel.style.color = 'var(--text-dim)';
            }
        }

        if (typeof window.togglePlugin === 'function') {
            await window.togglePlugin(id, checked, category);
        }
    };
})();
