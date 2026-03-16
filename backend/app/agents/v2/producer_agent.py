"""Producer Agent - 制片Agent"""
from typing import Dict, Any, Optional, List
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse
from app.services.zhipuai_service import get_zhipuai_service


class ProducerAgent(BaseAgentV2):
    """
    Producer Agent - AI制片
    负责prompt优化、生成稳定的提示词
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "producer"
        self.agent_name = "AI制片"
        self.description = "负责提示词优化和生成，确保可执行的创作指令"
        self.capabilities = [
            "optimize_prompt",
            "create_detailed_prompts",
            "ensure_prompt_stability",
            "add_technical_specifications",
            "version_control_prompts",
        ]

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        return "creative_concept" in input_data or "base_prompt" in input_data

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理创意概念，生成优化的提示词

        Args:
            input_data: 包含creative_concept或base_prompt，可能还包含storyline和visual_style
            context: 上下文（可能包含导演的创意）

        Returns:
            AgentResponse: 优化的提示词
        """
        try:
            # 获取创意概念（可能来自导演）
            creative_concept = input_data.get("creative_concept") or context.get("creative_concept")

            if not creative_concept:
                # 如果没有创意概念，直接处理基础prompt
                base_prompt = input_data.get("base_prompt", "")
                optimized_prompt = await self._optimize_prompt_with_llm(base_prompt)
                prompts = [{"version": 1, "content": optimized_prompt}]
            else:
                # 构建完整的数据结构，包含creative_concept, storyline, visual_style
                full_concept = {
                    **creative_concept,  # 包含title, theme等
                    "storyline": input_data.get("storyline", creative_concept.get("storyline", {})),
                    "visual_style": input_data.get("visual_style", creative_concept.get("visual_style", {})),
                }

                # 根据创意概念生成多个场景的提示词
                prompts = await self._create_scene_prompts(full_concept)

            return AgentResponse(
                success=True,
                data={
                    "prompts": prompts,
                    "total_prompts": len(prompts),
                },
                message=f"✅ 我创作了{len(prompts)}个优化提示词",
                next_agent="storyboard",  # 下一步传给分镜
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"制片处理失败: {str(e)}",
                message="抱歉，提示词生成遇到了问题",
            )

    async def _optimize_prompt(self, base_prompt: str) -> str:
        """
        优化单个提示词

        Args:
            base_prompt: 基础提示词

        Returns:
            优化后的提示词
        """
        # 添加技术规范和风格描述
        optimized = f"""{base_prompt}

Technical Specifications:
- Style: Cinematic, High Quality
- Lighting: Professional, Natural
- Composition: Rule of Thirds
- Color Grading: Warm, Film-like
- Detail: Ultra detailed, 8K resolution
- Camera: DSLR, Prime Lens"""

        return optimized.strip()

    async def _optimize_prompt_with_llm(self, base_prompt: str) -> str:
        """
        使用LLM优化提示词

        Args:
            base_prompt: 基础提示词

        Returns:
            优化后的提示词
        """
        try:
            llm_service = get_zhipuai_service()

            system_prompt = """你是一位专业的影视制片，擅长将简单的创意描述转化为详细的、可执行的影视制作提示词。

你的任务：
1. 将用户的创意描述扩展为专业的影视制作提示词
2. 添加必要的技术规格（镜头、光线、构图、色调等）
3. 确保提示词具体、可执行，适合AI图片或视频生成

输出格式：
- 直接输出优化后的提示词
- 不要有任何解释或开场白
- 使用中文"""

            optimized = await llm_service.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=base_prompt,
                temperature=0.7
            )

            return optimized.strip()
        except Exception as e:
            # 如果LLM调用失败，回退到模板方式
            print(f"LLM调用失败，使用模板方式: {str(e)}")
            return await self._optimize_prompt(base_prompt)

    async def _create_scene_prompts(self, creative_concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据创意概念创建场景提示词

        Args:
            creative_concept: 创意概念

        Returns:
            提示词列表
        """
        prompts = []

        # 从创意概念中提取信息
        theme = creative_concept.get("theme", "")
        visual_style = creative_concept.get("visual_style", {})
        storyline = creative_concept.get("storyline", {})

        # 为每个关键场景生成提示词
        key_scenes = storyline.get("key_scenes", [])

        if not key_scenes:
            # 如果没有定义场景，生成默认场景
            key_scenes = [
                {"description": "开场镜头", "duration": "3s"},
                {"description": "主体内容", "duration": "5s"},
                {"description": "结尾画面", "duration": "3s"},
            ]

        for i, scene in enumerate(key_scenes, 1):
            scene_prompt = await self._generate_scene_prompt_with_llm(
                scene_number=i,
                scene_description=scene.get("description", ""),
                theme=theme,
                visual_style=visual_style,
            )

            prompts.append({
                "version": 1,
                "scene_number": i,
                "content": scene_prompt,
                "duration": scene.get("duration", "5s"),
                "creative_concept": {
                    "theme": theme,
                    "genre": creative_concept.get("genre", ""),
                    "mood": creative_concept.get("mood", ""),
                    "target_audience": creative_concept.get("target_audience", ""),
                },
            })

        return prompts

    async def _generate_scene_prompt_with_llm(
        self,
        scene_number: int,
        scene_description: str,
        theme: str,
        visual_style: Dict[str, Any],
    ) -> str:
        """
        使用LLM生成单个场景的提示词

        Args:
            scene_number: 场景编号
            scene_description: 场景描述
            theme: 主题
            visual_style: 视觉风格

        Returns:
            场景提示词
        """
        try:
            llm_service = get_zhipuai_service()

            cinematography = visual_style.get("cinematography", "电影质感")
            lighting = visual_style.get("lighting", "自然光")
            composition = visual_style.get("composition", "黄金分割")

            system_prompt = f"""你是一位专业的影视导演和摄影师，擅长创作详细的、有视觉冲击力的场景描述。

你的任务：
1. 根据提供的场景描述、主题和视觉风格，生成专业的分镜提示词
2. 提示词应该包含：场景氛围、画面构图、光线设置、镜头运动、色调风格
3. 确保提示词具体、可执行，适合AI图片或视频生成

输出要求：
- 直接输出分镜提示词
- 不要有任何解释或开场白
- 使用中文
- 保持专业但易于理解"""

            user_message = f"""请为以下场景创作专业的分镜提示词：

场景编号: {scene_number}
主题: {theme}
场景描述: {scene_description}

视觉风格参考:
- 风格: {cinematography}
- 光线: {lighting}
- 构图: {composition}
- 色调: 温暖电影感

请生成详细的分镜提示词，包含画面描述、镜头角度、光线和氛围。"""

            prompt = await llm_service.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.8
            )

            return prompt.strip()
        except Exception as e:
            # 如果LLM调用失败，回退到模板方式
            print(f"LLM调用失败，使用模板方式: {str(e)}")
            return await self._generate_scene_prompt(
                scene_number=scene_number,
                scene_description=scene_description,
                theme=theme,
                visual_style=visual_style,
            )

    async def _generate_scene_prompt(
        self,
        scene_number: int,
        scene_description: str,
        theme: str,
        visual_style: Dict[str, Any],
    ) -> str:
        """
        生成单个场景的提示词（模板方式，作为LLM的后备）

        Args:
            scene_number: 场景编号
            scene_description: 场景描述
            theme: 主题
            visual_style: 视觉风格

        Returns:
            场景提示词
        """
        cinematography = visual_style.get("cinematography", "电影质感")
        lighting = visual_style.get("lighting", "自然光")
        composition = visual_style.get("composition", "黄金分割")

        prompt = f"""🎬 Scene {scene_number}: {scene_description}

主题: {theme}
场景描述: {scene_description}

视觉风格:
- 风格: {cinematography}
- 光线: {lighting}
- 构图: {composition}
- 色调: 温暖电影感
- 质量: 高画质，细节丰富
- 镜头: 专业电影镜头

参考: 电影级画面，精致细节，氛围感强"""

        return prompt.strip()

    async def ensure_prompt_stability(self, prompt: str) -> str:
        """
        确保提示词稳定性

        Args:
            prompt: 输入提示词

        Returns:
            稳定后的提示词
        """
        # 添加稳定性关键词
        stability_keywords = [
            "consistent style",
            "maintain character consistency",
            "uniform lighting",
            "coherent color palette",
        ]

        return f"{prompt}\n\nQuality Assurance: {', '.join(stability_keywords)}"

    async def add_technical_specifications(
        self,
        prompt: str,
        specs: Dict[str, Any],
    ) -> str:
        """
        添加技术规格

        Args:
            prompt: 基础提示词
            specs: 技术规格

        Returns:
            添加了技术规格的提示词
        """
        tech_specs = f"""
Technical Specifications:
- Resolution: {specs.get('resolution', '4K')}
- Aspect Ratio: {specs.get('aspect_ratio', '16:9')}
- Frame Rate: {specs.get('fps', '24fps')}
- Color Space: {specs.get('color_space', 'sRGB')}
- Bit Depth: {specs.get('bit_depth', '10-bit')}"""

        return f"{prompt}{tech_specs}"

