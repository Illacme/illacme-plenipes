import React from 'react';

const TokenGuard = ({ usage }) => {
  const { session_cost = 0, session_saved = 0, total_cost = 0, total_saved = 0 } = usage || {};
  
  const roi = (session_saved / (session_cost + session_saved) * 100) || 0;
  
  return (
    <div className="glass-card token-guard-widget animate-fade">
      <div className="section-title">
        <span className="icon">⚡</span> Token Guard 算力治理中心
      </div>
      
      <div className="usage-grid">
        <div className="usage-main">
          <div className="usage-large-label">本次 Session 支出</div>
          <div className="usage-large-value" style={{ color: 'var(--accent-error)' }}>
            ¥ {session_cost.toFixed(4)}
          </div>
          <div className="usage-mini-label">预算熔断阈值: ¥ 1.00</div>
        </div>
        
        <div className="usage-metrics">
          <div className="usage-sub-item">
            <div className="usage-sub-label">BlockCache 节省</div>
            <div className="usage-sub-value" style={{ color: 'var(--accent-success)' }}>
              + ¥ {session_saved.toFixed(4)}
            </div>
          </div>
          <div className="usage-sub-item">
            <div className="usage-sub-label">算力利用率 (ROI)</div>
            <div className="usage-sub-value" style={{ color: 'var(--accent-primary)' }}>
              {roi.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      <div className="usage-historical">
        <div className="historical-label">全寿命周期总支出: <span className="white">¥ {total_cost.toFixed(2)}</span></div>
        <div className="historical-label">累计节省额度: <span className="green">¥ {total_saved.toFixed(2)}</span></div>
      </div>

      <style jsx>{`
        .token-guard-widget {
          margin-top: 30px;
          grid-column: span 2;
        }
        .usage-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 40px;
          margin: 20px 0;
          align-items: center;
        }
        .usage-large-label {
          font-size: 0.9rem;
          color: var(--text-dim);
          margin-bottom: 5px;
        }
        .usage-large-value {
          font-size: 3rem;
          font-weight: 700;
          font-family: var(--font-mono);
          letter-spacing: -0.05em;
        }
        .usage-mini-label {
          font-size: 0.75rem;
          color: var(--text-dim);
          margin-top: 5px;
        }
        .usage-metrics {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }
        .usage-sub-label {
          font-size: 0.8rem;
          color: var(--text-dim);
          margin-bottom: 4px;
        }
        .usage-sub-value {
          font-size: 1.5rem;
          font-weight: 600;
          font-family: var(--font-mono);
        }
        .usage-historical {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid var(--glass-border);
          display: flex;
          gap: 40px;
        }
        .historical-label {
          font-size: 0.85rem;
          color: var(--text-dim);
        }
        .white { color: #fff; }
        .green { color: var(--accent-success); }
      `}</style>
    </div>
  );
};

export default TokenGuard;
