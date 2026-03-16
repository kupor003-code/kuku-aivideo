/**
 * WorkflowCanvas - 工作流画布组件
 *
 * 类似 ComfyUI 的可视化工作流编辑器
 * - 拖拽添加节点
 * - 连接节点创建工作流
 * - 运行工作流
 */

import { useState, useCallback, useRef } from 'react';
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
import ScriptNode from './canvas/ScriptNode';
import PromptNode from './canvas/PromptNode';
import StoryboardNode from './canvas/StoryboardNode';
import ImageNode from './canvas/ImageNode';
import VideoNode from './canvas/VideoNode';
import './WorkflowCanvas.css';

// 注册节点类型
const nodeTypes = {
  script: ScriptNode,
  prompt: PromptNode,
  storyboard: StoryboardNode,
  image: ImageNode,
  video: VideoNode,
};

// 初始节点
const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

interface WorkflowCanvasProps {
  projectId?: string;
  onNodeExecute?: (nodeId: string, nodeType: string) => Promise<any>;
  onWorkflowExecute?: (nodes: Node[], edges: Edge[]) => Promise<void>;
}

export default function WorkflowCanvas({
  projectId,
  onNodeExecute,
  onWorkflowExecute,
}: WorkflowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [isExecuting, setIsExecuting] = useState(false);

  // 添加节点
  const addNode = useCallback((type: string, position?: { x: number; y: number }) => {
    const newNode: Node = {
      id: `${type}-${Date.now()}`,
      type,
      position: position || { x: Math.random() * 500, y: Math.random() * 500 },
      data: {
        label: getNodeLabel(type),
        status: 'pending',
        projectId,
      },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes, projectId]);

  // 连接节点
  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge({ ...params, animated: true }, eds));
  }, [setEdges]);

  // 运行整个工作流
  const runWorkflow = useCallback(async () => {
    if (isExecuting) return;

    setIsExecuting(true);

    try {
      // 计算执行顺序（拓扑排序）
      const executionOrder = topologicalSort(nodes, edges);

      // 按顺序执行节点
      for (const nodeId of executionOrder) {
        const node = nodes.find((n) => n.id === nodeId);
        if (!node) continue;

        // 更新节点状态为运行中
        setNodes((nds) =>
          nds.map((n) =>
            n.id === nodeId
              ? { ...n, data: { ...n.data, status: 'running' } }
              : n
          )
        );

        // 执行节点
        if (onNodeExecute) {
          try {
            const result = await onNodeExecute(nodeId, node.type || '');

            // 更新节点状态为完成
            setNodes((nds) =>
              nds.map((n) =>
                n.id === nodeId
                  ? { ...n, data: { ...n.data, status: 'completed', result } }
                  : n
              )
            );
          } catch (error) {
            // 更新节点状态为失败
            setNodes((nds) =>
              nds.map((n) =>
                n.id === nodeId
                  ? { ...n, data: { ...n.data, status: 'error', error } }
                  : n
              )
            );
          }
        }
      }

      // 执行完成
      if (onWorkflowExecute) {
        await onWorkflowExecute(nodes, edges);
      }
    } finally {
      setIsExecuting(false);
    }
  }, [nodes, edges, isExecuting, onNodeExecute, onWorkflowExecute, setNodes]);

  // 清空画布
  const clearCanvas = useCallback(() => {
    if (confirm('确定要清空画布吗？')) {
      setNodes([]);
      setEdges([]);
    }
  }, [setNodes, setEdges]);

  return (
    <div className="workflow-canvas">
      {/* 工具栏 */}
      <div className="canvas-toolbar">
        <div className="toolbar-section">
          <h3>节点工具箱</h3>
          <button onClick={() => addNode('script')} className="toolbar-btn">
            📝 剧本
          </button>
          <button onClick={() => addNode('prompt')} className="toolbar-btn">
            ✨ 提示词
          </button>
          <button onClick={() => addNode('storyboard')} className="toolbar-btn">
            📸 分镜
          </button>
          <button onClick={() => addNode('image')} className="toolbar-btn">
            🖼️ 图片
          </button>
          <button onClick={() => addNode('video')} className="toolbar-btn">
            🎬 视频
          </button>
        </div>

        <div className="toolbar-section">
          <h3>运行控制</h3>
          <button
            onClick={runWorkflow}
            disabled={isExecuting || nodes.length === 0}
            className="toolbar-btn primary"
          >
            {isExecuting ? '⏳ 运行中...' : '▶️ 运行工作流'}
          </button>
          <button
            onClick={clearCanvas}
            className="toolbar-btn danger"
          >
            🗑️ 清空
          </button>
        </div>
      </div>

      {/* ReactFlow 画布 */}
      <div className="canvas-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}

// 获取节点标签
function getNodeLabel(type: string): string {
  const labels: Record<string, string> = {
    script: '剧本创作',
    prompt: '提示词优化',
    storyboard: '分镜设计',
    image: '生成图片',
    video: '生成视频',
  };
  return labels[type] || type;
}

// 拓扑排序 - 确定节点执行顺序
function topologicalSort(nodes: Node[], edges: Edge[]): string[] {
  // 构建邻接表和入度表
  const adj: Record<string, string[]> = {};
  const inDegree: Record<string, number> = {};

  nodes.forEach((node) => {
    adj[node.id] = [];
    inDegree[node.id] = 0;
  });

  edges.forEach((edge) => {
    if (edge.source) {
      adj[edge.source].push(edge.target);
      inDegree[edge.target] = (inDegree[edge.target] || 0) + 1;
    }
  });

  // 找到所有入度为0的节点
  const queue: string[] = [];
  Object.keys(inDegree).forEach((nodeId) => {
    if (inDegree[nodeId] === 0) {
      queue.push(nodeId);
    }
  });

  // 拓扑排序
  const result: string[] = [];
  while (queue.length > 0) {
    const nodeId = queue.shift()!;
    result.push(nodeId);

    adj[nodeId].forEach((neighbor) => {
      inDegree[neighbor]--;
      if (inDegree[neighbor] === 0) {
        queue.push(neighbor);
      }
    });
  }

  return result;
}
