/**
 * 直接测试 ReactFlow
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from '@xyflow/react';
import type { Connection, Edge, Node } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export default function WorkspaceTestReactFlow() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [nodes, setNodes, onNodesChange] = useNodesState([
    {
      id: '1',
      type: 'default',
      position: { x: 100, y: 100 },
      data: { label: '📝 剧本创作' },
    },
    {
      id: '2',
      type: 'default',
      position: { x: 100, y: 200 },
      data: { label: '✨ 提示词优化' },
    },
  ]);

  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = (params: Connection) => {
    setEdges((eds) => addEdge({ ...params, animated: true }, eds));
  };

  return (
    <div style={{
      height: '100vh',
      width: '100vw',
      display: 'flex',
      flexDirection: 'column',
      background: '#f5f5f5',
    }}>
      {/* 顶部导航 */}
      <div style={{
        padding: '20px',
        background: 'white',
        borderBottom: '1px solid #e0e0e0',
      }}>
        <button
          onClick={() => navigate('/projects')}
          style={{
            padding: '10px 20px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
          }}
        >
          ← 返回项目列表
        </button>
        <h1 style={{ margin: '0 0 0 20px', display: 'inline-block' }}>
          ReactFlow 测试 (项目ID: {projectId})
        </h1>
      </div>

      {/* ReactFlow 画布 */}
      <div style={{ flex: 1, minHeight: '500px' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          style={{ width: '100%', height: '100%' }}
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>

      {/* 操作提示 */}
      <div style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        background: 'white',
        padding: '16px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        maxWidth: '300px',
      }}>
        <h3 style={{ margin: '0 0 8px 0' }}>操作提示：</h3>
        <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px' }}>
          <li>拖动节点改变位置</li>
          <li>点击节点右侧圆点并拖动到另一个节点来连接</li>
          <li>使用左上角的控制按钮缩放和适应视图</li>
          <li>使用右下角的迷你地图导航</li>
        </ul>
        <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#666' }}>
          如果你能看到两个节点和背景点阵，说明 ReactFlow 工作正常！
        </p>
      </div>
    </div>
  );
}
