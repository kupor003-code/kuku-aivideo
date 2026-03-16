"""Storyboard Agent - 分镜导演Agent"""
from typing import Dict, Any, Optional, List
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse
from app.services.zhipuai_service import get_zhipuai_service


class StoryboardAgent(BaseAgentV2):
    """
    Storyboard Agent - AI分镜导演
    负责镜头拆分、分镜生成、图片生成提示词
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "storyboard"
        self.agent_name = "AI分镜导演"
        self.description = "负责镜头拆分、分镜生成和图片创作"
        self.capabilities = [
            "break_down_scenes",
            "generate_storyboard_images",
            "create_image_prompts",
            "sequence_shots",
            "visualize_composition",
        ]

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        return "prompts" in input_data or "prompt" in input_data

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理提示词，生成分镜

        Args:
            input_data: 包含prompts或prompt
            context: 上下文

        Returns:
            AgentResponse: 分镜生成结果
        """
        try:
            # 获取提示词
            prompts = input_data.get("prompts", [])
            if not prompts and "prompt" in input_data:
                prompts = [{"content": input_data["prompt"]}]

            # 为每个提示词生成分镜
            storyboard_results = []

            for i, prompt_data in enumerate(prompts):
                prompt_content = prompt_data.get("content", prompt_data) if isinstance(prompt_data, dict) else prompt_data

                # 1. 使用LLM智能拆分镜头
                shots = await self._break_down_shots_with_llm(prompt_content)

                # 2. 为每个镜头生成图片提示词（也使用LLM增强）
                for shot in shots:
                    image_prompt = await self._create_image_prompt_with_llm(shot, prompt_content)
                    shot["image_prompt"] = image_prompt

                storyboard_results.append({
                    "scene_number": i + 1,
                    "original_prompt": prompt_content,
                    "shots": shots,
                    "total_shots": len(shots),
                })

            return AgentResponse(
                success=True,
                data={
                    "storyboard": storyboard_results,
                    "total_scenes": len(storyboard_results),
                    "total_shots": sum(s["total_shots"] for s in storyboard_results),
                },
                message=f"📸 我生成了{len(storyboard_results)}个场景的分镜",
                next_agent="consistency",  # 下一步传给视觉审校
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"分镜生成失败: {str(e)}",
                message="抱歉，分镜创作遇到了问题",
            )

    async def _break_down_shots(self, prompt: str) -> List[Dict[str, Any]]:
        """
        将场景拆分为多个镜头（模板方式，作为fallback）

        Args:
            prompt: 场景提示词

        Returns:
            镜头列表
        """
        # 简化实现：每个场景生成3-5个镜头
        shots = []

        # 镜头类型
        shot_types = [
            {"type": "establishing", "name": "建立镜头", "duration": "2s"},
            {"type": "medium", "name": "中景", "duration": "3s"},
            {"type": "close-up", "name": "特写", "duration": "2s"},
            {"type": "detail", "name": "细节", "duration": "2s"},
            {"type": "transition", "name": "过渡", "duration": "1s"},
        ]

        for i, shot_type in enumerate(shot_types):
            shots.append({
                "shot_number": i + 1,
                "shot_type": shot_type["type"],
                "shot_name": shot_type["name"],
                "duration": shot_type["duration"],
                "description": f"{shot_type['name']} - {prompt[:50]}",
                "camera_movement": "缓慢推拉",
                "framing": shot_type["name"],
            })

        return shots

    async def _break_down_shots_with_llm(self, prompt: str) -> List[Dict[str, Any]]:
        """
        使用LLM智能拆分场景为多个镜头

        Args:
            prompt: 场景提示词

        Returns:
            镜头列表
        """
        try:
            llm_service = get_zhipuai_service()

            system_prompt = """你是一位专业的影视分镜导演，擅长将场景描述拆分为详细的镜头序列。

你的任务：
1. 分析场景描述，理解其核心内容和情感
2. 将场景拆分为3-6个镜头，每个镜头都有明确的目的
3. 为每个镜头指定合适的类型（建立镜头/中景/特写/细节/过肩镜头等）
4. 设计每个镜头的时长、机位运动和构图方式
5. 确保镜头之间有逻辑连贯性和视觉节奏

输出格式（必须是JSON数组）：
[
  {
    "shot_number": 1,
    "shot_type": "镜头类型（establishing/medium/close-up/detail/over_the_shoulder等）",
    "shot_name": "镜头名称",
    "duration": "时长（如3s）",
    "description": "详细的镜头画面描述",
    "camera_angle": "机位角度（平视/俯拍/仰拍等）",
    "camera_movement": "镜头运动（推/拉/摇/移/跟/固定等）",
    "composition": "构图方式（黄金分割/中心/对角线等）",
    "purpose": "这个镜头的作用"
  }
]

请只输出JSON数组，不要有任何其他文字。"""

            user_message = f"""请为以下场景设计专业的分镜镜头序列：

场景描述：{prompt}

请生成3-6个镜头，确保镜头连贯、有节奏感，适合影视制作。"""

            response = await llm_service.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.8
            )

            # 解析JSON
            import json
            try:
                # 清理可能的markdown标记
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]

                shots = json.loads(clean_response)

                # 验证并补充默认值
                for shot in shots:
                    shot.setdefault("shot_number", shot.get("shot_number", 1))
                    shot.setdefault("shot_type", shot.get("shot_type", "medium"))
                    shot.setdefault("shot_name", shot.get("shot_name", "中景"))
                    shot.setdefault("duration", shot.get("duration", "3s"))
                    shot.setdefault("camera_movement", shot.get("camera_movement", "固定"))
                    shot.setdefault("framing", shot.get("shot_name", "中景"))

                return shots

            except json.JSONDecodeError as e:
                print(f"LLM返回的不是有效JSON，使用模板方式: {response}, 错误: {e}")
                return await self._break_down_shots(prompt)

        except Exception as e:
            print(f"LLM调用失败，使用模板方式: {str(e)}")
            return await self._break_down_shots(prompt)

    async def _create_image_prompt(self, shot: Dict[str, Any]) -> str:
        """
        为镜头创建图片生成提示词（模板方式，作为fallback）

        Args:
            shot: 镜头信息

        Returns:
            图片生成提示词
        """
        shot_type = shot.get("shot_type", "medium")
        description = shot.get("description", "")
        camera_movement = shot.get("camera_movement", "静止")

        image_prompt = f"""{description}

镜头类型: {shot_type}
镜头运动: {camera_movement}
画面构图: 专业电影构图
光线: 自然光+补光
色调: 电影感调色
质量: 8K超高清，细节丰富
风格: 电影剧照级别"""

        return image_prompt.strip()

    async def _create_image_prompt_with_llm(
        self,
        shot: Dict[str, Any],
        scene_context: str
    ) -> str:
        """
        使用LLM为镜头创建优化的图片生成提示词

        Args:
            shot: 镜头信息
            scene_context: 场景上下文

        Returns:
            图片生成提示词
        """
        try:
            llm_service = get_zhipuai_service()

            shot_description = shot.get("description", "")
            shot_type = shot.get("shot_type", "中景")
            camera_angle = shot.get("camera_angle", "平视")
            camera_movement = shot.get("camera_movement", "固定")
            composition = shot.get("composition", "黄金分割")

            system_prompt = """你是一位专业的AI图片生成提示词专家，擅长创建高质量、细节丰富的图片生成提示词。

你的任务：
1. 根据镜头描述和场景上下文，生成详细的、适合AI图片生成的提示词
2. 提示词应该包含：主体描述、环境细节、光线设置、色彩风格、技术参数
3. 使用适合AI图片生成的专业术语（如"8K"、"cinematic lighting"、"depth of field"等）
4. 确保提示词具体、可执行，能生成高质量的电影级画面

输出要求：
- 直接输出提示词，不要有任何解释
- 使用中文
- 保持专业但易于理解
- 长度在200-400字之间"""

            user_message = f"""请为以下镜头创建专业的AI图片生成提示词：

场景上下文：{scene_context}

镜头信息：
- 镜头描述：{shot_description}
- 镜头类型：{shot_type}
- 机位角度：{camera_angle}
- 镜头运动：{camera_movement}
- 构图方式：{composition}

请生成详细的、电影级的图片生成提示词，包含画面描述、光线、色彩、技术参数等。"""

            image_prompt = await llm_service.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7
            )

            return image_prompt.strip()

        except Exception as e:
            print(f"LLM调用失败，使用模板方式: {str(e)}")
            return await self._create_image_prompt(shot)

    async def visualize_composition(
        self,
        shot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        可视化构图

        Args:
            shot: 镜头信息

        Returns:
            构图可视化数据
        """
        return {
            "framing": shot.get("framing", "中景"),
            "subject_position": "center-third",
            "background": "blurred",
            "depth_of_field": "shallow",
            "leading_lines": "use leading lines",
            "rule_of_thirds": True,
        }

    async def sequence_shots(
        self,
        shots: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        排序镜头序列

        Args:
            shots: 镜头列表

        Returns:
            排序后的镜头
        """
        # 根据镜头编号排序
        return sorted(shots, key=lambda x: x.get("shot_number", 0))
