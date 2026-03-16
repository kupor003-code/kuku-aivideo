# 镜头生成系统集成指南

## 概述

本指南说明如何将新的镜头生成系统集成到现有的 Canvas 和 ConversationPanel 中。

---

## 新增文件

### 前端新增文件

#### 1. 服务层

**文件**: `frontend/src/services/generationEventService.ts`
- **作用**: 事件发布/订阅系统，所有生成进度通过此系统分发
- **导入方式**: 
  ```typescript
  import { generationEventService } from '../services/generationEventService';
  ```

**文件**: `frontend/src/services/shotGenerationService.ts`
- **作用**: 调用后端 API，轮询生成状态
- **导入方式**:
  ```typescript
  import { 
    generateShotImages, 
    generateVideo,
    pauseShotGeneration,
    resumeShotGeneration
  } from '../services/shotGenerationService';
  ```

#### 2. UI 组件

**文件**: `frontend/src/components/ShotGenerationPanel.tsx`
- **作用**: 显示镜头列表和生成控制按钮
- **使用**:
  ```typescript
  import { ShotGenerationPanel } from './ShotGenerationPanel';
  
  <ShotGenerationPanel
    projectId={projectId}
    shots={shots}
    onGenerateImage={handleGenerateImage}
    onGenerateVideo={handleGenerateVideo}
  />
  ```

**文件**: `frontend/src/components/ShotGenerationPanel.css`
- **作用**: ShotGenerationPanel 的样式

---

## 修改的文件

### 1. ConversationPanel 修改

**文件**: `frontend/src/components/ConversationPanel.tsx`

#### 新增 imports
```typescript
import { ShotGenerationPanel } from './ShotGenerationPanel';
import { generateShotImages, generateVideo } from '../services/shotGenerationService';
import { generationEventService } from '../services/generationEventService';
```

#### 新增 props
```typescript
interface ConversationPanelProps {
  // ... 现有 props ...
  onShotsUpdate?: (shots: any[]) => void; // 用于更新Canvas中的镜头数据
}
```

#### 新增 state
```typescript
const [shots, setShots] = useState<Shot[]>([]);
const [basePrompt, setBasePrompt] = useState('');
const [generatedImages, setGeneratedImages] = useState<Map<string, string[]>>(new Map());
```

#### 新增生命周期
```typescript
// 订阅生成完成事件
useEffect(() => {
  const unsubscribeImageComplete = generationEventService.subscribe('image-generation-complete', (data: any) => {
    setGeneratedImages(prev => new Map(prev).set(data.shotId, data.imageUrls || []));
  });

  return () => {
    unsubscribeImageComplete();
  };
}, []);
```

#### 修改 loadMessages
```typescript
const loadMessages = async () => {
  try {
    const data = await conversationService.getMessages(projectId);
    setMessages(data);

    // 检查最后一条消息中是否有镜头数据
    if (data.length > 0) {
      const lastMessage = data[data.length - 1];
      if (lastMessage.shots_data && lastMessage.shots_data.length > 0) {
        const shotsData = lastMessage.shots_data;
        setShots(shotsData);
        setBasePrompt(lastMessage.content);
        
        // 通知Canvas更新
        if (onShotsUpdate) {
          onShotsUpdate(shotsData);
        }
      }
    }
  } catch (error) {
    console.error('Failed to load messages:', error);
  }
};
```

#### 新增处理函数
```typescript
// 处理生成图片
const handleGenerateImage = async (shot: Shot) => {
  try {
    const result = await generateShotImages(projectId, shot, basePrompt);
    console.log('图片生成完成:', result);
    
    // 触发事件以通知Canvas更新
    window.dispatchEvent(new CustomEvent('shot-image-generated', {
      detail: {
        shotId: shot.id,
        shotNumber: shot.shot_number,
        imageIds: result.imageIds,
        imageUrls: result.imageUrls,
      }
    }));
  } catch (error) {
    console.error('生成图片失败:', error);
  }
};

// 处理生成视频
const handleGenerateVideo = async (shot: Shot) => {
  try {
    const imageUrls = generatedImages.get(shot.id);
    if (!imageUrls || imageUrls.length === 0) {
      alert('请先生成图片');
      return;
    }

    const result = await generateVideo(projectId, shot, [], basePrompt);
    console.log('视频生成完成:', result);

    // 触发事件以通知Canvas更新
    window.dispatchEvent(new CustomEvent('shot-video-generated', {
      detail: {
        shotId: shot.id,
        shotNumber: shot.shot_number,
        videoId: result.videoId,
        videoUrl: result.videoUrl,
      }
    }));
  } catch (error) {
    console.error('生成视频失败:', error);
  }
};
```

#### 修改 JSX
在消息列表前添加：
```typescript
{/* 镜头生成面板 */}
{shots.length > 0 && (
  <div className="shot-generation-container">
    <ShotGenerationPanel
      projectId={projectId}
      shots={shots}
      onGenerateImage={handleGenerateImage}
      onGenerateVideo={handleGenerateVideo}
    />
  </div>
)}
```

#### 修改 CSS
在 `ConversationPanel.css` 中添加：
```css
.shot-generation-container {
  padding: 12px;
  border-bottom: 1px solid var(--color-border-default);
  max-height: 400px;
  overflow-y: auto;
}
```

---

### 2. StoryboardNode 修改

**文件**: `frontend/src/components/canvas/StoryboardNode.tsx`

#### 新增 imports
```typescript
import { generationEventService } from '../../services/generationEventService';
```

#### 新增 state
```typescript
const [currentShots, setCurrentShots] = useState<Shot[]>(nodeData.shots || []);
const [currentImages, setCurrentImages] = useState<Array<{ id: string; url: string }> | undefined>(nodeData.images);
const [activeImageIndex, setActiveImageIndex] = useState(0);
```

#### 新增生命周期 - 监听事件
```typescript
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
```

#### 新增生命周期 - 订阅进度
```typescript
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
```

#### 在 JSX 中使用 currentShots 和 currentImages
```typescript
// 在显示图片时使用 currentImages 而不是 nodeData.images
<img src={currentImages![activeImageIndex].url} alt="分镜预览" />

// 在显示镜头列表时使用 currentShots 而不是 nodeData.shots
{currentShots && currentShots.length > 0 && (
  <div className="shots-generation-list">
    {currentShots.map((shot) => (...))}
  </div>
)}
```

---

## 调用方式

### 在应用根组件中使用

```typescript
// App.tsx 或类似的顶级组件

function App() {
  const [projectId, setProjectId] = useState('');

  const handleShotsUpdate = (shots: any[]) => {
    // 这里可以更新 Canvas 中的节点数据
    console.log('Shots updated:', shots);
  };

  return (
    <div>
      <ConversationPanel
        projectId={projectId}
        onNodesUpdate={() => {}}
        onEdgesUpdate={() => {}}
        onShotsUpdate={handleShotsUpdate}  // 新增
      />
      {/* Canvas 组件 */}
    </div>
  );
}
```

---

## 数据流集成

### API 消息结构

后端返回的消息应包含 `shots_data` 字段：

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  agent_type?: string;
  agent_name?: string;
  created_at: string;
  related_node_id?: string;
  shots_data?: Shot[];  // 新增
}

interface Shot {
  id: string;
  shot_number: number;
  shot_description: string;
  prompt?: string;
}
```

### Canvas 节点数据结构

StoryboardNode 应接收包含 `shots` 的数据：

```typescript
interface StoryboardNodeData {
  label?: string;
  total_scenes?: number;
  total_shots?: number;
  shots?: Shot[];  // 新增
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
```

---

## 环境变量

确保 `.env` 或 `.env.local` 中设置：

```
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 依赖项

确保已安装以下包：

```
react
react-dom
@xyflow/react
lucide-react
```

无需添加新的依赖项！

---

## 后端集成检查清单

- [ ] `/api/v1/storyboard/shots/generate` - POST 端点已实现
- [ ] `/api/v1/storyboard/shots/{id}/status` - GET 端点已实现
- [ ] `/api/v1/storyboard/videos/generate` - POST 端点已实现
- [ ] `/api/v1/storyboard/videos/{id}/status` - GET 端点已实现
- [ ] Storyboard Agent 返回 `shots_data` 字段
- [ ] 返回的 Shot 对象包含 `id`, `shot_number`, `shot_description`

---

## 前端集成检查清单

- [ ] `generationEventService.ts` 已创建
- [ ] `shotGenerationService.ts` 已创建
- [ ] `ShotGenerationPanel.tsx` 已创建
- [ ] `ShotGenerationPanel.css` 已创建
- [ ] `ConversationPanel.tsx` 已更新
- [ ] `ConversationPanel.css` 已更新（新增 `.shot-generation-container`）
- [ ] `StoryboardNode.tsx` 已更新
- [ ] 所有导入路径正确
- [ ] 没有 TypeScript 错误
- [ ] 没有 linter 错误

---

## 常见集成问题

### 问题 1：找不到模块

**错误**: `Cannot find module './ShotGenerationPanel'`

**解决**: 确保文件路径正确，文件确实存在

### 问题 2：事件未接收

**错误**: StoryboardNode 中的图片不更新

**原因**: 可能是事件名称拼写错误

**解决**:
```typescript
// 确保事件名称一致
// 发射: 'shot-image-generated'
// 监听: 'shot-image-generated'
```

### 问题 3：进度不更新

**错误**: 生成中但进度条不动

**原因**: 后端可能没有返回 `progress` 字段

**解决**: 检查后端 `/status` 端点返回是否包含 `progress`

### 问题 4：视频按钮始终禁用

**错误**: 即使图片已生成，视频按钮仍禁用

**原因**: `generatedImages` Map 可能没有正确更新

**解决**: 确保 `image-generation-complete` 事件正确订阅

---

## 调试技巧

### 查看事件流

```typescript
// 在浏览器控制台中
import { generationEventService } from './services/generationEventService';

// 打印所有事件
const originalEmit = generationEventService.emit;
generationEventService.emit = function(eventType, data) {
  console.log('Event:', eventType, data);
  return originalEmit.call(this, eventType, data);
};
```

### 查看 API 调用

在浏览器 DevTools → Network 标签中查看：
- 所有对 `/api/v1/storyboard/*` 的请求
- 每个请求的返回数据

### React DevTools

使用 React DevTools 检查：
- ConversationPanel 的 state（shots, generatedImages）
- StoryboardNode 的 state（currentShots, currentImages）

---

## 性能优化建议

1. **事件防抖**: 如果进度更新过于频繁，可以在 `generationEventService` 中添加防抖
2. **内存管理**: 完成生成后清理进度 Map
3. **组件懒加载**: ShotGenerationPanel 仅在有镜头时渲染

---

## 扩展功能建议

1. **暂停/继续**: 实现 `pauseShotGeneration`/`resumeShotGeneration`
2. **重新生成**: 允许用户重新生成已完成的镜头
3. **批量操作**: 同时生成多个镜头
4. **进度预测**: 基于已完成时间预测剩余时间
5. **本地存储**: 保存生成历史到 localStorage

---

## 许可证和归属

此代码由 CatPaw 助手生成，可自由修改和使用。
