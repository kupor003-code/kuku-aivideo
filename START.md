# 🚀 快速启动指南

## 前置要求

- Python 3.9+
- Node.js 18+
- pip
- npm

## 第一步：配置后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 编辑.env文件，添加你的API密钥
# DASHSCOPE_API_KEY=你的阿里云API密钥
# ZHIPUAI_API_KEY=你的智谱AI API密钥
```

## 第二步：配置前端

```bash
cd frontend

# 安装依赖（已完成）
npm install

# 配置环境变量
cp .env.example .env
```

## 第三步：启动服务

### 启动后端

```bash
cd backend

# 方式1：使用uvicorn（推荐）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式2：使用FastAPI CLI
fastapi dev app/main.py

# 访问API文档：http://localhost:8000/docs
```

### 启动前端

```bash
cd frontend

# 启动开发服务器
npm run dev

# 访问应用：http://localhost:5173
```

## 项目结构

```
ai-video-platform/
├── backend/                 # 后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── agents/         # Agent实现
│   │   ├── services/       # 业务服务
│   │   ├── workflows/      # 工作流
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库
│   │   └── main.py         # FastAPI应用
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # 前端
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API调用
│   │   ├── store/          # 状态管理
│   │   ├── types/          # TypeScript类型
│   │   └── App.tsx
│   └── package.json
└── 通义生视频工作流/        # 原Streamlit项目（保留）
```

## API端点

启动后端后访问 http://localhost:8000/docs 查看完整API文档

### 基础端点

- `GET /` - 应用信息
- `GET /health` - 健康检查
- `GET /api/v1/info` - API信息

## 下一步

- [ ] 实现项目管理API
- [ ] 实现创意发散Agent
- [ ] 实现分镜生成Agent
- [ ] 实现视频导演Agent
- [ ] 实现前端页面
