"""Agent API端点"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, GeneratePromptRequest, GeneratePromptResponse
from app.agents.manager import get_agent_manager
import uuid

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    与Agent对话

    Args:
        request: 对话请求

    Returns:
        Agent回复
    """
    try:
        # 获取创意发散Agent
        agent_manager = get_agent_manager()
        creative_agent = agent_manager.get_creative_agent()

        # 构建上下文
        context = request.context or {}
        if "messages" not in context:
            context["messages"] = []

        # 生成会话ID（如果不存在）
        session_id = request.session_id or str(uuid.uuid4())

        # 调用Agent
        response = await creative_agent.chat(request.message, context)

        # 获取建议
        suggestions = await creative_agent.suggest(context)

        return ChatResponse(
            message=response,
            session_id=session_id,
            suggestions=suggestions,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-prompt", response_model=GeneratePromptResponse)
async def generate_prompt(request: GeneratePromptRequest):
    """
    生成提示词

    Args:
        request: 生成请求

    Returns:
        生成的提示词
    """
    try:
        # 获取创意发散Agent
        agent_manager = get_agent_manager()
        creative_agent = agent_manager.get_creative_agent()

        # 构建上下文
        context = {}
        if request.session_id:
            # 这里可以从数据库加载会话历史
            # context = await load_session_context(request.session_id)
            context["messages"] = []

        # 根据类型生成提示词
        if request.prompt_type == "storyboard":
            prompt = await creative_agent.generate_storyboard_prompt(context)
        elif request.prompt_type == "video":
            prompt = await creative_agent.generate_video_prompt(context)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的提示词类型：{request.prompt_type}"
            )

        return GeneratePromptResponse(
            prompt=prompt,
            prompt_type=request.prompt_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions(session_id: str = None):
    """
    获取建议操作

    Args:
        session_id: 会话ID（可选）

    Returns:
        建议列表
    """
    try:
        agent_manager = get_agent_manager()
        creative_agent = agent_manager.get_creative_agent()

        # 构建上下文
        context = {}
        if session_id:
            # 从数据库加载会话
            context["messages"] = []
        else:
            context["messages"] = []

        suggestions = await creative_agent.suggest(context)
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
