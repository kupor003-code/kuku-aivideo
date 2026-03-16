/**
 * 测试页面 - 用于诊断问题
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function TestPage() {
  const navigate = useNavigate();

  useEffect(() => {
    console.log('Test page loaded');
  }, []);

  return (
    <div style={{
      padding: '20px',
      background: '#f0f0f0',
      minHeight: '100vh',
    }}>
      <h1>测试页面</h1>
      <p>如果你能看到这个页面，说明路由工作正常</p>

      <button onClick={() => navigate('/projects')}>
        返回项目列表
      </button>

      <div style={{ marginTop: '20px' }}>
        <h2>测试组件</h2>
        <div style={{ background: 'white', padding: '20px', borderRadius: '8px' }}>
          <p>✓ 基本渲染正常</p>
        </div>
      </div>
    </div>
  );
}
