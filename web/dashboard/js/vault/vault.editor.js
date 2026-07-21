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

// 🚀 [V75.7] WYSIWYG 可视化 HTML 转 Markdown 渲染引擎 (html2md)
window.htmlToMarkdown = (html) => {
    const doc = document.createElement('div');
    doc.innerHTML = html;
    
    const convertNode = (node) => {
        if (node.nodeType === Node.TEXT_NODE) {
            return node.textContent;
        }
        if (node.nodeType !== Node.ELEMENT_NODE) {
            return '';
        }
        
        let childrenVal = Array.from(node.childNodes).map(convertNode).join('');
        const tag = node.tagName.toLowerCase();
        
        switch (tag) {
            case 'p':
                return childrenVal.trim() ? childrenVal.trim() + '\n\n' : '';
            case 'strong':
            case 'b':
                return `**${childrenVal}**`;
            case 'em':
            case 'i':
                return `*${childrenVal}*`;
            case 'h1':
                return `# ${childrenVal.trim()}\n\n`;
            case 'h2':
                return `## ${childrenVal.trim()}\n\n`;
            case 'h3':
                return `### ${childrenVal.trim()}\n\n`;
            case 'h4':
                return `#### ${childrenVal.trim()}\n\n`;
            case 'blockquote':
                return `> ${childrenVal.trim().replace(/\n/g, '\n> ')}\n\n`;
            case 'ul':
                return childrenVal + '\n';
            case 'ol':
                return childrenVal + '\n';
            case 'li':
                const parent = node.parentNode;
                if (parent && parent.tagName.toLowerCase() === 'ol') {
                    const index = Array.from(parent.children).indexOf(node) + 1;
                    return `${index}. ${childrenVal.trim()}\n`;
                }
                return `* ${childrenVal.trim()}\n`;
            case 'pre':
                const codeNode = node.querySelector('code');
                const codeText = codeNode ? codeNode.textContent : node.textContent;
                return `\`\`\`\n${codeText.trim()}\n\`\`\`\n\n`;
            case 'code':
                if (node.parentNode && node.parentNode.tagName.toLowerCase() === 'pre') {
                    return childrenVal;
                }
                return `\`${childrenVal}\``;
            case 'a':
                const href = node.getAttribute('href') || '';
                if (node.classList.contains('wiki-doc-link')) {
                    const wikiName = node.getAttribute('onclick')?.match(/openEditorFromPreview\('([^']+)'/)?.[1] || childrenVal;
                    if (wikiName === childrenVal) return `[[${wikiName}]]`;
                    return `[[${wikiName}|${childrenVal}]]`;
                }
                if (node.classList.contains('attachment-link')) {
                    const path = node.getAttribute('href')?.split('/api/vault-assets/')?.[1]?.split('?')[0] || '';
                    const decodedPath = decodeURIComponent(path);
                    return `[[${decodedPath}|${childrenVal.replace('📎 ', '')}]]`;
                }
                return `[${childrenVal}](${href})`;
            case 'img':
                const src = node.getAttribute('src') || '';
                const alt = node.getAttribute('alt') || '';
                const width = node.getAttribute('width') || '';
                if (src.includes('/api/vault-assets/')) {
                    const path = src.split('/api/vault-assets/')?.[1]?.split('?')[0] || '';
                    const decodedPath = decodeURIComponent(path);
                    if (width) return `![[${decodedPath}|${width}]]`;
                    return `![[${decodedPath}]]`;
                }
                return `![${alt}](${src})`;
            case 'br':
                return '\n';
            default:
                return childrenVal;
        }
    };
    
    let md = Array.from(doc.childNodes).map(convertNode).join('');
    return md.replace(/\n{3,}/g, '\n\n').trim();
};

// 🚀 [V75.7] WYSIWYG 快捷命令执行与物理同步
window.execWysiwygCmd = (cmd, value = null) => {
    document.execCommand(cmd, false, value);
    const wysiwyg = document.getElementById('editor-wysiwyg');
    const body = document.getElementById('editor-body');
    if (wysiwyg && body) {
        const md = window.htmlToMarkdown(wysiwyg.innerHTML);
        if (body.value !== md) {
            body.value = md;
            window.triggerAutoSave();
        }
    }
};

window.insertWysiwygLink = () => {
    const url = prompt("输入超链接 URL:");
    if (url) {
        window.execWysiwygCmd('createLink', url);
    }
};

window.insertWysiwygWikiLink = () => {
    const name = prompt("输入关联文稿名称（Wiki双链）:");
    if (name) {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const text = range.toString() || name;
            
            const a = document.createElement('a');
            a.href = '#';
            a.className = 'wiki-doc-link';
            a.setAttribute('onclick', `openEditorFromPreview('${name.replace(/'/g, "\\'")}', event)`);
            a.innerText = text;
            
            range.deleteContents();
            range.insertNode(a);
            
            const wysiwyg = document.getElementById('editor-wysiwyg');
            const body = document.getElementById('editor-body');
            if (wysiwyg && body) {
                const md = window.htmlToMarkdown(wysiwyg.innerHTML);
                body.value = md;
                window.triggerAutoSave();
            }
        }
    }
};
