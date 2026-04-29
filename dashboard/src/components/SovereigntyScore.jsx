import React from 'react';
import { Activity, Cpu, Zap } from 'lucide-react';

const SovereigntyScore = ({ score }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      <div className="glass-card score-widget">
        <div className="section-title" style={{ width: '100%', justifyContent: 'center' }}>
          主权健康度 (Sovereignty)
        </div>
        <div className="score-circle">
          <div className="score-ring"></div>
          <div className="score-number">{score}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: '600' }}>SCORE</div>
        </div>
        <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>
          系统已完全掌握自愈逻辑，主权偏移风险极低。
        </p>
      </div>

      <div className="glass-card">
        <div className="section-title">
          <Activity size={16} /> 算力节点负载
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Cpu size={14} /> DeepSeek Chat</span>
            <span style={{ color: 'var(--accent-success)' }}>98% Response Rate</span>
          </div>
          <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px' }}>
            <div style={{ width: '92%', height: '100%', background: 'var(--accent-primary)', borderRadius: '2px', boxShadow: '0 0 10px var(--accent-primary)' }}></div>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginTop: '10px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Cpu size={14} /> Local Ollama (Secondary)</span>
            <span style={{ color: 'var(--accent-warning)' }}>IDLE</span>
          </div>
          <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px' }}>
            <div style={{ width: '15%', height: '100%', background: 'var(--accent-warning)', borderRadius: '2px' }}></div>
          </div>
        </div>
      </div>

      <div className="glass-card" style={{ background: 'linear-gradient(135deg, rgba(0, 242, 255, 0.1) 0%, transparent 100%)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Zap size={20} style={{ color: 'var(--accent-primary)' }} />
          <div>
            <div style={{ fontWeight: '700', fontSize: '0.95rem' }}>自愈引擎已激活</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>实时拦截所有主权违规行为</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SovereigntyScore;
