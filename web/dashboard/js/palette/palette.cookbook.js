/**
 * 📖 [V1.0] Command Palette - Cookbook Guides & In-App Reader (🛡️ SOP-01 行数 ≤ 300)
 * 职责：注册实战指南命令，支持在工作台原地以高质感毛玻璃弹窗阅读 Cookbook。
 */

(function () {
    const COOKBOOK_DATA = {
        blog: {
            title: '🚀 场景一：将 Obsidian / 本地笔记一键发布为个人独立多语言博客',
            docPath: 'docs/cookbook/01_quickstart_blog_hosting.md',
            content: `### 🎯 目标与收益
将本地 Markdown 文库全自动翻译为多语言版本，并一键推送到 GitHub Pages 或 Vercel 静态网站。

---

### ⏱️ 极简操作 3 步法
1. **关联文库**：在 **「⚙️ 治理中心 ➔ 📂 存储适配」** 填入笔记物理路径 (\`vault_root\`)；
2. **配置托管凭据**：在 **「🧩 插件中心」** 启用 GitHub Pages / Vercel，点击 **「🔑 本地一键免密授权」** 即可免填 Token 自动识别；
3. **一键全域发布**：点击右上角 **「🚀 全站发布」**，完成后在发布中心直接点击 **\`GitHub Pages ↗\`** 直达公网阅读！`
        },
        syndicate: {
            title: '🛰️ 场景二：单篇长文一键同步分发至微信公众号、知乎与 Dev.to 矩阵',
            docPath: 'docs/cookbook/02_syndicate_to_social_media.md',
            content: `### 🎯 目标与收益
写完长文后，一次点击瞬间推送到各大技术社区与社交平台，无需在各个后台重复排版与手动上传图片。

---

### ⏱️ 极简操作 3 步法
1. **激活渠道**：进入 **「🧩 插件中心」** 填入微信公众号 AppID/AppSecret、知乎或 Dev.to 密钥；
2. **打开分发抽屉**：在 **「📂 原稿文库」** 找到目标文章，点击右侧 **「🌐 发布/分发」**；
3. **勾选并一键同步**：选择要投递的平台，点击 **「🚀 开始矩阵分发」**，系统自动清洗格式、转存插图并注入独立主站的 Canonical 声明。`
        },
        ebook: {
            title: '📚 场景三：一键装帧排版导出双语对照版 DOCX / PDF / EPUB 出版级电子书',
            docPath: 'docs/cookbook/03_export_polyglot_ebook.md',
            content: `### 🎯 目标与收益
将系列文章或单篇长文一键编译为具备印刷出版品质的电子书（Word 原生矢量公式、双语对照排版、深层目录）。

---

### ⏱️ 极简操作 3 步法
1. **进入装帧中心**：在 **「📂 原稿文库」** 顶部切换至 **「📖 装帧书架」**；
2. **选择目标格式**：勾选 \`DOCX\`（Word 表格对照）、\`PDF\` 或 \`EPUB 3.0\`，开启“双语对照排版”；
3. **一键装订编译**：点击 **「⚡ 启动装帧编译」**，数秒后即可在卡片上直接点击下载编译产物。`
        },
        covers: {
            title: '🎨 场景四：为文章生成高质感 AI 封面与本地 OG 社交卡片',
            docPath: 'docs/cookbook/04_generate_covers_and_assets.md',
            content: `### 🎯 目标与收益
无需打开专业作图软件，秒级为文章生成带极光弥散发光的 1200×630 科技卡片，或一键挑选高清免版权配图。

---

### ⏱️ 极简操作 3 步法
1. **针对原稿定制**：在文库列表点击文章右侧 **「🎨 封面设计」**，直达设计中心目标锁定模式；
2. **选择引擎生成**：
   * **极客科技风**：选择 \`本地渲染 (Local OG)\`，秒级生成 1200×630 极光卡片；
   * **实拍免版权**：选择 \`Unsplash / Pexels\` 挑选高清摄影图；
   * **AI 意境绘图**：选择 \`DALL-E 3 / Flux\` 自动生成 Prompt；
3. **一键落盘回填**：点击 **「✅ 应用为此文封面」**，自动写入 Frontmatter (\`cover:\`) 并返回原稿文库。`
        }
    };

    window.openCookbookModal = function (key) {
        const item = COOKBOOK_DATA[key];
        if (!item) return;

        let renderedBody = item.content;
        if (window.marked && typeof window.marked.parse === 'function') {
            renderedBody = window.marked.parse(item.content);
        }

        const modalHtml = `
            <div class="cookbook-modal-body" style="text-align: left; font-size: 0.88rem; line-height: 1.6; max-height: 60vh; overflow-y: auto; padding: 4px 8px;">
                ${renderedBody}
                <div style="margin-top: 18px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-secondary, #888);">
                    <span>📄 物理文档源: <code>${item.docPath}</code></span>
                    <span style="color: var(--accent-color, #00f2fe);">按 ESC 或点击外部即可关闭</span>
                </div>
            </div>
        `;

        if (window.Swal) {
            window.Swal.fire({
                title: `<div style="font-size: 1.05rem; font-weight: 700; text-align: left; padding: 2px 4px;">${item.title}</div>`,
                html: modalHtml,
                width: 680,
                showConfirmButton: true,
                confirmButtonText: '明白，去实操',
                background: 'rgba(15, 20, 32, 0.95)',
                color: '#fff',
                customClass: {
                    popup: 'swal2-glass-modal',
                    confirmButton: 'primary-btn glow-btn'
                }
            });
        } else {
            alert(item.title + '\n\n' + item.content);
        }
    };

    window.getCookbookCommands = function () {
        return [
            {
                id: 'cookbook_blog',
                title: '实战指南 ➔ 一键发布独立多语言博客 (GitHub Pages / Vercel)',
                icon: '🚀',
                shortcut: 'Guide 1',
                action: () => window.openCookbookModal('blog')
            },
            {
                id: 'cookbook_syndicate',
                title: '实战指南 ➔ 微信公众号、知乎与 30+ 社交矩阵同步',
                icon: '🛰️',
                shortcut: 'Guide 2',
                action: () => window.openCookbookModal('syndicate')
            },
            {
                id: 'cookbook_ebook',
                title: '实战指南 ➔ 导出双语对照 DOCX / PDF / EPUB 出版级电子书',
                icon: '📚',
                shortcut: 'Guide 3',
                action: () => window.openCookbookModal('ebook')
            },
            {
                id: 'cookbook_covers',
                title: '实战指南 ➔ AI 智能生图与本地极客 OG 封面设计',
                icon: '🎨',
                shortcut: 'Guide 4',
                action: () => window.openCookbookModal('covers')
            }
        ];
    };
})();
