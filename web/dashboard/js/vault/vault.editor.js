/**
 * 📝 [V87.0] Illacme Plenipes Modal Editor & Marked Parser Module
 * 职责：文稿编辑器交互、YAML Frontmatter 智能解析注入、Markdown 双链附件解析与 Wiki 联动、以及同步滚动渲染。
 */

// 4. 全量物理编辑器 (Modal)
window.openEditor = async (docId) => {
    window.activeDocId = docId;
    const modal = document.getElementById('editor-modal');
    const body = document.getElementById('editor-body');
    const title = document.getElementById('editor-title');
    const mTitle = document.getElementById('editor-meta-title');
    const mSlug = document.getElementById('editor-meta-slug');
    
    // 💾 初始化隐藏草稿恢复提示挂载条
    const recoveryBar = document.getElementById('editor-draft-recovery-bar');
    if (recoveryBar) recoveryBar.style.display = 'none';

    title.innerText = "EXTRACTING PHYSICAL ASSET...";
    if (body) body.placeholder = "等待数据载入...";
    const status = document.getElementById('save-status');
    if (status) status.innerText = ""; // 🚀 状态对齐：清除上一个文档的残留状态
    modal.style.display = 'flex';

    const doc = await apiFetch(`/ledger/document/${encodeURIComponent(docId)}`);
    if (doc) {
        title.innerText = `EDITOR: ${doc.title || docId}`;
        if (body) {
            body.placeholder = "在此处输入文稿内容（支持 Markdown 语法）...";
            body.value = doc.content || "";
        }
        if (mTitle) mTitle.value = doc.title || "";
        if (mSlug) mSlug.value = doc.slug || "";
        
        // 🚀 [V68.0] 动态元数据注入
        renderDynamicMetadata(doc.frontmatter || {});
        
        // 🌓 [V87.0] 初始化编辑器模式为源码模式，并预渲染预览内容
        setEditorMode('source');
        updateEditorPreview();
        initSyncScroll();

        // 💾 物理草稿核查与气泡呈现
        const draftStr = localStorage.getItem(`illacme_draft_${docId}`);
        if (draftStr) {
            try {
                const draft = JSON.parse(draftStr);
                const contentDiff = draft.content !== (doc.content || "");
                const titleDiff = draft.title !== (doc.title || "");
                const slugDiff = draft.slug !== (doc.slug || "");
                
                if (contentDiff || titleDiff || slugDiff) {
                    if (recoveryBar) {
                        const timeEl = document.getElementById('editor-draft-time');
                        if (timeEl) {
                            const d = new Date(draft.savedAt);
                            timeEl.innerText = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                        }
                        recoveryBar.style.display = 'flex';
                    }
                }
            } catch (e) {
                console.error("Draft parsing failed:", e);
            }
        }
    }
};

window.setEditorMode = (mode) => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    const btnSource = document.getElementById('mode-source');
    const btnPreview = document.getElementById('mode-preview');
    const btnSplit = document.getElementById('mode-split');

    if (!body || !preview) return;

    [btnSource, btnPreview, btnSplit].forEach(b => b?.classList.remove('active'));

    if (mode === 'source') {
        body.style.display = 'block';
        preview.style.display = 'none';
        btnSource?.classList.add('active');
    } else if (mode === 'preview') {
        body.style.display = 'none';
        preview.style.display = 'block';
        btnPreview?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    } else if (mode === 'split') {
        body.style.display = 'block';
        preview.style.display = 'block';
        btnSplit?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    }
};

window.closeEditor = () => {
    document.getElementById('editor-modal').style.display = 'none';
    const configTabs = document.getElementById('config-tabs');
    if (configTabs) configTabs.style.display = 'none';
};

window.saveDocument = async () => {
    const content = document.getElementById('editor-body').value;
    const titleEl = document.getElementById('editor-meta-title');
    const slugEl = document.getElementById('editor-meta-slug');
    const status = document.getElementById('save-status');
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
                    
                    const y = dateObj.getFullYear();
                    const m = pad(dateObj.getMonth() + 1);
                    const d = pad(dateObj.getDate());
                    const hh = pad(dateObj.getHours());
                    const mm = pad(dateObj.getMinutes());
                    const ss = pad(dateObj.getSeconds());
                    
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
        addAudit(`📄 资产 ${window.activeDocId.substring(0, 8)} 已完成物理变更。`);
        
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
        status.innerText = "❌ 写入失败";
        if (res && res.error) console.error(res.error);
    }
};

// 💾 全局一次性“零泄露事件委托”总线监听
setTimeout(() => {
    const modal = document.getElementById('editor-modal');
    if (modal) {
        modal.addEventListener('input', (e) => {
            const id = e.target.id;
            const isMeta = e.target.classList.contains('metadata-input');
            if (id === 'editor-body' || id === 'editor-meta-title' || id === 'editor-meta-slug' || isMeta) {
                window.triggerAutoSave();
            }
        });
        modal.addEventListener('change', (e) => {
            if (e.target.classList.contains('metadata-input')) {
                window.triggerAutoSave();
            }
        });
        console.info("💾 [Scratchpad] Zero-Leak Event Delegation registered successfully.");
    }
}, 500);
