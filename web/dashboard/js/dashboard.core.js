/**
 * 🚀 Illacme Plenipes Dashboard Core Command Module
 * 职责：核心指挥覆盖层切换、印记上下文下拉绑定，及全球出版点火链路。
 */

// 1. 核心指挥中枢控制 (全局单例)
window.toggleHub = (forceState) => {
    const hub = document.getElementById('command-hub-overlay');
    if (!hub) return;

    // 强制状态或切换
    if (forceState === 'show') {
        hub.style.display = 'flex';
    } else if (forceState === 'hide') {
        hub.style.display = 'none';
    } else {
        const isHidden = window.getComputedStyle(hub).display === 'none';
        hub.style.display = isHidden ? 'flex' : 'none';
    }
};

window.toggleImprintDropdown = (e) => {
    if (e) e.stopPropagation();
    const dropdown = document.getElementById('imprint-dropdown');
    if (!dropdown) return;
    const isHidden = dropdown.style.display === 'none';
    dropdown.style.display = isHidden ? 'block' : 'none';
    if (isHidden && typeof renderImprintDropdown === 'function') renderImprintDropdown();
};

// 🛰️ [V55.1] 核级事件委派：确保指挥中心关闭按钮在任何层级冲突下都能被捕获
document.addEventListener('click', (e) => {
    // 寻找最近的关闭按钮，且必须在指挥中心覆盖层内
    const closeBtn = e.target.closest('.overview-overlay .close-btn');
    if (closeBtn) {
        e.preventDefault();
        e.stopPropagation();
        window.toggleHub('hide');
    }
});

// 2. 统一出版点火接口
window.triggerPublish = async () => {
    if (typeof window.triggerSystemPulse === 'function') {
        window.triggerSystemPulse();
    }
    if (typeof window.addAudit === 'function') {
        window.addAudit('正在准备物理出版链路...', 'info');
    }

    // 🚀 [V74.8] 物理点火：连接重构后的编排中枢
    try {
        if (typeof apiFetch !== 'function') {
            throw new Error('apiFetch 核心未加载完毕');
        }
        const res = await apiFetch('/api/system/sync/trigger', { method: 'POST' });

        if (res && res.status === 'started') {
            if (typeof window.addAudit === 'function') {
                window.addAudit(`✅ 后台出版流水线已点火 (FutureID: ${res.future_id})`, 'success');
            }

            // 使用 SweetAlert2 展示全局进度遮罩 (如果需要)
            if (window.Swal) {
                window.Swal.fire({
                    title: '出版流水线已启动',
                    text: '正在跨线程调度全球节点，请关注右侧审计雷达。',
                    icon: 'success',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
            }
        } else if (res && res.status === 'rejected') {
            if (typeof window.addAudit === 'function') {
                window.addAudit('⚠️ 拦截重入：已有出版任务正在运行中。', 'warning');
            }
        } else {
            throw new Error(res ? res.reason : '后端拒绝点火');
        }
    } catch (err) {
        if (typeof window.addAudit === 'function') {
            window.addAudit(`❌ 链路溃决: ${err.message}`, 'error');
        }
        if (window.Swal) {
            window.Swal.fire('点火失败', err.message, 'error');
        }
    }
};
