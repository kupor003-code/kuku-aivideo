# 完整的镜头生成工作流程

## 系统架构概览

这个系统实现了一个完全手动控制的分镜头生成流程，支持在对话框和 Canvas 中同时进行实时进度同步。

### 核心特性

1. **完全手动流程** - 用户手动点击按钮触发生成
2. **对话框与 Canvas 实时同步** - 生成进度和结果同步显示在两个位置
3. **镜头级别控制** - 每个镜头有独立的生成、暂停、继续控制
4. **实时进度反馈** - 生成过程中实时显示进度百分比

---

## 核心组件与服务

### 1. 事件系统 - `generationEventService`
**文件**: `frontend/src/services/generationEventService.ts`

**职责**:
- 管理生成事件的发布/订阅
- 追踪每个镜头的生成进度
- 支持镜头级别的事件（进度更新、完成、失败）

**关键方法**:
- `subscribe(eventType, callback)` - 订阅事件
- `updateProgress(shotId, progress)` - 更新进度
- `startImageGeneration(shotId, shotNumber)` - 开始图片生成
- `completeImageGeneration(shotId, shotNumber, imageIds, imageUrls)` - 图片生成完成
- `startVideoGeneration(shotId, shotNumber)` - 开始视频生成
- `completeVideoGeneration(shotId, shotNumber, videoId, videoUrl)` - 视频生成完成

### 2. API 调用服务 - `shotGenerationService`
**文件**: `frontend/src/services/shotGenerationService.ts`

**职责**:
- 调用后端 API 执行生成任务
- 轮询获取生成进度
- 发射事件到 `generationEventService`

**关键方法**:
- `generateShotImages(projectId, shot, basePrompt)` - 生成镜头图片
- `generateVideo(projectId, shot, imageIds, basePrompt)` - 生成视频
- `pauseShotGeneration(shotGenId)` - 暂停生成
- `resumeShotGeneration(shotGenId)` - 继续生成

### 3. 镜头生成面板 - `ShotGenerationPanel`
**文件**: `frontend/src/components/ShotGenerationPanel.tsx`

**职责**:
- 显示镜头列表
- 为每个镜头提供生成按钮
- 显示实时进度和状态

**特性**:
- 显示生成中的进度条
- 显示生成错误信息
- 已生成图片后启用视频生成按钮
- 实时订阅生成进度事件

### 4. 对话框组件 - `ConversationPanel`
**文件**: `frontend/src/components/ConversationPanel.tsx`

**职责**:
- 显示 AI 对话消息
- 集成 `ShotGenerationPanel` 显示镜头列表
- 处理图片和视频生成请求
- 同步生成结果到 Canvas

**工作流**:
1. 用户发送消息到 AI
2. AI 返回带镜头数据的消息
3. `ShotGenerationPanel` 显示镜头列表
4. 用户点击生成按钮
5. 调用 `shotGenerationService.generateShotImages()`
6. 实时更新进度
7. 触发 `shot-image-generated` 事件
8. Canvas 接收事件并更新显示

### 5. Canvas 节点组件 - `StoryboardNode`
**文件**: `frontend/src/components/canvas/StoryboardNode.tsx`

**职责**:
- 显示分镜头及其预览图片
- 展示镜头级别的生成任务列表
- 监听来自对话框的生成完成事件
- 实时显示生成进度

**事件监听**:
- `shot-image-generated` - 图片生成完成，更新显示
- `shot-video-generated` - 视频生成完成
- `progress` - 实时进度更新

---

## 完整工作流程

### 场景 1：在对话框中生成图片

```
用户输入 "请创建一个关于未来城市的视频"
    ↓
AI Agent 生成分镜头列表（返回 shots_data）
    ↓
ConversationPanel 接收 shots_data
    ↓
ShotGenerationPanel 显示所有镜头
    ↓
用户点击"生成图片"按钮（针对镜头 #1）
    ↓
generationEventService.startImageGeneration() ← 立即发射事件
    ↓
ShotGenerationPanel 和 StoryboardNode 都显示"生成中"
    ↓
shotGenerationService.generateShotImages() ← 调用后端 API
    ↓
轮询状态（每 1 秒）
    ↓
generationEventService.updateImageProgress() ← 实时更新进度
    ↓
进度条更新，两个面板都可以看到
    ↓
生成完成 → generationEventService.completeImageGeneration()
    ↓
触发 window.dispatchEvent('shot-image-generated', {...})
    ↓
StoryboardNode 接收事件，添加图片到显示
    ↓
Canvas 中的预览图片更新
```

### 场景 2：生成视频（需要先有图片）

```
镜头已有图片（来自场景 1）
    ↓
用户点击"生成视频"按钮（针对镜头 #1）
    ↓
generationEventService.startVideoGeneration() ← 立即发射事件
    ↓
两个面板显示"视频生成中"
    ↓
shotGenerationService.generateVideo() ← 调用后端 API
    ↓
轮询状态
    ↓
generationEventService.updateVideoProgress()
    ↓
进度条更新
    ↓
生成完成 → generationEventService.completeVideoGeneration()
    ↓
触发 window.dispatchEvent('shot-video-generated', {...})
    ↓
Canvas 中可以播放视频
```

### 场景 3：在 Canvas 中直接生成（如果已有镜头数据）

```
如果 StoryboardNode 已有 shots 数据
    ↓
用户可以在 Canvas 中展开节点
    ↓
查看镜头生成任务列表
    ↓
点击"生成"按钮（针对镜头）
    ↓
调用相同的 shotGenerationService 方法
    ↓
进度同步到对话框中的 ShotGenerationPanel
    ↓
（流程与场景 1 相同）
```

---

## 事件流图

```
┌─────────────────────────────────────────────────────────────┐
│                    generationEventService                    │
│                     事件总线（单例）                         │
└─────────────────────────────────────────────────────────────┘
                        ▲  ▲
                        │  │
                ┌───────┘  └───────┐
                │                  │
                │                  │
         发射事件              订阅事件
                │                  │
    ┌───────────▼─────────────┬──┬─┴─────────────┐
    │                         │  │               │
    │  shotGenerationService  │  │ ShotGenerationPanel
    │  (调用 API，轮询)      │  │ (显示进度)
    │                         │  │
    │                         │  │ StoryboardNode
    │                         │  │ (显示进度和图片)
    └─────────────────────────┴──┴─────────────────┘
```

---

## 关键的事件类型

### 来自 `generationEventService`

1. **'progress'** - 任何镜头的进度更新
   ```
   {
     shot_id: string,
     shot_number: number,
     type: 'image' | 'video',
     status: 'pending' | 'generating' | 'paused' | 'completed' | 'failed',
     progress: 0-100,
     message?: string,
     error?: string
   }
   ```

2. **'progress:{shotId}'** - 特定镜头的进度更新

3. **'image-generation-complete'** - 图片生成完成
   ```
   {
     shotId: string,
     shotNumber: number,
     imageIds: string[],
     imageUrls: string[]
   }
   ```

4. **'video-generation-complete'** - 视频生成完成
   ```
   {
     shotId: string,
     shotNumber: number,
     videoId: string,
     videoUrl: string
   }
   ```

### Window 事件

1. **'shot-image-generated'** - 通知 Canvas 图片已生成
2. **'shot-video-generated'** - 通知 Canvas 视频已生成

---

## 使用指南

### 1. 在 ConversationPanel 中使用

```typescript
// ConversationPanel 会自动：
// 1. 检查 AI 返回的消息中是否有 shots_data
// 2. 如果有，显示 ShotGenerationPanel
// 3. 用户可以点击按钮生成图片/视频
// 4. 进度实时显示，完成后结果同步到 Canvas
```

### 2. 在 Canvas 中使用

```typescript
// StoryboardNode 会：
// 1. 显示镜头列表（如果节点有 shots 数据）
// 2. 允许用户点击生成按钮
// 3. 实时显示进度
// 4. 自动接收和显示来自对话框的结果
```

### 3. 订阅进度事件

```typescript
import { generationEventService } from '../services/generationEventService';

// 订阅所有镜头的进度
const unsubscribe = generationEventService.subscribe('progress', (progress) => {
  console.log(`镜头 ${progress.shot_number}: ${progress.progress}%`);
});

// 订阅特定镜头的进度
const unsubscribe2 = generationEventService.subscribe('progress:shot-123', (progress) => {
  console.log(`特定镜头: ${progress.progress}%`);
});

// 订阅图片生成完成
const unsubscribe3 = generationEventService.subscribe('image-generation-complete', (data) => {
  console.log(`图片已生成:`, data.imageUrls);
});
```

---

## 后端要求

后端需要提供以下 API 端点：

### 1. 生成镜头图片
```
POST /api/v1/storyboard/shots/generate
Request: {
  project_id: string,
  shot_number: number,
  shot_description: string,
  prompt: string,
  size: string,
  n: number
}
Response: {
  shot_gen_id: string
}
```

### 2. 查询生成状态
```
GET /api/v1/storyboard/shots/{shotGenId}/status
Response: {
  status: 'pending' | 'generating' | 'completed' | 'failed',
  progress: 0-100,
  image_ids?: string[],
  image_urls?: string[],
  error?: string
}
```

### 3. 生成视频
```
POST /api/v1/storyboard/videos/generate
Request: {
  project_id: string,
  shot_number: number,
  image_ids: string[],
  prompt: string,
  duration: number
}
Response: {
  video_gen_id: string
}
```

### 4. 查询视频状态
```
GET /api/v1/storyboard/videos/{videoGenId}/status
Response: {
  status: 'pending' | 'generating' | 'completed' | 'failed',
  progress: 0-100,
  video_id?: string,
  video_url?: string,
  error?: string
}
```

---

## 数据流总结

```
┌──────────────────────────────────────────────────────────────┐
│                      AI Agent                                 │
│              返回 shots_data 和 prompt                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │   ConversationPanel        │
            │  接收 shots_data           │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │   ShotGenerationPanel      │
            │  显示镜头列表和控制        │
            └────────────┬───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │ 用户点击生成  │               │
         ▼               │               ▼
    generationEvent      │         shotGenerationService
    Service 发射事件     │         调用后端 API
         │               │               │
         │ 订阅关系      │ 轮询状态      │
         │               │               │
         └───────────────┼───────────────┘
                         │
            ┌────────────▼────────────┐
            │   StoryboardNode        │
            │  订阅事件，实时更新     │
            │  显示进度和结果         │
            └─────────────────────────┘
```

---

## 注意事项

1. **完全手动流程** - 没有自动链式生成，用户必须明确点击按钮
2. **实时同步** - 对话框和 Canvas 通过事件系统同步，无需轮询
3. **错误处理** - 所有错误都会显示在 UI 中
4. **进度追踪** - 每个镜头的进度独立追踪
5. **生成隔离** - 不同镜头的生成不会互相影响
