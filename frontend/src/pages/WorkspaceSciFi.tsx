/**
 * 科幻风格分镜工作流系统
 * 高级乐高积木式搭建体验
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { projectService } from '../services/projectService';
import type { Project } from '../types';
import './WorkspaceSciFi.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const SHOT_AGENT_URL = 'http://localhost:8001/api/v1'; // video-shot-agent 服务地址（端口8001）

// 20种彩虹渐变颜色
const FRAGMENT_COLORS = [
  '#FF6B6B', '#FF8E72', '#FFB347', '#FFD93D', '#FFFF6B',
  '#CAFF6B', '#9DFF6B', '#6BFF9D', '#6BFFFF', '#6BD1FF',
  '#6B9DFF', '#856BFF', '#A66BFF', '#CA6BFF', '#FF6BFF',
  '#FF6BCA', '#FF6BA6', '#FF6B84', '#FF6B6B', '#FF8E72'
];

// 类型定义
type NodeStatus = 'pending' | 'running' | 'completed' | 'skipped' | 'error';

interface Fragment {
  fragment_id: string;
  number: number;
  duration: number;
  prompt: string;
  negative_prompt: string;
  audio_prompt: string;
  color: string;

  imageNode: {
    status: NodeStatus;
    result?: any;
    output?: any;
  };

  videoNode: {
    status: NodeStatus;
    dependsOn: 'image';
    result?: any;
    output?: any;
  };
}

interface ExecutionLine {
  id: string;
  name: string;
  fragmentNumber: number;
  selected: boolean;
}

// 加载动画组件
const LoadingIcon = () => (
  <svg className="loading-icon" viewBox="0 0 50 50">
    <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5">
      <animate attributeName="stroke-dasharray" from="0, 100" to="100, 0" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="stroke-dashoffset" from="0" to="-100" dur="2s" repeatCount="indefinite"/>
    </circle>
  </svg>
);

export default function WorkspaceSciFi() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  // 状态
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [scriptInput, setScriptInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [fragments, setFragments] = useState<Fragment[]>([]);
  const [expandedFragments, setExpandedFragments] = useState<Set<string>>(new Set());
  const [compositionStatus, setCompositionStatus] = useState<NodeStatus>('pending');
  const [compositionResult, setCompositionResult] = useState<any>(null);

  // 执行线路选择
  const [executionLines, setExecutionLines] = useState<ExecutionLine[]>([]);
  const [showExecutionDialog, setShowExecutionDialog] = useState(false);
  const [selectAll, setSelectAll] = useState(true);

  // 初始化
  useEffect(() => {
    if (!projectId) {
      navigate('/projects');
      return;
    }
    loadProject(projectId);
  }, [projectId, navigate]);

  // 加载项目
  const loadProject = async (id: string) => {
    try {
      const project = await projectService.get(id);
      setCurrentProject(project);
    } catch (error) {
      console.error('加载项目失败:', error);
      navigate('/projects');
    }
  };

  // 开始智能分镜分析
  const handleStartAnalysis = async () => {
    if (!scriptInput.trim() || isAnalyzing) return;

    setIsAnalyzing(true);

    try {
      // 调用 video-shot-agent API
      const response = await axios.post(
        `${SHOT_AGENT_URL}/storyboard`,
        {
          script: scriptInput,
          config: {
            max_fragment_duration: 5.0,
            model: 'qwen-plus'
          }
        }
      );

      const taskId = response.data.task_id;

      // 轮询获取结果
      const result = await pollForResult(taskId);

      if (result && result.fragments) {
        // 生成分镜数据
        const newFragments: Fragment[] = result.fragments.map((frag: any, index: number) => ({
          fragment_id: frag.fragment_id,
          number: index + 1,
          duration: frag.duration,
          prompt: frag.prompt,
          negative_prompt: frag.negative_prompt,
          audio_prompt: frag.audio_prompt?.prompt || '',
          color: FRAGMENT_COLORS[index % FRAGMENT_COLORS.length],
          imageNode: {
            status: 'pending',
          },
          videoNode: {
            status: 'pending',
            dependsOn: 'image',
          },
        }));

        setFragments(newFragments);

        // 自动展开第一个分镜
        if (newFragments.length > 0) {
          setExpandedFragments(new Set([newFragments[0].fragment_id]));

          // 初始化执行线路
          const lines: ExecutionLine[] = newFragments.map(frag => ({
            id: frag.fragment_id,
            name: `线路 ${frag.number} - ${frag.prompt.substring(0, 30)}...`,
            fragmentNumber: frag.number,
            selected: true,
          }));
          setExecutionLines(lines);
        }
      }

    } catch (error: any) {
      console.error('分镜分析失败:', error);
      alert(`分镜分析失败: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 轮询获取分镜结果
  const pollForResult = async (taskId: string): Promise<any> => {
    const maxAttempts = 60; // 最多轮询60次（5分钟）
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await axios.get(`${SHOT_AGENT_URL}/result/${taskId}`);

        if (response.data && response.data.fragments) {
          return response.data;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      } catch (error) {
        console.error('轮询失败:', error);
        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }
    }

    throw new Error('分镜分析超时，请稍后重试');
  };

  // 切换分镜展开/折叠
  const toggleFragment = (fragmentId: string) => {
    setExpandedFragments(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fragmentId)) {
        newSet.delete(fragmentId);
      } else {
        newSet.add(fragmentId);
      }
      return newSet;
    });
  };

  // 执行图片生成
  const executeImageGeneration = async (fragment: Fragment) => {
    setFragments(prev => prev.map(frag => {
      if (frag.fragment_id === fragment.fragment_id) {
        return {
          ...frag,
          imageNode: {
            ...frag.imageNode,
            status: 'running',
          },
        };
      }
      return frag;
    }));

    try {
      const response = await axios.post(`${API_URL}/generation/generate/image`, {
        prompt: fragment.prompt,
        negative_prompt: fragment.negative_prompt,
        size: '1024*1024',
        n: 1,
        style: 'photography',
      });

      setFragments(prev => prev.map(frag => {
        if (frag.fragment_id === fragment.fragment_id) {
          return {
            ...frag,
            imageNode: {
              status: 'completed',
              result: response.data,
              output: response.data.images?.[0], // 交付物
            },
          };
        }
        return frag;
      }));

    } catch (error: any) {
      setFragments(prev => prev.map(frag => {
        if (frag.fragment_id === fragment.fragment_id) {
          return {
            ...frag,
            imageNode: {
              status: 'error',
            },
          };
        }
        return frag;
      }));
      alert(`图片生成失败: ${error.message}`);
    }
  };

  // 执行视频生成
  const executeVideoGeneration = async (fragment: Fragment) => {
    // 检查上游节点是否完成
    if (fragment.imageNode.status !== 'completed') {
      alert('请先完成图片生成！');
      return;
    }

    setFragments(prev => prev.map(frag => {
      if (frag.fragment_id === fragment.fragment_id) {
        return {
          ...frag,
          videoNode: {
            ...frag.videoNode,
            status: 'running',
          },
        };
      }
      return frag;
    }));

    try {
      const imageUrl = fragment.imageNode.output?.url;

      const response = await axios.post(`${API_URL}/generation/generate/video`, {
        prompt: fragment.prompt,
        image_url: imageUrl, // 使用上游图片
        duration: fragment.duration,
        fps: 25,
        resolution: '720p',
      });

      setFragments(prev => prev.map(frag => {
        if (frag.fragment_id === fragment.fragment_id) {
          return {
            ...frag,
            videoNode: {
              status: 'completed',
              dependsOn: 'image',
              result: response.data,
              output: response.data.video_url, // 交付物
            },
          };
        }
        return frag;
      }));

    } catch (error: any) {
      setFragments(prev => prev.map(frag => {
        if (frag.fragment_id === fragment.fragment_id) {
          return {
            ...frag,
            videoNode: {
              ...frag.videoNode,
              status: 'error',
            },
          };
        }
        return frag;
      }));
      alert(`视频生成失败: ${error.message}`);
    }
  };

  // 跳过节点
  const skipNode = (fragment: Fragment, nodeType: 'image' | 'video') => {
    setFragments(prev => prev.map(frag => {
      if (frag.fragment_id === fragment.fragment_id) {
        if (nodeType === 'image') {
          return {
            ...frag,
            imageNode: {
              status: 'skipped',
            },
          };
        } else {
          return {
            ...frag,
            videoNode: {
              ...frag.videoNode,
              status: 'skipped',
            },
          };
        }
      }
      return frag;
    }));
  };

  // 重新生成
  const regenerateNode = (fragment: Fragment, nodeType: 'image' | 'video') => {
    if (nodeType === 'image') {
      executeImageGeneration(fragment);
    } else {
      executeVideoGeneration(fragment);
    }
  };

  // 显示执行对话框
  const showExecuteDialog = () => {
    setShowExecutionDialog(true);
    setSelectAll(true);
  };

  // 切换线路选择
  const toggleLineSelection = (lineId: string) => {
    setExecutionLines(prev => prev.map(line => {
      if (line.id === lineId) {
        return { ...line, selected: !line.selected };
      }
      return line;
    }));
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    const newValue = !selectAll;
    setSelectAll(newValue);
    setExecutionLines(prev => prev.map(line => ({
      ...line,
      selected: newValue,
    })));
  };

  // 执行选中的线路
  const executeSelectedLines = async () => {
    const selectedLines = executionLines.filter(line => line.selected);

    if (selectedLines.length === 0) {
      alert('请至少选择一条线路！');
      return;
    }

    setShowExecutionDialog(false);

    // 按顺序执行每条线路
    for (const line of selectedLines) {
      const fragment = fragments.find(f => f.fragment_id === line.id);
      if (!fragment) continue;

      // 执行图片生成
      if (fragment.imageNode.status === 'pending' || fragment.imageNode.status === 'error') {
        await executeImageGeneration(fragment);
      }

      // 执行视频生成
      if (fragment.videoNode.status === 'pending' || fragment.videoNode.status === 'error') {
        await executeVideoGeneration(fragment);
      }
    }
  };

  // 批量执行所有待处理节点
  const executeAllPending = () => {
    setExecutionLines(prev => prev.map(line => ({ ...line, selected: true })));
    setSelectAll(true);
    showExecuteDialog();
  };

  // 视频合成
  const composeVideo = async () => {
    // 检查所有视频是否完成
    const completedVideos = fragments.filter(f => f.videoNode.status === 'completed');

    if (completedVideos.length !== fragments.length) {
      alert(`请等待所有视频生成完成！\n当前进度: ${completedVideos.length}/${fragments.length}`);
      return;
    }

    setCompositionStatus('running');

    try {
      // 收集所有视频URL
      const videoUrls = fragments.map(f => f.videoNode.output?.url).filter(Boolean);

      // 调用视频合成API（需要后端实现）
      const response = await axios.post(`${API_URL}/generation/compose`, {
        video_urls: videoUrls,
        project_id: projectId,
      });

      setCompositionResult(response.data);
      setCompositionStatus('completed');
      alert('视频合成完成！');

    } catch (error: any) {
      alert(`视频合成失败: ${error.message}`);
      setCompositionStatus('error');
    }
  };

  if (!currentProject) {
    return (
      <div className="workspace-sifi">
        <div className="loading-state">
          <LoadingIcon />
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="workspace-sifi">
      {/* 顶部导航 */}
      <div className="sifi-header">
        <button className="back-btn" onClick={() => navigate('/projects')}>
          ← 返回项目列表
        </button>
        <div className="project-info">
          <h1>{currentProject.title}</h1>
          {currentProject.description && <p>{currentProject.description}</p>}
        </div>
        <div className="header-actions">
          <button className="icon-btn">⚙️</button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="sifi-content">
        {/* 剧本输入区 */}
        <div className="input-section">
          <div className="section-title">📝 剧本输入</div>
          <textarea
            className="script-input"
            placeholder="在此输入你的剧本或创作需求..."
            value={scriptInput}
            onChange={(e) => setScriptInput(e.target.value)}
            rows={6}
            disabled={fragments.length > 0}
          />
          {fragments.length === 0 && (
            <div className="input-actions">
              <button
                className="btn-primary"
                onClick={handleStartAnalysis}
                disabled={!scriptInput.trim() || isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <LoadingIcon />
                    分析中...
                  </>
                ) : (
                  '🚀 开始智能分镜分析'
                )}
              </button>
            </div>
          )}
        </div>

        {/* 分镜矩阵 */}
        {fragments.length > 0 && (
          <>
            <div className="matrix-section">
              <div className="section-title">
                🎯 分镜设计矩阵
                <span className="fragment-count">[{fragments.length}个分镜]</span>
              </div>
              <div className="storyboard-grid">
                {fragments.map((fragment) => (
                  <div
                    key={fragment.fragment_id}
                    className={`storyblock ${expandedFragments.has(fragment.fragment_id) ? 'expanded' : ''}`}
                    onClick={() => toggleFragment(fragment.fragment_id)}
                    style={{
                      borderColor: fragment.color,
                      boxShadow: expandedFragments.has(fragment.fragment_id)
                        ? `0 0 30px ${fragment.color}80`
                        : `0 0 10px ${fragment.color}40`,
                    }}
                  >
                    <div className="block-icon">💫</div>
                    <div className="block-number">{fragment.number}</div>
                    <div className="block-duration">{fragment.duration.toFixed(1)}s</div>
                    {expandedFragments.has(fragment.fragment_id) && (
                      <div className="expand-indicator">▼</div>
                    )}
                  </div>
                ))}
              </div>
              <div className="matrix-hint">
                💡 点击任意分镜块展开详细节点链
              </div>
            </div>

            {/* 工作流构建区 */}
            <div className="workflow-section">
              <div className="section-title">🎬 工作流构建区</div>

              {/* 展开的分镜详情 */}
              {fragments.map((fragment) => (
                expandedFragments.has(fragment.fragment_id) && (
                  <div
                    key={fragment.fragment_id}
                    className="fragment-detail"
                    style={{ borderColor: fragment.color }}
                  >
                    <div className="fragment-header">
                      <div className="fragment-title">
                        <span style={{ color: fragment.color }}>🎯 分镜 {fragment.number}</span>
                        <span className="fragment-duration">⏱️ {fragment.duration.toFixed(1)}秒</span>
                      </div>
                      <div className="fragment-actions">
                        <button onClick={() => toggleFragment(fragment.fragment_id)}>▼ 收起</button>
                        <button onClick={() => toggleFragment(fragment.fragment_id)}>⚙️</button>
                      </div>
                    </div>

                    <div className="fragment-prompt">
                      {fragment.prompt.substring(0, 100)}...
                    </div>

                    {/* 图片生成节点 */}
                    <div className="node-card">
                      <div className="node-header">
                        <span className="node-icon">📸</span>
                        <span className="node-title">图片生成</span>
                        <span className={`node-status status-${fragment.imageNode.status}`}>
                          {fragment.imageNode.status === 'pending' && '⏳ 待执行'}
                          {fragment.imageNode.status === 'running' && '⚙️ 生成中...'}
                          {fragment.imageNode.status === 'completed' && '✓ 已完成'}
                          {fragment.imageNode.status === 'skipped' && '⏭️ 已跳过'}
                          {fragment.imageNode.status === 'error' && '❌ 失败'}
                        </span>
                      </div>

                      {fragment.imageNode.status === 'pending' && (
                        <div className="node-actions">
                          <button
                            className="btn-execute"
                            onClick={() => executeImageGeneration(fragment)}
                            style={{ background: fragment.color }}
                          >
                            ▶️ 开始生成
                          </button>
                          <button onClick={() => skipNode(fragment, 'image')}>⏭️ 跳过</button>
                        </div>
                      )}

                      {fragment.imageNode.status === 'running' && (
                        <div className="node-loading">
                          <LoadingIcon />
                          <span>正在生成图片...</span>
                        </div>
                      )}

                      {fragment.imageNode.status === 'completed' && fragment.imageNode.result && (
                        <div className="node-result">
                          <div className="result-images">
                            <img
                              src={fragment.imageNode.output?.url}
                              alt={`分镜${fragment.number}`}
                            />
                          </div>
                          <div className="node-actions">
                            <button onClick={() => regenerateNode(fragment, 'image')}>🔄 重新生成</button>
                            <button>📤 导出</button>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* 能量流动连线 */}
                    {(fragment.imageNode.status === 'completed' || fragment.imageNode.status === 'skipped') && (
                      <div className="energy-flow" style={{ color: fragment.color }}>
                        ⚡️
                      </div>
                    )}

                    {/* 视频生成节点 */}
                    <div className="node-card">
                      <div className="node-header">
                        <span className="node-icon">🎬</span>
                        <span className="node-title">视频生成</span>
                        <span className={`node-status status-${fragment.videoNode.status}`}>
                          {fragment.videoNode.status === 'pending' && '⏳ 待执行'}
                          {fragment.videoNode.status === 'running' && '⚙️ 生成中...'}
                          {fragment.videoNode.status === 'completed' && '✓ 已完成'}
                          {fragment.videoNode.status === 'skipped' && '⏭️ 已跳过'}
                          {fragment.videoNode.status === 'error' && '❌ 失败'}
                        </span>
                      </div>

                      {fragment.videoNode.status === 'pending' && (
                        <div className="node-actions">
                          <button
                            className="btn-execute"
                            onClick={() => executeVideoGeneration(fragment)}
                            disabled={fragment.imageNode.status !== 'completed'}
                            style={{
                              background: fragment.imageNode.status === 'completed' ? fragment.color : '#666',
                            }}
                          >
                            ▶️ 开始生成
                          </button>
                          <button onClick={() => skipNode(fragment, 'video')}>⏭️ 跳过</button>
                        </div>
                      )}

                      {fragment.videoNode.status === 'running' && (
                        <div className="node-loading">
                          <LoadingIcon />
                          <span>正在生成视频...</span>
                        </div>
                      )}

                      {fragment.videoNode.status === 'completed' && fragment.videoNode.result && (
                        <div className="node-result">
                          <div className="result-video">
                            <video
                              src={fragment.videoNode.output}
                              controls
                            />
                          </div>
                          <div className="node-actions">
                            <button onClick={() => regenerateNode(fragment, 'video')}>🔄 重新生成</button>
                            <button>📤 导出</button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )
              ))}

              {/* 视频合成节点 */}
              <div className="composition-node">
                <div className="node-header">
                  <span className="node-icon">🎬</span>
                  <span className="node-title">视频合成</span>
                  <span className={`node-status status-${compositionStatus}`}>
                    {compositionStatus === 'pending' && '⏳ 等待中'}
                    {compositionStatus === 'running' && '⚙️ 合成中...'}
                    {compositionStatus === 'completed' && '✓ 已完成'}
                    {compositionStatus === 'error' && '❌ 失败'}
                  </span>
                </div>

                <div className="composition-progress">
                  <div className="progress-info">
                    完成进度: {fragments.filter(f => f.videoNode.status === 'completed').length} / {fragments.length}
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${(fragments.filter(f => f.videoNode.status === 'completed').length / fragments.length) * 100}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="node-actions">
                  <button onClick={() => window.location.reload()}>🔄 刷新进度</button>
                  {compositionStatus !== 'running' && (
                    <button
                      className="btn-compose"
                      onClick={composeVideo}
                      disabled={fragments.filter(f => f.videoNode.status === 'completed').length !== fragments.length}
                    >
                      🎬 开始合成
                    </button>
                  )}
                </div>

                {compositionStatus === 'completed' && compositionResult && (
                  <div className="composition-result">
                    <div className="result-video">
                      <video src={compositionResult.video_url} controls />
                    </div>
                    <div className="node-actions">
                      <button>📥 下载视频</button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 底部操作栏 */}
            <div className="bottom-actions">
              <button className="btn-batch" onClick={executeAllPending}>
                🎯 批量执行待处理节点
              </button>
              <button className="btn-save">💾 保存工作流</button>
              <button className="btn-export">📤 导出项目</button>
            </div>
          </>
        )}
      </div>

      {/* 执行线路选择对话框 */}
      {showExecutionDialog && (
        <div className="dialog-overlay" onClick={() => setShowExecutionDialog(false)}>
          <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
            <div className="dialog-header">
              <h2>选择要执行的线路</h2>
              <button onClick={() => setShowExecutionDialog(false)}>✕</button>
            </div>

            <div className="dialog-body">
              <div className="select-all-row">
                <label>
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={toggleSelectAll}
                  />
                  全选
                </label>
                <span>已选择: {executionLines.filter(l => l.selected).length} / {executionLines.length}</span>
              </div>

              <div className="lines-list">
                {executionLines.map((line) => (
                  <div key={line.id} className="line-item">
                    <label>
                      <input
                        type="checkbox"
                        checked={line.selected}
                        onChange={() => toggleLineSelection(line.id)}
                      />
                      <span className="line-name">{line.name}</span>
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="dialog-footer">
              <button onClick={() => setShowExecutionDialog(false)}>取消</button>
              <button className="btn-primary" onClick={executeSelectedLines}>
                开始执行 ({executionLines.filter(l => l.selected).length})
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
