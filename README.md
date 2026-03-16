# 🎬 AI视频创作平台

一个基于AI的智能视频创作工具，通过自然语言剧本自动生成分镜、图片和视频。

## ✨ 功能特点

- 🎭 **智能剧本解析**：使用AI自动将剧本转换为分镜
- 🖼️ **AI图片生成**：集成阿里云通义万相，生成分镜图片
- 🎬 **AI视频生成**：集成豆包Seedance 1.5 Pro，将图片转换为视频
- 💾 **本地持久化**：自动保存创作进度到本地存储
- 🌟 **演示案例系统**：保存真实生成的作品为演示案例
- 📊 **可视化编辑**：直观的节点式工作流编辑器

## 🏗️ 技术栈

### 前端
- React 19.2.4
- TypeScript
- Vite
- Axios

### 后端
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite数据库

### AI服务
- 阿里云通义万相 (图片生成)
- 豆包Seedance 1.5 Pro (视频生成)
- 智谱AI (对话和剧本解析)

## 项目结构

```
ai-video-platform/
├── backend/                 # 后端 (FastAPI + Python)
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   └── v1/         # API v1版本
│   │   ├── agents/         # Agent实现
│   │   │   ├── creative_agent.py      # 创意发散Agent
│   │   │   ├── storyboard_agent.py    # 分镜生成Agent
│   │   │   ├── director_agent.py      # 视频导演Agent
│   │   │   └── prompt_agent.py        # 提示词优化Agent
│   │   ├── services/       # 业务服务
│   │   │   ├── alibaba_service.py     # 阿里云服务
│   │   │   ├── zhipuai_service.py     # 智谱AI服务
│   │   │   └── file_service.py        # 文件服务
│   │   ├── workflows/      # 工作流
│   │   │   └── engine.py   # 工作流引擎
│   │   ├── models/         # 数据模型
│   │   │   ├── project.py  # 项目模型
│   │   │   ├── session.py  # 会话模型
│   │   │   ├── prompt.py   # 提示词模型
│   │   │   ├── storyboard.py # 分镜模型
│   │   │   └── video_task.py # 视频任务模型
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── core/           # 核心配置
│   │   │   └── config.py   # 配置文件
│   │   ├── db/             # 数据库
│   │   │   └── database.py # 数据库配置
│   │   └── main.py         # FastAPI主应用
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # 前端 (React + TypeScript)
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API调用
│   │   ├── store/          # 状态管理
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## 快速开始

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API密钥

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## API文档

启动后端后访问：http://localhost:8000/docs

## 技术栈

### 后端
- FastAPI - Web框架
- SQLAlchemy - ORM
- Pydantic - 数据验证
- 智谱AI - AI对话
- 阿里云通义万相 - 视频生成

### 前端
- React - UI框架
- TypeScript - 类型系统
- Vite - 构建工具
- Axios - HTTP客户端
- Zustand/Redux - 状态管理

## Agent系统

### 创意发散Agent
- 与用户讨论创意
- 提供创作建议
- 生成分镜提示词

### 分镜生成Agent
- 文生图
- 图片管理
- 多风格生成

### 视频导演Agent
- 图生视频
- 参数调优
- 批量生成

### 提示词优化Agent
- 提示词转换
- 提示词增强
- 版本管理
