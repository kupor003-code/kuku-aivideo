/**
 * 简化版 Workspace - 用于测试
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function WorkspaceSimple() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('WorkspaceSimple loaded, projectId:', projectId);
    setTimeout(() => setLoading(false), 500);
  }, [projectId]);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div style={{
      padding: '20px',
      minHeight: '100vh',
      background: '#f5f5f5',
    }}>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => navigate('/projects')}>
          ← 返回项目列表
        </button>
      </div>

      <h1>工作区（简化版）</h1>
      <p>项目ID: {projectId}</p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginTop: '20px',
      }}>
        <div style={{
          background: 'white',
          padding: '20px',
          borderRadius: '8px',
          minHeight: '400px',
        }}>
          <h2>💬 AI 对话区</h2>
          <p>对话功能将在完整版本中实现</p>
        </div>

        <div style={{
          background: 'white',
          padding: '20px',
          borderRadius: '8px',
          minHeight: '400px',
        }}>
          <h2>🎨 工作流画布</h2>
          <p>画布功能将在完整版本中实现</p>
        </div>
      </div>
    </div>
  );
}
