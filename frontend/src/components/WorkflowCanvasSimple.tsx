/**
 * WorkflowCanvas - 简化测试版
 *
 * 逐步测试 ReactFlow 功能
 */

import { useCallback } from 'react';
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
import './WorkflowCanvas.css';

// 初始节点
const initialNodes: Node[] = [
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
];

const initialEdges: Edge[] = [];

interface WorkflowCanvasSimpleProps {
  projectId?: string;
}

export default function WorkflowCanvasSimple({
  projectId,
}: WorkflowCanvasSimpleProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // 连接节点
  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge({ ...params, animated: true }, eds));
  }, [setEdges]);

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{
        padding: '10px',
        background: '#f8fafc',
        borderBottom: '1px solid #e2e8f0',
        display: 'flex',
        gap: '8px',
        flexShrink: 0,
      }}>
        <button
          onClick={() => {
            const newNode: Node = {
              id: `node-${Date.now()}`,
              type: 'default',
              position: { x: Math.random() * 400, y: Math.random() * 300 },
              data: { label: '新节点' },
            };
            setNodes((nds) => [...nds, newNode]);
          }}
          style={{
            padding: '8px 16px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          + 添加节点
        </button>
        <button
          onClick={() => {
            if (confirm('确定要清空画布吗？')) {
              setNodes([]);
              setEdges([]);
            }
          }}
          style={{
            padding: '8px 16px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          清空
        </button>
      </div>

      <div style={{ flex: 1, minHeight: '400px' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          style={{ width: '100%', height: '100%', background: '#f8fafc' }}
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
