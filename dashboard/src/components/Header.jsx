import React from 'react';
import { Layers } from 'lucide-react';

const Header = ({ healedCount }) => {
  return (
    <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div style={{ padding: '8px', background: 'var(--accent-primary)', borderRadius: '12px', color: '#000' }}>
            <Layers size={24} />
          </div>
          <h1 style={{ fontSize: '2rem' }}>Illacme Plenipes <span style={{ color: 'var(--accent-primary)', fontWeight: '300' }}>V11.5</span></h1>
        </div>
        <p style={{ color: 'var(--text-dim)', fontSize: '1.1rem' }}>翻译资产全息治理中心 | 已为您挽回 <strong>{healedCount}</strong> 次翻译事故</p>
      </div>
      <div className="glass-card" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '15px' }}>
        <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#00ffaa', boxShadow: '0 0 10px #00ffaa' }}></div>
        <span style={{ fontWeight: '600', fontSize: '0.9rem' }}>ENGINE LIVE</span>
        <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>{new Date().toLocaleTimeString()}</span>
      </div>
    </header>
  );
};

export default Header;
