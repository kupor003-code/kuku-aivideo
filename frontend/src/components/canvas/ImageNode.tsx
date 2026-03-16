import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import './ImageNode.css';

export default function ImageNode({ data, selected }: NodeProps) {
  return (
    <div className={`workflow-node image-node ${selected ? 'selected' : ''} ${data.status || 'pending'}`}>
      <Handle type="target" position={Position.Top} />

      <div className="node-header">
        <span className="node-icon">🖼️</span>
        <span className="node-title">生成图片</span>
      </div>

      <div className="node-content">
        {data.result ? (
          <div className="node-result">
            {data.result.images && data.result.images.length > 0 ? (
              <div className="image-grid">
                {data.result.images.map((img: any, idx: number) => (
                  <img key={idx} src={img.url} alt={`Generated ${idx}`} />
                ))}
              </div>
            ) : (
              <div className="result-info">
                已生成 {data.result.count || 0} 张图片
              </div>
            )}
            <button className="view-btn" onClick={() => data.onView?.(data)}>
              查看详情
            </button>
          </div>
        ) : (
          <div className="node-placeholder">
            等待提示词输入...
          </div>
        )}
      </div>

      <div className="node-status">
        {data.status === 'running' && <span className="status-running">生成中...</span>}
        {data.status === 'completed' && <span className="status-completed">✓ 已完成</span>}
        {data.status === 'error' && <span className="status-error">❌ 失败</span>}
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
