/**
 * 📝 [V1.0] Illacme Plenipes WYSIWYG HTML2Markdown & Commands Shard
 * 职责：WYSIWYG 可视化富文本与 Markdown 语法互转引擎及快捷编辑指令。
 */

(function () {
    'use strict';

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

})();
