/**
 * 🛡️ [V127.0] Illacme Plenipes - Dispatch Platform Rate Limiting & Cooldown Guard
 * 职责：社交媒体分发平台级频控限流、账号防封与防重推安全倒计时中枢。
 * 特性：Session 级防丢、毫秒级倒计时平滑驱动、大表与 Diff 弹窗全域状态同步。
 */

(function () {
    const STORAGE_KEY = 'illacme_dispatch_cooldowns_v1';
    let _cooldownMap = new Map(); // key -> { expireAt, total, targetName }
    let _timer = null;

    // 默认各渠道基准安全冷却周期 (秒)
    const CHANNEL_DEFAULT_COOLDOWN = {
        wechat: 30,
        weixin: 30,
        mp: 30,
        zhihu: 20,
        xiaohongshu: 30,
        medium: 15,
        devto: 15,
        hashnode: 15,
        default: 10
    };

    function _resolveChannelDuration(targetId) {
        if (!targetId) return CHANNEL_DEFAULT_COOLDOWN.default;
        const low = String(targetId).toLowerCase();
        for (const k of Object.keys(CHANNEL_DEFAULT_COOLDOWN)) {
            if (low.includes(k)) return CHANNEL_DEFAULT_COOLDOWN[k];
        }
        return CHANNEL_DEFAULT_COOLDOWN.default;
    }

    function _saveToStorage() {
        try {
            const data = {};
            _cooldownMap.forEach((val, key) => {
                if (val.expireAt > Date.now()) {
                    data[key] = val;
                }
            });
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        } catch (e) {
            // 静默降级
        }
    }

    function _restoreFromStorage() {
        try {
            const raw = sessionStorage.getItem(STORAGE_KEY);
            if (!raw) return;
            const parsed = JSON.parse(raw);
            const now = Date.now();
            Object.keys(parsed).forEach(key => {
                const item = parsed[key];
                if (item && item.expireAt > now) {
                    _cooldownMap.set(key, item);
                }
            });
        } catch (e) {
            // 静默降级
        }
    }

    function _tick() {
        const now = Date.now();
        let hasActive = false;

        _cooldownMap.forEach((val, key) => {
            const remMs = val.expireAt - now;
            const remSec = Math.ceil(remMs / 1000);

            // 查找所有关联当前任务 key 的 DOM 按钮
            const targets = document.querySelectorAll(`[data-cooldown-task="${key}"]`);

            if (remSec > 0) {
                hasActive = true;
                targets.forEach(el => {
                    el.classList.add('is-cooling-btn');
                    el.disabled = true;
                    if (el.classList.contains('ledger-icon-btn')) {
                        el.innerHTML = `<span>🛡️ ${remSec}s</span>`;
                        el.title = `🛡️ 平台安全频控保护中：建议间隔 ≥ ${val.total}s，剩余 ${remSec}s`;
                    } else if (el.id === 'diff-modal-republish-btn') {
                        el.innerHTML = `<span>🛡️ 平台安全冷却中 (${remSec}s)</span>`;
                        el.title = `🛡️ 平台安全频控护栏生效中：剩余 ${remSec} 秒`;
                    }
                });
            } else {
                // 冷却到期自动解除
                _cooldownMap.delete(key);
                targets.forEach(el => {
                    el.classList.remove('is-cooling-btn');
                    el.disabled = false;
                    if (el.classList.contains('ledger-icon-btn')) {
                        el.innerHTML = '<span>📡</span>';
                        el.title = '向此渠道重新广播推流';
                    } else if (el.id === 'diff-modal-republish-btn') {
                        const tName = val.targetName || '社交媒体';
                        el.innerHTML = `<span>📡 立即向 [${tName}] 推流更新</span>`;
                        el.title = '立即执行推流';
                    }
                });
                if (typeof window.loadDispatchCenter === 'function') {
                    window.loadDispatchCenter('ledger');
                }
            }
        });

        _saveToStorage();

        if (!hasActive && _timer) {
            clearInterval(_timer);
            _timer = null;
        }
    }

    function _ensureTimer() {
        if (!_timer && _cooldownMap.size > 0) {
            _timer = setInterval(_tick, 1000);
            _tick();
        }
    }

    window.DispatchCooldownManager = {
        /**
         * 启动单篇文档在目标渠道的冷却护栏
         */
        startCooldown(relPath, targetId, seconds = null, targetName = '') {
            if (!relPath || !targetId) return;
            const taskKey = `${relPath}::${targetId}`;
            const totalSec = Number(seconds) > 0 ? Number(seconds) : _resolveChannelDuration(targetId);
            const expireAt = Date.now() + totalSec * 1000;

            _cooldownMap.set(taskKey, {
                expireAt,
                total: totalSec,
                targetName: targetName || targetId
            });

            _saveToStorage();
            _ensureTimer();
            _tick();
        },

        /**
         * 立即解除单篇文档在目标渠道的冷却状态 (失败自愈)
         */
        clearCooldown(relPath, targetId) {
            if (!relPath || !targetId) return;
            const taskKey = `${relPath}::${targetId}`;
            _cooldownMap.delete(taskKey);
            _saveToStorage();
            const targets = document.querySelectorAll(`[data-cooldown-task="${taskKey}"]`);
            targets.forEach(el => {
                el.classList.remove('is-cooling-btn');
                el.disabled = false;
                if (el.classList.contains('ledger-icon-btn')) {
                    el.innerHTML = '<span>📡</span>';
                    el.title = '向此渠道重新广播推流';
                }
            });
        },

        /**
         * 获取剩余冷却秒数 (0 代表未处于冷却中)
         */
        getRemaining(relPath, targetId) {
            if (!relPath || !targetId) return 0;
            const taskKey = `${relPath}::${targetId}`;
            const val = _cooldownMap.get(taskKey);
            if (!val) return 0;
            const rem = Math.ceil((val.expireAt - Date.now()) / 1000);
            if (rem <= 0) {
                _cooldownMap.delete(taskKey);
                return 0;
            }
            return rem;
        },

        /**
         * 判断当前是否正处于平台冷却中
         */
        isCooling(relPath, targetId) {
            return this.getRemaining(relPath, targetId) > 0;
        },

        /**
         * 获取预设冷却秒数
         */
        getChannelDuration(targetId) {
            return _resolveChannelDuration(targetId);
        },

        /**
         * 触发全页面冷却状态重新绑订扫描
         */
        refreshUI() {
            _tick();
        }
    };

    // 初始化时从本地会话中恢复
    _restoreFromStorage();
    if (_cooldownMap.size > 0) {
        _ensureTimer();
    }
})();
