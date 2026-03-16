/**
 * 卡片式工作流 - 测试版本3（带 WorkflowCardSimple 组件）
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService } from '../services/projectService';
import type { Project } from '../types';
import WorkflowCardSimple, { WorkflowNode, WorkflowNodeType } from '../components/WorkflowCardSimple';

export default function WorkspaceWithCardsTest3() {
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

  // 执行节点（模拟）
  const handleNodeExecute = async (nodeId: string, nodeType: WorkflowNodeType) => {
    console.log(`执行节点: ${nodeId} (${nodeType})`);

    // 模拟执行延迟
    await new Promise(resolve => setTimeout(resolve, 2000));

    return {
      message: `✅ ${nodeType} 节点执行成功！`,
      timestamp: new Date().toISOString()
    };
  };

  // 工作流完成（模拟）
  const handleWorkflowComplete = async (nodes: WorkflowNode[]) => {
    console.log('工作流执行完成', { nodes });
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

      {/* 主内容区 - WorkflowCardSimple */}
      <div style={{
        flex: 1,
        padding: '20px',
        overflow: 'hidden'
      }}>
        <WorkflowCardSimple
          projectId={projectId}
          onNodeExecute={handleNodeExecute}
          onWorkflowComplete={handleWorkflowComplete}
        />
      </div>
    </div>
  );
}
