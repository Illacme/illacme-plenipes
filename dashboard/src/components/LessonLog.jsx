import React from 'react';
import { Brain, Fingerprint, ShieldCheck, AlertTriangle, RotateCcw, CheckCircle2 } from 'lucide-react';

const USER_LABELS = {
  "MASK_INTEGRITY": "AI 幻觉拦截 & 格式自愈",
  "SOVEREIGNTY_SHIELD": "核心资产/品牌标签保护",
  "SEO_ALIGNMENT": "SEO 权重对齐与精度优化"
};

const getCategoryIcon = (cat) => {
  if (cat === 'MASK_INTEGRITY') return <Fingerprint size={18} />;
  if (cat === 'SOVEREIGNTY_SHIELD') return <ShieldCheck size={18} />;
  return <AlertTriangle size={18} />;
};

const getCategoryColor = (cat) => {
  if (cat === 'MASK_INTEGRITY') return '#00f2ff';
  if (cat === 'SOVEREIGNTY_SHIELD') return '#00ffaa';
  return '#ff4466';
};

const LessonLog = ({ lessons }) => {
  return (
    <div className="glass-card">
      <div className="section-title">
        <Brain size={16} /> 智慧教训时间轴 (Memory Stream)
      </div>
      <div className="timeline">
        {lessons.length > 0 ? lessons.map((lesson, i) => (
          <div key={i} className="lesson-item">
            <div className="lesson-icon" style={{ background: `${getCategoryColor(lesson.category)}22`, color: getCategoryColor(lesson.category) }}>
              {getCategoryIcon(lesson.category)}
            </div>
            <div className="lesson-content">
              <div className="lesson-header">
                <span className="lesson-cat" style={{ color: getCategoryColor(lesson.category) }}>
                  {USER_LABELS[lesson.category] || lesson.category}
                </span>
                <span className="lesson-time">{lesson.timestamp?.split('T')[1]?.split('.')[0] || 'N/A'}</span>
              </div>
              <div className="lesson-error">{lesson.error}</div>
              <div className="lesson-meta">
                <span className="badge">分发轮次: {lesson.iter_id}</span>
                <span className="badge">目标语种: {lesson.context?.lang}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-success)' }}>
                  <RotateCcw size={12} /> 系统已自动修复
                </div>
              </div>
            </div>
          </div>
        )) : (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
            <CheckCircle2 size={48} style={{ marginBottom: '15px', opacity: 0.2 }} />
            <p>大脑清空：目前没有任何治理故障</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonLog;
