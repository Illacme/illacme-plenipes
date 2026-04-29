import React from 'react';
import { Zap, Fingerprint, ShieldCheck, Target } from 'lucide-react';

const ValueProposition = () => {
  return (
    <section style={{ marginTop: '40px' }}>
      <div className="section-title">
        <Zap size={16} /> 治理核心价值 (Core Value Proposition)
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <h4 style={{ color: 'var(--accent-primary)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Fingerprint size={16} /> 格式零损
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)', lineHeight: '1.5' }}>
            自动识别并拦截 AI 对代码块、内链及公式的篡改。确保翻译后的文档依然可以直接部署，无需人工二次排版。
          </p>
        </div>
        <div className="glass-card" style={{ padding: '20px' }}>
          <h4 style={{ color: 'var(--accent-success)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={16} /> 品牌主权
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)', lineHeight: '1.5' }}>
            保护核心品牌标签和业务逻辑占位符。无论 AI 如何发挥，你的商业核心定义在所有语种中都将保持 100% 一致。
          </p>
        </div>
        <div className="glass-card" style={{ padding: '20px' }}>
          <h4 style={{ color: 'var(--accent-warning)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={16} /> 进化式引擎
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)', lineHeight: '1.5' }}>
            每一次自动修复都将沉淀为系统知识。引擎会根据你的文档库特征持续进化，实现“一次纠错，全库免疫”。
          </p>
        </div>
      </div>
    </section>
  );
};

export default ValueProposition;
