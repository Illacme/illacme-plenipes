# -*- coding: utf-8 -*-
"""
🧪 单元测试：排版前置仿真工坊（Live Preview）真机多机型、一键复制与微调
覆盖模块：
1. web/dashboard/js/editorial/syndicate_shards/syndicate.preview.js:
   - 真机多机型仿真框架 (iPhone 灵动岛 / Android 打孔 / 平板 / 宽屏桌面)
   - 字号微调与 CSS 变量水合
2. web/dashboard/js/editorial/syndicate_shards/syndicate.exporter.js:
   - 平台自适应一键复制主按钮 (微信公众号富文本 / 知乎富文本 / 掘金排版 / 小红书笔记)
   - 多机型与字号调度器 (setSyndicatePreviewDevice, setSyndicateFontSize)
🛡️ [SOP-01 规范]：单文件物理行数严格 ≤ 300 行。
"""

import unittest
import subprocess


class TestSyndicateLivePreviewWorkshop(unittest.TestCase):
    """测试排版前置仿真工坊真机机型、一键复制与微调能力"""

    def test_live_preview_device_chassis_and_toolbar(self):
        """Node.js 前端沙箱运行断言：验证真机机型外壳、自适应复制按钮与字号微调 (SOP 规则 7)"""
        node_script = """
        const fs = require('fs');
        const vm = require('vm');

        let createdModal = null;
        const mockElements = {};

        const sandbox = {
            window: {},
            document: {
                getElementById: (id) => mockElements[id] || null,
                createElement: (tag) => {
                    const el = {
                        id: '',
                        className: '',
                        classList: {
                            _classes: new Set(),
                            add: function(...c) { c.forEach(x => this._classes.add(x)); },
                            remove: function(...c) { c.forEach(x => this._classes.delete(x)); },
                            contains: function(c) { return this._classes.has(c); },
                            toggle: function(c) { if (this._classes.has(c)) this._classes.delete(c); else this._classes.add(c); }
                        },
                        style: {
                            _props: {},
                            setProperty: function(k, v) { this._props[k] = v; },
                            getPropertyValue: function(k) { return this._props[k] || ''; }
                        },
                        innerHTML: '',
                        onclick: null
                    };
                    return el;
                },
                body: { appendChild: (el) => { createdModal = el; } },
                addEventListener: () => {},
                removeEventListener: () => {},
                querySelector: () => null,
                querySelectorAll: () => []
            },
            navigator: {
                clipboard: {
                    write: async () => {},
                    writeText: async () => {}
                }
            },
            showToast: () => {}
        };
        sandbox.window = sandbox;
        const ctx = vm.createContext(sandbox);

        // 加载预览与导出分片代码
        const exporterCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.exporter.js', 'utf8');
        vm.runInContext(exporterCode, ctx);
        const previewCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.preview.js', 'utf8');
        vm.runInContext(previewCode, ctx);

        // 1. 验证函数挂载
        const expectedFns = [
            'openSyndicateLivePreviewModal', 'closeSyndicateLivePreviewModal', 'switchSyndicatePreviewTarget',
            'renderSyndicateCardPreview', 'setSyndicatePreviewDevice', 'setSyndicateFontSize',
            'copyWeChatRichText', 'copyZhihuRichText', 'copyJuejinMarkdown', 'copyXiaohongshuNote'
        ];
        for (const fn of expectedFns) {
            if (typeof sandbox.window[fn] !== 'function') {
                throw new Error(fn + ' is not mounted to window');
            }
        }

        // 2. 模拟容器元素
        const previewContainer = { innerHTML: '', style: {} };
        const statsSlot = { innerHTML: '' };
        const actionsSlot = { innerHTML: '' };
        const bodySlot = {
            id: 'preview-rendered-body-slot',
            style: {
                _props: {},
                setProperty: function(k, v) { this._props[k] = v; },
                fontSize: ''
            }
        };

        mockElements['syndicate-card-preview-renderer'] = previewContainer;
        mockElements['syndicate-modal-stats-capsule'] = statsSlot;
        mockElements['syndicate-modal-actions-slot'] = actionsSlot;
        mockElements['preview-rendered-body-slot'] = bodySlot;

        // Mock 预览数据返回
        sandbox.window.fetchSyndicatePreviewData = async () => ({
            status: 'success',
            title: '全渠道仿真前置审查测试',
            clean_title: '全渠道仿真前置审查测试',
            digest: '这是一篇测试导读摘要',
            rendered_html: '<h1>标题</h1><p>这是一段高保真排版正文内容。</p>',
            rendered_markdown: '正文 Markdown',
            stats: { word_count: 520, reading_time_min: 2, footnotes_count: 3, title_length: 12 },
            compliance: { platform_rules: '微信公众号高保真内联排版规则' }
        });

        // 3. 异步沙箱执行测试
        (async () => {
            sandbox.window._previewDevice = 'iphone';
            sandbox.window._syndicateFontSize = 'medium';
            await sandbox.window.renderSyndicateCardPreview('wechat');

            const html = previewContainer.innerHTML;
            if (!html.includes('preview-viewport-chassis--iphone')) {
                throw new Error('Missing iPhone chassis class in preview HTML: ' + html);
            }
            if (!html.includes('ios-dynamic-island')) {
                throw new Error('Missing iOS dynamic island in preview HTML');
            }
            if (!html.includes('09:41')) {
                throw new Error('Missing iOS status bar clock');
            }
            if (!actionsSlot.innerHTML.includes('复制公众号富文本')) {
                throw new Error('Missing WeChat rich text copy button in toolbar');
            }

            // 4. 测试知乎渠道自适应按钮
            await sandbox.window.renderSyndicateCardPreview('zhihu');
            if (!actionsSlot.innerHTML.includes('复制知乎富文本')) {
                throw new Error('Missing Zhihu rich text copy button in toolbar');
            }

            // 5. 测试小红书渠道 (3:4 竖屏 + 复制小红书笔记)
            await sandbox.window.renderSyndicateCardPreview('xiaohongshu');
            const xhsHtml = previewContainer.innerHTML;
            if (!xhsHtml.includes('preview-xhs-badge')) {
                throw new Error('Missing Xiaohongshu header badge in preview HTML');
            }
            if (!actionsSlot.innerHTML.includes('复制小红书笔记')) {
                throw new Error('Missing Xiaohongshu copy button in toolbar');
            }

            // 6. 测试 Android 打孔屏机型切换
            sandbox.window.setSyndicatePreviewDevice('android');
            await sandbox.window.renderSyndicateCardPreview('wechat');
            const androidHtml = previewContainer.innerHTML;
            if (!androidHtml.includes('preview-viewport-chassis--android')) {
                throw new Error('Missing Android chassis class in preview HTML');
            }
            if (!androidHtml.includes('android-camera-hole')) {
                throw new Error('Missing Android camera hole in preview HTML');
            }

            // 7. 测试字号微调算子
            sandbox.window.setSyndicateFontSize('large');
            if (sandbox.window._syndicateFontSizePx !== '18px') {
                throw new Error('Expected 18px for large font size, got ' + sandbox.window._syndicateFontSizePx);
            }
            if (bodySlot.style.fontSize !== '18px') {
                throw new Error('Expected bodySlot font size to be 18px, got ' + bodySlot.style.fontSize);
            }

            // 8. 测试宽屏桌面审查模式 (含 macOS 控制点)
            sandbox.window.setSyndicatePreviewDevice('desktop');
            await sandbox.window.renderSyndicateCardPreview('wechat');
            const desktopHtml = previewContainer.innerHTML;
            if (!desktopHtml.includes('preview-viewport-chassis--desktop')) {
                throw new Error('Missing Desktop chassis class in preview HTML');
            }
            if (!desktopHtml.includes('preview-chassis-mac-controls')) {
                throw new Error('Missing macOS window controls in desktop preview');
            }
            console.log('✅ All Live Preview Device & Copy assertions passed successfully!');
        })().catch(err => {
            console.error(err);
            process.exit(1);
        });
        """
        proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node.js 仿真排版工坊沙箱执行失败: {proc.stderr}")

    def test_preview_css_word_wrap_and_title_wrapping(self):
        """静态断言：检查 CSS 中真机预览标题具备自动折行与防溢出样式"""
        with open("web/dashboard/css/components/syndicate.preview.css", "r", encoding="utf-8") as f:
            css_content = f.read()

        self.assertIn(".preview-general-title", css_content)
        self.assertIn("white-space: normal;", css_content)
        self.assertIn("word-break: break-word;", css_content)
        self.assertIn("overflow-wrap: break-word;", css_content)

        # 确保 dashboard.base.css 不再向全局污染 bare h1 { white-space: nowrap; }
        with open("web/dashboard/css/dashboard.base.css", "r", encoding="utf-8") as f:
            base_css = f.read()
        self.assertNotIn("\nh1 {\n    font-size: 1.05rem;\n    letter-spacing: 0.5px;\n    font-weight: 300;\n    white-space: nowrap;\n}", base_css)


if __name__ == "__main__":
    unittest.main()
