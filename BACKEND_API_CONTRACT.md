# 后端 API 契约

## 概述

本文档定义了前端镜头生成系统所需的后端 API 契约。

---

## 1. 生成镜头图片

### 端点
```
POST /api/v1/storyboard/shots/generate
```

### 请求

```json
{
  "project_id": "proj_123",
  "shot_number": 1,
  "shot_description": "宇航员登陆火星",
  "prompt": "一个宇航员穿着太空服，踏上火星表面，火星表面是红色的岩石，天空呈现紫红色",
  "size": "1024*1024",
  "n": 3
}
```

**参数说明**:
- `project_id` (string, required) - 项目 ID
- `shot_number` (integer, required) - 镜头编号
- `shot_description` (string, required) - 镜头描述
- `prompt` (string, required) - 生成提示词
- `size` (string, required) - 图片尺寸，格式 "宽*高"（e.g., "1024*1024"）
- `n` (integer, required) - 要生成的图片数量

### 响应

```json
{
  "shot_gen_id": "gen_1234567890",
  "status": "pending"
}
```

**响应字段说明**:
- `shot_gen_id` (string) - 生成任务 ID，用于后续查询状态
- `status` (string) - 初始状态，通常为 "pending"

### 状态码

- `200 OK` - 任务创建成功
- `400 Bad Request` - 参数有误
- `401 Unauthorized` - 未授权
- `500 Internal Server Error` - 服务器错误

---

## 2. 查询镜头图片生成状态

### 端点
```
GET /api/v1/storyboard/shots/{shot_gen_id}/status
```

### 请求参数

- `shot_gen_id` (path parameter, required) - 生成任务 ID

### 响应 - 生成中

```json
{
  "status": "generating",
  "progress": 45,
  "shot_gen_id": "gen_1234567890"
}
```

### 响应 - 完成

```json
{
  "status": "completed",
  "progress": 100,
  "shot_gen_id": "gen_1234567890",
  "image_ids": ["img_001", "img_002", "img_003"],
  "image_urls": [
    "https://cdn.example.com/img_001.png",
    "https://cdn.example.com/img_002.png",
    "https://cdn.example.com/img_003.png"
  ]
}
```

### 响应 - 失败

```json
{
  "status": "failed",
  "progress": 0,
  "shot_gen_id": "gen_1234567890",
  "error": "API 配额已用尽"
}
```

### 响应 - 暂停

```json
{
  "status": "paused",
  "progress": 60,
  "shot_gen_id": "gen_1234567890"
}
```

**响应字段说明**:
- `status` (string) - 生成状态：pending, generating, paused, completed, failed
- `progress` (integer, 0-100) - 生成进度百分比
- `shot_gen_id` (string) - 生成任务 ID
- `image_ids` (array of string, 仅当 status=completed) - 生成的图片 ID 列表
- `image_urls` (array of string, 仅当 status=completed) - 生成的图片 URL 列表
- `error` (string, 仅当 status=failed) - 错误信息

### 轮询建议

前端会按照以下方式轮询：
- 轮询间隔：1000ms（1 秒）
- 超时时间：120000ms（2 分钟）

---

## 3. 暂停镜头图片生成

### 端点
```
POST /api/v1/storyboard/shots/{shot_gen_id}/pause
```

### 请求体

```json
{}
```

### 响应

```json
{
  "status": "paused",
  "progress": 50,
  "shot_gen_id": "gen_1234567890"
}
```

### 状态码

- `200 OK` - 暂停成功
- `404 Not Found` - 任务不存在
- `409 Conflict` - 任务已完成或已失败，无法暂停
- `500 Internal Server Error` - 服务器错误

---

## 4. 继续镜头图片生成

### 端点
```
POST /api/v1/storyboard/shots/{shot_gen_id}/resume
```

### 请求体

```json
{}
```

### 响应

```json
{
  "status": "generating",
  "progress": 50,
  "shot_gen_id": "gen_1234567890"
}
```

### 状态码

- `200 OK` - 继续成功
- `404 Not Found` - 任务不存在
- `409 Conflict` - 任务未处于暂停状态
- `500 Internal Server Error` - 服务器错误

---

## 5. 生成视频

### 端点
```
POST /api/v1/storyboard/videos/generate
```

### 请求

```json
{
  "project_id": "proj_123",
  "shot_number": 1,
  "image_ids": ["img_001", "img_002", "img_003"],
  "prompt": "创建一个平缓的镜头运动，展示宇航员在火星表面的探索",
  "duration": 3
}
```

**参数说明**:
- `project_id` (string, required) - 项目 ID
- `shot_number` (integer, required) - 镜头编号
- `image_ids` (array of string, required) - 用于生成视频的图片 ID 列表
- `prompt` (string, required) - 视频生成提示词
- `duration` (integer, required) - 视频时长（秒）

### 响应

```json
{
  "video_gen_id": "vid_1234567890",
  "status": "pending"
}
```

**响应字段说明**:
- `video_gen_id` (string) - 视频生成任务 ID
- `status` (string) - 初始状态，通常为 "pending"

---

## 6. 查询视频生成状态

### 端点
```
GET /api/v1/storyboard/videos/{video_gen_id}/status
```

### 请求参数

- `video_gen_id` (path parameter, required) - 视频生成任务 ID

### 响应 - 生成中

```json
{
  "status": "generating",
  "progress": 50,
  "video_gen_id": "vid_1234567890"
}
```

### 响应 - 完成

```json
{
  "status": "completed",
  "progress": 100,
  "video_gen_id": "vid_1234567890",
  "video_id": "vid_001",
  "video_url": "https://cdn.example.com/video_001.mp4"
}
```

### 响应 - 失败

```json
{
  "status": "failed",
  "progress": 0,
  "video_gen_id": "vid_1234567890",
  "error": "视频编码失败"
}
```

**响应字段说明**:
- `status` (string) - 生成状态：pending, generating, paused, completed, failed
- `progress` (integer, 0-100) - 生成进度百分比
- `video_gen_id` (string) - 生成任务 ID
- `video_id` (string, 仅当 status=completed) - 视频 ID
- `video_url` (string, 仅当 status=completed) - 视频 URL（支持 HTTP/HTTPS）
- `error` (string, 仅当 status=failed) - 错误信息

### 轮询建议

前端会按照以下方式轮询：
- 轮询间隔：1000ms（1 秒）
- 超时时间：120000ms（2 分钟）

---

## 7. 修改消息结构（用于返回镜头数据）

### 消息对象结构

现有的消息结构应扩展为：

```json
{
  "id": "msg_123",
  "role": "assistant",
  "content": "我已经为您的项目创建了5个场景的分镜头",
  "agent_type": "storyboard_agent",
  "agent_name": "分镜头设计师",
  "created_at": "2024-01-15T10:30:00Z",
  "related_node_id": "node_456",
  "shots_data": [
    {
      "id": "shot_1",
      "shot_number": 1,
      "shot_description": "宇航员登陆火星",
      "prompt": "一个宇航员穿着太空服，踏上火星表面..."
    },
    {
      "id": "shot_2",
      "shot_number": 2,
      "shot_description": "探索火星表面",
      "prompt": "宇航员在火星表面行走，观察地形..."
    }
  ]
}
```

**新增字段**:
- `shots_data` (array of Shot objects, optional) - 如果消息包含镜头信息，在此字段中返回

**Shot 对象结构**:
```json
{
  "id": "shot_1",
  "shot_number": 1,
  "shot_description": "镜头描述文本",
  "prompt": "生成提示词（可选）"
}
```

---

## 8. 错误响应格式

所有错误应使用统一格式：

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "参数无效",
    "details": {
      "field": "project_id",
      "reason": "project_id 不能为空"
    }
  }
}
```

### 常见错误码

- `INVALID_REQUEST` - 请求参数无效
- `UNAUTHORIZED` - 未授权
- `NOT_FOUND` - 资源不存在
- `CONFLICT` - 操作冲突
- `RATE_LIMIT_EXCEEDED` - 请求过于频繁
- `API_QUOTA_EXCEEDED` - API 配额已用尽
- `INTERNAL_ERROR` - 内部服务器错误

---

## 9. 认证与授权

### Authorization Header

所有请求应包含以下头：

```
Authorization: Bearer <token>
```

或者通过 Cookie：

```
Set-Cookie: session=<session_id>
```

---

## 10. CORS 配置

确保后端配置了正确的 CORS 头：

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

---

## 11. 性能要求

### 响应时间

- 创建生成任务：< 100ms
- 查询状态：< 50ms
- 暂停/继续：< 100ms

### 吞吐量

- 应支持同时处理多个生成任务
- 每个项目应能同时生成至少 5 个镜头

### 并发

- 支持至少 100 个并发请求
- 状态查询应支持高频轮询

---

## 12. 测试用例

### 成功场景

```
1. POST /storyboard/shots/generate → 返回 shot_gen_id
2. GET /storyboard/shots/{shot_gen_id}/status → 返回 progress: 50
3. 多次 GET /storyboard/shots/{shot_gen_id}/status → progress 逐步增加
4. 最终 GET → 返回 status: "completed", image_urls
```

### 错误场景

```
1. 无效的 project_id → 返回 400 Bad Request
2. 查询不存在的 shot_gen_id → 返回 404 Not Found
3. 暂停已完成的任务 → 返回 409 Conflict
4. API 配额用尽 → 返回适当的错误状态
```

---

## 13. 示例实现

### Python (FastAPI)

```python
@app.post("/api/v1/storyboard/shots/generate")
async def generate_shot_images(request: GenerateShotRequest):
    # 创建生成任务
    shot_gen_id = create_generation_task(request)
    
    # 启动后台生成
    asyncio.create_task(process_image_generation(shot_gen_id))
    
    return {
        "shot_gen_id": shot_gen_id,
        "status": "pending"
    }

@app.get("/api/v1/storyboard/shots/{shot_gen_id}/status")
async def get_shot_status(shot_gen_id: str):
    task = get_task(shot_gen_id)
    
    if task.status == "completed":
        return {
            "status": "completed",
            "progress": 100,
            "shot_gen_id": shot_gen_id,
            "image_ids": task.image_ids,
            "image_urls": task.image_urls
        }
    else:
        return {
            "status": task.status,
            "progress": task.progress,
            "shot_gen_id": shot_gen_id
        }
```

---

## 14. 版本控制

本契约版本：`1.0`

如有更改，请更新版本号并通知前端团队。

---

## 15. 联系方式

有任何问题或建议，请联系前端团队。
