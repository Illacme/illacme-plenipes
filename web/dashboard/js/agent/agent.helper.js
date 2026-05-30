/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) UI Parser & Link Helper - SOP Compliant
 * 职责：负责思维链及文本消息中文件相对路径的提取、超链接渲染，以及 XML 节点的抽取美化与路径自愈。
 * 遵循 SOP-02 模块拆分协议与 300 行核心复杂度红线。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.helper.js initializing');

    /**
     * 🛡️ 辅助 HTML 转义函数防止 XSS 注入
     */
    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    /**
     * 🧠 智能文稿定位与编辑器跳转引擎
     * 解决大模型可能输出不带路径的短文件名（如 README.md）导致加载失败的问题。
     * 优先进行数据库检索寻址，保证 100% 精准打开正确 file.
     */
    window.openEditorSmart = async function(path) {
        if (typeof window.openEditor !== 'function') {
            console.warn("openEditor not found");
            return;
        }
        try {
            const cleanName = path.trim();
            const cleanNameNoExt = cleanName.replace(/\.mdx?$/, '');
            
            // 使用联邦检索寻找该文件
            const searchUrl = `/api/vault/search?q=${encodeURIComponent(cleanNameNoExt)}&limit=10`;
            const res = await (
                typeof window.apiFetch === 'function' ? window.apiFetch(searchUrl) :
                (typeof apiFetch === 'function' ? apiFetch(searchUrl) : fetch(searchUrl).then(r => r.json()))
            );
            
            if (res && res.items && res.items.length > 0) {
                // 1. 精准匹配：是否存在 rel_path 完全等于 path 的
                const exactMatch = res.items.find(item => item.rel_path === cleanName);
                if (exactMatch) {
                    window.openEditor(exactMatch.rel_path);
                    return;
                }
                
                // 2. 文件名匹配：是否存在文件名 (stem) 与 path 或 cleanNameNoExt 匹配 of the item
                const fileMatch = res.items.find(item => {
                    const parts = item.rel_path.split('/');
                    const filename = parts[parts.length - 1];
                    return filename.toLowerCase() === cleanName.toLowerCase() || 
                           filename.replace(/\.mdx?$/, '').toLowerCase() === cleanNameNoExt.toLowerCase();
                });
                if (fileMatch) {
                    window.openEditor(fileMatch.rel_path);
                    return;
                }
                
                // 3. 降级：如果找到了相关的文件，打开第一个匹配项
                window.openEditor(res.items[0].rel_path);
            } else {
                // 实在找不到匹配的记录，降级使用原始路径直接加载
                window.openEditor(cleanName);
            }
        } catch (e) {
            console.error("Smart open editor error, falling back:", e);
            window.openEditor(path);
        }
    };

    /**
     * 📁 自动格式化消息中的文稿路径为可点击的超链接，并美化 <tool_call> 节点结构
     * 流式状态下全能防护：实时解析未闭合 XML，临时隐藏残缺 HTML，防御任何隐形内容丢失。
     */
    window.formatFileLinks = function(text) {
        if (!text) return "";

        const placeholders = [];
        let workingText = text;

        // 1. 抽取所有【已闭合】的 <tool_call> 块并保存为占位符，防止渲染裸露的 XML 节点源码
        const toolCallRegex = /\s*<tool_call>([\s\S]*?)<\/tool_call>/gi;
        workingText = workingText.replace(toolCallRegex, (match, blockContent) => {
            const placeholderId = `__TOOL_CALL_PLACEHOLDER_${placeholders.length}__`;
            
            // 解析该 tool_call 块
            let funcName = "unknown";
            const funcMatch = blockContent.match(/<function=([a-zA-Z0-9_\-]+)>/i);
            if (funcMatch) {
                funcName = funcMatch[1];
            } else {
                const funcTagMatch = blockContent.match(/<function>([\s\S]*?)<\/function>/i);
                if (funcTagMatch) funcName = funcTagMatch[1].trim();
            }

            const paramRegex = /<parameter=([a-zA-Z0-9_\-]+)>([\s\S]*?)<\/parameter>/gi;
            let paramsHtml = "";
            let pMatch;
            while ((pMatch = paramRegex.exec(blockContent)) !== null) {
                const paramName = pMatch[1];
                let paramVal = pMatch[2].trim();

                const fileRegex = /^([a-zA-Z0-9_\-\/]+\.(?:md|mdx|markdown))$/i;
                if (fileRegex.test(paramVal)) {
                    paramVal = `<a href="#" onclick="event.preventDefault(); if (typeof window.openEditorSmart === 'function') { window.openEditorSmart('${paramVal.replace(/'/g, "\\'")}') } else if (typeof window.openEditor === 'function') { window.openEditor('${paramVal.replace(/'/g, "\\'")}') } else { console.warn('openEditor not found'); }" class="clickable-vault-link" title="点击打开此文稿编辑器">${paramVal}</a>`;
                } else {
                    if (paramVal.length > 120) {
                        paramVal = escapeHtml(paramVal.substring(0, 120)) + "... (已截断)";
                    } else {
                        paramVal = escapeHtml(paramVal);
                    }
                }
                paramsHtml += `<div style="margin-top: 3px;"><span style="color: var(--accent-secondary);">${paramName}</span>: ${paramVal}</div>`;
            }

            const toolCallHtml = `<div class="agent-msg tool-msg" style="margin: 8px 0; padding: 8px 12px; border-radius: 6px; border-left: 3px solid var(--accent-orange, #ff9d00); background: rgba(255, 157, 0, 0.03); font-family: var(--font-mono); text-align: left; word-break: break-all;"><span style="font-weight: bold; color: var(--accent-orange, #ff9d00);">🔧 CALL: ${funcName}</span>${paramsHtml ? `<div style="margin-top: 4px; font-size: 0.7rem; color: var(--text-dim); padding-left: 10px; border-left: 1px dashed rgba(255, 157, 0, 0.2);">${paramsHtml}</div>` : ''}</div>`;

            placeholders.push(toolCallHtml);
            return placeholderId;
        });

        // 2. 抽取并替换当前【未闭合】且仍在流式传输中的不完整 <tool_call> 块
        const unclosedToolCallRegex = /\s*<tool_call>([\s\S]*)$/i;
        let isStreamingTool = false;
        let streamingToolHtml = "";
        
        workingText = workingText.replace(unclosedToolCallRegex, (match, blockContent) => {
            isStreamingTool = true;
            
            // 尝试提取已经输出完毕的函数名称
            let funcName = "Preparing...";
            const funcMatch = blockContent.match(/<function=([a-zA-Z0-9_\-]+)>/i);
            if (funcMatch) {
                funcName = funcMatch[1];
            } else {
                const funcTagMatch = blockContent.match(/<function>([\s\S]*)$/i);
                if (funcTagMatch) {
                    const temp = funcTagMatch[1].trim();
                    if (temp) funcName = temp;
                }
            }

            streamingToolHtml = `<div class="agent-msg tool-msg" style="margin: 8px 0; padding: 8px 12px; border-radius: 6px; border-left: 3px solid var(--accent-orange, #ff9d00); background: rgba(255, 157, 0, 0.03); font-family: var(--font-mono); text-align: left; word-break: break-all;"><span style="font-weight: bold; color: var(--accent-orange, #ff9d00);"><span class="thinking-badge-pulse"></span>🔧 CALL: ${funcName} (Preparing...)</span></div>`;
            
            return "__STREAMING_TOOL_PLACEHOLDER__";
        });

        // 3. 防御性处理：在流式输出中临时切除尾部不完整的 HTML/XML 残缺标签（例如正在打字输出中的 <t, <to 等）
        // 这一物理动作彻底避免了浏览器解析 unclosed tag 导致后续正文/思维链发生隐藏不可见的重大 Bug
        const unclosedTagRegex = /<[a-zA-Z0-9_\-\s=\/'"]*$/;
        workingText = workingText.replace(unclosedTagRegex, "");

        // 4. 对普通文本中的文稿相对路径进行超链接替换
        const fileRegex = /`?([a-zA-Z0-9_\-\/]+\.(?:md|mdx|markdown))`?/gi;
        let formattedText = workingText.replace(fileRegex, (match, path) => {
            if (!path) return match;
            return `<a href="#" onclick="event.preventDefault(); if (typeof window.openEditorSmart === 'function') { window.openEditorSmart('${path.replace(/'/g, "\\'")}') } else if (typeof window.openEditor === 'function') { window.openEditor('${path.replace(/'/g, "\\'")}') } else { console.warn('openEditor not found'); }" class="clickable-vault-link" title="点击打开此文稿编辑器">${path}</a>`;
        });

        // 5. 还原占位符
        if (isStreamingTool) {
            formattedText = formattedText.replace("__STREAMING_TOOL_PLACEHOLDER__", streamingToolHtml);
        }
        for (let i = 0; i < placeholders.length; i++) {
            formattedText = formattedText.replace(`__TOOL_CALL_PLACEHOLDER_${i}__`, placeholders[i]);
        }

        return formattedText;
    };
})();
