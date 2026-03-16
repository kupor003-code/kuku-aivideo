import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { projectService } from '../services/projectService';
import { demoCaseService } from '../services/demoCaseService';
import type { Project } from '../types';
import './ProjectList.css';

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectTitle, setNewProjectTitle] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');

  // 演示案例状态
  const [demoCases, setDemoCases] = useState<any[]>([]);
  const [latestDemoCase, setLatestDemoCase] = useState<any>(null);
  const [showDemoDetailModal, setShowDemoDetailModal] = useState(false);
  const [selectedDemoCase, setSelectedDemoCase] = useState<any>(null);

  // 构建完整的静态文件URL
  const getStaticUrl = (path: string) => {
    if (!path) return '';
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    // 使用后端服务器地址（与API_URL相同）
    const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    const baseUrl = apiBaseUrl.replace('/api/v1', '');
    return `${baseUrl}${path}`;
  };

  useEffect(() => {
    loadProjects();
    loadDemoCases();
  }, []);

  const loadDemoCases = async () => {
    try {
      // 加载最新的演示案例
      const latest = await demoCaseService.getLatestDemoCase();
      console.log('✅ 加载演示案例成功:', latest);

      // 调试：检查第一个分镜的URL
      if (latest && latest.fragments && latest.fragments.length > 0) {
        const firstFrag = latest.fragments[0];
        console.log('📹 第一个分镜数据:', {
          imageUrl: firstFrag.imageNode?.output?.url,
          videoUrl: firstFrag.videoNode?.output,
          hasImage: firstFrag.imageNode?.status === 'completed',
          hasVideo: firstFrag.videoNode?.status === 'completed'
        });

        // 测试URL构建
        const fullImageUrl = getStaticUrl(firstFrag.imageNode?.output?.url);
        const fullVideoUrl = getStaticUrl(firstFrag.videoNode?.output);
        console.log('🔗 构建的完整URL:', {
          image: fullImageUrl,
          video: fullVideoUrl
        });
      }

      setLatestDemoCase(latest);

      // 加载演示案例列表（最多3个）
      const cases = await demoCaseService.getDemoCases(0, 3);
      setDemoCases(cases);
    } catch (error) {
      console.log('❌ 加载演示案例失败:', error);
    }
  };

  const loadProjects = async () => {
    try {
      setIsLoading(true);
      const data = await projectService.list();
      setProjects(data);
    } catch (error) {
      console.error('加载项目失败:', error);
      alert('加载项目失败，请检查后端是否正常运行');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectTitle.trim()) {
      alert('请输入项目标题');
      return;
    }

    try {
      const newProject = await projectService.create({
        title: newProjectTitle,
        description: newProjectDescription || undefined,
      });
      setProjects([newProject, ...projects]);
      setNewProjectTitle('');
      setNewProjectDescription('');
      setShowCreateModal(false);
    } catch (error) {
      console.error('创建项目失败:', error);
      alert('创建项目失败，请检查后端是否正常运行');
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('确定要删除这个项目吗？相关的会话、提示词、分镜图片和视频任务都会被删除。')) {
      return;
    }

    try {
      await projectService.delete(projectId);
      setProjects(projects.filter((p) => p.id !== projectId));
    } catch (error) {
      console.error('删除项目失败:', error);
      alert('删除项目失败');
    }
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      draft: '草稿',
      in_progress: '进行中',
      completed: '已完成',
      archived: '已归档',
    };
    return statusMap[status] || status;
  };

  const getStatusClass = (status: string) => {
    return `status-badge status-${status}`;
  };

  const getStatusValue = (status: string): string => {
    return status;
  };

  const handleViewDemoCase = async (demoCase: any) => {
    setSelectedDemoCase(demoCase);
    setShowDemoDetailModal(true);
  };

  if (isLoading) {
    return (
      <div className="project-list-page">
        <div className="loading-state">加载中...</div>
      </div>
    );
  }

  return (
    <div className="project-list-page">
      {/* 演示案例展示区域 */}
      {latestDemoCase && (() => {
        console.log('🎨 渲染演示案例，分镜数量:', latestDemoCase.fragments?.length);
        if (latestDemoCase.fragments?.length > 0) {
          console.log('📋 第一个分镜:', latestDemoCase.fragments[0]);
        }
        return null;
      })()}
      {latestDemoCase && (
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '32px',
          color: 'white',
          boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)'
        }}>
          <div style={{ marginBottom: '16px' }}>
            <h2 style={{ margin: '0 0 8px 0', fontSize: '1.5rem' }}>
              🌟 演示案例展示
            </h2>
            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.9rem' }}>
              查看其他用户创作的精彩案例，获取创作灵感
            </p>
          </div>

          {/* 案例卡片 */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <div style={{ marginBottom: '12px' }}>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '1.25rem' }}>
                {latestDemoCase.title}
              </h3>
              {latestDemoCase.description && (
                <p style={{ margin: '0 0 12px 0', opacity: 0.85, fontSize: '0.9rem' }}>
                  {latestDemoCase.description}
                </p>
              )}
            </div>

            {/* 统计信息 */}
            <div style={{
              display: 'flex',
              gap: '24px',
              marginBottom: '16px',
              fontSize: '0.9rem'
            }}>
              <div>📊 {latestDemoCase.total_images} 张图片</div>
              <div>🎬 {latestDemoCase.total_videos} 个视频</div>
              <div>⏱️ {latestDemoCase.total_duration} 秒</div>
            </div>

            {/* 剧本预览 */}
            <div style={{
              background: 'rgba(0, 0, 0, 0.2)',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
              maxHeight: '100px',
              overflow: 'auto',
              fontSize: '0.85rem',
              lineHeight: '1.5',
              opacity: 0.9
            }}>
              {latestDemoCase.script.substring(0, 200)}...
            </div>

            {/* 视频预览 - 显示所有分镜视频 */}
            {latestDemoCase.fragments.some((frag: any) =>
              frag.videoNode?.status === 'completed' && frag.videoNode?.output
            ) && (
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '0.85rem', marginBottom: '8px', opacity: 0.9 }}>
                  🎬 视频预览 (共{latestDemoCase.fragments.filter((f: any) =>
                    f.videoNode?.status === 'completed' && f.videoNode?.output
                  ).length}个)
                </div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '12px'
                }}>
                  {latestDemoCase.fragments
                    .filter((frag: any) => frag.videoNode?.status === 'completed' && frag.videoNode?.output)
                    .map((frag: any, index: number) => {
                      const imageUrl = frag.imageNode?.output?.url;
                      const videoUrl = getStaticUrl(frag.videoNode.output);
                      const posterUrl = imageUrl ? getStaticUrl(imageUrl) : undefined;

                      console.log(`🎬 渲染视频 ${index + 1}:`, {
                        fragNumber: frag.number,
                        videoUrl,
                        posterUrl,
                        originalVideoPath: frag.videoNode.output,
                        originalImagePath: imageUrl
                      });

                      return (
                        <div key={index} style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '0.75rem', marginBottom: '4px', opacity: 0.7 }}>
                            分镜 {frag.number}
                          </div>
                          <video
                            src={videoUrl}
                            poster={posterUrl}
                            preload="metadata"
                            controls
                            controlsList="nodownload"
                            style={{
                              width: '100%',
                              borderRadius: '8px',
                              background: 'rgba(0, 0, 0, 0.3)',
                              aspectRatio: '16/9',
                              objectFit: 'cover'
                            }}
                            onLoadStart={() => console.log(`🎬 视频${frag.number}开始加载`)}
                            onCanPlay={() => console.log(`✅ 视频${frag.number}可以播放`)}
                            onError={(e) => console.error(`❌ 视频${frag.number}加载失败:`, e)}
                          />
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            <div style={{ textAlign: 'center' }}>
              <button
                onClick={() => handleViewDemoCase(latestDemoCase)}
                style={{
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '8px',
                  padding: '10px 24px',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  transition: 'all 0.3s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}
              >
                查看完整案例
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="page-header">
        <h1>项目管理</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          + 新建项目
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state">
          <p>还没有项目，创建一个新项目开始创作吧！</p>
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            创建第一个项目
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.id} className="project-card">
              <div className="project-card-header">
                <h3 className="project-title">{project.title}</h3>
                <span className={getStatusClass(getStatusValue(project.status))}>
                  {getStatusText(getStatusValue(project.status))}
                </span>
              </div>
              {project.description && (
                <p className="project-description">{project.description}</p>
              )}
              <div className="project-card-footer">
                <div className="project-meta">
                  <span className="project-dates">
                    创建于 {new Date(project.created_at).toLocaleDateString('zh-CN')}
                  </span>
                </div>
                <div className="project-actions">
                  <Link
                    to={`/workspace/${project.id}`}
                    className="btn btn-secondary"
                  >
                    打开工作台
                  </Link>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDeleteProject(project.id)}
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>创建新项目</h2>
              <button
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleCreateProject} className="modal-body">
              <div className="form-group">
                <label htmlFor="title">项目标题 *</label>
                <input
                  id="title"
                  type="text"
                  value={newProjectTitle}
                  onChange={(e) => setNewProjectTitle(e.target.value)}
                  placeholder="例如：春天主题短片"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label htmlFor="description">项目描述</label>
                <textarea
                  id="description"
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  placeholder="简单描述一下你的视频创意..."
                  rows={4}
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  取消
                </button>
                <button type="submit" className="btn btn-primary">
                  创建
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 演示案例详情模态框 */}
      {showDemoDetailModal && selectedDemoCase && (
        <div className="modal-overlay" onClick={() => setShowDemoDetailModal(false)}>
          <div
            className="modal"
            style={{ maxWidth: '1200px', width: '90%', maxHeight: '90vh', overflow: 'auto' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>🌟 演示案例详情</h2>
              <button
                className="modal-close"
                onClick={() => setShowDemoDetailModal(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-body" style={{ padding: '24px' }}>
              {/* 案例基本信息 */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '1.5rem' }}>
                  {selectedDemoCase.title}
                </h3>
                {selectedDemoCase.description && (
                  <p style={{ margin: '0 0 16px 0', color: '#666', lineHeight: '1.6' }}>
                    {selectedDemoCase.description}
                  </p>
                )}
                <div style={{ display: 'flex', gap: '24px', fontSize: '0.9rem', color: '#666' }}>
                  <div>📊 {selectedDemoCase.total_images} 张图片</div>
                  <div>🎬 {selectedDemoCase.total_videos} 个视频</div>
                  <div>⏱️ {selectedDemoCase.total_duration} 秒</div>
                  <div>🕒 {new Date(selectedDemoCase.created_at).toLocaleDateString('zh-CN')}</div>
                </div>
              </div>

              {/* 剧本 */}
              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '1.1rem' }}>📜 剧本</h4>
                <div style={{
                  background: '#f5f5f5',
                  borderRadius: '8px',
                  padding: '16px',
                  lineHeight: '1.8',
                  whiteSpace: 'pre-wrap',
                  maxHeight: '200px',
                  overflow: 'auto'
                }}>
                  {selectedDemoCase.script}
                </div>
              </div>

              {/* 分镜展示 */}
              <div>
                <h4 style={{ margin: '0 0 16px 0', fontSize: '1.1rem' }}>🎬 分镜展示</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  {selectedDemoCase.fragments.map((frag: any, index: number) => {
                    const hasImage = frag.imageNode?.status === 'completed' && frag.imageNode?.output;
                    const hasVideo = frag.videoNode?.status === 'completed' && frag.videoNode?.output;

                    return (
                      <div
                        key={index}
                        style={{
                          border: '1px solid #e0e0e0',
                          borderRadius: '12px',
                          padding: '20px',
                          background: '#fafafa'
                        }}
                      >
                        {/* 分镜标题 */}
                        <div style={{ marginBottom: '12px' }}>
                          <h5 style={{ margin: '0 0 8px 0', fontSize: '1rem', color: frag.color }}>
                            分镜 {frag.number} · {frag.duration}秒
                          </h5>
                        </div>

                        {/* 提示词 */}
                        <div style={{ marginBottom: '12px' }}>
                          <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>
                            提示词：
                          </div>
                          <div style={{
                            fontSize: '0.9rem',
                            lineHeight: '1.6',
                            color: '#333',
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px'
                          }}>
                            {frag.prompt}
                          </div>
                        </div>

                        {/* 图片和视频展示 */}
                        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                          {/* 图片 */}
                          {hasImage && (
                            <div style={{ flex: '1 1 300px' }}>
                              <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '8px' }}>
                                🖼️ AI生成图片 ({frag.imageNode.modelName || '通义万相'})
                              </div>
                              <img
                                src={getStaticUrl(frag.imageNode.output?.url)}
                                alt={`分镜${frag.number}`}
                                style={{
                                  width: '100%',
                                  borderRadius: '8px',
                                  border: '1px solid #e0e0e0'
                                }}
                              />
                            </div>
                          )}

                          {/* 视频 */}
                          {hasVideo && (
                            <div style={{ flex: '1 1 300px' }}>
                              <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '8px' }}>
                                🎬 AI生成视频 ({frag.videoNode.modelName || '豆包视频生成'})
                              </div>
                              <video
                                src={getStaticUrl(frag.videoNode.output)}
                                poster={hasImage ? getStaticUrl(frag.imageNode.output?.url) : undefined}
                                preload="metadata"
                                controls
                                controlsList="nodownload"
                                style={{
                                  width: '100%',
                                  borderRadius: '8px',
                                  border: '1px solid #e0e0e0',
                                  aspectRatio: '16/9',
                                  objectFit: 'cover'
                                }}
                              />
                            </div>
                          )}
                        </div>

                        {/* 音频提示 */}
                        {frag.audio_prompt && (
                          <div style={{ marginTop: '12px', fontSize: '0.85rem', color: '#666' }}>
                            🎵 音频提示: {frag.audio_prompt}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-primary"
                onClick={() => setShowDemoDetailModal(false)}
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
