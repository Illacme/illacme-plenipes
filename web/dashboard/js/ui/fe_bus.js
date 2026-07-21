/**
 * 🛰️ [V75.95] Front-end Event Bus (前端事件总线)
 * 职责：解耦多模块异步加载时序竞争，为系统状态及 DOM 重绘后的对正提供物理钩子。
 */
(function() {
    const listeners = {};

    window.feBus = {
        /**
         * 订阅事件
         */
        on(event, callback) {
            if (!listeners[event]) {
                listeners[event] = [];
            }
            listeners[event].push(callback);
        },

        /**
         * 取消订阅
         */
        off(event, callback) {
            if (!listeners[event]) return;
            listeners[event] = listeners[event].filter(cb => cb !== callback);
        },

        /**
         * 广播广播事件
         */
        emit(event, data) {
            if (!listeners[event]) return;
            // 浅拷贝以防在执行回调时有 off 操作导致数组被修改
            const cbs = [...listeners[event]];
            cbs.forEach(cb => {
                try {
                    cb(data);
                } catch (e) {
                    console.error(`❌ [feBus] 事件 '${event}' 的回调执行异常:`, e);
                }
            });
        }
    };
})();
