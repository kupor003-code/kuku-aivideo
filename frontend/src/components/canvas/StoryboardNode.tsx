/*Storyboard节点组件 - V5：支持剧本输入和镜头选择控制*/
import { useState, useEffect } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Image, Film, ChevronDown, ChevronUp, Sparkles, Edit, RotateCcw, Download, Wand2, Pause, Play, AlertCircle, FileText, Check } from 'lucide-react';
import { generationEventService } from '../../services/generationEventService';
import './StoryboardNode.css';

interface Shot {
  id: string;
  shot_number: number;
  shot_description: string;
  prompt?: string;
  status?: string;  // pending | generating | paused | completed | failed
  progress?: number;
  error?: string;
  image_id?: string;
  images?: Array<{
    id: string;
    url: string;
    type: 'start' | 'middle' | 'end'; // 首帧、中间帧、尾帧
  }>;
  generation_info?: {
    num_images: number;
    seed?: number;
    generated_at: string;
  };
}

interface StoryboardNodeData {
  label?: string;
  total_scenes?: number;
  total_shots?: number;
  shots?: Shot[];
  images?: Array<{
    id: string;
    url: string;
  }>;
  prompt_version_id?: string;
  status?: string;
  prompt?: string;
  scenes?: Array<{
    scene_number: number;
    description: string;
    shots: Array<{
      shot_number: number;
      description: string;
      camera_angle: string;
      camera_movement: string;
    }>;
  }>;
  projectId?: string;
}

export default function StoryboardNode({ data, selected }: NodeProps) {
  const nodeData = data as StoryboardNodeData;
  const [isExpanded, setIsExpanded] = useState(false);
  const [showGenerateConfirm, setShowGenerateConfirm] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [currentShots, setCurrentShots] = useState<Shot[]>(nodeData.shots || []);
  const [currentImages, setCurrentImages] = useState<Array<{ id: string; url: string }> | undefined>(nodeData.images);

  // 剧本输入相关状态
  const [showScriptInput, setShowScriptInput] = useState(false);
  const [scriptText, setScriptText] = useState('');
  const [isProcessingScript, setIsProcessingScript] = useState(false);

  const totalScenes = nodeData.total_scenes || 0;
  const totalShots = nodeData.total_shots || 0;
  const hasImages = currentImages && currentImages.length > 0;

  // 监听来自对话框的生成完成事件
  useEffect(() => {
    const handleImageGenerated = (event: any) => {
      const detail = event.detail;
      // 添加生成的图片到节点数据
      setCurrentImages(prev => prev ? [...prev, ...detail.imageUrls.map((url: string, idx: number) => ({
        id: detail.imageIds[idx],
        url
      }))] : detail.imageUrls.map((url: string, idx: number) => ({
        id: detail.imageIds[idx],
        url
      })));

      // 更新对应镜头的生成信息
      setCurrentShots(prev =>
        prev.map(shot =>
          shot.shot_number === detail.shotNumber
            ? {
                ...shot,
                image_id: detail.imageIds[0],
                status: 'completed',
                generation_info: {
                  num_images: detail.imageIds.length,
                  seed: detail.seed,
                  generated_at: new Date().toISOString(),
                },
              }
            : shot
        )
      );
    };

    const handleVideoGenerated = (event: any) => {
      const detail = event.detail;
      // 处理视频生成完成
      console.log('视频已生成:', detail);
    };

    window.addEventListener('shot-image-generated', handleImageGenerated);
    window.addEventListener('shot-video-generated', handleVideoGenerated);

    return () => {
      window.removeEventListener('shot-image-generated', handleImageGenerated);
      window.removeEventListener('shot-video-generated', handleVideoGenerated);
    };
  }, []);

  // 订阅生成进度事件
  useEffect(() => {
    const unsubscribeProgress = generationEventService.subscribe('progress', (progress: any) => {
      // 更新对应镜头的进度
      setCurrentShots(prev =>
        prev.map(shot =>
          shot.id === progress.shot_id
            ? {
                ...shot,
                status: progress.status,
                progress: progress.progress,
                error: progress.error,
              }
            : shot
        )
      );
    });

    return () => {
      unsubscribeProgress();
    };
  }, []);

  // 处理单个镜头生成
  const handleGenerateShot = async (shot: Shot, frameType: 'start' | 'end' | 'both' = 'both') => {
    try {
      // 根据帧类型确定生成数量
      const n = frameType === 'both' ? 2 : 1;

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/storyboard/shots/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_id: nodeData.projectId,
            shot_number: shot.shot_number,
            shot_description: shot.shot_description,
            prompt: shot.prompt || nodeData.prompt,
            size: '1024*1024',
            n: n,
            frame_type: frameType, // 传递帧类型给后端
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log('镜头生成任务已启动:', result.shot_gen_id);
        // 可以在这里添加实时监听逻辑
      }
    } catch (error) {
      console.error('启动镜头生成失败:', error);
      alert('启动生成失败，请重试');
    }
  };

  // 暂停镜头生成
  const handlePauseShot = async (shot: Shot) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/storyboard/shots/${shot.id}/pause`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );
      
      if (response.ok) {
        console.log('镜头已暂停');
        // 刷新状态
      }
    } catch (error) {
      console.error('暂停失败:', error);
    }
  };

  // 继续镜头生成
  const handleResumeShot = async (shot: Shot) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/storyboard/shots/${shot.id}/resume`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );
      
      if (response.ok) {
        console.log('镜头已继续');
        // 刷新状态
      }
    } catch (error) {
      console.error('继续失败:', error);
    }
  };

  const handleGenerateImages = async () => {
    setShowGenerateConfirm(false);
    setIsGenerating(true);

    try {
      // 获取项目配置
      const configResponse = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/projects/${nodeData.projectId}/config`
      );
      const configData = await configResponse.json();
      const config = configData.config;

      // 检查是否需要用户确认
      if (config.agent_config.require_user_confirm) {
        setShowGenerateConfirm(true);
        return;
      }

      // 调用图片生成API
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/storyboard/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_id: nodeData.projectId,
            prompt: nodeData.prompt || '',
            size: '1024*1024',
            n: config.image_generation.default_images_per_scene || 3,
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log('图片生成任务已创建:', result.task_id);
      }
    } catch (error) {
      console.error('生成图片失败:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadImage = () => {
    const currentImage = currentImages?.[activeImageIndex];
    if (currentImage) {
      const a = document.createElement('a');
      a.href = currentImage.url;
      a.download = `storyboard_${currentImage.id}.png`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const handleDownloadAllImages = () => {
    if (!currentImages || currentImages.length === 0) return;
    currentImages.forEach((image, index) => {
      const a = document.createElement('a');
      a.href = image.url;
      a.download = `storyboard_${index + 1}_${image.id}.png`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
  };

  const handleGenerateVideoFromImage = () => {
    const currentImage = currentImages?.[activeImageIndex];
    if (!currentImage) {
      alert('请先生成图片，然后再生成视频');
      return;
    }

    if (!nodeData.projectId) {
      alert('项目ID缺失');
      return;
    }

    // 触发事件，让上层组件处理视频生成
    window.dispatchEvent(new CustomEvent('generate-video-from-image', {
      detail: {
        projectId: nodeData.projectId,
        imageUrl: currentImage.url,
        imageId: currentImage.id,
        prompt: nodeData.prompt || '生成视频',
      }
    }));
  };

  // 处理剧本提交
  const handleScriptSubmit = async () => {
    if (!scriptText.trim()) {
      alert('请输入剧本内容');
      return;
    }

    if (!nodeData.projectId) {
      alert('项目ID缺失');
      return;
    }

    setIsProcessingScript(true);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/script-storyboard/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_id: nodeData.projectId,
            script_text: scriptText,
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}`);

        // 更新镜头数据
        if (result.scenes && result.scenes.length > 0) {
          const newShots: Shot[] = [];
          result.scenes.forEach((scene: any) => {
            scene.shots.forEach((shot: any, idx: number) => {
              newShots.push({
                id: `shot_${scene.scene_number}_${idx}`,
                shot_number: shot.shot_number,
                shot_description: shot.description,
                prompt: shot.chinese_prompt || shot.english_prompt || '',
                status: 'pending',
              });
            });
          });

          setCurrentShots(newShots);
        }

        setShowScriptInput(false);
        setScriptText('');
      } else {
        const error = await response.json();
        alert(`生成失败: ${error.detail}`);
      }
    } catch (error) {
      console.error('生成剧本分镜失败:', error);
      alert('生成失败，请检查服务是否正常运行');
    } finally {
      setIsProcessingScript(false);
    }
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`storyboard-node ${selected ? 'selected' : ''}`}>
      {/* 输入连接点 */}
      <Handle type="target" position={Position.Top} className="node-handle" />

      {/* 节点头部 */}
      <div className="node-header" onClick={toggleExpand} style={{ cursor: 'pointer' }}>
        <div className="node-icon">
          <Image size={16} />
        </div>
        <div className="node-title">
          <span className="node-type">{nodeData.label || '分镜'}</span>
          <span className="node-count">{totalScenes} 场景</span>
        </div>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <button
            className="node-action-btn"
            onClick={(e) => { e.stopPropagation(); setShowScriptInput(true); }}
            title="使用剧本生成分镜"
            style={{
              background: 'var(--color-primary-soft)',
              border: '1px solid var(--color-primary)',
              borderRadius: '4px',
              padding: '4px 8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12px',
              color: 'var(--color-primary)',
            }}
          >
            <FileText size={12} />
            剧本
          </button>
          <button className="node-expand" onClick={(e) => { e.stopPropagation(); toggleExpand(); }}>
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* 节点内容 */}
      <div className="node-content">
        {hasImages ? (
          <div className="preview-section">
            <div className="image-preview">
              <img src={currentImages![activeImageIndex].url} alt="分镜预览" />
            </div>
            <div className="image-controls">
              <div className="image-counter">
                {activeImageIndex + 1} / {currentImages!.length}
              </div>
              <div className="image-nav">
                <button
                  className="nav-btn"
                  onClick={() => setActiveImageIndex(Math.max(0, activeImageIndex - 1))}
                  disabled={activeImageIndex === 0}
                  title="上一张"
                >
                  ◀
                </button>
                <button
                  className="nav-btn"
                  onClick={() => setActiveImageIndex(Math.min(currentImages!.length - 1, activeImageIndex + 1))}
                  disabled={activeImageIndex === currentImages!.length - 1}
                  title="下一张"
                >
                  ▶
                </button>
              </div>
            </div>
          </div>
        ) : totalScenes > 0 || totalShots > 0 ? (
          <div className="empty-state">
            <Film size={24} className="empty-icon" />
            <p>{totalScenes} 个场景 · {totalShots} 个镜头</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>
              分镜已生成
            </p>
          </div>
        ) : (
          <div className="empty-state">
            <Image size={24} className="empty-icon" />
            <p>生成中...</p>
          </div>
        )}

        {/* 展开后的详细内容 */}
        {isExpanded && (
          <div className="node-expanded-content">
            {/* 镜头生成列表 */}
            {currentShots && currentShots.length > 0 && (
              <div className="shots-generation-list">
                <h4 className="section-title">
                  镜头列表 ({currentShots.length})
                  <span style={{ fontSize: '12px', fontWeight: 'normal', color: 'var(--color-text-tertiary)' }}>
                    - 点击选择镜头进行操作
                  </span>
                </h4>
                {currentShots.map((shot) => {
                  const isSelected = selectedShotId === shot.id;
                  const hasImages = shot.images && shot.images.length > 0;

                  return (
                    <div
                      key={shot.id}
                      className={`shot-generation-item status-${shot.status || 'pending'} ${isSelected ? 'selected' : ''} clickable`}
                      onClick={() => setSelectedShotId(isSelected ? null : shot.id)}
                    >
                      <div className="shot-gen-header">
                        <span className="shot-gen-number">镜头 {shot.shot_number}</span>
                        <span className={`shot-gen-status status-${shot.status || 'pending'}`}>
                          {shot.status === 'generating' && '生成中'}
                          {shot.status === 'paused' && '已暂停'}
                          {shot.status === 'completed' && '✓'}
                          {shot.status === 'failed' && '✗'}
                          {!shot.status && '待生成'}
                        </span>
                      </div>

                      <div className="shot-gen-description">{shot.shot_description}</div>

                      {/* 显示已生成的图片 */}
                      {hasImages && (
                        <div className="shot-images-preview">
                          <div className="shot-images-label">已生成图片:</div>
                          <div className="shot-images-grid">
                            {shot.images!.map((img) => (
                              <div key={img.id} className="shot-image-item">
                                <img src={img.url} alt={`${img.type}帧`} />
                                <span className="shot-image-type">
                                  {img.type === 'start' && '首帧'}
                                  {img.type === 'middle' && '中间帧'}
                                  {img.type === 'end' && '尾帧'}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {shot.progress !== undefined && (shot.status === 'generating' || shot.status === 'paused') && (
                        <div className="progress-bar">
                          <div className="progress-fill" style={{ width: `${shot.progress}%` }}></div>
                        </div>
                      )}

                      {shot.error && (
                        <div className="shot-gen-error">
                          <AlertCircle size={12} />
                          {shot.error}
                        </div>
                      )}

                      {shot.generation_info && (
                        <div className="shot-generation-info">
                          <div className="generation-info-item">
                            <span className="generation-info-label">📊 生图数量:</span>
                            <span className="generation-info-value">{shot.generation_info.num_images} 张</span>
                          </div>
                          {shot.generation_info.seed !== undefined && (
                            <div className="generation-info-item">
                              <span className="generation-info-label">🌱 种子:</span>
                              <span className="generation-info-value">{shot.generation_info.seed}</span>
                            </div>
                          )}
                          <div className="generation-info-item">
                            <span className="generation-info-label">⏰ 生成时间:</span>
                            <span className="generation-info-value">
                              {new Date(shot.generation_info.generated_at).toLocaleString('zh-CN')}
                            </span>
                          </div>
                        </div>
                      )}

                      {/* 只在选中时显示操作按钮 */}
                      {isSelected && (
                        <div className="shot-gen-actions">
                          {shot.status === 'pending' && !hasImages && (
                            <>
                              <button
                                className="shot-btn generate"
                                onClick={(e) => { e.stopPropagation(); handleGenerateShot(shot, 'start'); }}
                                title="生成首帧"
                              >
                                <Sparkles size={12} />
                                首帧
                              </button>
                              <button
                                className="shot-btn generate"
                                onClick={(e) => { e.stopPropagation(); handleGenerateShot(shot, 'end'); }}
                                title="生成尾帧"
                              >
                                <Sparkles size={12} />
                                尾帧
                              </button>
                              <button
                                className="shot-btn generate"
                                onClick={(e) => { e.stopPropagation(); handleGenerateShot(shot, 'both'); }}
                                title="生成首尾帧"
                              >
                                <Sparkles size={12} />
                                首尾帧
                              </button>
                            </>
                          )}
                          {shot.status === 'generating' && (
                            <button
                              className="shot-btn pause"
                              onClick={(e) => { e.stopPropagation(); handlePauseShot(shot); }}
                              title="暂停生成"
                            >
                              <Pause size={12} />
                              暂停
                            </button>
                          )}
                          {shot.status === 'paused' && (
                            <button
                              className="shot-btn resume"
                              onClick={(e) => { e.stopPropagation(); handleResumeShot(shot); }}
                              title="继续生成"
                            >
                              <Play size={12} />
                              继续
                            </button>
                          )}
                          {hasImages && (
                            <span className="shot-gen-result">✓ 已生成</span>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* 操作按钮 */}
        <div className="node-actions">
          {!hasImages && totalScenes > 0 && (
            <button
              className="action-btn primary"
              onClick={handleGenerateImages}
              disabled={isGenerating}
            >
              <Sparkles size={14} />
              {isGenerating ? '生成中...' : '生成图片'}
            </button>
          )}
          {hasImages && (
            <>
              <button
                className="action-btn primary"
                onClick={handleGenerateVideoFromImage}
                title="从当前图片生成视频"
              >
                <Wand2 size={14} />
                生成视频
              </button>
              <button
                className="action-btn secondary"
                onClick={handleDownloadImage}
                title="下载当前图片"
              >
                <Download size={14} />
                下载图片
              </button>
              <button
                className="action-btn secondary"
                onClick={handleDownloadAllImages}
                title="下载所有图片"
              >
                <Download size={14} />
                全部下载
              </button>
            </>
          )}
          <button className="action-btn secondary">
            <Edit size={14} />
            编辑提示词
          </button>
          {hasImages && (
            <button className="action-btn secondary">
              <RotateCcw size={14} />
              重新生成
            </button>
          )}
        </div>

        {/* 确认对话框 */}
        {showGenerateConfirm && (
          <div className="confirm-dialog">
            <div className="confirm-content">
              <h4>确认生成图片</h4>
              <p>即将为 {totalScenes} 个场景生成图片</p>
              <p className="confirm-note">这将消耗API配额</p>
              <div className="confirm-actions">
                <button
                  className="btn btn-secondary"
                  onClick={() => setShowGenerateConfirm(false)}
                >
                  取消
                </button>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    setShowGenerateConfirm(false);
                    // 执行实际的生成逻辑
                    handleGenerateImages();
                  }}
                >
                  确认生成
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 剧本输入模态框 */}
        {showScriptInput && (
          <div className="modal-overlay" onClick={() => setShowScriptInput(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{
              background: 'var(--color-bg-primary)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px',
              padding: '20px',
              minWidth: '500px',
              maxWidth: '600px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ margin: 0, fontSize: '18px' }}>📝 剧本输入</h3>
                <button
                  onClick={() => setShowScriptInput(false)}
                  style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer' }}
                >
                  ×
                </button>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 500 }}>
                  请输入剧本内容
                </label>
                <textarea
                  value={scriptText}
                  onChange={(e) => setScriptText(e.target.value)}
                  placeholder="例如：
场景：现代办公室
时间：下午3点
人物：小李（程序员）
动作：小李正在写代码，突然接到电话，表情惊讶

或者直接描述：
一个男人在海边跑步，日出时分，阳光洒在海面上..."
                  style={{
                    width: '100%',
                    minHeight: '200px',
                    padding: '12px',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                    resize: 'vertical',
                  }}
                />
              </div>

              <div style={{
                padding: '12px',
                background: 'var(--color-bg-secondary)',
                borderRadius: '6px',
                marginBottom: '16px',
                fontSize: '13px',
              }}>
                <p style={{ margin: 0 }}>💡 支持自然语言或标准剧本格式</p>
              </div>

              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => setShowScriptInput(false)}
                  disabled={isProcessingScript}
                  style={{
                    padding: '8px 16px',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                    background: 'var(--color-bg-primary)',
                    cursor: isProcessingScript ? 'not-allowed' : 'pointer',
                  }}
                >
                  取消
                </button>
                <button
                  onClick={handleScriptSubmit}
                  disabled={isProcessingScript || !scriptText.trim()}
                  style={{
                    padding: '8px 16px',
                    border: 'none',
                    borderRadius: '6px',
                    background: isProcessingScript || !scriptText.trim()
                      ? 'var(--color-text-tertiary)'
                      : 'var(--color-primary)',
                    color: 'white',
                    cursor: isProcessingScript || !scriptText.trim() ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  {isProcessingScript ? (
                    <>
                      <div style={{
                        width: '14px',
                        height: '14px',
                        border: '2px solid white',
                        borderTop: '2px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                      }}></div>
                      生成中...
                    </>
                  ) : (
                    <>
                      <Check size={14} />
                      生成分镜
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 节点状态 */}
      <div className="node-status">
        {nodeData.status === 'generating' && (
          <span className="status-badge generating">生成中</span>
        )}
        {nodeData.status === 'completed' && (
          <span className="status-badge completed">已完成</span>
        )}
        {nodeData.status === 'failed' && (
          <span className="status-badge failed">失败</span>
        )}
        {!nodeData.status && totalScenes > 0 && (
          <span className="status-badge completed">已完成</span>
        )}
      </div>

      {/* 输出连接点 */}
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
}
