"""创意发散Agent"""
from typing import Dict, List
from app.agents.base import BaseAgent
from app.services.zhipuai_service import get_zhipuai_service


class CreativeAgent(BaseAgent):
    """
    创意发散Agent

    职责：
    - 与用户讨论创意
    - 提供创作建议
    - 生成分镜照片提示词
    - 提供视频提示词
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "creative"
        self.name = "创意顾问"
        self.description = "帮助用户讨论创意，提供建议"

        # 系统提示词（可以随时修改）
        self.SYSTEM_PROMPT = """# 角色定义
你是一位资深的视频创作顾问，精通AI视频生成和图片生成。你的特点是：**专业、直接、高效**。

# 核心工作原则
1. **直接给出方案** - 不要反复确认，基于已有信息直接提供建议
2. **一次说清楚** - 每次回复都要给出具体、可操作的内容
3. **先给方案，再问细节** - 如果信息不足，先给出一个可行方案
4. **简洁高效** - 避免过度询问，每个回复都要有实际价值
5. **区分图片和视频** - 图片提示词强调静态画面感，视频提示词强调动态和运动

# 提示词类型区分

**分镜照片提示词**（用于生成静态参考图）：
- 强调画面构图、光线、色彩、氛围
- 描述静态场景和人物姿态
- 突出视觉细节和质感

**视频提示词**（用于生成动态视频）：
- 强调动作、运动、变化
- 描述镜头运动和节奏
- 突出时间流逝和动态效果

# 回复结构
对于用户的每个问题，你都应该：
1. **直接回答** - 给出具体的建议或方案
2. **提供选项** - 如果需要选择，给出2-3个具体选项
3. **行动建议** - 明确告诉用户下一步应该做什么
4. **区分类型** - 清楚标注是图片提示词还是视频提示词

现在，请根据用户的问题，直接给出专业、可操作的方案或建议。"""

        self.ai_service = get_zhipuai_service()

    async def chat(self, message: str, context: Dict) -> str:
        """
        处理对话消息

        Args:
            message: 用户消息
            context: 对话上下文

        Returns:
            Agent回复
        """
        # 构建上下文字符串
        context_str = self._build_context_str(context)

        # 调用AI服务
        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=message,
                context=context_str if context_str else None,
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"抱歉，我遇到了一些问题：{str(e)}"

    async def suggest(self, context: Dict) -> List[str]:
        """
        基于上下文提供建议

        Args:
            context: 对话上下文

        Returns:
            建议列表
        """
        messages = context.get("messages", [])
        if not messages:
            return [
                "💡 讨论新创意",
                "📸 生成参考图提示词",
                "🎬 生成视频提示词",
            ]

        # 分析最后几条消息，提供建议
        suggestions = []

        last_message = messages[-1].get("content", "")
        if "分镜" in last_message or "图片" in last_message:
            suggestions.extend([
                "📸 基于刚才的讨论，生成分镜照片提示词",
                "🔄 调整风格（温馨/专业/活力）",
            ])
        elif "视频" in last_message:
            suggestions.extend([
                "🎬 生成视频提示词",
                "⏱️ 设置视频时长",
                "🎨 选择视频风格",
            ])
        else:
            suggestions.extend([
                "💡 继续深入讨论创意",
                "📸 生成分镜照片提示词",
                "🎬 生成视频提示词",
            ])

        return suggestions

    async def generate_storyboard_prompt(self, context: Dict) -> str:
        """
        基于上下文生成分镜照片提示词

        Args:
            context: 对话上下文

        Returns:
            分镜照片提示词
        """
        context_str = self._build_context_str(context)

        prompt = """基于我们的讨论，请生成一个用于生成分镜照片的提示词。

要求：
1. 强调画面构图、光线、色彩、氛围
2. 描述静态场景和人物姿态
3. 突出视觉细节和质感
4. 控制在100字以内

请直接给出提示词，不需要额外解释。"""

        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=prompt,
                context=context_str,
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"生成失败：{str(e)}"

    async def generate_video_prompt(self, context: Dict) -> str:
        """
        基于上下文生成视频提示词

        Args:
            context: 对话上下文

        Returns:
            视频提示词
        """
        context_str = self._build_context_str(context)

        prompt = """基于我们的讨论，请生成一个用于生成视频的提示词。

要求：
1. 强调动作、运动、变化
2. 描述镜头运动和节奏
3. 突出时间流逝和动态效果
4. 控制在100字以内

请直接给出提示词，不需要额外解释。"""

        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=prompt,
                context=context_str,
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"生成失败：{str(e)}"

    def update_system_prompt(self, new_prompt: str):
        """
        更新系统提示词

        Args:
            new_prompt: 新的系统提示词
        """
        self.SYSTEM_PROMPT = new_prompt
