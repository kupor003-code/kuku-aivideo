# AI短剧创作平台 V2 - 测试指南

## 📋 测试前准备

### 1. 环境检查

确保你已经安装了必要的依赖：

```bash
cd /Users/kupor/Desktop/ai-video-platform/backend

# 检查是否有虚拟环境
# 如果没有，创建一个
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置检查

检查 `/backend/.env` 文件，确保配置了必要的 API Key：

```env
# 智谱 AI API Key（必需）
ZHIPUAI_API_KEY=your_api_key_here

# 数据库配置
DATABASE_URL=sqlite:///./ai_video_platform.db
```

### 3. 数据库初始化

```bash
cd /Users/kupor/Desktop/ai-video-platform/backend
alembic upgrade head
```

---

## 🚀 方式一：通过 Python 脚本测试（推荐）

### 步骤 1: 启动测试脚本

```bash
cd /Users/kupor/Desktop/ai-video-platform/backend
python test_workflow.py
```

### 预期输出

```
🚀 开始工作流端到端测试

==================================================
测试 1: Orchestrator Agent 意图理解
==================================================

用户输入: 我想创作一个关于科幻主题的短剧

✅ 响应成功: True
📝 消息: 我理解了你的创意...
📋 执行计划: ...
```

---

## 🌐 方式二：通过 API 测试（使用浏览器）

### 步骤 1: 启动后端服务

```bash
cd /Users/kupor/Desktop/ai-video-platform/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

看到这个输出说明启动成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 步骤 2: 打开 API 文档

**在浏览器中打开**：
```
http://localhost:8000/docs
```

你会看到漂亮的 Swagger UI 界面！

### 步骤 3: 测试生成执行计划

在 Swagger UI 中：

1. 找到 `POST /api/v1/workflow/plan/generate`
2. 点击 "Try it out" 按钮
3. 在 Request body 中输入：
   ```json
   {
     "user_input": "我想创作一个关于人工智能觉醒的短剧，风格要赛博朋克",
     "project_id": "test_project_001"
   }
   ```
4. 点击 "Execute" 按钮
5. 查看 Response body 中的结果

**预期响应**：
```json
{
  "success": true,
  "intent": {
    "task_type": "create_video",
    "topic": "我想创作一个关于人工智能觉醒的短剧"
  },
  "execution_plan": {
    "overview": "创作关于...'的短剧视频",
    "steps": [
      {
        "order": 1,
        "agent": "storyboard",
        "action": "generate_storyboard",
        "description": "生成分镜脚本和镜头拆解"
      }
    ],
    "estimated_duration": "5-10分钟"
  },
  "message": "我理解了你的创意：..."
}
```

### 步骤 4: 测试执行工作流

1. 找到 `POST /api/v1/workflow/execute`
2. 点击 "Try it out"
3. 在 Request body 中输入：
   ```json
   {
     "user_input": "我想创作一个关于人工智能觉醒的短剧",
     "project_id": "test_project_002",
     "auto_execute": true
   }
   ```
4. 点击 "Execute"

**预期响应**：
```json
{
  "success": true,
  "project_id": "test_project_002",
  "execution_state": {
    "progress": 100.0,
    "is_completed": true,
    "completed_steps": [...]
  }
}
```

### 步骤 5: 查询执行状态

**在浏览器中直接访问**：
```
http://localhost:8000/api/v1/workflow/status/test_project_002
```

或者在 Swagger UI 中：
1. 找到 `GET /api/v1/workflow/status/{project_id}`
2. 输入 project_id: `test_project_002`
3. 点击 "Execute"

---

## 🌐 方式三：通过 curl 测试

### 生成执行计划

```bash
curl -X POST "http://localhost:8000/api/v1/workflow/plan/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想创作一个关于人工智能觉醒的短剧",
    "project_id": "test_project_001"
  }'
```

### 执行工作流

```bash
curl -X POST "http://localhost:8000/api/v1/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想创作一个关于人工智能觉醒的短剧",
    "project_id": "test_project_002",
    "auto_execute": true
  }'
```

### 查询状态

```bash
curl "http://localhost:8000/api/v1/workflow/status/test_project_002"
```

---

## 🎯 推荐测试流程

### 快速验证（5分钟）

1. **启动后端**
   ```bash
   cd /Users/kupor/Desktop/ai-video-platform/backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **打开 API 文档**
   ```
   http://localhost:8000/docs
   ```

3. **测试生成计划**
   - 使用 `POST /api/v1/workflow/plan/generate`
   - 输入任意创意描述

4. **测试执行工作流**
   - 使用 `POST /api/v1/workflow/execute`
   - 设置 `auto_execute: true`

5. **查看状态**
   - 使用 `GET /api/v1/workflow/status/{project_id}`

### 完整测试（15分钟）

运行 Python 测试脚本：
```bash
cd /Users/kupor/Desktop/ai-video-platform/backend
python test_workflow.py
```

---

## ⚠️ 常见问题

### 问题 1: 端口被占用

```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀掉进程
kill -9 <PID>

# 或者使用其他端口
uvicorn app.main:app --reload --port 8001
```

### 问题 2: 智谱 API Key 未配置

**错误**：
```
ValueError: ZHIPUAI_API_KEY未配置
```

**解决**：
在 `/backend/.env` 文件中添加：
```env
ZHIPUAI_API_KEY=你的实际API密钥
```

### 问题 3: 数据库表不存在

```bash
cd /Users/kupor/Desktop/ai-video-platform/backend
alembic upgrade head
```

---

## 📊 测试检查清单

测试完成后，确认以下功能都正常：

- [ ] 后端服务能正常启动
- [ ] API 文档可以访问（http://localhost:8000/docs）
- [ ] Orchestrator 能理解用户意图
- [ ] 能生成合理的执行计划
- [ ] WorkflowExecutor 能执行工作流
- [ ] 能查询执行状态
- [ ] Python 测试脚本运行成功

---

## 🎉 测试成功标志

如果看到以下输出，说明测试成功：

1. **API 测试成功**：所有端点返回 `"success": true`
2. **Python 脚本测试成功**：看到 `✅ 测试完成` 和 `✅ 通过` 标记
3. **工作流执行成功**：`progress: 100.0` 和 `is_completed: true`

---

**祝测试顺利！** 🚀

如有问题，请记录错误信息，我可以帮你调试！
