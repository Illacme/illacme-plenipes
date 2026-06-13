/**
 * 📝 [V87.0] Illacme Plenipes Modal Editor & Marked Parser Module
 * 职责：文稿编辑器交互、编辑器模式调度、生命周期控制，以及事件监听总线。
 */

// 4. 全量物理编辑器 (Modal)
window.openEditor = async (docId) => {
    window.activeDocId = docId;
    const modal = document.getElementById('editor-modal'), body = document.getElementById('editor-body');
    const title = document.getElementById('editor-title'), mTitle = document.getElementById('editor-meta-title'), mSlug = document.getElementById('editor-meta-slug');
    
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
        const existingSlug = doc.slug || "";
        window.editorSlugUserEdited = (existingSlug !== "" && existingSlug !== "未命名原稿");
        
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
    const btnSource = document.getElementById('mode-source'), btnPreview = document.getElementById('mode-preview'), btnSplit = document.getElementById('mode-split');

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

// 💾 全局一次性“零泄露事件委托”总线监听
setTimeout(() => {
    const modal = document.getElementById('editor-modal');
    if (modal) {
        modal.addEventListener('input', (e) => {
            const id = e.target.id;
            const isMeta = e.target.classList.contains('metadata-input');

            if (id === 'editor-meta-slug') {
                const val = e.target.value.trim();
                if (val === "") {
                    window.editorSlugUserEdited = false;
                    const titleVal = document.getElementById('editor-meta-title')?.value || "";
                    if (titleVal) window.generateAndSyncSlug(titleVal);
                } else {
                    window.editorSlugUserEdited = true;
                }
            }
            
            if (id === 'editor-meta-title') {
                const titleVal = e.target.value;
                if (!window.editorSlugUserEdited) {
                    window.generateAndSyncSlug(titleVal);
                }
            }

            if (id === 'editor-body' || id === 'editor-meta-title' || id === 'editor-meta-slug' || isMeta) {
                window.triggerAutoSave();
            }
        });
        modal.addEventListener('change', (e) => {
            if (e.target.classList.contains('metadata-input')) {
                window.triggerAutoSave();
            }
        });
        
        // 🚀 [V88.0] 物理图像无缝上传拦截
        modal.addEventListener('paste', async (e) => {
            if (e.target.id === 'editor-body') {
                await window.handleEditorAssetUpload(e, 'paste');
            }
        });
        modal.addEventListener('drop', async (e) => {
            if (e.target.id === 'editor-body') {
                await window.handleEditorAssetUpload(e, 'drop');
            }
        });
        modal.addEventListener('dragover', (e) => {
            if (e.target.id === 'editor-body') {
                e.preventDefault();
            }
        });
        
        console.info("💾 [Scratchpad] Zero-Leak Event Delegation registered successfully.");
    }
}, 500);
