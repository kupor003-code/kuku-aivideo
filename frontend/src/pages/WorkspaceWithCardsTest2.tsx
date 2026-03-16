/**
 * 卡片式工作流 - 测试版本2（带项目加载）
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService } from '../services/projectService';
import type { Project } from '../types';

export default function WorkspaceWithCardsTest2() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);

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
      setError(err.message);
    }
  };

  if (error) {
    return (
      <div style={{ padding: '40px', background: '#f5f5f5', minHeight: '100vh' }}>
        <h1 style={{ color: 'red' }}>❌ 加载失败</h1>
        <p>错误信息: {error}</p>
        <button onClick={() => navigate('/projects')}>返回项目列表</button>
      </div>
    );
  }

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
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
          <h2>加载项目中...</h2>
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
        <div>
          <h1 style={{ margin: 0 }}>{currentProject.title}</h1>
          {currentProject.description && (
            <p style={{ margin: '5px 0 0 0', color: '#666' }}>{currentProject.description}</p>
          )}
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
        {/* 左侧：测试面板 */}
        <div style={{
          flex: 1,
          background: 'white',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h2 style={{ color: '#333' }}>✅ 项目加载成功！</h2>
          <p><strong>项目ID:</strong> {currentProject.id}</p>
          <p><strong>标题:</strong> {currentProject.title}</p>
          <p><strong>描述:</strong> {currentProject.description || '无'}</p>
          <p><strong>创建时间:</strong> {new Date(currentProject.created_at).toLocaleString()}</p>
        </div>

        {/* 右侧：占位 */}
        <div style={{
          flex: 1,
          background: 'white',
          borderRadius: '12px',
          padding: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <p style={{ color: '#666' }}>右侧面板占位</p>
        </div>
      </div>
    </div>
  );
}
