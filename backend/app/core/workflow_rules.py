"""
工作流规则配置

定义每个阶段完成后可以执行的下一步操作
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class WorkflowStage(str, Enum):
    """工作流阶段"""
    SCRIPT = "script"          # 剧本创作
    PROMPTS = "prompts"        # 优化提示词
    STORYBOARD = "storyboard"  # 分镜设计
    FRAMES = "frames"          # 生成首尾帧
    VIDEO = "video"            # 生成视频
    CONSISTENCY = "consistency" # 一致性检查


class ActionType(str, Enum):
    """操作类型"""
    AI_CHAT = "ai_chat"              # AI对话（使用智谱AI）
    GENERATE_IMAGE = "generate_image" # 生成图片（使用阿里云）
    GENERATE_VIDEO = "generate_video" # 生成视频（使用阿里云）


# 工作流规则：定义每个阶段完成后可以执行的操作
WORKFLOW_RULES: Dict[WorkflowStage, List[Dict[str, Any]]] = {
    WorkflowStage.SCRIPT: [
        {
            "id": "optimize_prompts",
            "title": "✨ 优化场景提示词",
            "description": "AI优化剧本中的场景描述，使其更适合视频生成",
            "action": ActionType.AI_CHAT,
            "message": "请帮我优化这个剧本的场景提示词，让画面描述更生动、具体",
            "primary": True,
            "next_stage": WorkflowStage.PROMPTS,
        },
        {
            "id": "generate_storyboard",
            "title": "📸 直接生成分镜设计",
            "description": "根据剧本直接生成分镜脚本和镜头规划",
            "action": ActionType.AI_CHAT,
            "message": "请根据这个剧本生成分镜设计，包括每个镜头的描述、角度和构图",
            "primary": False,
            "next_stage": WorkflowStage.STORYBOARD,
        },
    ],

    WorkflowStage.PROMPTS: [
        {
            "id": "generate_storyboard",
            "title": "📸 生成分镜设计",
            "description": "根据优化后的提示词生成分镜脚本",
            "action": ActionType.AI_CHAT,
            "message": "请根据优化后的提示词生成分镜设计，规划每个镜头的描述、角度和构图",
            "primary": True,
            "next_stage": WorkflowStage.STORYBOARD,
        },
        {
            "id": "optimize_more",
            "title": "🔄 继续优化提示词",
            "description": "进一步改进和细化场景提示词",
            "action": ActionType.AI_CHAT,
            "message": "请继续优化这些提示词，增加更多细节和风格描述",
            "primary": False,
            "next_stage": WorkflowStage.PROMPTS,
        },
        {
            "id": "skip_to_frames",
            "title": "⏭️ 跳到生成首尾帧",
            "description": "直接跳过分镜，开始生成首尾帧图片",
            "action": ActionType.GENERATE_IMAGE,
            "primary": False,
            "next_stage": WorkflowStage.FRAMES,
        },
    ],

    WorkflowStage.STORYBOARD: [
        {
            "id": "generate_frames",
            "title": "🖼️ 生成首尾帧",
            "description": "为每个镜头生成首帧和尾帧图片",
            "action": ActionType.GENERATE_IMAGE,
            "message": "开始为分镜中的每个镜头生成首帧和尾帧图片",
            "primary": True,
            "next_stage": WorkflowStage.FRAMES,
        },
        {
            "id": "adjust_storyboard",
            "title": "🔄 调整分镜设计",
            "description": "修改分镜中的镜头设计",
            "action": ActionType.AI_CHAT,
            "message": "请帮我调整分镜设计，修改某些镜头的角度或构图",
            "primary": False,
            "next_stage": WorkflowStage.STORYBOARD,
        },
        {
            "id": "generate_video_directly",
            "title": "⏭️ 直接生成视频",
            "description": "跳过首尾帧，直接生成视频",
            "action": ActionType.GENERATE_VIDEO,
            "primary": False,
            "next_stage": WorkflowStage.VIDEO,
        },
    ],

    WorkflowStage.FRAMES: [
        {
            "id": "generate_video",
            "title": "🎬 生成视频",
            "description": "根据首尾帧生成视频片段",
            "action": ActionType.GENERATE_VIDEO,
            "message": "开始生成视频片段",
            "primary": True,
            "next_stage": WorkflowStage.VIDEO,
        },
        {
            "id": "regenerate_frames",
            "title": "🔄 重新生成首尾帧",
            "description": "不满意？重新生成某些镜头的首尾帧",
            "action": ActionType.GENERATE_IMAGE,
            "primary": False,
            "next_stage": WorkflowStage.FRAMES,
        },
        {
            "id": "check_consistency",
            "title": "✅ 检查视觉一致性",
            "description": "检查所有首尾帧的视觉一致性",
            "action": ActionType.AI_CHAT,
            "message": "请检查这些首尾帧的视觉一致性，包括角色、场景、色调等",
            "primary": False,
            "next_stage": WorkflowStage.CONSISTENCY,
        },
    ],

    WorkflowStage.VIDEO: [
        {
            "id": "check_consistency",
            "title": "✅ 检查视频一致性",
            "description": "检查生成视频的视觉一致性",
            "action": ActionType.AI_CHAT,
            "message": "请检查生成视频的视觉一致性，包括场景过渡、角色表现等",
            "primary": True,
            "next_stage": WorkflowStage.CONSISTENCY,
        },
        {
            "id": "regenerate_video",
            "title": "🔄 重新生成视频",
            "description": "不满意？重新生成某些视频片段",
            "action": ActionType.GENERATE_VIDEO,
            "primary": False,
            "next_stage": WorkflowStage.VIDEO,
        },
        {
            "id": "start_new_project",
            "title": "🆕 开始新项目",
            "description": "保存当前项目，开始新的创作",
            "action": ActionType.AI_CHAT,
            "message": "总结当前项目的创作成果，准备开始新项目",
            "primary": False,
            "next_stage": WorkflowStage.SCRIPT,
        },
    ],

    WorkflowStage.CONSISTENCY: [
        {
            "id": "finalize_project",
            "title": "🎉 完成项目",
            "description": "项目创作完成，导出最终成果",
            "action": ActionType.AI_CHAT,
            "message": "项目创作完成，请总结创作过程和最终成果",
            "primary": True,
            "next_stage": None,  # 流程结束
        },
        {
            "id": "back_to_video",
            "title": "🔄 返回视频生成",
            "description": "根据一致性检查结果重新生成视频",
            "action": ActionType.GENERATE_VIDEO,
            "primary": False,
            "next_stage": WorkflowStage.VIDEO,
        },
    ],
}


def get_next_actions(stage: WorkflowStage) -> List[Dict[str, Any]]:
    """
    获取指定阶段的可执行操作

    Args:
        stage: 当前工作流阶段

    Returns:
        可执行的操作列表
    """
    return WORKFLOW_RULES.get(stage, [])


def get_action_by_id(stage: WorkflowStage, action_id: str) -> Optional[Dict[str, Any]]:
    """
    根据action_id获取操作详情

    Args:
        stage: 当前工作流阶段
        action_id: 操作ID

    Returns:
        操作详情，如果不存在返回None
    """
    actions = get_next_actions(stage)
    for action in actions:
        if action.get("id") == action_id:
            return action
    return None


def get_primary_action(stage: WorkflowStage) -> Optional[Dict[str, Any]]:
    """
    获取主要推荐操作（primary=True的操作）

    Args:
        stage: 当前工作流阶段

    Returns:
        主要操作，如果不存在返回None
    """
    actions = get_next_actions(stage)
    for action in actions:
        if action.get("primary", False):
            return action
    return None
