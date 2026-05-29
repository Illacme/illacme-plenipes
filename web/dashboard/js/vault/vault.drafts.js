/**
 * 📝 [V87.0] Illacme Plenipes Modal Editor - Drafts Shard
 */

// ==================== 💾 自动草稿箱与自愈保活逻辑 ====================
window.vaultAutoSaveTimeout = null;

/**
 * 防抖草稿保存触发器
 */
window.triggerAutoSave = () => {
    if (window.vaultAutoSaveTimeout) clearTimeout(window.vaultAutoSaveTimeout);
    window.vaultAutoSaveTimeout = setTimeout(() => {
        window.saveDraftToStorage();
    }, 500);
};

/**
 * 序列化编辑器表单并存盘到 LocalStorage
 */
window.saveDraftToStorage = () => {
    if (!window.activeDocId) return;
    
    const content = document.getElementById('editor-body')?.value || "";
    const title = document.getElementById('editor-meta-title')?.value || "";
    const slug = document.getElementById('editor-meta-slug')?.value || "";
    
    const frontmatter = {};
    const metaInputs = document.querySelectorAll('.metadata-input');
    metaInputs.forEach(input => {
        const key = input.getAttribute('data-key');
        if (input.type === 'checkbox') {
            frontmatter[key] = input.checked;
        } else {
            frontmatter[key] = input.value;
        }
    });
    
    const draft = {
        docId: window.activeDocId,
        content: content,
        title: title,
        slug: slug,
        frontmatter: frontmatter,
        savedAt: new Date().getTime()
    };
    
    localStorage.setItem(`illacme_draft_${window.activeDocId}`, JSON.stringify(draft));
    console.info(`[AutoSave] Draft autosaved for asset: ${window.activeDocId}`);
};

/**
 * 💾 立即一键复苏草稿内容并回填
 */
window.restoreScratchpadDraft = () => {
    if (!window.activeDocId) return;
    const draftStr = localStorage.getItem(`illacme_draft_${window.activeDocId}`);
    if (!draftStr) return;
    
    try {
        const draft = JSON.parse(draftStr);
        
        const body = document.getElementById('editor-body');
        const mTitle = document.getElementById('editor-meta-title');
        const mSlug = document.getElementById('editor-meta-slug');
        
        if (body) body.value = draft.content || "";
        if (mTitle) mTitle.value = draft.title || "";
        if (mSlug) mSlug.value = draft.slug || "";
        
        if (draft.frontmatter) {
            renderDynamicMetadata(draft.frontmatter);
        }
        
        updateEditorPreview();
        
        const recoveryBar = document.getElementById('editor-draft-recovery-bar');
        if (recoveryBar) recoveryBar.style.display = 'none';
        
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'success',
                title: '✅ 草稿已成功复苏',
                showConfirmButton: false,
                timer: 1500,
                background: 'var(--card-bg)',
                color: 'var(--text-bright)'
            });
        } else if (typeof showNotification === 'function') {
            showNotification('✅ 草稿已成功复苏', 'success');
        }
    } catch (e) {
        console.error("Failed to restore scratchpad draft:", e);
    }
};

/**
 * 忽略本次草稿提醒
 */
window.discardScratchpadDraft = () => {
    const recoveryBar = document.getElementById('editor-draft-recovery-bar');
    if (recoveryBar) recoveryBar.style.display = 'none';
};
