/**
 * 完整的卡片式工作流系统
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { projectService } from '../services/projectService';
import type { Project } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// 节点类型
type NodeType = 'script' | 'prompt' | 'storyboard' | 'image' | 'video';
type NodeStatus = 'pending' | 'running' | 'completed' | 'error';

interface WorkflowNode {
  id: string;
  type: NodeType;
  status: NodeStatus;
  result?: any;
  error?: string;
  createdAt: Date;
}

// 节点配置
const NODE_CONFIGS: Record<NodeType, {
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

// 加载动画
const LoadingIcon = () => (
  <svg className="loading-icon" viewBox="0 0 50 50" style={{width: 20, height: 20}}>
    <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5">
      <animate attributeName="stroke-dasharray" from="0, 100" to="100, 0" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="stroke-dashoffset" from="0" to="-100" dur="2s" repeatCount="indefinite"/>
    </circle>
  </svg>
);

export default function WorkspaceWorkflowFinal() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 状态
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{role: string; content: string; timestamp: string}>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showView, setShowView] = useState<'chat' | 'workflow' | 'both'>('both');
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  // 初始化
  useEffect(() => {
    if (!projectId) {
      navigate('/projects');
      return;
    }
    loadProject(projectId);
  }, [projectId, navigate]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 加载项目
  const loadProject = async (id: string) => {
    try {
      const project = await projectService.get(id);
      setCurrentProject(project);
    } catch (error) {
      console.error('加载项目失败:', error);
      navigate('/projects');
    }
  };

  // 发送消息
  const handleSend = async () => {
    if (!input.trim() || isLoading || !projectId) return;

    const userMessage = input.trim();
    setInput('');

    addMessage('user', userMessage);
    setIsLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/agents/v2/chat`,
        {
          project_id: projectId,
          message: userMessage,
          current_stage: 'script',
        }
      );

      if (response.data.success) {
        const aiMessage = response.data.message || '正在处理您的请求...';
        addMessage('assistant', aiMessage);
      } else {
        addMessage('assistant', '⚠️ 处理失败，请重试。');
      }

    } catch (error: any) {
      console.error('发送失败:', error);
      addMessage('assistant', `❌ 抱歉，发送失败：${error.message || '未知错误'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 添加消息
  const addMessage = (role: string, content: string) => {
    setMessages(prev => [...prev, {
      role,
      content,
      timestamp: new Date().toISOString(),
    }]);
  };

  // 添加节点
  const addNode = (type: NodeType) => {
    const newNode: WorkflowNode = {
      id: `node-${Date.now()}-${type}`,
      type,
      status: 'pending',
      createdAt: new Date(),
    };
    setNodes((prev) => [...prev, newNode]);
  };

  // 删除节点
  const removeNode = (nodeId: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
  };

  // 执行单个节点
  const executeNode = async (node: WorkflowNode) => {
    if (isRunning) return;

    setNodes((prev) =>
      prev.map((n) =>
        n.id === node.id ? { ...n, status: 'running' } : n
      )
    );
    setIsRunning(true);

    try {
      let response;
      const config = NODE_CONFIGS[node.type];

      switch (node.type) {
        case 'script':
          response = await axios.post(`${API_URL}/agents/v2/chat`, {
            project_id: projectId,
            message: '请根据我们的对话创作一个完整的剧本',
            current_stage: 'script',
          });
          break;

        case 'prompt':
          response = await axios.post(`${API_URL}/agents/v2/chat`, {
            project_id: projectId,
            message: '请优化剧本的场景提示词，使其更适合视频生成',
            current_stage: 'prompts',
          });
          break;

        case 'storyboard':
          response = await axios.post(`${API_URL}/agents/v2/chat`, {
            project_id: projectId,
            message: '请根据剧本生成分镜设计，规划每个镜头的描述、角度和构图',
            current_stage: 'storyboard',
          });
          break;

        case 'image':
          response = await axios.post(`${API_URL}/generation/generate/image`, {
            prompt: '赛博朋克城市夜景，霓虹灯闪烁，雨中的街道',
            size: '1024*1024',
            n: 1,
            style: 'photography',
          });

          setNodes((prev) =>
            prev.map((n) =>
              n.id === node.id
                ? { ...n, status: 'completed', result: {
                    message: '✅ 图片生成成功！',
                    images: response.data.images || [],
                    count: response.data.images?.length || 0,
                  }}
                : n
            )
          );
          setIsRunning(false);
          return;

        case 'video':
          response = await axios.post(`${API_URL}/generation/generate/video`, {
            prompt: '赛博朋克城市夜景，霓虹灯闪烁，雨中的街道，未来感',
            duration: 3.0,
            fps: 25,
            resolution: '720p',
          });

          setNodes((prev) =>
            prev.map((n) =>
              n.id === node.id
                ? { ...n, status: 'completed', result: {
                    message: '✅ 视频生成成功！',
                    video_url: response.data.video_url,
                    video_id: response.data.video_id,
                    duration: response.data.duration,
                    count: 1,
                  }}
                : n
            )
          );
          setIsRunning(false);
          return;

        default:
          throw new Error(`未知节点类型: ${node.type}`);
      }

      setNodes((prev) =>
        prev.map((n) =>
          n.id === node.id
            ? { ...n, status: 'completed', result: response.data }
            : n
        )
      );
    } catch (error: any) {
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
  };

  // 运行所有节点
  const runAllNodes = async () => {
    if (isRunning || nodes.length === 0) return;

    setIsRunning(true);

    for (const node of nodes) {
      if (node.status === 'completed') continue;

      setNodes((prev) =>
        prev.map((n) =>
          n.id === node.id ? { ...n, status: 'running' } : n
        )
      );

      try {
        await executeNode(node);
      } catch (error: any) {
        setNodes((prev) =>
          prev.map((n) =>
            n.id === node.id
              ? { ...n, status: 'error', error: error.message }
              : n
          )
        );
        break;
      }
    }

    setIsRunning(false);
    addMessage('assistant', '✅ 工作流执行完成！');
  };

  // 清空所有节点
  const clearNodes = () => {
    if (confirm('确定要清空所有节点吗？')) {
      setNodes([]);
    }
  };

  if (!currentProject) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f5f5f5'
      }}>
        <div style={{ textAlign: 'center' }}>
          <LoadingIcon />
          <h2 style={{ marginTop: '20px' }}>加载中...</h2>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#f5f5f5'
    }}>
      {/* 顶部导航 */}
      <div style={{
        padding: '20px',
        background: 'white',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button
            onClick={() => navigate('/projects')}
            style={{
              padding: '10px 20px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            ← 返回项目列表
          </button>
          <div>
            <h1 style={{ margin: 0 }}>{currentProject.title}</h1>
            {currentProject.description && (
              <p style={{ margin: '5px 0 0 0', color: '#666', fontSize: '14px' }}>
                {currentProject.description}
              </p>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowView('chat')}
            style={{
              padding: '8px 16px',
              background: showView === 'chat' ? '#667eea' : 'white',
              color: showView === 'chat' ? 'white' : '#333',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            💬 仅对话
          </button>
          <button
            onClick={() => setShowView('workflow')}
            style={{
              padding: '8px 16px',
              background: showView === 'workflow' ? '#667eea' : 'white',
              color: showView === 'workflow' ? 'white' : '#333',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            📋 仅工作流
          </button>
          <button
            onClick={() => setShowView('both')}
            style={{
              padding: '8px 16px',
              background: showView === 'both' ? '#667eea' : 'white',
              color: showView === 'both' ? 'white' : '#333',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            📊 分屏
          </button>
        </div>
      </div>

      {/* 主内容区 */}
      <div style={{
        flex: 1,
        display: 'flex',
        gap: '20px',
        padding: '20px',
        overflow: 'hidden'
      }}>
        {/* 左侧：对话区 */}
        {showView !== 'workflow' && (
          <div style={{
            flex: 1,
            background: 'white',
            borderRadius: '12px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            minWidth: 0
          }}>
            <div style={{ padding: '16px', borderBottom: '1px solid #e0e0e0' }}>
              <h2 style={{ margin: 0 }}>💬 AI 对话</h2>
              <p style={{ margin: '5px 0 0 0', color: '#666', fontSize: '14px' }}>
                告诉我你的创意，我会帮你创作短剧
              </p>
            </div>

            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '16px'
            }}>
              {messages.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  padding: '40px 20px',
                  color: '#94a3b8'
                }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
                  <h3>开始创作</h3>
                  <p>告诉我你想要创作什么样的短剧</p>
                </div>
              ) : (
                <>
                  {messages.map((msg, index) => (
                    <div
                      key={index}
                      style={{
                        marginBottom: '16px',
                        display: 'flex',
                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
                      }}
                    >
                      <div style={{
                        maxWidth: '70%',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        background: msg.role === 'user' ? '#667eea' : '#f1f5f9',
                        color: msg.role === 'user' ? 'white' : '#333'
                      }}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{
                        display: 'inline-block',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        background: '#f1f5f9'
                      }}>
                        <LoadingIcon />
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            <div style={{ padding: '16px', borderTop: '1px solid #e0e0e0' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="输入你的创意..."
                  style={{
                    flex: 1,
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    resize: 'none',
                    minHeight: '50px',
                    fontFamily: 'inherit'
                  }}
                  rows={2}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  style={{
                    padding: '10px 20px',
                    background: !input.trim() || isLoading ? '#ccc' : '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: !input.trim() || isLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  发送
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 右侧：工作流面板 */}
        {showView !== 'chat' && (
          <div style={{
            flex: 1,
            background: 'white',
            borderRadius: '12px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            minWidth: 0
          }}>
            {/* 工具栏 */}
            <div style={{
              padding: '16px',
              background: '#f8fafc',
              borderBottom: '1px solid #e2e8f0'
            }}>
              <div style={{ marginBottom: '12px', fontSize: '14px', fontWeight: 'bold' }}>
                节点工具箱
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
                <button
                  onClick={() => addNode('script')}
                  disabled={isRunning}
                  style={{
                    padding: '8px 16px',
                    background: isRunning ? '#ccc' : '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: isRunning ? 'not-allowed' : 'pointer',
                    fontSize: '13px'
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
                    cursor: isRunning ? 'not-allowed' : 'pointer',
                    fontSize: '13px'
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
                    cursor: isRunning ? 'not-allowed' : 'pointer',
                    fontSize: '13px'
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
                    cursor: isRunning ? 'not-allowed' : 'pointer',
                    fontSize: '13px'
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
                    cursor: isRunning ? 'not-allowed' : 'pointer',
                    fontSize: '13px'
                  }}
                >
                  🎬 视频
                </button>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={runAllNodes}
                  disabled={isRunning || nodes.length === 0}
                  style={{
                    padding: '10px 20px',
                    background: isRunning || nodes.length === 0 ? '#ccc' : '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: isRunning || nodes.length === 0 ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    fontWeight: 'bold'
                  }}
                >
                  {isRunning ? '⏳ 运行中...' : '▶️ 运行全部'}
                </button>
                <button
                  onClick={clearNodes}
                  disabled={isRunning}
                  style={{
                    padding: '10px 20px',
                    background: isRunning ? '#ccc' : '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: isRunning ? 'not-allowed' : 'pointer',
                    fontSize: '13px'
                  }}
                >
                  🗑️ 清空
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
                  textAlign: 'center',
                  padding: '40px 20px',
                  color: '#94a3b8'
                }}>
                  <div style={{ fontSize: '64px', marginBottom: '16px' }}>📋</div>
                  <h3>工作流为空</h3>
                  <p>点击上方按钮添加节点开始创作</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {nodes.map((node, index) => {
                    const config = NODE_CONFIGS[node.type];
                    return (
                      <div
                        key={node.id}
                        style={{
                          background: node.status === 'completed' ? '#f0fdf4' : 'white',
                          border: `2px solid ${config.color}`,
                          borderRadius: '12px',
                          overflow: 'hidden',
                          transition: 'all 0.2s'
                        }}
                      >
                        {/* 节点头部 */}
                        <div style={{
                          padding: '12px 16px',
                          background: `${config.color}15`,
                          borderBottom: '1px solid #f1f5f9',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px'
                        }}>
                          <div style={{
                            width: '28px',
                            height: '28px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: config.color,
                            color: 'white',
                            borderRadius: '50%',
                            fontSize: '13px',
                            fontWeight: 'bold'
                          }}>
                            {index + 1}
                          </div>
                          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '20px' }}>{config.icon}</span>
                            <span style={{ fontSize: '15px', fontWeight: 'bold' }}>
                              {config.title}
                            </span>
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
                            title="删除节点"
                          >
                            ✕
                          </button>
                        </div>

                        {/* 节点主体 */}
                        <div style={{ padding: '16px' }}>
                          <p style={{ margin: '0 0 12px 0', fontSize: '13px', color: '#64748b' }}>
                            {config.description}
                          </p>

                          {/* 状态显示 */}
                          <div style={{ marginBottom: '12px' }}>
                            {node.status === 'pending' && (
                              <span style={{
                                display: 'inline-block',
                                padding: '6px 12px',
                                borderRadius: '20px',
                                fontSize: '12px',
                                fontWeight: 'bold',
                                background: '#f1f5f9',
                                color: '#64748b'
                              }}>
                                ⏳ 待执行
                              </span>
                            )}
                            {node.status === 'running' && (
                              <span style={{
                                display: 'inline-block',
                                padding: '6px 12px',
                                borderRadius: '20px',
                                fontSize: '12px',
                                fontWeight: 'bold',
                                background: '#fef3c7',
                                color: '#d97706'
                              }}>
                                ⚙️ 运行中...
                              </span>
                            )}
                            {node.status === 'completed' && (
                              <span style={{
                                display: 'inline-block',
                                padding: '6px 12px',
                                borderRadius: '20px',
                                fontSize: '12px',
                                fontWeight: 'bold',
                                background: '#d1fae5',
                                color: '#059669'
                              }}>
                                ✓ 已完成
                              </span>
                            )}
                            {node.status === 'error' && (
                              <span style={{
                                display: 'inline-block',
                                padding: '6px 12px',
                                borderRadius: '20px',
                                fontSize: '12px',
                                fontWeight: 'bold',
                                background: '#fee2e2',
                                color: '#dc2626'
                              }}>
                                ❌ 失败
                              </span>
                            )}
                          </div>

                          {/* 执行按钮 */}
                          {node.status !== 'completed' && node.status !== 'running' && (
                            <button
                              onClick={() => executeNode(node)}
                              disabled={isRunning}
                              style={{
                                width: '100%',
                                padding: '10px',
                                background: isRunning ? '#ccc' : config.color,
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                cursor: isRunning ? 'not-allowed' : 'pointer',
                                fontSize: '13px',
                                fontWeight: 'bold'
                              }}
                            >
                              执行此节点
                            </button>
                          )}

                          {/* 结果预览 */}
                          {node.status === 'completed' && node.result && (
                            <div style={{
                              marginTop: '12px',
                              padding: '12px',
                              background: '#f8fafc',
                              borderRadius: '8px',
                              border: '1px solid #e2e8f0'
                            }}>
                              <div style={{ fontSize: '13px', color: '#059669', fontWeight: 'bold' }}>
                                {node.result.message || '✅ 执行成功'}
                              </div>
                              {node.result.images && node.result.images.length > 0 && (
                                <div style={{
                                  display: 'grid',
                                  gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
                                  gap: '8px',
                                  marginTop: '8px'
                                }}>
                                  {node.result.images.map((img: any, idx: number) => (
                                    <img
                                      key={idx}
                                      src={img.url}
                                      alt={`Generated ${idx}`}
                                      style={{ width: '100%', borderRadius: '6px' }}
                                    />
                                  ))}
                                </div>
                              )}
                              {node.result.video_url && (
                                <div style={{ marginTop: '8px' }}>
                                  <video
                                    src={node.result.video_url}
                                    controls
                                    style={{ width: '100%', borderRadius: '6px' }}
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
        )}
      </div>
    </div>
  );
}
