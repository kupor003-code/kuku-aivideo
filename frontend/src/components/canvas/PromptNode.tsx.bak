/*Prompt节点组件*/
import { useState } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { FileText, Sparkles, ChevronDown, ChevronUp, Copy, Edit } from 'lucide-react';
import './PromptNode.css';

interface PromptNodeData {
  content: string;
  version: number;
  source: string;
  agent_type?: string;
  label?: string;
  creative_concept?: {
    theme?: string;
    genre?: string;
    mood?: string;
    target_audience?: string;
  };
}

export default function PromptNode({ data, selected }: NodeProps) {
  const nodeData = data as PromptNodeData;
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(nodeData.content);
  };

  return (
    <div className={`prompt-node ${selected ? 'selected' : ''}`}>
      {/* 输入连接点 */}
      <Handle type="target" position={Position.Top} className="node-handle" />

      {/* 节点头部 */}
      <div className="node-header" onClick={toggleExpand} style={{ cursor: 'pointer' }}>
        <div className="node-icon">
          <FileText size={16} />
        </div>
        <div className="node-title">
          <span className="node-type">{nodeData.label || 'Prompt'}</span>
          <span className="node-version">v{nodeData.version}</span>
        </div>
        <button className="node-expand" onClick={(e) => { e.stopPropagation(); toggleExpand(); }}>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* 节点内容 */}
      <div className="node-content">
        <p className={`prompt-text ${isExpanded ? 'expanded' : ''}`}>{nodeData.content}</p>

        {/* 展开后的详细内容 */}
        {isExpanded && (
          <div className="node-expanded-content">
            {/* 创意概念 */}
            {nodeData.creative_concept && (
              <div className="creative-concept">
                <h4 className="section-title">创意概念</h4>
                {nodeData.creative_concept.theme && (
                  <div className="concept-item">
                    <span className="concept-label">主题：</span>
                    <span className="concept-value">{nodeData.creative_concept.theme}</span>
                  </div>
                )}
                {nodeData.creative_concept.genre && (
                  <div className="concept-item">
                    <span className="concept-label">类型：</span>
                    <span className="concept-value">{nodeData.creative_concept.genre}</span>
                  </div>
                )}
                {nodeData.creative_concept.mood && (
                  <div className="concept-item">
                    <span className="concept-label">氛围：</span>
                    <span className="concept-value">{nodeData.creative_concept.mood}</span>
                  </div>
                )}
                {nodeData.creative_concept.target_audience && (
                  <div className="concept-item">
                    <span className="concept-label">受众：</span>
                    <span className="concept-value">{nodeData.creative_concept.target_audience}</span>
                  </div>
                )}
              </div>
            )}

            {/* 操作按钮 */}
            <div className="node-actions">
              <button className="action-btn secondary" onClick={handleCopy}>
                <Copy size={14} />
                复制
              </button>
              <button className="action-btn secondary">
                <Edit size={14} />
                编辑
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 节点元数据 */}
      <div className="node-meta">
        {nodeData.source === 'ai_director' && (
          <span className="meta-badge ai-director">
            <Sparkles size={12} />
            AI导演
          </span>
        )}
        {nodeData.source === 'ai_producer' && (
          <span className="meta-badge ai-producer">
            <Sparkles size={12} />
            AI制片
          </span>
        )}
        {nodeData.source === 'user' && (
          <span className="meta-badge user">用户输入</span>
        )}
      </div>

      {/* 输出连接点 */}
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
}
