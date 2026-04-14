---
title: Index
description: Next-generation knowledge base and business website with Obsidian integration, AI-powered SEO, and multi-language support.
keywords: knowledge base, business website, Obsidian integration, AI-powered SEO, multi-language support
author: Eason
template: splash
tableOfContents: false
hide_title: true
---

<!-- =========================================================
     1. Next-Gen Hero Section
     ========================================================= -->
<div class="award-hero">
<div class="hero-bg-grid"></div>
<div class="hero-glow-core"></div>
<div class="hero-content fade-in-up" style="--stagger: 1;">
<div class="hero-badge">
<span class="badge-pulse"></span>
Illacme Plenipes v14.0 Release
</div>
</div>
<div class="hero-content fade-in-up" style="--stagger: 2;">
<div class="hero-title">
Future-Facing<br/>
<span class="text-gradient">Knowledge Base & Business Website</span>
</div>
</div>
<div class="hero-content fade-in-up" style="--stagger: 3;">
<div class="hero-subtitle">
Break down data silos and defend creative sovereignty.<br/>
Natively integrated with Obsidian’s dual-link ecosystem, AI-powered automatic multi-language support and SEO engine.
</div>
</div>
<div class="hero-content fade-in-up" style="--stagger: 4;">
<div class="award-hero-actions">
<a href="/guide/" class="btn-neo primary">
Build Now
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
</a>
<a href="/about/" class="btn-neo secondary">Explore the Core Engine</a>
</div>
</div>
</div>
<!-- =========================================================
     2. Asymmetric Dark-Glass Bento Grid
     ========================================================= -->
<div class="section-header fade-in-up" style="--stagger: 5;">
<div class="section-title">Reimagining Industrial Standards for Static Sites</div>
<div class="section-desc">From decoupling at the base to rendering at the top, experience unparalleled creative flow.</div>
</div>
<div class="award-bento fade-in-up" style="--stagger: 6;">
<!-- [Huge Card] Spanning 8 columns and 2 rows -->
<div class="bento-card bento-span-8 bento-row-2 card-hero">
<div class="bento-glow"></div>
<div class="bento-content bottom-aligned">
<div class="bento-icon">⚡️</div>
<div class="bento-title jumbo">Millisecond-Level Incremental Compilation & Tear-Free Architecture</div>
<div class="bento-desc">Powered by an underlying MD5 fingerprint state machine, it mercilessly outperforms full rebuilds. Completely discards full recompilation, with built-in OS-level singleton defense and double-checked locking (DCL), ensuring resilience against crashes—updates to a ten-thousand-document library complete in the blink of an eye.</div>
</div>
</div>
<!-- [Side Card 1] Spanning 4 columns -->
<div class="bento-card bento-span-4">
<div class="bento-glow"></div>
<div class="bento-content">
<div class="bento-icon">🌍</div>
<div class="bento-title">Fully Native Multi-Language Support</div>
<div class="bento-desc">Write once, translate concurrently with large models. Automatically splits long texts to prevent truncation and instantly generates a full-site multi-language routing stack.</div>
</div>
</div>
<!-- [Side Card 2] Spanning 4 columns -->
<div class="bento-card bento-span-4">
<div class="bento-glow"></div>
<div class="bento-content">
<div class="bento-icon">🔍</div>
<div class="bento-title">Automatic SEO Engine</div>
<div class="bento-desc">AI deep reading extracts summaries, enforces standardized Chinese titles into pure English URLs (Slugs), and activates the traffic engine.</div>
</div>
</div>
<!-- [Bottom Trio] Each spanning 4 columns -->
<div class="bento-card bento-span-4">
<div class="bento-glow"></div>
<div class="bento-content">
<div class="bento-icon">💎</div>
<div class="bento-title">Obsidian Bridge</div>
<div class="bento-desc">Automatically recursively expands nested dual-links, safely mapping proprietary Callouts syntax to standard frontend components.</div>
</div>
</div>
<div class="bento-card bento-span-4">
<div class="bento-glow"></div>
<div class="bento-content">
<div class="bento-icon">📦</div>
<div class="bento-title">Image Asset Pipeline</div>
<div class="bento-desc">Fully automatic WebP deep compression and collision-resistant hash sharding, supports full lifecycle GC garbage collection to eliminate orphaned files.</div>
</div>
</div>
<div class="bento-card bento-span-4">
<div class="bento-glow"></div>
<div class="bento-content">
<div class="bento-icon">🛡️</div>
<div class="bento-title">Compute Lock & Debouncing</div>
<div class="bento-desc">Supports disabling <code>ai_sync: false</code> per article. Defends against IDE save storms and cuts off large model communication, ensuring zero token loss.</div>
</div>
</div>
</div>
<!-- =========================================================
     3. Page Style Control Area
     ========================================================= -->
<style is:global>
/* ---------------------------------------------------------
   A. Framework Baseline Override & Customization (Native Header Override)
   --------------------------------------------------------- */
/* Hide native search box and main title */
h1#_top, site-search { display: none !important; }
/* Release Starlight's native navbar with acrylic glass effect injection */
.header {
  background-color: color-mix(in srgb, var(--sl-color-bg) 70%, transparent) !important;
  backdrop-filter: blur(24px) saturate(150%) !important;
  -webkit-backdrop-filter: blur(24px) saturate(150%) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}
[data-theme="light"] .header { 
  border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important; 
}
/* Remove default top padding from main container to let content directly penetrate under the glass navbar */
.main-frame { padding-top: 0 !important; }
/* Staggered entrance animation */
@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(30px); filter: blur(4px); }
  100% { opacity: 1; transform: translateY(0); filter: blur(0); }
}
.fade-in-up {
  opacity: 0;
  animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  animation-delay: calc(var(--stagger, 0) * 0.1s);
}
/* ---------------------------------------------------------
   B. Hero Section
   --------------------------------------------------------- */
.award-hero {
  position: relative; text-align: center; 
  padding: 12rem 0 6rem; /* Reserve sufficient top padding to avoid navbar overlap */
  display: flex; flex-direction: column; align-items: center; overflow: hidden;
}
.hero-bg-grid {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-size: 40px 40px;
  background-image: linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%); mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
  z-index: -2;
}
[data-theme="light"] .hero-bg-grid { background-image: linear-gradient(to right, rgba(0, 0, 0, 0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 0, 0, 0.04) 1px, transparent 1px); }
.hero-glow-core {
  position: absolute; top: -10%; left: 50%; transform: translateX(-50%);
  width: 800px; height: 400px; background: radial-gradient(ellipse at 50% 0%, var(--sl-color-accent) 0%, transparent 70%);
  opacity: 0.15; z-index: -1; pointer-events: none; filter: blur(80px);
}
/* 🚀 Completely strip hardcoded colors, fully trust Starlight's variable-based natural inversion */
.hero-badge {
  display: inline-flex; align-items: center; gap: 0.6rem;
  padding: 0.4rem 1.2rem; border-radius: 999px;
  background: rgba(255, 255, 255, 0.03); 
  border: 1px solid rgba(255, 255, 255, 0.1); 
  backdrop-filter: blur(10px);
  font-size: 0.85rem; font-weight: 500; 
  color: var(--sl-color-white); /* Dark theme = white, light theme automatically becomes black */
  margin-bottom: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.1);
}
[data-theme="light"] .hero-badge { 
  background: rgba(0, 0, 0, 0.03); 
  border: 1px solid rgba(0, 0, 0, 0.1); 
}
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(var(--sl-color-accent-rgb), 0.7); } 70% { box-shadow: 0 0 0 6px rgba(var(--sl-color-accent-rgb), 0); } 100% { box-shadow: 0 0 0 0 rgba(var(--sl-color-accent-rgb), 0); } }
.badge-pulse { width: 6px; height: 6px; background-color: var(--sl-color-accent); border-radius: 50%; animation: pulse 2s infinite; }
.hero-title { font-size: clamp(3rem, 7vw, 5rem); font-weight: 800; letter-spacing: -0.04em; line-height: 1.1; color: var(--sl-color-white); margin-bottom: 1.5rem; }
.text-gradient { background: linear-gradient(135deg, var(--sl-color-white) 0%, var(--sl-color-gray-4) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-subtitle { font-size: clamp(1.1rem, 2vw, 1.25rem); line-height: 1.6; color: var(--sl-color-gray-3); max-width: 46rem; margin: 0 auto 3.5rem; }
.award-hero-actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.btn-neo {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.8rem 1.8rem; border-radius: 999px; font-size: 1rem; font-weight: 600; text-decoration: none; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
/* Primary button: background automatically adapts to inverted color (white/black), text adapts to base color (black/white) */
.btn-neo.primary { 
  background: var(--sl-color-white); 
  color: var(--sl-color-bg) !important; 
  box-shadow: 0 0 0 1px rgba(255,255,255,0.1), 0 8px 24px rgba(255,255,255,0.15); 
}
[data-theme="light"] .btn-neo.primary { box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
.btn-neo.primary:hover { transform: translateY(-2px); box-shadow: 0 0 0 1px rgba(255,255,255,0.1), 0 12px 32px rgba(255,255,255,0.25); }
/* Secondary button: color fully relies on var(--sl-color-white) for automatic inversion */
.btn-neo.secondary { 
  background: rgba(255, 255, 255, 0.03); 
  border: 1px solid rgba(255, 255, 255, 0.1); 
  color: var(--sl-color-white) !important; 
  backdrop-filter: blur(10px); 
}
[data-theme="light"] .btn-neo.secondary { 
  background: rgba(0, 0, 0, 0.03); 
  border: 1px solid rgba(0, 0, 0, 0.1); 
}
.btn-neo.secondary:hover { background: rgba(255, 255, 255, 0.08); }
[data-theme="light"] .btn-neo.secondary:hover { background: rgba(0, 0, 0, 0.08); }
/* ---------------------------------------------------------
   C. Section Header
   --------------------------------------------------------- */
.section-header { text-align: center; margin: 4rem 0 3rem; }
.section-title { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; color: var(--sl-color-white); margin-bottom: 0.8rem; }
.section-desc { font-size: 1.1rem; color: var(--sl-color-gray-3); }
/* ---------------------------------------------------------
   D. Asymmetric Dark-Glass Bento Grid
   --------------------------------------------------------- */
.award-bento {
  display: grid; grid-template-columns: repeat(12, 1fr); grid-auto-rows: minmax(180px, auto); gap: 1.25rem; margin-bottom: 8rem; max-width: 1200px; margin-left: auto; margin-right: auto;
}
.bento-card {
  position: relative; margin-top: 0 !important; border-radius: 24px;
  background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05), 0 4px 24px rgba(0,0,0,0.2);
  overflow: hidden; display: flex; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
[data-theme="light"] .bento-card { background: rgba(0, 0, 0, 0.02); border: 1px solid rgba(0, 0, 0, 0.06); box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 1), 0 4px 24px rgba(0,0,0,0.03); }
.bento-card:hover { border-color: rgba(255, 255, 255, 0.15); transform: translateY(-4px); box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 12px 32px rgba(0,0,0,0.3); }
[data-theme="light"] .bento-card:hover { border-color: rgba(0, 0, 0, 0.15); }
.bento-glow { position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle at 50% 50%, rgba(var(--sl-color-accent-rgb), 0.15) 0%, transparent 50%); opacity: 0; pointer-events: none; transition: opacity 0.5s; }
.bento-card:hover .bento-glow { opacity: 1; }
.bento-content { position: relative; z-index: 2; padding: 2.5rem; display: flex; flex-direction: column; height: 100%; width: 100%; }
.bento-content.bottom-aligned { justify-content: flex-end; }
.bento-span-12 { grid-column: span 12; } .bento-span-8 { grid-column: span 8; } .bento-span-4 { grid-column: span 4; } .bento-row-2 { grid-row: span 2; }
@media (max-width: 1024px) { .bento-span-8, .bento-span-4 { grid-column: span 12; } .bento-row-2 { grid-row: span 1; } }
.bento-highlight { background: rgba(var(--sl-color-accent-rgb), 0.03); border-color: rgba(var(--sl-color-accent-rgb), 0.15); }
.bento-icon { font-size: 2rem; margin-top: 0 !important; margin-bottom: 1.5rem; background: rgba(255,255,255,0.05); width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
[data-theme="light"] .bento-icon { background: rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.05); color: var(--sl-color-white); }
.bento-title { margin-top: 0 !important; margin-bottom: 0.8rem !important; font-size: 1.25rem; font-weight: 700; letter-spacing: -0.01em; color: var(--sl-color-white); }
.bento-title.jumbo { font-size: 2rem; letter-spacing: -0.02em; }
.bento-desc { margin-top: 0 !important; margin-bottom: 0 !important; font-size: 0.95rem; color: var(--sl-color-gray-3); line-height: 1.6; flex-grow: 1; }
.bento-desc code { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 0.1rem 0.4rem; border-radius: 6px; font-size: 0.85em; color: var(--sl-color-text-accent); }
[data-theme="light"] .bento-desc code { background: rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.08); }
</style>