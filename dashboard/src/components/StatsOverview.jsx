import React from 'react';

const StatsOverview = ({ stats }) => {
  return (
    <div className="stats-container">
      <div className="glass-card stat-item">
        <div className="stat-label">总处理资产</div>
        <div className="stat-value">{stats.total}</div>
        <div style={{ fontSize: '0.8rem', color: 'var(--accent-primary)' }}>+12% vs last cycle</div>
      </div>
      <div className="glass-card stat-item">
        <div className="stat-label">已对齐语种</div>
        <div className="stat-value">{stats.synced}</div>
        <div style={{ fontSize: '0.8rem', color: 'var(--accent-success)' }}>Synced & Audited</div>
      </div>
      <div className="glass-card stat-item">
        <div className="stat-label">自动自愈</div>
        <div className="stat-value" style={{ color: 'var(--accent-success)' }}>{stats.healed}</div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>AI Remedied</div>
      </div>
      <div className="glass-card stat-item">
        <div className="stat-label">隔离异常</div>
        <div className="stat-value" style={{ color: 'var(--accent-error)' }}>{stats.failed}</div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Sandbox Gated</div>
      </div>
    </div>
  );
};

export default StatsOverview;
