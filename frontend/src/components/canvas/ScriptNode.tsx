import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import './ScriptNode.css';

export default function ScriptNode({ data, selected }: NodeProps) {
  return (
    <div className={`custom-node script-node ${selected ? 'selected' : ''} ${data.status || 'pending'}`}>
      <Handle type="target" position={Position.Top} />

      <div className="node-header">
        <span className="node-icon">📝</span>
        <span className="node-title">剧本创作</span>
      </div>

      <div className="node-content">
        {data.result ? (
          <div className="node-result">
            <div className="result-preview">
              {data.result.content?.substring(0, 100)}...
            </div>
            <button className="view-btn" onClick={() => data.onView?.(data)}>
              查看完整剧本
            </button>
          </div>
        ) : (
          <div className="node-placeholder">
            等待输入...
          </div>
        )}
      </div>

      <div className="node-status">
        {data.status === 'running' && <span className="status-running">运行中...</span>}
        {data.status === 'completed' && <span className="status-completed">✓ 已完成</span>}
        {data.status === 'error' && <span className="status-error">❌ 失败</span>}
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
