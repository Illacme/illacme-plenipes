/**
 * ⚙️ [V1.0] Illacme Plenipes Plugins - Pod Status & Credential Judger Shard
 * 职责：插件可配置性研判 (isPluginConfigurable)、生命周期状态检测与多渠道凭据齐全度判定 (checkPluginConfiguredStatus)。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.isPluginConfigurable = function (p) {
        if (!p) return false;
        if (p.has_config === false || p.is_configurable === false) return false;
        if (p.is_manageable === false) return false;

        const configurableCategories = ['hosting', 'image_hosting', 'notification', 'publisher', 'theme', 'protocol', 'masker', 'ingress_source', 'tunnel'];
        if (configurableCategories.includes(p.category)) {
            return true;
        }
        return false;
    };

    window.checkPluginConfiguredStatus = function (p) {
        if (!p) return { label: '未激活', class: 'blocked', style: 'color: var(--text-dim); margin-right: 0 !important;' };
        const canConfig = window.isPluginConfigurable ? window.isPluginConfigurable(p) : false;
        if (!canConfig) {
            return { label: '⚡ 免配置', class: 'info', style: 'background: rgba(255, 255, 255, 0.05); color: var(--text-dim); border: 1px solid rgba(255, 255, 255, 0.15); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
        }

        if (!p.is_enabled) {
            return { label: '🚫 全局禁用', class: 'warning', style: 'background: rgba(255, 77, 77, 0.08); color: #ff4d4d; border: 1px solid rgba(255, 77, 77, 0.2); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
        }

        // 🎨 装帧主题状态呈现：统一严格 4 字符对齐（当前选用 / 本地就绪 / 云端母本）
        if (p.category === 'theme') {
            if (p.is_in_use) {
                return { label: '🟢 当前选用', class: 'info', style: 'background: rgba(var(--neon-green-rgb), 0.08); color: var(--neon-green); border: 1px solid rgba(var(--neon-green-rgb), 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; white-space: nowrap;' };
            }
            const loc = p.location || 'native';
            if (loc === 'local' || loc === 'global') {
                return { label: '📦 本地就绪', class: 'info', style: 'background: rgba(0, 242, 254, 0.08); color: var(--accent-secondary); border: 1px solid rgba(0, 242, 254, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; white-space: nowrap;' };
            }
            return { label: '☁️ 云端母本', class: 'warning', style: 'background: rgba(245, 158, 11, 0.08); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; white-space: nowrap;' };
        }

        const cfgData = window.settingsData || {};
        let settings = {};
        if (p.category === 'hosting') {
            settings = cfgData.publish_control?.direct_upload?.[p.id] || {};
        } else if (p.category === 'image_hosting') {
            settings = cfgData.image_hosting?.[p.id] || cfgData.publish_control?.direct_upload?.[p.id] || {};
        } else if (p.category === 'notification') {
            settings = cfgData.publish_control?.webhook_endpoints?.[p.id] || {};
        } else if (p.category === 'tunnel') {
            settings = cfgData.tunnel?.[p.id] || {};
        } else if (p.category === 'protocol' || p.category === 'compute') {
            const nodes = Object.values(cfgData.translation?.compute_nodes || {});
            const matched = nodes.find(n => n && (n.type === p.id || n.provider === p.id || n.id === p.id));
            settings = matched || {};
        } else {
            settings = cfgData.syndication?.[p.id] || {};
        }

        // 📭 [V80.2] 「从未配置」与「配置不完整」语义分离
        const SKIP_FIELDS = new Set(['enabled', 'proxy', 'force_push', 'git_user_name', 'git_user_email', 'branch', 'is_primary']);
        const _isPlaceholder = (v) => {
            if (!v || typeof v !== 'string') return true;
            const t = v.trim();
            if (!t) return true;
            return /^YOUR[_\-]/i.test(t) || /^REPLACE/i.test(t) || /^TOKEN_HERE$/i.test(t) ||
                   /^<.+>$/.test(t) || /^\{.+\}$/.test(t) || /^EXAMPLE[_\-]/i.test(t) || /^PLACEHOLDER/i.test(t);
        };
        const hasAnyUserInput = Object.entries(settings).some(([k, v]) => {
            if (SKIP_FIELDS.has(k)) return false;
            const s = String(v ?? '').trim();
            return s.length > 0 && !_isPlaceholder(s);
        });

        if (!hasAnyUserInput) {
            return { label: '─ 待配置', class: 'info', style: 'color: var(--text-dim); opacity: 0.55; font-weight: 500; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03);' };
        }

        if (window.isPluginCredentialReady) {
            const cred = window.isPluginCredentialReady(p.id, p.category, settings);
            if (cred.ready) {
                return { label: `🟢 ${cred.label || '配置齐全'}`, class: 'info', style: 'background: rgba(var(--neon-green-rgb), 0.08); color: var(--neon-green); border: 1px solid rgba(var(--neon-green-rgb), 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
            } else {
                return { label: `⚠️ ${cred.label || '待填凭据'}`, class: 'warning', style: 'background: rgba(245, 158, 11, 0.08); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
            }
        }

        // 兜底：有用户输入 → 判断是否完整（同样排除占位值）
        const hasKeys = Object.entries(settings).some(([k, v]) => {
            if (SKIP_FIELDS.has(k)) return false;
            const s = String(v ?? '').trim();
            return s.length > 0 && !_isPlaceholder(s);
        });

        if (hasKeys) {
            return { label: '🟢 配置齐全', class: 'info', style: 'background: rgba(var(--neon-green-rgb), 0.08); color: var(--neon-green); border: 1px solid rgba(var(--neon-green-rgb), 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
        } else {
            return { label: '⚠️ 待填凭据', class: 'warning', style: 'background: rgba(245, 158, 11, 0.08); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
        }
    };
})();
