/**
 * Workspace - 带简化画布的版本
 *
 * 测试基础 ReactFlow 功能
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Send } from '@geist-ui/icons';
import axios from 'axios';
import { projectService } from '../services/projectService';
import type { Project } from '../types';
import WorkflowCanvasSimple from '../components/WorkflowCanvasSimple';
import './Workspace.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// 简单的加载图标
const LoadingIcon = () => (
  <svg className="loading-icon" viewBox="0 0 50 50" style={{width: 20, height: 20}}>
    <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5">
      <animate attributeName="stroke-dasharray" from="0, 100" to="100, 0" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="stroke-dashoffset" from="0" to="-100" dur="2s" repeatCount="indefinite"/>
    </circle>
  </svg>
);

export default function WorkspaceWithCanvas() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 状态
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{role: string; content: string; timestamp: string}>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showView, setShowView] = useState<'chat' | 'canvas' | 'both'>('both');

  // 初始化
  useEffect(() => {
    if (!projectId) {
      navigate('/projects');
      return;
    }
    loadProject(projectId);
  }, [projectId, navigate]);

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

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!input.trim() || isLoading || !projectId) return;

    const userMessage = input.trim();
    setInput('');

    // 添加用户消息
    addMessage('user', userMessage);
    setIsLoading(true);

    try {
      // 直接调用 AI 对话接口
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

  if (!currentProject) {
    return (
      <div className="workspace">
        <div className="loading-state">
          <LoadingIcon />
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="workspace">
      {/* 顶部导航 */}
      <div className="workspace-header">
        <button className="back-button" onClick={() => navigate('/projects')}>
          ← 返回项目列表
        </button>
        <div className="project-info">
          <h1>{currentProject.title}</h1>
          {currentProject.description && <p>{currentProject.description}</p>}
        </div>
        <div className="view-controls">
          <button
            className={`view-btn ${showView === 'chat' ? 'active' : ''}`}
            onClick={() => setShowView('chat')}
          >
            💬 仅对话
          </button>
          <button
            className={`view-btn ${showView === 'canvas' ? 'active' : ''}`}
            onClick={() => setShowView('canvas')}
          >
            🎨 仅画布
          </button>
          <button
            className={`view-btn ${showView === 'both' ? 'active' : ''}`}
            onClick={() => setShowView('both')}
          >
            📊 分屏
          </button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="workspace-content">
        {/* 左侧：对话区 */}
        {showView !== 'canvas' && (
          <div className="chat-panel">
            <div className="chat-header">
              <h2>💬 AI 对话</h2>
              <p>告诉我你的创意，我会帮你创作短剧</p>
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">💬</div>
                  <h3>开始创作</h3>
                  <p>告诉我你想要创作什么样的短剧</p>
                  <div className="examples">
                    <p>试试这些：</p>
                    <button className="example-btn" onClick={() => setInput('我想创作一个关于人工智能觉醒的科幻短剧，风格要赛博朋克')}>
                      🤖 科幻短剧
                    </button>
                    <button className="example-btn" onClick={() => setInput('创作一个关于友情的温馨短片，展现人与人之间的真诚情感')}>
                      💝 温馨短片
                    </button>
                    <button className="example-btn" onClick={() => setInput('制作一个赛博朋克风格的城市夜景预告片')}>
                      🌃 赛博朋克
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}>
                      <div className="message-content">
                        <div className="message-avatar">
                          {msg.role === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className="message-bubble">
                          <div className="message-text">{msg.content}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="message assistant-message">
                      <div className="message-content">
                        <div className="message-avatar">🤖</div>
                        <div className="message-bubble loading">
                          <LoadingIcon />
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* 输入区 */}
            <div className="input-area">
              <textarea
                className="message-input"
                placeholder="输入你的创意...（例如：我想创作一个关于科幻主题的短剧）"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={2}
              />
              <button
                className="send-button"
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
              >
                <Send />
              </button>
            </div>
          </div>
        )}

        {/* 右侧：工作流画布（简化版） */}
        {showView !== 'chat' && (
          <div className="workflow-panel-canvas">
            <WorkflowCanvasSimple projectId={projectId} />
          </div>
        )}
      </div>
    </div>
  );
}
