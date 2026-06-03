/**
 * 🌓 Illacme Themes - Day/Night Mode Engine
 * 职责：[SOP-02] 物理拆分的昼夜模式管理器，基于 localStorage 缓存读写，支持 dark/light/auto 模式。
 */

window.ThemeModeManager = {
    MODE_KEY: 'illacme_daynight_mode',
    currentMode: 'dark', // 实际运行时的模式 (dark | light)
    setting: 'dark', // 用户设置 (dark | light | auto)

    /**
     * 🏁 初始化引擎，通常在 DOMContentLoaded 阶段调用
     */
    init() {
        this.setting = localStorage.getItem(this.MODE_KEY) || 'dark';
        this.applySetting(this.setting);
        
        // 监听系统时间的流逝，如果是 auto 模式需要动态切换
        setInterval(() => this.checkAutoMode(), 60000); // 每分钟检查一次
    },

    /**
     * 🔄 用户主动切换模式的循环：dark -> light -> auto -> dark...
     */
    cycleMode() {
        if (this.setting === 'dark') {
            this.applySetting('light');
        } else if (this.setting === 'light') {
            this.applySetting('auto');
        } else {
            this.applySetting('dark');
        }
    },

    /**
     * 🎯 应用设定并推导实际模式
     */
    applySetting(newSetting) {
        this.setting = newSetting;
        localStorage.setItem(this.MODE_KEY, newSetting);
        
        let targetMode = newSetting;
        if (newSetting === 'auto') {
            targetMode = this.calculateAutoMode();
        }

        this.setRealMode(targetMode);
        this.updateUI();
    },

    /**
     * 🕒 根据本地时间计算实际模式 (早 7:00 ~ 晚 19:00 为 light)
     */
    calculateAutoMode() {
        const hour = new Date().getHours();
        return (hour >= 7 && hour < 19) ? 'light' : 'dark';
    },

    /**
     * 🚦 被动轮询检查，仅在 auto 模式时生效
     */
    checkAutoMode() {
        if (this.setting === 'auto') {
            const targetMode = this.calculateAutoMode();
            if (targetMode !== this.currentMode) {
                this.setRealMode(targetMode);
            }
        }
    },

    /**
     * 物理应用模式到 DOM 并广播事件
     */
    setRealMode(mode) {
        if (this.currentMode === mode && document.documentElement.getAttribute('data-theme') === mode) {
            return; // 状态一致，防抖
        }
        
        this.currentMode = mode;
        
        if (mode === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme'); // dark 是默认 fallback
        }

        // 📡 广播模式变更信号给所有引擎（例如 Galaxy Engine）
        window.dispatchEvent(new CustomEvent('themeModeChanged', { detail: { mode: mode } }));
    },

    /**
     * 更新顶部/底部的 UI 控件显示
     */
    updateUI() {
        const selectEl = document.getElementById('theme-mode-select');
        if (selectEl) {
            selectEl.value = this.setting;
        }
    }
};

// 立即尝试预初始化（防止白屏闪烁）
if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem('illacme_daynight_mode') || 'dark';
    if (saved === 'light' || (saved === 'auto' && new Date().getHours() >= 7 && new Date().getHours() < 19)) {
        document.documentElement.setAttribute('data-theme', 'light');
    }
}
