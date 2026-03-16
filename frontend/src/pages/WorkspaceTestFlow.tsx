/**
 * 最简单的 ReactFlow 测试
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { projectService } from '../services/projectService';
import type { Project } from '../types';

export default function WorkspaceTestFlow() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{role: string; content: string}>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showReactFlow, setShowReactFlow] = useState(false);

  useEffect(() => {
    if (!projectId) {
      navigate('/projects');
      return;
    }
    loadProject(projectId);
  }, [projectId, navigate]);

  const loadProject = async (id: string) => {
    try {
      const project = await projectService.get(id);
      setCurrentProject(project);
    } catch (error) {
      console.error('加载项目失败:', error);
      navigate('/projects');
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading || !projectId) return;

    const userMessage = input.trim();
    setInput('');

    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/v1/agents/v2/chat',
        {
          project_id: projectId,
          message: userMessage,
          current_stage: 'script',
        }
      );

      if (response.data.success) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.data.message || '正在处理您的请求...'
        }]);
      }
    } catch (error: any) {
      console.error('发送失败:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ 发送失败：${error.message || '未知错误'}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentProject) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#f5f5f5',
    }}>
      {/* 顶部导航 */}
      <div style={{
        padding: '20px',
        background: 'white',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
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
          ← 返回
        </button>
        <div>
          <h1 style={{ margin: 0, fontSize: '20px' }}>{currentProject.title}</h1>
          {currentProject.description && (
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              {currentProject.description}
            </p>
          )}
        </div>
      </div>

      {/* 主内容 */}
      <div style={{
        flex: 1,
        display: 'flex',
        overflow: 'hidden',
      }}>
        {/* 左侧：对话区 */}
        <div style={{
          flex: 1,
          minWidth: '400px',
          maxWidth: '600px',
          display: 'flex',
          flexDirection: 'column',
          background: 'white',
          margin: '20px',
          borderRadius: '12px',
          border: '1px solid #e0e0e0',
        }}>
          <div style={{ padding: '20px', borderBottom: '1px solid #e0e0e0' }}>
            <h2 style={{ margin: 0 }}>💬 AI 对话</h2>
          </div>

          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '20px',
          }}>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#999' }}>
                <p>开始对话吧！</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  style={{
                    marginBottom: '16px',
                    padding: '12px',
                    background: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
                    borderRadius: '8px',
                  }}
                >
                  <strong>{msg.role === 'user' ? '👤 你' : '🤖 AI'}</strong>
                  <p style={{ margin: '8px 0 0 0' }}>{msg.content}</p>
                </div>
              ))
            )}
            {isLoading && <p>AI 正在思考...</p>}
          </div>

          <div style={{ padding: '16px', borderTop: '1px solid #e0e0e0' }}>
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
                width: '100%',
                minHeight: '60px',
                padding: '12px',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                resize: 'vertical',
              }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              style={{
                marginTop: '8px',
                padding: '10px 20px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              发送
            </button>
          </div>
        </div>

        {/* 右侧：测试区 */}
        <div style={{
          flex: 1,
          background: 'white',
          margin: '20px 20px 20px 0',
          borderRadius: '12px',
          border: '1px solid #e0e0e0',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ padding: '20px', borderBottom: '1px solid #e0e0e0' }}>
            <h2 style={{ margin: 0 }}>🧪 功能测试</h2>
          </div>

          <div style={{ padding: '20px' }}>
            <h3>测试步骤：</h3>
            <ol style={{ lineHeight: '1.8' }}>
              <li>✅ 对话功能 - 已测试正常</li>
              <li>⏳ ReactFlow 测试 - 准备测试</li>
              <li>⏳ 自定义节点 - 待测试</li>
            </ol>

            <div style={{ marginTop: '20px', padding: '16px', background: '#f0f0f0', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 8px 0' }}>当前状态：</h4>
              <p style={{ margin: 0 }}>
                {showReactFlow ? '正在加载 ReactFlow...' : '点击下方按钮测试 ReactFlow'}
              </p>
            </div>

            <button
              onClick={() => setShowReactFlow(true)}
              style={{
                marginTop: '16px',
                padding: '12px 24px',
                background: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
              }}
            >
              测试 ReactFlow 导入
            </button>

            {showReactFlow && (
              <div style={{ marginTop: '16px', padding: '16px', background: '#e8f5e9', borderRadius: '8px' }}>
                <p style={{ margin: 0, color: '#2e7d32' }}>
                  正在尝试导入 ReactFlow...
                </p>
                <p style={{ margin: '8px 0 0 0', fontSize: '13px', color: '#666' }}>
                  请查看浏览器控制台（F12）是否有错误信息
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
