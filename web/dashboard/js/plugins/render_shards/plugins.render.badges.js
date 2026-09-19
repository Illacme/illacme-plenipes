/**
 * ⚙️ [V1.0] Illacme Plenipes Plugins - Brand Badges & Icons Registry Shard
 * 职责：各平台品牌徽章、专属图标与分类回退样式字典 (getPlatformBrandBadge)。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.getPlatformBrandBadge = (id, category = '') => {
        const rawId = (id || '').toLowerCase();
        const cleanId = rawId.replace(/_/g, '');

        const BRAND_DICT = {
            // 📢 社交媒体与分发平台 (Publishers & Syndication)
            'xiaohongshu': { icon: '📕', color: '#ff2442', bg: 'rgba(255, 36, 66, 0.14)', border: 'rgba(255, 36, 66, 0.35)' },
            'red': { icon: '📕', color: '#ff2442', bg: 'rgba(255, 36, 66, 0.14)', border: 'rgba(255, 36, 66, 0.35)' },
            'toutiao': { icon: '⚡', color: '#ed4040', bg: 'rgba(237, 64, 64, 0.14)', border: 'rgba(237, 64, 64, 0.35)' },
            'csdn': { icon: '📑', color: '#fc5531', bg: 'rgba(252, 85, 49, 0.14)', border: 'rgba(252, 85, 49, 0.35)' },
            'cnblogs': { icon: '🌿', color: '#2b73af', bg: 'rgba(43, 115, 175, 0.14)', border: 'rgba(43, 115, 175, 0.35)' },
            'bilibili': { icon: '📺', color: '#00aeec', bg: 'rgba(0, 174, 236, 0.14)', border: 'rgba(0, 174, 236, 0.35)' },
            'segmentfault': { icon: '💡', color: '#009a61', bg: 'rgba(0, 154, 97, 0.14)', border: 'rgba(0, 154, 97, 0.35)' },
            'oschina': { icon: '🇨🇳', color: '#21b351', bg: 'rgba(33, 179, 81, 0.14)', border: 'rgba(33, 179, 81, 0.35)' },
            'devto': { icon: '👩‍💻', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
            'dev_to': { icon: '👩‍💻', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
            'hashnode': { icon: '🔷', color: '#2962ff', bg: 'rgba(41, 98, 255, 0.14)', border: 'rgba(41, 98, 255, 0.35)' },
            'medium': { icon: '📝', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.14)', border: 'rgba(255, 255, 255, 0.3)' },
            'ghost': { icon: '👻', color: '#738a94', bg: 'rgba(115, 138, 148, 0.14)', border: 'rgba(115, 138, 148, 0.35)' },
            'wordpress': { icon: '📰', color: '#21759b', bg: 'rgba(33, 117, 155, 0.14)', border: 'rgba(33, 117, 155, 0.35)' },
            'wechat': { icon: '💬', color: '#07c160', bg: 'rgba(7, 193, 96, 0.14)', border: 'rgba(7, 193, 96, 0.35)' },
            'zhihu': { icon: '💡', color: '#0084ff', bg: 'rgba(0, 132, 255, 0.14)', border: 'rgba(0, 132, 255, 0.35)' },
            'juejin': { icon: '🧱', color: '#1e80ff', bg: 'rgba(30, 128, 255, 0.14)', border: 'rgba(30, 128, 255, 0.35)' },
            'substack': { icon: '📮', color: '#ff6719', bg: 'rgba(255, 103, 25, 0.14)', border: 'rgba(255, 103, 25, 0.35)' },
            'telegram': { icon: '✈️', color: '#24a1de', bg: 'rgba(36, 161, 222, 0.14)', border: 'rgba(36, 161, 222, 0.35)' },
            'discord': { icon: '💬', color: '#5865f2', bg: 'rgba(88, 101, 242, 0.14)', border: 'rgba(88, 101, 242, 0.35)' },
            'linkedin': { icon: '💼', color: '#0a66c2', bg: 'rgba(10, 102, 194, 0.14)', border: 'rgba(10, 102, 194, 0.35)' },

            // 🌐 全站托管 (Hosting Platforms)
            'cloudflare_pages': { icon: '🟧', color: '#f38020', bg: 'rgba(243, 128, 32, 0.14)', border: 'rgba(243, 128, 32, 0.35)' },
            'cloudflare': { icon: '🟧', color: '#f38020', bg: 'rgba(243, 128, 32, 0.14)', border: 'rgba(243, 128, 32, 0.35)' },
            'github_pages': { icon: '🐙', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
            'github': { icon: '🐙', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
            'gitee_pages': { icon: '🔴', color: '#c71d23', bg: 'rgba(199, 29, 35, 0.14)', border: 'rgba(199, 29, 35, 0.35)' },
            'gitee': { icon: '🔴', color: '#c71d23', bg: 'rgba(199, 29, 35, 0.14)', border: 'rgba(199, 29, 35, 0.35)' },
            'gitlab_pages': { icon: '🦊', color: '#fc6d26', bg: 'rgba(252, 109, 38, 0.14)', border: 'rgba(252, 109, 38, 0.35)' },
            'coding_pages': { icon: '💎', color: '#3273dc', bg: 'rgba(50, 115, 220, 0.14)', border: 'rgba(50, 115, 220, 0.35)' },
            'netlify': { icon: '🌐', color: '#00c7b7', bg: 'rgba(0, 199, 183, 0.14)', border: 'rgba(0, 199, 183, 0.35)' },
            'vercel': { icon: '▲', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.14)', border: 'rgba(255, 255, 255, 0.35)' },
            'zeabur': { icon: '⛵', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.14)', border: 'rgba(99, 102, 241, 0.35)' },
            'render': { icon: '🟣', color: '#46e3b7', bg: 'rgba(70, 227, 183, 0.14)', border: 'rgba(70, 227, 183, 0.35)' },
            'railway': { icon: '🚂', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.14)', border: 'rgba(236, 72, 153, 0.35)' },
            'firebase': { icon: '🔥', color: '#ffca28', bg: 'rgba(255, 202, 40, 0.14)', border: 'rgba(255, 202, 40, 0.35)' },

            // 📷 图床与对象存储 (Image Hosting & Object Storage)
            's3': { icon: '🪣', color: '#ff9900', bg: 'rgba(255, 153, 0, 0.14)', border: 'rgba(255, 153, 0, 0.35)' },
            'imgur': { icon: '🟢', color: '#1bb76e', bg: 'rgba(27, 183, 110, 0.14)', border: 'rgba(27, 183, 110, 0.35)' },
            'aliyun_oss': { icon: '☁️', color: '#ff6a00', bg: 'rgba(255, 106, 0, 0.14)', border: 'rgba(255, 106, 0, 0.35)' },
            'tencent_cos': { icon: '🐧', color: '#00a4ff', bg: 'rgba(0, 164, 255, 0.14)', border: 'rgba(0, 164, 255, 0.35)' },
            'upyun_uss': { icon: '☁️', color: '#00b7ee', bg: 'rgba(0, 183, 238, 0.14)', border: 'rgba(0, 183, 238, 0.35)' },
            'upyun': { icon: '☁️', color: '#00b7ee', bg: 'rgba(0, 183, 238, 0.14)', border: 'rgba(0, 183, 238, 0.35)' },
            'qiniu': { icon: '🔵', color: '#0099ff', bg: 'rgba(0, 153, 255, 0.14)', border: 'rgba(0, 153, 255, 0.35)' },
            'qiniu_kodo': { icon: '🔵', color: '#0099ff', bg: 'rgba(0, 153, 255, 0.14)', border: 'rgba(0, 153, 255, 0.35)' },
            'lsky_pro': { icon: '🌌', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.14)', border: 'rgba(59, 130, 246, 0.35)' },
            'superbed': { icon: '🛏️', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.14)', border: 'rgba(236, 72, 153, 0.35)' },
            'telegraph': { icon: '⚡', color: '#ffaa00', bg: 'rgba(255, 170, 0, 0.14)', border: 'rgba(255, 170, 0, 0.35)' },
            'cloudflare_r2': { icon: '🟧', color: '#f38020', bg: 'rgba(243, 128, 32, 0.14)', border: 'rgba(243, 128, 32, 0.35)' },
            'imgbb': { icon: '🖼️', color: '#2a9d8f', bg: 'rgba(42, 157, 143, 0.14)', border: 'rgba(42, 157, 143, 0.35)' },
            'catbox': { icon: '🐱', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.14)', border: 'rgba(139, 92, 246, 0.35)' },
            'loli_io': { icon: '🌸', color: '#f472b6', bg: 'rgba(244, 114, 182, 0.14)', border: 'rgba(244, 114, 182, 0.35)' },
            'sftp': { icon: '🔒', color: '#10b981', bg: 'rgba(16, 185, 129, 0.14)', border: 'rgba(16, 185, 129, 0.35)' },

            // 🔔 消息通知 (Notifications)
            'feishu': { icon: '🕊️', color: '#00d6b9', bg: 'rgba(0, 214, 185, 0.14)', border: 'rgba(0, 214, 185, 0.35)' },
            'dingtalk': { icon: '🔔', color: '#0089ff', bg: 'rgba(0, 137, 255, 0.14)', border: 'rgba(0, 137, 255, 0.35)' },
            'wecom': { icon: '💬', color: '#2574eb', bg: 'rgba(37, 116, 235, 0.14)', border: 'rgba(37, 116, 235, 0.35)' },
            'email': { icon: '📧', color: '#ea4335', bg: 'rgba(234, 67, 53, 0.14)', border: 'rgba(234, 67, 53, 0.35)' },
            'sms': { icon: '📱', color: '#10b981', bg: 'rgba(16, 185, 129, 0.14)', border: 'rgba(16, 185, 129, 0.35)' },
            'app_push': { icon: '📲', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.14)', border: 'rgba(139, 92, 246, 0.35)' },
            'generic_webhook': { icon: '🪝', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.14)', border: 'rgba(0, 242, 254, 0.35)' },
            'webhook_dispatch': { icon: '🪝', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.14)', border: 'rgba(0, 242, 254, 0.35)' },

            // 🎨 装帧主题与引擎 (Themes & SSG Engines)
            'sovereign': { icon: '👑', color: '#ffd700', bg: 'rgba(255, 215, 0, 0.18)', border: 'rgba(255, 215, 0, 0.45)' },
            'universal': { icon: '🌌', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.18)', border: 'rgba(0, 242, 254, 0.45)' },
            'docusaurus': { icon: '🦖', color: '#3ecc5f', bg: 'rgba(62, 204, 95, 0.18)', border: 'rgba(62, 204, 95, 0.45)' },
            'starlight': { icon: '🌟', color: '#9d4edd', bg: 'rgba(157, 78, 221, 0.18)', border: 'rgba(157, 78, 221, 0.45)' },
            'vitepress': { icon: '⚡', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.18)', border: 'rgba(139, 92, 246, 0.45)' },
            'nextra': { icon: '📐', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.18)', border: 'rgba(0, 242, 254, 0.45)' },
            'hugo': { icon: '🦔', color: '#ff4088', bg: 'rgba(255, 64, 136, 0.18)', border: 'rgba(255, 64, 136, 0.45)' },
            'hexo': { icon: '⬡', color: '#0e83cd', bg: 'rgba(14, 131, 205, 0.18)', border: 'rgba(14, 131, 205, 0.45)' },
            'astro': { icon: '🚀', color: '#ff5d01', bg: 'rgba(255, 93, 1, 0.18)', border: 'rgba(255, 93, 1, 0.45)' },
            'nextjs': { icon: '▲', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.18)', border: 'rgba(255, 255, 255, 0.45)' },
            'vuepress': { icon: '💚', color: '#42b983', bg: 'rgba(66, 185, 131, 0.18)', border: 'rgba(66, 185, 131, 0.45)' },

            // 🧠 AI 协议与核心组件 (AI Protocols & Processing)
            'openai': { icon: '🤖', color: '#10a37f', bg: 'rgba(16, 163, 127, 0.14)', border: 'rgba(16, 163, 127, 0.35)' },
            'anthropic': { icon: '🧠', color: '#d97706', bg: 'rgba(217, 119, 6, 0.14)', border: 'rgba(217, 119, 6, 0.35)' },
            'claude': { icon: '🧠', color: '#d97706', bg: 'rgba(217, 119, 6, 0.14)', border: 'rgba(217, 119, 6, 0.35)' },
            'gemini': { icon: '♊', color: '#4285f4', bg: 'rgba(66, 133, 244, 0.14)', border: 'rgba(66, 133, 244, 0.35)' },
            'deepseek': { icon: '🐋', color: '#0066ff', bg: 'rgba(0, 102, 255, 0.14)', border: 'rgba(0, 102, 255, 0.35)' },
            'ollama': { icon: '🦙', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.14)', border: 'rgba(255, 255, 255, 0.35)' },
            'qwen': { icon: '🐲', color: '#ff6a00', bg: 'rgba(255, 106, 0, 0.14)', border: 'rgba(255, 106, 0, 0.35)' },
            'zhipu': { icon: '🌟', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.14)', border: 'rgba(59, 130, 246, 0.35)' },
            'exif_scrubber': { icon: '🛡️', color: '#00ff88', bg: 'rgba(0, 255, 136, 0.14)', border: 'rgba(0, 255, 136, 0.35)' },
            'sensitive_filter': { icon: '🚫', color: '#ff4d4d', bg: 'rgba(255, 77, 77, 0.14)', border: 'rgba(255, 77, 77, 0.35)' },
            'ast_processor': { icon: '🧬', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.14)', border: 'rgba(168, 85, 247, 0.35)' },
            'markdown_normalizer': { icon: '📝', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.14)', border: 'rgba(0, 242, 254, 0.35)' }
        };

        if (BRAND_DICT[rawId]) return BRAND_DICT[rawId];
        if (BRAND_DICT[cleanId]) return BRAND_DICT[cleanId];

        // 针对模糊命名的 fallback
        for (const k in BRAND_DICT) {
            if (rawId.includes(k)) return BRAND_DICT[k];
        }

        // 依据大类 fallback
        const CAT_FALLBACKS = {
            'publisher': { icon: '📢', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.12)', border: 'rgba(0, 242, 254, 0.3)' },
            'hosting': { icon: '🌐', color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.12)', border: 'rgba(56, 189, 248, 0.3)' },
            'image_hosting': { icon: '📷', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.12)', border: 'rgba(236, 72, 153, 0.3)' },
            'notification': { icon: '🔔', color: '#fbbf24', bg: 'rgba(251, 191, 36, 0.12)', border: 'rgba(251, 191, 36, 0.3)' },
            'theme': { icon: '🎨', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.12)', border: 'rgba(168, 85, 247, 0.3)' },
            'protocol': { icon: '🧠', color: '#10b981', bg: 'rgba(16, 185, 129, 0.12)', border: 'rgba(16, 185, 129, 0.3)' },
            'transformer': { icon: '🛠️', color: '#f97316', bg: 'rgba(249, 115, 22, 0.12)', border: 'rgba(249, 115, 22, 0.3)' },
            'masker': { icon: '🛡️', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.12)', border: 'rgba(6, 182, 212, 0.3)' },
            'ingress_source': { icon: '📥', color: '#84cc16', bg: 'rgba(132, 204, 22, 0.12)', border: 'rgba(132, 204, 22, 0.3)' },
            'ingress_dialect': { icon: '📖', color: '#84cc16', bg: 'rgba(132, 204, 22, 0.12)', border: 'rgba(132, 204, 22, 0.3)' },
            'editorial': { icon: '🧬', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.12)', border: 'rgba(99, 102, 241, 0.3)' }
        };

        return CAT_FALLBACKS[category] || { icon: '🧩', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.12)', border: 'rgba(0, 242, 254, 0.3)' };
    };

})();
