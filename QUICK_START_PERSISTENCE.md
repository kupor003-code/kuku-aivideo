# 快速开始 - 项目持久化功能

## 🚀 5分钟快速上手

### 1. 环境设置

确保你已经有可用的后端和前端环境。

### 2. 启动应用

```bash
# 终端 1 - 后端
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 终端 2 - 前端
cd frontend
npm run dev
```

### 3. 测试完整流程

#### 步骤 1: 创建项目
1. 打开 http://localhost:5173/projects
2. 点击"新建项目"按钮
3. 输入项目标题（例如："我的第一个视频"）
4. 点击"创建"

✅ **验证**：`projects/{project_id}/` 文件夹已创建

#### 步骤 2: 打开项目
1. 点击新创建的项目
2. 项目打开到 Canvas 页面

✅ **验证**：项目可以正常打开

#### 步骤 3: 生成内容（可选，需要后端 AI 服务）
1. 在左侧对话面板输入创意描述
2. 等待 AI 生成分镜和图片

✅ **验证**：
- 图片自动保存到 `projects/{project_id}/images/`
- 数据库中 `storyboard_images` 表的 `local_url` 字段有值

#### 步骤 4: 验证文件保存
```bash
# 查看项目文件夹结构
ls -la projects/
ls -la projects/{project_id}/images/
ls -la projects/{project_id}/videos/
```

#### 步骤 5: 测试自动加载
1. 关闭浏览器
2. 重新打开 http://localhost:5173/projects
3. 打开同一个项目

✅ **验证**：历史图片和视频自动加载到 Canvas

#### 步骤 6: 测试项目删除
1. 返回项目列表
2. 点击项目上的"删除"按钮
3. 确认删除

✅ **验证**：
- 项目从列表消失
- `projects/{project_id}/` 文件夹被删除

---

## 📊 API 快速参考

### 获取项目内容
```bash
curl http://localhost:8000/api/v1/projects/{project_id}/content
```

### 获取图片列表
```bash
curl http://localhost:8000/api/v1/projects/{project_id}/images
```

### 获取视频列表
```bash
curl http://localhost:8000/api/v1/projects/{project_id}/videos
```

### 访问本地文件
```bash
# 查看图片
curl http://localhost:8000/api/v1/files/projects/{project_id}/images/image_{id}.png -o image.png

# 查看视频
curl http://localhost:8000/api/v1/files/projects/{project_id}/videos/video_{id}.mp4 -o video.mp4
```

---

## 🔍 文件目录示例

运行完整流程后的目录结构：

```
project_root/
├── projects/
│   └── abc123def456/
│       ├── images/
│       │   ├── image_img1.png
│       │   ├── image_img2.jpg
│       │   └── image_img3.webp
│       └── videos/
│           ├── video_vid1.mp4
│           ├── video_vid2.mp4
│           └── video_vid3.webp
├── backend/
├── frontend/
└── ...
```

---

## 💡 常见问题

**Q: 文件夹在哪里？**
A: 在后端根目录的 `projects/` 文件夹内，与 `backend/` 和 `frontend/` 同级

**Q: 如何修改保存路径？**
A: 编辑 `backend/app/core/config.py` 中的 `PROJECTS_DIR` 配置

**Q: 本地文件无法访问？**
A: 检查 CORS 配置和 API 端点是否正确工作

**Q: 如何恢复已删除的项目？**
A: 文件夹删除后无法恢复，建议定期备份

---

## 🎯 下一步

1. **定制化配置** - 修改保存路径和文件格式
2. **批量导入** - 导入历史项目文件
3. **云存储** - 集成云存储服务（OSS、S3等）
4. **备份策略** - 定期备份项目文件

---

## 📚 完整文档

查看详细文档：[PERSISTENCE_IMPLEMENTATION.md](./PERSISTENCE_IMPLEMENTATION.md)
