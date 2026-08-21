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
                    <div class="vertical-page-mockup" style="background: radial-gradient(circle at 50% 0%, #0d1b2a, #050811); width:100%; display:flex; flex-direction:column; color: #e2f1ff; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:rgba(10, 20, 38, 0.85); backdrop-filter:blur(8px); border-bottom:1px solid rgba(0, 245, 255, 0.2); display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#00f5ff;"><span>👑</span> Sovereign</div>
                            <div style="background:rgba(0,245,255,0.1); border:1px solid rgba(0,245,255,0.3); border-radius:3px; padding:1px 6px; font-size:7px; color:#00f5ff;">🔍 Search Docs</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, rgba(0,245,255,0.15), transparent 70%); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px; border-bottom:1px solid rgba(0, 245, 255, 0.1);">
                            <div style="font-size:12px; font-weight:900; color:#ffffff; letter-spacing:0.5px; text-shadow:0 0 10px rgba(0,245,255,0.5);">Sovereign Studio</div>
                            <div style="font-size:7px; color:#a0d2eb; max-width:85%; line-height:1.2;">High-end digital publication engine with glassmorphic aesthetic.</div>
                            <div style="background:linear-gradient(135deg, #00f5ff, #0077b6); color:#050811; font-size:7px; font-weight:900; padding:3px 10px; border-radius:12px; margin-top:2px;">Get Started</div>
                        </div>
                        <div style="padding:10px 12px; display:flex; flex-direction:column; gap:6px; background:rgba(5, 10, 20, 0.6);">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:rgba(15, 30, 55, 0.6); border:1px solid rgba(0,245,255,0.2); border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#00f5ff;">🛡️ Zero Token Waste</div>
                                    <div style="font-size:6px; color:#7ebcd6; margin-top:2px;">BlockShadowCache incremental sync.</div>
                                </div>
                                <div style="background:rgba(15, 30, 55, 0.6); border:1px solid rgba(0,245,255,0.2); border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#00f5ff;">👑 Glassmorphism</div>
                                    <div style="font-size:6px; color:#7ebcd6; margin-top:2px;">High-end cyber aesthetics.</div>
                                </div>
                            </div>
                        </div>
                        <div style="padding:8px; background:#03060c; border-top:1px solid rgba(0,245,255,0.15); text-align:center; font-size:6.5px; color:#52796f; flex-shrink:0;">
                            Illacme Sovereign Publishing Engine • Native Edition
                        </div>
                    </div>`;
            case 'nextra':
                return `
                    <div class="vertical-page-mockup" style="background: #000000; width:100%; display:flex; flex-direction:column; color: #ededed; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#111111; border-bottom:1px solid #262626; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#ededed;"><span>📖</span> Nextra</div>
                            <div style="background:#222; border-radius:3px; padding:1px 6px; font-size:7px; color:#888;">Next.js & MDX</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #1f2937, #000000); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px; border-bottom:1px solid #262626;">
                            <div style="font-size:12px; font-weight:900; color:#ffffff;">The Next.js Static Site Generator</div>
                            <div style="font-size:7px; color:#9ca3af; max-width:85%; line-height:1.2;">Simple, powerful and flexible site generation with Next.js and MDX.</div>
                            <div style="background:#ffffff; color:#000000; font-size:7px; font-weight:bold; padding:3px 10px; border-radius:12px; margin-top:2px;">Get Started</div>
                        </div>
                        <div style="padding:10px; display:flex; flex-direction:column; gap:6px; background:#0a0a0a;">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:#171717; border:1px solid #262626; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#fff;">⚡ Next.js App Router</div>
                                    <div style="font-size:6px; color:#888; margin-top:2px;">Full Next.js ecosystem support.</div>
                                </div>
                                <div style="background:#171717; border:1px solid #262626; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#fff;">✨ MDX Remote</div>
                                    <div style="font-size:6px; color:#888; margin-top:2px;">Dynamic JSX rendering.</div>
                                </div>
                            </div>
                            <div style="background:#171717; border:1px solid #262626; border-radius:4px; padding:6px; font-family:monospace; font-size:6.5px; color:#38bdf8;">
                                npx create-next-app -e nextra
                            </div>
                        </div>
                        <div style="padding:8px; background:#050505; border-top:1px solid #1f1f1f; text-align:center; font-size:6.5px; color:#555; flex-shrink:0;">
                            Powered by Nextra & Vercel
                        </div>
                    </div>`;
            case 'hexo':
                return `
                    <div class="vertical-page-mockup" style="background: #0b1016; width:100%; display:flex; flex-direction:column; color: #c9d1d9; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#131c26; border-bottom:1px solid #223344; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#0e83cd;"><span>🎨</span> Hexo</div>
                            <div style="background:#1c2b3a; border-radius:3px; padding:1px 6px; font-size:7px; color:#70a5d6;">Node.js</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #0e4e7a, #0b1016); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px; border-bottom:1px solid #223344;">
                            <div style="font-size:12px; font-weight:900; color:#e0f2fe; letter-spacing:0.5px;">A fast, simple & powerful blog framework</div>
                            <div style="font-size:7px; color:#7dd3fc; max-width:85%; line-height:1.2;">Node.js powered super fast rendering engine.</div>
                            <div style="background:#0e83cd; color:#fff; font-size:7px; font-weight:bold; padding:3px 10px; border-radius:12px; margin-top:2px;">Documentation</div>
                        </div>
                        <div style="padding:10px; display:flex; flex-direction:column; gap:6px; background:#0d141d;">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:#131c26; border:1px solid #223344; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#38bdf8;">⚡ Blazing Fast</div>
                                    <div style="font-size:6px; color:#70a5d6; margin-top:2px;">Generates hundreds of files in seconds.</div>
                                </div>
                                <div style="background:#131c26; border:1px solid #223344; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#38bdf8;">🔌 Tag Plugins</div>
                                    <div style="font-size:6px; color:#70a5d6; margin-top:2px;">Rich ecosystem of plugins & themes.</div>
                                </div>
                            </div>
                            <div style="background:#090d13; border:1px solid #223344; border-radius:4px; padding:6px; font-family:monospace; font-size:6.5px; color:#38bdf8;">
                                npx hexo init blog && cd blog
                            </div>
                        </div>
                        <div style="padding:8px; background:#070a0f; border-top:1px solid #1a2838; text-align:center; font-size:6.5px; color:#476585; flex-shrink:0;">
                            Hexo Engine • Fast & Powerful
                        </div>
                    </div>`;
            case 'universal':
                return `
                    <div class="vertical-page-mockup" style="background: #111827; width:100%; display:flex; flex-direction:column; color: #f3f4f6; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#1f2937; border-bottom:1px solid #374151; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#60a5fa;"><span>🌐</span> Universal</div>
                            <div style="background:#374151; border-radius:3px; padding:1px 6px; font-size:7px; color:#9ca3af;">Multi-SSG</div>
                        </div>
                        <div style="padding:16px 12px; background:radial-gradient(ellipse at top, #1e3a8a, #111827); display:flex; flex-direction:column; align-items:center; text-align:center; gap:6px; border-bottom:1px solid #374151;">
                            <div style="font-size:12px; font-weight:bold; color:#93c5fd;">Universal Publication</div>
                            <div style="font-size:7px; color:#bfdbfe; max-width:85%; line-height:1.2;">Cross-compatible responsive publication theme.</div>
                            <div style="background:#2563eb; color:#fff; font-size:7px; font-weight:bold; padding:3px 10px; border-radius:12px; margin-top:2px;">Learn More</div>
                        </div>
                        <div style="padding:10px; display:flex; flex-direction:column; gap:6px; background:#0f172a;">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div style="background:#1e293b; border:1px solid #334155; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#60a5fa;">🌐 Multi-Framework</div>
                                    <div style="font-size:6px; color:#94a3b8; margin-top:2px;">Adaptive rendering across SSG targets.</div>
                                </div>
                                <div style="background:#1e293b; border:1px solid #334155; border-radius:4px; padding:6px;">
                                    <div style="font-size:7px; font-weight:bold; color:#60a5fa;">📱 Responsive</div>
                                    <div style="font-size:6px; color:#94a3b8; margin-top:2px;">Clean reading experience on any device.</div>
                                </div>
                            </div>
                        </div>
                        <div style="padding:8px; background:#090d16; text-align:center; font-size:6.5px; color:#64748b; flex-shrink:0;">
                            Illacme Universal Publishing Framework
                        </div>
                    </div>`;
            default:
                return `
                    <div class="vertical-page-mockup" style="background: #1e1e24; width:100%; display:flex; flex-direction:column; color: #d1d5db; font-family:-apple-system,BlinkMacSystemFont,sans-serif; transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);">
                        <div style="height:20px; background:#2b2b36; border-bottom:1px solid #3d3d4e; display:flex; align-items:center; justify-content:space-between; padding:0 8px; font-size:9px; flex-shrink:0;">
                            <div style="display:flex; align-items:center; gap:5px; font-weight:bold; color:#38bdf8;"><span>🎨</span> Theme</div>
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
