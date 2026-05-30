/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) Markdown Engine - SOP Compliant
 * 职责：独立且极轻量的流式安全 Markdown 语法渲染算法分片。
 * 遵循 SOP-01 核心复杂度红线与 SOP-02 模块拆分协议。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.markdown.js initializing');

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    /**
     * 🧠 极致轻量、完全流式安全、高颜值 Markdown 渲染引擎 - SOP Compliant
     * 职责：流式安全提取 fenced code blocks、表格、inline code、粗斜体及列表状态机解析
     */
    window.renderMarkdown = function(text) {
        if (!text) return "";

        const placeholders = [];
        let workingText = text;

        // 1. Fenced Code Blocks (流式安全闭合与提取)
        const codeBlockRegex = /```([a-zA-Z0-9_\-+]*)\n([\s\S]*?)(?:```|$)/gi;
        workingText = workingText.replace(codeBlockRegex, (match, lang, code) => {
            const placeholderId = `__CODE_BLOCK_PLACEHOLDER_${placeholders.length}__`;
            const cleanLang = (lang || "").trim() || "text";
            
            // 安全 HTML 转义防止 XSS 注入
            const escapedCode = escapeHtml(code.trim());
            const codeBlockHtml = `<pre class="agent-code-block" data-lang="${cleanLang}"><code class="hljs">${escapedCode}</code></pre>`;
            
            placeholders.push(codeBlockHtml);
            return placeholderId;
        });

        // 2. 表格解析 (流式安全闭合与提取)
        const lines = workingText.split('\n');
        const processedLines = [];
        let inTable = false;
        let tableRows = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line.startsWith('|') && line.endsWith('|')) {
                if (!inTable) {
                    inTable = true;
                    tableRows = [];
                }
                tableRows.push(line);
            } else {
                if (inTable) {
                    const tableHtml = parseTableRows(tableRows);
                    const placeholderId = `__TABLE_PLACEHOLDER_${placeholders.length}__`;
                    placeholders.push(tableHtml);
                    processedLines.push(placeholderId);
                    inTable = false;
                }
                processedLines.push(lines[i]);
            }
        }
        if (inTable) {
            const tableHtml = parseTableRows(tableRows);
            const placeholderId = `__TABLE_PLACEHOLDER_${placeholders.length}__`;
            placeholders.push(tableHtml);
            processedLines.push(placeholderId);
        }

        workingText = processedLines.join('\n');

        // 3. 调用原 formatFileLinks 提取 tool_call 与超链接
        workingText = typeof window.formatFileLinks === 'function' ? window.formatFileLinks(workingText) : workingText;

        // 4. Inline Code (行内代码 `code`)
        const inlineCodeRegex = /`([^`\n]+)`/g;
        workingText = workingText.replace(inlineCodeRegex, (match, code) => {
            return `<code class="agent-inline-code">${escapeHtml(code)}</code>`;
        });

        // 5. 粗斜体加粗解析 (成对匹配，天然流式安全)
        workingText = workingText.replace(/\*\*([^\*\n]+)\*\*/g, '<strong>$1</strong>');
        workingText = workingText.replace(/\*([^\*\n]+)\*/g, '<em>$1</em>');

        // 6. 行解析状态机：自动识别列表并拼接普通行
        const finalLines = workingText.split('\n');
        const renderedLines = [];
        let inList = false;
        let listType = null; // 'ul' | 'ol'

        for (let i = 0; i < finalLines.length; i++) {
            const line = finalLines[i];
            const trimmed = line.trim();

            const unorderedMatch = trimmed.match(/^[-*]\s+(.*)$/);
            const orderedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);

            if (unorderedMatch) {
                if (!inList || listType !== 'ul') {
                    if (inList) renderedLines.push(`</${listType}>`);
                    renderedLines.push('<ul class="agent-list-unordered">');
                    inList = true;
                    listType = 'ul';
                }
                renderedLines.push(`<li class="agent-list-item bullet-item">${unorderedMatch[1]}</li>`);
            } else if (orderedMatch) {
                if (!inList || listType !== 'ol') {
                    if (inList) renderedLines.push(`</${listType}>`);
                    renderedLines.push('<ol class="agent-list-ordered">');
                    inList = true;
                    listType = 'ol';
                }
                renderedLines.push(`<li class="agent-list-item ordered-item">${orderedMatch[2]}</li>`);
            } else {
                if (inList) {
                    renderedLines.push(`</${listType}>`);
                    inList = false;
                    listType = null;
                }
                renderedLines.push(line);
            }
        }
        if (inList) {
            renderedLines.push(`</${listType}>`);
        }

        // 用 <br/> 拼接普通文本，但对于已经包含块级列表或表格占位符的行不使用 br 污染
        let htmlResult = "";
        for (let i = 0; i < renderedLines.length; i++) {
            const line = renderedLines[i];
            const isPlaceholderOnly = /^__(?:CODE_BLOCK|TABLE)_PLACEHOLDER_\d+__$/i.test(line.trim());
            const isListTag = /^(?:<\/?ul|<\/?ol>|<\/?li)/i.test(line.trim());

            if (isPlaceholderOnly || isListTag) {
                htmlResult += line + "\n";
            } else {
                htmlResult += (line.trim() === "" ? "<br/>" : line + "<br/>");
            }
        }

        // 7. 顺序还原所有占位符 (使用函数式 Callback 杜绝正则 $ 符号替换 bug)
        for (let i = 0; i < placeholders.length; i++) {
            htmlResult = htmlResult.replace(`__CODE_BLOCK_PLACEHOLDER_${i}__`, () => placeholders[i]);
            htmlResult = htmlResult.replace(`__TABLE_PLACEHOLDER_${i}__`, () => placeholders[i]);
        }

        return htmlResult;
    };

    /**
     * 📊 辅助解析数据表格行并生成高颜值 HTML 表格
     */
    function parseTableRows(rows) {
        if (!rows || rows.length === 0) return "";

        const parseRowCells = (rowText) => {
            const rawCells = rowText.split('|');
            return rawCells.slice(1, rawCells.length - 1).map(c => c.trim());
        };

        const headers = parseRowCells(rows[0]);
        let startIdx = 1;

        if (rows.length > 1 && rows[1].includes('-')) {
            startIdx = 2;
        }

        let tableHtml = `<div class="agent-table-wrapper"><table class="agent-table"><thead><tr>`;
        for (let i = 0; i < headers.length; i++) {
            tableHtml += `<th>${headers[i]}</th>`;
        }
        tableHtml += `</tr></thead><tbody>`;

        for (let i = startIdx; i < rows.length; i++) {
            const cells = parseRowCells(rows[i]);
            tableHtml += `<tr>`;
            for (let j = 0; j < headers.length; j++) {
                const cellVal = cells[j] !== undefined ? cells[j] : "";
                tableHtml += `<td>${cellVal}</td>`;
            }
            tableHtml += `</tr>`;
        }
        tableHtml += `</tbody></table></div>`;
        return tableHtml;
    }
})();
