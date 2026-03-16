"""协调Agent API端点"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.coordinator import (
    CoordinatorChatRequest,
    CoordinatorChatResponse,
    GeneratePlanRequest,
    GeneratePlanResponse,
    RefinePromptRequest,
    RefinePromptResponse,
    GenerateStoryboardImagesRequest,
    GenerateStoryboardImagesResponse,
    WorkflowState,
    CreationPlan,
)
from app.agents.manager import get_agent_manager
from app.services.alibaba_image_service import get_alibaba_image_service
from app.models.session import Session as SessionModel
from app.models.storyboard import StoryboardImage as StoryboardImageModel
from app.db.database import SessionLocal
import uuid

router = APIRouter()


@router.post("/chat", response_model=CoordinatorChatResponse)
async def coordinator_chat(request: CoordinatorChatRequest):
    """
    与协调Agent对话

    Args:
        request: 对话请求，包含消息、项目ID和工作流状态

    Returns:
        Agent回复和更新后的工作流状态
    """
    try:
        agent_manager = get_agent_manager()
        coordinator_agent = agent_manager.get_coordinator_agent()
        storyboard_agent = agent_manager.get_storyboard_agent()

        # 构建上下文
        context = {}
        if request.workflow_state:
            context["workflow_state"] = request.workflow_state.dict()
            # 将 plan 传递给 Agent，方便生成后续提示词
            if request.workflow_state.plan:
                context["plan"] = request.workflow_state.plan.dict()
        else:
            context["workflow_state"] = {"current_step": "input"}

        if request.session_id:
            context["session_id"] = request.session_id
            context["messages"] = []
        else:
            context["messages"] = []

        # 更新工作流状态
        workflow_state = request.workflow_state or WorkflowState()
        current_step = workflow_state.current_step

        # 调用Agent获取回复
        response = await coordinator_agent.chat(request.message, context)

        # 检查是否需要自动生成分镜图片
        should_generate_images = False
        prompts_to_generate = []

        # 根据用户消息和当前步骤更新状态
        # 只有当用户提供了真实的消息输入且响应中包含创作计划时才推进状态
        if current_step == "input" and request.message.strip() and ("创作计划" in response or "📋" in response):
            workflow_state.current_step = "planning"

            # 总是创建一个 plan 对象
            try:
                # 尝试从响应中提取计划概述
                import re
                overview_match = re.search(r'【整体概述】\s*\n\s*([^\n]+)', response)
                overview = overview_match.group(1) if overview_match else response[:200]

                # 尝试提取创作步骤
                steps_match = re.findall(r'【创作步骤】.*?(\d+)\.\s*([^\n]+)', response, re.DOTALL)
                steps = [step[1] for step in steps_match] if steps_match else ["概念开发", "分镜设计", "图片生成", "视频合成"]

                workflow_state.plan = CreationPlan(
                    overview=overview,
                    steps=steps,
                    storyboard_prompts=[],  # 将在确认时提取
                    video_prompts=[],
                    estimated_duration="30-60秒"
                )
            except Exception as e:
                print(f"Failed to parse plan from response: {e}")
                # 如果解析失败，创建一个基础计划
                workflow_state.plan = CreationPlan(
                    overview=response[:200] if response else "视频创作计划",
                    steps=["概念开发", "分镜设计", "图片生成", "视频合成"],
                    storyboard_prompts=[],
                    video_prompts=[],
                    estimated_duration="30-60秒"
                )
        elif current_step == "planning" and any(kw in request.message for kw in ["确认", "满意", "继续"]):
            workflow_state.current_step = "storyboard_prompts"
            # 从响应中提取分镜提示词，无论 plan 是否存在
            if not workflow_state.plan:
                # 如果没有 plan，创建一个基础 plan
                workflow_state.plan = CreationPlan(
                    overview="视频创作计划",
                    steps=["分镜设计", "图片生成", "视频合成"],
                    storyboard_prompts=[],
                    video_prompts=[],
                    estimated_duration="30-60秒"
                )

            # 从响应中提取分镜提示词
            try:
                import re
                # 匹配 "分镜 #N: 标题" 后面跟着多行描述的内容
                storyboard_pattern = r'📸\s*分镜\s*#(\d+)[:：]\s*([^\n]+)\s*\n(?:场景描述[:：]\s*([^\n]+)\s*\n)?'
                matches = re.findall(storyboard_pattern, response)

                if matches:
                    # 构建完整的提示词列表
                    prompts = []
                    for match in matches:
                        scene_num, title, desc = match
                        # 提取该分镜后面的所有内容直到下一个分镜
                        section_pattern = rf'📸\s*分镜\s*#{scene_num}[:：].*?(?=📸\s*分镜|#|$)'
                        section_match = re.search(section_pattern, response, re.DOTALL)
                        if section_match:
                            prompts.append(section_match.group(0).strip())
                        else:
                            # 如果无法提取完整内容，使用标题和描述
                            full_prompt = f"📸 分镜 #{scene_num}: {title}"
                            if desc:
                                full_prompt += f"\n场景描述: {desc}"
                            prompts.append(full_prompt)

                    if prompts:
                        workflow_state.plan.storyboard_prompts = prompts[:5]
                        print(f"提取到 {len(prompts)} 个分镜提示词")
            except Exception as e:
                print(f"Failed to extract storyboard prompts: {e}")
        elif current_step == "storyboard_prompts" and any(kw in request.message for kw in ["确认", "满意", "继续"]):
            # 用户确认了提示词，需要自动生成图片
            should_generate_images = True
            # 从计划中获取提示词
            if workflow_state.plan and workflow_state.plan.storyboard_prompts:
                prompts_to_generate = workflow_state.plan.storyboard_prompts
            else:
                # 如果计划中没有提示词，从响应中提取
                try:
                    import re
                    prompt_matches = re.findall(r'(?:分镜\s*#\d+[:：]|场景[:：])\s*\n?\s*([^\n]+)', response)
                    if prompt_matches:
                        prompts_to_generate = prompt_matches[:5]
                    else:
                        prompts_to_generate = ["专业摄影级别的分镜图片，电影质感，高清"]
                except:
                    prompts_to_generate = ["专业摄影级别的分镜图片，电影质感，高清"]
            workflow_state.current_step = "generating_storyboard"

        # 如果需要生成图片，在这里处理
        if should_generate_images and prompts_to_generate:
            response += "\n\n🎨 准备生成分镜图片..."

            # 检查是否配置了阿里云API
            try:
                from app.core.config import settings
                if not settings.DASHSCOPE_API_KEY or settings.DASHSCOPE_API_KEY == "your-dashscope-api-key":
                    # 未配置阿里云API，提供引导信息
                    response += "\n\n💡 提示：生成分镜图片需要配置阿里云通义万相API。"
                    response += "\n\n你可以："
                    response += "\n1. 前往「分镜工作台」手动生成图片"
                    response += "\n2. 或者配置阿里云API Key后自动生成"
                    response += "\n\n📸 前往分镜工作台 → 点击导航栏的「分镜工作台」"

                    # 保持当前状态，让用户可以手动操作
                    workflow_state.current_step = "generating_storyboard"
                    workflow_state.selected_storyboard_prompt = prompts_to_generate[0] if prompts_to_generate else None
                else:
                    # 已配置API，自动生成图片
                    try:
                        db = SessionLocal()
                        generated_images = []

                        for prompt in prompts_to_generate[:3]:  # 最多生成3张
                            try:
                                # 调用分镜Agent生成图片
                                result = await storyboard_agent.generate_images(
                                    prompt=prompt,
                                    size="1024*1024",
                                    n=1,
                                )

                                task_id = result.get("task_id", str(uuid.uuid4()))

                                # 如果有返回的图片URL，立即保存
                                if "output" in result and "results" in result["output"]:
                                    for image_result in result["output"]["results"]:
                                        url = image_result.get("url", "")
                                        if url:
                                            db_image = StoryboardImageModel(
                                                project_id=request.project_id,
                                                prompt_id=None,
                                                url=url,
                                                parameters={
                                                    "prompt": prompt,
                                                    "size": "1024*1024",
                                                },
                                                meta=image_result,
                                            )
                                            db.add(db_image)
                                            db.commit()
                                            db.refresh(db_image)
                                            generated_images.append(url)
                            except Exception as img_error:
                                print(f"生成图片失败: {img_error}")
                                continue

                        db.close()

                        # 更新工作流状态
                        workflow_state.storyboard_images = generated_images
                        workflow_state.selected_storyboard_prompt = prompts_to_generate[0] if prompts_to_generate else None

                        if generated_images:
                            response += f"\n\n✅ 成功生成 {len(generated_images)} 张分镜图片！"
                            response += "\n\n💡 下一步："
                            response += "\n1. 查看上方生成的图片"
                            response += "\n2. 如果满意，继续生成视频提示词"
                            response += "\n3. 如果不满意，可以重新生成"
                        else:
                            response += "\n\n⚠️ 图片生成任务已提交，请稍后在「分镜工作台」查看结果。"
                            workflow_state.current_step = "generating_storyboard"

                    except Exception as e:
                        print(f"生成图片时出错: {e}")
                        response += f"\n\n❌ 生成图片时出错: {str(e)}"
                        response += "\n\n你可以前往「分镜工作台」手动生成图片"

            except Exception as config_error:
                print(f"检查配置时出错: {config_error}")
                response += "\n\n⚠️ 无法自动生成图片，请前往「分镜工作台」手动操作"

        # 获取建议
        suggestions = await coordinator_agent.suggest(context)

        return CoordinatorChatResponse(
            message=response,
            workflow_state=workflow_state,
            suggestions=suggestions,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest):
    """
    生成创作计划

    Args:
        request: 生成请求，包含用户输入和项目ID

    Returns:
        生成的创作计划
    """
    try:
        agent_manager = get_agent_manager()
        coordinator_agent = agent_manager.get_coordinator_agent()

        # 生成计划
        plan_dict = await coordinator_agent.generate_plan(request.user_input)

        plan = CreationPlan(**plan_dict)

        return GeneratePlanResponse(plan=plan)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine-prompt", response_model=RefinePromptResponse)
async def refine_prompt(request: RefinePromptRequest):
    """
    优化提示词

    Args:
        request: 优化请求，包含原始提示词和用户反馈

    Returns:
        优化后的提示词
    """
    try:
        agent_manager = get_agent_manager()
        coordinator_agent = agent_manager.get_coordinator_agent()

        if request.prompt_type == "storyboard":
            refined = await coordinator_agent.refine_storyboard_prompt(
                request.original_prompt,
                request.user_feedback
            )
        else:
            # 视频提示词优化逻辑类似
            refined = await coordinator_agent.refine_storyboard_prompt(
                request.original_prompt,
                request.user_feedback
            )

        return RefinePromptResponse(refined_prompt=refined)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-storyboard-images", response_model=GenerateStoryboardImagesResponse)
async def generate_storyboard_images(request: GenerateStoryboardImagesRequest):
    """
    生成分镜图片

    Args:
        request: 生成请求，包含提示词列表和项目ID

    Returns:
        任务信息
    """
    try:
        agent_manager = get_agent_manager()
        storyboard_agent = agent_manager.get_storyboard_agent()
        image_service = get_alibaba_image_service()

        task_ids = []

        # 为每个提示词生成图片
        for prompt in request.prompts:
            result = await storyboard_agent.generate_images(
                prompt=prompt,
                size=request.size,
                n=1,
            )

            task_ids.append(result.get("task_id", str(uuid.uuid4())))

            # 如果有output.results，保存到数据库
            if "output" in result and "results" in result["output"]:
                db = SessionLocal()
                try:
                    for image_result in result["output"]["results"]:
                        db_image = StoryboardImageModel(
                            project_id=request.project_id,
                            prompt_id=None,  # 可以关联到具体的提示词
                            url=image_result.get("url", ""),
                            parameters={
                                "prompt": prompt,
                                "size": request.size,
                            },
                            meta=image_result,
                        )
                        db.add(db_image)
                        db.commit()
                finally:
                    db.close()

        return GenerateStoryboardImagesResponse(
            task_ids=task_ids,
            status="processing"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-video-prompt")
async def generate_video_prompt(storyboard_images: list[str]):
    """
    生成视频提示词

    Args:
        storyboard_images: 分镜图片URL列表

    Returns:
        视频提示词
    """
    try:
        agent_manager = get_agent_manager()
        coordinator_agent = agent_manager.get_coordinator_agent()

        prompt = await coordinator_agent.generate_video_prompt(storyboard_images)

        return {"prompt": prompt}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow-state/{project_id}")
async def get_workflow_state(project_id: str):
    """
    获取项目的工作流状态

    Args:
        project_id: 项目ID

    Returns:
        工作流状态
    """
    try:
        db = SessionLocal()
        try:
            # 查找项目的最新coordinator会话
            session = db.query(SessionModel).filter(
                SessionModel.project_id == project_id,
                SessionModel.agent_type == "coordinator"
            ).order_by(SessionModel.created_at.desc()).first()

            if session and session.context:
                workflow_state = session.context.get("workflow_state", {})
                return {"workflow_state": workflow_state}

            return {"workflow_state": {"current_step": "input"}}

        finally:
            db.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow-state/{project_id}")
async def save_workflow_state(project_id: str, workflow_state: WorkflowState):
    """
    保存项目的工作流状态

    Args:
        project_id: 项目ID
        workflow_state: 工作流状态

    Returns:
        保存结果
    """
    try:
        import uuid
        db = SessionLocal()
        try:
            # 查找或创建会话
            session = db.query(SessionModel).filter(
                SessionModel.project_id == project_id,
                SessionModel.agent_type == "coordinator"
            ).order_by(SessionModel.created_at.desc()).first()

            if session:
                # 更新现有会话
                session.context = session.context or {}
                session.context["workflow_state"] = workflow_state.dict()
                db.commit()
            else:
                # 创建新会话
                session_id = str(uuid.uuid4())
                new_session = SessionModel(
                    id=session_id,
                    project_id=project_id,
                    agent_type="coordinator",
                    messages=[],
                    context={"workflow_state": workflow_state.dict()}
                )
                db.add(new_session)
                db.commit()

            return {"status": "saved", "workflow_state": workflow_state.dict()}

        finally:
            db.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
