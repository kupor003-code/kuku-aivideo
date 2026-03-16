# 快速开始指南

## 30 秒快速了解

你现在拥有一个完整的镜头生成系统，支持：

```
对话框 ←→ Canvas 实时同步
        ↓
    进度显示（0-100%）
        ↓
    手动生成流程（无自动链式）
        ↓
    单个镜头控制（暂停/继续）
```

## 5 分钟快速集成

### 第一步：添加新文件到 `frontend/src` 中

复制这两个新服务：
- `services/generationEventService.ts`
- `services/shotGenerationService.ts`

复制这个新组件：
- `components/ShotGenerationPanel.tsx`
- `components/ShotGenerationPanel.css`

### 第二步：修改现有文件

**编辑** `components/ConversationPanel.tsx`:

```typescript
// 在文件顶部添加
import { ShotGenerationPanel } from './ShotGenerationPanel';
import { generateShotImages, generateVideo } from '../services/shotGenerationService';
import { generationEventService } from '../services/generationEventService';

// 在 props 中添加
onShotsUpdate?: (shots: any[]) => void;

// 在 state 中添加
const [shots, setShots] = useState<Shot[]>([]);
const [generatedImages, setGeneratedImages] = useState<Map<string, string[]>>(new Map());

// 在消息列表前添加 JSX
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

**编辑** `components/canvas/StoryboardNode.tsx`:

```typescript
// 在文件顶部添加
import { generationEventService } from '../../services/generationEventService';

// 在 state 中添加
const [currentShots, setCurrentShots] = useState<Shot[]>(nodeData.shots || []);
const [currentImages, setCurrentImages] = useState(nodeData.images);

// 监听事件（在 useEffect 中）
window.addEventListener('shot-image-generated', handleImageGenerated);
generationEventService.subscribe('progress', updateProgress);
```

### 第三步：完成！

现在你的应用支持完整的手动镜头生成流程。

## 工作流程

```
1. 用户发消息 → "请创建视频"
2. AI 返回镜头列表
3. 对话框显示 ShotGenerationPanel
4. 用户点击"生成图片"
5. 进度条实时显示（对话框 + Canvas）
6. 完成后 Canvas 显示图片
7. 用户点击"生成视频"
8. 完成后可播放视频
9. 重复 4-8 生成其他镜头
```

## API 端点

后端需要实现这 4 个端点：

```
POST   /api/v1/storyboard/shots/generate
GET    /api/v1/storyboard/shots/{id}/status
POST   /api/v1/storyboard/videos/generate
GET    /api/v1/storyboard/videos/{id}/status
```

详见 `BACKEND_API_CONTRACT.md`

## 关键点

✅ **完全手动** - 用户主动点击每个按钮
✅ **实时同步** - 对话框和 Canvas 共享进度
✅ **错误处理** - 网络错误/API 错误均有提示
✅ **可扩展** - 易于添加暂停/继续/重新生成等功能

## 常见问题

**Q: 为什么我的进度条不动？**
A: 检查后端是否正确返回 `progress` 字段

**Q: 视频按钮为什么禁用？**
A: 图片必须先生成完成，确保 `image-generation-complete` 事件被触发

**Q: 如何调试？**
A: 打开浏览器控制台，使用 Network 标签查看 API 调用

## 文档导航

- **我想了解完整架构** → 阅读 `GENERATION_FLOW.md`
- **我想进行测试** → 阅读 `TESTING_GUIDE.md`
- **我想集成到项目** → 阅读 `INTEGRATION_GUIDE.md`
- **我是后端开发者** → 阅读 `BACKEND_API_CONTRACT.md`
- **我想看技术细节** → 阅读 `SYSTEM_SUMMARY.md`

## 下一步

1. ✅ 将新文件复制到项目
2. ✅ 修改现有文件
3. ✅ 后端实现 4 个 API 端点
4. ✅ 在浏览器中测试
5. ✅ 参考 `TESTING_GUIDE.md` 进行完整测试

---

**需要帮助？** 查看 `INTEGRATION_GUIDE.md` 的常见问题部分
