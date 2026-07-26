// 独立模块：各主题 1:1 网页 Mockup 视图 DOM 结构生成器
(function() {
    window.getThemeVerticalMockupContent = function(themeId) {
        switch (themeId) {
            case 'starlight':
                return `
                    <div class="vertical-page-mockup" style="background: #0f0b1a; width:100%; display:flex; flex-direction:column; color: #e2d9f3; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#181229; border-bottom:1px solid #2d2244; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#a855f7;"><span>🌟</span> Starlight</div>
                            <div style="background:#271c3d; border-radius:3px; padding:1px 6px; font-size:7px; color:#c084fc;">🔍 Search docs</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #2e1065, #0f0b1a); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px; border-bottom:1px solid #23183b;">
                            <div style="font-size:12px; font-weight:900; color:#f3e8ff; letter-spacing:0.5px;">Starlight Docs</div>
                            <div style="font-size:7px; color:#c084fc; max-width:85%; line-height:1.2;">Build beautiful, accessible documentation websites with Astro.</div>
                            <div style="background:#9333ea; color:#fff; font-size:7px; font-weight:bold; padding:3px 10px; border-radius:12px; margin-top:2px;">Get Started</div>
                        </div>
                        <div style="padding:12px; display:flex; flex-direction:column; gap:8px; background:#0b0814;">
                            <div style="font-size:8px; font-weight:bold; color:#a855f7;">FEATURED MODULES</div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:#170f2b; border:1px solid #2e1e52; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#e9d5ff;">🚀 Lightning Fast</div>
                                    <div style="font-size:6px; color:#9381b8; margin-top:2px;">Zero JS by default for ultra performance.</div>
                                </div>
                                <div style="background:#170f2b; border:1px solid #2e1e52; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#e9d5ff;">🌐 i18n Ready</div>
                                    <div style="font-size:6px; color:#9381b8; margin-top:2px;">Built-in internationalization support.</div>
                                </div>
                            </div>
                            <div style="background:#150b29; border:1px solid #3b2070; border-radius:4px; padding:6px 8px; font-family:monospace; font-size:6.5px; color:#d8b4fe; margin-top:2px;">
                                <span style="color:#f472b6;">import</span> { <span style="color:#38bdf8;">defineConfig</span> } <span style="color:#f472b6;">from</span> <span style="color:#a3e635;">'astro/config'</span>;
                            </div>
                        </div>
                        <div style="padding:10px; background:#07040d; border-top:1px solid #1a102e; text-align:center; font-size:6.5px; color:#6b5b95; flex-shrink:0;">
                            Built with Astro Starlight Engine • Sovereign Edition
                        </div>
                    </div>`;
            case 'docusaurus':
                return `
                    <div class="vertical-page-mockup" style="background: #1b1b1d; width:100%; display:flex; flex-direction:column; color: #e3e3e3; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#242526; border-bottom:1px solid #333437; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#25c2a0;"><span>🦖</span> Docusaurus</div>
                            <div style="display:flex; gap:6px; font-size:7px; color:#aaa;"><span>Docs</span><span>Tutorial</span><span style="color:#25c2a0;">v3.0</span></div>
                        </div>
                        <div style="padding:14px 12px; background:linear-gradient(180deg, #182823, #1b1b1d); display:flex; flex-direction:column; align-items:center; text-align:center; gap:5px; border-bottom:1px solid #2d2f31;">
                            <div style="font-size:12px; font-weight:bold; color:#25c2a0;">Build optimized websites quickly</div>
                            <div style="font-size:7px; color:#aaa; max-width:85%; line-height:1.2;">Focus on content while Docusaurus handles the static site build.</div>
                        </div>
                        <div style="padding:10px 12px; display:flex; flex-direction:column; gap:6px; background:#141416;">
                            <div style="background:rgba(37,194,160,0.08); border-left:3px solid #25c2a0; padding:5px 7px; font-size:7px; color:#a3e635;">
                                <b>💡 Tip:</b> Easy to maintain and powered by React.
                            </div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-top:2px;">
                                <div style="background:#242526; border:1px solid #333437; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#fff;">⚛️ Powered by React</div>
                                    <div style="font-size:6px; color:#888; margin-top:2px;">Extend layout with React components.</div>
                                </div>
                                <div style="background:#242526; border:1px solid #333437; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#fff;">🎯 Pluggable</div>
                                    <div style="font-size:6px; color:#888; margin-top:2px;">Flexible plugin architecture.</div>
                                </div>
                            </div>
                            <div style="background:#242526; border:1px solid #333437; border-radius:4px; padding:6px; font-family:monospace; font-size:6.5px; color:#4ade80;">
                                npx create-docusaurus@latest my-website
                            </div>
                        </div>
                        <div style="padding:8px; background:#101012; border-top:1px solid #222; text-align:center; font-size:6.5px; color:#666; flex-shrink:0;">
                            Copyright © Meta Platforms, Inc. Built with Docusaurus.
                        </div>
                    </div>`;
            case 'sovereign':
            case 'default':
                return `
                    <div class="vertical-page-mockup" style="background: #09090b; width:100%; display:flex; flex-direction:column; color: #f4f4f5; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:linear-gradient(90deg, #18181b, #27272a); border-bottom:1px solid #3f3f46; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:900; color:#fbbf24; letter-spacing:1px;"><span>👑</span> SOVEREIGN</div>
                            <div style="display:flex; gap:8px; font-size:7px; color:#e4e4e7;"><span>JOURNAL</span><span>MANIFESTO</span></div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #271a00, #09090b); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px; border-bottom:1px solid #27272a;">
                            <div style="font-size:13px; font-weight:900; color:#fef08a; letter-spacing:1px;">Sovereign Studio</div>
                            <div style="font-size:7px; color:#d4d4d8; max-width:85%; line-height:1.2;">High-end digital publication engine with glassmorphic aesthetic.</div>
                            <div style="background:linear-gradient(90deg, #d97706, #b45309); color:#fff; font-size:7px; font-weight:bold; padding:3px 10px; border-radius:12px; margin-top:2px;">EXPLORE ISSUES</div>
                        </div>
                        <div style="padding:10px; display:flex; flex-direction:column; gap:6px; background:#0c0c0e;">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(251,191,36,0.2); border-radius:4px; padding:6px; display:flex; flex-direction:column; gap:3px;">
                                    <div style="font-size:7px; font-weight:bold; color:#fbbf24;">🏛️ Independent Vault</div>
                                    <div style="font-size:6px; color:#a1a1aa;">Physical isolation for absolute data safety.</div>
                                </div>
                                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(251,191,36,0.2); border-radius:4px; padding:6px; display:flex; flex-direction:column; gap:3px;">
                                    <div style="font-size:7px; font-weight:bold; color:#fbbf24;">🌐 Global Matrix</div>
                                    <div style="font-size:6px; color:#a1a1aa;">Automated syndication across all platforms.</div>
                                </div>
                            </div>
                            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:4px; padding:6px; font-size:6.5px; color:#d4d4d8;">
                                "Sovereign provides absolute control over your written legacy."
                            </div>
                        </div>
                        <div style="padding:8px; background:#050506; border-top:1px solid #18181b; text-align:center; font-size:6.5px; color:#71717a; flex-shrink:0;">
                            Sovereign Sovereignty Protocol © 2026
                        </div>
                    </div>`;
            case 'vitepress':
                return `
                    <div class="vertical-page-mockup" style="background: #161618; width:100%; display:flex; flex-direction:column; color: #fffff5; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#1e1e20; border-bottom:1px solid #2e2e32; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#10b981;"><span>⚡</span> VitePress</div>
                            <div style="background:#28282a; border-radius:3px; padding:1px 6px; font-size:7px; color:#a1a1aa;">Ctrl+K</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #064e3b, #161618); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px;">
                            <div style="font-size:13px; font-weight:bold; color:#34d399;">Vite & Vue Powered</div>
                            <div style="font-size:7px; color:#9ca3af; max-width:85%; line-height:1.2;">Simple, powerful, and fast static site generator.</div>
                            <div style="display:flex; gap:4px; margin-top:2px;">
                                <div style="background:#10b981; color:#000; font-weight:bold; padding:2px 8px; border-radius:4px; font-size:7px;">Get Started</div>
                            </div>
                        </div>
                        <div style="padding:10px; display:flex; flex-direction:column; gap:6px; background:#1b1b1f;">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:#202124; border:1px solid #2e2e32; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#34d399;">⚡ Instant HMR</div>
                                    <div style="font-size:6px; color:#9ca3af; margin-top:2px;">Instant feedback on changes.</div>
                                </div>
                                <div style="background:#202124; border:1px solid #2e2e32; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#34d399;">📝 Markdown Extensions</div>
                                    <div style="font-size:6px; color:#9ca3af; margin-top:2px;">Built-in frontmatter & Vue syntax.</div>
                                </div>
                            </div>
                            <div style="background:#202124; border:1px solid #2e2e32; border-radius:4px; padding:6px; font-family:monospace; font-size:6.5px; color:#34d399;">
                                npm add -D vitepress vue
                            </div>
                        </div>
                        <div style="padding:8px; background:#111113; border-top:1px solid #222; text-align:center; font-size:6.5px; color:#666; flex-shrink:0;">
                            Released under the MIT License.
                        </div>
                    </div>`;
            case 'hugo':
                return `
                    <div class="vertical-page-mockup" style="background: #0d1117; width:100%; display:flex; flex-direction:column; color: #c9d1d9; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#161b22; border-bottom:1px solid #30363d; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#ff4088;"><span>🐹</span> Hugo</div>
                            <div style="background:#21262d; border-radius:3px; padding:1px 6px; font-size:7px; color:#8b949e;">v0.125</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #4c0519, #0d1117); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px; border-bottom:1px solid #21262d;">
                            <div style="font-size:12px; font-weight:900; color:#fda4af; letter-spacing:0.5px;">The World's Fastest Framework</div>
                            <div style="font-size:7px; color:#ff75a0; max-width:85%; line-height:1.2;">Sub-second builds & blazing speed for modern sites.</div>
                            <div style="background:#ff4088; color:#fff; font-size:7px; font-weight:bold; padding:3px 10px; border-radius:12px; margin-top:2px;">Read Documentation</div>
                        </div>
                        <div style="padding:10px; display:flex; flex-direction:column; gap:6px; background:#161b22;">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:#0d1117; border:1px solid #30363d; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#ff75a0;">⚡ Sub-millisecond</div>
                                    <div style="font-size:6px; color:#8b949e; margin-top:2px;">Built in Go for extreme speed.</div>
                                </div>
                                <div style="background:#0d1117; border:1px solid #30363d; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#ff75a0;">🧩 Rich Modules</div>
                                    <div style="font-size:6px; color:#8b949e; margin-top:2px;">Native content management.</div>
                                </div>
                            </div>
                            <div style="background:#010409; border:1px solid #30363d; border-radius:4px; padding:6px; font-family:monospace; font-size:6.5px; color:#ff75a0;">
                                hugo server -D --minify
                            </div>
                        </div>
                        <div style="padding:8px; background:#010409; border-top:1px solid #21262d; text-align:center; font-size:6.5px; color:#484f58; flex-shrink:0;">
                            Hugo Engine • High Performance Static Site Builder
                        </div>
                    </div>`;
            default:
                return `
                    <div class="vertical-page-mockup" style="background: #1e1e24; width:100%; display:flex; flex-direction:column; color: #d1d5db; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#2b2b36; border-bottom:1px solid #3d3d4e; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#38bdf8;"><span>🌐</span> Web Site</div>
                            <div style="font-size:7px; color:#9ca3af;">v1.0</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #0369a1, #1e1e24); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px;">
                            <div style="font-size:12px; font-weight:bold; color:#7dd3fc;">Digital Publication</div>
                            <div style="font-size:7px; color:#9ca3af; max-width:85%; line-height:1.2;">Standard responsive web layout template.</div>
                        </div>
                        <div style="padding:10px; display:flex; flex-direction:column; gap:6px; background:#18181c;">
                            <div style="background:#27272a; border-radius:4px; padding:6px; font-size:7px; color:#e5e7eb;">
                                Standard publication theme preview.
                            </div>
                        </div>
                        <div style="padding:8px; background:#111113; text-align:center; font-size:6.5px; color:#6b7280; flex-shrink:0;">
                            Illacme Sovereign Publishing Engine
                        </div>
                    </div>`;
        }
    };
})();
