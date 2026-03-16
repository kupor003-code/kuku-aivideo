/**
 * 最终测试版本 - 不依赖任何复杂组件
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService } from '../services/projectService';
import type { Project } from '../types';

export default function WorkspaceTestFinal() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [nodes, setNodes] = useState<Array<{id: string; type: string}>>([]);

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
    } catch (err: any) {
      console.error('加载失败:', err);
    }
  };

  const addNode = (type: string) => {
    const newNode = {
      id: `node-${Date.now()}`,
      type
    };
    setNodes([...nodes, newNode]);
  };

  const removeNode = (id: string) => {
    setNodes(nodes.filter(n => n.id !== id));
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
        <h2>加载中...</h2>
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
        gap: '20px'
      }}>
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
          ← 返回
        </button>
        <h1 style={{ margin: 0 }}>{currentProject.title}</h1>
      </div>

      {/* 主内容区 */}
      <div style={{
        flex: 1,
        padding: '20px',
        overflow: 'auto'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <h2 style={{ marginTop: 0 }}>卡片式工作流系统</h2>

          {/* 节点按钮 */}
          <div style={{
            display: 'flex',
            gap: '10px',
            marginBottom: '20px',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => addNode('script')}
              style={{
                padding: '10px 20px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              📝 剧本
            </button>
            <button
              onClick={() => addNode('prompt')}
              style={{
                padding: '10px 20px',
                background: '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              ✨ 提示词
            </button>
            <button
              onClick={() => addNode('storyboard')}
              style={{
                padding: '10px 20px',
                background: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              📸 分镜
            </button>
            <button
              onClick={() => addNode('image')}
              style={{
                padding: '10px 20px',
                background: '#8b5cf6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🖼️ 图片
            </button>
            <button
              onClick={() => addNode('video')}
              style={{
                padding: '10px 20px',
                background: '#ec4899',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🎬 视频
            </button>
          </div>

          {/* 节点列表 */}
          {nodes.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              color: '#94a3b8'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📋</div>
              <h3>工作流为空</h3>
              <p>点击上方按钮添加节点</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {nodes.map((node, index) => (
                <div
                  key={node.id}
                  style={{
                    background: '#f8fafc',
                    border: '2px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}
                >
                  <div style={{
                    width: '36px',
                    height: '36px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: '#667eea',
                    color: 'white',
                    borderRadius: '50%',
                    fontWeight: 'bold',
                    fontSize: '16px'
                  }}>
                    {index + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: '16px' }}>{node.type}</strong>
                    <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
                      节点ID: {node.id}
                    </div>
                  </div>
                  <button
                    onClick={() => removeNode(node.id)}
                    style={{
                      width: '32px',
                      height: '32px',
                      background: 'transparent',
                      border: 'none',
                      color: '#ef4444',
                      cursor: 'pointer',
                      borderRadius: '6px',
                      fontSize: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                    title="删除节点"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
