/**
 * 🌍 [V75.5] Illacme Plenipes Localization - Glossary Import Modal Shard
 * 职责：专有名词保护术语批量导入 SweetAlert2 弹窗、CSV/JSON 解析、冲突与环路检测。
 */

(function () {
    window.openGlossaryImportModal = () => {
        if (typeof Swal === 'undefined') return;

        Swal.fire({
            title: '📄 批量导入保护术语',
            html: `
                <div style="text-align: left; font-size: 0.8rem; color: var(--text-dim);">
                    <p style="margin-bottom: 10px;">支持两种导入方式：</p>
                    <p>1. <b>粘贴导入</b>：在下方文本域中输入术语项（格式为 <b>原文=译文</b>，每行一项）。</p>
                    <p style="margin-bottom: 12px;">2. <b>文件导入</b>：选择或拖拽本地 <b>.csv</b> 或 <b>.json</b> 文件。</p>
                    
                    <div style="margin-bottom: 12px; display: flex; gap: 15px; align-items: center; background: rgba(255,255,255,0.02); padding: 8px; border-radius: 6px; border: 1px solid var(--glass-border);">
                        <span style="font-size: 0.72rem; color: var(--text-dim);">导入模式：</span>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.72rem; color: var(--text-bright, #fff);">
                            <input type="radio" name="glossary-import-mode" value="merge" checked style="cursor: pointer; transform: scale(0.9);"> 📥 增量合并
                        </label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.72rem; color: var(--text-bright, #fff);">
                            <input type="radio" name="glossary-import-mode" value="replace" style="cursor: pointer; transform: scale(0.9);"> 🔄 覆盖替换
                        </label>
                    </div>
                    
                    <div style="margin-bottom: 12px;">
                        <input type="file" id="glossary-file-uploader" accept=".csv,.json" style="width: 100%; font-size: 0.75rem; background: var(--black-20); padding: 5px; border-radius: 4px; border: 1px solid var(--glass-border); color: var(--text-primary);">
                    </div>
                    
                    <textarea id="glossary-import-textarea" placeholder="原稿词汇1=保护译词1&#10;原稿词汇2=保护译词2" 
                              style="width: 100%; height: 160px; background: var(--black-20); color: var(--text-primary); border: 1px solid var(--glass-border); border-radius: 6px; padding: 10px; font-family: var(--font-mono); font-size: 0.75rem; box-sizing: border-box; resize: vertical;"></textarea>
                </div>
            `,
            showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)',
            color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '⚡ 开始导入',
            cancelButtonText: '❌ 取消',
            customClass: {
                popup: 'glass-panel',
                confirmButton: 'primary-btn glow-btn',
                cancelButton: 'danger-btn'
            },
            didOpen: () => {
                const uploader = document.getElementById('glossary-file-uploader');
                const textarea = document.getElementById('glossary-import-textarea');
                if (uploader && textarea) {
                    uploader.onchange = (e) => {
                        const file = e.target.files[0];
                        if (!file) return;
                        const reader = new FileReader();
                        reader.onload = (evt) => {
                            const content = evt.target.result;
                            if (file.name.endsWith('.json')) {
                                try {
                                    const obj = JSON.parse(content);
                                    let text = "";
                                    let targetObj = obj;
                                    if (obj[window.currentGlossaryLang]) {
                                        targetObj = obj[window.currentGlossaryLang];
                                    }
                                    for (const [k, v] of Object.entries(targetObj)) {
                                        if (typeof v === 'string') text += `${k}=${v}\n`;
                                    }
                                    textarea.value = text;
                                } catch (err) {
                                    Swal.showValidationMessage('❌ 无法解析此 JSON 文件！');
                                }
                            } else if (file.name.endsWith('.csv')) {
                                const lines = content.split('\n');
                                let text = "";
                                lines.forEach(line => {
                                    const parts = line.split(',');
                                    if (parts.length >= 2) {
                                        const k = parts[0].replace(/"/g, '').trim();
                                        const v = parts[1].replace(/"/g, '').trim();
                                        if (k && v && k !== 'source' && k !== 'src') {
                                            text += `${k}=${v}\n`;
                                        }
                                    }
                                });
                                textarea.value = text;
                            }
                        };
                        reader.readAsText(file, 'UTF-8');
                    };
                }
            },
            preConfirm: () => {
                const textarea = document.getElementById('glossary-import-textarea');
                if (!textarea || !textarea.value.trim()) {
                    Swal.showValidationMessage('❌ 导入文本域不能为空！');
                    return false;
                }

                const mode = document.querySelector('input[name="glossary-import-mode"]:checked')?.value || 'merge';

                const text = textarea.value.trim();
                const lines = text.split('\n');
                const newItems = {};
                lines.forEach(line => {
                    const parts = line.split(/[=|:]/);
                    if (parts.length >= 2) {
                        const src = parts[0].trim();
                        const dst = parts[1].trim();
                        if (src && dst) {
                            newItems[src] = dst;
                        }
                    }
                });

                const count = Object.keys(newItems).length;
                if (count === 0) {
                    Swal.showValidationMessage('❌ 未解析到任何合法的原文=译文项！');
                    return false;
                }

                // 安全环路与冲突校验
                const gov = window.settingsData?.translation?.governance || {};
                const glossary = gov.glossary || {};
                const currentLang = window.currentGlossaryLang || 'en';
                const existingGlossary = (mode === 'replace') ? {} : (glossary[currentLang] || {});

                // 1. 一词多译冲突校验 (Ambiguity Check)
                const conflicts = [];
                for (const [src, dst] of Object.entries(newItems)) {
                    if (existingGlossary[src] && existingGlossary[src] !== dst) {
                        conflicts.push(`【${src}】已映射为【${existingGlossary[src]}】（拟更新为【${dst}】）`);
                    }
                }
                if (conflicts.length > 0) {
                    Swal.showValidationMessage(`⚠️ 冲突: ${conflicts.slice(0, 1).join('; ')}${conflicts.length > 1 ? ' ...' : ''}`);
                    return false;
                }

                // 2. 环路依赖深度检测 (Cycle Detection)
                const tempMap = { ...existingGlossary, ...newItems };
                const hasCycle = (start) => {
                    let current = start;
                    const visited = new Set();
                    while (current && tempMap[current]) {
                        if (visited.has(current)) return true;
                        visited.add(current);
                        current = tempMap[current];
                    }
                    return false;
                };

                const cycleKeys = [];
                for (const k of Object.keys(tempMap)) {
                    if (hasCycle(k)) {
                        cycleKeys.push(k);
                    }
                }
                if (cycleKeys.length > 0) {
                    Swal.showValidationMessage(`❌ 环路依赖警告: 词项 【${cycleKeys.slice(0, 2).join(' / ')}】 构成了循环映射关系！`);
                    return false;
                }

                return {
                    text: text,
                    mode: mode
                };
            }
        }).then(async (result) => {
            if (result.isConfirmed && result.value) {
                const { text, mode } = result.value;
                const lines = text.split('\n');
                const newItems = {};
                lines.forEach(line => {
                    const parts = line.split(/[=|:]/);
                    if (parts.length >= 2) {
                        const src = parts[0].trim();
                        const dst = parts[1].trim();
                        if (src && dst) {
                            newItems[src] = dst;
                        }
                    }
                });

                const gov = window.settingsData?.translation?.governance || {};
                const glossary = { ...(gov.glossary || {}) };
                const currentLang = window.currentGlossaryLang || 'en';

                if (mode === 'replace') {
                    glossary[currentLang] = {};
                } else if (!glossary[currentLang]) {
                    glossary[currentLang] = {};
                } else {
                    glossary[currentLang] = { ...glossary[currentLang] };
                }

                Object.assign(glossary[currentLang], newItems);
                const count = Object.keys(newItems).length;

                if (typeof addAudit === 'function') {
                    addAudit(`📥 正在以【${mode === 'replace' ? '覆盖替换' : '增量合并'}】模式批量导入并保存 ${count} 个保护词条...`);
                }

                if (typeof window.syncTranslationGovernanceField === 'function') {
                    await window.syncTranslationGovernanceField('translation.governance.glossary', glossary);
                }

                window.currentGlossaryPage = 1;
                if (typeof window.refreshGlossaryUI === 'function') {
                    window.refreshGlossaryUI();
                }

                Swal.fire({
                    title: '🎉 导入成功',
                    text: `成功以【${mode === 'replace' ? '覆盖替换' : '增量合并'}】模式导入并保存了 ${count} 条保护术语！`,
                    icon: 'success',
                    background: 'hsla(236, 37%, 8%, 0.95)',
                    color: 'var(--text-bright, #ffffff)',
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        });
    };
})();
