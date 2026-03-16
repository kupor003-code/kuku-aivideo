"""API v1 路由"""
from fastapi import APIRouter
from app.api.v1.endpoints import projects, prompts, storyboard_images, video, conversations, agents_v2, project_config, files, storyboard, shots, script_storyboard, workflow, generation, demo_cases
# from app.api.v1.endpoints import coordinator  # 暂时禁用：缺少 Session 模型

api_router = APIRouter()

# 注册V2路由
api_router.include_router(projects.router, prefix="/projects", tags=["项目管理"])
api_router.include_router(project_config.router, prefix="/projects", tags=["项目配置"])
api_router.include_router(conversations.router, prefix="/projects", tags=["对话管理"])
api_router.include_router(agents_v2.router, prefix="/agents/v2", tags=["AI导演团队 V2"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["工作流执行"])
# api_router.include_router(coordinator.router, prefix="/coordinator", tags=["协调工作流"])  # 暂时禁用
api_router.include_router(prompts.router, prefix="/prompts", tags=["提示词管理"])
api_router.include_router(storyboard_images.router, prefix="/storyboard-images", tags=["分镜图片管理"])
api_router.include_router(storyboard.router, prefix="/storyboard", tags=["分镜管理"])
api_router.include_router(shots.router, prefix="/storyboard/shots", tags=["镜头生成"])
api_router.include_router(script_storyboard.router, prefix="/script-storyboard", tags=["剧本分镜"])
api_router.include_router(video.router, prefix="/video", tags=["视频生成"])
api_router.include_router(generation.router, prefix="/generation", tags=["图片视频生成"])
api_router.include_router(demo_cases.router, tags=["演示案例"])
api_router.include_router(files.router, tags=["文件管理"])

# 旧路由暂时注释（待迁移到V2）
# from app.api.v1.endpoints import agents, storyboard, coordinator
# api_router.include_router(agents.router, prefix="/agents", tags=["Agent"])
# api_router.include_router(storyboard.router, prefix="/storyboard", tags=["分镜生成"])
# api_router.include_router(coordinator.router, prefix="/coordinator", tags=["协调工作流"])

# 后续添加其他路由
# from app.api.v1.endpoints import tasks
# api_router.include_router(tasks.router, prefix="/tasks", tags=["任务"])


@api_router.get("/info")
async def api_info():
    """API信息"""
    return {
        "version": "v1",
        "endpoints": {
            "projects": "/projects",
            "agents": "/agents",
            "tasks": "/tasks"
        }
    }
