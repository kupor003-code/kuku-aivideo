/**
 * 卡片式工作流组件
 *
 * 简单、可靠的工作流管理系统
 */

import { useState, useCallback } from 'react';
import './WorkflowCard.css';

// 节点类型
export type WorkflowNodeType = 'script' | 'prompt' | 'storyboard' | 'image' | 'video';

// 节点状态
export type NodeStatus = 'pending' | 'running' | 'completed' | 'error';

// 工作流节点
export interface WorkflowNode {
  id: string;
  type: WorkflowNodeType;
  status: NodeStatus;
  result?: any;
  error?: string;
  createdAt: Date;
}

// 节点配置
const NODE_CONFIGS: Record<WorkflowNodeType, {
  title: string;
  icon: string;
  description: string;
  color: string;
}> = {
  script: {
    title: '剧本创作',
    icon: '📝',
    description: '创作短剧剧本',
    color: '#667eea',
  },
  prompt: {
    title: '提示词优化',
    icon: '✨',
    description: '优化场景提示词',
    color: '#f59e0b',
  },
  storyboard: {
    title: '分镜设计',
    icon: '📸',
    description: '生成分镜设计',
    color: '#10b981',
  },
  image: {
    title: '生成图片',
    icon: '🖼️',
    description: '生成首尾帧图片',
    color: '#8b5cf6',
  },
  video: {
    title: '生成视频',
    icon: '🎬',
    description: '生成视频片段',
    color: '#ec4899',
  },
};

interface WorkflowCardProps {
  projectId?: string;
  onNodeExecute?: (nodeId: string, nodeType: WorkflowNodeType) => Promise<any>;
  onWorkflowComplete?: (nodes: WorkflowNode[]) => Promise<void>;
  initialNodes?: WorkflowNode[];
}

export default function WorkflowCard({
  projectId,
  onNodeExecute,
  onWorkflowComplete,
  initialNodes = [],
}: WorkflowCardProps) {
  const [nodes, setNodes] = useState<WorkflowNode[]>(initialNodes);
  const [isRunning, setIsRunning] = useState(false);

  // 添加节点
  const addNode = useCallback((type: WorkflowNodeType) => {
    const newNode: WorkflowNode = {
      id: `node-${Date.now()}-${type}`,
      type,
      status: 'pending',
      createdAt: new Date(),
    };
    setNodes((prev) => [...prev, newNode]);
  }, []);

  // 删除节点
  const removeNode = useCallback((nodeId: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
  }, []);

  // 执行单个节点
  const executeNode = useCallback(async (node: WorkflowNode) => {
    if (isRunning || !onNodeExecute) return;

    // 更新状态为运行中
    setNodes((prev) =>
      prev.map((n) =>
        n.id === node.id ? { ...n, status: 'running' } : n
      )
    );
    setIsRunning(true);

    try {
      const result = await onNodeExecute(node.id, node.type);

      // 更新状态为完成
      setNodes((prev) =>
        prev.map((n) =>
          n.id === node.id
            ? { ...n, status: 'completed', result }
            : n
        )
      );
    } catch (error: any) {
      // 更新状态为失败
      setNodes((prev) =>
        prev.map((n) =>
          n.id === node.id
            ? { ...n, status: 'error', error: error.message }
            : n
        )
      );
    } finally {
      setIsRunning(false);
    }
  }, [isRunning, onNodeExecute]);

  // 运行所有节点
  const runAllNodes = useCallback(async () => {
    if (isRunning || nodes.length === 0) return;

    setIsRunning(true);

    // 按顺序执行每个节点
    for (const node of nodes) {
      if (node.status === 'completed') continue; // 跳过已完成的节点

      // 更新状态为运行中
      setNodes((prev) =>
        prev.map((n) =>
          n.id === node.id ? { ...n, status: 'running' } : n
        )
      );

      try {
        const result = await onNodeExecute?.(node.id, node.type);

        // 更新状态为完成
        setNodes((prev) =>
          prev.map((n) =>
            n.id === node.id
              ? { ...n, status: 'completed', result }
              : n
          )
        );
      } catch (error: any) {
        // 更新状态为失败
        setNodes((prev) =>
          prev.map((n) =>
            n.id === node.id
              ? { ...n, status: 'error', error: error.message }
              : n
          )
        );
        // 出错后停止执行
        break;
      }
    }

    setIsRunning(false);

    // 通知完成
    if (onWorkflowComplete) {
      await onWorkflowComplete(nodes);
    }
  }, [isRunning, nodes, onNodeExecute, onWorkflowComplete]);

  // 清空所有节点
  const clearNodes = useCallback(() => {
    if (confirm('确定要清空所有节点吗？')) {
      setNodes([]);
    }
  }, []);

  return (
    <div className="workflow-card">
      {/* 工具栏 */}
      <div className="workflow-toolbar">
        <div className="toolbar-section">
          <h3>节点工具箱</h3>
          <div className="node-buttons">
            <button
              onClick={() => addNode('script')}
              className="node-btn script-btn"
              disabled={isRunning}
            >
              📝 剧本
            </button>
            <button
              onClick={() => addNode('prompt')}
              className="node-btn prompt-btn"
              disabled={isRunning}
            >
              ✨ 提示词
            </button>
            <button
              onClick={() => addNode('storyboard')}
              className="node-btn storyboard-btn"
              disabled={isRunning}
            >
              📸 分镜
            </button>
            <button
              onClick={() => addNode('image')}
              className="node-btn image-btn"
              disabled={isRunning}
            >
              🖼️ 图片
            </button>
            <button
              onClick={() => addNode('video')}
              className="node-btn video-btn"
              disabled={isRunning}
            >
              🎬 视频
            </button>
          </div>
        </div>

        <div className="toolbar-section">
          <h3>运行控制</h3>
          <div className="control-buttons">
            <button
              onClick={runAllNodes}
              disabled={isRunning || nodes.length === 0}
              className="control-btn run-btn"
            >
              {isRunning ? '⏳ 运行中...' : '▶️ 运行全部'}
            </button>
            <button
              onClick={clearNodes}
              disabled={isRunning}
              className="control-btn clear-btn"
            >
              🗑️ 清空
            </button>
          </div>
        </div>
      </div>

      {/* 节点列表 */}
      <div className="workflow-nodes">
        {nodes.length === 0 ? (
          <div className="empty-workflow">
            <div className="empty-icon">📋</div>
            <h3>工作流为空</h3>
            <p>点击上方按钮添加节点开始创作</p>
            <div className="workflow-tips">
              <p>推荐工作流：</p>
              <ol>
                <li>添加 📝 剧本创作 节点</li>
                <li>添加 ✨ 提示词优化 节点</li>
                <li>添加 📸 分镜设计 节点</li>
                <li>添加 🖼️ 生成图片 节点</li>
                <li>添加 🎬 生成视频 节点</li>
                <li>点击"运行全部"执行工作流</li>
              </ol>
            </div>
          </div>
        ) : (
          <div className="nodes-list">
            {nodes.map((node, index) => {
              const config = NODE_CONFIGS[node.type];
              return (
                <div
                  key={node.id}
                  className={`workflow-node-card ${node.status}`}
                  style={{ borderColor: config.color }}
                >
                  {/* 节点头部 */}
                  <div
                    className="node-card-header"
                    style={{ background: `${config.color}15` }}
                  >
                    <div className="node-number">{index + 1}</div>
                    <div className="node-info">
                      <span className="node-icon">{config.icon}</span>
                      <span className="node-title">{config.title}</span>
                    </div>
                    <button
                      onClick={() => removeNode(node.id)}
                      className="remove-btn"
                      disabled={isRunning}
                      title="删除节点"
                    >
                      ✕
                    </button>
                  </div>

                  {/* 节点状态 */}
                  <div className="node-card-body">
                    <p className="node-description">{config.description}</p>

                    {/* 状态显示 */}
                    <div className="node-status">
                      {node.status === 'pending' && (
                        <span className="status-badge pending">⏳ 待执行</span>
                      )}
                      {node.status === 'running' && (
                        <span className="status-badge running">⚙️ 运行中...</span>
                      )}
                      {node.status === 'completed' && (
                        <span className="status-badge completed">✓ 已完成</span>
                      )}
                      {node.status === 'error' && (
                        <span className="status-badge error">❌ 失败: {node.error}</span>
                      )}
                    </div>

                    {/* 执行按钮 */}
                    {node.status !== 'completed' && node.status !== 'running' && (
                      <button
                        onClick={() => executeNode(node)}
                        className="execute-btn"
                        disabled={isRunning}
                        style={{ background: config.color }}
                      >
                        执行此节点
                      </button>
                    )}

                    {/* 结果预览 */}
                    {node.status === 'completed' && node.result && (
                      <div className="node-result">
                        <div className="result-summary">
                          {node.type === 'image' && node.result.images && (
                            <span>✅ 已生成 {node.result.images.length} 张图片</span>
                          )}
                          {node.type === 'video' && node.result.video_url && (
                            <span>✅ 视频已生成</span>
                          )}
                          {node.type === 'script' && node.result.message && (
                            <span>✅ {node.result.message.substring(0, 50)}...</span>
                          )}
                          {node.type === 'prompt' && node.result.message && (
                            <span>✅ {node.result.message.substring(0, 50)}...</span>
                          )}
                          {node.type === 'storyboard' && node.result.message && (
                            <span>✅ {node.result.message.substring(0, 50)}...</span>
                          )}
                        </div>
                        {node.result.images && node.result.images.length > 0 && (
                          <div className="result-images">
                            {node.result.images.map((img: any, idx: number) => (
                              <img
                                key={idx}
                                src={img.url}
                                alt={`Generated ${idx}`}
                                className="result-image"
                              />
                            ))}
                          </div>
                        )}
                        {node.result.video_url && (
                          <div className="result-video">
                            <video
                              src={node.result.video_url}
                              controls
                              className="result-video-player"
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
