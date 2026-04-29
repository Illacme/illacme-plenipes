import React, { useState, useEffect, useRef } from 'react';

/**
 * 🛰️ [V11.0] 实时全息监控组件 (Real-time Holographic Monitor)
 * 职责：订阅 SSE 事件流，展示 AI 思维链、算力波动与同步足迹。
 */
const RealtimeMonitor = () => {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    // 🚀 连接 SSE 事件流
    // 注意：在开发环境下可能需要处理跨域或端口问题
    const eventSource = new EventSource('/stream');

    eventSource.onopen = () => setIsConnected(true);
    eventSource.onerror = () => setIsConnected(false);

    eventSource.onmessage = (e) => {
      const payload = JSON.parse(e.data);
      setEvents(prev => [payload, ...prev].slice(0, 50)); // 保留最近 50 条
    };

    return () => eventSource.close();
  }, []);

  const getEventIcon = (type) => {
    switch (type) {
      case 'ai_call': return '🏎️';
      case 'ai_reasoning': return '🧠';
      case 'doc_start': return '📄';
      case 'error': return '🚨';
      case 'sync_completed': return '✅';
      default: return '📡';
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'ai_call': return 'text-cyan-400';
      case 'ai_reasoning': return 'text-purple-400';
      case 'doc_start': return 'text-amber-400';
      case 'error': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl shadow-2xl">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold tracking-tighter text-white flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
          全息实时监控
        </h3>
        <span className="text-xs text-slate-500 font-mono">SSE: {isConnected ? 'CONNECTED' : 'OFFLINE'}</span>
      </div>

      <div 
        className="h-[400px] overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-800"
        ref={scrollRef}
      >
        {events.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-600 italic text-sm">
            <p>等待引擎点火...</p>
            <p className="text-xs not-italic mt-2">只有在执行同步任务时才会产生实时信号</p>
          </div>
        ) : (
          events.map((ev, idx) => (
            <div 
              key={idx} 
              className="group bg-slate-950/50 border border-slate-900 rounded-lg p-3 hover:border-slate-700 transition-all animate-slide-in"
            >
              <div className="flex items-start gap-3">
                <span className="text-lg">{getEventIcon(ev.type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <span className={`text-xs font-bold uppercase tracking-widest ${getEventColor(ev.type)}`}>
                      {ev.type}
                    </span>
                    <span className="text-[10px] text-slate-600 font-mono">
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-sm text-slate-300 mt-1 break-words">
                    {ev.type === 'ai_reasoning' ? (
                      <em className="text-purple-300/70 block">「思维链」{ev.data.fragment}</em>
                    ) : (
                      typeof ev.data === 'string' ? ev.data : JSON.stringify(ev.data)
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RealtimeMonitor;
