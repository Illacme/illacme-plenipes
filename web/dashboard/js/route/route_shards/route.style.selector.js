/**
 * 🛣️ [V107.5] Illacme Plenipes Route Matrix - Translation Style Selector Shard
 * 职责：从产品系统全局语种智库动态解析语种元数据、构建带智能描述 Tooltip 的专属译文风格下拉选择器。
 */

(function () {
    /**
     * 🏷️ 从产品系统全局语种智库中动态获取名称与国旗图标（零重复定义）
     */
    window.getProductLanguageMeta = function (code) {
        if (window.availableLangs && Array.isArray(window.availableLangs)) {
            const cleanCode = (code || '').toLowerCase().trim();
            const found = window.availableLangs.find(l => l.code === cleanCode || l.code === code);
            if (found) {
                return { name: found.name || code, flag: found.icon || '🌐' };
            }
        }
        return { name: code ? code.toUpperCase() : 'UNKNOWN', flag: '🌐' };
    };

    /**
     * 🗣️ [V107.5] 构建译文风格下拉选择器（动态接入 治理中心-多语翻译-译文风格 数据源 window.translationStyles 并带智能 Tooltip）
     */
    window.buildTranslationStyleSelectHtml = function (selectedStyle, isLicensed, isExt) {
        if (isExt) {
            return `<select class="setting-input style-input" disabled style="width: 100%; font-size: 0.74rem; padding: 5px 6px; opacity: 0.5;" title="外部直链无需多语翻译">
                <option value="">不适用</option>
            </select>`;
        }

        const stylesObj = window.translationStyles || {
            professional: { name: "💼 商务专业 (Professional)", desc: "正式、严谨，采用严密的行业术语，适用于商业报告、官方规范与业务文档。" },
            casual: { name: "💬 活泼随性 (Casual)", desc: "口语化、自然亲切，注重本地读者的日常表达，适用于个人随笔、博客分享与社媒文案。" },
            literal: { name: "🔍 精准直译 (Literal)", desc: "结构对称、忠于原文，尽可能保留句型与字面对应，适用于学术条约及比对校验场景。" },
            academic: { name: "🎓 学术客观 (Academic)", desc: "客观严谨、使用被动语态与书面学术用词，完美保留 LaTeX 复杂公式与文献脚注。" },
            technical: { name: "💻 技术极客 (Technical)", desc: "保留通用技术术语、代码块与英文缩写不予硬译，符合开发者直觉，适用于技术文档与架构说明。" },
            literary: { name: "🎭 文学唯美 (Literary)", desc: "富有文采与感染力，运用修辞、对仗与地道成语，适合诗歌、散文、小说与深度文化读物。" }
        };

        const current = (selectedStyle || '').trim();
        let currentDesc = '继承全局多语翻译风格设置';
        if (current && stylesObj[current]) {
            currentDesc = stylesObj[current].desc || stylesObj[current].name;
        } else if (current) {
            currentDesc = `自定义专属风格: ${current}`;
        }

        let optionsHtml = `<option value="">继承全局默认</option>`;

        Object.entries(stylesObj).forEach(([key, item]) => {
            const name = item.name || key;
            const isSelected = (current === key) ? 'selected' : '';
            optionsHtml += `<option value="${key}" ${isSelected}>${name}</option>`;
        });

        // 兼容创作者历史可能自定义但在预设中不存在的 key
        if (current && !stylesObj[current]) {
            optionsHtml += `<option value="${current}" selected>⚙️ 自定义风格 (${current})</option>`;
        }

        return `<select class="setting-input style-input" style="width: 100%; font-size: 0.74rem; padding: 5px 6px;" ${!isLicensed ? 'disabled' : ''} title="${currentDesc.replace(/"/g, '&quot;')}" onchange="const descMap = window.translationStyles || {}; const d = descMap[this.value]?.desc || (this.value ? '自定义专属风格: ' + this.value : '继承全局多语翻译风格设置'); this.title = d; syncRouteMatrixToSettings();">
            ${optionsHtml}
        </select>`;
    };
})();
