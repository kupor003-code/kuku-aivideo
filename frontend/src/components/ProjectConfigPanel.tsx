/*项目配置面板组件*/
import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { projectConfigService, type ProjectConfig } from '../services/projectConfigService';
import './ProjectConfigPanel.css';

interface ProjectConfigPanelProps {
  projectId: string;
  onClose: () => void;
}

export default function ProjectConfigPanel({ projectId, onClose }: ProjectConfigPanelProps) {
  const [config, setConfig] = useState<ProjectConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadConfig();
  }, [projectId]);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const data = await projectConfigService.getConfig(projectId);
      setConfig(data);
    } catch (error) {
      console.error('Failed to load config:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;

    setIsSaving(true);
    try {
      await projectConfigService.updateConfig(projectId, config);
      onClose();
    } catch (error) {
      console.error('Failed to save config:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading || !config) {
    return <div className="config-panel-loading">加载中...</div>;
  }

  return (
    <div className="config-panel-overlay" onClick={onClose}>
      <div className="config-panel" onClick={(e) => e.stopPropagation()}>
        {/* 头部 */}
        <div className="config-panel-header">
          <h2>项目设置</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* 内容 */}
        <div className="config-panel-content">
          {/* 图片生成配置 */}
          <section className="config-section">
            <h3>📸 图片生成设置</h3>

            <div className="config-item">
              <label>
                <input
                  type="checkbox"
                  checked={config.image_generation.ai_recommend_images}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      image_generation: {
                        ...config.image_generation,
                        ai_recommend_images: e.target.checked,
                      },
                    })
                  }
                />
                AI智能推荐图片数量
              </label>
              <p className="config-item-desc">
                AI会根据场景复杂度自动推荐每个场景生成几张图片
              </p>
            </div>

            <div className="config-item">
              <label>默认每场景图片数：{config.image_generation.default_images_per_scene}张</label>
              <input
                type="range"
                min={config.image_generation.min_images}
                max={config.image_generation.max_images}
                value={config.image_generation.default_images_per_scene}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    image_generation: {
                      ...config.image_generation,
                      default_images_per_scene: parseInt(e.target.value),
                    },
                  })
                }
              />
              <div className="range-labels">
                <span>{config.image_generation.min_images}张</span>
                <span>{config.image_generation.max_images}张</span>
              </div>
            </div>

            <div className="config-item">
              <label>
                <input
                  type="checkbox"
                  checked={config.image_generation.allow_manual_adjust}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      image_generation: {
                        ...config.image_generation,
                        allow_manual_adjust: e.target.checked,
                      },
                    })
                  }
                />
                允许手动调整每场景的图片数量
              </label>
            </div>
          </section>

          {/* 视频生成配置 */}
          <section className="config-section">
            <h3>🎬 视频生成设置</h3>

            <div className="config-item">
              <label>分辨率</label>
              <select
                value={config.video_generation.resolution}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    video_generation: {
                      ...config.video_generation,
                      resolution: e.target.value as '720p' | '1080p' | '4K',
                    },
                  })
                }
              >
                <option value="720p">720p (HD)</option>
                <option value="1080p">1080p (Full HD)</option>
                <option value="4K">4K (Ultra HD)</option>
              </select>
            </div>

            <div className="config-item">
              <label>时长：{config.video_generation.duration}秒/片段</label>
              <select
                value={config.video_generation.duration}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    video_generation: {
                      ...config.video_generation,
                      duration: parseInt(e.target.value),
                    },
                  })
                }
              >
                <option value={2}>2秒</option>
                <option value={3}>3秒</option>
                <option value={5}>5秒</option>
                <option value={10}>10秒</option>
              </select>
            </div>

            <div className="config-item">
              <label>帧率</label>
              <select
                value={config.video_generation.fps}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    video_generation: {
                      ...config.video_generation,
                      fps: parseInt(e.target.value) as 24 | 30 | 60,
                    },
                  })
                }
              >
                <option value={24}>24 fps (电影标准)</option>
                <option value={30}>30 fps (流畅)</option>
                <option value={60}>60 fps (超流畅)</option>
              </select>
            </div>

            <div className="config-item">
              <label>风格强度</label>
              <select
                value={config.video_generation.style_strength}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    video_generation: {
                      ...config.video_generation,
                      style_strength: e.target.value as 'low' | 'medium' | 'high',
                    },
                  })
                }
              >
                <option value="low">低 - 更多创意空间</option>
                <option value="medium">中 - 平衡</option>
                <option value="high">高 - 严格遵循提示词</option>
              </select>
            </div>
          </section>

          {/* Agent配置 */}
          <section className="config-section">
            <h3>🤖 AI Agent设置</h3>

            <div className="config-item">
              <label>
                <input
                  type="checkbox"
                  checked={config.agent_config.enable_auto_generate}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      agent_config: {
                        ...config.agent_config,
                        enable_auto_generate: e.target.checked,
                      },
                    })
                  }
                />
                自动执行完整流程
              </label>
              <p className="config-item-desc">
                开启后，AI会自动执行所有步骤，无需手动确认（会消耗更多token）
              </p>
            </div>

            <div className="config-item">
              <label>
                <input
                  type="checkbox"
                  checked={config.agent_config.require_user_confirm}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      agent_config: {
                        ...config.agent_config,
                        require_user_confirm: e.target.checked,
                      },
                    })
                  }
                />
                每步需要用户确认
              </label>
              <p className="config-item-desc">
                生成图片和视频前需要你点击确认按钮
              </p>
            </div>
          </section>
        </div>

        {/* 底部按钮 */}
        <div className="config-panel-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            取消
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
            {isSaving ? '保存中...' : '保存设置'}
          </button>
        </div>
      </div>
    </div>
  );
}
