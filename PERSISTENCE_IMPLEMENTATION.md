# 项目持久化与自动加载完整实现指南

## 📌 功能概述

本实现提供了完整的项目内容持久化和自动加载系统，包括：
- ✅ 项目特定文件夹管理
- ✅ 自动保存图片和视频到本地
- ✅ 数据库记录文件路径
- ✅ 项目打开时自动加载历史内容到 Canvas
- ✅ 项目创建/删除时自动管理文件夹

---

## 🏗️ 系统架构

### 后端架构
```
API 请求
  ↓
VideoGeneration/StoryboardImage 创建
  ↓
自动下载文件到本地
  ↓
保存本地路径到数据库
  ↓
返回本地访问 URL
```

### 前端架构
```
项目打开
  ↓
检查 Canvas 数据
  ↓
如果无数据，加载历史内容
  ↓
创建 Canvas 节点
  ↓
显示历史图片和视频
```

---

## 📂 文件结构

### 新创建的文件

#### 1. **后端文件存储服务**
```
backend/app/services/file_storage_service.py
```
核心功能：
- `FileStorageService` 类
  - `get_project_dir(project_id)` - 获取项目文件夹
  - `get_images_dir(project_id)` - 获取图片文件夹
  - `get_videos_dir(project_id)` - 获取视频文件夹
  - `save_image()` - 保存图片
  - `save_video()` - 保存视频
  - `get_project_images()` - 获取项目图片
  - `get_project_videos()` - 获取项目视频
  - `delete_project()` - 删除项目文件夹

#### 2. **文件访问 API**
```
backend/app/api/v1/endpoints/files.py
```
端点列表：
- `GET /api/v1/files/{file_path:path}` - 获取文件
- `GET /api/v1/projects/{project_id}/images` - 获取图片列表
- `GET /api/v1/projects/{project_id}/videos` - 获取视频列表
- `GET /api/v1/projects/{project_id}/content` - 获取完整内容

### 修改的文件

#### 后端修改

**1. 配置文件** (`backend/app/core/config.py`)
```python
PROJECTS_DIR: str = "./projects"  # 项目文件夹根目录
```

**2. 项目模型** (`backend/app/models/project.py`)
- 无修改，已支持 `canvas_data` 字段

**3. 分镜模型** (`backend/app/models/storyboard.py`)
```python
url = Column(String, nullable=True)  # 图片URL（远程或本地）
file_path = Column(String, nullable=True)  # 本地文件路径（相对于项目根目录）
local_url = Column(String, nullable=True)  # 本地访问 URL（/api/v1/files/...）
```

**4. 视频生成模型** (`backend/app/models/video_generation.py`)
```python
video_url = Column(String, nullable=True)  # 视频URL（远程或本地）
video_file_path = Column(String, nullable=True)  # 本地文件路径（相对于项目根目录）
video_local_url = Column(String, nullable=True)  # 本地访问 URL（/api/v1/files/...）
```

**5. 项目创建 API** (`backend/app/api/v1/endpoints/projects.py`)
```python
# 创建项目时自动初始化文件夹
file_storage_service.get_project_dir(project_id)
file_storage_service.get_images_dir(project_id)
file_storage_service.get_videos_dir(project_id)

# 删除项目时自动删除文件夹
file_storage_service.delete_project(project_id)
```

**6. 分镜图片创建 API** (`backend/app/api/v1/endpoints/storyboard_images.py`)
```python
# 自动下载并保存图片
if image.url:
    response = requests.get(image.url, timeout=60)
    if response.status_code == 200:
        file_info = file_storage_service.save_image(...)
        local_url = file_info["file_url"]
        file_path = file_info["local_path"]
```

**7. 视频生成 API** (`backend/app/api/v1/endpoints/video.py`)
```python
# 后台任务自动保存视频
async def wait_for_video_task(task_id):
    # 下载视频
    # 保存到本地
    # 记录到数据库
    # 更新任务状态
```

**8. API 路由注册** (`backend/app/api/v1/api.py`)
```python
api_router.include_router(files.router, tags=["文件管理"])
```

#### 前端修改

**ProjectWorkspace 组件** (`frontend/src/pages/ProjectWorkspace.tsx`)
```typescript
// 新增函数：加载项目历史内容
const loadProjectHistoricalContent = async (projectId: string) => {
  // 获取 /api/v1/projects/{projectId}/content
  // 创建 Storyboard 和 Video 节点
  // 添加到 Canvas
};

// useEffect 中调用
if (!data.canvas_data?.nodes) {
  await loadProjectHistoricalContent(projectId);
}
```

---

## 🔄 完整工作流程

### 流程 1: 项目创建与初始化

```
1. 用户点击"新建项目"
   ↓
2. ProjectList.handleCreateProject()
   ↓
3. projectService.create(title, description)
   ↓
4. POST /api/v1/projects/
   ↓
5. 后端创建 Project 记录
   ↓
6. 自动调用 file_storage_service:
   - 创建 projects/{project_id}/ 文件夹
   - 创建 projects/{project_id}/images/ 文件夹
   - 创建 projects/{project_id}/videos/ 文件夹
   ↓
7. 返回项目信息
   ↓
8. 前端更新项目列表
```

### 流程 2: 分镜图片生成与保存

```
1. 用户创建分镜提示词
   ↓
2. 后端生成分镜图片
   ↓
3. 图片 URL 返回给前端
   ↓
4. 前端调用 POST /api/v1/storyboard-images/
   ↓
5. 后端接收图片信息：
   - 下载图片：requests.get(image_url)
   - 保存到本地：projects/{project_id}/images/image_{id}.png
   - 生成访问 URL：/api/v1/files/projects/{project_id}/images/...
   ↓
6. 创建 StoryboardImage 记录：
   - url: 原始 URL
   - file_path: projects/{project_id}/images/image_{id}.png
   - local_url: /api/v1/files/projects/{project_id}/images/image_{id}.png
   ↓
7. 返回图片信息
   ↓
8. 前端显示图片缩略图
```

### 流程 3: 视频生成与保存

```
1. 用户从图片生成视频
   ↓
2. 前端调用 POST /api/v1/video/generate
   ↓
3. 后端生成视频（异步）
   ↓
4. 后台任务 wait_for_video_task():
   - 轮询任务状态
   - 视频完成后：
     a) 下载视频：httpx.get(video_url)
     b) 保存到本地：projects/{project_id}/videos/video_{id}.mp4
     c) 生成访问 URL：/api/v1/files/projects/{project_id}/videos/...
     d) 创建 PromptVersion（如果需要）
     e) 创建 VideoGeneration 记录
   ↓
5. VideoGeneration 包含：
   - video_url: 原始 URL
   - video_file_path: projects/{project_id}/videos/video_{id}.mp4
   - video_local_url: /api/v1/files/projects/{project_id}/videos/video_{id}.mp4
   - status: COMPLETED
```

### 流程 4: 项目打开与内容加载

```
1. 用户点击"打开项目"
   ↓
2. ProjectWorkspace 挂载
   ↓
3. 加载项目信息：GET /api/v1/projects/{project_id}
   ↓
4. 检查 canvas_data 字段
   ↓
5. 如果有 canvas_data：
   - 加载 Canvas 节点和边
   ↓
   如果无 canvas_data：
   - 调用 loadProjectHistoricalContent(project_id)
   - GET /api/v1/projects/{project_id}/content
   - 返回所有历史图片和视频
   ↓
6. 创建 Canvas 节点：
   - 如果有图片：创建 Storyboard 节点
   - 如果有视频：创建 Video 节点
   - 自动连接节点
   ↓
7. 更新 setNodes()
   ↓
8. Canvas 显示所有历史内容
```

### 流程 5: 项目删除

```
1. 用户点击"删除项目"
   ↓
2. ProjectList.handleDeleteProject(project_id)
   ↓
3. 确认删除
   ↓
4. DELETE /api/v1/projects/{project_id}
   ↓
5. 后端：
   - 删除数据库中的 Project 记录
   - 删除关联的所有数据
   ↓
6. 自动调用：
   - file_storage_service.delete_project(project_id)
   - 删除 projects/{project_id}/ 文件夹及所有内容
   ↓
7. 返回成功
   ↓
8. 前端更新项目列表
```

---

## 📊 数据库字段对照表

### StoryboardImage
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `url` | String | 原始图片URL | `https://dashscope.oss-cn-...` |
| `file_path` | String | 本地相对路径 | `projects/abc123/images/image_xyz.png` |
| `local_url` | String | 本地访问URL | `/api/v1/files/projects/abc123/images/image_xyz.png` |

### VideoGeneration
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `video_url` | String | 原始视频URL | `https://dashscope.oss-cn-...` |
| `video_file_path` | String | 本地相对路径 | `projects/abc123/videos/video_xyz.mp4` |
| `video_local_url` | String | 本地访问URL | `/api/v1/files/projects/abc123/videos/video_xyz.mp4` |

---

## 🧪 测试步骤

### 测试 1: 项目创建与文件夹初始化

```bash
# 1. 创建项目
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -d '{"title": "测试项目", "description": "测试项目描述"}'

# 2. 验证文件夹是否创建
ls -la projects/
# 应该看到新的项目文件夹

# 3. 验证子文件夹
ls -la projects/{project_id}/
# 应该包含 images/ 和 videos/
```

### 测试 2: 图片保存

```bash
# 1. 创建分镜图片
curl -X POST http://localhost:8000/api/v1/storyboard-images/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "{project_id}",
    "prompt_id": "{prompt_id}",
    "url": "https://example.com/image.png",
    "metadata": {"size": "1024x1024"}
  }'

# 2. 验证文件是否保存
ls -la projects/{project_id}/images/

# 3. 验证数据库记录
# 检查 storyboard_images 表的 local_url 字段
```

### 测试 3: 视频保存

```bash
# 1. 生成视频（异步）
curl -X POST http://localhost:8000/api/v1/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "生成视频提示词",
    "image_url": "https://example.com/image.png",
    "project_id": "{project_id}"
  }'

# 2. 等待视频生成（可能需要几分钟）

# 3. 验证文件是否保存
ls -la projects/{project_id}/videos/

# 4. 验证数据库记录
# 检查 video_generations 表的 video_local_url 字段
```

### 测试 4: 内容加载

```bash
# 1. 获取项目完整内容
curl http://localhost:8000/api/v1/projects/{project_id}/content

# 输出示例：
{
  "project_id": "abc123",
  "images": [
    {
      "id": "img1",
      "url": "/api/v1/files/projects/abc123/images/image_xxx.png",
      "prompt": "...",
      "created_at": "2026-03-13T..."
    }
  ],
  "videos": [
    {
      "id": "vid1",
      "url": "/api/v1/files/projects/abc123/videos/video_xxx.mp4",
      "status": "completed",
      "created_at": "2026-03-13T..."
    }
  ]
}
```

### 测试 5: 前端自动加载

```
1. 打开浏览器，访问项目列表
2. 点击"创建项目"按钮
3. 创建新项目
4. 点击"打开"进入项目
5. 观察 Canvas 是否自动加载历史内容
6. 验证图片和视频节点是否正确显示
```

---

## 🔧 配置和部署

### 环境配置

`.env` 文件（如果使用）：
```
PROJECTS_DIR=./projects
```

或在 `backend/app/core/config.py` 中修改：
```python
PROJECTS_DIR: str = "./projects"
```

### 文件夹权限

确保后端有权创建和删除文件夹：
```bash
chmod 755 ./projects
chmod 755 ./projects/*
```

### 数据库迁移

由于添加了新的数据库字段，需要运行迁移（如果使用 Alembic）：

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "Add local file fields"

# 执行迁移
alembic upgrade head
```

或者直接删除旧数据库重新创建（开发环境）：
```bash
rm ai_video_platform.db
```

---

## 📝 API 文档

### 1. 获取项目完整内容

**请求**：
```
GET /api/v1/projects/{project_id}/content
```

**响应**：
```json
{
  "project_id": "project-123",
  "images": [
    {
      "id": "image-1",
      "url": "/api/v1/files/projects/project-123/images/image_abc.png",
      "prompt": "A beautiful sunset",
      "size": "1024x1024",
      "created_at": "2026-03-13T10:00:00"
    }
  ],
  "videos": [
    {
      "id": "video-1",
      "url": "/api/v1/files/projects/project-123/videos/video_xyz.mp4",
      "thumbnail": "...",
      "status": "completed",
      "duration": 5,
      "created_at": "2026-03-13T11:00:00"
    }
  ],
  "total_images": 1,
  "total_videos": 1
}
```

### 2. 获取项目图片列表

**请求**：
```
GET /api/v1/projects/{project_id}/images
```

**响应**：
```json
[
  {
    "id": "image-1",
    "url": "/api/v1/files/projects/project-123/images/image_abc.png",
    "prompt": "A beautiful sunset",
    "size": "1024x1024",
    "created_at": "2026-03-13T10:00:00"
  }
]
```

### 3. 获取项目视频列表

**请求**：
```
GET /api/v1/projects/{project_id}/videos
```

**响应**：
```json
[
  {
    "id": "video-1",
    "url": "/api/v1/files/projects/project-123/videos/video_xyz.mp4",
    "thumbnail": "...",
    "status": "completed",
    "duration": 5,
    "created_at": "2026-03-13T11:00:00"
  }
]
```

### 4. 获取文件内容

**请求**：
```
GET /api/v1/files/projects/{project_id}/images/image_abc.png
```

**响应**：文件二进制内容（图片、视频等）

---

## 🚨 故障排除

### 问题 1: 文件夹未创建

**症状**：项目创建后，`projects/` 文件夹不存在

**解决方案**：
```python
# 检查 config.py 中的 PROJECTS_DIR 是否配置正确
# 检查后端是否有写入权限
# 检查 file_storage_service.py 是否正确导入
```

### 问题 2: 图片未保存到本地

**症状**：`storyboard_images` 表中 `local_url` 为空

**解决方案**：
```python
# 检查图片 URL 是否可访问
# 检查网络连接
# 检查错误日志：print(f"下载并保存图片失败: {str(e)}")
```

### 问题 3: 项目打开时无法加载历史内容

**症状**：打开项目时 Canvas 为空，即使之前生成过内容

**解决方案**：
```javascript
// 检查浏览器控制台是否有错误信息
// 检查 /api/v1/projects/{id}/content 是否返回正确数据
// 检查网络请求是否成功
```

### 问题 4: 数据库错误

**症状**：创建视频时出现数据库约束错误

**解决方案**：
```python
# 确保 PromptVersion 记录存在
# 检查 prompt_version_id 是否正确
# 运行数据库迁移
```

---

## 📚 相关文件列表

### 后端新建文件
- `backend/app/services/file_storage_service.py`
- `backend/app/api/v1/endpoints/files.py`

### 后端修改文件
- `backend/app/core/config.py`
- `backend/app/models/storyboard.py`
- `backend/app/models/video_generation.py`
- `backend/app/api/v1/endpoints/projects.py`
- `backend/app/api/v1/endpoints/storyboard_images.py`
- `backend/app/api/v1/endpoints/video.py`
- `backend/app/api/v1/api.py`

### 前端修改文件
- `frontend/src/pages/ProjectWorkspace.tsx`

---

## ✅ 验证清单

- [x] 项目创建时自动创建文件夹
- [x] 项目删除时自动删除文件夹
- [x] 图片自动保存到本地
- [x] 视频自动保存到本地
- [x] 文件路径记录到数据库
- [x] 本地访问 URL 生成正确
- [x] 项目打开时自动加载历史内容
- [x] Canvas 节点自动创建和连接
- [x] 本地文件可以通过 API 访问
- [x] 没有 linting 错误

---

## 🎉 总结

这个实现完整地解决了你提出的所有需求：

1. **项目特定的文件夹** ✅
   - 每个项目有独立的文件夹结构
   - 自动创建和删除

2. **自动加载历史内容** ✅
   - 项目打开时自动加载所有图片和视频
   - 自动创建 Canvas 节点

3. **现有 Canvas 中展示** ✅
   - 历史内容自动显示在 Canvas 中
   - 支持预览和下载

4. **修改后端支持本地文件保存** ✅
   - 自动下载并保存文件到本地
   - 支持自定义保存路径

5. **数据库中记录文件路径** ✅
   - 记录本地相对路径
   - 记录本地访问 URL

所有代码已完成，无 linting 错误，可以直接使用！
