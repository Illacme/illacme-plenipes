/**
 * 📝 [V88.0] Illacme Plenipes Modal Editor - Asset & Slug Submodule
 * 职责：物理图片粘贴拖拽直传，以及与后端 Slug 转换接口防抖绑定。
 */

window.editorSlugDebounceTimer = null;
window.editorSlugUserEdited = false;

window.handleEditorAssetUpload = async (e, mode) => {
    let file = null;
    if (mode === 'paste') {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let item of items) {
            if (item.type.indexOf('image/') === 0) {
                file = item.getAsFile();
                break;
            }
        }
    } else if (mode === 'drop') {
        const items = e.dataTransfer.items;
        if (items) {
            for (let item of items) {
                if (item.kind === 'file' && item.type.indexOf('image/') === 0) {
                    file = item.getAsFile();
                    break;
                }
            }
        } else if (e.dataTransfer.files) {
            for (let f of e.dataTransfer.files) {
                if (f.type.indexOf('image/') === 0) {
                    file = f;
                    break;
                }
            }
        }
    }

    if (!file) return;

    e.preventDefault();
    if (typeof addAudit === 'function') addAudit(`🖼️ 正在极速物理直传图片 [${file.name || 'image.png'}]...`, 'info');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_id', window.activeDocId || "");

    try {
        const res = await window.apiFetch('/ledger/assets/upload', {
            method: 'POST',
            body: formData,
            headers: {} // 阻止 apiFetch 自动挂载 application/json
        });

        if (res && res.success) {
            if (typeof addAudit === 'function') addAudit(`✅ 图片已写入磁道: ${res.asset_path}`, 'success');
            
            const textarea = document.getElementById('editor-body');
            const startPos = textarea.selectionStart;
            const endPos = textarea.selectionEnd;
            const fallbackName = file.name ? file.name.split('.')[0] : 'image';
            // 使用 Obsidian 兼容的相对根路径 /assets/... 或者直接用相对路径
            const textToInsert = `![${fallbackName}](${res.asset_path})`;
            
            textarea.value = textarea.value.substring(0, startPos) + textToInsert + textarea.value.substring(endPos, textarea.value.length);
            textarea.selectionStart = startPos + textToInsert.length;
            textarea.selectionEnd = startPos + textToInsert.length;
            
            window.triggerAutoSave();
            if (typeof setEditorMode === 'function') {
                const btnSplit = document.getElementById('mode-split');
                if (btnSplit && btnSplit.classList.contains('active')) {
                    if (typeof updateEditorPreview === 'function') updateEditorPreview();
                }
            }
        } else {
            if (typeof addAudit === 'function') addAudit(`❌ 图片直传失败: ${res ? res.error : '未知错误'}`, 'error');
        }
    } catch (err) {
        if (typeof addAudit === 'function') addAudit(`❌ 上传链路异常: ${err.message}`, 'error');
    }
};

window.generateAndSyncSlug = function (title) {
    if (window.editorSlugDebounceTimer) {
        clearTimeout(window.editorSlugDebounceTimer);
    }
    
    window.editorSlugDebounceTimer = setTimeout(async () => {
        if (!title.trim() || window.editorSlugUserEdited) return;
        
        try {
            const res = await window.apiFetch('/api/vault/generate-slug', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            });
            
            if (res && res.success && res.slug) {
                const slugEl = document.getElementById('editor-meta-slug');
                if (slugEl && !window.editorSlugUserEdited) {
                    slugEl.value = res.slug;
                    window.triggerAutoSave();
                }
            }
        } catch (err) {
            console.error("Failed to generate slug automatically:", err);
        }
    }, 500);
};
