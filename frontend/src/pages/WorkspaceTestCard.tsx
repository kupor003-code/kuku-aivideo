/**
 * 超简单测试页面
 */

import { useParams } from 'react-router-dom';

export default function WorkspaceTestCard() {
  const { projectId } = useParams<{ projectId: string }>();

  return (
    <div style={{
      padding: '40px',
      background: '#f0f0f0',
      minHeight: '100vh'
    }}>
      <h1 style={{ color: '#333' }}>卡片工作流测试页面</h1>
      <p style={{ fontSize: '18px' }}>项目ID: {projectId}</p>
      <div style={{
        marginTop: '20px',
        padding: '20px',
        background: 'white',
        borderRadius: '8px'
      }}>
        <p style={{ color: 'green', fontSize: '16px' }}>✅ 如果你看到这个页面，说明路由正常工作！</p>
      </div>
    </div>
  );
}
