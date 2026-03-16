# 文件结构和概览

## 📁 新增文件位置

### 服务层 - `frontend/src/services/`

#### 1. `generationEventService.ts` (220 行)
**目的**: 中央事件系统，管理所有生成进度和结果

**关键方法**:
```typescript
subscribe(eventType, callback)           // 订阅事件
emit(eventType, data)                    // 发射事件
updateProgress(shotId, progress)         // 更新进度
startImageGeneration(shotId, shotNumber) // 开始图片生成
completeImageGeneration(...)             // 图片完成
```

**使用场景**:
- ShotGenerationPanel 订阅进度更新
- StoryboardNode 订阅进度更新
- 任何组件可以监听生成完成事件

---

#### 2. `shotGenerationService.ts` (200 行)
**目的**: 调用后端 API，处理轮询和错误

**关键方法**:
```typescript
generateShotImages(projectId, shot, basePrompt)  // 生成图片
generateVideo(projectId, shot, imageIds, prompt) // 生成视频
pauseShotGeneration(shotGenId)                   // 暂停生成
resumeShotGeneration(shotGenId)                  // 继续生成
```

**工作流**:
1. 调用后端 API
2. 获取 task_id
3. 每秒轮询状态
4. 更新到 generationEventService
5. 返回最终结果

---

### 组件层 - `frontend/src/components/`

#### 3. `ShotGenerationPanel.tsx` (180 行)
**目的**: 显示镜头列表和生成控制

**特性**:
- 显示所有镜头的列表
- 实时进度条（0-100%）
- 生成图片/视频按钮
- 错误提示
- 完成状态显示

**Props**:
```typescript
projectId: string
shots: Shot[]
onGenerateImage: (shot: Shot) => Promise<void>
onGenerateVideo: (shot: Shot) => Promise<void>
```

**事件**:
- 订阅 `generationEventService` 的 'progress' 事件
- 订阅 'image-generation-complete' 事件

---

#### 4. `ShotGenerationPanel.css` (280 行)
**目的**: ShotGenerationPanel 的样式

**特性**:
- 深色主题支持
- 响应式设计
- CSS 变量支持
- 平滑动画
- 无障碍设计

**关键类**:
```css
.shot-generation-panel        /* 主容器 */
.shot-item                    /* 单个镜头 */
.shot-action-btn              /* 操作按钮 */
.progress-bar                 /* 进度条 */
.shot-status                  /* 状态标签 */
```

---

## 🔧 修改的文件

### 1. `frontend/src/components/ConversationPanel.tsx`

**修改内容**:
- ✅ 添加 3 个新的 imports
- ✅ 修改 interface Props 添加 `onShotsUpdate`
- ✅ 添加 3 个新的 state hooks
- ✅ 添加 1 个新的 useEffect（生成完成事件订阅）
- ✅ 修改 `loadMessages` 函数以处理 shots_data
- ✅ 添加 `handleGenerateImage` 函数（30 行）
- ✅ 添加 `handleGenerateVideo` 函数（25 行）
- ✅ 在 JSX 中添加 ShotGenerationPanel 组件
- ✅ 添加 Canvas 同步事件触发

**行数变化**: +120 行

**关键片段**:
```typescript
// 新的状态
const [shots, setShots] = useState<Shot[]>([]);
const [generatedImages, setGeneratedImages] = useState<Map<string, string[]>>(new Map());

// 新的处理函数
const handleGenerateImage = async (shot: Shot) => {
  const result = await generateShotImages(projectId, shot, basePrompt);
  window.dispatchEvent(new CustomEvent('shot-image-generated', {...}));
};
```

---

### 2. `frontend/src/components/ConversationPanel.css`

**修改内容**:
- ✅ 添加 `.shot-generation-container` 样式类

**行数变化**: +8 行

```css
.shot-generation-container {
  padding: 12px;
  border-bottom: 1px solid var(--color-border-default);
  max-height: 400px;
  overflow-y: auto;
}
```

---

### 3. `frontend/src/components/canvas/StoryboardNode.tsx`

**修改内容**:
- ✅ 添加 `generationEventService` import
- ✅ 添加 `useEffect` import
- ✅ 修改 interface Shot（添加更多字段）
- ✅ 添加 currentShots state
- ✅ 添加 currentImages state
- ✅ 添加 activeImageIndex state
- ✅ 添加窗口事件监听 useEffect（40 行）
- ✅ 添加进度事件订阅 useEffect（20 行）
- ✅ 大量 JSX 更新以使用动态数据

**行数变化**: +180 行

**关键片段**:
```typescript
// 监听图片生成完成事件
window.addEventListener('shot-image-generated', handleImageGenerated);

// 订阅进度事件
generationEventService.subscribe('progress', (progress) => {
  setCurrentShots(prev => /* 更新进度 */);
});
```

---

## 📚 文档文件

### 核心文档

#### 1. `GENERATION_FLOW.md` (600 行)
**内容**: 完整的工作流程和架构设计
- 系统架构概览
- 核心组件说明
- 完整工作流程
- 事件流图
- 后端要求

**适合人群**: 想了解系统设计的人

---

#### 2. `TESTING_GUIDE.md` (500 行)
**内容**: 详细的测试指南和测试场景
- 快速开始
- 6 个完整的测试场景
- 测试检查清单
- 调试技巧
- 常见问题

**适合人群**: QA 和测试人员

---

#### 3. `INTEGRATION_GUIDE.md` (700 行)
**内容**: 详细的集成指南
- 新增文件清单
- 修改的文件说明
- 调用方式示例
- 数据流集成
- 常见集成问题

**适合人群**: 前端开发者

---

#### 4. `BACKEND_API_CONTRACT.md` (800 行)
**内容**: 后端 API 契约
- 完整的 API 端点规范
- 请求/响应格式
- 错误处理
- 性能要求
- 示例实现

**适合人群**: 后端开发者

---

### 参考文档

#### 5. `SYSTEM_SUMMARY.md` (600 行)
**内容**: 系统完整总结
- 项目概述
- 需求实现清单
- 架构设计
- 技术栈
- 可扩展性
- 已知限制

**适合人群**: 项目经理、架构师

---

#### 6. `QUICK_START.md` (150 行)
**内容**: 30 秒到 5 分钟快速了解
- 30 秒快速了解
- 5 分钟快速集成
- 工作流程
- API 端点
- 常见问题

**适合人群**: 急需了解的人

---

#### 7. `IMPLEMENTATION_CHECKLIST.md` (400 行)
**内容**: 实现和部署清单
- 前端实现状态
- 后端实现状态
- 集成清单
- 测试清单
- 发布前检查

**适合人群**: 项目经理、质量负责人

---

#### 8. `FILES_OVERVIEW.md` (本文件) (500 行)
**内容**: 文件结构和概览
- 所有文件的位置和用途
- 每个文件的关键内容
- 使用建议

**适合人群**: 所有人

---

## 📊 文件大小统计

### 代码文件

| 文件 | 行数 | 大小 |
|------|------|------|
| `generationEventService.ts` | 220 | 8 KB |
| `shotGenerationService.ts` | 200 | 7 KB |
| `ShotGenerationPanel.tsx` | 180 | 6 KB |
| `ShotGenerationPanel.css` | 280 | 10 KB |
| **新增代码总计** | **880** | **31 KB** |
| ConversationPanel.tsx (修改) | +120 | +4 KB |
| StoryboardNode.tsx (修改) | +180 | +6 KB |
| **修改代码总计** | **+300** | **+10 KB** |

### 文档文件

| 文件 | 行数 |
|------|------|
| `GENERATION_FLOW.md` | 600 |
| `TESTING_GUIDE.md` | 500 |
| `INTEGRATION_GUIDE.md` | 700 |
| `BACKEND_API_CONTRACT.md` | 800 |
| `SYSTEM_SUMMARY.md` | 600 |
| `QUICK_START.md` | 150 |
| `IMPLEMENTATION_CHECKLIST.md` | 400 |
| `FILES_OVERVIEW.md` | 500 |
| **文档总计** | **4,250** |

### 总计

- **代码**: 1,180 行（+41 KB）
- **文档**: 4,250 行（~140 KB）
- **总计**: 5,430 行

---

## 🎯 文件依赖关系

```
┌─────────────────────────────────────────┐
│  应用层                                  │
│  ConversationPanel  ←→  StoryboardNode  │
└────────┬──────────────────────┬─────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────┐
│  组件层                                  │
│  ShotGenerationPanel                    │
└────────┬──────────────────────┬─────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────┐
│  服务层                                  │
│  generationEventService (中央总线)      │
└────────┬──────────────────────┬─────────┘
         │                      │
         ▼                      ▼
    shotGenerationService    后端 API
         │                      │
         └──────────┬───────────┘
                    ▼
            HTTP 请求/响应
```

---

## 🔍 快速查找

### 我想... → 查看...

| 需求 | 参考文件 |
|------|---------|
| 快速开始 | `QUICK_START.md` |
| 了解架构 | `GENERATION_FLOW.md` |
| 进行测试 | `TESTING_GUIDE.md` |
| 集成代码 | `INTEGRATION_GUIDE.md` |
| 实现后端 | `BACKEND_API_CONTRACT.md` |
| 了解系统 | `SYSTEM_SUMMARY.md` |
| 查看进度 | `IMPLEMENTATION_CHECKLIST.md` |
| 查看文件 | `FILES_OVERVIEW.md` (本文件) |

---

## 📋 实现顺序建议

1. **第一步** (5分钟) - 复制新文件
   - `generationEventService.ts`
   - `shotGenerationService.ts`
   - `ShotGenerationPanel.tsx`
   - `ShotGenerationPanel.css`

2. **第二步** (10分钟) - 修改现有文件
   - `ConversationPanel.tsx`
   - `ConversationPanel.css`
   - `StoryboardNode.tsx`

3. **第三步** (30分钟) - 后端实现
   - 实现 4 个 API 端点
   - 测试 API 端点

4. **第四步** (20分钟) - 集成测试
   - 前后端集成
   - 完整流程测试

---

## ✅ 验证清单

复制完成后，检查：

```
□ 所有 TypeScript 文件已添加
□ 所有 CSS 文件已添加
□ 现有文件已正确修改
□ TypeScript 编译无错误: npm run type-check
□ Linter 无错误: npm run lint
□ 应用能正常启动: npm run dev
```

---

## 🚀 部署前检查

```
□ 前端代码通过所有测试
□ 后端 API 已实现并测试
□ 前后端集成测试通过
□ 所有文档已更新
□ 生产环境配置已设置
□ 监控和日志已就绪
```

---

## 📞 支持

有任何问题？
1. 查看相关的参考文档
2. 检查 `QUICK_START.md` 的常见问题
3. 参考 `INTEGRATION_GUIDE.md` 的调试技巧

---

**最后更新**: 2024-03-13
**版本**: 1.0
**状态**: ✅ 完成（待后端 API 实现）
