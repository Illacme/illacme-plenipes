/**
 * 📝 [V87.0] Illacme Plenipes Modal Editor - Save Submodule
 * 职责：元数据数据搜集、日期时区对正反解析、复杂 JSON 解析以及最终的文档落盘提交。
 */

window.saveDocument = async () => {
    // 🛡️ [安全防线] 拦截非法 activeDocId，防止无编辑器聚焦时触发保存
    if (!window.activeDocId || window.activeDocId === 'null' || window.activeDocId === 'undefined') {
        console.warn("[Save] window.activeDocId 为空或无效，放弃本次强制保存。");
        return { success: false, reason: "Invalid activeDocId" };
    }
    
    // 🛡️ [安全防线] 若编辑器 Modal 处于隐藏状态，说明并无未保存 of 脏数据，放弃本次保存
    const modal = document.getElementById('editor-modal');
    if (!modal || modal.style.display === 'none') {
        console.info("[Save] 编辑器当前处于隐藏状态，无脏数据需要落盘。");
        return { success: true, reason: "Editor is hidden" };
    }

    const content = document.getElementById('editor-body').value, titleEl = document.getElementById('editor-meta-title');
    const slugEl = document.getElementById('editor-meta-slug'), status = document.getElementById('save-status');
    status.innerText = "💾 正在写入磁道...";

    // 🚀 [V68.0] 收集动态元数据
    const frontmatter = {};
    const metaInputs = document.querySelectorAll('.metadata-input');
    metaInputs.forEach(input => {
        const key = input.getAttribute('data-key');
        if (input.type === 'checkbox') {
            frontmatter[key] = input.checked;
        } else {
            const val = input.value.trim();
            
            // 🚀 [V87.3] 智能日期时区反向对准与重塑
            if (input.getAttribute('data-is-date') === 'true') {
                if (!val) {
                    frontmatter[key] = "";
                    return;
                }
                const dateObj = new Date(val);
                if (!isNaN(dateObj.getTime())) {
                    const pad = (n) => String(n).padStart(2, '0');
                    const offset = -dateObj.getTimezoneOffset();
                    const sign = offset >= 0 ? '+' : '-';
                    const tz = sign + pad(Math.floor(Math.abs(offset) / 60)) + ':' + pad(Math.abs(offset) % 60);
                    
                    const y = dateObj.getFullYear(), m = pad(dateObj.getMonth() + 1), d = pad(dateObj.getDate());
                    const hh = pad(dateObj.getHours()), mm = pad(dateObj.getMinutes()), ss = pad(dateObj.getSeconds());
                    
                    frontmatter[key] = `${y}-${m}-${d}T${hh}:${mm}:${ss}${tz}`;
                    return;
                }
            }
            
            // 🚀 [V87.2] 智能解析 JSON 数组与复杂对象，防止结构混淆与二次破坏
            if ((val.startsWith('{') && val.endsWith('}')) || (val.startsWith('[') && val.endsWith(']'))) {
                try {
                    frontmatter[key] = JSON.parse(val);
                    return; // 成功解析为 JSON，跳过后续 standard 处理
                } catch (e) {
                    console.warn(`Failed to parse metadata field "${key}" as JSON, fallback to raw string:`, e);
                }
            }
            
            // 简单处理：如果包含逗号，尝试转为数组（对应用户对列表的支持要求）
            if (val.includes(',')) {
                frontmatter[key] = val.split(',').map(v => v.trim()).filter(v => v !== "");
            } else {
                frontmatter[key] = val;
            }
        }
    });

    const payload = { content, frontmatter };
    if (titleEl) payload.title = titleEl.value;
    if (slugEl) payload.slug = slugEl.value;

    const res = await apiFetch(`/ledger/document/${encodeURIComponent(window.activeDocId)}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.success) {
        status.innerText = "✅ 写入成功";
        
        // 💾 物理存盘生命周期闭环：成功写入后物理销毁该文档的本地草稿缓存
        localStorage.removeItem(`illacme_draft_${window.activeDocId}`);
        const recoveryBar = document.getElementById('editor-draft-recovery-bar');
        if (recoveryBar) recoveryBar.style.display = 'none';

        setTimeout(closeEditor, 800);
        // 🚀 [V100.0] 无论当前视图为什么，只要 3D 引擎准备就绪就去主动刷新，免去一切强刷
        if (typeof refreshGalaxy === 'function') {
            refreshGalaxy();
        }
        if (typeof loadVault === 'function') {
            loadVault(window.vaultCurrentQuery, window.vaultCurrentPage);
        }
    } else {
        const errorMsg = res && res.error ? res.error : "未知错误";
        status.innerText = `❌ 写入失败: ${errorMsg}`;
        if (res && res.error) console.error(res.error);

        // 🚀 [V100.0] 对 Slug 冲突或其它严重写入失败错误进行大屏 Swal 极致警告体验
        if (res && (res.error_code === 'SLUG_CONFLICT' || errorMsg.includes('Slug 冲突'))) {
            Swal.fire({
                title: '🔗 Slug 路径冲突',
                text: errorMsg,
                icon: 'warning',
                background: 'hsla(236, 37%, 8%, 0.95)',
                color: 'var(--text-bright, #ffffff)',
                confirmButtonText: '我知道了',
                customClass: {
                    popup: 'glass-panel',
                    confirmButton: 'primary-btn glow-btn'
                }
            });
        }
    }
};
