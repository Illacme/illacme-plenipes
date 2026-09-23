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
        
        // 🚀 [V68.0] 动态元数据注入（防御性挂载）
        if (typeof window.renderDynamicMetadata === 'function') {
            window.renderDynamicMetadata(doc.frontmatter || {});
        } else if (typeof renderDynamicMetadata === 'function') {
            renderDynamicMetadata(doc.frontmatter || {});
        }
        
        // 🌓 [V87.0] 初始化编辑器模式为源码模式，并预渲染预览内容与实时 URL 路径
        if (typeof window.setEditorMode === 'function') window.setEditorMode('source');
        if (typeof window.updateEditorPreview === 'function') window.updateEditorPreview();
        if (typeof window.updateEditorUrlPreview === 'function') window.updateEditorUrlPreview();
        if (typeof window.initSyncScroll === 'function') window.initSyncScroll();

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
    const wysiwygToolbar = document.getElementById('editor-wysiwyg-toolbar');
    const wysiwyg = document.getElementById('editor-wysiwyg');
    const btnSource = document.getElementById('mode-source'), 
          btnWysiwyg = document.getElementById('mode-wysiwyg'),
          btnPreview = document.getElementById('mode-preview'), 
          btnSplit = document.getElementById('mode-split');

    if (!body || !preview || !wysiwygToolbar || !wysiwyg) return;

    [btnSource, btnWysiwyg, btnPreview, btnSplit].forEach(b => b?.classList.remove('active'));

    if (mode === 'source') {
        body.style.display = 'block';
        preview.style.display = 'none';
        wysiwygToolbar.style.display = 'none';
        wysiwyg.style.display = 'none';
        btnSource?.classList.add('active');
    } else if (mode === 'wysiwyg') {
        body.style.display = 'none';
        preview.style.display = 'none';
        wysiwygToolbar.style.display = 'flex';
        wysiwyg.style.display = 'block';
        btnWysiwyg?.classList.add('active');
        // 先刷新一次 preview，以确保从 Markdown 解析出最新的真实 HTML 并注入到富文本编辑器
        updateEditorPreview();
        wysiwyg.innerHTML = preview.innerHTML;
    } else if (mode === 'preview') {
        body.style.display = 'none';
        preview.style.display = 'block';
        wysiwygToolbar.style.display = 'none';
        wysiwyg.style.display = 'none';
        btnPreview?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    } else if (mode === 'split') {
        body.style.display = 'block';
        preview.style.display = 'block';
        wysiwygToolbar.style.display = 'none';
        wysiwyg.style.display = 'none';
        btnSplit?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    }
};

window.closeEditor = () => {
    document.getElementById('editor-modal').style.display = 'none';
    const configTabs = document.getElementById('config-tabs');
    if (configTabs) configTabs.style.display = 'none';
    // 🪐 [V107.8] 若在知识星谱视图下操作，关闭编辑器后自动平滑复原星球控制仪与 3D 聚焦
    if (typeof window.restoreGalaxyDirectorIfActive === 'function') {
        window.restoreGalaxyDirectorIfActive();
    }
};

// 🌐 [V107.0] 统一物理/产物路径推演算子：根据当前网址组织形态 (slug_dir_mode) 计算预期 URL 相对路径
window.calculateDocUrlPath = (relPath, slugVal) => {
    if (!relPath) return { path: "", modeLabel: "目录树复刻", dirMode: "nested" };
    const settingsData = window.settingsData || {};
    const translation = settingsData.translation || {};
    const dirMode = (translation.slug_dir_mode || 'nested').toLowerCase();

    const parts = relPath.replace(/\\/g, '/').split('/');
    const fileName = parts.pop() || "";
    const baseSlug = fileName.replace(/\.(md|markdown)$/i, '');
    const subDir = parts.join('/');

    const cleanSlug = (slugVal && slugVal !== 'null' && slugVal !== 'undefined' && String(slugVal).trim())
        ? String(slugVal).trim()
        : (baseSlug || "index");

    const isGlobalHome = (['', 'index', 'home'].includes(cleanSlug.toLowerCase()) && !subDir);
    const isChannelHome = (['', 'index', 'home'].includes(cleanSlug.toLowerCase()) && !isGlobalHome);

    let path = "";
    let modeLabel = "目录树复刻";

    if (dirMode === 'flat') {
        modeLabel = "极简根目录";
        if (isGlobalHome) {
            path = "index.html";
        } else if (isChannelHome) {
            const channelName = subDir ? subDir.replace(/\//g, '-').toLowerCase() : 'docs';
            path = `${channelName}.html`;
        } else {
            path = `${cleanSlug}.html`;
        }
    } else if (dirMode === 'prefix') {
        modeLabel = "智能前缀";
        const prefix = subDir ? `${subDir.replace(/\//g, '-').toLowerCase()}-` : '';
        if (isGlobalHome) {
            path = "index.html";
        } else if (isChannelHome) {
            path = `${prefix}index.html`;
        } else {
            path = `${prefix}${cleanSlug}.html`;
        }
    } else {
        modeLabel = "目录树复刻";
        if (isGlobalHome) {
            path = "index.html";
        } else {
            const nestedSub = subDir ? `${subDir.toLowerCase()}/` : '';
            path = `${nestedSub}${cleanSlug}.html`;
        }
    }
    return { path, modeLabel, dirMode };
};

// 快捷字符串提取算子
window.resolveDocUrlString = (relPath, slugVal) => {
    const res = window.calculateDocUrlPath(relPath, slugVal);
    return res ? res.path : "";
};

// 🌐 [V107.0] 实时网址路径推导微端：根据当前治理中心网址组织形态 (slug_dir_mode) 计算预期 URL
window.updateEditorUrlPreview = () => {
    const previewEl = document.getElementById('editor-url-preview-text');
    if (!previewEl) return;

    const docId = window.activeDocId || "";
    const slugInput = document.getElementById('editor-meta-slug');
    const slugVal = (slugInput ? slugInput.value.trim() : "");

    const { path, modeLabel } = window.calculateDocUrlPath(docId, slugVal);
    previewEl.innerText = `预估: /${path} (${modeLabel})`;
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
                window.updateEditorUrlPreview();
            }
            
            if (id === 'editor-meta-title') {
                const titleVal = e.target.value;
                if (!window.editorSlugUserEdited) {
                    window.generateAndSyncSlug(titleVal);
                }
                window.updateEditorUrlPreview();
            }

            if (id === 'editor-wysiwyg') {
                const wysiwyg = e.target;
                const md = window.htmlToMarkdown(wysiwyg.innerHTML);
                const body = document.getElementById('editor-body');
                if (body && body.value !== md) {
                    body.value = md;
                    window.triggerAutoSave();
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
            if (e.target.id === 'editor-body' || e.target.id === 'editor-wysiwyg') {
                await window.handleEditorAssetUpload(e, 'paste');
            }
        });
        modal.addEventListener('drop', async (e) => {
            if (e.target.id === 'editor-body' || e.target.id === 'editor-wysiwyg') {
                await window.handleEditorAssetUpload(e, 'drop');
            }
        });
        modal.addEventListener('dragover', (e) => {
            if (e.target.id === 'editor-body' || e.target.id === 'editor-wysiwyg') {
                e.preventDefault();
            }
        });
        
        console.info("💾 [Scratchpad] Zero-Leak Event Delegation registered successfully.");
    }
}, 500);

window.binderyExportCurrentEditorDoc = function() {
    const docId = window.activeDocId;
    if (!docId) return window.showToast?.('当前无正在编辑的原稿', 'warning');
    const title = document.getElementById('editor-meta-title')?.value?.trim() || '';
    if (typeof window.quickBindSingleDoc === 'function') {
        window.quickBindSingleDoc(docId, title);
    } else if (typeof window.openBinderyModal === 'function') {
        window.openBinderyModal(`single:${docId}`, { rel_path: docId, title: title || docId });
    }
};

// ⌨️ 全域 Cmd+B / Ctrl+B 装订快捷键
if (typeof window.addEventListener === 'function') {
    window.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && (e.key === 'b' || e.key === 'B')) {
            const modal = document.getElementById('editor-modal');
            if (modal && modal.style.display !== 'none') {
                e.preventDefault();
                window.binderyExportCurrentEditorDoc();
            } else if (typeof window.openBinderyModal === 'function') {
                e.preventDefault();
                window.openBinderyModal();
            }
        }
    });
}
