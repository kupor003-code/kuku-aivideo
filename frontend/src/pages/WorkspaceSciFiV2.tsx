/**
 * 科幻风格分镜工作流系统 - 带内置分镜生成
 * 高级乐高积木式搭建体验
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { projectService } from '../services/projectService';
import { storyboardService } from '../services/storyboardService';
import { demoCaseService } from '../services/demoCaseService';
import type { Project } from '../types';
import './WorkspaceSciFi.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

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
    model?: string;
    modelName?: string;
  };

  videoNode: {
    status: NodeStatus;
    dependsOn: 'image';
    result?: any;
    output?: any;
    model?: string;
    modelName?: string;
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
  const [targetDuration, setTargetDuration] = useState(30); // 目标视频总时长（秒）
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [fragments, setFragments] = useState<Fragment[]>([]);
  const [expandedFragments, setExpandedFragments] = useState<Set<string>>(new Set());
  const [compositionStatus, setCompositionStatus] = useState<NodeStatus>('pending');
  const [compositionResult, setCompositionResult] = useState<any>(null);

  // 进度状态
  const [imageProgress, setImageProgress] = useState<Record<string, number>>({});
  const [videoProgress, setVideoProgress] = useState<Record<string, number>>({});

  // 执行线路选择
  const [executionLines, setExecutionLines] = useState<ExecutionLine[]>([]);
  const [showExecutionDialog, setShowExecutionDialog] = useState(false);
  const [selectAll, setSelectAll] = useState(true);

  // 演示模式状态
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [showDemoGallery, setShowDemoGallery] = useState(true);
  const [demoCaseId, setDemoCaseId] = useState<string | null>(null);  // 已保存的演示案例ID

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

      // 尝试从 localStorage 加载保存的进度
      loadWorkspaceState(id);
    } catch (error) {
      console.error('加载项目失败:', error);
      navigate('/projects');
    }
  };

  // 获取 localStorage key
  const getStorageKey = () => `workspace_${projectId}`;

  // 保存工作区状态到 localStorage
  const saveWorkspaceState = () => {
    if (!projectId) return;

    try {
      // 统计要保存的内容
      const completedImages = fragments.filter(f =>
        f.imageNode?.status === 'completed' || f.imageNode?.result
      ).length;
      const completedVideos = fragments.filter(f =>
        f.videoNode?.status === 'completed' || f.videoNode?.result
      ).length;

      const state = {
        scriptInput,
        targetDuration,
        fragments,
        expandedFragments: Array.from(expandedFragments),
        compositionStatus,
        compositionResult,
        executionLines,
        lastSaved: new Date().toISOString(),
      };

      localStorage.setItem(getStorageKey(), JSON.stringify(state));
      console.log(`✓ 已自动保存: ${fragments.length} 个分镜, ${completedImages} 张图片, ${completedVideos} 个视频`);
    } catch (error) {
      console.error('保存状态失败:', error);
    }
  };

  // 从 localStorage 加载工作区状态
  const loadWorkspaceState = (id: string) => {
    const storageKey = `workspace_${id}`;
    const saved = localStorage.getItem(storageKey);

    if (saved) {
      try {
        const state = JSON.parse(saved);
        const savedTime = new Date(state.lastSaved).toLocaleString();
        console.log('📂 发现保存的进度:', savedTime);

        // 统计生成内容
        const completedImages = state.fragments?.filter((f: any) =>
          f.imageNode?.status === 'completed' || f.imageNode?.result
        ).length || 0;
        const completedVideos = state.fragments?.filter((f: any) =>
          f.videoNode?.status === 'completed' || f.videoNode?.result
        ).length || 0;

        console.log(`✓ 已保存内容: ${state.fragments?.length || 0} 个分镜, ${completedImages} 张图片, ${completedVideos} 个视频`);

        // 恢复状态
        if (state.scriptInput) setScriptInput(state.scriptInput);
        if (state.targetDuration !== undefined) setTargetDuration(state.targetDuration);
        if (state.fragments && state.fragments.length > 0) {
          setFragments(state.fragments);
          setExecutionLines(state.executionLines || []);
          setCompositionStatus(state.compositionStatus || 'pending');
          setCompositionResult(state.compositionResult);
          setExpandedFragments(new Set(state.expandedFragments || []));
          setLastSavedTime(savedTime);

          // 延迟显示提示，让用户看到加载完成
          setTimeout(() => {
            if (completedImages > 0 || completedVideos > 0) {
              console.log(`💡 提示: 已从本地存储恢复 ${completedImages} 张图片和 ${completedVideos} 个视频，无需重新生成！`);
            }
          }, 500);
        }
      } catch (error) {
        console.error('加载保存状态失败:', error);
      }
    } else {
      console.log('📝 未找到保存的进度，这是新项目或已清除');
    }
  };

  // 清除保存的状态
  const clearSavedState = () => {
    if (!projectId) return;
    localStorage.removeItem(getStorageKey());
    console.log('🗑️ 已清除保存的进度');
  };

  // 保存状态时间
  const [lastSavedTime, setLastSavedTime] = useState<string | null>(null);

  // 改进保存函数，更新保存时间
  const saveWorkspaceStateWithTimestamp = () => {
    saveWorkspaceState();
    setLastSavedTime(new Date().toLocaleString());
  };

  // 自动保存：在关键状态变化时保存
  useEffect(() => {
    if (fragments.length > 0) {
      const timer = setTimeout(saveWorkspaceStateWithTimestamp, 1000);
      return () => clearTimeout(timer);
    }
  }, [fragments, compositionStatus, compositionResult]);

  // 加载时也恢复保存时间
  useEffect(() => {
    if (fragments.length > 0) {
      const saved = localStorage.getItem(getStorageKey());
      if (saved) {
        try {
          const state = JSON.parse(saved);
          if (state.lastSaved) {
            setLastSavedTime(new Date(state.lastSaved).toLocaleString());
          }
        } catch (e) {
          // 忽略错误
        }
      }
    }
  }, []);

  // 加载演示项目
  const loadDemoProject = () => {
    if (!confirm('加载演示项目将覆盖当前内容，确定要继续吗？')) return;

    // 设置演示模式
    setIsDemoMode(true);
    setShowDemoGallery(true);

    const demoScript = `【城市风光短视频】

镜头1：日出时分的城市天际线，金色的阳光洒满摩天大楼
镜头2：繁华的街道，车水马龙，行人匆匆
镜头3：夜晚的都市霓虹，灯光璀璨，美轮美奂
镜头4：俯瞰城市全景，展现现代都市的壮观
镜头5：黎明前的宁静街道，路灯昏黄，氛围温馨`;

    setScriptInput(demoScript);
    setTargetDuration(20);

    // 演示项目的分镜数据
    const demoFragments: Fragment[] = [
      {
        fragment_id: `demo-frag-${Date.now()}-1`,
        number: 1,
        duration: 4.0,
        prompt: "日出时分的城市天际线，金色的阳光洒满摩天大楼，朝霞满天",
        negative_prompt: "",
        audio_prompt: "",
        color: "#FF6B6B",
        imageNode: {
          status: 'completed',
          result: {
            model: "wanx-v1",
            model_name: "通义万相 (Wanxiang v1)"
          },
          output: {
            url: "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/1d/69/20260315/c70535fc/e8f217ee-d852-4b2a-ba9b-776c805c6ef6-1.png?Expires=1773674914&OSSAccessKeyId=LTAI5tQZd8AEcZX6KZV4G8qL&Signature=RLXnztTfiGwBWk48Bk1e3Z6P10c%3D"
          },
          modelName: "通义万相 (Wanxiang v1)"
        },
        videoNode: {
          status: 'completed',
          dependsOn: 'image',
          result: {
            model: "doubao-seedance-1-5-pro-251215",
            model_name: "豆包视频生成 (Seedance 1.5 Pro)"
          },
          output: "/static/demo-cases/demo-video-1.mp4",
          modelName: "豆包视频生成 (Seedance 1.5 Pro)"
        }
      },
      {
        fragment_id: `demo-frag-${Date.now()}-2`,
        number: 2,
        duration: 4.0,
        prompt: "繁华的城市街道，车水马龙，行人匆匆而过，充满生机活力",
        negative_prompt: "",
        audio_prompt: "",
        color: "#4ECDC4",
        imageNode: {
          status: 'completed',
          result: {
            model: "wanx-v1",
            model_name: "通义万相 (Wanxiang v1)"
          },
          output: {
            url: "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/1d/fe/20260315/c70535fc/20250315/001-demo-2.png"
          },
          modelName: "通义万相 (Wanxiang v1)"
        },
        videoNode: {
          status: 'completed',
          dependsOn: 'image',
          result: {
            model: "doubao-seedance-1-5-pro-251215",
            model_name: "豆包视频生成 (Seedance 1.5 Pro)"
          },
          output: "/static/demo-cases/demo-video-2.mp4",
          modelName: "豆包视频生成 (Seedance 1.5 Pro)"
        }
      },
      {
        fragment_id: `demo-frag-${Date.now()}-3`,
        number: 3,
        duration: 4.0,
        prompt: "夜晚的都市霓虹灯海，摩天大楼灯火辉煌，色彩斑斓",
        negative_prompt: "",
        audio_prompt: "",
        color: "#95E1D3",
        imageNode: {
          status: 'completed',
          result: {
            model: "wanx-v1",
            model_name: "通义万相 (Wanxiang v1)"
          },
          output: {
            url: "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/1d/69/20260315/c70535fc/fcb22041-53b4-415e-a7d4-0f44a0960dea-1.png?Expires=1773674872&OSSAccessKeyId=LTAI5tQZd8AEcZX6KZV4G8qL&Signature=jwKKswd8hhBJX%2FVliO%2BvcuxB3vw%3D"
          },
          modelName: "通义万相 (Wanxiang v1)"
        },
        videoNode: {
          status: 'pending',
          dependsOn: 'image'
        }
      },
      {
        fragment_id: `demo-frag-${Date.now()}-4`,
        number: 4,
        duration: 4.0,
        prompt: "俯瞰城市全景，展现现代都市的壮观景象，高楼林立",
        negative_prompt: "",
        audio_prompt: "",
        color: "#F38181",
        imageNode: {
          status: 'completed',
          result: {
            model: "wanx-v1",
            model_name: "通义万相 (Wanxiang v1)"
          },
          output: {
            url: "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/1d/fe/20260315/c70535fc/e8f217ee-d852-4b2a-ba9b-776c805c6ef6-1.png?Expires=1773674914&OSSAccessKeyId=LTAI5tQZd8AEcZX6KZV4G8qL&Signature=RLXnztTfiGwBWk48Bk1e3Z6P10c%3D"
          },
          modelName: "通义万相 (Wanxiang v1)"
        },
        videoNode: {
          status: 'pending',
          dependsOn: 'image'
        }
      },
      {
        fragment_id: `demo-frag-${Date.now()}-5`,
        number: 5,
        duration: 4.0,
        prompt: "黎明前的宁静街道，路灯昏黄温暖，晨雾缭绕，氛围温馨",
        negative_prompt: "",
        audio_prompt: "",
        color: "#AA96DA",
        imageNode: {
          status: 'pending',
        },
        videoNode: {
          status: 'pending',
          dependsOn: 'image'
        }
      }
    ];

    setFragments(demoFragments);

    // 设置执行线路
    const demoLines = demoFragments.map(frag => ({
      id: frag.fragment_id,
      name: `线路 ${frag.number} - ${frag.prompt.substring(0, 20)}...`,
      fragmentNumber: frag.number,
      selected: true,
    }));
    setExecutionLines(demoLines);

    // 自动展开所有分镜
    setExpandedFragments(new Set(demoFragments.map(f => f.fragment_id)));

    console.log('✅ 演示项目已加载');
    console.log('📝 包含内容:');
    console.log(`   - 5 个分镜（总时长 20 秒）`);
    console.log(`   - 4 张已生成的示例图片`);
    console.log(`   - 2 个已生成的示例视频`);
    console.log(`   - 完整的提示词展示`);
    console.log('\n💡 提示: 点击各分镜可以查看详细信息，包括:');
    console.log('   • AI生成的提示词');
    console.log('   • 使用了哪个模型（通义万相/豆包）');
    console.log('   • 生成的图片和视频');
    console.log('   • 可以重新生成或下载');
  };

  // 开始智能分镜分析
  const handleStartAnalysis = async () => {
    if (!scriptInput.trim() || isAnalyzing) return;

    setIsAnalyzing(true);

    try {
      // 使用智谱AI生成分镜，传入目标总时长
      const result = await storyboardService.generateFromScript(scriptInput, targetDuration);

      // 验证总时长
      const totalDuration = result.fragments.reduce((sum, frag) => sum + frag.duration, 0);
      console.log(`生成了 ${result.fragments.length} 个分镜，总时长: ${totalDuration}秒（目标: ${targetDuration}秒）`);

      // 转换为Fragment格式
      const newFragments: Fragment[] = result.fragments.map((frag, index) => ({
        ...frag,
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

    } catch (error: any) {
      console.error('分镜分析失败:', error);
      alert(`分镜分析失败: ${error.message}\n\n请检查API密钥配置或稍后重试。`);
    } finally {
      setIsAnalyzing(false);
    }
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

  // 执行图片生成（使用真实的 VolcEngine API + 进度条）
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

    // 模拟进度（图片生成约需15-20秒）
    const estimatedTime = 18000; // 18秒
    const updateInterval = 500; // 每500ms更新一次
    let progress = 0;

    const progressTimer = setInterval(() => {
      progress += (updateInterval / estimatedTime) * 100;
      if (progress > 95) progress = 95; // 最高到95%，等待实际完成
      setImageProgress(prev => ({
        ...prev,
        [fragment.fragment_id]: Math.min(progress, 95),
      }));
    }, updateInterval);

    try {
      // 调用后端 API 生成图片
      const response = await axios.post(`${API_URL}/generation/generate/image`, {
        prompt: fragment.prompt,
        size: "1024*1024",  // 阿里云API支持的尺寸格式
        n: 1,
      });

      clearInterval(progressTimer);
      setImageProgress(prev => ({ ...prev, [fragment.fragment_id]: 100 }));

      if (response.data.success && response.data.images && response.data.images.length > 0) {
        const generatedImage = response.data.images[0];

        setFragments(prev => prev.map(frag => {
          if (frag.fragment_id === fragment.fragment_id) {
            return {
              ...frag,
              imageNode: {
                status: 'completed',
                result: response.data,
                output: generatedImage,
                model: response.data.model,
                modelName: response.data.model_name,
              },
            };
          }
          return frag;
        }));

        // 延迟移除进度条
        setTimeout(() => {
          setImageProgress(prev => {
            const newProgress = { ...prev };
            delete newProgress[fragment.fragment_id];
            return newProgress;
          });
        }, 2000);
      } else {
        throw new Error('图片生成失败');
      }

    } catch (error: any) {
      clearInterval(progressTimer);
      setImageProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[fragment.fragment_id];
        return newProgress;
      });

      console.error('图片生成错误:', error);
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
      alert(`图片生成失败: ${error.response?.data?.detail || error.message}`);
    }
  };

  // 执行视频生成（使用真实的 VolcEngine API + 进度条）
  const executeVideoGeneration = async (fragment: Fragment) => {
    if (fragment.imageNode.status !== 'completed' && fragment.imageNode.status !== 'skipped') {
      alert('请先完成图片生成！');
      return;
    }

    // 如果图片生成被跳过，检查是否有自定义图片URL
    let imageUrl = '';
    if (fragment.imageNode.status === 'completed' && fragment.imageNode.output) {
      imageUrl = (fragment.imageNode.output as any).url;
    } else {
      alert('无法获取图片URL');
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

    // 模拟进度（视频生成约需30-90秒，根据时长）
    const estimatedTime = Math.max(30000, fragment.duration * 15000); // 根据视频时长估算
    const updateInterval = 500; // 每500ms更新一次
    let progress = 0;

    const progressTimer = setInterval(() => {
      progress += (updateInterval / estimatedTime) * 100;
      if (progress > 95) progress = 95; // 最高到95%，等待实际完成
      setVideoProgress(prev => ({
        ...prev,
        [fragment.fragment_id]: Math.min(progress, 95),
      }));
    }, updateInterval);

    try {
      // 调用后端 API 生成视频
      const response = await axios.post(`${API_URL}/generation/generate/video`, {
        image_url: imageUrl,
        prompt: fragment.prompt,
        duration: fragment.duration,
        fps: 25,
        enable_audio: false,  // 默认不生成音频
      });

      clearInterval(progressTimer);
      setVideoProgress(prev => ({ ...prev, [fragment.fragment_id]: 100 }));

      if (response.data.success && response.data.video_url) {
        setFragments(prev => prev.map(frag => {
          if (frag.fragment_id === fragment.fragment_id) {
            return {
              ...frag,
              videoNode: {
                status: 'completed',
                dependsOn: 'image',
                result: response.data,
                output: response.data.video_url,
                model: response.data.model,
                modelName: response.data.model_name,
              },
            };
          }
          return frag;
        }));

        // 延迟移除进度条
        setTimeout(() => {
          setVideoProgress(prev => {
            const newProgress = { ...prev };
            delete newProgress[fragment.fragment_id];
            return newProgress;
          });
        }, 2000);
      } else {
        throw new Error('视频生成失败');
      }

    } catch (error: any) {
      clearInterval(progressTimer);
      setVideoProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[fragment.fragment_id];
        return newProgress;
      });

      console.error('视频生成错误:', error);
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
      alert(`视频生成失败: ${error.response?.data?.detail || error.message}`);
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

  // 保存为演示案例
  const saveAsDemoCase = async () => {
    const completedImages = fragments.filter(f => f.imageNode.status === 'completed').length;
    const completedVideos = fragments.filter(f => f.videoNode.status === 'completed').length;

    if (completedImages === 0 && completedVideos === 0) {
      alert('请先生成至少一张图片或视频后再保存为演示案例！');
      return;
    }

    try {
      const demoData = {
        title: currentProject?.title || '未命名项目',
        description: currentProject?.description || `AI生成的演示案例 - ${completedImages}张图片, ${completedVideos}个视频`,
        script: scriptInput,
        total_duration: targetDuration,
        fragments: fragments,
        total_images: completedImages,
        total_videos: completedVideos,
      };

      let savedCase;
      if (demoCaseId) {
        // 更新现有案例
        savedCase = await demoCaseService.updateDemoCase(demoCaseId, demoData);
        console.log('✅ 演示案例已更新:', savedCase.id);
      } else {
        // 创建新案例
        savedCase = await demoCaseService.saveAsDemoCase(demoData);
        setDemoCaseId(savedCase.id);
        console.log('✅ 已保存为演示案例:', savedCase.id);
      }

      alert(`✅ ${demoCaseId ? '更新' : '保存'}为演示案例成功！\n\n案例ID: ${savedCase.id}\n图片: ${completedImages}张\n视频: ${completedVideos}个\n\n该案例将在主页展示给所有用户。`);
    } catch (error: any) {
      console.error('保存演示案例失败:', error);
      alert(`保存失败: ${error.response?.data?.detail || error.message}`);
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

    for (const line of selectedLines) {
      const fragment = fragments.find(f => f.fragment_id === line.id);
      if (!fragment) continue;

      if (fragment.imageNode.status === 'pending' || fragment.imageNode.status === 'error') {
        await executeImageGeneration(fragment);
      }

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
    const completedVideos = fragments.filter(f => f.videoNode.status === 'completed');

    if (completedVideos.length !== fragments.length) {
      alert(`请等待所有视频生成完成！\n当前进度: ${completedVideos.length}/${fragments.length}`);
      return;
    }

    setCompositionStatus('running');

    try {
      const videoUrls = fragments.map(f => f.videoNode.output).filter(Boolean);

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

  // 下载图片
  const downloadImage = async (fragment: Fragment) => {
    if (fragment.imageNode.status !== 'completed' || !fragment.imageNode.output) {
      alert('请先生成图片！');
      return;
    }

    const imageUrl = (fragment.imageNode.output as any).url;
    try {
      // 使用后端代理下载，避免CORS问题
      const proxyUrl = `${API_URL}/generation/proxy/download?url=${encodeURIComponent(imageUrl)}`;
      const response = await fetch(proxyUrl);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fragment_${fragment.number}_image.jpg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('下载图片失败:', error);
      alert('下载图片失败，请尝试在新窗口打开图片链接手动保存。');
    }
  };

  // 下载视频
  const downloadVideo = async (fragment: Fragment) => {
    if (fragment.videoNode.status !== 'completed' || !fragment.videoNode.output) {
      alert('请先生成视频！');
      return;
    }

    const videoUrl = fragment.videoNode.output as string;
    try {
      // 使用后端代理下载，避免CORS问题
      const proxyUrl = `${API_URL}/generation/proxy/download?url=${encodeURIComponent(videoUrl)}`;
      const response = await fetch(proxyUrl);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fragment_${fragment.number}_video.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('下载视频失败:', error);
      alert('下载视频失败，请尝试在新窗口打开视频链接手动保存。');
    }
  };

  // 批量下载所有图片
  const downloadAllImages = async () => {
    const completedFragments = fragments.filter(f => f.imageNode.status === 'completed');
    if (completedFragments.length === 0) {
      alert('没有已生成的图片！');
      return;
    }

    for (const fragment of completedFragments) {
      await downloadImage(fragment);
      // 间隔500ms避免浏览器阻止多个下载
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  };

  // 批量下载所有视频
  const downloadAllVideos = async () => {
    const completedFragments = fragments.filter(f => f.videoNode.status === 'completed');
    if (completedFragments.length === 0) {
      alert('没有已生成的视频！');
      return;
    }

    for (const fragment of completedFragments) {
      await downloadVideo(fragment);
      // 间隔500ms避免浏览器阻止多个下载
      await new Promise(resolve => setTimeout(resolve, 500));
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
          {fragments.length > 0 && lastSavedTime && (
            <div
              style={{
                fontSize: '0.75rem',
                opacity: 0.7,
                marginRight: '12px',
                textAlign: 'right'
              }}
              title="所有进度已自动保存到浏览器本地存储"
            >
              💾 已保存<br/>{lastSavedTime}
            </div>
          )}
          {fragments.length > 0 && (
            <>
              <button
                className="icon-btn"
                onClick={saveAsDemoCase}
                style={{ marginRight: '8px' }}
                title="保存为演示案例，展示给所有用户"
              >
                🌟 保存为演示
              </button>
              <button
                className="icon-btn"
                onClick={() => {
                  if (confirm('确定要清除所有保存的进度吗？此操作不可恢复。')) {
                    clearSavedState();
                    setLastSavedTime(null);
                    setDemoCaseId(null);  // 清除演示案例ID
                    // 重置状态
                    setFragments([]);
                    setExpandedFragments(new Set());
                    setExecutionLines([]);
                    setCompositionStatus('pending');
                    setCompositionResult(null);
                    setScriptInput('');
                    setImageProgress({});
                    setVideoProgress({});
                  }
                }}
                title="清除保存的进度"
              >
                🗑️ 清除进度
              </button>
            </>
          )}
          <button className="icon-btn">⚙️</button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="sifi-content">
        {/* 剧本输入区 */}
        <div className="input-section">
          <div className="section-title">📝 剧本输入</div>
          {fragments.length === 0 && (
            <div style={{
              background: 'rgba(100, 200, 255, 0.1)',
              border: '1px solid rgba(100, 200, 255, 0.3)',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '12px',
              fontSize: '0.875rem'
            }}>
              💡 <strong>新手提示</strong>：想先看看效果？点击下方"🎬 加载演示项目"按钮，立即查看包含示例图片和视频的完整演示！
            </div>
          )}
          <textarea
            className="script-input"
            placeholder="在此输入你的剧本或创作需求..."
            value={scriptInput}
            onChange={(e) => setScriptInput(e.target.value)}
            rows={6}
            disabled={fragments.length > 0}
          />
          {fragments.length === 0 && (
            <>
              <div className="duration-selector">
                <label>⏱️ 目标视频总时长：</label>
                <select
                  value={targetDuration}
                  onChange={(e) => setTargetDuration(Number(e.target.value))}
                  className="duration-select"
                >
                  <option value={10}>10秒</option>
                  <option value={15}>15秒</option>
                  <option value={20}>20秒</option>
                  <option value={30}>30秒</option>
                  <option value={45}>45秒</option>
                  <option value={60}>60秒</option>
                </select>
                <span className="duration-hint">
                  系统将根据总时长自动分配分镜数量和时长
                </span>
              </div>
              <div className="input-actions">
                <button
                  className="btn-secondary"
                  onClick={loadDemoProject}
                  disabled={isAnalyzing}
                  style={{ marginRight: '12px' }}
                  title="加载包含示例图片和视频的演示项目"
                >
                  🎬 加载演示项目
                </button>
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
            </>
          )}
        </div>

        {/* 演示画廊 - 只在演示模式下显示 */}
        {isDemoMode && showDemoGallery && fragments.length > 0 && (
          <div style={{
            background: 'rgba(0, 20, 40, 0.6)',
            border: '2px solid rgba(0, 255, 255, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* 关闭按钮 */}
            <button
              onClick={() => setShowDemoGallery(false)}
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'rgba(255, 100, 100, 0.2)',
                border: '1px solid rgba(255, 100, 100, 0.5)',
                color: '#ff6b6b',
                borderRadius: '8px',
                padding: '8px 16px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                transition: 'all 0.3s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 100, 100, 0.4)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 100, 100, 0.2)'}
            >
              ✕ 关闭画廊
            </button>

            {/* 标题 */}
            <div style={{
              textAlign: 'center',
              marginBottom: '24px'
            }}>
              <h2 style={{
                color: '#00ffff',
                fontSize: '1.75rem',
                margin: '0 0 8px 0',
                textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
              }}>
                🎨 AI生成作品展示
              </h2>
              <p style={{
                color: 'rgba(255, 255, 255, 0.7)',
                fontSize: '0.9rem',
                margin: 0
              }}>
                以下是为您生成的示例图片和视频，展示AI的创作能力
              </p>
            </div>

            {/* 内容网格 */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '20px',
              marginBottom: '20px'
            }}>
              {fragments.map((fragment, index) => {
                const hasImage = fragment.imageNode.status === 'completed' && fragment.imageNode.output;
                const hasVideo = fragment.videoNode.status === 'completed' && fragment.videoNode.output;

                if (!hasImage && !hasVideo) return null;

                return (
                  <div
                    key={fragment.fragment_id}
                    style={{
                      background: 'rgba(0, 0, 0, 0.4)',
                      border: `2px solid ${fragment.color}`,
                      borderRadius: '12px',
                      padding: '16px',
                      transition: 'all 0.3s'
                    }}
                  >
                    {/* 分镜标题 */}
                    <div style={{
                      color: fragment.color,
                      fontSize: '1.1rem',
                      fontWeight: 'bold',
                      marginBottom: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <span>🎯 分镜 {fragment.number}</span>
                      <span style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                        ({fragment.duration}秒)
                      </span>
                    </div>

                    {/* 提示词 */}
                    <div style={{
                      color: 'rgba(255, 255, 255, 0.8)',
                      fontSize: '0.85rem',
                      marginBottom: '12px',
                      lineHeight: '1.4',
                      fontStyle: 'italic'
                    }}>
                      "{fragment.prompt}"
                    </div>

                    {/* 图片展示 */}
                    {hasImage && (
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{
                          color: '#4ECDC4',
                          fontSize: '0.8rem',
                          marginBottom: '6px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}>
                          <span>🖼️</span>
                          <span>AI生成图片</span>
                          {fragment.imageNode.modelName && (
                            <span style={{ fontSize: '0.75rem', opacity: 0.6 }}>
                              ({fragment.imageNode.modelName})
                            </span>
                          )}
                        </div>
                        <img
                          src={fragment.imageNode.output?.url}
                          alt={`分镜${fragment.number}`}
                          style={{
                            width: '100%',
                            borderRadius: '8px',
                            border: '1px solid rgba(255, 255, 255, 0.1)'
                          }}
                        />
                      </div>
                    )}

                    {/* 视频展示 */}
                    {hasVideo && (
                      <div>
                        <div style={{
                          color: '#FF6B6B',
                          fontSize: '0.8rem',
                          marginBottom: '6px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}>
                          <span>🎬</span>
                          <span>AI生成视频</span>
                          {fragment.videoNode.modelName && (
                            <span style={{ fontSize: '0.75rem', opacity: 0.6 }}>
                              ({fragment.videoNode.modelName})
                            </span>
                          )}
                        </div>
                        <video
                          src={fragment.videoNode.output as string}
                          controls
                          style={{
                            width: '100%',
                            borderRadius: '8px',
                            border: '1px solid rgba(255, 255, 255, 0.1)'
                          }}
                        />
                      </div>
                    )}

                    {/* 待生成提示 */}
                    {!hasImage && !hasVideo && (
                      <div style={{
                        color: 'rgba(255, 255, 255, 0.5)',
                        fontSize: '0.85rem',
                        textAlign: 'center',
                        padding: '20px',
                        fontStyle: 'italic'
                      }}>
                        等待生成...
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* 统计信息 */}
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '32px',
              flexWrap: 'wrap',
              paddingTop: '16px',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '0.9rem'
            }}>
              <div>
                <strong style={{ color: '#00ffff' }}>📊 统计：</strong>
                {fragments.filter(f => f.imageNode.status === 'completed').length} 张图片 ·
                {fragments.filter(f => f.videoNode.status === 'completed').length} 个视频
              </div>
              <div>
                <strong style={{ color: '#00ffff' }}>⏱️ 总时长：</strong>
                {fragments.reduce((sum, f) => sum + f.duration, 0).toFixed(1)} 秒
              </div>
            </div>
          </div>
        )}

        {/* 分镜矩阵 */}
        {fragments.length > 0 && (
          <>
            <div className="matrix-section">
              <div className="section-title">
                🎯 分镜设计矩阵
                <span className="fragment-count">[{fragments.length}个分镜 | 总时长: {fragments.reduce((sum, f) => sum + f.duration, 0).toFixed(1)}秒]</span>
                <span className="save-status">💾 进度自动保存中...</span>
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
              <div className="section-title">
                🎬 工作流构建区
                <div className="batch-actions">
                  <button
                    className="btn-secondary"
                    onClick={downloadAllImages}
                    disabled={!fragments.some(f => f.imageNode.status === 'completed')}
                  >
                    📥 批量下载图片
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={downloadAllVideos}
                    disabled={!fragments.some(f => f.videoNode.status === 'completed')}
                  >
                    🎥 批量下载视频
                  </button>
                </div>
              </div>

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
                          {imageProgress[fragment.fragment_id] !== undefined && (
                            <div className="progress-bar">
                              <div
                                className="progress-fill"
                                style={{
                                  width: `${imageProgress[fragment.fragment_id]}%`,
                                  background: fragment.color,
                                }}
                              />
                              <span className="progress-text">
                                {Math.round(imageProgress[fragment.fragment_id])}%
                              </span>
                            </div>
                          )}
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
                          {fragment.imageNode.modelName && (
                            <div className="model-info" style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '4px' }}>
                              🤖 模型: {fragment.imageNode.modelName}
                            </div>
                          )}
                          <div className="node-actions">
                            <button onClick={() => regenerateNode(fragment, 'image')}>🔄 重新生成</button>
                            <button onClick={() => downloadImage(fragment)}>📥 下载图片</button>
                          </div>
                        </div>
                      )}

                      {fragment.imageNode.status === 'error' && (
                        <div className="node-error" style={{ padding: '12px' }}>
                          <div style={{ color: '#ff6b6b', marginBottom: '8px' }}>❌ 图片生成失败</div>
                          <div className="node-actions">
                            <button
                              onClick={() => regenerateNode(fragment, 'image')}
                              style={{ background: fragment.color }}
                            >
                              🔄 重新生成图片
                            </button>
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
                          {videoProgress[fragment.fragment_id] !== undefined && (
                            <div className="progress-bar">
                              <div
                                className="progress-fill"
                                style={{
                                  width: `${videoProgress[fragment.fragment_id]}%`,
                                  background: fragment.color,
                                }}
                              />
                              <span className="progress-text">
                                {Math.round(videoProgress[fragment.fragment_id])}%
                              </span>
                            </div>
                          )}
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
                          {fragment.videoNode.modelName && (
                            <div className="model-info" style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '4px' }}>
                              🤖 模型: {fragment.videoNode.modelName}
                            </div>
                          )}
                          <div className="node-actions">
                            <button onClick={() => regenerateNode(fragment, 'video')}>🔄 重新生成</button>
                            <button onClick={() => downloadVideo(fragment)}>📥 下载视频</button>
                          </div>
                        </div>
                      )}

                      {fragment.videoNode.status === 'error' && (
                        <div className="node-error" style={{ padding: '12px' }}>
                          <div style={{ color: '#ff6b6b', marginBottom: '8px' }}>❌ 视频生成失败</div>
                          <div className="node-actions">
                            <button
                              onClick={() => regenerateNode(fragment, 'video')}
                              style={{ background: fragment.color }}
                            >
                              🔄 重新生成视频
                            </button>
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
