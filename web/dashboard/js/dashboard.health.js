/**
 * 🩺 [V55.0] Illacme Plenipes Health & Operations Module (Hub Controller)
 * 职责：主权系统关机控制总线。
 */

/**
 * 🚀 [V55.0] 紧急关机指令
 * 职责：向核心引擎发起 SIGINT 信号，安全关闭所有出版管线并停机。
 */
window.shutdownSystem = async () => {
    const confirmed = confirm("⚠️ 警告：正在执行物理级紧急关机指令！\n\n这将立即中断所有正在进行的出版任务、同步进程和 API 服务。是否继续？");
    if (!confirmed) return;

    try {
        addAudit("🛑 正在发起紧急停机指令...");
        // 🚀 [V55.0] 预留最后一次心跳上报
        await apiFetch('/api/system/shutdown', { method: 'POST' });
        
        // 瞬间切换 UI 状态为离线
        document.body.innerHTML = `
            <div style="height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--bg-solid, #000000); color: var(--neon-red, #ff4d4d); font-family: 'Inter', sans-serif;">
                <h1 style="font-size: 3rem; margin-bottom: 1rem;">SYSTEM OFFLINE</h1>
                <p style="color: var(--text-dim, #666666);">主权出版中心已安全关闭。请在终端执行 python3 plenipes.py 重新启动。</p>
                <div style="margin-top: 2rem; padding: 10px 20px; border: 1px solid var(--white-10, #333333); border-radius: 5px; cursor: pointer;" onclick="location.reload()">重新连接</div>
            </div>
        `;
    } catch (err) {
        // 关机成功通常会导致连接中断，这也是预期的
        console.log("System shutting down...");
    }
};
