import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StatsOverview from './components/StatsOverview';
import LessonLog from './components/LessonLog';
import SovereigntyScore from './components/SovereigntyScore';
import ValueProposition from './components/ValueProposition';
import TokenGuard from './components/TokenGuard';
import HolographicGraph from './components/HolographicGraph';
import RealtimeMonitor from './components/RealtimeMonitor';

/**
 * 🛡️ [V11.5 Architecture] 主权控制塔 (Main Controller)
 * 职责：负责全局数据调度、生命周期管理与子组件状态同步。
 */
const App = () => {
  const [stats, setStats] = useState({
    total: 0,
    synced: 0,
    healed: 0,
    failed: 0,
    score: 100
  });

  const [view, setView] = useState('dashboard'); 
  const [lessons, setLessons] = useState([]);
  const [usage, setUsage] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. 抓取教训流
        try {
          const lessonRes = await fetch('/data/brain/lessons_learned.json');
          if (lessonRes.ok) {
            const lessonData = await lessonRes.json();
            setLessons([...lessonData].reverse());
          }
        } catch (e) { }

        // 2. 抓取物理审计统计
        try {
          const statsRes = await fetch('/data/sync_stats.json');
          if (statsRes.ok) {
            const statsData = await statsRes.json();
            if (statsData.usage) setUsage(statsData.usage);
          }
        } catch (e) { }

        // 3. 抓取健康矩阵
        try {
          const healthRes = await fetch('/data/sentinel_health.json');
          if (healthRes.ok) {
            const healthData = await healthRes.json();
            const matrix = healthData.matrix || {};
            
            const healed = Object.values(matrix).filter(v => v.includes('FIXED') || v === 'HEALED').length;
            const failed = Object.values(matrix).filter(v => v === 'PENDING').length;
            const synced = Object.keys(matrix).length;
            
            setStats(prev => ({
              ...prev,
              synced: synced,
              healed: healed,
              failed: failed,
              score: Math.min(Math.max(100 - (lessons.length * 5) + (healed * 2), 0), 100)
            }));
          }
        } catch (e) { }
        setLoading(false);
      } catch (err) { }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [lessons.length]);

  return (
    <div className="container animate-fade">
      <Header healedCount={stats.healed} />
      
      <div className="flex justify-center gap-4 mb-8">
        <button 
          onClick={() => setView('dashboard')} 
          className={`px-6 py-2 rounded-full transition-all text-sm font-bold tracking-widest uppercase border ${view === 'dashboard' ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-900/40' : 'bg-slate-900/50 border-slate-800 text-slate-500 hover:text-slate-300'}`}
        >
          主权仪表盘
        </button>
        <button 
          onClick={() => setView('graph')} 
          className={`px-6 py-2 rounded-full transition-all text-sm font-bold tracking-widest uppercase border ${view === 'graph' ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-900/40' : 'bg-slate-900/50 border-slate-800 text-slate-500 hover:text-slate-300'}`}
        >
          全息拓扑
        </button>
      </div>

      {view === 'dashboard' ? (
        <>
          <StatsOverview stats={stats} />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <RealtimeMonitor />
            </div>
            <div className="space-y-6">
              <SovereigntyScore score={stats.score} />
              <LessonLog lessons={lessons} />
            </div>
          </div>

          <TokenGuard usage={usage} />
          <ValueProposition />
        </>
      ) : (
        <div className="h-[700px] mb-8">
          <HolographicGraph />
        </div>
      )}
    </div>
  );
};

export default App;
