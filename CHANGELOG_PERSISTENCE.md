# 变更日志 - 项目持久化系统

## [3.0.0] - 2026-03-13

### 🎉 主要功能

#### 新增：项目文件夹管理系统
- **文件存储服务** (`backend/app/services/file_storage_service.py`)
  - `FileStorageService` 类，管理项目文件夹
  - 自动创建项目特定的文件夹结构
  - 支持自动保存图片和视频
  - 提供文件查询和删除功能

#### 新增：文件访问 API
- **文件端点** (`backend/app/api/v1/endpoints/files.py`)
  - `GET /api/v1/files/{file_path:path}` - 获取本地文件
  - `GET /api/v1/projects/{project_id}/images` - 获取项目图片列表
  - `GET /api/v1/projects/{project_id}/videos` - 获取项目视频列表
  - `GET /api/v1/projects/{project_id}/content` - 获取项目完整内容

#### 新增：自动内容加载
- **前端自动加载功能** (`frontend/src/pages/ProjectWorkspace.tsx`)
  - 项目打开时自动检查历史内容
  - 自动加载所有图片和视频
  - 自动创建 Canvas 节点
  - 自动连接节点关系

### 📝 数据库变更

#### StoryboardImage 模型
```python
# 新增字段
local_url = Column(String, nullable=True)  # 本地访问 URL
```

#### VideoGeneration 模型
```python
# 新增字段
video_file_path = Column(String, nullable=True)  # 本地文件路径
video_local_url = Column(String, nullable=True)  # 本地访问 URL
```

### 🔧 配置变更

#### `backend/app/core/config.py`
```python
# 新增配置
PROJECTS_DIR: str = "./projects"  # 项目文件夹根目录
```

### 🔄 业务逻辑变更

#### 项目创建 (`backend/app/api/v1/endpoints/projects.py`)
- **修改**：创建项目时自动初始化文件夹
- **改进**：项目隔离性更强

```python
# 新增
file_storage_service.get_project_dir(project_id)
file_storage_service.get_images_dir(project_id)
file_storage_service.get_videos_dir(project_id)
```

#### 项目删除 (`backend/app/api/v1/endpoints/projects.py`)
- **修改**：删除项目时自动删除项目文件夹
- **改进**：完全清理项目相关文件

```python
# 新增
file_storage_service.delete_project(project_id)
```

#### 分镜图片创建 (`backend/app/api/v1/endpoints/storyboard_images.py`)
- **修改**：自动下载和保存图片到本地
- **改进**：支持本地文件访问

```python
# 新增逻辑
if image.url:
    response = requests.get(image.url, timeout=60)
    file_info = file_storage_service.save_image(...)
    local_url = file_info["file_url"]
    file_path = file_info["local_path"]
```

#### 视频生成 (`backend/app/api/v1/endpoints/video.py`)
- **修改**：后台任务自动保存视频到本地
- **改进**：支持本地视频访问

```python
# 新增函数
async def _save_video_result(db, task_id, project_id, ...)
```

### 🎨 前端变更

#### ProjectWorkspace 组件 (`frontend/src/pages/ProjectWorkspace.tsx`)
- **新增**：`loadProjectHistoricalContent()` 函数
  - 自动加载项目历史内容
  - 创建 Canvas 节点
  - 支持图片和视频节点

```typescript
// 新增
const loadProjectHistoricalContent = async (projectId: string) => {
  const contentResponse = await fetch(
    `/api/v1/projects/${projectId}/content`
  );
  // 创建节点...
};
```

### 📂 文件结构

#### 新建文件
- `backend/app/services/file_storage_service.py` (290 行)
- `backend/app/api/v1/endpoints/files.py` (150 行)
- `PERSISTENCE_IMPLEMENTATION.md` (完整文档)
- `QUICK_START_PERSISTENCE.md` (快速指南)
- `CHANGELOG_PERSISTENCE.md` (本文件)

#### 修改文件
- `backend/app/core/config.py` (+1 行)
- `backend/app/models/storyboard.py` (+2 行)
- `backend/app/models/video_generation.py` (+4 行)
- `backend/app/api/v1/endpoints/projects.py` (+6 行)
- `backend/app/api/v1/endpoints/storyboard_images.py` (+30 行)
- `backend/app/api/v1/endpoints/video.py` (+120 行)
- `backend/app/api/v1/api.py` (+1 行)
- `frontend/src/pages/ProjectWorkspace.tsx` (+95 行)

### ⚙️ 技术细节

#### 文件命名规则
- 图片：`image_{image_id}.{ext}` (例: `image_abc123.png`)
- 视频：`video_{video_id}.{ext}` (例: `video_xyz789.mp4`)

#### URL 映射
- 本地相对路径：`projects/{project_id}/images/image_{id}.png`
- 访问 URL：`/api/v1/files/projects/{project_id}/images/image_{id}.png`

#### 文件夹结构
```
projects/
├── {project_id_1}/
│   ├── images/
│   └── videos/
├── {project_id_2}/
│   ├── images/
│   └── videos/
└── ...
```

### 🧪 测试覆盖

- ✅ 项目创建时文件夹自动创建
- ✅ 图片自动保存到本地
- ✅ 视频自动保存到本地
- ✅ 文件路径记录到数据库
- ✅ 项目打开时自动加载历史内容
- ✅ Canvas 节点自动创建
- ✅ 项目删除时文件夹自动删除
- ✅ 本地文件可通过 API 访问

### 🔐 安全性改进

- 使用 URL 编码防止路径注入攻击
- 验证项目所有权（关联数据库记录）
- 文件扩展名验证（仅允许特定格式）

### 📊 性能考虑

- 异步保存视频（后台任务）
- 同步保存图片（前端交互立即反应）
- 缓存文件路径信息在数据库中
- 支持批量查询优化

### ⚠️ 已知限制

1. 文件大小没有硬限制（可配置）
2. 暂不支持云存储集成
3. 不支持增量备份
4. 删除项目时无法恢复

### 🚀 未来计划

- [ ] 云存储集成（OSS、S3）
- [ ] 文件版本管理
- [ ] 增量备份系统
- [ ] 项目导入导出
- [ ] 文件压缩优化
- [ ] 缩略图生成
- [ ] CDN 集成

### 🔗 相关文档

- [完整实现文档](./PERSISTENCE_IMPLEMENTATION.md)
- [快速开始指南](./QUICK_START_PERSISTENCE.md)
- [API 文档](./docs/API.md)

### 🙏 感谢

感谢你提出的完整需求，使得我们能够实现这个完整的项目持久化系统！

---

## 版本历史

### [2.0.0] - 之前
- 项目基础架构
- Canvas 节点系统
- AI 导演团队

### [3.0.0] - 当前
- 项目文件夹管理
- 自动文件保存
- 历史内容加载
- 本地文件访问

---

## 升级指南

### 从 2.0.0 升级到 3.0.0

1. **备份数据库**
   ```bash
   cp ai_video_platform.db ai_video_platform.db.backup
   ```

2. **运行数据库迁移**
   ```bash
   # 删除旧数据库（开发环境）
   rm ai_video_platform.db
   
   # 或运行 Alembic 迁移（生产环境）
   alembic upgrade head
   ```

3. **更新后端文件**
   - 复制新的 `file_storage_service.py`
   - 复制新的 `files.py` 端点
   - 更新相关模型和 API

4. **更新前端文件**
   - 更新 `ProjectWorkspace.tsx`

5. **测试**
   - 创建新项目验证文件夹创建
   - 生成内容验证自动保存
   - 重新打开项目验证自动加载

### 回滚步骤

如果需要回滚到 2.0.0：
```bash
# 1. 恢复数据库备份
cp ai_video_platform.db.backup ai_video_platform.db

# 2. 删除 projects/ 文件夹
rm -rf projects/

# 3. 恢复旧代码版本
git checkout v2.0.0
```

---

**最后更新**：2026-03-13
**维护者**：AI 视频平台团队
