/**
 * 超级简化的 WorkflowCard 测试组件
 */

import { useState, useCallback } from 'react';

export type WorkflowNodeType = 'script' | 'prompt' | 'storyboard' | 'image' | 'video';

export interface WorkflowNode {
  id: string;
  type: WorkflowNodeType;
  status: 'pending' | 'running' | 'completed' | 'error';
}

interface WorkflowCardSimpleProps {
  projectId?: string;
  onNodeExecute?: (nodeId: string, nodeType: WorkflowNodeType) => Promise<any>;
  onWorkflowComplete?: (nodes: WorkflowNode[]) => Promise<void>;
}

export default function WorkflowCardSimple({
  projectId,
  onNodeExecute,
  onWorkflowComplete,
}: WorkflowCardSimpleProps) {
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const addNode = useCallback((type: WorkflowNodeType) => {
    const newNode: WorkflowNode = {
      id: `node-${Date.now()}-${type}`,
      type,
      status: 'pending',
    };
    setNodes((prev) => [...prev, newNode]);
  }, []);

  const removeNode = useCallback((nodeId: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: 'white',
      borderRadius: '12px',
      overflow: 'hidden'
    }}>
      {/* 工具栏 */}
      <div style={{
        padding: '16px',
        background: '#f8fafc',
        borderBottom: '1px solid #e2e8f0'
      }}>
        <div style={{ marginBottom: '12px', fontSize: '14px', fontWeight: 'bold' }}>
          添加节点：
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={() => addNode('script')}
            disabled={isRunning}
            style={{
              padding: '8px 16px',
              background: isRunning ? '#ccc' : '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isRunning ? 'not-allowed' : 'pointer'
            }}
          >
            📝 剧本
          </button>
          <button
            onClick={() => addNode('prompt')}
            disabled={isRunning}
            style={{
              padding: '8px 16px',
              background: isRunning ? '#ccc' : '#f59e0b',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isRunning ? 'not-allowed' : 'pointer'
            }}
          >
            ✨ 提示词
          </button>
          <button
            onClick={() => addNode('storyboard')}
            disabled={isRunning}
            style={{
              padding: '8px 16px',
              background: isRunning ? '#ccc' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isRunning ? 'not-allowed' : 'pointer'
            }}
          >
            📸 分镜
          </button>
          <button
            onClick={() => addNode('image')}
            disabled={isRunning}
            style={{
              padding: '8px 16px',
              background: isRunning ? '#ccc' : '#8b5cf6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isRunning ? 'not-allowed' : 'pointer'
            }}
          >
            🖼️ 图片
          </button>
          <button
            onClick={() => addNode('video')}
            disabled={isRunning}
            style={{
              padding: '8px 16px',
              background: isRunning ? '#ccc' : '#ec4899',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isRunning ? 'not-allowed' : 'pointer'
            }}
          >
            🎬 视频
          </button>
        </div>
      </div>

      {/* 节点列表 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        background: '#f8fafc'
      }}>
        {nodes.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: '#94a3b8'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>📋</div>
            <h3>工作流为空</h3>
            <p>点击上方按钮添加节点开始创作</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {nodes.map((node, index) => (
              <div
                key={node.id}
                style={{
                  background: 'white',
                  border: '2px solid #e2e8f0',
                  borderRadius: '12px',
                  padding: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}
              >
                <div style={{
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: '#667eea',
                  color: 'white',
                  borderRadius: '50%',
                  fontWeight: 'bold'
                }}>
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <strong>{node.type}</strong>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>
                    状态: {node.status}
                  </div>
                </div>
                <button
                  onClick={() => removeNode(node.id)}
                  disabled={isRunning}
                  style={{
                    width: '28px',
                    height: '28px',
                    background: 'transparent',
                    border: 'none',
                    color: '#94a3b8',
                    cursor: isRunning ? 'not-allowed' : 'pointer',
                    borderRadius: '6px',
                    fontSize: '18px'
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
