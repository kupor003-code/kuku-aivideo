/*Video节点组件*/
import { useState } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Video, Download, Film, ChevronDown, ChevronUp, Play, Edit, RotateCcw } from 'lucide-react';
import './VideoNode.css';

interface VideoNodeData {
  label?: string;
  total_videos?: number;
  estimated_time?: string;
  video_url?: string;
  thumbnail_url?: string;
  status?: string;
  progress?: number;
  video_urls?: Array<{
    id: string;
    url: string;
    thumbnail?: string;
  }>;
  projectId?: string;
  resolution?: string;
  duration?: number;
  fps?: number;
  style_strength?: string;
}

export default function VideoNode({ data, selected }: NodeProps) {
  const nodeData = data as VideoNodeData;
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeVideoIndex, setActiveVideoIndex] = useState(0);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleDownload = (videoUrl?: string) => {
    const url = videoUrl || nodeData.video_url || (nodeData.video_urls && nodeData.video_urls[0]?.url);
    if (url) {
      const a = document.createElement('a');
      a.href = url;
      a.download = `video_${Date.now()}.mp4`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const handleDownloadAllVideos = () => {
    if (!nodeData.video_urls || nodeData.video_urls.length === 0) return;
    nodeData.video_urls.forEach((video, index) => {
      const a = document.createElement('a');
      a.href = video.url;
      a.download = `video_${index + 1}_${video.id}.mp4`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
  };

  const totalVideos = nodeData.total_videos || 0;
  const estimatedTime = nodeData.estimated_time || '';
  const hasVideos = nodeData.video_urls && nodeData.video_urls.length > 0;
  const hasVideo = nodeData.video_url && nodeData.video_url.length > 0;
  const currentVideo = hasVideos ? nodeData.video_urls![activeVideoIndex] : null;

  return (
    <div className={`video-node ${selected ? 'selected' : ''}`}>
      {/* 输入连接点 */}
      <Handle type="target" position={Position.Top} className="node-handle" />

      {/* 节点头部 */}
      <div className="node-header" onClick={toggleExpand} style={{ cursor: 'pointer' }}>
        <div className="node-icon">
          <Video size={16} />
        </div>
        <div className="node-title">
          <span className="node-type">{nodeData.label || '视频'}</span>
          {(hasVideo || hasVideos) && (
            <span className="video-count">{hasVideos ? nodeData.video_urls!.length : 1}个</span>
          )}
        </div>
        {(hasVideo || hasVideos) && (
          <div className="node-actions-header">
            <button 
              className="action-button" 
              title="下载当前视频" 
              onClick={(e) => { 
                e.stopPropagation(); 
                handleDownload(currentVideo?.url); 
              }}
            >
              <Download size={14} />
            </button>
          </div>
        )}
        <button className="node-expand" onClick={(e) => { e.stopPropagation(); toggleExpand(); }}>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* 节点内容 */}
      <div className="node-content">
        {hasVideo ? (
          <div className="preview-section">
            <div className="video-preview">
              <video
                src={nodeData.video_url}
                poster={nodeData.thumbnail_url}
                controls
                className="video-player"
              />
            </div>
            <div className="video-controls">
              <div className="video-info">1 / 1</div>
              <button 
                className="action-button"
                onClick={() => handleDownload(nodeData.video_url)}
                title="下载视频"
              >
                <Download size={12} />
              </button>
            </div>
          </div>
        ) : hasVideos ? (
          <div className="preview-section">
            <div className="video-preview">
              <video
                key={nodeData.video_urls![activeVideoIndex].id}
                src={nodeData.video_urls![activeVideoIndex].url}
                controls
                className="video-player"
              />
            </div>
            <div className="video-controls">
              <div className="video-info">
                {activeVideoIndex + 1} / {nodeData.video_urls!.length}
              </div>
              <div className="video-nav">
                <button
                  className="nav-btn"
                  onClick={() => setActiveVideoIndex(Math.max(0, activeVideoIndex - 1))}
                  disabled={activeVideoIndex === 0}
                  title="上一个"
                >
                  ◀
                </button>
                <button
                  className="nav-btn"
                  onClick={() => setActiveVideoIndex(Math.min(nodeData.video_urls!.length - 1, activeVideoIndex + 1))}
                  disabled={activeVideoIndex === nodeData.video_urls!.length - 1}
                  title="下一个"
                >
                  ▶
                </button>
              </div>
              <button 
                className="action-button"
                onClick={() => handleDownload(nodeData.video_urls![activeVideoIndex].url)}
                title="下载当前视频"
              >
                <Download size={12} />
              </button>
            </div>
          </div>
        ) : nodeData.status === 'generating' ? (
          <div className="generating-state">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${nodeData.progress || 50}%` }}
              />
            </div>
            <p>生成中... {nodeData.progress || 50}%</p>
          </div>
        ) : totalVideos > 0 ? (
          <div className="empty-state">
            <Film size={24} className="empty-icon" />
            <p>{totalVideos} 个视频片段</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>
              预计时间：{estimatedTime}
            </p>
          </div>
        ) : (
          <div className="empty-state">
            <Video size={24} className="empty-icon" />
            <p>等待生成视频...</p>
          </div>
        )}

        {/* 展开后的详细内容 */}
        {isExpanded && (
          <div className="node-expanded-content">
            {/* 视频参数 */}
            {(nodeData.resolution || nodeData.duration || nodeData.fps || nodeData.style_strength) && (
              <div className="video-params">
                <h4 className="section-title">视频参数</h4>
                {nodeData.resolution && (
                  <div className="param-item">
                    <span className="param-label">分辨率：</span>
                    <span className="param-value">{nodeData.resolution}</span>
                  </div>
                )}
                {nodeData.duration && (
                  <div className="param-item">
                    <span className="param-label">时长：</span>
                    <span className="param-value">{nodeData.duration}秒/片段</span>
                  </div>
                )}
                {nodeData.fps && (
                  <div className="param-item">
                    <span className="param-label">帧率：</span>
                    <span className="param-value">{nodeData.fps} fps</span>
                  </div>
                )}
                {nodeData.style_strength && (
                  <div className="param-item">
                    <span className="param-label">风格强度：</span>
                    <span className="param-value">{nodeData.style_strength}</span>
                  </div>
                )}
              </div>
            )}

            {/* 视频列表 */}
            {hasVideos && nodeData.video_urls && nodeData.video_urls.length > 1 && (
              <div className="video-list">
                <h4 className="section-title">视频列表 ({nodeData.video_urls.length})</h4>
                <div className="video-items">
                  {nodeData.video_urls.map((video, idx) => (
                    <div key={video.id} className="video-item">
                      <span className="video-number">#{idx + 1}</span>
                      <button
                        className="video-play-btn"
                        onClick={() => window.open(video.url, '_blank')}
                      >
                        <Play size={12} />
                        播放
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="node-actions">
              {(hasVideo || hasVideos) && (
                <>
                  <button 
                    className="action-btn primary" 
                    onClick={() => handleDownload(currentVideo?.url)}
                  >
                    <Download size={14} />
                    下载当前
                  </button>
                  {hasVideos && (
                    <button 
                      className="action-btn primary" 
                      onClick={handleDownloadAllVideos}
                    >
                      <Download size={14} />
                      全部下载
                    </button>
                  )}
                </>
              )}
              <button className="action-btn secondary">
                <Edit size={14} />
                调整参数
              </button>
              {(hasVideo || hasVideos) && (
                <button className="action-btn secondary">
                  <RotateCcw size={14} />
                  重新生成
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 节点状态 */}
      <div className="node-status">
        {nodeData.status === 'generating' && (
          <span className="status-badge generating">
            <span className="status-dot"></span>
            生成中
          </span>
        )}
        {nodeData.status === 'completed' && (
          <span className="status-badge completed">
            <span className="status-dot"></span>
            已完成
          </span>
        )}
        {nodeData.status === 'failed' && (
          <span className="status-badge failed">
            <span className="status-dot"></span>
            失败
          </span>
        )}
        {!nodeData.status && totalVideos > 0 && (
          <span className="status-badge generating">
            <span className="status-dot"></span>
            生成中
          </span>
        )}
      </div>

      {/* 输出连接点 */}
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
}
