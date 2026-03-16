"""协调Agent - 负责整体工作流程协调"""
from typing import Dict, List, Optional
from app.agents.base import BaseAgent
from app.services.zhipuai_service import get_zhipuai_service


class CoordinatorAgent(BaseAgent):
    """
    协调Agent

    职责：
    - 理解用户创意
    - 制定创作计划
    - 生成分镜和视频提示词
    - 协调工作流程
    - 确保每步都得到用户确认
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "coordinator"
        self.name = "创作协调员"
        self.description = "协调视频创作流程，管理整体工作流程"

        self.SYSTEM_PROMPT = """# 视频创作协调专家

你是一位专业的视频创作协调专家，负责：
1. **理解用户创意** - 深入理解用户的视频创意需求
2. **制定创作计划** - 生成详细的、可执行的创作步骤
3. **生成提示词** - 为分镜和视频生成高质量提示词
4. **流程协调** - 确保每个环节都得到用户确认后再继续

## 工作流程

### 第1步：理解需求
当用户提供创意时，你需要：
- 分析视频主题、风格、情感基调
- 识别关键场景和情节要点
- 确定目标受众和视频类型

### 第2步：制定计划
生成结构化的创作计划，包含：
- **整体概述** (100字内)
- **创作步骤** (3-8个具体步骤)
- **分镜建议** (建议的镜头数量和类型)
- **预计时长**

### 第3步：生成分镜提示词
基于用户确认的计划，为每个关键场景生成详细的分镜提示词，每个提示词包含：
- **场景描述**
- **画面构图** (景别、角度、光线)
- **色彩风格**
- **情感氛围**
- **技术参数** (建议比例等)

### 第4步：生成视频提示词
基于选定的分镜图片，生成视频提示词，包含：
- **镜头运动** (推拉摇移等)
- **转场方式**
- **节奏控制**
- **特效需求** (如有)

## 重要原则

1. **等待用户确认** - 每一步完成后都要询问用户是否满意，是否需要修改
2. **提供选项** - 当有多个方案时，提供2-3个不同方向供用户选择
3. **尊重用户修改** - 用户提出的任何修改意见都要认真采纳并调整
4. **保持专业** - 始终以专业的视频制作标准来要求
5. **清晰简洁** - 输出要结构清晰、易于理解

## 输出格式

计划阶段：
```
📋 创作计划

【整体概述】
...

【创作步骤】
1. ...
2. ...
...

【其他信息】
- 预计时长: ...
- 建议分镜数: ...
```

分镜提示词阶段：
```
📸 分镜 #1: [场景名称]

场景描述: ...
画面构图: ...
色彩风格: ...
情感氛围: ...
```

请始终以专业、耐心的态度与用户沟通。"""

        self.ai_service = get_zhipuai_service()

    async def chat(self, message: str, context: Dict) -> str:
        """
        处理对话消息

        Args:
            message: 用户消息
            context: 对话上下文，包含 workflow_state

        Returns:
            Agent回复
        """
        workflow_state = context.get("workflow_state", {"current_step": "input"})

        # 根据当前工作流状态决定如何响应
        current_step = workflow_state.get("current_step", "input")

        if current_step == "input":
            return await self.handle_input(message, context)
        elif current_step == "planning":
            return await self.handle_planning_feedback(message, context)
        elif current_step == "storyboard_prompts":
            return await self.handle_storyboard_prompt_feedback(message, context)
        else:
            return await self.general_chat(message, context)

    async def handle_input(self, message: str, context: Dict) -> str:
        """处理用户初始输入，生成创作计划"""
        # 如果消息为空，返回欢迎信息
        if not message or not message.strip():
            return """👋 欢迎使用AI视频创作平台！

我是你的创作协调助手，我会帮助你：
1. 📋 理解你的创意并制定创作计划
2. 📸 生成分镜照片提示词
3. 🎬 生成视频制作提示词
4. ✨ 确保每一步都符合你的要求

请告诉我你想制作什么样的视频？比如：
- 🌸 制作一个春天的主题短片
- 🎬 创作一个产品宣传视频
- 📱 制作一个APP使用教程
- 🎨 创作一个艺术展示视频

或者直接描述你的创意！"""

        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=f"用户创意：{message}\n\n请分析这个创意，并生成一个详细的视频创作计划。",
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"抱歉，生成计划时出错：{str(e)}"

    async def handle_planning_feedback(self, message: str, context: Dict) -> str:
        """处理用户对计划的反馈"""
        plan = context.get("plan")

        if any(keyword in message for keyword in ["确认", "满意", "继续", "好的", "可以"]):
            # 用户确认计划，生成分镜提示词
            return "✅ 计划已确认！现在开始生成分镜提示词...\n\n" + await self.generate_storyboard_prompts(plan)

        if any(keyword in message for keyword in ["重新生成", "重新制作", "再来一个"]):
            # 重新生成计划
            try:
                response = await self.ai_service.chat_with_system_prompt(
                    system_prompt=self.SYSTEM_PROMPT,
                    user_message=f"请重新生成一个创作计划，要求：\n{message}\n\n请按照标准格式输出创作计划。",
                    temperature=0.8,  # 提高温度以获得不同的结果
                )
                return "🔄 " + response
            except Exception as e:
                return f"重新生成计划时出错：{str(e)}"

        if any(keyword in message for keyword in ["修改", "调整", "不满意", "改变", "想要"]):
            # 用户想修改计划
            try:
                response = await self.ai_service.chat_with_system_prompt(
                    system_prompt=self.SYSTEM_PROMPT,
                    user_message=f"""原计划：{plan}

用户反馈：{message}

请根据用户反馈调整计划。调整后请按照之前的格式输出创作计划，包含：
- 【整体概述】
- 【创作步骤】
- 【其他信息】

保持专业水准并满足用户需求。""",
                    temperature=0.7,
                )
                return "🔄 " + response
            except Exception as e:
                return f"调整计划时出错：{str(e)}"

        return await self.general_chat(message, context)

    async def generate_storyboard_prompts(self, plan: Dict) -> str:
        """生成分镜提示词"""
        try:
            # 生成结构化的分镜提示词
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=f"""基于以下创作计划，请生成3-5个关键场景的分镜提示词。

要求：
1. 每个提示词必须以 "分镜 #N: [场景名称]" 开头
2. 包含详细的场景描述、画面构图、色彩风格、情感氛围
3. 提示词要专业、具体，适合AI图片生成

创作计划：
{plan}

请按以下格式输出：

📸 分镜 #1: [场景名称]

场景描述: [详细描述]
画面构图: [景别、角度、光线]
色彩风格: [色彩描述]
情感氛围: [氛围描述]

📸 分镜 #2: [场景名称]
...

请现在生成分镜提示词。""",
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"生成分镜提示词时出错：{str(e)}"

    async def handle_storyboard_prompt_feedback(self, message: str, context: Dict) -> str:
        """处理用户对分镜提示词的反馈"""
        if any(keyword in message for keyword in ["确认", "满意", "继续", "好的", "可以"]):
            return "✅ 分镜提示词已确认！现在可以生成图片了。请点击\"生成分镜图片\"按钮开始。"

        if any(keyword in message for keyword in ["重新生成", "重新制作", "再来一个"]):
            # 重新生成分镜提示词
            plan = context.get("plan", {})
            try:
                response = await self.ai_service.chat_with_system_prompt(
                    system_prompt=self.SYSTEM_PROMPT,
                    user_message=f"""请重新生成分镜提示词，使用不同的创意方向。

创作计划：{plan}

请生成3-5个全新的分镜提示词，要求：
1. 每个提示词必须以 "分镜 #N: [场景名称]" 开头
2. 包含详细的场景描述、画面构图、色彩风格、情感氛围
3. 使用与之前不同的创意角度

请按以下格式输出：

📸 分镜 #1: [场景名称]
场景描述: [详细描述]
画面构图: [景别、角度、光线]
色彩风格: [色彩描述]
情感氛围: [氛围描述]...

请现在重新生成。""",
                    temperature=0.8,  # 提高温度获得不同结果
                )
                return "🔄 " + response
            except Exception as e:
                return f"重新生成分镜提示词时出错：{str(e)}"

        if any(keyword in message for keyword in ["修改", "调整", "改变", "想要", "不满意"]):
            # 用户想修改提示词
            return """好的，请告诉我您想如何修改分镜提示词。您可以：
- 🎨 修改某个分镜的场景描述
- 📐 调整画面构图或角度
- 🌈 改变色彩风格
- 😊 调整情感氛围
- ➕ 添加新的分镜场景
- ➖ 删除某个分镜
- 🔄 替换某个分镜

请详细描述您的修改需求，例如：
"把第2个分镜改成日落场景"
"增加一个雨天场景"
"让整体色调更温暖一些"
"""

        return await self.general_chat(message, context)

    async def general_chat(self, message: str, context: Dict) -> str:
        """普通对话"""
        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=message,
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"抱歉，我遇到了一些问题：{str(e)}"

    async def generate_plan(self, user_input: str) -> Dict:
        """
        生成结构化的创作计划

        Args:
            user_input: 用户的创意输入

        Returns:
            包含创作计划的字典
        """
        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=f"""请分析以下创意，生成创作计划（以JSON格式返回）：

{user_input}

请返回JSON格式：
{{
  "overview": "概述",
  "steps": ["步骤1", "步骤2", ...],
  "storyboard_prompts": ["提示词1", "提示词2", ...],
  "video_prompts": ["提示词1", ...],
  "estimated_duration": "预计时长"
}}""",
                temperature=0.7,
            )

            # 尝试解析JSON
            import json
            import re

            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Failed to parse plan JSON: {e}")

        # 如果解析失败，返回默认计划
        return {
            "overview": response[:200] if response else "视频创作计划",
            "steps": ["概念开发", "分镜设计", "图片生成", "视频合成"],
            "storyboard_prompts": [],
            "video_prompts": [],
            "estimated_duration": "30-60秒"
        }

    async def refine_storyboard_prompt(self, original_prompt: str, user_feedback: str) -> str:
        """
        优化分镜提示词

        Args:
            original_prompt: 原始提示词
            user_feedback: 用户反馈

        Returns:
            优化后的提示词
        """
        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=f"原提示词：{original_prompt}\n\n用户反馈：{user_feedback}\n\n请根据用户反馈优化提示词，保持专业水准。",
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"优化提示词时出错：{str(e)}"

    async def generate_video_prompt(self, storyboard_images: List[str]) -> str:
        """
        生成视频提示词

        Args:
            storyboard_images: 分镜图片URL列表

        Returns:
            视频提示词
        """
        try:
            response = await self.ai_service.chat_with_system_prompt(
                system_prompt=self.SYSTEM_PROMPT,
                user_message="基于已完成的分镜图片，请生成视频制作提示词，包含镜头运动、转场、节奏等专业要求。",
                temperature=0.7,
            )
            return response
        except Exception as e:
            return f"生成视频提示词时出错：{str(e)}"

    async def suggest(self, context: Dict) -> List[str]:
        """
        基于上下文提供建议

        Args:
            context: 对话上下文

        Returns:
            建议列表
        """
        workflow_state = context.get("workflow_state", {"current_step": "input"})
        current_step = workflow_state.get("current_step", "input")

        if current_step == "input":
            return [
                "🌸 制作一个春天的主题短片",
                "🎬 创作一个产品宣传视频",
                "📱 制作一个APP使用教程",
                "🎨 创作一个艺术展示视频",
            ]

        if current_step == "planning":
            return ["✅ 计划很完美，继续下一步", "🔄 请调整一下计划", "❌ 不满意，重新制定"]

        if current_step == "storyboard_prompts":
            return ["✅ 提示词很棒，继续生成图片", "🔄 请修改这个提示词", "❌ 重新生成提示词"]

        if current_step == "generating_storyboard":
            # 检查是否已有图片
            storyboard_images = workflow_state.get("storyboard_images", [])
            if storyboard_images and len(storyboard_images) > 0:
                return ["🎬 继续生成视频提示词", "📸 查看分镜工作台", "🔄 重新生成图片"]
            else:
                return ["📸 前往分镜工作台生成图片", "🔄 修改提示词重新生成"]

        return ["继续", "修改", "返回上一步"]

    def update_system_prompt(self, new_prompt: str):
        """更新系统提示词"""
        self.SYSTEM_PROMPT = new_prompt
