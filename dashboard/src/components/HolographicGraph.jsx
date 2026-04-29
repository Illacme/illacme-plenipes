import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Maximize2, Minimize2, ZoomIn, ZoomOut, RefreshCw, Layers } from 'lucide-react';

const HolographicGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const fgRef = useRef();

  // 颜色映射：基于语种
  const colorMap = {
    'zh-CN': '#3b82f6', // blue
    'en': '#ef4444',    // red
    'ja': '#10b981',    // green
    'unknown': '#6b7280' // gray
  };

  useEffect(() => {
    fetch('/data/link_graph.json')
      .then(res => res.json())
      .then(data => {
        setGraphData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load graph:', err);
        setLoading(false);
      });
  }, []);

  const handleNodeClick = useCallback(node => {
    setSelectedNode(node);
    // 聚焦到节点
    fgRef.current.centerAt(node.x, node.y, 1000);
    fgRef.current.zoom(3, 1000);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <RefreshCw className="animate-spin mr-2" /> 正在构建全息拓扑星系...
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-[#030712] overflow-hidden rounded-2xl border border-slate-800 shadow-2xl">
      {/* 控制栏 */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 bg-slate-900/80 backdrop-blur-md p-2 rounded-lg border border-slate-700">
        <button onClick={() => fgRef.current.zoomToFit(400)} className="p-1.5 hover:bg-slate-700 rounded text-slate-300" title="自适应">
          <Maximize2 size={18} />
        </button>
        <button onClick={() => fgRef.current.zoom(fgRef.current.zoom() * 1.2, 400)} className="p-1.5 hover:bg-slate-700 rounded text-slate-300" title="放大">
          <ZoomIn size={18} />
        </button>
        <button onClick={() => fgRef.current.zoom(fgRef.current.zoom() * 0.8, 400)} className="p-1.5 hover:bg-slate-700 rounded text-slate-300" title="缩小">
          <ZoomOut size={18} />
        </button>
      </div>

      {/* 详情浮窗 */}
      {selectedNode && (
        <div className="absolute top-4 right-4 z-10 w-64 bg-slate-900/90 backdrop-blur-xl p-4 rounded-xl border border-blue-500/30 shadow-xl text-slate-200">
          <h3 className="font-bold text-blue-400 mb-1 truncate">{selectedNode.title}</h3>
          <div className="text-xs text-slate-500 mb-3 font-mono">{selectedNode.id}</div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>语种</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">{selectedNode.lang}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>大小</span>
              <span>{(selectedNode.size / 1024).toFixed(1)} KB</span>
            </div>
          </div>
          <button 
            onClick={() => setSelectedNode(null)}
            className="mt-4 w-full py-1 text-xs bg-slate-800 hover:bg-slate-700 rounded transition-colors"
          >
            关闭详情
          </button>
        </div>
      )}

      {/* 图谱主体 */}
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel={node => `${node.title} (${node.lang})`}
        nodeColor={node => colorMap[node.lang] || colorMap.unknown}
        nodeRelSize={6}
        linkColor={() => 'rgba(148, 163, 184, 0.2)'}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        onNodeClick={handleNodeClick}
        cooldownTicks={100}
        onEngineStop={() => fgRef.current.zoomToFit(400)}
        backgroundColor="rgba(0,0,0,0)"
      />

      {/* 底部提示 */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-[10px] text-slate-500 uppercase tracking-widest bg-slate-950/50 px-3 py-1 rounded-full border border-slate-900">
        Illacme-plenipes Holographic Topology Engine
      </div>
    </div>
  );
};

export default HolographicGraph;
