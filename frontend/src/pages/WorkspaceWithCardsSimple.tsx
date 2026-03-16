/**
 * 卡片式工作流 - 简化测试版
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function WorkspaceWithCardsSimple() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [input, setInput] = useState('');

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
        <h1 style={{ margin: 0 }}>卡片工作流测试 (项目ID: {projectId})</h1>
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
          padding: '20px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h2 style={{ color: '#333' }}>测试面板</h2>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="测试输入..."
            style={{
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              marginTop: '10px'
            }}
          />
          <p style={{ color: 'green', marginTop: '20px' }}>
            ✅ 输入框工作正常！你输入了: {input}
          </p>
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
